"""
Dashboard — overview of portfolio performance, regime, top holdings, alerts.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data.fetcher import fetch_close_matrix, fetch_fundamentals
from data.universe import get_universe, get_symbols
from core.factors.scorer import compute_composite_scores, rank_stocks, score_to_signal
from core.regime.detector import get_current_regime, REGIME_COLORS
from core.risk.manager import check_portfolio_risk, compute_var
from components.equity_curve import plot_equity_curve, plot_drawdown
from components.radar_chart import plot_factor_radar
from config.settings import DEFAULT_FACTOR_WEIGHTS, BENCHMARK

st.set_page_config(page_title="Dashboard — AlphaForge", layout="wide")
st.title("Dashboard")

# --- Sidebar ---
with st.sidebar:
    st.header("Settings")
    universe_df = get_universe()
    sectors = ["All"] + sorted(universe_df["sector"].unique().tolist())
    selected_sector = st.selectbox("Sector Filter", sectors)
    top_n = st.slider("Top N Stocks", 5, 50, 20)
    start_date = st.date_input("Start Date", value=pd.Timestamp("2018-01-01"))

    if st.button("Compute Scores", type="primary"):
        st.session_state.scores_computed = False

# --- Load Data ---
@st.cache_data(ttl=3600, show_spinner="Fetching market data...")
def load_data(sector, start):
    if sector == "All":
        symbols = get_symbols()
    else:
        symbols = get_symbols(sector=sector)
    symbols = symbols[:50]  # limit for speed

    prices = fetch_close_matrix(symbols + [BENCHMARK], start=str(start))
    return prices, symbols

prices, symbols = load_data(selected_sector, start_date)

if prices.empty:
    st.error("No data loaded. Check your internet connection.")
    st.stop()

bench_prices = prices.get(BENCHMARK, pd.Series(dtype=float))
stock_prices = prices.drop(columns=[BENCHMARK], errors="ignore")

# --- Regime ---
regime_info = get_current_regime(bench_prices) if not bench_prices.empty else {}
regime = regime_info.get("regime", "Unknown")
regime_color = REGIME_COLORS.get(regime, "#888")

# --- Factor Scores ---
@st.cache_data(ttl=3600, show_spinner="Computing factor scores...")
def get_scores(symbols, start):
    fundamentals = {}
    for sym in symbols[:30]:
        f = fetch_fundamentals(sym)
        if f:
            fundamentals[sym] = f
    prices_ = fetch_close_matrix(symbols, start=str(start))
    return compute_composite_scores(prices_, fundamentals, DEFAULT_FACTOR_WEIGHTS)

scores = get_scores(symbols, start_date)
top_stocks = rank_stocks(scores, top_n=top_n)

# ==============================
# TOP ROW: Key Metrics
# ==============================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Universe", f"{len(symbols)} stocks",
              f"{selected_sector}" if selected_sector != "All" else "Nifty 500")

with col2:
    st.markdown(
        f"<div style='background:{regime_color}20;border-left:4px solid {regime_color};"
        f"padding:10px;border-radius:4px'>"
        f"<div style='font-size:11px;color:#888'>MARKET REGIME</div>"
        f"<div style='font-size:22px;font-weight:700;color:{regime_color}'>{regime}</div>"
        f"<div style='font-size:11px'>{regime_info.get('confidence', 0):.0%} confidence</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

with col3:
    avg_composite = top_stocks["composite"].mean() if not top_stocks.empty else 0
    st.metric("Avg Composite Score", f"{avg_composite:.2f}",
              "Top portfolio factor score")

with col4:
    avg_momentum = top_stocks["momentum"].mean() if not top_stocks.empty else 0
    st.metric("Avg Momentum", f"{avg_momentum:.2f}")

with col5:
    avg_quality = top_stocks["quality"].mean() if not top_stocks.empty else 0
    st.metric("Avg Quality", f"{avg_quality:.2f}")

st.divider()

# ==============================
# MIDDLE ROW: Scores + Radar
# ==============================
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader(f"Top {top_n} Stocks by Factor Score")
    if not top_stocks.empty:
        display = top_stocks[["momentum", "value", "quality", "volatility", "composite"]].copy()
        display = display.round(3)
        display["signal"] = display["composite"].apply(score_to_signal)

        # Color coding
        def color_signal(val):
            colors = {
                "Strong Buy": "background-color:#00c85320",
                "Buy": "background-color:#69f09020",
                "Neutral": "background-color:#ffd60020",
                "Sell": "background-color:#ff6d0020",
                "Strong Sell": "background-color:#d5000020",
            }
            return colors.get(val, "")

        styled = display.style.applymap(color_signal, subset=["signal"])
        st.dataframe(styled, use_container_width=True, height=450)
    else:
        st.info("No scores computed yet.")

with col_right:
    st.subheader("Portfolio Factor Exposure")
    if not top_stocks.empty:
        avg_scores = {
            "Momentum": float(top_stocks["momentum"].mean()),
            "Value": float(top_stocks["value"].mean()),
            "Quality": float(top_stocks["quality"].mean()),
            "Low Vol": float(top_stocks["volatility"].mean()),
        }
        fig_radar = plot_factor_radar(avg_scores)
        st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# ==============================
# BOTTOM ROW: Benchmark Trend
# ==============================
st.subheader("Market Trend (Benchmark)")
if not bench_prices.empty:
    bench_returns = bench_prices.pct_change().dropna()
    col_curve, col_dd = st.columns([3, 1])

    with col_curve:
        fig_eq = plot_equity_curve(bench_returns, title="Nifty 50 Cumulative Return")
        st.plotly_chart(fig_eq, use_container_width=True)

    with col_dd:
        var_95 = compute_var(bench_returns, confidence=0.95)
        vol = bench_returns.std() * (252 ** 0.5)
        total_ret = (1 + bench_returns).prod() - 1
        st.metric("Total Return", f"{total_ret:.1%}")
        st.metric("Annual Volatility", f"{vol:.1%}")
        st.metric("VaR (95%)", f"{var_95:.1%}")
        st.metric("Current Regime", regime,
                  delta=f"{regime_info.get('confidence', 0):.0%} confidence")
