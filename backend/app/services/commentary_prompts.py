"""
Prompt template for AI commentary on financial ratio trends/anomalies.
"""


def build_commentary_prompt(ratio_data: dict) -> str:
    table = ratio_data.get("ratio_table", [])

    # Render the ratio table as a simple text table, oldest year first for
    # natural narrative reading.
    rows = list(reversed(table))
    lines = []
    for row in rows:
        lines.append(
            f"  {row['year']}: Revenue={_fmt(row['revenue'])}, Net Profit={_fmt(row['net_profit'])}, "
            f"Gross Margin={_fmt_pct(row['gross_margin_pct'])}, Operating Margin={_fmt_pct(row['operating_margin_pct'])}, "
            f"Net Margin={_fmt_pct(row['net_margin_pct'])}, Current Ratio={_fmt(row['current_ratio'])}, "
            f"Debt-to-Equity={_fmt(row['debt_to_equity'])}, ROE={_fmt_pct(row['roe_pct'])}, "
            f"Interest Coverage={_fmt(row['interest_coverage'])}"
        )
    table_text = "\n".join(lines)

    return f"""You are a financial analyst reviewing a multi-year ratio summary for {ratio_data.get('name')} ({ratio_data.get('ticker')}), an NSE-listed Indian company. The data below is ordered from oldest to most recent year.

RATIO TABLE:
{table_text}

Write a plain-English commentary for a non-technical stakeholder (e.g. a relationship manager, not a financial analyst). Your commentary must:

1. Identify the 2-3 most notable trends across the years (e.g. consistent margin expansion, accelerating revenue growth, improving/worsening leverage).
2. Flag any anomalies or concerns - for example, margin compression despite revenue growth, rising debt-to-equity, declining interest coverage, or a current ratio trending toward risk levels. If there are no significant anomalies, say so explicitly rather than inventing one.
3. End with a short overall summary sentence.

Constraints:
- Total response under 200 words.
- Plain English, no jargon without brief explanation, no markdown formatting, no bullet point symbols (write in flowing prose or simple numbered sentences).
- Be specific - reference actual numbers/years from the table where relevant.
- Do not speculate beyond what the data shows; if a ratio is missing/None for a year, don't comment on it.

Respond with ONLY the commentary text, no preamble, no headers, no JSON."""


def _fmt(val):
    if val is None:
        return "N/A"
    if isinstance(val, (int, float)) and abs(val) >= 1e9:
        return f"₹{val/1e9:.1f}B"
    return str(val)


def _fmt_pct(val):
    if val is None:
        return "N/A"
    return f"{val}%"
