"""
Value factor: lower PE/PB = better value score.
"""
import pandas as pd
import numpy as np


def compute_value_scores(fundamentals: dict[str, dict]) -> pd.Series:
    """
    Compute value scores from fundamental data.
    Higher score = more undervalued.
    
    Args:
        fundamentals: {symbol: {pe_ratio, pb_ratio, ...}}
    
    Returns:
        Series indexed by symbol, value score (percentile rank)
    """
    rows = []
    for sym, f in fundamentals.items():
        pe = f.get("pe_ratio")
        pb = f.get("pb_ratio")
        div = f.get("dividend_yield") or 0
        rows.append({"symbol": sym, "pe": pe, "pb": pb, "div": div})

    df = pd.DataFrame(rows).set_index("symbol")
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df[df["pe"] > 0]  # remove negative PE (losses)

    score = pd.Series(0.0, index=df.index)

    # Invert PE and PB (lower is better value)
    if "pe" in df.columns and df["pe"].notna().sum() > 2:
        score += (-df["pe"]).rank(pct=True)
    if "pb" in df.columns and df["pb"].notna().sum() > 2:
        score += (-df["pb"]).rank(pct=True)
    # Higher dividend yield = better value
    if "div" in df.columns and df["div"].notna().sum() > 2:
        score += df["div"].rank(pct=True)

    score /= 3
    return score.rename("value_score")


def earnings_yield(pe_ratio: float) -> float:
    """E/P ratio — inverse of PE."""
    if pe_ratio and pe_ratio > 0:
        return 1 / pe_ratio
    return np.nan
