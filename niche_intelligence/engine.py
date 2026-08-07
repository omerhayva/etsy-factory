from __future__ import annotations

from typing import Any

from database.db import EtsyDatabase
from niche_intelligence.audience import analyze_audience
from niche_intelligence.competition import analyze_competition
from niche_intelligence.evergreen import analyze_evergreen
from niche_intelligence.giftability import analyze_giftability
from niche_intelligence.recommendations import build_recommendation
from niche_intelligence.report_generator import NicheIntelligenceReportGenerator
from niche_intelligence.scoring import ScoreComponents, calculate_niche_score, classify_niche
from niche_intelligence.seasonality import analyze_seasonality
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


class NicheIntelligenceEngine:
    """Transforms research signals into business-grade niche decisions."""

    def __init__(self, db: EtsyDatabase):
        self.db = db
        self.report_generator = NicheIntelligenceReportGenerator()

    def run(self, session_label: str = "niche-intelligence", export_dir: str | None = None) -> dict[str, Any]:
        opportunity_df = self.db.fetch_opportunity_overview(limit=500)
        if opportunity_df.empty:
            return {"session_id": None, "rows": [], "report": {}, "exports": {}}

        session_id = self.db.save_research_session(
            {
                "session_label": session_label,
                "sources": ["niche_intelligence"],
                "status": "running",
            }
        )

        rows: list[dict[str, Any]] = []
        try:
            for _, row in opportunity_df.iterrows():
                intelligence = self._process_row(session_id, row.to_dict())
                rows.append(intelligence)

            report = self.report_generator.generate(rows)
            exports: dict[str, str] = {}
            if export_dir:
                exports = self.report_generator.export(report, export_dir=export_dir, prefix=f"session_{session_id}")

            self.db.save_market_report(
                {
                    "session_id": session_id,
                    "report_name": "niche_intelligence_report",
                    "report_payload": report,
                }
            )
            self.db.close_research_session(session_id, status="completed", summary=f"Scored {len(rows)} niches")
            return {"session_id": session_id, "rows": rows, "report": report, "exports": exports}
        except Exception as exc:
            LOGGER.exception("Niche intelligence engine failed")
            self.db.close_research_session(session_id, status="failed", summary=str(exc))
            raise

    def _process_row(self, session_id: int, source_row: dict[str, Any]) -> dict[str, Any]:
        niche_name = str(source_row.get("niche_name", "unknown niche"))
        demand = float(source_row.get("opportunity_score", 50))
        competition_score = float(source_row.get("competition_score", 50))
        profit = float(source_row.get("profit_potential", 50))
        trend = float(source_row.get("confidence_score", 50))
        design_simplicity = max(0.0, min(100.0, 100.0 - float(source_row.get("competition_score", 50)) * 0.35))

        audience = analyze_audience(niche_name)
        seasonality = analyze_seasonality(niche_name)
        competition = analyze_competition(niche_name, competition_score)
        giftability = analyze_giftability(niche_name)
        evergreen = analyze_evergreen(niche_name, trend, seasonality.seasonal)

        evergreen_score = {
            "Evergreen": 85.0,
            "Seasonal": 60.0,
            "Trending": 78.0,
            "Temporary": 45.0,
            "Declining": 20.0,
        }.get(evergreen.classification, 50.0)

        overall_score, confidence, risk_level = calculate_niche_score(
            ScoreComponents(
                demand=demand,
                competition=competition.score,
                profit=profit,
                trend=trend,
                gift_potential=giftability.suitability,
                evergreen=evergreen_score,
                design_simplicity=design_simplicity,
                confidence_inputs=len(audience.audiences) + len(audience.buyer_intents),
            )
        )
        classification = classify_niche(overall_score, confidence)

        reasons = [
            f"Demand signal {demand:.1f}",
            f"Competition {competition.label} ({competition.score:.1f})",
            f"Profit potential {profit:.1f}",
            f"Gift suitability {giftability.suitability:.1f}",
            f"Evergreen class {evergreen.classification}",
            f"Audience coverage {len(audience.audiences)} groups",
        ]
        decision = build_recommendation(
            niche_name=niche_name,
            overall_score=overall_score,
            confidence=confidence,
            classification=classification,
            risk_level=risk_level,
            reasons=reasons,
        )

        self.db.save_audience(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "audiences": audience.audiences,
                "buyer_intents": audience.buyer_intents,
            }
        )
        self.db.save_seasonality(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "seasonal": 1 if seasonality.seasonal else 0,
                "season_labels": seasonality.seasons,
                "confidence": seasonality.confidence,
            }
        )
        self.db.save_gift_score(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "gift_suitability": giftability.suitability,
                "gift_occasions": giftability.occasions,
                "target_recipients": giftability.recipients,
                "gift_confidence": giftability.confidence,
            }
        )
        self.db.save_competition_score(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "competition_label": competition.label,
                "competition_score": competition.score,
            }
        )
        self.db.save_evergreen_score(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "evergreen_classification": evergreen.classification,
                "confidence": evergreen.confidence,
            }
        )
        self.db.save_niche_score(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "overall_score": decision.overall_score,
                "confidence": decision.confidence,
                "risk_level": decision.risk_level,
                "classification": decision.classification,
                "recommendation": decision.recommendation,
                "reasoning": decision.reasoning,
                "demand": demand,
                "competition": competition.score,
                "profit": profit,
                "trend": trend,
                "gift_potential": giftability.suitability,
                "evergreen": evergreen_score,
                "design_simplicity": design_simplicity,
            }
        )
        self.db.save_recommendation(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "overall_score": decision.overall_score,
                "classification": decision.classification,
                "reasons": reasons,
                "recommendation": decision.recommendation,
            }
        )

        return {
            "session_id": session_id,
            "niche_name": niche_name,
            "overall_score": decision.overall_score,
            "confidence": decision.confidence,
            "risk_level": decision.risk_level,
            "classification": decision.classification,
            "recommendation": decision.recommendation,
            "reasoning": decision.reasoning,
            "audiences": audience.audiences,
            "buyer_intents": audience.buyer_intents,
            "seasonal": 1 if seasonality.seasonal else 0,
            "season_labels": seasonality.seasons,
            "gift_suitability": giftability.suitability,
            "competition_score": competition.score,
            "competition_label": competition.label,
            "evergreen_classification": evergreen.classification,
            "profit_potential": profit,
        }
