from __future__ import annotations


def infer_trend_style_bias(niche_name: str, evergreen_classification: str) -> dict[str, float]:
    """Return heuristic style boosts from trend context."""

    text = niche_name.lower()
    boosts: dict[str, float] = {}

    if any(token in text for token in ["vintage", "retro", "classic"]):
        boosts["Vintage"] = 10.0
        boosts["Retro"] = 12.0
        boosts["Distressed"] = 8.0
    if any(token in text for token in ["minimal", "clean", "simple"]):
        boosts["Minimal"] = 12.0
        boosts["Minimal Typography"] = 10.0
        boosts["Scandinavian"] = 8.0
    if any(token in text for token in ["luxury", "premium", "gold"]):
        boosts["Luxury"] = 14.0
    if any(token in text for token in ["anime", "japan", "manga", "kanji"]):
        boosts["Japanese"] = 14.0
        boosts["Comic"] = 9.0
    if any(token in text for token in ["christian", "faith", "bible"]):
        boosts["Christian"] = 14.0
    if any(token in text for token in ["islam", "ramadan", "arabic"]):
        boosts["Islamic"] = 14.0
    if any(token in text for token in ["cyber", "neon", "futuristic", "gamer"]):
        boosts["Cyberpunk"] = 12.0
        boosts["Neon"] = 12.0

    if evergreen_classification == "Evergreen":
        boosts["Minimal"] = boosts.get("Minimal", 0.0) + 4.0
        boosts["Modern"] = boosts.get("Modern", 0.0) + 4.0
    elif evergreen_classification == "Trending":
        boosts["Y2K"] = boosts.get("Y2K", 0.0) + 6.0
        boosts["Bold Typography"] = boosts.get("Bold Typography", 0.0) + 4.0

    return boosts
