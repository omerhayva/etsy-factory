from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReviewInsights:
    review_count: int
    average_rating: float
    positive_themes: list[str]
    negative_themes: list[str]
    customer_requests: list[str]


class ReviewAnalyzer:
    """Prepares review-derived insight structure for future NLP enrichment."""

    def analyze(self, product_titles: list[str], review_counts: list[int]) -> ReviewInsights:
        total_reviews = sum(max(0, int(value)) for value in review_counts)
        avg_rating = 4.4 if total_reviews > 0 else 0.0

        title_blob = " ".join(product_titles).lower()
        positive_themes: list[str] = []
        negative_themes: list[str] = []
        customer_requests: list[str] = []

        if "gift" in title_blob:
            positive_themes.append("gift-friendly")
            customer_requests.append("gift packaging")
        if "vintage" in title_blob or "retro" in title_blob:
            positive_themes.append("nostalgic style")
        if total_reviews < 50:
            negative_themes.append("low review confidence")
        if "custom" not in title_blob:
            customer_requests.append("personalization options")

        return ReviewInsights(
            review_count=total_reviews,
            average_rating=avg_rating,
            positive_themes=positive_themes or ["design appeal"],
            negative_themes=negative_themes or ["unknown quality concerns"],
            customer_requests=customer_requests or ["faster shipping"],
        )
