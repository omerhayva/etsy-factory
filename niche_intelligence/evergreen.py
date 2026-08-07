from __future__ import annotations

from niche_intelligence.models import EvergreenAnalysis


def analyze_evergreen(niche_name: str, trend_score: float | None, seasonal: bool) -> EvergreenAnalysis:
    lowered = niche_name.lower()

    if any(term in lowered for term in ["halloween", "christmas", "ramadan", "eid", "valentine"]):
        return EvergreenAnalysis(niche_name=niche_name, classification="Seasonal", confidence=88.0)
    if trend_score is None:
        return EvergreenAnalysis(niche_name=niche_name, classification="Temporary", confidence=45.0)
    if trend_score < 35:
        return EvergreenAnalysis(niche_name=niche_name, classification="Declining", confidence=70.0)
    if seasonal:
        return EvergreenAnalysis(niche_name=niche_name, classification="Seasonal", confidence=74.0)
    if trend_score >= 70:
        return EvergreenAnalysis(niche_name=niche_name, classification="Trending", confidence=78.0)
    return EvergreenAnalysis(niche_name=niche_name, classification="Evergreen", confidence=80.0)
