import json
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from app.config import VALID_TICKERS, COMPANIES
from app.db.database import db_cursor
from app.services import news_fetcher
from app.services.news_summarizer import build_summarization_prompt, parse_summarization_response
from app.services.llm_provider import get_llm_completion

router = APIRouter(prefix="/api/news", tags=["news"])

NAME_BY_TICKER = {c["ticker"]: c["name"] for c in COMPANIES}


class WatchlistAddRequest(BaseModel):
    ticker: str


@router.get("/watchlist")
def get_watchlist():
    with db_cursor() as cur:
        cur.execute("SELECT ticker, name, added_at FROM watchlist ORDER BY added_at ASC")
        rows = cur.fetchall()
    return {"watchlist": [dict(r) for r in rows]}


@router.post("/watchlist")
def add_to_watchlist(req: WatchlistAddRequest):
    ticker = req.ticker.strip()
    if ticker not in VALID_TICKERS:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker}")

    with db_cursor() as cur:
        cur.execute("SELECT 1 FROM watchlist WHERE ticker = ?", (ticker,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail=f"{ticker} is already in the watchlist")

        cur.execute(
            "INSERT INTO watchlist (ticker, name, added_at) VALUES (?, ?, ?)",
            (ticker, NAME_BY_TICKER.get(ticker, ticker), datetime.utcnow().isoformat()),
        )

    return {"status": "added", "ticker": ticker}


@router.delete("/watchlist/{ticker}")
def remove_from_watchlist(ticker: str):
    with db_cursor() as cur:
        cur.execute("SELECT 1 FROM watchlist WHERE ticker = ?", (ticker,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"{ticker} is not in the watchlist")

        cur.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker,))

    return {"status": "removed", "ticker": ticker}


@router.get("/fetch")
def fetch_news():
    """
    Fetches RSS feeds for each company in the watchlist and returns raw
    matched articles (title, link, source, published date) - no AI
    processing yet (that's the /digest pipeline).

    If the live fetch returns nothing (e.g. feeds unreachable), falls back
    to the last cached raw articles so the demo isn't empty.
    """
    with db_cursor() as cur:
        cur.execute("SELECT ticker FROM watchlist")
        watchlist_tickers = [r["ticker"] for r in cur.fetchall()]

    if not watchlist_tickers:
        return {"articles": [], "cached": False}

    try:
        matches_by_ticker = news_fetcher.fetch_news_for_watchlist(watchlist_tickers)
    except Exception as e:
        print(f"[news] fetch_news_for_watchlist failed: {e}")
        matches_by_ticker = {}

    all_articles = [a for articles in matches_by_ticker.values() for a in articles]

    if all_articles:
        # Cache this fetch's results for fallback use later
        with db_cursor() as cur:
            cur.execute("DELETE FROM raw_articles_cache")
            for a in all_articles:
                cur.execute(
                    "INSERT OR REPLACE INTO raw_articles_cache (id, ticker, title, link, source, published, fetched_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (a["id"], a["ticker"], a["title"], a["link"], a["source"], a["published"], datetime.utcnow().isoformat()),
                )

        return {"articles": all_articles, "cached": False}

    # Live fetch returned nothing - fall back to cached raw articles
    with db_cursor() as cur:
        cur.execute(
            "SELECT id, ticker, title, link, source, published FROM raw_articles_cache "
            "WHERE ticker IN ({}) ORDER BY published DESC".format(
                ",".join("?" for _ in watchlist_tickers)
            ),
            watchlist_tickers,
        )
        cached_rows = [dict(r) for r in cur.fetchall()]

    return {
        "articles": cached_rows,
        "cached": True,
        "warning": "Live RSS fetch returned no results; showing cached articles from a previous fetch." if cached_rows else None,
    }


