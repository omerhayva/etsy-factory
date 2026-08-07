from __future__ import annotations

from typing import Any

from seo_intelligence.policy_manager import PolicyManager


def evaluate_copyright_risk(text: str, policy_manager: PolicyManager) -> dict[str, Any]:
    """Estimate copyright exposure from protected content references."""

    patterns = [item.lower() for item in policy_manager.rules().get("copyright_risk", {}).get("protected_content_patterns", [])]
    lower = text.lower()
    hits = [pattern for pattern in patterns if pattern in lower]

    if hits:
        level = "High" if len(hits) > 1 else "Medium"
        score = 72.0 if level == "High" else 48.0
        reason = f"Protected content patterns found: {', '.join(hits)}"
        recommendation = "Rewrite listing to remove copyrighted references"
    else:
        level = "Low"
        score = 10.0
        reason = "No obvious copyrighted reference patterns"
        recommendation = "Continue with originality checks"

    return {"risk_level": level, "risk_score": score, "reason": reason, "recommendation": recommendation}
