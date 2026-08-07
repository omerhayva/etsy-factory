from __future__ import annotations

from niche_intelligence.models import SeasonalityAnalysis


SEASON_MAP = {
    "New Year": ["new year"],
    "Valentine": ["valentine", "love"],
    "Ramadan": ["ramadan"],
    "Eid": ["eid"],
    "Mother's Day": ["mother", "mom"],
    "Father's Day": ["father", "dad"],
    "Graduation": ["graduation", "graduate"],
    "Halloween": ["halloween", "spooky"],
    "Thanksgiving": ["thanksgiving", "turkey"],
    "Christmas": ["christmas", "xmas", "santa"],
    "Wedding Season": ["wedding", "bride", "groom"],
    "Summer": ["summer", "beach", "vacation"],
    "Back to School": ["school", "teacher", "classroom"],
}


def analyze_seasonality(niche_name: str) -> SeasonalityAnalysis:
    lowered = niche_name.lower()
    matched = [name for name, terms in SEASON_MAP.items() if any(term in lowered for term in terms)]
    if not matched:
        return SeasonalityAnalysis(niche_name=niche_name, seasonal=False, seasons=[], confidence=65.0)
    confidence = min(95.0, 55.0 + len(matched) * 12.0)
    return SeasonalityAnalysis(niche_name=niche_name, seasonal=True, seasons=matched, confidence=confidence)
