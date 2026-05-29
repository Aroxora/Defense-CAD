#!/usr/bin/env python3
"""
Canonical pure-function calculators -- the single source of truth shared by the Python
analysis and the browser (TypeScript) engine. Every function here is a plain scalar/array
computation with no side effects, so the TS port in web/src/app/engine.ts can mirror it
1:1 and be parity-checked against scripts/export_parity.py output.

All equations are the same textbook forms used elsewhere in osint_cad; this module just
collects the pure math in one verifiable place.

Classification: UNCLASSIFIED // CONCEPTUAL // PUBLIC RELEASE
"""

import math
from typing import Dict, List, Tuple

C = 299_792_458.0          # m/s
K_BOLTZMANN = 1.380649e-23  # J/K
T0 = 290.0                 # K, reference noise temperature


# ---------------------------------------------------------------- radar range equation
def radar_max_range_km(pt_w: float, gain_dbi: float, freq_ghz: float, rcs_m2: float,
                       bandwidth_hz: float = 1e6, noise_figure_db: float = 3.0,
                       snr_min_db: float = 13.0, losses_db: float = 5.0,
                       n_integrate: int = 1) -> float:
    """Monostatic radar range equation:
        R = [ Pt G^2 lambda^2 sigma n / ( (4 pi)^3 k T0 B F SNR_min L ) ]^(1/4)
    Returns max detection range in km.
    """
    if rcs_m2 <= 0 or pt_w <= 0:
        return 0.0
    g = 10 ** (gain_dbi / 10.0)
    lam = C / (freq_ghz * 1e9)
    f = 10 ** (noise_figure_db / 10.0)
    snr = 10 ** (snr_min_db / 10.0)
    loss = 10 ** (losses_db / 10.0)
    num = pt_w * g * g * lam * lam * rcs_m2 * max(1, n_integrate)
    den = (4 * math.pi) ** 3 * K_BOLTZMANN * T0 * bandwidth_hz * f * snr * loss
    return (num / den) ** 0.25 / 1000.0


def aperture_gain_dbi(a_eff_m2: float, eta: float, freq_ghz: float) -> float:
    """Antenna gain from effective aperture: G = 4 pi A eta / lambda^2."""
    lam = C / (freq_ghz * 1e9)
    return 10.0 * math.log10(4 * math.pi * a_eff_m2 * eta / (lam * lam))


def scan_loss_db(az_deg: float) -> float:
    """Phased-array scan loss (beam broadening), 0 at boresight, ~-1.5 dB at 60 deg."""
    return -1.5 * (az_deg / 60.0) ** 2


def fspl_db(freq_ghz: float, range_km: float) -> float:
    """Free-space path loss: 20 log10(4 pi R / lambda)."""
    lam = C / (freq_ghz * 1e9)
    return 20.0 * math.log10(4 * math.pi * (range_km * 1000.0) / lam)


def aspect_rcs_m2(frontal_m2: float, side_m2: float, rear_m2: float, aspect_deg: float) -> float:
    """Smooth illustrative aspect-dependent RCS: interpolate in dBsm across sectors.

    aspect 0 = nose-on, 90/270 = beam, 180 = tail. Symmetric about 0-180.
    """
    a = aspect_deg % 360.0
    if a > 180.0:
        a = 360.0 - a
    f_db, s_db, r_db = (10 * math.log10(x) for x in (frontal_m2, side_m2, rear_m2))
    if a <= 90.0:
        w = (1 - math.cos(math.pi * a / 90.0)) / 2.0
        db = f_db * (1 - w) + s_db * w
    else:
        w = (1 - math.cos(math.pi * (a - 90.0) / 90.0)) / 2.0
        db = s_db * (1 - w) + r_db * w
    return 10 ** (db / 10.0)


# ---------------------------------------------------------------- radar horizon / coverage
def radar_horizon_km(h_radar_m: float, h_target_m: float) -> float:
    """4/3-Earth radar horizon (km)."""
    return 4.12 * (math.sqrt(max(0.0, h_radar_m)) + math.sqrt(max(0.0, h_target_m)))


def power_limited_range_km(ref_range_km: float, ref_rcs_m2: float, rcs_m2: float) -> float:
    """Radar-equation range scaled from a reference: R = R_ref (RCS/RCS_ref)^(1/4)."""
    if rcs_m2 <= 0:
        return 0.0
    return ref_range_km * (rcs_m2 / ref_rcs_m2) ** 0.25


