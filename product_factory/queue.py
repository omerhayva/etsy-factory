from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class QueueItem:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)


class ProductFactoryQueue:
    def __init__(self, items: list[QueueItem] | None = None):
        self._items: deque[QueueItem] = deque(items or [])

    def enqueue(self, name: str, payload: dict[str, Any] | None = None) -> None:
        self._items.append(QueueItem(name=name, payload=dict(payload or {})))

    def dequeue(self) -> QueueItem | None:
        if not self._items:
            return None
        return self._items.popleft()

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
