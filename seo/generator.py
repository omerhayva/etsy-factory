from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SeoListing:
    title: str
    description: str
    tags: list[str]
    keywords: list[str]
    category: str
    price: float


def _title_case(text: str) -> str:
    return " ".join(part.capitalize() for part in text.split())


def generate_etsy_seo(niche: str, product_name: str, design_prompt: str, price_hint: float = 24.0) -> SeoListing:
    base_terms = [word for word in niche.lower().replace("/", " ").split() if word]
    keywords = list(dict.fromkeys(base_terms + [product_name.lower(), "etsy pod", "gift idea", "custom design"]))

    tags: list[str] = []
    for keyword in keywords:
        candidate = keyword.replace(" ", "")[:20]
        if candidate and candidate not in tags:
            tags.append(candidate)
        if len(tags) == 13:
            break

    while len(tags) < 13:
        tags.append(f"tag{len(tags) + 1}")

    title = _title_case(f"{niche} {product_name} - Trendy Gift for {niche.split()[0].capitalize() if niche.split() else 'Shoppers'}")[:140]
    description = (
        f"Create a standout {product_name} for {niche}. "
        f"Inspired by the prompt: {design_prompt}. "
        f"Optimized for Etsy discovery, gifting, and print-on-demand production."
    )
    return SeoListing(
        title=title,
        description=description,
        tags=tags[:13],
        keywords=keywords,
        category="Print-On-Demand",
        price=round(price_hint, 2),
    )
