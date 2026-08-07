from pathlib import Path

from dashboard.app import _packages_to_rows
from database.db import EtsyDatabase
from utils.config import load_config


def test_database_initialization_and_insert(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "factory.sqlite3")
    db.initialize()

    niche_id = db.save_niche(
        {
            "niche_name": "vintage dog lover",
            "demand_score": 85,
            "competition_score": 60,
            "profit_potential": 80,
            "design_difficulty": 10,
            "pod_compatibility": 90,
            "opportunity_score": 82,
            "market_data": [],
        }
    )

    assert niche_id > 0
    frame = db.fetch_top_niches()
    assert not frame.empty
    assert frame.iloc[0]["niche_name"] == "vintage dog lover"


def test_database_creates_expected_tables(tmp_path: Path):
    db = EtsyDatabase(tmp_path / "factory.sqlite3")
    db.initialize()

    with db.connection() as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

    table_names = {row["name"] for row in rows}
    assert {
        "niches",
        "products",
        "designs",
        "keywords",
        "listings",
        "research_history",
        "keyword_metrics",
        "competitors",
        "market_reports",
        "price_history",
        "trend_history",
        "reviews",
        "research_sessions",
        "niche_scores",
        "audiences",
        "seasonality",
        "gift_scores",
        "competition_scores",
        "evergreen_scores",
        "recommendations",
        "product_catalog",
        "product_scores",
        "product_profit",
        "product_shipping",
        "product_quality",
        "product_risk",
        "product_recommendations",
        "design_styles",
        "design_scores",
        "color_palettes",
        "typography_profiles",
        "layout_profiles",
        "design_prompts",
        "design_variations",
        "mockup_recommendations",
        "seo_titles",
        "seo_tags",
        "seo_descriptions",
        "listing_scores",
        "listing_quality",
        "policy_checks",
        "spam_reports",
        "buyer_intent",
        "publish_reports",
        "ai_disclosures",
        "listing_reports",
        "commercial_reports",
        "commercial_scores",
        "publish_decisions",
        "factory_runs",
        "pipeline_logs",
        "workflow_reports",
    }.issubset(table_names)


def test_config_loader_uses_defaults_when_missing(tmp_path: Path):
    config_path = tmp_path / "missing-config.yaml"
    config = load_config(config_path)

    assert config["app"]["database_path"]
    assert isinstance(config["research"]["search_terms"], list)


def test_dashboard_rows_support_dict_payloads():
    packages = [
        {
            "niche": {"niche_name": "vintage dog lover"},
            "product": {"product_name": "t-shirt"},
            "design": {"prompt": "retro design prompt"},
            "listing": {
                "title": "Vintage Dog Lover T-Shirt",
                "description": "Sample",
                "tags": ["dog", "vintage"],
            },
        }
    ]

    rows = _packages_to_rows(packages)
    assert len(rows) == 1
    assert rows[0]["product_name"] == "t-shirt"
    assert rows[0]["niche"] == "vintage dog lover"
    assert "dog" in rows[0]["tags"]
