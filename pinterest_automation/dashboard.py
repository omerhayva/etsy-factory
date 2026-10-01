from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd
import streamlit as st

from pinterest_automation.errors import AutomationError, DuplicateScheduleError
from pinterest_automation.etsy_client import EtsyClient
from pinterest_automation.listing_import import listings_to_csv, parse_listings_csv
from pinterest_automation.pin_copy import build_pin_copy
from pinterest_automation.pinterest_client import PinterestClient
from pinterest_automation.settings import Settings
from pinterest_automation.store import PinterestStore
from pinterest_automation.tokens import TokenManager
from pinterest_automation.worker import PinterestWorker

APP_TITLE = "Etsy → Pinterest Scheduler"


def _get_timezone(settings: Settings):
    try:
        return ZoneInfo(settings.timezone_name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def _format_local(value: str | None, timezone: Any) -> str:
    if not value:
        return "—"
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))
        return parsed.astimezone(timezone).strftime("%Y-%m-%d %H:%M %Z")
    except (ValueError, TypeError):
        return str(value)


def _listing_label(listing: dict[str, Any]) -> str:
    title = str(listing.get("title") or "Untitled listing")
    if len(title) > 64:
        title = title[:61] + "..."
    return f"{title}  ·  #{listing.get('listing_id', '')}"


def _show_connection_status(settings: Settings) -> None:
    col1, col2 = st.columns(2)
    with col1:
        if settings.etsy_configured:
            st.success("Etsy API yapılandırılmış")
        else:
            st.warning("Etsy API bağlı değil — CSV ile listing içe aktarabilirsiniz.")
            missing = settings.missing_etsy_settings()
            if missing:
                st.caption("Eksik ayarlar: " + ", ".join(missing))
    with col2:
        if settings.pinterest_configured:
            st.success("Pinterest API yapılandırılmış")
        else:
            st.warning("Pinterest API bağlı değil — işler kuyruğa eklenebilir, yayımlanamaz.")
            missing = settings.missing_pinterest_settings()
            if missing:
                st.caption("Eksik ayarlar: " + ", ".join(missing))


def _read_uploaded_csv(file) -> tuple[int, list[str]]:
    listings, errors = parse_listings_csv(file.getvalue())
    store = st.session_state["pin_store"]
    imported = store.upsert_listings(listings)
    return imported, errors


def _fetch_boards(settings: Settings) -> list[dict[str, Any]]:
    return PinterestClient(settings, TokenManager(settings)).list_boards()


def _render_home(store: PinterestStore, settings: Settings, timezone: Any) -> None:
    st.subheader("Paylaşım merkezi")
    st.write(
        "Etsy ürünlerini içe aktarın, Pinterest panosuna bağlayın ve paylaşım saatlerini kuyruğa alın. "
        "Zamanı gelen Pin'leri yayımlamak için scheduler worker ayrı bir süreçte açık kalmalıdır."
    )
    _show_connection_status(settings)

    stats = store.stats()
    cols = st.columns(5)
    cols[0].metric("Etsy listing", stats["listings"])
    cols[1].metric("Kuyrukta", stats["scheduled"])
    cols[2].metric("Yayımlandı", stats["published"])
    cols[3].metric("Başarısız", stats["failed"])
    cols[4].metric("Gönderiliyor", stats["publishing"])

    heartbeat = store.get_heartbeat()
    if heartbeat:
        st.caption(f"Worker son sinyal: {_format_local(heartbeat, timezone)}")
    else:
        st.info("Scheduler worker henüz çalışmamış. Ayrı terminalde `python -m pinterest_automation.worker` komutunu başlatın.")

    upcoming = [job for job in store.list_jobs(status="scheduled", limit=50)]
    if upcoming:
        st.markdown("#### Yaklaşan paylaşımlar")
        frame = pd.DataFrame(
            [
                {
                    "Saat": _format_local(job["scheduled_at"], timezone),
                    "Listing": job["listing_title"],
                    "Pinterest başlığı": job["title"],
                    "Board ID": job["board_id"],
                    "Durum": job["status"],
                }
                for job in sorted(upcoming, key=lambda item: item["scheduled_at"])
            ]
        )
        st.dataframe(frame, hide_index=True, use_container_width=True)
    else:
        st.info("Henüz planlanmış paylaşım yok. Önce Etsy listing içe aktarın, sonra Paylaşım Planı sayfasından Pin ekleyin.")

    with st.expander("Bu uygulama nasıl çalışır?"):
        st.markdown(
            "1. **Etsy Listings:** Etsy Open API ile aktif listing'leri senkronize edin veya CSV yükleyin.\n"
            "2. **Paylaşım Planı:** Board, görsel, Etsy hedef bağlantısı ve zaman seçip Pin kuyruğu oluşturun.\n"
            "3. **Scheduler:** `python -m pinterest_automation.worker` sürecini sürekli çalışır bırakın.\n"
            "4. **Takip:** Kuyruk / Geçmiş sayfasında başarılı ve başarısız gönderimleri izleyip gerektiğinde yeniden deneyin.\n\n"
            "Uygulama API anahtarlarını sohbetten istemez. Gizli değerleri proje kökündeki `.env` dosyasında tutun; bu dosya Git'e eklenmez."
        )


