# scripts/fetch_data.py
import os
import requests
import json
import datetime as dt

OUTFILE = 'data/data.json'

# Hilfsfunktion für Ampeln
def lamp_status(spread_val, vix_val, hy_bps_val, cape_val):
    s = {}
    try:
        if vix_val is None:
            s['vix'] = 'unknown'
        elif vix_val < 20:
            s['vix'] = 'green'
        elif vix_val <= 30:
            s['vix'] = 'yellow'
        else:
            s['vix'] = 'red'
    except:
        s['vix'] = 'unknown'

    try:
        if hy_bps_val is None:
            s['hy'] = 'unknown'
        elif hy_bps_val < 350:
            s['hy'] = 'green'
        elif hy_bps_val <= 500:
            s['hy'] = 'yellow'
        else:
            s['hy'] = 'red'
    except:
        s['hy'] = 'unknown'

    try:
        if cape_val is None:
            s['cape'] = 'unknown'
        elif cape_val < 30:
            s['cape'] = 'green'
        elif cape_val <= 35:
            s['cape'] = 'yellow'
        else:
            s['cape'] = 'red'
    except:
        s['cape'] = 'unknown'

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

# API Key aus GitHub Secret
fred_key = os.environ.get("FRED_API_KEY")
if not fred_key:
    raise ValueError("FRED_API_KEY nicht gesetzt")

# Beispiel: Daten abrufen (hier nur SP500 als Platzhalter)
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=SP500&api_key={fred_key}&file_type=json"
resp = requests.get(url)
if resp.status_code != 200:
    raise ValueError(f"FRED API Fehler: {resp.status_code}")
data_json = resp.json()

# Platzhalterwerte für andere Faktoren (hier könntest du echte API-Requests einfügen)
spread_val, spread_date = 100, dt.datetime.utcnow().isoformat()
vix, vix_date = 22, dt.datetime.utcnow().isoformat()
hy_bps, hy_date = 400, dt.datetime.utcnow().isoformat()
cape, cape_date = 32, dt.datetime.utcnow().isoformat()

# Ampeln berechnen
status = lamp_status(spread_val, vix, hy_bps, cape)

# Ausgabe-JSON
out = {
    'timestamp_utc': dt.datetime.utcnow().isoformat(),
    'spread': {'value': spread_val, 'date': spread_date},
    'vix': {'value': vix, 'date': vix_date},
    'high_yield_bps': {'value': hy_bps, 'date': hy_date},
    'shiller_cape': {'value': cape, 'date': cape_date},
    'status': status
}

# Datei schreiben
os.makedirs('data', exist_ok=True)
with open(OUTFILE, 'w', encoding='utf8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('Werte geschrieben:', OUTFILE)
