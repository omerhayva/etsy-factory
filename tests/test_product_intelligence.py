from __future__ import annotations

from pathlib import Path

from database.db import EtsyDatabase
from niche_intelligence.engine import NicheIntelligenceEngine
from product_intelligence.engine import ProductIntelligenceEngine


def test_product_intelligence_engine_persists_outputs(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "pi.sqlite3")
    db.initialize()

    db.save_niche(
        {
            "niche_name": "vintage camping gift",
            "demand_score": 84,
            "competition_score": 42,
            "profit_potential": 79,
            "design_difficulty": 30,
            "pod_compatibility": 91,
            "opportunity_score": 86,
            "market_data": [],
            "category": "Camping",
            "source": "test",
            "status": "active",
            "confidence_score": 76,
            "reasoning": "seed",
            "session_id": 1,
        }
    )

    niche_engine = NicheIntelligenceEngine(db)
    niche_output = niche_engine.run(session_label="niche-intelligence-product-test", export_dir=str(tmp_path / "exports"))
    assert niche_output["session_id"] is not None
    assert niche_output["rows"]

    product_engine = ProductIntelligenceEngine(db)
    output = product_engine.run(session_label="product-intelligence-test", export_dir=str(tmp_path / "exports"))

    assert output["session_id"] is not None
    assert output["rows"]
    assert "json" in output["exports"]
    assert "csv" in output["exports"]
    assert "recommendations_json" in output["exports"]
    assert "recommendations_csv" in output["exports"]

    rec_df = db.fetch_product_intelligence_recommendations(limit=5)
    assert not rec_df.empty

    profit_df = db.fetch_product_profit_overview(limit=5)
    assert not profit_df.empty

    risk_df = db.fetch_product_low_risk(limit=5)
    assert not risk_df.empty
