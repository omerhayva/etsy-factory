# Product Intelligence Engine Report

## Ozet
Product Intelligence Engine, mevcut Research + Niche Intelligence verilerini urun secim kararina donusturen adapter tabanli bir motor olarak eklendi. Cozum, veritabani katmanini genisletir, provider bagimsiz urun degerlendirmesi yapar, skorlar ve raporlar uretir.

## Mimari
- `product_intelligence/provider_adapter.py`
  - `BasePODProviderAdapter`: Provider sozlesmesi.
  - `GenericPODProviderAdapter`: Varsayilan provider davranisi.
- `product_intelligence/catalog.py`
  - Giyim, aksesuar, ev/dekor, ofis, sezonluk gruplari iceren genisletilebilir urun katalogu.
- `product_intelligence/engine.py`
  - Niche Intelligence ciktilarini okuyup urun eslestirme/skorlama/analizleri calistiran orkestrator.
- Yardimci analiz modulleri:
  - `matching.py`, `pricing.py`, `profit.py`, `shipping.py`, `quality.py`, `risk.py`, `recommendations.py`
- Raporlama:
  - `report_generator.py` ile dashboard uyumlu KPI listeleri + CSV/JSON disa aktarim.

## Eslestirme ve Skorlama Mantigi
Girdi sinyalleri:
- Niche
- Audience (hazir alan, su an bos listeden gelebilir)
- Season
- Competition
- Gift Intent
- Trend
- Evergreen Score

Urun skoru (0-100 araligina kisitlanir):
- Popularity
- Gift alignment
- Competition advantage
- Trend + evergreen uyumu
- Tahmini kar marji
- Print area
- Seasonal bonus
- Customization ve shipping penaltilari

## Karlilik Hesabi
- Onerilen satis fiyati: talep + trend sinyaline gore tipik fiyatin dinamik ayarlanmasi.
- Gross profit = satis fiyati - uretim maliyeti.
- Margin % = gross profit / satis fiyati * 100.
- Onerilen indirim araligi otomatik hesaplanir.

## Shipping / Quality / Risk
- Shipping:
  - Shipping difficulty
  - Packaging complexity
  - Damage risk
  - International suitability
- Quality:
  - Design visibility
  - Print quality expectation
  - Color flexibility
  - Customer satisfaction potential
- Risk:
  - Return risk
  - Complaint risk
  - Sizing issue risk
  - Fragility risk
  - Seasonality risk

## Dashboard Entegrasyonu
`dashboard/app.py` icinde `Urunler` sayfasi Product Intelligence paneliyle genisletildi:
- Top Recommended Products
- Highest Profit Products
- Lowest Risk Products
- Gift Product Ranking
- Seasonal Opportunities
- Product Intelligence calistirma butonu ve son oturum gorunumu

## Veritabani Entegrasyonu
Kullanilan tablolar:
- `product_catalog`
- `product_scores`
- `product_profit`
- `product_shipping`
- `product_quality`
- `product_risk`
- `product_recommendations`

Ek olarak:
- `fetch_niche_intelligence_overview` sorgusuna `competition_score` eklendi.
- `fetch_latest_product_intelligence_session` eklendi.

## Disa Aktarim
Product Intelligence calistiginda:
- Kategori bazli raporlar: JSON + CSV
- Tum oneriler: JSON + CSV

## Test Kapsami
Yeni test:
- `tests/test_product_intelligence.py`
  - Niche Intelligence + Product Intelligence ardışık calisimi
  - Session/row/export dogrulama
  - Product recommendation/profit/risk tablo dolulugu kontrolu

## Gelecek Provider Entegrasyonu
Provider adapter mimarisi nedeniyle Printify/Printful/Gelato entegrasyonu asagidaki adimlarla yapılabilir:
1. Yeni adapter sinifi eklenir (BasePODProviderAdapter implementasyonu).
2. Provider bazli uretim maliyeti, shipping ve kalite carpani uygulanir.
3. Engine olusturulurken provider listesine eklenir.

Bu sekilde cekirdek is kurallari degismeden yeni providerlar sisteme dahil edilir.
