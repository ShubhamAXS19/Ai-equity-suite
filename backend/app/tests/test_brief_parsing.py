"""
Quick manual tests for brief_generator parsing logic (no API calls).
Run with: python3 -m app.tests.test_brief_parsing
"""
from app.services.brief_generator import _try_parse_json, _fallback_unstructured_brief, _strip_code_fences


def test_clean_json():
    text = '{"business_overview": "ABC", "financial_snapshot": "DEF", "recent_developments": ["a","b","c"], "key_risks": ["x","y"]}'
    parsed = _try_parse_json(text)
    assert parsed is not None
    assert parsed["business_overview"] == "ABC"
    print("test_clean_json passed")


def test_code_fenced_json():
    text = '```json\n{"business_overview": "ABC", "financial_snapshot": "DEF", "recent_developments": [], "key_risks": []}\n```'
    parsed = _try_parse_json(text)
    assert parsed is not None
    assert parsed["financial_snapshot"] == "DEF"
    print("test_code_fenced_json passed")


def test_json_with_preamble():
    text = 'Sure, here is the brief:\n{"business_overview": "ABC", "financial_snapshot": "DEF", "recent_developments": [], "key_risks": []}'
    parsed = _try_parse_json(text)
    assert parsed is not None
    assert parsed["business_overview"] == "ABC"
    print("test_json_with_preamble passed")


def test_unstructured_fallback():
    text = "This is just a paragraph of text about the company, no JSON here."
    parsed = _try_parse_json(text)
    assert parsed is None
    fallback = _fallback_unstructured_brief(text)
    assert fallback["business_overview"] == text
    assert fallback["_unstructured"] is True
    assert fallback["recent_developments"] == []
    print("test_unstructured_fallback passed")


if __name__ == "__main__":
    test_clean_json()
    test_code_fenced_json()
    test_json_with_preamble()
    test_unstructured_fallback()
    print("\nAll tests passed.")
