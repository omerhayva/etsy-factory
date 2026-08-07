from __future__ import annotations

from product_intelligence.models import ProductCatalogItem, QualityAnalysis


def analyze_quality(product: ProductCatalogItem, provider_quality_multiplier: float) -> QualityAnalysis:
    design_visibility = min(100.0, product.print_area * 0.92)
    print_expectation = min(100.0, (68.0 + product.popularity * 0.25) * provider_quality_multiplier)
    color_flexibility = min(100.0, 35.0 + product.color_variants * 2.4)
    satisfaction = min(100.0, (design_visibility * 0.30 + print_expectation * 0.40 + color_flexibility * 0.30))

    return QualityAnalysis(
        design_visibility=round(design_visibility, 2),
        print_quality_expectation=round(print_expectation, 2),
        color_flexibility=round(color_flexibility, 2),
        customer_satisfaction_potential=round(satisfaction, 2),
    )
