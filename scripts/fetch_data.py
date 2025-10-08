import requests
import yfinance as yf
import pandas as pd
import json
from datetime import datetime

API_KEY = "DEIN_FRED_API_KEY"

def fetch_fred(series_id):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEY}&file_type=json"
    resp = requests.get(url)
    data = resp.json()
    obs = data.get("observations", [])
    if len(obs) < 2:
        return None
    last = obs[-1]
    prev = obs[-2]
    return {
        "value": float(last["value"]),
        "date": last["date"],
        "prev_value": float(prev["value"]),
        "prev_date": prev["date"]
    }

def fetch_yahoo(ticker):
    df = yf.download(ticker, period="10d", interval="1d")
    if len(df) < 2:
        return None
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return {
        "value": float(last["Close"]),
        "date": str(last.name.date()),
        "prev_value": float(prev["Close"]),
        "prev_date": str(prev.name.date())
    }

def fetch_cape():
    url = "https://www.econ.yale.edu/~shiller/data/ie_data.xls"
    df = pd.read_excel(url, sheet_name="Data", skiprows=7)
    df.columns = ["Date", "P", "D", "E", "CPI", "DateFraction", "Price", "Dividend", 
                  "Earnings", "CPI_adj", "RealPrice", "RealDividend", "RealEarnings", 
                  "CAPE", "TR_S&P", "Real_TR_S&P"]
    df = df.dropna(subset=["CAPE"])
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return {
        "value": float(last["CAPE"]),
        "date": str(last["Date"]),
        "prev_value": float(prev["CAPE"]),
        "prev_date": str(prev["Date"])
    }

def main():
    data = {
        "spread": fetch_fred("T10Y2Y"),          # 10y-2y Spread
        "high_yield_bps": fetch_fred("BAMLH0A0HYM2"),  # HY Spread
        "vix": fetch_yahoo("^VIX"),
        "shiller_cape": fetch_cape(),
        "timestamp_utc": datetime.utcnow().isoformat()
    }

    with open("data/data.json", "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()
