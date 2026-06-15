"""
Shared configuration and constants for the AI Equity Research Suite backend.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Server-side fallback keys (from .env) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
INSIGHTSENTRY_API_KEY = os.getenv("INSIGHTSENTRY_API_KEY", "")  # optional server-side fallback

# --- Model names ---
CLAUDE_MODEL = "claude-sonnet-4-6"
GROQ_MODEL = "llama-3.3-70b-versatile"

# --- Database ---
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.db")

# --- Hardcoded NSE large-cap company list (shared across all three modules) ---
COMPANIES = [
    {"ticker": "RELIANCE.NS", "name": "Reliance Industries Ltd"},
    {"ticker": "TCS.NS", "name": "Tata Consultancy Services Ltd"},
    {"ticker": "INFY.NS", "name": "Infosys Ltd"},
    {"ticker": "HDFCBANK.NS", "name": "HDFC Bank Ltd"},
    {"ticker": "ICICIBANK.NS", "name": "ICICI Bank Ltd"},
    {"ticker": "ITC.NS", "name": "ITC Ltd"},
    {"ticker": "SBIN.NS", "name": "State Bank of India"},
    {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd"},
    {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance Ltd"},
    {"ticker": "LT.NS", "name": "Larsen & Toubro Ltd"},
    {"ticker": "MARUTI.NS", "name": "Maruti Suzuki India Ltd"},
    {"ticker": "TATAMOTORS.NS", "name": "Tata Motors Ltd"},
    {"ticker": "WIPRO.NS", "name": "Wipro Ltd"},
    {"ticker": "AXISBANK.NS", "name": "Axis Bank Ltd"},
    {"ticker": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Ltd"},
]

VALID_TICKERS = {c["ticker"] for c in COMPANIES}

# --- Default watchlist for News Monitor (first 5 companies) ---
DEFAULT_WATCHLIST = [c["ticker"] for c in COMPANIES[:5]]

# --- Search terms used to match news articles to companies ---
# yfinance/legal names (e.g. "Reliance Industries Ltd") often don't appear
# verbatim in headlines, so each company maps to a list of terms that are
# checked case-insensitively against article titles.
COMPANY_SEARCH_TERMS = {
    "RELIANCE.NS": ["Reliance Industries", "Reliance Jio", "RIL"],
    "TCS.NS": ["Tata Consultancy", "TCS"],
    "INFY.NS": ["Infosys"],
    "HDFCBANK.NS": ["HDFC Bank"],
    "ICICIBANK.NS": ["ICICI Bank"],
    "ITC.NS": ["ITC Ltd", "ITC Hotels", "ITC shares", " ITC "],
    "SBIN.NS": ["State Bank of India", "SBI"],
    "HINDUNILVR.NS": ["Hindustan Unilever", "HUL"],
    "BAJFINANCE.NS": ["Bajaj Finance"],
    "LT.NS": ["Larsen & Toubro", "Larsen and Toubro", "L&T"],
    "MARUTI.NS": ["Maruti Suzuki", "Maruti"],
    "TATAMOTORS.NS": ["Tata Motors"],
    "WIPRO.NS": ["Wipro"],
    "AXISBANK.NS": ["Axis Bank"],
    "KOTAKBANK.NS": ["Kotak Mahindra", "Kotak Bank"],
}

# --- RSS feed sources for News Monitor ---
RSS_FEEDS = [
    {"name": "Moneycontrol", "url": "https://www.moneycontrol.com/rss/latestnews.xml"},
    {"name": "Economic Times Markets", "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"},
    {"name": "LiveMint Markets", "url": "https://www.livemint.com/rss/markets"},
]
