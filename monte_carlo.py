import json
from data.historical_loader import HistoricalLoader
from data.bootstrap import BlockBootstrap
from simulation_engine import SimulationEngine

class MonteCarloSimulator:
    @staticmethod
    def stream_simulation(us_alloc, intl_alloc, bond_alloc, n_sims, n_years, block_size_years, drift_pct, drawdown_pct, initial_swr, step_swr, success_threshold):
        hist_data = HistoricalLoader.load_dataset()
        n_months = n_years * 12
        block_size_months = block_size_years * 12
        
        curr = initial_swr
        success_rate = 100.0
        
        while success_rate >= success_threshold:
            success_count = 0
            for _ in range(n_sims):
                returns_seq = BlockBootstrap.get_bootstrap_sequence(hist_data, n_months, block_size_months)
                survived = SimulationEngine.run_single_simulation(
                    returns_seq, us_alloc, intl_alloc, bond_alloc, curr, n_months, drift_pct, drawdown_pct
                )
                if survived:
                    success_count += 1
            
            success_rate = (success_count / n_sims) * 100.0
            rate_pct = round(curr * 100, 2)
            curr += step_swr
            
            payload = json.dumps({'rate': rate_pct, 'success': success_rate})
            yield f"data: {payload}\n\n"
