# Research Engine Report

## Modules Created

Inside `research/`:

- `base_provider.py`
- `research_manager.py`
- `keyword_collector.py`
- `trend_analyzer.py`
- `niche_finder.py`
- `competitor_analyzer.py`
- `pricing_analyzer.py`
- `review_analyzer.py`
- `opportunity_engine.py`
- `market_report.py`

## Database Changes

The database initializer now supports research intelligence tables and schema evolution:

- `keywords` (extended)
- `keyword_metrics`
- `niches` (extended)
- `competitors`
- `market_reports`
- `price_history`
- `trend_history`
- `reviews`
- `research_sessions`

Additional repository-style methods were added to `EtsyDatabase` for save/fetch operations used by the research engine.

## Research Workflow

1. Create research session entry.
2. Collect keywords per provider.
3. Persist keywords and keyword metrics.
4. Discover niche candidates and assign categories.
5. Collect competitor and trend signals.
6. Analyze pricing and review signals.
7. Compute opportunity and confidence scores with reasoning.
8. Persist niche intelligence and history tables.
9. Build report sets:
   - Top 20 Niches
   - Fastest Growing Niches
   - Best Gift Niches
   - Highest Profit Niches
   - Lowest Competition Niches
   - Most Balanced Opportunities
10. Store report payload and export CSV/JSON.
11. Close research session with summary.

## Dashboard Integration

The existing `Arastirma` page now includes:

- latest research session view,
- professional research run button,
- top niches and opportunity scores,
- trend overview,
- keyword overview.

## Future Provider Integration Points

All future providers can be integrated through `BaseResearchProvider`:

- `collect_keywords(seed, limit)`
- `collect_competitors(seed, limit)`
- `collect_trends(seed, keywords)`

Current implementation includes `EtsySearchProvider` as default. Additional providers can be added without modifying core research orchestration.

## Stability Status

- Imports verified.
- Database schema creation verified.
- Dashboard startup verified.
- Test suite green.
