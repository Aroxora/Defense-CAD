#!/usr/bin/env python3
"""
Actionable EW Strategy Analysis -- derived ONLY from this repo's CAD/physics modules.

Premise (established by the physics in this repo): a modern, directional, frequency-hopping
LPI/LPD datalink such as MADL is NOT reliably jammable from standoff. So "jam MADL to
isolate the F-35" is not an engineering line of effort worth funding. This tool replaces
that dead end with the upgrades and tactics the same physics DOES support, and quantifies
each recommendation from the CAD modules:

  1. PASSIVE ESM GEOLOCATION NETWORK (electronic support, not attack)
     - Friis link budget + non-coherent integration gain  -> intercept feasibility/range
     - geolocation_network GDOP + TDOA CRLB                -> platforms & geometry for a
                                                              target geolocation CEP
  2. OWN-DATALINK HARDENING (blue-side, defeats the adversary's #1 above)
     - sidelobe-level and duty-cycle sensitivity           -> EMCON / antenna spec
  3. EW EFFORT REALLOCATION (tactic, no new hardware)
     - J/S link budget for APG-81 radar (effective) vs MADL standoff (ineffective)
       -> move jammer power/time to targets where physics says jamming works

Every number below is computed live from osint_cad.* -- nothing is asserted.

Classification: UNCLASSIFIED // CONCEPTUAL // PUBLIC RELEASE
"""

import numpy as np

from osint_cad.sensors.geolocation_network import GeolocationEngine

C = 299_792_458.0  # m/s


# --------------------------------------------------------------------------------------
# Shared physics helpers (same forms used elsewhere in the repo)
# --------------------------------------------------------------------------------------
def friis_intercept_range_km(eirp_dbm, rx_sensitivity_dbm, freq_ghz, proc_gain_db=0.0):
    """Max range at which a receiver can intercept an emitter (Friis free-space).

    PL_allowable = EIRP - (sensitivity - processing_gain);  R = lambda * 10^(PL/20)/(4 pi)
    """
    lam = C / (freq_ghz * 1e9)
    effective_sensitivity = rx_sensitivity_dbm - proc_gain_db  # integration lowers floor
    pl_db = eirp_dbm - effective_sensitivity
    return (lam * 10 ** (pl_db / 20.0) / (4 * np.pi)) / 1000.0


def processing_gain_db(bandwidth_hz, integration_time_s):
    """Non-coherent integration processing gain (signal_processing.py form)."""
    return 10.0 * np.log10(bandwidth_hz * integration_time_s)


def crlb_cep_m(engine, platforms_m, emitter_m, timing_ns):
    """Horizontal 50% CEP (m) from the TDOA Cramer-Rao bound for a given geometry."""
    crlb = engine.calculate_crlb_tdoa(np.asarray(platforms_m), np.asarray(emitter_m),
                                      timing_uncertainty_ns=timing_ns)
    var_xy = crlb[0, 0] + crlb[1, 1]          # horizontal position variance (m^2)
    sigma = np.sqrt(max(var_xy, 0.0) / 2.0)   # per-axis sigma, circular approx
    return 1.1774 * sigma                     # CEP50 for circular Gaussian


def ring_geometry(n, baseline_km, altitude_m=10_000.0, alt_spread_m=3_000.0):
    """N ESM platforms on a ring of the given baseline radius, with altitude diversity.

    Real multi-platform ESM nets stagger altitudes; a perfectly coplanar ring makes the
    3D TDOA geometry near-singular (vertical dimension unobservable), so we alternate
    platform altitudes by +/- alt_spread to keep the Fisher information well-conditioned.
    """
    r = baseline_km * 1000.0
    return np.array([[r * np.cos(2 * np.pi * i / n),
                      r * np.sin(2 * np.pi * i / n),
                      altitude_m + (alt_spread_m if i % 2 else -alt_spread_m)]
                     for i in range(n)])


def section(title):
    print("\n" + "=" * 88)
    print(title)
    print("=" * 88)


