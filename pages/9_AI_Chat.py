"""
AI Chat — multi-turn portfolio Q&A powered by Claude.
"""
import streamlit as st
from ai.portfolio_chat import render_chat
from ai.strategy_critique import critique_strategy, compare_strategies

st.set_page_config(page_title="AI Chat — AlphaForge", layout="wide")
st.title("AI Research Assistant")

tab1, tab2, tab3 = st.tabs(["Portfolio Chat", "Strategy Critique", "Compare Strategies"])

with tab1:
    if "backtest_result" not in st.session_state:
        st.info("Run a backtest first (Backtester page), then come back here to chat about it.")
    else:
        render_chat(st.session_state.backtest_result)

with tab2:
    st.subheader("Strategy Critique")
    st.caption("Get AI-powered feedback on your backtest strategy.")

    if "backtest_result" not in st.session_state:
        st.info("Run a backtest first.")
    else:
        extra = st.text_area("Any additional context for the critique?",
                              placeholder="e.g. This strategy is for a 3-year investment horizon...")
        if st.button("Generate Critique", type="primary"):
            with st.spinner("Analyzing strategy..."):
                critique = critique_strategy(st.session_state.backtest_result, extra)
            st.markdown(critique)

with tab3:
    st.subheader("Compare Two Strategies")
    if "backtest_result" not in st.session_state:
        st.info("Run at least one backtest first.")
    else:
        st.info("Run a second backtest and save it, then compare here. "
                "Feature requires two saved backtest results.")
