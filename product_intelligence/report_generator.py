from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from exports.exporter import export_csv, export_json


class ProductIntelligenceReportGenerator:
    def generate(self, rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        if not rows:
            return {
                "top_recommended_products": [],
                "highest_profit_products": [],
                "lowest_risk_products": [],
                "gift_product_ranking": [],
                "seasonal_opportunities": [],
            }

        df = pd.DataFrame(rows).fillna(0)
        return {
            "top_recommended_products": df.sort_values("score", ascending=False).head(100).to_dict("records"),
            "highest_profit_products": df.sort_values("estimated_margin_percent", ascending=False).head(100).to_dict("records"),
            "lowest_risk_products": df.sort_values("risk_index", ascending=True).head(100).to_dict("records"),
            "gift_product_ranking": df.sort_values("gift_suitability", ascending=False).head(100).to_dict("records"),
            "seasonal_opportunities": df[df["seasonal"] == 1].sort_values("score", ascending=False).head(100).to_dict("records"),
        }

    def export(self, report: dict[str, list[dict[str, Any]]], export_dir: str | Path, prefix: str) -> dict[str, str]:
        root = Path(export_dir)
        root.mkdir(parents=True, exist_ok=True)
        json_path = export_json(report, root / f"{prefix}_product_intelligence_report.json")

        rows: list[dict[str, Any]] = []
        for report_name, items in report.items():
            for item in items:
                copied = dict(item)
                copied["report_name"] = report_name
                rows.append(copied)
        csv_path = export_csv(rows, root / f"{prefix}_product_intelligence_report.csv")
        return {"json": str(json_path), "csv": str(csv_path)}
