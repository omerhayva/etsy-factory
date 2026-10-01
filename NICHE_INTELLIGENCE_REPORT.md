# Niche Intelligence Report

> Historical documentation for the previous POD factory prototype. The active application is now the Etsy → Pinterest Scheduler; see `README.md`.

## Architecture

The Niche Intelligence Engine is implemented as a separate package that extends the current system:

- `niche_intelligence/engine.py`: orchestration entry point
- `niche_intelligence/models.py`: shared dataclasses
- `niche_intelligence/scoring.py`: weighted score computation and niche class mapping
- `niche_intelligence/audience.py`: audience and buyer intent discovery
- `niche_intelligence/seasonality.py`: seasonal event and seasonal flag analysis
- `niche_intelligence/competition.py`: competition label and numeric scoring
- `niche_intelligence/giftability.py`: gift suitability and recipient mapping
- `niche_intelligence/evergreen.py`: evergreen/seasonal/trending/temporary/declining classification
- `niche_intelligence/recommendations.py`: recommendation text and reasoning builder
- `niche_intelligence/report_generator.py`: structured reports + JSON/CSV export

Integration points:

- Uses `EtsyDatabase` repository methods for all persistence.
- Consumes Research Engine output via `niches` / opportunity views.
- Exposes results to dashboard sections under `Arastirma`.

## Scoring System

Overall niche score uses these weights:

- Demand: 25%
- Competition: 20% (as competition advantage)
- Profit: 20%
- Trend: 15%
- Gift Potential: 10%
- Evergreen: 5%
- Design Simplicity: 5%

Outputs:

- `overall_score` (0-100)
- `confidence` (0-100)
- `risk_level` (`Low`, `Moderate`, `Elevated`, `High`)
- `classification` (`Gold`, `Silver`, `Bronze`, `Watchlist`, `Avoid`)

## Recommendation Logic

Classification to action mapping:

- Gold: Scale aggressively
- Silver: Launch and optimize
- Bronze: Test small batches
- Watchlist: Monitor trend shifts
- Avoid: Avoid new investment

Reasoning is generated from the strongest input signals:

- Demand strength
- Competition pressure
- Profit potential
- Gift suitability
- Evergreen profile
- Audience coverage depth

## Database Additions

New tables:

- `niche_scores`
- `audiences`
- `seasonality`
- `gift_scores`
- `competition_scores`
- `evergreen_scores`
- `recommendations`

## Reports Produced

- Top 100 Niches
- Top Evergreen Niches
- Top Seasonal Niches
- Top Gift Niches
- Highest Profit Potential
- Lowest Competition
- Watchlist Niches
- Avoid Niches

All reports are exportable as JSON and CSV.

## Future Improvements

1. Add provider-level audience enrichment from real channel data (Reddit, Pinterest, TikTok).
2. Improve evergreen prediction with historical multi-session trend slopes.
3. Add confidence calibration using source reliability weighting.
4. Add portfolio-level recommendations (launch queue, hold queue, kill queue).