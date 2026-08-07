from __future__ import annotations


def recommend_mockups(*, product_name: str, audience_tags: list[str], seasonal: bool) -> list[dict[str, str | int]]:
    """Recommend mockup types by product and audience context."""

    product = product_name.lower()
    audience = " ".join(audience_tags).lower()

    choices = [
        "Lifestyle",
        "Studio",
        "Flat Lay",
        "Outdoor",
        "Holiday",
        "Office",
        "Home",
        "Gift Scene",
    ]

    ranked: list[tuple[str, str]] = []
    for option in choices:
        reason = "General conversion-safe mockup"
        if option == "Lifestyle" and any(token in product for token in ["shirt", "hoodie", "hat", "cap"]):
            reason = "Wearable products convert better with lifestyle scenes"
        if option == "Flat Lay" and any(token in product for token in ["mug", "notebook", "sticker", "ornament"]):
            reason = "Small products need clear scale and detail"
        if option == "Gift Scene" and any(token in audience for token in ["gift", "family", "mom", "dad"]):
            reason = "Audience has high gift intent"
        if option == "Holiday" and seasonal:
            reason = "Seasonal niche should show campaign context"
        if option == "Office" and any(token in product for token in ["notebook", "desk", "calendar", "mouse"]):
            reason = "Product use-case is office environment"
        if option == "Home" and any(token in product for token in ["pillow", "blanket", "canvas", "poster", "doormat"]):
            reason = "Home products need realistic living context"

        ranked.append((option, reason))

    ordered = []
    for priority, (mockup, rationale) in enumerate(ranked[:4], start=1):
        ordered.append({"mockup_type": mockup, "rationale": rationale, "priority": priority})
    return ordered
