from __future__ import annotations

from dataclasses import dataclass
from statistics import median


@dataclass(slots=True)
class PriceInsights:
    min_price: float
    max_price: float
    avg_price: float
    median_price: float
    recommended_selling_price: float


class PricingAnalyzer:
    """Computes pricing intelligence from competitor product prices."""

    def analyze(self, prices: list[float]) -> PriceInsights:
        valid_prices = [float(value) for value in prices if value is not None]
        if not valid_prices:
            valid_prices = [24.0]

        min_price = min(valid_prices)
        max_price = max(valid_prices)
        avg_price = sum(valid_prices) / len(valid_prices)
        median_price = float(median(valid_prices))
        recommended = round(avg_price * 1.03, 2)

        return PriceInsights(
            min_price=round(min_price, 2),
            max_price=round(max_price, 2),
            avg_price=round(avg_price, 2),
            median_price=round(median_price, 2),
            recommended_selling_price=recommended,
        )
