# Final Report

## Completed Features

- Etsy market research engine with scraper fallback data.
- Niche analysis and opportunity scoring.
- POD product selector for common merchandise.
- AI-style design prompt generator.
- Etsy SEO generator with titles, descriptions, tags, keywords, and pricing.
- SQLite database with the requested tables.
- Streamlit dashboard with core workflow pages.
- JSON and CSV export support.
- Daily discovery automation via `daily_product_discovery()`.
- Pytest coverage for database, scoring, SEO, and product selection.

## How To Run

```bash
pip install -r requirements.txt
streamlit run main.py
pytest
```

## Future Improvements

- Add live Etsy data ingestion from approved sources.
- Improve trend detection with historical snapshots.
- Add richer product visual generation support.
- Add scheduled background execution for daily discovery.
