
# Ampel-Dashboard


Dieses Repo erzeugt täglich ein kleines Ampel-Dashboard, das vier Indikatoren prüft: 10y-2y Spread, VIX, High Yield OAS, Shiller CAPE.


## Einrichtung
1. Setze im GitHub-Repo ein Secret `FRED_API_KEY` (free API-Key von FRED).
2. Aktiviere GitHub Pages (Branch: main, Ordner: /)
3. Push alle Dateien in das Repo.
4. Workflow ausführen oder warten, bis der Zeitplan greift.


## Hinweise
- CAPE wird primär über multpl geparst. Falls multpl nicht erreichbar ist, nutze `data/shiller_cape.csv`.
- Passe Schwellenwerte in `scripts/fetch_data.py` an, falls du andere Regeln willst.
