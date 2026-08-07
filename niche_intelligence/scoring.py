from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ScoreComponents:
    demand: float
    competition: float
    profit: float
    trend: float
    gift_potential: float
    evergreen: float
    design_simplicity: float
    confidence_inputs: int


def _clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    return max(min_value, min(max_value, value))


def calculate_niche_score(components: ScoreComponents) -> tuple[int, int, str]:
    competition_advantage = _clamp(100.0 - components.competition)
    overall = (
        _clamp(components.demand) * 0.25
        + competition_advantage * 0.20
        + _clamp(components.profit) * 0.20
        + _clamp(components.trend) * 0.15
        + _clamp(components.gift_potential) * 0.10
        + _clamp(components.evergreen) * 0.05
        + _clamp(components.design_simplicity) * 0.05
    )
    overall_score = int(round(_clamp(overall)))

    confidence = int(round(_clamp(35 + components.confidence_inputs * 7)))

    if overall_score >= 85:
        risk = "Low"
    elif overall_score >= 70:
        risk = "Moderate"
    elif overall_score >= 55:
        risk = "Elevated"
    else:
        risk = "High"

    return overall_score, confidence, risk


def classify_niche(overall_score: int, confidence: int) -> str:
    if overall_score >= 88 and confidence >= 70:
        return "Gold"
    if overall_score >= 74:
        return "Silver"
    if overall_score >= 60:
        return "Bronze"
    if overall_score >= 45:
        return "Watchlist"
    return "Avoid"
