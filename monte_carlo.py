import json
import os
from concurrent.futures import ProcessPoolExecutor
from data.historical_loader import HistoricalLoader
from data.bootstrap import BlockBootstrap
from simulation_engine import SimulationEngine

def _run_single_simulation_worker(args):
    hist_data, us_alloc, intl_alloc, bond_alloc, curr, n_months, drift_pct, drawdown_pct = args
    returns_seq = BlockBootstrap.get_bootstrap_sequence(hist_data, n_months)
    return SimulationEngine.run_single_simulation(
        returns_seq, us_alloc, intl_alloc, bond_alloc, curr, n_months, drift_pct, drawdown_pct
    )

class MonteCarloSimulator:
    @staticmethod
    def stream_simulation(us_alloc, intl_alloc, bond_alloc, n_sims, n_years, drift_pct, drawdown_pct, initial_swr, step_swr, success_threshold):
        hist_data = HistoricalLoader.load_dataset()
        n_months = n_years * 12
        curr = initial_swr
        success_rate = 100.0
        
        # Automatically detect optimal core count (leave 1 core free to keep UI/OS responsive)
        max_workers = max(1, os.cpu_count() - 1)

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            while success_rate >= success_threshold:
                # Pack arguments for each simulation run
                task_args = [
                    (hist_data, us_alloc, intl_alloc, bond_alloc, curr, n_months, drift_pct, drawdown_pct)
                    for _ in range(n_sims)
                ]
                
                # Execute simulations in parallel across all cores
                results = list(executor.map(_run_single_simulation_worker, task_args))
                
                success_count = sum(1 for survived in results if survived)
                success_rate = (success_count / n_sims) * 100.0
                rate_pct = round(curr * 100, 2)
                curr += step_swr
                
                payload = json.dumps({'rate': rate_pct, 'success': success_rate})
                yield f"data: {payload}\n\n"
