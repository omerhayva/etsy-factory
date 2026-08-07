from __future__ import annotations

from typing import Any

from seo_intelligence.policy_manager import PolicyManager


PRIORITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def decide_publish(*, score: float, compliance_score: float, risk_level: str, warnings: list[str], fixes: list[str], policy_manager: PolicyManager) -> dict[str, Any]:
    """Return final publish gate decision."""

    rules = policy_manager.rules().get("publish_decision", {})
    blocked_levels = {item.lower() for item in rules.get("blocked_risk_levels", ["high", "critical"])}
    min_overall = float(rules.get("min_overall_score_for_publish", 72))
    min_compliance = float(rules.get("min_compliance_score_for_publish", 75))

    reasons: list[str] = []
    if risk_level.lower() in blocked_levels:
        reasons.append(f"Risk level is blocked: {risk_level}")
    if score < min_overall:
        reasons.append(f"Overall listing score below threshold: {score:.2f} < {min_overall:.2f}")
    if compliance_score < min_compliance:
        reasons.append(f"Compliance score below threshold: {compliance_score:.2f} < {min_compliance:.2f}")
    if warnings:
        reasons.append("Warnings exist in compliance validation")

    decision = "READY FOR PUBLISH" if not reasons else "NEEDS IMPROVEMENT"
    priority = "low"
    if risk_level in {"High", "Critical"}:
        priority = "critical"
    elif len(reasons) >= 3:
        priority = "high"
    elif reasons:
        priority = "medium"

    return {
        "decision": decision,
        "reasons": reasons,
        "suggested_fixes": fixes,
        "priority_level": priority,
    }
