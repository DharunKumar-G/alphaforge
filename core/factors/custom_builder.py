"""
Custom Factor Builder — user defines formula, system evaluates and backtests it.
"""
import pandas as pd
import numpy as np
from loguru import logger


AVAILABLE_SIGNALS = {
    "momentum": "12-1 month momentum score (percentile)",
    "value": "Value score (lower PE/PB = higher score)",
    "quality": "Quality score (high ROE, low debt)",
    "volatility": "Low-volatility score (lower vol = higher score)",
    "pe_ratio": "Price-to-Earnings ratio",
    "pb_ratio": "Price-to-Book ratio",
    "roe": "Return on Equity",
    "debt_to_equity": "Debt-to-Equity ratio",
    "profit_margin": "Profit margin",
    "momentum_1m": "1-month return",
    "momentum_3m": "3-month return",
    "momentum_6m": "6-month return",
}


def evaluate_custom_formula(formula: str, scores: pd.DataFrame,
                             fundamentals: dict[str, dict]) -> pd.Series:
    """
    Evaluate a user-defined factor formula.
    
    Example formulas:
        "momentum * 0.5 + quality * 0.5"
        "momentum * 0.3 + value * 0.4 + quality * 0.3"
        "(roe * 0.5) + (momentum * 0.3) - (debt_to_equity * 0.2)"
    
    Args:
        formula: string formula using signal names
        scores: DataFrame with precomputed factor scores (index = symbol)
        fundamentals: dict of {symbol: fundamental_dict}
    
    Returns:
        Series of custom factor scores indexed by symbol
    """
    # Build eval namespace per symbol
    results = {}
    for sym in scores.index:
        fund = fundamentals.get(sym, {})
        namespace = {}

        # Add factor scores
        for col in scores.columns:
            val = scores.loc[sym, col]
            namespace[col] = val if pd.notna(val) else 0.0

        # Add fundamentals
        for k, v in fund.items():
            if v is not None:
                namespace[k.replace("-", "_")] = float(v)

        # Safe eval
        try:
            result = eval(formula, {"__builtins__": {}}, namespace)
            results[sym] = float(result)
        except Exception as e:
            results[sym] = np.nan

    series = pd.Series(results, name="custom_factor")
    # Normalize to 0-1 percentile
    return series.rank(pct=True).rename("custom_factor")


def validate_formula(formula: str, scores: pd.DataFrame,
                     fundamentals: dict) -> tuple[bool, str]:
    """
    Validate a formula before running. Returns (is_valid, error_message).
    """
    if not formula.strip():
        return False, "Formula is empty"

    # Security check — block dangerous keywords
    blocked = ["import", "exec", "open", "os.", "sys.", "__"]
    for b in blocked:
        if b in formula:
            return False, f"Blocked keyword: '{b}'"

    # Test on first symbol
    if scores.empty:
        return False, "No scores available to validate against"

    sym = scores.index[0]
    fund = fundamentals.get(sym, {})
    namespace = {}
    for col in scores.columns:
        namespace[col] = 0.5
    for k, v in fund.items():
        if v is not None:
            namespace[k.replace("-", "_")] = float(v) if v else 0.0

    try:
        eval(formula, {"__builtins__": {}}, namespace)
        return True, "Valid"
    except Exception as e:
        return False, str(e)
