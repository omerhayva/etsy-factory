from __future__ import annotations

from typing import Any


PALETTES: dict[str, dict[str, list[str] | str]] = {
    "Monochrome": {"primary": ["#111111"], "secondary": ["#EDEDED"], "accent": ["#666666"]},
    "Pastel": {"primary": ["#F4C2C2", "#C2E9FB"], "secondary": ["#F7E7CE"], "accent": ["#D4A5A5"]},
    "Earth Tone": {"primary": ["#7B5E57", "#A47148"], "secondary": ["#D9C3A5"], "accent": ["#4E6E58"]},
    "Vintage Palette": {"primary": ["#8C6A5D", "#C9A47A"], "secondary": ["#E5D0B1"], "accent": ["#5A4632"]},
    "High Contrast": {"primary": ["#000000", "#FFFFFF"], "secondary": ["#F4C300"], "accent": ["#FF0054"]},
    "Muted Colors": {"primary": ["#6B7A8F", "#8DA399"], "secondary": ["#C7D3DD"], "accent": ["#9C8E7B"]},
    "Luxury Palette": {"primary": ["#1F1A17", "#D4AF37"], "secondary": ["#F5E8C7"], "accent": ["#6A4C2F"]},
    "Retro Palette": {"primary": ["#FF7F50", "#4F6D7A"], "secondary": ["#EAD7D1"], "accent": ["#F2B134"]},
    "Dark Theme": {"primary": ["#101820"], "secondary": ["#2D3A45"], "accent": ["#9B5DE5"]},
    "Seasonal Colors": {"primary": ["#C1121F", "#2A9D8F"], "secondary": ["#F4A261"], "accent": ["#E9C46A"]},
}


def recommend_palette(
    *,
    niche_name: str,
    product_name: str,
    season_labels: list[str],
    audience_tags: list[str],
    style_name: str,
) -> dict[str, Any]:
    """Pick a palette based on niche/product/audience/season/style signals."""

    text = f"{niche_name} {product_name} {style_name}".lower()
    season_text = " ".join(season_labels).lower()
    audience_text = " ".join(audience_tags).lower()

    palette_name = "Muted Colors"
    if any(token in text for token in ["luxury", "premium", "gold"]):
        palette_name = "Luxury Palette"
    elif any(token in text for token in ["retro", "vintage", "distressed"]):
        palette_name = "Vintage Palette" if "vintage" in text else "Retro Palette"
    elif any(token in text for token in ["minimal", "scandinavian", "line art"]):
        palette_name = "Monochrome"
    elif any(token in text for token in ["cute", "floral", "cottagecore", "boho"]):
        palette_name = "Pastel"
    elif any(token in text for token in ["gothic", "cyberpunk", "neon", "dark"]):
        palette_name = "Dark Theme"
    elif any(token in text for token in ["rustic", "botanical", "earth"]):
        palette_name = "Earth Tone"

    if "seasonal" in season_text or any(token in season_text for token in ["winter", "summer", "spring", "autumn", "holiday"]):
        palette_name = "Seasonal Colors"
    if "kids" in audience_text or "youth" in audience_text:
        palette_name = "High Contrast" if palette_name == "Monochrome" else palette_name

    selected = PALETTES[palette_name]
    return {
        "palette_name": palette_name,
        "primary_colors": selected["primary"],
        "secondary_colors": selected["secondary"],
        "accent_colors": selected["accent"],
        "rationale": f"style={style_name}, season={season_text or 'all'}, audience={audience_text or 'general'}",
    }
