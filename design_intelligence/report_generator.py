from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from exports.exporter import export_csv, export_json


class DesignIntelligenceReportGenerator:
    """Creates category reports and exports full design packages."""

    def generate(self, rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        if not rows:
            return {
                "top_design_styles": [],
                "top_design_scores": [],
                "best_prompt_packages": [],
                "gift_oriented_designs": [],
                "seasonal_designs": [],
            }

        df = pd.DataFrame(rows).fillna(0)
        return {
            "top_design_styles": df.sort_values("style_score", ascending=False).head(100).to_dict("records"),
            "top_design_scores": df.sort_values("overall_design_score", ascending=False).head(100).to_dict("records"),
            "best_prompt_packages": df.sort_values("commercial_appeal", ascending=False).head(100).to_dict("records"),
            "gift_oriented_designs": df.sort_values("gift_appeal", ascending=False).head(100).to_dict("records"),
            "seasonal_designs": df[df["seasonal"] == 1].sort_values("overall_design_score", ascending=False).head(100).to_dict("records"),
        }

    def export(self, report: dict[str, list[dict[str, Any]]], all_rows: list[dict[str, Any]], export_dir: str | Path, prefix: str) -> dict[str, str]:
        root = Path(export_dir)
        root.mkdir(parents=True, exist_ok=True)

        report_json = export_json(report, root / f"{prefix}_design_intelligence_report.json")
        flattened: list[dict[str, Any]] = []
        for report_name, items in report.items():
            for item in items:
                copy = dict(item)
                copy["report_name"] = report_name
                flattened.append(copy)
        report_csv = export_csv(flattened, root / f"{prefix}_design_intelligence_report.csv")

        package_json = export_json(all_rows, root / f"{prefix}_design_package.json")
        package_csv = export_csv(all_rows, root / f"{prefix}_design_package.csv")

        md_lines = [
            "# Design Intelligence Package",
            "",
            f"Total rows: {len(all_rows)}",
            "",
            "## Top Rows",
        ]
        for row in all_rows[:20]:
            md_lines.append(
                f"- {row['niche_name']} | {row['product_name']} | style={row['style_name']} | score={row['overall_design_score']}"
            )
        md_path = root / f"{prefix}_design_package.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")

        return {
            "report_json": str(report_json),
            "report_csv": str(report_csv),
            "package_json": str(package_json),
            "package_csv": str(package_csv),
            "package_md": str(md_path),
        }
