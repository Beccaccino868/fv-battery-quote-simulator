"""
Genera la tabella di resa specifica FV (kWh/kWp/anno) da PVGIS
per provincia e orientamento del tetto, da incollare nel simulatore.

Uso:  python pvgis_tabella_rese.py
Output: rese_pvgis.json, rese_pvgis.csv e, a schermo, la riga JavaScript
        "var RESE = {...}" da incollare nel simulatore.

Endpoint e parametri: documentazione PVGIS "non-interactive service"
(lat, lon, peakpower, loss, angle, aspect con 0=sud, 90=ovest, -90=est,
outputformat=json). Il valore letto è outputs.totals.fixed.E_y.
"""
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://re.jrc.ec.europa.eu/api/PVcalc"
LOSS = 14      # perdite di sistema in % (valore di partenza suggerito da PVGIS)
TILT = 30      # inclinazione tipica di un tetto residenziale: assunzione, modificabile

# Orientamento -> azimut PVGIS (0=sud, 90=ovest, -90=est). Se ce n'è più di uno, si fa la media.
ORIENT = {
    "Sud": [0],
    "Sud-est / Sud-ovest": [-45, 45],
    "Est / Ovest": [-90, 90],
}

# Coordinate approssimative dei capoluoghi. Aggiungi le province che ti servono.
PROVINCE = {
    "Valencia": (39.47, -0.38),
    "Alicante": (38.35, -0.48),
    "Castellón": (39.99, -0.04),
    "Madrid": (40.42, -3.70),
    "Barcelona": (41.39, 2.17),
    "Sevilla": (37.39, -5.98),
    "Bilbao": (43.26, -2.93),
}


def resa(lat, lon, aspect, tentativi=3):
    """kWh/kWp/anno per un impianto fisso da 1 kWp."""
    params = urllib.parse.urlencode({
        "lat": lat, "lon": lon, "peakpower": 1, "loss": LOSS,
        "angle": TILT, "aspect": aspect, "outputformat": "json",
    })
    url = BASE + "?" + params
    for i in range(tentativi):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                dati = json.load(r)
            return float(dati["outputs"]["totals"]["fixed"]["E_y"])
        except (urllib.error.URLError, KeyError, ValueError) as e:
            print(f"  tentativo {i + 1} fallito ({e})")
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"PVGIS non risponde per lat={lat} lon={lon} aspect={aspect}")


def main():
    tabella = {}
    for nome, (lat, lon) in PROVINCE.items():
        print(nome)
        tabella[nome] = {}
        for etichetta, aspetti in ORIENT.items():
            valori = []
            for a in aspetti:
                valori.append(resa(lat, lon, a))
                time.sleep(0.3)  # resta ben sotto il limite di richieste di PVGIS
            tabella[nome][etichetta] = round(sum(valori) / len(valori))

    with open("rese_pvgis.json", "w", encoding="utf-8") as f:
        json.dump(tabella, f, ensure_ascii=False, indent=2)
    with open("rese_pvgis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["provincia"] + list(ORIENT))
        for nome, riga in tabella.items():
            w.writerow([nome] + [riga[o] for o in ORIENT])

    print("\nParametri usati: perdite %d%%, inclinazione %d gradi" % (LOSS, TILT))
    print("Incolla nel simulatore:\n")
    print("var RESE = " + json.dumps(tabella, ensure_ascii=False) + ";")


if __name__ == "__main__":
    main()
