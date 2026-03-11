"""
Momentum factor calculations.
Uses price momentum over multiple lookback windows.
"""
import pandas as pd
import numpy as np


def compute_momentum(prices: pd.DataFrame, windows: list[int] = [21, 63, 126, 252]) -> pd.DataFrame:
    """
    Compute momentum scores for each stock.
    
    Args:
        prices: DataFrame with date index, symbol columns (Close prices)
        windows: Lookback periods in trading days
    
    Returns:
        DataFrame with same shape as prices, momentum scores (z-scored)
    """
    scores = pd.DataFrame(index=prices.index, columns=prices.columns, dtype=float)

    for window in windows:
        # Return over window, skip last month (t-1 month to avoid reversal)
        skip = 21
        ret = prices.shift(skip).pct_change(window - skip)
        scores += ret

    scores /= len(windows)

    # Cross-sectional z-score at each date
    scores = scores.apply(lambda row: _zscore(row), axis=1)
    return scores


def compute_12_1_momentum(prices: pd.DataFrame) -> pd.Series:
    """
    Classic 12-1 momentum: 12-month return excluding last month.
    Returns cross-sectional rank (0 to 1) at the latest date.
    """
    ret_12m = prices.pct_change(252)
    ret_1m = prices.pct_change(21)
    momentum = ret_12m - ret_1m  # subtract recent reversal
    latest = momentum.iloc[-1].dropna()
    return latest.rank(pct=True)


def compute_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """RSI for a single stock price series."""
    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _zscore(row: pd.Series) -> pd.Series:
    mean = row.mean()
    std = row.std()
    if std == 0 or pd.isna(std):
        return row * 0
    return (row - mean) / std
