from __future__ import annotations

from product_intelligence.models import ProductCatalogItem, ShippingAnalysis


def analyze_shipping(product: ProductCatalogItem) -> ShippingAnalysis:
    damage_risk = min(100.0, product.return_risk * 0.6 + product.shipping_complexity * 0.7)
    international = max(0.0, 100.0 - product.shipping_complexity * 0.9)

    return ShippingAnalysis(
        shipping_difficulty=round(product.shipping_complexity, 2),
        packaging_complexity=round(product.shipping_complexity * 0.9, 2),
        damage_risk=round(damage_risk, 2),
        international_suitability=round(international, 2),
    )
