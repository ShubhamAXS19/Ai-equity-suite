import json
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Header
from app.config import VALID_TICKERS
from app.db.database import db_cursor
from app.services import market_data
from app.services.ratio_calculator import compute_ratios
from app.services.commentary_prompts import build_commentary_prompt
from app.services.llm_provider import get_llm_completion

router = APIRouter(prefix="/api/analyzer", tags=["analyzer"])


def _get_financials_with_fallback(ticker: str, x_insightsentry_key: str | None):
    """
    Try live fetch of raw financial statements, cache the raw data on
    success, fall back to cached raw data on failure. Returns
    (raw_financials_dict, source, cached_bool, warning_or_none).
    """
    try:
        result = market_data.get_financial_statements(ticker, x_insightsentry_key)
        data = result.data
        source = result.source

        with db_cursor() as cur:
            cur.execute(
                "INSERT OR REPLACE INTO ratio_cache (ticker, data, source, fetched_at) VALUES (?, ?, ?, ?)",
                (ticker, json.dumps(data), source, datetime.utcnow().isoformat()),
            )

        return data, source, False, None

    except Exception as e:
        print(f"[analyzer] live financials fetch failed for {ticker}: {e}")
        with db_cursor() as cur:
            cur.execute("SELECT data, source, fetched_at FROM ratio_cache WHERE ticker = ?", (ticker,))
            row = cur.fetchone()

        if row:
            return (
                json.loads(row["data"]),
                row["source"],
                True,
                "Live data fetch failed; showing cached financial statements.",
            )

        raise HTTPException(
            status_code=503,
            detail=f"Live fetch failed and no cached financial data available for {ticker}: {e}",
        )


@router.get("/company/{ticker}/ratios")
def get_ratios(
    ticker: str,
    x_insightsentry_key: str | None = Header(default=None, alias="X-InsightSentry-Key"),
):
    if ticker not in VALID_TICKERS:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker}")

    raw_financials, source, cached, warning = _get_financials_with_fallback(ticker, x_insightsentry_key)

    if not raw_financials.get("income_statement"):
        raise HTTPException(
            status_code=503,
            detail=f"No income statement data available for {ticker} (live fetch failed, no cache).",
        )

    ratios = compute_ratios(raw_financials)

    response = {
        "ratio_table": ratios["ratio_table"],
        "series": ratios["series"],
        "company": {"ticker": raw_financials.get("ticker"), "name": raw_financials.get("name")},
        "data_sources": {"market_data": source},
        "cached": cached,
    }
    if warning:
        response["warning"] = warning

    return response


@router.post("/company/{ticker}/commentary")
def get_commentary(
    ticker: str,
    force_refresh: bool = False,
    x_claude_key: str | None = Header(default=None, alias="X-Claude-Key"),
    x_insightsentry_key: str | None = Header(default=None, alias="X-InsightSentry-Key"),
):
    if ticker not in VALID_TICKERS:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker}")

    today = date.today().isoformat()

    if not force_refresh:
        with db_cursor() as cur:
            cur.execute(
                "SELECT commentary, llm_source FROM commentary_cache WHERE ticker = ? AND date = ?",
                (ticker, today),
            )
            row = cur.fetchone()

        if row:
            return {
                "commentary": json.loads(row["commentary"])["text"],
                "data_sources": {"llm": row["llm_source"]},
                "cached": True,
            }

    raw_financials, market_source, _, _ = _get_financials_with_fallback(ticker, x_insightsentry_key)

    if not raw_financials.get("income_statement"):
        raise HTTPException(
            status_code=503,
            detail=f"No financial data available for {ticker}; cannot generate commentary.",
        )

    ratios = compute_ratios(raw_financials)

    if len(ratios["ratio_table"]) < 2:
        raise HTTPException(
            status_code=422,
            detail=f"Not enough years of data for {ticker} to identify trends (need at least 2).",
        )

    prompt = build_commentary_prompt(ratios)

    try:
        result = get_llm_completion(prompt, x_claude_key, max_tokens=500)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Commentary generation failed: {e}")

    with db_cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO commentary_cache (ticker, date, commentary, llm_source, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (ticker, today, json.dumps({"text": result.text}), result.source, datetime.utcnow().isoformat()),
        )

    return {
        "commentary": result.text,
        "data_sources": {"llm": result.source, "market_data": market_source},
        "cached": False,
    }
