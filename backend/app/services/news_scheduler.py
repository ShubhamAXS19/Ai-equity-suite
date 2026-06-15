"""
Background scheduler for the News Monitor's daily fetch + summarize pipeline.

Runs once a day (default: 08:00 server time) to keep the digest fresh
without requiring manual "Fetch News" clicks. The same logic used by the
manual fetch/summarize endpoints is reused here via run_daily_pipeline,
so there's a single source of truth for the pipeline behavior.
"""
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from app.db.database import db_cursor
from app.services import news_fetcher
from app.services.news_summarizer import build_summarization_prompt, parse_summarization_response
from app.services.llm_provider import get_llm_completion

scheduler = BackgroundScheduler()


def run_daily_pipeline():
    """
    Fetches RSS feeds for the current watchlist, summarizes any new
    articles with the server's configured LLM fallback (Groq, since no
    user Claude key is available in a background job), and stores results
    under today's digest_date.
    """
    print(f"[scheduler] running daily news pipeline at {datetime.utcnow().isoformat()}")

    with db_cursor() as cur:
        cur.execute("SELECT ticker, name FROM watchlist")
        watchlist = {r["ticker"]: r["name"] for r in cur.fetchall()}

    if not watchlist:
        print("[scheduler] watchlist is empty, skipping")
        return

    try:
        matches_by_ticker = news_fetcher.fetch_news_for_watchlist(list(watchlist.keys()))
    except Exception as e:
        print(f"[scheduler] fetch_news_for_watchlist failed: {e}")
        matches_by_ticker = {}

    all_articles = [a for articles in matches_by_ticker.values() for a in articles]
    today = date.today().isoformat()
    processed_count = 0

    for article in all_articles:
        with db_cursor() as cur:
            cur.execute("SELECT 1 FROM processed_articles WHERE id = ?", (article["id"],))
            if cur.fetchone():
                continue

        company_name = watchlist.get(article["ticker"], article["ticker"])
        prompt = build_summarization_prompt(article, company_name)

        try:
            # No user Claude key available in a background job - this will
            # use Groq if configured, or fail gracefully per-article.
            result = get_llm_completion(prompt, None, max_tokens=400)
        except Exception as e:
            print(f"[scheduler] summarization failed for article {article['id']}: {e}")
            continue

        parsed = parse_summarization_response(result.text)

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

    print(f"[scheduler] daily pipeline complete: {processed_count} new articles processed")


def start_scheduler():
    if scheduler.running:
        return
    # Runs once daily at 08:00 server time
    scheduler.add_job(run_daily_pipeline, "cron", hour=8, minute=0, id="daily_news_pipeline")
    scheduler.start()
    print("[scheduler] started - daily news pipeline scheduled for 08:00")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
