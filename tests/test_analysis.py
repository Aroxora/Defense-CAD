#!/usr/bin/env python3
"""Tests for the standalone analytical CAD tools."""

import math

from osint_cad.analysis import missile_defense as md
from osint_cad.analysis import radar_coverage as rc


def test_salvo_kill_probability():
    assert md.kill_prob_salvo(0.7, 1) == 0.7
    # two independent 0.7 shots -> 1 - 0.3^2 = 0.91
    assert abs(md.kill_prob_salvo(0.7, 2) - 0.91) < 1e-9
    assert md.kill_prob_salvo(0.7, 0) == 0.0


def test_engagement_magazine_exhaustion_and_leakers():
    interceptor = md.Interceptor("I", pk_single_shot=0.7, unit_cost_musd=4.0, magazine=10)
    threat = md.Threat("T", count=20, unit_cost_musd=1.0)
    # 2 shots/target, magazine 10 -> only 5 targets engageable, 15 unengaged leak entirely
    e = md.engage(interceptor, threat, shots_per_target=2)
    assert e["engageable_targets"] == 5
    assert e["magazine_exhausted"] is True
    # leakers >= the 15 unengaged
    assert e["expected_leakers"] >= 15


def test_exchange_ratio_direction():
    cheap_threat = md.Threat("cheap", count=10, unit_cost_musd=0.5)
    pricey_threat = md.Threat("pricey", count=10, unit_cost_musd=50.0)
    interceptor = md.Interceptor("I", pk_single_shot=0.7, unit_cost_musd=4.0, magazine=100)
    x_cheap = md.exchange_ratio(interceptor, cheap_threat, 2)
    x_pricey = md.exchange_ratio(interceptor, pricey_threat, 2)
    # defending a cheap threat is a worse cost trade than defending an expensive one
    assert x_cheap["cost_exchange_ratio"] > x_pricey["cost_exchange_ratio"]
    assert x_pricey["favorable_for_defender"] is True


def test_radar_horizon_and_low_altitude_gap():
    radar = rc.Radar("R", antenna_height_m=30.0, ref_range_km=300.0, ref_rcs_m2=1.0)
    # horizon grows with target altitude
    assert rc.radar_horizon_km(30, 10000) > rc.radar_horizon_km(30, 10)
    # power scales as RCS^0.25
    assert abs(rc.power_limited_range_km(radar, 16.0) - 300.0 * 2.0) < 1e-6  # 16^0.25 = 2
    # sea-skimmer is horizon-limited, not power-limited
    r = rc.effective_range_km(radar, target_rcs_m2=0.1, target_alt_m=10)
    assert r["limited_by"] == "horizon"
    assert r["effective_km"] == r["horizon_km"]
    assert r["coverage_area_km2"] == round(math.pi * r["effective_km"] ** 2)
