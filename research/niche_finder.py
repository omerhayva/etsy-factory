from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


DEFAULT_CATEGORIES = [
    "Pets",
    "Camping",
    "Fishing",
    "Christian",
    "Islamic",
    "Family",
    "Teacher",
    "Nurse",
    "Halloween",
    "Christmas",
    "Gaming",
    "Books",
    "Sports",
    "Motivation",
    "Nature",
    "Space",
    "Funny",
    "Minimalist",
    "Vintage",
    "Retro",
]


@dataclass(slots=True)
class NicheCandidate:
    niche_name: str
    category: str
    keyword_count: int


class NicheFinder:
    """Discovers niche candidates and assigns configurable categories."""

    def __init__(self, categories: list[str] | None = None):
        self.categories = categories or DEFAULT_CATEGORIES

    def discover(self, keywords: list[dict]) -> list[NicheCandidate]:
        grouped: dict[tuple[str, str], int] = defaultdict(int)

        for item in keywords:
            keyword = str(item.get("keyword", "")).strip()
            if not keyword:
                continue
            category = self._detect_category(keyword)
            grouped[(keyword, category)] += 1

        candidates = [
            NicheCandidate(niche_name=niche, category=category, keyword_count=count)
            for (niche, category), count in grouped.items()
        ]
        return sorted(candidates, key=lambda x: x.keyword_count, reverse=True)

    def _detect_category(self, keyword: str) -> str:
        lowered = keyword.lower()
        for category in self.categories:
            if category.lower() in lowered:
                return category

        keyword_map = {
            "dog": "Pets",
            "cat": "Pets",
            "camp": "Camping",
            "fish": "Fishing",
            "christ": "Christian",
            "islam": "Islamic",
            "family": "Family",
            "teacher": "Teacher",
            "nurse": "Nurse",
            "halloween": "Halloween",
            "christmas": "Christmas",
            "game": "Gaming",
            "book": "Books",
            "sport": "Sports",
            "motivat": "Motivation",
            "nature": "Nature",
            "space": "Space",
            "funny": "Funny",
            "minimal": "Minimalist",
            "vintage": "Vintage",
            "retro": "Retro",
        }
        for token, category in keyword_map.items():
            if token in lowered and category in self.categories:
                return category

        return "General"
