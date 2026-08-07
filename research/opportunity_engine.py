from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OpportunityInput:
    demand: float
    competition: float
    profit_potential: float
    trend: float
    gift_potential: float
    design_simplicity: float
    data_points: int


@dataclass(slots=True)
class OpportunityResult:
    opportunity_score: int
    confidence_score: int
    reasoning: str


class OpportunityEngine:
    """Scores niche opportunities with weighted market intelligence signals."""

    WEIGHTS = {
        "demand": 0.30,
        "competition": 0.20,
        "profit_potential": 0.20,
        "trend": 0.15,
        "gift_potential": 0.10,
        "design_simplicity": 0.05,
    }

    def score(self, payload: OpportunityInput) -> OpportunityResult:
        competition_advantage = max(0.0, 100.0 - payload.competition)
        raw_score = (
            payload.demand * self.WEIGHTS["demand"]
            + competition_advantage * self.WEIGHTS["competition"]
            + payload.profit_potential * self.WEIGHTS["profit_potential"]
            + payload.trend * self.WEIGHTS["trend"]
            + payload.gift_potential * self.WEIGHTS["gift_potential"]
            + payload.design_simplicity * self.WEIGHTS["design_simplicity"]
        )

        opportunity_score = int(max(0, min(100, round(raw_score))))
        confidence = int(max(30, min(100, round(45 + payload.data_points * 4))))

        reasoning = (
            f"Demand={payload.demand:.1f}, Competition={payload.competition:.1f}, "
            f"Profit={payload.profit_potential:.1f}, Trend={payload.trend:.1f}, "
            f"Gift={payload.gift_potential:.1f}, Simplicity={payload.design_simplicity:.1f}."
        )
        return OpportunityResult(opportunity_score=opportunity_score, confidence_score=confidence, reasoning=reasoning)
