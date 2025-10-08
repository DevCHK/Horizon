import os
import json
import datetime as dt
import requests
import yfinance as yf

OUTFILE = 'data/data.json'

def lamp_status(spread_val, vix, hy_bps, cape):
    s = {}

    try:
        if vix is None:
            s['vix'] = 'unknown'
        elif vix < 20:
            s['vix'] = 'green'
        elif vix <= 30:
            s['vix'] = 'yellow'
        else:
            s['vix'] = 'red'
    except:
        s['vix'] = 'unknown'

    try:
        if hy_bps is None:
            s['hy'] = 'unknown'
        elif hy_bps < 350:
            s['hy'] = 'green'
        elif hy_bps <= 500:
            s['hy'] = 'yellow'
        else:
            s['hy'] = 'red'
    except:
        s['hy'] = 'unknown'

    try:
        if cape is None:
            s['cape'] = 'unknown'
        elif cape < 30:
            s['cape'] = 'green'
        elif cape <= 35:
            s['cape'] = 'yellow'
        else:
            s['cape'] = 'red'
    except:
        s['cape'] = 'unknown'

    try:
        if spread_val is None:
            s['spread'] = 'unknown'
        elif spread_val < 100:
            s['spread'] = 'green'
        elif spread_val <= 200:
            s['spread'] = 'yellow'
        else:
            s['spread'] = 'red'
    except:
        s['spread'] = 'unknown'

    colors = list(s.values())
    reds = colors.count('red')
    yellows = colors.count('yellow')
    if reds >= 3:
        overall = 'red'
    elif reds >= 1 and (reds + yellows) >= 2:
        overall = 'yellow'
    else:
        overall = 'green'

    s['overall'] = overall
    return s

# FRED API Key
fred_key = os.environ.get("FRED_API_KEY")

# Spread
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=T10Y2Y&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    last_obs = [o for o in resp.json()['observations'] if o['value'] != '.'][-1]
    spread_val = float(last_obs['value'])
    spread_date = last_obs['date']
except:
    spread_val = None
    spread_date = None

# VIX
try:
    vix_data = yf.Ticker('^VIX').history(period='1d')
    vix = vix_data['Close'].iloc[-1]
    vix_date = str(vix_data.index[-1].date())
except:
    vix = None
    vix_date = None

# High Yield
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=BAMLH0A0HYM2&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    last_obs = [o for o in resp.json()['observations'] if o['value'] != '.'][-1]
    hy_bps = float(last_obs['value'])
    hy_date = last_obs['date']
except:
    hy_bps = None
    hy_date = None

# CAPE
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CAPESP500&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    last_obs = [o for o in resp.json()['observations'] if o['value'] != '.'][-1]
    cape = float(last_obs['value'])
    cape_date = last_obs['date']
except:
    cape = None
    cape_date = None

# Ampelstatus
status = lamp_status(spread_val, vix, hy_bps, cape)

# JSON speichern
out = {
    'timestamp_utc': dt.datetime.utcnow().isoformat(),
    'spread': {'value': spread_val, 'date': spread_date},
    'vix': {'value': vix, 'date': vix_date},
    'high_yield_bps': {'value': hy_bps, 'date': hy_date},
    'shiller_cape': {'value': cape, 'date': cape_date},
    'status': status
}

os.makedirs('data', exist_ok=True)
with open(OUTFILE, 'w', encoding='utf8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('Daten erfolgreich geschrieben:', OUTFILE)
