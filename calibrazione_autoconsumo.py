# =====================================================================
# CALIBRAZIONE DELL'AUTOCONSUMO - da incollare in una NUOVA CELLA
# in fondo al notebook v2, dopo aver eseguito tutte le celle precedenti.
#
# Cosa fa: simula un anno intero (8760 ore) con una regola semplice,
# la stessa che segue un vero impianto di autoconsumo:
#   1) il FV alimenta prima la casa
#   2) l'eccesso di FV carica la batteria
#   3) se la batteria e' piena, l'eccesso va in rete
#   4) se la casa ha ancora bisogno di energia: prima la batteria, poi la rete
# La batteria NON si carica dalla rete e NON vende alla rete: niente arbitraggio.
# I prezzi non servono: qui misuriamo solo energie (kWh).
#
# Usa dal notebook: df_fv, genera_serie_consumo, PEAK_POWER_KW
# =====================================================================
import numpy as np
import pandas as pd

for nome in ("df_fv", "genera_serie_consumo", "PEAK_POWER_KW"):
    if nome not in globals():
        raise NameError(f"Manca '{nome}': esegui prima le celle precedenti del notebook.")


def simula_autoconsumo(fv_kwh, consumo_kwh, batt_kwh=0.0, batt_kw=None, efficienza=0.90):
    """Simulazione ora per ora. fv_kwh e consumo_kwh sono array numpy (kWh in ogni ora)."""
    if batt_kw is None:
        batt_kw = batt_kwh / 2          # assunzione: la batteria si carica/scarica in 2 ore
    eta = efficienza ** 0.5             # perdita metà in carica, metà in scarica
    soc = 0.0                           # stato di carica della batteria, parte da vuota
    tot = dict(diretto=0.0, in_batteria=0.0, batt_a_casa=0.0, export=0.0, acquisto=0.0)

    for fv, c in zip(fv_kwh, consumo_kwh):
        diretto = min(fv, c)            # 1) FV -> casa
        fv_res = fv - diretto
        c_res = c - diretto
        if batt_kwh > 0:
            # 2) eccesso FV -> batteria (nei limiti di potenza e di spazio libero)
            carica = min(fv_res, batt_kw, (batt_kwh - soc) / eta)
            soc += carica * eta
            fv_res -= carica
            # 4) casa scoperta -> batteria (nei limiti di potenza e di energia disponibile)
            scarica = min(c_res, batt_kw, soc * eta)
            soc -= scarica / eta
            c_res -= scarica
            tot["in_batteria"] += carica
            tot["batt_a_casa"] += scarica
        tot["diretto"] += diretto
        tot["export"] += fv_res         # 3) eccesso finale -> rete
        tot["acquisto"] += c_res        # resto del fabbisogno -> rete
    return tot


# --- Dati di base: un anno intero di produzione FV (PVGIS 2023) ---
fv_per_kwp = (df_fv["potenza_fv_kw"] / PEAK_POWER_KW).to_numpy()   # kWh per ogni kWp installato
indice = df_fv["datetime"]

righe = []
for consumo_annuo in (3000, 5500):
    consumo = genera_serie_consumo(indice, consumo_annuo)["consumo_kwh"].to_numpy()
    for kwp in (2.2, 3.5):
        fv = fv_per_kwp * kwp
        for batt in (0, 5, 10):
            r = simula_autoconsumo(fv, consumo, batt_kwh=batt)
            prod = fv.sum()
            usata = r["diretto"] + r["batt_a_casa"]
            righe.append({
                "Consumo (kWh)": round(consumo.sum()),
                "FV (kWp)": kwp,
                "Batteria (kWh)": batt,
                "Produzione FV (kWh)": round(prod),
                "Quota autoconsumo (%)": round(100 * usata / prod, 1),
                "Copertura consumo (%)": round(100 * usata / consumo.sum(), 1),
                "Acquisto da rete (kWh)": round(r["acquisto"]),
                "Immesso in rete (kWh)": round(r["export"]),
            })

tabella_cal = pd.DataFrame(righe)
print(tabella_cal.to_string(index=False))
tabella_cal.to_csv("calibrazione_autoconsumo.csv", index=False)
print("\nSalvato anche come calibrazione_autoconsumo.csv (cartella file a sinistra).")
