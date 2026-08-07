from __future__ import annotations

from product_intelligence.models import ProfitAnalysis
from product_intelligence.pricing import suggest_selling_price


def analyze_profit(
    typical_retail_price: float,
    production_cost: float,
    demand_signal: float,
    trend_signal: float,
) -> ProfitAnalysis:
    selling_price = suggest_selling_price(typical_retail_price, demand_signal, trend_signal)
    gross_profit = selling_price - production_cost
    margin_percent = (gross_profit / selling_price * 100.0) if selling_price > 0 else 0.0

    discount_min = round(max(0.0, selling_price * 0.05), 2)
    discount_max = round(max(discount_min, selling_price * 0.18), 2)

    return ProfitAnalysis(
        suggested_selling_price=round(selling_price, 2),
        estimated_production_cost=round(production_cost, 2),
        estimated_gross_profit=round(gross_profit, 2),
        estimated_margin_percent=round(margin_percent, 2),
        suggested_discount_min=discount_min,
        suggested_discount_max=discount_max,
    )