def _render_listings(store: PinterestStore, settings: Settings) -> None:
    st.subheader("Etsy listing'leri")
    st.caption("Etsy API bağlantısı olmadan da CSV ile listing ekleyebilirsiniz.")

    api_col, sync_col = st.columns([3, 1])
    with api_col:
        if settings.etsy_configured:
            st.success(f"Etsy shop ID: {settings.etsy_shop_id}")
        else:
            st.info("Etsy API ayarları eksik. Ayarlar sekmesinden `.env` kurulum talimatlarını görebilirsiniz.")
    with sync_col:
        max_listings = st.number_input("Senkron limiti", min_value=1, max_value=500, value=100, step=25)
        if st.button("Etsy'den senkronize et", disabled=not settings.etsy_configured, use_container_width=True):
            try:
                with st.spinner("Etsy listing'leri alınıyor…"):
                    listings = EtsyClient(settings).list_active_listings(max_listings=int(max_listings))
                    imported = store.upsert_listings(listings)
                st.success(f"{imported} aktif listing senkronize edildi.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Etsy senkronizasyonu başarısız: {exc}")

    st.markdown("#### CSV ile içe aktar")
    st.download_button(
        "CSV şablonunu indir",
        listings_to_csv([]).encode("utf-8-sig"),
        file_name="etsy_listings_template.csv",
        mime="text/csv",
    )
    uploaded = st.file_uploader(
        "listing_id, title, description, listing_url, image_url, tags, price sütunlarını içeren CSV",
        type=["csv"],
        key="etsy_listing_csv",
    )
    if uploaded is not None and st.button("CSV'yi içe aktar", key="import_listings_csv"):
        try:
            imported, errors = _read_uploaded_csv(uploaded)
            st.success(f"{imported} listing eklendi veya güncellendi.")
            for error in errors[:20]:
                st.warning(error)
            if len(errors) > 20:
                st.caption(f"{len(errors) - 20} ek satır hatası gizlendi.")
        except AutomationError as exc:
            st.error(str(exc))
        except Exception as exc:  # noqa: BLE001
            st.error(f"CSV içe aktarılamadı: {exc}")

    listings = store.list_listings(limit=500)
    st.markdown(f"#### Kaydedilmiş listing'ler ({len(listings)})")
    if not listings:
        st.info("Henüz listing yok. Etsy API senkronizasyonu veya CSV içe aktarma ile başlayın.")
        return
    search = st.text_input("Listing ara", key="listing_search")
    if search.strip():
        listings = store.list_listings(limit=500, search=search)
    frame = pd.DataFrame(
        [
            {
                "Listing ID": item["listing_id"],
                "Başlık": item["title"],
                "Durum": item["state"],
                "Fiyat": item["price"],
                "Etiketler": ", ".join(item.get("tags", [])),
                "Görsel": "Var" if item.get("image_url") else "Yok",
                "Kaynak": item["source"],
                "Senkron": item["synced_at"],
            }
            for item in listings
        ]
    )
    st.dataframe(frame, hide_index=True, use_container_width=True)


def _board_selector(settings: Settings) -> str:
    board_id = settings.pinterest_default_board_id
    cached = st.session_state.get("pinterest_boards", [])
    if cached:
        by_id = {str(board.get("id")): board for board in cached if board.get("id")}
        ids = list(by_id)
        default_index = ids.index(board_id) if board_id in ids else 0
        selected = st.selectbox(
            "Pinterest panosu",
            ids,
            index=default_index,
            format_func=lambda value: f"{by_id[value].get('name', 'Board')}  ·  {value}",
        )
        return str(selected)
    return st.text_input("Pinterest board ID", value=board_id, help="Board ID'yi Pinterest Ayarlar sayfasından veya API ile alın.")


