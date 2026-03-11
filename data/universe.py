"""
Nifty 500 universe management.
Returns list of NSE symbols with sector mapping.
"""
import pandas as pd
import requests
from pathlib import Path
from loguru import logger

CACHE_PATH = Path("data/cache/universe.csv")

# Nifty 500 sector buckets (sampled — extend as needed)
NIFTY500_SYMBOLS = {
    # IT
    "TCS.NS": "IT", "INFY.NS": "IT", "WIPRO.NS": "IT", "HCLTECH.NS": "IT",
    "TECHM.NS": "IT", "LTIM.NS": "IT", "MPHASIS.NS": "IT", "PERSISTENT.NS": "IT",
    # Banks
    "HDFCBANK.NS": "Banks", "ICICIBANK.NS": "Banks", "AXISBANK.NS": "Banks",
    "KOTAKBANK.NS": "Banks", "SBIN.NS": "Banks", "BANDHANBNK.NS": "Banks",
    "FEDERALBNK.NS": "Banks", "IDFCFIRSTB.NS": "Banks",
    # FMCG
    "HINDUNILVR.NS": "FMCG", "ITC.NS": "FMCG", "NESTLEIND.NS": "FMCG",
    "BRITANNIA.NS": "FMCG", "DABUR.NS": "FMCG", "MARICO.NS": "FMCG",
    # Auto
    "MARUTI.NS": "Auto", "TATAMOTORS.NS": "Auto", "M&M.NS": "Auto",
    "BAJAJ-AUTO.NS": "Auto", "HEROMOTOCO.NS": "Auto", "EICHERMOT.NS": "Auto",
    # Pharma
    "SUNPHARMA.NS": "Pharma", "DRREDDY.NS": "Pharma", "CIPLA.NS": "Pharma",
    "DIVISLAB.NS": "Pharma", "APOLLOHOSP.NS": "Pharma", "LUPIN.NS": "Pharma",
    # Energy
    "RELIANCE.NS": "Energy", "ONGC.NS": "Energy", "BPCL.NS": "Energy",
    "IOC.NS": "Energy", "POWERGRID.NS": "Energy", "NTPC.NS": "Energy",
    # Metals
    "TATASTEEL.NS": "Metals", "HINDALCO.NS": "Metals", "JSWSTEEL.NS": "Metals",
    "SAIL.NS": "Metals", "VEDL.NS": "Metals", "COALINDIA.NS": "Metals",
    # Financials (NBFC)
    "BAJFINANCE.NS": "Financials", "BAJAJFINSV.NS": "Financials",
    "CHOLAFIN.NS": "Financials", "HDFCLIFE.NS": "Financials",
    "SBILIFE.NS": "Financials", "ICICIGI.NS": "Financials",
    # Infra / Capital Goods
    "LT.NS": "Infra", "ADANIPORTS.NS": "Infra", "SIEMENS.NS": "Infra",
    "ABB.NS": "Infra", "BEL.NS": "Infra", "HAL.NS": "Infra",
    # Consumer Durables
    "TITAN.NS": "ConsumerDurables", "HAVELLS.NS": "ConsumerDurables",
    "VOLTAS.NS": "ConsumerDurables", "DIXON.NS": "ConsumerDurables",
    # Telecom
    "BHARTIARTL.NS": "Telecom", "INDUSTOWER.NS": "Telecom",
    # Cement
    "ULTRACEMCO.NS": "Cement", "SHREECEM.NS": "Cement", "AMBUJACEM.NS": "Cement",
    # Chemicals
    "PIDILITIND.NS": "Chemicals", "SRF.NS": "Chemicals", "ATUL.NS": "Chemicals",
}


def get_universe(reload: bool = False) -> pd.DataFrame:
    """Return universe as DataFrame with symbol and sector columns."""
    if CACHE_PATH.exists() and not reload:
        return pd.read_csv(CACHE_PATH)

    rows = [{"symbol": sym, "sector": sec} for sym, sec in NIFTY500_SYMBOLS.items()]
    df = pd.DataFrame(rows)
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CACHE_PATH, index=False)
    logger.info(f"Universe loaded: {len(df)} stocks")
    return df


def get_symbols(sector: str = None) -> list[str]:
    df = get_universe()
    if sector:
        df = df[df["sector"] == sector]
    return df["symbol"].tolist()


def get_sectors() -> list[str]:
    return sorted(get_universe()["sector"].unique().tolist())
