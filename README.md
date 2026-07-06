# 3-Fund (60/20/20) Threshold Allocation Engine & Retirement Simulator

---

* A low-maintenance, highly resilient retirement planning tool and Monte Carlo simulation engine designed for long-term financial independence. The simulator models a sustainable 65-year retirement using an 80% Equity (60% US / 20% International) and 20% Fixed Income portfolio, supported by a 12-month cash reserve and a threshold-based rebalancing strategy.

* Rather than continuously rebalancing, the engine performs portfolio reviews only twice per year, allowing assets to drift naturally while minimizing unnecessary transactions. Spending is funded through a dedicated cash reserve, reducing the likelihood of selling long-term investments during unfavorable market conditions.

* The application uses Flask together with Server-Sent Events (SSE) and the JavaScript Streams API to provide real-time simulation progress updates without requiring page refreshes.

---

## 🚀 Quick Start

Prerequisites

- Python 3.8 or later

### Installation

1. Clone the repository

```bash
git clone <repository-url>
cd <repository-name>
```

Or simply navigate to your existing project directory.

2. Create a virtual environment

* macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

* Windows
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies

The project has a minimal dependency footprint.
```bash
pip install Flask
```

4. Run the application
```bash
python main.py
```

* The application will start a local web server.

* Open your browser and navigate to: http://127.0.0.1:5000

---

## 🏛️ Application Architecture

* The simulator is intentionally designed around a small set of deterministic rules. Rather than attempting to predict markets, it focuses on maintaining a stable spending process while allowing investments to compound over long periods.

---

### Cash Buffer

* At initialization, the engine immediately separates one full year of inflation-adjusted living expenses into a dedicated cash reserve ("self.cash").

* This reserve serves as the primary spending account throughout retirement.

* All regular withdrawals are funded from cash first, allowing the investment portfolio to remain untouched whenever possible.

---

### Spending Order

* The withdrawal hierarchy follows a deterministic order:

1. Spend from Cash.
1. If Cash is depleted, liquidate the asset class that is above its target allocation.
1. During prolonged equity downturns, harvest Bonds before Stocks whenever possible.
1. Resume normal threshold-based portfolio management once allocations return within acceptable ranges.

* This process helps reduce sequence-of-returns risk by avoiding unnecessary equity sales during major bear markets.

---

### Threshold-Based Rebalancing

* Portfolio reviews occur twice each year:
  - January
  - July

* Asset allocations are measured against the investable portfolio, excluding the target cash reserve.

* A rebalance is triggered only when an asset allocation exceeds its allowable drift threshold of ±5%.

* When triggered, allocations are restored to their target weights:

| Asset | Target Allocation |
| -------- | -------- |
| US Stocks  | 60%  | 
| International Stocks  | 20%  |
| Bonds | 20% |

* If no threshold has been crossed, no trades are executed.

* This significantly reduces turnover while still maintaining long-term allocation discipline.

---

### Cash Reserve Protection

* The cash reserve is intentionally treated separately from the investable portfolio.

* Rather than automatically replenishing cash every year, the reserve is refilled only when required by the rebalancing rules.

* This prevents unnecessary asset sales during periods when markets are temporarily depressed.

---

### Monte Carlo Simulation Engine

* The retirement simulator performs thousands of independent market simulations using randomized annual returns for each asset class.

* Each simulation models:
  - Portfolio growth
  - Inflation-adjusted spending
  - Cash reserve depletion
  - Threshold-based rebalancing
  - Portfolio longevity
  - Success or failure over the complete retirement horizon

* Because every simulation is independent, the engine can estimate long-term retirement success probabilities under a wide variety of market environments.

---

### Real-Time Progress Streaming

* Long-running Monte Carlo simulations are streamed to the browser using Server-Sent Events (SSE).

* Instead of waiting for the simulation to finish, the backend continuously emits progress updates through an open HTTP connection using the "text/event-stream" content type.

* The frontend consumes these updates using the JavaScript Streams API, allowing live updates for:
  - Simulation progress
  - Current iteration
  - Estimated completion
  - Running success statistics

* This architecture keeps the interface responsive even when executing 10,000+ simulations.

---

## 📖 Retirement Operating Manual

* The following sections describe the operational framework used to manage the retirement portfolio throughout the retirement period.

### 📊 Table 1: Asset Allocation & Target Funds

