from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "app": {
        "name": "Etsy to Pinterest Scheduler",
        "database_path": "database/etsy_pinterest.sqlite3",
        "export_dir": "exports",
    },
    "pinterest_scheduler": {
        "timezone": "Europe/Istanbul",
        "poll_seconds": 30,
        "stale_job_minutes": 20,
        "default_api_base_url": "https://api-sandbox.pinterest.com/v5",
    },
    "research": {
        "search_terms": [
            "vintage dog lover",
            "astronomy shirt",
            "cottagecore tote bag",
            "minimal line art mug",
        ],
        "categories": [
            "Pets",
            "Camping",
            "Fishing",
            "Christian",
            "Islamic",
            "Family",
            "Teacher",
            "Nurse",
            "Halloween",
            "Christmas",
            "Gaming",
            "Books",
            "Sports",
            "Motivation",
            "Nature",
            "Space",
            "Funny",
            "Minimalist",
            "Vintage",
            "Retro",
        ],
        "providers": ["etsy_search"],
    },
}


def load_config(config_path: str | Path = "config.yaml") -> dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        return deepcopy(DEFAULT_CONFIG)

    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}

    config = deepcopy(DEFAULT_CONFIG)
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(config.get(key), dict):
            config[key].update(value)
        else:
            config[key] = value
    return config


def get_setting(config: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = config
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current
