<div align="center">

# 📈 AlphaForge

**Quantitative Investment Research Platform for Indian Markets**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://alphaforge-2oucww4kcb8ef3pzt8crdx.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Market](https://img.shields.io/badge/Market-NSE%20%7C%20BSE-orange)

*Stop picking stocks on gut feeling. Let the data decide.*

[**Live Demo →**](https://alphaforge-2oucww4kcb8ef3pzt8crdx.streamlit.app/)

</div>

---

## What Is AlphaForge?

AlphaForge is a full-stack quantitative finance platform that scores every stock in the Nifty 500 on 4 research-backed factors, builds and backtests a portfolio of top-ranked stocks, and uses AI + Machine Learning to explain, predict, and optimize your strategy — all in a browser.

Built for:
- Finance students learning quant investing
- Individual investors who want a systematic edge
- Quant interns building a portfolio project

---

## Features

### Core Engine
| Feature | Description |
|---|---|
| **4-Factor Scoring** | Momentum · Value · Quality · Low Volatility — scored and ranked across 70 NSE stocks |
| **Walk-Forward Backtester** | Simulate monthly rebalancing from 2015–today, compare vs Nifty 50 |
| **Performance Analytics** | CAGR, Sharpe, Sortino, Calmar, Max Drawdown, Alpha, Beta, Information Ratio |
| **Market Regime Detector** | Bull / Sideways / Bear classification using 4 signals with confidence score |
| **Risk Manager** | VaR, CVaR, drawdown monitor, sector concentration, correlation heatmap |

### AI (Google Gemini)
| Feature | Description |
|---|---|
| **Portfolio Chat** | Ask *"why did my portfolio drop in June 2022?"* — AI reads your backtest and answers |
| **Strategy Critique** | One-click AI analysis of your strategy's weaknesses and action items |
| **NL Stock Screener** | Type *"undervalued banking stocks with strong momentum"* — AI converts to filters |
| **Watchlist Commentary** | Daily one-line AI summary per stock: momentum, value, risk |

### Machine Learning
| Feature | Description |
|---|---|
| **Return Predictor** | Random Forest + XGBoost trained on factor scores, walk-forward validated |
| **Stock Clustering** | K-Means groups stocks by factor profile, visualized via PCA in 2D |
| **Anomaly Detection** | Isolation Forest flags unusual price moves with Z-scores |

### Advanced Quant
| Feature | Description |
|---|---|
| **Portfolio Optimizer** | Markowitz Max-Sharpe, Min-Variance, Risk Parity, Efficient Frontier |
| **Monte Carlo Simulation** | 1,000–5,000 paths, probability cone, VaR, probability of loss |
| **Sector Rotation Engine** | Tracks which sectors lead/lag by regime |
| **Tax Simulator** | India-specific: STT, GST, STCG/LTCG with optimal rebalance frequency |
| **Live Portfolio Tracker** | Enter real holdings, see P&L + live factor scores |
| **Macro Dashboard** | India VIX, USD/INR, Crude, Gold, US 10Y — with correlation matrix |

---

## Screenshots

> Dashboard · Backtester · Portfolio Optimizer · AI Chat

```
[ Dashboard ]          [ Backtester ]
  Regime: Bull 🟢        CAGR:      24.3%
  Top stocks ranked      Sharpe:     1.41
  Factor radar chart     Max DD:   -18.2%
                         Alpha:      9.1%

[ Portfolio Optimizer ] [ AI Chat ]
  Efficient Frontier      "Your strategy has high
  Monte Carlo cone         IT concentration in bull
  Risk Parity weights      regimes — consider a 30%
                           sector cap..."
```

---

## Tech Stack

```
Frontend    Streamlit (15 pages, dark theme)
Charts      Plotly (interactive, zoomable)
Data        yfinance — NSE/BSE historical prices + fundamentals
AI          Google Gemini (gemma-3-4b-it via google-genai SDK)
ML          scikit-learn · XGBoost · scipy
Storage     SQLite (portfolio, journal, alerts, regime history)
Language    Python 3.11
```

---

## Project Structure

```
AlphaForge/
├── app.py                        # Entry point
├── pages/                        # 15 Streamlit pages
│   ├── 1_Dashboard.py
│   ├── 2_Backtester.py
│   ├── 3_Factor_Analysis.py
│   ├── 4_Stock_Screener.py
│   ├── 5_Portfolio_Optimizer.py
│   ├── 6_ML_Models.py
│   ├── 7_Regime_Detector.py
│   ├── 8_Risk_Manager.py
│   ├── 9_AI_Chat.py
│   ├── 10_Research_Journal.py
│   ├── 11_Live_Portfolio.py
│   ├── 12_Macro_Dashboard.py
│   ├── 13_Alerts.py
│   ├── 14_Tax_Simulator.py
│   └── 15_Watchlist.py
├── core/
│   ├── factors/                  # momentum, value, quality, volatility, scorer
│   ├── backtesting/              # engine, performance, tearsheet
│   ├── regime/                   # detector, sector rotation
│   ├── risk/                     # manager, monte carlo
│   └── optimization/             # markowitz, risk parity, frontier
├── ml/
│   └── models/                   # return predictor, clustering, anomaly
├── ai/
│   ├── client.py                 # Gemini API wrapper
│   ├── portfolio_chat.py
│   ├── nl_screener.py
│   └── strategy_critique.py
├── data/
│   ├── fetcher.py                # yfinance wrapper with caching
│   ├── universe.py               # 70 NSE stocks with sector labels
│   └── store.py                  # SQLite schema + connection
└── config/
    └── settings.py               # Factor weights, risk limits, tax rates
```

---

## Run Locally

```bash
# 1. Clone
git clone https://github.com/DharunKumar-G/alphaforge.git
cd alphaforge

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API key
echo 'GEMINI_API_KEY=your_key_here' > .env

# 4. Launch
streamlit run app.py
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com/app/apikey).

---

## Deploy on Streamlit Cloud (Free)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select this repo · branch `master` · file `app.py`
4. Under **Advanced settings → Secrets**, add:
```toml
GEMINI_API_KEY = "your_key_here"
```
5. Click Deploy — live in ~3 minutes

---

## The 4 Factors Explained

| Factor | Signal | Why It Works |
|---|---|---|
| **Momentum** | 12-month return minus last month | Stocks trending up tend to keep going up — documented since 1993 |
| **Value** | Low PE, low PB, high dividend yield | Cheap stocks mean-revert to fair value over time |
| **Quality** | High ROE, low debt, strong margins | Great businesses compound wealth and survive downturns |
| **Low Volatility** | Low 63-day realized vol | Low-vol stocks are under-owned and deliver better risk-adjusted returns |

Each factor scores stocks 0–1 (percentile rank). The composite score is a weighted average. Default weights: Momentum 30% · Value 25% · Quality 25% · Volatility 20%.

---

## Key Metrics Explained

| Metric | What it means | Good benchmark |
|---|---|---|
| CAGR | Annualized return | > Nifty 50 + 5% |
| Sharpe Ratio | Return per unit of risk | > 1.0 |
| Max Drawdown | Worst peak-to-trough loss | < -25% |
| Alpha | Excess return over benchmark | > 5% |
| Beta | Market sensitivity | 0.8 – 1.1 |
| Sortino | Return / downside risk only | > 1.2 |

---

## India-Specific Features

- **Tax Simulator** — STT (0.1%), brokerage, GST on brokerage, STCG (20%), LTCG (12.5% above ₹1.25L)
- **Nifty 500 Universe** — 70 stocks across 13 sectors: IT, Banks, FMCG, Pharma, Auto, Energy, Metals, Financials, Infra, Consumer Durables, Telecom, Cement, Chemicals
- **Benchmark** — Nifty 50 (^NSEI)
- **Risk-free rate** — 6.5% (10-year G-Sec)
- **Regime-preferred sectors** — Bull: IT/Auto/Metals · Bear: FMCG/Pharma/Telecom

---

## Documentation

- [`HOW_IT_WORKS.md`](HOW_IT_WORKS.md) — Complete guide explaining every feature and all trading concepts from scratch (1,000+ lines, written for non-finance readers)
- [`DEPLOY_AZURE.md`](DEPLOY_AZURE.md) — Step-by-step Azure Container Apps deployment guide

---

## Roadmap

- [ ] Earnings call analyzer (transcript → sentiment score)
- [ ] FII/DII flow integration as regime signal
- [ ] Survivorship bias correction with delisted stocks
- [ ] Custom factor formula builder (UI)
- [ ] PDF tear sheet export
- [ ] Email/Telegram alert notifications

---

<div align="center">

Built with Python · Streamlit · Google Gemini · scikit-learn

**[Live Demo](https://alphaforge-2oucww4kcb8ef3pzt8crdx.streamlit.app/)** · **[Full Guide](HOW_IT_WORKS.md)**

</div>
