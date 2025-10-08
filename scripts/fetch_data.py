import os
import json
import datetime as dt
import requests
import yfinance as yf
from bs4 import BeautifulSoup

OUTFILE = 'data/data.json'
PREV_FILE = 'data/prev_values.json'

# -------------------
# Hilfsfunktion für Ampel
# -------------------
def lamp_status(spread_val, vix, hy_bps, cape):
    s = {}
    s['vix'] = 'green' if vix is not None and vix < 20 else 'yellow' if vix is not None and vix <= 30 else 'red' if vix is not None else 'unknown'
    s['hy'] = 'green' if hy_bps is not None and hy_bps < 3.5 else 'yellow' if hy_bps is not None and hy_bps <= 5 else 'red' if hy_bps is not None else 'unknown'
    s['cape'] = 'green' if cape is not None and cape < 30 else 'yellow' if cape is not None and cape <= 35 else 'red' if cape is not None else 'unknown'
    s['spread'] = 'green' if spread_val is not None and spread_val > 100 else 'yellow' if spread_val is not None and spread_val >= 0 else 'red' if spread_val is not None else 'unknown'

    colors = list(s.values())
    reds = colors.count('red')
    yellows = colors.count('yellow')
    if reds >= 2:
        overall = 'red'
    elif reds == 1 or yellows >= 1:
        overall = 'yellow'
    else:
        overall = 'green'
    s['overall'] = overall
    return s

# -------------------
# Vorherige Werte laden
# -------------------
if os.path.exists(PREV_FILE):
    with open(PREV_FILE, 'r', encoding='utf8') as f:
        prev_values = json.load(f)
else:
    prev_values = {}

fred_key = os.environ.get("FRED_API_KEY")

# -------------------
# Spread 10y-2y
# -------------------
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=T10Y2Y&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    obs = resp.json().get('observations', [])
    if obs and len(obs) >= 2:
        last = obs[-1]
        prev = obs[-2]
        spread_val = float(last['value'])
        spread_prev = float(prev['value'])
        spread_date = last['date']
    else:
        spread_val = spread_prev = None
        spread_date = None
except:
    spread_val = spread_prev = None
    spread_date = None

# -------------------
# VIX über Yahoo Finance
# -------------------
def fetch_yf(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1d", progress=False)
        if not df.empty:
            last = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else last
            return {"value": float(last["Close"]), "prev_value": float(prev["Close"]), "date": str(last.name.date())}
    except:
        pass
    return {"value": None, "prev_value": None, "date": None}

vix = fetch_yf('^VIX')

# -------------------
# High Yield Spread
# -------------------
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=BAMLH0A0HYM2&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    obs = resp.json().get('observations', [])
    if obs and len(obs) >= 2:
        last = obs[-1]
        prev = obs[-2]
        hy_bps = float(last['value'])
        hy_prev = float(prev['value'])
        hy_date = last['date']
    else:
        hy_bps = hy_prev = None
        hy_date = None
except:
    hy_bps = hy_prev = None
    hy_date = None

# -------------------
# CAPE
# -------------------
def fetch_cape(prev_value=None):
    try:
        url = "https://www.multpl.com/shiller-pe"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        div = soup.find('div', id='current')
        cape_val = float(div.contents[2].strip())
        return {"value": cape_val, "prev_value": prev_value, "date": str(dt.datetime.utcnow().date())}
    except:
        return {"value": None, "prev_value": prev_value, "date": None}

cape_prev = prev_values.get("cape")
cape = fetch_cape(cape_prev)

# -------------------
# Ampel
# -------------------
status = lamp_status(spread_val, vix["value"], hy_bps, cape["value"])

# -------------------
# JSON speichern
# -------------------
out = {
    "timestamp_utc": dt.datetime.utcnow().isoformat(),
    "spread": {"value": spread_val, "prev_value": spread_prev, "date": spread_date},
    "vix": vix,
    "high_yield_bps": {"value": hy_bps, "prev_value": hy_prev, "date": hy_date},
    "shiller_cape": cape,
    "status": status
}

os.makedirs('data', exist_ok=True)
with open(OUTFILE, 'w', encoding='utf8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

# -------------------
# aktuelle Werte als prev_values speichern
# -------------------
prev_values = {
    "spread": spread_val,
    "vix": vix["value"],
    "hy": hy_bps,
    "cape": cape["value"]
}
with open(PREV_FILE, 'w', encoding='utf8') as f:
    json.dump(prev_values, f, indent=2, ensure_ascii=False)

print("Daten erfolgreich geschrieben:", OUTFILE)
