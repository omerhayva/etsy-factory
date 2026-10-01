from __future__ import annotations

import json
import os
import time
from typing import Any

import requests

from pinterest_automation.errors import ApiError, ConfigurationError
from pinterest_automation.settings import Settings


class TokenManager:
    """Keeps refreshed OAuth tokens in a private, git-ignored local token file."""

    def __init__(self, settings: Settings, session: Any | None = None):
        self.settings = settings
        self.session = session or requests.Session()
        self.path = settings.token_store_path

    def get_access_token(self, service: str) -> str:
        data = self._load()
        entry = data.get(service, {})
        access_token = str(entry.get("access_token") or self._env_access_token(service)).strip()
        refresh_token = str(entry.get("refresh_token") or self._env_refresh_token(service)).strip()
        expires_at = entry.get("expires_at")

        if refresh_token and expires_at is not None and float(expires_at) <= time.time() + 90:
            return self.refresh(service)
        if access_token:
            return access_token
        if refresh_token:
            return self.refresh(service)
        raise ConfigurationError(f"{service.title()} OAuth access/refresh token ayarlanmamış.")

    def refresh(self, service: str) -> str:
        data = self._load()
        entry = data.get(service, {})
        refresh_token = str(entry.get("refresh_token") or self._env_refresh_token(service)).strip()
        if not refresh_token:
            raise ConfigurationError(f"{service.title()} refresh token bulunamadı.")

        if service == "etsy":
            if not self.settings.etsy_api_keystring:
                raise ConfigurationError("ETSY_API_KEYSTRING ayarlanmamış; Etsy token yenilenemiyor.")
            response = self.session.post(
                "https://api.etsy.com/v3/public/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.settings.etsy_api_keystring,
                    "refresh_token": refresh_token,
                },
                timeout=20,
            )
        elif service == "pinterest":
            if not (self.settings.pinterest_client_id and self.settings.pinterest_client_secret):
                raise ConfigurationError("Pinterest refresh için client ID ve secret gerekli.")
            response = self.session.post(
                f"{self.settings.pinterest_api_base_url}/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "scope": self.settings.pinterest_scopes,
                },
                auth=(self.settings.pinterest_client_id, self.settings.pinterest_client_secret),
                timeout=20,
            )
        else:
            raise ConfigurationError(f"Bilinmeyen OAuth servisi: {service}")

        try:
            payload = response.json()
        except ValueError:
            payload = {"message": getattr(response, "text", "")}
        if response.status_code >= 400:
            message = payload.get("error_description") or payload.get("message") or payload.get("error") or "OAuth token yenileme başarısız."
            raise ApiError(f"{service.title()} token yenileme hatası ({response.status_code}): {message}")

        access_token = str(payload.get("access_token", "")).strip()
        if not access_token:
            raise ApiError(f"{service.title()} token yanıtında access_token yok.")
        saved = {
            "access_token": access_token,
            "refresh_token": str(payload.get("refresh_token") or refresh_token),
            "expires_at": time.time() + max(60, int(payload.get("expires_in", 3600))) - 90,
            "scope": payload.get("scope", ""),
        }
        if payload.get("refresh_token_expires_at"):
            saved["refresh_token_expires_at"] = payload["refresh_token_expires_at"]
        data[service] = saved
        self._save(data)
        return access_token

    def _load(self) -> dict[str, dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ConfigurationError(f"OAuth token dosyası okunamadı: {self.path}") from exc
        if not isinstance(payload, dict):
            raise ConfigurationError("OAuth token dosyasının biçimi geçersiz.")
        return payload

    def _save(self, data: dict[str, dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        try:
            os.chmod(temporary_path, 0o600)
        except OSError:
            pass
        temporary_path.replace(self.path)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def _env_access_token(self, service: str) -> str:
        name = "ETSY_ACCESS_TOKEN" if service == "etsy" else "PINTEREST_ACCESS_TOKEN"
        return getattr(self.settings, name.lower(), "")

    def _env_refresh_token(self, service: str) -> str:
        name = "ETSY_REFRESH_TOKEN" if service == "etsy" else "PINTEREST_REFRESH_TOKEN"
        return getattr(self.settings, name.lower(), "")
