# 3-Fund Retirement Simulator

---

A lightweight Flask web application that models long-term retirement portfolio survival rates using **Block Bootstrap Monte Carlo simulations** (historical data spanning 1928–2025) combined with dynamic cash buffer protection rules.

---

## Demo

![](demo/demo.gif)

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
|Monthly| Automatic| Cash → Checking| 1. Automate recurring transfer from savings to checking for spending every month. <br>2. Direct all portfolio dividends (VTI, VXUS) into Cash Buffer rather than auto-reinvesting. <br>3. Direct all bond yields (BND) into Cash Buffer rather than auto-reinvesting.|
|Semi-Annual| January 2| Full Portfolio Review| 1. Calculate inflation-adjusted spending budget. <br>2. Check asset weights against +/- 5% drift threshold. <br>3. Check Market Drawdown (>15% drop). <br>4. Execute Decision Matrix.|
|Semi-Annual| July 2| Mid-Year Portfolio Review| 1. Calculate inflation-adjusted spending budget. <br>2. Check asset weights against +/- 5% drift threshold. <br>3. Check Market Drawdown (>15% drop). <br>4. Execute Decision Matrix.|

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

### 🧭 Table 3: Complete Scenario Rebalancing & Extraction Matrix

* At each January and July review, determine whether each investable asset class is:

  - Overweight (+) — Above its upper threshold / Above target
  - In-Band (0) — Within its allowable range / Within ±5% range
  - Underweight (-) — Below its lower threshold / Below target

* For each state, execute the corresponding action exactly as described in the following matrix.

**«Important:** If no asset class has crossed its threshold, do nothing. The strategy intentionally avoids unnecessary rebalancing.»

---

