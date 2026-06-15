"""
Integration tests for /api/analyzer endpoints.
Run with: python3 -m app.tests.test_analyzer_endpoint
"""
import json
import os
from unittest.mock import patch

TEST_DB = "/tmp/test_analyzer.db"
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


def test_ratios_from_seed_data():
    """RELIANCE.NS has seed data with 4 years; live yfinance is expected to
    fail in this sandbox, so this exercises the cache fallback path."""
    resp = client.get("/api/analyzer/company/RELIANCE.NS/ratios")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data["ratio_table"]) == 4
    assert data["ratio_table"][0]["year"] == "2024"
    assert data["series"]["years"] == ["2021", "2022", "2023", "2024"]
    assert data["cached"] is True  # seed data served via cache fallback
    print("test_ratios_from_seed_data passed")


def test_ratios_invalid_ticker():
    resp = client.get("/api/analyzer/company/FAKE.NS/ratios")
    assert resp.status_code == 404
    print("test_ratios_invalid_ticker passed")


def test_ratios_no_data_for_ticker_without_seed():
    """A valid ticker with no cache and (in this sandbox) no live data
    should return 503, not crash."""
    resp = client.get("/api/analyzer/company/WIPRO.NS/ratios")
    assert resp.status_code == 503
    print("test_ratios_no_data_for_ticker_without_seed passed")


MOCK_COMMENTARY = (
    "Revenue grew steadily from FY2021 to FY2024, supported by rising operating and net margins. "
    "Profitability has improved each year, with net margin increasing from about 10.7% to 8.8% "
    "(noting some compression in the most recent year despite revenue growth). Debt-to-equity has "
    "remained broadly stable, indicating leverage has not increased significantly relative to the "
    "growth in equity. Overall, the company shows consistent top-line growth with generally healthy "
    "profitability, though the recent dip in net margin despite revenue growth is worth monitoring."
)


def test_commentary_generation_and_caching():
    with patch("app.routers.analyzer.get_llm_completion") as mock_llm:
        mock_llm.return_value = LLMResult(text=MOCK_COMMENTARY, source="claude")

        resp = client.post("/api/analyzer/company/RELIANCE.NS/commentary")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["cached"] is False
        assert data["data_sources"]["llm"] == "claude"
        assert "Revenue grew steadily" in data["commentary"]
        print("test_commentary_generation_and_caching: fresh generation passed")

        # Second call same day - cached, LLM not called
        mock_llm.reset_mock()
        resp2 = client.post("/api/analyzer/company/RELIANCE.NS/commentary")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["cached"] is True
        mock_llm.assert_not_called()
        print("test_commentary_generation_and_caching: cache hit passed")

        # force_refresh bypasses cache
        mock_llm.reset_mock()
        resp3 = client.post("/api/analyzer/company/RELIANCE.NS/commentary?force_refresh=true")
        assert resp3.status_code == 200
        mock_llm.assert_called_once()
        print("test_commentary_generation_and_caching: force_refresh passed")


def test_commentary_no_data():
    resp = client.post("/api/analyzer/company/WIPRO.NS/commentary")
    assert resp.status_code == 503
    print("test_commentary_no_data passed")


def test_commentary_invalid_ticker():
    resp = client.post("/api/analyzer/company/FAKE.NS/commentary")
    assert resp.status_code == 404
    print("test_commentary_invalid_ticker passed")


if __name__ == "__main__":
    test_ratios_from_seed_data()
    test_ratios_invalid_ticker()
    test_ratios_no_data_for_ticker_without_seed()
    test_commentary_generation_and_caching()
    test_commentary_no_data()
    test_commentary_invalid_ticker()
    print("\nAll integration tests passed.")
