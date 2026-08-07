from __future__ import annotations

from typing import Any


def build_composition(*, style_name: str, layout_type: str) -> dict[str, Any]:
    """Recommend composition details for print-ready design decisions."""

    style = style_name.lower()
    layout = layout_type.lower()
    image_text_ratio = 0.65
    whitespace = 0.30
    hierarchy = "Primary focal icon, secondary headline, tertiary subtext"
    icon_placement = "center"
    border_usage = "minimal"
    frame_usage = "none"

    if "typography" in style or layout in {"top heavy", "minimal"}:
        image_text_ratio = 0.35
        whitespace = 0.45
        hierarchy = "Bold headline, short support line, optional icon"
        icon_placement = "top"
    elif any(token in style for token in ["botanical", "floral", "watercolor", "illustration"]):
        image_text_ratio = 0.75
        whitespace = 0.25
        hierarchy = "Large illustration, medium title, tiny descriptor"
        icon_placement = "around edges"
    elif any(token in style for token in ["geometric", "abstract", "scandinavian"]):
        image_text_ratio = 0.55
        whitespace = 0.38
        border_usage = "thin"
        frame_usage = "soft"

    if layout in {"badge", "circular"}:
        frame_usage = "strong"
        border_usage = "medium"
    if layout in {"full front", "asymmetrical"}:
        icon_placement = "off-center"

    return {
        "image_text_ratio": round(image_text_ratio, 2),
        "whitespace": round(whitespace, 2),
        "visual_hierarchy": hierarchy,
        "icon_placement": icon_placement,
        "border_usage": border_usage,
        "frame_usage": frame_usage,
    }
