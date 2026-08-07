from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from database.db import EtsyDatabase
from research.engine import ResearchEngine
from utils.config import load_config
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


def _build_result_payload(niche_name: str, package: Any) -> dict[str, Any]:
    niche_row = {
        "niche_name": package.niche.niche_name,
        "demand_score": package.niche.demand_score,
        "competition_score": package.niche.competition_score,
        "profit_potential": package.niche.profit_potential,
        "design_difficulty": package.niche.design_difficulty,
        "pod_compatibility": package.niche.pod_compatibility,
        "opportunity_score": package.niche.opportunity_score,
        "market_data": package.niche.market_data,
    }
    return {
        "niche": niche_row,
        "product": asdict(package.product),
        "design": asdict(package.design),
        "listing": asdict(package.listing),
        "niche_name": niche_name,
    }


def daily_product_discovery(config_path: str | Path = "config.yaml") -> list[dict[str, Any]]:
    config = load_config(config_path)
    db = EtsyDatabase(config["app"]["database_path"])
    db.initialize()

    engine = ResearchEngine()
    results: list[dict[str, Any]] = []
    for niche in config.get("research", {}).get("search_terms", []):
        try:
            package = engine.build_opportunity_package(niche)
            payload = _build_result_payload(niche, package)

            db.save_niche(payload["niche"])
            db.save_product(
                {
                    "niche_name": niche,
                    "product_name": package.product.product_name,
                    "score": package.product.score,
                    "rationale": package.product.rationale,
                }
            )
            db.save_design(
                {
                    "niche_name": niche,
                    "product_name": package.product.product_name,
                    "design_prompt": package.design.prompt,
                    "style": package.design.style,
                    "colors": package.design.colors,
                }
            )
            db.save_listing(
                {
                    "niche_name": niche,
                    "product_name": package.product.product_name,
                    "title": package.listing.title,
                    "description": package.listing.description,
                    "tags": package.listing.tags,
                    "category": package.listing.category,
                    "price": package.listing.price,
                    "keywords": package.listing.keywords,
                }
            )
            db.save_research_history("daily_product_discovery", payload)
            results.append(payload)
        except Exception as exc:
            LOGGER.exception("Nis islenirken hata olustu: %s", niche)
            results.append({"niche_name": niche, "error": str(exc)})

    LOGGER.info("Daily discovery completed for %s niches", len(results))
    return results
