"""
ML Models — Return Predictor, Stock Clustering, Anomaly Detection.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data.fetcher import fetch_close_matrix, fetch_fundamentals
from data.universe import get_symbols
from core.factors.scorer import compute_composite_scores
from ml.models.return_predictor import build_features, walk_forward_predict, feature_importance, FEATURE_COLS
from ml.models.clustering import cluster_stocks, cluster_summary, optimal_clusters
from ml.models.anomaly import detect_return_anomalies, portfolio_anomaly_report
from config.settings import DEFAULT_FACTOR_WEIGHTS

st.set_page_config(page_title="ML Models — AlphaForge", layout="wide")
st.title("Machine Learning Models")

tab1, tab2, tab3 = st.tabs(["Return Predictor", "Stock Clustering", "Anomaly Detection"])

# ---- Shared data load ----
@st.cache_data(ttl=3600, show_spinner="Loading data for ML...")
def load_ml_data():
    symbols = get_symbols()[:40]
    prices = fetch_close_matrix(symbols, start="2018-01-01")
    fundamentals = {}
    for sym in symbols[:30]:
        f = fetch_fundamentals(sym)
        if f:
            fundamentals[sym] = f
    scores = compute_composite_scores(prices, fundamentals, DEFAULT_FACTOR_WEIGHTS)
    return prices, fundamentals, scores, symbols

prices, fundamentals, scores, symbols = load_ml_data()

# ======== TAB 1: Return Predictor ========
with tab1:
    st.subheader("ML Return Predictor")
    st.caption("Trains Random Forest / XGBoost on factor scores to predict next-month returns. "
               "Walk-forward validated.")

    col1, col2 = st.columns([1, 2])
    with col1:
        model_type = st.selectbox("Model", ["Random Forest", "XGBoost"])
        train_periods = st.slider("Training Window (months)", 12, 36, 24)
        run_ml = st.button("Train & Validate", type="primary")

    if run_ml:
        if "scores_history" not in st.session_state.get("backtest_result", {}):
            st.warning("Run a backtest first to get scores history for ML training.")
        else:
            scores_history = st.session_state.backtest_result["scores_history"]
            with st.spinner("Training model with walk-forward validation..."):
                dataset = build_features(scores_history, prices)
                model_key = "rf" if "Random" in model_type else "xgb"
                results = walk_forward_predict(dataset, model_type=model_key,
                                               train_periods=train_periods)
                st.session_state.ml_results = results

    if "ml_results" in st.session_state:
        results = st.session_state.ml_results
        if not results.empty:
            corr = results[["actual", "predicted"]].corr().iloc[0, 1]
            st.metric("Prediction-Actual Correlation", f"{corr:.3f}")

            fig = px.scatter(results, x="actual", y="predicted",
                             title="Predicted vs Actual Returns",
                             trendline="ols",
                             template="plotly_dark",
                             labels={"actual": "Actual Return", "predicted": "Predicted Return"})
            fig.update_traces(marker=dict(opacity=0.4, size=4))
            st.plotly_chart(fig, use_container_width=True)

            # Feature importance
            st.subheader("Factor Importance")
            train_data = build_features(
                st.session_state.backtest_result["scores_history"], prices
            ) if "backtest_result" in st.session_state else pd.DataFrame()

            if not train_data.empty:
                importance = feature_importance(train_data[FEATURE_COLS].fillna(0),
                                                train_data["next_month_return"])
                fig_imp = px.bar(importance.reset_index(),
                                 x="index", y=0, title="Feature Importance",
                                 template="plotly_dark",
                                 labels={"index": "Factor", 0: "Importance"})
                st.plotly_chart(fig_imp, use_container_width=True)

# ======== TAB 2: Clustering ========
with tab2:
    st.subheader("Stock Clustering by Factor Profile")
    st.caption("K-Means clusters stocks by factor scores. Visualized in 2D via PCA.")

    col1, col2 = st.columns([1, 3])
    with col1:
        n_clusters = st.slider("Number of Clusters", 2, 8, 5)
        run_cluster = st.button("Run Clustering", type="primary")

    if run_cluster:
        with st.spinner("Clustering stocks..."):
            clustered = cluster_stocks(scores, n_clusters=n_clusters)
            st.session_state.clustered = clustered

    if "clustered" in st.session_state:
        clustered = st.session_state.clustered
        if not clustered.empty:
            fig_cluster = px.scatter(
                clustered.reset_index(),
                x="pca_x", y="pca_y",
                color="cluster_label",
                hover_name="symbol" if "symbol" in clustered.reset_index().columns else "index",
                title="Stock Clusters (PCA 2D Projection)",
                template="plotly_dark",
                height=500,
            )
            st.plotly_chart(fig_cluster, use_container_width=True)

            st.subheader("Cluster Summary")
            summary = cluster_summary(clustered)
            st.dataframe(summary.style.background_gradient(cmap="Greens"), use_container_width=True)

# ======== TAB 3: Anomaly Detection ========
with tab3:
    st.subheader("Anomaly Detection")
    st.caption("Flags unusual price moves using Isolation Forest + Z-score.")

    col1, col2 = st.columns([1, 2])
    with col1:
        symbol_choice = st.selectbox("Select Stock", symbols)
        contamination = st.slider("Sensitivity (contamination)", 0.01, 0.15, 0.05, 0.01)
        run_anomaly = st.button("Detect Anomalies", type="primary")

    if run_anomaly:
        with st.spinner("Running anomaly detection..."):
            stock_prices = prices.get(symbol_choice, pd.Series(dtype=float))
            if stock_prices.empty:
                st.error("No price data for selected stock.")
            else:
                rets = stock_prices.pct_change().dropna()
                anomalies = detect_return_anomalies(rets, contamination=contamination)
                st.session_state.anomalies = anomalies
                st.session_state.anomaly_symbol = symbol_choice

    if "anomalies" in st.session_state:
        anomalies = st.session_state.anomalies
        sym = st.session_state.anomaly_symbol

        n_anomalies = anomalies["is_anomaly"].sum() if "is_anomaly" in anomalies.columns else 0
        st.metric(f"Anomalous Days ({sym})", int(n_anomalies),
                  f"out of {len(anomalies)} trading days")

        if "anomaly_score" in anomalies.columns:
            fig_anom = go.Figure()
            normal = anomalies[~anomalies["is_anomaly"]]
            flagged = anomalies[anomalies["is_anomaly"]]

            fig_anom.add_trace(go.Scatter(x=normal.index, y=normal["return"],
                                           mode="markers",
                                           marker=dict(color="#00c853", size=3),
                                           name="Normal"))
            fig_anom.add_trace(go.Scatter(x=flagged.index, y=flagged["return"],
                                           mode="markers",
                                           marker=dict(color="#d50000", size=7, symbol="x"),
                                           name="Anomaly"))
            fig_anom.update_layout(
                title=f"{sym} — Daily Returns with Anomaly Flags",
                yaxis_tickformat=".1%",
                template="plotly_dark",
                height=400,
            )
            st.plotly_chart(fig_anom, use_container_width=True)
