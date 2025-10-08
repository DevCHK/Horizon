# scripts/fetch_data.py
import os
import json
import datetime as dt
import requests
import yfinance as yf
import pandas as pd

OUTFILE = 'data/data.json'

# -------------------
# Hilfsfunktion für Ampel
# -------------------
def lamp_status(spread_val, vix, hy_bps, cape):
    s = {}

    # VIX Ampel: <20 Grün, 20-30 Gelb, >30 Rot
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

    # HY Ampel: <350bp Grün, 350-500 Gelb, >500 Rot
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

    # CAPE Ampel: <30 Grün, 30-35 Gelb, >35 Rot
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

    # Spread Ampel: <100bp Grün, 100-200bp Gelb, >200bp Rot
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

    # Gesamte Ampel
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

# -------------------
# Daten holen
# -------------------

# FRED API Key aus Secret
fred_key = os.environ.get("FRED_API_KEY")

# 1. US 10y-2y Spread (GS10 - GS2)
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=T10Y2Y&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    data_spread = resp.json()['observations'][-1]
    spread_val = float(data_spread['value'])
    spread_date = data_spread['date']
except:
    spread_val = None
    spread_date = None

# 2. VIX
try:
    vix_data = yf.Ticker('^VIX').history(period='1d')
    vix = vix_data['Close'].iloc[-1]
    vix_date = str(vix_data.index[-1].date())
except:
    vix = None
    vix_date = None

# 3. High Yield Spread (BofA US HY Option-Adjusted Spread)
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=BAMLH0A0HYM2&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    hy_data = resp.json()['observations'][-1]
    hy_bps = float(hy_data['value'])
    hy_date = hy_data['date']
except:
    hy_bps = None
    hy_date = None

# 4. Shiller CAPE (S&P500)
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CAPESP500&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    cape_data = resp.json()['observations'][-1]
    cape = float(cape_data['value'])
    cape_date = cape_data['date']
except:
    cape = None
    cape_date = None

# Ampelstatus
status = lamp_status(spread_val, vix, hy_bps, cape)

# -------------------
# JSON speichern
# -------------------
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
