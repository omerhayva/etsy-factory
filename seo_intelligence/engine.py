from __future__ import annotations

from typing import Any

from database.db import EtsyDatabase
from seo_intelligence.ai_disclosure import build_ai_disclosure
from seo_intelligence.buyer_intent import classify_buyer_intent
from seo_intelligence.compliance_engine import ComplianceEngine
from seo_intelligence.description_generator import generate_description
from seo_intelligence.keyword_optimizer import categorize_keywords
from seo_intelligence.listing_optimizer import optimize_listing
from seo_intelligence.listing_quality import evaluate_listing_quality
from seo_intelligence.listing_score import calculate_overall_listing_score
from seo_intelligence.policy_manager import PolicyManager
from seo_intelligence.publish_decision import decide_publish
from seo_intelligence.report_generator import SeoComplianceReportGenerator
from seo_intelligence.tags_generator import generate_tags
from seo_intelligence.title_generator import generate_title_versions
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


class SeoComplianceIntelligenceEngine:
    """Final quality gate for SEO, compliance, and publish readiness."""

    def __init__(self, db: EtsyDatabase, policy_manager: PolicyManager | None = None):
        self.db = db
        self.policy_manager = policy_manager or PolicyManager()
        self.compliance_engine = ComplianceEngine(self.policy_manager)
        self.report_generator = SeoComplianceReportGenerator()

    def run(self, session_label: str = "seo-intelligence", export_dir: str | None = None) -> dict[str, Any]:
        research_df = self.db.fetch_opportunity_overview(limit=500)
        niche_df = self.db.fetch_niche_intelligence_overview()
        product_df = self.db.fetch_product_intelligence_recommendations(limit=500)
        design_df = self.db.fetch_design_intelligence_overview(limit=500)

        if research_df.empty or niche_df.empty or product_df.empty or design_df.empty:
            return {"session_id": None, "rows": [], "report": {}, "exports": {}}

        session_id = self.db.save_research_session(
            {
                "session_label": session_label,
                "sources": [
                    "research_engine",
                    "niche_intelligence",
                    "product_intelligence",
                    "design_intelligence",
                ],
                "status": "running",
            }
        )

        niche_lookup = {str(row["niche_name"]): row for _, row in niche_df.iterrows()}
        research_lookup = {str(row["niche_name"]): row for _, row in research_df.iterrows()}
        design_lookup: dict[tuple[str, str], dict[str, Any]] = {}
        for _, row in design_df.iterrows():
            key = (str(row.get("niche_name", "")), str(row.get("product_name", "")))
            if key not in design_lookup:
                design_lookup[key] = row.to_dict()

        rows: list[dict[str, Any]] = []
        seen_signatures: set[str] = set()

        try:
            for _, product_row in product_df.iterrows():
                row = self._process_row(
                    session_id=session_id,
                    product_row=product_row.to_dict(),
                    niche_row=niche_lookup.get(str(product_row.get("niche_name", "")), {}),
                    research_row=research_lookup.get(str(product_row.get("niche_name", "")), {}),
                    design_row=design_lookup.get(
                        (str(product_row.get("niche_name", "")), str(product_row.get("recommended_product", ""))),
                        {},
                    ),
                    seen_signatures=seen_signatures,
                )
                if row:
                    rows.append(row)

            report = self.report_generator.generate(rows)
            exports: dict[str, str] = {}
            if export_dir:
                exports = self.report_generator.export(report, rows=rows, export_dir=export_dir, prefix=f"session_{session_id}")

            self.db.save_market_report(
                {
                    "session_id": session_id,
                    "report_name": "seo_compliance_intelligence_report",
                    "report_payload": report,
                }
            )
            self.db.close_research_session(session_id, status="completed", summary=f"Evaluated {len(rows)} listing packages")
            return {"session_id": session_id, "rows": rows, "report": report, "exports": exports}
        except Exception as exc:
            LOGGER.exception("SEO Compliance intelligence engine failed")
            self.db.close_research_session(session_id, status="failed", summary=str(exc))
            raise

    def _process_row(
        self,
        *,
        session_id: int,
        product_row: dict[str, Any],
        niche_row: dict[str, Any],
        research_row: dict[str, Any],
        design_row: dict[str, Any],
        seen_signatures: set[str],
    ) -> dict[str, Any] | None:
        niche_name = str(product_row.get("niche_name", "")).strip()
        product_name = str(product_row.get("recommended_product", "")).strip()
        if not niche_name or not product_name:
            return None

        style_name = str(design_row.get("style_name") or "Modern")
        trend_terms = ["gift"] if float(niche_row.get("gift_suitability") or 0) >= 70 else []

        keywords = categorize_keywords(
            niche_name=niche_name,
            product_name=product_name,
            style_name=style_name,
            trend_terms=trend_terms,
        )

        initial_intent = classify_buyer_intent(niche_name, keywords.get("gift", []) + keywords.get("seasonal", []))
        titles = generate_title_versions(
            niche_name=niche_name,
            product_name=product_name,
            keywords=keywords,
            intent=str(initial_intent["intent"]),
        )
        tags = generate_tags(
            niche_name=niche_name,
            product_name=product_name,
            keywords=keywords,
            intent=str(initial_intent["intent"]),
        )
        buyer_intent = classify_buyer_intent(niche_name, tags)

        description = generate_description(
            niche_name=niche_name,
            product_name=product_name,
            style_name=style_name,
            intent=str(buyer_intent["intent"]),
            gift_occasion="gift moments",
            policy_manager=self.policy_manager,
        )

        listing = optimize_listing(
            title_versions=titles,
            description=description,
            tags=tags,
            keyword_categories=keywords,
            buyer_intent=buyer_intent,
        )

        signature = f"{listing['title'].lower()}|{','.join(tags)}"
        duplicate_detected = signature in seen_signatures
        seen_signatures.add(signature)

        compliance = self.compliance_engine.evaluate(listing)
        if duplicate_detected:
            compliance["warnings"].append("Potential duplicate listing detected")
            compliance["suggested_fixes"].append("Regenerate title and tags to increase uniqueness")
            compliance["compliance_score"] = max(0.0, float(compliance["compliance_score"]) - 15.0)

        design_score = float(design_row.get("overall_design_score") or 60.0)
        product_score = float(product_row.get("score") or 60.0)
        quality = evaluate_listing_quality(
            title=listing["title"],
            description=listing["description"],
            tags=tags,
            design_score=design_score,
            product_score=product_score,
            intent_confidence=float(buyer_intent.get("confidence", 50.0)),
        )

        score_bundle = calculate_overall_listing_score(
            quality=quality,
            compliance_score=float(compliance["compliance_score"]),
            spam_score=float(compliance["spam"]["spam_score"]),
        )

        disclosure = build_ai_disclosure(self.policy_manager)
        publish = decide_publish(
            score=float(score_bundle["overall_listing_score"]),
            compliance_score=float(compliance["compliance_score"]),
            risk_level=str(compliance["risk"]["risk_level"]),
            warnings=list(compliance["warnings"]),
            fixes=list(compliance["suggested_fixes"]),
            policy_manager=self.policy_manager,
        )

        self.db.save_seo_title(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "selected_title": listing["title"],
                "title_versions": titles,
                "keyword_payload": keywords,
            }
        )
        self.db.save_seo_tags(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "tags": tags,
            }
        )
        self.db.save_seo_description(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "description": listing["description"],
            }
        )

        self.db.save_listing_quality(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "validation_score": compliance["validation"]["validation_score"],
                "quality_warnings": compliance["warnings"],
                "quality_fixes": compliance["suggested_fixes"],
            }
        )
        self.db.save_policy_check(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "policy_version": compliance["policy"]["policy_version"],
                "policy_score": compliance["policy"]["policy_score"],
                "warnings": compliance["policy"]["warnings"],
                "fixes": compliance["policy"]["suggested_fixes"],
                "passed": 1 if compliance["policy"]["passed"] else 0,
            }
        )
        self.db.save_spam_report(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "spam_score": compliance["spam"]["spam_score"],
                "warnings": compliance["spam"]["warnings"],
                "stuffing_terms": compliance["spam"]["keyword_stuffing"],
                "clickbait_hits": compliance["spam"]["clickbait_hits"],
                "misleading_hits": compliance["spam"]["misleading_hits"],
                "passed": 1 if compliance["spam"]["passed"] else 0,
            }
        )
        self.db.save_buyer_intent(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "intent_label": buyer_intent["intent"],
                "confidence": buyer_intent["confidence"],
                "intent_scores": buyer_intent["intent_scores"],
            }
        )

        self.db.save_listing_score(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "seo_score": quality["seo_score"],
                "compliance_score": score_bundle["compliance_score"],
                "commercial_score": quality["commercial_score"],
                "buyer_intent_score": quality["buyer_intent_score"],
                "gift_score": quality["gift_score"],
                "readability_score": quality["readability_score"],
                "visual_compatibility_score": quality["visual_compatibility_score"],
                "competition_score": quality["competition_score"],
                "originality_score": quality["originality_score"],
                "expected_conversion_score": quality["expected_conversion_score"],
                "trust_score": quality["trust_score"],
                "overall_listing_score": score_bundle["overall_listing_score"],
            }
        )

        self.db.save_publish_report(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "publish_decision": publish["decision"],
                "risk_level": compliance["risk"]["risk_level"],
                "risk_score": compliance["risk"]["risk_score"],
                "priority_level": publish["priority_level"],
                "reasons": publish["reasons"],
                "fixes": publish["suggested_fixes"],
            }
        )
        self.db.save_ai_disclosure(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "disclosure_placeholder": disclosure["placeholder"],
                "disclosure_note": disclosure["note"],
            }
        )

        listing_payload = {
            "niche_name": niche_name,
            "product_name": product_name,
            "style_name": style_name,
            "title": listing["title"],
            "title_versions": listing["title_versions"],
            "description": listing["description"],
            "tags": listing["tags"],
            "buyer_intent": buyer_intent,
            "quality": quality,
            "compliance": compliance,
            "publish": publish,
            "ai_disclosure": disclosure,
        }
        self.db.save_listing_report(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "listing_payload": listing_payload,
            }
        )

        return {
            "session_id": session_id,
            "niche_name": niche_name,
            "product_name": product_name,
            "selected_title": listing["title"],
            "tags": tags,
            "seo_score": quality["seo_score"],
            "compliance_score": score_bundle["compliance_score"],
            "commercial_score": quality["commercial_score"],
            "buyer_intent_score": quality["buyer_intent_score"],
            "gift_score": quality["gift_score"],
            "readability_score": quality["readability_score"],
            "visual_compatibility_score": quality["visual_compatibility_score"],
            "competition_score": quality["competition_score"],
            "originality_score": quality["originality_score"],
            "expected_conversion_score": quality["expected_conversion_score"],
            "trust_score": quality["trust_score"],
            "overall_listing_score": score_bundle["overall_listing_score"],
            "risk_level": compliance["risk"]["risk_level"],
            "risk_score": compliance["risk"]["risk_score"],
            "publish_decision": publish["decision"],
            "priority_level": publish["priority_level"],
            "warnings": compliance["warnings"],
            "suggested_fixes": publish["suggested_fixes"],
            "design_score": design_score,
            "product_score": product_score,
            "research_demand": float(research_row.get("opportunity_score") or 0.0),
        }
