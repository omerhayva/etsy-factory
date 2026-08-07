from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from product_factory.queue import ProductFactoryQueue
from product_factory.state_manager import ProductFactoryStateManager


@dataclass(slots=True)
class PipelineStep:
    name: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]


class ProductFactoryPipeline:
    STEP_NAMES = [
        "Research",
        "Analyze",
        "Choose Product",
        "Generate Design Strategy",
        "Generate Listing",
        "Validate",
        "Export",
    ]

    def __init__(self, state_manager: ProductFactoryStateManager):
        self.state_manager = state_manager
        self.queue = ProductFactoryQueue()
        for step_name in self.STEP_NAMES:
            self.queue.enqueue(step_name)

    def run(self, *, run_id: int, context: dict[str, Any], handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        pipeline_steps: list[dict[str, Any]] = []
        working_context = dict(context)
        while step := self.queue.dequeue():
            handler = handlers[step.name]
            self.state_manager.log_step(run_id=run_id, step_name=step.name, status="running", payload=working_context)
            try:
                result = handler(working_context) or {}
                if isinstance(result, dict):
                    working_context.update(result)
                step_record = {"step": step.name, "status": "completed", "payload": result}
                pipeline_steps.append(step_record)
                self.state_manager.log_step(run_id=run_id, step_name=step.name, status="completed", payload=result)
            except Exception as exc:
                step_record = {"step": step.name, "status": "failed", "message": str(exc)}
                pipeline_steps.append(step_record)
                self.state_manager.log_step(run_id=run_id, step_name=step.name, status="failed", message=str(exc))
                raise
        return pipeline_steps, working_context
