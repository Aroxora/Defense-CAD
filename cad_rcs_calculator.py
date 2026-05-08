#!/usr/bin/env python3
"""
CAD-Driven RCS Calculator

Uses parametric 3D geometry from CAD models to calculate Radar Cross Section
using Physical Optics (PO) approximation. Enables sensitivity analysis of
geometric parameters on RCS.

Key Features:
- Physical Optics RCS calculation from triangle mesh
- Aspect-dependent RCS sweeps
- Frequency-dependent calculations
- Material properties (RAM, dielectric)
- Parametric sensitivity analysis
- Integration with existing RCS models for validation

Physical Optics Approximation:
RCS = (4*pi/lambda^2) * |sum(A_n * exp(j*2k*r_n) * (n_hat . k_hat))|^2

where:
- A_n = triangle area
- r_n = triangle centroid position
- n_hat = surface normal
- k_hat = incident wave direction
- k = 2*pi/lambda

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Callable
from enum import Enum

from cad_geometry import (
    TriangleMesh, Triangle, Point3D, Vector3D,
    MissileCADModel, CADGeometryResult,
    create_pl15_cad_model, create_aim120_cad_model
)


class MaterialType(Enum):
    """Surface material types for RCS calculation"""
    PERFECT_CONDUCTOR = "pec"
    ALUMINUM = "aluminum"
    COMPOSITE = "composite"
    RAM_COATING = "ram"  # Radar Absorbing Material
    DIELECTRIC = "dielectric"


@dataclass
class MaterialProperties:
    """Electromagnetic material properties"""
    name: str
    material_type: MaterialType
    reflection_coefficient: float  # 0-1, 1 = perfect reflector
    frequency_dependent: bool = False
    frequency_factor: float = 0.0  # For frequency-dependent materials

    @classmethod
    def perfect_conductor(cls) -> 'MaterialProperties':
        return cls("Perfect Conductor", MaterialType.PERFECT_CONDUCTOR, 1.0)

    @classmethod
    def aluminum(cls) -> 'MaterialProperties':
        return cls("Aluminum", MaterialType.ALUMINUM, 0.95)

    @classmethod
    def composite(cls) -> 'MaterialProperties':
        return cls("Composite", MaterialType.COMPOSITE, 0.85)

    @classmethod
    def ram_coating(cls, absorption_db: float = 10) -> 'MaterialProperties':
        """RAM with specified absorption in dB"""
        reflection = 10 ** (-absorption_db / 10)
        return cls("RAM Coating", MaterialType.RAM_COATING, reflection,
                   frequency_dependent=True, frequency_factor=0.1)


@dataclass
class RCSCalculationResult:
    """Result of RCS calculation"""
    rcs_m2: float
    rcs_dbsm: float
    azimuth_deg: float
    elevation_deg: float
    frequency_ghz: float
    num_triangles: int
    visible_triangles: int
    method: str = "Physical Optics"
    confidence: float = 0.6


@dataclass
class RCSSweepResult:
    """Result of RCS sweep over angles"""
    azimuth_angles: np.ndarray
    elevation_angles: np.ndarray
    rcs_values_m2: np.ndarray
    rcs_values_dbsm: np.ndarray
    frequency_ghz: float
    min_rcs_dbsm: float
    max_rcs_dbsm: float
    mean_rcs_dbsm: float


class PhysicalOpticsRCSCalculator:
    """
    Physical Optics RCS calculator using triangle mesh geometry.

    Uses the Physical Optics approximation which is valid when:
    - Object size >> wavelength
    - Smooth surfaces (no sharp edges/corners)
    - Angles not too close to grazing incidence

    For typical X-band radar (10 GHz, lambda = 3 cm), valid for objects > ~10 cm.
    """

    SPEED_OF_LIGHT = 299792458.0  # m/s

    def __init__(self, mesh: TriangleMesh,
                 material: MaterialProperties = None):
        """
        Initialize calculator with mesh and material.

        Args:
            mesh: Triangle mesh of the target
            material: Surface material properties (default: aluminum)
        """
        self.mesh = mesh
        self.material = material or MaterialProperties.aluminum()

        # Pre-compute triangle properties
        self._precompute_triangle_data()

    def _precompute_triangle_data(self):
        """Pre-compute triangle areas, centroids, and normals"""
        self.triangle_areas = np.array([t.area for t in self.mesh.triangles])
        self.triangle_centroids = np.array([
            [t.centroid.x, t.centroid.y, t.centroid.z]
            for t in self.mesh.triangles
        ])
        self.triangle_normals = np.array([
            [t.normal.dx, t.normal.dy, t.normal.dz]
            for t in self.mesh.triangles
        ])
        self.num_triangles = len(self.mesh.triangles)

    def calculate_rcs(self,
                      azimuth_deg: float,
                      elevation_deg: float,
                      frequency_ghz: float = 10.0) -> RCSCalculationResult:
        """
        Calculate RCS at given viewing angle and frequency.

        Args:
            azimuth_deg: Azimuth angle (0° = nose-on, 90° = beam, 180° = tail)
            elevation_deg: Elevation angle (0° = level, +90° = top view)
            frequency_ghz: Radar frequency in GHz

        Returns:
            RCSCalculationResult with RCS value and metadata
        """
        # Calculate wavelength
        wavelength = self.SPEED_OF_LIGHT / (frequency_ghz * 1e9)
        k = 2 * np.pi / wavelength

        # Incident wave direction (from radar toward target)
        az_rad = np.radians(azimuth_deg)
        el_rad = np.radians(elevation_deg)

        # Wave vector direction (toward target)
        k_hat = np.array([
            np.cos(el_rad) * np.cos(az_rad),
            np.cos(el_rad) * np.sin(az_rad),
            np.sin(el_rad)
        ])

        # Physical Optics integration
        # RCS = (4*pi/lambda^2) * |sum(A_n * Gamma * (n.k) * exp(j*2k*r.k))|^2
        # Only sum over illuminated triangles (n.k > 0)

        complex_sum = 0j
        visible_count = 0

        for i in range(self.num_triangles):
            n_hat = self.triangle_normals[i]
            n_dot_k = np.dot(n_hat, k_hat)

            # Only include front-facing (illuminated) triangles
            if n_dot_k > 0:
                visible_count += 1

                A = self.triangle_areas[i]
                r = self.triangle_centroids[i]

                # Phase term
                phase = 2 * k * np.dot(r, k_hat)

                # Reflection coefficient (material dependent)
                gamma = self.material.reflection_coefficient
                if self.material.frequency_dependent:
                    # Frequency scaling for RAM
                    gamma *= (1 - self.material.frequency_factor *
                              np.log10(frequency_ghz / 10.0))

                # Add contribution
                complex_sum += A * gamma * n_dot_k * np.exp(1j * phase)

        # Calculate RCS
        if visible_count > 0:
            rcs = (4 * np.pi / wavelength**2) * np.abs(complex_sum)**2
        else:
            rcs = 1e-10  # Very small RCS if nothing visible

        # Apply material correction
        rcs *= self.material.reflection_coefficient**2

        # Convert to dBsm
        rcs_dbsm = 10 * np.log10(max(rcs, 1e-10))

        return RCSCalculationResult(
            rcs_m2=rcs,
            rcs_dbsm=rcs_dbsm,
            azimuth_deg=azimuth_deg,
            elevation_deg=elevation_deg,
            frequency_ghz=frequency_ghz,
            num_triangles=self.num_triangles,
            visible_triangles=visible_count,
            confidence=0.6 if visible_count > 10 else 0.3
        )

    def calculate_rcs_sweep(self,
                            azimuth_range: Tuple[float, float] = (0, 180),
                            elevation: float = 0,
                            num_points: int = 37,
                            frequency_ghz: float = 10.0) -> RCSSweepResult:
        """
        Calculate RCS over a range of azimuth angles.

        Args:
            azimuth_range: (start, end) azimuth angles in degrees
            elevation: Fixed elevation angle
            num_points: Number of azimuth points
            frequency_ghz: Radar frequency

        Returns:
            RCSSweepResult with arrays of RCS values
        """
        azimuths = np.linspace(azimuth_range[0], azimuth_range[1], num_points)
        rcs_m2 = np.zeros(num_points)
        rcs_dbsm = np.zeros(num_points)

        for i, az in enumerate(azimuths):
            result = self.calculate_rcs(az, elevation, frequency_ghz)
            rcs_m2[i] = result.rcs_m2
            rcs_dbsm[i] = result.rcs_dbsm

        return RCSSweepResult(
            azimuth_angles=azimuths,
            elevation_angles=np.full(num_points, elevation),
            rcs_values_m2=rcs_m2,
            rcs_values_dbsm=rcs_dbsm,
            frequency_ghz=frequency_ghz,
            min_rcs_dbsm=np.min(rcs_dbsm),
            max_rcs_dbsm=np.max(rcs_dbsm),
            mean_rcs_dbsm=np.mean(rcs_dbsm)
        )

    def calculate_2d_rcs_pattern(self,
                                 azimuth_range: Tuple[float, float] = (0, 360),
                                 elevation_range: Tuple[float, float] = (-90, 90),
                                 num_azimuth: int = 37,
                                 num_elevation: int = 19,
                                 frequency_ghz: float = 10.0) -> np.ndarray:
        """
        Calculate 2D RCS pattern over azimuth and elevation.

        Returns:
            2D array of RCS in dBsm, shape (num_elevation, num_azimuth)
        """
        azimuths = np.linspace(azimuth_range[0], azimuth_range[1], num_azimuth)
        elevations = np.linspace(elevation_range[0], elevation_range[1], num_elevation)

        rcs_pattern = np.zeros((num_elevation, num_azimuth))

        for i, el in enumerate(elevations):
            for j, az in enumerate(azimuths):
                result = self.calculate_rcs(az, el, frequency_ghz)
                rcs_pattern[i, j] = result.rcs_dbsm

        return rcs_pattern


class CADRCSIntegrator:
    """
    Integrates CAD geometry with RCS calculations for parametric analysis.

    Enables:
    - Parametric RCS sensitivity analysis
    - Design optimization for RCS reduction
    - Comparison with empirical RCS models
    - Uncertainty quantification
    """

    def __init__(self, cad_model: MissileCADModel):
        """
        Initialize with a parametric CAD model.

        Args:
            cad_model: Parametric missile or aircraft CAD model
        """
        self.cad_model = cad_model
        self.geometry = None
        self.rcs_calculator = None

    def build_geometry(self, resolution: int = 32,
                       material: MaterialProperties = None) -> CADGeometryResult:
        """
        Build geometry and initialize RCS calculator.

        Args:
            resolution: Mesh resolution (higher = more accurate, slower)
            material: Surface material properties

        Returns:
            CADGeometryResult
        """
        self.geometry = self.cad_model.generate_geometry(resolution)
        self.rcs_calculator = PhysicalOpticsRCSCalculator(
            self.geometry.mesh,
            material or MaterialProperties.aluminum()
        )
        return self.geometry

    def calculate_rcs_pattern(self,
                              frequency_ghz: float = 10.0) -> RCSSweepResult:
        """
        Calculate RCS pattern for the model.

        Args:
            frequency_ghz: Radar frequency

        Returns:
            RCSSweepResult with azimuth sweep
        """
        if self.rcs_calculator is None:
            self.build_geometry()

        return self.rcs_calculator.calculate_rcs_sweep(
            azimuth_range=(0, 180),
            elevation=0,
            num_points=37,
            frequency_ghz=frequency_ghz
        )

    def sensitivity_analysis(self,
                             parameter: str,
                             values: List[float],
                             frequency_ghz: float = 10.0) -> Dict[str, List[float]]:
        """
        Perform sensitivity analysis on a geometric parameter.

        Args:
            parameter: Parameter name to vary (e.g., "nose_length", "body_diameter")
            values: List of parameter values to test
            frequency_ghz: Radar frequency

        Returns:
            Dictionary with parameter values and corresponding RCS metrics
        """
        results = {
            "parameter_values": values,
            "frontal_rcs_dbsm": [],
            "beam_rcs_dbsm": [],
            "mean_rcs_dbsm": [],
            "valid": []
        }

        original_value = getattr(self.cad_model, parameter)

        for value in values:
            try:
                # Update parameter
                setattr(self.cad_model, parameter, value)

                # Rebuild geometry
                self.build_geometry(resolution=16)

                # Calculate RCS at key aspects
                frontal = self.rcs_calculator.calculate_rcs(0, 0, frequency_ghz)
                beam = self.rcs_calculator.calculate_rcs(90, 0, frequency_ghz)
                sweep = self.calculate_rcs_pattern(frequency_ghz)

                results["frontal_rcs_dbsm"].append(frontal.rcs_dbsm)
                results["beam_rcs_dbsm"].append(beam.rcs_dbsm)
                results["mean_rcs_dbsm"].append(sweep.mean_rcs_dbsm)
                results["valid"].append(True)

            except Exception:
                results["frontal_rcs_dbsm"].append(None)
                results["beam_rcs_dbsm"].append(None)
                results["mean_rcs_dbsm"].append(None)
                results["valid"].append(False)

        # Restore original value
        setattr(self.cad_model, parameter, original_value)
        self.build_geometry(resolution=16)

        return results

    def compare_with_empirical(self,
                               empirical_rcs_function: Callable,
                               frequency_ghz: float = 10.0) -> Dict[str, float]:
        """
        Compare CAD-calculated RCS with empirical model.

        Args:
            empirical_rcs_function: Function that takes (azimuth, elevation) and returns RCS
            frequency_ghz: Radar frequency

        Returns:
            Comparison metrics
        """
        if self.rcs_calculator is None:
            self.build_geometry()

        azimuths = np.linspace(0, 180, 19)
        cad_rcs = []
        empirical_rcs = []

        for az in azimuths:
            # CAD-based RCS
            cad_result = self.rcs_calculator.calculate_rcs(az, 0, frequency_ghz)
            cad_rcs.append(cad_result.rcs_dbsm)

            # Empirical RCS
            emp_result = empirical_rcs_function(az, 0)
            if hasattr(emp_result, 'rcs_dbsm'):
                empirical_rcs.append(emp_result.rcs_dbsm)
            else:
                empirical_rcs.append(emp_result)

        cad_rcs = np.array(cad_rcs)
        empirical_rcs = np.array(empirical_rcs)

        # Calculate comparison metrics
        diff = cad_rcs - empirical_rcs
        rmse = np.sqrt(np.mean(diff**2))
        max_diff = np.max(np.abs(diff))
        correlation = np.corrcoef(cad_rcs, empirical_rcs)[0, 1]

        return {
            "rmse_db": rmse,
            "max_diff_db": max_diff,
            "correlation": correlation,
            "cad_mean_dbsm": np.mean(cad_rcs),
            "empirical_mean_dbsm": np.mean(empirical_rcs),
            "bias_db": np.mean(diff)
        }

    def generate_rcs_report(self, frequency_ghz: float = 10.0) -> str:
        """Generate comprehensive RCS report"""
        if self.rcs_calculator is None:
            self.build_geometry()

        lines = []
        lines.append("=" * 70)
        lines.append(f"CAD-BASED RCS ANALYSIS: {self.cad_model.name}")
        lines.append("=" * 70)
        lines.append(f"Frequency: {frequency_ghz} GHz")
        lines.append(f"Wavelength: {299.792 / frequency_ghz:.3f} mm")
        lines.append("")

        # Geometry summary
        lines.append("GEOMETRY SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Length: {self.geometry.bounding_box.length:.3f} m")
        lines.append(f"Body Diameter: {self.cad_model.body_diameter:.3f} m")
        lines.append(f"Total Volume: {self.geometry.total_volume:.6f} m³")
        lines.append(f"Surface Area: {self.geometry.total_surface_area:.4f} m²")
        lines.append(f"Mesh Triangles: {self.rcs_calculator.num_triangles}")
        lines.append("")

        # Key RCS values
        lines.append("KEY RCS VALUES")
        lines.append("-" * 70)

        aspects = [
            ("Nose-on (0°)", 0, 0),
            ("30° off-nose", 30, 0),
            ("45° oblique", 45, 0),
            ("Beam (90°)", 90, 0),
            ("Rear quarter (135°)", 135, 0),
            ("Tail-on (180°)", 180, 0),
            ("Top view (0°, +45°)", 0, 45),
            ("Bottom view (0°, -45°)", 0, -45),
        ]

        for name, az, el in aspects:
            result = self.rcs_calculator.calculate_rcs(az, el, frequency_ghz)
            lines.append(f"  {name:25s}: {result.rcs_dbsm:+6.1f} dBsm "
                        f"({result.rcs_m2:.6f} m²)")

        # RCS statistics
        sweep = self.calculate_rcs_pattern(frequency_ghz)
        lines.append("")
        lines.append("RCS STATISTICS (0-180° azimuth sweep)")
        lines.append("-" * 70)
        lines.append(f"  Minimum RCS: {sweep.min_rcs_dbsm:+6.1f} dBsm")
        lines.append(f"  Maximum RCS: {sweep.max_rcs_dbsm:+6.1f} dBsm")
        lines.append(f"  Mean RCS: {sweep.mean_rcs_dbsm:+6.1f} dBsm")
        lines.append(f"  Dynamic Range: {sweep.max_rcs_dbsm - sweep.min_rcs_dbsm:.1f} dB")

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)


class RCSComparisonFramework:
    """
    Framework for comparing RCS across multiple platforms and configurations.
    """

    def __init__(self):
        self.platforms: Dict[str, CADRCSIntegrator] = {}

    def add_platform(self, name: str, cad_model: MissileCADModel,
                     material: MaterialProperties = None):
        """Add a platform for comparison"""
        integrator = CADRCSIntegrator(cad_model)
        integrator.build_geometry(material=material)
        self.platforms[name] = integrator

    def compare_all(self, frequency_ghz: float = 10.0) -> Dict[str, Dict]:
        """Compare RCS of all platforms"""
        results = {}

        for name, integrator in self.platforms.items():
            sweep = integrator.calculate_rcs_pattern(frequency_ghz)
            frontal = integrator.rcs_calculator.calculate_rcs(0, 0, frequency_ghz)
            beam = integrator.rcs_calculator.calculate_rcs(90, 0, frequency_ghz)
            tail = integrator.rcs_calculator.calculate_rcs(180, 0, frequency_ghz)

            results[name] = {
                "frontal_dbsm": frontal.rcs_dbsm,
                "beam_dbsm": beam.rcs_dbsm,
                "tail_dbsm": tail.rcs_dbsm,
                "mean_dbsm": sweep.mean_rcs_dbsm,
                "min_dbsm": sweep.min_rcs_dbsm,
                "max_dbsm": sweep.max_rcs_dbsm,
                "length_m": integrator.geometry.bounding_box.length,
                "diameter_m": integrator.cad_model.body_diameter
            }

        return results

    def generate_comparison_report(self, frequency_ghz: float = 10.0) -> str:
        """Generate comparison report"""
        results = self.compare_all(frequency_ghz)

        lines = []
        lines.append("=" * 80)
        lines.append("MULTI-PLATFORM RCS COMPARISON")
        lines.append("=" * 80)
        lines.append(f"Frequency: {frequency_ghz} GHz")
        lines.append("")

        # Header
        lines.append(f"{'Platform':<15} {'Length':<8} {'Diam':<8} "
                    f"{'Frontal':<10} {'Beam':<10} {'Tail':<10} {'Mean':<10}")
        lines.append(f"{'':<15} {'(m)':<8} {'(m)':<8} "
                    f"{'(dBsm)':<10} {'(dBsm)':<10} {'(dBsm)':<10} {'(dBsm)':<10}")
        lines.append("-" * 80)

        for name, data in results.items():
            lines.append(
                f"{name:<15} "
                f"{data['length_m']:<8.3f} "
                f"{data['diameter_m']:<8.3f} "
                f"{data['frontal_dbsm']:<+10.1f} "
                f"{data['beam_dbsm']:<+10.1f} "
                f"{data['tail_dbsm']:<+10.1f} "
                f"{data['mean_dbsm']:<+10.1f}"
            )

        lines.append("=" * 80)
        return "\n".join(lines)


# Example usage and validation
if __name__ == "__main__":
    print("=" * 70)
    print("CAD-Driven RCS Calculator - Validation")
    print("=" * 70)

    # Create PL-15 model
    print("\n[1] PL-15 CAD-based RCS Analysis")
    print("-" * 70)

    pl15 = create_pl15_cad_model()
    integrator = CADRCSIntegrator(pl15)
    integrator.build_geometry(resolution=24, material=MaterialProperties.aluminum())

    print(integrator.generate_rcs_report(frequency_ghz=10.0))

    # Compare PL-15 vs AIM-120
    print("\n[2] Multi-Platform Comparison")
    print("-" * 70)

    framework = RCSComparisonFramework()
    framework.add_platform("PL-15", create_pl15_cad_model())
    framework.add_platform("AIM-120D", create_aim120_cad_model())

    print(framework.generate_comparison_report(frequency_ghz=10.0))

    # Sensitivity analysis
    print("\n[3] Nose Length Sensitivity Analysis")
    print("-" * 70)

    pl15_integrator = CADRCSIntegrator(create_pl15_cad_model())
    nose_lengths = [0.3, 0.4, 0.5, 0.6, 0.7]
    sensitivity = pl15_integrator.sensitivity_analysis(
        "nose_length", nose_lengths, frequency_ghz=10.0
    )

    print(f"{'Nose Length (m)':<15} {'Frontal (dBsm)':<15} {'Mean (dBsm)':<15}")
    print("-" * 45)
    for i, length in enumerate(nose_lengths):
        if sensitivity["valid"][i]:
            print(f"{length:<15.2f} "
                  f"{sensitivity['frontal_rcs_dbsm'][i]:<+15.1f} "
                  f"{sensitivity['mean_rcs_dbsm'][i]:<+15.1f}")

    print("\n" + "=" * 70)
    print("CAD RCS Calculator validation complete.")
    print("=" * 70)
