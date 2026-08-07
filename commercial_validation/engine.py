from __future__ import annotations

import json
from typing import Any

import pandas as pd

from database.db import EtsyDatabase
from commercial_validation.buyer_psychology import analyze_buyer_psychology
from commercial_validation.competitor_gap import analyze_competitor_gap
from commercial_validation.gift_validation import validate_gift_potential
from commercial_validation.pricing_validation import validate_pricing
from commercial_validation.publish_decision import decide_publish
from commercial_validation.report import CommercialValidationReport
from commercial_validation.scoring import calculate_commercial_score
from commercial_validation.trend_validation import validate_trend_fit
from commercial_validation.validator import validate_candidate
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


class CommercialValidationEngine:
    """Final commercial worth gate before export or publish."""

    def __init__(self, db: EtsyDatabase):
        self.db = db
        self.report = CommercialValidationReport()

    def run(
        self,
        session_label: str = "commercial-validation",
        export_dir: str | None = None,
        candidate_rows: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if candidate_rows is not None:
            listing_df = pd.DataFrame(candidate_rows)
        else:
            listing_df = self.db.fetch_dataframe("listing_reports")
            if listing_df.empty:
                listing_df = self.db.fetch_seo_listing_overview(limit=500)
                if listing_df.empty:
                    return {"session_id": None, "rows": [], "report": {}, "exports": {}}

        session_id = self.db.save_research_session(
            {
                "session_label": session_label,
                "sources": ["seo_intelligence", "design_intelligence", "product_intelligence", "niche_intelligence", "research_engine"],
                "status": "running",
            }
        )

        niche_df = self.db.fetch_niche_intelligence_overview()
        product_df = self.db.fetch_product_intelligence_recommendations(limit=500)
        design_df = self.db.fetch_design_intelligence_overview(limit=500)
        research_df = self.db.fetch_opportunity_overview(limit=500)

        niche_lookup = {str(row["niche_name"]): row for _, row in niche_df.iterrows()}
        product_lookup = {(str(row["niche_name"]), str(row["recommended_product"])): row for _, row in product_df.iterrows()}
        design_lookup = {(str(row["niche_name"]), str(row["product_name"])): row for _, row in design_df.iterrows()}
        research_lookup = {str(row["niche_name"]): row for _, row in research_df.iterrows()}

        rows: list[dict[str, Any]] = []
        try:
            for _, listing_row in listing_df.iterrows():
                listing = listing_row.to_dict()
                result = self._process_candidate(
                    session_id=session_id,
                    listing=listing,
                    niche_row=niche_lookup.get(str(listing.get("niche_name", "")), {}),
                    product_row=product_lookup.get((str(listing.get("niche_name", "")), str(listing.get("product_name", ""))), {}),
                    design_row=design_lookup.get((str(listing.get("niche_name", "")), str(listing.get("product_name", ""))), {}),
                    research_row=research_lookup.get(str(listing.get("niche_name", "")), {}),
                )
                rows.append(result)

            report = self.report.generate(rows)
            exports: dict[str, str] = {}
            if export_dir:
                exports = self.report.export(report, rows=rows, export_dir=export_dir, prefix=f"session_{session_id}")

            self.db.save_market_report(
                {
                    "session_id": session_id,
                    "report_name": "commercial_validation_report",
                    "report_payload": report,
                }
            )
            self.db.close_research_session(session_id, status="completed", summary=f"Validated {len(rows)} commercial candidates")
            return {"session_id": session_id, "rows": rows, "report": report, "exports": exports}
        except Exception as exc:
            LOGGER.exception("Commercial validation failed")
            self.db.close_research_session(session_id, status="failed", summary=str(exc))
            raise

    def _process_candidate(
        self,
        *,
        session_id: int,
        listing: dict[str, Any],
        niche_row: dict[str, Any],
        product_row: dict[str, Any],
        design_row: dict[str, Any],
        research_row: dict[str, Any],
    ) -> dict[str, Any]:
        niche_name = str(listing.get("niche_name", ""))
        product_name = str(listing.get("product_name", ""))
        listing_payload = listing.get("listing_payload", {})
        if isinstance(listing_payload, str):
            try:
                listing_payload = json.loads(listing_payload)
            except json.JSONDecodeError:
                listing_payload = {}
        if not isinstance(listing_payload, dict):
            listing_payload = {}

        normalized_listing = dict(listing)
        normalized_listing.update(listing_payload)

        title = str(normalized_listing.get("selected_title") or normalized_listing.get("title") or product_name)
        description = str(normalized_listing.get("description") or "")
        tags_value = normalized_listing.get("tags") or []
        if isinstance(tags_value, str):
            try:
                tags_value = json.loads(tags_value)
            except json.JSONDecodeError:
                tags_value = [token.strip() for token in tags_value.split(",") if token.strip()]
        tags = list(tags_value) if isinstance(tags_value, list) else []

        normalized_listing.update({"title": title, "description": description, "tags": tags})

        validation = validate_candidate(normalized_listing)

        product_score = float(product_row.get("score") or listing.get("product_score") or 60.0)
        design_score = float(design_row.get("overall_design_score") or listing.get("design_score") or 60.0)
        research_score = float(research_row.get("opportunity_score") or listing.get("research_demand") or 50.0)
        niche_score = float(niche_row.get("overall_score") or listing.get("niche_score") or 50.0)
        gift_score = float(niche_row.get("gift_suitability") or listing.get("gift_score") or 50.0)
        competition_score = float(niche_row.get("competition_score") or listing.get("competition_score") or 50.0)
        trend_signal = float(niche_row.get("confidence") or listing.get("buyer_intent_score") or 50.0)
        evergreen_potential = 85.0 if str(niche_row.get("evergreen_classification") or "").lower() == "evergreen" else 65.0
        seasonal_fit = 80.0 if int(listing.get("seasonal") or niche_row.get("seasonal") or 0) == 1 else 55.0

        buyer_psychology = analyze_buyer_psychology(
            title=title,
            gift_score=gift_score,
            emotional_appeal=design_score,
            brand_potential=design_score,
        )
        gap = analyze_competitor_gap(
            competition_score=competition_score,
            product_score=product_score,
            design_score=design_score,
            originality_score=float(listing.get("originality_score") or 65.0),
        )
        pricing = validate_pricing(
            suggested_retail_price=float(listing.get("suggested_selling_price") or listing.get("price") or 24.0),
            estimated_profit_margin=float(listing.get("estimated_margin_percent") or listing.get("estimated_profit_margin") or 50.0),
            premium_position=float(listing.get("suggested_selling_price") or 24.0) >= 30.0,
            budget_position=float(listing.get("suggested_selling_price") or 24.0) <= 20.0,
        )
        buyer_intent_payload = listing.get("buyer_intent", {})
        if isinstance(buyer_intent_payload, str):
            try:
                buyer_intent_payload = json.loads(buyer_intent_payload)
            except json.JSONDecodeError:
                buyer_intent_payload = {}
        if not isinstance(buyer_intent_payload, dict):
            buyer_intent_payload = {}

        gift_validation = validate_gift_potential(
            niche_name=niche_name,
            buyer_intent=str(buyer_intent_payload.get("intent", "Personal")),
            gift_score=gift_score,
        )
        trend_validation = validate_trend_fit(
            seasonal_fit=seasonal_fit,
            evergreen_potential=evergreen_potential,
            trend_signal=trend_signal,
        )

        score_bundle = calculate_commercial_score(
            commercial_potential=max(0.0, min(100.0, (research_score + niche_score + product_score + design_score) / 4.0)),
            buyer_intent=buyer_psychology["would_buy"],
            gift_potential=gift_validation["gift_potential_score"],
            emotional_appeal=design_score,
            visual_appeal=design_score,
            originality=max(0.0, min(100.0, 100.0 - competition_score * 0.2 + gap["stand_out_score"] * 0.5)),
            competition_strength=max(0.0, min(100.0, 100.0 - competition_score)),
            pricing_logic=pricing["pricing_logic_score"],
            estimated_profit=float(listing.get("estimated_gross_profit") or listing.get("estimated_margin_percent") or 50.0),
            seasonal_fit=trend_validation["trend_fit_score"],
            evergreen_potential=evergreen_potential,
            brand_potential=design_score,
        )

        composite_risk = max(0.0, 100.0 - score_bundle["commercial_score"])
        suggestions = list(dict.fromkeys(
            gap["improvements"]
            + (["Improve buyer intent alignment"] if buyer_psychology["would_buy"] < 60 else [])
            + (["Rework pricing or position"] if pricing["pricing_logic_score"] < 60 else [])
            + (["Strengthen gift angle"] if gift_validation["gift_fit"] is False else [])
            + (["Improve seasonal or evergreen relevance"] if trend_validation["trend_fit_score"] < 60 else [])
        ))
        reasons = []
        if validation["warnings"]:
            reasons.extend(validation["warnings"])
        if score_bundle["commercial_score"] < 70:
            reasons.append("Commercial score below threshold")
        if composite_risk > 40:
            reasons.append("Risk score too high for safe publish")

        publish = decide_publish(
            commercial_score=score_bundle["commercial_score"],
            risk_score=composite_risk,
            confidence_score=score_bundle["confidence_score"],
        )

        self.db.save_commercial_score(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "commercial_potential": max(0.0, min(100.0, (research_score + niche_score + product_score + design_score) / 4.0)),
                "buyer_intent": buyer_psychology["would_buy"],
                "gift_potential": gift_validation["gift_potential_score"],
                "emotional_appeal": design_score,
                "visual_appeal": design_score,
                "originality": max(0.0, min(100.0, 100.0 - competition_score * 0.2 + gap["stand_out_score"] * 0.5)),
                "competition_strength": max(0.0, min(100.0, 100.0 - competition_score)),
                "pricing_logic": pricing["pricing_logic_score"],
                "estimated_profit": float(listing.get("estimated_gross_profit") or listing.get("estimated_margin_percent") or 50.0),
                "seasonal_fit": trend_validation["trend_fit_score"],
                "evergreen_potential": evergreen_potential,
                "brand_potential": design_score,
                **score_bundle,
            }
        )
        self.db.save_publish_decision(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "publish_decision": publish["decision"],
                "reasons": reasons[:5],
                "recommendations": publish["recommendations"][:5] + suggestions[:5],
                "priority_level": publish["priority_level"],
                "commercial_score": score_bundle["commercial_score"],
                "confidence_score": score_bundle["confidence_score"],
                "risk_score": composite_risk,
                "estimated_success_level": score_bundle["estimated_success_level"],
            }
        )
        self.db.save_commercial_report(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "report_payload": {
                    "validation": validation,
                    "gap": gap,
                    "buyer_psychology": buyer_psychology,
                    "pricing": pricing,
                    "gift_validation": gift_validation,
                    "trend_validation": trend_validation,
                    "scores": score_bundle,
                    "publish": publish,
                },
            }
        )

        return {
            "session_id": session_id,
            "niche_name": niche_name,
            "product_name": product_name,
            "commercial_score": score_bundle["commercial_score"],
            "confidence_score": score_bundle["confidence_score"],
            "risk_score": round(composite_risk, 2),
            "estimated_success_level": score_bundle["estimated_success_level"],
            "publish_decision": publish["decision"],
            "reasons": reasons[:5],
            "recommendations": (publish["recommendations"] + suggestions)[:5],
            "competitor_gap": gap,
            "buyer_psychology": buyer_psychology,
            "pricing_validation": pricing,
            "gift_validation": gift_validation,
            "trend_validation": trend_validation,
            "validation": validation,
        }
