# Simulatore di preventivo FV + batteria

Interactive quote simulator for residential solar + battery proposals in Spain. Input a customer's consumption, province and roof orientation; get back a sized system, self-consumption estimate and payback range — formatted as a printable customer-facing proposal, not an analyst's notebook.

**[Live demo →](https://beccaccino868.github.io/fv-battery-quote-simulator/)** 

Third project in a small energy-sector portfolio, alongside [`battery-arbitrage-spain`](#) (v1/v2: hourly linear-programming battery dispatch against Spanish day-ahead prices). Where v1/v2 answers "how do you optimize a battery against market prices," this project answers a different question: "what would a técnico comercial hand a customer."

## Two proposal modes

- **New installation** — sizes a new FV system (and optional battery) from the customer's annual consumption.
- **Battery retrofit** — for a customer who already has FV and is evaluating adding storage. Only the battery is costed; the existing FV size is a direct input.

The retrofit mode exists because of a specific market fact, not because two modes look more sophisticated than one: according to APPA Renovables' *Informe Anual de Autoconsumo Fotovoltaico y Almacenamiento 2025*, new residential FV installations fell for a third consecutive year in 2025 (−15%), while behind-the-meter battery storage grew 119% in the same year — largely existing FV owners adding storage. A tool aimed at a 2026 técnico comercial that only models new installations is modeling last decade's sale.

## How the numbers are produced

- **Yield (kWh/kWp/year), by province and roof orientation** — [PVGIS](https://re.jrc.ec.europa.eu/api/PVcalc), fixed system, 30° tilt, 14% system losses. See `pvgis_tabella_rese.py`.
- **Self-consumption quota** — not a fixed assumption. Calibrated by running an hour-by-hour rule-based dispatch (FV → house → battery → grid, no arbitrage) over a full year of PVGIS production and a synthetic consumption profile, across a grid of FV-size-to-consumption and battery-size-to-consumption ratios. See `calibrazione_autoconsumo.py` and `tabella_autoconsumo_griglia.py`. The simulator bilinearly interpolates this table at run time.
- **Costs (FV €/kWp, battery €/kWh)** — mid-range estimates from public Spanish-market sources, September 2026 (FV: 850–1,300 €/kWp; battery: 600–900 €/kWh retail, small residential systems). Not verified against a real invoice.
- **State tax deduction** — 10% IRPF deduction on a deductible base up to €5,000/year (Plan Anticrisis 2026). Shown separately from the gross investment; payback is computed on the net figure.

## What is a placeholder, not a fact

Every one of these is editable in the "Parametri provvisori" panel and should be treated as provisional until checked against a real quote or an official source:
- FV and battery unit costs
- Surplus compensation rate (€/kWh)
- Cost uncertainty margin
- Deduction rate and cap

## What is deliberately left out

- **Municipal IBI/ICIO property-tax rebates.** These exist (up to 50%/95% in some Valencia-area municipalities) and materially change payback, but vary by municipality and I don't have a verified figure for any specific one. Showing a number here would be false precision; the simulator states this omission rather than guessing.
- **Autoconsumo colectivo (shared/community self-consumption).** EU Directive 2024/1711 allows sharing surplus generation with neighbours up to 6 MW collectively; transposition into Spanish law is pending as of September 2026. Not modeled — the regulatory basis isn't settled enough to size reliably yet — but worth tracking for a v3.
- **Panel degradation, incentive changes over the system's lifetime, electricity price inflation.** The payback is a snapshot at today's prices and today's incentives.

## Known limitations of the self-consumption model

- Calibrated on **one synthetic household consumption profile** (evening-peak, low daytime use) and **one year of PVGIS data (2023) for Valencia**. It does not account for different household consumption shapes (e.g. someone home during the day) or other provinces' weather years.
- Battery sizing rule (kWh per MWh of annual consumption) and the assumed charge/discharge rate (capacity ÷ 2 hours) are my own choices, not requirements.

## Repository structure

```
simulatore-preventivo-fv.html   — the tool itself (self-contained, no build step)
pvgis_tabella_rese.py           — regenerates the PVGIS yield table
calibrazione_autoconsumo.py     — single-scenario self-consumption calibration (sanity check)
tabella_autoconsumo_griglia.py  — full FV/consumption × battery/consumption calibration grid
README.md                       — this file
```

## Status

Prototype. Costs, surplus compensation and the deduction cap need verification against real Spanish market data before any output is shown to an actual customer.
