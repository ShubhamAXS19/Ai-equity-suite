"""
Financial ratio computation.

Takes the raw multi-year income statement / balance sheet / cash flow data
(as returned by market_data._fetch_yfinance_financials, keyed by year ->
line item -> value) and computes standard ratios for each available year.

yfinance's line-item naming is fairly standardized but can vary slightly by
company (e.g. banks lack "Current Assets"/"Current Liabilities", and some
companies report "Stockholders Equity" vs "Common Stock Equity"). The
helpers below try a list of candidate keys for each concept and use the
first one present, so ratios degrade gracefully (return None) rather than
raising when a line item is missing.
"""
import pandas as pd


# Candidate key names for each financial statement concept, in priority order.
INCOME_KEYS = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "gross_profit": ["Gross Profit"],
    "operating_income": ["Operating Income", "Total Operating Income As Reported"],
    "net_income": ["Net Income", "Net Income Common Stockholders"],
    "ebit": ["EBIT", "Operating Income"],
    "interest_expense": ["Interest Expense", "Interest Expense Non Operating"],
}

BALANCE_KEYS = {
    "current_assets": ["Current Assets", "Total Current Assets"],
    "current_liabilities": ["Current Liabilities", "Total Current Liabilities"],
    "total_debt": ["Total Debt", "Net Debt"],
    "stockholders_equity": ["Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest"],
    "total_assets": ["Total Assets"],
}


def _get_first(year_data: dict, keys: list[str]):
    for k in keys:
        if k in year_data and year_data[k] is not None:
            return year_data[k]
    return None


def _safe_div(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def _round_pct(value):
    if value is None:
        return None
    return round(value * 100, 2)


def _round_ratio(value, decimals=2):
    if value is None:
        return None
    return round(value, decimals)


def compute_ratios(financials: dict) -> dict:
    """
    `financials` is the dict returned by _fetch_yfinance_financials:
        {
          "ticker": ...,
          "name": ...,
          "income_statement": {"2024": {...}, "2023": {...}, ...},
          "balance_sheet": {"2024": {...}, ...},
          "cash_flow": {"2024": {...}, ...},
        }

    Returns:
        {
          "ticker": ..., "name": ...,
          "ratio_table": [ {year, gross_margin_pct, operating_margin_pct,
                            net_margin_pct, current_ratio, debt_to_equity,
                            roe_pct, interest_coverage}, ... ]  # most recent first
          "series": {
              "years": [...],
              "revenue": [...],
              "net_profit": [...],
              "net_margin_pct": [...],
          }
        }
    """
    income = financials.get("income_statement", {})
    balance = financials.get("balance_sheet", {})

    # Years present in income statement, sorted descending (most recent first)
    years = sorted(income.keys(), reverse=True)

    ratio_table = []
    series_years = []
    series_revenue = []
    series_net_profit = []
    series_net_margin = []

    for year in years:
        inc = income.get(year, {})
        bal = balance.get(year, {})

        revenue = _get_first(inc, INCOME_KEYS["revenue"])
        gross_profit = _get_first(inc, INCOME_KEYS["gross_profit"])
        operating_income = _get_first(inc, INCOME_KEYS["operating_income"])
        net_income = _get_first(inc, INCOME_KEYS["net_income"])
        ebit = _get_first(inc, INCOME_KEYS["ebit"])
        interest_expense = _get_first(inc, INCOME_KEYS["interest_expense"])

        current_assets = _get_first(bal, BALANCE_KEYS["current_assets"])
        current_liabilities = _get_first(bal, BALANCE_KEYS["current_liabilities"])
        total_debt = _get_first(bal, BALANCE_KEYS["total_debt"])
        stockholders_equity = _get_first(bal, BALANCE_KEYS["stockholders_equity"])

        gross_margin = _round_pct(_safe_div(gross_profit, revenue))
        operating_margin = _round_pct(_safe_div(operating_income, revenue))
        net_margin = _round_pct(_safe_div(net_income, revenue))
        current_ratio = _round_ratio(_safe_div(current_assets, current_liabilities))
        debt_to_equity = _round_ratio(_safe_div(total_debt, stockholders_equity))
        roe = _round_pct(_safe_div(net_income, stockholders_equity))

        # Interest coverage: EBIT / |interest expense|. Skip if no debt-related
        # interest expense was reported (common for some non-financial years).
        interest_coverage = None
        if interest_expense is not None and abs(interest_expense) > 0:
            interest_coverage = _round_ratio(_safe_div(ebit, abs(interest_expense)))

        ratio_table.append({
            "year": year,
            "revenue": revenue,
            "net_profit": net_income,
            "gross_margin_pct": gross_margin,
            "operating_margin_pct": operating_margin,
            "net_margin_pct": net_margin,
            "current_ratio": current_ratio,
            "debt_to_equity": debt_to_equity,
            "roe_pct": roe,
            "interest_coverage": interest_coverage,
        })

        series_years.append(year)
        series_revenue.append(revenue)
        series_net_profit.append(net_income)
        series_net_margin.append(net_margin)

    return {
        "ticker": financials.get("ticker"),
        "name": financials.get("name"),
        "ratio_table": ratio_table,
        # Series are returned oldest-to-newest for natural left-to-right charting
        "series": {
            "years": list(reversed(series_years)),
            "revenue": list(reversed(series_revenue)),
            "net_profit": list(reversed(series_net_profit)),
            "net_margin_pct": list(reversed(series_net_margin)),
        },
    }
