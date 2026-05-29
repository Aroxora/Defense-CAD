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
SIGMA_SB = 5.670374419e-8  # W m^-2 K^-4, Stefan-Boltzmann
MU_EARTH = 398_600.4418    # km^3/s^2, Earth gravitational parameter
R_EARTH = 6378.137         # km, Earth equatorial radius


def _bisect(f, lo, hi, iters=80):
    """Deterministic bisection (fixed iteration count) so Python and the TS port agree.
    Assumes f(lo) <= 0 <= f(hi)."""
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


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


# ---------------------------------------------------------------- EW: jamming & detection
def ssj_burnthrough_range_km(pt_kw: float, gt_dbi: float, sigma_m2: float, pj_w: float,
                             gj_dbi: float, br_mhz: float, bj_mhz: float,
                             sjreq_db: float) -> float:
    """Self-screening-jammer burn-through range (km). Skin return overtakes the on-board
    jammer as the target closes: R_bt = sqrt(Pt Gt sigma Bj (S/J)_req / (4 pi Pj Gj Br))."""
    pt, gt, gj = pt_kw * 1000.0, 10 ** (gt_dbi / 10), 10 ** (gj_dbi / 10)
    sj, br, bj = 10 ** (sjreq_db / 10), br_mhz * 1e6, bj_mhz * 1e6
    num = pt * gt * sigma_m2 * bj * sj
    den = 4 * math.pi * pj_w * gj * br
    return (num / den) ** 0.5 / 1000.0 if den > 0 else 0.0


def soj_ssj_crossover_km(gt_dbi: float, gs_dbi: float, rj_km: float) -> float:
    """Target range where standoff (sidelobe) and self-protection (mainlobe) jamming have
    equal J/S: R_x = Rj * sqrt(Gt/Gs). Parameter-independent of power/RCS/bandwidth."""
    return rj_km * math.sqrt(10 ** ((gt_dbi - gs_dbi) / 10))


def albersheim_required_snr_db(pd: float, pfa: float, n: int = 1) -> float:
    """Albersheim's closed-form required single-pulse SNR (dB) for detection probability pd
    at false-alarm pfa, noncoherently integrating n pulses (Swerling 0, linear detector)."""
    a = math.log(0.62 / pfa)
    b = math.log(pd / (1.0 - pd))
    return -5 * math.log10(n) + (6.2 + 4.54 / math.sqrt(n + 0.44)) * math.log10(a + 0.12 * a * b + 1.7 * b)


def albersheim_pd_from_snr(snr_db: float, pfa: float, n: int = 1) -> float:
    """Inverse Albersheim: detection probability from single-pulse SNR (dB) at pfa, n pulses."""
    a = math.log(0.62 / pfa)
    z = (snr_db + 5 * math.log10(n)) / (6.2 + 4.54 / math.sqrt(n + 0.44))
    b = (10 ** z - a) / (0.12 * a + 1.7)
    return 1.0 / (1.0 + math.exp(-b))


def chaff_cloud_rcs_m2(n_dipoles: float, freq_ghz: float, k: float = 0.17) -> float:
    """Average RCS of a cloud of N randomly-oriented resonant half-wave dipoles:
    sigma ~= k * N * lambda^2 (k ~ 0.15-0.18)."""
    lam = C / (freq_ghz * 1e9)
    return k * n_dipoles * lam * lam


def noise_jamming_range_factor(jn_db: float) -> float:
    """Detection-range shrink factor under barrage noise jamming that raises the noise floor
    by J/N: R_eff/R_free = (1/(1 + J/N))^(1/4)."""
    return (1.0 / (1.0 + 10 ** (jn_db / 10))) ** 0.25


# ---------------------------------------------------------------- CAD-derived / materials
def radar_range_simple_km(pt_w: float, g_dbi: float, freq_ghz: float, sigma_m2: float,
                          pmin_w: float) -> float:
    """Simplified radar range equation with an explicit minimum detectable power:
    R = [Pt G^2 lambda^2 sigma / ((4 pi)^3 Pmin)]^(1/4). Used for aspect-RCS envelopes."""
    if sigma_m2 <= 0 or pt_w <= 0:
        return 0.0
    g = 10 ** (g_dbi / 10)
    lam = C / (freq_ghz * 1e9)
    return ((pt_w * g * g * lam * lam * sigma_m2) / ((4 * math.pi) ** 3 * pmin_w)) ** 0.25 / 1000.0


def ram_reflection_coefficient(absorption_db: float) -> float:
    """Reflection coefficient (power) of radar-absorbent material: Gamma = 10^(-A/10)."""
    return 10 ** (-absorption_db / 10)


