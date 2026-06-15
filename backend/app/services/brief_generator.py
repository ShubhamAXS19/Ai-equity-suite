"""
Research brief generation service.

Builds a prompt from snapshot data (using the requested prompt version),
calls the LLM provider (Claude with Groq fallback), and parses the result
into a structured brief. v1 (rough draft) often doesn't return clean JSON,
so a best-effort fallback wraps unstructured text into the same shape.
"""
import json
import re
from app.services.llm_provider import get_llm_completion
from app.services.prompts import PROMPT_VERSIONS, DEFAULT_PROMPT_VERSION


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _try_parse_json(text: str):
    cleaned = _strip_code_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find the first {...} block in the text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


def _fallback_unstructured_brief(raw_text: str) -> dict:
    """
    Used when the LLM (typically prompt v1) doesn't return valid JSON.
    Wraps the raw text into the standard brief shape so the frontend
    always receives a consistent structure, with the full text placed
    in business_overview and the other sections left empty - this also
    visually demonstrates *why* the refined prompt (v2/v3) is better.
    """
    return {
        "business_overview": raw_text.strip(),
        "financial_snapshot": "",
        "recent_developments": [],
        "key_risks": [],
        "_unstructured": True,
    }


def generate_brief(snapshot: dict, user_claude_key: str | None, prompt_version: str = DEFAULT_PROMPT_VERSION):
    """
    Returns (brief_dict, llm_source, prompt_version_used).
    """
    if prompt_version not in PROMPT_VERSIONS:
        prompt_version = DEFAULT_PROMPT_VERSION

    builder = PROMPT_VERSIONS[prompt_version]["builder"]
    prompt = builder(snapshot)

    result = get_llm_completion(prompt, user_claude_key, max_tokens=1200)

    parsed = _try_parse_json(result.text)
    if parsed is None:
        parsed = _fallback_unstructured_brief(result.text)

    # Ensure all expected keys exist even if the model omitted one
    parsed.setdefault("business_overview", "")
    parsed.setdefault("financial_snapshot", "")
    parsed.setdefault("recent_developments", [])
    parsed.setdefault("key_risks", [])

    return parsed, result.source, prompt_version
