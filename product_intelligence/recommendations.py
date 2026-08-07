from __future__ import annotations

from product_intelligence.models import ProductScore


def top_ranked_recommendations(scores: list[ProductScore], top_k: int = 4) -> list[ProductScore]:
    ordered = sorted(scores, key=lambda item: item.match_score, reverse=True)
    return ordered[:top_k]


def recommendation_reasons(score: ProductScore, niche_name: str, evergreen_classification: str) -> list[str]:
    reasons = list(score.reasons)
    reasons.append(f"Niche alignment: {niche_name}")
    reasons.append(f"Evergreen profile: {evergreen_classification}")
    return reasons
