from __future__ import annotations

import time
from typing import Any

import requests

from pinterest_automation.errors import ApiError, ConfigurationError
from pinterest_automation.models import EtsyListing
from pinterest_automation.settings import Settings
from pinterest_automation.tokens import TokenManager


class EtsyClient:
    """Read active shop listings and their primary images through Etsy Open API v3."""

    def __init__(
        self,
        settings: Settings,
        token_manager: TokenManager | None = None,
        session: Any | None = None,
        image_request_delay: float = 0.08,
    ):
        self.settings = settings
        self.session = session or requests.Session()
        self.token_manager = token_manager or TokenManager(settings, session=self.session)
        self.image_request_delay = max(0.0, image_request_delay)

    def list_active_listings(self, *, max_listings: int = 200) -> list[EtsyListing]:
        if not self.settings.etsy_shop_id:
            raise ConfigurationError("ETSY_SHOP_ID ayarlanmamış.")
        if max_listings < 1:
            return []

        output: list[EtsyListing] = []
        limit = min(100, max_listings)
        offset = 0
        while len(output) < max_listings:
            payload = self._request(
                "GET",
                f"/shops/{self.settings.etsy_shop_id}/listings",
                params={
                    "state": "active",
                    "limit": min(limit, max_listings - len(output)),
                    "offset": offset,
                    "includes": "Images",
                },
            )
            rows = payload.get("results", []) if isinstance(payload, dict) else []
            if not isinstance(rows, list) or not rows:
                break
            for row in rows:
                if not isinstance(row, dict):
                    continue
                listing = self._to_listing(row)
                if not listing.image_url:
                    listing = self._with_primary_image(listing)
                output.append(listing)
                if len(output) >= max_listings:
                    break
            offset += len(rows)
            total = payload.get("count") if isinstance(payload, dict) else None
            if len(rows) < limit or (total is not None and offset >= int(total)):
                break
        return output

    def _with_primary_image(self, listing: EtsyListing) -> EtsyListing:
        if self.image_request_delay:
            time.sleep(self.image_request_delay)
        payload = self._request(
            "GET",
            f"/shops/{self.settings.etsy_shop_id}/listings/{listing.listing_id}/images",
        )
        images = payload.get("results", []) if isinstance(payload, dict) else []
        image_url = self._select_image_url(images)
        return EtsyListing(
            listing_id=listing.listing_id,
            title=listing.title,
            description=listing.description,
            listing_url=listing.listing_url,
            image_url=image_url,
            tags=listing.tags,
            price=listing.price,
            state=listing.state,
            shop_id=listing.shop_id,
            source=listing.source,
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.settings.etsy_api_base_url}{path}"
        response = None
        for attempt in range(2):
            access_token = self.token_manager.get_access_token("etsy")
            headers = {
                "x-api-key": f"{self.settings.etsy_api_keystring}:{self.settings.etsy_shared_secret}",
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }
            response = self.session.request(method, url, headers=headers, timeout=25, **kwargs)
            if response.status_code == 401 and attempt == 0:
                try:
                    self.token_manager.refresh("etsy")
                except (ApiError, ConfigurationError):
                    break
                continue
            break

        if response is None:
            raise ApiError("Etsy API isteği yanıt vermedi.")
        if response.status_code >= 400:
            raise self._api_error("Etsy", response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiError("Etsy API geçerli JSON döndürmedi.") from exc
        if not isinstance(payload, dict):
            raise ApiError("Etsy API yanıt biçimi beklenmiyor.")
        return payload

    @staticmethod
    def _api_error(name: str, response: Any) -> ApiError:
        try:
            payload = response.json()
            detail = payload.get("error") or payload.get("message") or payload
        except ValueError:
            detail = getattr(response, "text", "")
        return ApiError(f"{name} API hatası ({response.status_code}): {detail}")

    def _to_listing(self, row: dict[str, Any]) -> EtsyListing:
        listing_id = str(row.get("listing_id") or row.get("id") or "").strip()
        if not listing_id:
            raise ApiError("Etsy listing yanıtında listing_id bulunamadı.")
        images = row.get("images") or []
        image_url = self._select_image_url(images)
        price = self._parse_price(row.get("price"))
        tags = row.get("tags") or []
        if isinstance(tags, str):
            tags = [part.strip() for part in tags.split(",") if part.strip()]
        return EtsyListing(
            listing_id=listing_id,
            title=str(row.get("title") or "").strip(),
            description=str(row.get("description") or "").strip(),
            listing_url=str(row.get("url") or f"https://www.etsy.com/listing/{listing_id}").strip(),
            image_url=image_url,
            tags=tuple(str(tag).strip() for tag in tags if str(tag).strip()),
            price=price,
            state=str(row.get("state") or "active"),
            shop_id=self.settings.etsy_shop_id,
            source="etsy_api",
        )

    @staticmethod
    def _select_image_url(images: Any) -> str:
        if not isinstance(images, list):
            return ""
        for image in images:
            if not isinstance(image, dict):
                continue
            for field in ("url_fullxfull", "url_170x135", "url_570xN", "url_75x75"):
                value = image.get(field)
                if value:
                    return str(value)
        return ""

    @staticmethod
    def _parse_price(value: Any) -> float | None:
        if isinstance(value, dict):
            try:
                amount = float(value.get("amount", 0))
                divisor = float(value.get("divisor", 1)) or 1.0
                return amount / divisor
            except (TypeError, ValueError):
                return None
        try:
            return float(value) if value not in (None, "") else None
        except (TypeError, ValueError):
            return None
