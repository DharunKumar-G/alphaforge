"""
Watchlist — track stocks with daily AI commentary.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from data.store import get_connection
from data.fetcher import fetch_close_matrix, fetch_fundamentals
from core.factors.scorer import compute_composite_scores, score_to_signal
from ai.client import chat
from config.settings import DEFAULT_FACTOR_WEIGHTS

st.set_page_config(page_title="Watchlist — AlphaForge", layout="wide")
st.title("Watchlist")

COMMENTARY_SYSTEM = """You are a quantitative analyst producing brief daily stock commentary 
for Indian equities. For each stock, write a single crisp sentence covering:
momentum trend, quality/value status, and any notable risk.
Be specific. Use numbers. Max 25 words per stock. Format: "SYMBOL: <commentary>" """

# ---- Add stock ----
col1, col2 = st.columns([3, 1])
with col1:
    new_sym = st.text_input("Add to watchlist (e.g. TCS.NS)")
with col2:
    st.write("")
    st.write("")
    add = st.button("Add", type="primary")

if add and new_sym:
    sym = new_sym.strip().upper()
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO watchlist (symbol, added_at)
        VALUES (?, ?)
    """, (sym, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    st.success(f"Added {sym} to watchlist")
    st.rerun()

# ---- Load watchlist ----
conn = get_connection()
watchlist_df = pd.read_sql("SELECT * FROM watchlist ORDER BY added_at DESC", conn)
conn.close()

if watchlist_df.empty:
    st.info("Your watchlist is empty. Add some stocks above.")
    st.stop()

symbols = watchlist_df["symbol"].tolist()

# ---- Fetch data ----
@st.cache_data(ttl=900, show_spinner="Loading watchlist data...")
def load_watchlist_data(syms):
    prices = fetch_close_matrix(syms, start="2022-01-01")
    fundamentals = {}
    for sym in syms:
        f = fetch_fundamentals(sym)
        if f:
            fundamentals[sym] = f
    return prices, fundamentals

prices, fundamentals = load_watchlist_data(symbols)

# ---- Factor scores ----
scores = pd.DataFrame()
if not prices.empty:
    scores = compute_composite_scores(prices, fundamentals, DEFAULT_FACTOR_WEIGHTS)
    scores["signal"] = scores["composite"].apply(score_to_signal)

# ---- Display ----
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Watchlist")
    if not scores.empty:
        watchlist_with_scores = watchlist_df.set_index("symbol").join(
            scores[["momentum", "value", "quality", "volatility", "composite", "signal"]]
        ).reset_index()
        st.dataframe(
            watchlist_with_scores.style.format({
                "momentum": "{:.3f}", "value": "{:.3f}",
                "quality": "{:.3f}", "volatility": "{:.3f}",
                "composite": "{:.3f}",
            }),
            use_container_width=True,
        )

with col2:
    remove_sym = st.selectbox("Remove from watchlist", ["--"] + symbols)
    if st.button("Remove") and remove_sym != "--":
        conn = get_connection()
        conn.execute("DELETE FROM watchlist WHERE symbol = ?", (remove_sym,))
        conn.commit()
        conn.close()
        st.rerun()

# ---- AI Commentary ----
st.subheader("AI Daily Commentary")
if st.button("Generate AI Commentary for All Stocks", type="primary"):
    if scores.empty:
        st.warning("No factor scores available.")
    else:
        context = "Factor scores for watchlist stocks:\n"
        for sym in symbols:
            if sym in scores.index:
                row = scores.loc[sym]
                context += (f"{sym}: momentum={row.get('momentum', 0):.2f}, "
                            f"value={row.get('value', 0):.2f}, "
                            f"quality={row.get('quality', 0):.2f}, "
                            f"volatility={row.get('volatility', 0):.2f}, "
                            f"composite={row.get('composite', 0):.2f}\n")

        with st.spinner("Generating commentary..."):
            commentary = chat(COMMENTARY_SYSTEM, context, max_tokens=600)

        st.session_state.watchlist_commentary = commentary

if "watchlist_commentary" in st.session_state:
    st.markdown(st.session_state.watchlist_commentary)
