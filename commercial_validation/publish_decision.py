from __future__ import annotations

from typing import Any


def decide_publish(*, commercial_score: float, risk_score: float, confidence_score: float) -> dict[str, Any]:
    """Return the only allowed final publish decision."""

    if commercial_score >= 70 and risk_score <= 40 and confidence_score >= 50:
        return {"decision": "READY FOR PUBLISH", "reasons": [], "recommendations": [], "priority_level": "low"}

    reasons: list[str] = []
    recommendations: list[str] = []

    if commercial_score < 70:
        reasons.append("Commercial score is below publish threshold")
        recommendations.append("Improve niche/product fit and commercial appeal")
    if risk_score > 40:
        reasons.append("Risk score is too high")
        recommendations.append("Reduce policy, originality, or differentiation risk")
    if confidence_score < 50:
        reasons.append("Confidence score is too low")
        recommendations.append("Increase evidence from upstream modules")

    priority = "critical" if risk_score >= 70 else ("high" if commercial_score < 55 else "medium")
    return {"decision": "NEEDS IMPROVEMENT", "reasons": reasons[:5], "recommendations": recommendations[:5], "priority_level": priority}
