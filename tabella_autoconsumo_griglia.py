# =====================================================================
# TABELLA DI AUTOCONSUMO PER IL SIMULATORE - da incollare in una NUOVA CELLA
# in fondo al notebook v2, DOPO aver eseguito la cella di calibrazione
# (quella che ha stampato le 12 righe): questa cella riusa da li' la
# funzione simula_autoconsumo, fv_per_kwp, indice e genera_serie_consumo.
#
# Idea: la quota di autoconsumo dipende da due rapporti, non da valori assoluti:
#   - quanto FV c'e' rispetto al consumo (kWp per 1000 kWh/anno)
#   - quanta batteria c'e' rispetto al consumo (kWh per 1000 kWh/anno)
# Se raddoppi FV, consumo e batteria insieme, la quota non cambia: e' una
# proprieta' del modello (tutto e' proporzionale). Quindi basta UNA tabella
# a due entrate, invece di una costante o di migliaia di casi.
# =====================================================================
import json
import numpy as np
import pandas as pd

for nome in ("simula_autoconsumo", "fv_per_kwp", "indice", "genera_serie_consumo"):
    if nome not in globals():
        raise NameError(f"Manca '{nome}': esegui prima la cella di calibrazione.")

RAPPORTI_FV = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5]   # kWp per 1000 kWh/anno di consumo
RAPPORTI_BATT = [0, 0.5, 1, 1.5, 2, 3, 4]                     # kWh per 1000 kWh/anno di consumo

consumo = genera_serie_consumo(indice, 3000)["consumo_kwh"].to_numpy()
mwh = consumo.sum() / 1000          # consumo annuo simulato, in MWh (circa 3,05)

quota = {}                          # quota[rapporto_batteria][rapporto_fv] = quota autoconsumo %
for b in RAPPORTI_BATT:
    quota[b] = {}
    for r in RAPPORTI_FV:
        fv = fv_per_kwp * (r * mwh)
        sim = simula_autoconsumo(fv, consumo, batt_kwh=b * mwh)
        usata = sim["diretto"] + sim["batt_a_casa"]
        quota[b][r] = round(100 * usata / fv.sum(), 1)

tab = pd.DataFrame(quota).T
tab.index.name = "batteria kWh/MWh"
tab.columns = [f"FV {r} kWp/MWh" for r in RAPPORTI_FV]
print("Quota di autoconsumo (%) - righe: batteria, colonne: FV\n")
print(tab.to_string())

# Controllo: raddoppiando consumo, FV e batteria il risultato deve restare uguale
fv2 = fv_per_kwp * (1.0 * mwh * 2)
c2 = consumo * 2
s2 = simula_autoconsumo(fv2, c2, batt_kwh=2 * mwh * 2)
q2 = round(100 * (s2["diretto"] + s2["batt_a_casa"]) / fv2.sum(), 1)
print(f"\nControllo di scala: quota {quota[2][1.0]}% (base) contro {q2}% (tutto x2): devono coincidere.")

tab.to_csv("autoconsumo_griglia.csv")
print("\nDa incollare nel simulatore:\n")
print("var QUOTA = " + json.dumps({"fv": RAPPORTI_FV, "batt": RAPPORTI_BATT,
                                   "q": [[quota[b][r] for r in RAPPORTI_FV] for b in RAPPORTI_BATT]}) + ";")
