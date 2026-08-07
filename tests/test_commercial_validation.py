from __future__ import annotations

from pathlib import Path

from commercial_validation.engine import CommercialValidationEngine
from database.db import EtsyDatabase
from design_intelligence.engine import DesignIntelligenceEngine
from niche_intelligence.engine import NicheIntelligenceEngine
from product_intelligence.engine import ProductIntelligenceEngine
from seo_intelligence.engine import SeoComplianceIntelligenceEngine


def test_commercial_validation_engine_runs_and_persists_outputs(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "commercial.sqlite3")
    db.initialize()

    db.save_niche(
        {
            "niche_name": "retro teacher gift",
            "demand_score": 82,
            "competition_score": 44,
            "profit_potential": 76,
            "design_difficulty": 28,
            "pod_compatibility": 89,
            "opportunity_score": 84,
            "market_data": [],
            "category": "Education",
            "source": "test",
            "status": "active",
            "confidence_score": 74,
            "reasoning": "seed",
            "session_id": 1,
        }
    )

    niche_output = NicheIntelligenceEngine(db).run(session_label="niche-intelligence-commercial-test", export_dir=str(tmp_path / "exports"))
    assert niche_output["rows"]

    product_output = ProductIntelligenceEngine(db).run(session_label="product-intelligence-commercial-test", export_dir=str(tmp_path / "exports"))
    assert product_output["rows"]

    design_output = DesignIntelligenceEngine(db).run(session_label="design-intelligence-commercial-test", export_dir=str(tmp_path / "exports"))
    assert design_output["rows"]

    seo_output = SeoComplianceIntelligenceEngine(db).run(session_label="seo-intelligence-commercial-test", export_dir=str(tmp_path / "exports"))
    assert seo_output["rows"]

    output = CommercialValidationEngine(db).run(session_label="commercial-validation-test", export_dir=str(tmp_path / "exports"))

    assert output["session_id"] is not None
    assert output["rows"]
    assert "report_json" in output["exports"]
    assert "report_csv" in output["exports"]
    assert "package_json" in output["exports"]
    assert "package_csv" in output["exports"]
    assert "package_md" in output["exports"]

    overview_df = db.fetch_commercial_overview(limit=10)
    assert not overview_df.empty

    scores_df = db.fetch_commercial_scores(limit=10)
    assert not scores_df.empty

    decisions_df = db.fetch_commercial_publish_decisions(limit=10)
    assert not decisions_df.empty

    assert set(decisions_df["publish_decision"].dropna().unique()).issubset({"READY FOR PUBLISH", "NEEDS IMPROVEMENT"})
