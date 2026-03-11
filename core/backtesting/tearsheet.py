"""
One-click professional tear sheet generator.
Outputs PNG or PDF summary of backtest results.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def generate_tearsheet(result: dict) -> go.Figure:
    """
    Generate a single-page tear sheet figure with all key metrics and charts.
    Returns a Plotly figure that can be exported as PNG/PDF.
    """
    returns = result["returns"]
    bench = result["benchmark_returns"]
    metrics = result["metrics"]

    cum_port = (1 + returns).cumprod()
    cum_bench = (1 + bench.reindex(returns.index).fillna(0)).cumprod()
    dd = (cum_port - cum_port.cummax()) / cum_port.cummax()

    monthly = returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)
    monthly_df = pd.DataFrame({
        "year": monthly.index.year,
        "month": monthly.index.month,
        "return": monthly.values,
    })
    pivot = monthly_df.pivot(index="year", columns="month", values="return")

    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            "Equity Curve", "Drawdown", "Monthly Return Distribution",
            "Rolling Sharpe (1Y)", "Monthly Heatmap", "",
            "Performance Summary", "", "",
        ),
        specs=[
            [{"colspan": 2}, None, {"type": "histogram"}],
            [{"type": "scatter"}, {"type": "heatmap"}, None],
            [{"type": "table", "colspan": 3}, None, None],
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.08,
    )

    # Equity curve
    fig.add_trace(go.Scatter(x=cum_port.index, y=cum_port.values,
                              name="Portfolio", line=dict(color="#00c853")), row=1, col=1)
    fig.add_trace(go.Scatter(x=cum_bench.index, y=cum_bench.values,
                              name="Benchmark", line=dict(color="#2196f3", dash="dash")), row=1, col=1)

    # Drawdown
    fig.add_trace(go.Scatter(x=dd.index, y=dd.values, fill="tozeroy",
                              fillcolor="rgba(213,0,0,0.3)", line=dict(color="#d50000"),
                              name="Drawdown", showlegend=False), row=1, col=1)

    # Monthly distribution
    fig.add_trace(go.Histogram(x=monthly.values, nbinsx=20,
                                marker_color="#00c853", name="Monthly Returns",
                                showlegend=False), row=1, col=3)

    # Rolling Sharpe
    rf = 0.065 / 252
    roll_sharpe = ((returns - rf).rolling(252).mean() /
                   returns.rolling(252).std() * np.sqrt(252))
    fig.add_trace(go.Scatter(x=roll_sharpe.index, y=roll_sharpe.values,
                              line=dict(color="#ffd600"), name="Rolling Sharpe",
                              showlegend=False), row=2, col=1)

    # Metrics table
    metric_items = [
        ("CAGR", f"{metrics.get('cagr', 0):.1%}"),
        ("Sharpe", f"{metrics.get('sharpe', 0):.2f}"),
        ("Max Drawdown", f"{metrics.get('max_drawdown', 0):.1%}"),
        ("Alpha", f"{metrics.get('alpha', 0):.1%}"),
        ("Beta", f"{metrics.get('beta', 1):.2f}"),
        ("Sortino", f"{metrics.get('sortino', 0):.2f}"),
        ("Calmar", f"{metrics.get('calmar', 0):.2f}"),
        ("Info Ratio", f"{metrics.get('information_ratio', 0):.2f}"),
    ]
    fig.add_trace(go.Table(
        header=dict(values=["Metric", "Value"],
                    fill_color="#1e1e1e", font=dict(color="white")),
        cells=dict(values=[[m[0] for m in metric_items],
                            [m[1] for m in metric_items]],
                   fill_color="#2a2a2a", font=dict(color="white")),
    ), row=3, col=1)

    fig.update_layout(
        title=dict(text="AlphaForge — Strategy Tear Sheet", font=dict(size=18)),
        template="plotly_dark",
        height=900,
        width=1400,
        showlegend=True,
    )

    return fig
