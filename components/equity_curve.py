"""
Interactive equity curve chart with drawdown shading and benchmark comparison.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def plot_equity_curve(returns: pd.Series, benchmark: pd.Series = None,
                      title: str = "Portfolio Equity Curve") -> go.Figure:
    """
    Zoomable equity curve with:
    - Portfolio cumulative return
    - Benchmark overlay (toggleable)
    - Drawdown period shading in red
    """
    cum_port = (1 + returns).cumprod()
    drawdown = (cum_port - cum_port.cummax()) / cum_port.cummax()

    fig = go.Figure()

    # Drawdown shading
    fig.add_trace(go.Scatter(
        x=pd.concat([drawdown.index.to_series(), drawdown.index.to_series()[::-1]]),
        y=pd.concat([cum_port, cum_port.cummax()[::-1]]),
        fill="toself",
        fillcolor="rgba(213, 0, 0, 0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Drawdown",
        showlegend=True,
        hoverinfo="skip",
    ))

    # Portfolio line
    fig.add_trace(go.Scatter(
        x=cum_port.index,
        y=cum_port.values,
        mode="lines",
        name="AlphaForge Portfolio",
        line=dict(color="#00c853", width=2.5),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Value: %{y:.3f}<extra></extra>",
    ))

    # Benchmark
    if benchmark is not None and not benchmark.empty:
        cum_bench = (1 + benchmark.reindex(returns.index).fillna(0)).cumprod()
        fig.add_trace(go.Scatter(
            x=cum_bench.index,
            y=cum_bench.values,
            mode="lines",
            name="Benchmark (Nifty 50)",
            line=dict(color="#2196f3", width=1.5, dash="dash"),
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Benchmark: %{y:.3f}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=dict(title="Date", rangeslider=dict(visible=True)),
        yaxis=dict(title="Cumulative Return (₹1 = base)", tickformat=".2f"),
        hovermode="x unified",
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
    )

    return fig


def plot_drawdown(returns: pd.Series) -> go.Figure:
    """Standalone drawdown chart."""
    cum = (1 + returns).cumprod()
    dd = (cum - cum.cummax()) / cum.cummax()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dd.index, y=dd.values,
        fill="tozeroy",
        fillcolor="rgba(213, 0, 0, 0.3)",
        line=dict(color="#d50000"),
        name="Drawdown",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Drawdown: %{y:.1%}<extra></extra>",
    ))

    fig.update_layout(
        title="Drawdown",
        yaxis=dict(title="Drawdown", tickformat=".0%"),
        template="plotly_dark",
        height=250,
    )

    return fig


def plot_monthly_heatmap(returns: pd.Series) -> go.Figure:
    """Monthly returns heatmap."""
    monthly = returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    df = pd.DataFrame({
        "year": monthly.index.year,
        "month": monthly.index.month,
        "return": monthly.values,
    })

    pivot = df.pivot(index="year", columns="month", values="return")
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values * 100,
        x=[month_names[m - 1] for m in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=[
            [0, "#d50000"], [0.5, "#ffffff"], [1, "#00c853"]
        ],
        zmid=0,
        text=[[f"{v:.1f}%" if not pd.isna(v) else "" for v in row]
              for row in pivot.values * 100],
        texttemplate="%{text}",
        hovertemplate="<b>%{y} %{x}</b><br>Return: %{z:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        title="Monthly Returns (%)",
        template="plotly_dark",
        height=350,
    )

    return fig
