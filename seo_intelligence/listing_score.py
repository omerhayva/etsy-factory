from __future__ import annotations


def calculate_overall_listing_score(*, quality: dict[str, float], compliance_score: float, spam_score: float) -> dict[str, float]:
    """Compute unified listing scorecard."""

    overall = (
        quality["seo_score"] * 0.12
        + compliance_score * 0.16
        + quality["commercial_score"] * 0.10
        + quality["buyer_intent_score"] * 0.09
        + quality["gift_score"] * 0.07
        + quality["readability_score"] * 0.08
        + quality["visual_compatibility_score"] * 0.08
        + quality["competition_score"] * 0.07
        + quality["originality_score"] * 0.07
        + quality["expected_conversion_score"] * 0.08
        + quality["trust_score"] * 0.08
        + spam_score * 0.10
    )

    return {
        "overall_listing_score": round(overall, 2),
        "compliance_score": round(compliance_score, 2),
        "spam_score": round(spam_score, 2),
    }
