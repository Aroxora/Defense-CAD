#!/usr/bin/env python3
"""
Math DERIVED FROM THE CAD GEOMETRY.

Uses the existing Physical-Optics RCS calculator and triangle-mesh geometry to compute
real, geometry-grounded quantities: the monostatic RCS profile over an azimuth sweep (with
statistics), the aspect-dependent detection-range envelope (RCS profile + radar range
equation), and mesh geometric properties (wetted area, bounding box, divergence-theorem
enclosed volume, characteristic length).

These are conceptual OSINT analyses for study -- the underlying RCS is a Physical-Optics
approximation valid only for size >> wavelength (see the PO-validity calculator).

Classification: UNCLASSIFIED // CONCEPTUAL // PUBLIC RELEASE
"""

from typing import Callable, Dict

import numpy as np

from osint_cad.geometry.cad_geometry import create_pl15_cad_model, create_aim120_cad_model
from osint_cad.geometry.cad_rcs_calculator import CADRCSIntegrator, MaterialProperties
from osint_cad.analysis.calculators import radar_range_simple_km

# Built-in parametric CAD models available for derived analysis.
MODELS: Dict[str, Callable] = {
    "pl15": create_pl15_cad_model,
    "aim120": create_aim120_cad_model,
}


def _build(model_name: str, resolution: int, material: MaterialProperties = None):
    if model_name not in MODELS:
        raise KeyError(f"unknown model {model_name!r}; choose from {list(MODELS)}")
    integ = CADRCSIntegrator(MODELS[model_name]())
    integ.build_geometry(resolution=resolution, material=material or MaterialProperties.aluminum())
    return integ


def rcs_aspect_profile(model_name: str = "pl15", freq_ghz: float = 10.0,
                       num_points: int = 37, resolution: int = 16) -> Dict:
    """Monostatic RCS over a 0-360 deg azimuth sweep + statistics, computed from the mesh."""
    calc = _build(model_name, resolution).rcs_calculator
    sweep = calc.calculate_rcs_sweep(azimuth_range=(0, 360), elevation=0,
                                     num_points=num_points, frequency_ghz=freq_ghz)
    dbsm = sweep.rcs_values_dbsm
    stats = dbsm[:-1]  # drop the duplicated 360deg == 0deg endpoint so it isn't double-counted
    return {
        "model": model_name, "frequency_ghz": freq_ghz, "num_triangles": calc.num_triangles,
        "resolution": resolution,
        "azimuth_deg": [round(float(a), 1) for a in sweep.azimuth_angles],
        "rcs_dbsm": [round(float(x), 2) for x in dbsm],
        "min_dbsm": round(float(np.min(stats)), 2),
        "max_dbsm": round(float(np.max(stats)), 2),
        "mean_dbsm": round(float(np.mean(stats)), 2),
        "median_dbsm": round(float(np.median(stats)), 2),
        "dynamic_range_db": round(float(np.max(stats) - np.min(stats)), 2),
    }


def detection_envelope(model_name: str = "pl15", freq_ghz: float = 10.0,
                       pt_w: float = 1e6, gain_dbi: float = 40.0, pmin_w: float = 1e-13,
                       num_points: int = 37, resolution: int = 16) -> Dict:
    """Per-aspect detection range: combine each swept RCS with the radar range equation."""
    calc = _build(model_name, resolution).rcs_calculator
    sweep = calc.calculate_rcs_sweep(azimuth_range=(0, 360), elevation=0,
                                     num_points=num_points, frequency_ghz=freq_ghz)
    ranges = [round(radar_range_simple_km(pt_w, gain_dbi, freq_ghz, float(s), pmin_w), 1)
              for s in sweep.rcs_values_m2]
    return {
        "model": model_name, "frequency_ghz": freq_ghz,
        "azimuth_deg": [round(float(a), 1) for a in sweep.azimuth_angles],
        "detection_range_km": ranges,
        "min_range_km": min(ranges), "max_range_km": max(ranges),
    }


