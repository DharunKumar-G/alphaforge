"""
Risk Manager — drawdown alerts, VaR, CVaR, correlation, Monte Carlo.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from data.fetcher import fetch_close_matrix
from core.risk.manager import check_portfolio_risk, compute_var, compute_cvar, max_drawdown_series
from core.risk.monte_carlo import run_monte_carlo, get_probability_cone
from data.universe import get_universe

st.set_page_config(page_title="Risk Manager — AlphaForge", layout="wide")
st.title("Risk Manager")

universe_df = get_universe()
sector_map = dict(zip(universe_df["symbol"], universe_df["sector"]))

# ---- Load from backtest or manual ----
if "backtest_result" in st.session_state:
    result = st.session_state.backtest_result
    returns = result["returns"]
    holdings = result["holdings_history"][-1][1] if result["holdings_history"] else []
    source = "backtest"
else:
    st.info("No backtest loaded. Enter stocks manually.")
    stock_input = st.text_input("Stocks", "HDFCBANK.NS, INFY.NS, RELIANCE.NS, TCS.NS")
    symbols = [s.strip() for s in stock_input.split(",") if s.strip()]
    start = st.date_input("Start", pd.Timestamp("2020-01-01"))
    if st.button("Load"):
        prices = fetch_close_matrix(symbols, start=str(start))
        returns = prices.pct_change().dropna().mean(axis=1)
        holdings = symbols
        st.session_state.risk_returns = returns
        st.session_state.risk_holdings = holdings
    returns = st.session_state.get("risk_returns", pd.Series(dtype=float))
    holdings = st.session_state.get("risk_holdings", [])
    source = "manual"

if returns.empty:
    st.stop()

# ---- Risk Metrics ----
risk = check_portfolio_risk(returns, holdings, sector_map)
alerts = risk.get("alerts", [])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Drawdown", f"{risk.get('current_drawdown', 0):.1%}")
col2.metric("VaR (95%, 1-day)", f"{compute_var(returns, 0.95):.1%}")
col3.metric("CVaR (95%)", f"{compute_cvar(returns, 0.95):.1%}")
col4.metric("Active Alerts", len(alerts))

# ---- Alerts ----
if alerts:
    st.subheader("Risk Alerts")
    for alert in alerts:
        severity = alert.get("severity", "medium")
        if severity == "high":
            st.error(f"🔴 {alert['message']}")
        else:
            st.warning(f"🟡 {alert['message']}")

st.divider()

# ---- Drawdown Chart ----
dd_series = max_drawdown_series(returns)
fig_dd = go.Figure(go.Scatter(
    x=dd_series.index, y=dd_series.values,
    fill="tozeroy", fillcolor="rgba(213,0,0,0.25)",
    line=dict(color="#d50000"),
))
fig_dd.update_layout(title="Drawdown History", yaxis_tickformat=".0%",
                      template="plotly_dark", height=300)
st.plotly_chart(fig_dd, use_container_width=True)

# ---- Sector Breakdown ----
if holdings:
    sector_counts = {}
    for sym in holdings:
        sec = sector_map.get(sym, "Unknown")
        sector_counts[sec] = sector_counts.get(sec, 0) + 1

    st.subheader("Sector Concentration")
    sec_df = pd.DataFrame(list(sector_counts.items()), columns=["Sector", "Count"])
    sec_df["Weight"] = sec_df["Count"] / sec_df["Count"].sum()
    fig_sec = px.bar(sec_df.sort_values("Weight", ascending=False),
                      x="Sector", y="Weight",
                      color="Weight", color_continuous_scale="reds_r",
                      title="Portfolio Sector Weights",
                      template="plotly_dark")
    fig_sec.add_hline(y=0.30, line_dash="dash", line_color="red",
                       annotation_text="30% limit")
    fig_sec.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_sec, use_container_width=True)

# ---- Correlation (if multiple stocks from backtest) ----
if "backtest_result" in st.session_state and holdings:
    st.subheader("Holdings Correlation")
    try:
        prices = fetch_close_matrix(holdings[:15], start="2022-01-01")
        corr_matrix = prices.pct_change().dropna().corr()
        fig_corr = px.imshow(corr_matrix, color_continuous_scale="RdYlGn",
                              zmin=-1, zmax=1,
                              title="Rolling Correlation Heatmap",
                              template="plotly_dark")
        st.plotly_chart(fig_corr, use_container_width=True)

        # High correlation pairs
        high_corr = []
        for i in range(len(corr_matrix)):
            for j in range(i + 1, len(corr_matrix)):
                c = corr_matrix.iloc[i, j]
                if abs(c) > 0.8:
                    high_corr.append({
                        "Stock A": corr_matrix.index[i],
                        "Stock B": corr_matrix.columns[j],
                        "Correlation": round(c, 3),
                    })
        if high_corr:
            st.warning(f"{len(high_corr)} highly correlated pairs (>0.8):")
            st.dataframe(pd.DataFrame(high_corr), use_container_width=True)
    except Exception as e:
        st.info(f"Correlation unavailable: {e}")
