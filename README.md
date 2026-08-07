# Etsy-POD-AI-Factory

Simple Streamlit MVP for finding Etsy print-on-demand opportunities, generating product ideas, and exporting ready-to-list assets.

## Installation

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

## Running The Application

```bash
streamlit run main.py
```

The app uses:

- SQLite database: `database/etsy_pod_factory.sqlite3`
- Export output directory: `exports/`

## Running Tests

```bash
pytest
```

## Current Features

- Etsy market research with scraper fallback
- Modular research provider architecture
- Professional research session orchestration
- Keyword collection and keyword metrics tracking
- Niche discovery with configurable categories
- Trend classification and trend history
- Competitor, pricing, and review intelligence layers
- Opportunity score + confidence score + reasoning
- Structured market report generation
- Market report CSV and JSON exports
- Niche Intelligence Engine for business decision scoring
- Audience, buyer intent, seasonality, giftability, competition, evergreen analysis
- Niche classification (Gold/Silver/Bronze/Watchlist/Avoid)
- Niche recommendation ranking and intelligence reports
- Niche opportunity scoring
- POD product recommendations
- Design prompt generation
- Etsy SEO listing generation
- SQLite persistence
- JSON and CSV export
- Streamlit dashboard
- Daily discovery automation

## Project Structure

```
Etsy-POD-AI-Factory/
├── dashboard/
├── database/
├── design/
├── exports/
├── products/
├── research/
│   ├── base_provider.py
│   ├── research_manager.py
│   ├── keyword_collector.py
│   ├── trend_analyzer.py
│   ├── niche_finder.py
│   ├── competitor_analyzer.py
│   ├── pricing_analyzer.py
│   ├── review_analyzer.py
│   ├── opportunity_engine.py
│   └── market_report.py
├── niche_intelligence/
│   ├── engine.py
│   ├── models.py
│   ├── scoring.py
│   ├── audience.py
│   ├── seasonality.py
│   ├── competition.py
│   ├── giftability.py
│   ├── evergreen.py
│   ├── recommendations.py
│   └── report_generator.py
├── scraper/
├── scoring/
├── seo/
├── tests/
├── utils/
├── config.yaml
├── main.py
├── requirements.txt
└── README.md
```

## Notes

- No API keys are required for the current MVP.
- Live Etsy scraping can fail due to network or markup changes; the app safely falls back to synthetic market data.

## Research Workflow

1. Start a research session with one or more seed terms.
2. Collect keywords from one or many providers.
3. Discover niche candidates and categorize them.
4. Collect competitor and trend signals.
5. Compute pricing, review, and opportunity intelligence.
6. Persist all outputs to SQLite research tables.
7. Generate market reports and export JSON/CSV.

## Future Provider Integration

- New data source integration is plug-and-play through `BaseResearchProvider`.
- To add providers such as Google Trends, Pinterest, Reddit, TikTok, Amazon, eRank, EverBee, Marmalead, or CSV import:
	- implement `collect_keywords`, `collect_competitors`, and `collect_trends`,
	- register provider in `ResearchManager` configuration,
	- no core orchestration changes are required.

## Niche Intelligence Workflow

1. Pull latest scored niches from the Research Engine output.
2. Derive audience groups and buyer intent.
3. Detect seasonality and evergreen profile.
4. Score competition level and gift market strength.
5. Calculate overall niche business score and confidence.
6. Classify niche as Gold, Silver, Bronze, Watchlist, or Avoid.
7. Persist recommendation records and export reports in JSON/CSV.

## Future Improvements

- Connect to approved data sources or APIs
- Add richer seasonal trend signals
- Support batch niche research from CSV input
- Add image prompt presets for different POD providers
