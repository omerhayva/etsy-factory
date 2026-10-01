from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections.abc import Iterable
from urllib.parse import urlparse

from pinterest_automation.errors import AutomationError
from pinterest_automation.models import EtsyListing

ALIASES = {
    "listing_id": {"listing_id", "listingid", "id"},
    "title": {"title", "listing_title", "listing_name"},
    "description": {"description", "listing_description"},
    "listing_url": {"listing_url", "url", "link", "listing_link"},
    "image_url": {"image_url", "image", "primary_image_url", "image_1", "image1", "photo_1"},
    "tags": {"tags", "tag"},
    "price": {"price", "listing_price"},
    "state": {"state", "status", "listing_state"},
}


def _normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _first(row: dict[str, str], aliases: set[str]) -> str:
    for key, value in row.items():
        if _normalize_header(key) in aliases and value and value.strip():
            return value.strip()
    return ""


def _valid_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _parse_tags(value: str) -> tuple[str, ...]:
    text = value.strip()
    if not text:
        return ()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            values = [str(item).strip() for item in parsed]
        else:
            values = [part.strip() for part in text.split(",")]
    except json.JSONDecodeError:
        values = [part.strip() for part in re.split(r"[,;]", text)]
    return tuple(dict.fromkeys(item for item in values if item))


def _parse_price(value: str) -> float | None:
    if not value.strip():
        return None
    cleaned = re.sub(r"[^0-9,.-]", "", value).replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _listing_id_from_url(url: str) -> str:
    match = re.search(r"/listing/(\d+)", url)
    if match:
        return match.group(1)
    return "import-" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def parse_listings_csv(content: bytes | str, *, shop_id: str = "") -> tuple[list[EtsyListing], list[str]]:
    """Read a small, portable CSV export; accepts a UTF-8 BOM and Etsy-style headers."""
    if isinstance(content, bytes):
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = content.decode("cp1252")
    else:
        text = content.lstrip("\ufeff")

    if not text.strip():
        raise AutomationError("CSV dosyası boş.")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise AutomationError("CSV başlık satırı bulunamadı.")

    header_set = {_normalize_header(header) for header in reader.fieldnames if header}
    has_title = bool(header_set.intersection(ALIASES["title"]))
    has_url = bool(header_set.intersection(ALIASES["listing_url"]))
    has_image = bool(header_set.intersection(ALIASES["image_url"]))
    missing_columns = [name for name, present in (("title", has_title), ("listing_url", has_url), ("image_url / image_1", has_image)) if not present]
    if missing_columns:
        raise AutomationError("CSV'de gerekli sütunlar eksik: " + ", ".join(missing_columns))

    listings: list[EtsyListing] = []
    errors: list[str] = []
    for row_number, raw_row in enumerate(reader, start=2):
        row = {str(key or ""): str(value or "") for key, value in raw_row.items()}
        title = _first(row, ALIASES["title"])
        description = _first(row, ALIASES["description"])
        listing_url = _first(row, ALIASES["listing_url"])
        image_url = _first(row, ALIASES["image_url"])
        if not any(value.strip() for value in row.values()):
            continue
        row_errors = []
        if not title:
            row_errors.append("başlık boş")
        if not _valid_http_url(listing_url):
            row_errors.append("listing URL geçersiz")
        if not _valid_http_url(image_url):
            row_errors.append("görsel URL geçersiz")
        if row_errors:
            errors.append(f"Satır {row_number}: " + ", ".join(row_errors))
            continue

        listing_id = _first(row, ALIASES["listing_id"]) or _listing_id_from_url(listing_url)
        listings.append(
            EtsyListing(
                listing_id=listing_id,
                title=title,
                description=description,
                listing_url=listing_url,
                image_url=image_url,
                tags=_parse_tags(_first(row, ALIASES["tags"])),
                price=_parse_price(_first(row, ALIASES["price"])),
                state=_first(row, ALIASES["state"]) or "active",
                shop_id=shop_id,
                source="csv",
            )
        )
    return listings, errors


def listings_to_csv(listings: Iterable[EtsyListing]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["listing_id", "title", "description", "listing_url", "image_url", "tags", "price", "state"],
    )
    writer.writeheader()
    for listing in listings:
        data = listing.as_dict()
        data["tags"] = ", ".join(listing.tags)
        writer.writerow({field: data.get(field, "") for field in writer.fieldnames})
    return output.getvalue()
