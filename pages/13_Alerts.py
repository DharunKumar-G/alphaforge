"""
Alerts — regime changes, drawdown breaches, factor degradation, anomalies.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from data.store import get_connection
from data.fetcher import fetch_prices
from core.regime.detector import get_current_regime
from core.risk.manager import compute_var
from ml.models.anomaly import portfolio_anomaly_report
from data.fetcher import fetch_close_matrix
from config.settings import BENCHMARK, MAX_DRAWDOWN_ALERT

st.set_page_config(page_title="Alerts — AlphaForge", layout="wide")
st.title("Alerts & Monitoring")

# ---- Unread alerts from DB ----
conn = get_connection()
alerts_df = pd.read_sql(
    "SELECT * FROM alerts ORDER BY triggered_at DESC LIMIT 50", conn
)
conn.close()

# ---- Live checks ----
live_alerts = []

# Regime check
bench = fetch_prices(BENCHMARK, start="2022-01-01")
if not bench.empty:
    regime = get_current_regime(bench["Close"])
    conn = get_connection()
    last_regime = conn.execute(
        "SELECT regime FROM regime_history ORDER BY date DESC LIMIT 1"
    ).fetchone()
    conn.close()
    current_regime = regime["regime"]
    if last_regime and last_regime[0] != current_regime:
        live_alerts.append({
            "type": "regime_change",
            "severity": "high",
            "message": f"Regime changed: {last_regime[0]} → {current_regime}",
        })

# Backtest drawdown check
if "backtest_result" in st.session_state:
    returns = st.session_state.backtest_result.get("returns", pd.Series())
    if not returns.empty:
        cum = (1 + returns).cumprod()
        dd = (cum.iloc[-1] - cum.max()) / cum.max()
        if abs(dd) >= MAX_DRAWDOWN_ALERT:
            live_alerts.append({
                "type": "drawdown",
                "severity": "high",
                "message": f"Portfolio drawdown {dd:.1%} exceeds {MAX_DRAWDOWN_ALERT:.0%} threshold",
            })

# Anomaly check on live portfolio
conn = get_connection()
live_holdings = pd.read_sql("SELECT symbol FROM live_portfolio", conn)
conn.close()

if not live_holdings.empty:
    syms = live_holdings["symbol"].tolist()
    try:
        prices = fetch_close_matrix(syms, start="2023-01-01")
        returns_dict = {sym: prices[sym].pct_change().dropna()
                        for sym in syms if sym in prices.columns}
        anomaly_report = portfolio_anomaly_report(returns_dict)
        for _, row in anomaly_report.iterrows():
            live_alerts.append({
                "type": "anomaly",
                "severity": row.get("severity", "medium"),
                "message": (f"{row['symbol']} — unusual move: "
                            f"{row.get('return_today', 0):.1%} "
                            f"(Z-score: {row.get('z_score', 0):.1f})"),
            })
    except Exception:
        pass

# ---- Display ----
total = len(live_alerts) + len(alerts_df)
st.metric("Active Alerts", len(live_alerts), f"{len(alerts_df)} historical")

if not live_alerts and alerts_df.empty:
    st.success("All clear! No active alerts.")
else:
    if live_alerts:
        st.subheader("Live Alerts")
        for alert in live_alerts:
            if alert["severity"] == "high":
                st.error(f"🔴 **{alert['type'].replace('_', ' ').title()}**: {alert['message']}")
            else:
                st.warning(f"🟡 **{alert['type'].replace('_', ' ').title()}**: {alert['message']}")

            # Save to DB
            conn = get_connection()
            conn.execute("""
                INSERT INTO alerts (alert_type, message, severity, triggered_at)
                VALUES (?, ?, ?, ?)
            """, (alert["type"], alert["message"], alert["severity"],
                  datetime.now().isoformat()))
            conn.commit()
            conn.close()

    if not alerts_df.empty:
        st.subheader("Alert History")
        st.dataframe(alerts_df[["triggered_at", "alert_type", "severity", "message"]],
                     use_container_width=True)
        if st.button("Clear History"):
            conn = get_connection()
            conn.execute("DELETE FROM alerts")
            conn.commit()
            conn.close()
            st.rerun()
