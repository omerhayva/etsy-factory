# Etsy → Pinterest Scheduler — Durum Raporu

## Amaç
Kullanıcının mevcut Etsy listing'lerini Pinterest board'larında düzenli paylaşmak; içerik ve zaman planını yönetmek, Pin'leri resmi Pinterest API v5 ile yayımlamak.

## Uygulanan akış

1. Etsy Open API v3 üzerinden aktif listing senkronizasyonu veya CSV import.
2. Listing görseli, Etsy bağlantısı, title, description ve tags ile Pin taslağı.
3. Tekil veya aralıklı toplu zamanlama.
4. SQLite tabanlı kuyruk, durum takibi, hata kaydı ve manuel yeniden deneme.
5. Ayrı worker süreci ile zamanı gelen Pin'leri Pinterest'e yayımlama.

## Test durumu

- Etsy/Pinterest API çağrıları için izole mock testleri.
- CSV import, SQLite kuyruk/claim, Pin medya payload'ı ve worker akışı test kapsamındadır.
- Gerçek platforma yayın için kullanıcının kendi developer uygulama bilgileri ve OAuth izinleri gerekir.

## Güvenlik

API bilgileri `.env`/yerel OAuth token dosyasında tutulur; repo'ya eklenmez. Yeni kurulumda Pinterest Sandbox varsayılandır. Production'a geçiş açıkça yapılandırılır.

> Eski POD araştırma ve `Product Factory` paketleri repoda legacy kod olarak durmaktadır; `main.py` artık bu modülleri başlatmaz.
