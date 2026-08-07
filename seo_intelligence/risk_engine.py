from __future__ import annotations

from typing import Any

from seo_intelligence.copyright_checker import evaluate_copyright_risk
from seo_intelligence.policy_manager import PolicyManager
from seo_intelligence.trademark_checker import evaluate_trademark_risk


RISK_ORDER = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}


def evaluate_listing_risk(text: str, policy_manager: PolicyManager) -> dict[str, Any]:
    """Combine trademark and copyright signals into a final risk profile."""

    trademark = evaluate_trademark_risk(text, policy_manager)
    copyright = evaluate_copyright_risk(text, policy_manager)

    level = trademark["risk_level"]
    if RISK_ORDER.get(copyright["risk_level"], 1) > RISK_ORDER.get(level, 1):
        level = copyright["risk_level"]

    risk_score = max(float(trademark["risk_score"]), float(copyright["risk_score"]))
    recommendation = "Manual legal review required" if level in {"High", "Critical"} else "Proceed with caution"

    return {
        "risk_level": level,
        "risk_score": round(risk_score, 2),
        "trademark": trademark,
        "copyright": copyright,
        "recommendation": recommendation,
    }