@router.post("/summarize")
def summarize_news(
    x_claude_key: str | None = Header(default=None, alias="X-Claude-Key"),
):
    """
    Runs the fetch -> summarize -> materiality/category tagging pipeline
    for the current watchlist. Articles already processed (by id) are
    skipped to avoid re-calling the LLM for the same article.

    Returns a summary of how many articles were newly processed, plus the
    digest_date they were filed under.
    """
    with db_cursor() as cur:
        cur.execute("SELECT ticker, name FROM watchlist")
        watchlist = {r["ticker"]: r["name"] for r in cur.fetchall()}

    if not watchlist:
        return {"processed": 0, "skipped": 0, "digest_date": date.today().isoformat()}

    try:
        matches_by_ticker = news_fetcher.fetch_news_for_watchlist(list(watchlist.keys()))
    except Exception as e:
        print(f"[news] fetch_news_for_watchlist failed during summarize: {e}")
        matches_by_ticker = {}

    all_articles = [a for articles in matches_by_ticker.values() for a in articles]

    # If live fetch returned nothing, fall back to cached raw articles so
    # the summarization pipeline still has something to process in a demo.
    if not all_articles:
        with db_cursor() as cur:
            cur.execute(
                "SELECT id, ticker, title, link, source, published FROM raw_articles_cache "
                "WHERE ticker IN ({})".format(",".join("?" for _ in watchlist)),
                list(watchlist.keys()),
            )
            all_articles = [dict(r) for r in cur.fetchall()]

    today = date.today().isoformat()
    processed_count = 0
    skipped_count = 0
    llm_source_used = None

    for article in all_articles:
        with db_cursor() as cur:
            cur.execute("SELECT 1 FROM processed_articles WHERE id = ?", (article["id"],))
            if cur.fetchone():
                skipped_count += 1
                continue

        company_name = watchlist.get(article["ticker"], article["ticker"])
        prompt = build_summarization_prompt(article, company_name)

        try:
            result = get_llm_completion(prompt, x_claude_key, max_tokens=400)
        except Exception as e:
            print(f"[news] summarization failed for article {article['id']}: {e}")
            continue

        parsed = parse_summarization_response(result.text)
        llm_source_used = result.source

        with db_cursor() as cur:
            cur.execute(
                "INSERT OR REPLACE INTO processed_articles "
                "(id, ticker, title, link, source, published, summary, materiality, category, llm_source, processed_at, digest_date) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    article["id"], article["ticker"], article["title"], article["link"],
                    article["source"], article["published"], parsed["summary"], parsed["materiality"],
                    parsed["category"], result.source, datetime.utcnow().isoformat(), today,
                ),
            )
        processed_count += 1

    return {
        "processed": processed_count,
        "skipped": skipped_count,
        "digest_date": today,
        "data_sources": {"llm": llm_source_used} if llm_source_used else None,
    }


@router.get("/digest")
def get_digest(
    company: str | None = None,
    materiality: str | None = None,
    category: str | None = None,
    digest_date: str | None = None,
):
    """
    Returns processed articles, sorted by materiality (High > Medium > Low)
    then by published date (newest first), with optional filters.
    """
    materiality_order = {"High": 0, "Medium": 1, "Low": 2}

    query = "SELECT * FROM processed_articles WHERE 1=1"
    params = []

    if company:
        if company not in VALID_TICKERS:
            raise HTTPException(status_code=404, detail=f"Unknown ticker: {company}")
        query += " AND ticker = ?"
        params.append(company)

    if materiality:
        if materiality not in ("High", "Medium", "Low"):
            raise HTTPException(status_code=400, detail="materiality must be High, Medium, or Low")
        query += " AND materiality = ?"
        params.append(materiality)

    if category:
        query += " AND category = ?"
        params.append(category)

    if digest_date:
        query += " AND digest_date = ?"
        params.append(digest_date)
    else:
        # Default to the most recent digest_date available
        with db_cursor() as cur:
            cur.execute("SELECT MAX(digest_date) as max_date FROM processed_articles")
            row = cur.fetchone()
            latest = row["max_date"] if row else None
        if latest:
            query += " AND digest_date = ?"
            params.append(latest)

    with db_cursor() as cur:
        cur.execute(query, params)
        rows = [dict(r) for r in cur.fetchall()]

    rows.sort(key=lambda r: (materiality_order.get(r["materiality"], 3), r["published"]), reverse=False)
    # Within same materiality, newest first
    rows.sort(key=lambda r: materiality_order.get(r["materiality"], 3))

    return {"articles": rows, "count": len(rows)}


@router.get("/digest-dates")
def get_digest_dates():
    """Returns all distinct digest dates available, newest first - used for the history date picker (Phase 3.3)."""
    with db_cursor() as cur:
        cur.execute("SELECT DISTINCT digest_date FROM processed_articles ORDER BY digest_date DESC")
        rows = [r["digest_date"] for r in cur.fetchall()]
    return {"dates": rows}

