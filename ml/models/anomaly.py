"""
Anomaly detection in stock returns using Isolation Forest + Z-score.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from loguru import logger


def detect_return_anomalies(returns: pd.Series, contamination: float = 0.05,
                             window: int = 63) -> pd.DataFrame:
    """
    Detect anomalous return days using Isolation Forest.
    
    Args:
        returns: daily return series for a single stock or portfolio
        contamination: expected fraction of anomalies
        window: rolling window for features
    
    Returns:
        DataFrame with anomaly_score, is_anomaly, z_score columns
    """
    df = pd.DataFrame({"return": returns})
    df["rolling_mean"] = returns.rolling(window).mean()
    df["rolling_std"] = returns.rolling(window).std()
    df["z_score"] = (returns - df["rolling_mean"]) / df["rolling_std"]
    df["rolling_vol"] = returns.rolling(21).std()

    # Features for Isolation Forest
    features = df[["return", "z_score", "rolling_vol"]].dropna()

    if len(features) < 50:
        return df

    iso = IsolationForest(contamination=contamination, random_state=42)
    scores = iso.fit_predict(features)
    anomaly_scores = iso.score_samples(features)

    df.loc[features.index, "if_label"] = scores  # -1 = anomaly, 1 = normal
    df.loc[features.index, "anomaly_score"] = -anomaly_scores  # higher = more anomalous

    # Z-score based flag (|z| > 3 = anomaly)
    df["z_anomaly"] = df["z_score"].abs() > 3
    df["is_anomaly"] = (df["if_label"] == -1) | df["z_anomaly"]

    return df


def portfolio_anomaly_report(returns_dict: dict[str, pd.Series],
                              threshold: float = 3.0) -> pd.DataFrame:
    """
    Scan all portfolio holdings for anomalous recent returns.
    
    Returns:
        DataFrame of stocks with recent anomalies, sorted by severity.
    """
    alerts = []
    for symbol, returns in returns_dict.items():
        if returns.empty or len(returns) < 30:
            continue
        recent_return = returns.iloc[-1]
        mean = returns.rolling(63).mean().iloc[-1]
        std = returns.rolling(63).std().iloc[-1]
        if std and std > 0:
            z = (recent_return - mean) / std
            if abs(z) > threshold:
                alerts.append({
                    "symbol": symbol,
                    "return_today": recent_return,
                    "z_score": z,
                    "severity": "high" if abs(z) > 4 else "medium",
                    "direction": "down" if recent_return < 0 else "up",
                })

    if not alerts:
        return pd.DataFrame()

    return (pd.DataFrame(alerts)
            .sort_values("z_score", key=abs, ascending=False)
            .reset_index(drop=True))