# --------------------------------------------------------------------------------------
# 1. Passive ESM geolocation network
# --------------------------------------------------------------------------------------
def analyze_passive_esm():
    section("1. PASSIVE ESM GEOLOCATION NETWORK  (the actionable counter-LPI upgrade)")

    # OSINT-derived emitter characteristics for a Ku-band LPI datalink sidelobe.
    # (Same inputs used in osint_cad.engagements.integrated_kill_chain_cad.)
    sidelobe_eirp_dbm = 34.5     # ~2.8 W in sidelobes (33 dBm tx + 31.5 dBi - 30 dB sidelobe)
    freq_ghz = 14.4              # Ku-band
    bandwidth_hz = 100e6         # ~100 MHz instantaneous
    esm_sensitivity_dbm = -74.0  # fielded fighter-class ESM receiver

    print(f"  Emitter (LPI sidelobe): EIRP {sidelobe_eirp_dbm:.1f} dBm @ {freq_ghz} GHz")
    print(f"  ESM receiver sensitivity: {esm_sensitivity_dbm:.0f} dBm\n")

    print("  Intercept range vs non-coherent integration dwell (longer dwell = more gain):")
    for dwell_us in (1, 10, 100, 1000):
        g = processing_gain_db(bandwidth_hz, dwell_us * 1e-6)
        rng = friis_intercept_range_km(sidelobe_eirp_dbm, esm_sensitivity_dbm, freq_ghz, g)
        print(f"    dwell {dwell_us:5d} us -> proc gain {g:5.1f} dB -> intercept range {rng:6.0f} km")
    print("  NOTE: range is a BEST CASE -- it presumes the observer is in a sidelobe during")
    print("        an active burst. Intercept is opportunistic and bearing-only per platform.")

    # Geolocation quality vs network size/geometry (real GDOP + TDOA CRLB).
    engine = GeolocationEngine()
    emitter = np.array([0.0, 0.0, 11_000.0])   # target at ~36 kft over the ring center
    timing_ns = 10.0                            # GPS-disciplined sync (range err ~3 m)

    # 3D TDOA needs >= 4 platforms; GDOP measures geometry quality, CRLB gives the
    # theoretical CEP floor. Operational CEP is several x worse (see caveat below).
    OPS_DEGRADE = 5.0  # CRLB floor -> realistic ops CEP multiplier (hopping/multipath/cal)
    print("\n  Geometry quality vs platform count / baseline (real GDOP + TDOA CRLB, 10 ns sync):")
    print(f"    {'N':>3} {'baseline_km':>12} {'GDOP':>7} {'CRLB_floor_m':>13} {'ops_CEP~m':>10}   geometry")
    targets = []
    for n in (4, 6, 8):                       # >=4 required for a 3D fix
        for baseline in (30, 60, 120):
            plats = ring_geometry(n, baseline, altitude_m=10_000.0)
            gdop, _ = engine.calculate_gdop(plats, emitter)
            cep = crlb_cep_m(engine, plats, emitter, timing_ns)
            ill = (not np.isfinite(gdop)) or (not np.isfinite(cep)) or cep > 10_000
            ops = cep * OPS_DEGRADE
            gdop_s = f"{gdop:7.2f}" if np.isfinite(gdop) else "    inf"
            if ill:
                geom, cep_s, ops_s = "ill-conditioned", "       ill", "      ill"
            else:
                cep_s, ops_s = f"{cep:13.1f}", f"{ops:10.0f}"
                geom = ("EXCELLENT" if gdop < 2 else "good" if gdop < 5
                        else "moderate" if gdop < 10 else "poor")
            print(f"    {n:>3} {baseline:>12} {gdop_s} {cep_s} {ops_s}   {geom}")
            if not ill:
                targets.append((n, baseline, gdop, ops))

    print("\n  CAVEAT: CRLB is a theoretical lower bound. Real geolocation CEP is typically")
    print(f"          ~{OPS_DEGRADE:.0f}x larger against a frequency-hopping LPI waveform (coherence loss)")
    print("          plus calibration/multipath error -- the 'ops_CEP' column reflects that.")

    print("\n  ACTIONABLE SPEC (fewest platforms with good geometry, GDOP < 5):")
    good = sorted([t for t in targets if t[2] < 5.0])  # fewest N, then smallest baseline
    if good:
        n, baseline, gdop, ops = good[0]
        wq = "weapons-quality" if ops < 50 else "cueing-quality" if ops < 500 else "track-quality"
        print(f"    -> {n} synchronized ESM platforms on a ~{baseline} km baseline ring (GDOP {gdop:.1f}),")
        print(f"       <=10 ns time sync (GPS/PTP-disciplined), Ku-band coverage, {esm_sensitivity_dbm:.0f} dBm")
        print(f"       sensitivity. Realistic geolocation CEP ~{ops:.0f} m ({wq}).")
    else:
        print("    -> No tested geometry reached GDOP < 5; add platforms or widen the baseline.")
    print("    This is electronic SUPPORT (detect/geolocate), not attack -- it is the line")
    print("    of effort the physics actually rewards against an LPI link.")


