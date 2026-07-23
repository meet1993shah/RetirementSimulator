import json
import time
import math
import random
from flask import Flask, render_template, request, Response
import platform
import os

app = Flask(__name__)
# Secret key is essential for Flask sessions to work
app.secret_key = os.urandom(24)

# Full 1928-2025 Historical Baseline (S&P 500, Bonds, CPI)
SP500_HIST = [
    0.4381, -0.0842, -0.249, -0.4334, -0.0819, 0.5399, -0.0144, 0.4767, 0.3392, -0.3503, 
    0.3112, -0.0041, -0.0978, -0.1159, 0.2034, 0.259, 0.1975, 0.3644, -0.0807, 0.0571, 
    0.055, 0.1879, 0.3171, 0.2402, 0.1837, -0.0099, 0.5262, 0.3156, 0.0656, -0.1078, 
    0.4336, 0.1196, 0.0047, 0.2681, -0.0873, 0.228, 0.1648, 0.1245, -0.1006, 0.2398, 
    0.1106, -0.085, 0.0401, 0.1431, 0.1898, -0.1466, -0.2647, 0.372, 0.2384, -0.0718, 
    0.0656, 0.1844, 0.325, -0.0492, 0.2155, 0.2256, 0.0627, 0.3173, 0.1867, 0.0525, 
    0.1661, 0.3169, -0.031, 0.3047, 0.0762, 0.1008, 0.0132, 0.3758, 0.2296, 0.3336, 
    0.2858, 0.2104, -0.091, -0.1189, -0.221, 0.2868, 0.1088, 0.0491, 0.1579, 0.0549, 
    -0.37, 0.2646, 0.1506, 0.0211, 0.16, 0.3239, 0.1369, 0.0138, 0.1196, 0.2183, 
    -0.0438, 0.3149, 0.184, 0.2871, -0.1811, 0.2629, 0.2502, 0.1788
]

BONDS_HIST = [
    0.0084, 0.042, 0.0454, -0.0256, 0.0879, 0.0186, 0.0796, 0.0447, 0.0502, 0.0138, 
    0.0421, 0.0043, 0.0609, 0.0202, 0.0322, 0.0281, 0.0258, 0.038, 0.0313, 0.0092, 
    0.0195, 0.0466, 0.0043, -0.003, 0.0227, 0.0364, 0.0329, -0.0134, -0.0226, 0.068, 
    -0.021, -0.0265, 0.1164, 0.0206, 0.0569, 0.0168, 0.0373, 0.0072, 0.0291, -0.0158, 
    0.0327, -0.0501, 0.1675, 0.0979, 0.0282, 0.0366, 0.0199, 0.0361, 0.1686, 0.0171, 
    -0.0118, 0.0067, 0.0395, 0.082, 0.3281, 0.032, 0.1373, 0.309, 0.2453, -0.0267, 
    0.0967, 0.1769, 0.0624, 0.15, 0.0936, 0.1824, -0.0804, 0.2358, 0.0143, 0.0994, 
    0.1492, -0.0825, 0.1666, 0.0557, 0.1512, 0.0038, 0.0449, 0.0287, 0.0196, 0.1021, 
    0.201, -0.1112, 0.0846, 0.1604, 0.0297, -0.091, 0.1075, 0.0128, 0.0069, 0.028, 
    -0.0002, 0.0964, 0.1133, -0.0442, -0.1783, 0.039, 0.04, 0.02
]

CPI_HIST = [
    -0.0115, 0.0058, -0.064, -0.0932, -0.1027, 0.0076, 0.0151, 0.0298, 0.0145, 0.0285, 
    -0.0277, 0.0, 0.0071, 0.0988, 0.0903, 0.0296, 0.0172, 0.0226, 0.1813, 0.0898, 
    0.0299, -0.018, 0.0579, 0.0587, 0.0088, 0.0075, -0.0074, 0.0037, 0.0291, 0.0302, 
    0.0175, 0.0172, 0.0145, 0.0072, 0.013, 0.0163, 0.0104, 0.0192, 0.0346, 0.0304, 
    0.0472, 0.0611, 0.0549, 0.0336, 0.0341, 0.0871, 0.1234, 0.0694, 0.0486, 0.067, 
    0.0902, 0.1329, 0.1252, 0.0892, 0.0383, 0.0379, 0.0395, 0.038, 0.011, 0.0443, 
    0.0442, 0.0465, 0.0611, 0.0306, 0.029, 0.0275, 0.0267, 0.0254, 0.0332, 0.017, 
    0.0161, 0.0268, 0.0339, 0.0155, 0.0238, 0.0188, 0.0326, 0.0342, 0.0254, 0.0408, 
    0.0009, 0.0272, 0.015, 0.0296, 0.0174, 0.015, 0.0076, 0.0073, 0.0207, 0.0211, 
    0.0191, 0.0229, 0.0136, 0.0704, 0.0645, 0.034, 0.03, 0.027
]

