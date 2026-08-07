from __future__ import annotations

from typing import Any


def analyze_competitor_gap(*, competition_score: float, product_score: float, design_score: float, originality_score: float) -> dict[str, Any]:
    """Estimate whether the product can stand out and what needs improvement."""

    gap = max(0.0, 100.0 - competition_score)
    stand_out = min(100.0, gap * 0.35 + product_score * 0.25 + design_score * 0.2 + originality_score * 0.2)

    if stand_out >= 75:
        verdict = "Strong differentiation"
        improvements = ["Keep the current concept direction", "Maintain distinct title and design language"]
    elif stand_out >= 55:
        verdict = "Moderate differentiation"
        improvements = ["Strengthen visual uniqueness", "Improve niche-specific messaging"]
    else:
        verdict = "Weak differentiation"
        improvements = ["Change the angle or niche hook", "Reduce generic keywords", "Increase visual distinctiveness"]

    return {
        "can_stand_out": stand_out >= 60,
        "why": verdict,
        "stand_out_score": round(stand_out, 2),
        "improvements": improvements,
    }
