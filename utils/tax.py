"""
India tax calculations for portfolio returns.
"""
from config.settings import (STCG_TAX_RATE, LTCG_TAX_RATE, LTCG_EXEMPTION,
                              STT_DELIVERY, BROKERAGE, GST_ON_BROKERAGE)


def compute_transaction_cost(trade_value: float) -> dict:
    stt = trade_value * STT_DELIVERY
    brokerage = trade_value * BROKERAGE
    gst = brokerage * GST_ON_BROKERAGE
    sebi = trade_value * 0.000001
    stamp = trade_value * 0.00015
    total = stt + brokerage + gst + sebi + stamp
    return {"stt": stt, "brokerage": brokerage, "gst": gst,
            "sebi": sebi, "stamp": stamp, "total": total}


def compute_capital_gains_tax(gain: float, holding_days: int) -> dict:
    if holding_days < 365:
        taxable = gain
        tax = max(0, taxable * STCG_TAX_RATE)
        tax_type = "STCG"
    else:
        taxable = max(0, gain - LTCG_EXEMPTION)
        tax = max(0, taxable * LTCG_TAX_RATE)
        tax_type = "LTCG"
    return {"tax_type": tax_type, "taxable_gain": taxable, "tax": tax,
            "net_gain": gain - tax}


def post_tax_cagr(gross_cagr: float, portfolio_value: float,
                  holding_days: int, n_years: float) -> float:
    """Approximate post-tax CAGR."""
    gross_gain = portfolio_value * ((1 + gross_cagr) ** n_years - 1)
    tax_info = compute_capital_gains_tax(gross_gain, holding_days)
    net_gain = tax_info["net_gain"]
    return (1 + net_gain / portfolio_value) ** (1 / n_years) - 1
