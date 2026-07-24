class DecisionEngine:
    
    @classmethod
    def evaluate_portfolio(cls, portfolio, us_target, intl_target, bond_target, drift_pct, drawdown_pct, us_market_index, us_market_peak, intl_market_index, intl_market_peak):
        """Evaluates crash status based on pure market index and asset band deviations."""
        us_w, intl_w, bond_w = portfolio.get_weights()
        
        us_status = cls._get_band_status(us_w, us_target, drift_pct)
        intl_status = cls._get_band_status(intl_w, intl_target, drift_pct)
        bond_status = cls._get_band_status(bond_w, bond_target, drift_pct)
        
        is_crash = cls._check_crash_condition(us_market_index, us_market_peak, intl_market_index, intl_market_peak, drawdown_pct, us_status)
        
        statuses = {
            'us': us_status,
            'intl': intl_status,
            'bond': bond_status
        }
        return is_crash, statuses

    @classmethod
    def execute_harvest_and_rebalance(cls, portfolio, us_target, intl_target, bond_target, drift_pct, drawdown_pct, current_monthly_spending, us_market_index, us_market_peak, intl_market_index, intl_market_peak):
        """Main orchestration method for the harvest and capital allocation protocol."""
        is_crash, statuses = cls.evaluate_portfolio(
            portfolio, us_target, intl_target, bond_target, drift_pct, drawdown_pct,
            us_market_index, us_market_peak, intl_market_index, intl_market_peak
        )
        
        if cls._is_portfolio_balanced(statuses):
            return
            
        if portfolio.invested_pool <= 0.0:
            return
            
        # Step 1: Primary Harvest Action
        harvested_proceeds = cls._harvest_overweight_assets(
            portfolio, statuses, us_target, intl_target, bond_target
        )
        
        # Step 2: Top off Cash Buffer
        remaining_proceeds = cls._replenish_cash_buffer(
            portfolio, harvested_proceeds, current_monthly_spending, is_crash
        )
        
        # Step 3: Capital Allocation Protocol
        if remaining_proceeds > 0.0:
            cls._allocate_excess_proceeds(
                portfolio, remaining_proceeds, statuses, is_crash, 
                us_target, intl_target, bond_target
            )

    # ---------------------------------------------------------
    # Private Helper Methods: Evaluation
    # ---------------------------------------------------------

    @staticmethod
    def _get_band_status(current_weight, target_weight, drift_pct):
        if current_weight > target_weight + drift_pct:
            return "Over"
        if current_weight < target_weight - drift_pct:
            return "Under"
        return "In-Band"

    @staticmethod
    def _check_crash_condition(us_market_index, us_market_peak, intl_market_index, intl_market_peak, drawdown_pct, us_status):
        us_dd = (us_market_peak - us_market_index) / us_market_peak
        if us_dd >= drawdown_pct:
            return True
        if us_status == "Over":
            return False
        intl_dd = (intl_market_peak - intl_market_index) / intl_market_peak
        return intl_dd >= drawdown_pct

    @staticmethod
    def _is_portfolio_balanced(statuses):
        return all(status == "In-Band" for status in statuses.values())

    # ---------------------------------------------------------
    # Private Helper Methods: Execution
    # ---------------------------------------------------------

    @staticmethod
    def _harvest_overweight_assets(portfolio, statuses, us_target, intl_target, bond_target):
        """Sells assets that exceed their target bands and returns total proceeds."""
        proceeds = 0.0
        total_inv = portfolio.invested_pool
        
        if statuses['us'] == "Over":
            harvest = portfolio.us_stocks - (total_inv * us_target)
            portfolio.us_stocks -= harvest
            proceeds += harvest
            
        if statuses['intl'] == "Over":
            harvest = portfolio.intl_stocks - (total_inv * intl_target)
            portfolio.intl_stocks -= harvest
            proceeds += harvest
            
        if statuses['bond'] == "Over":
            harvest = portfolio.bonds - (total_inv * bond_target)
            portfolio.bonds -= harvest
            proceeds += harvest
            
        return proceeds

    @staticmethod
    def _replenish_cash_buffer(portfolio, proceeds, current_monthly_spending, is_crash):
        """Tops off cash buffer to target threshold and returns unspent proceeds."""
        target_cash_months = 6 if is_crash else 12
        target_cash_value = current_monthly_spending * target_cash_months
        
        cash_needed = max(0.0, target_cash_value - portfolio.cash_buffer)
        cash_topoff = min(proceeds, cash_needed)
        
        portfolio.cash_buffer += cash_topoff
        return proceeds - cash_topoff

    @classmethod
    def _allocate_excess_proceeds(cls, portfolio, proceeds, statuses, is_crash, us_target, intl_target, bond_target):
        """Routes remaining proceeds based on market regime and decision matrix."""
        if is_crash:
            cls._execute_crash_protocol(portfolio, proceeds, statuses)
        else:
            cls._execute_normal_protocol(portfolio, proceeds, statuses, us_target, intl_target, bond_target)

    @staticmethod
    def _execute_crash_protocol(portfolio, proceeds, statuses):
        """Capital Allocation Protocol for Bear Markets (>15% Drop)."""
        if statuses['us'] == "Under" and statuses['intl'] == "Under":
            portfolio.us_stocks += proceeds * 0.75
            portfolio.intl_stocks += proceeds * 0.25
        elif statuses['us'] == "Under":
            portfolio.us_stocks += proceeds
        elif statuses['intl'] == "Under":
            portfolio.intl_stocks += proceeds
        else:
            portfolio.cash_buffer += proceeds

    @staticmethod
    def _execute_normal_protocol(portfolio, proceeds, statuses, us_target, intl_target, bond_target):
        """Capital Allocation Protocol for Bull / Normal / Minor Dip environments."""
        us, intl, bond = statuses['us'], statuses['intl'], statuses['bond']
        
        if us == "Over":
            if intl == "Under" and bond == "Under":
                denom = intl_target + bond_target
                portfolio.intl_stocks += proceeds * (intl_target / denom)
                portfolio.bonds += proceeds * (bond_target / denom)
            elif intl == "Under":
                portfolio.intl_stocks += proceeds
            else:
                portfolio.bonds += proceeds
        elif intl == "Over":
            if us == "Under" and bond == "Under":
                denom = us_target + bond_target
                portfolio.us_stocks += proceeds * (us_target / denom)
                portfolio.bonds += proceeds * (bond_target / denom)
            elif us == "Under":
                portfolio.us_stocks += proceeds
            else:
                portfolio.bonds += proceeds
        else:
            if us == "Under" and intl == "Under":
                denom = us_target + intl_target
                portfolio.us_stocks += proceeds * (us_target / denom)
                portfolio.intl_stocks += proceeds * (intl_target / denom)
            elif us == "Under":
                portfolio.us_stocks += proceeds
            else:
                portfolio.intl_stocks += proceeds
