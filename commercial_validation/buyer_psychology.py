from __future__ import annotations

from typing import Any


def analyze_buyer_psychology(*, title: str, gift_score: float, emotional_appeal: float, brand_potential: float) -> dict[str, Any]:
    """Estimate click, buy, gift, and favorite behavior."""

    title_text = title.lower()
    click = min(100.0, 30.0 + len(title_text.split()) * 2.0 + emotional_appeal * 0.25 + gift_score * 0.25)
    buy = min(100.0, emotional_appeal * 0.3 + brand_potential * 0.3 + gift_score * 0.25 + 15.0)
    gift = min(100.0, gift_score * 0.7 + emotional_appeal * 0.2 + 10.0)
    fav = min(100.0, (click + buy) / 2.0)

    return {
        "would_click": round(click, 2),
        "would_buy": round(buy, 2),
        "would_gift": round(gift, 2),
        "would_favorite": round(fav, 2),
    }
