"""
Macro Dashboard — India VIX, bond yields, USD/INR, crude oil, FII/DII flows.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data.fetcher import fetch_prices

st.set_page_config(page_title="Macro Dashboard — AlphaForge", layout="wide")
st.title("Macro Dashboard")
st.caption("Key macroeconomic indicators for Indian markets.")

MACRO_SYMBOLS = {
    "India VIX": "^INDIAVIX",
    "Nifty 50": "^NSEI",
    "USD/INR": "USDINR=X",
    "Crude Oil (WTI)": "CL=F",
    "Gold (USD)": "GC=F",
    "US 10Y Bond": "^TNX",
}

start = st.date_input("Start Date", pd.Timestamp("2020-01-01"))

@st.cache_data(ttl=1800, show_spinner="Loading macro data...")
def load_macro(start):
    data = {}
    for name, sym in MACRO_SYMBOLS.items():
        df = fetch_prices(sym, start=str(start))
        if not df.empty:
            data[name] = df["Close"]
    return data

macro_data = load_macro(start)

if not macro_data:
    st.error("Failed to load macro data.")
    st.stop()

# ---- Summary metrics ----
cols = st.columns(len(macro_data))
for i, (name, series) in enumerate(macro_data.items()):
    current = series.iloc[-1]
    change = series.pct_change().iloc[-1]
    cols[i].metric(name, f"{current:.2f}",
                   f"{change:+.2%}" if not pd.isna(change) else "N/A")

st.divider()

# ---- Charts ----
tab1, tab2 = st.tabs(["Individual Charts", "Correlation Matrix"])

with tab1:
    selected = st.multiselect("Select indicators", list(macro_data.keys()),
                               default=list(macro_data.keys())[:3])

    for name in selected:
        series = macro_data[name]
        fig = go.Figure(go.Scatter(x=series.index, y=series.values,
                                    mode="lines", name=name,
                                    line=dict(color="#00c853")))
        fig.update_layout(title=name, template="plotly_dark", height=280)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    if len(macro_data) >= 2:
        df_macro = pd.DataFrame(macro_data)
        ret_macro = df_macro.pct_change().dropna()
        corr = ret_macro.corr()

        fig_corr = px.imshow(corr, color_continuous_scale="RdYlGn",
                              zmin=-1, zmax=1,
                              title="Macro Indicator Correlation Matrix",
                              template="plotly_dark")
        st.plotly_chart(fig_corr, use_container_width=True)

        # Insight
        if "Nifty 50" in corr.columns and "USD/INR" in corr.columns:
            nifty_usdinr_corr = corr.loc["Nifty 50", "USD/INR"]
            if abs(nifty_usdinr_corr) > 0.3:
                direction = "negatively" if nifty_usdinr_corr < 0 else "positively"
                st.info(f"Nifty 50 is {direction} correlated with USD/INR "
                        f"({nifty_usdinr_corr:.2f}) — currency risk is material.")
