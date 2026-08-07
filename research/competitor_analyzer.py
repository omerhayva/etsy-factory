from __future__ import annotations

from dataclasses import asdict

from database.db import EtsyDatabase
from research.base_provider import CompetitorRecord


class CompetitorAnalyzer:
    """Normalizes competitor data and writes comparable market snapshots."""

    def __init__(self, db: EtsyDatabase):
        self.db = db

    def persist(
        self,
        session_id: int,
        niche_name: str,
        competitors: list[CompetitorRecord],
    ) -> list[dict]:
        rows: list[dict] = []
        for item in competitors:
            row = asdict(item)
            row["session_id"] = session_id
            row["niche_name"] = niche_name
            self.db.save_competitor(row)
            rows.append(row)
        return rows
