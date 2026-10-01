from __future__ import annotations

import base64
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from io import BytesIO

import pytest
from PIL import Image

from pinterest_automation.errors import DuplicateScheduleError
from pinterest_automation.etsy_client import EtsyClient
from pinterest_automation.listing_import import parse_listings_csv
from pinterest_automation.models import EtsyListing
from pinterest_automation.pinterest_client import PinterestClient
from pinterest_automation.settings import Settings
from pinterest_automation.store import PinterestStore
from pinterest_automation.worker import PinterestWorker


class FakeResponse:
    def __init__(self, payload=None, *, status_code=200, content=b"", headers=None):
        self.payload = payload or {}
        self.status_code = status_code
        self.content = content
        self.headers = headers or {"Content-Type": "application/json"}
        self.text = json.dumps(self.payload)

    def json(self):
        return self.payload


class FakeEtsySession:
    def __init__(self):
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeResponse(
            {
                "count": 1,
                "results": [
                    {
                        "listing_id": 42,
                        "title": "Botanical print",
                        "description": "A lovely art print",
                        "state": "active",
                        "url": "https://www.etsy.com/listing/42/botanical-print",
                        "price": {"amount": 1999, "divisor": 100, "currency_code": "USD"},
                        "tags": ["botanical", "wall art"],
                        "images": [{"url_fullxfull": "https://i.etsystatic.com/image.jpg"}],
                    }
                ],
            }
        )


class FakePinterestSession:
    def __init__(self, image_bytes: bytes):
        self.image_bytes = image_bytes
        self.api_calls = []

    def get(self, url, **kwargs):
        return FakeResponse(content=self.image_bytes, headers={"Content-Type": "image/jpeg"})

    def request(self, method, url, **kwargs):
        self.api_calls.append((method, url, kwargs))
        if url.endswith("/boards"):
            return FakeResponse({"items": [{"id": "1001", "name": "My shop"}], "bookmark": None})
        return FakeResponse({"id": "987654321", "board_id": "1001"}, status_code=201)


def make_settings(tmp_path, **overrides):
    settings = Settings.from_env(load_env_file=False)
    return replace(
        settings,
        database_path=tmp_path / "etsy-pinterest.sqlite3",
        token_store_path=tmp_path / "oauth_tokens.json",
        **overrides,
    )


def make_listing(listing_id="42"):
    return EtsyListing(
        listing_id=listing_id,
        title="Botanical wall print",
        description="A botanical art print for your home.",
        listing_url=f"https://www.etsy.com/listing/{listing_id}/botanical-wall-print",
        image_url="https://i.etsystatic.com/listing-image.jpg",
        tags=("botanical", "wall art", "gift"),
        price=19.99,
        state="active",
        shop_id="shop-1",
        source="test",
    )


def test_csv_import_accepts_etsy_style_headers_and_utf8_bom():
    csv_data = (
        "\ufeffListing ID,Title,Description,URL,Image 1,Tags,Price,State\n"
        '42,Botanical print,Handmade art,https://www.etsy.com/listing/42,https://cdn.example/a.jpg,"botanical; wall art",19.99,active\n'
    ).encode("utf-8")
    listings, errors = parse_listings_csv(csv_data, shop_id="shop-1")

    assert not errors
    assert len(listings) == 1
    assert listings[0].listing_id == "42"
    assert listings[0].tags == ("botanical", "wall art")
    assert listings[0].price == 19.99
    assert listings[0].shop_id == "shop-1"


def test_csv_import_reports_invalid_rows_without_discarding_valid_rows():
    csv_data = (
        "listing_id,title,listing_url,image_url\n"
        "42,Good listing,https://www.etsy.com/listing/42,https://cdn.example/a.jpg\n"
        "43,Missing image,https://www.etsy.com/listing/43,\n"
    )
    listings, errors = parse_listings_csv(csv_data)
    assert [listing.listing_id for listing in listings] == ["42"]
    assert errors == ["Satır 3: görsel URL geçersiz"]