def ram_reflection_coefficient_eff(absorption_db: float, freq_ghz: float) -> float:
    """Frequency-scaled RAM reflection coefficient (matches cad_rcs_calculator's RAM model):
    Gamma_eff = Gamma * (1 - 0.1*log10(f/10))."""
    return ram_reflection_coefficient(absorption_db) * (1 - 0.1 * math.log10(freq_ghz / 10.0))


def po_validity_ratio(freq_ghz: float, char_length_m: float) -> float:
    """Object-size-to-wavelength ratio L/lambda; Physical Optics is valid when L/lambda >> 1."""
    lam = C / (freq_ghz * 1e9)
    return char_length_m / lam


# ---------------------------------------------------------------- comms / SATCOM link budget
def parabolic_gain_dbi(diameter_m: float, eta: float, freq_ghz: float) -> float:
    """Parabolic-dish gain: G = eta * (pi D / lambda)^2 -> dBi."""
    lam = C / (freq_ghz * 1e9)
    return 10.0 * math.log10(eta * (math.pi * diameter_m / lam) ** 2)


def link_margin_db(p_tx_dbw: float, g_tx_dbi: float, diameter_m: float, eta: float,
                   freq_ghz: float, range_km: float, l_other_db: float, t_sys_k: float,
                   rb_mbps: float, ebn0_req_db: float) -> float:
    """End-to-end Eb/N0 link margin (dB). Positive => link closes."""
    g_rx = parabolic_gain_dbi(diameter_m, eta, freq_ghz)
    p_rx = p_tx_dbw + g_tx_dbi + g_rx - fspl_db(freq_ghz, range_km) - l_other_db
    cn0 = p_rx - 10.0 * math.log10(K_BOLTZMANN * t_sys_k)          # dB-Hz
    ebn0 = cn0 - 10.0 * math.log10(rb_mbps * 1e6)
    return ebn0 - ebn0_req_db


# ---------------------------------------------------------------- PNT / GNSS
def gnss_uere_m(sig_iono: float, sig_tropo: float, sig_clk: float,
                sig_mp: float, sig_rx: float) -> float:
    """User-equivalent range error (1-sigma) as the RSS of the error budget."""
    return math.sqrt(sig_iono ** 2 + sig_tropo ** 2 + sig_clk ** 2 + sig_mp ** 2 + sig_rx ** 2)


def gnss_horizontal_error_m(uere_m: float, hdop: float) -> float:
    """Horizontal 1-sigma position error = HDOP * UERE."""
    return hdop * uere_m


# ---------------------------------------------------------------- IR / EO (IRST)
def irst_radiant_intensity(t_target_k: float, t_back_k: float, area_m2: float,
                           emissivity: float, in_band_fraction: float) -> float:
    """Apparent in-band radiant intensity contrast (W/sr): eps*sigma*(Tt^4-Tb^4)*A*frac/pi."""
    dt4 = t_target_k ** 4 - t_back_k ** 4
    return emissivity * SIGMA_SB * dt4 * area_m2 * in_band_fraction / math.pi


def irst_detection_range_km(t_target_k: float, t_back_k: float, area_m2: float,
                            emissivity: float, in_band_fraction: float, tau_opt: float,
                            alpha_per_km: float, nei_w_m2: float) -> float:
    """Point-source IR detection range with Beer-Lambert atmosphere.
    Detect when intensity*tau_opt*exp(-alpha R) / R^2 >= NEI. Solved by bisection (km)."""
    di = irst_radiant_intensity(t_target_k, t_back_k, area_m2, emissivity, in_band_fraction)
    if di <= 0 or nei_w_m2 <= 0:
        return 0.0
    r_vac_km = math.sqrt(di * tau_opt / nei_w_m2) / 1000.0  # vacuum (no atmosphere)

    def f(r_km):  # received irradiance minus NEI, sign flips at the detection range
        r_m = r_km * 1000.0
        return nei_w_m2 - di * tau_opt * math.exp(-alpha_per_km * r_km) / (r_m * r_m)

    return _bisect(f, 1e-3, max(r_vac_km, 1e-3))


# ---------------------------------------------------------------- undersea / passive sonar
def sonar_figure_of_merit_db(source_level_db: float, noise_level_db: float,
                             directivity_index_db: float, detection_threshold_db: float) -> float:
    """Passive-sonar figure of merit = max allowable transmission loss = SL-(NL-DI)-DT."""
    return source_level_db - (noise_level_db - directivity_index_db) - detection_threshold_db


def sonar_tl_spherical_db(range_km: float, alpha_db_per_km: float) -> float:
    """Spherical-spreading transmission loss: 20 log10(r_m) + alpha*r_km."""
    r_m = max(range_km * 1000.0, 1.0)
    return 20.0 * math.log10(r_m) + alpha_db_per_km * range_km


