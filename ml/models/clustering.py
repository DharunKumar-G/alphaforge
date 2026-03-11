"""
Stock clustering by factor profile using K-Means + PCA visualization.
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from loguru import logger


FEATURE_COLS = ["momentum", "value", "quality", "volatility"]


def cluster_stocks(scores: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    """
    Cluster stocks by factor profile.
    
    Args:
        scores: DataFrame with momentum, value, quality, volatility columns
        n_clusters: number of clusters
    
    Returns:
        DataFrame with cluster labels and 2D PCA coordinates
    """
    features = scores[FEATURE_COLS].dropna()
    if len(features) < n_clusters:
        logger.warning("Not enough stocks to cluster")
        return pd.DataFrame()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    # K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # PCA for 2D visualization
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X_scaled)

    result = features.copy()
    result["cluster"] = labels
    result["pca_x"] = coords[:, 0]
    result["pca_y"] = coords[:, 1]
    result["cluster_label"] = result["cluster"].apply(_label_cluster)

    # Add composite score
    if "composite" in scores.columns:
        result["composite"] = scores.loc[features.index, "composite"]

    explained = pca.explained_variance_ratio_
    logger.info(f"PCA explains {explained.sum():.1%} variance. Clusters: {n_clusters}")

    return result


def _label_cluster(cluster_id: int) -> str:
    labels = {
        0: "High Momentum / Low Value",
        1: "Deep Value / Low Quality",
        2: "Quality Growth",
        3: "Low Volatility Income",
        4: "Turnaround / High Risk",
    }
    return labels.get(cluster_id, f"Cluster {cluster_id}")


def optimal_clusters(scores: pd.DataFrame, max_k: int = 10) -> dict:
    """
    Find optimal number of clusters using inertia (elbow method).
    Returns dict of k → inertia for plotting.
    """
    features = scores[FEATURE_COLS].dropna()
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    inertias = {}
    for k in range(2, min(max_k + 1, len(features))):
        km = KMeans(n_clusters=k, random_state=42, n_init=5)
        km.fit(X)
        inertias[k] = km.inertia_

    return inertias


def cluster_summary(clustered: pd.DataFrame) -> pd.DataFrame:
    """Compute mean factor scores per cluster."""
    return clustered.groupby("cluster_label")[FEATURE_COLS + ["composite"]].mean().round(3)
