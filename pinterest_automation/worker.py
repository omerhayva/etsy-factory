from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timezone
from typing import Any

from pinterest_automation.errors import AutomationError
from pinterest_automation.pinterest_client import PinterestClient
from pinterest_automation.settings import Settings
from pinterest_automation.store import PinterestStore
from pinterest_automation.tokens import TokenManager

LOGGER = logging.getLogger("pinterest_automation.worker")


class PinterestWorker:
    def __init__(
        self,
        settings: Settings,
        store: PinterestStore | None = None,
        publisher: Any | None = None,
    ):
        self.settings = settings
        self.store = store or PinterestStore(settings.database_path)
        self.store.initialize()
        self.publisher = publisher or PinterestClient(settings, TokenManager(settings))

    def publish_job(self, job_id: int, *, now: bool = False) -> dict[str, Any]:
        """Publish a queued Pin from the dashboard or CLI, bypassing its scheduled time if requested."""
        job = self.store.claim_job_now(job_id) if now else self.store.claim_specific_due_job(job_id, now=datetime.now(timezone.utc))
        if not job:
            raise AutomationError("Bu paylaşım gönderilemedi: iş bulunamadı, zamanı gelmedi veya durumu uygun değil.")
        return self._publish_claimed_job(job)

    def process_one_due_job(self) -> dict[str, Any] | None:
        self.store.heartbeat()
        self.store.recover_stale_jobs(older_than_minutes=self.settings.worker_stale_minutes)
        if not self.settings.pinterest_configured:
            return None
        job = self.store.claim_due_job(now=datetime.now(timezone.utc))
        if not job:
            return None
        return self._publish_claimed_job(job)

    def run_forever(self) -> None:
        LOGGER.info(
            "Pinterest scheduler çalışıyor; kontrol aralığı %s saniye.",
            self.settings.worker_poll_seconds,
        )
        if not self.settings.pinterest_configured:
            LOGGER.warning("Pinterest API ayarları eksik. Kuyruktaki işler korunacak, yayımlanmayacak.")
        while True:
            try:
                self.store.heartbeat()
                self.store.recover_stale_jobs(older_than_minutes=self.settings.worker_stale_minutes)
                if self.settings.pinterest_configured:
                    job = self.store.claim_due_job(now=datetime.now(timezone.utc))
                    if job:
                        self._publish_claimed_job(job)
            except Exception:
                LOGGER.exception("Scheduler döngüsünde beklenmeyen hata")
            time.sleep(self.settings.worker_poll_seconds)

    def _publish_claimed_job(self, job: dict[str, Any]) -> dict[str, Any]:
        job_id = int(job["id"])
        try:
            result = self.publisher.create_pin(job)
            pin_id = str(result.get("id") or "").strip()
            if not pin_id:
                raise AutomationError("Pinterest API Pin ID döndürmedi; iş başarısız işaretlendi.")
        except Exception as exc:
            self.store.mark_failed(job_id, str(exc))
            LOGGER.exception("Pin paylaşımı başarısız oldu: job=%s", job_id)
            return {"job_id": job_id, "status": "failed", "error": str(exc)}
        self.store.mark_published(
            job_id,
            pinterest_pin_id=pin_id,
            pin_url=f"https://www.pinterest.com/pin/{pin_id}/",
        )
        LOGGER.info("Pinterest Pin yayımlandı: job=%s pin=%s", job_id, pin_id)
        return {"job_id": job_id, "status": "published", "pinterest_pin_id": pin_id}


def main() -> None:
    parser = argparse.ArgumentParser(description="Etsy listing'lerini zamanında Pinterest'te paylaşır.")
    parser.add_argument("--once", action="store_true", help="Vakti gelen tek bir paylaşımı kontrol et ve çık.")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = Settings.from_env()
    store = PinterestStore(settings.database_path)
    worker = PinterestWorker(settings, store=store)
    if args.once:
        if not settings.pinterest_configured:
            LOGGER.error("Pinterest ayarları eksik. .env dosyasını yapılandırın.")
            raise SystemExit(2)
        result = worker.process_one_due_job()
        LOGGER.info("Kontrol tamamlandı: %s", result or "Vakti gelen iş yok.")
        return
    worker.run_forever()


if __name__ == "__main__":
    main()
