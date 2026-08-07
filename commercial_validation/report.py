from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from exports.exporter import export_csv, export_json


class CommercialValidationReport:
    """Generate and export commercial validation reports."""

    def generate(self, rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        if not rows:
            return {
                "top_commercial_candidates": [],
                "ready_for_publish": [],
                "needs_improvement": [],
                "high_risk_candidates": [],
            }

        frame = pd.DataFrame(rows).fillna(0)
        return {
            "top_commercial_candidates": frame.sort_values("commercial_score", ascending=False).head(100).to_dict("records"),
            "ready_for_publish": frame[frame["publish_decision"] == "READY FOR PUBLISH"].sort_values("commercial_score", ascending=False).head(100).to_dict("records"),
            "needs_improvement": frame[frame["publish_decision"] == "NEEDS IMPROVEMENT"].sort_values("commercial_score", ascending=False).head(100).to_dict("records"),
            "high_risk_candidates": frame[frame["risk_score"] >= 50].sort_values("risk_score", ascending=False).head(100).to_dict("records"),
        }

    def export(self, report: dict[str, list[dict[str, Any]]], rows: list[dict[str, Any]], export_dir: str | Path, prefix: str) -> dict[str, str]:
        root = Path(export_dir)
        root.mkdir(parents=True, exist_ok=True)
        report_json = export_json(report, root / f"{prefix}_commercial_validation_report.json")
        merged_rows: list[dict[str, Any]] = []
        for report_name, items in report.items():
            for item in items:
                copied = dict(item)
                copied["report_name"] = report_name
                merged_rows.append(copied)
        report_csv = export_csv(merged_rows, root / f"{prefix}_commercial_validation_report.csv")
        package_json = export_json(rows, root / f"{prefix}_commercial_package.json")
        package_csv = export_csv(rows, root / f"{prefix}_commercial_package.csv")

        md_lines = ["# Commercial Validation Package", "", f"Total candidates: {len(rows)}", "", "## Decisions"]
        for row in rows[:30]:
            md_lines.append(f"- {row['niche_name']} | {row['product_name']} | {row['publish_decision']} | score={row['commercial_score']}")
        package_md = root / f"{prefix}_commercial_package.md"
        package_md.write_text("\n".join(md_lines), encoding="utf-8")

        return {
            "report_json": str(report_json),
            "report_csv": str(report_csv),
            "package_json": str(package_json),
            "package_csv": str(package_csv),
            "package_md": str(package_md),
        }
