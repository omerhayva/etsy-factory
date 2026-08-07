from __future__ import annotations

from typing import Any

from seo_intelligence.policy_manager import PolicyManager


def evaluate_trademark_risk(text: str, policy_manager: PolicyManager) -> dict[str, Any]:
    """Detect potential trademark references and assign risk level."""

    rules = policy_manager.rules().get("trademark_risk", {})
    high_terms = [term.lower() for term in rules.get("high_risk_terms", [])]
    medium_terms = [term.lower() for term in rules.get("medium_risk_terms", [])]

    lower = text.lower()
    high_hits = [term for term in high_terms if term in lower]
    med_hits = [term for term in medium_terms if term in lower]

    if high_hits:
        level = "Critical" if len(high_hits) > 1 else "High"
        score = 90.0 if level == "Critical" else 78.0
        reason = f"High-risk terms detected: {', '.join(high_hits)}"
    elif med_hits:
        level = "Medium"
        score = 52.0
        reason = f"Medium-risk terms detected: {', '.join(med_hits)}"
    else:
        level = "Low"
        score = 12.0
        reason = "No obvious trademark signals"

    return {"risk_level": level, "risk_score": score, "reason": reason}
