from __future__ import annotations

from collections import defaultdict


def _tokenize(text: str) -> list[str]:
    cleaned = text.replace("-", " ").replace("_", " ").replace("'", "")
    return [token.strip().lower() for token in cleaned.split() if token.strip()]


def categorize_keywords(*, niche_name: str, product_name: str, style_name: str, trend_terms: list[str] | None = None) -> dict[str, list[str]]:
    """Categorize keywords for SEO assembly."""

    trend_terms = trend_terms or []
    tokens = _tokenize(f"{niche_name} {product_name} {style_name}")

    categories: dict[str, list[str]] = defaultdict(list)

    for token in tokens:
        if token in {"gift", "gifts", "present"}:
            categories["gift"].append(token)
        elif token in {"summer", "winter", "spring", "autumn", "holiday", "christmas", "halloween", "easter"}:
            categories["seasonal"].append(token)
        elif token in {"mom", "dad", "kids", "teacher", "nurse", "couple", "family"}:
            categories["audience"].append(token)
        elif token in {"home", "decor", "office", "lifestyle", "boho", "rustic"}:
            categories["lifestyle"].append(token)
        elif token in {"best", "top", "premium", "unique", "custom"}:
            categories["commercial_intent"].append(token)
        else:
            categories["primary"].append(token)

    categories["secondary"] = categories["primary"][1:6]
    long_tail = []
    base_terms = [token for token in categories["primary"] if len(token) > 2]
    for idx in range(max(0, len(base_terms) - 1)):
        long_tail.append(f"{base_terms[idx]} {base_terms[idx + 1]}")
    categories["long_tail"] = long_tail[:8]

    categories["seasonal"] = list(dict.fromkeys(categories["seasonal"] + [term.lower() for term in trend_terms if term]))
    return {key: list(dict.fromkeys(value)) for key, value in categories.items()}
