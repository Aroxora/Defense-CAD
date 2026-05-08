#!/usr/bin/env python3
"""
Test Suite for Advanced CAD Modules

Tests geometry primitives, parametric shapes, missile models,
RCS calculations, and visualization components.

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import pytest
import numpy as np
from typing import Tuple


# =============================================================================
# Geometry Primitives Tests
# =============================================================================

class TestPoint3D:
    """Test Point3D class operations"""

    def test_creation(self):
        """Test point creation"""
        from cad_geometry import Point3D
        p = Point3D(1.0, 2.0, 3.0)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0

    def test_to_array(self):
        """Test conversion to numpy array"""
        from cad_geometry import Point3D
        p = Point3D(1.0, 2.0, 3.0)
        arr = p.to_array()
        assert np.allclose(arr, [1.0, 2.0, 3.0])

    def test_distance(self):
        """Test distance calculation"""
        from cad_geometry import Point3D
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(3, 4, 0)
        assert np.isclose(p1.distance_to(p2), 5.0)

    def test_addition(self):
        """Test point addition"""
        from cad_geometry import Point3D
        p1 = Point3D(1, 2, 3)
        p2 = Point3D(4, 5, 6)
        result = p1 + p2
        assert result.x == 5 and result.y == 7 and result.z == 9

    def test_subtraction(self):
        """Test point subtraction"""
        from cad_geometry import Point3D
        p1 = Point3D(4, 5, 6)
        p2 = Point3D(1, 2, 3)
        result = p1 - p2
        assert result.x == 3 and result.y == 3 and result.z == 3


class TestVector3D:
    """Test Vector3D class operations"""

    def test_magnitude(self):
        """Test vector magnitude"""
        from cad_geometry import Vector3D
        v = Vector3D(3, 4, 0)
        assert np.isclose(v.magnitude(), 5.0)

    def test_normalize(self):
        """Test vector normalization"""
        from cad_geometry import Vector3D
        v = Vector3D(3, 4, 0)
        n = v.normalize()
        assert np.isclose(n.magnitude(), 1.0)
        assert np.isclose(n.dx, 0.6)
        assert np.isclose(n.dy, 0.8)

    def test_dot_product(self):
        """Test dot product"""
        from cad_geometry import Vector3D
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        assert v1.dot(v2) == 0  # Perpendicular

        v3 = Vector3D(1, 0, 0)
        assert v1.dot(v3) == 1  # Parallel

    def test_cross_product(self):
        """Test cross product"""
        from cad_geometry import Vector3D
        v1 = Vector3D(1, 0, 0)
        v2 = Vector3D(0, 1, 0)
        cross = v1.cross(v2)
        assert np.isclose(cross.dz, 1.0)
        assert np.isclose(cross.dx, 0.0)
        assert np.isclose(cross.dy, 0.0)


class TestTriangle:
    """Test Triangle class operations"""

    def test_area_right_triangle(self):
        """Test triangle area for right triangle"""
        from cad_geometry import Point3D, Triangle
        tri = Triangle(
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0)
        )
        assert np.isclose(tri.area, 0.5)

    def test_area_equilateral(self):
        """Test triangle area for equilateral triangle"""
        from cad_geometry import Point3D, Triangle
        # Equilateral triangle with side 2
        tri = Triangle(
            Point3D(0, 0, 0),
            Point3D(2, 0, 0),
            Point3D(1, np.sqrt(3), 0)
        )
        expected_area = np.sqrt(3)  # sqrt(3) for side=2
        assert np.isclose(tri.area, expected_area)

    def test_normal(self):
        """Test triangle normal calculation"""
        from cad_geometry import Point3D, Triangle
        tri = Triangle(
            Point3D(0, 0, 0),
            Point3D(1, 0, 0),
            Point3D(0, 1, 0)
        )
        normal = tri.normal
        assert np.isclose(normal.dz, 1.0)  # Points up in Z

    def test_centroid(self):
        """Test triangle centroid"""
        from cad_geometry import Point3D, Triangle
        tri = Triangle(
            Point3D(0, 0, 0),
            Point3D(3, 0, 0),
            Point3D(0, 3, 0)
        )
        centroid = tri.centroid
        assert np.isclose(centroid.x, 1.0)
        assert np.isclose(centroid.y, 1.0)
        assert np.isclose(centroid.z, 0.0)


# =============================================================================
# Parametric Shapes Tests
# =============================================================================

class TestOgiveNose:
    """Test ogive nose geometry"""

    def test_ogive_creation(self):
        """Test ogive nose creation"""
        from cad_geometry import OgiveNose
        ogive = OgiveNose(length=0.5, base_radius=0.1)
        assert ogive.length == 0.5
        assert ogive.base_radius == 0.1
        assert ogive.ogive_radius is not None

    def test_ogive_mesh_generation(self):
        """Test ogive mesh generation"""
        from cad_geometry import OgiveNose
        ogive = OgiveNose(length=0.5, base_radius=0.1)
        mesh = ogive.generate_mesh(resolution=16)
        assert len(mesh.triangles) > 0

    def test_ogive_volume(self):
        """Test ogive volume is between cone and cylinder"""
        from cad_geometry import OgiveNose
        ogive = OgiveNose(length=0.5, base_radius=0.1)
        vol = ogive.calculate_volume()

        # Volume should be between cone and cylinder
        cone_vol = np.pi * 0.1**2 * 0.5 / 3
        cyl_vol = np.pi * 0.1**2 * 0.5

        assert cone_vol < vol < cyl_vol


class TestSearsHaackBody:
    """Test Sears-Haack body geometry"""

    def test_sears_haack_creation(self):
        """Test Sears-Haack body creation"""
        from cad_geometry import SearsHaackBody
        sh = SearsHaackBody(length=1.0, max_radius=0.15)
        assert sh.length == 1.0
        assert sh.max_radius == 0.15

    def test_sears_haack_volume(self):
        """Test Sears-Haack volume formula"""
        from cad_geometry import SearsHaackBody
        sh = SearsHaackBody(length=1.0, max_radius=0.15)
        vol = sh.calculate_volume()

        # Sears-Haack formula: V = (3*pi/16) * L * R^2
        expected = (3 * np.pi / 16) * 1.0 * 0.15**2
        assert np.isclose(vol, expected)


class TestCylindricalSection:
    """Test cylindrical section geometry"""

    def test_cylinder_volume(self):
        """Test cylinder volume calculation"""
        from cad_geometry import CylindricalSection
        cyl = CylindricalSection(length=1.0, forward_radius=0.1)
        vol = cyl.calculate_volume()

        expected = np.pi * 0.1**2 * 1.0
        assert np.isclose(vol, expected)

    def test_tapered_volume(self):
        """Test tapered (frustum) volume"""
        from cad_geometry import CylindricalSection
        cyl = CylindricalSection(length=1.0, forward_radius=0.1, aft_radius=0.05)
        vol = cyl.calculate_volume()

        # Frustum volume formula
        R, r, h = 0.1, 0.05, 1.0
        expected = (np.pi * h / 3) * (R**2 + R*r + r**2)
        assert np.isclose(vol, expected)


# =============================================================================
# Missile CAD Model Tests
# =============================================================================

class TestMissileCADModel:
    """Test missile CAD model generation and validation"""

    def test_pl15_model_creation(self):
        """Test PL-15 model creation"""
        from cad_geometry import create_pl15_cad_model
        pl15 = create_pl15_cad_model()
        assert pl15.name == "PL-15"
        assert pl15.total_length == 4.0
        assert pl15.body_diameter == 0.203

    def test_pl15_validation(self):
        """Test PL-15 parameter validation"""
        from cad_geometry import create_pl15_cad_model
        pl15 = create_pl15_cad_model()
        valid, errors = pl15.validate_parameters()
        assert valid, f"Validation failed: {errors}"

    def test_pl15_geometry_generation(self):
        """Test PL-15 geometry generation"""
        from cad_geometry import create_pl15_cad_model
        pl15 = create_pl15_cad_model()
        geom = pl15.generate_geometry(resolution=16)

        # Check bounding box matches expected dimensions
        assert geom.bounding_box.length > 3.5
        assert geom.bounding_box.length < 4.5

    def test_aim120_model(self):
        """Test AIM-120 model"""
        from cad_geometry import create_aim120_cad_model
        aim120 = create_aim120_cad_model()
        assert aim120.name == "AIM-120D"
        valid, errors = aim120.validate_parameters()
        assert valid

    def test_stl_export(self):
        """Test STL export functionality"""
        from cad_geometry import create_pl15_cad_model
        pl15 = create_pl15_cad_model()
        geom = pl15.generate_geometry(resolution=8)

        stl = geom.mesh.to_stl_ascii()
        assert "solid mesh" in stl
        assert "endsolid mesh" in stl
        assert "facet normal" in stl

    def test_mass_properties(self):
        """Test mass properties calculation"""
        from cad_geometry import create_pl15_cad_model
        pl15 = create_pl15_cad_model()
        props = pl15.get_mass_properties()

        assert "volume_m3" in props
        assert "estimated_mass_kg" in props
        assert "center_of_mass_x" in props
        assert props["volume_m3"] > 0


# =============================================================================
# RCS Calculator Tests
# =============================================================================

class TestPhysicalOpticsRCS:
    """Test Physical Optics RCS calculator"""

    def test_rcs_calculator_creation(self):
        """Test RCS calculator creation"""
        from cad_geometry import CylindricalSection
        from cad_rcs_calculator import PhysicalOpticsRCSCalculator, MaterialProperties

        cyl = CylindricalSection(length=1.0, forward_radius=0.1)
        mesh = cyl.generate_mesh(resolution=16)

        calc = PhysicalOpticsRCSCalculator(mesh, MaterialProperties.aluminum())
        assert calc.num_triangles > 0

    def test_rcs_calculation(self):
        """Test basic RCS calculation"""
        from cad_geometry import create_pl15_cad_model
        from cad_rcs_calculator import CADRCSIntegrator, MaterialProperties

        pl15 = create_pl15_cad_model()
        integrator = CADRCSIntegrator(pl15)
        integrator.build_geometry(resolution=12)

        result = integrator.rcs_calculator.calculate_rcs(0, 0, 10.0)

        # Check result has expected fields
        assert hasattr(result, 'rcs_m2')
        assert hasattr(result, 'rcs_dbsm')
        assert result.rcs_m2 > 0

    def test_rcs_sweep(self):
        """Test RCS sweep calculation"""
        from cad_geometry import create_pl15_cad_model
        from cad_rcs_calculator import CADRCSIntegrator

        pl15 = create_pl15_cad_model()
        integrator = CADRCSIntegrator(pl15)
        integrator.build_geometry(resolution=12)

        sweep = integrator.rcs_calculator.calculate_rcs_sweep(
            azimuth_range=(0, 180),
            num_points=19
        )

        assert len(sweep.azimuth_angles) == 19
        assert len(sweep.rcs_values_dbsm) == 19

    def test_material_properties(self):
        """Test different material properties"""
        from cad_rcs_calculator import MaterialProperties, MaterialType

        pec = MaterialProperties.perfect_conductor()
        assert pec.reflection_coefficient == 1.0

        alum = MaterialProperties.aluminum()
        assert alum.reflection_coefficient < 1.0

        ram = MaterialProperties.ram_coating(absorption_db=10)
        assert ram.reflection_coefficient < 0.2


# =============================================================================
# CAD Integration Tests
# =============================================================================

class TestCADIntegration:
    """Test CAD-RCS integration"""

    @pytest.mark.integration
    def test_full_pipeline(self):
        """Test full CAD to RCS pipeline"""
        from cad_geometry import create_pl15_cad_model
        from cad_rcs_calculator import CADRCSIntegrator, MaterialProperties

        # Create model
        pl15 = create_pl15_cad_model()

        # Validate geometry
        valid, errors = pl15.validate_parameters()
        assert valid

        # Generate geometry
        integrator = CADRCSIntegrator(pl15)
        geom = integrator.build_geometry(resolution=16)

        # Check geometry
        assert geom.total_volume > 0
        assert geom.total_surface_area > 0

        # Calculate RCS
        pattern = integrator.calculate_rcs_pattern(frequency_ghz=10.0)
        assert pattern.min_rcs_dbsm < pattern.max_rcs_dbsm

    @pytest.mark.integration
    def test_comparison_framework(self):
        """Test multi-platform comparison"""
        from cad_geometry import create_pl15_cad_model, create_aim120_cad_model
        from cad_rcs_calculator import RCSComparisonFramework

        framework = RCSComparisonFramework()
        framework.add_platform("PL-15", create_pl15_cad_model())
        framework.add_platform("AIM-120D", create_aim120_cad_model())

        results = framework.compare_all(frequency_ghz=10.0)

        assert "PL-15" in results
        assert "AIM-120D" in results


# =============================================================================
# Visualization Tests
# =============================================================================

class TestVisualization:
    """Test visualization components (non-GUI)"""

    def test_trajectory_generation(self):
        """Test trajectory generation"""
        from cad_visualization import TrajectoryGenerator, Point3D

        traj = TrajectoryGenerator.generate_missile_trajectory(
            launch_position=Point3D(0, 0, 10000),
            target_position=Point3D(100000, 0, 10000),
            max_time=100
        )

        assert len(traj.points) > 0
        assert traj.points[0].position.x == 0

    def test_aircraft_trajectory(self):
        """Test aircraft trajectory generation"""
        from cad_visualization import TrajectoryGenerator, Point3D

        traj = TrajectoryGenerator.generate_aircraft_trajectory(
            start_position=Point3D(0, 0, 12000),
            heading_deg=90,
            velocity=250,
            duration=60
        )

        assert len(traj.points) > 0

    def test_platform_state(self):
        """Test platform state creation"""
        from cad_visualization import PlatformState, PlatformSymbol, Point3D, Vector3D

        platform = PlatformState(
            name="Test Fighter",
            platform_type=PlatformSymbol.FIGHTER,
            position=Point3D(0, 0, 10000),
            velocity=Vector3D(250, 0, 0),
            heading_deg=90,
            altitude_m=10000
        )

        assert platform.name == "Test Fighter"
        assert platform.color == 'blue'  # Default for non-hostile

    def test_hostile_platform(self):
        """Test hostile platform color"""
        from cad_visualization import PlatformState, PlatformSymbol, Point3D, Vector3D

        platform = PlatformState(
            name="Enemy",
            platform_type=PlatformSymbol.FIGHTER,
            position=Point3D(0, 0, 10000),
            velocity=Vector3D(250, 0, 0),
            heading_deg=90,
            altitude_m=10000,
            is_hostile=True
        )

        assert platform.color == 'red'


# =============================================================================
# Numerical Stability Tests
# =============================================================================

class TestNumericalStability:
    """Test numerical stability of CAD calculations"""

    def test_small_dimensions(self):
        """Test handling of small dimensions"""
        from cad_geometry import OgiveNose

        # Very small ogive
        small = OgiveNose(length=0.01, base_radius=0.001)
        mesh = small.generate_mesh(resolution=8)
        assert len(mesh.triangles) > 0
        assert mesh.surface_area > 0

    def test_large_dimensions(self):
        """Test handling of large dimensions"""
        from cad_geometry import CylindricalSection

        # Large cylinder (like a ship hull section)
        large = CylindricalSection(length=100, forward_radius=10)
        vol = large.calculate_volume()
        expected = np.pi * 10**2 * 100
        assert np.isclose(vol, expected)

    def test_zero_velocity_aspect(self):
        """Test aspect angle with stationary target"""
        from cad_geometry import Point3D
        from rcs_models import calculate_aspect_angles

        radar = Point3D(0, 0, 0).to_array()
        target = Point3D(1000, 0, 0).to_array()
        velocity = np.array([0, 0, 0])  # Stationary

        az, el = calculate_aspect_angles(radar, target, velocity)
        # Should not raise error, return some reasonable angle
        assert not np.isnan(az)
        assert not np.isnan(el)


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
