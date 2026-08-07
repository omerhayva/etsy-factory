from __future__ import annotations

from niche_intelligence.models import NicheScore


def build_recommendation(
    niche_name: str,
    overall_score: int,
    confidence: int,
    classification: str,
    risk_level: str,
    reasons: list[str],
) -> NicheScore:
    if classification == "Gold":
        recommendation = "Scale aggressively"
    elif classification == "Silver":
        recommendation = "Launch and optimize"
    elif classification == "Bronze":
        recommendation = "Test small batches"
    elif classification == "Watchlist":
        recommendation = "Monitor trend shifts"
    else:
        recommendation = "Avoid new investment"

    reasoning = "; ".join(reasons[:6]) if reasons else "Insufficient signal diversity."
    return NicheScore(
        niche_name=niche_name,
        overall_score=overall_score,
        confidence=confidence,
        risk_level=risk_level,
        classification=classification,
        recommendation=recommendation,
        reasoning=reasoning,
    )
