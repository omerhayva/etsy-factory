from __future__ import annotations

from product_intelligence.models import ProductCatalogItem, RiskAnalysis


def analyze_risk(product: ProductCatalogItem, seasonal: bool) -> RiskAnalysis:
    return_risk = min(100.0, product.return_risk)
    complaint_risk = min(100.0, product.customization_difficulty * 0.6 + product.return_risk * 0.5)
    sizing_issue = min(100.0, product.return_risk * 1.1) if product.category == "APPAREL" else 8.0
    fragility = min(100.0, product.shipping_complexity * 1.1)
    seasonality_risk = 64.0 if seasonal and product.category != "SEASONAL" else (35.0 if seasonal else 22.0)

    return RiskAnalysis(
        return_risk=round(return_risk, 2),
        complaint_risk=round(complaint_risk, 2),
        sizing_issue_risk=round(sizing_issue, 2),
        fragility_risk=round(fragility, 2),
        seasonality_risk=round(seasonality_risk, 2),
    )
