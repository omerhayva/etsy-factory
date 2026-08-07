from __future__ import annotations

from pathlib import Path

from database.db import EtsyDatabase
from research.base_provider import BaseResearchProvider, CompetitorRecord, KeywordRecord, TrendRecord
from research.opportunity_engine import OpportunityEngine, OpportunityInput
from research.research_manager import ResearchManager
from research.trend_analyzer import TrendAnalyzer


class FakeProvider(BaseResearchProvider):
    name = "fake_provider"

    def collect_keywords(self, seed: str, limit: int = 20) -> list[KeywordRecord]:
        return [
            KeywordRecord(keyword=f"{seed} vintage gift", source=self.name, search_volume=1800, competition=35.0, trend="growing"),
            KeywordRecord(keyword=f"{seed} minimalist", source=self.name, search_volume=900, competition=42.0, trend="stable"),
        ][:limit]

    def collect_competitors(self, seed: str, limit: int = 20) -> list[CompetitorRecord]:
        return [
            CompetitorRecord(
                shop_name="shop_one",
                product_title=f"{seed} gift shirt",
                price=24.0,
                estimated_popularity=78.0,
                review_count=140,
                favorite_count=30,
                product_age_days=120,
                store_category="Pets",
                data_source=self.name,
            ),
            CompetitorRecord(
                shop_name="shop_two",
                product_title=f"{seed} retro tee",
                price=27.0,
                estimated_popularity=74.0,
                review_count=110,
                favorite_count=20,
                product_age_days=95,
                store_category="Pets",
                data_source=self.name,
            ),
        ][:limit]

    def collect_trends(self, seed: str, keywords: list[str]) -> list[TrendRecord]:
        return [TrendRecord(keyword=keywords[0], trend_score=75.0, trend_status="Growing", source=self.name)]


def test_opportunity_engine_returns_expected_range():
    engine = OpportunityEngine()
    result = engine.score(
        OpportunityInput(
            demand=80,
            competition=40,
            profit_potential=70,
            trend=75,
            gift_potential=68,
            design_simplicity=85,
            data_points=12,
        )
    )
    assert 0 <= result.opportunity_score <= 100
    assert 0 <= result.confidence_score <= 100
    assert "Demand" in result.reasoning


def test_trend_analyzer_classification_and_storage(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "trend.sqlite3")
    db.initialize()
    analyzer = TrendAnalyzer(db)

    trend = analyzer.store(session_id=1, niche_name="vintage pets", keyword="vintage pets", source="fake", score=72.0)
    assert trend.trend_status == "Growing"

    trend_df = db.fetch_dataframe("trend_history")
    assert not trend_df.empty
    assert trend_df.iloc[0]["trend_status"] == "Growing"


def test_research_manager_runs_end_to_end_and_persists_outputs(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "research.sqlite3")
    db.initialize()

    manager = ResearchManager(
        db=db,
        providers=[FakeProvider()],
        categories=["Pets", "Vintage", "Retro"],
    )

    export_dir = tmp_path / "exports"
    result = manager.run_session(
        seed_terms=["dog lover"],
        session_label="test-session",
        export_dir=str(export_dir),
    )

    assert result["session_id"] > 0
    assert result["opportunities"]
    assert "json" in result["exports"]
    assert "csv" in result["exports"]

    sessions = db.fetch_dataframe("research_sessions")
    assert not sessions.empty
    assert sessions.iloc[0]["status"] == "completed"

    keyword_overview = db.fetch_keyword_overview(limit=5)
    assert not keyword_overview.empty
