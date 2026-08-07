from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DesignBrief:
    product_idea: str
    style: str
    colors: str
    typography: str
    image_style: str
    prompt: str


def generate_design_prompt(niche: str, product_name: str, audience: str = "") -> DesignBrief:
    niche_lower = niche.lower()
    product_lower = product_name.lower()

    if "vintage" in niche_lower or "retro" in niche_lower:
        style = "1970s engraving"
        colors = "cream black dark green"
        typography = "bold serif with worn texture"
        image_style = "retro illustration"
    elif "astronomy" in niche_lower or "moon" in niche_lower:
        style = "celestial minimalism"
        colors = "navy cream gold"
        typography = "clean condensed sans serif"
        image_style = "scientific line art"
    elif product_lower == "poster":
        style = "gallery wall art"
        colors = "muted neutrals with one accent color"
        typography = "elegant display serif"
        image_style = "editorial print composition"
    else:
        style = "modern hand-drawn"
        colors = "black white muted accent"
        typography = "simple sans serif"
        image_style = "high-contrast vector art"

    product_idea = f"{niche} {product_name}"
    prompt = f'"{niche} {product_name}, {style}, {image_style}, print ready, high quality vector artwork, tailored for {audience or "etsy shoppers"}"'
    return DesignBrief(product_idea, style, colors, typography, image_style, prompt)
