"""
Prompt template and response parsing for AI news summarization +
materiality/category tagging (Phase 3.2 of News Monitor).
"""
import json
import re


VALID_MATERIALITY = {"High", "Medium", "Low"}
VALID_CATEGORIES = {"Earnings", "M&A", "Regulatory", "Leadership Change", "Other"}


def build_summarization_prompt(article: dict, company_name: str) -> str:
    return f"""You are a financial analyst triaging news for a portfolio monitoring system. Below is a news article headline (and source) related to {company_name} ({article['ticker']}), an NSE-listed Indian company.

ARTICLE TITLE: {article['title']}
SOURCE: {article['source']}
PUBLISHED: {article['published']}

Based on the title (and your general knowledge of the company and context), provide:

1. "summary": a 2-3 sentence summary of what this article likely covers and why it matters for an investor in {company_name}. If the title alone doesn't give enough detail to summarize confidently, say so explicitly in the summary rather than inventing specifics.

2. "materiality": one of "High", "Medium", or "Low" - how significant is this news for the company's investment thesis? High = could meaningfully move the stock or change the outlook (e.g. major earnings surprise, M&A, regulatory action). Medium = relevant but not thesis-changing (e.g. routine leadership change, minor partnership). Low = minor or routine (e.g. analyst note, small operational update).

3. "category": one of "Earnings", "M&A", "Regulatory", "Leadership Change", or "Other" - the type of news this represents.

Respond with ONLY a valid JSON object, no markdown, no code fences, no commentary:
{{
  "summary": "...",
  "materiality": "High" | "Medium" | "Low",
  "category": "Earnings" | "M&A" | "Regulatory" | "Leadership Change" | "Other"
}}"""


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_summarization_response(text: str) -> dict:
    """
    Parses the LLM response into {summary, materiality, category}, with
    safe defaults if parsing fails or values are out of the expected set.
    """
    cleaned = _strip_code_fences(text)
    parsed = None
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    if not isinstance(parsed, dict):
        return {
            "summary": text.strip()[:500] if text else "Summary unavailable.",
            "materiality": "Low",
            "category": "Other",
        }

    summary = parsed.get("summary") or "Summary unavailable."
    materiality = parsed.get("materiality") if parsed.get("materiality") in VALID_MATERIALITY else "Low"
    category = parsed.get("category") if parsed.get("category") in VALID_CATEGORIES else "Other"

    return {"summary": summary, "materiality": materiality, "category": category}
