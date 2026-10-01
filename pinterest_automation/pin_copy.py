from __future__ import annotations

import html
import re
from typing import Any


def clean_listing_text(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*(p|div|li|h[1-6])\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[\t\r\f\v ]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def build_pin_copy(listing: dict[str, Any]) -> tuple[str, str, str]:
    title = clean_listing_text(listing.get("title"))[:100]
    description = clean_listing_text(listing.get("description"))
    tags = listing.get("tags") or []
    if isinstance(tags, str):
        tags = [tag.strip() for tag in re.split(r"[,;]", tags) if tag.strip()]
    tags = [str(tag).strip().lstrip("#") for tag in tags if str(tag).strip()]
    if tags:
        tag_line = "Tags: " + " · ".join(f"#{tag.replace(' ', '')}" for tag in tags[:8])
        description = f"{description}\n\n{tag_line}".strip()
    if not description:
        description = title
    description = description[:800]
    alt_text = clean_listing_text(listing.get("title"))[:500]
    return title, description, alt_text
