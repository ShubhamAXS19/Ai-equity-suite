"""
Market data provider abstraction.

Resolution order per request:
  1. If the frontend sends an `X-InsightSentry-Key` header with a non-empty
     value, use InsightSentry for quote/fundamentals data.
  2. Otherwise, fall back to yfinance (no key required).

NOTE: InsightSentry integration is currently a stub - `fetch_insightsentry_*`
functions raise NotImplementedError until real endpoint details are wired in.
When that happens, only this module needs to change; routers call the
provider-agnostic functions below.
"""
import yfinance as yf
import pandas as pd


class MarketDataResult:
    def __init__(self, data: dict, source: str):
        self.data = data
        self.source = source  # 'yfinance' | 'insightsentry'


# ---------------------------------------------------------------------------
# Public entrypoints (provider-agnostic)
# ---------------------------------------------------------------------------

def get_snapshot(ticker: str, user_insightsentry_key: str | None) -> MarketDataResult:
    user_insightsentry_key = (user_insightsentry_key or "").strip()

    if user_insightsentry_key:
        try:
            data = _fetch_insightsentry_snapshot(ticker, user_insightsentry_key)
            return MarketDataResult(data=data, source="insightsentry")
        except NotImplementedError:
            print("[market_data] InsightSentry not yet wired up; using yfinance")
        except Exception as e:
            print(f"[market_data] InsightSentry call failed ({e}); falling back to yfinance")

    data = _fetch_yfinance_snapshot(ticker)
    return MarketDataResult(data=data, source="yfinance")


def get_financial_statements(ticker: str, user_insightsentry_key: str | None) -> MarketDataResult:
    user_insightsentry_key = (user_insightsentry_key or "").strip()

    if user_insightsentry_key:
        try:
            data = _fetch_insightsentry_financials(ticker, user_insightsentry_key)
            return MarketDataResult(data=data, source="insightsentry")
        except NotImplementedError:
            print("[market_data] InsightSentry not yet wired up; using yfinance")
        except Exception as e:
            print(f"[market_data] InsightSentry call failed ({e}); falling back to yfinance")

    data = _fetch_yfinance_financials(ticker)
    return MarketDataResult(data=data, source="yfinance")


# ---------------------------------------------------------------------------
# yfinance implementation
# ---------------------------------------------------------------------------

def _fetch_yfinance_snapshot(ticker: str) -> dict:
    tk = yf.Ticker(ticker)
    info = tk.info or {}

    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    market_cap = info.get("marketCap")
    pe_ratio = info.get("trailingPE")
    pb_ratio = info.get("priceToBook")
    week52_high = info.get("fiftyTwoWeekHigh")
    week52_low = info.get("fiftyTwoWeekLow")
    currency = info.get("currency", "INR")
    name = info.get("longName") or info.get("shortName") or ticker

    # Latest revenue / net profit + YoY growth from annual financials
    latest_revenue = None
    latest_net_profit = None
    revenue_yoy = None
    net_profit_yoy = None
    fiscal_year = None

    try:
        fin = tk.financials  # columns are periods, most recent first
        if fin is not None and not fin.empty:
            cols = list(fin.columns)
            if len(cols) >= 1:
                latest_col = cols[0]
                fiscal_year = pd.to_datetime(latest_col).strftime("FY%Y")

                if "Total Revenue" in fin.index:
                    latest_revenue = _safe_float(fin.loc["Total Revenue", latest_col])
                    if len(cols) >= 2:
                        prev_revenue = _safe_float(fin.loc["Total Revenue", cols[1]])
                        revenue_yoy = _yoy(latest_revenue, prev_revenue)

                if "Net Income" in fin.index:
                    latest_net_profit = _safe_float(fin.loc["Net Income", latest_col])
                    if len(cols) >= 2:
                        prev_net_profit = _safe_float(fin.loc["Net Income", cols[1]])
                        net_profit_yoy = _yoy(latest_net_profit, prev_net_profit)
    except Exception as e:
        print(f"[yfinance] financials fetch failed for {ticker}: {e}")

    return {
        "ticker": ticker,
        "name": name,
        "current_price": current_price,
        "currency": currency,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "pb_ratio": pb_ratio,
        "week52_high": week52_high,
        "week52_low": week52_low,
        "latest_revenue": latest_revenue,
        "latest_net_profit": latest_net_profit,
        "revenue_yoy_growth": revenue_yoy,
        "net_profit_yoy_growth": net_profit_yoy,
        "fiscal_year": fiscal_year,
    }


def _fetch_yfinance_financials(ticker: str) -> dict:
    """
    Returns multi-year income statement, balance sheet, cash flow data
    needed for ratio computation (Phase 2 of Financial Analyzer module).
    """
    tk = yf.Ticker(ticker)
    income = tk.financials
    balance = tk.balance_sheet
    cashflow = tk.cashflow
    info = tk.info or {}

    def df_to_dict(df):
        if df is None or df.empty:
            return {}
        out = {}
        for col in df.columns:
            year = pd.to_datetime(col).strftime("%Y")
            out[year] = {idx: _safe_float(df.loc[idx, col]) for idx in df.index}
        return out

    return {
        "ticker": ticker,
        "name": info.get("longName") or info.get("shortName") or ticker,
        "income_statement": df_to_dict(income),
        "balance_sheet": df_to_dict(balance),
        "cash_flow": df_to_dict(cashflow),
    }


def _safe_float(val):
    try:
        if pd.isna(val):
            return None
        return float(val)
    except Exception:
        return None


def _yoy(latest, prev):
    if latest is None or prev is None or prev == 0:
        return None
    return round((latest - prev) / abs(prev) * 100, 2)


# ---------------------------------------------------------------------------
# InsightSentry implementation (stub - to be filled in with real endpoints)
# ---------------------------------------------------------------------------

def _fetch_insightsentry_snapshot(ticker: str, api_key: str) -> dict:
    raise NotImplementedError("InsightSentry snapshot endpoint not yet configured")


def _fetch_insightsentry_financials(ticker: str, api_key: str) -> dict:
    raise NotImplementedError("InsightSentry financials endpoint not yet configured")
