from __future__ import annotations

import json
import stat
from dataclasses import replace

from pinterest_automation.settings import Settings
from pinterest_automation.tokens import TokenManager


class FakeResponse:
    status_code = 200

    def json(self):
        return {
            "access_token": "new-access",
            "refresh_token": "new-refresh",
            "expires_in": 3600,
            "scope": "boards:read,pins:write",
        }


class FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse()


def make_settings(tmp_path, **overrides):
    settings = Settings.from_env(load_env_file=False)
    return replace(
        settings,
        token_store_path=tmp_path / "private" / "tokens.json",
        **overrides,
    )


def test_pinterest_refresh_rotates_tokens_and_stores_file_privately(tmp_path):
    settings = make_settings(
        tmp_path,
        pinterest_client_id="client-id",
        pinterest_client_secret="client-secret",
        pinterest_refresh_token="old-refresh",
        pinterest_api_base_url="https://api-sandbox.pinterest.com/v5",
    )
    session = FakeSession()
    manager = TokenManager(settings, session=session)

    assert manager.refresh("pinterest") == "new-access"
    url, kwargs = session.calls[0]
    assert url == "https://api-sandbox.pinterest.com/v5/oauth/token"
    assert kwargs["data"]["refresh_token"] == "old-refresh"
    assert kwargs["auth"] == ("client-id", "client-secret")

    stored = json.loads(settings.token_store_path.read_text(encoding="utf-8"))
    assert stored["pinterest"]["access_token"] == "new-access"
    assert stored["pinterest"]["refresh_token"] == "new-refresh"
    assert stat.S_IMODE(settings.token_store_path.stat().st_mode) == 0o600


def test_etsy_refresh_uses_refresh_grant_and_keystring(tmp_path):
    settings = make_settings(
        tmp_path,
        etsy_api_keystring="etsy-key",
        etsy_refresh_token="etsy-refresh",
    )
    session = FakeSession()
    manager = TokenManager(settings, session=session)

    assert manager.refresh("etsy") == "new-access"
    url, kwargs = session.calls[0]
    assert url == "https://api.etsy.com/v3/public/oauth/token"
    assert kwargs["data"] == {
        "grant_type": "refresh_token",
        "client_id": "etsy-key",
        "refresh_token": "etsy-refresh",
    }
