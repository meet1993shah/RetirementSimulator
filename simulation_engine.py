from models.portfolio import Portfolio
from models.market import MarketState
from strategies.decision_engine import DecisionEngine

class SimulationEngine:
    
    @classmethod
    def run_single_simulation(cls, monthly_rows, us_alloc, intl_alloc, bond_alloc, initial_swr, n_months, drift_pct, drawdown_pct):
        """Executes a single Monte Carlo run across the provided historical sequence."""
        initial_portfolio_value = 1000000.0
        annual_spending = initial_portfolio_value * initial_swr
        current_monthly_spending = annual_spending / 12.0
        
        portfolio = Portfolio(initial_portfolio_value, us_alloc, intl_alloc, bond_alloc, annual_spending)
        
        # Track Pure Market Return indices for accurate crash detection
        us_market_index = 1.0
        us_market_peak = 1.0
        intl_market_index = 1.0
        intl_market_peak = 1.0
        
        for raw_row in monthly_rows:
            market = MarketState(raw_row)
            
            # Phase 1: Update True Market Indices
            us_market_index *= (1.0 + market.us_return)
            intl_market_index *= (1.0 + market.intl_return)
            
            us_market_peak = max(us_market_peak, us_market_index)
            intl_market_peak = max(intl_market_peak, intl_market_index)
            
            # Phase 2: Growth, Yields, and Economic adjustments
            current_monthly_spending = cls._update_inflation(current_monthly_spending, market.inflation)
            cls._apply_market_growth(portfolio, market)
            cls._distribute_income_to_cash(portfolio, market)
            
            # Phase 3: Spending and emergency liquidity
            survived = cls._process_living_expenses(portfolio, current_monthly_spending)
            if not survived:
                return False
                
            # Phase 4: Strategic Portfolio Rebalancing
            if market.month in [1, 7]:
                DecisionEngine.execute_harvest_and_rebalance(
                    portfolio, us_alloc, intl_alloc, bond_alloc, drift_pct, drawdown_pct, current_monthly_spending,
                    us_market_index, us_market_peak, intl_market_index, intl_market_peak
                )
                
        return True

    # ---------------------------------------------------------
    # Private Helper Methods
    # ---------------------------------------------------------

    @staticmethod
    def _update_inflation(current_spending, monthly_inflation):
        new_spending = current_spending
        if monthly_inflation > 0.0:
            new_spending *= (1.0 + monthly_inflation)
        return new_spending

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
            portfolio.bonds -= bond_yield_amount
        
        if market.us_dividend > 0.0:
            us_div_amount = portfolio.us_stocks * market.us_dividend
            portfolio.cash_buffer += us_div_amount
            portfolio.us_stocks -= us_div_amount
            
        if market.intl_dividend > 0.0:
            intl_div_amount = portfolio.intl_stocks * market.intl_dividend
            portfolio.cash_buffer += intl_div_amount
            portfolio.intl_stocks -= intl_div_amount

    @staticmethod
    def _process_living_expenses(portfolio, monthly_spending):
        """Fulfills monthly withdrawal, executing a 3-month emergency block drawdown if necessary."""
        if portfolio.cash_buffer >= monthly_spending:
            portfolio.cash_buffer -= monthly_spending
            return True
            
        shortfall = monthly_spending - portfolio.cash_buffer
        portfolio.cash_buffer = 0.0
        inv = portfolio.invested_pool
        
        if inv <= shortfall:
            return False  # Portfolio Ruined
            
        # Drawdown a 3-month block (or whatever is left) proportionally from invested assets
        drawdown_amount = min(monthly_spending * 3, inv)
        
        portfolio.us_stocks -= drawdown_amount * (portfolio.us_stocks / inv)
        portfolio.intl_stocks -= drawdown_amount * (portfolio.intl_stocks / inv)
        portfolio.bonds -= drawdown_amount * (portfolio.bonds / inv)
        
        # Fulfill immediate shortfall and retain remaining block in cash buffer
        portfolio.cash_buffer += (drawdown_amount - shortfall)
        return True
