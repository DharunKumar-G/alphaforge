"""
Mean-Variance Optimization (Markowitz) and related portfolio construction.
"""
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from loguru import logger


def compute_efficient_frontier(returns_df: pd.DataFrame,
                                n_points: int = 50) -> pd.DataFrame:
    """
    Compute efficient frontier portfolios.
    
    Args:
        returns_df: DataFrame of daily returns (date × symbol)
        n_points: number of target return points
    
    Returns:
        DataFrame with columns: return, volatility, sharpe, weights_*
    """
    mu = returns_df.mean() * 252
    cov = returns_df.cov() * 252
    n = len(mu)

    target_returns = np.linspace(mu.min(), mu.max(), n_points)
    results = []

    for target in target_returns:
        weights = _min_variance_for_target(mu.values, cov.values, target)
        if weights is None:
            continue
        port_ret = mu.values @ weights
        port_vol = np.sqrt(weights @ cov.values @ weights)
        sharpe = (port_ret - 0.065) / port_vol if port_vol > 0 else 0
        row = {"return": port_ret, "volatility": port_vol, "sharpe": sharpe}
        for sym, w in zip(returns_df.columns, weights):
            row[f"w_{sym}"] = w
        results.append(row)

    return pd.DataFrame(results)


def max_sharpe_portfolio(returns_df: pd.DataFrame,
                          risk_free: float = 0.065) -> dict:
    """Find portfolio with maximum Sharpe ratio."""
    mu = returns_df.mean() * 252
    cov = returns_df.cov() * 252
    n = len(mu)

    def neg_sharpe(w):
        ret = mu.values @ w
        vol = np.sqrt(w @ cov.values @ w)
        return -(ret - risk_free) / vol if vol > 0 else 0

    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    bounds = [(0, 0.25)] * n  # max 25% per stock
    w0 = np.ones(n) / n

    result = minimize(neg_sharpe, w0, method="SLSQP",
                      bounds=bounds, constraints=constraints)

    weights = result.x
    ret = mu.values @ weights
    vol = np.sqrt(weights @ cov.values @ weights)

    return {
        "weights": dict(zip(returns_df.columns, weights)),
        "return": ret,
        "volatility": vol,
        "sharpe": (ret - risk_free) / vol,
    }


def min_variance_portfolio(returns_df: pd.DataFrame) -> dict:
    """Find minimum variance portfolio."""
    mu = returns_df.mean() * 252
    cov = returns_df.cov() * 252
    n = len(mu)

    def port_variance(w):
        return w @ cov.values @ w

    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    bounds = [(0, 0.25)] * n
    w0 = np.ones(n) / n

    result = minimize(port_variance, w0, method="SLSQP",
                      bounds=bounds, constraints=constraints)
    weights = result.x
    vol = np.sqrt(weights @ cov.values @ weights)
    ret = mu.values @ weights

    return {
        "weights": dict(zip(returns_df.columns, weights)),
        "return": ret,
        "volatility": vol,
        "sharpe": (ret - 0.065) / vol,
    }


def _min_variance_for_target(mu, cov, target_return):
    n = len(mu)
    constraints = [
        {"type": "eq", "fun": lambda w: w.sum() - 1},
        {"type": "eq", "fun": lambda w: mu @ w - target_return},
    ]
    bounds = [(0, 1)] * n
    w0 = np.ones(n) / n
    result = minimize(lambda w: w @ cov @ w, w0, method="SLSQP",
                      bounds=bounds, constraints=constraints)
    return result.x if result.success else None
