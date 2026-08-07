from __future__ import annotations

from typing import Any


def validate_gift_potential(*, niche_name: str, buyer_intent: str, gift_score: float) -> dict[str, Any]:
    """Evaluate giftworthiness for the candidate."""

    reason = "Strong gift suitability" if gift_score >= 70 else ("Moderate gift suitability" if gift_score >= 50 else "Weak gift suitability")
    return {"gift_potential_score": round(gift_score, 2), "reason": reason, "gift_fit": buyer_intent == "Gift" or gift_score >= 60}
