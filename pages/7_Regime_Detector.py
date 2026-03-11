"""
Regime Detector — visualize market regimes and sector rotation signals.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from data.fetcher import fetch_close_matrix, fetch_prices
from core.regime.detector import detect_regime, get_current_regime, REGIME_COLORS, REGIME_SECTOR_PREFERENCE
from config.settings import BENCHMARK

st.set_page_config(page_title="Regime Detector — AlphaForge", layout="wide")
st.title("Market Regime Detector")

with st.sidebar:
    start = st.date_input("Start Date", pd.Timestamp("2015-01-01"))
    benchmark = st.selectbox("Market Index", ["^NSEI", "^NSEBANK", "^BSESN"], index=0)
    smooth_window = st.slider("Smoothing Window (days)", 1, 30, 5)

@st.cache_data(ttl=3600, show_spinner="Loading market data...")
def load_benchmark(sym, start):
    df = fetch_prices(sym, start=str(start))
    return df

bench_df = load_benchmark(benchmark, start)

if bench_df.empty:
    st.error("Failed to load benchmark data.")
    st.stop()

bench_prices = bench_df["Close"]
regimes = detect_regime(bench_prices)

current = get_current_regime(bench_prices)
regime = current["regime"]
regime_color = REGIME_COLORS.get(regime, "#888")

# ---- Current Regime Banner ----
st.markdown(
    f"<div style='background:{regime_color}20;border:2px solid {regime_color};"
    f"padding:16px;border-radius:8px;margin-bottom:16px'>"
    f"<h2 style='margin:0;color:{regime_color}'>Current Regime: {regime}</h2>"
    f"<p style='margin:4px 0 0 0'>Confidence: {current['confidence']:.0%} | "
    f"3M Momentum: {current.get('momentum_3m', 0):.1%} | "
    f"Volatility: {current.get('volatility', 0):.1%} annualized</p>"
    f"</div>",
    unsafe_allow_html=True,
)

# Preferred sectors in this regime
st.subheader("Preferred Sectors in This Regime")
preferred = REGIME_SECTOR_PREFERENCE.get(regime, [])
cols = st.columns(len(preferred) if preferred else 1)
for i, sec in enumerate(preferred):
    cols[i].success(f"✓ {sec}")

st.divider()

# ---- Regime History Chart ----
st.subheader("Regime History")

# Color map for plotly
regime_color_map = {"Bull": "#00c853", "Sideways": "#ffd600", "Bear": "#d50000"}

fig = go.Figure()

# Price line
fig.add_trace(go.Scatter(
    x=bench_prices.index, y=bench_prices.values,
    mode="lines", name=benchmark,
    line=dict(color="#2196f3", width=1.5),
))

# Regime shading
if not regimes.empty:
    for regime_type, color in regime_color_map.items():
        mask = regimes["regime"] == regime_type
        regime_dates = regimes[mask].index
        if len(regime_dates) > 0:
            # Add colored background spans
            for date in regime_dates[::5]:  # sample every 5 days for performance
                fig.add_vrect(
                    x0=date, x1=date + pd.Timedelta(days=5),
                    fillcolor=color, opacity=0.05,
                    line_width=0,
                )

fig.update_layout(
    title=f"Price with Regime Overlay ({benchmark})",
    xaxis_title="Date",
    yaxis_title="Price",
    template="plotly_dark",
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

# Regime score over time
if not regimes.empty:
    smooth = regimes["regime_score"].rolling(smooth_window).mean()
    fig_score = go.Figure()
    fig_score.add_trace(go.Scatter(
        x=smooth.index, y=smooth.values,
        mode="lines", fill="tozeroy",
        fillcolor="rgba(0, 200, 83, 0.1)",
        line=dict(color="#00c853"),
        name="Regime Score",
    ))
    fig_score.add_hline(y=2, line_dash="dash", line_color="#00c853",
                         annotation_text="Bull threshold")
    fig_score.add_hline(y=-2, line_dash="dash", line_color="#d50000",
                         annotation_text="Bear threshold")
    fig_score.update_layout(
        title="Regime Score (smoothed)",
        yaxis_title="Score (-4 to +4)",
        template="plotly_dark",
        height=300,
    )
    st.plotly_chart(fig_score, use_container_width=True)

# Regime stats
if not regimes.empty:
    st.subheader("Regime Distribution")
    dist = regimes["regime"].value_counts()
    fig_pie = px.pie(values=dist.values, names=dist.index,
                      color=dist.index,
                      color_discrete_map=regime_color_map,
                      title="Time in Each Regime",
                      template="plotly_dark")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.dataframe(
            regimes.groupby("regime").agg(
                days=("regime", "count"),
                avg_confidence=("confidence", "mean"),
            ).round(2),
            use_container_width=True,
        )
