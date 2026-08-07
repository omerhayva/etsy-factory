from __future__ import annotations

from typing import Any


def default_style_library() -> list[dict[str, Any]]:
    """Return configurable style definitions with targeting metadata."""

    return [
        {"name": "Vintage", "family": "nostalgic", "audiences": ["gift", "adult", "collector"], "products": ["T-Shirt", "Mug", "Poster"], "seasons": ["all"], "keywords": ["vintage", "classic", "retro"]},
        {"name": "Retro", "family": "nostalgic", "audiences": ["gift", "youth", "adult"], "products": ["T-Shirt", "Sticker", "Poster"], "seasons": ["all"], "keywords": ["retro", "80s", "90s"]},
        {"name": "Minimal", "family": "clean", "audiences": ["adult", "professional", "gift"], "products": ["T-Shirt", "Tote Bag", "Notebook"], "seasons": ["all"], "keywords": ["minimal", "simple", "clean"]},
        {"name": "Modern", "family": "clean", "audiences": ["adult", "professional", "youth"], "products": ["T-Shirt", "Phone Case", "Desk Mat"], "seasons": ["all"], "keywords": ["modern", "contemporary"]},
        {"name": "Luxury", "family": "premium", "audiences": ["adult", "professional", "gift"], "products": ["Framed Poster", "Canvas", "Hoodie"], "seasons": ["all"], "keywords": ["luxury", "premium", "gold"]},
        {"name": "Boho", "family": "lifestyle", "audiences": ["adult", "gift", "female"], "products": ["Tote Bag", "Pillow", "Poster"], "seasons": ["spring", "summer"], "keywords": ["boho", "free spirit"]},
        {"name": "Rustic", "family": "lifestyle", "audiences": ["adult", "gift", "family"], "products": ["Doormat", "Kitchen Towel", "Poster"], "seasons": ["autumn", "winter"], "keywords": ["rustic", "farmhouse"]},
        {"name": "Watercolor", "family": "illustrative", "audiences": ["gift", "female", "family"], "products": ["Mug", "Poster", "Notebook"], "seasons": ["spring", "all"], "keywords": ["watercolor", "paint"]},
        {"name": "Line Art", "family": "illustrative", "audiences": ["adult", "professional"], "products": ["Poster", "T-Shirt", "Tote Bag"], "seasons": ["all"], "keywords": ["line art", "outline"]},
        {"name": "Hand Drawn", "family": "illustrative", "audiences": ["gift", "family", "youth"], "products": ["Sticker", "Notebook", "Mug"], "seasons": ["all"], "keywords": ["hand drawn", "sketch"]},
        {"name": "Botanical", "family": "nature", "audiences": ["adult", "gift", "female"], "products": ["Poster", "Pillow", "Notebook"], "seasons": ["spring", "summer", "all"], "keywords": ["botanical", "plant", "leaf"]},
        {"name": "Floral", "family": "nature", "audiences": ["gift", "female", "family"], "products": ["Mug", "Tote Bag", "Pillow"], "seasons": ["spring", "summer"], "keywords": ["floral", "flower"]},
        {"name": "Cute", "family": "playful", "audiences": ["kids", "gift", "youth"], "products": ["Sticker", "Kids Shirt", "Mug"], "seasons": ["all"], "keywords": ["cute", "adorable"]},
        {"name": "Cartoon", "family": "playful", "audiences": ["kids", "youth", "gift"], "products": ["Kids Shirt", "Sticker", "Poster"], "seasons": ["all"], "keywords": ["cartoon", "character"]},
        {"name": "Comic", "family": "playful", "audiences": ["youth", "collector", "gift"], "products": ["T-Shirt", "Poster", "Phone Case"], "seasons": ["all"], "keywords": ["comic", "panel", "hero"]},
        {"name": "Cyberpunk", "family": "futuristic", "audiences": ["youth", "gamer", "collector"], "products": ["Poster", "Phone Case", "Hoodie"], "seasons": ["all"], "keywords": ["cyberpunk", "futuristic", "neon"]},
        {"name": "Neon", "family": "futuristic", "audiences": ["youth", "nightlife", "gamer"], "products": ["T-Shirt", "Poster", "Phone Case"], "seasons": ["all"], "keywords": ["neon", "glow"]},
        {"name": "Gothic", "family": "dark", "audiences": ["adult", "collector", "youth"], "products": ["Hoodie", "Poster", "Mug"], "seasons": ["autumn", "winter", "all"], "keywords": ["gothic", "dark", "victorian"]},
        {"name": "Dark Academia", "family": "dark", "audiences": ["adult", "student", "collector"], "products": ["Notebook", "Poster", "Mug"], "seasons": ["autumn", "winter"], "keywords": ["dark academia", "scholarly"]},
        {"name": "Cottagecore", "family": "lifestyle", "audiences": ["gift", "female", "adult"], "products": ["Tote Bag", "Mug", "Poster"], "seasons": ["spring", "summer"], "keywords": ["cottagecore", "pastoral"]},
        {"name": "Y2K", "family": "nostalgic", "audiences": ["youth", "fashion", "gift"], "products": ["T-Shirt", "Phone Case", "Sticker"], "seasons": ["all"], "keywords": ["y2k", "2000s"]},
        {"name": "Minimal Typography", "family": "typography", "audiences": ["adult", "professional"], "products": ["T-Shirt", "Mug", "Notebook"], "seasons": ["all"], "keywords": ["typography", "quote", "minimal"]},
        {"name": "Bold Typography", "family": "typography", "audiences": ["youth", "gift", "adult"], "products": ["T-Shirt", "Hoodie", "Poster"], "seasons": ["all"], "keywords": ["bold", "statement", "typography"]},
        {"name": "Distressed", "family": "texture", "audiences": ["adult", "collector", "gift"], "products": ["T-Shirt", "Hat", "Poster"], "seasons": ["all"], "keywords": ["distressed", "grunge"]},
        {"name": "Geometric", "family": "abstract", "audiences": ["adult", "professional", "gift"], "products": ["Poster", "Phone Case", "Desk Mat"], "seasons": ["all"], "keywords": ["geometric", "shapes"]},
        {"name": "Abstract", "family": "abstract", "audiences": ["adult", "collector", "gift"], "products": ["Canvas", "Poster", "Mug"], "seasons": ["all"], "keywords": ["abstract", "art"]},
        {"name": "Christian", "family": "cultural", "audiences": ["family", "gift", "adult"], "products": ["T-Shirt", "Mug", "Poster"], "seasons": ["all", "holiday"], "keywords": ["christian", "faith", "bible"]},
        {"name": "Islamic", "family": "cultural", "audiences": ["family", "gift", "adult"], "products": ["Poster", "Mug", "Notebook"], "seasons": ["all", "holiday"], "keywords": ["islamic", "arabic", "ramadan"]},
        {"name": "Japanese", "family": "cultural", "audiences": ["youth", "collector", "gift"], "products": ["Poster", "T-Shirt", "Sticker"], "seasons": ["all"], "keywords": ["japanese", "anime", "kanji"]},
        {"name": "Scandinavian", "family": "clean", "audiences": ["adult", "home", "gift"], "products": ["Poster", "Pillow", "Mug"], "seasons": ["all", "winter"], "keywords": ["scandinavian", "nordic", "minimal"]},
    ]


