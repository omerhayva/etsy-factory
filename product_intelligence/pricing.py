from __future__ import annotations


def suggest_selling_price(typical_retail_price: float, demand_signal: float, trend_signal: float) -> float:
    demand_boost = (demand_signal - 50.0) / 500.0
    trend_boost = (trend_signal - 50.0) / 500.0
    multiplier = 1.0 + demand_boost + trend_boost
    return round(max(typical_retail_price * 0.85, typical_retail_price * multiplier), 2)
