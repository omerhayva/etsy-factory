from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from database.db import EtsyDatabase
from product_factory.factory import ProductFactory


class FakeResearchManager:
    def __init__(self, db: EtsyDatabase):
        self.db = db

    def run_session(self, seed_terms: list[str], session_label: str = "research-session", export_dir: str | None = None) -> dict[str, Any]:
        session_id = self.db.save_research_session(
            {
                "session_label": session_label,
                "sources": ["fake_research_manager"],
                "status": "running",
            }
        )
        self.db.save_niche(
            {
                "niche_name": "vintage camping gift",
                "demand_score": 88,
                "competition_score": 44,
                "profit_potential": 82,
                "design_difficulty": 28,
                "pod_compatibility": 92,
                "opportunity_score": 87,
                "market_data": seed_terms,
                "category": "Camping",
                "source": "fake_research_manager",
                "status": "active",
                "confidence_score": 79,
                "reasoning": "seeded for product factory",
                "session_id": session_id,
            }
        )
        self.db.close_research_session(session_id, status="completed", summary="Seeded factory niche")
        return {"session_id": session_id, "opportunities": seed_terms, "report": {}, "exports": {}}


class FakeCommercialEngine:
    def __init__(self):
        self.calls = 0

    def run(self, session_label: str = "commercial-validation", export_dir: str | None = None, candidate_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        self.calls += 1
        rows: list[dict[str, Any]] = []
        for candidate in candidate_rows or []:
            title = str(candidate.get("selected_title") or candidate.get("title") or "")
            tags = candidate.get("tags") or []
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
            has_gift_signal = "gift" in title.lower() or any("gift" in str(tag).lower() for tag in tags)
            ready = self.calls > 1 and has_gift_signal
            rows.append(
                {
                    "session_id": self.calls,
                    "niche_name": candidate.get("niche_name"),
                    "product_name": candidate.get("product_name") or candidate.get("recommended_product"),
                    "commercial_score": 82.0 if ready else 58.0,
                    "confidence_score": 74.0 if ready else 48.0,
                    "risk_score": 24.0 if ready else 61.0,
                    "estimated_success_level": "High" if ready else "Moderate",
                    "publish_decision": "READY FOR PUBLISH" if ready else "NEEDS IMPROVEMENT",
                    "reasons": [] if ready else ["Add gift angle", "Strengthen pricing position"],
                    "recommendations": [] if ready else ["Add gift angle", "Strengthen pricing position"],
                    "competitor_gap": {},
                    "buyer_psychology": {},
                    "pricing_validation": {},
                    "gift_validation": {},
                    "trend_validation": {},
                    "validation": {},
                }
            )
        return {"session_id": self.calls, "rows": rows, "report": {}, "exports": {}}


def test_product_factory_runs_pipeline_and_exports_approved_products(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "factory.sqlite3")
    db.initialize()

    factory = ProductFactory(
        db=db,
        research_manager=FakeResearchManager(db),
        commercial_engine=FakeCommercialEngine(),
    )

    export_dir = tmp_path / "exports"
    result = factory.run(
        niche="vintage camping gift",
        audience="gift buyers",
        product_category="t-shirt",
        language="en",
        market="US",
        session_label="product-factory-test",
        export_dir=str(export_dir),
    )

    assert result["status"] == "completed"
    assert result["generated_products"]
    assert result["retry_used"] is True
    assert result["approved_products"]
    assert result["exports"]

    run_df = db.fetch_factory_runs()
    assert not run_df.empty
    assert run_df.iloc[0]["status"] == "completed"

    pipeline_df = db.fetch_pipeline_logs(run_id=result["run_id"])
    assert not pipeline_df.empty

    workflow_df = db.fetch_workflow_reports(run_id=result["run_id"])
    assert not workflow_df.empty

    approved_folders = json.loads(result["exports"]["approved_folders"])
    assert approved_folders
    first_folder = Path(approved_folders[0])
    assert (first_folder / "listing.json").exists()
    assert (first_folder / "listing.md").exists()
    assert (first_folder / "design_prompt.txt").exists()
    assert (first_folder / "summary.txt").exists()
