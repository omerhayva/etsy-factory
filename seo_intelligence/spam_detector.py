from __future__ import annotations

from collections import Counter
from typing import Any

from seo_intelligence.policy_manager import PolicyManager


def detect_spam(*, title: str, description: str, tags: list[str], policy_manager: PolicyManager) -> dict[str, Any]:
    """Detect keyword stuffing, clickbait, and misleading/spam patterns."""

    rules = policy_manager.rules()
    spam_rules = rules.get("spam_rules", {})
    restricted = rules.get("restricted_claim_rules", {})

    text = f"{title} {description} {' '.join(tags)}".lower()
    tokens = [token for token in text.replace("|", " ").replace(",", " ").split() if token]
    counts = Counter(tokens)

    max_repeat = int(spam_rules.get("max_keyword_repeat_per_word", 3))
    stuffing = [token for token, count in counts.items() if count > max_repeat and len(token) > 2]

    blocked_hits = [phrase for phrase in spam_rules.get("blocked_phrases", []) if str(phrase).lower() in text]
    clickbait_hits = [phrase for phrase in spam_rules.get("clickbait_patterns", []) if str(phrase).lower() in text]
    medical_hits = [phrase for phrase in restricted.get("medical_claim_patterns", []) if str(phrase).lower() in text]
    misleading_hits = [phrase for phrase in restricted.get("misleading_patterns", []) if str(phrase).lower() in text]

    warnings = []
    if stuffing:
        warnings.append(f"Keyword stuffing detected: {', '.join(stuffing[:8])}")
    if blocked_hits:
        warnings.append(f"Blocked phrases detected: {', '.join(blocked_hits)}")
    if clickbait_hits:
        warnings.append(f"Clickbait patterns detected: {', '.join(clickbait_hits)}")
    if medical_hits:
        warnings.append(f"Medical claim patterns detected: {', '.join(medical_hits)}")
    if misleading_hits:
        warnings.append(f"Misleading claim patterns detected: {', '.join(misleading_hits)}")

    score = max(0.0, 100.0 - len(warnings) * 18.0)
    return {
        "spam_score": round(score, 2),
        "warnings": warnings,
        "keyword_stuffing": stuffing,
        "clickbait_hits": clickbait_hits,
        "misleading_hits": misleading_hits,
        "passed": len(warnings) == 0,
    }
