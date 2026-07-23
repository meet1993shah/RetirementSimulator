let simChart = null;

document.getElementById('sim-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const statusText = document.getElementById('status-text');
    statusText.textContent = "Running live simulation... streaming data points.";
    
    const payload = {
        us_alloc: document.getElementById('us_alloc').value,
        intl_alloc: document.getElementById('intl_alloc').value,
        bond_alloc: document.getElementById('bond_alloc').value,
        n_sims: document.getElementById('n_sims').value,
        n_years: document.getElementById('n_years').value,
        block_size: document.getElementById('block_size').value,
        drift_pct: document.getElementById('drift_pct').value,
        drawdown_pct: document.getElementById('drawdown_pct').value,
        initial_swr: document.getElementById('initial_swr').value,
        step_swr: document.getElementById('step_swr').value,
        success_threshold: document.getElementById('success_threshold').value
    };
    
    // Destroy existing chart if present
    if (simChart) {
        simChart.destroy();
    }
    
    // Initialize Chart.js configuration
    const ctx = document.getElementById('simChart').getContext('2d');
    simChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Success Rate (%)',
                data: [],
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                pointRadius: 3,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Initial Withdrawal Rate (%)' }
                },
                y: {
                    min: success_threshold-5,
                    max: 100,
                    ticks: {
                        stepSize: 1
                    },
                    title: { display: true, text: 'Success Rate (%)' }
                }
            }
        }
    });
    
    // Trigger Server-Sent Events via fetch POST (using response body reader)
    fetch('/stream-simulation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        function readStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    statusText.textContent = "Simulation completed successfully!";
                    return;
                }
                
                buffer += decoder.decode(value, { stream: true });
                let lines = buffer.split('\n\n');
                buffer = lines.pop(); // Keep incomplete chunk
                
                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const jsonStr = line.replace('data: ', '');
                        const data = JSON.parse(jsonStr);
                        
                        // Append live data point to Chart.js
                        simChart.data.labels.push(data.rate.toFixed(2) + '%');
                        simChart.data.datasets[0].data.push(data.success);
                        simChart.update('none'); // Update smoothly without full re-animation
                    }
                });
                
                readStream();
            }).catch(err => {
                console.error("Stream reading error:", err);
                statusText.textContent = "Error occurred during streaming.";
            });
        }
        
        readStream();
    });
});
