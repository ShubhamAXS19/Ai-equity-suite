"""
SQLite database setup and connection helpers.
Tables are created on startup if they don't exist; one sample row is seeded
into snapshot_cache so the demo never shows a fully blank screen.
"""
import sqlite3
import json
from contextlib import contextmanager
from app.config import DB_PATH


SCHEMA = """
-- Phase 0/1: snapshot cache for Research Brief module
CREATE TABLE IF NOT EXISTS snapshot_cache (
    ticker TEXT PRIMARY KEY,
    data TEXT NOT NULL,          -- JSON blob of snapshot fields
    source TEXT NOT NULL,        -- 'yfinance' | 'insightsentry'
    fetched_at TEXT NOT NULL
);

-- Phase 1: AI research briefs
CREATE TABLE IF NOT EXISTS brief_cache (
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,          -- YYYY-MM-DD
    prompt_version TEXT NOT NULL DEFAULT 'v2',
    brief TEXT NOT NULL,         -- JSON blob of structured brief
    llm_source TEXT NOT NULL,    -- 'claude' | 'groq'
    created_at TEXT NOT NULL,
    PRIMARY KEY (ticker, date, prompt_version)
);

-- Phase 2: financial ratio cache
CREATE TABLE IF NOT EXISTS ratio_cache (
    ticker TEXT PRIMARY KEY,
    data TEXT NOT NULL,          -- JSON blob: ratio table + raw series
    source TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);

-- Phase 2: AI commentary cache
CREATE TABLE IF NOT EXISTS commentary_cache (
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    commentary TEXT NOT NULL,    -- JSON blob
    llm_source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (ticker, date)
);

-- Phase 3: news watchlist
CREATE TABLE IF NOT EXISTS watchlist (
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    added_at TEXT NOT NULL
);

-- Phase 3: cache of raw (unprocessed) matched articles from the last fetch,
-- so the "Fetch News" UI has something to show even if live RSS fails
CREATE TABLE IF NOT EXISTS raw_articles_cache (
    id TEXT PRIMARY KEY,          -- hash of link
    ticker TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    source TEXT NOT NULL,
    published TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);

-- Phase 3: processed news articles
CREATE TABLE IF NOT EXISTS processed_articles (
    id TEXT PRIMARY KEY,         -- hash of link
    ticker TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    source TEXT NOT NULL,
    published TEXT NOT NULL,
    summary TEXT,
    materiality TEXT,            -- High | Medium | Low
    category TEXT,                -- Earnings | M&A | Regulatory | Leadership Change | Other
    llm_source TEXT,
    processed_at TEXT NOT NULL,
    digest_date TEXT NOT NULL    -- YYYY-MM-DD, for history snapshots
);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    finally:
        conn.close()


def init_db():
    with db_cursor() as cur:
        cur.executescript(SCHEMA)

    _seed_sample_data()


def _seed_sample_data():
    """Seed a few pre-fetched snapshots so demos never start blank, even
    when live yfinance/InsightSentry calls fail (e.g. blocked network)."""
    samples = {
        "RELIANCE.NS": {
            "ticker": "RELIANCE.NS",
            "name": "Reliance Industries Ltd",
            "current_price": 1462.35,
            "currency": "INR",
            "market_cap": 19850000000000,
            "pe_ratio": 24.8,
            "pb_ratio": 2.3,
            "week52_high": 1608.95,
            "week52_low": 1201.5,
            "latest_revenue": 9009000000000,
            "latest_net_profit": 791000000000,
            "revenue_yoy_growth": 7.3,
            "net_profit_yoy_growth": 11.6,
            "fiscal_year": "FY2024",
        },
        "TCS.NS": {
            "ticker": "TCS.NS",
            "name": "Tata Consultancy Services Ltd",
            "current_price": 3845.6,
            "currency": "INR",
            "market_cap": 13920000000000,
            "pe_ratio": 28.4,
            "pb_ratio": 13.1,
            "week52_high": 4259.75,
            "week52_low": 3311.0,
            "latest_revenue": 2402000000000,
            "latest_net_profit": 460000000000,
            "revenue_yoy_growth": 6.8,
            "net_profit_yoy_growth": 9.1,
            "fiscal_year": "FY2024",
        },
        "INFY.NS": {
            "ticker": "INFY.NS",
            "name": "Infosys Ltd",
            "current_price": 1612.2,
            "currency": "INR",
            "market_cap": 6690000000000,
            "pe_ratio": 25.1,
            "pb_ratio": 8.2,
            "week52_high": 1953.9,
            "week52_low": 1351.65,
            "latest_revenue": 1538000000000,
            "latest_net_profit": 264000000000,
            "revenue_yoy_growth": 4.3,
            "net_profit_yoy_growth": 7.2,
            "fiscal_year": "FY2024",
        },
    }
    with db_cursor() as cur:
        for ticker, snapshot in samples.items():
            cur.execute("SELECT COUNT(*) as c FROM snapshot_cache WHERE ticker = ?", (ticker,))
            if cur.fetchone()["c"] == 0:
                cur.execute(
                    "INSERT INTO snapshot_cache (ticker, data, source, fetched_at) VALUES (?, ?, ?, ?)",
                    (ticker, json.dumps(snapshot), "seed", "2025-01-01T00:00:00"),
                )

    _seed_ratio_data()


def _seed_ratio_data():
    """
    Seed 4 years of raw financial statement data for RELIANCE.NS, using
    yfinance-standard line item names, so the Financial Analyzer demo works
    even when live yfinance calls are blocked.
    """
    financials = {
        "ticker": "RELIANCE.NS",
        "name": "Reliance Industries Ltd",
        "income_statement": {
            "2024": {
                "Total Revenue": 9009000000000,
                "Gross Profit": 2702700000000,
                "Operating Income": 1531530000000,
                "EBIT": 1531530000000,
                "Net Income": 791000000000,
                "Interest Expense": 207300000000,
            },
            "2023": {
                "Total Revenue": 8392000000000,
                "Gross Profit": 2434680000000,
                "Operating Income": 1342720000000,
                "EBIT": 1342720000000,
                "Net Income": 708900000000,
                "Interest Expense": 213600000000,
            },
            "2022": {
                "Total Revenue": 7929000000000,
                "Gross Profit": 2298410000000,
                "Operating Income": 1228000000000,
                "EBIT": 1228000000000,
                "Net Income": 676600000000,
                "Interest Expense": 188900000000,
            },
            "2021": {
                "Total Revenue": 4669000000000,
                "Gross Profit": 1353000000000,
                "Operating Income": 754000000000,
                "EBIT": 754000000000,
                "Net Income": 498800000000,
                "Interest Expense": 169400000000,
            },
        },
        "balance_sheet": {
            "2024": {
                "Current Assets": 3120000000000,
                "Current Liabilities": 2540000000000,
                "Total Debt": 3360000000000,
                "Stockholders Equity": 8520000000000,
                "Total Assets": 17680000000000,
            },
            "2023": {
                "Current Assets": 2890000000000,
                "Current Liabilities": 2410000000000,
                "Total Debt": 3270000000000,
                "Stockholders Equity": 7790000000000,
                "Total Assets": 16480000000000,
            },
            "2022": {
                "Current Assets": 2660000000000,
                "Current Liabilities": 2210000000000,
                "Total Debt": 3170000000000,
                "Stockholders Equity": 7180000000000,
                "Total Assets": 15280000000000,
            },
            "2021": {
                "Current Assets": 2310000000000,
                "Current Liabilities": 1740000000000,
                "Total Debt": 2580000000000,
                "Stockholders Equity": 6390000000000,
                "Total Assets": 13110000000000,
            },
        },
        "cash_flow": {},
    }

    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as c FROM ratio_cache WHERE ticker = ?", ("RELIANCE.NS",))
        if cur.fetchone()["c"] == 0:
            cur.execute(
                "INSERT INTO ratio_cache (ticker, data, source, fetched_at) VALUES (?, ?, ?, ?)",
                ("RELIANCE.NS", json.dumps(financials), "seed", "2025-01-01T00:00:00"),
            )

    _seed_news_data()


def _seed_news_data():
    """
    Seed the default watchlist (5 companies) and a handful of processed
    news articles so the News Monitor digest demo has content even when
    live RSS feeds are unreachable.
    """
    from app.config import DEFAULT_WATCHLIST, COMPANIES

    name_by_ticker = {c["ticker"]: c["name"] for c in COMPANIES}

    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as c FROM watchlist")
        if cur.fetchone()["c"] == 0:
            for ticker in DEFAULT_WATCHLIST:
                cur.execute(
                    "INSERT INTO watchlist (ticker, name, added_at) VALUES (?, ?, ?)",
                    (ticker, name_by_ticker.get(ticker, ticker), "2025-01-01T00:00:00"),
                )

    seed_articles = [
        {
            "id": "seed0001",
            "ticker": "RELIANCE.NS",
            "title": "Reliance Industries Q3 net profit rises 11% YoY on strong retail and Jio growth",
            "link": "https://example.com/news/reliance-q3-results-seed",
            "source": "Moneycontrol",
            "published": "2025-01-15T09:30:00",
            "summary": "Reliance Industries reported an 11% year-on-year increase in net profit for Q3, driven by continued growth in its retail and Jio telecom segments. Management highlighted strong subscriber additions and store expansion as key contributors.",
            "materiality": "High",
            "category": "Earnings",
            "llm_source": "seed",
        },
        {
            "id": "seed0002",
            "ticker": "TCS.NS",
            "title": "TCS announces new leadership appointment for European operations",
            "link": "https://example.com/news/tcs-leadership-seed",
            "source": "Economic Times Markets",
            "published": "2025-01-14T11:00:00",
            "summary": "Tata Consultancy Services announced a new regional head for its European operations as part of a broader leadership reshuffle. The company stated the move aims to strengthen client relationships across key European markets.",
            "materiality": "Medium",
            "category": "Leadership Change",
            "llm_source": "seed",
        },
        {
            "id": "seed0003",
            "ticker": "HDFCBANK.NS",
            "title": "HDFC Bank receives RBI approval for new digital banking initiative",
            "link": "https://example.com/news/hdfc-rbi-approval-seed",
            "source": "LiveMint Markets",
            "published": "2025-01-14T08:15:00",
            "summary": "HDFC Bank received regulatory approval from the Reserve Bank of India for a new digital banking initiative aimed at expanding financial inclusion in semi-urban areas. The bank plans to roll out the service over the coming quarters.",
            "materiality": "Medium",
            "category": "Regulatory",
            "llm_source": "seed",
        },
        {
            "id": "seed0004",
            "ticker": "ICICIBANK.NS",
            "title": "ICICI Bank shares largely flat after routine analyst coverage update",
            "link": "https://example.com/news/icici-analyst-note-seed",
            "source": "Moneycontrol",
            "published": "2025-01-13T14:45:00",
            "summary": "A brokerage firm reiterated its rating on ICICI Bank following a routine review of the stock, with no major changes to estimates. The note had minimal impact on trading activity.",
            "materiality": "Low",
            "category": "Other",
            "llm_source": "seed",
        },
        {
            "id": "seed0005",
            "ticker": "INFY.NS",
            "title": "Infosys in early discussions for potential acquisition of European IT services firm",
            "link": "https://example.com/news/infosys-acquisition-seed",
            "source": "Economic Times Markets",
            "published": "2025-01-13T07:20:00",
            "summary": "Infosys is reportedly in early-stage discussions to acquire a mid-sized European IT services firm, according to people familiar with the matter. The deal, if finalized, could expand Infosys's presence in continental Europe.",
            "materiality": "High",
            "category": "M&A",
            "llm_source": "seed",
        },
    ]

    digest_date = "2025-01-15"
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as c FROM processed_articles")
        if cur.fetchone()["c"] == 0:
            for a in seed_articles:
                cur.execute(
                    "INSERT INTO processed_articles "
                    "(id, ticker, title, link, source, published, summary, materiality, category, llm_source, processed_at, digest_date) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        a["id"], a["ticker"], a["title"], a["link"], a["source"], a["published"],
                        a["summary"], a["materiality"], a["category"], a["llm_source"],
                        "2025-01-15T10:00:00", digest_date,
                    ),
                )