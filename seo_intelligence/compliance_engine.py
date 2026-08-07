from __future__ import annotations

from typing import Any

from seo_intelligence.listing_validator import validate_listing_content
from seo_intelligence.policy_engine import PolicyEngine
from seo_intelligence.policy_manager import PolicyManager
from seo_intelligence.risk_engine import evaluate_listing_risk
from seo_intelligence.spam_detector import detect_spam


class ComplianceEngine:
    """Runs compliance, risk, and spam checks for a listing package."""

    def __init__(self, policy_manager: PolicyManager):
        self.policy_manager = policy_manager
        self.policy_engine = PolicyEngine(policy_manager)

    def evaluate(self, listing: dict[str, Any]) -> dict[str, Any]:
        validation = validate_listing_content(listing)
        policy = self.policy_engine.validate(listing)
        spam = detect_spam(
            title=str(listing.get("title", "")),
            description=str(listing.get("description", "")),
            tags=list(listing.get("tags", [])),
            policy_manager=self.policy_manager,
        )
        risk = evaluate_listing_risk(
            text=f"{listing.get('title', '')} {listing.get('description', '')} {' '.join(listing.get('tags', []))}",
            policy_manager=self.policy_manager,
        )

        warnings = validation["warnings"] + policy["warnings"] + spam["warnings"]
        fixes = validation["suggested_fixes"] + policy["suggested_fixes"]
        compliance_score = max(0.0, min(100.0, (validation["validation_score"] * 0.3 + policy["policy_score"] * 0.45 + spam["spam_score"] * 0.25)))

        return {
            "validation": validation,
            "policy": policy,
            "spam": spam,
            "risk": risk,
            "warnings": warnings,
            "suggested_fixes": fixes,
            "compliance_score": round(compliance_score, 2),
        }
