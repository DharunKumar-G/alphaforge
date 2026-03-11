"""
Backtester — run factor backtest, view performance, export results.
"""
import streamlit as st
import pandas as pd
import json

from data.universe import get_symbols, get_sectors
from core.backtesting.engine import run_backtest
from core.backtesting.performance import monthly_returns_table, rolling_metrics
from components.equity_curve import plot_equity_curve, plot_drawdown, plot_monthly_heatmap
from components.radar_chart import plot_factor_radar
from config.settings import DEFAULT_FACTOR_WEIGHTS

st.set_page_config(page_title="Backtester — AlphaForge", layout="wide")
st.title("Backtester")

# ---- Sidebar Config ----
with st.sidebar:
    st.header("Backtest Configuration")

    sectors = ["All"] + get_sectors()
    selected_sectors = st.multiselect("Sectors", sectors, default=["All"])
    if "All" in selected_sectors:
        symbols = get_symbols()
    else:
        symbols = []
        for sec in selected_sectors:
            symbols += get_symbols(sector=sec)
    symbols = list(set(symbols))
    st.caption(f"{len(symbols)} stocks in universe")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start", pd.Timestamp("2018-01-01"))
    with col2:
        end_date = st.date_input("End", pd.Timestamp("today"))

    top_n = st.slider("Top N Stocks", 5, 50, 20)
    rebalance_freq = st.selectbox("Rebalance Frequency",
                                   ["monthly", "quarterly", "weekly"], index=0)

    st.subheader("Factor Weights")
    w_mom = st.slider("Momentum", 0.0, 1.0, DEFAULT_FACTOR_WEIGHTS["momentum"], 0.05)
    w_val = st.slider("Value", 0.0, 1.0, DEFAULT_FACTOR_WEIGHTS["value"], 0.05)
    w_qual = st.slider("Quality", 0.0, 1.0, DEFAULT_FACTOR_WEIGHTS["quality"], 0.05)
    w_vol = st.slider("Low Volatility", 0.0, 1.0, DEFAULT_FACTOR_WEIGHTS["volatility"], 0.05)

    total_w = w_mom + w_val + w_qual + w_vol
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"Weights sum to {total_w:.2f}. They will be normalized.")

    weights = {
        "momentum": w_mom / total_w,
        "value": w_val / total_w,
        "quality": w_qual / total_w,
        "volatility": w_vol / total_w,
    }

    run_btn = st.button("Run Backtest", type="primary", use_container_width=True)

# ---- Run ----
if run_btn:
    with st.spinner("Running backtest... this may take a minute."):
        result = run_backtest(
            symbols=symbols,
            start=str(start_date),
            end=str(end_date),
            top_n=top_n,
            weights=weights,
            rebalance_freq=rebalance_freq,
        )
        st.session_state.backtest_result = result
        st.session_state.backtest_ran = True
    st.success("Backtest complete!")

# ---- Results ----
if "backtest_result" not in st.session_state:
    st.info("Configure your backtest in the sidebar and click **Run Backtest**.")
    st.stop()

result = st.session_state.backtest_result
metrics = result["metrics"]
returns = result["returns"]
bench = result["benchmark_returns"]

# ---- Key Metrics Row ----
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("CAGR", f"{metrics.get('cagr', 0):.1%}")
m2.metric("Sharpe", f"{metrics.get('sharpe', 0):.2f}")
m3.metric("Sortino", f"{metrics.get('sortino', 0):.2f}")
m4.metric("Max Drawdown", f"{metrics.get('max_drawdown', 0):.1%}")
m5.metric("Alpha", f"{metrics.get('alpha', 0):.1%}")
m6.metric("Beta", f"{metrics.get('beta', 1):.2f}")

st.divider()

col_left, col_right = st.columns([3, 1])

with col_left:
    # Equity Curve
    fig_eq = plot_equity_curve(returns, bench, "Factor Portfolio vs Nifty 50")
    st.plotly_chart(fig_eq, use_container_width=True)

    # Drawdown
    fig_dd = plot_drawdown(returns)
    st.plotly_chart(fig_dd, use_container_width=True)

with col_right:
    st.subheader("Full Metrics")
    metric_rows = [
        ("Total Return", f"{metrics.get('total_return', 0):.1%}"),
        ("CAGR", f"{metrics.get('cagr', 0):.1%}"),
        ("Benchmark CAGR", f"{metrics.get('benchmark_cagr', 0):.1%}"),
        ("Excess Return", f"{metrics.get('excess_return', 0):.1%}"),
        ("Sharpe", f"{metrics.get('sharpe', 0):.2f}"),
        ("Sortino", f"{metrics.get('sortino', 0):.2f}"),
        ("Calmar", f"{metrics.get('calmar', 0):.2f}"),
        ("Info Ratio", f"{metrics.get('information_ratio', 0):.2f}"),
        ("Max Drawdown", f"{metrics.get('max_drawdown', 0):.1%}"),
        ("Volatility", f"{metrics.get('ann_volatility', 0):.1%}"),
        ("Alpha", f"{metrics.get('alpha', 0):.1%}"),
        ("Beta", f"{metrics.get('beta', 1):.2f}"),
        ("Win Rate", f"{metrics.get('win_rate', 0):.1%}"),
        ("Best Month", f"{metrics.get('best_month', 0):.1%}"),
        ("Worst Month", f"{metrics.get('worst_month', 0):.1%}"),
    ]
    for label, value in metric_rows:
        col_a, col_b = st.columns([1.5, 1])
        col_a.caption(label)
        col_b.markdown(f"**{value}**")

st.divider()

# Monthly Returns Heatmap
st.subheader("Monthly Returns")
fig_heatmap = plot_monthly_heatmap(returns)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Rolling Metrics
st.subheader("Rolling Performance")
roll = rolling_metrics(returns)
import plotly.express as px
fig_roll = px.line(roll, title="Rolling 1-Year Sharpe & Volatility",
                   template="plotly_dark")
st.plotly_chart(fig_roll, use_container_width=True)

# Holdings History
st.subheader("Holdings at Last Rebalance")
if result["holdings_history"]:
    last_date, last_holdings = result["holdings_history"][-1]
    st.caption(f"Last rebalance: {last_date.strftime('%d %b %Y')}")
    cols = st.columns(5)
    for i, sym in enumerate(last_holdings):
        cols[i % 5].markdown(f"• `{sym}`")

# Export
st.divider()
st.download_button(
    "Export Metrics (JSON)",
    data=json.dumps(metrics, default=str, indent=2),
    file_name="alphaforge_metrics.json",
    mime="application/json",
)
