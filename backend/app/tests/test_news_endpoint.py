"""
Integration tests for /api/news endpoints.
Run with: python3 -m app.tests.test_news_endpoint
"""
import json
import os
from unittest.mock import patch

TEST_DB = "/tmp/test_news.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

import app.config as config
config.DB_PATH = TEST_DB

from app.db.database import init_db, db_cursor
from app.services.llm_provider import LLMResult

init_db()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_watchlist_seeded_with_defaults():
    resp = client.get("/api/news/watchlist")
    assert resp.status_code == 200
    data = resp.json()
    tickers = [w["ticker"] for w in data["watchlist"]]
    assert len(tickers) == 5
    assert "RELIANCE.NS" in tickers
    print("test_watchlist_seeded_with_defaults passed")


def test_watchlist_add_and_remove():
    resp = client.post("/api/news/watchlist", json={"ticker": "WIPRO.NS"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "added"

    resp2 = client.get("/api/news/watchlist")
    tickers = [w["ticker"] for w in resp2.json()["watchlist"]]
    assert "WIPRO.NS" in tickers

    resp3 = client.post("/api/news/watchlist", json={"ticker": "WIPRO.NS"})
    assert resp3.status_code == 409

    resp4 = client.delete("/api/news/watchlist/WIPRO.NS")
    assert resp4.status_code == 200
    assert resp4.json()["status"] == "removed"

    resp5 = client.delete("/api/news/watchlist/WIPRO.NS")
    assert resp5.status_code == 404
    print("test_watchlist_add_and_remove passed")


def test_watchlist_add_invalid_ticker():
    resp = client.post("/api/news/watchlist", json={"ticker": "FAKE.NS"})
    assert resp.status_code == 404
    print("test_watchlist_add_invalid_ticker passed")


def test_fetch_news_falls_back_gracefully():
    resp = client.get("/api/news/fetch")
    assert resp.status_code == 200
    data = resp.json()
    assert "articles" in data
    print("test_fetch_news_falls_back_gracefully passed")


MOCK_SUMMARY_JSON = json.dumps({
    "summary": "This article discusses a significant business development for the company that could affect its near-term outlook.",
    "materiality": "High",
    "category": "Earnings",
})


def test_summarize_with_mocked_articles():
    with db_cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO raw_articles_cache (id, ticker, title, link, source, published, fetched_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("testid001", "RELIANCE.NS", "Reliance Industries announces major capex plan",
             "https://example.com/test1", "Moneycontrol", "2025-01-20T10:00:00", "2025-01-20T10:00:00"),
        )

    with patch("app.routers.news.get_llm_completion") as mock_llm:
        mock_llm.return_value = LLMResult(text=MOCK_SUMMARY_JSON, source="claude")

        resp = client.post("/api/news/summarize")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["processed"] >= 1
        print("test_summarize_with_mocked_articles: summarize passed")

        mock_llm.reset_mock()
        resp2 = client.post("/api/news/summarize")
        data2 = resp2.json()
        assert data2["processed"] == 0
        print("test_summarize_with_mocked_articles: skip already-processed passed")

    resp3 = client.get("/api/news/digest", params={"company": "RELIANCE.NS"})
    assert resp3.status_code == 200
    articles = resp3.json()["articles"]
    found = [a for a in articles if a["id"] == "testid001"]
    assert len(found) == 1
    assert found[0]["materiality"] == "High"
    assert found[0]["category"] == "Earnings"
    print("test_summarize_with_mocked_articles: digest contains processed article")


def test_digest_default_returns_latest_date():
    resp = client.get("/api/news/digest")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    print("test_digest_default_returns_latest_date passed")


def test_digest_sorted_by_materiality():
    resp = client.get("/api/news/digest", params={"digest_date": "2025-01-15"})
    assert resp.status_code == 200
    articles = resp.json()["articles"]
    materiality_order = {"High": 0, "Medium": 1, "Low": 2}
    orders = [materiality_order[a["materiality"]] for a in articles]
    assert orders == sorted(orders)
    print("test_digest_sorted_by_materiality passed")


def test_digest_filters():
    resp = client.get("/api/news/digest", params={"digest_date": "2025-01-15", "materiality": "High"})
    data = resp.json()
    assert all(a["materiality"] == "High" for a in data["articles"])

    resp2 = client.get("/api/news/digest", params={"digest_date": "2025-01-15", "category": "M&A"})
    data2 = resp2.json()
    assert all(a["category"] == "M&A" for a in data2["articles"])

    resp3 = client.get("/api/news/digest", params={"digest_date": "2025-01-15", "company": "TCS.NS"})
    data3 = resp3.json()
    assert all(a["ticker"] == "TCS.NS" for a in data3["articles"])
    print("test_digest_filters passed")


def test_digest_invalid_materiality():
    resp = client.get("/api/news/digest", params={"materiality": "Critical"})
    assert resp.status_code == 400
    print("test_digest_invalid_materiality passed")


def test_digest_dates():
    resp = client.get("/api/news/digest-dates")
    assert resp.status_code == 200
    dates = resp.json()["dates"]
    assert "2025-01-15" in dates
    assert len(dates) >= 2
    print("test_digest_dates passed")


if __name__ == "__main__":
    test_watchlist_seeded_with_defaults()
    test_watchlist_add_and_remove()
    test_watchlist_add_invalid_ticker()
    test_fetch_news_falls_back_gracefully()
    test_summarize_with_mocked_articles()
    test_digest_default_returns_latest_date()
    test_digest_sorted_by_materiality()
    test_digest_filters()
    test_digest_invalid_materiality()
    test_digest_dates()
    print("\nAll integration tests passed.")
