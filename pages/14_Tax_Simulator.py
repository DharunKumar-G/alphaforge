"""
India-specific Tax & Transaction Cost Simulator.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from config.settings import (STT_DELIVERY, BROKERAGE, GST_ON_BROKERAGE,
                              STCG_TAX_RATE, LTCG_TAX_RATE, LTCG_EXEMPTION)

st.set_page_config(page_title="Tax Simulator — AlphaForge", layout="wide")
st.title("Tax & Transaction Cost Simulator (India)")
st.caption("Models STT, brokerage, GST, STCG/LTCG for realistic post-tax return estimation.")

with st.sidebar:
    st.header("Transaction Parameters")
    trade_value = st.number_input("Trade Value (₹)", min_value=10000, value=100000, step=10000)
    n_trades_per_year = st.slider("Trades per Year", 1, 100, 24)
    holding_period_days = st.slider("Average Holding Period (days)", 1, 730, 180)
    portfolio_value = st.number_input("Portfolio Value (₹)", min_value=100000,
                                       value=1000000, step=100000)
    annual_return = st.slider("Gross Annual Return (%)", 0, 50, 20) / 100

# ---- Per-trade costs ----
stt = trade_value * STT_DELIVERY
brokerage = trade_value * BROKERAGE
gst = brokerage * GST_ON_BROKERAGE
sebi_charges = trade_value * 0.000001
stamp_duty = trade_value * 0.00015  # 0.015% on buy side
total_per_trade = stt + brokerage + gst + sebi_charges + stamp_duty

col1, col2, col3 = st.columns(3)
col1.metric("STT per Trade", f"₹{stt:.2f}")
col2.metric("Brokerage + GST", f"₹{brokerage + gst:.2f}")
col3.metric("Total Cost per Trade", f"₹{total_per_trade:.2f}")

st.divider()

# ---- Annual transaction cost drag ----
annual_trade_cost = total_per_trade * n_trades_per_year * 2  # buy + sell
cost_as_pct = annual_trade_cost / portfolio_value
st.metric("Annual Transaction Costs", f"₹{annual_trade_cost:,.0f}",
          f"{cost_as_pct:.2%} drag on portfolio")

# ---- Capital Gains Tax ----
st.subheader("Capital Gains Tax Impact")

gross_gain = portfolio_value * annual_return

if holding_period_days < 365:
    # STCG
    taxable = gross_gain
    tax = taxable * STCG_TAX_RATE
    tax_type = "STCG (20%)"
else:
    # LTCG — exempt up to 1.25L
    taxable = max(0, gross_gain - LTCG_EXEMPTION)
    tax = taxable * LTCG_TAX_RATE
    tax_type = "LTCG (12.5% above ₹1.25L)"

net_gain = gross_gain - tax - annual_trade_cost
net_return = net_gain / portfolio_value

col1, col2, col3, col4 = st.columns(4)
col1.metric("Gross Gain", f"₹{gross_gain:,.0f}", f"{annual_return:.1%}")
col2.metric(f"Tax ({tax_type})", f"₹{tax:,.0f}")
col3.metric("Transaction Costs", f"₹{annual_trade_cost:,.0f}")
col4.metric("Net Gain", f"₹{net_gain:,.0f}", f"{net_return:.1%} net return")

# ---- Rebalance frequency vs tax drag ----
st.subheader("Optimal Rebalance Frequency")
st.caption("More rebalancing = higher costs but potentially better alpha capture")

freq_data = []
for freq, trades in [(1, 4), (2, 8), (4, 12), (6, 16), (12, 24), (24, 52)]:
    label = {1: "Quarterly", 2: "Bi-Monthly", 4: "Monthly",
             6: "3x/month", 12: "2x/month", 24: "Weekly"}[freq]
    cost = total_per_trade * trades * 2
    tax_drag = gross_gain * (STCG_TAX_RATE if trades > 4 else LTCG_TAX_RATE * 0.7)
    net = gross_gain - cost - tax_drag
    freq_data.append({
        "Frequency": label,
        "Transaction Costs": cost,
        "Estimated Tax": tax_drag,
        "Net Gain": net,
        "Net Return": net / portfolio_value,
    })

freq_df = pd.DataFrame(freq_data)
fig = px.bar(freq_df, x="Frequency", y=["Transaction Costs", "Estimated Tax"],
              barmode="stack", title="Cost Breakdown by Rebalance Frequency",
              template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.dataframe(freq_df.set_index("Frequency").style.format({
    "Transaction Costs": "₹{:,.0f}",
    "Estimated Tax": "₹{:,.0f}",
    "Net Gain": "₹{:,.0f}",
    "Net Return": "{:.1%}",
}), use_container_width=True)
