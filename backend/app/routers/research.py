import json
from datetime import datetime, date, timedelta
from fastapi import APIRouter, HTTPException, Header
from app.config import VALID_TICKERS
from app.db.database import db_cursor
from app.services import market_data
from app.services.brief_generator import generate_brief
from app.services.prompts import PROMPT_VERSIONS, DEFAULT_PROMPT_VERSION

router = APIRouter(prefix="/api/research", tags=["research"])

SNAPSHOT_CACHE_TTL = timedelta(hours=12)


def _get_snapshot_with_fallback(ticker: str, x_insightsentry_key: str | None):
    with db_cursor() as cur:
        cur.execute("SELECT data, source, fetched_at FROM snapshot_cache WHERE ticker = ?", (ticker,))
        cached_row = cur.fetchone()

    # Serve fresh-enough cache without touching Yahoo at all
    if cached_row:
        fetched_at = datetime.fromisoformat(cached_row["fetched_at"])
        if datetime.utcnow() - fetched_at < SNAPSHOT_CACHE_TTL:
            return {
                "snapshot": json.loads(cached_row["data"]),
                "data_sources": {"market_data": cached_row["source"]},
                "cached": True,
                "cached_at": cached_row["fetched_at"],
            }

    try:
        result = market_data.get_snapshot(ticker, x_insightsentry_key)
        data = result.data
        source = result.source

        with db_cursor() as cur:
            cur.execute(
                "INSERT OR REPLACE INTO snapshot_cache (ticker, data, source, fetched_at) VALUES (?, ?, ?, ?)",
                (ticker, json.dumps(data), source, datetime.utcnow().isoformat()),
            )

        return {
            "snapshot": data,
            "data_sources": {"market_data": source},
            "cached": False,
        }

    except Exception as e:
        print(f"[snapshot] live fetch failed for {ticker}: {e}")

        # Fall back to stale cache if we have it, even past the TTL
        if cached_row:
            return {
                "snapshot": json.loads(cached_row["data"]),
                "data_sources": {"market_data": cached_row["source"]},
                "cached": True,
                "cached_at": cached_row["fetched_at"],
                "warning": "Live data fetch failed; showing cached data.",
            }

        raise HTTPException(
            status_code=503,
            detail=f"Live fetch failed and no cached data available for {ticker}: {e}",
        )

@router.get("/company/{ticker}/snapshot")
def get_snapshot(
    ticker: str,
    x_insightsentry_key: str | None = Header(default=None, alias="X-InsightSentry-Key"),
):
    if ticker not in VALID_TICKERS:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker}")

    return _get_snapshot_with_fallback(ticker, x_insightsentry_key)


@router.post("/company/{ticker}/brief")
def get_brief(
    ticker: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    force_refresh: bool = False,
    x_claude_key: str | None = Header(default=None, alias="X-Claude-Key"),
    x_insightsentry_key: str | None = Header(default=None, alias="X-InsightSentry-Key"),
):
    if ticker not in VALID_TICKERS:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker}")

    if prompt_version not in PROMPT_VERSIONS:
        raise HTTPException(status_code=400, detail=f"Unknown prompt_version: {prompt_version}")

    today = date.today().isoformat()

    # Check cache first (ticker + date + prompt_version), unless forced refresh
    if not force_refresh:
        with db_cursor() as cur:
            cur.execute(
                "SELECT brief, llm_source FROM brief_cache WHERE ticker = ? AND date = ? AND prompt_version = ?",
                (ticker, today, prompt_version),
            )
            row = cur.fetchone()

        if row:
            return {
                "brief": json.loads(row["brief"]),
                "data_sources": {"llm": row["llm_source"]},
                "prompt_version": prompt_version,
                "cached": True,
            }

    # Need fresh snapshot data to build the prompt
    snapshot_result = _get_snapshot_with_fallback(ticker, x_insightsentry_key)
    snapshot = snapshot_result["snapshot"]

    try:
        brief, llm_source, used_version = generate_brief(snapshot, x_claude_key, prompt_version)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Brief generation failed: {e}")

    with db_cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO brief_cache (ticker, date, prompt_version, brief, llm_source, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (ticker, today, used_version, json.dumps(brief), llm_source, datetime.utcnow().isoformat()),
        )

    return {
        "brief": brief,
        "data_sources": {"llm": llm_source, "market_data": snapshot_result["data_sources"]["market_data"]},
        "prompt_version": used_version,
        "cached": False,
    }


@router.get("/prompt-versions")
def list_prompt_versions():
    return {
        "versions": [
            {"id": k, "label": v["label"], "description": v["description"]}
            for k, v in PROMPT_VERSIONS.items()
        ],
        "default": DEFAULT_PROMPT_VERSION,
    }
