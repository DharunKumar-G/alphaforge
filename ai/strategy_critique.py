"""
AI Strategy Critique — feed backtest results to Claude for actionable feedback.
"""
from ai.client import chat

CRITIQUE_SYSTEM = """You are a senior quantitative portfolio manager reviewing a factor-based 
investment strategy for Indian equity markets. 

Your critique should be:
1. Specific and data-driven (reference the exact numbers provided)
2. Constructive — identify weaknesses AND suggest concrete fixes
3. Cover: factor exposures, regime sensitivity, concentration risk, transaction costs,
   survivorship bias concerns, and overall risk-adjusted performance
4. End with 3-5 bullet point action items

Be direct. Don't pad with generic statements. The user wants expert-level feedback."""

COMPARE_SYSTEM = """You are comparing two quantitative strategies for Indian equity markets.
Analyze both strategies and give a clear recommendation on which is better for:
1. A growth-oriented investor
2. A conservative investor
3. A quant intern wanting to demonstrate skill

Back every claim with numbers from the data provided. Be decisive — pick a winner."""


def critique_strategy(backtest_result: dict, extra_context: str = "") -> str:
    """Generate AI critique of a single backtest."""
    metrics = backtest_result.get("metrics", {})
    holdings = backtest_result.get("holdings_history", [])

    context = f"""
STRATEGY DETAILS:
Period: {backtest_result.get('start')} to {backtest_result.get('end')}
Rebalance: {backtest_result.get('rebalance_freq')}
Top N: {backtest_result.get('top_n')} stocks
Factor Weights: {backtest_result.get('factor_weights')}

PERFORMANCE METRICS:
CAGR: {metrics.get('cagr', 0):.1%}
Sharpe: {metrics.get('sharpe', 0):.2f}
Sortino: {metrics.get('sortino', 0):.2f}
Max Drawdown: {metrics.get('max_drawdown', 0):.1%}
Calmar: {metrics.get('calmar', 0):.2f}
Alpha: {metrics.get('alpha', 0):.1%}
Beta: {metrics.get('beta', 1):.2f}
Information Ratio: {metrics.get('information_ratio', 0):.2f}
Win Rate: {metrics.get('win_rate', 0):.1%}
Best Month: {metrics.get('best_month', 0):.1%}
Worst Month: {metrics.get('worst_month', 0):.1%}
Number of Rebalances: {len(holdings)}

{extra_context}

Please provide a thorough critique of this strategy."""

    return chat(CRITIQUE_SYSTEM, context, max_tokens=2000)


def compare_strategies(result_a: dict, name_a: str,
                        result_b: dict, name_b: str) -> str:
    """Compare two strategies."""
    def fmt(r, name):
        m = r.get("metrics", {})
        return f"""
{name}:
  CAGR: {m.get('cagr', 0):.1%} | Sharpe: {m.get('sharpe', 0):.2f} | MaxDD: {m.get('max_drawdown', 0):.1%}
  Alpha: {m.get('alpha', 0):.1%} | Beta: {m.get('beta', 1):.2f} | IR: {m.get('information_ratio', 0):.2f}
  Factor Weights: {r.get('factor_weights')}
  Top N: {r.get('top_n')} | Rebalance: {r.get('rebalance_freq')}"""

    context = fmt(result_a, name_a) + "\n" + fmt(result_b, name_b)
    return chat(COMPARE_SYSTEM, context, max_tokens=1500)