def effective_coverage(h_radar_m: float, h_target_m: float, ref_range_km: float,
                       ref_rcs_m2: float, rcs_m2: float) -> Dict:
    pwr = power_limited_range_km(ref_range_km, ref_rcs_m2, rcs_m2)
    hor = radar_horizon_km(h_radar_m, h_target_m)
    eff = round(min(pwr, hor), 1)
    return {"power_limited_km": round(pwr, 1), "horizon_km": round(hor, 1),
            "effective_km": eff, "limited_by": "horizon" if hor < pwr else "power",
            "coverage_area_km2": round(math.pi * eff * eff)}


# ---------------------------------------------------------------- RF intercept / EW
def friis_intercept_range_km(eirp_dbm: float, rx_sensitivity_dbm: float, freq_ghz: float,
                             proc_gain_db: float = 0.0) -> float:
    lam = C / (freq_ghz * 1e9)
    pl_db = eirp_dbm - (rx_sensitivity_dbm - proc_gain_db)
    return (lam * 10 ** (pl_db / 20.0) / (4 * math.pi)) / 1000.0


def processing_gain_db(bandwidth_hz: float, integration_time_s: float) -> float:
    """Time-bandwidth (coherent) processing gain, 10*log10(B*T)."""
    return 10.0 * math.log10(bandwidth_hz * integration_time_s)


def js_ratio_db(jam_power_kw: float, range_km: float, victim_signal_dbm: float,
                freq_hz: float, jammer_ant_gain_db: float = 30.0) -> float:
    jam_power_dbw = 10 * math.log10(jam_power_kw * 1000.0)
    path_loss_db = 20 * math.log10(range_km * 1000.0) + 20 * math.log10(freq_hz) - 147.55
    return (jam_power_dbw + 30 - path_loss_db + jammer_ant_gain_db) - victim_signal_dbm


# ---------------------------------------------------------------- atmospheric (ITU-R P.676)
def atmospheric_specific_attenuation(freq_ghz: float, rho_vapor: float = 7.5) -> Dict:
    """Sea-level O2 + H2O specific attenuation (dB/km), ITU-R P.676-consistent."""
    f = freq_ghz
    if f < 54.0:
        gamma_o = (7.2 / (f ** 2 + 0.34) + 0.62 / ((54.0 - f) ** 1.16 + 0.83)) * f ** 2 * 1e-3
    elif f < 63.0:
        gamma_o = 0.5 + 14.5 / (1.0 + ((f - 60.0) / 1.5) ** 2)
    else:
        gamma_o = 0.5 + 6.0 / (1.0 + ((f - 63.0) / 9.0) ** 2)
    gamma_w = (0.05 + 0.0021 * rho_vapor
               + 3.6 / ((f - 22.235) ** 2 + 8.5)) * f ** 2 * rho_vapor * 1e-4
    return {"oxygen_db_km": gamma_o, "water_db_km": gamma_w, "total_db_km": gamma_o + gamma_w}


# ---------------------------------------------------------------- geolocation (GDOP / CRLB)
def ring_geometry(n: int, baseline_km: float, altitude_m: float = 10_000.0,
                  alt_spread_m: float = 3_000.0) -> List[List[float]]:
    r = baseline_km * 1000.0
    return [[r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n),
             altitude_m + (alt_spread_m if i % 2 else -alt_spread_m)] for i in range(n)]


def _mat3_inv(m: List[List[float]]):
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, i = m[2]
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-12:
        return None
    inv_det = 1.0 / det
    return [
        [(e * i - f * h) * inv_det, (c * h - b * i) * inv_det, (b * f - c * e) * inv_det],
        [(f * g - d * i) * inv_det, (a * i - c * g) * inv_det, (c * d - a * f) * inv_det],
        [(d * h - e * g) * inv_det, (b * g - a * h) * inv_det, (a * e - b * d) * inv_det],
    ]


def _unit(p, q):
    d = [p[0] - q[0], p[1] - q[1], p[2] - q[2]]
    r = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2) or 1.0
    return [d[0] / r, d[1] / r, d[2] / r]


