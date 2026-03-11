"""
Backtesting engine — factor-based portfolio simulation.
Walk-forward: each rebalance date, score stocks, pick top N, hold till next rebalance.
"""
import pandas as pd
import numpy as np
from loguru import logger
from datetime import datetime

from data.fetcher import fetch_close_matrix, fetch_fundamentals
from core.factors.scorer import compute_composite_scores, rank_stocks
from core.backtesting.performance import compute_metrics
from config.settings import DEFAULT_FACTOR_WEIGHTS, DEFAULT_REBALANCE_FREQ, TOP_N_STOCKS


REBALANCE_OFFSETS = {
    "monthly": "MS",    # Month start
    "weekly": "W-MON",
    "quarterly": "QS",
    "daily": "B",
}


def run_backtest(
    symbols: list[str],
    start: str = "2018-01-01",
    end: str = None,
    top_n: int = TOP_N_STOCKS,
    weights: dict = None,
    rebalance_freq: str = DEFAULT_REBALANCE_FREQ,
    benchmark_symbol: str = "^NSEI",
    equal_weight: bool = True,
) -> dict:
    """
    Run a full factor backtest.
    
    Returns dict with:
        - returns: pd.Series of daily portfolio returns
        - benchmark_returns: pd.Series of benchmark returns
        - holdings_history: list of (date, [symbols]) tuples
        - scores_history: list of (date, DataFrame) tuples
        - metrics: performance metrics dict
    """
    if end is None:
        end = datetime.today().strftime("%Y-%m-%d")
    if weights is None:
        weights = DEFAULT_FACTOR_WEIGHTS

    logger.info(f"Backtest: {len(symbols)} stocks, {start} → {end}, top {top_n}, {rebalance_freq}")

    # --- Fetch all price data ---
    logger.info("Fetching price data...")
    all_symbols = symbols + [benchmark_symbol]
    prices = fetch_close_matrix(all_symbols, start=start, end=end)

    benchmark_prices = prices.get(benchmark_symbol, pd.Series(dtype=float))
    stock_prices = prices.drop(columns=[benchmark_symbol], errors="ignore")

    # --- Rebalance dates ---
    offset = REBALANCE_OFFSETS.get(rebalance_freq, "MS")
    rebalance_dates = pd.date_range(start=start, end=end, freq=offset)
    rebalance_dates = [d for d in rebalance_dates if d in stock_prices.index or
                       stock_prices.index[stock_prices.index.searchsorted(d) - 1] is not None]

    # --- Fetch fundamentals (once, for now) ---
    logger.info("Fetching fundamentals...")
    fundamentals = {}
    for sym in symbols[:40]:  # limit to avoid rate limits
        f = fetch_fundamentals(sym)
        if f:
            fundamentals[sym] = f

    # --- Walk-forward simulation ---
    portfolio_returns = pd.Series(dtype=float)
    holdings_history = []
    scores_history = []
    current_holdings = []

    all_dates = stock_prices.index
    prev_rebal = None

    for i, rebal_date in enumerate(rebalance_dates):
        # Get prices up to this date
        hist_prices = stock_prices[stock_prices.index <= rebal_date].copy()
        if len(hist_prices) < 252:
            continue  # need at least 1 year of history

        # Score stocks
        try:
            scores = compute_composite_scores(hist_prices, fundamentals, weights)
            top_stocks = rank_stocks(scores, top_n=top_n)
            current_holdings = top_stocks.index.tolist()
            holdings_history.append((rebal_date, current_holdings.copy()))
            scores_history.append((rebal_date, scores.copy()))
        except Exception as e:
            logger.warning(f"Scoring failed at {rebal_date}: {e}")
            continue

        # Calculate returns from this rebalance to next
        next_rebal = rebalance_dates[i + 1] if i + 1 < len(rebalance_dates) else pd.Timestamp(end)
        period_mask = (all_dates > rebal_date) & (all_dates <= next_rebal)
        period_dates = all_dates[period_mask]

        if len(period_dates) == 0:
            continue

        period_prices = stock_prices.loc[period_dates, current_holdings].copy()
        period_prices = period_prices.dropna(axis=1, how="all")

        if period_prices.empty:
            continue

        # Equal-weight portfolio daily returns
        period_rets = period_prices.pct_change().dropna(how="all")
        port_ret = period_rets.mean(axis=1)
        portfolio_returns = pd.concat([portfolio_returns, port_ret])

    portfolio_returns = portfolio_returns.sort_index()
    portfolio_returns = portfolio_returns[~portfolio_returns.index.duplicated(keep="first")]

    # Benchmark returns
    if not benchmark_prices.empty:
        bench_rets = benchmark_prices.pct_change().reindex(portfolio_returns.index).fillna(0)
    else:
        bench_rets = pd.Series(0, index=portfolio_returns.index)

    # Metrics
    metrics = compute_metrics(portfolio_returns, bench_rets)

    logger.info(f"Backtest complete. Sharpe: {metrics.get('sharpe', 0):.2f}, "
                f"CAGR: {metrics.get('cagr', 0):.1%}")

    return {
        "returns": portfolio_returns,
        "benchmark_returns": bench_rets,
        "holdings_history": holdings_history,
        "scores_history": scores_history,
        "metrics": metrics,
        "start": start,
        "end": end,
        "top_n": top_n,
        "rebalance_freq": rebalance_freq,
        "factor_weights": weights,
    }
