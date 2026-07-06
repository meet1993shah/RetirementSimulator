import json
import math
import random
from typing import Dict, Any, Optional, Generator
from flask import Flask, render_template, request, Response

app = Flask(__name__)

# =====================================================================
# SIMULATION ENGINE
# =====================================================================

class SimulationEngine:
    def __init__(self, initial_nw: float, initial_expenses: float, 
                 us_stock_mu: float, us_stock_sigma: float,
                 intl_stock_mu: float, intl_stock_sigma: float,
                 bond_rate: float, inflation_mu: float, horizon_years: int, 
                 rng_instance: random.Random) -> None:
        
        self.rng = rng_instance
        self.horizon_years: int = horizon_years
        
        self.us_stock_mu: float = us_stock_mu
        self.us_stock_sigma: float = us_stock_sigma
        self.intl_stock_mu: float = intl_stock_mu
        self.intl_stock_sigma: float = intl_stock_sigma
        
        self.bond_rate: float = bond_rate
        self.bond_sigma: float = 0.04
        
        self.inflation_target: float = inflation_mu
        self.inflation_sigma: float = 0.012    
        self.inflation_kappa: float = 0.25     
        self.current_inflation_rate: float = inflation_mu
        
        self.target_us_pct = 0.60
        self.target_intl_pct = 0.20
        self.target_bond_pct = 0.20
        self.drift_threshold = 0.05

        self.cash: float = initial_expenses * 1.0
        remaining_nw = max(0.0, initial_nw - self.cash)
        
        self.us_stocks: float = remaining_nw * self.target_us_pct
        self.intl_stocks: float = remaining_nw * self.target_intl_pct
        self.bonds: float = remaining_nw * self.target_bond_pct
        
        self.annual_expenses: float = initial_expenses
        self.is_insolvent: bool = False

    def _update_inflation_annually(self) -> None:
        drift = self.inflation_kappa * (self.inflation_target - self.current_inflation_rate)
        shock = self.inflation_sigma * self.rng.normalvariate(0, 1)
        self.current_inflation_rate = max(-0.01, self.current_inflation_rate + drift + shock)

    def _update_markets_monthly(self, dt: float = 1.0 / 12.0) -> None:
        if self.cash > 0:
            cash_rate = max(0.0, self.bond_rate - 0.01)
            self.cash *= math.exp((cash_rate - 0.5 * 0.005**2) * dt + 0.005 * math.sqrt(dt) * self.rng.normalvariate(0, 1))

        if self.bonds > 0:
            self.bonds *= math.exp((self.bond_rate - 0.5 * self.bond_sigma**2) * dt + self.bond_sigma * math.sqrt(dt) * self.rng.normalvariate(0, 1))

        if self.us_stocks > 0:
            self.us_stocks *= math.exp((self.us_stock_mu - 0.5 * self.us_stock_sigma**2) * dt + self.us_stock_sigma * math.sqrt(dt) * self.rng.normalvariate(0, 1))

        if self.intl_stocks > 0:
            self.intl_stocks *= math.exp((self.intl_stock_mu - 0.5 * self.intl_stock_sigma**2) * dt + self.intl_stock_sigma * math.sqrt(dt) * self.rng.normalvariate(0, 1))

    def _execute_annual_withdrawal(self) -> None:
        withdrawal_needed = self.annual_expenses
        
        if self.cash >= withdrawal_needed:
            self.cash -= withdrawal_needed
            return
            
        shortfall = withdrawal_needed - self.cash
        self.cash = 0.0
        
        total_invested = self.us_stocks + self.intl_stocks + self.bonds
        if total_invested <= 0:
            self.is_insolvent = True
            return
            
        current_equity_pct = (self.us_stocks + self.intl_stocks) / total_invested
        
        if current_equity_pct > 0.80:
            total_equities = self.us_stocks + self.intl_stocks
            if total_equities >= shortfall:
                us_ratio = self.us_stocks / total_equities if total_equities > 0 else 0.75
                self.us_stocks -= shortfall * us_ratio
                self.intl_stocks -= shortfall * (1 - us_ratio)
            else:
                shortfall -= total_equities
                self.us_stocks = 0.0
                self.intl_stocks = 0.0
                self.bonds -= shortfall
        else:
            if self.bonds >= shortfall:
                self.bonds -= shortfall
            else:
                shortfall -= self.bonds
                self.bonds = 0.0
                total_equities = self.us_stocks + self.intl_stocks
                if total_equities >= shortfall:
                    us_ratio = self.us_stocks / total_equities if total_equities > 0 else 0.75
                    self.us_stocks -= shortfall * us_ratio
                    self.intl_stocks -= shortfall * (1 - us_ratio)
                else:
                    self.us_stocks = 0.0
                    self.intl_stocks = 0.0
                    self.is_insolvent = True

        if (self.cash + self.bonds + self.us_stocks + self.intl_stocks) <= 0:
            self.is_insolvent = True

    def _check_and_execute_rebalance(self) -> None:
        total_portfolio = self.cash + self.bonds + self.us_stocks + self.intl_stocks
        if total_portfolio <= 0:
            return

        target_cash = self.annual_expenses
        remaining_allocatable = max(0.0, total_portfolio - target_cash)
        
        target_us = remaining_allocatable * self.target_us_pct
        target_intl = remaining_allocatable * self.target_intl_pct
        target_bond = remaining_allocatable * self.target_bond_pct
        
        denom = remaining_allocatable if remaining_allocatable > 0 else total_portfolio
        us_drift = abs((self.us_stocks - target_us) / denom)
        intl_drift = abs((self.intl_stocks - target_intl) / denom)
        bond_drift = abs((self.bonds - target_bond) / denom)
        cash_drift = abs((self.cash - target_cash) / total_portfolio)

        if us_drift > self.drift_threshold or intl_drift > self.drift_threshold or bond_drift > self.drift_threshold or cash_drift > self.drift_threshold:
            self.cash = target_cash
            self.us_stocks = target_us
            self.intl_stocks = target_intl
            self.bonds = target_bond

    def run_simulation(self) -> Optional[int]:
        for year in range(1, self.horizon_years + 1):
            if self.is_insolvent:
                return year
            self._execute_annual_withdrawal()

            for month in range(1, 13):
                if self.is_insolvent:
                    return year
                self._update_markets_monthly(dt=1.0 / 12.0)
                
                if month in [6, 12] and not self.is_insolvent:
                    self._check_and_execute_rebalance()

            self._update_inflation_annually()
            self.annual_expenses *= (1.0 + self.current_inflation_rate)
                    
        return None if not self.is_insolvent else self.horizon_years


