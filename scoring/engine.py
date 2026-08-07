from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OpportunityScores:
    demand: int
    competition: int
    profit: int
    design_potential: int
    trend: int


def clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def score_opportunity(scores: OpportunityScores | dict[str, int]) -> int:
    if isinstance(scores, dict):
        scores = OpportunityScores(**scores)

    demand_component = scores.demand * 0.30
    competition_component = (100 - scores.competition) * 0.20
    profit_component = scores.profit * 0.25
    design_component = scores.design_potential * 0.15
    trend_component = scores.trend * 0.10
    return clamp_score(demand_component + competition_component + profit_component + design_component + trend_component)
