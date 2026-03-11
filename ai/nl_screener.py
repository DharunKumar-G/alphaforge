"""
Natural Language Stock Screener — parses user query into factor filters via Claude.
"""
import json
from ai.client import chat
from ai.prompts.screener import SCREENER_SYSTEM, SCREENER_FOLLOWUP_SYSTEM


def parse_query_to_filters(query: str) -> dict:
    """
    Convert natural language query to structured filter dict.
    Example: "undervalued banking stocks with strong momentum"
    → {"sectors": ["Banks"], "min_momentum_score": 0.7, "max_value_score": 0.3}
    """
    response = chat(SCREENER_SYSTEM, query, max_tokens=512)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from response
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {}


def refine_filters(current_filters: dict, follow_up: str) -> dict:
    """Refine existing filters with a follow-up instruction."""
    user_msg = f"Current filters: {json.dumps(current_filters)}\nNew instruction: {follow_up}"
    response = chat(SCREENER_FOLLOWUP_SYSTEM, user_msg, max_tokens=512)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return current_filters


def apply_filters(scores_df, fundamentals: dict, filters: dict):
    """
    Apply filter dict to scores DataFrame.
    scores_df must have columns: momentum, value, quality, volatility, composite
    """
    df = scores_df.copy()

    for factor in ["momentum", "value", "quality", "volatility", "composite"]:
        min_key = f"min_{factor}_score"
        max_key = f"max_{factor}_score"
        if filters.get(min_key) is not None:
            df = df[df[factor] >= filters[min_key]]
        if filters.get(max_key) is not None:
            df = df[df[factor] <= filters[max_key]]

    # Fundamental filters
    if filters.get("max_pe") or filters.get("min_roe") or filters.get("max_debt_equity"):
        fund_rows = []
        for sym, f in fundamentals.items():
            ok = True
            if filters.get("max_pe") and f.get("pe_ratio"):
                ok = ok and f["pe_ratio"] <= filters["max_pe"]
            if filters.get("min_roe") and f.get("roe"):
                ok = ok and f["roe"] >= filters["min_roe"]
            if filters.get("max_debt_equity") and f.get("debt_to_equity"):
                ok = ok and f["debt_to_equity"] <= filters["max_debt_equity"]
            if ok:
                fund_rows.append(sym)
        df = df[df.index.isin(fund_rows)]

    # Sort
    sort_by = filters.get("sort_by", "composite")
    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=False)

    top_n = filters.get("top_n", 20)
    return df.head(top_n)
