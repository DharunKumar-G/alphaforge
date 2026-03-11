"""
AlphaForge — Quantitative Investment Research Platform
Entry point: run with `streamlit run app.py`
"""
import streamlit as st

st.set_page_config(
    page_title="AlphaForge",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("AlphaForge")
st.markdown(
    """
    **Quantitative Investment Research Platform — Indian Markets**

    Use the sidebar to navigate between modules.
    """
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Universe", "Nifty 500", "NSE")
with col2:
    st.metric("Factors", "4 Active", "Momentum · Value · Quality · Vol")
with col3:
    st.metric("Status", "Ready", "")
