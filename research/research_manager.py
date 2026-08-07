from __future__ import annotations

from dataclasses import asdict
from statistics import mean
from typing import Any

from database.db import EtsyDatabase
from research.base_provider import BaseResearchProvider, CompetitorRecord, KeywordRecord, TrendRecord
from research.competitor_analyzer import CompetitorAnalyzer
from research.keyword_collector import KeywordCollector
from research.market_report import MarketReportGenerator
from research.niche_finder import NicheFinder
from research.opportunity_engine import OpportunityEngine, OpportunityInput
from research.pricing_analyzer import PricingAnalyzer
from research.review_analyzer import ReviewAnalyzer
from research.trend_analyzer import TrendAnalyzer
from scraper.etsy_scraper import EtsyScraper
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


class EtsySearchProvider(BaseResearchProvider):
    """Default provider using current Etsy scraper to bootstrap research intelligence."""

    name = "etsy_search"

    def __init__(self, scraper: EtsyScraper | None = None):
        self.scraper = scraper or EtsyScraper()

    def collect_keywords(self, seed: str, limit: int = 20) -> list[KeywordRecord]:
        base_terms = [term for term in seed.lower().split() if term]
        records: list[KeywordRecord] = []
        for term in base_terms[:limit]:
            records.append(
                KeywordRecord(
                    keyword=f"{seed} {term}",
                    source=self.name,
                    language="en",
                    search_volume=1200 - len(term) * 15,
                    competition=max(10.0, min(95.0, 40.0 + len(seed) * 0.8)),
                    trend="growing" if "vintage" in seed or "gift" in seed else "stable",
                    status="active",
                )
            )
        if not records:
            records.append(KeywordRecord(keyword=seed, source=self.name))
        return records[:limit]

    def collect_competitors(self, seed: str, limit: int = 20) -> list[CompetitorRecord]:
        listings = self.scraper.scrape_search_term(seed, limit=limit)
        competitors: list[CompetitorRecord] = []
        for item in listings:
            competitors.append(
                CompetitorRecord(
                    shop_name=f"shop_{abs(hash(item.title)) % 10000}",
                    product_title=item.title,
                    price=item.price,
                    estimated_popularity=float(item.popularity),
                    review_count=item.reviews,
                    favorite_count=None,
                    product_age_days=None,
                    store_category=item.category,
                    data_source=self.name,
                )
            )
        return competitors

    def collect_trends(self, seed: str, keywords: list[str]) -> list[TrendRecord]:
        records: list[TrendRecord] = []
        for keyword in keywords:
            score = 72.0 if any(token in keyword.lower() for token in ["vintage", "gift", "retro"]) else 52.0
            status = "Growing" if score >= 70 else "Stable"
            records.append(TrendRecord(keyword=keyword, trend_score=score, trend_status=status, source=self.name))
        return records


