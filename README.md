# AI Equity Research Suite

A portfolio project for a Finance & AI Analyst role at an Indian financial
services firm. It combines three AI-powered tools for NSE-listed Indian
large-cap companies into a single web app:

1. **Research Brief** — live company snapshots (price, P/E, P/B, 52-week
   range, revenue/profit growth) plus AI-generated one-page research briefs
   (business overview, financial interpretation, recent developments, key
   risks).
2. **Financial Analyzer** — multi-year financial ratio computation (margins,
   current ratio, debt-to-equity, ROE, interest coverage) with charts, plus
   AI commentary that flags trends and anomalies.
3. **News Monitor** — a watchlist-based news digest pulling from financial
   RSS feeds, with AI summarization and materiality (High/Medium/Low) and
   category tagging.

The app also includes an interactive, game-style spotlight tutorial, and
supports bring-your-own API keys (Claude + InsightSentry) with automatic
fallback to free alternatives (Groq + yfinance) if no keys are provided.

---

## Tech Stack

- **Backend**: Python, FastAPI, SQLite
- **Frontend**: React (Vite), Tailwind CSS, Recharts
- **Market data**: yfinance (default) / InsightSentry (optional, user-provided key)
- **AI**: Anthropic Claude API (default with user key) / Groq Llama 3.3 70B (fallback)
- **News**: feedparser (RSS) + APScheduler (daily digest pipeline)

---

## Project Structure

```
ai-equity-suite/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, startup/shutdown
│   │   ├── config.py            # Company list, RSS feeds, model names
│   │   ├── db/database.py       # SQLite schema + seed data
│   │   ├── routers/
│   │   │   ├── companies.py     # GET /api/companies
│   │   │   ├── settings.py      # API key validation, provider status
│   │   │   ├── research.py      # Snapshot + AI brief endpoints
│   │   │   ├── analyzer.py       # Ratio + AI commentary endpoints
│   │   │   └── news.py          # Watchlist, fetch, summarize, digest
│   │   ├── services/
│   │   │   ├── llm_provider.py    # Claude -> Groq fallback
│   │   │   ├── market_data.py     # yfinance -> InsightSentry abstraction
│   │   │   ├── prompts.py          # Versioned research brief prompts (v1-v3)
│   │   │   ├── brief_generator.py  # Brief generation + JSON parsing
│   │   │   ├── ratio_calculator.py # pandas-based ratio computation
│   │   │   ├── commentary_prompts.py
│   │   │   ├── news_fetcher.py     # RSS fetching + company matching
│   │   │   ├── news_summarizer.py  # Summarization prompt + parsing
│   │   │   └── news_scheduler.py   # APScheduler daily pipeline
│   │   └── tests/                # Unit + integration tests (mocked LLM)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/client.js          # Centralized API client, attaches user keys as headers
    │   ├── context/SettingsContext.jsx  # API key storage (localStorage), provider status
    │   ├── components/            # Shared UI: cards, tables, charts, tutorial overlay, etc.
    │   ├── pages/                 # ResearchPage, AnalyzerPage, NewsPage
    │   └── tutorial/steps.js      # Spotlight tutorial step definitions
    ├── package.json
    └── tailwind.config.js
```

---

