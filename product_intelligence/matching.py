from __future__ import annotations

from product_intelligence.models import ProductCatalogItem, ProductMatchInput, ProductScore


def match_product(input_row: ProductMatchInput, product: ProductCatalogItem, provider: str) -> ProductScore:
    seasonal_bonus = 0.0
    if input_row.season_labels and product.category == "SEASONAL":
        seasonal_bonus = 12.0
    elif input_row.season_labels and product.category in {"APPAREL", "ACCESSORIES"}:
        seasonal_bonus = 6.0

    gift_alignment = (input_row.gift_intent * 0.35 + product.gift_potential * 0.65)
    competition_advantage = max(0.0, 100.0 - input_row.competition_score)
    trend_alignment = (input_row.trend_score * 0.6 + input_row.evergreen_score * 0.4)
    customization_penalty = max(0.0, product.customization_difficulty * 0.2)
    shipping_penalty = max(0.0, product.shipping_complexity * 0.15)

    score = (
        product.popularity * 0.26
        + gift_alignment * 0.20
        + competition_advantage * 0.16
        + trend_alignment * 0.16
        + product.estimated_profit_margin * 0.14
        + product.print_area * 0.08
        + seasonal_bonus
        - customization_penalty
        - shipping_penalty
    )
    score = max(0.0, min(100.0, score))

    reasons = [
        f"Popularity {product.popularity:.1f}",
        f"Gift alignment {gift_alignment:.1f}",
        f"Competition advantage {competition_advantage:.1f}",
        f"Profit margin {product.estimated_profit_margin:.1f}",
    ]
    if seasonal_bonus > 0:
        reasons.append("Seasonal relevance")

    return ProductScore(product_name=product.name, provider=provider, match_score=round(score, 2), reasons=reasons)
