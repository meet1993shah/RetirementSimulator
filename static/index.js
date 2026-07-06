class SimulationDashboard {
    constructor() {
        this.form = document.getElementById('simulationParametersForm');
        this.submitBtn = document.getElementById('simulateBtn');
        this.statusText = document.getElementById('systemStatus');
        
        // Progress elements
        this.progressWrapper = document.getElementById('progressWrapper');
        this.progressBarFill = document.getElementById('progressBarFill');
        this.progressBarPct = document.getElementById('progressBarPct');
        
        // Scorecard elements
        this.domSuccessRate = document.getElementById('valSuccessRate');
        this.domSuccessfulRuns = document.getElementById('valSuccessfulRuns');
        this.domInsolventRuns = document.getElementById('valInsolventRuns');
        this.domAvgInsolvencyYear = document.getElementById('valAvgInsolvencyYear');
        
        this.registerEventHandlers();
    }

    registerEventHandlers() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.executeBatchSimulation();
        });
    }

    async executeBatchSimulation() {
        this.setEngineState(true, 'Engine Status: Initializing SSE Stream...');
        this.updateProgressBar(0);
        this.progressWrapper.classList.remove('idled');

        const formData = new FormData(this.form);
        const payload = {
            net_worth: parseFloat(formData.get('net_worth')),
            expenses: parseFloat(formData.get('expenses')),
            us_stock_rate: parseFloat(formData.get('us_stock_rate')),
            us_stock_sigma: parseFloat(formData.get('us_stock_sigma')),
            intl_stock_rate: parseFloat(formData.get('intl_stock_rate')),
            intl_stock_sigma: parseFloat(formData.get('intl_stock_sigma')),
            bond_rate: parseFloat(formData.get('bond_rate')),
            inflation_rate: parseFloat(formData.get('inflation_rate')),
            horizon: parseInt(formData.get('horizon'), 10),
            num_simulations: parseInt(formData.get('num_simulations'), 10)
        };

        try {
            const response = await fetch('/api/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Simulation stream configuration rejected.');

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop(); // Save trailing unfinished line back to the buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const rawJson = line.substring(6).trim();
                        if (!rawJson) continue;
                        
                        const msg = JSON.parse(rawJson);
                        if (msg.type === 'progress') {
                            this.updateProgressBar(msg.percentage);
                            this.statusText.innerText = `Engine Status: Running Cycles (${msg.percentage}%)`;
                        } else if (msg.type === 'final') {
                            this.renderFinalMetrics(msg);
                        }
                    }
                }
            }
            
            this.setEngineState(false, 'Engine Status: Idle');
        } catch (err) {
            console.error(err);
            this.setEngineState(false, 'Engine Status: Stream Fault Error');
        }
    }

    updateProgressBar(pct) {
        this.progressBarFill.style.width = `${pct}%`;
        this.progressBarPct.innerText = `${pct}%`;
    }

    renderFinalMetrics(data) {
        this.domSuccessRate.innerText = `${data.success_rate_pct}%`;
        this.domSuccessfulRuns.innerText = data.successful_runs.toLocaleString();
        this.domInsolventRuns.innerText = data.insolvent_runs.toLocaleString();
        
        if (data.insolvent_runs > 0) {
            this.domAvgInsolvencyYear.innerText = `Year ${data.avg_insolvency_year}`;
        } else {
            this.domAvgInsolvencyYear.innerText = 'No Ruin';
        }
    }

    setEngineState(isLoading, text) {
        this.statusText.innerText = text;
        if (isLoading) {
            this.submitBtn.disabled = true;
            this.submitBtn.style.opacity = '0.6';
            this.submitBtn.innerText = 'Streaming MC Nodes...';
        } else {
            this.submitBtn.disabled = false;
            this.submitBtn.style.opacity = '1.0';
            this.submitBtn.innerText = 'Run Monte Carlo Simulation';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.AppEngineInstance = new SimulationDashboard();
});
