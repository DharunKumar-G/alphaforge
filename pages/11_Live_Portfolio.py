"""
Live Portfolio Tracker — enter real holdings, see live factor scores and alerts.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from data.fetcher import fetch_close_matrix, fetch_fundamentals, fetch_prices
from data.store import get_connection
from core.factors.scorer import compute_composite_scores, score_to_signal
from core.risk.manager import compute_var
from config.settings import DEFAULT_FACTOR_WEIGHTS

st.set_page_config(page_title="Live Portfolio — AlphaForge", layout="wide")
st.title("Live Portfolio Tracker")

# ---- Add Holdings ----
with st.expander("Add / Edit Holdings"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_sym = st.text_input("Symbol (e.g. INFY.NS)")
    with col2:
        new_shares = st.number_input("Shares", min_value=0.0, value=100.0)
    with col3:
        new_cost = st.number_input("Avg Cost (₹)", min_value=0.0, value=0.0)
    with col4:
        new_date = st.date_input("Purchase Date", datetime.today())
        add_btn = st.button("Add Holding")

    if add_btn and new_sym:
        conn = get_connection()
        conn.execute("""
            INSERT OR REPLACE INTO live_portfolio (symbol, shares, avg_cost, purchase_date)
            VALUES (?, ?, ?, ?)
        """, (new_sym.upper().strip(), new_shares, new_cost, str(new_date)))
        conn.commit()
        conn.close()
        st.success(f"Added {new_sym}")
        st.rerun()

# ---- Load Holdings ----
conn = get_connection()
holdings_df = pd.read_sql("SELECT * FROM live_portfolio WHERE shares > 0", conn)
conn.close()

if holdings_df.empty:
    st.info("No holdings added yet. Add stocks above.")
    st.stop()

symbols = holdings_df["symbol"].tolist()

# ---- Fetch live data ----
@st.cache_data(ttl=900, show_spinner="Fetching live prices...")
def fetch_live(syms):
    prices = fetch_close_matrix(syms, start="2022-01-01")
    fundamentals = {}
    for sym in syms:
        f = fetch_fundamentals(sym)
        if f:
            fundamentals[sym] = f
    return prices, fundamentals

prices, fundamentals = fetch_live(symbols)

# ---- Current prices & P&L ----
current_prices = {}
for sym in symbols:
    if sym in prices.columns:
        current_prices[sym] = prices[sym].iloc[-1]

holdings_df["current_price"] = holdings_df["symbol"].map(current_prices)
holdings_df["market_value"] = holdings_df["shares"] * holdings_df["current_price"]
holdings_df["cost_basis"] = holdings_df["shares"] * holdings_df["avg_cost"]
holdings_df["pnl"] = holdings_df["market_value"] - holdings_df["cost_basis"]
holdings_df["pnl_pct"] = (holdings_df["pnl"] / holdings_df["cost_basis"].replace(0, float("nan"))) * 100
holdings_df["weight"] = holdings_df["market_value"] / holdings_df["market_value"].sum()

# ---- Factor Scores ----
if not prices.empty:
    scores = compute_composite_scores(prices, fundamentals, DEFAULT_FACTOR_WEIGHTS)
    for col in ["momentum", "value", "quality", "volatility", "composite"]:
        if col in scores.columns:
            holdings_df[col] = holdings_df["symbol"].map(scores[col].to_dict())
    holdings_df["signal"] = holdings_df["composite"].apply(
        lambda x: score_to_signal(x) if pd.notna(x) else "N/A"
    )

# ---- Summary ----
total_value = holdings_df["market_value"].sum()
total_pnl = holdings_df["pnl"].sum()
total_cost = holdings_df["cost_basis"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Portfolio Value", f"₹{total_value:,.0f}")
col2.metric("Total P&L", f"₹{total_pnl:,.0f}",
            f"{(total_pnl / total_cost * 100):.1f}% overall")
col3.metric("Holdings", len(holdings_df))
col4.metric("Avg Composite Score",
            f"{holdings_df['composite'].mean():.2f}" if "composite" in holdings_df.columns else "N/A")

st.divider()

# ---- Holdings Table ----
st.subheader("Holdings")
display_cols = ["symbol", "shares", "avg_cost", "current_price",
                "market_value", "pnl", "pnl_pct", "weight",
                "composite", "signal"]
display_cols = [c for c in display_cols if c in holdings_df.columns]

st.dataframe(
    holdings_df[display_cols].style
    .format({
        "current_price": "₹{:.2f}",
        "avg_cost": "₹{:.2f}",
        "market_value": "₹{:,.0f}",
        "pnl": "₹{:,.0f}",
        "pnl_pct": "{:.1f}%",
        "weight": "{:.1%}",
        "composite": "{:.3f}",
    })
    .applymap(lambda v: "color:#00c853" if isinstance(v, (int, float)) and v > 0
              else ("color:#d50000" if isinstance(v, (int, float)) and v < 0 else ""),
              subset=["pnl", "pnl_pct"]),
    use_container_width=True,
)

# Delete holding
with st.expander("Remove a Holding"):
    del_sym = st.selectbox("Select to remove", symbols)
    if st.button("Remove", type="secondary"):
        conn = get_connection()
        conn.execute("DELETE FROM live_portfolio WHERE symbol = ?", (del_sym,))
        conn.commit()
        conn.close()
        st.rerun()
