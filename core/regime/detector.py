"""
Market regime detection using multiple signals.
Regimes: Bull, Sideways, Bear
"""
import pandas as pd
import numpy as np
from loguru import logger


def detect_regime(market_prices: pd.Series, window_short: int = 50,
                  window_long: int = 200) -> pd.DataFrame:
    """
    Detect market regime using:
    - Price vs 200-day MA (trend)
    - 50 vs 200 MA crossover (golden/death cross)
    - Rolling volatility (VIX proxy)
    - Momentum (3-month return)
    
    Returns DataFrame with date index and columns:
        regime (Bull/Sideways/Bear), confidence (0-1), signals
    """
    df = pd.DataFrame(index=market_prices.index)
    df["price"] = market_prices
    df["ma50"] = market_prices.rolling(window_short).mean()
    df["ma200"] = market_prices.rolling(window_long).mean()
    df["returns"] = market_prices.pct_change()
    df["vol_21d"] = df["returns"].rolling(21).std() * np.sqrt(252)
    df["mom_63d"] = market_prices.pct_change(63)

    # Signals (1 = bullish, -1 = bearish, 0 = neutral)
    df["sig_trend"] = np.where(df["price"] > df["ma200"], 1, -1)
    df["sig_cross"] = np.where(df["ma50"] > df["ma200"], 1, -1)
    df["sig_mom"] = np.where(df["mom_63d"] > 0.05, 1,
                    np.where(df["mom_63d"] < -0.05, -1, 0))
    df["sig_vol"] = np.where(df["vol_21d"] < 0.18, 1,
                   np.where(df["vol_21d"] > 0.28, -1, 0))

    # Composite score: -4 to +4
    df["regime_score"] = (df["sig_trend"] + df["sig_cross"] +
                          df["sig_mom"] + df["sig_vol"])

    # Classify
    def classify(score):
        if score >= 2:
            return "Bull"
        elif score <= -2:
            return "Bear"
        else:
            return "Sideways"

    df["regime"] = df["regime_score"].apply(classify)

    # Confidence: how many signals agree / total signals
    df["confidence"] = df["regime_score"].abs() / 4.0

    return df[["regime", "confidence", "regime_score",
               "ma50", "ma200", "vol_21d", "mom_63d"]].dropna()


def get_current_regime(market_prices: pd.Series) -> dict:
    """Returns current regime info as dict."""
    regimes = detect_regime(market_prices)
    if regimes.empty:
        return {"regime": "Unknown", "confidence": 0}
    latest = regimes.iloc[-1]
    return {
        "regime": latest["regime"],
        "confidence": latest["confidence"],
        "regime_score": latest["regime_score"],
        "volatility": latest["vol_21d"],
        "momentum_3m": latest["mom_63d"],
    }


REGIME_COLORS = {
    "Bull": "#00c853",
    "Sideways": "#ffd600",
    "Bear": "#d50000",
}

REGIME_SECTOR_PREFERENCE = {
    "Bull": ["IT", "Auto", "ConsumerDurables", "Metals"],
    "Sideways": ["FMCG", "Pharma", "Financials"],
    "Bear": ["FMCG", "Pharma", "Telecom"],
}
