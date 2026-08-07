from __future__ import annotations

from typing import Any


def validate_listing_content(listing: dict[str, Any]) -> dict[str, Any]:
    """Validate basic completeness and structural quality."""

    warnings: list[str] = []
    fixes: list[str] = []

    title = str(listing.get("title", ""))
    description = str(listing.get("description", ""))
    tags = list(listing.get("tags", []))

    if not title.strip():
        warnings.append("Missing title")
        fixes.append("Generate title")
    if not description.strip():
        warnings.append("Missing description")
        fixes.append("Generate full description")
    if not tags:
        warnings.append("Missing tags")
        fixes.append("Generate exactly 13 tags")
    if len(title) < 45:
        warnings.append("Title may be too short for SEO")
        fixes.append("Expand title with long-tail phrase")
    if len(description) < 350:
        warnings.append("Description depth is low")
        fixes.append("Add richer feature/benefit details")

    score = max(0.0, 100.0 - len(warnings) * 9.0)
    return {"validation_score": round(score, 2), "warnings": warnings, "suggested_fixes": fixes, "passed": len(warnings) == 0}