# =====================================================================
# HTTP ENDPOINTS CONTROLLER
# =====================================================================

@app.route('/')
def index() -> str:
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate() -> Response:
    payload: Dict[str, Any] = request.get_json() or {}
    
    try:
        net_worth = max(1000.0, float(payload.get('net_worth', 0)))
        expenses = max(1000.0, float(payload.get('expenses', 0)))
        us_stock_rate = float(payload.get('us_stock_rate', 0.08))
        us_stock_sigma = float(payload.get('us_stock_sigma', 0.16))
        intl_stock_rate = float(payload.get('intl_stock_rate', 0.075))
        intl_stock_sigma = float(payload.get('intl_stock_sigma', 0.18))
        bond_rate = float(payload.get('bond_rate', 0.04))
        inflation_rate = float(payload.get('inflation_rate', 0.025))
        horizon = max(1, int(payload.get('horizon', 65)))
        num_simulations = max(1, int(payload.get('num_simulations', 2000)))
    except (ValueError, TypeError):
        return Response("json: {\"error\": \"Invalid parameters\"}", status=400, mimetype='application/json')

    def event_stream_generator() -> Generator[str, None, None]:
        shared_rng = random.Random()
        successful_runs = 0
        insolvent_runs = 0
        ruin_years_sum = 0
        
        # Determine notification chunks dynamically (every 5% completed)
        update_interval = max(1, num_simulations // 20)

        for i in range(1, num_simulations + 1):
            engine = SimulationEngine(
                initial_nw=net_worth, initial_expenses=expenses,
                us_stock_mu=us_stock_rate, us_stock_sigma=us_stock_sigma,
                intl_stock_mu=intl_stock_rate, intl_stock_sigma=intl_stock_sigma,
                bond_rate=bond_rate, inflation_mu=inflation_rate,
                horizon_years=horizon, rng_instance=shared_rng
            )
            ruin_year = engine.run_simulation()
            
            if ruin_year is not None:
                insolvent_runs += 1
                ruin_years_sum += ruin_year
            else:
                successful_runs += 1
            
            if i % update_interval == 0 or i == num_simulations:
                progress_pct = round((i / num_simulations) * 100, 1)
                yield f"data: {json.dumps({'type': 'progress', 'percentage': progress_pct})}\n\n"

        avg_insolvency_year = round(ruin_years_sum / insolvent_runs, 1) if insolvent_runs > 0 else 0.0
        success_rate_pct = round((successful_runs / num_simulations) * 100, 2)

        final_data = {
            "type": "final",
            "total_simulations": num_simulations,
            "successful_runs": successful_runs,
            "insolvent_runs": insolvent_runs,
            "success_rate_pct": success_rate_pct,
            "avg_insolvency_year": avg_insolvency_year
        }
        yield f"data: {json.dumps(final_data)}\n\n"

    return Response(event_stream_generator(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
