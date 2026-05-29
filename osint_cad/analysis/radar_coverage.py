#!/usr/bin/env python3
"""
Radar Coverage & Horizon CAD (defensive / analytical).

Combines two physics limits that together set a surveillance radar's usable coverage:

  1) RADAR HORIZON (geometry): with standard 4/3-Earth refraction,
        R_horizon_km ~= 4.12 * (sqrt(h_radar_m) + sqrt(h_target_m))
     -- low-altitude targets are hidden below the horizon regardless of power.
  2) POWER-LIMITED DETECTION (radar range equation): detection range scales as RCS^(1/4)
     from a reference (R_ref at RCS_ref).

Effective coverage is the MIN of the two. This exposes the classic "low-altitude gap":
against a sea-skimming/terrain-following target the horizon, not power, is the limit.

Analytical study of sensor coverage -- NOT operational guidance.

Classification: UNCLASSIFIED // CONCEPTUAL // PUBLIC RELEASE
"""

import math
from dataclasses import dataclass


@dataclass
class Radar:
    name: str
    antenna_height_m: float      # height of the radar antenna above the surface
    ref_range_km: float          # detection range against ref_rcs_m2 (power-limited)
    ref_rcs_m2: float


def radar_horizon_km(h_radar_m: float, h_target_m: float) -> float:
    """4/3-Earth radar horizon range (km)."""
    return 4.12 * (math.sqrt(max(0.0, h_radar_m)) + math.sqrt(max(0.0, h_target_m)))


def power_limited_range_km(radar: Radar, target_rcs_m2: float) -> float:
    """Radar-equation detection range (km): R = R_ref * (RCS/RCS_ref)^(1/4)."""
    if target_rcs_m2 <= 0:
        return 0.0
    return radar.ref_range_km * (target_rcs_m2 / radar.ref_rcs_m2) ** 0.25


def effective_range_km(radar: Radar, target_rcs_m2: float, target_alt_m: float) -> dict:
    """Effective detection range = min(power-limited, horizon); flags the binding limit."""
    pwr = power_limited_range_km(radar, target_rcs_m2)
    hor = radar_horizon_km(radar.antenna_height_m, target_alt_m)
    eff = round(min(pwr, hor), 1)
    return {
        "power_limited_km": round(pwr, 1),
        "horizon_km": round(hor, 1),
        "effective_km": eff,
        "limited_by": "horizon" if hor < pwr else "power",
        "coverage_area_km2": round(math.pi * eff * eff),  # consistent with effective_km
    }


def report(radar: Radar, targets: list) -> str:
    """`targets` is a list of (label, rcs_m2, altitude_m)."""
    lines = [
        "=" * 88,
        f"RADAR COVERAGE & HORIZON CAD: {radar.name}",
        f"antenna {radar.antenna_height_m:.0f} m | ref {radar.ref_range_km:.0f} km @ "
        f"{radar.ref_rcs_m2:g} m^2. Defensive coverage study. NOT operational guidance.",
        "=" * 88,
        f"  {'target':26s} {'RCS m^2':>9s} {'alt m':>7s} {'power km':>9s} "
        f"{'horizon km':>11s} {'effective':>10s} {'limit':>8s}",
        "-" * 88,
    ]
    for label, rcs, alt in targets:
        r = effective_range_km(radar, rcs, alt)
        lines.append(f"  {label:26s} {rcs:9g} {alt:7.0f} {r['power_limited_km']:9.1f} "
                     f"{r['horizon_km']:11.1f} {r['effective_km']:10.1f} {r['limited_by']:>8s}")
    lines += ["-" * 88,
              "Where 'limit' = horizon, more radar power does NOT help -- the target is below "
              "the horizon.",
              "That is the low-altitude gap; closing it needs higher/elevated apertures or "
              "airborne/space sensors."]
    return "\n".join(lines)


def _demo():
    # Illustrative shipborne S-band surveillance radar.
    radar = Radar("S-band surveillance (mast ~30 m)", antenna_height_m=30.0,
                  ref_range_km=300.0, ref_rcs_m2=1.0)
    targets = [
        ("high-alt bomber (10 m^2)", 10.0, 11_000),
        ("fighter (1 m^2)", 1.0, 8_000),
        ("sea-skimming ASCM (0.1 m^2)", 0.1, 10),
        ("stealth fighter (0.005 m^2)", 0.005, 9_000),
    ]
    print(report(radar, targets))


if __name__ == "__main__":
    _demo()
