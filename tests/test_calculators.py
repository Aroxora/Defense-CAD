#!/usr/bin/env python3
"""Tests for the canonical pure-function calculators (the web engine's source of truth)."""

import math

from osint_cad.analysis import calculators as c


def test_radar_range_scales_as_quarter_power():
    base = c.radar_max_range_km(10000, 40, 10, 1.0)
    # 16x RCS -> 2x range (16^0.25 = 2)
    assert math.isclose(c.radar_max_range_km(10000, 40, 10, 16.0), base * 2, rel_tol=1e-9)
    assert c.radar_max_range_km(10000, 40, 10, 0) == 0.0


def test_aperture_gain_and_scan_loss():
    g = c.aperture_gain_dbi(0.5, 0.7, 9.5)
    assert 30 < g < 42  # plausible fighter AESA gain
    assert c.scan_loss_db(0) == 0.0
    assert abs(c.scan_loss_db(60) + 1.5) < 1e-9  # -1.5 dB at 60 deg


def test_atmospheric_p676_anchors():
    assert 0.005 < c.atmospheric_specific_attenuation(15)["total_db_km"] < 0.1
    assert 10 < c.atmospheric_specific_attenuation(60)["total_db_km"] < 20


def test_aspect_rcs_monotonic_nose_to_beam():
    # frontal lowest, beam highest -> RCS rises from 0 to 90 deg, symmetric
    nose = c.aspect_rcs_m2(0.0002, 0.05, 0.01, 0)
    beam = c.aspect_rcs_m2(0.0002, 0.05, 0.01, 90)
    assert beam > nose
    assert abs(c.aspect_rcs_m2(0.0002, 0.05, 0.01, 45) - c.aspect_rcs_m2(0.0002, 0.05, 0.01, 315)) < 1e-9


def test_geolocation_requires_four_platforms():
    assert c.geolocation_quality(3, 30)["ill_conditioned"] is True
    q = c.geolocation_quality(4, 30)
    assert q["ill_conditioned"] is False and q["gdop"] is not None and q["ops_cep_m"] > 0


def test_missile_defense_and_value_consistency():
    assert abs(c.kill_prob_salvo(0.7, 2) - 0.91) < 1e-9
    assert c.md_exchange_ratio(0.7, 4.3, 1.5, 2)["cost_exchange_ratio"] > 1  # unfavorable
    lcc = c.lifecycle_cost_busd(10000, 4, 15000, 350, 40)
    assert abs(lcc - 111.0) < 1e-6
    lo, hi = c.value_ci(35, 20, lcc, 0.30)
    assert lo <= c.value_index(35, 20, lcc) <= hi
