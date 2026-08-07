from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from exports.exporter import export_csv, export_json


class ProductFactoryReport:
    def generate(
        self,
        *,
        run_id: int,
        factory_input: dict[str, Any],
        pipeline_steps: list[dict[str, Any]],
        packages: list[dict[str, Any]],
        retry_used: bool,
        status: str,
    ) -> dict[str, Any]:
        approved = [package for package in packages if package.get("publish_decision") == "READY FOR PUBLISH"]
        blocked = [package for package in packages if package.get("publish_decision") != "READY FOR PUBLISH"]
        commercial_scores = [
            {
                "niche_name": package.get("niche_name"),
                "product_name": package.get("recommended_product"),
                "commercial_score": package.get("commercial_score"),
                "confidence_score": package.get("commercial_confidence"),
                "risk_score": package.get("commercial_risk"),
            }
            for package in packages
        ]
        publish_decisions = [
            {
                "niche_name": package.get("niche_name"),
                "product_name": package.get("recommended_product"),
                "publish_decision": package.get("publish_decision"),
                "commercial_score": package.get("commercial_score"),
                "commercial_recommendations": package.get("commercial_recommendations", []),
            }
            for package in packages
        ]
        return {
            "run_id": run_id,
            "status": status,
            "input": factory_input,
            "retry_used": retry_used,
            "pipeline_steps": pipeline_steps,
            "generated_products": packages,
            "approved_products": approved,
            "needs_improvement": blocked,
            "commercial_scores": commercial_scores,
            "publish_decisions": publish_decisions,
            "summary": {
                "generated_count": len(packages),
                "approved_count": len(approved),
                "blocked_count": len(blocked),
            },
        }

    def export(self, report: dict[str, Any], export_dir: str | Path, prefix: str) -> dict[str, str]:
        packages = list(report.get("approved_products", []))
        if not packages:
            return {}

        root = Path(export_dir) / prefix
        root.mkdir(parents=True, exist_ok=True)

        summary_json = export_json(report, root / "factory_report.json")
        summary_rows = []
        for package in report.get("generated_products", []):
            summary_rows.append(
                {
                    "niche_name": package.get("niche_name"),
                    "product_name": package.get("recommended_product"),
                    "commercial_score": package.get("commercial_score"),
                    "publish_decision": package.get("publish_decision"),
                    "recommended_price": package.get("pricing_recommendation", {}).get("suggested_selling_price"),
                }
            )
        summary_csv = export_csv(summary_rows, root / "factory_report.csv")

        folder_paths: list[str] = []
        for package in packages:
            folder_name = self._slugify(f"{package.get('niche_name', 'product')}-{package.get('recommended_product', 'listing')}")
            package_root = root / folder_name
            package_root.mkdir(parents=True, exist_ok=True)

            listing_json = package_root / "listing.json"
            listing_json.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")

            listing_md = package_root / "listing.md"
            listing_md.write_text(self._render_listing_markdown(package), encoding="utf-8")

            design_prompt = package_root / "design_prompt.txt"
            design_prompt.write_text(str(package.get("ai_prompt", "")), encoding="utf-8")

            summary_txt = package_root / "summary.txt"
            summary_txt.write_text(self._render_summary_text(package), encoding="utf-8")

            folder_paths.append(str(package_root))

        return {
            "summary_json": str(summary_json),
            "summary_csv": str(summary_csv),
            "approved_folders": json.dumps(folder_paths),
        }

    def _render_listing_markdown(self, package: dict[str, Any]) -> str:
        tags = package.get("tags") or []
        if isinstance(tags, str):
            tags_text = tags
        else:
            tags_text = ", ".join(str(tag) for tag in tags)

        lines = [
            f"# {package.get('title', package.get('recommended_product', 'Listing'))}",
            "",
            f"Product Summary: {package.get('product_summary', '')}",
            f"Recommended Product: {package.get('recommended_product', '')}",
            f"Commercial Score: {package.get('commercial_score', '')}",
            f"Publish Decision: {package.get('publish_decision', '')}",
            "",
            "## Description",
            str(package.get("description", "")),
            "",
            "## Tags",
            tags_text,
            "",
            "## Pricing Recommendation",
            str(package.get("pricing_recommendation", {})),
        ]
        return "\n".join(lines)

    def _render_summary_text(self, package: dict[str, Any]) -> str:
        return "\n".join(
            [
                f"Product Summary: {package.get('product_summary', '')}",
                f"Recommended Product: {package.get('recommended_product', '')}",
                f"Commercial Score: {package.get('commercial_score', '')}",
                f"Publish Decision: {package.get('publish_decision', '')}",
                f"Pricing Recommendation: {package.get('pricing_recommendation', {})}",
            ]
        )

    def _slugify(self, value: str) -> str:
        cleaned = [character.lower() if character.isalnum() else "-" for character in value]
        slug = "".join(cleaned)
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug.strip("-") or "product"