def _render_schedule(store: PinterestStore, settings: Settings, timezone: Any) -> None:
    st.subheader("Paylaşım planı")
    if not settings.pinterest_configured:
        st.warning("Pinterest API bağlı değil. Paylaşım kuyruğu hazırlayabilirsiniz; canlı gönderim için Ayarlar'daki bağlantıyı tamamlayın.")

    board_col, refresh_col = st.columns([3, 1])
    with refresh_col:
        if st.button("Board'ları getir", disabled=not settings.pinterest_configured, use_container_width=True):
            try:
                st.session_state["pinterest_boards"] = _fetch_boards(settings)
                st.success(f"{len(st.session_state['pinterest_boards'])} pano yüklendi.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Pinterest panoları alınamadı: {exc}")
    with board_col:
        board_id = _board_selector(settings)

    listings = store.list_listings(limit=500)
    if not listings:
        st.info("Önce Etsy listing'lerini senkronize edin veya CSV ile içe aktarın.")
        return
    by_id = {str(item["listing_id"]): item for item in listings}
    labels = {_listing_label(item): str(item["listing_id"]) for item in listings}
    default_date = datetime.now(timezone).date() + timedelta(days=1)
    default_time = time(10, 0)

    st.markdown("#### Tek listing planla")
    selected_label = st.selectbox("Etsy listing", list(labels), key="single_listing_choice")
    listing_id = labels[selected_label]
    listing = by_id[listing_id]
    if listing.get("image_url"):
        st.image(listing["image_url"], caption=listing["title"], width=260)
    else:
        st.error("Bu listing'de görsel URL yok; Pin oluşturmak için görsel ekleyin veya listing'i Etsy'den yeniden senkronize edin.")
    default_title, default_description, default_alt = build_pin_copy(listing)

    with st.form("schedule_single_pin"):
        title = st.text_input("Pin başlığı (en fazla 100 karakter)", value=default_title, max_chars=100)
        description = st.text_area("Pin açıklaması (en fazla 800 karakter)", value=default_description, max_chars=800)
        alt_text = st.text_input("Görsel alt metni", value=default_alt, max_chars=500)
        date_col, time_col = st.columns(2)
        publish_date = date_col.date_input("Yayın tarihi", value=default_date, key="single_publish_date")
        publish_time = time_col.time_input("Yayın saati", value=default_time, key="single_publish_time")
        submit_single = st.form_submit_button("Paylaşımı kuyruğa ekle", type="primary", use_container_width=True)

    if submit_single:
        if not board_id.strip():
            st.error("Pinterest board ID girin veya board listesini yükleyin.")
        elif not listing.get("image_url"):
            st.error("Bu listing'in Pinterest'te paylaşılabilecek görseli yok.")
        else:
            scheduled_local = datetime.combine(publish_date, publish_time).replace(tzinfo=timezone)
            if scheduled_local <= datetime.now(timezone):
                st.error("Yayın zamanı gelecekte olmalı. Hemen yayınlamak için Kuyruk sayfasını kullanın.")
            else:
                try:
                    job_id = store.schedule_pin(
                        listing=listing,
                        board_id=board_id,
                        title=title,
                        description=description,
                        alt_text=alt_text,
                        scheduled_at=scheduled_local,
                    )
                    st.success(f"Paylaşım kuyruğa eklendi (Job #{job_id}).")
                except (ValueError, DuplicateScheduleError) as exc:
                    st.error(str(exc))

    with st.expander("Birden fazla listing'i aralıklı planla"):
        with st.form("schedule_batch_pins"):
            selected_ids = st.multiselect(
                "Listing'ler",
                list(by_id),
                format_func=lambda value: _listing_label(by_id[value]),
                key="batch_listing_choices",
            )
            batch_start_date = st.date_input("İlk Pin tarihi", value=default_date, key="batch_publish_date")
            batch_start_time = st.time_input("İlk Pin saati", value=default_time, key="batch_publish_time")
            spacing_hours = st.number_input("Paylaşımlar arası saat", min_value=1, max_value=720, value=24, step=1)
            submit_batch = st.form_submit_button("Seçilenleri sıraya koy", use_container_width=True)
        if submit_batch:
            if not board_id.strip():
                st.error("Pinterest board ID girin veya board listesini yükleyin.")
            elif not selected_ids:
                st.error("En az bir listing seçin.")
            else:
                start_local = datetime.combine(batch_start_date, batch_start_time).replace(tzinfo=timezone)
                if start_local <= datetime.now(timezone):
                    st.error("İlk yayın zamanı gelecekte olmalı.")
                else:
                    created = []
                    failures = []
                    for index, selected_id in enumerate(selected_ids):
                        selected_listing = by_id[str(selected_id)]
                        if not selected_listing.get("image_url"):
                            failures.append(f"{selected_listing['title']}: görsel bulunamadı")
                            continue
                        pin_title, pin_description, pin_alt = build_pin_copy(selected_listing)
                        try:
                            job_id = store.schedule_pin(
                                listing=selected_listing,
                                board_id=board_id,
                                title=pin_title,
                                description=pin_description,
                                alt_text=pin_alt,
                                scheduled_at=start_local + timedelta(hours=int(spacing_hours) * index),
                            )
                            created.append(job_id)
                        except (ValueError, DuplicateScheduleError) as exc:
                            failures.append(f"{selected_listing['title']}: {exc}")
                    if created:
                        st.success(f"{len(created)} paylaşım kuyruğa eklendi: {', '.join(f'#{job}' for job in created)}")
                    for failure in failures:
                        st.warning(failure)


