"""
Monte Carlo simulation for portfolio return distribution.
"""
import pandas as pd
import numpy as np


def run_monte_carlo(returns: pd.Series, n_simulations: int = 1000,
                    n_days: int = 252) -> pd.DataFrame:
    """
    Run Monte Carlo simulation using historical return bootstrapping.
    
    Returns:
        DataFrame of shape (n_days, n_simulations) — cumulative return paths
    """
    mu = returns.mean()
    sigma = returns.std()

    paths = np.zeros((n_days, n_simulations))
    for i in range(n_simulations):
        daily = np.random.normal(mu, sigma, n_days)
        paths[:, i] = (1 + daily).cumprod() - 1

    return pd.DataFrame(paths)


def get_probability_cone(paths: pd.DataFrame) -> dict:
    """
    Compute percentile bands for the probability cone.
    Returns dict with p5, p25, p50, p75, p95 series.
    """
    return {
        "p5": paths.quantile(0.05, axis=1),
        "p25": paths.quantile(0.25, axis=1),
        "p50": paths.quantile(0.50, axis=1),
        "p75": paths.quantile(0.75, axis=1),
        "p95": paths.quantile(0.95, axis=1),
    }


def monte_carlo_var(returns: pd.Series, confidence: float = 0.95,
                    n_simulations: int = 10000, horizon: int = 21) -> dict:
    """
    Monte Carlo VaR over a given horizon.
    """
    paths = run_monte_carlo(returns, n_simulations=n_simulations, n_days=horizon)
    terminal = paths.iloc[-1]
    var = -terminal.quantile(1 - confidence)
    cvar = -terminal[terminal < -var].mean()
    prob_loss = (terminal < 0).mean()

    return {
        "var": var,
        "cvar": cvar,
        "prob_loss": prob_loss,
        "expected_return": terminal.mean(),
        "best_case_95": terminal.quantile(0.95),
        "worst_case_5": terminal.quantile(0.05),
    }
