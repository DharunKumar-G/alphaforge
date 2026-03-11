PORTFOLIO_SYSTEM = """You are AlphaForge's AI analyst — an expert quantitative analyst specializing 
in Indian equity markets. You have access to the user's backtest data, factor scores, and portfolio 
performance metrics.

Your role:
- Answer questions about portfolio performance in plain English
- Explain factor-driven moves (momentum, value, quality, volatility)
- Be concise, data-driven, and actionable
- Reference specific numbers from the context provided
- When uncertain, say so — never fabricate data

Indian market context: NSE/BSE, Nifty 500 universe, factors measured in Indian rupees.
Risk-free rate: ~6.5% (10-year G-Sec).
"""

def build_portfolio_context(backtest_result: dict) -> str:
    metrics = backtest_result.get("metrics", {})
    holdings = backtest_result.get("holdings_history", [])
    latest_holdings = holdings[-1][1] if holdings else []

    return f"""
PORTFOLIO CONTEXT:
- Period: {backtest_result.get('start')} to {backtest_result.get('end')}
- CAGR: {metrics.get('cagr', 0):.1%}
- Sharpe Ratio: {metrics.get('sharpe', 0):.2f}
- Max Drawdown: {metrics.get('max_drawdown', 0):.1%}
- Volatility: {metrics.get('ann_volatility', 0):.1%}
- Alpha: {metrics.get('alpha', 0):.1%}
- Beta: {metrics.get('beta', 1):.2f}
- Win Rate: {metrics.get('win_rate', 0):.1%}
- Rebalance Frequency: {backtest_result.get('rebalance_freq')}
- Top N Stocks: {backtest_result.get('top_n')}
- Factor Weights: {backtest_result.get('factor_weights')}
- Current Holdings ({len(latest_holdings)} stocks): {', '.join(latest_holdings[:15])}
"""
