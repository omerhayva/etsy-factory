from __future__ import annotations

import base64
from io import BytesIO
from typing import Any

import requests
from PIL import Image, UnidentifiedImageError

from pinterest_automation.errors import ApiError, ConfigurationError
from pinterest_automation.settings import Settings
from pinterest_automation.tokens import TokenManager

MAX_PIN_IMAGE_BYTES = 20 * 1024 * 1024


class PinterestClient:
    """Pinterest API v5 client for boards and organic image Pins."""

    def __init__(
        self,
        settings: Settings,
        token_manager: TokenManager | None = None,
        session: Any | None = None,
    ):
        self.settings = settings
        self.session = session or requests.Session()
        self.token_manager = token_manager or TokenManager(settings, session=self.session)

    def list_boards(self) -> list[dict[str, Any]]:
        boards: list[dict[str, Any]] = []
        bookmark = ""
        seen_bookmarks: set[str] = set()
        while True:
            params: dict[str, Any] = {"page_size": 250}
            if bookmark:
                params["bookmark"] = bookmark
            payload = self._request("GET", "/boards", params=params)
            items = payload.get("items", [])
            if isinstance(items, list):
                boards.extend(item for item in items if isinstance(item, dict))
            next_bookmark = str(payload.get("bookmark") or "")
            if not next_bookmark or next_bookmark in seen_bookmarks:
                break
            seen_bookmarks.add(next_bookmark)
            bookmark = next_bookmark
        return boards

    def create_pin(self, job: dict[str, Any]) -> dict[str, Any]:
        board_id = str(job.get("board_id") or "").strip()
        image_url = str(job.get("image_url") or "").strip()
        link = str(job.get("link") or "").strip()
        if not board_id or not board_id.isdigit():
            raise ConfigurationError("Pinterest board ID boş veya geçersiz.")
        if not image_url.startswith("https://"):
            raise ConfigurationError("Pin görseli herkese açık bir HTTPS URL olmalı.")
        if not link.startswith("https://"):
            raise ConfigurationError("Etsy hedef bağlantısı HTTPS olmalı.")

        media_source = self._encode_image(image_url)
        body = {
            "board_id": board_id,
            "title": str(job.get("title") or "").strip()[:100],
            "description": str(job.get("description") or "").strip()[:800],
            "alt_text": str(job.get("alt_text") or job.get("title") or "").strip()[:500],
            "link": link[:2048],
            "media_source": media_source,
        }
        payload = self._request("POST", "/pins", json=body)
        if not payload.get("id"):
            raise ApiError("Pinterest Pin oluşturduğunu bildirdi ancak Pin ID döndürmedi.")
        return payload

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.settings.pinterest_api_base_url}{path}"
        response = None
        for attempt in range(2):
            access_token = self.token_manager.get_access_token("pinterest")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            response = self.session.request(method, url, headers=headers, timeout=30, **kwargs)
            if response.status_code == 401 and attempt == 0:
                try:
                    self.token_manager.refresh("pinterest")
                except (ApiError, ConfigurationError):
                    break
                continue
            break

        if response is None:
            raise ApiError("Pinterest API isteği yanıt vermedi.")
        if response.status_code >= 400:
            try:
                payload = response.json()
                detail = payload.get("message") or payload.get("error") or payload
            except ValueError:
                detail = getattr(response, "text", "")
            raise ApiError(f"Pinterest API hatası ({response.status_code}): {detail}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiError("Pinterest API geçerli JSON döndürmedi.") from exc
        if not isinstance(payload, dict):
            raise ApiError("Pinterest API yanıt biçimi beklenmiyor.")
        return payload

    def _encode_image(self, image_url: str) -> dict[str, Any]:
        response = self.session.get(
            image_url,
            timeout=30,
            headers={"User-Agent": "EtsyPinterestScheduler/0.1"},
        )
        if response.status_code >= 400:
            raise ApiError(f"Listing görseli indirilemedi ({response.status_code}).")
        image_bytes = bytes(response.content)
        if not image_bytes:
            raise ApiError("Listing görseli boş döndü.")
        if len(image_bytes) > MAX_PIN_IMAGE_BYTES:
            raise ApiError("Listing görseli Pinterest için 20 MB sınırını aşıyor.")

        try:
            image = Image.open(BytesIO(image_bytes))
            image.seek(0)
            if image.width < 100 or image.height < 100:
                raise ApiError("Pinterest Pin görseli en az 100 x 100 piksel olmalı.")
            image_format = (image.format or "").upper()
            if image_format in {"JPEG", "JPG"}:
                content_type = "image/jpeg"
                if image.mode not in {"RGB", "L"}:
                    image = image.convert("RGB")
                    buffer = BytesIO()
                    image.save(buffer, format="JPEG", quality=92, optimize=True)
                    image_bytes = buffer.getvalue()
            elif image_format == "PNG":
                content_type = "image/png"
            else:
                image = image.convert("RGB")
                buffer = BytesIO()
                image.save(buffer, format="JPEG", quality=92, optimize=True)
                image_bytes = buffer.getvalue()
                content_type = "image/jpeg"
        except UnidentifiedImageError as exc:
            raise ApiError("Etsy listing görseli desteklenen bir JPEG/PNG görseli değil.") from exc
        except OSError as exc:
            raise ApiError("Listing görseli okunamadı.") from exc

        if len(image_bytes) > MAX_PIN_IMAGE_BYTES:
            raise ApiError("Dönüştürülmüş Pin görseli 20 MB sınırını aşıyor.")
        return {
            "source_type": "image_base64",
            "content_type": content_type,
            "is_standard": True,
            "data": base64.b64encode(image_bytes).decode("ascii"),
        }
