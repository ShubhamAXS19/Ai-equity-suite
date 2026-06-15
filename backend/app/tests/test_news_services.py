"""
Unit tests for news_fetcher.match_articles_for_company and
news_summarizer.parse_summarization_response.

Run with: python3 -m app.tests.test_news_services
"""
from app.services.news_fetcher import match_articles_for_company, _article_id
from app.services.news_summarizer import parse_summarization_response


SAMPLE_ARTICLES = [
    {"title": "Reliance Industries Q3 profit beats estimates", "link": "https://example.com/a1", "source": "Moneycontrol", "published": "2025-01-15T09:00:00"},
    {"title": "TCS wins large deal from European bank", "link": "https://example.com/a2", "source": "ET Markets", "published": "2025-01-15T08:00:00"},
    {"title": "HDFC Bank shares gain on RBI policy news", "link": "https://example.com/a3", "source": "LiveMint", "published": "2025-01-15T07:00:00"},
    {"title": "Global markets mixed amid Fed commentary", "link": "https://example.com/a4", "source": "Moneycontrol", "published": "2025-01-15T06:00:00"},
    {"title": "ITC announces dividend; ITC Hotels demerger update", "link": "https://example.com/a5", "source": "ET Markets", "published": "2025-01-15T05:00:00"},
]


def test_match_reliance():
    matches = match_articles_for_company(SAMPLE_ARTICLES, "RELIANCE.NS")
    assert len(matches) == 1
    assert matches[0]["title"] == "Reliance Industries Q3 profit beats estimates"
    assert matches[0]["ticker"] == "RELIANCE.NS"
    assert "id" in matches[0]
    print("test_match_reliance passed")


def test_match_tcs():
    matches = match_articles_for_company(SAMPLE_ARTICLES, "TCS.NS")
    assert len(matches) == 1
    assert "TCS" in matches[0]["title"]
    print("test_match_tcs passed")


def test_match_no_results():
    matches = match_articles_for_company(SAMPLE_ARTICLES, "WIPRO.NS")
    assert matches == []
    print("test_match_no_results passed")


def test_match_itc_multiple_terms():
    matches = match_articles_for_company(SAMPLE_ARTICLES, "ITC.NS")
    assert len(matches) == 1
    print("test_match_itc_multiple_terms passed")


def test_article_id_stable():
    id1 = _article_id("https://example.com/a1")
    id2 = _article_id("https://example.com/a1")
    id3 = _article_id("https://example.com/a2")
    assert id1 == id2
    assert id1 != id3
    print("test_article_id_stable passed")


def test_parse_clean_json():
    text = '{"summary": "Test summary", "materiality": "High", "category": "Earnings"}'
    parsed = parse_summarization_response(text)
    assert parsed["summary"] == "Test summary"
    assert parsed["materiality"] == "High"
    assert parsed["category"] == "Earnings"
    print("test_parse_clean_json passed")


def test_parse_invalid_materiality_defaults_low():
    text = '{"summary": "Test", "materiality": "Critical", "category": "Earnings"}'
    parsed = parse_summarization_response(text)
    assert parsed["materiality"] == "Low"
    print("test_parse_invalid_materiality_defaults_low passed")


def test_parse_invalid_category_defaults_other():
    text = '{"summary": "Test", "materiality": "Medium", "category": "Weird"}'
    parsed = parse_summarization_response(text)
    assert parsed["category"] == "Other"
    print("test_parse_invalid_category_defaults_other passed")


def test_parse_unstructured_fallback():
    text = "This is just plain text, not JSON."
    parsed = parse_summarization_response(text)
    assert parsed["materiality"] == "Low"
    assert parsed["category"] == "Other"
    assert "plain text" in parsed["summary"]
    print("test_parse_unstructured_fallback passed")


if __name__ == "__main__":
    test_match_reliance()
    test_match_tcs()
    test_match_no_results()
    test_match_itc_multiple_terms()
    test_article_id_stable()
    test_parse_clean_json()
    test_parse_invalid_materiality_defaults_low()
    test_parse_invalid_category_defaults_other()
    test_parse_unstructured_fallback()
    print("\nAll tests passed.")
