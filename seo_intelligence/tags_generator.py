from __future__ import annotations


def _normalize_tag(tag: str) -> str:
    return " ".join(tag.strip().lower().split())[:20]


def generate_tags(*, niche_name: str, product_name: str, keywords: dict[str, list[str]], intent: str) -> list[str]:
    """Generate exactly 13 balanced Etsy tags with minimal duplication."""

    pools = []
    pools.extend(keywords.get("primary", [])[:4])
    pools.extend(keywords.get("secondary", [])[:3])
    pools.extend(keywords.get("long_tail", [])[:2])
    pools.extend(keywords.get("gift", [])[:2])
    pools.extend(keywords.get("seasonal", [])[:1])
    pools.extend(keywords.get("audience", [])[:1])
    pools.extend(keywords.get("lifestyle", [])[:1])

    pools.append(product_name.lower())
    pools.append(niche_name.lower())
    pools.append(intent.lower())

    tags: list[str] = []
    used = set()
    for item in pools:
        norm = _normalize_tag(item)
        if not norm:
            continue
        signature = norm.replace(" ", "")
        if signature in used:
            continue
        used.add(signature)
        tags.append(norm)
        if len(tags) == 13:
            break

    attempts = 0
    while len(tags) < 13:
        filler = _normalize_tag(f"pod gift tag {len(tags)+1} {attempts}")
        signature = filler.replace(" ", "")
        if signature not in used:
            used.add(signature)
            tags.append(filler)
        attempts += 1
        if attempts > 100:
            break

    return tags[:13]
