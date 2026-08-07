# Design Intelligence Report

## Ozet
Design Intelligence Engine, platformin kreatif karar katmani olarak eklendi. Bu motor sadece prompt uretmez; her niche ve urun icin en yuksek ticari olasiliga sahip gorsel stili secer.

Karar girdileri zorunlu olarak su motorlardan gelir:
- Research Engine
- Niche Intelligence Engine
- Product Intelligence Engine

## Mimari
Yeni modul: `design_intelligence/`

Dosyalar:
- `engine.py`
- `style_analyzer.py`
- `color_engine.py`
- `typography_engine.py`
- `layout_engine.py`
- `composition.py`
- `prompt_builder.py`
- `quality_score.py`
- `design_variations.py`
- `mockup_strategy.py`
- `trend_styles.py`
- `report_generator.py`

Mimari ozellikler:
- Dependency Injection: `DesignIntelligenceEngine(db, style_library=...)`
- Repository Pattern: tum persistence islemleri `EtsyDatabase` uzerinden
- Moduler analiz: style, color, typography, layout, quality, prompt ayri bileşenlerde
- Logging ve hata yonetimi: engine seviyesinde try/except + session status

## Style Recommendation
`style_analyzer.py` icinde genisletilebilir style library bulunur.

Kapsanan minimum stiller:
Vintage, Retro, Minimal, Modern, Luxury, Boho, Rustic, Watercolor, Line Art, Hand Drawn, Botanical, Floral, Cute, Cartoon, Comic, Cyberpunk, Neon, Gothic, Dark Academia, Cottagecore, Y2K, Minimal Typography, Bold Typography, Distressed, Geometric, Abstract, Christian, Islamic, Japanese, Scandinavian.

Skorlama sinyalleri:
- Niche keyword uyumu
- Product uyumu
- Audience uyumu
- Season uyumu
- Trend signal
- Gift signal
- `trend_styles.py` ile trend tabanli style bias

## Prompt Generation
`prompt_builder.py` su providerlari destekler:
- Midjourney
- DALL-E
- Stable Diffusion
- Flux
- Future providers (genel fallback)

Her prompt paketinde:
- Subject
- Style
- Composition
- Lighting
- Colors
- Typography guidance
- Print-ready instructions
- Negative prompt guidance

## Color, Typography, Layout, Composition
- Color Intelligence (`color_engine.py`): Monochrome, Pastel, Earth Tone, Vintage Palette, High Contrast, Muted Colors, Luxury Palette, Retro Palette, Dark Theme, Seasonal Colors
- Typography (`typography_engine.py`): Serif, Sans Serif, Script, Handwritten, Vintage, Retro, Luxury, Minimal, Decorative, Bold, Playful
- Layout (`layout_engine.py`): Centered, Top Heavy, Bottom Heavy, Circular, Badge, Minimal, Full Front, Pocket Style, Symmetrical, Asymmetrical
- Composition (`composition.py`): image/text ratio, whitespace, hierarchy, icon placement, border/frame

## Quality Scoring
`quality_score.py` hesaplar:
- Print Quality
- Visual Balance
- Commercial Appeal
- Gift Appeal
- Brandability
- Readability
- Production Suitability
- Overall Design Score

## Design Variations
`design_variations.py` her niche+urun icin otomatik uretir:
- Minimal version
- Premium version
- Vintage version
- Modern version
- Typography-focused version
- Illustration-focused version

## Mockup Strategy
`mockup_strategy.py` onerir:
- Lifestyle
- Studio
- Flat Lay
- Outdoor
- Holiday
- Office
- Home
- Gift Scene

Oneriler product ve audience sinyallerine gore siralanir.

## Database Entegrasyonu
Eklenen tablolar:
- `design_styles`
- `design_scores`
- `color_palettes`
- `typography_profiles`
- `layout_profiles`
- `design_prompts`
- `design_variations`
- `mockup_recommendations`

Eklenen repository metodlari:
- save_* ve fetch_* metotlari (`fetch_design_intelligence_overview`, `fetch_design_prompts`, `fetch_design_variations`, `fetch_mockup_recommendations`, `fetch_latest_design_intelligence_session`)

## Dashboard Entegrasyonu
`dashboard/app.py` icine "Design Intelligence" sayfasi eklendi.

Gorunur bolumler:
- Recommended Style
- Recommended Colors
- Typography
- Design Score
- Generated AI Prompts
- Design Variations
- Mockup Suggestions

## Export
Tam design package export:
- CSV
- JSON
- Markdown

Dosya seti:
- session_*_design_intelligence_report.json
- session_*_design_intelligence_report.csv
- session_*_design_package.json
- session_*_design_package.csv
- session_*_design_package.md

## Future AI Provider Integration
Yeni provider entegrasyonu icin:
1. Prompt builder icinde provider kurali eklenir.
2. Provider-specific parametreler (ratio, stylize, safety vb.) merkezi mapping ile tanimlanir.
3. Engine akisi degismeden prompt paketi yeni provideri uretir.

Bu yapiyla Design Intelligence modulu SEO Intelligence asamasi icin hazir ve genisletilebilir durumdadir.
