# 3-Fund (60/20/20) Threshold Allocation Engine & Retirement Simulator

A low-maintenance, ultra-reliable retirement planning tool and Monte Carlo simulation engine. This application models a highly sustainable 65-year horizon built on an **80% Equity (60% US / 20% International) and 20% Fixed Income** asset matrix, supported by a 12-month liquid cash shield and threshold-based drift rebalancing.

The application leverages a responsive, asynchronous streaming protocol (**Server-Sent Events**) via Flask and the JavaScript Streams API to update simulation progress metrics in real-time.


## 🚀 Quick Start & Installation

### 1. Prerequisites

Ensure you have Python 3.8+ installed on your system.

### 2. Environment Setup

Clone or navigate to your project directory and create a virtual environment:

* Create virtual environment: `python3 -m venv venv`

* Activate on macOS/Linux: `source venv/bin/activate`

* Activate on Windows: `.\venv\Scripts\activate`


### 3. Install Dependencies

Install Flask (the only required backend framework) via your terminal:
`pip install Flask`

### 4. Run the Application

Execute the backend controller script:
`python main.py`

Open your browser and navigate to **[http://127.0.0.1:5000](https://www.google.com/search?q=http://127.0.0.1:5000)** to interact with the system interface.

---

## 🏛️ Application Architecture & Core Logic

* **Deterministic Cash Buffer Extraction:** The engine initializes by setting aside exactly 1 Year of baseline living expenses into a High-Yield liquid account (`self.cash`). Annual spending demands draw down from this shield first.


* **Order-of-Operations Shortfall Recovery:** If liquid cash drops to zero during a severe market drawdown, shortfalls are algorithmically harvested from the asset pool currently drifted above target limits. If equities are underperforming, the system enters Safe-Harbor Mode, liquidating stable bonds (`self.bonds`) first to avoid selling equities at a cyclical bottom.


* **Investable Pool Drift Metric:** Rebalancing checks occur semi-annually (Months 6 and 12). Drifts are calculated strictly against the allocatable investable asset pool base (`total_portfolio - target_cash`) to avoid cash-buffer denominator dampening, resetting the system to exactly 60/20/20 when any asset breaks past a clean $\pm5\%$ boundary.


* **Asynchronous Event Streaming (SSE):** The backend processes chunks of simulations dynamically, yielding structural text updates down an open HTTP pipe (`text/event-stream`), enabling a zero-lag frontend progress bar even across 10,000 continuous random-walk iterations.



---

## 📖 The Retirement Manual: Step-by-Step Execution Guidelines

Use the following operational framework to manage your real-world portfolio over a long-term horizon.

### Table 1: Asset Allocation & Target Funds

This matrix details your structural allocation. To maintain maximum simplicity, **turn off automatic dividend reinvestment** on your brokerage accounts so distributions flow straight into your cash settlement layer.

| Asset Class | Target Allocation | Example Fund Name (ETF) | Operational Mandate |
| --- | --- | --- | --- |
| **Cash Buffer** | 12 Months of Expenses | Brokerage Settlement / High-Yield Savings (HYSA) | Primary funding pipeline; insulates long-term equity layers from short-term liquidity shocks.

 |
| **US Equities** | 60% of investable pool | Vanguard Total Stock Market (VTI) | Principal compounding growth asset engineered to outpace structural inflation.

 |
| **International Equities** | 20% of investable pool | Vanguard Total International Stock (VXUS) | Global market diversification layer to hedge country-specific structural risks.

 |
| **Fixed Income / Bonds** | 20% of investable pool | Vanguard Total Bond Market (BND) | Deflation hedge, ballast, and secondary spending stabilizer.

 |

### Table 2: The Semi-Annual Execution Timeline

To keep maintenance low, review your portfolio exactly twice per year on a calendar schedule.

| Frequency | Action Window | Target Mechanism | Operational Checklist |
| --- | --- | --- | --- |
| **Monthly** | Fully Automated | Cash Buffer $\rightarrow$ Checking Account | Set up an automated recurring monthly clearing transfer from your settlement/savings account into your daily checking account to cover regular living costs.

 |
| **Semi-Annually** | January 2nd | Portfolio Matrix Evaluation | 1. Recalculate your trailing inflation-adjusted annual spending budget.<br>

<br>2. Calculate your asset allocation weights relative to the investable pool.<br>

<br>3. Refill the liquid cash shield to 100% only if target rebalancing thresholds are crossed.

 |
| **Semi-Annually** | July 2nd | Portfolio Matrix Evaluation | 1. Check current liquid cash shield runway metrics.<br>

<br>2. Evaluate asset weights for drift boundaries.<br>

<br>3. Execute a balancing correction only if an explicit threshold is broken.

 |

### Table 3: Complete 27-Scenario Rebalancing & Extraction Matrix

During your January and July review windows, check your current asset weights against your targets. If no asset class has moved up or down by more than $\pm5\%$ relative to your investable layer, **do absolutely nothing**. If a threshold is crossed, find your scenario below and execute the exact trade instructions.

| # | US Stock State | Intl Stock State | Bonds State | Exact Portfolio Action to Execute | Operational Intent & System Mechanics |
| --- | --- | --- | --- | --- | --- |
| **1** | In-Band (0) | In-Band (0) | In-Band (0) | **Do Absolutely Nothing.** | Perfect structural equilibrium. Disconnect and log out.

 |
| **2** | In-Band (0) | In-Band (0) | Under (-) | **Do Absolutely Nothing.** | Bonds are slightly soft, but drift hasn't hit the action boundary trigger.

 |
| **3** | In-Band (0) | In-Band (0) | Over (+) | **Do Absolutely Nothing.** | Bonds grew slightly; within tolerable noise bounds.

 |
| **4** | In-Band (0) | Under (-) | In-Band (0) | **Do Absolutely Nothing.** | International equities are depressed but within tolerance limits.

 |
| **5** | In-Band (0) | Over (+) | In-Band (0) | **Do Absolutely Nothing.** | International equities outperformed minorly; let compounding ride.

 |
| **6** | Under (-) | In-Band (0) | In-Band (0) | **Do Absolutely Nothing.** | US equities dipped slightly; no action required.

 |
| **7** | Over (+) | In-Band (0) | In-Band (0) | **Do Absolutely Nothing.** | US equities gained slightly; within safe parameters.

 |
| **8** | Over (+) | In-Band (0) | Under (-) | Sell US Stocks down to target. Fill Cash to 100%, then put all remaining proceeds into Bonds.

 | Equity bull run. Harvest domestic winners to lock in your living cash and buy bonds at a discount.

 |
| **9** | In-Band (0) | Over (+) | Under (-) | Sell Intl Stocks down to target. Fill Cash to 100%, then put all remaining proceeds into Bonds.

 | International bull run. Harvest global gains to reinforce your fixed-income safety floor.

 |
| **10** | Over (+) | Over (+) | Under (-) | Sell both US and Intl Stocks down to target. Fill Cash to 100%, then put the remainder into Bonds.

 | Global equity boom. Skim excess profits across all stock positions to reinforce your stable reserves.

 |
| **11** | Over (+) | Under (-) | In-Band (0) | Sell US Stocks down to target. Top off Cash to 100%, then use the remaining proceeds to buy Intl Stocks.

 | Divergent equity behavior. Harvest domestic gains to deliberately shift capital into cheaper international assets.

 |
| **12** | Under (-) | Over (+) | In-Band (0) | Sell Intl Stocks down to target. Top off Cash to 100%, then use the remaining proceeds to buy US Stocks.

 | Reverse divergence. Harvest outperforming international shares to pick up discounted domestic index funds.

 |
| **13** | Over (+) | Under (-) | Under (-) | Sell US Stocks down to target. Top off Cash, then allocate remaining proceeds to bring both Intl Stocks and Bonds back up to target.

 | Mega domestic bull run. Single-asset outperformance feeds your cash reserves and normalizes laggards.

 |
| **14** | Under (-) | Over (+) | Under (-) | Sell Intl Stocks down to target. Top off Cash, then allocate remaining proceeds to bring both US Stocks and Bonds back up to target.

 | Mega international bull run. Reallocate international windfall to balance domestic equities and fixed income.

 |
| **15** | Under (-) | In-Band (0) | Over (+) | Sell Bonds down to target. Top off Cash to 100%, then buy US Stocks up to target weight.

 | Domestic bear market. Bonds acted as a shield; use them to buy cheap domestic equity blocks.

 |
| **16** | In-Band (0) | Under (-) | Over (+) | Sell Bonds down to target. Top off Cash to 100%, then buy Intl Stocks up to target weight.

 | International bear market. Safe-haven fixed income is harvested to purchase global stock assets on sale.

 |
| **17** | Under (-) | Under (-) | Over (+) | Sell Bonds down to target. Top off Cash to 100%, then buy both US and Intl Stocks back up to target.

 | Severe global bear market. Fixed income serves its purpose as an emergency buffer; you buy cheap equities globally.

 |
| **18** | Under (-) | Over (+) | Over (+) | Sell Bonds and Intl Stocks down to target. Top off Cash, then buy US Stocks back up to target.

 | Mixed environment. Domestic equities crashed while bonds and global indexes held firm. Move cash to domestic stocks.

 |
| **19** | Over (+) | Under (-) | Over (+) | Sell US Stocks and Bonds down to target. Top off Cash, then buy Intl Stocks back up to target.

 | Mixed environment. Global equities crashed while bonds and domestic large-caps stayed high. Reallocate to international.

 |
| **20** | Under (-) | Under (-) | Under (-) | **Do Absolutely Nothing.** | The High-Cash Shock Case: If all investments are low relative to cash, cash is overweighted. Let the cash buffer safely draw down.

 |
| **21** | Over (+) | Over (+) | Over (+) | **Do Absolutely Nothing.** | The Growth Bubble Case: All long-term funds outpaced cash growth uniformly. Your buying power increased, no asset rebalance needed.

 |
| **22** | In-Band (0) | Under (-) | Under (-) | **Do Absolutely Nothing.** | Minor correlated downturn across international and fixed income. Assets haven't breached thresholds.

 |
| **23** | In-Band (0) | Over (+) | Over (+) | **Do Absolutely Nothing.** | International and bonds gained strength over domestic holdings without crossing actionable target boundaries.

 |
| **24** | Under (-) | In-Band (0) | Under (-) | **Do Absolutely Nothing.** | International stocks preserved baseline value while domestic assets fell. Allow the cash buffer to draw down normally.

 |
| **25** | Over (+) | In-Band (0) | Over (+) | **Do Absolutely Nothing.** | Multi-asset appreciation without internal structural distortion between the components.

 |
| **26** | Under (-) | Over (+) | Under (-) | Sell Intl Stocks down to target. Top off Cash to 100%, then buy US Stocks and Bonds back up to weight.

 | Rare decoupling where international markets rocket upwards independently. Skim gains to fix domestic positions.

 |
| **27** | Over (+) | Under (-) | In-Band (0) | Sell US Stocks down to target. Top off Cash to 100%, then buy Intl Stocks up to target weight.

 | Domestic markets decouple upward from international stagnancy. Standard profit extraction to fund global value.

 |

---

## 🛠️ Automated Fallback Guideline

If you ever find yourself in a highly volatile market and need to manually resolve a fractional discrepancy, use this single fallback calculation:

1. **Aggregate your entire liquid net worth:**

$$\text{Total Asset Net Worth} = \text{Cash} + \text{US Stocks} + \text{Intl Stocks} + \text{Bonds}$$


2. Carve out exactly **1 Year of Current Inflation-Adjusted Expenses** and move it to your Cash Account.


3. Take all remaining capital and split it up using standard market buys/sells: **60% VTI**, **20% VXUS**, and **20% BND**.