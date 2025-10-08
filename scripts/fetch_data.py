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
    # VIX Ampel
    if vix is None:
        s['vix'] = 'unknown'
    elif vix < 20:
        s['vix'] = 'green'
    elif vix <= 30:
        s['vix'] = 'yellow'
    else:
        s['vix'] = 'red'

    # HY Ampel
    if hy_bps is None:
        s['hy'] = 'unknown'
    elif hy_bps < 350:
        s['hy'] = 'green'
    elif hy_bps <= 500:
        s['hy'] = 'yellow'
    else:
        s['hy'] = 'red'

    # CAPE Ampel
    if cape is None:
        s['cape'] = 'unknown'
    elif cape < 30:
        s['cape'] = 'green'
    elif cape <= 35:
        s['cape'] = 'yellow'
    else:
        s['cape'] = 'red'

    # Spread Ampel
    if spread_val is None:
        s['spread'] = 'unknown'
    elif spread_val < 100:
        s['spread'] = 'green'
    elif spread_val <= 200:
        s['spread'] = 'yellow'
    else:
        s['spread'] = 'red'

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
fred_key = os.environ.get("FRED_API_KEY")

# Zeitraum für die letzten 3 Jahre
end_date = dt.datetime.today()
start_date = end_date - dt.timedelta(days=3*365)
start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# 1. US 10y-2y Spread (GS10 - GS2)
try:
    url_10y = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={fred_key}&file_type=json&observation_start={start_str}&observation_end={end_str}"
    url_2y = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS2&api_key={fred_key}&file_type=json&observation_start={start_str}&observation_end={end_str}"

    data_10y = requests.get(url_10y).json()['observations']
    data_2y = requests.get(url_2y).json()['observations']

    df_10y = pd.DataFrame(data_10y)
    df_10y['value'] = pd.to_numeric(df_10y['value'], errors='coerce')
    df_10y['date'] = pd.to_datetime(df_10y['date'])

    df_2y = pd.DataFrame(data_2y)
    df_2y['value'] = pd.to_numeric(df_2y['value'], errors='coerce')
    df_2y['date'] = pd.to_datetime(df_2y['date'])

    df_spread = pd.merge(df_10y, df_2y, on='date', suffixes=('_10y', '_2y'))
    df_spread['spread'] = df_spread['value_10y'] - df_spread['value_2y']

    # Aktueller Spread
    latest_spread = df_spread['spread'].iloc[-1]
    latest_date = df_spread['date'].iloc[-1].strftime('%Y-%m-%d')

    # Historische Werte für Chart.js
    spread_history = df_spread[['date','spread']].dropna().to_dict(orient='records')

except:
    latest_spread = None
    latest_date = None
    spread_history = []

# 2. VIX
try:
    vix_data = yf.Ticker('^VIX').history(period='1d')
    vix = vix_data['Close'].iloc[-1]
    vix_date = str(vix_data.index[-1].date())
except:
    vix = None
    vix_date = None

# 3. High Yield Spread
try:
    url_hy = f"https://api.stlouisfed.org/fred/series/observations?series_id=BAMLH0A0HYM2&api_key={fred_key}&file_type=json"
    hy_data = requests.get(url_hy).json()['observations'][-1]
    hy_bps = float(hy_data['value'])
    hy_date = hy_data['date']
except:
    hy_bps = None
    hy_date = None

# 4. Shiller CAPE
try:
    url_cape = f"https://api.stlouisfed.org/fred/series/observations?series_id=CAPESP500&api_key={fred_key}&file_type=json"
    cape_data = requests.get(url_cape).json()['observations'][-1]
    cape = float(cape_data['value'])
    cape_date = cape_data['date']
except:
    cape = None
    cape_date = None

# Ampelstatus
status = lamp_status(latest_spread, vix, hy_bps, cape)

# -------------------
# JSON speichern
# -------------------
out = {
    'timestamp_utc': dt.datetime.utcnow().isoformat(),
    'spread': {'value': latest_spread, 'date': latest_date, 'history': spread_history},
    'vix': {'value': vix, 'date': vix_date},
    'high_yield_bps': {'value': hy_bps, 'date': hy_date},
    'shiller_cape': {'value': cape, 'date': cape_date},
    'status': status
}

os.makedirs('data', exist_ok=True)
with open(OUTFILE, 'w', encoding='utf8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('Daten erfolgreich geschrieben:', OUTFILE)
