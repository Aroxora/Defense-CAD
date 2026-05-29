#!/usr/bin/env python3
"""
Emit reference values from osint_cad.analysis.calculators so the browser TypeScript engine
(web/src/app/engine.ts) can be parity-checked against the Python source of truth.

Writes web/public/data/parity.json: a list of {fn, args, expected} scalar cases. The Node
checker web/parity-check.mjs calls the matching TS function and asserts agreement.
"""

import json
import os

from osint_cad.analysis import calculators as c

OUT = os.path.join(os.path.dirname(__file__), "..", "web", "public", "data", "parity.json")


def cases():
    out = []

    def add(fn, args, val):
        out.append({"fn": fn, "args": args, "expected": val})

    add("radarMaxRangeKm", [10000, 40, 10, 1.0, 1e6, 3.0, 13.0, 5.0, 1000],
        c.radar_max_range_km(10000, 40, 10, 1.0, 1e6, 3.0, 13.0, 5.0, 1000))
    add("radarMaxRangeKm", [10000, 40, 10, 0.0002, 1e6, 3.0, 13.0, 5.0, 1000],
        c.radar_max_range_km(10000, 40, 10, 0.0002, 1e6, 3.0, 13.0, 5.0, 1000))
    add("apertureGainDbi", [0.5, 0.7, 9.5], c.aperture_gain_dbi(0.5, 0.7, 9.5))
    add("scanLossDb", [60], c.scan_loss_db(60))
    add("scanLossDb", [30], c.scan_loss_db(30))
    add("fsplDb", [10, 100], c.fspl_db(10, 100))
    add("aspectRcsM2", [0.0002, 0.05, 0.01, 0], c.aspect_rcs_m2(0.0002, 0.05, 0.01, 0))
    add("aspectRcsM2", [0.0002, 0.05, 0.01, 90], c.aspect_rcs_m2(0.0002, 0.05, 0.01, 90))
    add("aspectRcsM2", [0.0002, 0.05, 0.01, 45], c.aspect_rcs_m2(0.0002, 0.05, 0.01, 45))
    add("radarHorizonKm", [30, 10], c.radar_horizon_km(30, 10))
    add("radarHorizonKm", [300, 11000], c.radar_horizon_km(300, 11000))
    add("powerLimitedRangeKm", [300, 1.0, 0.1], c.power_limited_range_km(300, 1.0, 0.1))
    add("friisInterceptRangeKm", [34.5, -74, 14.4, 40], c.friis_intercept_range_km(34.5, -74, 14.4, 40))
    add("processingGainDb", [100e6, 100e-6], c.processing_gain_db(100e6, 100e-6))
    add("jsRatioDb", [30, 100, -60, 10e9, 30], c.js_ratio_db(30, 100, -60, 10e9, 30))
    for f in (3, 10, 15, 22.235, 30, 60, 94):
        add("atmosphericTotalDbKm", [f, 7.5], c.atmospheric_specific_attenuation(f, 7.5)["total_db_km"])
    for (n, b) in [(4, 30), (6, 60), (8, 120), (4, 120)]:
        q = c.geolocation_quality(n, b)
        add("gdop", [n, b], q["gdop"] if q["gdop"] is not None else -1)
        add("opsCepM", [n, b], q["ops_cep_m"] if q["ops_cep_m"] is not None else -1)
    add("killProbSalvo", [0.7, 2], c.kill_prob_salvo(0.7, 2))
    add("killProbSalvo", [0.7, 3], c.kill_prob_salvo(0.7, 3))
    add("exchangeRatio", [0.7, 4.3, 1.5, 2], c.md_exchange_ratio(0.7, 4.3, 1.5, 2)["cost_exchange_ratio"])
    add("expectedLeakers", [0.7, 48, 24, 2], c.md_engage(0.7, 48, 24, 2)["expected_leakers"])
    lcc = c.lifecycle_cost_busd(10000, 4, 15000, 350, 40)
    add("lifecycleCostBusd", [10000, 4, 15000, 350, 40], lcc)
    add("valueIndex", [35, 20, lcc], c.value_index(35, 20, lcc))
    lo, hi = c.value_ci(35, 20, lcc, 0.30)
    add("valueCiLow", [35, 20, lcc, 0.30], lo)
    add("valueCiHigh", [35, 20, lcc, 0.30], hi)
    # EW + CAD-derived
    add("ssjBurnthroughRangeKm", [100, 40, 5, 200, 10, 1, 50, 13], c.ssj_burnthrough_range_km(100, 40, 5, 200, 10, 1, 50, 13))
    add("sojSsjCrossoverKm", [40, 0, 150], c.soj_ssj_crossover_km(40, 0, 150))
    add("albersheimRequiredSnrDb", [0.9, 1e-6, 1], c.albersheim_required_snr_db(0.9, 1e-6, 1))
    add("albersheimRequiredSnrDb", [0.9, 1e-6, 10], c.albersheim_required_snr_db(0.9, 1e-6, 10))
    add("albersheimPdFromSnr", [13.1, 1e-6, 1], c.albersheim_pd_from_snr(13.1, 1e-6, 1))
    add("chaffCloudRcsM2", [1e6, 10], c.chaff_cloud_rcs_m2(1e6, 10))
    add("noiseJammingRangeFactor", [10], c.noise_jamming_range_factor(10))
    add("radarRangeSimpleKm", [1e6, 40, 10, 1.0, 1e-13], c.radar_range_simple_km(1e6, 40, 10, 1.0, 1e-13))
    add("ramReflectionCoefficient", [10], c.ram_reflection_coefficient(10))
    add("ramReflectionCoefficientEff", [10, 15], c.ram_reflection_coefficient_eff(10, 15))
    add("poValidityRatio", [10, 0.68], c.po_validity_ratio(10, 0.68))
    return out


def main():
    payload = {"cases": cases()}
    os.makedirs(os.path.dirname(os.path.normpath(OUT)), exist_ok=True)
    with open(os.path.normpath(OUT), "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"wrote {os.path.normpath(OUT)} ({len(payload['cases'])} cases)")


if __name__ == "__main__":
    main()
