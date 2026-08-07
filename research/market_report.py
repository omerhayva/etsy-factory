from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from exports.exporter import export_csv, export_json


class MarketReportGenerator:
    """Builds and exports structured market reports from opportunity data."""

    def generate(self, opportunity_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        if not opportunity_rows:
            return {
                "top_20_niches": [],
                "fastest_growing_niches": [],
                "best_gift_niches": [],
                "highest_profit_niches": [],
                "lowest_competition_niches": [],
                "most_balanced_opportunities": [],
            }

        frame = pd.DataFrame(opportunity_rows)
        frame = frame.fillna(0)
        frame["balance_score"] = (
            frame["opportunity_score"]
            - (frame["competition_score"] * 0.25)
            + (frame["profit_potential"] * 0.15)
        )

        return {
            "top_20_niches": frame.sort_values("opportunity_score", ascending=False).head(20).to_dict("records"),
            "fastest_growing_niches": frame.sort_values("trend_score", ascending=False).head(20).to_dict("records"),
            "best_gift_niches": frame.sort_values("gift_potential", ascending=False).head(20).to_dict("records"),
            "highest_profit_niches": frame.sort_values("profit_potential", ascending=False).head(20).to_dict("records"),
            "lowest_competition_niches": frame.sort_values("competition_score", ascending=True).head(20).to_dict("records"),
            "most_balanced_opportunities": frame.sort_values("balance_score", ascending=False).head(20).to_dict("records"),
        }

    def export(self, report: dict[str, list[dict[str, Any]]], export_dir: str | Path, prefix: str) -> dict[str, Path]:
        output_dir = Path(export_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = export_json(report, output_dir / f"{prefix}_market_report.json")

        flat_rows: list[dict[str, Any]] = []
        for report_name, rows in report.items():
            for row in rows:
                flattened = dict(row)
                flattened["report_name"] = report_name
                flat_rows.append(flattened)

        csv_path = export_csv(flat_rows, output_dir / f"{prefix}_market_report.csv")
        return {"json": json_path, "csv": csv_path}
