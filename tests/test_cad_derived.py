#!/usr/bin/env python3
"""Tests for CAD-geometry-derived analytics (RCS profile, envelope, mesh properties)."""

from osint_cad.analysis import cad_derived as cd


def test_rcs_profile_from_mesh():
    p = cd.rcs_aspect_profile("pl15", freq_ghz=10.0, num_points=19, resolution=10)
    assert len(p["azimuth_deg"]) == len(p["rcs_dbsm"]) == 19
    assert p["min_dbsm"] <= p["mean_dbsm"] <= p["max_dbsm"]
    assert p["dynamic_range_db"] > 5  # shaped body: meaningful nose-to-beam swing
    assert p["num_triangles"] > 0


def test_mesh_properties_realistic():
    m = cd.mesh_properties("pl15", resolution=10)
    # PL-15 is ~4 m long, ~0.2 m diameter
    assert 3.0 < m["bbox_length_m"] < 5.0
    assert m["surface_area_m2"] > 0
    assert m["divergence_volume_m3"] > 0
    assert m["characteristic_length_m"] > 0


def test_detection_envelope_tracks_rcs():
    e = cd.detection_envelope("pl15", freq_ghz=10.0, num_points=19, resolution=10)
    assert len(e["detection_range_km"]) == 19
    # beam aspect (high RCS) gives longer detection range than the minimum
    assert e["max_range_km"] > e["min_range_km"] > 0


def test_2d_rcs_pattern_consistent_with_direct_po():
    # The 2D pattern (az x el) must agree with a direct Physical-Optics RCS call at the
    # same aspect — proves the heatmap data is the real PO output, not a fabrication.
    from osint_cad.geometry.cad_geometry import create_pl15_cad_model
    from osint_cad.geometry.cad_rcs_calculator import CADRCSIntegrator, MaterialProperties
    p = cd.rcs_pattern_2d("pl15", freq_ghz=10.0, num_az=25, num_el=9, resolution=12)
    assert len(p["pattern_dbsm"]) == 9 and len(p["pattern_dbsm"][0]) == 25
    assert p["min_dbsm"] <= p["max_dbsm"]
    # el=0 is the middle row (index 4 of -60..60); az=90 deg is index 90/360*24 -> col 6
    integ = CADRCSIntegrator(create_pl15_cad_model())
    integ.build_geometry(resolution=12, material=MaterialProperties.aluminum())
    direct = integ.rcs_calculator.calculate_rcs(90.0, 0.0, 10.0).rcs_dbsm
    assert abs(p["pattern_dbsm"][4][6] - round(direct, 2)) < 0.05


def test_unknown_model_raises():
    import pytest
    with pytest.raises(KeyError):
        cd.rcs_aspect_profile("nonexistent")
