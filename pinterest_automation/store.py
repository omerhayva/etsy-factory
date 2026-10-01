from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from pinterest_automation.errors import DuplicateScheduleError
from pinterest_automation.models import EtsyListing


def utc_iso(value: datetime | None = None) -> str:
    moment = value or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        raise ValueError("Datetime must include a timezone.")
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class PinterestStore:
    """SQLite repository for imported Etsy listings, scheduled Pins, and worker status."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS etsy_listings (
                    listing_id TEXT PRIMARY KEY,
                    shop_id TEXT NOT NULL DEFAULT '',
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    listing_url TEXT NOT NULL,
                    image_url TEXT NOT NULL DEFAULT '',
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    price REAL,
                    state TEXT NOT NULL DEFAULT 'active',
                    source TEXT NOT NULL DEFAULT 'csv',
                    synced_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS pin_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id TEXT NOT NULL,
                    listing_title TEXT NOT NULL,
                    board_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    alt_text TEXT NOT NULL DEFAULT '',
                    image_url TEXT NOT NULL,
                    link TEXT NOT NULL,
                    scheduled_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'scheduled',
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT NOT NULL DEFAULT '',
                    pinterest_pin_id TEXT NOT NULL DEFAULT '',
                    pinterest_pin_url TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_pin_jobs_due
                    ON pin_jobs(status, scheduled_at);
                CREATE INDEX IF NOT EXISTS idx_pin_jobs_listing
                    ON pin_jobs(listing_id, board_id, scheduled_at);

                CREATE TABLE IF NOT EXISTS worker_heartbeat (
                    worker_name TEXT PRIMARY KEY,
                    last_seen_at TEXT NOT NULL
                );
                """
            )

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.database_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def upsert_listings(self, listings: list[EtsyListing]) -> int:
        now = utc_iso()
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO etsy_listings (
                    listing_id, shop_id, title, description, listing_url, image_url,
                    tags_json, price, state, source, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(listing_id) DO UPDATE SET
                    shop_id=excluded.shop_id,
                    title=excluded.title,
                    description=excluded.description,
                    listing_url=excluded.listing_url,
                    image_url=excluded.image_url,
                    tags_json=excluded.tags_json,
                    price=excluded.price,
                    state=excluded.state,
                    source=excluded.source,
                    synced_at=excluded.synced_at
                """,
                [
                    (
                        str(item.listing_id), item.shop_id, item.title, item.description,
                        item.listing_url, item.image_url, json.dumps(item.tags, ensure_ascii=False),
                        item.price, item.state, item.source, now,
                    )
                    for item in listings
                ],
            )
        return len(listings)

    def list_listings(self, *, limit: int = 500, search: str = "") -> list[dict[str, Any]]:
        query = "SELECT * FROM etsy_listings"
        params: list[Any] = []
        if search.strip():
            query += " WHERE title LIKE ? OR listing_id LIKE ?"
            wildcard = f"%{search.strip()}%"
            params.extend([wildcard, wildcard])
        query += " ORDER BY title COLLATE NOCASE LIMIT ?"
        params.append(max(1, min(limit, 5000)))
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._listing_row(row) for row in rows]

    def get_listing(self, listing_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM etsy_listings WHERE listing_id = ?", (str(listing_id),)).fetchone()
        return self._listing_row(row) if row else None

    def schedule_pin(
        self,
        *,
        listing: dict[str, Any],
        board_id: str,
        title: str,
        description: str,
        alt_text: str,
        scheduled_at: datetime,
    ) -> int:
        listing_id = str(listing.get("listing_id") or "").strip()
        board_id = str(board_id or "").strip()
        if not listing_id or not board_id:
            raise ValueError("Listing ID ve Pinterest board ID gerekli.")
        if not str(listing.get("image_url") or "").strip():
            raise ValueError("Bu listing için görsel URL bulunamadı.")
        if scheduled_at.tzinfo is None:
            raise ValueError("Paylaşım saati bir saat dilimi içermeli.")
        scheduled = utc_iso(scheduled_at)
        now = utc_iso()
        link = str(listing.get("listing_url") or "").strip()
        image_url = str(listing.get("image_url") or "").strip()
        title = title.strip()[:100]
        description = description.strip()[:800]
        alt_text = alt_text.strip()[:500]
        with self._connect() as conn:
            existing = conn.execute(
                """
                SELECT id FROM pin_jobs
                WHERE listing_id = ? AND board_id = ? AND scheduled_at = ?
                  AND status != 'cancelled'
                LIMIT 1
                """,
                (listing_id, board_id, scheduled),
            ).fetchone()
            if existing:
                raise DuplicateScheduleError(
                    f"Bu listing aynı board'a aynı saatte zaten kuyruğa eklenmiş (Job #{existing['id']})."
                )
            cursor = conn.execute(
                """
                INSERT INTO pin_jobs (
                    listing_id, listing_title, board_id, title, description, alt_text,
                    image_url, link, scheduled_at, status, attempt_count, last_error,
                    pinterest_pin_id, pinterest_pin_url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'scheduled', 0, '', '', '', ?, ?)
                """,
                (
                    listing_id, str(listing.get("title") or title), board_id, title,
                    description, alt_text, image_url, link, scheduled, now, now,
                ),
            )
            return int(cursor.lastrowid)

    def list_jobs(self, *, status: str | None = None, limit: int = 500) -> list[dict[str, Any]]:
        query = "SELECT * FROM pin_jobs"
        params: list[Any] = []
        if status and status != "all":
            query += " WHERE status = ?"
            params.append(status)
        if status == "scheduled":
            query += " ORDER BY scheduled_at ASC, id ASC LIMIT ?"
        else:
            query += " ORDER BY scheduled_at DESC, id DESC LIMIT ?"
        params.append(max(1, min(limit, 5000)))
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_job(self, job_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM pin_jobs WHERE id = ?", (int(job_id),)).fetchone()
        return dict(row) if row else None

    def claim_due_job(self, *, now: datetime | None = None) -> dict[str, Any] | None:
        due_at = utc_iso(now)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """
                SELECT * FROM pin_jobs
                WHERE status = 'scheduled' AND scheduled_at <= ?
                ORDER BY scheduled_at ASC, id ASC LIMIT 1
                """,
                (due_at,),
            ).fetchone()
            if row is None:
                conn.commit()
                return None
            conn.execute(
                "UPDATE pin_jobs SET status = 'publishing', attempt_count = attempt_count + 1, updated_at = ? WHERE id = ?",
                (utc_iso(), row["id"]),
            )
            conn.commit()
        claimed = dict(row)
        claimed["status"] = "publishing"
        claimed["attempt_count"] = int(claimed.get("attempt_count", 0)) + 1
        return claimed

    def claim_job_now(self, job_id: int) -> dict[str, Any] | None:
        now = utc_iso()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM pin_jobs WHERE id = ? AND status IN ('scheduled', 'failed')",
                (int(job_id),),
            ).fetchone()
            if row is None:
                conn.commit()
                return None
            conn.execute(
                "UPDATE pin_jobs SET status = 'publishing', attempt_count = attempt_count + 1, updated_at = ? WHERE id = ?",
                (now, int(job_id)),
            )
            conn.commit()
        claimed = dict(row)
        claimed["status"] = "publishing"
        claimed["attempt_count"] = int(claimed.get("attempt_count", 0)) + 1
        return claimed

    def mark_published(self, job_id: int, *, pinterest_pin_id: str, pin_url: str = "") -> None:
        now = utc_iso()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE pin_jobs
                SET status = 'published', pinterest_pin_id = ?, pinterest_pin_url = ?,
                    last_error = '', updated_at = ?
                WHERE id = ? AND status = 'publishing'
                """,
                (str(pinterest_pin_id), pin_url, now, int(job_id)),
            )

    def mark_failed(self, job_id: int, error: str) -> None:
        now = utc_iso()
        with self._connect() as conn:
            conn.execute(
                "UPDATE pin_jobs SET status = 'failed', last_error = ?, updated_at = ? WHERE id = ? AND status = 'publishing'",
                (str(error)[:2000], now, int(job_id)),
            )

    def cancel_job(self, job_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE pin_jobs SET status = 'cancelled', updated_at = ? WHERE id = ? AND status IN ('scheduled', 'failed')",
                (utc_iso(), int(job_id)),
            )
            return cursor.rowcount > 0

    def retry_job(self, job_id: int, *, scheduled_at: datetime | None = None) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE pin_jobs SET status = 'scheduled', scheduled_at = ?, last_error = '', updated_at = ?
                WHERE id = ? AND status = 'failed'
                """,
                (utc_iso(scheduled_at), utc_iso(), int(job_id)),
            )
            return cursor.rowcount > 0

    def recover_stale_jobs(self, *, older_than_minutes: int = 20) -> int:
        cutoff = utc_iso(datetime.now(timezone.utc) - timedelta(minutes=max(1, older_than_minutes)))
        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE pin_jobs SET status = 'failed',
                    last_error = 'Worker kesintiye uğradı; olası çift paylaşımı önlemek için otomatik tekrar yapılmadı. Pinterest’te kontrol edip elle yeniden deneyin.',
                    updated_at = ?
                WHERE status = 'publishing' AND updated_at < ?
                """,
                (utc_iso(), cutoff),
            )
            return cursor.rowcount

    def heartbeat(self, worker_name: str = "default") -> None:
        now = utc_iso()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO worker_heartbeat(worker_name, last_seen_at) VALUES (?, ?)
                ON CONFLICT(worker_name) DO UPDATE SET last_seen_at = excluded.last_seen_at
                """,
                (worker_name, now),
            )

    def get_heartbeat(self, worker_name: str = "default") -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT last_seen_at FROM worker_heartbeat WHERE worker_name = ?", (worker_name,)
            ).fetchone()
        return str(row["last_seen_at"]) if row else None

    def stats(self) -> dict[str, int]:
        with self._connect() as conn:
            listing_count = int(conn.execute("SELECT COUNT(*) FROM etsy_listings").fetchone()[0])
            rows = conn.execute("SELECT status, COUNT(*) AS count FROM pin_jobs GROUP BY status").fetchall()
        result = {"listings": listing_count, "scheduled": 0, "publishing": 0, "published": 0, "failed": 0, "cancelled": 0}
        for row in rows:
            result[str(row["status"])] = int(row["count"])
        return result

    @staticmethod
    def _listing_row(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        try:
            result["tags"] = json.loads(result.pop("tags_json", "[]"))
        except json.JSONDecodeError:
            result["tags"] = []
        return result
