from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from database.db import EtsyDatabase


@dataclass(slots=True)
class ProductFactoryInput:
    niche: str
    audience: str
    product_category: str
    language: str
    market: str


class ProductFactoryWorkflow:
    def __init__(self, db: EtsyDatabase):
        self.db = db

    def normalize_input(self, payload: dict[str, Any] | ProductFactoryInput) -> ProductFactoryInput:
        if isinstance(payload, ProductFactoryInput):
            return payload
        return ProductFactoryInput(
            niche=str(payload.get("niche", "")).strip() or "General",
            audience=str(payload.get("audience", "")).strip() or "General audience",
            product_category=str(payload.get("product_category", "")).strip() or "T-shirt",
            language=str(payload.get("language", "en")).strip() or "en",
            market=str(payload.get("market", "Global")).strip() or "Global",
        )

    def seed_terms(self, factory_input: ProductFactoryInput) -> list[str]:
        terms = [
            factory_input.niche,
            factory_input.audience,
            factory_input.product_category,
            factory_input.market,
            f"{factory_input.niche} {factory_input.audience}",
            f"{factory_input.product_category} {factory_input.market}",
        ]
        unique_terms: list[str] = []
        for term in terms:
            cleaned = term.strip()
            if cleaned and cleaned not in unique_terms:
                unique_terms.append(cleaned)
        return unique_terms

    def build_candidate_retry(self, candidate: dict[str, Any], factory_input: ProductFactoryInput) -> dict[str, Any]:
        improved = dict(candidate)
        listing_payload = improved.get("listing_payload", {})
        if isinstance(listing_payload, str):
            try:
                listing_payload = json.loads(listing_payload)
            except json.JSONDecodeError:
                listing_payload = {}
        if not isinstance(listing_payload, dict):
            listing_payload = {}

        recommendations = self._collect_recommendation_text(improved)
        title = str(listing_payload.get("selected_title") or improved.get("selected_title") or improved.get("title") or improved.get("product_name") or "")
        description = str(listing_payload.get("description") or improved.get("description") or "")
        tags = self._normalize_tags(listing_payload.get("tags") or improved.get("tags") or [])
        price = float(listing_payload.get("price") or improved.get("price") or improved.get("suggested_selling_price") or 24.0)

        if any(token in recommendations for token in ["gift", "buyer intent", "gift angle"]):
            title = self._ensure_phrase(title, "Gift")
            description = self._append_sentence(description, f"Optimized for {factory_input.audience} gift buyers in {factory_input.market}.")
            tags = self._normalize_tags(tags + [f"{factory_input.audience} gift", f"{factory_input.market} gift"])

        if any(token in recommendations for token in ["pricing", "position", "margin"]):
            price = round(max(12.0, price * 0.92), 2)
            description = self._append_sentence(description, "Pricing has been adjusted for a stronger market position.")

        if any(token in recommendations for token in ["originality", "differentiation", "stand out"]):
            title = self._ensure_phrase(title, factory_input.market)
            tags = self._normalize_tags(tags + [factory_input.market, factory_input.niche])

        if any(token in recommendations for token in ["seasonal", "evergreen", "timing"]):
            description = self._append_sentence(description, f"Built for {factory_input.market} demand and longer-term relevance.")

        listing_payload.update(
            {
                "selected_title": title,
                "title": title,
                "description": description,
                "tags": tags,
                "price": price,
            }
        )
        improved.update(
            {
                "selected_title": title,
                "title": title,
                "description": description,
                "tags": tags,
                "price": price,
                "suggested_selling_price": price,
                "listing_payload": listing_payload,
            }
        )
        return improved

    def build_product_package(
        self,
        *,
        factory_input: ProductFactoryInput,
        run_id: int,
        seo_row: dict[str, Any],
        commercial_row: dict[str, Any],
        product_row: dict[str, Any],
        design_row: dict[str, Any],
        niche_row: dict[str, Any],
        research_row: dict[str, Any],
        attempt_number: int,
    ) -> dict[str, Any]:
        listing_payload = seo_row.get("listing_payload", {})
        if isinstance(listing_payload, str):
            try:
                listing_payload = json.loads(listing_payload)
            except json.JSONDecodeError:
                listing_payload = {}
        if not isinstance(listing_payload, dict):
            listing_payload = {}

        design_prompt = self._lookup_design_prompt(seo_row.get("niche_name", ""), seo_row.get("product_name", ""))
        selected_title = str(seo_row.get("selected_title") or listing_payload.get("selected_title") or listing_payload.get("title") or product_row.get("recommended_product") or seo_row.get("product_name") or "")
        tags = self._normalize_tags(listing_payload.get("tags") or seo_row.get("tags") or [])
        description = str(listing_payload.get("description") or seo_row.get("description") or "")
        recommended_price = listing_payload.get("price") or seo_row.get("suggested_selling_price") or commercial_row.get("pricing_recommendation", {}).get("suggested_selling_price") or 24.0

        return {
            "run_id": run_id,
            "attempt_number": attempt_number,
            "niche_name": seo_row.get("niche_name") or product_row.get("niche_name") or niche_row.get("niche_name"),
            "audience": factory_input.audience,
            "product_category": factory_input.product_category,
            "language": factory_input.language,
            "market": factory_input.market,
            "recommended_product": seo_row.get("product_name") or product_row.get("recommended_product") or product_row.get("product_name"),
            "product_summary": self._build_product_summary(factory_input, seo_row, product_row, niche_row, research_row),
            "design_strategy": {
                "style_name": design_row.get("style_name"),
                "palette_name": design_row.get("palette_name"),
                "primary_font_style": design_row.get("primary_font_style"),
                "layout_type": design_row.get("layout_type"),
                "overall_design_score": design_row.get("overall_design_score"),
            },
            "ai_prompt": design_prompt,
            "title": selected_title,
            "description": description,
            "tags": tags,
            "pricing_recommendation": {
                "suggested_selling_price": recommended_price,
                "estimated_margin_percent": listing_payload.get("estimated_margin_percent") or commercial_row.get("estimated_profit"),
            },
            "commercial_score": commercial_row.get("commercial_score"),
            "commercial_confidence": commercial_row.get("confidence_score"),
            "commercial_risk": commercial_row.get("risk_score"),
            "publish_decision": commercial_row.get("publish_decision"),
            "commercial_recommendations": commercial_row.get("recommendations", []),
            "commercial_reasons": commercial_row.get("reasons", []),
            "listing_payload": listing_payload,
            "seo_listing": seo_row,
            "commercial_validation": commercial_row,
            "upstream": {
                "niche": niche_row,
                "product": product_row,
                "design": design_row,
                "research": research_row,
            },
        }

    def _lookup_design_prompt(self, niche_name: str, product_name: str) -> str:
        prompt_df = self.db.fetch_design_prompts(limit=500)
        if prompt_df.empty:
            return ""
        match = prompt_df[(prompt_df["niche_name"] == niche_name) & (prompt_df["product_name"] == product_name)]
        if match.empty:
            match = prompt_df[prompt_df["niche_name"] == niche_name]
        if match.empty:
            return str(prompt_df.iloc[0].get("prompt", ""))
        return str(match.iloc[0].get("prompt", ""))

    def _build_product_summary(
        self,
        factory_input: ProductFactoryInput,
        seo_row: dict[str, Any],
        product_row: dict[str, Any],
        niche_row: dict[str, Any],
        research_row: dict[str, Any],
    ) -> str:
        pieces = [
            f"{factory_input.niche} for {factory_input.audience}",
            f"Market: {factory_input.market}",
            f"Category: {factory_input.product_category}",
            f"Recommended product: {product_row.get('recommended_product') or seo_row.get('product_name') or 'unknown'}",
            f"Niche score: {niche_row.get('overall_score', 'n/a')}",
            f"Research demand: {research_row.get('opportunity_score', 'n/a')}",
        ]
        return " | ".join(str(piece) for piece in pieces)

    def _collect_recommendation_text(self, candidate: dict[str, Any]) -> str:
        recommendations = candidate.get("recommendations") or candidate.get("commercial_recommendations") or []
        if isinstance(recommendations, str):
            return recommendations.lower()
        return " ".join(str(item).lower() for item in recommendations)

    def _normalize_tags(self, tags: Any) -> list[str]:
        if isinstance(tags, str):
            tags = [token.strip() for token in tags.split(",") if token.strip()]
        if not isinstance(tags, list):
            tags = []
        unique_tags: list[str] = []
        for tag in tags:
            text = str(tag).strip()
            if not text:
                continue
            lowered = text.lower()
            if lowered in {item.lower() for item in unique_tags}:
                continue
            unique_tags.append(text)
            if len(unique_tags) >= 13:
                break
        return unique_tags

    def _ensure_phrase(self, text: str, phrase: str) -> str:
        cleaned = text.strip()
        if phrase.lower() in cleaned.lower():
            return cleaned
        return f"{cleaned} {phrase}".strip()

    def _append_sentence(self, text: str, sentence: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            return sentence
        if sentence.lower() in cleaned.lower():
            return cleaned
        if cleaned.endswith((".", "!", "?")):
            return f"{cleaned} {sentence}"
        return f"{cleaned}. {sentence}"
