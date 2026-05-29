#!/usr/bin/env python3
"""
Actionable EW strategy -- reusable physics helpers + structured export.

Shared source of truth for both scripts/ew_strategy_analysis.py (human-readable report)
and scripts/export_web_data.py (JSON for the web app). All figures are computed from Friis
link budget, non-coherent integration gain, and the geolocation_network GDOP/CRLB models.

Premise (established by the physics): a directional, frequency-hopping LPI/LPD link such as
MADL is NOT reliably jammable from standoff -- so the actionable lines of effort are passive
ESM geolocation, own-datalink hardening, and reallocating active EW to where J/S is favorable.

Classification: UNCLASSIFIED // CONCEPTUAL // PUBLIC RELEASE
"""

import numpy as np

from osint_cad.sensors.geolocation_network import GeolocationEngine

C = 299_792_458.0  # m/s

# Representative OSINT inputs (Ku-band LPI sidelobe; fielded fighter-class ESM)
SIDELOBE_EIRP_DBM = 34.5
FREQ_GHZ = 14.4
BANDWIDTH_HZ = 100e6
ESM_SENSITIVITY_DBM = -74.0
TX_PLUS_MAIN_GAIN_DBM = 33.0 + 31.5
OPS_DEGRADE = 5.0  # CRLB floor -> realistic ops CEP multiplier (hopping/multipath/cal)


def friis_intercept_range_km(eirp_dbm, rx_sensitivity_dbm, freq_ghz, proc_gain_db=0.0):
    """Max free-space intercept range (km). R = lambda * 10^(PL/20) / (4 pi)."""
    lam = C / (freq_ghz * 1e9)
    pl_db = eirp_dbm - (rx_sensitivity_dbm - proc_gain_db)
    return (lam * 10 ** (pl_db / 20.0) / (4 * np.pi)) / 1000.0


def processing_gain_db(bandwidth_hz, integration_time_s):
    """Non-coherent integration processing gain (dB)."""
    return 10.0 * np.log10(bandwidth_hz * integration_time_s)


def js_db(jam_power_kw, range_km, victim_signal_dbm, freq_hz, jammer_ant_gain_db=30.0):
    """Jammer-to-signal ratio (dB) at the victim (free-space)."""
    jam_power_dbw = 10 * np.log10(jam_power_kw * 1000.0)
    path_loss_db = 20 * np.log10(range_km * 1000.0) + 20 * np.log10(freq_hz) - 147.55
    return (jam_power_dbw + 30 - path_loss_db + jammer_ant_gain_db) - victim_signal_dbm


def ring_geometry(n, baseline_km, altitude_m=10_000.0, alt_spread_m=3_000.0):
    """N ESM platforms on a ring of given baseline radius, with altitude diversity."""
    r = baseline_km * 1000.0
    return np.array([[r * np.cos(2 * np.pi * i / n),
                      r * np.sin(2 * np.pi * i / n),
                      altitude_m + (alt_spread_m if i % 2 else -alt_spread_m)]
                     for i in range(n)])


def crlb_cep_m(engine, platforms_m, emitter_m, timing_ns):
    """Horizontal 50% CEP (m) from the TDOA CRLB for a given geometry."""
    crlb = engine.calculate_crlb_tdoa(np.asarray(platforms_m), np.asarray(emitter_m),
                                      timing_uncertainty_ns=timing_ns)
    var_xy = crlb[0, 0] + crlb[1, 1]
    sigma = np.sqrt(max(var_xy, 0.0) / 2.0)
    return 1.1774 * sigma


# --- structured results -------------------------------------------------------------

def intercept_vs_dwell():
    rows = []
    for dwell_us in (1, 10, 100, 1000):
        g = processing_gain_db(BANDWIDTH_HZ, dwell_us * 1e-6)
        rng = friis_intercept_range_km(SIDELOBE_EIRP_DBM, ESM_SENSITIVITY_DBM, FREQ_GHZ, g)
        rows.append({"dwell_us": dwell_us, "proc_gain_db": round(g, 1),
                     "intercept_range_km": round(rng)})
    return rows