def sonar_detection_range_km(source_level_db: float, noise_level_db: float,
                             directivity_index_db: float, detection_threshold_db: float,
                             alpha_db_per_km: float) -> float:
    """Range where transmission loss equals the figure of merit (spherical spreading)."""
    fom = sonar_figure_of_merit_db(source_level_db, noise_level_db,
                                   directivity_index_db, detection_threshold_db)
    return _bisect(lambda r: sonar_tl_spherical_db(r, alpha_db_per_km) - fom, 1e-3, 10000.0)


# ---------------------------------------------------------------- space / orbital mechanics
def orbital_velocity_kms(altitude_km: float) -> float:
    """Circular-orbit speed v = sqrt(mu/a), a = R_E + h."""
    return math.sqrt(MU_EARTH / (R_EARTH + altitude_km))


def orbital_period_min(altitude_km: float) -> float:
    """Circular-orbit period T = 2 pi sqrt(a^3/mu), in minutes."""
    a = R_EARTH + altitude_km
    return 2 * math.pi * math.sqrt(a ** 3 / MU_EARTH) / 60.0


def coverage_half_angle_deg(altitude_km: float, min_elevation_deg: float) -> float:
    """Earth-central half-angle of the access footprint at a minimum elevation angle:
    lambda = arccos( (R_E/a) cos(el) ) - el."""
    a = R_EARTH + altitude_km
    el = math.radians(min_elevation_deg)
    arg = max(-1.0, min(1.0, (R_EARTH / a) * math.cos(el)))
    return math.degrees(math.acos(arg) - el)


# ---------------------------------------------------------------- kinematics / ballistics
def projectile_range_km(v0_ms: float, theta_deg: float, g: float = 9.81) -> float:
    """Vacuum projectile range over level ground: R = v0^2 sin(2 theta)/g."""
    return (v0_ms ** 2 * math.sin(2 * math.radians(theta_deg)) / g) / 1000.0


def projectile_apogee_km(v0_ms: float, theta_deg: float, g: float = 9.81) -> float:
    """Vacuum maximum ordinate: h = v0^2 sin^2(theta)/(2g)."""
    return (v0_ms ** 2 * math.sin(math.radians(theta_deg)) ** 2 / (2 * g)) / 1000.0


def projectile_tof_s(v0_ms: float, theta_deg: float, g: float = 9.81) -> float:
    """Vacuum time of flight: t = 2 v0 sin(theta)/g."""
    return 2 * v0_ms * math.sin(math.radians(theta_deg)) / g


# ---------------------------------------------------------------- directed energy (laser)
def laser_divergence_urad(wavelength_um: float, aperture_m: float, m2: float) -> float:
    """Diffraction-limited beam divergence half-angle: theta = M2 * 1.22 * lambda / D (urad)."""
    return m2 * 1.22 * (wavelength_um * 1e-6) / aperture_m * 1e6


def laser_spot_radius_m(wavelength_um: float, aperture_m: float, m2: float, range_km: float) -> float:
    """Far-field spot radius: w = sqrt((D/2)^2 + (theta*R)^2)."""
    theta = m2 * 1.22 * (wavelength_um * 1e-6) / aperture_m  # rad
    return math.sqrt((aperture_m / 2) ** 2 + (theta * range_km * 1000.0) ** 2)


def laser_irradiance_kw_cm2(power_kw: float, wavelength_um: float, aperture_m: float,
                            m2: float, alpha_per_km: float, range_km: float) -> float:
    """Peak irradiance on target: I = P*exp(-alpha R) / (pi w^2), in kW/cm^2."""
    w = laser_spot_radius_m(wavelength_um, aperture_m, m2, range_km)
    area_cm2 = math.pi * w * w * 1e4
    return power_kw * math.exp(-alpha_per_km * range_km) / area_cm2 if area_cm2 > 0 else 0.0


# ---------------------------------------------------------------- guidance (collision triangle)
def collision_lead_angle_deg(vm_ms: float, vt_ms: float, beta_deg: float) -> float:
    """Lead angle off the LOS for a constant-bearing collision: sin(L) = (Vt/Vm) sin(beta)."""
    ratio = (vt_ms / vm_ms) * math.sin(math.radians(beta_deg))
    return math.degrees(math.asin(min(1.0, max(-1.0, ratio))))


def collision_closing_speed_ms(vm_ms: float, vt_ms: float, beta_deg: float) -> float:
    """Closing speed along the LOS: Vc = Vm cos(L) + Vt cos(beta)."""
    lead = math.radians(collision_lead_angle_deg(vm_ms, vt_ms, beta_deg))
    return vm_ms * math.cos(lead) + vt_ms * math.cos(math.radians(beta_deg))


