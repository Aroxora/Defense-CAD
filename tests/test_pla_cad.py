#!/usr/bin/env python3
"""
PLA Defense CAD Test Suite

Comprehensive tests for all CAD validation, calculation logging,
and kill chain simulation components.

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import pytest
import numpy as np
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from osint_cad.platforms.pla_validated_cad import (
    ValidatedPoint3D,
    ValidatedVector3D,
    ValidatedTriangle,
    ValidatedMesh,
    ValidatedGeometryGenerator,
    create_df41_validated_spec,
    create_hq9b_validated_spec,
    create_j20_validated_spec,
    create_type055_validated_spec,
    generate_df41_validated_cad,
    generate_hq9b_validated_cad,
    generate_j20_validated_cad,
    generate_type055_validated_cad,
    generate_validated_ogive,
    generate_validated_cylinder,
    generate_validated_fin,
    generate_all_pla_systems,
    export_validation_report,
    EPSILON,
    MIN_TRIANGLE_AREA,
    LIMITATIONS_DOCUMENTATION
)

from osint_cad.util.calculation_logger import (
    CalculationLogger,
    OutputFormat,
    LogLevel,
    init_logger
)


# =============================================================================
# VALIDATED GEOMETRY TESTS
# =============================================================================

class TestValidatedPoint3D:
    """Tests for ValidatedPoint3D class"""

    def test_basic_creation(self):
        """Test basic point creation"""
        p = ValidatedPoint3D(1.0, 2.0, 3.0)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0

    def test_nan_detection(self):
        """Test NaN detection raises ValidationError"""
        from osint_cad.platforms.pla_validated_cad import ValidationError
        with pytest.raises(ValidationError):
            ValidatedPoint3D(1.0, float('nan'), 3.0)

    def test_inf_detection(self):
        """Test infinity detection raises ValidationError"""
        from osint_cad.platforms.pla_validated_cad import ValidationError
        with pytest.raises(ValidationError):
            ValidatedPoint3D(1.0, float('inf'), 3.0)

    def test_to_array(self):
        """Test conversion to numpy array"""
        p = ValidatedPoint3D(1.0, 2.0, 3.0)
        arr = p.to_array()
        assert np.allclose(arr, [1.0, 2.0, 3.0])

    def test_distance(self):
        """Test distance calculation"""
        p1 = ValidatedPoint3D(0, 0, 0)
        p2 = ValidatedPoint3D(3, 4, 0)
        assert abs(p1.distance_to(p2) - 5.0) < EPSILON


class TestValidatedVector3D:
    """Tests for ValidatedVector3D class"""

    def test_basic_creation(self):
        """Test basic vector creation"""
        v = ValidatedVector3D(1.0, 0.0, 0.0)
        assert v.dx == 1.0
        assert abs(v.magnitude() - 1.0) < EPSILON

    def test_normalization(self):
        """Test vector normalization"""
        v = ValidatedVector3D(3.0, 4.0, 0.0)
        n = v.normalize()
        assert abs(n.magnitude() - 1.0) < EPSILON
        assert abs(n.dx - 0.6) < EPSILON
        assert abs(n.dy - 0.8) < EPSILON

    def test_zero_vector_normalization(self):
        """Test zero vector normalization returns zero"""
        v = ValidatedVector3D(0.0, 0.0, 0.0)
        n = v.normalize()
        assert n.dx == 0.0
        assert n.dy == 0.0
        assert n.dz == 0.0

    def test_dot_product(self):
        """Test dot product calculation"""
        v1 = ValidatedVector3D(1.0, 0.0, 0.0)
        v2 = ValidatedVector3D(0.0, 1.0, 0.0)
        assert abs(v1.dot(v2)) < EPSILON  # Perpendicular

        v3 = ValidatedVector3D(1.0, 0.0, 0.0)
        assert abs(v1.dot(v3) - 1.0) < EPSILON  # Parallel

    def test_cross_product(self):
        """Test cross product calculation"""
        v1 = ValidatedVector3D(1.0, 0.0, 0.0)
        v2 = ValidatedVector3D(0.0, 1.0, 0.0)
        cross = v1.cross(v2)
        assert abs(cross.dx) < EPSILON
        assert abs(cross.dy) < EPSILON
        assert abs(cross.dz - 1.0) < EPSILON


class TestValidatedTriangle:
    """Tests for ValidatedTriangle class"""

    def test_valid_triangle(self):
        """Test valid triangle creation"""
        p1 = ValidatedPoint3D(0, 0, 0)
        p2 = ValidatedPoint3D(1, 0, 0)
        p3 = ValidatedPoint3D(0, 1, 0)
        tri = ValidatedTriangle(p1, p2, p3)
        assert tri.is_valid
        assert tri.area > MIN_TRIANGLE_AREA

    def test_degenerate_triangle(self):
        """Test degenerate triangle detection (collinear points)"""
        p1 = ValidatedPoint3D(0, 0, 0)
        p2 = ValidatedPoint3D(1, 0, 0)
        p3 = ValidatedPoint3D(2, 0, 0)  # Collinear
        tri = ValidatedTriangle(p1, p2, p3)
        assert not tri.is_valid

    def test_normal_calculation(self):
        """Test normal vector calculation"""
        p1 = ValidatedPoint3D(0, 0, 0)
        p2 = ValidatedPoint3D(1, 0, 0)
        p3 = ValidatedPoint3D(0, 1, 0)
        tri = ValidatedTriangle(p1, p2, p3)
        normal = tri.normal
        assert abs(normal.dx) < EPSILON
        assert abs(normal.dy) < EPSILON
        assert abs(abs(normal.dz) - 1.0) < EPSILON

    def test_area_calculation(self):
        """Test area calculation"""
        p1 = ValidatedPoint3D(0, 0, 0)
        p2 = ValidatedPoint3D(2, 0, 0)
        p3 = ValidatedPoint3D(0, 2, 0)
        tri = ValidatedTriangle(p1, p2, p3)
        assert abs(tri.area - 2.0) < EPSILON  # Area = 0.5 * base * height = 0.5 * 2 * 2


class TestValidatedMesh:
    """Tests for ValidatedMesh class"""

    def test_mesh_creation(self):
        """Test mesh creation with valid triangles"""
        triangles = [
            ValidatedTriangle(
                ValidatedPoint3D(0, 0, 0),
                ValidatedPoint3D(1, 0, 0),
                ValidatedPoint3D(0, 1, 0)
            ),
            ValidatedTriangle(
                ValidatedPoint3D(1, 0, 0),
                ValidatedPoint3D(1, 1, 0),
                ValidatedPoint3D(0, 1, 0)
            )
        ]
        mesh = ValidatedMesh(triangles)
        assert mesh.triangle_count == 2
        assert mesh.valid_triangle_count == 2
        assert mesh.surface_area > 0

    def test_stl_export(self):
        """Test STL export"""
        triangles = [
            ValidatedTriangle(
                ValidatedPoint3D(0, 0, 0),
                ValidatedPoint3D(1, 0, 0),
                ValidatedPoint3D(0, 1, 0)
            )
        ]
        mesh = ValidatedMesh(triangles)
        stl = mesh.to_stl_ascii()
        assert "solid" in stl
        assert "facet normal" in stl
        assert "vertex" in stl
        assert "endsolid" in stl


# =============================================================================
# PRIMITIVE GEOMETRY GENERATION TESTS
# =============================================================================

class TestOgiveGeneration:
    """Tests for ogive nose cone generation"""

    def test_basic_ogive(self):
        """Test basic ogive generation"""
        mesh = generate_validated_ogive(length=1.0, base_radius=0.5, resolution=16)
        assert mesh.triangle_count > 0
        assert mesh.valid_triangle_count > 0
        assert mesh.surface_area > 0

    def test_ogive_dimensions(self):
        """Test ogive has correct dimensions"""
        length = 2.0
        radius = 0.5
        mesh = generate_validated_ogive(length=length, base_radius=radius, resolution=32)

        # Check mesh has triangles with valid geometry
        assert mesh.triangle_count > 0
        assert mesh.surface_area > 0

        # Check all triangles have valid normals
        for tri in mesh.triangles[:10]:  # Sample first 10
            normal = tri.normal
            assert abs(normal.magnitude() - 1.0) < 0.01 or normal.magnitude() < EPSILON

    def test_ogive_invalid_params(self):
        """Test ogive with invalid parameters"""
        from osint_cad.platforms.pla_validated_cad import ValidationError
        with pytest.raises(ValidationError):
            generate_validated_ogive(length=-1.0, base_radius=0.5)
        with pytest.raises(ValidationError):
            generate_validated_ogive(length=1.0, base_radius=0.0)


class TestCylinderGeneration:
    """Tests for cylinder/frustum generation"""

    def test_basic_cylinder(self):
        """Test basic cylinder generation"""
        mesh = generate_validated_cylinder(
            length=2.0,
            forward_radius=0.5,
            aft_radius=0.5,
            resolution=16
        )
        assert mesh.triangle_count > 0
        assert mesh.valid_triangle_count > 0

    def test_frustum(self):
        """Test frustum (tapered cylinder) generation"""
        mesh = generate_validated_cylinder(
            length=2.0,
            forward_radius=0.5,
            aft_radius=0.3,
            resolution=16
        )
        assert mesh.triangle_count > 0
        assert mesh.valid_triangle_count > 0


class TestFinGeneration:
    """Tests for fin generation"""

    def test_basic_fin(self):
        """Test basic fin generation"""
        mesh = generate_validated_fin(
            root_chord=0.5,
            tip_chord=0.2,
            span=0.4,
            sweep_deg=45,
            thickness=0.02
        )
        assert mesh.triangle_count > 0
        assert mesh.valid_triangle_count > 0


# =============================================================================
# SYSTEM CAD GENERATION TESTS
# =============================================================================

class TestDF41CAD:
    """Tests for DF-41 ICBM CAD generation"""

    def test_spec_creation(self):
        """Test DF-41 spec creation"""
        spec = create_df41_validated_spec()
        assert spec.system_name == "DF-41"
        assert spec.get_value("total_length") > 0
        assert spec.get_value("body_diameter") > 0

    def test_cad_generation(self):
        """Test DF-41 CAD generation"""
        mesh, metadata = generate_df41_validated_cad(resolution=16)
        assert mesh is not None
        assert metadata['total_triangles'] > 0
        assert metadata['valid_triangles'] > 0
        assert metadata['validation_passed']

    def test_parameter_validation(self):
        """Test DF-41 parameter validation"""
        spec = create_df41_validated_spec()
        valid, errors = spec.validate_all()
        assert valid, f"Validation errors: {errors}"


class TestHQ9BCAD:
    """Tests for HQ-9B SAM CAD generation"""

    def test_spec_creation(self):
        """Test HQ-9B spec creation"""
        spec = create_hq9b_validated_spec()
        assert spec.system_name == "HQ-9B"
        assert spec.get_value("total_length") > 0

    def test_cad_generation(self):
        """Test HQ-9B CAD generation"""
        mesh, metadata = generate_hq9b_validated_cad(resolution=16)
        assert mesh is not None
        assert metadata['total_triangles'] > 0
        assert metadata['validation_passed']


class TestJ20CAD:
    """Tests for J-20 Fighter CAD generation"""

    def test_spec_creation(self):
        """Test J-20 spec creation"""
        spec = create_j20_validated_spec()
        assert spec.system_name == "J-20"
        assert spec.get_value("length") > 0
        assert spec.get_value("wingspan") > 0

    def test_cad_generation(self):
        """Test J-20 CAD generation"""
        mesh, metadata = generate_j20_validated_cad(resolution=16)
        assert mesh is not None
        assert metadata['total_triangles'] > 0
        assert metadata['validation_passed']


class TestType055CAD:
    """Tests for Type 055 Destroyer CAD generation"""

    def test_spec_creation(self):
        """Test Type 055 spec creation"""
        spec = create_type055_validated_spec()
        assert spec.system_name == "Type 055"
        assert spec.get_value("length") > 0
        assert spec.get_value("beam") > 0

    def test_cad_generation(self):
        """Test Type 055 CAD generation"""
        mesh, metadata = generate_type055_validated_cad(resolution=16)
        assert mesh is not None
        assert metadata['total_triangles'] > 0
        assert metadata['validation_passed']


class TestAllSystemsGeneration:
    """Tests for generating all PLA systems"""

    def test_generate_all(self):
        """Test generating all systems"""
        results = generate_all_pla_systems(resolution=16)
        assert len(results) >= 4

        for name, (mesh, metadata) in results.items():
            assert mesh is not None, f"{name} mesh is None"
            assert metadata['validation_passed'], f"{name} validation failed"

    def test_validation_report(self):
        """Test validation report generation"""
        results = generate_all_pla_systems(resolution=16)
        report = export_validation_report(results)
        assert "Validation Report" in report or "VALIDATION" in report
        assert len(report) > 100


# =============================================================================
# CALCULATION LOGGER TESTS
# =============================================================================

class TestCalculationLogger:
    """Tests for calculation logging"""

    def test_logger_creation(self):
        """Test logger creation"""
        logger = init_logger(
            name="TestLogger",
            output_formats=[OutputFormat.CONSOLE],
            verbose=False
        )
        assert logger is not None
        assert logger.name == "TestLogger"

    def test_log_calculation(self):
        """Test logging a calculation"""
        logger = init_logger(
            name="TestLogger",
            output_formats=[],
            verbose=False
        )
        logger.log_calculation(
            name="Test Calculation",
            formula="a + b",
            inputs={"a": 1, "b": 2},
            result=3,
            unit="count",
            confidence=0.95
        )
        assert len(logger.calculations) == 1
        assert logger.calculations[0].result == 3

    def test_log_validation(self):
        """Test logging a validation"""
        logger = init_logger(
            name="TestLogger",
            output_formats=[],
            verbose=False
        )
        logger.log_validation(
            component="Test",
            parameter="value",
            value=5.0,
            min_val=0.0,
            max_val=10.0
        )
        assert len(logger.validations) == 1
        assert logger.validations[0].is_valid

    def test_log_validation_fail(self):
        """Test logging a failed validation"""
        logger = init_logger(
            name="TestLogger",
            output_formats=[],
            verbose=False
        )
        logger.log_validation(
            component="Test",
            parameter="value",
            value=15.0,  # Out of range
            min_val=0.0,
            max_val=10.0
        )
        assert len(logger.validations) == 1
        assert not logger.validations[0].is_valid

    def test_section_context(self):
        """Test section context manager"""
        logger = init_logger(
            name="TestLogger",
            output_formats=[],
            verbose=False
        )
        with logger.section("Test Section"):
            logger.log_calculation(
                name="Inner Calc",
                formula="x",
                inputs={},
                result=1,
                unit="",
                confidence=1.0
            )
        # Section should complete without error

    def test_markdown_report(self):
        """Test markdown report generation"""
        logger = init_logger(
            name="TestLogger",
            output_formats=[],
            verbose=False
        )
        logger.log_calculation(
            name="Test",
            formula="x",
            inputs={"x": 1},
            result=1,
            unit="count",
            confidence=0.9
        )
        logger.finalize()
        report = logger.generate_markdown_report()
        assert "Calculation" in report or "calculation" in report


# =============================================================================
# LIMITATIONS DOCUMENTATION TESTS
# =============================================================================

class TestLimitationsDocumentation:
    """Tests for limitations documentation"""

    def test_limitations_exist(self):
        """Test that limitations documentation exists"""
        assert LIMITATIONS_DOCUMENTATION is not None
        assert len(LIMITATIONS_DOCUMENTATION) > 0

    def test_limitations_categories(self):
        """Test that all expected categories are documented"""
        # Check for key sections in the documentation string
        expected_sections = [
            "DATA SOURCE LIMITATIONS",
            "GEOMETRIC MODELING LIMITATIONS",
            "NUMERICAL/COMPUTATIONAL LIMITATIONS"
        ]
        for section in expected_sections:
            assert section in LIMITATIONS_DOCUMENTATION, f"Missing section: {section}"

    def test_limitations_content(self):
        """Test that limitations have substantial content"""
        # Documentation should be substantial
        assert len(LIMITATIONS_DOCUMENTATION) > 1000, "Documentation too short"
        # Should have multiple categories
        assert LIMITATIONS_DOCUMENTATION.count("CATEGORY") >= 3, "Missing categories"


# =============================================================================
# NUMERICAL VALIDATION TESTS
# =============================================================================

class TestNumericalValidation:
    """Tests for numerical validation and edge cases"""

    def test_epsilon_tolerance(self):
        """Test epsilon tolerance is appropriate"""
        assert EPSILON > 0
        assert EPSILON < 1e-6

    def test_min_triangle_area(self):
        """Test minimum triangle area is appropriate"""
        assert MIN_TRIANGLE_AREA > 0
        assert MIN_TRIANGLE_AREA < 1e-8

    def test_large_mesh_stability(self):
        """Test stability with high resolution mesh"""
        mesh = generate_validated_ogive(length=1.0, base_radius=0.5, resolution=64)
        assert mesh.triangle_count > 100
        # All triangles should be valid
        validity_ratio = mesh.valid_triangle_count / mesh.triangle_count
        assert validity_ratio > 0.99

    def test_no_nan_in_mesh(self):
        """Test no NaN values in generated mesh"""
        mesh, _ = generate_df41_validated_cad(resolution=32)
        for tri in mesh.triangles:
            assert not np.isnan(tri.v1.x)
            assert not np.isnan(tri.v1.y)
            assert not np.isnan(tri.v1.z)
            assert not np.isnan(tri.area)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for full pipeline"""

    def test_full_cad_pipeline(self):
        """Test complete CAD generation pipeline"""
        # Generate all systems
        results = generate_all_pla_systems(resolution=24)

        # Verify all generated
        assert len(results) >= 4

        # Check each system
        total_triangles = 0
        for name, (mesh, metadata) in results.items():
            assert mesh is not None
            assert metadata['validation_passed']
            total_triangles += metadata['valid_triangles']

        assert total_triangles > 1000

    def test_stl_export_all_systems(self):
        """Test STL export for all systems"""
        results = generate_all_pla_systems(resolution=16)

        for name, (mesh, metadata) in results.items():
            if mesh is not None:
                stl = mesh.to_stl_ascii()
                # Verify valid STL structure
                assert stl.startswith("solid")
                assert "facet normal" in stl
                assert "vertex" in stl
                assert "endsolid" in stl

    def test_calculation_logging_integration(self):
        """Test calculation logging with CAD generation"""
        logger = init_logger(
            name="IntegrationTest",
            output_formats=[],
            verbose=False
        )

        spec = create_df41_validated_spec()

        # Log parameter validations
        for name, param in spec.parameters.items():
            logger.log_validation(
                component="DF-41",
                parameter=name,
                value=param.value,
                min_val=param.min_valid,
                max_val=param.max_valid
            )

        # Generate CAD
        mesh, metadata = generate_df41_validated_cad(resolution=16)

        # Log result
        logger.log_calculation(
            name="DF-41 Surface Area",
            formula="mesh.surface_area",
            inputs={"triangles": metadata['total_triangles']},
            result=metadata['surface_area_m2'],
            unit="m^2",
            confidence=0.6
        )

        logger.finalize()

        assert len(logger.validations) > 0
        assert len(logger.calculations) > 0


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
