from __future__ import annotations

from pathlib import Path

from database.db import EtsyDatabase
from niche_intelligence.engine import NicheIntelligenceEngine
from niche_intelligence.scoring import ScoreComponents, calculate_niche_score, classify_niche


def test_niche_scoring_and_classification_ranges():
    overall, confidence, risk = calculate_niche_score(
        ScoreComponents(
            demand=82,
            competition=35,
            profit=78,
            trend=70,
            gift_potential=76,
            evergreen=80,
            design_simplicity=84,
            confidence_inputs=6,
        )
    )
    classification = classify_niche(overall, confidence)

    assert 0 <= overall <= 100
    assert 0 <= confidence <= 100
    assert risk in {"Low", "Moderate", "Elevated", "High"}
    assert classification in {"Gold", "Silver", "Bronze", "Watchlist", "Avoid"}


def test_niche_intelligence_engine_persists_outputs(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "ni.sqlite3")
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

    engine = NicheIntelligenceEngine(db)
    output = engine.run(session_label="niche-intelligence-test", export_dir=str(tmp_path / "exports"))

    assert output["session_id"] is not None
    assert output["rows"]
    assert "json" in output["exports"]
    assert "csv" in output["exports"]

    top_df = db.fetch_niche_intelligence_top(limit=5)
    assert not top_df.empty

    overview_df = db.fetch_niche_intelligence_overview()
    assert not overview_df.empty
