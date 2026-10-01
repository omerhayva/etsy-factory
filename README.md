# Etsy → Pinterest Scheduler

Streamlit uygulaması Etsy'deki mevcut listing'leri Pinterest Pin'lerine dönüştürmek, paylaşım kuyruğu/takvimi oluşturmak ve zamanı gelen Pin'leri Pinterest API v5 üzerinden yayımlamak için hazırlanmıştır.

## Neler yapar?

- Etsy Open API v3 ile aktif listing'leri ve ilk ürün görselini senkronize eder.
- Etsy API bağlantısı olmadan CSV ile listing içe aktarmayı destekler.
- Listing'in başlık/açıklama/etiketlerinden Pinterest Pin taslağı oluşturur; paylaşım metni düzenlenebilir.
- Pin'i seçilen board'a, seçilen yerel tarih ve saatte kuyruğa alır.
- Birden fazla listing'i belirli saat aralığıyla sıraya koyar.
- Ayrı bir worker süreci vakti gelen Pin'leri Pinterest API v5 ile yayımlar.
- Durum, hata, deneme sayısı ve Pinterest Pin bağlantısını SQLite'ta saklar.
- Access token süresi dolduğunda mevcut refresh token ile yenilemeyi dener.
- Pinterest API varsayılanı güvenli test amacıyla **Sandbox**'tır. Canlı paylaşım için production URL'yi açıkça seçin.

> Uygulama listing görselini olduğu gibi kullanır; yeni tasarım/görsel üretmez ve Etsy listing'lerini değiştirmez. İlk sürümde Pin başlığı/açıklaması kullanıcı tarafından düzenlenebilir.

## Kurulum

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Uygulamayı çalıştırma

```bash
streamlit run main.py
```

Dashboard içinden:

1. **Etsy Listing'leri** sayfasında Etsy API'yi senkronize edin veya CSV yükleyin.
2. **Paylaşım Planı** sayfasında board ID, Pin metni ve yayın zamanını seçin.
3. **Kuyruk / Geçmiş** sayfasında işleri izleyin, başarısız gönderimleri inceleyin ve gerekirse yeniden kuyruğa alın.

### CSV formatı

Uygulama `examples/etsy_listings_template.csv` şablonunu kullanır. Başlıklar:

```text
listing_id,title,description,listing_url,image_url,tags,price,state
```

`listing_id`, `title`, `listing_url` ve doğrudan erişilebilen `image_url` gereklidir. Etsy CSV'sindeki `Listing ID`, `Title`, `URL`, `Image 1` gibi başlıklar da tanınır. Etiketler virgül veya noktalı virgülle ayrılabilir. Listing ID boşsa Etsy URL'sinden çıkartılır.

## Gerçek zamanlı paylaşım için scheduler

Streamlit arayüzü planlı işleri kuyruğa alır. Zamanı geldiğinde yayımlama için worker'ın ayrıca ve sürekli çalışması gerekir:

```bash
python -m pinterest_automation.worker
```

Worker çalıştığını SQLite heartbeat kaydıyla dashboard'da gösterir. Bilgisayar kapanırsa veya worker durursa planlanan saatte gönderim yapılamaz. Sürekli kullanımda worker'ı açık kalan bir sunucuda `systemd`, Docker restart policy veya benzeri bir süreç yöneticisiyle çalıştırın.

Bir defalık kontrol:

```bash
python -m pinterest_automation.worker --once
```

## API bağlantısı ve gizli bilgiler

Gerçek API erişimi için Etsy ve Pinterest developer uygulamalarının kurulması ve kullanıcı OAuth izinlerinin alınması gerekir. Bu erişimler olmadan CSV ile içe aktarma ve paylaşım kuyruğu çalışır; **gerçek Pinterest yayını yapılamaz**. API anahtarlarını veya token'ları sohbet içinde paylaşmayın.

1. `.env.example` dosyasını proje kökünde `.env` adıyla kopyalayın.
2. Değerleri kendi ortamınızda doldurun. `.env` ve yenilenen OAuth token dosyası Git'e eklenmez.
3. Pinterest için `boards:read` ve `pins:write`; Etsy listing'lerini okumak için `listings_r` izni gerekir. Resmî kılavuzlar: [Etsy OAuth](https://developers.etsy.com/documentation/essentials/authentication/), [Pinterest OAuth](https://developers.pinterest.com/docs/getting-started/set-up-authentication-and-authorization/), [Pinterest Create Pin](https://developers.pinterest.com/docs/api/v5/pins-create/).
4. İlk denemeyi Pinterest Sandbox ile yapın. Canlı yayın için `PINTEREST_API_BASE_URL=https://api.pinterest.com/v5` ayarını açıkça yapın.

Önemli ayarlar:

| Değişken | Açıklama |
| --- | --- |
| `ETSY_API_KEYSTRING`, `ETSY_SHARED_SECRET` | Etsy Open API anahtar çifti |
| `ETSY_SHOP_ID` | Etsy mağaza ID'si |
| `ETSY_ACCESS_TOKEN`, `ETSY_REFRESH_TOKEN` | Etsy OAuth token'ları (`listings_r` scope) |
| `PINTEREST_CLIENT_ID`, `PINTEREST_CLIENT_SECRET` | Pinterest developer uygulaması |
| `PINTEREST_ACCESS_TOKEN`, `PINTEREST_REFRESH_TOKEN` | Pinterest kullanıcı OAuth token'ları |
| `PINTEREST_API_BASE_URL` | Varsayılan Sandbox; canlı API'ye geçmek için production adresi |
| `PINTEREST_DEFAULT_BOARD_ID` | Formlarda ön seçili board (isteğe bağlı) |
| `APP_TIMEZONE` | Takvim saat dilimi; varsayılan `Europe/Istanbul` |

OAuth token yenilemesi başarısız olursa bağlantı Ayarlar sayfasında hata verir. Refresh token'ın geçerlilik süresi ve uygulama erişim seviyesi ilgili platform tarafından belirlenir.

## Testler

```bash
pytest -q
```

API testleri gerçek Etsy/Pinterest hesabına istek göndermez; HTTP istemcileri mock'lanır. Böylece testler token veya ağ bağlantısı gerektirmez.

## Mevcut kapsam ve notlar

- Pinterest Pin'leri API'de kullanıcı adına oluşturulur; başlık 100, açıklama 800, alt metin 500 karakter sınırında tutulur.
- Listing görseli Pinterest'e base64 medya kaynağı olarak gönderilir; Etsy CDN URL'sinin Pinterest tarafından ayrıca indirilmesine bağımlı değildir.
- Aynı listing/board/zaman için yinelenen aktif kuyruk işi engellenir.
- Gönderim sırasında worker kapanırsa olası çift Pin riskine karşı iş otomatik tekrar gönderilmez; geçmişte başarısız olarak işaretlenir ve kullanıcı kontrolünden sonra yeniden kuyruğa alınabilir.
- Repo içindeki `research/`, `product_factory/` ve ilgili intelligence modülleri eski POD araştırma prototipinden kalmıştır; yeni `main.py` akışında kullanılmaz.
