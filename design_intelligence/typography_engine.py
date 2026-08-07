from __future__ import annotations

from typing import Any


def recommend_typography(*, style_name: str, niche_name: str, audience_tags: list[str]) -> dict[str, Any]:
    """Recommend primary/secondary font style and hierarchy."""

    style = style_name.lower()
    text = niche_name.lower()
    audience = " ".join(audience_tags).lower()

    primary = "Sans Serif"
    secondary = "Serif"
    hierarchy = "Bold headline, medium subheadline, compact supporting text"

    if any(token in style for token in ["vintage", "retro", "distressed"]):
        primary = "Vintage"
        secondary = "Sans Serif"
        hierarchy = "Decorative title, clean subtitle, minimal body"
    elif any(token in style for token in ["luxury", "dark academia"]):
        primary = "Serif"
        secondary = "Script"
        hierarchy = "Elegant heading, script accent, restrained body"
    elif any(token in style for token in ["cute", "cartoon", "comic"]):
        primary = "Playful"
        secondary = "Bold"
        hierarchy = "Playful title, bold supporting text"
    elif any(token in style for token in ["minimal", "modern", "scandinavian"]):
        primary = "Minimal"
        secondary = "Sans Serif"
        hierarchy = "Large simple heading, high whitespace, concise subtext"
    elif any(token in style for token in ["botanical", "floral", "watercolor"]):
        primary = "Handwritten"
        secondary = "Serif"
        hierarchy = "Handwritten hero word, serif body"

    if any(token in text for token in ["faith", "christian", "islamic", "wedding"]):
        secondary = "Script"
    if "kids" in audience:
        primary = "Playful"
        secondary = "Sans Serif"

    return {
        "primary_font_style": primary,
        "secondary_font_style": secondary,
        "hierarchy": hierarchy,
        "rationale": f"style={style_name}, audience={audience or 'general'}",
    }
