from __future__ import annotations

from typing import Any


def recommend_layout(*, product_name: str, style_name: str, typography_primary: str) -> dict[str, Any]:
    """Recommend layout type for product and style context."""

    product = product_name.lower()
    style = style_name.lower()
    layout = "Centered"

    if any(token in product for token in ["hoodie", "t-shirt", "shirt", "sweatshirt"]):
        layout = "Full Front"
    if any(token in product for token in ["cap", "hat", "beanie"]):
        layout = "Pocket Style"
    if any(token in product for token in ["mug", "ornament", "badge"]):
        layout = "Badge"
    if any(token in style for token in ["minimal", "line art", "scandinavian"]):
        layout = "Minimal"
    if any(token in style for token in ["geometric", "abstract", "botanical"]):
        layout = "Symmetrical"
    if typography_primary in {"Bold", "Playful"}:
        layout = "Top Heavy"

    if any(token in style for token in ["comic", "cartoon", "cyberpunk"]):
        secondary_layout = "Asymmetrical"
    elif any(token in style for token in ["retro", "vintage", "distressed"]):
        secondary_layout = "Circular"
    else:
        secondary_layout = "Centered"

    return {
        "layout_type": layout,
        "secondary_layout": secondary_layout,
        "rationale": f"product={product_name}, style={style_name}, typo={typography_primary}",
    }
