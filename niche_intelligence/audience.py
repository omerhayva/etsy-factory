from __future__ import annotations

from niche_intelligence.models import AudienceAnalysis


AUDIENCE_KEYWORDS = {
    "Dog Owners": ["dog", "puppy", "canine"],
    "Cat Owners": ["cat", "kitten", "feline"],
    "Teachers": ["teacher", "school", "classroom"],
    "Nurses": ["nurse", "rn", "medical"],
    "Gamers": ["game", "gamer", "gaming"],
    "Campers": ["camp", "camping", "outdoor"],
    "Mothers": ["mom", "mother", "mama"],
    "Fathers": ["dad", "father", "papa"],
    "Grandparents": ["grandma", "grandpa", "grandparent"],
    "Christians": ["christian", "jesus", "bible"],
    "Muslims": ["muslim", "islam", "allah", "ramadan", "eid"],
    "Book Lovers": ["book", "reader", "library"],
    "Fitness": ["fitness", "gym", "workout"],
    "Fishing": ["fishing", "fish", "angler"],
    "Cars": ["car", "auto"],
    "Motorcycles": ["motorcycle", "biker"],
    "Children": ["kid", "child", "children"],
    "Baby Gifts": ["baby", "newborn"],
    "Couples": ["couple", "anniversary"],
    "Wedding": ["wedding", "bride", "groom"],
    "Graduation": ["graduation", "graduate"],
    "Birthday": ["birthday", "bday"],
    "Retirement": ["retirement", "retired"],
}


def analyze_audience(niche_name: str) -> AudienceAnalysis:
    lowered = niche_name.lower()
    audiences = [name for name, terms in AUDIENCE_KEYWORDS.items() if any(term in lowered for term in terms)]

    buyer_intents: list[str] = []
    if any(term in lowered for term in ["gift", "birthday", "wedding", "graduation", "retirement"]):
        buyer_intents.append("Gift Purchase")
    if any(term in lowered for term in ["christmas", "halloween", "ramadan", "eid", "summer", "school"]):
        buyer_intents.append("Seasonal Purchase")
    if any(term in lowered for term in ["collectible", "limited", "exclusive"]):
        buyer_intents.append("Collectible")
    if any(term in lowered for term in ["hobby", "gaming", "fishing", "camping", "book"]):
        buyer_intents.append("Hobby")
    if any(term in lowered for term in ["minimal", "lifestyle", "fitness", "retro", "vintage"]):
        buyer_intents.append("Lifestyle")
    if not buyer_intents:
        buyer_intents.append("Personal Purchase")
    if "funny" in lowered:
        buyer_intents.append("Impulse Purchase")

    if not audiences:
        audiences = ["General Audience"]

    return AudienceAnalysis(niche_name=niche_name, audiences=audiences, buyer_intents=sorted(set(buyer_intents)))
