"""
Multi-turn portfolio chat using Claude API.
Maintains conversation history within a Streamlit session.
"""
import streamlit as st
from ai.client import stream_chat
from ai.prompts.portfolio import PORTFOLIO_SYSTEM, build_portfolio_context


def init_chat_session(backtest_result: dict):
    """Initialize chat history in Streamlit session state."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "portfolio_context" not in st.session_state:
        st.session_state.portfolio_context = build_portfolio_context(backtest_result)


def render_chat(backtest_result: dict):
    """Full Streamlit chat UI for portfolio Q&A."""
    init_chat_session(backtest_result)

    st.subheader("Chat with your Portfolio")
    st.caption("Ask anything about your strategy's performance, factors, or holdings.")

    # Display history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Ask a question about your portfolio..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build message list with context injected in first message
        messages = []
        for i, msg in enumerate(st.session_state.chat_messages):
            content = msg["content"]
            if i == 0:
                content = f"Portfolio Data:\n{st.session_state.portfolio_context}\n\nQuestion: {content}"
            messages.append({"role": msg["role"], "content": content})

        # Stream response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            system = PORTFOLIO_SYSTEM
            for chunk in stream_chat(system, messages):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": full_response,
        })
