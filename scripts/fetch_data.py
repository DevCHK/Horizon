import os
import json
import datetime as dt
import requests
import yfinance as yf
import pandas as pd

OUTFILE = 'data/data.json'
fred_key = os.environ.get("FRED_API_KEY")

# Zeitraum
start_date = (dt.date.today() - dt.timedelta(days=3*365)).isoformat()  # 3 Jahre zurück

# Hilfsfunktion Ampel
def lamp_status(spread_val, vix, hy_bps, cape):
    s = {}
    # gleiche Logik wie bisher
    ...
    return s

# -------------------
# 1. US 10y-2y Spread
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=T10Y2Y&api_key={fred_key}&file_type=json&observation_start={start_date}"
resp = requests.get(url)
obs = resp.json()['observations']

# Aktuell + Vortag
spread_val = float(obs[-1]['value']) if obs[-1]['value'] not in ('.','') else None
spread_date = obs[-1]['date']
prev_spread_val = float(obs[-2]['value']) if obs[-2]['value'] not in ('.','') else None
prev_spread_date = obs[-2]['date']

# -------------------
# 2. VIX über yfinance
vix_data = yf.Ticker('^VIX').history(start=start_date)
vix = vix_data['Close'].iloc[-1]
prev_vix = vix_data['Close'].iloc[-2]

# -------------------
# 3. High Yield Spread (BofA US HY)
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=BAMLH0A0HYM2&api_key={fred_key}&file_type=json&observation_start={start_date}"
resp = requests.get(url)
obs = resp.json()['observations']
hy_bps = float(obs[-1]['value']) if obs[-1]['value'] not in ('.','') else None
hy_date = obs[-1]['date']
prev_hy_bps = float(obs[-2]['value']) if obs[-2]['value'] not in ('.','') else None

# -------------------
# 4. Shiller CAPE (S&P500)
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CAPESP500&api_key={fred_key}&file_type=json&observation_start={start_date}"
resp = requests.get(url)
obs = resp.json()['observations']
cape = float(obs[-1]['value']) if obs[-1]['value'] not in ('.','') else None
cape_date = obs[-1]['date']
prev_cape = float(obs[-2]['value']) if obs[-2]['value'] not in ('.','') else None

# Ampel
status = lamp_status(spread_val, vix, hy_bps, cape)

# -------------------
# JSON schreiben
out = {
    'timestamp_utc': dt.datetime.utcnow().isoformat(),
    'spread': {'value': spread_val, 'date': spread_date},
    'vix': {'value': vix, 'date': str(vix_data.index[-1].date())},
    'high_yield_bps': {'value': hy_bps, 'date': hy_date},
    'shiller_cape': {'value': cape, 'date': cape_date},
    'status': status,
    'previous': {
        'spread': {'value': prev_spread_val, 'date': prev_spread_date},
        'vix': prev_vix,
        'high_yield_bps': prev_hy_bps,
        'shiller_cape': prev_cape
    },
    'history': {  # optional: alle Werte der letzten 3 Jahre
        'spread': obs[-3*365:],
        'vix': vix_data['Close'].tail(3*365).to_dict(),
        'high_yield_bps': obs[-3*365:],
        'shiller_cape': obs[-3*365:]
    }
}

os.makedirs('data', exist_ok=True)
with open(OUTFILE, 'w', encoding='utf8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print("Daten für 3 Jahre erfolgreich geschrieben:", OUTFILE)
