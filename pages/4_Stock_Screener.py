"""
Stock Screener — natural language + manual filter modes.
"""
import streamlit as st
import pandas as pd

from data.universe import get_universe, get_symbols
from data.fetcher import fetch_close_matrix, fetch_fundamentals
from core.factors.scorer import compute_composite_scores, score_to_signal
from ai.nl_screener import parse_query_to_filters, refine_filters, apply_filters
from config.settings import DEFAULT_FACTOR_WEIGHTS

st.set_page_config(page_title="Stock Screener — AlphaForge", layout="wide")
st.title("Stock Screener")

tab_nl, tab_manual = st.tabs(["Natural Language Screen", "Manual Filters"])

universe_df = get_universe()

@st.cache_data(ttl=3600, show_spinner="Loading factor scores...")
def load_scores():
    symbols = get_symbols()[:50]
    prices = fetch_close_matrix(symbols, start="2020-01-01")
    fundamentals = {}
    for sym in symbols[:30]:
        f = fetch_fundamentals(sym)
        if f:
            fundamentals[sym] = f
    scores = compute_composite_scores(prices, fundamentals, DEFAULT_FACTOR_WEIGHTS)
    return scores, fundamentals

scores, fundamentals = load_scores()

# ---- Natural Language Tab ----
with tab_nl:
    st.subheader("Describe the stocks you're looking for")

    example_queries = [
        "undervalued banking stocks with strong momentum",
        "high quality IT companies with low debt",
        "FMCG stocks with above average dividend yield",
        "pharma stocks with momentum above 0.7",
    ]
    example = st.selectbox("Try an example", [""] + example_queries)
    query = st.text_input("Your query", value=example,
                           placeholder="e.g. find me high quality stocks with low volatility in auto sector")

    col1, col2 = st.columns([1, 4])
    with col1:
        run_nl = st.button("Screen", type="primary")
    with col2:
        if "nl_filters" in st.session_state:
            followup = st.text_input("Refine results",
                                      placeholder="e.g. remove anything with PE > 40")
            if st.button("Refine"):
                st.session_state.nl_filters = refine_filters(
                    st.session_state.nl_filters, followup)

    if run_nl and query:
        with st.spinner("Parsing query with AI..."):
            filters = parse_query_to_filters(query)
            st.session_state.nl_filters = filters

    if "nl_filters" in st.session_state:
        filters = st.session_state.nl_filters
        st.caption("Parsed filters:")
        st.json(filters)

        results = apply_filters(scores, fundamentals, filters)

        if results.empty:
            st.warning("No stocks matched. Try relaxing the filters.")
        else:
            results["signal"] = results["composite"].apply(score_to_signal)
            st.dataframe(results[["momentum", "value", "quality", "volatility",
                                   "composite", "signal"]].round(3),
                         use_container_width=True)
            st.caption(f"{len(results)} stocks found")

# ---- Manual Filter Tab ----
with tab_manual:
    st.subheader("Filter by factor score thresholds")

    col1, col2 = st.columns(2)
    with col1:
        min_momentum = st.slider("Min Momentum Score", 0.0, 1.0, 0.0, 0.05)
        min_value = st.slider("Min Value Score", 0.0, 1.0, 0.0, 0.05)
        sectors = ["All"] + sorted(universe_df["sector"].unique().tolist())
        sel_sector = st.selectbox("Sector", sectors)
    with col2:
        min_quality = st.slider("Min Quality Score", 0.0, 1.0, 0.0, 0.05)
        min_composite = st.slider("Min Composite Score", 0.0, 1.0, 0.5, 0.05)
        top_n = st.slider("Top N Results", 5, 50, 20)

    filtered = scores.copy()
    filtered = filtered[filtered["momentum"] >= min_momentum]
    filtered = filtered[filtered["value"] >= min_value]
    filtered = filtered[filtered["quality"] >= min_quality]
    filtered = filtered[filtered["composite"] >= min_composite]
    filtered = filtered.nlargest(top_n, "composite")
    filtered["signal"] = filtered["composite"].apply(score_to_signal)

    st.dataframe(filtered[["momentum", "value", "quality", "volatility",
                             "composite", "signal"]].round(3),
                 use_container_width=True)
    st.caption(f"{len(filtered)} stocks found")
