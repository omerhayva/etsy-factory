from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from exports.exporter import export_csv, export_json


class NicheIntelligenceReportGenerator:
    """Generates and exports intelligence-first niche decision reports."""

    def generate(self, rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        if not rows:
            return {
                "top_100_niches": [],
                "top_evergreen_niches": [],
                "top_seasonal_niches": [],
                "top_gift_niches": [],
                "highest_profit_potential": [],
                "lowest_competition": [],
                "watchlist_niches": [],
                "avoid_niches": [],
            }

        df = pd.DataFrame(rows).fillna(0)
        return {
            "top_100_niches": df.sort_values("overall_score", ascending=False).head(100).to_dict("records"),
            "top_evergreen_niches": df[df["evergreen_classification"] == "Evergreen"].sort_values("overall_score", ascending=False).head(100).to_dict("records"),
            "top_seasonal_niches": df[df["seasonal"] == 1].sort_values("overall_score", ascending=False).head(100).to_dict("records"),
            "top_gift_niches": df.sort_values("gift_suitability", ascending=False).head(100).to_dict("records"),
            "highest_profit_potential": df.sort_values("profit_potential", ascending=False).head(100).to_dict("records"),
            "lowest_competition": df.sort_values("competition_score", ascending=True).head(100).to_dict("records"),
            "watchlist_niches": df[df["classification"] == "Watchlist"].sort_values("overall_score", ascending=False).head(100).to_dict("records"),
            "avoid_niches": df[df["classification"] == "Avoid"].sort_values("overall_score", ascending=False).head(100).to_dict("records"),
        }

    def export(self, report: dict[str, list[dict[str, Any]]], export_dir: str | Path, prefix: str) -> dict[str, str]:
        export_base = Path(export_dir)
        export_base.mkdir(parents=True, exist_ok=True)
        json_path = export_json(report, export_base / f"{prefix}_niche_intelligence_report.json")

        merged_rows: list[dict[str, Any]] = []
        for report_name, rows in report.items():
            for row in rows:
                copied = dict(row)
                copied["report_name"] = report_name
                merged_rows.append(copied)
        csv_path = export_csv(merged_rows, export_base / f"{prefix}_niche_intelligence_report.csv")

        return {"json": str(json_path), "csv": str(csv_path)}
