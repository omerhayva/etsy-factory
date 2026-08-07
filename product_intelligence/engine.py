from __future__ import annotations

from dataclasses import asdict
from typing import Any

from database.db import EtsyDatabase
from exports.exporter import export_csv, export_json
from product_intelligence.catalog import default_product_catalog
from product_intelligence.matching import match_product
from product_intelligence.models import ProductCatalogItem, ProductMatchInput
from product_intelligence.profit import analyze_profit
from product_intelligence.provider_adapter import BasePODProviderAdapter, GenericPODProviderAdapter
from product_intelligence.quality import analyze_quality
from product_intelligence.recommendations import recommendation_reasons, top_ranked_recommendations
from product_intelligence.report_generator import ProductIntelligenceReportGenerator
from product_intelligence.risk import analyze_risk
from product_intelligence.shipping import analyze_shipping
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


class ProductIntelligenceEngine:
    """Selects the best POD product per niche with provider-adapter architecture."""

    def __init__(
        self,
        db: EtsyDatabase,
        catalog: list[ProductCatalogItem] | None = None,
        provider_adapters: list[BasePODProviderAdapter] | None = None,
    ):
        self.db = db
        self.catalog = catalog or default_product_catalog()
        self.provider_adapters = provider_adapters or [GenericPODProviderAdapter()]
        self.report_generator = ProductIntelligenceReportGenerator()

    def run(self, session_label: str = "product-intelligence", export_dir: str | None = None) -> dict[str, Any]:
        niches_df = self.db.fetch_niche_intelligence_overview()
        if niches_df.empty:
            return {"session_id": None, "rows": [], "report": {}, "exports": {}}

        session_id = self.db.save_research_session(
            {
                "session_label": session_label,
                "sources": [adapter.name for adapter in self.provider_adapters],
                "status": "running",
            }
        )

        self._persist_catalog_once()
        all_rows: list[dict[str, Any]] = []

        try:
            for _, niche_row in niches_df.iterrows():
                best_rows = self._process_niche(session_id, niche_row.to_dict())
                all_rows.extend(best_rows)

            report = self.report_generator.generate(all_rows)
            exports: dict[str, str] = {}
            if export_dir:
                exports = self.report_generator.export(report, export_dir=export_dir, prefix=f"session_{session_id}")
                exports["recommendations_json"] = str(
                    export_json(all_rows, f"{export_dir}/session_{session_id}_product_recommendations.json")
                )
                exports["recommendations_csv"] = str(
                    export_csv(all_rows, f"{export_dir}/session_{session_id}_product_recommendations.csv")
                )

            self.db.save_market_report(
                {
                    "session_id": session_id,
                    "report_name": "product_intelligence_report",
                    "report_payload": report,
                }
            )
            self.db.close_research_session(session_id, status="completed", summary=f"Matched {len(all_rows)} product recommendations")
            return {"session_id": session_id, "rows": all_rows, "report": report, "exports": exports}
        except Exception as exc:
            LOGGER.exception("Product intelligence engine failed")
            self.db.close_research_session(session_id, status="failed", summary=str(exc))
            raise

    def _persist_catalog_once(self) -> None:
        existing = self.db.fetch_dataframe("product_catalog")
        if not existing.empty:
            return
        for adapter in self.provider_adapters:
            for item in self.catalog:
                adjustment = adapter.get_adjustment(item.name)
                self.db.save_product_catalog_item(
                    {
                        "provider": adapter.name,
                        "product_name": item.name,
                        "category": item.category,
                        "subcategory": item.subcategory,
                        "typical_retail_price": item.typical_retail_price,
                        "estimated_production_cost": round(item.estimated_production_cost * adjustment.production_cost_multiplier, 2),
                        "estimated_profit_margin": item.estimated_profit_margin,
                        "popularity": item.popularity,
                        "gift_potential": item.gift_potential,
                        "customization_difficulty": item.customization_difficulty,
                        "shipping_complexity": round(item.shipping_complexity * adjustment.shipping_complexity_multiplier, 2),
                        "average_processing_time": item.average_processing_time,
                        "return_risk": item.return_risk,
                        "print_area": item.print_area,
                        "color_variants": item.color_variants,
                    }
                )

    def _process_niche(self, session_id: int, niche: dict[str, Any]) -> list[dict[str, Any]]:
        niche_name = str(niche.get("niche_name", "unknown"))
        seasonal = int(niche.get("seasonal", 0) or 0)
        season_labels = []
        if seasonal:
            season_labels = ["seasonal"]

        input_row = ProductMatchInput(
            niche_name=niche_name,
            audiences=[],
            season_labels=season_labels,
            competition_score=float(niche.get("competition_score") or 50),
            gift_intent=float(niche.get("gift_suitability") or 50),
            trend_score=float(niche.get("confidence") or 50),
            evergreen_score=85.0 if niche.get("evergreen_classification") == "Evergreen" else (72.0 if niche.get("evergreen_classification") == "Trending" else 58.0),
        )

        scored = []
        for adapter in self.provider_adapters:
            for product in self.catalog:
                scored.append(match_product(input_row, product, adapter.name))

        ranked = top_ranked_recommendations(scored, top_k=4)
        rows: list[dict[str, Any]] = []

        for rank, score_item in enumerate(ranked, start=1):
            product = next(item for item in self.catalog if item.name == score_item.product_name)
            adapter = next(item for item in self.provider_adapters if item.name == score_item.provider)
            adjust = adapter.get_adjustment(product.name)

            adjusted_cost = round(product.estimated_production_cost * adjust.production_cost_multiplier, 2)
            profit = analyze_profit(
                typical_retail_price=product.typical_retail_price,
                production_cost=adjusted_cost,
                demand_signal=float(niche.get("overall_score") or 50),
                trend_signal=input_row.trend_score,
            )
            shipping = analyze_shipping(product)
            quality = analyze_quality(product, adjust.quality_multiplier)
            risk = analyze_risk(product, seasonal=bool(seasonal))

            reasons = recommendation_reasons(score_item, niche_name, str(niche.get("evergreen_classification") or "Unknown"))

            self.db.save_product_score(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "product_name": score_item.product_name,
                    "provider": score_item.provider,
                    "match_score": score_item.match_score,
                    "ranking": rank,
                    "reasoning": "; ".join(reasons),
                }
            )
            self.db.save_product_profit(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "product_name": score_item.product_name,
                    **asdict(profit),
                }
            )
            self.db.save_product_shipping(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "product_name": score_item.product_name,
                    **asdict(shipping),
                }
            )
            self.db.save_product_quality(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "product_name": score_item.product_name,
                    **asdict(quality),
                }
            )
            self.db.save_product_risk(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "product_name": score_item.product_name,
                    **asdict(risk),
                }
            )
            self.db.save_product_recommendation(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "recommended_product": score_item.product_name,
                    "provider": score_item.provider,
                    "score": score_item.match_score,
                    "reasons": reasons,
                }
            )

            risk_index = (risk.return_risk + risk.complaint_risk + risk.fragility_risk + risk.seasonality_risk) / 4.0
            rows.append(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "recommended_product": score_item.product_name,
                    "provider": score_item.provider,
                    "score": score_item.match_score,
                    "ranking": rank,
                    "reasons": "; ".join(reasons),
                    "estimated_margin_percent": profit.estimated_margin_percent,
                    "estimated_gross_profit": profit.estimated_gross_profit,
                    "gift_suitability": product.gift_potential,
                    "seasonal": seasonal,
                    "risk_index": round(risk_index, 2),
                }
            )

        return rows
