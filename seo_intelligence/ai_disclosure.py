from __future__ import annotations

from seo_intelligence.policy_manager import PolicyManager


def build_ai_disclosure(policy_manager: PolicyManager) -> dict[str, str]:
    """Return configurable AI disclosure placeholder package."""

    return {
        "placeholder": policy_manager.disclosure_placeholder(),
        "note": "Replace placeholder with the current store disclosure statement before publish.",
    }
