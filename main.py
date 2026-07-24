import platform
from flask import Flask, render_template, request, Response
from config import Config
from monte_carlo import MonteCarloSimulator

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream-simulation', methods=['POST'])
def stream_simulation():
    data = request.json
    us_alloc = float(data.get('us_alloc', 60)) / 100.0
    intl_alloc = float(data.get('intl_alloc', 20)) / 100.0
    bond_alloc = float(data.get('bond_alloc', 20)) / 100.0
    n_sims = int(data.get('n_sims', 1000))
    n_years = int(data.get('n_years', 65))
    block_size = int(data.get('block_size', 5))
    drift_pct = float(data.get('drift_pct', 5)) / 100.0
    drawdown_pct = float(data.get('drawdown_pct', 20)) / 100.0
    initial_swr = float(data.get('initial_swr', 1)) / 100.0
    step_swr = float(data.get('step_swr', 0.05)) / 100.0
    success_threshold = float(data.get('success_threshold', 90))

    return Response(
        MonteCarloSimulator.stream_simulation(
            us_alloc, intl_alloc, bond_alloc, n_sims, n_years, block_size, drift_pct, drawdown_pct, initial_swr, step_swr, success_threshold
        ), 
        mimetype='text/event-stream'
    )

if __name__ == '__main__':
    if platform.system() == 'Android':
        try:
            from android.permissions import Permission, request_permissions
            request_permissions([Permission.INTERNET, Permission.WAKE_LOCK, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        except ImportError:
            pass
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'], threaded=True)
