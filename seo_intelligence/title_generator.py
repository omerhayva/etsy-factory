from __future__ import annotations


def generate_title_versions(*, niche_name: str, product_name: str, keywords: dict[str, list[str]], intent: str) -> list[str]:
    """Generate multiple SEO-safe Etsy title options."""

    primary = keywords.get("primary", [])[:4]
    long_tail = keywords.get("long_tail", [])[:2]
    gift_terms = keywords.get("gift", [])[:2]

    base_phrase = " ".join(word.title() for word in primary[:3])
    long_tail_phrase = ", ".join(term.title() for term in long_tail)
    gift_phrase = " ".join(word.title() for word in gift_terms) if gift_terms else "Gift"

    variants = [
        f"{base_phrase} {product_name} | {intent} {gift_phrase}",
        f"{product_name} for {base_phrase} | {long_tail_phrase}",
        f"{gift_phrase} {product_name} - {base_phrase} Etsy Design",
    ]

    clean = []
    for title in variants:
        compact = " ".join(title.split())
        if len(compact) > 140:
            compact = compact[:137].rstrip() + "..."
        clean.append(compact)
    return clean