def pn_lateral_accel_g(vm_ms: float, vt_ms: float, beta_deg: float, n: float,
                       los_rate_deg_s: float) -> float:
    """Proportional-navigation lateral acceleration command a = N Vc (LOS rate), in g."""
    vc = collision_closing_speed_ms(vm_ms, vt_ms, beta_deg)
    return n * vc * math.radians(los_rate_deg_s) / 9.81


# ---------------------------------------------------------------- ISR / SAR & optical
def sar_azimuth_resolution_m(antenna_az_len_m: float) -> float:
    """Stripmap SAR azimuth resolution = D_az/2 (independent of range and wavelength)."""
    return antenna_az_len_m / 2.0


def sar_range_resolution_m(bandwidth_mhz: float) -> float:
    """Slant-range resolution = c / (2 B)."""
    return C / (2 * bandwidth_mhz * 1e6)


def eo_diffraction_gsd_m(wavelength_um: float, aperture_m: float, range_km: float) -> float:
    """Diffraction-limited optical ground sample distance = 1.22 lambda R / D."""
    return 1.22 * (wavelength_um * 1e-6) * (range_km * 1000.0) / aperture_m


# ---------------------------------------------------------------- propagation (rain, ITU-R P.838)
# ITU-R P.838-3 horizontal-polarization coefficients, tabulated at standard frequencies.
# (The legacy inline fit in rf_propagation.py is ~1000x too small; these match the Rec.)
_P838_F = [1, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 35, 40]
_P838_K = [0.0000259, 0.0000847, 0.0006001, 0.001805, 0.004115, 0.01010, 0.01880,
           0.03670, 0.07510, 0.1240, 0.1870, 0.2630, 0.3500]
_P838_A = [0.9691, 1.0664, 1.1206, 1.1216, 1.1500, 1.2760, 1.2170, 1.1540, 1.0990,
           1.0610, 1.0210, 0.9790, 0.9390]


def _interp_logf(freq_ghz: float, ys, logy: bool) -> float:
    """Piecewise-linear interpolation of a coefficient vs log10(frequency)."""
    lf = math.log10(max(freq_ghz, _P838_F[0]))
    xs = [math.log10(f) for f in _P838_F]
    if lf <= xs[0]:
        i = 0
    elif lf >= xs[-1]:
        i = len(xs) - 2
    else:
        i = max(j for j in range(len(xs) - 1) if xs[j] <= lf)
    t = (lf - xs[i]) / (xs[i + 1] - xs[i])
    if logy:
        return 10 ** (math.log10(ys[i]) + t * (math.log10(ys[i + 1]) - math.log10(ys[i])))
    return ys[i] + t * (ys[i + 1] - ys[i])


def rain_k_coeff(freq_ghz: float) -> float:
    """ITU-R P.838-3 horizontal-pol k coefficient (log-log interpolated, 1-40 GHz)."""
    return _interp_logf(freq_ghz, _P838_K, logy=True)


def rain_alpha_coeff(freq_ghz: float) -> float:
    """ITU-R P.838-3 horizontal-pol alpha exponent (interpolated vs log frequency)."""
    return _interp_logf(freq_ghz, _P838_A, logy=False)


def rain_specific_attenuation_db_km(freq_ghz: float, rain_mm_hr: float) -> float:
    """Specific rain attenuation gamma = k R^alpha (dB/km)."""
    if rain_mm_hr <= 0:
        return 0.0
    return rain_k_coeff(freq_ghz) * rain_mm_hr ** rain_alpha_coeff(freq_ghz)


def rain_total_attenuation_db(freq_ghz: float, rain_mm_hr: float, path_km: float,
                              cell_cap_km: float = 20.0) -> float:
    """Total rain attenuation over an effective path (rain cell extent caps the path)."""
    return rain_specific_attenuation_db_km(freq_ghz, rain_mm_hr) * min(path_km, cell_cap_km)


# ---------------------------------------------------------------- pulse-Doppler radar
def doppler_shift_hz(freq_ghz: float, radial_velocity_ms: float) -> float:
    """Two-way Doppler shift f_d = 2 v_r / lambda."""
    lam = C / (freq_ghz * 1e9)
    return 2 * radial_velocity_ms / lam


def unambiguous_range_km(prf_khz: float) -> float:
    """Maximum unambiguous range R_u = c / (2 PRF)."""
    return C / (2 * prf_khz * 1e3) / 1000.0


def unambiguous_velocity_ms(freq_ghz: float, prf_khz: float) -> float:
    """Unambiguous (+/-) velocity v_u = lambda PRF / 4."""
    lam = C / (freq_ghz * 1e9)
    return lam * (prf_khz * 1e3) / 4.0


def first_blind_speed_ms(freq_ghz: float, prf_khz: float) -> float:
    """First blind speed v_blind = lambda PRF / 2."""
    lam = C / (freq_ghz * 1e9)
    return lam * (prf_khz * 1e3) / 2.0


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
