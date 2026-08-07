from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_PRODUCT_CATALOG = {
    "t-shirt": {"base_price": 24.0, "margin": 0.62, "pod_compatibility": 95, "design_difficulty": 50},
    "hoodie": {"base_price": 42.0, "margin": 0.58, "pod_compatibility": 88, "design_difficulty": 58},
    "mug": {"base_price": 18.0, "margin": 0.67, "pod_compatibility": 96, "design_difficulty": 42},
    "poster": {"base_price": 28.0, "margin": 0.72, "pod_compatibility": 91, "design_difficulty": 46},
    "phone case": {"base_price": 22.0, "margin": 0.55, "pod_compatibility": 86, "design_difficulty": 64},
    "tote bag": {"base_price": 26.0, "margin": 0.60, "pod_compatibility": 90, "design_difficulty": 49},
}


@dataclass(slots=True)
class ProductRecommendation:
    product_name: str
    score: int
    rationale: str


def recommend_product(
    niche: str,
    audience: str,
    season: str,
    competition: int,
    profit: int,
    catalog: dict[str, Any] | None = None,
) -> ProductRecommendation:
    catalog = catalog or DEFAULT_PRODUCT_CATALOG
    niche_lower = niche.lower()
    audience_lower = audience.lower()
    season_lower = season.lower()

    product_scores: dict[str, int] = {}
    for product_name, details in catalog.items():
        score = int(details["pod_compatibility"] * 0.35 + details["margin"] * 100 * 0.25)
        score += int(profit * 0.25)
        score += int((100 - competition) * 0.15)

        if product_name in {"t-shirt", "hoodie"} and any(term in niche_lower for term in ["dog", "cat", "vintage", "lover"]):
            score += 6
        if product_name == "mug" and any(term in audience_lower for term in ["gift", "mom", "dad", "teacher"]):
            score += 8
        if product_name == "poster" and any(term in niche_lower for term in ["astronomy", "wall art", "home decor"]):
            score += 10
        if product_name == "tote bag" and any(term in season_lower for term in ["spring", "summer", "holiday"]):
            score += 4

        product_scores[product_name] = score

    best_product = max(product_scores, key=product_scores.get)
    rationale = f"Best match for {niche} with {audience} demand and {season} seasonality."
    return ProductRecommendation(best_product, min(100, product_scores[best_product]), rationale)
