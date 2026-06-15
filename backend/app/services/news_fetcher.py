"""
News fetching service.

Fetches RSS feeds (Moneycontrol, Economic Times Markets, LiveMint Markets)
and filters articles by company name/search terms. Designed to degrade
gracefully: if a feed fails to fetch (network issue, feed URL changed,
etc.), it's skipped with a logged warning rather than crashing the whole
fetch.
"""
import hashlib
import feedparser
from datetime import datetime
from app.config import RSS_FEEDS, COMPANY_SEARCH_TERMS


def _article_id(link: str) -> str:
    """Stable hash of an article's link, used as its primary key."""
    return hashlib.sha256(link.encode("utf-8")).hexdigest()[:16]


def _parse_published(entry) -> str:
    """Best-effort extraction of a published date as an ISO string."""
    for field in ("published_parsed", "updated_parsed"):
        val = getattr(entry, field, None)
        if val:
            try:
                return datetime(*val[:6]).isoformat()
            except Exception:
                pass
    # Fall back to whatever string fields are present
    return getattr(entry, "published", "") or getattr(entry, "updated", "") or ""


def fetch_all_feeds() -> list[dict]:
    """
    Fetches all configured RSS feeds and returns a flat list of raw
    articles: {title, link, source, published}. Feeds that fail to fetch
    are skipped (logged), not raised.
    """
    articles = []
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            if parsed.bozo and not parsed.entries:
                print(f"[news] feed parse issue for {feed['name']} ({feed['url']}): {parsed.bozo_exception}")
                continue

            for entry in parsed.entries:
                title = getattr(entry, "title", "").strip()
                link = getattr(entry, "link", "").strip()
                if not title or not link:
                    continue
                articles.append({
                    "title": title,
                    "link": link,
                    "source": feed["name"],
                    "published": _parse_published(entry),
                })
        except Exception as e:
            print(f"[news] failed to fetch feed {feed['name']} ({feed['url']}): {e}")
            continue

    return articles


def match_articles_for_company(articles: list[dict], ticker: str) -> list[dict]:
    """
    Filters a list of raw articles down to those whose title mentions the
    given company, based on COMPANY_SEARCH_TERMS. Matching is case-insensitive
    substring matching on the title.
    """
    terms = COMPANY_SEARCH_TERMS.get(ticker, [])
    if not terms:
        return []

    matched = []
    for article in articles:
        title_lower = article["title"].lower()
        if any(term.lower() in title_lower for term in terms):
            matched.append({**article, "ticker": ticker, "id": _article_id(article["link"])})

    return matched


def fetch_news_for_watchlist(watchlist_tickers: list[str]) -> dict[str, list[dict]]:
    """
    Fetches all feeds once, then matches articles per ticker in the
    watchlist. Returns {ticker: [articles]}.
    """
    all_articles = fetch_all_feeds()

    result = {}
    for ticker in watchlist_tickers:
        result[ticker] = match_articles_for_company(all_articles, ticker)

    return result
