from __future__ import annotations

from typing import Any


def validate_pricing(*, suggested_retail_price: float, estimated_profit_margin: float, premium_position: bool, budget_position: bool) -> dict[str, Any]:
    """Validate pricing logic for the product market position."""

    if estimated_profit_margin >= 60:
        pricing_logic = 88.0
    elif estimated_profit_margin >= 45:
        pricing_logic = 74.0
    elif estimated_profit_margin >= 30:
        pricing_logic = 60.0
    else:
        pricing_logic = 42.0

    if premium_position:
        pricing_logic += 6.0
    if budget_position:
        pricing_logic += 2.0

    recommendation = "Premium position" if premium_position else ("Budget position" if budget_position else "Balanced position")

    return {
        "suggested_retail_price": round(suggested_retail_price, 2),
        "estimated_profit_margin": round(estimated_profit_margin, 2),
        "pricing_logic_score": round(min(100.0, pricing_logic), 2),
        "position": recommendation,
    }
