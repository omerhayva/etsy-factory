from __future__ import annotations

from dataclasses import asdict

from database.db import EtsyDatabase
from research.base_provider import BaseResearchProvider, KeywordRecord
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


class KeywordCollector:
    """Collects and persists keyword intelligence from one or multiple providers."""

    def __init__(self, db: EtsyDatabase):
        self.db = db

    def collect(
        self,
        seed: str,
        providers: list[BaseResearchProvider],
        session_id: int | None = None,
        limit_per_provider: int = 20,
    ) -> list[dict]:
        seen: set[tuple[str, str]] = set()
        collected: list[dict] = []

        for provider in providers:
            try:
                records = provider.collect_keywords(seed, limit=limit_per_provider)
            except Exception as exc:
                LOGGER.exception("Keyword collection failed for provider %s", provider.name)
                continue

            for record in records:
                key = (record.keyword.lower(), record.source)
                if key in seen:
                    continue
                seen.add(key)

                row = {
                    "niche_name": seed,
                    "keyword": record.keyword,
                    "source": record.source,
                    "language": record.language,
                    "search_volume": record.search_volume,
                    "competition": record.competition,
                    "trend": record.trend,
                    "status": record.status,
                    "score": 0,
                }
                self.db.save_keyword(row)
                self.db.save_keyword_metric(
                    {
                        "keyword": record.keyword,
                        "source": record.source,
                        "search_volume": record.search_volume,
                        "competition": record.competition,
                        "trend_score": self._trend_to_score(record.trend),
                        "status": record.status,
                    }
                )
                normalized = asdict(record)
                normalized["session_id"] = session_id
                collected.append(normalized)

        return collected

    @staticmethod
    def _trend_to_score(trend: str | None) -> float:
        mapping = {
            "growing": 80.0,
            "stable": 55.0,
            "declining": 25.0,
            "unknown": 40.0,
        }
        if not trend:
            return mapping["unknown"]
        return mapping.get(trend.lower(), mapping["unknown"])
