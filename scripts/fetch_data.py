# scripts/fetch_data.py
import os
import requests

fred_key = os.environ.get("FRED_API_KEY")

url = f"https://api.stlouisfed.org/fred/series/observations?series_id=SP500&api_key={fred_key}&file_type=json"
resp = requests.get(url)
data = resp.json()

print(data)  # optional: zeigt die Rohdaten, zum Testen



# VIX: <20 Grün, 20-30 Gelb, >30 Rot
try:
if vix_v is None:
s['vix'] = 'unknown'
elif vix_v < 20:
s['vix'] = 'green'
elif vix_v <= 30:
s['vix'] = 'yellow'
else:
s['vix'] = 'red'
except:
s['vix'] = 'unknown'


# HY: <350bp Grün, 350-500 Gelb, >500 Rot
try:
if hy_bps_v is None:
s['hy'] = 'unknown'
elif hy_bps_v < 350:
s['hy'] = 'green'
elif hy_bps_v <= 500:
s['hy'] = 'yellow'
else:
s['hy'] = 'red'
except:
s['hy'] = 'unknown'


# CAPE: <30 Grün, 30-35 Gelb, >35 Rot
try:
if cape_v is None:
s['cape'] = 'unknown'
elif cape_v < 30:
s['cape'] = 'green'
elif cape_v <= 35:
s['cape'] = 'yellow'
else:
s['cape'] = 'red'
except:
s['cape'] = 'unknown'


# Gesamteinschätzung: count rote/gelbe
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


status = lamp_status(spread_val, vix, hy_bps, cape)


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


print('Werte geschrieben:', OUTFILE)
