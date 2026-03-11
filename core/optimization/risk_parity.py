"""
Risk Parity: allocate so each asset contributes equally to portfolio risk.
"""
import pandas as pd
import numpy as np
from scipy.optimize import minimize


def risk_parity_weights(returns_df: pd.DataFrame) -> dict:
    """
    Compute risk-parity weights.
    Each stock contributes equally to total portfolio volatility.
    """
    cov = returns_df.cov().values * 252
    n = cov.shape[0]
    w0 = np.ones(n) / n

    def risk_contributions(w):
        port_vol = np.sqrt(w @ cov @ w)
        mrc = cov @ w  # marginal risk contribution
        rc = w * mrc / port_vol  # risk contribution
        return rc

    def objective(w):
        rc = risk_contributions(w)
        # Minimize variance of risk contributions
        return np.sum((rc - rc.mean()) ** 2)

    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    bounds = [(0.01, 0.5)] * n

    result = minimize(objective, w0, method="SLSQP",
                      bounds=bounds, constraints=constraints)

    weights = result.x / result.x.sum()
    rc = risk_contributions(weights)
    port_vol = np.sqrt(weights @ cov @ weights)

    return {
        "weights": dict(zip(returns_df.columns, weights)),
        "risk_contributions": dict(zip(returns_df.columns, rc)),
        "portfolio_volatility": port_vol,
        "portfolio_return": (returns_df.mean() * 252).values @ weights,
    }
