from __future__ import annotations

from typing import Any


def validate_trend_fit(*, seasonal_fit: float, evergreen_potential: float, trend_signal: float) -> dict[str, Any]:
    """Validate whether the product fits current trend and evergreen demand."""

    trend_score = min(100.0, seasonal_fit * 0.4 + evergreen_potential * 0.4 + trend_signal * 0.2)
    if trend_score >= 75:
        verdict = "Excellent trend fit"
    elif trend_score >= 55:
        verdict = "Acceptable trend fit"
    else:
        verdict = "Weak trend fit"
    return {"trend_fit_score": round(trend_score, 2), "verdict": verdict}