class ResearchManager:
    """Central orchestrator for multi-provider market research workflows."""

    def __init__(
        self,
        db: EtsyDatabase,
        providers: list[BaseResearchProvider] | None = None,
        categories: list[str] | None = None,
    ):
        self.db = db
        self.providers = providers or [EtsySearchProvider()]
        self.keyword_collector = KeywordCollector(db)
        self.niche_finder = NicheFinder(categories=categories)
        self.trend_analyzer = TrendAnalyzer(db)
        self.competitor_analyzer = CompetitorAnalyzer(db)
        self.pricing_analyzer = PricingAnalyzer()
        self.review_analyzer = ReviewAnalyzer()
        self.opportunity_engine = OpportunityEngine()
        self.report_generator = MarketReportGenerator()

    def run_session(
        self,
        seed_terms: list[str],
        session_label: str = "research-session",
        export_dir: str | None = None,
    ) -> dict[str, Any]:
        session_id = self.db.save_research_session(
            {
                "session_label": session_label,
                "sources": [provider.name for provider in self.providers],
                "status": "running",
            }
        )

        all_keyword_rows: list[dict] = []
        all_opportunities: list[dict[str, Any]] = []

        try:
            for seed in seed_terms:
                keyword_rows = self.keyword_collector.collect(seed, self.providers, session_id=session_id)
                all_keyword_rows.extend(keyword_rows)
                niches = self.niche_finder.discover(keyword_rows)

                for niche in niches:
                    opportunity_row = self._analyze_niche(session_id, seed, niche.niche_name, niche.category)
                    all_opportunities.append(opportunity_row)

            report = self.report_generator.generate(all_opportunities)
            self.db.save_market_report(
                {
                    "session_id": session_id,
                    "report_name": "core_market_report",
                    "report_payload": report,
                }
            )

            exports: dict[str, str] = {}
            if export_dir:
                exported = self.report_generator.export(report, export_dir=export_dir, prefix=f"session_{session_id}")
                exports = {key: str(path) for key, path in exported.items()}

            summary = f"Processed {len(seed_terms)} seeds, {len(all_keyword_rows)} keywords, {len(all_opportunities)} opportunities."
            self.db.close_research_session(session_id, status="completed", summary=summary)
            return {
                "session_id": session_id,
                "keywords": all_keyword_rows,
                "opportunities": all_opportunities,
                "report": report,
                "exports": exports,
                "summary": summary,
            }
        except Exception as exc:
            LOGGER.exception("Research session failed")
            self.db.close_research_session(session_id, status="failed", summary=str(exc))
            raise

    def _analyze_niche(self, session_id: int, seed: str, niche_name: str, category: str) -> dict[str, Any]:
        competitors: list[CompetitorRecord] = []
        trends: list[TrendRecord] = []

        for provider in self.providers:
            competitors.extend(provider.collect_competitors(niche_name, limit=12))
            trends.extend(provider.collect_trends(niche_name, [niche_name]))

        competitor_rows = self.competitor_analyzer.persist(session_id, niche_name, competitors)
        prices = [row["price"] for row in competitor_rows]
        popularity = [row["estimated_popularity"] for row in competitor_rows]
        review_counts = [row["review_count"] for row in competitor_rows]
        titles = [row["product_title"] for row in competitor_rows]

        pricing = self.pricing_analyzer.analyze(prices)
        review_insights = self.review_analyzer.analyze(titles, review_counts)

        trend_scores = []
        for trend in trends:
            trend_record = self.trend_analyzer.store(
                session_id=session_id,
                niche_name=niche_name,
                keyword=trend.keyword,
                source=trend.source,
                score=trend.trend_score,
            )
            trend_scores.append(trend_record.trend_score)

        avg_popularity = float(mean(popularity)) if popularity else 50.0
        avg_reviews = float(mean(review_counts)) if review_counts else 30.0
        trend_score = float(mean(trend_scores)) if trend_scores else 40.0

        demand = max(0.0, min(100.0, avg_popularity + 5.0))
        competition = max(0.0, min(100.0, avg_reviews * 0.9))
        profit_potential = max(0.0, min(100.0, (pricing.avg_price / max(pricing.min_price, 1.0)) * 35.0))
        gift_potential = 80.0 if any(token in niche_name.lower() for token in ["gift", "mom", "dad", "teacher"]) else 55.0
        design_simplicity = 82.0 if any(token in niche_name.lower() for token in ["minimal", "retro", "vintage"]) else 62.0

        opportunity_result = self.opportunity_engine.score(
            OpportunityInput(
                demand=demand,
                competition=competition,
                profit_potential=profit_potential,
                trend=trend_score,
                gift_potential=gift_potential,
                design_simplicity=design_simplicity,
                data_points=len(competitor_rows),
            )
        )

        self.db.save_price_history(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "min_price": pricing.min_price,
                "max_price": pricing.max_price,
                "avg_price": pricing.avg_price,
                "median_price": pricing.median_price,
                "recommended_price": pricing.recommended_selling_price,
            }
        )
        self.db.save_review_analysis(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "review_count": review_insights.review_count,
                "average_rating": review_insights.average_rating,
                "positive_themes": review_insights.positive_themes,
                "negative_themes": review_insights.negative_themes,
                "customer_requests": review_insights.customer_requests,
            }
        )

        niche_row = {
            "session_id": session_id,
            "niche_name": niche_name,
            "category": category,
            "source": ",".join(sorted({provider.name for provider in self.providers})),
            "status": "active",
            "demand_score": int(round(demand)),
            "competition_score": int(round(competition)),
            "profit_potential": int(round(profit_potential)),
            "design_difficulty": int(round(100 - design_simplicity)),
            "pod_compatibility": 90,
            "opportunity_score": opportunity_result.opportunity_score,
            "confidence_score": opportunity_result.confidence_score,
            "reasoning": opportunity_result.reasoning,
            "market_data": competitor_rows,
        }
        self.db.save_niche(niche_row)

        result = dict(niche_row)
        result["trend_score"] = trend_score
        result["gift_potential"] = gift_potential
        result["review_insights"] = asdict(review_insights)
        result["price_insights"] = asdict(pricing)
        return result
