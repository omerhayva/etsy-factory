from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any

from design.generator import DesignBrief, generate_design_prompt
from products.selector import ProductRecommendation, recommend_product
from scoring.engine import OpportunityScores, score_opportunity
from scraper.etsy_scraper import EtsyScraper
from seo.generator import SeoListing, generate_etsy_seo
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


@dataclass(slots=True)
class NicheAnalysis:
    niche_name: str
    demand_score: int
    competition_score: int
    profit_potential: int
    design_difficulty: int
    pod_compatibility: int
    opportunity_score: int
    market_data: list[dict[str, Any]]


@dataclass(slots=True)
class OpportunityPackage:
    niche: NicheAnalysis
    product: ProductRecommendation
    design: DesignBrief
    listing: SeoListing


class ResearchEngine:
    def __init__(self, scraper: EtsyScraper | None = None):
        self.scraper = scraper or EtsyScraper()

    def collect_market_data(self, niche: str, limit: int = 8) -> list[dict[str, Any]]:
        listings = self.scraper.scrape_search_term(niche, limit=limit)
        return [asdict(item) for item in listings]

    def analyze_niche(self, niche: str, market_data: list[dict[str, Any]]) -> NicheAnalysis:
        prices = [float(item.get("price", 0.0)) for item in market_data] or [24.0]
        reviews = [int(item.get("reviews", 0)) for item in market_data] or [0]
        popularity = [int(item.get("popularity", 0)) for item in market_data] or [50]

        avg_price = mean(prices)
        avg_reviews = mean(reviews)
        avg_popularity = mean(popularity)

        demand = min(100, int(avg_popularity + len(market_data) * 2))
        competition = min(100, int(avg_reviews * 1.2 + len(market_data) * 3))
        profit = min(100, int((avg_price / 40.0) * 100 + 30))
        design_difficulty = min(100, 100 - min(90, int(len(niche.split()) * 8 + avg_reviews / 6)))
        pod_compatibility = min(100, int(82 + max(0, 18 - len(niche.split()) * 2)))

        opportunity_score = score_opportunity(
            OpportunityScores(
                demand=demand,
                competition=competition,
                profit=profit,
                design_potential=100 - design_difficulty,
                trend=min(100, int(avg_popularity)),
            )
        )

        return NicheAnalysis(
            niche_name=niche,
            demand_score=demand,
            competition_score=competition,
            profit_potential=profit,
            design_difficulty=design_difficulty,
            pod_compatibility=pod_compatibility,
            opportunity_score=opportunity_score,
            market_data=market_data,
        )

    def build_opportunity_package(self, niche: str, audience: str = "gift buyers", season: str = "all year") -> OpportunityPackage:
        market_data = self.collect_market_data(niche)
        niche_analysis = self.analyze_niche(niche, market_data)
        product = recommend_product(
            niche=niche,
            audience=audience,
            season=season,
            competition=niche_analysis.competition_score,
            profit=niche_analysis.profit_potential,
        )
        design = generate_design_prompt(niche=niche, product_name=product.product_name, audience=audience)
        listing = generate_etsy_seo(niche=niche, product_name=product.product_name, design_prompt=design.prompt, price_hint=24.0)
        return OpportunityPackage(niche=niche_analysis, product=product, design=design, listing=listing)

    def bulk_research(self, niches: list[str]) -> list[OpportunityPackage]:
        return [self.build_opportunity_package(niche) for niche in niches]
