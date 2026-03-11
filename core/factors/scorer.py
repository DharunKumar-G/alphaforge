"""
Composite factor scorer — combines momentum, value, quality, volatility.
Main entry point for factor computation.
"""
import pandas as pd
import numpy as np
from loguru import logger

from core.factors.momentum import compute_12_1_momentum
from core.factors.value import compute_value_scores
from core.factors.quality import compute_quality_scores
from core.factors.volatility import compute_volatility_scores
from config.settings import DEFAULT_FACTOR_WEIGHTS


def compute_composite_scores(
    prices: pd.DataFrame,
    fundamentals: dict[str, dict],
    weights: dict[str, float] = None,
) -> pd.DataFrame:
    """
    Main scorer. Combines all factors into one composite score.
    
    Args:
        prices: date × symbol Close prices
        fundamentals: {symbol: fundamental dict}
        weights: factor weights dict (default from settings)
    
    Returns:
        DataFrame with columns: momentum, value, quality, volatility, composite
        Indexed by symbol.
    """
    if weights is None:
        weights = DEFAULT_FACTOR_WEIGHTS

    symbols = list(prices.columns)
    result = pd.DataFrame(index=symbols)

    # --- Momentum ---
    try:
        mom = compute_12_1_momentum(prices)
        result["momentum"] = mom
    except Exception as e:
        logger.warning(f"Momentum failed: {e}")
        result["momentum"] = np.nan

    # --- Value ---
    try:
        val = compute_value_scores(fundamentals)
        result["value"] = val
    except Exception as e:
        logger.warning(f"Value failed: {e}")
        result["value"] = np.nan

    # --- Quality ---
    try:
        qual = compute_quality_scores(fundamentals)
        result["quality"] = qual
    except Exception as e:
        logger.warning(f"Quality failed: {e}")
        result["quality"] = np.nan

    # --- Volatility (low-vol) ---
    try:
        vol = compute_volatility_scores(prices)
        result["volatility"] = vol
    except Exception as e:
        logger.warning(f"Volatility failed: {e}")
        result["volatility"] = np.nan

    # --- Composite ---
    result["composite"] = (
        result["momentum"].fillna(0.5) * weights.get("momentum", 0.25) +
        result["value"].fillna(0.5) * weights.get("value", 0.25) +
        result["quality"].fillna(0.5) * weights.get("quality", 0.25) +
        result["volatility"].fillna(0.5) * weights.get("volatility", 0.25)
    )

    result = result.sort_values("composite", ascending=False)
    logger.info(f"Scores computed for {len(result)} stocks")
    return result


def rank_stocks(scores: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Return top N stocks by composite score."""
    return scores.nlargest(top_n, "composite")


def score_to_signal(score: float) -> str:
    """Convert a 0-1 score to a signal label."""
    if score >= 0.75:
        return "Strong Buy"
    elif score >= 0.55:
        return "Buy"
    elif score >= 0.45:
        return "Neutral"
    elif score >= 0.25:
        return "Sell"
    else:
        return "Strong Sell"
