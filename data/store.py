"""
SQLite-backed data store for AlphaForge.
Handles universe, factor scores, backtest results, portfolio snapshots, alerts, journal.
"""
import sqlite3
from pathlib import Path
from config.settings import SQLITE_DB_PATH


def get_connection() -> sqlite3.Connection:
    Path(SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS universe (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            sector TEXT,
            market_cap REAL,
            is_active INTEGER DEFAULT 1,
            listed_date TEXT,
            delisted_date TEXT
        );

        CREATE TABLE IF NOT EXISTS price_data (
            symbol TEXT,
            date TEXT,
            open REAL, high REAL, low REAL,
            close REAL, volume REAL,
            PRIMARY KEY (symbol, date)
        );

        CREATE TABLE IF NOT EXISTS factor_scores (
            symbol TEXT,
            date TEXT,
            momentum REAL,
            value REAL,
            quality REAL,
            volatility REAL,
            composite REAL,
            PRIMARY KEY (symbol, date)
        );

        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_at TEXT,
            config_json TEXT,
            returns_json TEXT,
            metrics_json TEXT
        );

        CREATE TABLE IF NOT EXISTS live_portfolio (
            symbol TEXT PRIMARY KEY,
            shares REAL,
            avg_cost REAL,
            purchase_date TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS watchlist (
            symbol TEXT PRIMARY KEY,
            added_at TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT,
            message TEXT,
            severity TEXT,
            triggered_at TEXT,
            is_read INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS research_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            title TEXT,
            content TEXT,
            tags TEXT
        );

        CREATE TABLE IF NOT EXISTS regime_history (
            date TEXT PRIMARY KEY,
            regime TEXT,
            confidence REAL
        );
    """)

    conn.commit()
    conn.close()
    print("DB initialized.")


if __name__ == "__main__":
    init_db()