def geolocation_sizing(timing_ns=10.0):
    engine = GeolocationEngine()
    emitter = np.array([0.0, 0.0, 11_000.0])
    rows = []
    for n in (4, 6, 8):
        for baseline in (30, 60, 120):
            plats = ring_geometry(n, baseline)
            gdop, _ = engine.calculate_gdop(plats, emitter)
            cep = crlb_cep_m(engine, plats, emitter, timing_ns)
            ill = bool((not np.isfinite(gdop)) or (not np.isfinite(cep)) or cep > 10_000)
            rows.append({
                "platforms": int(n), "baseline_km": int(baseline),
                "gdop": None if not np.isfinite(gdop) else round(float(gdop), 2),
                "crlb_floor_m": None if ill else round(float(cep), 1),
                "ops_cep_m": None if ill else int(round(float(cep) * OPS_DEGRADE)),
                "ill_conditioned": ill,
            })
    return rows


def hardening_sweep(adversary_dwell_us=100):
    g = processing_gain_db(BANDWIDTH_HZ, adversary_dwell_us * 1e-6)
    rows = []
    for sidelobe_db in (-20, -25, -30, -35, -40, -45):
        eirp = TX_PLUS_MAIN_GAIN_DBM + sidelobe_db
        rng = friis_intercept_range_km(eirp, ESM_SENSITIVITY_DBM, FREQ_GHZ, g)
        rows.append({"sidelobe_db": sidelobe_db, "sidelobe_eirp_dbm": round(eirp, 1),
                     "adversary_intercept_km": round(rng)})
    return rows


def reallocation(jam_power_kw=30.0, range_km=100.0, madl_isolation_db=25.0):
    js_radar = js_db(jam_power_kw, range_km, -60.0, 10e9)
    js_madl = js_db(jam_power_kw, range_km, -60.0, 14.4e9) - madl_isolation_db
    return {
        "jam_power_kw": jam_power_kw, "range_km": range_km,
        "js_radar_db": round(float(js_radar), 1), "radar_effective": bool(js_radar > 10),
        "js_madl_db": round(float(js_madl), 1), "madl_effective": bool(js_madl > 10),
        "madl_isolation_db": madl_isolation_db,
    }


LINES_OF_EFFORT = [
    {"id": 1, "title": "Passive ESM geolocation network",
     "subtitle": "detect, don't jam",
     "detail": "Sidelobe intercept + multi-platform TDOA/FDOA. >=4 synchronized platforms, "
               "~30 km baseline, <=10 ns sync -> GDOP < 5, operational CEP ~8-11 m."},
    {"id": 2, "title": "Harden your own datalink",
     "subtitle": "defeat the adversary's LoE 1",
     "detail": "Driving sidelobes -30 -> -40 dB cuts an adversary's intercept range ~68%. "
               "Concrete antenna/EMCON spec, no new weapon."},
    {"id": 3, "title": "Reallocate active EW to where physics rewards it",
     "subtitle": "tactic, no new hardware",
     "detail": "The same jammer useless vs the LPI link is +12 dB J/S vs the main radar and "
               "valuable in the terminal endgame."},
    {"id": 4, "title": "Stop funding standoff MADL jamming",
     "subtitle": "physics says ~0 effect",
     "detail": "Redirect that capacity to passive ESM (LoE 1) and radar denial (LoE 3)."},
]


def export() -> dict:
    """Structured dict consumed by the web exporter."""
    return {
        "premise": "A directional, frequency-hopping LPI/LPD link (e.g. MADL) is not "
                   "reliably jammable from standoff; the actionable answer is passive ES, "
                   "hardening, and EW reallocation.",
        "intercept_vs_dwell": intercept_vs_dwell(),
        "geolocation_sizing": geolocation_sizing(),
        "hardening_sweep": hardening_sweep(),
        "reallocation": reallocation(),
        "lines_of_effort": LINES_OF_EFFORT,
    }
