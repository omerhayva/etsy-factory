from __future__ import annotations

from typing import Any


def score_design(
    *,
    style_score: float,
    product_match_score: float,
    gift_signal: float,
    competition_score: float,
    composition: dict[str, Any],
    typography: dict[str, Any],
) -> dict[str, float]:
    """Compute design quality and commercial performance indicators."""

    image_text_ratio = float(composition.get("image_text_ratio", 0.6))
    whitespace = float(composition.get("whitespace", 0.3))
    readability_boost = 8.0 if typography.get("primary_font_style") in {"Sans Serif", "Minimal", "Bold"} else 4.0

    print_quality = max(0.0, min(100.0, style_score * 0.45 + product_match_score * 0.35 + 18.0))
    visual_balance = max(0.0, min(100.0, 70.0 + (0.5 - abs(image_text_ratio - 0.55)) * 40.0 + whitespace * 12.0))
    commercial_appeal = max(0.0, min(100.0, style_score * 0.38 + gift_signal * 0.22 + (100.0 - competition_score) * 0.25 + 10.0))
    gift_appeal = max(0.0, min(100.0, gift_signal * 0.7 + style_score * 0.2 + 8.0))
    brandability = max(0.0, min(100.0, visual_balance * 0.45 + style_score * 0.25 + 20.0))
    readability = max(0.0, min(100.0, visual_balance * 0.5 + readability_boost + whitespace * 15.0))
    production_suitability = max(0.0, min(100.0, print_quality * 0.55 + readability * 0.3 + 12.0))

    overall = (
        print_quality * 0.18
        + visual_balance * 0.15
        + commercial_appeal * 0.22
        + gift_appeal * 0.10
        + brandability * 0.12
        + readability * 0.12
        + production_suitability * 0.11
    )

    return {
        "print_quality": round(print_quality, 2),
        "visual_balance": round(visual_balance, 2),
        "commercial_appeal": round(commercial_appeal, 2),
        "gift_appeal": round(gift_appeal, 2),
        "brandability": round(brandability, 2),
        "readability": round(readability, 2),
        "production_suitability": round(production_suitability, 2),
        "overall_design_score": round(overall, 2),
    }
