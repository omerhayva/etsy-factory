from __future__ import annotations

from typing import Any


SUPPORTED_PROMPT_PROVIDERS = ["Midjourney", "DALL-E", "Stable Diffusion", "Flux"]


def build_prompt_payload(
    *,
    provider: str,
    niche_name: str,
    product_name: str,
    style_name: str,
    palette_name: str,
    typography: dict[str, Any],
    composition: dict[str, Any],
) -> dict[str, str]:
    """Create model-specific prompt and negative prompt guidance."""

    primary_font = typography.get("primary_font_style", "Sans Serif")
    secondary_font = typography.get("secondary_font_style", "Serif")
    hierarchy = typography.get("hierarchy", "Clear title and supporting text")

    subject = f"{niche_name} theme for {product_name} print-on-demand design"
    style = f"visual style: {style_name}"
    colors = f"color direction: {palette_name}"
    comp = (
        f"layout {composition.get('layout_type', 'Centered')}, "
        f"image-text ratio {composition.get('image_text_ratio', 0.6)}, "
        f"whitespace {composition.get('whitespace', 0.3)}, "
        f"icon placement {composition.get('icon_placement', 'center')}"
    )
    typo = f"typography: primary {primary_font}, secondary {secondary_font}, hierarchy {hierarchy}"

    lighting = "soft studio lighting" if any(token in product_name.lower() for token in ["poster", "canvas", "framed"]) else "flat print-ready lighting"
    print_ready = "vector-friendly clean edges, transparent background, high contrast layers, print-ready CMYK-safe approach"

    provider_rule = {
        "Midjourney": "--ar 1:1 --stylize 250 --v 6",
        "DALL-E": "high-detail illustration, clean text-safe zones",
        "Stable Diffusion": "masterpiece, high quality, sharp details",
        "Flux": "balanced composition, realistic texture, premium output",
    }.get(provider, "high quality, production ready")

    prompt = (
        f"{subject}; {style}; {colors}; {comp}; {typo}; "
        f"lighting: {lighting}; {print_ready}; {provider_rule}"
    )
    negative_prompt = (
        "low resolution, watermark, logo artifacts, blurry typography, over-complex background, "
        "wrong spelling, text distortion, over-saturated colors"
    )

    return {"provider": provider, "prompt": prompt, "negative_prompt": negative_prompt}
