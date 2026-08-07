from __future__ import annotations

from typing import Any

from database.db import EtsyDatabase
from design_intelligence.color_engine import recommend_palette
from design_intelligence.composition import build_composition
from design_intelligence.design_variations import generate_variations
from design_intelligence.layout_engine import recommend_layout
from design_intelligence.mockup_strategy import recommend_mockups
from design_intelligence.prompt_builder import SUPPORTED_PROMPT_PROVIDERS, build_prompt_payload
from design_intelligence.quality_score import score_design
from design_intelligence.report_generator import DesignIntelligenceReportGenerator
from design_intelligence.style_analyzer import default_style_library, recommend_styles
from design_intelligence.trend_styles import infer_trend_style_bias
from design_intelligence.typography_engine import recommend_typography
from utils.logging_utils import get_logger


LOGGER = get_logger(__name__)


class DesignIntelligenceEngine:
    """Creative decision engine that selects commercially optimal design directions."""

    def __init__(self, db: EtsyDatabase, style_library: list[dict[str, Any]] | None = None):
        self.db = db
        self.style_library = style_library or default_style_library()
        self.report_generator = DesignIntelligenceReportGenerator()

    def run(self, session_label: str = "design-intelligence", export_dir: str | None = None) -> dict[str, Any]:
        niche_df = self.db.fetch_niche_intelligence_overview()
        product_df = self.db.fetch_product_intelligence_recommendations(limit=500)
        research_df = self.db.fetch_opportunity_overview(limit=500)

        if niche_df.empty or product_df.empty or research_df.empty:
            return {"session_id": None, "rows": [], "report": {}, "exports": {}}

        session_id = self.db.save_research_session(
            {
                "session_label": session_label,
                "sources": ["research_engine", "niche_intelligence", "product_intelligence"],
                "status": "running",
            }
        )

        rows: list[dict[str, Any]] = []
        try:
            niche_lookup = {str(row["niche_name"]): row for _, row in niche_df.iterrows()}
            research_lookup = {str(row["niche_name"]): row for _, row in research_df.iterrows()}

            for _, product_row in product_df.iterrows():
                niche_name = str(product_row.get("niche_name", "unknown"))
                if niche_name not in niche_lookup:
                    continue
                result = self._process_row(
                    session_id=session_id,
                    product_row=product_row.to_dict(),
                    niche_row=niche_lookup[niche_name],
                    research_row=research_lookup.get(niche_name, {}),
                )
                rows.append(result)

            report = self.report_generator.generate(rows)
            exports: dict[str, str] = {}
            if export_dir:
                exports = self.report_generator.export(report, all_rows=rows, export_dir=export_dir, prefix=f"session_{session_id}")

            self.db.save_market_report(
                {
                    "session_id": session_id,
                    "report_name": "design_intelligence_report",
                    "report_payload": report,
                }
            )
            self.db.close_research_session(session_id, status="completed", summary=f"Generated {len(rows)} design packages")
            return {"session_id": session_id, "rows": rows, "report": report, "exports": exports}
        except Exception as exc:
            LOGGER.exception("Design intelligence engine failed")
            self.db.close_research_session(session_id, status="failed", summary=str(exc))
            raise

    def _process_row(
        self,
        *,
        session_id: int,
        product_row: dict[str, Any],
        niche_row: dict[str, Any],
        research_row: dict[str, Any],
    ) -> dict[str, Any]:
        niche_name = str(product_row.get("niche_name", "unknown"))
        product_name = str(product_row.get("recommended_product", "t-shirt"))
        style_name_seed = niche_name
        evergreen = str(niche_row.get("evergreen_classification") or "Trending")
        seasonal = int(niche_row.get("seasonal") or 0)
        season_labels = ["seasonal"] if seasonal else ["all"]
        gift_signal = float(niche_row.get("gift_suitability") or 50)
        trend_signal = float(niche_row.get("confidence") or 50)
        competition_score = float(niche_row.get("competition_score") or 50)
        audience_tags = ["gift"] if gift_signal >= 70 else ["adult"]
        if "kids" in niche_name.lower():
            audience_tags.append("kids")

        styles = recommend_styles(
            niche_name=style_name_seed,
            product_name=product_name,
            audience_tags=audience_tags,
            season_tags=season_labels,
            trend_signal=trend_signal,
            gift_signal=gift_signal,
            style_library=self.style_library,
        )

        boosts = infer_trend_style_bias(niche_name, evergreen)
        for row in styles:
            row["score"] = round(max(0.0, min(100.0, float(row["score"]) + boosts.get(row["style_name"], 0.0))), 2)
        styles.sort(key=lambda item: float(item["score"]), reverse=True)
        selected_style = styles[0]

        palette = recommend_palette(
            niche_name=niche_name,
            product_name=product_name,
            season_labels=season_labels,
            audience_tags=audience_tags,
            style_name=selected_style["style_name"],
        )
        typography = recommend_typography(
            style_name=selected_style["style_name"],
            niche_name=niche_name,
            audience_tags=audience_tags,
        )
        layout = recommend_layout(
            product_name=product_name,
            style_name=selected_style["style_name"],
            typography_primary=str(typography.get("primary_font_style", "Sans Serif")),
        )
        composition = build_composition(
            style_name=selected_style["style_name"],
            layout_type=str(layout.get("layout_type", "Centered")),
        )
        composition["layout_type"] = layout.get("layout_type", "Centered")

        quality = score_design(
            style_score=float(selected_style["score"]),
            product_match_score=float(product_row.get("score") or 50),
            gift_signal=gift_signal,
            competition_score=competition_score,
            composition=composition,
            typography=typography,
        )

        prompts: list[dict[str, str]] = []
        for provider in SUPPORTED_PROMPT_PROVIDERS:
            payload = build_prompt_payload(
                provider=provider,
                niche_name=niche_name,
                product_name=product_name,
                style_name=selected_style["style_name"],
                palette_name=str(palette["palette_name"]),
                typography=typography,
                composition=composition,
            )
            prompts.append(payload)
            self.db.save_design_prompt_record(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "product_name": product_name,
                    "provider": provider,
                    "prompt": payload["prompt"],
                    "negative_prompt": payload["negative_prompt"],
                }
            )

        variations = generate_variations(
            niche_name=niche_name,
            product_name=product_name,
            style_name=selected_style["style_name"],
            palette_name=str(palette["palette_name"]),
            typography=typography,
            composition=composition,
            provider="Midjourney",
            base_score=float(quality["overall_design_score"]),
        )

        mockups = recommend_mockups(product_name=product_name, audience_tags=audience_tags, seasonal=bool(seasonal))

        self.db.save_design_style(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "style_name": selected_style["style_name"],
                "style_family": selected_style.get("style_family"),
                "score": selected_style["score"],
                "trend_alignment": selected_style.get("trend_alignment"),
                "reasoning": selected_style.get("reasoning"),
            }
        )
        self.db.save_color_palette(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "palette_name": palette["palette_name"],
                "primary_colors": palette["primary_colors"],
                "secondary_colors": palette["secondary_colors"],
                "accent_colors": palette["accent_colors"],
                "rationale": palette["rationale"],
            }
        )
        self.db.save_typography_profile(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "primary_font_style": typography["primary_font_style"],
                "secondary_font_style": typography["secondary_font_style"],
                "hierarchy": typography["hierarchy"],
                "rationale": typography["rationale"],
            }
        )
        self.db.save_layout_profile(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "layout_type": layout["layout_type"],
                "composition_profile": composition["visual_hierarchy"],
                "image_text_ratio": composition["image_text_ratio"],
                "whitespace_level": composition["whitespace"],
                "icon_placement": composition["icon_placement"],
                "border_usage": composition["border_usage"],
                "frame_usage": composition["frame_usage"],
                "rationale": layout["rationale"],
            }
        )
        self.db.save_design_score(
            {
                "session_id": session_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "style_name": selected_style["style_name"],
                **quality,
            }
        )

        for variation in variations:
            self.db.save_design_variation(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "product_name": product_name,
                    "variation_type": variation["variation_type"],
                    "style_name": variation["style_name"],
                    "prompt": variation["prompt"],
                    "score": variation["score"],
                }
            )

        for mockup in mockups:
            self.db.save_mockup_recommendation(
                {
                    "session_id": session_id,
                    "niche_name": niche_name,
                    "product_name": product_name,
                    "mockup_type": mockup["mockup_type"],
                    "rationale": mockup["rationale"],
                    "priority": mockup["priority"],
                }
            )

        return {
            "session_id": session_id,
            "niche_name": niche_name,
            "product_name": product_name,
            "style_name": selected_style["style_name"],
            "style_score": float(selected_style["score"]),
            "palette_name": palette["palette_name"],
            "primary_font_style": typography["primary_font_style"],
            "layout_type": layout["layout_type"],
            "overall_design_score": quality["overall_design_score"],
            "commercial_appeal": quality["commercial_appeal"],
            "gift_appeal": quality["gift_appeal"],
            "seasonal": seasonal,
            "prompts": prompts,
            "variations": variations,
            "mockups": mockups,
            "research_demand": float(research_row.get("opportunity_score") or 0.0),
            "product_recommendation_score": float(product_row.get("score") or 0.0),
        }
