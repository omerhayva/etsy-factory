from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from utils.config import load_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _path_from_env(name: str, default: Path) -> Path:
    raw = os.getenv(name, "").strip()
    candidate = Path(raw).expanduser() if raw else default
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return candidate.resolve()


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: Path
    token_store_path: Path
    timezone_name: str
    worker_poll_seconds: int
    worker_stale_minutes: int
    etsy_api_keystring: str
    etsy_shared_secret: str
    etsy_shop_id: str
    etsy_access_token: str
    etsy_refresh_token: str
    etsy_api_base_url: str
    pinterest_client_id: str
    pinterest_client_secret: str
    pinterest_access_token: str
    pinterest_refresh_token: str
    pinterest_scopes: str
    pinterest_api_base_url: str
    pinterest_default_board_id: str

    @classmethod
    def from_env(cls, *, load_env_file: bool = True) -> Settings:
        if load_env_file:
            load_dotenv(PROJECT_ROOT / ".env", override=False)
        config = load_config(PROJECT_ROOT / "config.yaml")
        app_defaults = config.get("app", {})
        scheduler_defaults = config.get("pinterest_scheduler", {})

        return cls(
            database_path=_path_from_env(
                "APP_DATABASE_PATH",
                PROJECT_ROOT / str(app_defaults.get("database_path", "database/etsy_pinterest.sqlite3")),
            ),
            token_store_path=_path_from_env(
                "OAUTH_TOKEN_STORE", PROJECT_ROOT / ".secrets" / "oauth_tokens.json"
            ),
            timezone_name=os.getenv(
                "APP_TIMEZONE", str(scheduler_defaults.get("timezone", "Europe/Istanbul"))
            ).strip() or "Europe/Istanbul",
            worker_poll_seconds=max(
                5,
                int(os.getenv("WORKER_POLL_SECONDS", str(scheduler_defaults.get("poll_seconds", 30)))),
            ),
            worker_stale_minutes=max(
                5,
                int(os.getenv("WORKER_STALE_MINUTES", str(scheduler_defaults.get("stale_job_minutes", 20)))),
            ),
            etsy_api_keystring=os.getenv("ETSY_API_KEYSTRING", "").strip(),
            etsy_shared_secret=os.getenv("ETSY_SHARED_SECRET", "").strip(),
            etsy_shop_id=os.getenv("ETSY_SHOP_ID", "").strip(),
            etsy_access_token=os.getenv("ETSY_ACCESS_TOKEN", "").strip(),
            etsy_refresh_token=os.getenv("ETSY_REFRESH_TOKEN", "").strip(),
            etsy_api_base_url=os.getenv(
                "ETSY_API_BASE_URL", "https://openapi.etsy.com/v3/application"
            ).rstrip("/"),
            pinterest_client_id=os.getenv("PINTEREST_CLIENT_ID", "").strip(),
            pinterest_client_secret=os.getenv("PINTEREST_CLIENT_SECRET", "").strip(),
            pinterest_access_token=os.getenv("PINTEREST_ACCESS_TOKEN", "").strip(),
            pinterest_refresh_token=os.getenv("PINTEREST_REFRESH_TOKEN", "").strip(),
            pinterest_scopes=os.getenv("PINTEREST_SCOPES", "boards:read,pins:write").strip(),
            pinterest_api_base_url=os.getenv(
                "PINTEREST_API_BASE_URL",
                str(scheduler_defaults.get("default_api_base_url", "https://api-sandbox.pinterest.com/v5")),
            ).rstrip("/"),
            pinterest_default_board_id=os.getenv("PINTEREST_DEFAULT_BOARD_ID", "").strip(),
        )

    @property
    def etsy_configured(self) -> bool:
        token_available = bool(self.etsy_access_token or self.etsy_refresh_token)
        return bool(
            self.etsy_api_keystring
            and self.etsy_shared_secret
            and self.etsy_shop_id
            and token_available
        )

    @property
    def pinterest_configured(self) -> bool:
        token_available = bool(self.pinterest_access_token or self.pinterest_refresh_token)
        can_refresh = bool(self.pinterest_client_id and self.pinterest_client_secret)
        return bool(token_available and (self.pinterest_access_token or can_refresh))

    def missing_etsy_settings(self) -> list[str]:
        missing = []
        if not self.etsy_api_keystring:
            missing.append("ETSY_API_KEYSTRING")
        if not self.etsy_shared_secret:
            missing.append("ETSY_SHARED_SECRET")
        if not self.etsy_shop_id:
            missing.append("ETSY_SHOP_ID")
        if not (self.etsy_access_token or self.etsy_refresh_token):
            missing.append("ETSY_ACCESS_TOKEN or ETSY_REFRESH_TOKEN")
        return missing

    def missing_pinterest_settings(self) -> list[str]:
        missing = []
        if not (self.pinterest_access_token or self.pinterest_refresh_token):
            missing.append("PINTEREST_ACCESS_TOKEN or PINTEREST_REFRESH_TOKEN")
        if self.pinterest_refresh_token and not (
            self.pinterest_client_id and self.pinterest_client_secret
        ):
            missing.extend(
                name
                for name, value in (
                    ("PINTEREST_CLIENT_ID", self.pinterest_client_id),
                    ("PINTEREST_CLIENT_SECRET", self.pinterest_client_secret),
                )
                if not value
            )
        return missing
