# AlphaForge — Complete Guide
### Everything you need to understand this project, even if you've never traded before.

---

## Table of Contents

1. [What Is AlphaForge?](#1-what-is-alphaforge)
2. [The Big Picture — How It All Fits Together](#2-the-big-picture)
3. [Trading Concepts You Must Know](#3-trading-concepts-you-must-know)
   - Stocks and the Stock Market
   - What Is a Portfolio?
   - What Is a Factor?
   - The 4 Factors AlphaForge Uses
   - What Is Backtesting?
   - Market Regimes
   - Key Performance Numbers (Sharpe, CAGR, Drawdown, Alpha, Beta)
   - What Is Rebalancing?
   - Sector Rotation
   - Risk and Diversification
4. [Feature-by-Feature Breakdown](#4-feature-by-feature-breakdown)
   - Dashboard
   - Backtester
   - Factor Analysis
   - Stock Screener
   - Portfolio Optimizer
   - ML Models
   - Regime Detector
   - Risk Manager
   - AI Chat
   - Research Journal
   - Live Portfolio
   - Macro Dashboard
   - Alerts
   - Tax Simulator
   - Watchlist
5. [The AI Brain (Gemini)](#5-the-ai-brain-gemini)
6. [The Machine Learning Engine](#6-the-machine-learning-engine)
7. [How the Data Flows](#7-how-the-data-flows)
8. [The File Structure Explained](#8-the-file-structure-explained)
9. [How to Run and Use AlphaForge](#9-how-to-run-and-use-alphaforge)
10. [Interpreting Your Results](#10-interpreting-your-results)
11. [Common Questions](#11-common-questions)

---

## 1. What Is AlphaForge?

AlphaForge is a **quantitative investment research platform** built for the Indian stock market (NSE/BSE).

In plain English: it is a software tool that helps you **find the best stocks to invest in** using math, data, and AI — instead of gut feeling, tips, or news headlines.

### The problem it solves

Most retail investors in India:
- Buy stocks based on tips from friends, YouTube, or Twitter
- Have no systematic way to pick stocks
- Don't know when to sell or rebalance
- Can't measure whether their strategy actually works

AlphaForge replaces all of that with a **data-driven, repeatable process** that:
1. Scores every stock in the Nifty 500 on 4 proven factors
2. Builds a portfolio of the top-ranked stocks
3. Simulates how that portfolio would have performed historically
4. Detects which market phase we're in (bull/bear/sideways)
5. Uses AI (Google Gemini) to explain everything in plain English
6. Uses Machine Learning to predict which stocks will outperform next month

### Who is it for?

- Finance students wanting to learn quantitative investing
- Individual investors who want a systematic approach
- Interns building a project to showcase at job interviews
- Anyone curious about how professional hedge funds and mutual funds pick stocks

---

## 2. The Big Picture

Here's the entire system in one paragraph:

> AlphaForge downloads historical stock price and fundamental data for ~70 Indian stocks. It computes 4 "factor scores" for each stock (momentum, value, quality, volatility). It ranks all stocks by a composite of these scores and picks the top N. It then simulates what would have happened if you had bought these top stocks every month for the last 5-10 years — this is called backtesting. You see charts of the simulated returns, risk metrics, and compare against the Nifty 50 benchmark. An AI (Gemini) can answer questions about your results in plain English. Machine learning models try to predict which stocks will outperform next month. There's also a live portfolio tracker, alerts for regime changes and drawdowns, and a tax simulator for India-specific costs.

Here's how it flows visually:

```
Raw Data (yfinance)
       ↓
  Price Data + Fundamentals
       ↓
  Factor Scores (Momentum, Value, Quality, Volatility)
       ↓
  Composite Score → Rank Stocks → Pick Top 20
       ↓
  Backtesting Engine → Simulated Returns
       ↓
  Performance Metrics + Charts
       ↓
  AI Analysis (Gemini) + ML Predictions
       ↓
  You (making informed decisions)
```

---

## 3. Trading Concepts You Must Know

### 3.1 Stocks and the Stock Market

A **stock** (also called a share or equity) is a small piece of ownership in a company. When you buy one share of Infosys, you own a tiny fraction of Infosys.

The **stock market** is a marketplace where these shares are bought and sold. In India:
- **NSE** (National Stock Exchange) — the main exchange, located in Mumbai
- **BSE** (Bombay Stock Exchange) — the older exchange, also in Mumbai
- **Nifty 50** — an index of the 50 largest companies on NSE. Think of it as a "temperature reading" of the Indian stock market
- **Nifty 500** — the 500 largest companies on NSE. AlphaForge uses a subset of these as its investment universe

Stock prices go up and down based on supply and demand, which is driven by company performance, economic news, investor sentiment, and many other factors.

### 3.2 What Is a Portfolio?

A **portfolio** is your collection of stocks. Instead of putting all your money in one stock (risky), you spread it across many — this is called **diversification**.

Example: Instead of putting ₹1,00,000 in just Infosys, you put ₹5,000 each in 20 different stocks across IT, banking, FMCG, pharma, etc.

AlphaForge builds a portfolio of the **top 20 stocks** ranked by factor scores, distributed equally (equal weight — each stock gets the same amount of money).

### 3.3 What Is a Factor?

In quantitative finance, a **factor** is a measurable characteristic of a stock that has historically predicted whether that stock will outperform or underperform the market.

Think of factors like a rating system for stocks. Instead of asking "is this a good company?", we ask:
- "Has this stock been going up more than others?" (Momentum)
- "Is this stock cheap relative to its earnings?" (Value)
- "Does this company make a lot of profit efficiently?" (Quality)
- "Does this stock's price move smoothly without big swings?" (Volatility)

These 4 questions form the backbone of AlphaForge's scoring system. Decades of academic research and real-world data have shown that stocks scoring high on these factors tend to outperform over time.

### 3.4 The 4 Factors AlphaForge Uses

#### Factor 1: Momentum 📈

**What it is:** Stocks that have been going up recently tend to keep going up. This is the momentum effect.

**The intuition:** If a stock has risen 40% in the last year while the market rose 15%, something good is happening at that company. Other investors notice, buy more, which pushes the price higher — creating momentum.

**How AlphaForge measures it:**
- Calculates the stock's return over the last 12 months, minus the last 1 month (this "skipping" avoids short-term reversal noise)
- Stocks with the highest 12-1 month return get the highest momentum score

**Example:** Tata Motors rose 80% in 2023. Its momentum score would be very high. A stock that fell 20% in the same period would have a very low momentum score.

**Real world proof:** The momentum factor has been documented since the 1990s. In India, it's been shown to add 3-5% annual excess return over a buy-and-hold strategy.

---

#### Factor 2: Value 💰

**What it is:** Cheap stocks (relative to their earnings or book value) tend to outperform expensive stocks over time.

**The intuition:** If you can buy ₹100 worth of earnings for only ₹10 (PE ratio of 10), that's a bargain. The market will eventually "correct" and recognize the true value — driving the price up.

**Key metrics:**
- **PE Ratio (Price to Earnings):** How many years of earnings you're paying for. PE of 15 means you're paying 15 years' worth of earnings upfront. Lower is cheaper.
- **PB Ratio (Price to Book):** Compares market price to the company's accounting value. PB below 1 means you're buying assets cheaper than their stated value.
- **Dividend Yield:** Higher dividends mean you're getting more income for your investment price.

**How AlphaForge measures it:** Inverts PE and PB (lower PE = higher value score), adds dividend yield, ranks all stocks, converts to a 0-1 percentile score.

**Example:** A banking stock with PE of 8 gets a higher value score than a tech stock with PE of 50.

---

#### Factor 3: Quality ⭐

**What it is:** Companies with strong financials — high profitability, low debt, stable earnings — tend to outperform.

**The intuition:** A company that consistently earns 25% return on equity, has almost no debt, and grows earnings every year is a fundamentally strong business. These companies survive downturns better and compound wealth over time.

**Key metrics:**
- **ROE (Return on Equity):** How much profit the company makes per rupee of shareholder money. ROE of 20% means the company made ₹20 profit for every ₹100 invested in it.
- **Debt-to-Equity Ratio:** How much debt the company has relative to its own capital. Lower is better — less debt = less risk.
- **Profit Margin:** What % of revenue becomes profit. Higher margin = more efficient business.
- **Earnings Growth:** Is the company growing its profits year over year?
- **Current Ratio:** Can the company pay its short-term bills? Ratio above 1 = yes.

**Example:** Asian Paints has ROE of ~30%, low debt, and consistent profit growth — it would score very high on quality. A company with 60% debt, negative earnings growth, and shrinking margins would score very low.

---

#### Factor 4: Low Volatility 🛡️

**What it is:** Stocks that move smoothly (low volatility) tend to outperform high-volatility stocks on a risk-adjusted basis. This seems counterintuitive — more risk should mean more reward, right? But the data says otherwise.

**The intuition:** Very volatile stocks attract speculators and lottery-seekers who overpay for excitement. Low-volatility stocks are boring — institutional investors hold them steadily, they don't get overcrowded, and they deliver consistent returns.

**How AlphaForge measures it:** Calculates the 63-day (3-month) rolling standard deviation of daily returns, annualizes it, and inverts it. A stock with 15% annual volatility gets a higher score than a stock with 45% volatility.

**Example:** Hindustan Unilever (HUL) barely moves day to day — very low volatility, high score. A small-cap penny stock might move 5% every day — very high volatility, low score.

### 3.5 What Is Backtesting?

**Backtesting** is simulating your investment strategy on historical data to see how it would have performed.

**Think of it like this:** You have a theory — "if I had bought the top 20 stocks by composite score every month from 2018 to 2024, how much money would I have made?" Backtesting answers this question.

**AlphaForge's backtesting process (step by step):**

1. Start date: January 2018. You have ₹1,00,000 to invest.
2. Score all 70 stocks using the 4 factors. Pick the top 20.
3. "Buy" equal amounts of each of those 20 stocks.
4. Fast forward 1 month (February 2018).
5. Re-score all stocks. The rankings may have changed.
6. "Sell" stocks that dropped out of the top 20. "Buy" new ones that entered.
7. This is called **rebalancing**.
8. Repeat every month until the end date.
9. Track how much your ₹1,00,000 grew (or shrank) over the entire period.
10. Compare this to what would have happened if you had just bought the Nifty 50 index.

**Why backtesting is useful:** It shows whether your strategy has an "edge" over simply buying the index. If your strategy returned 22% annually while the Nifty returned 14%, that 8% difference is your alpha.

**Important caveat:** Past performance doesn't guarantee future results. Backtesting can be misleading if done incorrectly (survivorship bias, overfitting). AlphaForge includes a survivorship bias warning.

### 3.6 Market Regimes

The stock market doesn't behave the same way all the time. It goes through distinct phases:

| Regime | What it looks like | Duration |
|---|---|---|
| **Bull Market** | Prices rising, economy growing, optimism high | Months to years |
| **Bear Market** | Prices falling, economy contracting, fear dominant | Months to years |
| **Sideways Market** | Prices flat, neither rising nor falling clearly | Months |

**Why regimes matter:** The same strategy that works brilliantly in a bull market might fail badly in a bear market. Momentum stocks fly in bull markets but crash hardest in bear markets. Defensive stocks (FMCG, Pharma) hold up better in bear markets.

**How AlphaForge detects regimes:** It looks at 4 signals simultaneously:
1. Is the Nifty 50 above its 200-day moving average? (Long-term trend signal)
2. Is the 50-day MA above the 200-day MA? (Golden cross / Death cross signal)
3. Is the 3-month return positive or negative? (Momentum signal)
4. Is volatility elevated? (Fear signal)

Each signal votes Bull (+1) or Bear (-1). The sum determines the regime:
- Score of +2 to +4 → **Bull Market**
- Score of -2 to -4 → **Bear Market**
- Score of -1 to +1 → **Sideways Market**

**What AlphaForge recommends in each regime:**
- Bull: Lean into IT, Auto, Consumer Durables, Metals (cyclicals that rise with the economy)
- Bear: Shift to FMCG, Pharma, Telecom (defensives that people need regardless of economy)
- Sideways: Financials, balanced allocation

### 3.7 Key Performance Numbers

These are the numbers you'll see everywhere in AlphaForge. Here's what they mean:

#### CAGR (Compound Annual Growth Rate)

The annualized return of your portfolio.

> **Formula:** `CAGR = (Final Value / Initial Value)^(1/Years) - 1`

**Example:** You invested ₹1,00,000 in 2018. By 2024 (6 years), it became ₹3,20,000.
CAGR = (3.2)^(1/6) - 1 = **21.4% per year**

**What's good:** Nifty 50 returns ~12-14% annually. A good strategy should beat this by 3-8%.

---

#### Sharpe Ratio

Measures return per unit of risk. The higher, the better.

> **Formula:** `Sharpe = (Portfolio Return - Risk-Free Rate) / Portfolio Volatility`

The risk-free rate in India is approximately 6.5% (10-year government bond yield). This is what you'd earn without any risk.

**Example:** Your strategy returns 20% annually with 15% volatility.
Sharpe = (20% - 6.5%) / 15% = **0.9**

**What's good:**
- Below 0.5: Poor
- 0.5 to 1.0: Acceptable
- 1.0 to 1.5: Good
- Above 1.5: Excellent

**Why it matters:** A strategy returning 25% with 30% volatility (Sharpe: 0.62) is actually worse than one returning 18% with 10% volatility (Sharpe: 1.15) — because the first one gives you terrifying swings along the way.

---

#### Max Drawdown

The worst peak-to-trough loss your portfolio experienced.

**Example:** Your portfolio peak was ₹2,00,000 in January 2020. By March 2020 (COVID crash), it fell to ₹1,30,000. Max drawdown = -35%.

**What's acceptable:** Most professional investors target max drawdowns below 20-25%. Above 40% is considered extreme — very few investors can stomach this psychologically.

---

#### Alpha

The excess return above what the benchmark (Nifty 50) returned, adjusted for market risk.

**Example:** Your strategy returned 22% in a year when the Nifty returned 15%. Your alpha is roughly +7% — you outperformed the market by 7%.

**Why it matters:** Alpha is the real "edge" of your strategy. A strategy with consistent positive alpha is adding real value. Negative alpha means you're worse than just buying an index fund.

---

#### Beta

How much your portfolio moves relative to the market.

- **Beta = 1:** Your portfolio moves exactly with the market
- **Beta = 1.5:** When market falls 10%, your portfolio falls 15% (amplified)
- **Beta = 0.7:** When market falls 10%, your portfolio falls only 7% (defensive)

**What to aim for:** A beta close to 1 with positive alpha means you're beating the market without taking extra risk. Very high beta is dangerous.

---

#### Sortino Ratio

Like Sharpe, but only penalizes downside volatility (bad swings), not upside volatility (good swings). More relevant for real investor behavior.

---

#### Calmar Ratio

> `Calmar = CAGR / |Max Drawdown|`

Measures return per unit of worst-case loss. Higher is better. A Calmar of 1.0 means you're earning 1% of annual return for every 1% of maximum drawdown you experienced.

---

#### Information Ratio (IR)

Measures the consistency of outperformance over the benchmark. High IR means you're beating the benchmark regularly, not just occasionally getting lucky.

---

### 3.8 What Is Rebalancing?

When you first build your portfolio, each stock has equal weight (5% each for 20 stocks). Over time, some stocks go up and some go down — the weights drift. Also, new stocks might deserve to be in the portfolio based on updated factor scores.

**Rebalancing** means periodically:
1. Re-scoring all stocks
2. Selling stocks that are no longer in the top 20
3. Buying stocks that newly entered the top 20
4. Restoring equal weights

AlphaForge supports monthly, quarterly, and weekly rebalancing. More frequent rebalancing captures new opportunities faster but incurs more transaction costs.

### 3.9 Sector Rotation

Different sectors of the economy perform differently at different times in the economic cycle:

| Economic Phase | Outperforming Sectors |
|---|---|
| Early recovery | Financials, Consumer Discretionary |
| Bull run | IT, Auto, Metals, Capital Goods |
| Slowdown | FMCG, Pharma, Utilities |
| Recession | FMCG, Pharma, Telecom |

**Sector rotation** means deliberately shifting your portfolio's sector exposure based on where we are in the economic cycle. AlphaForge's Regime Detector + Sector Rotation Engine suggests which sectors to overweight in each regime.

### 3.10 Risk and Diversification

**Diversification** is the only "free lunch" in investing. By holding stocks that don't all move together (low correlation), you reduce portfolio risk without reducing expected return.

**Correlation** ranges from -1 to +1:
- +1: Two stocks always move together (no diversification benefit)
- 0: Stocks move independently (good diversification)
- -1: Stocks move in opposite directions (perfect hedge)

**Example:** Holding only IT stocks is risky because they all get hurt by the same events (rupee appreciation, US recession fears). Adding FMCG stocks provides diversification because FMCG is driven by different forces (domestic consumption).

AlphaForge's Risk Manager flags when two holdings become too correlated (above 0.8) — suggesting you replace one with a less correlated alternative.

---

## 4. Feature-by-Feature Breakdown

### 4.1 Dashboard (Page 1)

**What it does:** The home screen. Gives you a bird's-eye view of the current state of the market and your factor universe.

**What you see:**
- **Universe size:** How many stocks are being tracked (currently 70)
- **Market Regime:** Is it a Bull, Bear, or Sideways market right now? With a confidence percentage.
- **Average Factor Scores:** What's the average momentum, quality score of the top stocks?
- **Top N Stocks by Factor Score:** A sortable table of all stocks with their individual factor scores and a final signal (Strong Buy / Buy / Neutral / Sell / Strong Sell)
- **Factor Radar Chart:** A spider/web chart showing the portfolio's average exposure to each factor
- **Benchmark Trend:** How the Nifty 50 has moved since your chosen start date

**How to use it:** Check this page first every time you open AlphaForge. If the regime is Bear and most signals are Sell, you might want to reduce risk or shift to defensive sectors.

---

### 4.2 Backtester (Page 2)

**What it does:** This is the core feature. You configure a strategy and it simulates how that strategy would have performed historically.

**Configuration options:**
- **Sectors:** Which sectors to include in the universe (All, or specific sectors like Banking, IT)
- **Start/End Date:** The historical period to test
- **Top N Stocks:** How many stocks to hold (5 to 50)
- **Rebalance Frequency:** Monthly, Quarterly, or Weekly
- **Factor Weights:** How much importance to give each factor (sliders from 0 to 100%)

**What you see:**
- **6 key metrics:** CAGR, Sharpe, Sortino, Max Drawdown, Alpha, Beta
- **Equity Curve:** A chart showing your ₹1 growing over time, vs the Nifty 50
- **Drawdown Chart:** The red areas where your portfolio was below its peak
- **Monthly Returns Heatmap:** A grid of Jan-Dec for each year, green = good months, red = bad months
- **Rolling Sharpe:** How the risk-adjusted return changed over time
- **Holdings at Last Rebalance:** Which 20 stocks are currently in the portfolio

**How to use it:** Experiment with different factor weights. Try momentum-heavy (0.5 weight) vs balanced. Try 10 stocks vs 30 stocks. See what gives the best Sharpe ratio. The key is to not just optimize for the highest return — optimize for the best risk-adjusted return.

---

### 4.3 Factor Analysis (Page 3)

**What it does:** Deep dive into how each individual factor is performing. Helps you understand the "why" behind your strategy.

**Tabs:**
- **Score Distribution:** Histograms showing how all stocks are distributed across each factor score. A healthy distribution is roughly bell-shaped.
- **Factor Spreads:** Compares the top 20% vs bottom 20% of stocks on each factor. A wide spread means the factor is strongly differentiating stocks.
- **Momentum Deep Dive:** Shows the top/bottom momentum stocks, and lets you see a single stock's rolling 12-month momentum over time.
- **Factor Decay:** Tracks whether the factor is still "working" — are top-ranked stocks actually outperforming? If factor effectiveness is declining, it may be getting crowded.

**Key concept — Factor Decay:** Sometimes a factor stops working because too many investors discover it and pile in, eliminating the edge. This is called "factor crowding." The decay tracker gives early warning when this is happening.

---

### 4.4 Stock Screener (Page 4)

**What it does:** Lets you find specific stocks matching criteria, either by typing in plain English or by setting manual filters.

**Natural Language mode:** You type things like:
- *"Find undervalued banking stocks with strong momentum"*
- *"High quality pharma companies with low debt"*
- *"Stocks with value score above 0.7 and quality above 0.6"*

The AI (Gemini) reads your query, converts it into structured filter parameters, and applies them to the factor scores database.

**Follow-up refinement:** After seeing results, you can say:
- *"Now remove anything with PE above 30"*
- *"Sort these by Sharpe ratio"*
- *"Show me only mid-cap stocks"*

**Manual filter mode:** Traditional sliders for minimum/maximum values of each factor.

---

### 4.5 Portfolio Optimizer (Page 5)

**What it does:** Given a list of stocks, finds the mathematically optimal way to allocate money among them.

**Three optimization methods:**

**Method 1: Maximum Sharpe Portfolio (Markowitz)**
Finds the exact allocation that maximizes the Sharpe ratio. Invented by Harry Markowitz in 1952 (he won the Nobel Prize for it). Uses the historical returns and correlations between stocks to find the allocation that gives the best return per unit of risk.

*Example:* Given HDFC Bank, Infosys, Reliance, TCS — it might say: put 35% in HDFC Bank, 25% in Reliance, 25% in Infosys, 15% in TCS — because this exact combination has historically had the best Sharpe ratio.

**Method 2: Risk Parity**
Instead of maximizing return, this method makes each stock contribute equally to the portfolio's total risk. If HDFC Bank is twice as volatile as TCS, you put half as much money in HDFC Bank so both contribute the same amount of risk.

*Why it's useful:* Prevents any single volatile stock from dominating your risk. More robust in real-world conditions.

**Method 3: Efficient Frontier**
A chart showing all possible portfolio combinations (different allocations between the stocks) — plotting risk on the X-axis and return on the Y-axis. The "frontier" is the boundary of best possible portfolios — you can't get more return at a given risk level than the frontier portfolios.

**Monte Carlo Simulation:**
Runs 1,000 to 5,000 random simulations of future 1-year returns based on the historical distribution. Shows you a "probability cone":
- The median expected path
- The 90% confidence interval (95th percentile to 5th percentile)
- Probability of loss
- Expected VaR (Value at Risk)

*Example output:* "There's a 95% chance your portfolio will return between -8% and +42% in the next year. Expected return: +18%. Probability of any loss: 22%."

---

### 4.6 ML Models (Page 6)

**What it does:** Uses Machine Learning to predict stock performance and discover hidden patterns.

**Three ML features:**

**Feature 1: Return Predictor**
Trains a Random Forest or XGBoost model on historical factor scores to predict next-month returns.

*How it works (simplified):*
1. For every month from 2018 to 2022 (training data): Look at each stock's factor scores and what its actual return was the following month.
2. The model learns patterns: "Stocks with momentum above 0.8 AND quality above 0.7 tended to return +3% the next month."
3. Walk-forward validation: Train on 2018-2020, test on 2021. Then train on 2018-2021, test on 2022. This mimics real-world use.
4. Shows the correlation between predicted and actual returns.
5. Feature importance chart: Which factor matters most for predictions?

**Random Forest vs XGBoost:**
- Both are "ensemble" methods — they combine hundreds of simple decision trees
- Random Forest: More stable, less prone to overfitting
- XGBoost: Often more accurate, but needs more careful tuning
- AlphaForge lets you compare both

**Feature 2: Stock Clustering**
Groups stocks by their factor profile using K-Means clustering. Visualizes in 2D using PCA.

*Why it's useful:* Reveals hidden groups of stocks that behave similarly. If your portfolio has 5 stocks all in the same cluster ("high momentum, low value"), you have hidden concentration risk. You'd want stocks from different clusters for true diversification.

*What you see:* A scatter plot where each dot is a stock, colored by cluster. Stocks close together in the plot have similar factor profiles.

**Feature 3: Anomaly Detection**
Finds unusual days in a stock's return history using Isolation Forest (an ML algorithm) and Z-scores.

*How it works:* Learns what "normal" daily returns look like for a stock. Flags days where the return was so unusual it likely signals something — earnings surprise, news event, corporate action, or market manipulation.

*Example:* "HDFC Bank dropped 8% on October 3rd — anomaly score: 0.95. Z-score: -4.2. This move was 4.2 standard deviations below normal." This flags the date for investigation.

---

### 4.7 Regime Detector (Page 7)

**What it does:** Continuously analyzes the Nifty 50 to determine whether we're in a Bull, Bear, or Sideways market, and how confident the model is.

**The 4 signals it uses:**
1. **Price vs 200-day MA:** The 200-day Moving Average is the average price over the last 200 days. If today's price is above this average, it's bullish (uptrend). Below = bearish.
2. **Golden Cross / Death Cross:** 
   - Golden Cross: The 50-day MA crosses above the 200-day MA → strong bullish signal
   - Death Cross: The 50-day MA crosses below the 200-day MA → strong bearish signal
3. **3-Month Momentum:** Has the market risen more than 5% in the last 3 months (bull) or fallen more than 5% (bear)?
4. **Volatility:** Is the market unusually volatile? High volatility (above 28% annualized) signals fear — bearish.

**Regime Score:** Each signal votes +1 (bullish) or -1 (bearish). Sum:
- +3 or +4: Strong Bull
- +1 or +2: Mild Bull
- -1 to +1: Sideways
- -3 or -4: Strong Bear

**Confidence:** The absolute value of the score / 4. A score of +4 means 100% confidence it's a bull market. A score of 0 means 0% confidence — regime is ambiguous.

**What to do with this:**
- **Bull:** Take more risk. Overweight cyclical sectors (IT, Auto, Metals).
- **Bear:** Reduce risk. Overweight defensive sectors (FMCG, Pharma). Consider reducing equity allocation.
- **Sideways:** Stay balanced. Don't overcommit to either direction.

---

### 4.8 Risk Manager (Page 8)

**What it does:** Monitors your portfolio's risk in real time and alerts you to problems.

**Checks it runs:**
1. **Drawdown Alert:** Is your portfolio more than 15% below its peak? → Alert.
2. **Concentration Alert:** If you hold only 5 stocks, each one is 20% of your portfolio — too concentrated.
3. **Sector Concentration:** If 7 out of 20 stocks are in IT, that's 35% in one sector — risky.
4. **Correlation Alert:** Are any two holdings moving almost identically (correlation > 0.8)? That's a hidden concentration.

**Metrics it shows:**
- **Current Drawdown:** How far below the peak you are right now
- **VaR (Value at Risk) at 95%:** The maximum loss you'd expect on a normal bad day. "On 95% of days, you won't lose more than X%."
- **CVaR (Conditional VaR):** The average loss on the worst 5% of days. More conservative than VaR.
- **Correlation Heatmap:** A color-coded grid showing correlations between all your holdings

---

### 4.9 AI Chat (Page 9)

**What it does:** Lets you have a conversation with an AI (Google Gemini) about your portfolio and strategy.

**Three modes:**

**Portfolio Chat:** Ask anything about your backtest results:
- *"Why did my portfolio underperform in 2020?"*
- *"Which factor contributed most to my returns?"*
- *"Should I increase the momentum weight given the current regime?"*
- *"Explain my portfolio's performance like I'm a beginner"*

The AI reads your actual backtest data (CAGR, Sharpe, drawdown, holdings, factor weights) and answers with specific numbers.

**Strategy Critique:** Click a button, and the AI writes a full critique of your strategy. It covers:
- Strengths and weaknesses
- Factor concentration risks
- Regime sensitivity
- Transaction cost concerns
- Survivorship bias issues
- 5 specific action items to improve the strategy

**Compare Strategies:** After running two different backtests, the AI compares them and tells you which is better for a growth investor vs a conservative investor — with specific reasoning.

---

### 4.10 Research Journal (Page 10)

**What it does:** A built-in notes application for recording your research observations.

**Why it matters:** Professional fund managers keep detailed research journals. When you notice something interesting ("momentum underperformed in July") or form a hypothesis ("I think FMCG stocks are overvalued"), you write it down. Over time, this builds your research edge.

**AI Suggestions feature:** After writing several entries, click "Get AI Suggestions." The AI reads your recent notes and suggests:
- *"You've mentioned momentum underperformance 3 times this quarter. Consider running a momentum decay analysis."*
- *"Your notes suggest you're worried about IT sector concentration. Try adding a sector cap constraint to your backtest."*

**Tags system:** Tag entries by factor, sector, stock name, or regime for easy filtering later.

---

### 4.11 Live Portfolio Tracker (Page 11)

**What it does:** Enter your actual real-world holdings and see their current factor scores and P&L.

**What you enter:** Stock symbol, number of shares, average cost price, purchase date.

**What it shows:**
- Current market value of each holding
- Unrealized P&L (profit/loss) in ₹ and %
- Current factor scores for each holding
- AI signal (Buy/Sell/Neutral) based on current scores
- Portfolio total value, total P&L, weighted average composite score

**Why it's useful:** You might see that a stock you own has dropped from a "Strong Buy" signal to "Sell" signal — the factors have deteriorated. This is a signal to consider trimming or exiting that position.

---

### 4.12 Macro Dashboard (Page 12)

**What it does:** Tracks key macroeconomic indicators that affect the Indian stock market.

**Indicators tracked:**
- **India VIX:** The "fear index" for Indian markets. VIX above 20 = elevated fear. VIX above 30 = panic.
- **Nifty 50:** The main market index
- **USD/INR exchange rate:** A weak rupee hurts companies that import (oil, tech hardware) but helps IT exporters. Strong correlation with stock market.
- **Crude Oil (WTI):** India imports 85% of its oil. High crude = bad for the economy, inflation risk.
- **Gold:** Often inversely correlated with equities. Gold rising = risk-off sentiment.
- **US 10-Year Bond Yield:** Higher US rates attract money out of emerging markets like India → negative for Indian stocks.

**Correlation Matrix:** A heatmap showing how these macro indicators relate to each other. *Example:* If USD/INR and Nifty have correlation of -0.7, when the rupee weakens, the market tends to fall.

---

### 4.13 Alerts (Page 13)

**What it does:** Automatically monitors for important events and sends you alerts within the app.

**Alert types:**
- **Regime Change Alert:** The market has shifted from Bull to Bear (or any transition) → time to review your allocation
- **Drawdown Alert:** Your portfolio has crossed the 15% drawdown threshold
- **Factor Degradation Alert:** Factor scores for a holding have significantly dropped
- **Anomaly Alert:** A stock in your live portfolio made an unusual price move today

**Alert severity:**
- 🔴 Red = High priority — act soon
- 🟡 Yellow = Medium — review when you can

All alerts are logged to the database with timestamps so you can review your alert history.

---

### 4.14 Tax Simulator (Page 14)

**What it does:** Calculates the realistic cost of trading and taxes in India, showing the difference between gross returns (before costs) and net returns (what you actually keep).

**India-specific costs modeled:**

| Cost | Rate |
|---|---|
| STT (Securities Transaction Tax) | 0.1% on delivery trades |
| Brokerage | ~0.03% (typical discount broker) |
| GST on Brokerage | 18% of brokerage |
| SEBI charges | 0.0001% |
| Stamp duty | 0.015% on buy side |

**Capital Gains Tax in India (FY2024-25):**
- **STCG (Short-Term Capital Gains):** If you sell within 1 year → 20% tax on profits
- **LTCG (Long-Term Capital Gains):** If you sell after 1 year → 12.5% tax on profits ABOVE ₹1.25 lakh (the first ₹1.25 lakh is tax-free)

**Key insight from the simulator:** Monthly rebalancing generates short-term gains (taxed at 20%) and high transaction costs. Annual rebalancing generates long-term gains (12.5% with exemption) and lower costs. The simulator shows the optimal rebalancing frequency for your portfolio size and return rate.

**Example:** A ₹10 lakh portfolio returning 20% gross:
- Monthly rebalancing: ~₹18,000 in costs + ₹40,000 STCG tax = net return 16.2%
- Annual rebalancing: ~₹3,000 in costs + ₹23,000 LTCG tax = net return 17.4%

---

### 4.15 Watchlist (Page 15)

**What it does:** Track stocks you're interested in but haven't bought yet. Get daily AI-generated commentary on each.

**AI Commentary:** Click "Generate AI Commentary" and for each stock in your watchlist, the AI writes one line like:
- *"TITAN: Momentum improving (+0.78), quality remains strong, slightly stretched on value (PB: 14x) — hold off on adding at current levels."*
- *"ICICIBANK: All factors positive, strong quality and momentum, reasonable value — high conviction buy signal."*

This saves you from reading lengthy research reports — you get the key quant takeaway in one sentence per stock.

---

## 5. The AI Brain (Gemini)

AlphaForge uses Google's **Gemma-3-4b-it** model (via the Gemini API) for all AI features.

**How it works:**
1. AlphaForge collects context (your backtest metrics, factor scores, portfolio data)
2. It crafts a detailed prompt with this context and a system instruction (e.g., "You are a quant analyst for Indian markets...")
3. The Gemini API sends this to the model and gets a response
4. AlphaForge streams the response back to you word by word (you see it typing)

**What the AI doesn't do:**
- It doesn't access the internet in real-time
- It doesn't have information about today's news
- It doesn't always get numbers exactly right — always cross-check important claims
- It's a language model, not an infallible oracle

**Prompt engineering:** Each AI feature has a carefully crafted system prompt in the `ai/prompts/` folder. These prompts tell the AI its role, the context, and the format of the response. This is why the strategy critique comes back structured while the portfolio chat is conversational.

---

## 6. The Machine Learning Engine

### What's the difference between ML and AI in AlphaForge?

- **AI (Gemini):** A large language model. Processes text in and out. Used for explaining, analyzing, critiquing.
- **ML (scikit-learn / XGBoost):** Statistical models trained on numerical data. Used for predicting returns, clustering stocks, finding anomalies.

### Random Forest (for Return Prediction)

Imagine you have 1,000 different financial advisors (decision trees), each looking at the factor scores of a stock slightly differently (using random subsets of data). Each advisor says "this stock will go up" or "this stock will go down." The final prediction is a majority vote.

- **Why it works:** Averaging many imperfect predictors reduces noise and produces more reliable predictions than any single model.
- **Walk-forward validation:** The model is retrained every month using only past data, then tested on the upcoming month. This accurately simulates real-world use and avoids "cheating" by looking at the future.

### XGBoost (eXtreme Gradient Boosting)

Instead of training trees independently (like Random Forest), XGBoost trains each new tree to fix the mistakes of the previous trees. It "boosts" accuracy by focusing on hard-to-predict cases.

- **Often more accurate than Random Forest**
- **More prone to overfitting** if not carefully tuned
- AlphaForge uses cross-validation to prevent overfitting

### K-Means Clustering (for Stock Groups)

K-Means looks at each stock as a point in 4-dimensional space (momentum score, value score, quality score, volatility score). It groups stocks into K clusters so that stocks within a cluster are similar to each other and different from other clusters.

Since humans can't visualize 4 dimensions, AlphaForge uses **PCA (Principal Component Analysis)** to compress the 4 dimensions down to 2 dimensions for visualization — while preserving as much information as possible.

### Isolation Forest (for Anomaly Detection)

Anomaly detection works by asking: "How easy is it to isolate this data point?" Normal data points are surrounded by many others — you need many splits to isolate them. Anomalous data points are in sparse regions — they're easy to isolate quickly.

The "isolation score" tells you how anomalous a stock's return was. High score = very unusual = worth investigating.

---

## 7. How the Data Flows

```
1. yfinance API
   ↓ Downloads historical prices (OHLCV) for each stock
   ↓ Caches to .parquet files (fast, columnar storage)

2. Fundamental Data
   ↓ yfinance.Ticker.info for PE, PB, ROE, Debt/Equity, etc.
   ↓ Used by Value and Quality factors

3. Factor Computation (core/factors/)
   ↓ Momentum: computed from price history
   ↓ Value: computed from fundamentals
   ↓ Quality: computed from fundamentals
   ↓ Volatility: computed from price history
   ↓ Composite: weighted average of above 4

4. SQLite Database (data/db/alphaforge.db)
   ↓ Stores factor scores, backtest results, live portfolio,
   ↓ watchlist, alerts, regime history, research journal

5. Backtesting Engine
   ↓ Walk-forward: for each rebalance date, re-score and re-rank
   ↓ Simulate daily returns of equal-weight top-N portfolio
   ↓ Track portfolio value over time

6. Performance Analytics
   ↓ CAGR, Sharpe, Sortino, Max Drawdown, Alpha, Beta, IR
   ↓ Rolling metrics, monthly returns pivot table

7. ML Models
   ↓ Trained on factor scores + realized returns
   ↓ Walk-forward validated
   ↓ Predictions for next-month outperformers

8. AI (Gemini API)
   ↓ Context (metrics + holdings) + User question
   ↓ Streamed response

9. Streamlit UI (pages/)
   ↓ 15 pages rendering all of the above
   ↓ Interactive charts (Plotly), tables, forms
```

---

## 8. The File Structure Explained

```
AlphaForge/
│
├── app.py                    ← The main entry point. Run this with streamlit.
│
├── config/
│   └── settings.py           ← All configurable constants: tax rates, factor weights,
│                               risk limits, API keys, model names.
│
├── data/
│   ├── fetcher.py            ← Downloads stock prices and fundamentals from yfinance.
│   │                           Caches everything so you don't re-download each run.
│   ├── universe.py           ← The list of 70 NSE stocks AlphaForge tracks, with sector labels.
│   └── store.py              ← SQLite database layer. Creates and manages all DB tables.
│
├── core/
│   ├── factors/
│   │   ├── momentum.py       ← 12-1 month momentum calculation
│   │   ├── value.py          ← PE/PB/dividend value scoring
│   │   ├── quality.py        ← ROE/debt/margin quality scoring
│   │   ├── volatility.py     ← Low-vol scoring, beta, Sharpe calculation
│   │   ├── scorer.py         ← Combines all 4 factors into composite score
│   │   └── custom_builder.py ← Let users define their own factor formula
│   │
│   ├── backtesting/
│   │   ├── engine.py         ← Main walk-forward backtest engine
│   │   ├── performance.py    ← All performance metric calculations
│   │   ├── tearsheet.py      ← Professional one-page summary chart
│   │   └── survivorship.py   ← Survivorship bias warnings
│   │
│   ├── regime/
│   │   └── detector.py       ← Bull/Bear/Sideways detector using 4 signals
│   │
│   ├── risk/
│   │   ├── manager.py        ← Drawdown, concentration, sector checks
│   │   └── monte_carlo.py    ← Monte Carlo simulation and probability cone
│   │
│   └── optimization/
│       ├── markowitz.py      ← Mean-variance optimization (max Sharpe, min variance)
│       ├── risk_parity.py    ← Equal risk contribution allocation
│       └── frontier.py       ← Efficient frontier computation
│
├── ml/
│   ├── models/
│   │   ├── return_predictor.py  ← Random Forest + XGBoost with walk-forward validation
│   │   ├── clustering.py        ← K-Means stock clustering + PCA visualization
│   │   └── anomaly.py           ← Isolation Forest anomaly detection
│   └── validation/
│       └── walk_forward.py      ← Generic walk-forward validation framework
│
├── ai/
│   ├── client.py            ← Gemini API wrapper (chat + streaming)
│   ├── portfolio_chat.py    ← Multi-turn portfolio Q&A Streamlit component
│   ├── nl_screener.py       ← Natural language → filter parameters conversion
│   ├── strategy_critique.py ← AI strategy analysis and comparison
│   └── prompts/             ← System prompts for each AI feature
│
├── components/
│   ├── equity_curve.py      ← Equity curve chart with drawdown shading
│   ├── radar_chart.py       ← Factor exposure radar/spider chart
│   └── ...                  ← Other reusable chart components
│
├── pages/                   ← 15 Streamlit pages (auto-appear in sidebar)
│   ├── 1_Dashboard.py
│   ├── 2_Backtester.py
│   └── ... through 15_Watchlist.py
│
├── utils/
│   └── tax.py               ← India-specific tax calculation utilities
│
├── scripts/
│   └── init_db.py           ← Run once to create the database
│
├── requirements.txt         ← All Python packages needed
└── .env                     ← Your API keys (never share this file!)
```

---

## 9. How to Run and Use AlphaForge

### First-time setup

```bash
# Navigate to the project
cd /home/dharunthegreat/AlphaForge

# Install dependencies
pip install -r requirements.txt

# Initialize the database (run only once)
python scripts/init_db.py

# Add your API key to .env
echo "GEMINI_API_KEY=your_key_here" > .env

# Start the app
streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

### Recommended workflow for a new user

**Day 1: Explore**
1. Open Dashboard → see which stocks have strong signals right now
2. Open Regime Detector → understand current market phase
3. Open Macro Dashboard → get the big picture

**Day 2: Backtest**
1. Go to Backtester
2. Use default settings (all sectors, monthly rebalance, equal factor weights)
3. Run the backtest — observe CAGR, Sharpe, Max Drawdown
4. Go to AI Chat → ask "what are the weaknesses of this strategy?"
5. Tweak factor weights → re-run → compare

**Day 3: Optimize**
1. Take the top 20 stocks from your best backtest
2. Go to Portfolio Optimizer → paste the symbols
3. Run Max Sharpe, Risk Parity, Monte Carlo
4. Understand the probability cone

**Ongoing:**
1. Add stocks to Live Portfolio as you buy them
2. Add to Watchlist as you research candidates
3. Check Alerts daily
4. Write observations in Research Journal

---

## 10. Interpreting Your Results

### Is my backtest good?

| Metric | Poor | Acceptable | Good | Excellent |
|---|---|---|---|---|
| CAGR vs Nifty | < Nifty | Nifty + 2% | Nifty + 5% | Nifty + 10%+ |
| Sharpe Ratio | < 0.5 | 0.5 – 0.8 | 0.8 – 1.2 | > 1.2 |
| Max Drawdown | > -40% | -25% to -40% | -15% to -25% | < -15% |
| Alpha | Negative | 0 – 3% | 3 – 7% | > 7% |
| Beta | > 1.3 | 1.0 – 1.3 | 0.8 – 1.0 | < 0.8 |

### Warning signs to watch for

1. **CAGR is very high but Sharpe is low:** You're taking too much risk. The return isn't worth the volatility.
2. **Great backtest but small universe:** If you only tested on 10 stocks and got 35% CAGR, that's likely luck. Test on 50+ stocks.
3. **All top holdings are in one sector:** Factor scores alone don't guarantee diversification. Add sector caps.
4. **Results are suspiciously perfect:** No real strategy has a Sharpe of 3.0. If you see this, you've likely made an error (look-ahead bias, survivorship bias).
5. **Max drawdown happened in 2020 (COVID):** Most strategies looked terrible in March 2020. See how fast the strategy recovered — recovery speed matters.

### The Survivorship Bias Problem

AlphaForge only tracks currently-listed stocks. But historically, many companies got delisted (went bankrupt, got acquired, or were removed from the exchange). Companies like Jet Airways, Reliance Communications were once in the Nifty 500. If your backtest is from 2015-2024, it would never have "bought" these companies — even though at the time, they might have scored highly on some factors.

This makes backtests look better than reality. AlphaForge shows a survivorship bias warning to remind you of this. A professional backtest would include delisted stocks — reducing returns by an estimated 0.5-2% annually.

---

## 11. Common Questions

**Q: Can I use AlphaForge to actually trade?**
A: AlphaForge is a research and analysis tool, not a trading platform. It doesn't connect to any broker. You use it to decide what to buy, then execute the trade manually through your broker (Zerodha, Upstox, etc.).

**Q: How often should I rebalance?**
A: The Tax Simulator shows that monthly rebalancing often costs 1-2% more in taxes and transaction costs than quarterly. For most portfolios above ₹5 lakh, monthly or quarterly rebalancing makes sense. Below that, quarterly or annual.

**Q: The backtest shows 28% CAGR. Will I actually get that?**
A: Probably not. Backtests are optimistic because of:
- Survivorship bias (only surviving stocks included)
- Transaction costs (partially modeled)
- Market impact (large trades move prices against you)
- Future factor decay (past patterns may not repeat)
Assume 30-40% reduction from backtest CAGR to realistic expectations.

**Q: Why does the AI sometimes give wrong answers?**
A: The AI is a language model — it generates plausible text based on patterns. When given specific numbers from your backtest, it's fairly reliable. When asked about general market conditions or specific stock predictions, treat it as a starting point for research, not as fact.

**Q: What does it mean if a stock has high momentum but low quality?**
A: The stock is going up strongly (investors are buying it) but the underlying business is not particularly strong. This can happen when stocks are overbought or driven by speculation. These are higher-risk momentum plays — they can continue rising but crash hard when momentum reverses. Low momentum + high quality is the "value trap" version — the business is great but nobody is buying.

**Q: How is this different from what a professional quant fund does?**
A: Professional quant funds use:
- Alternative data (satellite imagery, credit card data, social media sentiment)
- Intraday signals (microsecond price patterns)
- Execution algorithms (to trade without moving the market)
- Risk models (factor exposure targets, not just weights)
- Much larger universes (all liquid global stocks)
AlphaForge uses the same conceptual framework but with freely available data. The concepts are identical — the sophistication of data and execution is different.

**Q: Can I add my own factor?**
A: Yes! The Custom Factor Builder (core/factors/custom_builder.py and the Factor Analysis page) lets you define a formula like:
```
(roe * 0.4) + (momentum * 0.4) - (debt_to_equity * 0.2)
```
AlphaForge evaluates this formula for every stock and ranks them by the result. You can then backtest this custom factor.

---

*AlphaForge — Built for learning quantitative investing through doing.*

*The best way to understand any concept in this guide is to run AlphaForge, observe the numbers, change one parameter, and see what happens. The learning is in the experimentation.*

