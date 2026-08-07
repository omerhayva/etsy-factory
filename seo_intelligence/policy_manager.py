from __future__ import annotations

from pathlib import Path
from typing import Any

from seo_intelligence.policy_loader import PolicyLoader


class PolicyManager:
    """Provides policy access helpers without hardcoding rule values."""

    def __init__(self, loader: PolicyLoader | None = None, policies_dir: str | Path = "policies"):
        self.loader = loader or PolicyLoader(policies_dir=policies_dir)
        self._policy_cache: dict[str, Any] | None = None
        self._version_cache: dict[str, Any] | None = None

    def policy(self) -> dict[str, Any]:
        if self._policy_cache is None:
            self._policy_cache = self.loader.load_policy()
        return self._policy_cache

    def version(self) -> dict[str, Any]:
        if self._version_cache is None:
            self._version_cache = self.loader.load_version()
        return self._version_cache

    def rules(self) -> dict[str, Any]:
        return self.policy().get("policy", {})

    def disclosure_placeholder(self) -> str:
        return str(self.rules().get("disclosure", {}).get("ai_assisted_placeholder", "[AI_DISCLOSURE_PLACEHOLDER]"))

    def production_partner_placeholder(self) -> str:
        return str(self.rules().get("disclosure", {}).get("production_partner_placeholder", "[PRODUCTION_PARTNER_PLACEHOLDER]"))
