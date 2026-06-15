"""
Unit tests for ratio_calculator.compute_ratios.
Run with: python3 -m app.tests.test_ratio_calculator
"""
from app.services.ratio_calculator import compute_ratios


SAMPLE_FINANCIALS = {
    "ticker": "RELIANCE.NS",
    "name": "Reliance Industries Ltd",
    "income_statement": {
        "2024": {
            "Total Revenue": 1000.0,
            "Gross Profit": 300.0,
            "Operating Income": 170.0,
            "EBIT": 170.0,
            "Net Income": 88.0,
            "Interest Expense": 23.0,
        },
        "2023": {
            "Total Revenue": 900.0,
            "Gross Profit": 270.0,
            "Operating Income": 148.0,
            "EBIT": 148.0,
            "Net Income": 78.0,
            "Interest Expense": 21.0,
        },
    },
    "balance_sheet": {
        "2024": {
            "Current Assets": 350.0,
            "Current Liabilities": 280.0,
            "Total Debt": 373.0,
            "Stockholders Equity": 947.0,
        },
        "2023": {
            "Current Assets": 320.0,
            "Current Liabilities": 270.0,
            "Total Debt": 364.0,
            "Stockholders Equity": 866.0,
        },
    },
    "cash_flow": {},
}


def test_basic_ratios():
    result = compute_ratios(SAMPLE_FINANCIALS)
    table = result["ratio_table"]
    assert len(table) == 2

    row_2024 = table[0]  # most recent first
    assert row_2024["year"] == "2024"
    assert row_2024["gross_margin_pct"] == 30.0
    assert row_2024["operating_margin_pct"] == 17.0
    assert row_2024["net_margin_pct"] == 8.8
    assert row_2024["current_ratio"] == round(350 / 280, 2)
    assert row_2024["debt_to_equity"] == round(373 / 947, 2)
    assert row_2024["roe_pct"] == round(88 / 947 * 100, 2)
    assert row_2024["interest_coverage"] == round(170 / 23, 2)
    print("test_basic_ratios passed")


def test_series_order():
    result = compute_ratios(SAMPLE_FINANCIALS)
    series = result["series"]
    # series should be oldest-to-newest
    assert series["years"] == ["2023", "2024"]
    assert series["revenue"] == [900.0, 1000.0]
    assert series["net_profit"] == [78.0, 88.0]
    print("test_series_order passed")


def test_missing_line_items_graceful():
    partial = {
        "ticker": "TEST.NS",
        "name": "Test Co",
        "income_statement": {
            "2024": {"Total Revenue": 500.0, "Net Income": 40.0},
        },
        "balance_sheet": {
            "2024": {},
        },
        "cash_flow": {},
    }
    result = compute_ratios(partial)
    row = result["ratio_table"][0]
    assert row["net_margin_pct"] == 8.0
    assert row["gross_margin_pct"] is None  # no Gross Profit reported
    assert row["current_ratio"] is None  # no balance sheet data
    assert row["interest_coverage"] is None  # no interest expense
    print("test_missing_line_items_graceful passed")


def test_empty_financials():
    empty = {"ticker": "EMPTY.NS", "name": "Empty Co", "income_statement": {}, "balance_sheet": {}, "cash_flow": {}}
    result = compute_ratios(empty)
    assert result["ratio_table"] == []
    assert result["series"]["years"] == []
    print("test_empty_financials passed")


if __name__ == "__main__":
    test_basic_ratios()
    test_series_order()
    test_missing_line_items_graceful()
    test_empty_financials()
    print("\nAll tests passed.")
