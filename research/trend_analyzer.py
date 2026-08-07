from __future__ import annotations

from dataclasses import dataclass

from database.db import EtsyDatabase


@dataclass(slots=True)
class TrendAnalysis:
    trend_status: str
    trend_score: float


class TrendAnalyzer:
    """Analyzes trend movement and persists historical snapshots."""

    def __init__(self, db: EtsyDatabase):
        self.db = db

    def classify(self, score: float | None) -> TrendAnalysis:
        if score is None:
            return TrendAnalysis(trend_status="Unknown", trend_score=40.0)
        if score >= 70:
            return TrendAnalysis(trend_status="Growing", trend_score=score)
        if score <= 35:
            return TrendAnalysis(trend_status="Declining", trend_score=score)
        return TrendAnalysis(trend_status="Stable", trend_score=score)

    def store(
        self,
        session_id: int,
        niche_name: str,
        keyword: str,
        source: str,
        score: float | None,
    ) -> TrendAnalysis:
        trend = self.classify(score)
        self.db.save_trend_history(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "keyword": keyword,
                "trend_status": trend.trend_status,
                "trend_score": trend.trend_score,
                "source": source,
            }
        )
        return trend
