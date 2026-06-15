"""
Integration test for the /brief endpoint, mocking get_llm_completion so no
real API key is needed. Verifies: prompt building, JSON parsing, caching
(ticker+date+prompt_version), and the cached/fresh response shape.

Run with: python3 -m app.tests.test_brief_endpoint
"""
import json
import os
import sys
from unittest.mock import patch

# Use a separate test DB so we don't pollute the real one
TEST_DB = "/tmp/test_brief.db"
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

MOCK_BRIEF_JSON = json.dumps({
    "business_overview": "Reliance Industries is a diversified Indian conglomerate with operations in energy, retail, and telecommunications.",
    "financial_snapshot": "The company shows steady revenue growth with a moderate P/E ratio, suggesting fair valuation relative to growth.",
    "recent_developments": [
        "Continued expansion of Jio's 5G network across India.",
        "Growth in Reliance Retail's store footprint.",
        "Ongoing investments in renewable energy ventures."
    ],
    "key_risks": [
        "High capital expenditure requirements across segments.",
        "Regulatory risks in telecom and energy sectors."
    ]
})


def test_brief_generation_and_caching():
    with patch("app.services.brief_generator.get_llm_completion") as mock_llm:
        mock_llm.return_value = LLMResult(text=MOCK_BRIEF_JSON, source="claude")

        # First call - should generate fresh
        resp = client.post("/api/research/company/RELIANCE.NS/brief")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["cached"] is False
        assert data["data_sources"]["llm"] == "claude"
        assert data["prompt_version"] == "v2"
        assert "business_overview" in data["brief"]
        assert len(data["brief"]["recent_developments"]) == 3
        print("test_brief_generation_and_caching: fresh generation passed")

        # Second call same day - should be cached, mock NOT called again
        mock_llm.reset_mock()
        resp2 = client.post("/api/research/company/RELIANCE.NS/brief")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["cached"] is True
        mock_llm.assert_not_called()
        print("test_brief_generation_and_caching: cache hit passed")

        # Different prompt version - should generate fresh again
        resp3 = client.post("/api/research/company/RELIANCE.NS/brief?prompt_version=v1")
        assert resp3.status_code == 200
        data3 = resp3.json()
        assert data3["cached"] is False
        assert data3["prompt_version"] == "v1"
        print("test_brief_generation_and_caching: different prompt version generates fresh")

        # force_refresh should bypass cache
        mock_llm.reset_mock()
        resp4 = client.post("/api/research/company/RELIANCE.NS/brief?force_refresh=true")
        assert resp4.status_code == 200
        data4 = resp4.json()
        assert data4["cached"] is False
        mock_llm.assert_called_once()
        print("test_brief_generation_and_caching: force_refresh bypasses cache")


def test_invalid_ticker():
    resp = client.post("/api/research/company/FAKE.NS/brief")
    assert resp.status_code == 404
    print("test_invalid_ticker passed")


def test_invalid_prompt_version():
    resp = client.post("/api/research/company/RELIANCE.NS/brief?prompt_version=v99")
    assert resp.status_code == 400
    print("test_invalid_prompt_version passed")


def test_unstructured_v1_fallback():
    """v1 prompt might return plain text - verify graceful fallback shape."""
    with patch("app.services.brief_generator.get_llm_completion") as mock_llm:
        mock_llm.return_value = LLMResult(
            text="Reliance is a big company in India with many businesses including retail and telecom.",
            source="groq",
        )
        resp = client.post("/api/research/company/TCS.NS/brief?prompt_version=v1&force_refresh=true")
        assert resp.status_code == 200
        data = resp.json()
        assert data["brief"]["_unstructured"] is True
        assert data["brief"]["business_overview"]
        assert data["brief"]["recent_developments"] == []
        print("test_unstructured_v1_fallback passed")


if __name__ == "__main__":
    test_brief_generation_and_caching()
    test_invalid_ticker()
    test_invalid_prompt_version()
    test_unstructured_v1_fallback()
    print("\nAll integration tests passed.")
