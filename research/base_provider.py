from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class KeywordRecord:
    keyword: str
    source: str
    language: str = "en"
    search_volume: int | None = None
    competition: float | None = None
    trend: str | None = None
    status: str = "active"


@dataclass(slots=True)
class CompetitorRecord:
    shop_name: str
    product_title: str
    price: float
    estimated_popularity: float
    review_count: int
    favorite_count: int | None = None
    product_age_days: int | None = None
    store_category: str | None = None
    data_source: str = "unknown"


@dataclass(slots=True)
class TrendRecord:
    keyword: str
    trend_score: float
    trend_status: str
    source: str


class BaseResearchProvider(ABC):
    """Provider abstraction to plug different research data sources into the same core workflow."""

    name: str = "base"

    @abstractmethod
    def collect_keywords(self, seed: str, limit: int = 20) -> list[KeywordRecord]:
        raise NotImplementedError

    @abstractmethod
    def collect_competitors(self, seed: str, limit: int = 20) -> list[CompetitorRecord]:
        raise NotImplementedError

    @abstractmethod
    def collect_trends(self, seed: str, keywords: list[str]) -> list[TrendRecord]:
        raise NotImplementedError
