
import os
import json
import datetime as dt
import requests
import yfinance as yf
from bs4 import BeautifulSoup

OUTFILE = 'data/data.json'

# -------------------
# Hilfsfunktion für Ampel
# -------------------
def lamp_status(spread_val, vix, hy_bps, cape):
    s = {}
    s['vix'] = 'green' if vix is not None and vix < 20 else 'yellow' if vix is not None and vix <= 30 else 'red' if vix is not None else 'unknown'
    s['hy'] = 'green' if hy_bps is not None and hy_bps < 350 else 'yellow' if hy_bps is not None and hy_bps <= 500 else 'red' if hy_bps is not None else 'unknown'
    s['cape'] = 'green' if cape is not None and cape < 30 else 'yellow' if cape is not None and cape <= 35 else 'red' if cape is not None else 'unknown'
    s['spread'] = 'green' if spread_val is not None and spread_val < 100 else 'yellow' if spread_val is not None and spread_val <= 200 else 'red' if spread_val is not None else 'unknown'

    # Gesamteinschätzung
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

# Spread 10y-2y
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=T10Y2Y&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    spread_data = resp.json().get('observations', [])
    if spread_data:
        last = spread_data[-1]
        spread_val = float(last['value'])
        spread_date = last['date']
    else:
        spread_val, spread_date = None, None
except:
    spread_val, spread_date = None, None

# VIX über Yahoo Finance
def fetch_yf(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1d", progress=False)
        if not df.empty:
            last = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else last
            return {
                "value": float(last["Close"]),
                "prev_value": float(prev["Close"]),
                "date": str(last.name.date())
            }
    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")
    return {"value": None, "prev_value": None, "date": None}

vix = fetch_yf('^VIX')
hy = fetch_yf('BAMLH0A0HYM2')  # Optional: ersetzen, wenn BofA HY Spread via Yahoo nicht verfügbar

# CAPE über multpl.com
# CAPE über multpl.com
def fetch_cape():
    try:
        url = "https://www.multpl.com/shiller-pe"
        response = requests.get(url)
        response.raise_for_status()  # sicherstellen, dass die Seite geladen wurde
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Das div mit id="current" auswählen
        div = soup.find('div', id='current')
        if div is None or len(div.contents) < 3:
            raise ValueError("CAPE-Wert nicht gefunden")
        
        # Den Wert extrahieren (childNodes[2] entspricht contents[2] in BeautifulSoup)
        cape_value = div.contents[2].strip()
        cape_value = float(cape_value)

        # Datum der Abfrage
        cape_date = str(dt.datetime.utcnow().date())
        
        return {
            "value": cape_value,
            "date": cape_date
        }
    except Exception as e:
        print("Fehler beim Abrufen des CAPE-Werts:", e)
        return {
            "value": None,
            "date": None
        }

if __name__ == "__main__":
    cape = fetch_cape()
    print("CAPE:", cape)

# High Yield Spread über FRED
try:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=BAMLH0A0HYM2&api_key={fred_key}&file_type=json"
    resp = requests.get(url)
    hy_data = resp.json().get('observations', [])
    if hy_data:
        last = hy_data[-1]
        hy_bps = float(last['value'])
        hy_date = last['date']
    else:
        hy_bps, hy_date = None, None
except:
    hy_bps, hy_date = None, None

# Ampel
status = lamp_status(spread_val, vix["value"], hy_bps, cape["value"])

# -------------------
# JSON speichern
# -------------------
out = {
    "timestamp_utc": dt.datetime.utcnow().isoformat(),
    "spread": {"value": spread_val, "date": spread_date},
    "vix": vix,
    "high_yield_bps": {"value": hy_bps, "date": hy_date},
    "shiller_cape": cape,
    "status": status
}

os.makedirs('data', exist_ok=True)
with open(OUTFILE, 'w', encoding='utf8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print('Daten erfolgreich geschrieben:', OUTFILE)
