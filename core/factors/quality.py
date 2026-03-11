"""
Quality factor: high ROE, low debt, stable earnings.
"""
import pandas as pd
import numpy as np


def compute_quality_scores(fundamentals: dict[str, dict]) -> pd.Series:
    """
    Quality = high ROE + low D/E + high profit margin + earnings growth.
    Returns percentile rank (higher = better quality).
    """
    rows = []
    for sym, f in fundamentals.items():
        rows.append({
            "symbol": sym,
            "roe": f.get("roe"),
            "debt_to_equity": f.get("debt_to_equity"),
            "profit_margin": f.get("profit_margin"),
            "earnings_growth": f.get("earnings_growth"),
            "current_ratio": f.get("current_ratio"),
        })

    df = pd.DataFrame(rows).set_index("symbol")
    df = df.apply(pd.to_numeric, errors="coerce")

    score = pd.Series(0.0, index=df.index)
    n_factors = 0

    if df["roe"].notna().sum() > 2:
        score += df["roe"].rank(pct=True)
        n_factors += 1

    if df["debt_to_equity"].notna().sum() > 2:
        score += (-df["debt_to_equity"]).rank(pct=True)  # lower debt = better
        n_factors += 1

    if df["profit_margin"].notna().sum() > 2:
        score += df["profit_margin"].rank(pct=True)
        n_factors += 1

    if df["earnings_growth"].notna().sum() > 2:
        score += df["earnings_growth"].rank(pct=True)
        n_factors += 1

    if df["current_ratio"].notna().sum() > 2:
        score += df["current_ratio"].rank(pct=True)  # higher liquidity = safer
        n_factors += 1

    if n_factors > 0:
        score /= n_factors

    return score.rename("quality_score")