### 📊 All Scenarios
| US Stocks | Intl Stocks | Bonds | Market Condition | Cash Target | Primary Harvest Action | Capital Allocation Protocol | Strategic Intent |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| In-Band | In-Band | In-Band | Any | Maintain Current | None | Draw cash for living expenses. If cash reaches 0, execute proportional drawdown (60% VTI / 20% VXUS / 20% BND) in 3-month blocks. | Equilibrium. Maintain holdings and do not interrupt compounding. |
| Over (+) | In-Band | Under (-) | Normal / Bull | 12 Months | Sell US Stocks down to target | 1. Top off Cash Buffer to 12 months.<br>2. Allocate 100% of remaining proceeds into Bonds. | Domestic bull run. Lock in living runway and buy bonds at a discount. |
| Over (+) | Under (-) | In-Band | Normal / Bull | 12 Months | Sell US Stocks down to target | 1. Top off Cash Buffer to 12 months.<br>2. Use remaining proceeds to buy Intl Stocks up to target. | Divergent equity behavior. Harvest domestic gains to buy cheaper international assets. |
| Over (+) | Under (-) | Over (+) | Normal / Bull | 12 Months | Sell US Stocks & Bonds down to target | 1. Top off Cash Buffer to 12 months.<br>2. Buy Intl Stocks up to target weight. | Mixed environment. Harvest domestic gains and bonds to fund international value. |
| Over (+) | Under (-) | Under (-) | Normal / Bull | 12 Months | Sell US Stocks down to target | 1. Top off Cash Buffer to 12 months.<br>2. Allocate remaining proceeds to bring both Intl Stocks and Bonds to target. | Mega domestic bull run. Outperformance normalizes laggards across the portfolio. |
| Over (+) | Over (+) | Under (-) | Normal / Bull | 12 Months | Sell both US & Intl Stocks down to target | 1. Top off Cash Buffer to 12 months.<br>2. Allocate 100% of remaining proceeds into Bonds. | Global equity boom. Skim excess gains across all stocks to reinforce safe reserves. |
| In-Band | Over (+) | Under (-) | Normal / Bull | 12 Months | Sell Intl Stocks down to target | 1. Top off Cash Buffer to 12 months.<br>2. Allocate 100% of remaining proceeds into Bonds. | International bull run. Harvest global gains to reinforce fixed-income floor. |
| Under (-) | Over (+) | In-Band | Normal / Bull | 12 Months | Sell Intl Stocks down to target | 1. Top off Cash Buffer to 12 months.<br>2. Use remaining proceeds to buy US Stocks up to target. | Reverse divergence. Harvest international outperformance to buy discounted domestic stocks. |
| Under (-) | Over (+) | Under (-) | Normal / Bull | 12 Months | Sell Intl Stocks down to target | 1. Top off Cash Buffer to 12 months.<br>2. Allocate remaining proceeds to bring both US Stocks and Bonds to target. | Mega international bull run. Reallocate international windfall to balance domestic stocks and bonds. |
| Under (-) | Over (+) | Over (+) | Minor Dip (<15%) | 12 Months | Sell Bonds & Intl Stocks down to target | 1. Top off Cash Buffer to 12 months.<br>2. Buy US Stocks back to target weight. | Mixed environment. Move excess global index and bond funds into domestic stocks. |
| Under (-) | Over (+) | Over (+) | Crash (>15%) | 6 Months | Sell Bonds & Intl Stocks down to target | 1. Top off Cash Buffer to 6 months ONLY.<br>2. Allocate ALL remaining proceeds to buy discounted US Stocks. | Crash execution. Harvest firm assets to load up on heavily discounted domestic shares. |
| Under (-) | In-Band | Over (+) | Minor Dip (<15%) | 12 Months | Sell Bonds down to target | 1. Top off Cash Buffer to 12 months.<br>2. Buy US Stocks up to target with remaining proceeds. | Standard rebalance. Preserve 12-month cushion while buying minor equity dips. |
| Under (-) | In-Band | Over (+) | Crash (>15%) | 6 Months | Sell Bonds down to target | 1. Top off Cash Buffer to 6 months ONLY.<br>2. Allocate ALL excess proceeds to buy discounted US Stocks. | Bear Market Rule. Bond shield active. Maximize buying power in cheap domestic equities. |
| In-Band | Under (-) | Over (+) | Minor Dip (<15%) | 12 Months | Sell Bonds down to target | 1. Top off Cash Buffer to 12 months.<br>2. Buy Intl Stocks up to target with remaining proceeds. | Standard rebalance. Preserve 12-month cushion while buying international value. |
| In-Band | Under (-) | Over (+) | Crash (>15%) | 6 Months | Sell Bonds down to target | 1. Top off Cash Buffer to 6 months ONLY.<br>2. Allocate ALL excess proceeds to buy discounted Intl Stocks. | Bear Market Rule. Fixed income harvested to fund discounted international equities. |
| Under (-) | Under (-) | Over (+) | Minor Dip (<15%) | 12 Months | Sell Bonds down to target | 1. Top off Cash Buffer to 12 months.<br>2. Buy US and Intl Stocks back to target weight. | Standard global dip. Preserve 12-month runway and rebalance stock allocations. |
| Under (-) | Under (-) | Over (+) | Crash (>15%) | 6 Months | Sell Bonds down to target | 1. Top off Cash Buffer to 6 months ONLY.<br>2. Split excess proceeds 75/25 to buy US & Intl Stocks back to target. | Severe Bear Market. Fixed income acts as emergency reserve; maximize equity buying at market bottom. |

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

## Creating Android APP

* I'm assuming you've already performed the steps mentioned in Getting Started Section

1. **Install Buildozer:** Install Buildozer
```bash
pip3 install --user --upgrade buildozer
```

2. **Connect Android Device:** Connect your android device to the local machine, you can check if the device is connected or not by the following bash commands
```bash
adb devices
# If the service needs to start
adb start-server
adb --help
```

3. **Update Buildozer Spec:** If needed you can change the spec info in buildozer.spec file

4. **Run Buildozer:** Run Buildozer
```bash
buildozer -v android debug deploy run logcat > app_log.txt
```
* this will take a long time to build on the first run, on successful completion you'll find the apk file in bin/ folder
* this will also create a app_log.txt file for debugging and logging
* the apk will automatically be installed on your Android Device on success

---