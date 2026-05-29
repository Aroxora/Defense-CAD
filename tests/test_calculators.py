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


def test_ew_calculators():
    # Albersheim returns the canonical ~13.1 dB at Pd=0.9, Pfa=1e-6, N=1
    assert abs(c.albersheim_required_snr_db(0.9, 1e-6, 1) - 13.1) < 0.2
    # integrating pulses lowers the requirement
    assert c.albersheim_required_snr_db(0.9, 1e-6, 10) < c.albersheim_required_snr_db(0.9, 1e-6, 1)
    # inverse round-trips
    snr = c.albersheim_required_snr_db(0.85, 1e-6, 1)
    assert abs(c.albersheim_pd_from_snr(snr, 1e-6, 1) - 0.85) < 0.01
    # burn-through shrinks as jammer power rises
    assert c.ssj_burnthrough_range_km(100, 40, 5, 400, 10, 1, 50, 13) < c.ssj_burnthrough_range_km(100, 40, 5, 100, 10, 1, 50, 13)
    # chaff RCS scales with N and lambda^2
    assert abs(c.chaff_cloud_rcs_m2(2e6, 10) - 2 * c.chaff_cloud_rcs_m2(1e6, 10)) < 1e-9
    # noise-jamming fourth-root law: 10 dB J/N -> ~0.55 range retained
    assert abs(c.noise_jamming_range_factor(10) - 0.5493) < 1e-3
    assert c.noise_jamming_range_factor(0) == 2 ** -0.25 or abs(c.noise_jamming_range_factor(0) - 0.8409) < 1e-3


def test_cad_material_helpers():
    assert abs(c.ram_reflection_coefficient(10) - 0.1) < 1e-9
    assert c.ram_reflection_coefficient_eff(10, 15) < c.ram_reflection_coefficient(10)  # mild f-scaling
    assert abs(c.po_validity_ratio(10, 0.3) - 0.3 / (c.C / 10e9)) < 1e-6
    # radar_range_simple scales as sigma^0.25
    import math as _m
    base = c.radar_range_simple_km(1e6, 40, 10, 1.0, 1e-13)
    assert _m.isclose(c.radar_range_simple_km(1e6, 40, 10, 16.0, 1e-13), base * 2, rel_tol=1e-9)


def test_cross_domain_calculators():
    # comms: a 2.4 m Ku dish is ~47 dBi; bigger dish + closer range -> more margin
    assert 44 < c.parabolic_gain_dbi(2.4, 0.6, 12) < 50
    assert c.link_margin_db(10, 30, 4.0, 0.6, 12, 1000, 3, 290, 10, 7) > c.link_margin_db(10, 30, 2.4, 0.6, 12, 1000, 3, 290, 10, 7)
    # PNT: UERE is the RSS; horizontal error scales with HDOP
    u = c.gnss_uere_m(4, 0.7, 2.1, 1.4, 0.5)
    assert abs(u - (4**2 + 0.7**2 + 2.1**2 + 1.4**2 + 0.5**2) ** 0.5) < 1e-9
    assert abs(c.gnss_horizontal_error_m(u, 2) - 2 * u) < 1e-9
    # IRST: more haze (higher extinction) shortens detection range
    far = c.irst_detection_range_km(330, 280, 2, 0.9, 0.35, 0.7, 0.05, 10e-12)
    near = c.irst_detection_range_km(330, 280, 2, 0.9, 0.35, 0.7, 0.5, 10e-12)
    assert far > near > 0
    # sonar: at the detection range, TL ~= figure of merit
    fom = c.sonar_figure_of_merit_db(130, 65, 20, 5)
    rng = c.sonar_detection_range_km(130, 65, 20, 5, 1)
    assert abs(c.sonar_tl_spherical_db(rng, 1) - fom) < 0.1
    # orbit: LEO 550 km -> ~7.6 km/s, ~95 min; higher orbit slower & longer period
    assert 7.4 < c.orbital_velocity_kms(550) < 7.7
    assert 90 < c.orbital_period_min(550) < 100
    assert c.orbital_period_min(20000) > c.orbital_period_min(550)
    # ballistics: 45 deg maximizes range; symmetry about 45
    assert c.projectile_range_km(800, 45) >= c.projectile_range_km(800, 30)
    assert abs(c.projectile_range_km(800, 30) - c.projectile_range_km(800, 60)) < 1e-9


def test_missile_defense_and_value_consistency():
    assert abs(c.kill_prob_salvo(0.7, 2) - 0.91) < 1e-9
    assert c.md_exchange_ratio(0.7, 4.3, 1.5, 2)["cost_exchange_ratio"] > 1  # unfavorable
    lcc = c.lifecycle_cost_busd(10000, 4, 15000, 350, 40)
    assert abs(lcc - 111.0) < 1e-6
    lo, hi = c.value_ci(35, 20, lcc, 0.30)
    assert lo <= c.value_index(35, 20, lcc) <= hi
