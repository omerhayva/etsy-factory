from __future__ import annotations

from typing import Any


def calculate_commercial_score(
    *,
    commercial_potential: float,
    buyer_intent: float,
    gift_potential: float,
    emotional_appeal: float,
    visual_appeal: float,
    originality: float,
    competition_strength: float,
    pricing_logic: float,
    estimated_profit: float,
    seasonal_fit: float,
    evergreen_potential: float,
    brand_potential: float,
) -> dict[str, float]:
    """Aggregate commercial viability into a publish-oriented scorecard."""

    commercial_score = (
        commercial_potential * 0.16
        + buyer_intent * 0.10
        + gift_potential * 0.10
        + emotional_appeal * 0.08
        + visual_appeal * 0.08
        + originality * 0.10
        + competition_strength * 0.06
        + pricing_logic * 0.10
        + estimated_profit * 0.12
        + seasonal_fit * 0.05
        + evergreen_potential * 0.07
        + brand_potential * 0.08
    )
    confidence_score = min(100.0, max(0.0, (buyer_intent + originality + pricing_logic + estimated_profit) / 4.0))
    risk_score = max(0.0, 100.0 - commercial_score + max(0.0, 50.0 - originality) * 0.35)

    if commercial_score >= 82:
        success = "High"
    elif commercial_score >= 68:
        success = "Moderate"
    elif commercial_score >= 55:
        success = "Low"
    else:
        success = "Very Low"

    return {
        "commercial_score": round(min(100.0, max(0.0, commercial_score)), 2),
        "confidence_score": round(confidence_score, 2),
        "risk_score": round(min(100.0, risk_score), 2),
        "estimated_success_level": success,
    }
