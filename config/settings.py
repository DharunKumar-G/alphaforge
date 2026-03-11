import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API — reads from .env locally, or Streamlit Cloud secrets in production
def _get_gemini_key():
    # Try env var first (local .env or Azure)
    key = os.getenv("GEMINI_API_KEY", "")
    if key:
        return key
    # Fall back to Streamlit secrets (Streamlit Cloud)
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""

GEMINI_API_KEY = _get_gemini_key()
GEMINI_MODEL = "gemma-3-4b-it"

# Database — use /tmp on Streamlit Cloud (writable), local path otherwise
_default_db = "/tmp/alphaforge.db" if os.getenv("STREAMLIT_SHARING_MODE") or not os.access(".", os.W_OK) else "data/db/alphaforge.db"
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", _default_db)

# Universe
DEFAULT_UNIVERSE = "nifty500"
BENCHMARK = "^NSEI"  # Nifty 50 index

# Backtest defaults
DEFAULT_START_DATE = "2015-01-01"
DEFAULT_REBALANCE_FREQ = "monthly"  # daily | weekly | monthly | quarterly
TOP_N_STOCKS = 20

# Factor weights (default, user can override)
DEFAULT_FACTOR_WEIGHTS = {
    "momentum": 0.30,
    "value": 0.25,
    "quality": 0.25,
    "volatility": 0.20,
}

# Regime thresholds
REGIME_BULL_THRESHOLD = 0.60
REGIME_BEAR_THRESHOLD = 0.40

# Risk limits
MAX_DRAWDOWN_ALERT = 0.15   # 15%
MAX_SINGLE_STOCK_WEIGHT = 0.10  # 10%
MAX_SECTOR_WEIGHT = 0.30        # 30%

# India tax (FY2024-25)
STT_DELIVERY = 0.001    # 0.1% on delivery
STT_INTRADAY = 0.00025  # 0.025% on sell side
BROKERAGE = 0.0003      # ~0.03% typical
GST_ON_BROKERAGE = 0.18
STCG_TAX_RATE = 0.20    # Short-term capital gains (< 1 year)
LTCG_TAX_RATE = 0.125   # Long-term capital gains (> 1 year, above 1.25L)
LTCG_EXEMPTION = 125000  # ₹1.25 lakh exempt
