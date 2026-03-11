"""
Portfolio Optimizer — Markowitz, Risk Parity, Efficient Frontier.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data.fetcher import fetch_close_matrix
from core.optimization.markowitz import max_sharpe_portfolio, min_variance_portfolio, compute_efficient_frontier
from core.optimization.risk_parity import risk_parity_weights
from core.risk.monte_carlo import run_monte_carlo, get_probability_cone, monte_carlo_var

st.set_page_config(page_title="Portfolio Optimizer — AlphaForge", layout="wide")
st.title("Portfolio Optimizer")

with st.sidebar:
    st.header("Configuration")
    if "backtest_result" in st.session_state:
        holdings = st.session_state.backtest_result.get("holdings_history", [])
        if holdings:
            default_stocks = ", ".join(holdings[-1][1][:10])
        else:
            default_stocks = ""
        st.caption("Pre-filled from last backtest")
    else:
        default_stocks = "HDFCBANK.NS, INFY.NS, RELIANCE.NS, TCS.NS, ICICIBANK.NS"

    stock_input = st.text_area("Stocks (comma-separated)", value=default_stocks)
    start = st.date_input("Start Date", pd.Timestamp("2020-01-01"))
    n_mc = st.slider("Monte Carlo Simulations", 100, 5000, 1000, 100)
    run = st.button("Optimize", type="primary", use_container_width=True)

if not run:
    st.info("Enter stocks and click **Optimize** to run portfolio optimization.")
    st.stop()

symbols = [s.strip() for s in stock_input.split(",") if s.strip()]
if len(symbols) < 2:
    st.error("Enter at least 2 stocks.")
    st.stop()

with st.spinner("Fetching data and optimizing..."):
    prices = fetch_close_matrix(symbols, start=str(start))
    prices = prices.dropna(axis=1, how="any")
    if prices.shape[1] < 2:
        st.error("Not enough data for selected stocks.")
        st.stop()
    returns = prices.pct_change().dropna()

    max_sharpe = max_sharpe_portfolio(returns)
    min_var = min_variance_portfolio(returns)
    risk_par = risk_parity_weights(returns)
    frontier = compute_efficient_frontier(returns, n_points=30)

# ---- Results tabs ----
tab1, tab2, tab3, tab4 = st.tabs(["Max Sharpe", "Risk Parity", "Efficient Frontier", "Monte Carlo"])

def weights_chart(weights_dict: dict, title: str):
    df = pd.DataFrame(list(weights_dict.items()), columns=["Stock", "Weight"])
    df = df[df["Weight"] > 0.001].sort_values("Weight", ascending=False)
    fig = px.bar(df, x="Stock", y="Weight", title=title,
                 color="Weight", color_continuous_scale="greens",
                 template="plotly_dark")
    fig.update_yaxes(tickformat=".0%")
    return fig

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Expected Return", f"{max_sharpe['return']:.1%}")
    col2.metric("Volatility", f"{max_sharpe['volatility']:.1%}")
    col3.metric("Sharpe Ratio", f"{max_sharpe['sharpe']:.2f}")
    st.plotly_chart(weights_chart(max_sharpe["weights"], "Max Sharpe Weights"),
                    use_container_width=True)

    vs_minvar = pd.DataFrame({
        "Portfolio": ["Max Sharpe", "Min Variance"],
        "Return": [max_sharpe["return"], min_var["return"]],
        "Volatility": [max_sharpe["volatility"], min_var["volatility"]],
        "Sharpe": [max_sharpe["sharpe"], min_var["sharpe"]],
    })
    st.dataframe(vs_minvar.set_index("Portfolio").style.format("{:.2%}", subset=["Return", "Volatility"]),
                 use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    col1.metric("Portfolio Volatility", f"{risk_par['portfolio_volatility']:.1%}")
    col2.metric("Expected Return", f"{risk_par['portfolio_return']:.1%}")

    st.plotly_chart(weights_chart(risk_par["weights"], "Risk Parity Weights"),
                    use_container_width=True)

    rc_df = pd.DataFrame(list(risk_par["risk_contributions"].items()),
                          columns=["Stock", "Risk Contribution"])
    rc_df["Risk Contribution %"] = rc_df["Risk Contribution"] / rc_df["Risk Contribution"].sum()
    st.caption("Risk Contributions (should be equal for true risk parity)")
    st.dataframe(rc_df.sort_values("Risk Contribution %", ascending=False), use_container_width=True)

with tab3:
    if not frontier.empty:
        fig_ef = go.Figure()
        fig_ef.add_trace(go.Scatter(
            x=frontier["volatility"], y=frontier["return"],
            mode="lines+markers",
            marker=dict(color=frontier["sharpe"], colorscale="Greens",
                        showscale=True, colorbar=dict(title="Sharpe")),
            text=[f"Sharpe: {s:.2f}" for s in frontier["sharpe"]],
            hovertemplate="Vol: %{x:.1%}<br>Return: %{y:.1%}<br>%{text}<extra></extra>",
            name="Efficient Frontier",
        ))
        fig_ef.add_trace(go.Scatter(
            x=[max_sharpe["volatility"]], y=[max_sharpe["return"]],
            mode="markers", marker=dict(size=12, color="#ffd600", symbol="star"),
            name="Max Sharpe",
        ))
        fig_ef.add_trace(go.Scatter(
            x=[min_var["volatility"]], y=[min_var["return"]],
            mode="markers", marker=dict(size=12, color="#00c853", symbol="diamond"),
            name="Min Variance",
        ))
        fig_ef.update_layout(
            title="Efficient Frontier",
            xaxis=dict(title="Volatility", tickformat=".0%"),
            yaxis=dict(title="Expected Return", tickformat=".0%"),
            template="plotly_dark", height=500,
        )
        st.plotly_chart(fig_ef, use_container_width=True)

with tab4:
    with st.spinner("Running Monte Carlo simulation..."):
        port_returns = returns[list(max_sharpe["weights"].keys())].mean(axis=1)
        paths = run_monte_carlo(port_returns, n_simulations=n_mc, n_days=252)
        cone = get_probability_cone(paths)
        mc_stats = monte_carlo_var(port_returns)

    col1, col2, col3 = st.columns(3)
    col1.metric("Expected Return (1Y)", f"{mc_stats['expected_return']:.1%}")
    col2.metric("VaR (95%)", f"{mc_stats['var']:.1%}")
    col3.metric("Prob of Loss", f"{mc_stats['prob_loss']:.1%}")

    fig_mc = go.Figure()
    x = list(range(252))
    fig_mc.add_trace(go.Scatter(x=x+x[::-1],
                                 y=list(cone["p95"])+list(cone["p5"])[::-1],
                                 fill="toself", fillcolor="rgba(0,200,83,0.1)",
                                 line=dict(color="rgba(0,0,0,0)"), name="90% CI"))
    fig_mc.add_trace(go.Scatter(x=x+x[::-1],
                                 y=list(cone["p75"])+list(cone["p25"])[::-1],
                                 fill="toself", fillcolor="rgba(0,200,83,0.2)",
                                 line=dict(color="rgba(0,0,0,0)"), name="50% CI"))
    fig_mc.add_trace(go.Scatter(x=x, y=cone["p50"], line=dict(color="#00c853", width=2),
                                 name="Median Path"))
    fig_mc.update_layout(title=f"Monte Carlo Probability Cone ({n_mc} simulations)",
                          xaxis_title="Trading Days",
                          yaxis_title="Cumulative Return",
                          yaxis_tickformat=".0%",
                          template="plotly_dark", height=450)
    st.plotly_chart(fig_mc, use_container_width=True)