def gdop(platforms: List[List[float]], emitter: List[float]):
    """sqrt(trace((G^T G)^-1)) with G = unit vectors emitter->platform. None if N<4/singular."""
    if len(platforms) < 4:
        return None
    g = [_unit(p, emitter) for p in platforms]
    gtg = [[sum(g[k][r] * g[k][col] for k in range(len(g))) for col in range(3)] for r in range(3)]
    inv = _mat3_inv(gtg)
    if inv is None:
        return None
    return math.sqrt(inv[0][0] + inv[1][1] + inv[2][2])


def crlb_cep_m(platforms: List[List[float]], emitter: List[float],
               timing_ns: float = 10.0):
    """Horizontal 50% CEP (m) from the TDOA Cramer-Rao bound. None if singular."""
    n = len(platforms)
    if n < 4:
        return None
    sigma_range = (timing_ns * 1e-9) * C
    u0 = _unit(platforms[0], emitter)
    rows = [[_unit(platforms[i], emitter)[k] - u0[k] for k in range(3)] for i in range(1, n)]
    fim = [[sum(rows[m][r] * rows[m][col] for m in range(len(rows))) / sigma_range ** 2
            for col in range(3)] for r in range(3)]
    inv = _mat3_inv(fim)
    if inv is None:
        return None
    var_xy = inv[0][0] + inv[1][1]
    return 1.1774 * math.sqrt(max(0.0, var_xy) / 2.0)


def geolocation_quality(n: int, baseline_km: float, timing_ns: float = 10.0,
                        ops_degrade: float = 5.0) -> Dict:
    plats = ring_geometry(n, baseline_km)
    emitter = [0.0, 0.0, 11_000.0]
    g = gdop(plats, emitter)
    cep = crlb_cep_m(plats, emitter, timing_ns)
    ill = (g is None) or (cep is None) or cep > 10_000
    return {"platforms": n, "baseline_km": baseline_km,
            "gdop": None if g is None else round(g, 2),
            "crlb_floor_m": None if ill else round(cep, 1),
            "ops_cep_m": None if ill else round(cep * ops_degrade),
            "ill_conditioned": ill}


# ---------------------------------------------------------------- missile defense
def kill_prob_salvo(pk: float, shots: int) -> float:
    return 1.0 - (1.0 - pk) ** max(0, shots)


def md_engage(pk: float, magazine: int, raid: int, shots_per_target: int = 2) -> Dict:
    pk_t = kill_prob_salvo(pk, shots_per_target)
    engageable = magazine // max(1, shots_per_target)
    engaged = min(raid, engageable)
    leakers = (raid - engaged) + engaged * (1.0 - pk_t)
    return {"pk_per_target": round(pk_t, 4), "engageable": engageable, "engaged": engaged,
            "expected_leakers": round(leakers, 2),
            "intercept_fraction": round(1.0 - leakers / raid, 4) if raid else 0.0,
            "magazine_exhausted": (raid - engaged) > 0}


def md_exchange_ratio(pk: float, interceptor_cost_musd: float, threat_cost_musd: float,
                      shots_per_target: int = 2) -> Dict:
    pk_t = kill_prob_salvo(pk, shots_per_target)
    per_kill = (shots_per_target / pk_t) if pk_t > 0 else float("inf")
    defender_cost = per_kill * interceptor_cost_musd
    ratio = defender_cost / threat_cost_musd if threat_cost_musd else float("inf")
    return {"interceptors_per_kill": round(per_kill, 2),
            "defender_cost_per_kill_musd": round(defender_cost, 1),
            "cost_exchange_ratio": round(ratio, 2),
            "favorable_for_defender": ratio < 1.0}


# ---------------------------------------------------------------- cost-benefit value
def lifecycle_cost_busd(unit_musd: float, qty: int, rnd_musd: float,
                        oandm_musd: float, life_years: int) -> float:
    return (rnd_musd + unit_musd * qty + oandm_musd * qty * life_years) / 1000.0


def value_index(benefit: float, survivability: float, lcc_busd: float) -> float:
    return (benefit * survivability / 100.0 / lcc_busd) if lcc_busd > 0 else 0.0


def value_ci(benefit: float, survivability: float, lcc_busd: float,
             confidence: float) -> Tuple[float, float]:
    v = value_index(benefit, survivability, lcc_busd)
    rel = max(0.0, 1.0 - confidence) * math.sqrt(3)
    return (max(0.0, v * (1 - rel)), v * (1 + rel))