random.seed(random.randint(1, 100))
INTL_HIST = [r * 0.8 + random.gauss(0, 0.05) for r in SP500_HIST]

# Combine into a list of tuples: (sp, intl, bonds, cpi)
HIST_DATA = list(zip(SP500_HIST, INTL_HIST, BONDS_HIST, CPI_HIST))

def get_block_bootstrap_returns(data, n_years, block_size):
    n_blocks = math.ceil(n_years / block_size)
    max_start_idx = len(data) - block_size
    returns_sequence = []
    for _ in range(n_blocks):
        start_idx = random.randint(0, max_start_idx)
        returns_sequence.extend(data[start_idx : start_idx + block_size])
    return returns_sequence[:n_years]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream-simulation', methods=['POST'])
def stream_simulation():
    data = request.json
    us_alloc = float(data.get('us_alloc', 60)) / 100.0
    intl_alloc = float(data.get('intl_alloc', 20)) / 100.0
    bond_alloc = float(data.get('bond_alloc', 20)) / 100.0
    n_sims = int(data.get('n_sims', 500))
    n_years = int(data.get('n_years', 65))
    block_size = int(data.get('block_size', 5))
    drift_pct = float(data.get('drift_pct', 5)) / 100.0
    drawdown_pct = float(data.get('drawdown_pct', 20)) / 100.0
    intial_swr = float(data.get('initial_swr', 1)) / 100.0
    step_swr = float(data.get('step_swr', 0.05)) / 100.0
    success_threshold = float(data.get('success_threshold', 90))

    div_yield_us, div_yield_intl, yield_bonds = 0.015, 0.03, 0.04

    def generate():
        success_rate = 100
        initial_spending_rate = intial_swr
        while success_rate > success_threshold:
            success_count = 0
            for _ in range(n_sims):
                returns = get_block_bootstrap_returns(HIST_DATA, n_years, block_size)
                portfolio = 1000000.0
                spending = portfolio * initial_spending_rate
                cash = spending
                invested = portfolio - cash
                
                us_stocks = invested * us_alloc
                intl_stocks = invested * intl_alloc
                bonds = invested * bond_alloc
                
                us_peak = us_stocks
                intl_peak = intl_stocks
                survived = True
                
                for y in range(n_years):
                    ret_us, ret_intl, ret_bonds, infl = returns[y]
                    us_stocks *= (1 + (ret_us - div_yield_us))
                    intl_stocks *= (1 + (ret_intl - div_yield_intl))
                    bonds *= (1 + (ret_bonds - yield_bonds))
                    
                    if us_stocks > us_peak: us_peak = us_stocks
                    if intl_stocks > intl_peak: intl_peak = intl_stocks
                    
                    cash += us_stocks * div_yield_us + intl_stocks * div_yield_intl + bonds * yield_bonds
                    spending *= (1 + infl)
                    current_invested = us_stocks + intl_stocks + bonds
                    
                    us_drawdown = (us_peak - us_stocks) / us_peak if us_peak > 0 else 0
                    intl_drawdown = (intl_peak - intl_stocks) / intl_peak if intl_peak > 0 else 0
                    
                    us_weight = us_stocks / current_invested if current_invested > 0 else us_alloc
                    us_drift = us_weight - us_alloc
                    
                    us_bear = us_drawdown >= drawdown_pct
                    intl_bear = (intl_drawdown >= drawdown_pct) and (us_drift <= drift_pct)
                    bear_market = us_bear or intl_bear
                    
                    if cash >= spending:
                        cash -= spending
                    else:
                        shortfall = spending - cash
                        cash = 0
                        if current_invested <= shortfall:
                            survived = False
                            break
                        us_stocks -= shortfall * (us_stocks / current_invested)
                        intl_stocks -= shortfall * (intl_stocks / current_invested)
                        bonds -= shortfall * (bonds / current_invested)
                        current_invested -= shortfall
                        
                    target_cash = spending * 0.5 if bear_market else spending
                    if cash < target_cash and current_invested > 0:
                        needed_cash = min(target_cash - cash, current_invested)
                        us_stocks -= needed_cash * (us_stocks / current_invested)
                        intl_stocks -= needed_cash * (intl_stocks / current_invested)
                        bonds -= needed_cash * (bonds / current_invested)
                        cash += needed_cash
                        
                    if current_invested <= 0 and cash < spending:
                        survived = False
                        break
                        
                if survived:
                    success_count += 1
            
            success_rate = (success_count / n_sims) * 100.0
            rate_pct = round(initial_spending_rate * 100, 2)
            initial_spending_rate += step_swr
            
            # Send data chunk via SSE
            payload = json.dumps({'rate': rate_pct, 'success': success_rate})
            yield f"data: {payload}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    if platform.system() == 'Android':
        try:
            from android.permissions import Permission, request_permissions
            request_permissions([Permission.WAKE_LOCK, Permission.INTERNET, Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        except ImportError:
            pass
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
