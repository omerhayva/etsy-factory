from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class PolicyLoader:
    """Loads policy definitions and metadata from files."""

    def __init__(self, policies_dir: str | Path = "policies"):
        self.policies_dir = Path(policies_dir)

    def load_policy(self, policy_name: str = "etsy_policy.yaml") -> dict[str, Any]:
        path = self.policies_dir / policy_name
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
        return payload

    def load_version(self, version_file: str = "policy_version.json") -> dict[str, Any]:
        path = self.policies_dir / version_file
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
