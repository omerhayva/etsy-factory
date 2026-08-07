from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from database.db import EtsyDatabase
from commercial_validation.engine import CommercialValidationEngine
from design_intelligence.engine import DesignIntelligenceEngine
from exports.exporter import export_csv, export_json
from product_factory.factory import ProductFactory
from niche_intelligence.engine import NicheIntelligenceEngine
from product_intelligence.engine import ProductIntelligenceEngine
from seo_intelligence.engine import SeoComplianceIntelligenceEngine
from research.daily import daily_product_discovery
from research.engine import ResearchEngine
from research.research_manager import ResearchManager
from utils.config import load_config
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


def _ensure_state() -> None:
    if "latest_packages" not in st.session_state:
        st.session_state.latest_packages = []
    if "latest_factory_result" not in st.session_state:
        st.session_state.latest_factory_result = {}


def _package_get(package: Any, root: str, field: str, default: Any = "") -> Any:
    if isinstance(package, dict):
        root_value = package.get(root, {})
        if isinstance(root_value, dict):
            return root_value.get(field, default)
        return default

    root_value = getattr(package, root, None)
    if root_value is None:
        return default
    return getattr(root_value, field, default)


def _to_tag_text(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value) if value else ""


def _packages_to_rows(packages: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for package in packages:
        tags = _package_get(package, "listing", "tags", [])
        rows.append(
            {
                "product_name": _package_get(package, "product", "product_name"),
                "niche": _package_get(package, "niche", "niche_name"),
                "title": _package_get(package, "listing", "title"),
                "description": _package_get(package, "listing", "description"),
                "tags": _to_tag_text(tags),
                "design_prompt": _package_get(package, "design", "prompt"),
                "recommended_product": _package_get(package, "product", "product_name"),
            }
        )
    return rows


def _period_metrics(niche_df: pd.DataFrame) -> dict[str, float]:
    if niche_df.empty:
        return {
            "weekly_count": 0,
            "monthly_count": 0,
            "weekly_avg": 0.0,
            "monthly_avg": 0.0,
        }

    df = niche_df.copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    now = pd.Timestamp.now()
    weekly_df = df[df["created_at"] >= now - pd.Timedelta(days=7)]
    monthly_df = df[df["created_at"] >= now - pd.Timedelta(days=30)]

    weekly_avg = float(weekly_df["opportunity_score"].mean()) if not weekly_df.empty else 0.0
    monthly_avg = float(monthly_df["opportunity_score"].mean()) if not monthly_df.empty else 0.0
    return {
        "weekly_count": int(len(weekly_df)),
        "monthly_count": int(len(monthly_df)),
        "weekly_avg": round(weekly_avg, 1),
        "monthly_avg": round(monthly_avg, 1),
    }


def run_dashboard() -> None:
    st.set_page_config(page_title="Etsy POD AI Factory", layout="wide")
    _ensure_state()

    config = load_config("config.yaml")
    db = EtsyDatabase(config["app"]["database_path"])
    db.initialize()
    engine = ResearchEngine()
    research_manager = ResearchManager(db=db, categories=config.get("research", {}).get("categories", []))
    niche_engine = NicheIntelligenceEngine(db=db)
    product_engine = ProductIntelligenceEngine(db=db)
    design_engine = DesignIntelligenceEngine(db=db)
    seo_engine = SeoComplianceIntelligenceEngine(db=db)
    commercial_engine = CommercialValidationEngine(db=db)
    factory = ProductFactory(
        db=db,
        research_manager=research_manager,
        niche_engine=niche_engine,
        product_engine=product_engine,
        design_engine=design_engine,
        seo_engine=seo_engine,
        commercial_engine=commercial_engine,
    )

    st.title("Etsy POD AI Factory")
    st.caption("Etsy POD firsatlarini bul, nisleri skorla, urun onerileri olustur ve listeleme ciktilarini disa aktar.")

    page = st.sidebar.radio(
        "Sayfalar",
        [
            "Ana Sayfa",
            "Arastirma",
            "Nis Firsatlari",
            "Urunler",
            "Design Intelligence",
            "SEO Intelligence",
            "Commercial Validation",
            "Product Factory",
            "Tasarim Promptlari",
            "Listelemeler",
        ],
    )

    if page == "Ana Sayfa":
        st.subheader("En Iyi Firsatlar")
        niche_df = db.fetch_top_niches(limit=10)
        if niche_df.empty:
            st.info("Veritabani su an bos. Once arastirma calistirin.")
        else:
            metrics = _period_metrics(db.fetch_dataframe("niches"))
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Haftalik Nis Sayisi", metrics["weekly_count"])
            col2.metric("Aylik Nis Sayisi", metrics["monthly_count"])
            col3.metric("Haftalik Ort. Firsat Skoru", metrics["weekly_avg"])
            col4.metric("Aylik Ort. Firsat Skoru", metrics["monthly_avg"])

            st.dataframe(
                niche_df[["niche_name", "opportunity_score", "demand_score", "competition_score", "profit_potential"]],
                width="stretch",
            )

            history_df = db.fetch_dataframe("niches")
            history_df["created_at"] = pd.to_datetime(history_df["created_at"], errors="coerce")
            history_df["opportunity_score"] = pd.to_numeric(history_df["opportunity_score"], errors="coerce")
            history_df = history_df.dropna(subset=["created_at", "opportunity_score"])
            if not history_df.empty:
                daily_trend = (
                    history_df
                    .assign(day=history_df["created_at"].dt.date)
                    .groupby("day", as_index=False)["opportunity_score"]
                    .mean()
                    .dropna(subset=["opportunity_score"])
                    .tail(30)
                )
                if len(daily_trend) > 1:
                    st.subheader("Son 30 Gun Firsat Skor Trendi")
                    st.line_chart(daily_trend.set_index("day"))
                else:
                    st.info("Trend grafigi icin en az iki gunluk veri gerekiyor.")

        if st.button("Gunluk Kesif Calistir"):
            try:
                st.session_state.latest_packages = daily_product_discovery("config.yaml")
                st.success("Gunluk kesif tamamlandi.")
            except Exception as exc:
                LOGGER.exception("Gunluk kesif sirasinda hata olustu")
                st.error(f"Gunluk kesif basarisiz oldu: {exc}")

    elif page == "Arastirma":
        st.subheader("Profesyonel Arastirma Motoru")
        latest_session = db.fetch_latest_research_session()
        if latest_session.empty:
            st.info("Henuz arastirma oturumu yok.")
        else:
            st.write("Son Arastirma Oturumu")
            st.dataframe(latest_session, width="stretch")

        if st.button("Profesyonel Arastirmayi Calistir"):
            try:
                session_output = research_manager.run_session(
                    seed_terms=config.get("research", {}).get("search_terms", []),
                    session_label="dashboard-professional-research",
                    export_dir=config["app"]["export_dir"],
                )
                st.success(f"Arastirma tamamlandi. Session ID: {session_output['session_id']}")
                if session_output.get("exports"):
                    st.json(session_output["exports"])
            except Exception as exc:
                LOGGER.exception("Profesyonel arastirma calisamadi")
                st.error(f"Profesyonel arastirma basarisiz oldu: {exc}")

        st.subheader("Top Nisler ve Firsat Skorlari")
        st.dataframe(db.fetch_opportunity_overview(limit=20), width="stretch")

        trend_overview = db.fetch_trend_overview()
        st.subheader("Trend Ozeti")
        if trend_overview.empty:
            st.info("Trend verisi yok.")
        else:
            st.dataframe(trend_overview, width="stretch")

        keyword_overview = db.fetch_keyword_overview(limit=20)
        st.subheader("Anahtar Kelime Ozeti")
        if keyword_overview.empty:
            st.info("Anahtar kelime verisi yok.")
        else:
            st.dataframe(keyword_overview, width="stretch")

        st.divider()
        st.subheader("Niche Intelligence Engine")
        latest_ni_session = db.fetch_latest_niche_intelligence_session()
        if latest_ni_session.empty:
            st.info("Henuz niche intelligence oturumu yok.")
        else:
            st.write("Son Niche Intelligence Oturumu")
            st.dataframe(latest_ni_session, width="stretch")

        if st.button("Niche Intelligence Calistir"):
            try:
                ni_output = niche_engine.run(
                    session_label="niche-intelligence-dashboard",
                    export_dir=config["app"]["export_dir"],
                )
                st.success(f"Niche intelligence tamamlandi. Session ID: {ni_output['session_id']}")
                if ni_output.get("exports"):
                    st.json(ni_output["exports"])
            except Exception as exc:
                LOGGER.exception("Niche intelligence calisamadi")
                st.error(f"Niche intelligence basarisiz oldu: {exc}")

        ni_overview = db.fetch_niche_intelligence_overview()

        st.subheader("Top Niches")
        if ni_overview.empty:
            st.info("Top niche verisi yok.")
        else:
            st.dataframe(ni_overview[["niche_name", "overall_score", "confidence", "classification", "risk_level"]].head(100), width="stretch")

        st.subheader("Audience Analysis")
        audience_df = db.fetch_dataframe("audiences")
        if audience_df.empty:
            st.info("Audience analizi verisi yok.")
        else:
            st.dataframe(audience_df[["niche_name", "audiences", "buyer_intents", "created_at"]].head(100), width="stretch")

        st.subheader("Seasonality")
        seasonality_df = db.fetch_dataframe("seasonality")
        if seasonality_df.empty:
            st.info("Seasonality verisi yok.")
        else:
            st.dataframe(seasonality_df[["niche_name", "seasonal", "season_labels", "confidence", "created_at"]].head(100), width="stretch")

        st.subheader("Gift Market")
        gift_df = db.fetch_dataframe("gift_scores")
        if gift_df.empty:
            st.info("Gift market verisi yok.")
        else:
            st.dataframe(gift_df[["niche_name", "gift_suitability", "gift_occasions", "target_recipients", "gift_confidence"]].head(100), width="stretch")

        st.subheader("Competition")
        comp_df = db.fetch_dataframe("competition_scores")
        if comp_df.empty:
            st.info("Competition verisi yok.")
        else:
            st.dataframe(comp_df[["niche_name", "competition_label", "competition_score", "created_at"]].head(100), width="stretch")

        st.subheader("Recommendation Ranking")
        rec_df = db.fetch_dataframe("recommendations")
        if rec_df.empty:
            st.info("Recommendation verisi yok.")
        else:
            st.dataframe(rec_df[["niche_name", "overall_score", "classification", "recommendation", "reasons"]].head(100), width="stretch")

        st.divider()
        st.subheader("Hizli Tek Nis Analizi")
        niche = st.text_input("Nis", value="vintage dog lover")
        audience = st.text_input("Hedef Kitle", value="hediye alicilari")
        season = st.text_input("Sezon", value="tum yil")
        if st.button("Nis Analiz Et"):
            try:
                package = engine.build_opportunity_package(niche, audience=audience, season=season)
                st.session_state.latest_packages = [package]
                st.json({
                    "niche": asdict(package.niche),
                    "product": asdict(package.product),
                    "design": asdict(package.design),
                    "listing": asdict(package.listing),
                })
            except Exception as exc:
                LOGGER.exception("Nis analizi sirasinda hata olustu")
                st.error(f"Nis analizi basarisiz oldu: {exc}")

    elif page == "Nis Firsatlari":
        niche_df = db.fetch_top_niches(limit=100)
        st.dataframe(niche_df, width="stretch")

    elif page == "Urunler":
        st.subheader("Product Intelligence")
        latest_pi_session = db.fetch_latest_product_intelligence_session()
        if latest_pi_session.empty:
            st.info("Henuz product intelligence oturumu yok.")
        else:
            st.write("Son Product Intelligence Oturumu")
            st.dataframe(latest_pi_session, width="stretch")

        if st.button("Product Intelligence Calistir"):
            try:
                pi_output = product_engine.run(
                    session_label="product-intelligence-dashboard",
                    export_dir=config["app"]["export_dir"],
                )
                st.success(f"Product intelligence tamamlandi. Session ID: {pi_output['session_id']}")
                if pi_output.get("exports"):
                    st.json(pi_output["exports"])
            except Exception as exc:
                LOGGER.exception("Product intelligence calisamadi")
                st.error(f"Product intelligence basarisiz oldu: {exc}")

        st.subheader("Top Recommended Products")
        rec_df = db.fetch_product_intelligence_recommendations(limit=50)
        if rec_df.empty:
            st.info("Product recommendation verisi yok.")
        else:
            st.dataframe(rec_df[["niche_name", "recommended_product", "provider", "score", "reasons", "created_at"]], width="stretch")

        st.subheader("Highest Profit Products")
        profit_df = db.fetch_product_profit_overview(limit=50)
        if profit_df.empty:
            st.info("Product profit verisi yok.")
        else:
            st.dataframe(
                profit_df[
                    [
                        "niche_name",
                        "product_name",
                        "suggested_selling_price",
                        "estimated_production_cost",
                        "estimated_gross_profit",
                        "estimated_margin_percent",
                    ]
                ],
                width="stretch",
            )

        st.subheader("Lowest Risk Products")
        risk_df = db.fetch_product_low_risk(limit=50)
        if risk_df.empty:
            st.info("Product risk verisi yok.")
        else:
            st.dataframe(
                risk_df[
                    [
                        "niche_name",
                        "product_name",
                        "return_risk",
                        "complaint_risk",
                        "fragility_risk",
                        "seasonality_risk",
                        "created_at",
                    ]
                ],
                width="stretch",
            )

        st.subheader("Gift Product Ranking")
        gift_df = db.fetch_product_gift_ranking(limit=50)
        if gift_df.empty:
            st.info("Gift product ranking verisi yok.")
        else:
            st.dataframe(gift_df[["niche_name", "recommended_product", "provider", "score", "reasons", "created_at"]], width="stretch")

        st.subheader("Seasonal Opportunities")
        seasonal_df = db.fetch_product_seasonal_opportunities(limit=50)
        if seasonal_df.empty:
            st.info("Seasonal product firsati verisi yok.")
        else:
            st.dataframe(
                seasonal_df[["niche_name", "product_name", "provider", "match_score", "ranking", "reasoning", "created_at"]],
                width="stretch",
            )

        st.divider()
        st.subheader("Hizli Paket Urun Onerileri")
        if st.session_state.latest_packages:
            rows = [
                {
                    "niche": _package_get(package, "niche", "niche_name"),
                    "recommended_product": _package_get(package, "product", "product_name"),
                    "score": _package_get(package, "product", "score"),
                    "rationale": _package_get(package, "product", "rationale"),
                }
                for package in st.session_state.latest_packages
            ]
            st.dataframe(pd.DataFrame(rows), width="stretch")
        else:
            st.info("Urun onerilerini gormek icin once arastirma sonucu olusturun.")

    elif page == "Design Intelligence":
        st.subheader("AI Design Intelligence Engine")

        latest_di_session = db.fetch_latest_design_intelligence_session()
        if latest_di_session.empty:
            st.info("Henuz design intelligence oturumu yok.")
        else:
            st.write("Son Design Intelligence Oturumu")
            st.dataframe(latest_di_session, width="stretch")

        if st.button("Design Intelligence Calistir"):
            try:
                di_output = design_engine.run(
                    session_label="design-intelligence-dashboard",
                    export_dir=config["app"]["export_dir"],
                )
                st.success(f"Design intelligence tamamlandi. Session ID: {di_output['session_id']}")
                if di_output.get("exports"):
                    st.json(di_output["exports"])
            except Exception as exc:
                LOGGER.exception("Design intelligence calisamadi")
                st.error(f"Design intelligence basarisiz oldu: {exc}")

        overview_df = db.fetch_design_intelligence_overview(limit=50)
        st.subheader("Recommended Style")
        if overview_df.empty:
            st.info("Recommended style verisi yok.")
        else:
            st.dataframe(
                overview_df[
                    [
                        "niche_name",
                        "product_name",
                        "style_name",
                        "palette_name",
                        "primary_font_style",
                        "layout_type",
                        "overall_design_score",
                    ]
                ],
                width="stretch",
            )

        st.subheader("Recommended Colors")
        color_df = db.fetch_dataframe("color_palettes")
        if color_df.empty:
            st.info("Color palette verisi yok.")
        else:
            st.dataframe(color_df[["niche_name", "product_name", "palette_name", "primary_colors", "secondary_colors", "accent_colors"]].head(100), width="stretch")

        st.subheader("Typography")
        typo_df = db.fetch_dataframe("typography_profiles")
        if typo_df.empty:
            st.info("Typography verisi yok.")
        else:
            st.dataframe(typo_df[["niche_name", "product_name", "primary_font_style", "secondary_font_style", "hierarchy"]].head(100), width="stretch")

        st.subheader("Design Score")
        score_df = db.fetch_dataframe("design_scores")
        if score_df.empty:
            st.info("Design score verisi yok.")
        else:
            st.dataframe(
                score_df[
                    [
                        "niche_name",
                        "product_name",
                        "style_name",
                        "print_quality",
                        "visual_balance",
                        "commercial_appeal",
                        "overall_design_score",
                    ]
                ].head(100),
                width="stretch",
            )

        st.subheader("Generated AI Prompts")
        prompts_df = db.fetch_design_prompts(limit=100)
        if prompts_df.empty:
            st.info("Prompt verisi yok.")
        else:
            st.dataframe(prompts_df[["niche_name", "product_name", "provider", "prompt", "negative_prompt", "created_at"]], width="stretch")

        st.subheader("Design Variations")
        variations_df = db.fetch_design_variations(limit=100)
        if variations_df.empty:
            st.info("Design variation verisi yok.")
        else:
            st.dataframe(variations_df[["niche_name", "product_name", "variation_type", "style_name", "score", "prompt"]], width="stretch")

        st.subheader("Mockup Suggestions")
        mockup_df = db.fetch_mockup_recommendations(limit=100)
        if mockup_df.empty:
            st.info("Mockup onerisi verisi yok.")
        else:
            st.dataframe(mockup_df[["niche_name", "product_name", "mockup_type", "rationale", "priority", "created_at"]], width="stretch")

    elif page == "SEO Intelligence":
        st.subheader("Etsy SEO, Compliance & Listing Intelligence")

        latest_session = db.fetch_latest_seo_intelligence_session()
        if latest_session.empty:
            st.info("Henuz SEO intelligence oturumu yok.")
        else:
            st.write("Son SEO Intelligence Oturumu")
            st.dataframe(latest_session, width="stretch")

        if st.button("SEO Intelligence Calistir"):
            try:
                seo_output = seo_engine.run(
                    session_label="seo-intelligence-dashboard",
                    export_dir=config["app"]["export_dir"],
                )
                st.success(f"SEO intelligence tamamlandi. Session ID: {seo_output['session_id']}")
                if seo_output.get("exports"):
                    st.json(seo_output["exports"])
            except Exception as exc:
                LOGGER.exception("SEO intelligence calisamadi")
                st.error(f"SEO intelligence basarisiz oldu: {exc}")

        st.subheader("SEO Intelligence")
        overview_df = db.fetch_seo_listing_overview(limit=100)
        if overview_df.empty:
            st.info("SEO listing overview verisi yok.")
        else:
            st.dataframe(overview_df, width="stretch")

        st.subheader("Compliance Center")
        policy_df = db.fetch_dataframe("policy_checks")
        if policy_df.empty:
            st.info("Policy check verisi yok.")
        else:
            st.dataframe(policy_df[["niche_name", "product_name", "policy_version", "policy_score", "warnings", "passed", "created_at"]].head(100), width="stretch")

        st.subheader("Listing Validator")
        quality_df = db.fetch_dataframe("listing_quality")
        if quality_df.empty:
            st.info("Listing validator verisi yok.")
        else:
            st.dataframe(quality_df[["niche_name", "product_name", "validation_score", "quality_warnings", "quality_fixes", "created_at"]].head(100), width="stretch")

        st.subheader("Listing Preview")
        listing_report_df = db.fetch_dataframe("listing_reports")
        if listing_report_df.empty:
            st.info("Listing preview verisi yok.")
        else:
            st.dataframe(listing_report_df[["niche_name", "product_name", "listing_payload", "created_at"]].head(100), width="stretch")

        st.subheader("Quality Score")
        score_df = db.fetch_dataframe("listing_scores")
        if score_df.empty:
            st.info("Listing score verisi yok.")
        else:
            st.dataframe(
                score_df[
                    [
                        "niche_name",
                        "product_name",
                        "seo_score",
                        "compliance_score",
                        "commercial_score",
                        "buyer_intent_score",
                        "overall_listing_score",
                    ]
                ].head(100),
                width="stretch",
            )

        st.subheader("Publish Decision")
        publish_df = db.fetch_publish_decisions(limit=100)
        if publish_df.empty:
            st.info("Publish decision verisi yok.")
        else:
            st.dataframe(
                publish_df[
                    [
                        "niche_name",
                        "product_name",
                        "publish_decision",
                        "risk_level",
                        "risk_score",
                        "priority_level",
                        "reasons",
                        "fixes",
                        "created_at",
                    ]
                ],
                width="stretch",
            )

        st.subheader("Risk Alerts")
        risk_df = db.fetch_risk_alerts(limit=100)
        if risk_df.empty:
            st.info("Risk alert verisi yok.")
        else:
            st.dataframe(risk_df[["niche_name", "product_name", "risk_level", "risk_score", "reasons", "created_at"]], width="stretch")

    elif page == "Commercial Validation":
        st.subheader("Commercial Validation Engine")

        latest_session = db.fetch_latest_commercial_validation_session()
        if latest_session.empty:
            st.info("Henuz commercial validation oturumu yok.")
        else:
            st.write("Son Commercial Validation Oturumu")
            st.dataframe(latest_session, width="stretch")

        if st.button("Commercial Validation Calistir"):
            try:
                commercial_output = commercial_engine.run(
                    session_label="commercial-validation-dashboard",
                    export_dir=config["app"]["export_dir"],
                )
                st.success(f"Commercial validation tamamlandi. Session ID: {commercial_output['session_id']}")
                if commercial_output.get("exports"):
                    st.json(commercial_output["exports"])
            except Exception as exc:
                LOGGER.exception("Commercial validation calisamadi")
                st.error(f"Commercial validation basarisiz oldu: {exc}")

        st.subheader("Commercial Score")
        commercial_df = db.fetch_commercial_scores(limit=100)
        if commercial_df.empty:
            st.info("Commercial score verisi yok.")
        else:
            st.dataframe(
                commercial_df[
                    [
                        "niche_name",
                        "product_name",
                        "commercial_score",
                        "confidence_score",
                        "risk_score",
                        "estimated_success_level",
                    ]
                ],
                width="stretch",
            )

        st.subheader("Publish Decision")
        decisions_df = db.fetch_commercial_publish_decisions(limit=100)
        if decisions_df.empty:
            st.info("Publish decision verisi yok.")
        else:
            st.dataframe(
                decisions_df[
                    [
                        "niche_name",
                        "product_name",
                        "publish_decision",
                        "priority_level",
                        "commercial_score",
                        "confidence_score",
                        "risk_score",
                        "created_at",
                    ]
                ],
                width="stretch",
            )

        st.subheader("Improvement Suggestions")
        overview_df = db.fetch_commercial_overview(limit=100)
        if overview_df.empty:
            st.info("Improvement suggestions yok.")
        else:
            st.dataframe(
                overview_df[
                    [
                        "niche_name",
                        "product_name",
                        "publish_decision",
                        "priority_level",
                        "reasons",
                        "recommendations",
                    ]
                ],
                width="stretch",
            )

    elif page == "Product Factory":
        st.subheader("AI Product Factory")

        input_columns = st.columns(5)
        factory_niche = input_columns[0].text_input("Niche", value="vintage camping gift")
        factory_audience = input_columns[1].text_input("Audience", value="gift buyers")
        factory_category = input_columns[2].text_input("Product Category", value="t-shirt")
        factory_language = input_columns[3].text_input("Language", value="en")
        factory_market = input_columns[4].text_input("Market", value="US")

        if st.button("Product Factory Calistir"):
            try:
                factory_output = factory.run(
                    niche=factory_niche,
                    audience=factory_audience,
                    product_category=factory_category,
                    language=factory_language,
                    market=factory_market,
                    session_label="product-factory-dashboard",
                    export_dir=config["app"]["export_dir"],
                )
                st.session_state.latest_factory_result = factory_output
                st.success(f"Product factory tamamlandi. Run ID: {factory_output['run_id']}")
                if factory_output.get("exports"):
                    st.json(factory_output["exports"])
            except Exception as exc:
                LOGGER.exception("Product factory calisamadi")
                st.error(f"Product factory basarisiz oldu: {exc}")

        latest_factory_run = db.fetch_latest_factory_run()
        if latest_factory_run.empty:
            st.info("Henuz product factory run yok.")
        else:
            st.write("Son Product Factory Run")
            st.dataframe(latest_factory_run, width="stretch")

            latest_run_id = int(latest_factory_run.iloc[0]["id"])
            pipeline_logs = db.fetch_pipeline_logs(run_id=latest_run_id, limit=200)
            st.subheader("Pipeline Status")
            if pipeline_logs.empty:
                st.info("Pipeline logu yok.")
            else:
                st.dataframe(pipeline_logs, width="stretch")

            workflow_reports = db.fetch_workflow_reports(run_id=latest_run_id, limit=200)
            st.subheader("Generated Products")
            if workflow_reports.empty:
                st.info("Uretilen product paketi yok.")
            else:
                st.dataframe(workflow_reports[["niche_name", "product_name", "created_at"]], width="stretch")

        if st.session_state.latest_factory_result:
            factory_result = st.session_state.latest_factory_result
            st.subheader("Commercial Scores")
            scores_df = pd.DataFrame(factory_result.get("commercial_scores", []))
            if scores_df.empty:
                st.info("Commercial score verisi yok.")
            else:
                st.dataframe(scores_df, width="stretch")

            st.subheader("Publish Decisions")
            decisions_df = pd.DataFrame(factory_result.get("publish_decisions", []))
            if decisions_df.empty:
                st.info("Publish decision verisi yok.")
            else:
                st.dataframe(decisions_df, width="stretch")

            st.subheader("Generated Products Preview")
            product_rows = pd.DataFrame(factory_result.get("generated_products", []))
            if product_rows.empty:
                st.info("Factory uretim paketi yok.")
            else:
                display_columns = [column for column in ["niche_name", "recommended_product", "title", "commercial_score", "publish_decision", "pricing_recommendation"] if column in product_rows.columns]
                st.dataframe(product_rows[display_columns], width="stretch")

    elif page == "Tasarim Promptlari":
        if st.session_state.latest_packages:
            rows = [
                {
                    "niche": _package_get(package, "niche", "niche_name"),
                    "product": _package_get(package, "product", "product_name"),
                    "style": _package_get(package, "design", "style"),
                    "colors": _package_get(package, "design", "colors"),
                    "prompt": _package_get(package, "design", "prompt"),
                }
                for package in st.session_state.latest_packages
            ]
            st.dataframe(pd.DataFrame(rows), width="stretch")
        else:
            st.info("Henuz tasarim promptu uretilmedi.")

    elif page == "Listelemeler":
        if st.session_state.latest_packages:
            rows = _packages_to_rows(st.session_state.latest_packages)
            st.dataframe(pd.DataFrame(rows), width="stretch")
            export_dir = Path(config["app"]["export_dir"])
            try:
                json_path = export_json(rows, export_dir / "latest_listings.json")
                csv_path = export_csv(rows, export_dir / "latest_listings.csv")
                st.download_button("JSON Indir", data=json_path.read_text(encoding="utf-8"), file_name=json_path.name)
                st.download_button("CSV Indir", data=csv_path.read_text(encoding="utf-8"), file_name=csv_path.name)
            except Exception as exc:
                LOGGER.exception("Listeleme disa aktariminda hata olustu")
                st.error(f"Disa aktarim basarisiz oldu: {exc}")
        else:
            st.info("Disa aktarim icin once arastirma sonucu olusturun.")