def recommend_styles(
    *,
    niche_name: str,
    product_name: str,
    audience_tags: list[str],
    season_tags: list[str],
    trend_signal: float,
    gift_signal: float,
    style_library: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Score styles for a niche/product context and return ranked choices."""

    niche_tokens = set(niche_name.lower().replace("'", "").split())
    product_text = product_name.lower()
    season_set = {item.lower() for item in season_tags if item}
    audience_set = {item.lower() for item in audience_tags if item}

    scored: list[dict[str, Any]] = []
    for style in style_library:
        keyword_hits = sum(1 for token in style.get("keywords", []) if token.lower() in niche_tokens or token.lower() in niche_name.lower())
        product_hits = sum(1 for token in style.get("products", []) if token.lower() in product_text)
        audience_hits = len(audience_set.intersection({item.lower() for item in style.get("audiences", [])}))
        season_hits = 1 if "all" in {item.lower() for item in style.get("seasons", [])} or season_set.intersection({item.lower() for item in style.get("seasons", [])}) else 0

        base = 34.0
        score = (
            base
            + keyword_hits * 12.0
            + product_hits * 9.0
            + audience_hits * 7.0
            + season_hits * 5.0
            + trend_signal * 0.18
            + gift_signal * 0.16
        )
        score = max(0.0, min(100.0, score))

        scored.append(
            {
                "style_name": style["name"],
                "style_family": style.get("family", "general"),
                "score": round(score, 2),
                "trend_alignment": round((trend_signal * 0.6 + keyword_hits * 10.0 + season_hits * 8.0), 2),
                "reasoning": f"keywords={keyword_hits}, product_fit={product_hits}, audience_fit={audience_hits}, season_fit={season_hits}",
            }
        )

    return sorted(scored, key=lambda item: item["score"], reverse=True)
