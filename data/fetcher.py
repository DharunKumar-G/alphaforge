"""
Price and fundamental data fetcher using yfinance.
Caches results to avoid repeated downloads.
"""
import pandas as pd
import yfinance as yf
from pathlib import Path
from loguru import logger
from datetime import datetime, timedelta

import os
CACHE_DIR = Path("/tmp/alphaforge/prices") if not os.access("data", os.W_OK) else Path("data/cache/prices")


def _cache_path(symbol: str) -> Path:
    return CACHE_DIR / f"{symbol.replace('.', '_')}.parquet"


def fetch_prices(symbol: str, start: str = "2015-01-01", end: str = None,
                 use_cache: bool = True) -> pd.DataFrame:
    """
    Fetch OHLCV data for a symbol. Returns DataFrame indexed by date.
    Columns: Open, High, Low, Close, Volume, Adj Close
    """
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")

    cache = _cache_path(symbol)

    if use_cache and cache.exists():
        cached = pd.read_parquet(cache)
        # Extend cache if needed
        last_date = cached.index.max()
        if pd.Timestamp(end) > last_date + timedelta(days=1):
            new_start = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
            new_data = _download(symbol, new_start, end)
            if not new_data.empty:
                cached = pd.concat([cached, new_data])
                cached.to_parquet(cache)
        return cached[cached.index >= pd.Timestamp(start)]

    df = _download(symbol, start, end)
    if not df.empty:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache)
    return df


def _download(symbol: str, start: str, end: str) -> pd.DataFrame:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, auto_adjust=True)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        logger.info(f"Downloaded {symbol}: {len(df)} rows")
        return df
    except Exception as e:
        logger.warning(f"Failed to fetch {symbol}: {e}")
        return pd.DataFrame()


def fetch_multiple(symbols: list[str], start: str = "2015-01-01",
                   end: str = None) -> dict[str, pd.DataFrame]:
    """Fetch prices for multiple symbols. Returns dict of symbol -> DataFrame."""
    result = {}
    for sym in symbols:
        df = fetch_prices(sym, start=start, end=end)
        if not df.empty:
            result[sym] = df
    return result


def fetch_close_matrix(symbols: list[str], start: str = "2015-01-01",
                        end: str = None) -> pd.DataFrame:
    """Returns wide DataFrame: date × symbol (Close prices)."""
    prices = fetch_multiple(symbols, start=start, end=end)
    closes = {sym: df["Close"] for sym, df in prices.items()}
    return pd.DataFrame(closes).sort_index()


def fetch_fundamentals(symbol: str) -> dict:
    """Return key fundamental metrics from yfinance."""
    try:
        info = yf.Ticker(symbol).info
        return {
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "profit_margin": info.get("profitMargins"),
            "market_cap": info.get("marketCap"),
            "dividend_yield": info.get("dividendYield"),
            "sector": info.get("sector"),
            "name": info.get("longName"),
        }
    except Exception as e:
        logger.warning(f"Fundamentals failed for {symbol}: {e}")
        return {}
