from __future__ import annotations

INTENT_LABELS = [
    "Gift",
    "Personal",
    "Home Decor",
    "Lifestyle",
    "Holiday",
    "Memorial",
    "Celebration",
    "Humor",
    "Motivation",
    "Education",
]


def classify_buyer_intent(niche_name: str, tags: list[str]) -> dict[str, float | str]:
    """Classify dominant buyer intent from niche and tags."""

    text = f"{niche_name} {' '.join(tags)}".lower()
    scores = {label: 0.0 for label in INTENT_LABELS}

    if any(token in text for token in ["gift", "present", "birthday", "anniversary"]):
        scores["Gift"] += 40
    if any(token in text for token in ["home", "decor", "wall", "canvas", "poster"]):
        scores["Home Decor"] += 35
    if any(token in text for token in ["lifestyle", "daily", "routine", "outdoor"]):
        scores["Lifestyle"] += 28
    if any(token in text for token in ["christmas", "halloween", "easter", "holiday"]):
        scores["Holiday"] += 36
    if any(token in text for token in ["memorial", "remembrance"]):
        scores["Memorial"] += 45
    if any(token in text for token in ["celebration", "party", "wedding"]):
        scores["Celebration"] += 32
    if any(token in text for token in ["funny", "humor", "joke"]):
        scores["Humor"] += 30
    if any(token in text for token in ["motivation", "inspire", "quote"]):
        scores["Motivation"] += 30
    if any(token in text for token in ["teacher", "school", "education"]):
        scores["Education"] += 34

    # Personal intent baseline
    scores["Personal"] += 22

    label = max(scores, key=scores.get)
    confidence = min(100.0, max(scores.values()) + 25.0)
    return {"intent": label, "confidence": round(confidence, 2), "intent_scores": scores}
