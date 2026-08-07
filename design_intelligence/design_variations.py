from __future__ import annotations

from typing import Any

from design_intelligence.prompt_builder import build_prompt_payload


VARIATION_TYPES = [
    "Minimal version",
    "Premium version",
    "Vintage version",
    "Modern version",
    "Typography-focused version",
    "Illustration-focused version",
]


def generate_variations(
    *,
    niche_name: str,
    product_name: str,
    style_name: str,
    palette_name: str,
    typography: dict[str, Any],
    composition: dict[str, Any],
    provider: str,
    base_score: float,
) -> list[dict[str, Any]]:
    """Generate six required concept variations with prompt adaptations."""

    rows: list[dict[str, Any]] = []
    for variation in VARIATION_TYPES:
        variation_style = style_name
        if "Minimal" in variation:
            variation_style = "Minimal"
        elif "Premium" in variation:
            variation_style = "Luxury"
        elif "Vintage" in variation:
            variation_style = "Vintage"
        elif "Modern" in variation:
            variation_style = "Modern"
        elif "Typography" in variation:
            variation_style = "Bold Typography"
        elif "Illustration" in variation:
            variation_style = "Hand Drawn"

        payload = build_prompt_payload(
            provider=provider,
            niche_name=niche_name,
            product_name=product_name,
            style_name=variation_style,
            palette_name=palette_name,
            typography=typography,
            composition=composition,
        )

        score_modifier = {
            "Minimal version": 0.96,
            "Premium version": 1.02,
            "Vintage version": 0.99,
            "Modern version": 1.01,
            "Typography-focused version": 0.97,
            "Illustration-focused version": 1.00,
        }[variation]

        rows.append(
            {
                "variation_type": variation,
                "style_name": variation_style,
                "prompt": payload["prompt"],
                "score": round(max(0.0, min(100.0, base_score * score_modifier)), 2),
            }
        )
    return rows