def mesh_properties(model_name: str = "pl15", resolution: int = 16) -> Dict:
    """Wetted area, bounding box, divergence-theorem enclosed volume, characteristic length."""
    calc = _build(model_name, resolution).rcs_calculator
    mesh = calc.mesh
    bb = mesh.bounding_box
    length = bb.max_point.x - bb.min_point.x
    width = bb.max_point.y - bb.min_point.y
    height = bb.max_point.z - bb.min_point.z
    # divergence theorem: V = (1/3) sum A_i (C_i . n_hat_i)
    a = np.asarray(calc.triangle_areas)
    cdotn = np.einsum("ij,ij->i", np.asarray(calc.triangle_centroids),
                      np.asarray(calc.triangle_normals))
    div_volume = float((1.0 / 3.0) * np.sum(a * cdotn))
    char_len = float((abs(length) * abs(width) * abs(height)) ** (1.0 / 3.0))
    return {
        "model": model_name, "num_triangles": calc.num_triangles, "resolution": resolution,
        "surface_area_m2": round(float(mesh.surface_area), 4),
        "bbox_length_m": round(float(length), 3),
        "bbox_width_m": round(float(width), 3),
        "bbox_height_m": round(float(height), 3),
        # Divergence-theorem volume is APPROXIMATE: the tessellated meshes are not perfectly
        # watertight (open fin/control surfaces), so this is a coarse closed-volume estimate.
        "divergence_volume_m3": round(abs(div_volume), 5),
        "volume_note": "approximate (mesh not fully watertight)",
        "characteristic_length_m": round(char_len, 3),
    }


def rcs_pattern_2d(model_name: str = "pl15", freq_ghz: float = 10.0, num_az: int = 25,
                   num_el: int = 9, resolution: int = 12) -> Dict:
    """Full 2D monostatic RCS map (dBsm) over an azimuth x elevation grid, from the mesh."""
    calc = _build(model_name, resolution).rcs_calculator
    grid = calc.calculate_2d_rcs_pattern(azimuth_range=(0, 360), elevation_range=(-60, 60),
                                         num_azimuth=num_az, num_elevation=num_el,
                                         frequency_ghz=freq_ghz)  # (num_el, num_az) dBsm
    import numpy as np
    rows = [[round(float(v), 2) for v in row] for row in grid]
    az = [round(a, 1) for a in np.linspace(0, 360, num_az).tolist()]
    el = [round(e, 1) for e in np.linspace(-60, 60, num_el).tolist()]
    flat = [v for row in rows for v in row]
    return {"model": model_name, "frequency_ghz": freq_ghz,
            "azimuth_deg": az, "elevation_deg": el, "pattern_dbsm": rows,
            "min_dbsm": round(min(flat), 2), "max_dbsm": round(max(flat), 2)}


def analyze(model_name: str = "pl15", freq_ghz: float = 10.0, resolution: int = 16) -> Dict:
    """Bundle the RCS profile, detection envelope, mesh properties, and 2D RCS map."""
    return {
        "rcs_profile": rcs_aspect_profile(model_name, freq_ghz, resolution=resolution),
        "detection_envelope": detection_envelope(model_name, freq_ghz, resolution=resolution),
        "mesh_properties": mesh_properties(model_name, resolution=resolution),
        "rcs_pattern": rcs_pattern_2d(model_name, freq_ghz, resolution=resolution),
    }


def report(model_name: str = "pl15", freq_ghz: float = 10.0) -> str:
    p = rcs_aspect_profile(model_name, freq_ghz)
    m = mesh_properties(model_name)
    return "\n".join([
        "=" * 80,
        f"CAD-DERIVED ANALYSIS: {model_name}  (Physical-Optics, {freq_ghz} GHz)",
        "Conceptual OSINT; PO RCS valid for size >> wavelength. NOT operational guidance.",
        "=" * 80,
        f"  Mesh: {m['num_triangles']} triangles | wetted area {m['surface_area_m2']} m^2 | "
        f"bbox {m['bbox_length_m']}x{m['bbox_width_m']}x{m['bbox_height_m']} m",
        f"  Enclosed volume (divergence): {m['divergence_volume_m3']} m^3 | "
        f"characteristic length {m['characteristic_length_m']} m",
        f"  RCS over 0-360 deg: min {p['min_dbsm']} / mean {p['mean_dbsm']} / "
        f"median {p['median_dbsm']} / max {p['max_dbsm']} dBsm "
        f"(dynamic range {p['dynamic_range_db']} dB)",
        "=" * 80,
    ])


if __name__ == "__main__":
    for name in MODELS:
        print(report(name))
        print()
