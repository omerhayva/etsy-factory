from __future__ import annotations

from typing import Any

from database.db import EtsyDatabase


class ProductFactoryStateManager:
    def __init__(self, db: EtsyDatabase):
        self.db = db

    def start_run(self, payload: dict[str, Any]) -> int:
        return self.db.save_factory_run(payload)

    def log_step(self, *, run_id: int, step_name: str, status: str, message: str = "", payload: dict[str, Any] | None = None) -> int:
        return self.db.save_pipeline_log(
            {
                "run_id": run_id,
                "step_name": step_name,
                "status": status,
                "message": message,
                "payload": payload or {},
            }
        )

    def save_report(self, *, run_id: int, niche_name: str, product_name: str, report_payload: dict[str, Any]) -> int:
        return self.db.save_workflow_report(
            {
                "run_id": run_id,
                "niche_name": niche_name,
                "product_name": product_name,
                "report_payload": report_payload,
            }
        )

    def finish_run(self, *, run_id: int, status: str, summary: str, retry_count: int) -> None:
        self.db.update_factory_run(
            {
                "id": run_id,
                "status": status,
                "summary": summary,
                "retry_count": retry_count,
            }
        )
