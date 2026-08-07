from __future__ import annotations

from typing import Any

from seo_intelligence.policy_manager import PolicyManager


class PolicyEngine:
    """Evaluates policy constraints for generated Etsy listings."""

    def __init__(self, policy_manager: PolicyManager):
        self.policy_manager = policy_manager

    def validate(self, listing: dict[str, Any]) -> dict[str, Any]:
        rules = self.policy_manager.rules()
        requirements = rules.get("listing_requirements", {})
        validation = rules.get("validation_rules", {})

        warnings: list[str] = []
        fixes: list[str] = []

        title = str(listing.get("title", ""))
        description = str(listing.get("description", ""))
        tags = list(listing.get("tags", []))

        max_title = int(requirements.get("max_title_length", 140))
        min_desc = int(requirements.get("min_description_length", 450))
        required_tag_count = int(requirements.get("required_tag_count", 13))

        if len(title) > max_title:
            warnings.append("Title exceeds allowed length")
            fixes.append("Shorten title to policy limit")

        if len(description) < min_desc:
            warnings.append("Description is too short")
            fixes.append("Expand description with required sections")

        if len(tags) != required_tag_count:
            warnings.append("Tag count is not exactly required value")
            fixes.append("Regenerate tags to exact policy count")

        if bool(validation.get("require_unique_tags", True)) and len({tag.lower() for tag in tags}) != len(tags):
            warnings.append("Duplicate tags detected")
            fixes.append("Use unique tags")

        required_sections = requirements.get("required_sections", [])
        lower_desc = description.lower()
        for section in required_sections:
            normalized = str(section).replace("_", " ")
            if normalized not in lower_desc:
                warnings.append(f"Missing section: {section}")
                fixes.append(f"Add section: {section}")

        score = max(0.0, 100.0 - len(warnings) * 7.5)
        return {
            "policy_score": round(score, 2),
            "warnings": warnings,
            "suggested_fixes": fixes,
            "passed": len(warnings) == 0,
            "policy_version": self.policy_manager.version().get("policy_version", "unknown"),
        }
