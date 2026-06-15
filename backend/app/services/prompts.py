"""
Prompt templates for AI research brief generation.

Two versions are kept side by side to demonstrate prompt iteration
(used in Phase 3's "Prompt Versions" comparison toggle):

  v1 - a rough first draft: minimal structure/guidance, prone to vague
       or inconsistent output.
  v2 - a refined version: explicit section structure, word caps, tone
       guidance, and a request for valid JSON output for reliable parsing.

Both versions are built from the same snapshot data so outputs can be
compared directly.
"""


def _format_snapshot_for_prompt(snapshot: dict) -> str:
    def fmt(val, suffix=""):
        if val is None:
            return "N/A"
        return f"{val}{suffix}"

    return (
        f"Company: {snapshot.get('name')} ({snapshot.get('ticker')})\n"
        f"Current Price: {fmt(snapshot.get('current_price'))} {snapshot.get('currency', 'INR')}\n"
        f"Market Cap: {fmt(snapshot.get('market_cap'))}\n"
        f"P/E Ratio: {fmt(snapshot.get('pe_ratio'))}\n"
        f"P/B Ratio: {fmt(snapshot.get('pb_ratio'))}\n"
        f"52-Week High: {fmt(snapshot.get('week52_high'))}\n"
        f"52-Week Low: {fmt(snapshot.get('week52_low'))}\n"
        f"Latest Revenue ({snapshot.get('fiscal_year', 'latest FY')}): {fmt(snapshot.get('latest_revenue'))}\n"
        f"Revenue YoY Growth: {fmt(snapshot.get('revenue_yoy_growth'), '%')}\n"
        f"Latest Net Profit ({snapshot.get('fiscal_year', 'latest FY')}): {fmt(snapshot.get('latest_net_profit'))}\n"
        f"Net Profit YoY Growth: {fmt(snapshot.get('net_profit_yoy_growth'), '%')}\n"
    )


def build_prompt_v1(snapshot: dict) -> str:
    """Rough first-draft prompt: loose instructions, no output format constraints."""
    snapshot_text = _format_snapshot_for_prompt(snapshot)
    return (
        f"Write a research brief about {snapshot.get('name')}.\n\n"
        f"Here is some data:\n{snapshot_text}\n\n"
        f"Include a business overview, talk about the financials, mention recent news, "
        f"and any risks. Keep it short."
    )


def build_prompt_v2(snapshot: dict) -> str:
    """Refined prompt: explicit structure, word limits, tone, and strict JSON output."""
    snapshot_text = _format_snapshot_for_prompt(snapshot)
    return f"""You are a sell-side equity research analyst writing a concise one-page brief on an NSE-listed Indian company. Use a professional, neutral research tone.

COMPANY SNAPSHOT DATA:
{snapshot_text}

Write a structured research brief with exactly these four sections:

1. "business_overview": 2-3 sentences describing what the company does, its sector, and its market position. Base this on your general knowledge of the company.

2. "financial_snapshot": 2-4 sentences interpreting the key metrics above (valuation, growth, profitability) - what do these numbers suggest about the company's current state?

3. "recent_developments": exactly 3 bullet points (each one sentence) on recent developments, strategic moves, or news relevant to this company. Use your general knowledge - note that this is a placeholder for a live news feed and may not reflect the most recent events.

4. "key_risks": 2-3 bullet points (each one sentence) on the key risks an investor should be aware of for this company.

Keep the ENTIRE brief under 400 words total.

Respond with ONLY a valid JSON object in this exact shape, with no markdown formatting, no code fences, and no extra commentary:
{{
  "business_overview": "...",
  "financial_snapshot": "...",
  "recent_developments": ["...", "...", "..."],
  "key_risks": ["...", "..."]
}}"""


def build_prompt_v3(snapshot: dict) -> str:
    """
    Most refined version: adds explicit handling for missing/N/A data and
    instructs the model to flag data gaps rather than fabricate numbers.
    """
    snapshot_text = _format_snapshot_for_prompt(snapshot)
    return f"""You are a sell-side equity research analyst at an Indian brokerage, writing a concise one-page brief on an NSE-listed company for an internal audience of portfolio managers. Use a professional, neutral, fact-based research tone - avoid hype or promotional language.

COMPANY SNAPSHOT DATA (most recently available):
{snapshot_text}

Note: any field marked "N/A" was unavailable from the data source - do not fabricate a value for it; simply omit it from your interpretation.

Write a structured research brief with exactly these four sections:

1. "business_overview": 2-3 sentences on what the company does, its sector/industry, and its competitive position in India. Base this on your general knowledge of the company as of your training data.

2. "financial_snapshot": 2-4 sentences interpreting the valuation (P/E, P/B vs. typical sector norms if known), growth (revenue/profit YoY), and what these collectively suggest about the company's current financial health. Be specific about what the numbers imply, not just restating them.

3. "recent_developments": exactly 3 bullet points (one sentence each) on recent strategic developments, business updates, or notable events for this company, based on your general knowledge. Explicitly note in your response that this section is a placeholder pending integration with a live news feed.

4. "key_risks": 2-3 bullet points (one sentence each) on the most relevant risks for an investor in this company right now - consider sector-specific, company-specific, and macro risks.

Hard constraints:
- Total brief length under 400 words.
- No markdown, no headers, no asterisks within the text fields.
- Respond with ONLY a valid JSON object, no code fences, no preamble, no trailing commentary.

JSON shape:
{{
  "business_overview": "...",
  "financial_snapshot": "...",
  "recent_developments": ["...", "...", "..."],
  "key_risks": ["...", "..."]
}}"""


PROMPT_VERSIONS = {
    "v1": {
        "label": "v1 - Rough Draft",
        "description": "Minimal instructions, no output structure or constraints.",
        "builder": build_prompt_v1,
    },
    "v2": {
        "label": "v2 - Structured & Constrained",
        "description": "Explicit sections, word cap, professional tone, strict JSON output.",
        "builder": build_prompt_v2,
    },
    "v3": {
        "label": "v3 - Refined (handles missing data)",
        "description": "Adds guidance for N/A fields and sector-aware interpretation.",
        "builder": build_prompt_v3,
    },
}

DEFAULT_PROMPT_VERSION = "v2"
