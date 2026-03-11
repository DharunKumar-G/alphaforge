"""
Risk management: drawdown monitoring, position limits, alerts.
"""
import pandas as pd
import numpy as np
from config.settings import MAX_DRAWDOWN_ALERT, MAX_SINGLE_STOCK_WEIGHT, MAX_SECTOR_WEIGHT


def check_portfolio_risk(returns: pd.Series, holdings: list[str],
                         sector_map: dict[str, str]) -> dict:
    """
    Run full risk check on current portfolio.
    Returns dict with risk flags and metrics.
    """
    alerts = []
    metrics = {}

    # Drawdown check
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    current_dd = ((cumulative.iloc[-1] - rolling_max.iloc[-1]) / rolling_max.iloc[-1])
    metrics["current_drawdown"] = current_dd

    if abs(current_dd) >= MAX_DRAWDOWN_ALERT:
        alerts.append({
            "type": "drawdown",
            "severity": "high",
            "message": f"Portfolio in {current_dd:.1%} drawdown (threshold: {MAX_DRAWDOWN_ALERT:.0%})",
        })

    # Concentration check
    n = len(holdings)
    if n > 0:
        equal_weight = 1 / n
        if equal_weight > MAX_SINGLE_STOCK_WEIGHT:
            alerts.append({
                "type": "concentration",
                "severity": "medium",
                "message": f"High concentration: {n} stocks means {equal_weight:.0%} per stock",
            })

    # Sector concentration
    if sector_map and holdings:
        sector_counts = {}
        for sym in holdings:
            sec = sector_map.get(sym, "Unknown")
            sector_counts[sec] = sector_counts.get(sec, 0) + 1

        for sec, count in sector_counts.items():
            weight = count / len(holdings)
            if weight > MAX_SECTOR_WEIGHT:
                alerts.append({
                    "type": "sector_concentration",
                    "severity": "medium",
                    "message": f"{sec} sector: {weight:.0%} of portfolio (limit: {MAX_SECTOR_WEIGHT:.0%})",
                })

    metrics["n_stocks"] = n
    metrics["sector_breakdown"] = sector_counts if sector_map and holdings else {}
    metrics["alerts"] = alerts
    metrics["risk_score"] = len(alerts)

    return metrics


def compute_var(returns: pd.Series, confidence: float = 0.95,
                horizon: int = 1) -> float:
    """
    Historical VaR at given confidence level.
    Returns the loss (positive number) at the confidence level.
    """
    if returns.empty:
        return 0
    return -np.percentile(returns, (1 - confidence) * 100) * np.sqrt(horizon)


def compute_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """Expected Shortfall (CVaR) — average loss beyond VaR."""
    var = compute_var(returns, confidence)
    tail_returns = returns[returns < -var]
    return -tail_returns.mean() if not tail_returns.empty else var


def max_drawdown_series(returns: pd.Series) -> pd.Series:
    """Return rolling max drawdown series."""
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    return (cumulative - rolling_max) / rolling_max