def test_store_upserts_listings_schedules_and_claims_jobs(tmp_path):
    store = PinterestStore(tmp_path / "store.sqlite3")
    store.initialize()
    listing = make_listing()
    store.upsert_listings([listing])
    saved = store.get_listing(listing.listing_id)
    assert saved is not None
    assert saved["tags"] == ["botanical", "wall art", "gift"]

    scheduled_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    job_id = store.schedule_pin(
        listing=saved,
        board_id="1001",
        title="Botanical wall print",
        description="Shop this botanical print.",
        alt_text="Botanical illustration in muted green",
        scheduled_at=scheduled_at,
    )
    with pytest.raises(DuplicateScheduleError):
        store.schedule_pin(
            listing=saved,
            board_id="1001",
            title="Botanical wall print",
            description="Shop this botanical print.",
            alt_text="Botanical illustration in muted green",
            scheduled_at=scheduled_at,
        )
    later_job_id = store.schedule_pin(
        listing=saved,
        board_id="1001",
        title="Botanical wall print — alternate date",
        description="Shop this botanical print.",
        alt_text="Botanical illustration in muted green",
        scheduled_at=scheduled_at + timedelta(days=1),
    )
    assert [job["id"] for job in store.list_jobs(status="scheduled")] == [job_id, later_job_id]

    assert store.claim_due_job(now=scheduled_at - timedelta(minutes=1)) is None
    claimed = store.claim_due_job(now=scheduled_at + timedelta(seconds=1))
    assert claimed is not None
    assert claimed["id"] == job_id
    assert claimed["status"] == "publishing"
    assert claimed["attempt_count"] == 1
    store.mark_published(job_id, pinterest_pin_id="pin-1", pin_url="https://www.pinterest.com/pin/pin-1/")
    assert store.get_job(job_id)["status"] == "published"
    assert store.stats()["published"] == 1


def test_etsy_client_maps_shop_listings_and_auth_headers(tmp_path):
    settings = make_settings(
        tmp_path,
        etsy_api_keystring="etsy-key",
        etsy_shared_secret="etsy-secret",
        etsy_shop_id="shop-1",
        etsy_access_token="etsy-access",
    )
    session = FakeEtsySession()
    listings = EtsyClient(settings, session=session, image_request_delay=0).list_active_listings(max_listings=10)

    assert len(listings) == 1
    assert listings[0].listing_id == "42"
    assert listings[0].price == 19.99
    assert listings[0].image_url.endswith("image.jpg")
    headers = session.calls[0][2]["headers"]
    assert headers["x-api-key"] == "etsy-key:etsy-secret"
    assert headers["Authorization"] == "Bearer etsy-access"
    assert session.calls[0][2]["params"]["state"] == "active"
    assert session.calls[0][2]["params"]["includes"] == "Images"


def test_pinterest_client_posts_listing_image_as_base64_pin(tmp_path):
    buffer = BytesIO()
    Image.new("RGB", (200, 300), color=(130, 80, 50)).save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()
    settings = make_settings(
        tmp_path,
        pinterest_access_token="pinterest-access",
        pinterest_api_base_url="https://api-sandbox.pinterest.com/v5",
    )
    session = FakePinterestSession(image_bytes)
    client = PinterestClient(settings, session=session)

    boards = client.list_boards()
    result = client.create_pin(
        {
            "board_id": "1001",
            "title": "Botanical print",
            "description": "Shop the print on Etsy.",
            "alt_text": "Botanical print in green",
            "link": "https://www.etsy.com/listing/42",
            "image_url": "https://i.etsystatic.com/listing-image.jpg",
        }
    )

    assert boards[0]["name"] == "My shop"
    assert result["id"] == "987654321"
    method, url, kwargs = session.api_calls[-1]
    assert (method, url) == ("POST", "https://api-sandbox.pinterest.com/v5/pins")
    assert kwargs["json"]["board_id"] == "1001"
    assert kwargs["json"]["link"].startswith("https://www.etsy.com/listing/")
    media = kwargs["json"]["media_source"]
    assert media["source_type"] == "image_base64"
    assert base64.b64decode(media["data"]) == image_bytes


def test_worker_publishes_due_jobs_with_injected_publisher(tmp_path):
    settings = make_settings(tmp_path, pinterest_access_token="configured-for-test")
    store = PinterestStore(settings.database_path)
    store.initialize()
    listing = make_listing()
    store.upsert_listings([listing])
    listing_row = store.get_listing(listing.listing_id)
    job_id = store.schedule_pin(
        listing=listing_row,
        board_id="1001",
        title="Botanical wall print",
        description="Shop on Etsy",
        alt_text="Botanical wall print",
        scheduled_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )

    class FakePublisher:
        def create_pin(self, job):
            assert job["id"] == job_id
            return {"id": "pin-123"}

    result = PinterestWorker(settings, store=store, publisher=FakePublisher()).process_one_due_job()
    assert result == {"job_id": job_id, "status": "published", "pinterest_pin_id": "pin-123"}
    job = store.get_job(job_id)
    assert job["status"] == "published"
    assert job["pinterest_pin_url"].endswith("pin-123/")