## Setup & Running Locally

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or use a virtualenv
cp .env.example .env
```

Edit `.env` to optionally add:

```env
GROQ_API_KEY=your_groq_key        # fallback LLM if no Claude key is entered in the UI
INSIGHTSENTRY_API_KEY=             # optional server-side fallback for market data
ANTHROPIC_API_KEY=                 # optional, for local dev convenience only
```

> The app works without any keys: market data falls back to yfinance and AI
> features fall back to Groq (if `GROQ_API_KEY` is set) or show a clear error
> prompting you to add a key in Settings.

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

The first run creates `data.db` (SQLite) and seeds it with sample data
(snapshots, financial statements, and news articles) so the UI never shows a
blank screen, even if live data sources are unreachable.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**.

### 3. Using your own API keys (optional)

Click **Settings** in the app:

- **Claude API key** ([console.anthropic.com](https://console.anthropic.com/)) —
  enables higher-quality AI briefs, commentary, and news summaries. Without
  it, the app uses Groq's free Llama 3.3 70B model.
- **InsightSentry API key** — enables real-time/fundamental market data.
  Without it, the app uses yfinance.

Keys are stored only in your browser's `localStorage` and sent per-request
via headers — never persisted on the server.

---

## Running Tests

```bash
cd backend
python3 -m app.tests.test_brief_parsing
python3 -m app.tests.test_brief_endpoint
python3 -m app.tests.test_ratio_calculator
python3 -m app.tests.test_analyzer_endpoint
python3 -m app.tests.test_news_services
python3 -m app.tests.test_news_endpoint
```

All integration tests mock the LLM provider, so they run without any API
keys.

---

## Features by Module

### Research Brief
- Searchable company selector (15 NSE large-caps)
- Live snapshot: price, market cap, P/E, P/B, 52-week range, revenue/net
  profit with YoY growth
- AI-generated research brief: business overview, financial snapshot,
  recent developments (placeholder for a live news feed), key risks
- Three versions of the brief-generation prompt (rough draft → refined →
  handles missing data) used to demonstrate prompt iteration
- Daily caching so repeat demos don't re-call the API

### Financial Analyzer
- Up to 4 years of income statement / balance sheet data via yfinance
- Computed ratios: gross/operating/net margin, current ratio,
  debt-to-equity, ROE, interest coverage
- Recharts visualization: revenue & net profit (bars) with net margin
  trend (line)
- AI commentary on trends and anomalies, visually separated from the
  computed data section

### News Monitor
- Watchlist management (5 default companies, customizable from the 15-company list)
- RSS fetching from Moneycontrol, Economic Times Markets, and LiveMint Markets
- AI summarization with materiality (High/Medium/Low) and category
  (Earnings, M&A, Regulatory, Leadership Change, Other) tagging
- Filterable digest view with a date picker for historical digests
- Daily automated pipeline via APScheduler

### Cross-cutting
- Interactive spotlight tutorial covering every section, replayable via the
  "Help" button (which also pulses on tab change)
- Bring-your-own-key support for Claude and InsightSentry, with automatic
  fallback to Groq and yfinance and a visible data-source badge

---

## Known Limitations / Notes

- **InsightSentry integration is a stub.** The provider-abstraction layer
  (`market_data.py`) is in place and ready to wire up, but currently falls
  back to yfinance regardless of the key provided.
- **RSS feed URLs** may occasionally change or rate-limit; the app degrades
  gracefully (cached fallback, empty state) rather than crashing if a feed
  is unreachable.
- **News article matching** is title-based substring matching against a
  per-company list of search terms — reasonable for a demo, but a
  production system would use a more robust entity-matching approach.
- Seed/sample data is included for a subset of companies (primarily
  RELIANCE.NS) so the demo works even without live data access; other
  companies require a working internet connection to yfinance/RSS sources.

---

## Approach

> _(Placeholder — fill in with your own write-up before sharing this
> project. Suggested points to cover below.)_

- **Why this project**: _[e.g. how it demonstrates the intersection of
  financial analysis and applied AI/LLM engineering relevant to the role]_
- **Architecture decisions**: _[e.g. why a provider-abstraction layer for
  LLM/market data, why SQLite caching, why a single combined app vs. three
  separate ones]_
- **Prompt engineering**: _[discuss the three prompt versions in
  `prompts.py` — what changed between v1 → v2 → v3 and why, and how that's
  surfaced in the UI]_
- **Trade-offs**: _[e.g. yfinance reliability vs. paid data providers,
  RSS-based news vs. a dedicated news API, title-matching vs. NLP-based
  entity recognition]_
- **What I'd do with more time**: _[e.g. wire up InsightSentry, add more
  seed/historical data, improve news entity matching, add authentication
  for multi-user use]_

---

## Disclaimer

This is a portfolio/demo project. AI-generated content (research briefs,
commentary, news summaries) should be reviewed by a qualified analyst before
being used for any investment decision.
