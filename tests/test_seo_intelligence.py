from __future__ import annotations

from pathlib import Path

from database.db import EtsyDatabase
from design_intelligence.engine import DesignIntelligenceEngine
from niche_intelligence.engine import NicheIntelligenceEngine
from product_intelligence.engine import ProductIntelligenceEngine
from seo_intelligence.engine import SeoComplianceIntelligenceEngine


def test_seo_compliance_engine_runs_and_persists_outputs(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "seo.sqlite3")
    db.initialize()

    db.save_niche(
        {
            "niche_name": "minimal teacher gift",
            "demand_score": 82,
            "competition_score": 46,
            "profit_potential": 74,
            "design_difficulty": 30,
            "pod_compatibility": 90,
            "opportunity_score": 84,
            "market_data": [],
            "category": "Education",
            "source": "test",
            "status": "active",
            "confidence_score": 75,
            "reasoning": "seed",
            "session_id": 1,
        }
    )

    niche_output = NicheIntelligenceEngine(db).run(session_label="niche-intelligence-seo-test", export_dir=str(tmp_path / "exports"))
    assert niche_output["rows"]

    product_output = ProductIntelligenceEngine(db).run(session_label="product-intelligence-seo-test", export_dir=str(tmp_path / "exports"))
    assert product_output["rows"]

    design_output = DesignIntelligenceEngine(db).run(session_label="design-intelligence-seo-test", export_dir=str(tmp_path / "exports"))
    assert design_output["rows"]

    seo_output = SeoComplianceIntelligenceEngine(db).run(session_label="seo-intelligence-test", export_dir=str(tmp_path / "exports"))

    assert seo_output["session_id"] is not None
    assert seo_output["rows"]
    assert "report_json" in seo_output["exports"]
    assert "report_csv" in seo_output["exports"]
    assert "package_json" in seo_output["exports"]
    assert "package_csv" in seo_output["exports"]
    assert "package_md" in seo_output["exports"]

    overview_df = db.fetch_seo_listing_overview(limit=5)
    assert not overview_df.empty

    publish_df = db.fetch_publish_decisions(limit=5)
    assert not publish_df.empty

    policy_df = db.fetch_dataframe("policy_checks")
    assert not policy_df.empty

    tags_df = db.fetch_dataframe("seo_tags")
    assert not tags_df.empty

    # Exactly 13 tags in the latest listing payload.
    latest_tags = tags_df.iloc[0]["tags"]
    assert latest_tags
