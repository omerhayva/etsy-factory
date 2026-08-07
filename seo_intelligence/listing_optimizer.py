from __future__ import annotations

from typing import Any


def optimize_listing(
    *,
    title_versions: list[str],
    description: str,
    tags: list[str],
    keyword_categories: dict[str, list[str]],
    buyer_intent: dict[str, Any],
) -> dict[str, Any]:
    """Select best candidate pieces for final listing package."""

    best_title = max(title_versions, key=lambda item: len(item)) if title_versions else ""

    # Prefer keyword-rich but readable title.
    if title_versions:
        ranked = sorted(
            title_versions,
            key=lambda item: (sum(1 for token in keyword_categories.get("primary", []) if token in item.lower()), -abs(len(item) - 120)),
            reverse=True,
        )
        best_title = ranked[0]

    return {
        "title": best_title,
        "title_versions": title_versions,
        "description": description,
        "tags": tags,
        "intent": buyer_intent.get("intent", "Personal"),
        "intent_confidence": buyer_intent.get("confidence", 50.0),
    }
