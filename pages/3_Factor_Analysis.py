"""
Factor Analysis — deep dive into each factor, decay analysis, cross-sectional spreads.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from data.fetcher import fetch_close_matrix, fetch_fundamentals
from data.universe import get_symbols, get_sectors
from core.factors.momentum import compute_12_1_momentum
from core.factors.volatility import compute_volatility_scores, compute_sharpe
from core.factors.scorer import compute_composite_scores
from config.settings import DEFAULT_FACTOR_WEIGHTS

st.set_page_config(page_title="Factor Analysis — AlphaForge", layout="wide")
st.title("Factor Analysis")

with st.sidebar:
    sectors = ["All"] + get_sectors()
    sector = st.selectbox("Sector", sectors)
    start = st.date_input("Start", pd.Timestamp("2018-01-01"))
    n_stocks = st.slider("Max Stocks", 20, 80, 40)
    compute_btn = st.button("Compute", type="primary", use_container_width=True)

@st.cache_data(ttl=3600)
def load_factor_data(sector, start, n):
    if sector == "All":
        symbols = get_symbols()[:n]
    else:
        symbols = get_symbols(sector=sector)[:n]
    prices = fetch_close_matrix(symbols, start=str(start))
    fundamentals = {}
    for sym in symbols[:30]:
        f = fetch_fundamentals(sym)
        if f:
            fundamentals[sym] = f
    scores = compute_composite_scores(prices, fundamentals, DEFAULT_FACTOR_WEIGHTS)
    return scores, prices, fundamentals

if compute_btn or "factor_scores" not in st.session_state:
    with st.spinner("Computing factor data..."):
        scores, prices, fundamentals = load_factor_data(sector, start, n_stocks)
        st.session_state.factor_scores = scores
        st.session_state.factor_prices = prices

scores = st.session_state.factor_scores
prices = st.session_state.factor_prices

tab1, tab2, tab3, tab4 = st.tabs(["Score Distribution", "Factor Spreads", "Momentum Deep Dive", "Factor Decay"])

with tab1:
    st.subheader("Factor Score Distribution")
    for factor in ["momentum", "value", "quality", "volatility", "composite"]:
        if factor in scores.columns:
            fig = px.histogram(scores, x=factor, nbins=20,
                               title=f"{factor.title()} Score Distribution",
                               template="plotly_dark", color_discrete_sequence=["#00c853"])
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Top vs Bottom Quintile Spread")
    for factor in ["momentum", "value", "quality", "volatility"]:
        if factor not in scores.columns:
            continue
        top20 = scores.nlargest(max(1, len(scores)//5), factor)
        bot20 = scores.nsmallest(max(1, len(scores)//5), factor)
        spread = top20[factor].mean() - bot20[factor].mean()
        col1, col2, col3 = st.columns(3)
        col1.metric(f"{factor.title()} — Top Q", f"{top20[factor].mean():.3f}")
        col2.metric(f"{factor.title()} — Bot Q", f"{bot20[factor].mean():.3f}")
        col3.metric("Spread", f"{spread:.3f}")

    # Scatter: Momentum vs Value
    if "momentum" in scores.columns and "value" in scores.columns:
        fig_scatter = px.scatter(scores.reset_index(), x="momentum", y="value",
                                  color="composite", size="composite",
                                  hover_name="index" if "index" in scores.reset_index().columns else None,
                                  color_continuous_scale="Greens",
                                  title="Momentum vs Value Score",
                                  template="plotly_dark")
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.subheader("Momentum Deep Dive")
    if not prices.empty:
        mom_12_1 = compute_12_1_momentum(prices)
        vol_scores = compute_volatility_scores(prices)

        top_mom = mom_12_1.nlargest(10)
        bot_mom = mom_12_1.nsmallest(10)

        col1, col2 = st.columns(2)
        with col1:
            st.caption("Top 10 Momentum Stocks")
            st.dataframe(top_mom.rename("12-1 Momentum").to_frame().style.format("{:.3f}"),
                         use_container_width=True)
        with col2:
            st.caption("Bottom 10 Momentum Stocks")
            st.dataframe(bot_mom.rename("12-1 Momentum").to_frame().style.format("{:.3f}"),
                         use_container_width=True)

        # Rolling momentum chart for selected stock
        selected = st.selectbox("Select stock to analyze momentum trend",
                                 [s for s in prices.columns if s in mom_12_1.index])
        if selected:
            stock_prices = prices[selected]
            rolling_mom = stock_prices.pct_change(252).dropna()
            fig_mom = go.Figure()
            fig_mom.add_trace(go.Scatter(x=rolling_mom.index, y=rolling_mom.values,
                                          mode="lines", name="12M Momentum",
                                          line=dict(color="#00c853")))
            fig_mom.add_hline(y=0, line_dash="dash", line_color="#888")
            fig_mom.update_layout(title=f"{selected} — 12-Month Rolling Momentum",
                                   yaxis_tickformat=".0%", template="plotly_dark", height=350)
            st.plotly_chart(fig_mom, use_container_width=True)

with tab4:
    st.subheader("Factor Decay Analysis")
    st.caption("Tracks rolling factor effectiveness over time — early warning for factor crowding.")

    if "backtest_result" in st.session_state:
        scores_history = st.session_state.backtest_result.get("scores_history", [])
        if scores_history:
            # Track top-quintile momentum performance over time
            decay_rows = []
            for date, sc in scores_history:
                if "composite" in sc.columns:
                    top_n = sc.nlargest(max(1, len(sc)//5), "composite")
                    decay_rows.append({
                        "date": date,
                        "avg_composite": top_n["composite"].mean(),
                        "avg_momentum": top_n["momentum"].mean() if "momentum" in sc.columns else None,
                    })

            if decay_rows:
                decay_df = pd.DataFrame(decay_rows)
                fig_decay = px.line(decay_df, x="date", y="avg_composite",
                                     title="Composite Score of Top Quintile (Factor Effectiveness)",
                                     template="plotly_dark")
                st.plotly_chart(fig_decay, use_container_width=True)

                # Trend signal
                if len(decay_df) >= 3:
                    trend = decay_df["avg_composite"].iloc[-1] - decay_df["avg_composite"].iloc[-3]
                    if trend < -0.05:
                        st.warning(f"Factor effectiveness declining: {trend:.3f} over last 3 periods. "
                                   "Consider reducing factor weights or investigating crowding.")
                    else:
                        st.success("Factor effectiveness stable or improving.")
    else:
        st.info("Run a backtest to enable factor decay analysis.")
