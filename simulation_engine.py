from models.portfolio import Portfolio
from models.market import MarketState
from strategies.decision_engine import DecisionEngine

class SimulationEngine:
    
    @classmethod
    def run_single_simulation(cls, monthly_rows, us_alloc, intl_alloc, bond_alloc, initial_swr, n_months, drift_pct, drawdown_pct):
        """Executes a single Monte Carlo run across the provided historical sequence."""
        initial_portfolio_value = 10000000.0
        annual_spending = initial_portfolio_value * initial_swr
        current_monthly_spending = annual_spending / 12.0
        
        portfolio = Portfolio(initial_portfolio_value, us_alloc, intl_alloc, bond_alloc, annual_spending)
        
        # Track Pure Market Return indices for accurate crash detection
        us_market_index = 1.0
        us_market_peak = 1.0
        intl_market_index = 1.0
        intl_market_peak = 1.0
        
        # Track cumulative inflation for semi-annual budget adjustments
        cumulative_inflation = 1.0
        
        for num_month, raw_row in enumerate(monthly_rows):
            market = MarketState(raw_row)
            
            # Phase 1: Update True Market Indices and Inflation
            us_market_index *= (1.0 + market.us_return)
            intl_market_index *= (1.0 + market.intl_return)
            
            us_market_peak = max(us_market_peak, us_market_index)
            intl_market_peak = max(intl_market_peak, intl_market_index)
            
            cumulative_inflation *= (1.0 + market.inflation)

            # Phase 2: Growth and Yields
            cls._apply_market_growth(portfolio, market)
            cls._distribute_income_to_cash(portfolio, market)
            
            # Phase 3: Spending and emergency liquidity
            survived = cls._process_living_expenses(portfolio, current_monthly_spending)
            if not survived:
                return False
                
            # Phase 4: Strategic Portfolio Rebalancing (Semi-Annually)
            if (num_month % 12 == 0) or (num_month % 12 == 6):
                # 1. Calculate inflation-adjusted spending budget
                current_monthly_spending *= cumulative_inflation
                cumulative_inflation = 1.0  # Reset for the next 6-month window
                
                # 2. Check asset weights, drawdowns, and execute decision matrix
                DecisionEngine.execute_harvest_and_rebalance(
                    portfolio, us_alloc, intl_alloc, bond_alloc, drift_pct, drawdown_pct, current_monthly_spending,
                    us_market_index, us_market_peak, intl_market_index, intl_market_peak
                )
                
        return True

    # ---------------------------------------------------------
    # Private Helper Methods
    # ---------------------------------------------------------

    @staticmethod
    def _apply_market_growth(portfolio, market):
        """Applies HYSA interest and market capital appreciation."""
        portfolio.cash_buffer *= (1.0 + market.hysa_interest)
        portfolio.us_stocks *= (1.0 + market.us_return)
        portfolio.intl_stocks *= (1.0 + market.intl_return)
        portfolio.bonds *= (1.0 + market.bond_return)

    @staticmethod
    def _distribute_income_to_cash(portfolio, market):
        """Routes yields to cash buffer and deducts them from assets to prevent 'infinite money'."""
        if market.bond_interest_rate > 0.0:
            bond_yield_amount = portfolio.bonds * market.bond_interest_rate
            portfolio.cash_buffer += bond_yield_amount
        
        if market.us_dividend > 0.0:
            us_div_amount = portfolio.us_stocks * market.us_dividend
            portfolio.cash_buffer += us_div_amount
            
        if market.intl_dividend > 0.0:
            intl_div_amount = portfolio.intl_stocks * market.intl_dividend
            portfolio.cash_buffer += intl_div_amount

    @staticmethod
    def _process_living_expenses(portfolio, monthly_spending):
        """Fulfills monthly withdrawal, preventing negative asset balances."""
        if portfolio.cash_buffer >= monthly_spending:
            portfolio.cash_buffer -= monthly_spending
            return True
            
        shortfall = monthly_spending - portfolio.cash_buffer
        portfolio.cash_buffer = 0.0
        inv = portfolio.invested_pool
        
        if inv <= shortfall:
            return False  # Portfolio Ruined
            
        drawdown_amount = min(monthly_spending * 3, inv)
        
        # Calculate strict target pulls
        to_pull_us = drawdown_amount * portfolio.us_alloc
        to_pull_intl = drawdown_amount * portfolio.intl_alloc
        to_pull_bonds = drawdown_amount * portfolio.bond_alloc
        
        # Safely cap the pull at whatever is actually available in the asset
        actual_us = min(to_pull_us, portfolio.us_stocks)
        actual_intl = min(to_pull_intl, portfolio.intl_stocks)
        actual_bonds = min(to_pull_bonds, portfolio.bonds)
        
        # Deduct the safe amounts
        portfolio.us_stocks -= actual_us
        portfolio.intl_stocks -= actual_intl
        portfolio.bonds -= actual_bonds
        
        # If an asset was empty, we have a leftover remainder to pull from survivors
        remainder = drawdown_amount - (actual_us + actual_intl + actual_bonds)
        if remainder > 0.001:
            cur_inv = portfolio.invested_pool
            if cur_inv > 0:
                portfolio.us_stocks -= remainder * (portfolio.us_stocks / cur_inv)
                portfolio.intl_stocks -= remainder * (portfolio.intl_stocks / cur_inv)
                portfolio.bonds -= remainder * (portfolio.bonds / cur_inv)
        
        # Fulfill immediate shortfall and retain remaining block in cash buffer
        portfolio.cash_buffer += (drawdown_amount - shortfall)
        return True