* The portfolio consists of a dedicated cash reserve and three investment funds. To simplify cash management, consider turning off automatic dividend reinvestment (DRIP) so that dividends accumulate in your brokerage settlement account and naturally help replenish the cash buffer.

|Asset Class| Target Allocation| Example ETF| Purpose |
| -------- | -------- | -------- | -------- |
| Cash Buffer| 12 Months of Annual Expenses| Brokerage Settlement Account / High-Yield Savings Account (HYSA)| Primary spending account. Provides one year of living expenses and reduces the need to sell investments during market downturns.|
|US Equities| 60% of Investable Portfolio| Vanguard Total Stock Market ETF (VTI)| Primary long-term growth engine designed to outpace inflation over multiple decades.|
|International Equities| 20% of Investable Portfolio| Vanguard Total International Stock ETF (VXUS)| Diversifies the portfolio across developed and emerging international markets.|
|Fixed Income (Bonds)| 20% of Investable Portfolio| Vanguard Total Bond Market ETF (BND)| Portfolio stabilizer that reduces volatility and provides a reliable source of liquidity during equity bear markets.|

**«Note:** The cash reserve is not considered part of the investable portfolio when calculating allocation percentages or rebalancing thresholds.»

---

### 📅 Table 2: Semi-Annual Execution Timeline

* The portfolio is intentionally designed to require minimal maintenance. Outside of routine monthly spending, portfolio management occurs only twice per year.

|Frequency| Time| Action| Checklist|
|----|----|----|----|
|Monthly| Automatic| Cash → Checking| Maintain an automatic monthly transfer from your Cash Buffer (brokerage settlement account or HYSA) into your checking account to cover living expenses. No investment transactions are required.|
|Semi-Annual| January 2| Full Portfolio Review| 1. Update your annual spending amount for inflation.<br>2. Calculate current asset allocations relative to the investable portfolio.<br>3. Determine whether any allocation has exceeded the ±5% threshold.<br>4. Execute the appropriate scenario from the rebalancing matrix.<br>5. Refill the Cash Buffer if required by that scenario.|
|Semi-Annual| July 2| Mid-Year Portfolio Review| 1. Review remaining Cash Buffer runway.<br>2. Recalculate portfolio allocations.<br>3. Determine whether any asset has breached the ±5% threshold.<br>4. Execute trades only if a threshold has been crossed. Otherwise, take no action.|

---

### ⚖️ Rebalancing Philosophy

* This retirement strategy intentionally avoids unnecessary trading.

* Unlike traditional portfolios that rebalance on a fixed schedule regardless of market conditions, this system follows a threshold-based approach.

* The portfolio is reviewed only twice each year, and trades occur only when one or more asset classes move beyond the permitted drift range.

* This approach provides several advantages:
  - Lower portfolio turnover
  - Reduced taxable events (where applicable)
  - Lower transaction costs
  - Greater participation in long-term market trends
  - Less emotional decision-making
  - Simpler long-term portfolio management

---

### 📏 Allocation Thresholds

* Each investable asset class has an allowable drift range of ±5% around its target allocation.

|Asset Class| Target| Lower Threshold| Upper Threshold|
|----|----|----|----|
|US Stocks| 60%| 55%| 65%|
|International Stocks| 20%| 15%| 25%|
|Bonds| 20%| 15%| 25%|

* As long as every asset remains within these boundaries, no portfolio changes are made.

* Only when at least one asset exceeds its allowable range does the portfolio move to the rebalancing decision matrix described in the following section.

---

### 🧭 Table 3: Complete 27-Scenario Rebalancing & Extraction Matrix

* At each January and July review, determine whether each investable asset class is:

  - Overweight (+) — Above its upper threshold / Above target
  - In-Band (0) — Within its allowable range / Within ±5% range
  - Underweight (-) — Below its lower threshold / Below target

* This creates 27 possible portfolio states (3 × 3 × 3).

* For each state, execute the corresponding action exactly as described in the following matrix.

**«Important:** If no asset class has crossed its threshold, do nothing. The strategy intentionally avoids unnecessary rebalancing.»

---