def _jobs_frame(jobs: list[dict[str, Any]], timezone: Any) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Job": job["id"],
                "Yayın zamanı": _format_local(job["scheduled_at"], timezone),
                "Etsy listing": job["listing_title"],
                "Pin başlığı": job["title"],
                "Board ID": job["board_id"],
                "Durum": job["status"],
                "Deneme": job["attempt_count"],
                "Pinterest Pin ID": job["pinterest_pin_id"] or "—",
                "Hata": job["last_error"] or "—",
            }
            for job in jobs
        ]
    )


def _render_queue(store: PinterestStore, settings: Settings, timezone: Any) -> None:
    st.subheader("Kuyruk ve geçmiş")
    flash = st.session_state.pop("queue_flash", None)
    if flash:
        level, message = flash
        if level == "success":
            st.success(message)
        else:
            st.error(message)
    status = st.selectbox("Durum filtresi", ["all", "scheduled", "publishing", "published", "failed", "cancelled"], format_func=lambda value: "Tümü" if value == "all" else value)
    jobs = store.list_jobs(status=status, limit=500)
    if not jobs:
        st.info("Bu filtrede paylaşım yok.")
        return
    st.dataframe(_jobs_frame(jobs, timezone), hide_index=True, use_container_width=True)

    job_options = [f"#{job['id']} · {job['listing_title']} · {job['status']}" for job in jobs]
    option_to_job = {label: int(job["id"]) for label, job in zip(job_options, jobs)}
    selected = st.selectbox("İşlem yapılacak paylaşım", job_options)
    job_id = option_to_job[selected]
    job = store.get_job(job_id)
    if job and job.get("pinterest_pin_url"):
        st.link_button("Pinterest Pin'ini aç", job["pinterest_pin_url"])
    if job:
        st.image(job["image_url"], caption=job["title"], width=240)
        st.caption(f"Etsy hedefi: {job['link']}")
        st.write(job["description"])

    cancel_col, send_col, retry_col = st.columns(3)
    with cancel_col:
        if st.button("İptal et", disabled=not job or job["status"] not in {"scheduled", "failed"}, use_container_width=True):
            if store.cancel_job(job_id):
                st.session_state["queue_flash"] = ("success", "Paylaşım iptal edildi.")
            else:
                st.session_state["queue_flash"] = ("error", "Bu iş iptal edilemiyor.")
            st.rerun()
    with send_col:
        if st.button("Şimdi Pinterest'e gönder", disabled=not settings.pinterest_configured or not job or job["status"] not in {"scheduled", "failed"}, type="primary", use_container_width=True):
            try:
                result = PinterestWorker(settings, store=store).publish_job(job_id, now=True)
                if result["status"] == "published":
                    st.session_state["queue_flash"] = ("success", f"Pin yayımlandı: {result['pinterest_pin_id']}")
                else:
                    st.session_state["queue_flash"] = ("error", result.get("error", "Pinterest gönderimi başarısız."))
            except Exception as exc:  # noqa: BLE001
                st.session_state["queue_flash"] = ("error", str(exc))
            st.rerun()
    with retry_col:
        if st.button("Başarısız işi yeniden kuyruğa al", disabled=not job or job["status"] != "failed", use_container_width=True):
            if store.retry_job(job_id):
                st.session_state["queue_flash"] = ("success", "İş yeniden kuyruğa alındı; worker zamanı gelince tekrar deneyecek.")
            else:
                st.session_state["queue_flash"] = ("error", "İş yeniden kuyruğa alınamadı.")
            st.rerun()


