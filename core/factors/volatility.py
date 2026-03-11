"""
Volatility factor: lower volatility = higher score (low-vol premium).
"""
import pandas as pd
import numpy as np


def compute_volatility_scores(prices: pd.DataFrame, window: int = 63) -> pd.Series:
    """
    Compute low-volatility scores. Lower realized vol → higher score.
    
    Args:
        prices: date × symbol Close price DataFrame
        window: rolling window in trading days
    
    Returns:
        Series of volatility scores (percentile rank, higher = lower vol)
    """
    returns = prices.pct_change()
    vol = returns.rolling(window).std() * np.sqrt(252)
    latest_vol = vol.iloc[-1].dropna()
    # Invert: low vol stocks get high score
    score = (-latest_vol).rank(pct=True)
    return score.rename("volatility_score")


def compute_beta(stock_returns: pd.Series, market_returns: pd.Series,
                 window: int = 252) -> pd.Series:
    """Rolling beta of stock vs market."""
    cov = stock_returns.rolling(window).cov(market_returns)
    var = market_returns.rolling(window).var()
    return cov / var


def compute_max_drawdown(returns: pd.Series) -> float:
    """Maximum drawdown from a return series."""
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    return drawdown.min()


def compute_sharpe(returns: pd.Series, risk_free: float = 0.065) -> float:
    """Annualized Sharpe ratio. India risk-free ~6.5%."""
    excess = returns - risk_free / 252
    if returns.std() == 0:
        return 0
    return (excess.mean() / returns.std()) * np.sqrt(252)