### 📊 All 27 Scenarios
| # | US Stocks| Intl Stocks| Bonds| Action| Interpretation |
|----|----|----|----|----|----|
|1| 0| 0| 0| Do nothing| Perfect equilibrium. No drift detected.|
|2| 0| 0| -| Do nothing| Minor bond weakness within tolerance.|
|3| 0| 0| +| Do nothing| Bonds slightly strong; no action required.|
|4| 0| -| 0| Do nothing| International weakness within tolerance band.|
|5| 0| +| 0| Do nothing| International strength is non-actionable.|
|6| -| 0| 0| Do nothing| US equities slightly weak but within band.|
|7| +| 0| 0| Do nothing| US equities slightly strong but within band.|
|8| +| 0| -| Sell US → refill Cash → Buy Bonds| US bull run harvested into fixed income.|
|9| 0| +| -| Sell Intl → refill Cash → Buy Bonds| International gains redirected to bonds.|
|10| +| +| -| Sell both equities → refill Cash → Buy Bonds| Broad equity rally, de-risk into bonds.|
|11| +| -| 0| Sell US → refill Cash → Buy Intl| Rotate from US into cheaper international equity.|
|12| -| +| 0| Sell Intl → refill Cash → Buy US| Rotate from international into US equities.|
|13| +| -| -| Sell US → refill Cash → Rebalance Intl + Bonds| US outperformance funds underweight assets.|
|14| -| +| -| Sell Intl → refill Cash → Rebalance US + Bonds| International outperformance redistributed.|
|15| -| 0| +| Sell Bonds → refill Cash → Buy US Stocks| Bonds fund US equity recovery.|
|16| 0| -| +| Sell Bonds → refill Cash → Buy Intl Stocks| Bonds fund international recovery.|
|17| -| -| +| Sell Bonds → refill Cash → Buy both equities| Bonds deployed into broad equity drawdown.|
|18| -| +| +| Sell Bonds + Intl → refill Cash → Buy US Stocks| US equity underperformance corrected.|
|19| +| -| +| Sell Bonds + US → refill Cash → Buy Intl Stocks| International equities become target allocation.|
|20| -| -| -| Do nothing| Deep systemic drawdown; cash buffer absorbs spending.|
|21| +| +| +| Do nothing| Broad market expansion; no structural imbalance.|
|22| 0| -| -| Do nothing| Mild international + bond weakness within tolerance.|
|23| 0| +| +| Do nothing| International + bonds strong but not actionable.|
|24| -| 0| -| Do nothing| US + bonds weak but within tolerance.|
|25| +| 0| +| Do nothing| Multi-asset strength without drift violation.|
|26| -| +| -| Sell Intl → refill Cash → Buy US + Bonds| International outperformance harvested.|
|27| +| -| 0| Sell US → refill Cash → Buy Intl| US outperformance rotated into international.|

---

### 🧠 System Behavior Summary

* The full 27-scenario engine encodes the following behaviors:

1. **Cash Buffer Priority**

    * All actions route through cash first, ensuring liquidity stability for ongoing withdrawals.

1. **Bonds as Primary Liquidity Source**

    * Bonds are the default funding source for portfolio rebalancing during equity stress environments.

1. **Equity Mean Reversion**

    * The system systematically:
      - Sells high-performing equities
      - Buys underperforming equities
      - Maintains long-term allocation balance without frequent intervention

1. **Rare Extreme States**

    * Certain scenarios intentionally trigger no action, even during volatility, because:
      - Cash buffer absorbs spending pressure
      - Temporary mispricings are allowed to persist
      - Over-trading is explicitly avoided

---

### 🛠️ Automated Fallback Guideline

* If manual intervention is required during extreme volatility or system uncertainty, use the following deterministic procedure:

---

**Step 1: Compute Total Portfolio Value**

```math
Total Net Worth = Cash + US Stocks + Intl Stocks + Bonds
```

---

**Step 2: Rebuild Cash Buffer**

Set aside:

«1 Year of Inflation-Adjusted Living Expenses»

Transfer this amount into the Cash Buffer (HYSA / Settlement Account).

---

**Step 3: Reallocate Remaining Portfolio**

Take all remaining capital and rebalance strictly into:

- 60% US Stocks (VTI)
- 20% International Stocks (VXUS)
- 20% Bonds (BND)

---

### 🧾 Final Design Principles

This system is built on four long-term principles:

1. Sequence-of-Returns Protection

    * A 12-month cash buffer prevents forced liquidation of equities during downturns.

1. Threshold-Based Discipline

    * Rebalancing occurs only when meaningful drift occurs (±5%), avoiding unnecessary trading noise.

1. Structural Simplicity

    * Only three investable asset classes are used, ensuring long-term maintainability.

1. Behavioral Isolation

    * Rules are deterministic and reduce emotional decision-making during volatility.

---
