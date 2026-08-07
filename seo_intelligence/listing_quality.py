from __future__ import annotations

from typing import Any


def evaluate_listing_quality(
    *,
    title: str,
    description: str,
    tags: list[str],
    design_score: float,
    product_score: float,
    intent_confidence: float,
) -> dict[str, float]:
    """Estimate quality metrics for listing readiness."""

    seo_score = min(100.0, 35.0 + len(title) * 0.25 + len(tags) * 2.0)
    readability_score = min(100.0, 35.0 + min(len(description), 1200) / 18.0)
    commercial_score = min(100.0, product_score * 0.45 + design_score * 0.35 + 15.0)
    buyer_intent_score = min(100.0, intent_confidence)
    gift_score = min(100.0, 30.0 + (15.0 if "gift" in " ".join(tags).lower() else 0.0) + intent_confidence * 0.4)
    visual_compatibility_score = min(100.0, design_score * 0.9 + 8.0)
    competition_score = max(0.0, 100.0 - min(80.0, len(tags) * 2.0))
    originality_score = max(0.0, 70.0 + (5.0 if len(set(tags)) == len(tags) else -8.0))
    expected_conversion_score = min(100.0, (commercial_score + buyer_intent_score + readability_score) / 3.0)
    trust_score = min(100.0, 55.0 + readability_score * 0.3)

    return {
        "seo_score": round(seo_score, 2),
        "commercial_score": round(commercial_score, 2),
        "buyer_intent_score": round(buyer_intent_score, 2),
        "gift_score": round(gift_score, 2),
        "readability_score": round(readability_score, 2),
        "visual_compatibility_score": round(visual_compatibility_score, 2),
        "competition_score": round(competition_score, 2),
        "originality_score": round(originality_score, 2),
        "expected_conversion_score": round(expected_conversion_score, 2),
        "trust_score": round(trust_score, 2),
    }
