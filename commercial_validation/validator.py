from __future__ import annotations

from typing import Any


def validate_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    """Check that the commercial validation input is structurally complete."""

    warnings: list[str] = []
    required_fields = ["niche_name", "product_name", "title", "description", "tags"]
    for field in required_fields:
        if not str(candidate.get(field, "")).strip():
            warnings.append(f"Missing required field: {field}")

    tags = list(candidate.get("tags", []))
    if len(tags) < 10:
        warnings.append("Tag coverage is weak")

    return {"passed": len(warnings) == 0, "warnings": warnings}