def _render_settings(settings: Settings) -> None:
    st.subheader("Bağlantı ayarları")
    _show_connection_status(settings)
    st.caption(f"Pinterest API endpoint: `{settings.pinterest_api_base_url}`")
    if "sandbox" in settings.pinterest_api_base_url.lower():
        st.info("Sandbox açık: test gönderileri üretim Pinterest hesabına yayımlanmaz.")
    else:
        st.warning("Production API açık: gönderilen Pin'ler gerçek Pinterest hesabında yayımlanır.")
    st.markdown("""
    API anahtarlarını uygulama ekranına yazmayın. Repo kökünde `.env.example` dosyasını `.env` olarak kopyalayın ve gizli değerleri yalnızca kendi ortamınızda doldurun. `.env` ve OAuth token dosyası Git dışında tutulur.

    **Etsy:** Etsy developer uygulamasından API keystring/shared secret alın; OAuth token'ı `listings_r` scope'u ile oluşturun. Shop ID ve token değerlerini `.env`'e ekleyin. Access token süresi dolduğunda refresh token otomatik yenilenir.

    **Pinterest:** Pinterest Developer uygulaması oluşturup `boards:read` ve `pins:write` izinli kullanıcı OAuth token'ı kullanın. İlk test için Sandbox API adresi kullanılabilir; gerçek paylaşımlar için production API erişimi gerekir. Access token yenileme, client ID/secret ve refresh token ayarlıysa otomatik yapılır.
    """)

    st.markdown("#### Scheduler")
    st.code("python -m pinterest_automation.worker", language="bash")
    st.caption(
        f"Worker kontrol aralığı: {settings.worker_poll_seconds} saniye · "
        f"Saat dilimi: {settings.timezone_name} · Veritabanı: {settings.database_path}"
    )
    st.markdown("#### API bağlantı testi")
    etsy_col, pinterest_col = st.columns(2)
    with etsy_col:
        if st.button("Etsy bağlantısını test et", disabled=not settings.etsy_configured, use_container_width=True):
            try:
                listings = EtsyClient(settings).list_active_listings(max_listings=1)
                st.success(f"Etsy bağlantısı başarılı. Örnek listing sayısı: {len(listings)}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Etsy bağlantı testi başarısız: {exc}")
    with pinterest_col:
        if st.button("Pinterest bağlantısını test et", disabled=not settings.pinterest_configured, use_container_width=True):
            try:
                boards = PinterestClient(settings).list_boards()
                st.success(f"Pinterest bağlantısı başarılı. Board sayısı: {len(boards)}")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Pinterest bağlantı testi başarısız: {exc}")


def run_dashboard() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="📌", layout="wide")
    settings = Settings.from_env()
    store = PinterestStore(settings.database_path)
    store.initialize()
    st.session_state["pin_store"] = store
    timezone = _get_timezone(settings)

    st.title(APP_TITLE)
    st.caption("Etsy listing'lerini Pinterest'e planlı ve takip edilebilir şekilde paylaşın.")
    page = st.sidebar.radio(
        "Menü",
        ["Genel Bakış", "Etsy Listing'leri", "Paylaşım Planı", "Kuyruk / Geçmiş", "Ayarlar"],
    )

    if page == "Genel Bakış":
        _render_home(store, settings, timezone)
    elif page == "Etsy Listing'leri":
        _render_listings(store, settings)
    elif page == "Paylaşım Planı":
        _render_schedule(store, settings, timezone)
    elif page == "Kuyruk / Geçmiş":
        _render_queue(store, settings, timezone)
    elif page == "Ayarlar":
        _render_settings(settings)
