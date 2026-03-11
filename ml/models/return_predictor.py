"""
ML Return Predictor: Random Forest + XGBoost with walk-forward validation.
Predicts next-month stock returns from factor scores.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import xgboost as xgb
from loguru import logger


FEATURE_COLS = ["momentum", "value", "quality", "volatility"]
TARGET_COL = "next_month_return"


def build_features(scores_history: list, prices: pd.DataFrame) -> pd.DataFrame:
    """
    Build ML training dataset from factor scores history and prices.
    Each row = (symbol, date, factor scores, next_month_return).
    """
    rows = []
    for i, (date, scores) in enumerate(scores_history[:-1]):
        next_date, _ = scores_history[i + 1]
        for sym in scores.index:
            if sym not in prices.columns:
                continue
            try:
                price_now = prices.loc[prices.index <= date, sym].iloc[-1]
                price_next = prices.loc[prices.index <= next_date, sym].iloc[-1]
                ret = price_next / price_now - 1
            except (IndexError, KeyError):
                continue

            row = {
                "symbol": sym,
                "date": date,
                "momentum": scores.loc[sym, "momentum"] if "momentum" in scores.columns else np.nan,
                "value": scores.loc[sym, "value"] if "value" in scores.columns else np.nan,
                "quality": scores.loc[sym, "quality"] if "quality" in scores.columns else np.nan,
                "volatility": scores.loc[sym, "volatility"] if "volatility" in scores.columns else np.nan,
                TARGET_COL: ret,
            }
            rows.append(row)

    df = pd.DataFrame(rows).dropna()
    return df


def train_random_forest(X_train: pd.DataFrame, y_train: pd.Series) -> tuple:
    """Train Random Forest. Returns (model, scaler)."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = RandomForestRegressor(n_estimators=200, max_depth=6,
                                   min_samples_leaf=5, random_state=42, n_jobs=-1)
    model.fit(X_scaled, y_train)
    return model, scaler


def train_xgboost(X_train: pd.DataFrame, y_train: pd.Series) -> tuple:
    """Train XGBoost. Returns (model, scaler)."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = xgb.XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.05,
                               subsample=0.8, colsample_bytree=0.8,
                               random_state=42, verbosity=0)
    model.fit(X_scaled, y_train)
    return model, scaler


def walk_forward_predict(dataset: pd.DataFrame, model_type: str = "rf",
                          train_periods: int = 24) -> pd.DataFrame:
    """
    Walk-forward validation.
    Train on train_periods months, predict next month, roll forward.
    
    Returns DataFrame with actual vs predicted returns.
    """
    dates = sorted(dataset["date"].unique())
    results = []

    for i in range(train_periods, len(dates)):
        train_dates = dates[i - train_periods:i]
        test_date = dates[i]

        train_df = dataset[dataset["date"].isin(train_dates)]
        test_df = dataset[dataset["date"] == test_date]

        if train_df.empty or test_df.empty:
            continue

        X_train = train_df[FEATURE_COLS].fillna(0)
        y_train = train_df[TARGET_COL]
        X_test = test_df[FEATURE_COLS].fillna(0)

        try:
            if model_type == "rf":
                model, scaler = train_random_forest(X_train, y_train)
            else:
                model, scaler = train_xgboost(X_train, y_train)

            preds = model.predict(scaler.transform(X_test))

            for j, (_, row) in enumerate(test_df.iterrows()):
                results.append({
                    "date": test_date,
                    "symbol": row["symbol"],
                    "actual": row[TARGET_COL],
                    "predicted": preds[j],
                })
        except Exception as e:
            logger.warning(f"Walk-forward failed at {test_date}: {e}")

    return pd.DataFrame(results)


def feature_importance(X_train: pd.DataFrame, y_train: pd.Series) -> pd.Series:
    """Return feature importances from a trained Random Forest."""
    model, scaler = train_random_forest(X_train, y_train)
    return pd.Series(model.feature_importances_,
                     index=FEATURE_COLS).sort_values(ascending=False)
