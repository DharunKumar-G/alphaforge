"""
Performance metrics for backtest results.
"""
import pandas as pd
import numpy as np
from config.settings import DEFAULT_START_DATE


def compute_metrics(returns: pd.Series, benchmark: pd.Series = None,
                    risk_free: float = 0.065) -> dict:
    """
    Compute full set of performance metrics.
    
    Args:
        returns: daily portfolio return series
        benchmark: daily benchmark return series
        risk_free: annual risk-free rate (India: ~6.5%)
    
    Returns:
        dict of metric name → value
    """
    if returns.empty:
        return {}

    returns = returns.dropna()
    n_days = len(returns)
    n_years = n_days / 252

    cumulative = (1 + returns).cumprod()
    total_return = cumulative.iloc[-1] - 1
    cagr = (cumulative.iloc[-1]) ** (1 / n_years) - 1 if n_years > 0 else 0

    # Volatility
    ann_vol = returns.std() * np.sqrt(252)

    # Sharpe
    daily_rf = risk_free / 252
    sharpe = ((returns.mean() - daily_rf) / returns.std() * np.sqrt(252)
              if returns.std() > 0 else 0)

    # Sortino (downside deviation)
    downside_returns = returns[returns < 0]
    downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 1
    sortino = (cagr - risk_free) / downside_std if downside_std > 0 else 0

    # Max drawdown
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_dd = drawdown.min()

    # Calmar
    calmar = cagr / abs(max_dd) if max_dd != 0 else 0

    # Win rate
    win_rate = (returns > 0).mean()

    # Monthly returns
    monthly = returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    best_month = monthly.max()
    worst_month = monthly.min()

    metrics = {
        "total_return": total_return,
        "cagr": cagr,
        "ann_volatility": ann_vol,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": max_dd,
        "calmar": calmar,
        "win_rate": win_rate,
        "best_month": best_month,
        "worst_month": worst_month,
        "n_days": n_days,
    }

    # Alpha / Beta vs benchmark
    if benchmark is not None and not benchmark.empty:
        bench = benchmark.reindex(returns.index).fillna(0)
        cov_matrix = np.cov(returns.values, bench.values)
        beta = cov_matrix[0, 1] / cov_matrix[1, 1] if cov_matrix[1, 1] != 0 else 1
        alpha = cagr - (risk_free + beta * (bench.mean() * 252 - risk_free))
        bench_cagr = (1 + bench).cumprod().iloc[-1] ** (1 / n_years) - 1
        excess_return = cagr - bench_cagr

        # Information ratio
        active_returns = returns.values - bench.values
        ir = (active_returns.mean() / active_returns.std() * np.sqrt(252)
              if active_returns.std() > 0 else 0)

        metrics.update({
            "alpha": alpha,
            "beta": beta,
            "benchmark_cagr": bench_cagr,
            "excess_return": excess_return,
            "information_ratio": ir,
        })

    return metrics


def rolling_metrics(returns: pd.Series, window: int = 252) -> pd.DataFrame:
    """Rolling 1-year Sharpe and volatility."""
    rf_daily = 0.065 / 252
    rolling_sharpe = (
        (returns - rf_daily).rolling(window).mean() /
        returns.rolling(window).std() * np.sqrt(252)
    )
    rolling_vol = returns.rolling(window).std() * np.sqrt(252)
    rolling_return = returns.rolling(window).apply(lambda x: (1 + x).prod() - 1)

    return pd.DataFrame({
        "rolling_sharpe": rolling_sharpe,
        "rolling_volatility": rolling_vol,
        "rolling_return": rolling_return,
    })


def monthly_returns_table(returns: pd.Series) -> pd.DataFrame:
    """Pivot table: Year × Month with monthly returns."""
    monthly = returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    df = pd.DataFrame({
        "year": monthly.index.year,
        "month": monthly.index.strftime("%b"),
        "return": monthly.values,
    })
    pivot = df.pivot(index="year", columns="month", values="return")
    # Add annual column
    annual = returns.resample("YE").apply(lambda x: (1 + x).prod() - 1)
    pivot["Annual"] = annual.values[:len(pivot)]
    return pivot