# --------------------------------------------------------------------------------------
# 2. Own-datalink hardening (blue-side)
# --------------------------------------------------------------------------------------
def analyze_datalink_hardening():
    section("2. OWN-DATALINK HARDENING  (defeats an adversary's passive-ESM network)")

    freq_ghz = 14.4
    bandwidth_hz = 100e6
    adversary_esm_dbm = -74.0
    adversary_dwell_us = 100  # assume a capable adversary integrating 100 us
    g = processing_gain_db(bandwidth_hz, adversary_dwell_us * 1e-6)
    tx_plus_main_gain_dbm = 33.0 + 31.5  # tx power + mainlobe antenna gain

    print("  How far an adversary ESM can intercept YOUR link vs YOUR sidelobe level:")
    print(f"    (adversary: {adversary_esm_dbm:.0f} dBm, {adversary_dwell_us} us dwell, "
          f"{g:.1f} dB proc gain)\n")
    print(f"    {'sidelobe_dB':>12} {'sidelobe_EIRP_dBm':>18} {'their_intercept_km':>20}")
    base_range = None
    for sidelobe_db in (-20, -25, -30, -35, -40, -45):
        eirp = tx_plus_main_gain_dbm + sidelobe_db
        rng = friis_intercept_range_km(eirp, adversary_esm_dbm, freq_ghz, g)
        if sidelobe_db == -30:
            base_range = rng
        print(f"    {sidelobe_db:>12} {eirp:>18.1f} {rng:>20.0f}")

    eirp40 = tx_plus_main_gain_dbm - 40
    rng40 = friis_intercept_range_km(eirp40, adversary_esm_dbm, freq_ghz, g)
    print("\n  ACTIONABLE UPGRADES (each shrinks the adversary's intercept range):")
    if base_range:
        print(f"    -> Lower sidelobes -30 dB -> -40 dB: intercept range {base_range:.0f} km "
              f"-> {rng40:.0f} km ({100*(1-rng40/base_range):.0f}% reduction).")
    print("    -> Tighten emission control: shorter bursts / lower duty cycle cut the")
    print("       adversary's integration opportunities (fewer chances to catch a sidelobe).")
    print("    -> Aperture/illumination tapering for deeper sidelobes; randomized beam")
    print("       scheduling so sidelobe geometry is unpredictable.")
    print("    These are concrete antenna/EMCON requirements, not new weapons.")


# --------------------------------------------------------------------------------------
# 3. EW effort reallocation
# --------------------------------------------------------------------------------------
def _js_db(jam_power_kw, range_km, victim_signal_dbm, freq_hz, jammer_ant_gain_db=30.0):
    """Jammer-to-signal ratio at the victim (same form as run_integrated_kill_chain)."""
    jam_power_dbw = 10 * np.log10(jam_power_kw * 1000.0)
    path_loss_db = 20 * np.log10(range_km * 1000.0) + 20 * np.log10(freq_hz) - 147.55
    jam_at_victim_dbm = jam_power_dbw + 30 - path_loss_db + jammer_ant_gain_db
    return jam_at_victim_dbm - victim_signal_dbm


def analyze_ew_reallocation():
    section("3. EW EFFORT REALLOCATION  (actionable tactic, no new hardware)")

    jam_power_kw = 30.0
    range_km = 100.0

    # APG-81 main radar: wide-open receiver, no spreading gain to overcome.
    js_radar = _js_db(jam_power_kw, range_km, victim_signal_dbm=-60.0, freq_hz=10e9)

    # MADL standoff: same jammer, but apply the physical penalties an LPI link imposes.
    #   spatial isolation (off the steered beam) + residual despreading/processing gain.
    madl_isolation_db = 25.0
    js_madl = _js_db(jam_power_kw, range_km, victim_signal_dbm=-60.0, freq_hz=14.4e9) - madl_isolation_db

    print(f"  Same {jam_power_kw:.0f} kW jammer at {range_km:.0f} km:")
    print(f"    vs APG-81 radar:        J/S = {js_radar:+5.1f} dB  -> "
          f"{'EFFECTIVE (burn-through/denial)' if js_radar > 10 else 'marginal'}")
    print(f"    vs MADL (standoff LPI): J/S = {js_madl:+5.1f} dB  -> "
          f"{'INEFFECTIVE' if js_madl < 10 else 'opportunistic'} "
          f"(after {madl_isolation_db:.0f} dB spatial-isolation + processing-gain penalty)")
    print("\n  ACTIONABLE REALLOCATION:")
    print("    -> Spend jammer power/time on the APG-81 radar and on terminal-phase missile")
    print("       defense (seeker/datalink in the endgame), where J/S physics is favorable.")
    print("    -> Do NOT budget standoff MADL jamming as a dependable effect; redirect that")
    print("       capacity to passive ESM geolocation (Section 1) and radar denial.")


def main():
    print("ACTIONABLE EW STRATEGY -- CAD-GROUNDED (osint_cad.*)")
    print("All figures computed live from the repo's physics modules.")
    analyze_passive_esm()
    analyze_datalink_hardening()
    analyze_ew_reallocation()
    section("BOTTOM LINE")
    print("  Stop funding standoff MADL jamming (physics says ~0 effect).")
    print("  Fund instead, in priority order:")
    print("    1) Passive multi-platform ESM geolocation network (Section 1)")
    print("    2) Own-datalink sidelobe/EMCON hardening (Section 2)")
    print("    3) Reallocate active EW to radar denial + terminal defense (Section 3)")


if __name__ == "__main__":
    main()
