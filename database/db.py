from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterator

import pandas as pd

from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)

ALLOWED_TABLES = {
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
}

TABLE_ORDER_COLUMN = {
    "research_sessions": "started_at",
}


class EtsyDatabase:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS niches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche_name TEXT NOT NULL,
                    demand_score INTEGER NOT NULL,
                    competition_score INTEGER NOT NULL,
                    profit_potential INTEGER NOT NULL,
                    design_difficulty INTEGER NOT NULL,
                    pod_compatibility INTEGER NOT NULL,
                    opportunity_score INTEGER NOT NULL,
                    market_data TEXT,
                    category TEXT,
                    source TEXT,
                    status TEXT,
                    confidence_score REAL,
                    reasoning TEXT,
                    session_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    rationale TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS designs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    design_prompt TEXT NOT NULL,
                    style TEXT,
                    colors TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche_name TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    source TEXT,
                    language TEXT DEFAULT 'en',
                    search_volume INTEGER,
                    competition REAL,
                    trend TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS listings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    category TEXT,
                    price REAL NOT NULL,
                    keywords TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS research_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_label TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS keyword_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    source TEXT NOT NULL,
                    search_volume INTEGER,
                    competition REAL,
                    trend_score REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS competitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT,
                    shop_name TEXT NOT NULL,
                    product_title TEXT NOT NULL,
                    price REAL NOT NULL,
                    estimated_popularity REAL,
                    review_count INTEGER,
                    favorite_count INTEGER,
                    product_age_days INTEGER,
                    store_category TEXT,
                    data_source TEXT NOT NULL,
                    collected_date TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS market_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    report_name TEXT NOT NULL,
                    report_payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    min_price REAL,
                    max_price REAL,
                    avg_price REAL,
                    median_price REAL,
                    recommended_price REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS trend_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT,
                    keyword TEXT,
                    trend_status TEXT NOT NULL,
                    trend_score REAL,
                    source TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT,
                    review_count INTEGER,
                    average_rating REAL,
                    positive_themes TEXT,
                    negative_themes TEXT,
                    customer_requests TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS research_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_label TEXT NOT NULL,
                    sources TEXT,
                    status TEXT NOT NULL,
                    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    ended_at TEXT,
                    summary TEXT
                );

                CREATE TABLE IF NOT EXISTS niche_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    overall_score INTEGER NOT NULL,
                    confidence INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    reasoning TEXT,
                    demand REAL,
                    competition REAL,
                    profit REAL,
                    trend REAL,
                    gift_potential REAL,
                    evergreen REAL,
                    design_simplicity REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS audiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    audiences TEXT NOT NULL,
                    buyer_intents TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS seasonality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    seasonal INTEGER NOT NULL,
                    season_labels TEXT,
                    confidence REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS gift_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    gift_suitability REAL,
                    gift_occasions TEXT,
                    target_recipients TEXT,
                    gift_confidence REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS competition_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    competition_label TEXT,
                    competition_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS evergreen_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    evergreen_classification TEXT,
                    confidence REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    overall_score INTEGER,
                    classification TEXT,
                    reasons TEXT,
                    recommendation TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS product_catalog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    typical_retail_price REAL,
                    estimated_production_cost REAL,
                    estimated_profit_margin REAL,
                    popularity REAL,
                    gift_potential REAL,
                    customization_difficulty REAL,
                    shipping_complexity REAL,
                    average_processing_time REAL,
                    return_risk REAL,
                    print_area REAL,
                    color_variants INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS product_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    match_score REAL NOT NULL,
                    ranking INTEGER,
                    reasoning TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS product_profit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    suggested_selling_price REAL,
                    estimated_production_cost REAL,
                    estimated_gross_profit REAL,
                    estimated_margin_percent REAL,
                    suggested_discount_min REAL,
                    suggested_discount_max REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS product_shipping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    shipping_difficulty REAL,
                    packaging_complexity REAL,
                    damage_risk REAL,
                    international_suitability REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS product_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    design_visibility REAL,
                    print_quality_expectation REAL,
                    color_flexibility REAL,
                    customer_satisfaction_potential REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS product_risk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    return_risk REAL,
                    complaint_risk REAL,
                    sizing_issue_risk REAL,
                    fragility_risk REAL,
                    seasonality_risk REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS product_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    recommended_product TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    score REAL,
                    reasons TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS design_styles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    style_name TEXT NOT NULL,
                    style_family TEXT,
                    score REAL,
                    trend_alignment REAL,
                    reasoning TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS design_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    style_name TEXT,
                    print_quality REAL,
                    visual_balance REAL,
                    commercial_appeal REAL,
                    gift_appeal REAL,
                    brandability REAL,
                    readability REAL,
                    production_suitability REAL,
                    overall_design_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS color_palettes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    palette_name TEXT NOT NULL,
                    primary_colors TEXT,
                    secondary_colors TEXT,
                    accent_colors TEXT,
                    rationale TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS typography_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    primary_font_style TEXT,
                    secondary_font_style TEXT,
                    hierarchy TEXT,
                    rationale TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS layout_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    layout_type TEXT,
                    composition_profile TEXT,
                    image_text_ratio REAL,
                    whitespace_level REAL,
                    icon_placement TEXT,
                    border_usage TEXT,
                    frame_usage TEXT,
                    rationale TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS design_prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    negative_prompt TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS design_variations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    variation_type TEXT NOT NULL,
                    style_name TEXT,
                    prompt TEXT,
                    score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS mockup_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    mockup_type TEXT NOT NULL,
                    rationale TEXT,
                    priority INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS seo_titles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    selected_title TEXT NOT NULL,
                    title_versions TEXT,
                    keyword_payload TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS seo_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS seo_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS listing_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    seo_score REAL,
                    compliance_score REAL,
                    commercial_score REAL,
                    buyer_intent_score REAL,
                    gift_score REAL,
                    readability_score REAL,
                    visual_compatibility_score REAL,
                    competition_score REAL,
                    originality_score REAL,
                    expected_conversion_score REAL,
                    trust_score REAL,
                    overall_listing_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS listing_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    validation_score REAL,
                    quality_warnings TEXT,
                    quality_fixes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS policy_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    policy_version TEXT,
                    policy_score REAL,
                    warnings TEXT,
                    fixes TEXT,
                    passed INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS spam_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    spam_score REAL,
                    warnings TEXT,
                    stuffing_terms TEXT,
                    clickbait_hits TEXT,
                    misleading_hits TEXT,
                    passed INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS buyer_intent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    intent_label TEXT,
                    confidence REAL,
                    intent_scores TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS publish_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    publish_decision TEXT,
                    risk_level TEXT,
                    risk_score REAL,
                    priority_level TEXT,
                    reasons TEXT,
                    fixes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS ai_disclosures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    disclosure_placeholder TEXT,
                    disclosure_note TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS listing_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    listing_payload TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS commercial_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    report_payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS commercial_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    commercial_potential REAL,
                    buyer_intent REAL,
                    gift_potential REAL,
                    emotional_appeal REAL,
                    visual_appeal REAL,
                    originality REAL,
                    competition_strength REAL,
                    pricing_logic REAL,
                    estimated_profit REAL,
                    seasonal_fit REAL,
                    evergreen_potential REAL,
                    brand_potential REAL,
                    commercial_score REAL,
                    confidence_score REAL,
                    risk_score REAL,
                    estimated_success_level TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS publish_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    niche_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    publish_decision TEXT,
                    reasons TEXT,
                    recommendations TEXT,
                    priority_level TEXT,
                    commercial_score REAL,
                    confidence_score REAL,
                    risk_score REAL,
                    estimated_success_level TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS factory_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_label TEXT NOT NULL,
                    niche TEXT,
                    audience TEXT,
                    product_category TEXT,
                    language TEXT,
                    market TEXT,
                    status TEXT NOT NULL,
                    summary TEXT,
                    retry_count INTEGER DEFAULT 0,
                    input_payload TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS pipeline_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    step_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    payload TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS workflow_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    niche_name TEXT,
                    product_name TEXT,
                    report_payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            self._ensure_column(conn, "keywords", "source", "TEXT")
            self._ensure_column(conn, "keywords", "language", "TEXT DEFAULT 'en'")
            self._ensure_column(conn, "keywords", "search_volume", "INTEGER")
            self._ensure_column(conn, "keywords", "competition", "REAL")
            self._ensure_column(conn, "keywords", "trend", "TEXT")
            self._ensure_column(conn, "keywords", "status", "TEXT DEFAULT 'active'")

            self._ensure_column(conn, "niches", "category", "TEXT")
            self._ensure_column(conn, "niches", "source", "TEXT")
            self._ensure_column(conn, "niches", "status", "TEXT")
            self._ensure_column(conn, "niches", "confidence_score", "REAL")
            self._ensure_column(conn, "niches", "reasoning", "TEXT")
            self._ensure_column(conn, "niches", "session_id", "INTEGER")

            self._ensure_column(conn, "factory_runs", "retry_count", "INTEGER DEFAULT 0")
            self._ensure_column(conn, "factory_runs", "input_payload", "TEXT")
            self._ensure_column(conn, "factory_runs", "updated_at", "TEXT DEFAULT CURRENT_TIMESTAMP")

    def _ensure_column(self, conn: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        existing_columns = {row[1] for row in rows}
        if column_name not in existing_columns:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")

    def _to_json(self, value: Any) -> str:
        if is_dataclass(value):
            value = asdict(value)
        return json.dumps(value, ensure_ascii=False, default=str)

    def save_niche(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO niches (
                    niche_name, demand_score, competition_score, profit_potential,
                    design_difficulty, pod_compatibility, opportunity_score, market_data,
                    category, source, status, confidence_score, reasoning, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["niche_name"],
                    row["demand_score"],
                    row["competition_score"],
                    row["profit_potential"],
                    row["design_difficulty"],
                    row["pod_compatibility"],
                    row["opportunity_score"],
                    self._to_json(row.get("market_data", [])),
                    row.get("category"),
                    row.get("source"),
                    row.get("status", "active"),
                    row.get("confidence_score"),
                    row.get("reasoning"),
                    row.get("session_id"),
                ),
            )
            return int(cursor.lastrowid)

    def save_keyword(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO keywords (
                    niche_name, keyword, score, source, language,
                    search_volume, competition, trend, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("niche_name", "general"),
                    row["keyword"],
                    row.get("score", 0),
                    row.get("source", "unknown"),
                    row.get("language", "en"),
                    row.get("search_volume"),
                    row.get("competition"),
                    row.get("trend"),
                    row.get("status", "active"),
                ),
            )
            return int(cursor.lastrowid)

    def save_keyword_metric(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO keyword_metrics (
                    keyword, source, search_volume, competition, trend_score, status
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row["keyword"],
                    row.get("source", "unknown"),
                    row.get("search_volume"),
                    row.get("competition"),
                    row.get("trend_score"),
                    row.get("status", "active"),
                ),
            )
            return int(cursor.lastrowid)

    def save_competitor(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO competitors (
                    session_id, niche_name, shop_name, product_title, price,
                    estimated_popularity, review_count, favorite_count,
                    product_age_days, store_category, data_source, collected_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row.get("niche_name"),
                    row["shop_name"],
                    row["product_title"],
                    row["price"],
                    row.get("estimated_popularity"),
                    row.get("review_count"),
                    row.get("favorite_count"),
                    row.get("product_age_days"),
                    row.get("store_category"),
                    row.get("data_source", "unknown"),
                    row.get("collected_date"),
                ),
            )
            return int(cursor.lastrowid)

    def save_price_history(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO price_history (
                    session_id, niche_name, min_price, max_price,
                    avg_price, median_price, recommended_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row.get("min_price"),
                    row.get("max_price"),
                    row.get("avg_price"),
                    row.get("median_price"),
                    row.get("recommended_price"),
                ),
            )
            return int(cursor.lastrowid)

    def save_trend_history(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO trend_history (
                    session_id, niche_name, keyword, trend_status,
                    trend_score, source
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row.get("niche_name"),
                    row.get("keyword"),
                    row["trend_status"],
                    row.get("trend_score"),
                    row.get("source"),
                ),
            )
            return int(cursor.lastrowid)

    def save_review_analysis(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO reviews (
                    session_id, niche_name, review_count, average_rating,
                    positive_themes, negative_themes, customer_requests
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row.get("niche_name"),
                    row.get("review_count"),
                    row.get("average_rating"),
                    self._to_json(row.get("positive_themes", [])),
                    self._to_json(row.get("negative_themes", [])),
                    self._to_json(row.get("customer_requests", [])),
                ),
            )
            return int(cursor.lastrowid)

    def save_market_report(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO market_reports (session_id, report_name, report_payload)
                VALUES (?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["report_name"],
                    self._to_json(row["report_payload"]),
                ),
            )
            return int(cursor.lastrowid)

    def save_audience(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO audiences (session_id, niche_name, audiences, buyer_intents)
                VALUES (?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    self._to_json(row.get("audiences", [])),
                    self._to_json(row.get("buyer_intents", [])),
                ),
            )
            return int(cursor.lastrowid)

    def save_seasonality(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO seasonality (session_id, niche_name, seasonal, season_labels, confidence)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row.get("seasonal", 0),
                    self._to_json(row.get("season_labels", [])),
                    row.get("confidence"),
                ),
            )
            return int(cursor.lastrowid)

    def save_gift_score(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO gift_scores (
                    session_id, niche_name, gift_suitability,
                    gift_occasions, target_recipients, gift_confidence
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row.get("gift_suitability"),
                    self._to_json(row.get("gift_occasions", [])),
                    self._to_json(row.get("target_recipients", [])),
                    row.get("gift_confidence"),
                ),
            )
            return int(cursor.lastrowid)

    def save_competition_score(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO competition_scores (session_id, niche_name, competition_label, competition_score)
                VALUES (?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row.get("competition_label"),
                    row.get("competition_score"),
                ),
            )
            return int(cursor.lastrowid)

    def save_evergreen_score(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO evergreen_scores (session_id, niche_name, evergreen_classification, confidence)
                VALUES (?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row.get("evergreen_classification"),
                    row.get("confidence"),
                ),
            )
            return int(cursor.lastrowid)

    def save_niche_score(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO niche_scores (
                    session_id, niche_name, overall_score, confidence, risk_level,
                    classification, recommendation, reasoning, demand, competition,
                    profit, trend, gift_potential, evergreen, design_simplicity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["overall_score"],
                    row["confidence"],
                    row["risk_level"],
                    row["classification"],
                    row["recommendation"],
                    row.get("reasoning"),
                    row.get("demand"),
                    row.get("competition"),
                    row.get("profit"),
                    row.get("trend"),
                    row.get("gift_potential"),
                    row.get("evergreen"),
                    row.get("design_simplicity"),
                ),
            )
            return int(cursor.lastrowid)

    def save_recommendation(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO recommendations (
                    session_id, niche_name, overall_score,
                    classification, reasons, recommendation
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row.get("overall_score"),
                    row.get("classification"),
                    self._to_json(row.get("reasons", [])),
                    row.get("recommendation"),
                ),
            )
            return int(cursor.lastrowid)

    def save_product_catalog_item(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO product_catalog (
                    provider, product_name, category, subcategory, typical_retail_price,
                    estimated_production_cost, estimated_profit_margin, popularity,
                    gift_potential, customization_difficulty, shipping_complexity,
                    average_processing_time, return_risk, print_area, color_variants
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["provider"],
                    row["product_name"],
                    row["category"],
                    row.get("subcategory"),
                    row.get("typical_retail_price"),
                    row.get("estimated_production_cost"),
                    row.get("estimated_profit_margin"),
                    row.get("popularity"),
                    row.get("gift_potential"),
                    row.get("customization_difficulty"),
                    row.get("shipping_complexity"),
                    row.get("average_processing_time"),
                    row.get("return_risk"),
                    row.get("print_area"),
                    row.get("color_variants"),
                ),
            )
            return int(cursor.lastrowid)

    def save_product_score(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO product_scores (
                    session_id, niche_name, product_name, provider,
                    match_score, ranking, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row["provider"],
                    row["match_score"],
                    row.get("ranking"),
                    row.get("reasoning"),
                ),
            )
            return int(cursor.lastrowid)

    def save_product_profit(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO product_profit (
                    session_id, niche_name, product_name, suggested_selling_price,
                    estimated_production_cost, estimated_gross_profit,
                    estimated_margin_percent, suggested_discount_min, suggested_discount_max
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("suggested_selling_price"),
                    row.get("estimated_production_cost"),
                    row.get("estimated_gross_profit"),
                    row.get("estimated_margin_percent"),
                    row.get("suggested_discount_min"),
                    row.get("suggested_discount_max"),
                ),
            )
            return int(cursor.lastrowid)

    def save_product_shipping(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO product_shipping (
                    session_id, niche_name, product_name, shipping_difficulty,
                    packaging_complexity, damage_risk, international_suitability
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("shipping_difficulty"),
                    row.get("packaging_complexity"),
                    row.get("damage_risk"),
                    row.get("international_suitability"),
                ),
            )
            return int(cursor.lastrowid)

    def save_product_quality(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO product_quality (
                    session_id, niche_name, product_name, design_visibility,
                    print_quality_expectation, color_flexibility, customer_satisfaction_potential
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("design_visibility"),
                    row.get("print_quality_expectation"),
                    row.get("color_flexibility"),
                    row.get("customer_satisfaction_potential"),
                ),
            )
            return int(cursor.lastrowid)

    def save_product_risk(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO product_risk (
                    session_id, niche_name, product_name, return_risk,
                    complaint_risk, sizing_issue_risk, fragility_risk, seasonality_risk
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("return_risk"),
                    row.get("complaint_risk"),
                    row.get("sizing_issue_risk"),
                    row.get("fragility_risk"),
                    row.get("seasonality_risk"),
                ),
            )
            return int(cursor.lastrowid)

    def save_product_recommendation(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO product_recommendations (
                    session_id, niche_name, recommended_product, provider, score, reasons
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["recommended_product"],
                    row["provider"],
                    row.get("score"),
                    self._to_json(row.get("reasons", [])),
                ),
            )
            return int(cursor.lastrowid)

    def save_design_style(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO design_styles (
                    session_id, niche_name, product_name, style_name,
                    style_family, score, trend_alignment, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row["style_name"],
                    row.get("style_family"),
                    row.get("score"),
                    row.get("trend_alignment"),
                    row.get("reasoning"),
                ),
            )
            return int(cursor.lastrowid)

    def save_design_score(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO design_scores (
                    session_id, niche_name, product_name, style_name,
                    print_quality, visual_balance, commercial_appeal,
                    gift_appeal, brandability, readability,
                    production_suitability, overall_design_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("style_name"),
                    row.get("print_quality"),
                    row.get("visual_balance"),
                    row.get("commercial_appeal"),
                    row.get("gift_appeal"),
                    row.get("brandability"),
                    row.get("readability"),
                    row.get("production_suitability"),
                    row.get("overall_design_score"),
                ),
            )
            return int(cursor.lastrowid)

    def save_color_palette(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO color_palettes (
                    session_id, niche_name, product_name, palette_name,
                    primary_colors, secondary_colors, accent_colors, rationale
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row["palette_name"],
                    self._to_json(row.get("primary_colors", [])),
                    self._to_json(row.get("secondary_colors", [])),
                    self._to_json(row.get("accent_colors", [])),
                    row.get("rationale"),
                ),
            )
            return int(cursor.lastrowid)

    def save_typography_profile(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO typography_profiles (
                    session_id, niche_name, product_name,
                    primary_font_style, secondary_font_style,
                    hierarchy, rationale
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("primary_font_style"),
                    row.get("secondary_font_style"),
                    row.get("hierarchy"),
                    row.get("rationale"),
                ),
            )
            return int(cursor.lastrowid)

    def save_layout_profile(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO layout_profiles (
                    session_id, niche_name, product_name, layout_type,
                    composition_profile, image_text_ratio, whitespace_level,
                    icon_placement, border_usage, frame_usage, rationale
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("layout_type"),
                    row.get("composition_profile"),
                    row.get("image_text_ratio"),
                    row.get("whitespace_level"),
                    row.get("icon_placement"),
                    row.get("border_usage"),
                    row.get("frame_usage"),
                    row.get("rationale"),
                ),
            )
            return int(cursor.lastrowid)

    def save_design_prompt_record(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO design_prompts (
                    session_id, niche_name, product_name,
                    provider, prompt, negative_prompt
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row["provider"],
                    row["prompt"],
                    row.get("negative_prompt"),
                ),
            )
            return int(cursor.lastrowid)

    def save_design_variation(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO design_variations (
                    session_id, niche_name, product_name,
                    variation_type, style_name, prompt, score
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row["variation_type"],
                    row.get("style_name"),
                    row.get("prompt"),
                    row.get("score"),
                ),
            )
            return int(cursor.lastrowid)

    def save_mockup_recommendation(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO mockup_recommendations (
                    session_id, niche_name, product_name,
                    mockup_type, rationale, priority
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row["mockup_type"],
                    row.get("rationale"),
                    row.get("priority"),
                ),
            )
            return int(cursor.lastrowid)

    def save_seo_title(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO seo_titles (
                    session_id, niche_name, product_name,
                    selected_title, title_versions, keyword_payload
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row["selected_title"],
                    self._to_json(row.get("title_versions", [])),
                    self._to_json(row.get("keyword_payload", {})),
                ),
            )
            return int(cursor.lastrowid)

    def save_seo_tags(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO seo_tags (
                    session_id, niche_name, product_name, tags
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    self._to_json(row.get("tags", [])),
                ),
            )
            return int(cursor.lastrowid)

    def save_seo_description(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO seo_descriptions (
                    session_id, niche_name, product_name, description
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row["description"],
                ),
            )
            return int(cursor.lastrowid)

    def save_listing_score(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO listing_scores (
                    session_id, niche_name, product_name,
                    seo_score, compliance_score, commercial_score,
                    buyer_intent_score, gift_score, readability_score,
                    visual_compatibility_score, competition_score,
                    originality_score, expected_conversion_score,
                    trust_score, overall_listing_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("seo_score"),
                    row.get("compliance_score"),
                    row.get("commercial_score"),
                    row.get("buyer_intent_score"),
                    row.get("gift_score"),
                    row.get("readability_score"),
                    row.get("visual_compatibility_score"),
                    row.get("competition_score"),
                    row.get("originality_score"),
                    row.get("expected_conversion_score"),
                    row.get("trust_score"),
                    row.get("overall_listing_score"),
                ),
            )
            return int(cursor.lastrowid)

    def save_listing_quality(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO listing_quality (
                    session_id, niche_name, product_name,
                    validation_score, quality_warnings, quality_fixes
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("validation_score"),
                    self._to_json(row.get("quality_warnings", [])),
                    self._to_json(row.get("quality_fixes", [])),
                ),
            )
            return int(cursor.lastrowid)

    def save_policy_check(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO policy_checks (
                    session_id, niche_name, product_name,
                    policy_version, policy_score, warnings,
                    fixes, passed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("policy_version"),
                    row.get("policy_score"),
                    self._to_json(row.get("warnings", [])),
                    self._to_json(row.get("fixes", [])),
                    row.get("passed", 0),
                ),
            )
            return int(cursor.lastrowid)

    def save_spam_report(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO spam_reports (
                    session_id, niche_name, product_name,
                    spam_score, warnings, stuffing_terms,
                    clickbait_hits, misleading_hits, passed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("spam_score"),
                    self._to_json(row.get("warnings", [])),
                    self._to_json(row.get("stuffing_terms", [])),
                    self._to_json(row.get("clickbait_hits", [])),
                    self._to_json(row.get("misleading_hits", [])),
                    row.get("passed", 0),
                ),
            )
            return int(cursor.lastrowid)

    def save_buyer_intent(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO buyer_intent (
                    session_id, niche_name, product_name,
                    intent_label, confidence, intent_scores
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("intent_label"),
                    row.get("confidence"),
                    self._to_json(row.get("intent_scores", {})),
                ),
            )
            return int(cursor.lastrowid)

    def save_publish_report(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO publish_reports (
                    session_id, niche_name, product_name,
                    publish_decision, risk_level, risk_score,
                    priority_level, reasons, fixes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("publish_decision"),
                    row.get("risk_level"),
                    row.get("risk_score"),
                    row.get("priority_level"),
                    self._to_json(row.get("reasons", [])),
                    self._to_json(row.get("fixes", [])),
                ),
            )
            return int(cursor.lastrowid)

    def save_ai_disclosure(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO ai_disclosures (
                    session_id, niche_name, product_name,
                    disclosure_placeholder, disclosure_note
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("disclosure_placeholder"),
                    row.get("disclosure_note"),
                ),
            )
            return int(cursor.lastrowid)

    def save_listing_report(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO listing_reports (
                    session_id, niche_name, product_name, listing_payload
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    self._to_json(row.get("listing_payload", {})),
                ),
            )
            return int(cursor.lastrowid)

    def save_commercial_report(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO commercial_reports (
                    session_id, niche_name, product_name, report_payload
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    self._to_json(row.get("report_payload", {})),
                ),
            )
            return int(cursor.lastrowid)

    def save_commercial_score(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO commercial_scores (
                    session_id, niche_name, product_name,
                    commercial_potential, buyer_intent, gift_potential,
                    emotional_appeal, visual_appeal, originality,
                    competition_strength, pricing_logic, estimated_profit,
                    seasonal_fit, evergreen_potential, brand_potential,
                    commercial_score, confidence_score, risk_score,
                    estimated_success_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("commercial_potential"),
                    row.get("buyer_intent"),
                    row.get("gift_potential"),
                    row.get("emotional_appeal"),
                    row.get("visual_appeal"),
                    row.get("originality"),
                    row.get("competition_strength"),
                    row.get("pricing_logic"),
                    row.get("estimated_profit"),
                    row.get("seasonal_fit"),
                    row.get("evergreen_potential"),
                    row.get("brand_potential"),
                    row.get("commercial_score"),
                    row.get("confidence_score"),
                    row.get("risk_score"),
                    row.get("estimated_success_level"),
                ),
            )
            return int(cursor.lastrowid)

    def save_publish_decision(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO publish_decisions (
                    session_id, niche_name, product_name, publish_decision,
                    reasons, recommendations, priority_level, commercial_score,
                    confidence_score, risk_score, estimated_success_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row.get("session_id"),
                    row["niche_name"],
                    row["product_name"],
                    row.get("publish_decision"),
                    self._to_json(row.get("reasons", [])),
                    self._to_json(row.get("recommendations", [])),
                    row.get("priority_level"),
                    row.get("commercial_score"),
                    row.get("confidence_score"),
                    row.get("risk_score"),
                    row.get("estimated_success_level"),
                ),
            )
            return int(cursor.lastrowid)

    def save_factory_run(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO factory_runs (
                    session_label, niche, audience, product_category,
                    language, market, status, summary, retry_count, input_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["session_label"],
                    row.get("niche"),
                    row.get("audience"),
                    row.get("product_category"),
                    row.get("language"),
                    row.get("market"),
                    row.get("status", "running"),
                    row.get("summary"),
                    row.get("retry_count", 0),
                    self._to_json(row.get("input_payload", {})),
                ),
            )
            return int(cursor.lastrowid)

    def update_factory_run(self, row: dict[str, Any]) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE factory_runs
                SET status = ?, summary = ?, retry_count = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    row.get("status", "completed"),
                    row.get("summary"),
                    row.get("retry_count", 0),
                    row["id"],
                ),
            )

    def save_pipeline_log(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO pipeline_logs (
                    run_id, step_name, status, message, payload
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row.get("run_id"),
                    row["step_name"],
                    row.get("status", "running"),
                    row.get("message"),
                    self._to_json(row.get("payload", {})),
                ),
            )
            return int(cursor.lastrowid)

    def save_workflow_report(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO workflow_reports (
                    run_id, niche_name, product_name, report_payload
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    row.get("run_id"),
                    row.get("niche_name"),
                    row.get("product_name"),
                    self._to_json(row.get("report_payload", {})),
                ),
            )
            return int(cursor.lastrowid)

    def save_research_session(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO research_sessions (session_label, sources, status, summary)
                VALUES (?, ?, ?, ?)
                """,
                (
                    row["session_label"],
                    self._to_json(row.get("sources", [])),
                    row.get("status", "running"),
                    row.get("summary"),
                ),
            )
            return int(cursor.lastrowid)

    def close_research_session(self, session_id: int, status: str = "completed", summary: str | None = None) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE research_sessions
                SET status = ?, ended_at = CURRENT_TIMESTAMP, summary = ?
                WHERE id = ?
                """,
                (status, summary, session_id),
            )

    def save_product(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO products (niche_name, product_name, score, rationale)
                VALUES (?, ?, ?, ?)
                """,
                (row["niche_name"], row["product_name"], row["score"], row.get("rationale", "")),
            )
            return int(cursor.lastrowid)

    def save_design(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO designs (niche_name, product_name, design_prompt, style, colors)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row["niche_name"],
                    row["product_name"],
                    row["design_prompt"],
                    row.get("style", ""),
                    row.get("colors", ""),
                ),
            )
            return int(cursor.lastrowid)

    def save_listing(self, row: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO listings (niche_name, product_name, title, description, tags, category, price, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["niche_name"],
                    row["product_name"],
                    row["title"],
                    row["description"],
                    self._to_json(row["tags"]),
                    row.get("category", ""),
                    row["price"],
                    self._to_json(row.get("keywords", [])),
                ),
            )
            return int(cursor.lastrowid)

    def save_research_history(self, run_label: str, payload: dict[str, Any]) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO research_history (run_label, payload) VALUES (?, ?)",
                (run_label, self._to_json(payload)),
            )
            return int(cursor.lastrowid)

    def fetch_dataframe(self, table_name: str) -> pd.DataFrame:
        if table_name not in ALLOWED_TABLES:
            raise ValueError(f"Unsupported table name: {table_name}")
        order_column = TABLE_ORDER_COLUMN.get(table_name, "created_at")
        with self.connection() as conn:
            return pd.read_sql_query(f"SELECT * FROM {table_name} ORDER BY {order_column} DESC", conn)

    def fetch_top_niches(self, limit: int = 10) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                "SELECT * FROM niches ORDER BY opportunity_score DESC, created_at DESC LIMIT ?",
                conn,
                params=(limit,),
            )

    def fetch_latest_research_session(self) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                "SELECT * FROM research_sessions ORDER BY started_at DESC LIMIT 1",
                conn,
            )

    def fetch_keyword_overview(self, limit: int = 20) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT
                    keyword,
                    MAX(source) AS source,
                    MAX(language) AS language,
                    AVG(search_volume) AS avg_search_volume,
                    AVG(competition) AS avg_competition,
                    MAX(trend) AS trend,
                    COUNT(*) AS sample_count
                FROM keywords
                GROUP BY keyword
                ORDER BY avg_search_volume DESC, sample_count DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_trend_overview(self) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT trend_status, COUNT(*) AS total
                FROM trend_history
                GROUP BY trend_status
                ORDER BY total DESC
                """,
                conn,
            )

    def fetch_opportunity_overview(self, limit: int = 20) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT
                    niche_name,
                    category,
                    opportunity_score,
                    confidence_score,
                    competition_score,
                    profit_potential,
                    source,
                    status,
                    created_at
                FROM niches
                ORDER BY opportunity_score DESC, confidence_score DESC, created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_niche_intelligence_top(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM niche_scores
                ORDER BY overall_score DESC, confidence DESC, created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_niche_intelligence_overview(self) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT
                    ns.niche_name,
                    ns.overall_score,
                    ns.confidence,
                    ns.risk_level,
                    ns.classification,
                    ns.recommendation,
                    es.evergreen_classification,
                    gs.gift_suitability,
                    cs.competition_label,
                    cs.competition_score,
                    s.seasonal,
                    ns.created_at
                FROM niche_scores ns
                LEFT JOIN evergreen_scores es ON es.session_id = ns.session_id AND es.niche_name = ns.niche_name
                LEFT JOIN gift_scores gs ON gs.session_id = ns.session_id AND gs.niche_name = ns.niche_name
                LEFT JOIN competition_scores cs ON cs.session_id = ns.session_id AND cs.niche_name = ns.niche_name
                LEFT JOIN seasonality s ON s.session_id = ns.session_id AND s.niche_name = ns.niche_name
                ORDER BY ns.overall_score DESC, ns.confidence DESC, ns.created_at DESC
                """,
                conn,
            )

    def fetch_latest_niche_intelligence_session(self) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM research_sessions
                WHERE session_label LIKE 'niche-intelligence%'
                ORDER BY started_at DESC
                LIMIT 1
                """,
                conn,
            )

    def fetch_latest_product_intelligence_session(self) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM research_sessions
                WHERE session_label LIKE 'product-intelligence%'
                ORDER BY started_at DESC
                LIMIT 1
                """,
                conn,
            )

    def fetch_latest_design_intelligence_session(self) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM research_sessions
                WHERE session_label LIKE 'design-intelligence%'
                ORDER BY started_at DESC
                LIMIT 1
                """,
                conn,
            )

    def fetch_product_intelligence_recommendations(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM product_recommendations
                ORDER BY score DESC, created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_product_profit_overview(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM product_profit
                ORDER BY estimated_margin_percent DESC, estimated_gross_profit DESC, created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_product_low_risk(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM product_risk
                ORDER BY return_risk ASC, complaint_risk ASC, fragility_risk ASC, created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_product_gift_ranking(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM product_recommendations
                WHERE LOWER(reasons) LIKE '%gift%'
                ORDER BY score DESC, created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_product_seasonal_opportunities(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT ps.*
                FROM product_scores ps
                INNER JOIN seasonality s ON s.niche_name = ps.niche_name
                WHERE s.seasonal = 1
                ORDER BY ps.match_score DESC, ps.created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_design_intelligence_overview(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT
                    ds.niche_name,
                    ds.product_name,
                    ds.style_name,
                    ds.score AS style_score,
                    cp.palette_name,
                    tp.primary_font_style,
                    lp.layout_type,
                    dsc.overall_design_score,
                    ds.created_at
                FROM design_styles ds
                LEFT JOIN color_palettes cp
                    ON cp.session_id = ds.session_id
                    AND cp.niche_name = ds.niche_name
                    AND cp.product_name = ds.product_name
                LEFT JOIN typography_profiles tp
                    ON tp.session_id = ds.session_id
                    AND tp.niche_name = ds.niche_name
                    AND tp.product_name = ds.product_name
                LEFT JOIN layout_profiles lp
                    ON lp.session_id = ds.session_id
                    AND lp.niche_name = ds.niche_name
                    AND lp.product_name = ds.product_name
                LEFT JOIN design_scores dsc
                    ON dsc.session_id = ds.session_id
                    AND dsc.niche_name = ds.niche_name
                    AND dsc.product_name = ds.product_name
                ORDER BY dsc.overall_design_score DESC, ds.score DESC, ds.created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_design_prompts(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM design_prompts
                ORDER BY created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_design_variations(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM design_variations
                ORDER BY score DESC, created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_mockup_recommendations(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM mockup_recommendations
                ORDER BY priority ASC, created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_latest_seo_intelligence_session(self) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM research_sessions
                WHERE session_label LIKE 'seo-intelligence%'
                ORDER BY started_at DESC
                LIMIT 1
                """,
                conn,
            )

    def fetch_seo_listing_overview(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT
                    st.niche_name,
                    st.product_name,
                    st.selected_title,
                    ls.overall_listing_score,
                    ls.seo_score,
                    ls.compliance_score,
                    pr.publish_decision,
                    pr.risk_level,
                    st.created_at
                FROM seo_titles st
                LEFT JOIN listing_scores ls
                    ON ls.session_id = st.session_id
                    AND ls.niche_name = st.niche_name
                    AND ls.product_name = st.product_name
                LEFT JOIN publish_reports pr
                    ON pr.session_id = st.session_id
                    AND pr.niche_name = st.niche_name
                    AND pr.product_name = st.product_name
                ORDER BY ls.overall_listing_score DESC, st.created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_publish_decisions(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM publish_reports
                ORDER BY created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_risk_alerts(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM publish_reports
                WHERE risk_level IN ('High', 'Critical')
                ORDER BY created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_latest_commercial_validation_session(self) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM research_sessions
                WHERE session_label LIKE 'commercial-validation%'
                ORDER BY started_at DESC
                LIMIT 1
                """,
                conn,
            )

    def fetch_commercial_overview(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT
                    cs.niche_name,
                    cs.product_name,
                    cs.commercial_score,
                    cs.confidence_score,
                    cs.risk_score,
                    cs.estimated_success_level,
                    pd.publish_decision,
                    pd.priority_level,
                    pd.reasons,
                    pd.recommendations,
                    cs.created_at
                FROM commercial_scores cs
                LEFT JOIN publish_decisions pd
                    ON pd.session_id = cs.session_id
                    AND pd.niche_name = cs.niche_name
                    AND pd.product_name = cs.product_name
                ORDER BY cs.commercial_score DESC, cs.created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_commercial_scores(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM commercial_scores
                ORDER BY commercial_score DESC, created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_commercial_publish_decisions(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                """
                SELECT *
                FROM publish_decisions
                ORDER BY created_at DESC
                LIMIT ?
                """,
                conn,
                params=(limit,),
            )

    def fetch_latest_factory_run(self) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                "SELECT * FROM factory_runs ORDER BY created_at DESC LIMIT 1",
                conn,
            )

    def fetch_factory_runs(self, limit: int = 100) -> pd.DataFrame:
        with self.connection() as conn:
            return pd.read_sql_query(
                "SELECT * FROM factory_runs ORDER BY created_at DESC LIMIT ?",
                conn,
                params=(limit,),
            )

    def fetch_pipeline_logs(self, run_id: int | None = None, limit: int = 200) -> pd.DataFrame:
        with self.connection() as conn:
            if run_id is None:
                return pd.read_sql_query(
                    "SELECT * FROM pipeline_logs ORDER BY created_at DESC LIMIT ?",
                    conn,
                    params=(limit,),
                )
            return pd.read_sql_query(
                "SELECT * FROM pipeline_logs WHERE run_id = ? ORDER BY created_at ASC LIMIT ?",
                conn,
                params=(run_id, limit),
            )

    def fetch_workflow_reports(self, run_id: int | None = None, limit: int = 200) -> pd.DataFrame:
        with self.connection() as conn:
            if run_id is None:
                return pd.read_sql_query(
                    "SELECT * FROM workflow_reports ORDER BY created_at DESC LIMIT ?",
                    conn,
                    params=(limit,),
                )
            return pd.read_sql_query(
                "SELECT * FROM workflow_reports WHERE run_id = ? ORDER BY created_at DESC LIMIT ?",
                conn,
                params=(run_id, limit),
            )
