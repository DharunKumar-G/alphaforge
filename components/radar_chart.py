"""
Factor exposure radar chart.
"""
import plotly.graph_objects as go
import pandas as pd


def plot_factor_radar(scores: dict, title: str = "Factor Exposure") -> go.Figure:
    """
    Spider/radar chart for factor scores.
    
    Args:
        scores: dict like {"momentum": 0.8, "value": 0.4, "quality": 0.7, "volatility": 0.6}
    """
    categories = list(scores.keys())
    values = [scores[k] for k in categories]
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(0, 200, 83, 0.2)",
        line=dict(color="#00c853", width=2),
        name="Portfolio",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], tickformat=".0%"),
            angularaxis=dict(tickfont=dict(size=13)),
        ),
        title=title,
        template="plotly_dark",
        height=400,
        showlegend=False,
    )

    return fig


def plot_factor_radar_comparison(portfolio_scores: dict,
                                  benchmark_scores: dict) -> go.Figure:
    """Radar chart comparing portfolio factor exposure vs benchmark."""
    categories = list(portfolio_scores.keys())
    port_vals = [portfolio_scores[k] for k in categories] + [portfolio_scores[categories[0]]]
    bench_vals = [benchmark_scores[k] for k in categories] + [benchmark_scores[categories[0]]]
    cats = categories + [categories[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=port_vals, theta=cats, fill="toself",
        fillcolor="rgba(0, 200, 83, 0.2)",
        line=dict(color="#00c853", width=2),
        name="Portfolio",
    ))

    fig.add_trace(go.Scatterpolar(
        r=bench_vals, theta=cats, fill="toself",
        fillcolor="rgba(33, 150, 243, 0.1)",
        line=dict(color="#2196f3", width=2, dash="dash"),
        name="Benchmark",
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Factor Exposure: Portfolio vs Benchmark",
        template="plotly_dark",
        height=400,
    )

    return fig
