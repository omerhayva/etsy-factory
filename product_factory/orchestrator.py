from __future__ import annotations

from dataclasses import asdict
from typing import Any

from commercial_validation.engine import CommercialValidationEngine
from database.db import EtsyDatabase
from design_intelligence.engine import DesignIntelligenceEngine
from niche_intelligence.engine import NicheIntelligenceEngine
from product_factory.pipeline import ProductFactoryPipeline
from product_factory.report import ProductFactoryReport
from product_factory.state_manager import ProductFactoryStateManager
from product_factory.workflow import ProductFactoryInput, ProductFactoryWorkflow
from product_intelligence.engine import ProductIntelligenceEngine
from research.research_manager import ResearchManager
from seo_intelligence.engine import SeoComplianceIntelligenceEngine
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


class ProductFactoryOrchestrator:
    def __init__(
        self,
        db: EtsyDatabase,
        research_manager: ResearchManager | None = None,
        niche_engine: NicheIntelligenceEngine | None = None,
        product_engine: ProductIntelligenceEngine | None = None,
        design_engine: DesignIntelligenceEngine | None = None,
        seo_engine: SeoComplianceIntelligenceEngine | None = None,
        commercial_engine: CommercialValidationEngine | None = None,
    ):
        self.db = db
        self.workflow = ProductFactoryWorkflow(db)
        self.report = ProductFactoryReport()
        self.state_manager = ProductFactoryStateManager(db)
        self.research_manager = research_manager or ResearchManager(db=db)
        self.niche_engine = niche_engine or NicheIntelligenceEngine(db=db)
        self.product_engine = product_engine or ProductIntelligenceEngine(db=db)
        self.design_engine = design_engine or DesignIntelligenceEngine(db=db)
        self.seo_engine = seo_engine or SeoComplianceIntelligenceEngine(db=db)
        self.commercial_engine = commercial_engine or CommercialValidationEngine(db=db)

    def run(
        self,
        *,
        niche: str,
        audience: str,
        product_category: str,
        language: str,
        market: str,
        session_label: str = "product-factory",
        export_dir: str | None = None,
    ) -> dict[str, Any]:
        factory_input = self.workflow.normalize_input(
            {
                "niche": niche,
                "audience": audience,
                "product_category": product_category,
                "language": language,
                "market": market,
            }
        )
        run_id = self.state_manager.start_run(
            {
                "session_label": session_label,
                "niche": factory_input.niche,
                "audience": factory_input.audience,
                "product_category": factory_input.product_category,
                "language": factory_input.language,
                "market": factory_input.market,
                "status": "running",
                "summary": "",
                "retry_count": 0,
                "input_payload": asdict(factory_input),
            }
        )

        pipeline = ProductFactoryPipeline(self.state_manager)
        context: dict[str, Any] = {
            "factory_input": factory_input,
            "session_label": session_label,
            "run_id": run_id,
            "export_dir": export_dir,
            "seed_terms": self.workflow.seed_terms(factory_input),
        }

        def research_step(working_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "research_output": self.research_manager.run_session(
                    seed_terms=working_context["seed_terms"],
                    session_label=f"{session_label}-research",
                    export_dir=None,
                )
            }

        def analyze_step(working_context: dict[str, Any]) -> dict[str, Any]:
            return {"niche_output": self.niche_engine.run(session_label=f"{session_label}-niche", export_dir=None)}

        def choose_product_step(working_context: dict[str, Any]) -> dict[str, Any]:
            return {"product_output": self.product_engine.run(session_label=f"{session_label}-product", export_dir=None)}

        def design_step(working_context: dict[str, Any]) -> dict[str, Any]:
            return {"design_output": self.design_engine.run(session_label=f"{session_label}-design", export_dir=None)}

        def listing_step(working_context: dict[str, Any]) -> dict[str, Any]:
            return {"seo_output": self.seo_engine.run(session_label=f"{session_label}-seo", export_dir=None)}

        def validate_step(working_context: dict[str, Any]) -> dict[str, Any]:
            return {"commercial_output": self._run_commercial_validation(working_context)}

        def export_step(working_context: dict[str, Any]) -> dict[str, Any]:
            report = self._build_report(working_context)
            exports = self.report.export(report, export_dir=export_dir, prefix=f"product_factory_run_{run_id}") if export_dir else {}
            return {"report": report, "exports": exports}

        handlers = {
            "Research": research_step,
            "Analyze": analyze_step,
            "Choose Product": choose_product_step,
            "Generate Design Strategy": design_step,
            "Generate Listing": listing_step,
            "Validate": validate_step,
            "Export": export_step,
        }

        try:
            pipeline_steps, finished_context = pipeline.run(run_id=run_id, context=context, handlers=handlers)
            report = finished_context.get("report") or self._build_report(finished_context)
            approved_products = list(report.get("approved_products", []))
            status = "completed"
            summary = f"Generated {len(report.get('generated_products', []))} products, approved {len(approved_products)}, retry_used={report.get('retry_used', False)}"
            self._persist_workflow_reports(run_id, report)
            self.state_manager.finish_run(run_id=run_id, status=status, summary=summary, retry_count=int(report.get("retry_used", False)))
            return {
                "run_id": run_id,
                "status": status,
                "factory_input": asdict(factory_input),
                "pipeline_steps": pipeline_steps,
                "generated_products": report.get("generated_products", []),
                "commercial_scores": report.get("commercial_scores", []),
                "publish_decisions": report.get("publish_decisions", []),
                "approved_products": approved_products,
                "report": report,
                "exports": finished_context.get("exports", {}),
                "retry_used": report.get("retry_used", False),
                "summary": summary,
            }
        except Exception as exc:
            LOGGER.exception("Product factory run failed")
            self.state_manager.finish_run(run_id=run_id, status="failed", summary=str(exc), retry_count=0)
            raise

    def _run_commercial_validation(self, working_context: dict[str, Any]) -> dict[str, Any]:
        seo_output = working_context["seo_output"]
        factory_input: ProductFactoryInput = working_context["factory_input"]
        commercial_output = self.commercial_engine.run(
            session_label=f"{working_context['session_label']}-commercial",
            export_dir=None,
            candidate_rows=list(seo_output.get("rows", [])),
        )

        needs_improvement = [row for row in commercial_output.get("rows", []) if row.get("publish_decision") != "READY FOR PUBLISH"]
        retry_used = bool(needs_improvement)
        final_rows = list(commercial_output.get("rows", []))

        if needs_improvement:
            retry_candidates = []
            for row in needs_improvement:
                retry_candidates.append(self.workflow.build_candidate_retry(row, factory_input))
            retry_output = self.commercial_engine.run(
                session_label=f"{working_context['session_label']}-commercial-retry",
                export_dir=None,
                candidate_rows=retry_candidates,
            )
            final_rows = self._merge_commercial_results(final_rows, retry_output.get("rows", []))
            commercial_output = dict(commercial_output)
            commercial_output["retry_output"] = retry_output
            commercial_output["rows"] = final_rows
            commercial_output["retry_used"] = True
        else:
            commercial_output = dict(commercial_output)
            commercial_output["retry_used"] = False

        working_context["commercial_output"] = commercial_output
        return commercial_output

    def _merge_commercial_results(self, initial_rows: list[dict[str, Any]], retry_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged = []
        retry_lookup = {(str(row.get("niche_name")), str(row.get("product_name"))): row for row in retry_rows}
        for row in initial_rows:
            key = (str(row.get("niche_name")), str(row.get("product_name")))
            merged.append(retry_lookup.get(key, row))
        return merged

    def _build_report(self, working_context: dict[str, Any]) -> dict[str, Any]:
        factory_input: ProductFactoryInput = working_context["factory_input"]
        seo_rows = list(working_context.get("seo_output", {}).get("rows", []))
        commercial_rows = list(working_context.get("commercial_output", {}).get("rows", []))

        niche_lookup = self._frame_lookup(self.db.fetch_niche_intelligence_overview(), ("niche_name",))
        product_lookup = self._frame_lookup(self.db.fetch_product_intelligence_recommendations(limit=500), ("niche_name", "product_name"))
        design_lookup = self._frame_lookup(self.db.fetch_design_intelligence_overview(limit=500), ("niche_name", "product_name"))
        research_lookup = self._frame_lookup(self.db.fetch_opportunity_overview(limit=500), ("niche_name",))
        commercial_lookup = {(str(row.get("niche_name")), str(row.get("product_name"))): row for row in commercial_rows}
        seo_lookup = {(str(row.get("niche_name")), str(row.get("product_name"))): row for row in seo_rows}

        packages: list[dict[str, Any]] = []
        for key, commercial_row in commercial_lookup.items():
            seo_row = seo_lookup.get(key, {})
            niche_row = niche_lookup.get((str(commercial_row.get("niche_name")),), {})
            product_row = product_lookup.get((str(commercial_row.get("niche_name")), str(commercial_row.get("product_name"))), {})
            design_row = design_lookup.get((str(commercial_row.get("niche_name")), str(commercial_row.get("product_name"))), {})
            research_row = research_lookup.get((str(commercial_row.get("niche_name")),), {})
            package = self.workflow.build_product_package(
                factory_input=factory_input,
                run_id=working_context["run_id"],
                seo_row=seo_row,
                commercial_row=commercial_row,
                product_row=product_row,
                design_row=design_row,
                niche_row=niche_row,
                research_row=research_row,
                attempt_number=2 if working_context.get("commercial_output", {}).get("retry_used") else 1,
            )
            packages.append(package)

        report = self.report.generate(
            run_id=working_context["run_id"],
            factory_input=asdict(factory_input),
            pipeline_steps=list(working_context.get("pipeline_steps", [])),
            packages=packages,
            retry_used=bool(working_context.get("commercial_output", {}).get("retry_used")),
            status="completed",
        )
        return report

    def _persist_workflow_reports(self, run_id: int, report: dict[str, Any]) -> None:
        for package in report.get("generated_products", []):
            self.state_manager.save_report(
                run_id=run_id,
                niche_name=str(package.get("niche_name", "")),
                product_name=str(package.get("recommended_product", "")),
                report_payload=package,
            )

    def _frame_lookup(self, frame, key_fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, Any]]:
        if frame.empty:
            return {}
        lookup: dict[tuple[str, ...], dict[str, Any]] = {}
        for _, row in frame.iterrows():
            lookup[tuple(str(row.get(field, "")) for field in key_fields)] = row.to_dict()
        return lookup
