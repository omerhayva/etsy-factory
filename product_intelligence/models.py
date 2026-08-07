from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProductCatalogItem:
    name: str
    category: str
    subcategory: str
    typical_retail_price: float
    estimated_production_cost: float
    estimated_profit_margin: float
    popularity: float
    gift_potential: float
    customization_difficulty: float
    shipping_complexity: float
    average_processing_time: float
    return_risk: float
    print_area: float
    color_variants: int


@dataclass(slots=True)
class ProductMatchInput:
    niche_name: str
    audiences: list[str]
    season_labels: list[str]
    competition_score: float
    gift_intent: float
    trend_score: float
    evergreen_score: float


@dataclass(slots=True)
class ProductScore:
    product_name: str
    provider: str
    match_score: float
    reasons: list[str]


@dataclass(slots=True)
class ProfitAnalysis:
    suggested_selling_price: float
    estimated_production_cost: float
    estimated_gross_profit: float
    estimated_margin_percent: float
    suggested_discount_min: float
    suggested_discount_max: float


@dataclass(slots=True)
class ShippingAnalysis:
    shipping_difficulty: float
    packaging_complexity: float
    damage_risk: float
    international_suitability: float


@dataclass(slots=True)
class QualityAnalysis:
    design_visibility: float
    print_quality_expectation: float
    color_flexibility: float
    customer_satisfaction_potential: float


@dataclass(slots=True)
class RiskAnalysis:
    return_risk: float
    complaint_risk: float
    sizing_issue_risk: float
    fragility_risk: float
    seasonality_risk: float
