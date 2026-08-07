# SEO Compliance Intelligence Report

## Ozet
SEO, Compliance & Listing Intelligence Engine platformin final quality gate katmani olarak eklendi. Bu motor her listingi yayin oncesi SEO, policy, spam ve hukuki risk acisindan degerlendirir.

Temel prensip: Etsy policy uyumu, kisa vadeli SEO kazancindan onceliklidir.

## Mimari
Yeni modul: seo_intelligence/

Dosyalar:
- engine.py
- title_generator.py
- description_generator.py
- tags_generator.py
- keyword_optimizer.py
- buyer_intent.py
- listing_optimizer.py
- listing_validator.py
- listing_quality.py
- compliance_engine.py
- policy_engine.py
- policy_loader.py
- policy_manager.py
- risk_engine.py
- trademark_checker.py
- copyright_checker.py
- spam_detector.py
- ai_disclosure.py
- listing_score.py
- publish_decision.py
- report_generator.py

Mimari ozellikler:
- Repository Pattern: tum persistence `database/db.py` uzerinden
- Dependency Injection: `SeoComplianceIntelligenceEngine(db, policy_manager=...)`
- Moduler tasarim: SEO, compliance, risk, quality, decision ayrik bileşenler
- Error handling ve session lifecycle: run-level try/except + session status

## Policy System
Hardcoded policy yoktur.

Policy kaynaklari:
- policies/etsy_policy.yaml
- policies/policy_version.json

Saklanan alanlar:
- Policy Version
- Last Updated
- Policy Notes
- Policy Rules
- Validation Rules

`PolicyLoader` ve `PolicyManager` sayesinde policy update islemleri kod degisikligi olmadan dosya bazli yonetilir.

## SEO Workflow
1. Research + Niche + Product + Design ciktilari birlestirilir
2. Keyword kategorileri uretilir (primary/secondary/long-tail/seasonal/gift/audience/lifestyle/commercial)
3. Buyer intent siniflandirilir
4. Coklu title versiyonlari uretilir
5. 13 adet tag uretilir
6. Zorunlu section'lari iceren profesyonel description olusturulur
7. Listing optimizer final package secimini yapar

## Compliance Checks
Engine her listingte su kontrolleri uygular:
- Policy validation
- Listing completeness validation
- Spam detection
- Trademark risk
- Copyright risk
- Duplicate listing sinyali

Uretilen ciktilar:
- Compliance score
- Warnings
- Suggested fixes
- Risk level

## Risk Analysis
- Trademark risk seviyeleri: Low, Medium, High, Critical
- Copyright risk seviyesi ve oneriler
- Final risk level: en yuksek risk kaynagına gore belirlenir
- High/Critical listingler otomatik publish onayi alamaz

## Quality Scoring
Skorlanan metrikler:
- SEO Score
- Compliance Score
- Commercial Score
- Buyer Intent Score
- Gift Score
- Readability Score
- Visual Compatibility Score
- Competition Score
- Originality Score
- Expected Conversion Score
- Trust Score
- Overall Listing Score

## Publish Decision Logic
Final kararlar:
- READY FOR PUBLISH
- NEEDS IMPROVEMENT

Karar kosullari:
- Policy threshold'leri
- Overall score threshold'i
- Compliance threshold'i
- Risk level blok listesi (High/Critical)
- Warnings/fixes varligi

## Database Entegrasyonu
Eklenen tablolar:
- seo_titles
- seo_tags
- seo_descriptions
- listing_scores
- listing_quality
- policy_checks
- spam_reports
- buyer_intent
- publish_reports
- ai_disclosures
- listing_reports

Ek repository metodlari:
- save_* ve fetch_* metotlari
- fetch_latest_seo_intelligence_session
- fetch_seo_listing_overview
- fetch_publish_decisions
- fetch_risk_alerts

## Dashboard Entegrasyonu
Dashboard'a yeni sayfa eklendi: SEO Intelligence

Gosterilen bolumler:
- SEO Intelligence
- Compliance Center
- Listing Validator
- Listing Preview
- Quality Score
- Publish Decision
- Risk Alerts

## Export
Tam listing paketi export edilir:
- CSV
- JSON
- Markdown

## Gelecek Iyilestirmeler
- Harici trademark/copyright API entegrasyonu
- Gercek zamanli policy sync
- Dil bazli SEO tuning
- A/B title scoring modelleri
- Niche bazli compliance auto-learn
