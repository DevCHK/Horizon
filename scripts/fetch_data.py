# scripts/fetch_data_full.py
import os
import json
import datetime as dt
import requests
import yfinance as yf
import pandas as pd

OUTFILE = 'data/data.json'
fred_key = os.environ.get("FRED_API_KEY")
END_DATE = dt.date.today()
START_DATE = END_DATE - dt.timedelta(days=3*365)  # 3 Jahre

# -------------------
# Hilfsfunktion Ampel
# -------------------
def lamp_status(spread_val, vix, hy_bps, cape):
    s = {}
    # VIX
    if vix is None: s['vix']='unknown'
    elif vix<20: s['vix']='green'
    elif vix<=30: s['vix']='yellow'
    else: s['vix']='red'
    # HY
    if hy_bps is None: s['hy']='unknown'
    elif hy_bps<350: s['hy']='green'
    elif hy_bps<=500: s['hy']='yellow'
    else: s['hy']='red'
    # CAPE
    if cape is None: s['cape']='unknown'
    elif cape<30: s['cape']='green'
    elif cape<=35: s['cape']='yellow'
    else: s['cape']='red'
    # Spread
    if spread_val is None: s['spread']='unknown'
    elif spread_val<100: s['spread']='green'
    elif spread_val<=200: s['spread']='yellow'
    else: s['spread']='red'
    # Overall
    colors = list(s.values())
    reds = colors.count('red')
    yellows = colors.count('yellow')
    overall = 'green'
    if reds>=3: overall='red'
    elif reds>=1 and (reds+yellows)>=2: overall='yellow'
    s['overall']=overall
    return s

# -------------------
# FRED-Historie abrufen
# -------------------
def fetch_fred_history(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": fred_key,
        "file_type": "json",
        "observation_start": START_DATE.isoformat(),
        "observation_end": END_DATE.isoformat()
    }
    resp = requests.get(url, params=params)
    obs = resp.json().get('observations', [])
    history = []
    for o in obs:
        try:
            value = float(o['value'])
            history.append({'date': o['date'], 'value': value})
        except:
            continue
    last = history[-1] if history else {'date': None, 'value': None}
    return last['value'], last['date'], history

# -------------------
# Spread (10y-2y)
# -------------------
spread_val, spread_date, spread_hist = fetch_fred_history('T10Y2Y')

# -------------------
# High Yield Spread
# -------------------
hy_val, hy_date, hy_hist = fetch_fred_history('BAMLH0A0HYM2')

# -------------------
# Shiller CAPE
# -------------------
cape_val, cape_date, cape_hist = fetch_fred_history('CAPESP500')

# -------------------
# VIX (Yahoo Finance)
# -------------------
vix_data = yf.Ticker('^VIX').history(start=START_DATE, end=END_DATE)
vix_data = vix_data['Close'].dropna()
vix_hist = [{'date': str(d.date()), 'value': float(v)} for d,v in zip(vix_data.index, vix_data.values)]
vix_val = vix_hist[-1]['value'] if vix_hist else None
vix_date = vix_hist[-1]['date'] if vix_hist else None

# -------------------
# Ampelstatus
# -------------------
status = lamp_status(spread_val, vix_val, hy_val, cape_val)

# -------------------
# JSON speichern
# -------------------
out = {
    'timestamp_utc': dt.datetime.utcnow().isoformat(),
    'spread': {'value': spread_val, 'date': spread_date, 'history': spread_hist},
    'vix': {'value': vix_val, 'date': vix_date, 'history': vix_hist},
    'high_yield_bps': {'value': hy_val, 'date': hy_date, 'history': hy_hist},
    'shiller_cape': {'value': cape_val, 'date': cape_date, 'history': cape_hist},
    'status': status
}

os.makedirs('data', exist_ok=True)
with open(OUTFILE, 'w', encoding='utf8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('Daten erfolgreich geschrieben:', OUTFILE)
