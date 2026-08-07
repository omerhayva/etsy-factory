from __future__ import annotations

from pathlib import Path

from database.db import EtsyDatabase
from design_intelligence.engine import DesignIntelligenceEngine
from niche_intelligence.engine import NicheIntelligenceEngine
from product_intelligence.engine import ProductIntelligenceEngine


def test_design_intelligence_runs_and_persists_outputs(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "di.sqlite3")
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

    niche_engine = NicheIntelligenceEngine(db)
    niche_output = niche_engine.run(session_label="niche-intelligence-design-test", export_dir=str(tmp_path / "exports"))
    assert niche_output["rows"]

    product_engine = ProductIntelligenceEngine(db)
    product_output = product_engine.run(session_label="product-intelligence-design-test", export_dir=str(tmp_path / "exports"))
    assert product_output["rows"]

    design_engine = DesignIntelligenceEngine(db)
    output = design_engine.run(session_label="design-intelligence-test", export_dir=str(tmp_path / "exports"))

    assert output["session_id"] is not None
    assert output["rows"]
    assert "report_json" in output["exports"]
    assert "report_csv" in output["exports"]
    assert "package_json" in output["exports"]
    assert "package_csv" in output["exports"]
    assert "package_md" in output["exports"]

    overview_df = db.fetch_design_intelligence_overview(limit=10)
    assert not overview_df.empty

    prompt_df = db.fetch_design_prompts(limit=10)
    assert not prompt_df.empty

    variation_df = db.fetch_design_variations(limit=10)
    assert not variation_df.empty

    mockup_df = db.fetch_mockup_recommendations(limit=10)
    assert not mockup_df.empty
