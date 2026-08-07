from __future__ import annotations

from niche_intelligence.models import GiftabilityAnalysis


def analyze_giftability(niche_name: str) -> GiftabilityAnalysis:
    lowered = niche_name.lower()

    occasion_map = {
        "Birthday": ["birthday", "bday"],
        "Graduation": ["graduation", "graduate"],
        "Wedding": ["wedding", "bride", "groom"],
        "Christmas": ["christmas", "xmas", "santa"],
        "Mother's Day": ["mom", "mother"],
        "Father's Day": ["dad", "father"],
        "Valentine": ["love", "valentine"],
        "Retirement": ["retirement", "retired"],
    }
    recipient_map = {
        "Dog Owners": ["dog", "puppy"],
        "Cat Owners": ["cat", "kitten"],
        "Teachers": ["teacher", "school"],
        "Nurses": ["nurse", "medical"],
        "Gamers": ["game", "gaming"],
        "Parents": ["mom", "dad", "parent"],
        "Couples": ["couple", "love", "wedding"],
    }

    occasions = [name for name, terms in occasion_map.items() if any(term in lowered for term in terms)]
    recipients = [name for name, terms in recipient_map.items() if any(term in lowered for term in terms)]

    suitability = 45.0
    if "gift" in lowered:
        suitability += 25.0
    suitability += min(20.0, len(occasions) * 7.0)
    suitability += min(10.0, len(recipients) * 3.0)
    suitability = max(0.0, min(100.0, suitability))

    confidence = 50.0 + min(45.0, len(occasions) * 8.0 + len(recipients) * 4.0)

    return GiftabilityAnalysis(
        niche_name=niche_name,
        suitability=suitability,
        occasions=occasions or ["General Gifting"],
        recipients=recipients or ["General Audience"],
        confidence=confidence,
    )
