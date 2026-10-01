from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EtsyListing:
    listing_id: str
    title: str
    description: str
    listing_url: str
    image_url: str
    tags: tuple[str, ...] = ()
    price: float | None = None
    state: str = "active"
    shop_id: str = ""
    source: str = "csv"

    def as_dict(self) -> dict[str, object]:
        return {
            "listing_id": self.listing_id,
            "title": self.title,
            "description": self.description,
            "listing_url": self.listing_url,
            "image_url": self.image_url,
            "tags": list(self.tags),
            "price": self.price,
            "state": self.state,
            "shop_id": self.shop_id,
            "source": self.source,
        }
