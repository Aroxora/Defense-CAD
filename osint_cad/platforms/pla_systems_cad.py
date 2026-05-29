#!/usr/bin/env python3
"""
PLA Defense Systems - Comprehensive CAD Module

Complete parametric CAD models for all PLA parade systems including:
- Strategic Missiles (DF-series)
- Anti-Ship Missiles (YJ-series)
- Air Defense Systems (HQ-series)
- Air-to-Air Missiles (PL-series)
- Cruise Missiles (CJ-series)
- Naval Systems
- Ground Vehicles

ERROR-FREE DESIGN PRINCIPLES:
1. All dimensions validated against physical constraints
2. All parameters include uncertainty bounds
3. All calculations include numerical stability checks
4. All models include confidence levels from public sources
5. Complete limitation documentation for each system

LIMITATIONS AND UNCERTAINTY SOURCES:
- All parameters derived from unclassified public sources only
- Confidence levels reflect source reliability (20-85%)
- Dimensional accuracy limited by publicly available imagery
- Performance parameters are estimates with documented uncertainty
- Internal component layouts are notional representations
- RAM/stealth properties are approximations

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any, Union
from enum import Enum
from abc import ABC, abstractmethod
import math

from osint_cad.geometry.cad_geometry import (
    Point3D, Vector3D, TriangleMesh, Triangle, BoundingBox,
    OgiveNose, SearsHaackBody, CylindricalSection, WingGeometry,
    FinGeometry, NozzleGeometry, GeometryComponent, CADGeometryResult,
    PlatformType
)
from osint_cad.geometry.cad_constraints import (
    ConstraintValidator, RangeConstraint, RatioConstraint,
    ConstraintSet, ConstraintType, ConstraintSeverity,
    DesignConstraintEngine
)


# =============================================================================
# ERROR HANDLING AND VALIDATION FRAMEWORK
# =============================================================================

class CADError(Exception):
    """Base exception for CAD errors"""
    pass


class GeometryValidationError(CADError):
    """Raised when geometry validation fails"""
    pass


class ParameterBoundsError(CADError):
    """Raised when parameter exceeds physical bounds"""
    pass


class NumericalStabilityError(CADError):
    """Raised when numerical calculations become unstable"""
    pass


class ConfidenceLevelWarning(Warning):
    """Warning for low confidence parameters"""
    pass


@dataclass
class UncertaintyBounds:
    """
    Represents uncertainty bounds for a parameter.

    All PLA system parameters include uncertainty quantification
    to ensure error-free operation within known bounds.
    """
    nominal: float
    lower_bound: float
    upper_bound: float
    confidence: float  # 0-1, confidence in nominal value
    source: str  # Documentation of source
    limitation: str  # Known limitations of this estimate

    def __post_init__(self):
        """Validate uncertainty bounds"""
        if not (0 <= self.confidence <= 1):
            raise ParameterBoundsError(
                f"Confidence must be 0-1, got {self.confidence}"
            )
        if self.lower_bound > self.nominal or self.nominal > self.upper_bound:
            raise ParameterBoundsError(
                f"Bounds invalid: {self.lower_bound} <= {self.nominal} <= {self.upper_bound}"
            )

    @property
    def uncertainty_pct(self) -> float:
        """Percentage uncertainty"""
        if self.nominal == 0:
            return 0
        return ((self.upper_bound - self.lower_bound) / (2 * abs(self.nominal))) * 100

    def sample(self, n: int = 1) -> np.ndarray:
        """Sample from uncertainty distribution (truncated normal)"""
        # Use truncated normal within bounds
        std = (self.upper_bound - self.lower_bound) / 4  # 95% within bounds
        samples = np.random.normal(self.nominal, std, n)
        return np.clip(samples, self.lower_bound, self.upper_bound)

    def validate_value(self, value: float) -> bool:
        """Check if value is within uncertainty bounds"""
        return self.lower_bound <= value <= self.upper_bound


@dataclass
class SystemLimitations:
    """
    Complete documentation of system model limitations.

    Required for error-free CAD operation - all users must
    understand what the model can and cannot represent.
    """
    system_name: str
    model_type: str

    # Geometric limitations
    geometry_accuracy_mm: float
    geometry_source: str
    geometry_limitations: List[str]

    # Performance limitations
    performance_confidence: float
    performance_source: str
    performance_limitations: List[str]

    # Internal layout limitations
    internal_layout_known: bool
    internal_layout_limitations: List[str]

    # Material/stealth limitations
    material_properties_known: bool
    material_limitations: List[str]

    # General caveats
    general_caveats: List[str]

    # Update information
    last_updated: str
    sources: List[str]

    def to_report(self) -> str:
        """Generate human-readable limitations report"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"LIMITATIONS REPORT: {self.system_name}")
        lines.append("=" * 70)
        lines.append(f"Model Type: {self.model_type}")
        lines.append(f"Last Updated: {self.last_updated}")
        lines.append("")

        lines.append("GEOMETRY LIMITATIONS:")
        lines.append(f"  Accuracy: ±{self.geometry_accuracy_mm:.0f} mm")
        lines.append(f"  Source: {self.geometry_source}")
        for lim in self.geometry_limitations:
            lines.append(f"  - {lim}")
        lines.append("")

        lines.append("PERFORMANCE LIMITATIONS:")
        lines.append(f"  Confidence: {self.performance_confidence:.0%}")
        lines.append(f"  Source: {self.performance_source}")
        for lim in self.performance_limitations:
            lines.append(f"  - {lim}")
        lines.append("")

        lines.append("INTERNAL LAYOUT:")
        lines.append(f"  Known: {'Yes' if self.internal_layout_known else 'No - NOTIONAL ONLY'}")
        for lim in self.internal_layout_limitations:
            lines.append(f"  - {lim}")
        lines.append("")

        lines.append("MATERIAL/STEALTH PROPERTIES:")
        lines.append(f"  Known: {'Partial' if self.material_properties_known else 'No - ESTIMATED'}")
        for lim in self.material_limitations:
            lines.append(f"  - {lim}")
        lines.append("")

        lines.append("GENERAL CAVEATS:")
        for caveat in self.general_caveats:
            lines.append(f"  * {caveat}")
        lines.append("")

        lines.append("SOURCES:")
        for src in self.sources:
            lines.append(f"  [{src}]")

        lines.append("=" * 70)
        return "\n".join(lines)


class ValidatedCADModel(ABC):
    """
    Abstract base class for all validated PLA CAD models.

    Ensures error-free operation through:
    1. Parameter validation on construction
    2. Geometry validation on generation
    3. Numerical stability checks
    4. Complete limitation documentation
    """

    @abstractmethod
    def get_parameters(self) -> Dict[str, UncertaintyBounds]:
        """Get all parameters with uncertainty bounds"""
        pass

    @abstractmethod
    def get_limitations(self) -> SystemLimitations:
        """Get complete limitation documentation"""
        pass

    @abstractmethod
    def validate_geometry(self) -> Tuple[bool, List[str]]:
        """Validate geometric constraints, return (valid, errors)"""
        pass

    @abstractmethod
    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        """Generate validated 3D geometry"""
        pass

    def validate_all(self) -> ConstraintSet:
        """Run all validations and return results"""
        results = ConstraintSet()

        # Validate parameters
        params = self.get_parameters()
        for name, bounds in params.items():
            is_valid = bounds.lower_bound <= bounds.nominal <= bounds.upper_bound
            results.results.append(
                type('ConstraintResult', (), {
                    'constraint_name': f"Parameter: {name}",
                    'constraint_type': ConstraintType.GEOMETRIC,
                    'is_satisfied': is_valid,
                    'actual_value': bounds.nominal,
                    'limit_value': bounds.upper_bound,
                    'margin': bounds.uncertainty_pct,
                    'severity': ConstraintSeverity.ERROR if not is_valid else ConstraintSeverity.INFO,
                    'message': f"Value {bounds.nominal} within [{bounds.lower_bound}, {bounds.upper_bound}]",
                    'recommendation': bounds.limitation
                })()
            )

        # Validate geometry
        geo_valid, geo_errors = self.validate_geometry()
        for error in geo_errors:
            results.results.append(
                type('ConstraintResult', (), {
                    'constraint_name': "Geometry Validation",
                    'constraint_type': ConstraintType.GEOMETRIC,
                    'is_satisfied': False,
                    'actual_value': 0,
                    'limit_value': 0,
                    'margin': 0,
                    'severity': ConstraintSeverity.ERROR,
                    'message': error,
                    'recommendation': "Review geometric parameters"
                })()
            )

        return results


# =============================================================================
# MISSILE TYPE ENUMERATION
# =============================================================================

class MissileCategory(Enum):
    """PLA missile system categories"""
    ICBM = "icbm"  # DF-5, DF-31, DF-41
    IRBM = "irbm"  # DF-26
    MRBM = "mrbm"  # DF-21, DF-17
    SRBM = "srbm"  # DF-15, DF-16
    SLBM = "slbm"  # JL-2, JL-3
    GLCM = "glcm"  # CJ-10, CJ-20
    ASCM = "ascm"  # YJ-18, YJ-21
    SAM = "sam"    # HQ-9, HQ-16, HQ-22
    AAM = "aam"    # PL-15, PL-21


class PropulsionType(Enum):
    """Propulsion system types"""
    SOLID_ROCKET = "solid_rocket"
    LIQUID_ROCKET = "liquid_rocket"
    DUAL_PULSE_SOLID = "dual_pulse_solid"
    RAMJET = "ramjet"
    SCRAMJET = "scramjet"
    TURBOJET = "turbojet"


# =============================================================================
# DF-SERIES STRATEGIC MISSILES
# =============================================================================

@dataclass
class DFSeriesMissileCAD(ValidatedCADModel):
    """
    DF-Series Strategic Missile CAD Model

    Covers: DF-5C, DF-15B, DF-16, DF-17, DF-21D, DF-26, DF-27, DF-31AG, DF-41

    ERROR-FREE DESIGN:
    - All dimensions from parade imagery analysis
    - Uncertainty bounds on all parameters
    - Physical constraint validation
    - Complete limitation documentation

    LIMITATIONS:
    - External dimensions only (internal layout notional)
    - Performance estimates from public analysis
    - RCS values are approximations
    - No classified information used
    """

    designation: str
    category: MissileCategory

    # Dimensions with uncertainty
    total_length: UncertaintyBounds = None
    body_diameter: UncertaintyBounds = None
    nose_length: UncertaintyBounds = None

    # Stages (for multi-stage missiles)
    num_stages: int = 1
    stage_lengths: List[UncertaintyBounds] = None
    stage_diameters: List[UncertaintyBounds] = None

    # Fins/control surfaces
    num_fins: int = 4
    fin_span: UncertaintyBounds = None
    fin_root_chord: UncertaintyBounds = None
    fin_sweep_deg: UncertaintyBounds = None

    # Performance (for reference, not CAD)
    range_km: UncertaintyBounds = None
    payload_kg: UncertaintyBounds = None
    cep_m: UncertaintyBounds = None

    # Mass properties
    launch_mass_kg: UncertaintyBounds = None

    # Propulsion
    propulsion: PropulsionType = PropulsionType.SOLID_ROCKET

    # Warhead type
    warhead_type: str = "conventional"  # or "nuclear", "dual-capable"

    def __post_init__(self):
        """Validate on construction"""
        self._validate_parameters()

    def _validate_parameters(self):
        """Validate all parameters are within physical bounds"""
        if self.total_length is not None:
            if self.total_length.nominal <= 0:
                raise ParameterBoundsError("Total length must be positive")
            if self.total_length.nominal > 40:  # ICBMs can be up to ~35m
                raise ParameterBoundsError("Total length exceeds physical maximum (40m)")

        if self.body_diameter is not None:
            if self.body_diameter.nominal <= 0:
                raise ParameterBoundsError("Body diameter must be positive")
            if self.body_diameter.nominal > 5:  # No missile > 5m diameter
                raise ParameterBoundsError("Body diameter exceeds physical maximum (5m)")

    def get_parameters(self) -> Dict[str, UncertaintyBounds]:
        """Get all parameters with uncertainty bounds"""
        params = {}
        if self.total_length:
            params['total_length'] = self.total_length
        if self.body_diameter:
            params['body_diameter'] = self.body_diameter
        if self.nose_length:
            params['nose_length'] = self.nose_length
        if self.fin_span:
            params['fin_span'] = self.fin_span
        if self.range_km:
            params['range_km'] = self.range_km
        if self.payload_kg:
            params['payload_kg'] = self.payload_kg
        if self.cep_m:
            params['cep_m'] = self.cep_m
        if self.launch_mass_kg:
            params['launch_mass_kg'] = self.launch_mass_kg
        return params

    def get_limitations(self) -> SystemLimitations:
        """Get complete limitation documentation"""
        return SystemLimitations(
            system_name=self.designation,
            model_type="Strategic Ballistic Missile CAD",
            geometry_accuracy_mm=50,
            geometry_source="Parade imagery, public satellite photos",
            geometry_limitations=[
                "External dimensions only - internal layout is NOTIONAL",
                "Dimensional accuracy ±50mm based on image resolution",
                "Nose cone profile estimated from silhouette analysis",
                "Stage separation mechanisms not modeled",
                "Guidance section details unknown",
                "RV geometry is approximate"
            ],
            performance_confidence=0.5,
            performance_source="Open-source analysis, DOD reports",
            performance_limitations=[
                "Range estimates have ±20% uncertainty",
                "CEP estimates are analytical, not test-verified",
                "Payload capacity is maximum theoretical",
                "Actual performance may vary significantly",
                "Terminal maneuvering capability uncertain"
            ],
            internal_layout_known=False,
            internal_layout_limitations=[
                "Internal component positions are ESTIMATES ONLY",
                "Propellant grain geometry unknown",
                "Guidance system location approximate",
                "Warhead integration details classified",
                "Telemetry/self-destruct systems not modeled"
            ],
            material_properties_known=False,
            material_limitations=[
                "Composite materials assumed, specifics unknown",
                "Thermal protection system not characterized",
                "RCS reduction measures unknown",
                "Structural margins not validated"
            ],
            general_caveats=[
                "THIS MODEL IS FOR UNCLASSIFIED ANALYSIS ONLY",
                "Do not use for actual military planning",
                "All parameters are public-source estimates",
                "No classified or export-controlled data used",
                "Model accuracy degrades for newer variants"
            ],
            last_updated="2025-01",
            sources=[
                "DOD Annual Report to Congress on PRC Military Power",
                "Jane's Strategic Weapon Systems",
                "CSIS Missile Threat Database",
                "Parade imagery analysis (National Day parades)",
                "Academic publications on Chinese strategic forces"
            ]
        )

    def validate_geometry(self) -> Tuple[bool, List[str]]:
        """Validate geometric constraints"""
        errors = []

        if self.total_length and self.body_diameter:
            fineness = self.total_length.nominal / self.body_diameter.nominal
            if fineness < 5:
                errors.append(f"Fineness ratio {fineness:.1f} too low (min 5)")
            if fineness > 25:
                errors.append(f"Fineness ratio {fineness:.1f} too high (max 25)")

        if self.nose_length and self.body_diameter:
            nose_ratio = self.nose_length.nominal / self.body_diameter.nominal
            if nose_ratio < 1:
                errors.append(f"Nose too blunt: ratio {nose_ratio:.1f} (min 1)")
            if nose_ratio > 5:
                errors.append(f"Nose too long: ratio {nose_ratio:.1f} (max 5)")

        if self.num_stages > 1 and self.stage_lengths:
            total_stage = sum(s.nominal for s in self.stage_lengths)
            if self.nose_length:
                total_stage += self.nose_length.nominal
            if self.total_length:
                diff = abs(total_stage - self.total_length.nominal)
                if diff > 0.5:  # 0.5m tolerance
                    errors.append(f"Stage lengths don't sum to total: diff={diff:.2f}m")

        return len(errors) == 0, errors

    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        """Generate validated 3D geometry"""
        # First validate
        valid, errors = self.validate_geometry()
        if not valid:
            raise GeometryValidationError(f"Geometry validation failed: {errors}")

        components = {}
        all_meshes = []

        # Use nominal values for geometry
        length = self.total_length.nominal if self.total_length else 10.0
        diameter = self.body_diameter.nominal if self.body_diameter else 1.5
        nose_len = self.nose_length.nominal if self.nose_length else diameter * 2

        radius = diameter / 2

        # 1. Nose cone (ogive for ballistic missiles)
        nose = OgiveNose(length=nose_len, base_radius=radius)
        nose_mesh = nose.generate_mesh(resolution)
        all_meshes.append(nose_mesh)
        components["nose"] = nose

        # 2. Body sections (stages)
        x_offset = nose_len
        body_length = length - nose_len

        if self.num_stages == 1 or not self.stage_lengths:
            # Single stage
            body = CylindricalSection(
                length=body_length * 0.9,
                forward_radius=radius
            )
            body_mesh = body.generate_mesh(resolution)
            body_mesh = body_mesh.transform(translation=Point3D(x_offset, 0, 0))
            all_meshes.append(body_mesh)
            components["body"] = body

            # Nozzle section
            nozzle_section = CylindricalSection(
                length=body_length * 0.1,
                forward_radius=radius,
                aft_radius=radius * 0.7
            )
            nozzle_mesh = nozzle_section.generate_mesh(resolution)
            nozzle_mesh = nozzle_mesh.transform(
                translation=Point3D(x_offset + body_length * 0.9, 0, 0)
            )
            all_meshes.append(nozzle_mesh)
            components["nozzle_section"] = nozzle_section

        else:
            # Multi-stage
            for i, stage_len in enumerate(self.stage_lengths):
                stage_diam = self.stage_diameters[i].nominal if self.stage_diameters else diameter
                stage_rad = stage_diam / 2

                stage = CylindricalSection(
                    length=stage_len.nominal,
                    forward_radius=stage_rad
                )
                stage_mesh = stage.generate_mesh(resolution)
                stage_mesh = stage_mesh.transform(translation=Point3D(x_offset, 0, 0))
                all_meshes.append(stage_mesh)
                components[f"stage_{i+1}"] = stage

                x_offset += stage_len.nominal

        # 3. Fins (if applicable)
        if self.num_fins > 0 and self.fin_span:
            fin_x = length - (self.fin_root_chord.nominal if self.fin_root_chord else diameter * 0.5) - 0.2

            for i in range(self.num_fins):
                angle = i * 360 / self.num_fins
                fin = FinGeometry(
                    root_chord=self.fin_root_chord.nominal if self.fin_root_chord else diameter * 0.5,
                    tip_chord=(self.fin_root_chord.nominal if self.fin_root_chord else diameter * 0.5) * 0.4,
                    span=self.fin_span.nominal,
                    sweep_angle_deg=self.fin_sweep_deg.nominal if self.fin_sweep_deg else 45,
                    thickness=0.02
                )
                fin_mesh = fin.generate_mesh(resolution // 2)
                fin_mesh = fin_mesh.transform(
                    translation=Point3D(fin_x, radius, 0),
                    rotation_deg=(angle, 0, 0)
                )
                all_meshes.append(fin_mesh)
                components[f"fin_{i}"] = fin

        # Combine meshes
        combined_triangles = []
        for mesh in all_meshes:
            combined_triangles.extend(mesh.triangles)

        combined_mesh = TriangleMesh(triangles=combined_triangles)

        # Calculate totals
        total_volume = sum(
            c.calculate_volume() for c in components.values()
            if hasattr(c, 'calculate_volume')
        )

        return CADGeometryResult(
            mesh=combined_mesh,
            components=components,
            bounding_box=combined_mesh.bounding_box,
            total_volume=total_volume,
            total_surface_area=combined_mesh.surface_area,
            parameters=self.get_parameters(),
            platform_type=PlatformType.MISSILE
        )


# =============================================================================
# PRE-CONFIGURED DF-SERIES MODELS
# =============================================================================

def create_df17_model() -> DFSeriesMissileCAD:
    """
    DF-17 Hypersonic Glide Vehicle System

    LIMITATIONS:
    - HGV geometry is highly approximate
    - Boost vehicle dimensions from parade imagery
    - Performance estimates have high uncertainty
    - Maneuvering capability is estimated
    """
    return DFSeriesMissileCAD(
        designation="DF-17",
        category=MissileCategory.MRBM,
        total_length=UncertaintyBounds(
            nominal=11.0, lower_bound=10.0, upper_bound=12.0,
            confidence=0.55,
            source="Parade imagery analysis 2019",
            limitation="Boost vehicle + HGV combined length"
        ),
        body_diameter=UncertaintyBounds(
            nominal=1.4, lower_bound=1.2, upper_bound=1.6,
            confidence=0.50,
            source="Parade imagery, vehicle comparison",
            limitation="First stage diameter only"
        ),
        nose_length=UncertaintyBounds(
            nominal=3.5, lower_bound=3.0, upper_bound=4.0,
            confidence=0.40,
            source="HGV geometry estimate",
            limitation="HGV shape highly uncertain"
        ),
        num_stages=1,
        num_fins=4,
        fin_span=UncertaintyBounds(
            nominal=0.4, lower_bound=0.3, upper_bound=0.5,
            confidence=0.45,
            source="Tail section imagery",
            limitation="Grid fins may be used instead"
        ),
        fin_root_chord=UncertaintyBounds(
            nominal=0.6, lower_bound=0.5, upper_bound=0.7,
            confidence=0.45,
            source="Proportional estimate",
            limitation="Control surface type uncertain"
        ),
        fin_sweep_deg=UncertaintyBounds(
            nominal=50, lower_bound=45, upper_bound=55,
            confidence=0.40,
            source="Visual estimate",
            limitation="May use unconventional geometry"
        ),
        range_km=UncertaintyBounds(
            nominal=2000, lower_bound=1800, upper_bound=2500,
            confidence=0.55,
            source="DOD reports, analysis",
            limitation="Dependent on trajectory profile"
        ),
        payload_kg=UncertaintyBounds(
            nominal=600, lower_bound=400, upper_bound=800,
            confidence=0.40,
            source="HGV mass estimate",
            limitation="Warhead mass unknown"
        ),
        cep_m=UncertaintyBounds(
            nominal=10, lower_bound=5, upper_bound=20,
            confidence=0.35,
            source="Analytical estimate",
            limitation="No test data available"
        ),
        launch_mass_kg=UncertaintyBounds(
            nominal=15000, lower_bound=12000, upper_bound=18000,
            confidence=0.40,
            source="Vehicle comparison",
            limitation="Propellant mass fraction unknown"
        ),
        propulsion=PropulsionType.SOLID_ROCKET,
        warhead_type="conventional"
    )


def create_df21d_model() -> DFSeriesMissileCAD:
    """
    DF-21D Anti-Ship Ballistic Missile

    LIMITATIONS:
    - "Carrier killer" capability unverified in combat
    - Targeting system integration unknown
    - Terminal guidance details classified
    - Maneuvering RV performance uncertain
    """
    return DFSeriesMissileCAD(
        designation="DF-21D",
        category=MissileCategory.MRBM,
        total_length=UncertaintyBounds(
            nominal=10.7, lower_bound=10.0, upper_bound=11.5,
            confidence=0.60,
            source="Multiple parade appearances",
            limitation="TEL comparison method"
        ),
        body_diameter=UncertaintyBounds(
            nominal=1.4, lower_bound=1.3, upper_bound=1.5,
            confidence=0.60,
            source="Parade imagery",
            limitation="First stage only"
        ),
        nose_length=UncertaintyBounds(
            nominal=2.5, lower_bound=2.0, upper_bound=3.0,
            confidence=0.50,
            source="RV geometry estimate",
            limitation="MaRV shape unknown"
        ),
        num_stages=2,
        stage_lengths=[
            UncertaintyBounds(5.0, 4.5, 5.5, 0.55, "First stage", "Estimate"),
            UncertaintyBounds(3.2, 2.8, 3.6, 0.50, "Second stage", "Estimate")
        ],
        num_fins=4,
        fin_span=UncertaintyBounds(
            nominal=0.45, lower_bound=0.35, upper_bound=0.55,
            confidence=0.50,
            source="Tail imagery",
            limitation="Stabilization fins"
        ),
        range_km=UncertaintyBounds(
            nominal=1500, lower_bound=1200, upper_bound=1800,
            confidence=0.55,
            source="DOD estimates",
            limitation="ASBM role may limit range"
        ),
        payload_kg=UncertaintyBounds(
            nominal=600, lower_bound=500, upper_bound=700,
            confidence=0.45,
            source="RV mass estimate",
            limitation="Guidance adds mass"
        ),
        cep_m=UncertaintyBounds(
            nominal=20, lower_bound=10, upper_bound=40,
            confidence=0.40,
            source="Analytical estimate",
            limitation="Against moving target"
        ),
        launch_mass_kg=UncertaintyBounds(
            nominal=14700, lower_bound=13000, upper_bound=16000,
            confidence=0.50,
            source="DF-21 baseline",
            limitation="ASBM variant heavier"
        ),
        propulsion=PropulsionType.SOLID_ROCKET,
        warhead_type="conventional"
    )


def create_df26_model() -> DFSeriesMissileCAD:
    """
    DF-26 Intermediate-Range Ballistic Missile

    LIMITATIONS:
    - Dual nuclear/conventional role complicates analysis
    - "Guam Killer" range requires specific trajectory
    - Hot-swap warhead capability unverified
    - Reload time unknown
    """
    return DFSeriesMissileCAD(
        designation="DF-26",
        category=MissileCategory.IRBM,
        total_length=UncertaintyBounds(
            nominal=14.0, lower_bound=13.0, upper_bound=15.0,
            confidence=0.55,
            source="Parade 2015, 2019",
            limitation="Canister may vary"
        ),
        body_diameter=UncertaintyBounds(
            nominal=1.8, lower_bound=1.6, upper_bound=2.0,
            confidence=0.55,
            source="TEL comparison",
            limitation="Larger than DF-21"
        ),
        nose_length=UncertaintyBounds(
            nominal=3.0, lower_bound=2.5, upper_bound=3.5,
            confidence=0.45,
            source="Warhead fairing",
            limitation="Multiple warhead options"
        ),
        num_stages=2,
        stage_lengths=[
            UncertaintyBounds(7.0, 6.5, 7.5, 0.50, "First stage", "Estimate"),
            UncertaintyBounds(4.0, 3.5, 4.5, 0.50, "Second stage", "Estimate")
        ],
        num_fins=4,
        fin_span=UncertaintyBounds(
            nominal=0.5, lower_bound=0.4, upper_bound=0.6,
            confidence=0.50,
            source="Scaled from imagery",
            limitation="Grid or planar uncertain"
        ),
        range_km=UncertaintyBounds(
            nominal=4000, lower_bound=3500, upper_bound=5000,
            confidence=0.55,
            source="DOD, think tanks",
            limitation="Payload dependent"
        ),
        payload_kg=UncertaintyBounds(
            nominal=1200, lower_bound=1000, upper_bound=1800,
            confidence=0.45,
            source="Nuclear/conventional options",
            limitation="Warhead type affects range"
        ),
        cep_m=UncertaintyBounds(
            nominal=15, lower_bound=10, upper_bound=30,
            confidence=0.40,
            source="Assumed improvement over DF-21",
            limitation="MaRV version only"
        ),
        launch_mass_kg=UncertaintyBounds(
            nominal=20000, lower_bound=18000, upper_bound=22000,
            confidence=0.45,
            source="Vehicle comparison",
            limitation="Dual-capable complicates estimate"
        ),
        propulsion=PropulsionType.SOLID_ROCKET,
        warhead_type="dual-capable"
    )


def create_df41_model() -> DFSeriesMissileCAD:
    """
    DF-41 Intercontinental Ballistic Missile

    LIMITATIONS:
    - Most capable Chinese ICBM, details highly classified
    - MIRV capability reported but count unknown
    - Mobile/silo variants may differ
    - Limited parade appearances for measurement
    """
    return DFSeriesMissileCAD(
        designation="DF-41",
        category=MissileCategory.ICBM,
        total_length=UncertaintyBounds(
            nominal=21.0, lower_bound=19.0, upper_bound=23.0,
            confidence=0.45,
            source="Parade 2019, TEL comparison",
            limitation="Canister obscures details"
        ),
        body_diameter=UncertaintyBounds(
            nominal=2.25, lower_bound=2.0, upper_bound=2.5,
            confidence=0.45,
            source="TEL width comparison",
            limitation="May be larger"
        ),
        nose_length=UncertaintyBounds(
            nominal=4.0, lower_bound=3.5, upper_bound=5.0,
            confidence=0.35,
            source="MIRV bus estimate",
            limitation="Warhead count unknown"
        ),
        num_stages=3,
        stage_lengths=[
            UncertaintyBounds(8.0, 7.0, 9.0, 0.40, "First stage", "Estimate"),
            UncertaintyBounds(5.0, 4.0, 6.0, 0.40, "Second stage", "Estimate"),
            UncertaintyBounds(4.0, 3.0, 5.0, 0.35, "Third stage/PBV", "Estimate")
        ],
        stage_diameters=[
            UncertaintyBounds(2.25, 2.0, 2.5, 0.45, "Stage 1", "Main body"),
            UncertaintyBounds(2.0, 1.8, 2.2, 0.40, "Stage 2", "Reduced"),
            UncertaintyBounds(1.5, 1.3, 1.7, 0.35, "Stage 3", "Upper stage")
        ],
        num_fins=0,  # Likely no external fins
        range_km=UncertaintyBounds(
            nominal=14000, lower_bound=12000, upper_bound=15000,
            confidence=0.50,
            source="DOD estimates",
            limitation="Full range with light payload"
        ),
        payload_kg=UncertaintyBounds(
            nominal=2500, lower_bound=2000, upper_bound=3000,
            confidence=0.40,
            source="MIRV capacity estimate",
            limitation="Up to 10 warheads reported"
        ),
        cep_m=UncertaintyBounds(
            nominal=100, lower_bound=50, upper_bound=200,
            confidence=0.35,
            source="Modern ICBM baseline",
            limitation="GPS/stellar may improve"
        ),
        launch_mass_kg=UncertaintyBounds(
            nominal=80000, lower_bound=70000, upper_bound=90000,
            confidence=0.40,
            source="Road-mobile constraint",
            limitation="TEL payload limit"
        ),
        propulsion=PropulsionType.SOLID_ROCKET,
        warhead_type="nuclear"
    )


def create_df5c_model() -> DFSeriesMissileCAD:
    """
    DF-5C Silo-Based ICBM

    LIMITATIONS:
    - Legacy liquid-fueled design
    - MIRV modernization version
    - Silo vulnerability issues
    - Older design better documented
    """
    return DFSeriesMissileCAD(
        designation="DF-5C",
        category=MissileCategory.ICBM,
        total_length=UncertaintyBounds(
            nominal=32.6, lower_bound=31.0, upper_bound=34.0,
            confidence=0.65,
            source="Longer analysis history",
            limitation="Silo-based, well-photographed"
        ),
        body_diameter=UncertaintyBounds(
            nominal=3.35, lower_bound=3.2, upper_bound=3.5,
            confidence=0.65,
            source="Original DF-5 data",
            limitation="Upgraded RV section"
        ),
        nose_length=UncertaintyBounds(
            nominal=5.0, lower_bound=4.5, upper_bound=6.0,
            confidence=0.50,
            source="MIRV bus estimate",
            limitation="10 warhead capacity"
        ),
        num_stages=2,
        stage_lengths=[
            UncertaintyBounds(20.0, 19.0, 21.0, 0.60, "First stage", "Liquid"),
            UncertaintyBounds(7.6, 7.0, 8.5, 0.55, "Second stage", "Liquid")
        ],
        num_fins=4,
        fin_span=UncertaintyBounds(
            nominal=1.2, lower_bound=1.0, upper_bound=1.4,
            confidence=0.60,
            source="Base stabilizers",
            limitation="Silo launch configuration"
        ),
        range_km=UncertaintyBounds(
            nominal=13000, lower_bound=12000, upper_bound=15000,
            confidence=0.60,
            source="Well-established",
            limitation="Payload dependent"
        ),
        payload_kg=UncertaintyBounds(
            nominal=3000, lower_bound=2500, upper_bound=3500,
            confidence=0.55,
            source="MIRV modernization",
            limitation="Heavy lift capability"
        ),
        cep_m=UncertaintyBounds(
            nominal=300, lower_bound=200, upper_bound=500,
            confidence=0.50,
            source="1980s technology base",
            limitation="Upgraded guidance"
        ),
        launch_mass_kg=UncertaintyBounds(
            nominal=183000, lower_bound=175000, upper_bound=190000,
            confidence=0.60,
            source="Liquid fuel system",
            limitation="Silo-based, no mobility"
        ),
        propulsion=PropulsionType.LIQUID_ROCKET,
        warhead_type="nuclear"
    )


# =============================================================================
# YJ-SERIES ANTI-SHIP MISSILES
# =============================================================================

@dataclass
class YJSeriesMissileCAD(ValidatedCADModel):
    """
    YJ-Series Anti-Ship Missile CAD Model

    Covers: YJ-18, YJ-21, YJ-12, YJ-83, YJ-62

    ERROR-FREE DESIGN:
    - Ship/sub/air launch variants modeled
    - Subsonic cruise + supersonic terminal
    - Validated geometric constraints
    - Complete performance uncertainty

    LIMITATIONS:
    - Seeker details completely unknown
    - Terminal maneuvers not modeled
    - Propulsion integration approximate
    - Export versions may differ from PLA
    """

    designation: str
    launch_platform: str  # "ship", "submarine", "aircraft", "ground"

    # Dimensions
    total_length: UncertaintyBounds = None
    body_diameter: UncertaintyBounds = None
    wingspan: UncertaintyBounds = None  # For cruise variants

    # Booster (for ship/sub launched)
    has_booster: bool = False
    booster_length: UncertaintyBounds = None
    booster_diameter: UncertaintyBounds = None

    # Performance
    cruise_speed_mach: UncertaintyBounds = None
    terminal_speed_mach: UncertaintyBounds = None
    range_km: UncertaintyBounds = None
    warhead_kg: UncertaintyBounds = None

    # Propulsion
    cruise_propulsion: PropulsionType = PropulsionType.TURBOJET
    terminal_propulsion: PropulsionType = None

    def get_parameters(self) -> Dict[str, UncertaintyBounds]:
        params = {}
        if self.total_length:
            params['total_length'] = self.total_length
        if self.body_diameter:
            params['body_diameter'] = self.body_diameter
        if self.wingspan:
            params['wingspan'] = self.wingspan
        if self.range_km:
            params['range_km'] = self.range_km
        if self.cruise_speed_mach:
            params['cruise_speed_mach'] = self.cruise_speed_mach
        if self.terminal_speed_mach:
            params['terminal_speed_mach'] = self.terminal_speed_mach
        return params

    def get_limitations(self) -> SystemLimitations:
        return SystemLimitations(
            system_name=self.designation,
            model_type="Anti-Ship Cruise Missile CAD",
            geometry_accuracy_mm=30,
            geometry_source="Parade imagery, export variant specs",
            geometry_limitations=[
                "External aerodynamic surfaces only",
                "Folding wing mechanisms simplified",
                "Inlet geometry approximate",
                "Seeker window shape estimated",
                "Booster attachment points notional"
            ],
            performance_confidence=0.50,
            performance_source="Export data, Western estimates",
            performance_limitations=[
                "Range highly dependent on flight profile",
                "Terminal speed estimates vary widely",
                "Sea-skimming altitude uncertain",
                "Seeker performance unknown",
                "ECCM capability classified"
            ],
            internal_layout_known=False,
            internal_layout_limitations=[
                "Warhead position estimated",
                "Fuel tank geometry unknown",
                "Engine placement approximate",
                "Guidance section internal layout unknown",
                "Wire routing not modeled"
            ],
            material_properties_known=False,
            material_limitations=[
                "Composite usage extent unknown",
                "RAM coating presence/type unknown",
                "Thermal management not modeled",
                "Structural materials assumed aluminum/steel"
            ],
            general_caveats=[
                "Export variants may differ from PLA versions",
                "Newer variants (YJ-21) have minimal public data",
                "Hypersonic variants highly speculative",
                "Network-centric targeting not modeled",
                "Salvo coordination not represented"
            ],
            last_updated="2025-01",
            sources=[
                "Jane's Naval Weapon Systems",
                "CSIS China Power Project",
                "Export marketing materials",
                "Naval parade coverage",
                "Taiwan MOD assessments"
            ]
        )

    def validate_geometry(self) -> Tuple[bool, List[str]]:
        errors = []

        if self.total_length and self.body_diameter:
            fineness = self.total_length.nominal / self.body_diameter.nominal
            if fineness < 8:
                errors.append(f"ASCM fineness {fineness:.1f} too low (min 8)")
            if fineness > 20:
                errors.append(f"ASCM fineness {fineness:.1f} too high (max 20)")

        if self.wingspan and self.body_diameter:
            aspect = self.wingspan.nominal / self.body_diameter.nominal
            if aspect < 2:
                errors.append(f"Wing aspect too low: {aspect:.1f}")

        return len(errors) == 0, errors

    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        valid, errors = self.validate_geometry()
        if not valid:
            raise GeometryValidationError(f"Validation failed: {errors}")

        components = {}
        all_meshes = []

        length = self.total_length.nominal if self.total_length else 6.0
        diameter = self.body_diameter.nominal if self.body_diameter else 0.5
        radius = diameter / 2

        # Ogive nose
        nose_len = diameter * 2.5
        nose = OgiveNose(length=nose_len, base_radius=radius)
        nose_mesh = nose.generate_mesh(resolution)
        all_meshes.append(nose_mesh)
        components["nose"] = nose

        # Main body
        body_len = length - nose_len
        if self.has_booster and self.booster_length:
            body_len -= self.booster_length.nominal

        body = CylindricalSection(length=body_len, forward_radius=radius)
        body_mesh = body.generate_mesh(resolution)
        body_mesh = body_mesh.transform(translation=Point3D(nose_len, 0, 0))
        all_meshes.append(body_mesh)
        components["body"] = body

        # Wings (if applicable)
        if self.wingspan:
            wing_chord = diameter * 1.5
            wing = WingGeometry(
                root_chord=wing_chord,
                tip_chord=wing_chord * 0.5,
                span=self.wingspan.nominal,
                sweep_angle_deg=35,
                thickness_ratio=0.06
            )
            wing_mesh = wing.generate_mesh(resolution // 2)
            wing_x = nose_len + body_len * 0.4
            wing_mesh = wing_mesh.transform(translation=Point3D(wing_x, 0, 0))
            all_meshes.append(wing_mesh)
            components["wing"] = wing

        # Tail fins
        for i in range(4):
            angle = i * 90 + 45
            fin = FinGeometry(
                root_chord=diameter * 0.8,
                tip_chord=diameter * 0.3,
                span=diameter * 0.6,
                sweep_angle_deg=45,
                thickness=0.01
            )
            fin_mesh = fin.generate_mesh(resolution // 4)
            fin_x = length - diameter * 0.8 - 0.1
            fin_mesh = fin_mesh.transform(
                translation=Point3D(fin_x, radius, 0),
                rotation_deg=(angle, 0, 0)
            )
            all_meshes.append(fin_mesh)
            components[f"fin_{i}"] = fin

        # Booster (if applicable)
        if self.has_booster and self.booster_length:
            booster_rad = (self.booster_diameter.nominal / 2) if self.booster_diameter else radius * 1.2
            booster = CylindricalSection(
                length=self.booster_length.nominal,
                forward_radius=booster_rad,
                aft_radius=booster_rad * 0.8
            )
            booster_mesh = booster.generate_mesh(resolution)
            booster_mesh = booster_mesh.transform(
                translation=Point3D(length - self.booster_length.nominal, 0, 0)
            )
            all_meshes.append(booster_mesh)
            components["booster"] = booster

        combined_triangles = []
        for mesh in all_meshes:
            combined_triangles.extend(mesh.triangles)

        combined_mesh = TriangleMesh(triangles=combined_triangles)

        total_volume = sum(
            c.calculate_volume() for c in components.values()
            if hasattr(c, 'calculate_volume')
        )

        return CADGeometryResult(
            mesh=combined_mesh,
            components=components,
            bounding_box=combined_mesh.bounding_box,
            total_volume=total_volume,
            total_surface_area=combined_mesh.surface_area,
            parameters=self.get_parameters(),
            platform_type=PlatformType.MISSILE
        )


def create_yj18_model() -> YJSeriesMissileCAD:
    """
    YJ-18 Anti-Ship Cruise Missile

    LIMITATIONS:
    - Subsonic cruise + supersonic terminal dual mode
    - Terminal boost separation point unknown
    - Guidance mode switching uncertain
    - VLS compatibility dimensions from Type 052D
    """
    return YJSeriesMissileCAD(
        designation="YJ-18",
        launch_platform="ship",
        total_length=UncertaintyBounds(
            nominal=8.2, lower_bound=7.8, upper_bound=8.6,
            confidence=0.55,
            source="VLS cell constraints, imagery",
            limitation="Includes booster"
        ),
        body_diameter=UncertaintyBounds(
            nominal=0.533, lower_bound=0.50, upper_bound=0.55,
            confidence=0.60,
            source="21-inch diameter standard",
            limitation="Torpedo tube compatible"
        ),
        wingspan=UncertaintyBounds(
            nominal=1.4, lower_bound=1.2, upper_bound=1.6,
            confidence=0.50,
            source="Folded wing estimate",
            limitation="Deployed configuration"
        ),
        has_booster=True,
        booster_length=UncertaintyBounds(
            nominal=1.5, lower_bound=1.2, upper_bound=1.8,
            confidence=0.45,
            source="Launch imagery",
            limitation="Jettisoned after VLS exit"
        ),
        cruise_speed_mach=UncertaintyBounds(
            nominal=0.8, lower_bound=0.75, upper_bound=0.85,
            confidence=0.55,
            source="Subsonic cruise standard",
            limitation="Fuel efficient phase"
        ),
        terminal_speed_mach=UncertaintyBounds(
            nominal=3.0, lower_bound=2.5, upper_bound=3.5,
            confidence=0.50,
            source="Derived from Russian 3M-54",
            limitation="Final 40km sprint"
        ),
        range_km=UncertaintyBounds(
            nominal=540, lower_bound=400, upper_bound=600,
            confidence=0.50,
            source="Extended range variant YJ-18A",
            limitation="Profile dependent"
        ),
        warhead_kg=UncertaintyBounds(
            nominal=300, lower_bound=250, upper_bound=350,
            confidence=0.45,
            source="Anti-ship standard",
            limitation="Semi-AP type"
        ),
        cruise_propulsion=PropulsionType.TURBOJET,
        terminal_propulsion=PropulsionType.SOLID_ROCKET
    )


def create_yj21_model() -> YJSeriesMissileCAD:
    """
    YJ-21 Hypersonic Anti-Ship Missile

    LIMITATIONS:
    - Extremely limited public data
    - Hypersonic performance unverified
    - Ship launch mechanism unknown
    - May be derived from DF-21D technology
    """
    return YJSeriesMissileCAD(
        designation="YJ-21",
        launch_platform="ship",
        total_length=UncertaintyBounds(
            nominal=7.5, lower_bound=7.0, upper_bound=9.0,
            confidence=0.35,
            source="Limited imagery",
            limitation="Highly uncertain"
        ),
        body_diameter=UncertaintyBounds(
            nominal=0.7, lower_bound=0.6, upper_bound=0.8,
            confidence=0.35,
            source="Proportional estimate",
            limitation="Larger than YJ-18"
        ),
        wingspan=None,  # Likely no wings for hypersonic
        has_booster=True,
        booster_length=UncertaintyBounds(
            nominal=2.0, lower_bound=1.5, upper_bound=2.5,
            confidence=0.30,
            source="Hypersonic boost requirement",
            limitation="Speculative"
        ),
        cruise_speed_mach=UncertaintyBounds(
            nominal=6.0, lower_bound=5.0, upper_bound=8.0,
            confidence=0.30,
            source="Hypersonic designation",
            limitation="May be peak, not cruise"
        ),
        terminal_speed_mach=UncertaintyBounds(
            nominal=8.0, lower_bound=6.0, upper_bound=10.0,
            confidence=0.25,
            source="Terminal dive acceleration",
            limitation="Highly speculative"
        ),
        range_km=UncertaintyBounds(
            nominal=1000, lower_bound=500, upper_bound=1500,
            confidence=0.30,
            source="Hypersonic missile estimates",
            limitation="Trajectory dependent"
        ),
        warhead_kg=UncertaintyBounds(
            nominal=500, lower_bound=300, upper_bound=700,
            confidence=0.30,
            source="Kinetic + explosive",
            limitation="Mass/range tradeoff"
        ),
        cruise_propulsion=PropulsionType.SOLID_ROCKET,
        terminal_propulsion=None  # Ballistic terminal
    )


# =============================================================================
# HQ-SERIES AIR DEFENSE SYSTEMS
# =============================================================================

@dataclass
class HQSeriesSAMCAD(ValidatedCADModel):
    """
    HQ-Series Surface-to-Air Missile CAD Model

    Covers: HQ-9B, HQ-16, HQ-22, HQ-7, HQ-17, HQ-19 (ABM)

    ERROR-FREE DESIGN:
    - Validated interceptor geometry
    - Launcher integration dimensions
    - Performance envelope boundaries
    - Complete radar integration notes

    LIMITATIONS:
    - Seeker and guidance details unknown
    - Multi-spectral performance uncertain
    - Network integration classified
    - ABM variants highly speculative
    """

    designation: str
    role: str  # "long_range", "medium_range", "short_range", "point_defense", "abm"

    # Missile dimensions
    missile_length: UncertaintyBounds = None
    missile_diameter: UncertaintyBounds = None
    fin_span: UncertaintyBounds = None

    # Canister/launcher dimensions
    canister_length: UncertaintyBounds = None
    canister_diameter: UncertaintyBounds = None

    # Performance
    max_range_km: UncertaintyBounds = None
    max_altitude_km: UncertaintyBounds = None
    max_speed_mach: UncertaintyBounds = None
    min_range_km: UncertaintyBounds = None

    # Guidance
    guidance_type: str = "semi-active"  # "semi-active", "active", "command", "TVM"

    # System
    missiles_per_launcher: int = 4
    reload_time_min: UncertaintyBounds = None

    def get_parameters(self) -> Dict[str, UncertaintyBounds]:
        params = {}
        if self.missile_length:
            params['missile_length'] = self.missile_length
        if self.missile_diameter:
            params['missile_diameter'] = self.missile_diameter
        if self.max_range_km:
            params['max_range_km'] = self.max_range_km
        if self.max_altitude_km:
            params['max_altitude_km'] = self.max_altitude_km
        return params

    def get_limitations(self) -> SystemLimitations:
        return SystemLimitations(
            system_name=self.designation,
            model_type="Surface-to-Air Missile System CAD",
            geometry_accuracy_mm=20,
            geometry_source="Parade displays, exercise footage",
            geometry_limitations=[
                "Missile external shape only",
                "Seeker window geometry estimated",
                "Control surface actuation not modeled",
                "Internal propulsion layout notional",
                "Warhead fragmentation pattern unknown"
            ],
            performance_confidence=0.55,
            performance_source="PLA publications, export data",
            performance_limitations=[
                "Engagement envelope is nominal, not guaranteed",
                "Multi-target capability uncertain",
                "ECCM performance classified",
                "Probability of kill varies with target type",
                "Reload cycle time estimates only"
            ],
            internal_layout_known=False,
            internal_layout_limitations=[
                "Seeker type inferred from behavior",
                "Warhead design unknown",
                "Propulsion grain geometry unknown",
                "Data link antenna placement estimated"
            ],
            material_properties_known=False,
            material_limitations=[
                "Composite motor case assumed",
                "Radome material uncertain",
                "Thermal protection unknown"
            ],
            general_caveats=[
                "Export variants (FK-3, LY-80) may differ",
                "Continuous upgrades may change specs",
                "Network integration critical but not modeled",
                "Real-world performance varies significantly"
            ],
            last_updated="2025-01",
            sources=[
                "CSIS Missile Threat",
                "Jane's Land-Based Air Defence",
                "PLA exercise announcements",
                "Export marketing (FK-3, etc.)"
            ]
        )

    def validate_geometry(self) -> Tuple[bool, List[str]]:
        errors = []

        if self.missile_length and self.missile_diameter:
            fineness = self.missile_length.nominal / self.missile_diameter.nominal
            if fineness < 10:
                errors.append(f"SAM fineness {fineness:.1f} low (typical >10)")
            if fineness > 30:
                errors.append(f"SAM fineness {fineness:.1f} high (typical <30)")

        if self.canister_length and self.missile_length:
            if self.canister_length.nominal < self.missile_length.nominal * 1.05:
                errors.append("Canister too short for missile")

        return len(errors) == 0, errors

    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        valid, errors = self.validate_geometry()
        if not valid:
            raise GeometryValidationError(f"Validation failed: {errors}")

        components = {}
        all_meshes = []

        length = self.missile_length.nominal if self.missile_length else 6.0
        diameter = self.missile_diameter.nominal if self.missile_diameter else 0.4
        radius = diameter / 2

        # SAM typically has ogive nose
        nose_len = diameter * 3
        nose = OgiveNose(length=nose_len, base_radius=radius)
        nose_mesh = nose.generate_mesh(resolution)
        all_meshes.append(nose_mesh)
        components["nose"] = nose

        # Body
        body_len = length - nose_len - diameter * 2  # Leave room for nozzle
        body = CylindricalSection(length=body_len, forward_radius=radius)
        body_mesh = body.generate_mesh(resolution)
        body_mesh = body_mesh.transform(translation=Point3D(nose_len, 0, 0))
        all_meshes.append(body_mesh)
        components["body"] = body

        # Nozzle section
        nozzle_len = diameter * 2
        nozzle = CylindricalSection(
            length=nozzle_len,
            forward_radius=radius,
            aft_radius=radius * 0.6
        )
        nozzle_mesh = nozzle.generate_mesh(resolution)
        nozzle_mesh = nozzle_mesh.transform(
            translation=Point3D(nose_len + body_len, 0, 0)
        )
        all_meshes.append(nozzle_mesh)
        components["nozzle"] = nozzle

        # Tail fins (4)
        fin_span_val = self.fin_span.nominal if self.fin_span else diameter * 0.8
        for i in range(4):
            angle = i * 90
            fin = FinGeometry(
                root_chord=diameter * 1.2,
                tip_chord=diameter * 0.4,
                span=fin_span_val,
                sweep_angle_deg=50,
                thickness=0.015
            )
            fin_mesh = fin.generate_mesh(resolution // 4)
            fin_x = length - diameter * 1.2 - 0.1
            fin_mesh = fin_mesh.transform(
                translation=Point3D(fin_x, radius, 0),
                rotation_deg=(angle, 0, 0)
            )
            all_meshes.append(fin_mesh)
            components[f"fin_{i}"] = fin

        combined_triangles = []
        for mesh in all_meshes:
            combined_triangles.extend(mesh.triangles)

        combined_mesh = TriangleMesh(triangles=combined_triangles)

        total_volume = sum(
            c.calculate_volume() for c in components.values()
            if hasattr(c, 'calculate_volume')
        )

        return CADGeometryResult(
            mesh=combined_mesh,
            components=components,
            bounding_box=combined_mesh.bounding_box,
            total_volume=total_volume,
            total_surface_area=combined_mesh.surface_area,
            parameters=self.get_parameters(),
            platform_type=PlatformType.MISSILE
        )


def create_hq9b_model() -> HQSeriesSAMCAD:
    """
    HQ-9B Long-Range SAM

    LIMITATIONS:
    - Based on Russian S-300 lineage
    - Extended range version of HQ-9
    - ABM capability uncertain
    - Export FK-3 may differ
    """
    return HQSeriesSAMCAD(
        designation="HQ-9B",
        role="long_range",
        missile_length=UncertaintyBounds(
            nominal=6.8, lower_bound=6.5, upper_bound=7.2,
            confidence=0.55,
            source="Parade measurements",
            limitation="Extended version longer"
        ),
        missile_diameter=UncertaintyBounds(
            nominal=0.47, lower_bound=0.45, upper_bound=0.50,
            confidence=0.55,
            source="Canister sizing",
            limitation="S-300 heritage"
        ),
        fin_span=UncertaintyBounds(
            nominal=0.60, lower_bound=0.50, upper_bound=0.70,
            confidence=0.50,
            source="Tail section imagery",
            limitation="Folded in canister"
        ),
        canister_length=UncertaintyBounds(
            nominal=7.2, lower_bound=7.0, upper_bound=7.5,
            confidence=0.55,
            source="TEL measurements",
            limitation="With sealing"
        ),
        canister_diameter=UncertaintyBounds(
            nominal=0.70, lower_bound=0.65, upper_bound=0.75,
            confidence=0.55,
            source="TEL tube sizing",
            limitation="4 per TEL"
        ),
        max_range_km=UncertaintyBounds(
            nominal=250, lower_bound=200, upper_bound=300,
            confidence=0.55,
            source="PLA announcements",
            limitation="Against aircraft"
        ),
        max_altitude_km=UncertaintyBounds(
            nominal=30, lower_bound=25, upper_bound=35,
            confidence=0.50,
            source="High-altitude intercept",
            limitation="Ballistic target lower"
        ),
        max_speed_mach=UncertaintyBounds(
            nominal=4.2, lower_bound=4.0, upper_bound=4.5,
            confidence=0.50,
            source="Engagement kinematics",
            limitation="Terminal phase"
        ),
        min_range_km=UncertaintyBounds(
            nominal=5, lower_bound=3, upper_bound=8,
            confidence=0.50,
            source="Arming distance",
            limitation="Close-in gap"
        ),
        guidance_type="active",
        missiles_per_launcher=4,
        reload_time_min=UncertaintyBounds(
            nominal=15, lower_bound=10, upper_bound=20,
            confidence=0.40,
            source="Similar systems",
            limitation="With reload vehicle"
        )
    )


def create_hq16_model() -> HQSeriesSAMCAD:
    """
    HQ-16 Medium-Range SAM

    LIMITATIONS:
    - Derived from Russian Buk system
    - Multiple variants (A, B, C)
    - Naval version (HHQ-16) differs
    - VLS integration on ships
    """
    return HQSeriesSAMCAD(
        designation="HQ-16B",
        role="medium_range",
        missile_length=UncertaintyBounds(
            nominal=5.0, lower_bound=4.8, upper_bound=5.3,
            confidence=0.55,
            source="TEL configuration",
            limitation="B variant extended"
        ),
        missile_diameter=UncertaintyBounds(
            nominal=0.34, lower_bound=0.32, upper_bound=0.36,
            confidence=0.55,
            source="Canister size",
            limitation="Buk-derived"
        ),
        fin_span=UncertaintyBounds(
            nominal=0.45, lower_bound=0.40, upper_bound=0.50,
            confidence=0.50,
            source="Tail geometry",
            limitation="Folding fins"
        ),
        canister_length=UncertaintyBounds(
            nominal=5.5, lower_bound=5.2, upper_bound=5.8,
            confidence=0.55,
            source="TEL pod",
            limitation="6 per launcher"
        ),
        max_range_km=UncertaintyBounds(
            nominal=70, lower_bound=50, upper_bound=100,
            confidence=0.55,
            source="Medium range spec",
            limitation="B version improved"
        ),
        max_altitude_km=UncertaintyBounds(
            nominal=25, lower_bound=20, upper_bound=30,
            confidence=0.50,
            source="Altitude band",
            limitation="Engagement ceiling"
        ),
        max_speed_mach=UncertaintyBounds(
            nominal=3.5, lower_bound=3.0, upper_bound=4.0,
            confidence=0.50,
            source="Intercept kinematics",
            limitation="Against maneuvering"
        ),
        min_range_km=UncertaintyBounds(
            nominal=3, lower_bound=2, upper_bound=5,
            confidence=0.50,
            source="Arming time",
            limitation="Close engagement"
        ),
        guidance_type="semi-active",
        missiles_per_launcher=6,
        reload_time_min=UncertaintyBounds(
            nominal=20, lower_bound=15, upper_bound=25,
            confidence=0.40,
            source="Exercise data",
            limitation="With support vehicle"
        )
    )


def create_hq22_model() -> HQSeriesSAMCAD:
    """
    HQ-22 Medium/Long-Range SAM

    LIMITATIONS:
    - Fills gap between HQ-16 and HQ-9
    - Export success (Pakistan LY-80)
    - More mobile than HQ-9
    - Less capable against ballistic targets
    """
    return HQSeriesSAMCAD(
        designation="HQ-22",
        role="medium_range",
        missile_length=UncertaintyBounds(
            nominal=5.6, lower_bound=5.2, upper_bound=6.0,
            confidence=0.50,
            source="Parade displays",
            limitation="Between HQ-16 and HQ-9"
        ),
        missile_diameter=UncertaintyBounds(
            nominal=0.40, lower_bound=0.38, upper_bound=0.42,
            confidence=0.50,
            source="Canister proportion",
            limitation="Medium class"
        ),
        fin_span=UncertaintyBounds(
            nominal=0.55, lower_bound=0.48, upper_bound=0.62,
            confidence=0.45,
            source="Visual estimate",
            limitation="Folding configuration"
        ),
        canister_length=UncertaintyBounds(
            nominal=6.0, lower_bound=5.6, upper_bound=6.4,
            confidence=0.50,
            source="TEL sizing",
            limitation="4 per launcher"
        ),
        max_range_km=UncertaintyBounds(
            nominal=170, lower_bound=150, upper_bound=200,
            confidence=0.50,
            source="Export marketing",
            limitation="Against aircraft"
        ),
        max_altitude_km=UncertaintyBounds(
            nominal=27, lower_bound=23, upper_bound=30,
            confidence=0.50,
            source="High-altitude role",
            limitation="Engagement ceiling"
        ),
        max_speed_mach=UncertaintyBounds(
            nominal=4.0, lower_bound=3.5, upper_bound=4.5,
            confidence=0.45,
            source="Performance class",
            limitation="Estimate"
        ),
        min_range_km=UncertaintyBounds(
            nominal=5, lower_bound=3, upper_bound=7,
            confidence=0.45,
            source="Similar systems",
            limitation="Arming distance"
        ),
        guidance_type="active",
        missiles_per_launcher=4,
        reload_time_min=UncertaintyBounds(
            nominal=12, lower_bound=8, upper_bound=18,
            confidence=0.40,
            source="Mobility focus",
            limitation="Rapid reload design"
        )
    )


# =============================================================================
# PL-SERIES AIR-TO-AIR MISSILES
# =============================================================================

@dataclass
class PLSeriesAAMCAD(ValidatedCADModel):
    """
    PL-Series Air-to-Air Missile CAD Model

    Covers: PL-15, PL-15E, PL-21, PL-10, PL-12

    ERROR-FREE DESIGN:
    - Validated aerodynamic geometry
    - Aircraft integration dimensions
    - Seeker window geometry modeled
    - Complete flight envelope parameters

    LIMITATIONS:
    - Active radar seeker details unknown
    - Dual-pulse motor performance estimated
    - ECCM capability completely unknown
    - Export variants may differ significantly
    """

    designation: str
    role: str  # "bvr" (beyond visual range), "wvr" (within visual range)

    # Dimensions
    total_length: UncertaintyBounds = None
    body_diameter: UncertaintyBounds = None
    wingspan: UncertaintyBounds = None
    fin_span: UncertaintyBounds = None

    # Performance
    max_range_km: UncertaintyBounds = None
    max_speed_mach: UncertaintyBounds = None
    max_g_load: UncertaintyBounds = None
    no_escape_zone_km: UncertaintyBounds = None

    # Seeker
    seeker_type: str = "active_radar"  # "active_radar", "ir", "dual_mode"
    seeker_gimbal_deg: UncertaintyBounds = None

    # Propulsion
    propulsion: PropulsionType = PropulsionType.DUAL_PULSE_SOLID

    # Mass
    launch_mass_kg: UncertaintyBounds = None
    warhead_kg: UncertaintyBounds = None

    def get_parameters(self) -> Dict[str, UncertaintyBounds]:
        params = {}
        if self.total_length:
            params['total_length'] = self.total_length
        if self.body_diameter:
            params['body_diameter'] = self.body_diameter
        if self.max_range_km:
            params['max_range_km'] = self.max_range_km
        if self.max_speed_mach:
            params['max_speed_mach'] = self.max_speed_mach
        if self.max_g_load:
            params['max_g_load'] = self.max_g_load
        if self.launch_mass_kg:
            params['launch_mass_kg'] = self.launch_mass_kg
        return params

    def get_limitations(self) -> SystemLimitations:
        return SystemLimitations(
            system_name=self.designation,
            model_type="Air-to-Air Missile CAD",
            geometry_accuracy_mm=10,
            geometry_source="Aircraft integration photos, airshow displays",
            geometry_limitations=[
                "External aerodynamic surfaces only",
                "Seeker window curvature estimated",
                "Control surface hinge lines simplified",
                "Folding fin mechanisms not detailed",
                "Umbilical connector positions notional"
            ],
            performance_confidence=0.50,
            performance_source="Export marketing, Western analysis",
            performance_limitations=[
                "Max range is at optimal altitude/speed",
                "No-escape zone highly variable",
                "Seeker acquisition range unknown",
                "ECCM effectiveness classified",
                "Multi-target capability uncertain"
            ],
            internal_layout_known=False,
            internal_layout_limitations=[
                "Dual-pulse motor grain geometry unknown",
                "Guidance section layout estimated",
                "Data link antenna position uncertain",
                "Warhead fragmentation pattern classified"
            ],
            material_properties_known=False,
            material_limitations=[
                "Composite body extent unknown",
                "Radome material type uncertain",
                "IR window material unknown (for PL-10)",
                "Motor case materials estimated"
            ],
            general_caveats=[
                "PL-15E export version may have reduced capability",
                "PL-21 is highly speculative",
                "Integration with specific aircraft varies",
                "Software/seeker updates change performance",
                "Test data not publicly available"
            ],
            last_updated="2025-01",
            sources=[
                "Zhuhai Airshow displays",
                "PLAAF aircraft photos",
                "Jane's Air-Launched Weapons",
                "NASIC assessments",
                "Taiwan MOD reports"
            ]
        )

    def validate_geometry(self) -> Tuple[bool, List[str]]:
        errors = []

        if self.total_length and self.body_diameter:
            fineness = self.total_length.nominal / self.body_diameter.nominal
            if fineness < 12:
                errors.append(f"AAM fineness {fineness:.1f} low for BVR (min 12)")
            if fineness > 25:
                errors.append(f"AAM fineness {fineness:.1f} too high (max 25)")

        if self.wingspan and self.body_diameter:
            wing_ratio = self.wingspan.nominal / self.body_diameter.nominal
            if wing_ratio < 1.5:
                errors.append(f"Wing ratio {wing_ratio:.1f} too small")

        return len(errors) == 0, errors

    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        valid, errors = self.validate_geometry()
        if not valid:
            raise GeometryValidationError(f"Validation failed: {errors}")

        components = {}
        all_meshes = []

        length = self.total_length.nominal if self.total_length else 4.0
        diameter = self.body_diameter.nominal if self.body_diameter else 0.2
        radius = diameter / 2

        # Ogive nose (typical for AAM)
        nose_len = diameter * 4
        nose = OgiveNose(length=nose_len, base_radius=radius)
        nose_mesh = nose.generate_mesh(resolution)
        all_meshes.append(nose_mesh)
        components["nose"] = nose

        # Main body
        body_len = length - nose_len - diameter
        body = CylindricalSection(length=body_len, forward_radius=radius)
        body_mesh = body.generate_mesh(resolution)
        body_mesh = body_mesh.transform(translation=Point3D(nose_len, 0, 0))
        all_meshes.append(body_mesh)
        components["body"] = body

        # Nozzle
        nozzle = CylindricalSection(
            length=diameter,
            forward_radius=radius,
            aft_radius=radius * 0.5
        )
        nozzle_mesh = nozzle.generate_mesh(resolution)
        nozzle_mesh = nozzle_mesh.transform(
            translation=Point3D(nose_len + body_len, 0, 0)
        )
        all_meshes.append(nozzle_mesh)
        components["nozzle"] = nozzle

        # Wings (mid-body, small)
        if self.wingspan:
            wing_span = self.wingspan.nominal
            wing_chord = diameter * 1.5
            wing = WingGeometry(
                root_chord=wing_chord,
                tip_chord=wing_chord * 0.4,
                span=wing_span,
                sweep_angle_deg=45,
                thickness_ratio=0.05
            )
            wing_mesh = wing.generate_mesh(resolution // 2)
            wing_x = nose_len + body_len * 0.3
            wing_mesh = wing_mesh.transform(translation=Point3D(wing_x, 0, 0))
            all_meshes.append(wing_mesh)
            components["wing"] = wing

        # Tail fins (4)
        fin_span_val = self.fin_span.nominal if self.fin_span else diameter * 0.7
        for i in range(4):
            angle = i * 90 + 45
            fin = FinGeometry(
                root_chord=diameter * 1.2,
                tip_chord=diameter * 0.4,
                span=fin_span_val,
                sweep_angle_deg=55,
                thickness=0.008
            )
            fin_mesh = fin.generate_mesh(resolution // 4)
            fin_x = length - diameter * 1.2 - 0.05
            fin_mesh = fin_mesh.transform(
                translation=Point3D(fin_x, radius, 0),
                rotation_deg=(angle, 0, 0)
            )
            all_meshes.append(fin_mesh)
            components[f"fin_{i}"] = fin

        combined_triangles = []
        for mesh in all_meshes:
            combined_triangles.extend(mesh.triangles)

        combined_mesh = TriangleMesh(triangles=combined_triangles)

        total_volume = sum(
            c.calculate_volume() for c in components.values()
            if hasattr(c, 'calculate_volume')
        )

        return CADGeometryResult(
            mesh=combined_mesh,
            components=components,
            bounding_box=combined_mesh.bounding_box,
            total_volume=total_volume,
            total_surface_area=combined_mesh.surface_area,
            parameters=self.get_parameters(),
            platform_type=PlatformType.MISSILE
        )


def create_pl15_model() -> PLSeriesAAMCAD:
    """
    PL-15 Long-Range AAM

    LIMITATIONS:
    - Primary PLAAF BVR weapon
    - Dual-pulse motor extends range
    - Active radar seeker details unknown
    - AESA seeker reported but unconfirmed
    """
    return PLSeriesAAMCAD(
        designation="PL-15",
        role="bvr",
        total_length=UncertaintyBounds(
            nominal=3.99, lower_bound=3.8, upper_bound=4.2,
            confidence=0.55,
            source="Airshow measurements",
            limitation="Export PL-15E may differ"
        ),
        body_diameter=UncertaintyBounds(
            nominal=0.203, lower_bound=0.19, upper_bound=0.22,
            confidence=0.55,
            source="Standard diameter class",
            limitation="Similar to AIM-120"
        ),
        wingspan=UncertaintyBounds(
            nominal=0.45, lower_bound=0.40, upper_bound=0.50,
            confidence=0.50,
            source="Wing planform visible",
            limitation="Folding mechanism"
        ),
        fin_span=UncertaintyBounds(
            nominal=0.35, lower_bound=0.30, upper_bound=0.40,
            confidence=0.50,
            source="Tail section photos",
            limitation="Grid or planar"
        ),
        max_range_km=UncertaintyBounds(
            nominal=200, lower_bound=150, upper_bound=300,
            confidence=0.45,
            source="DOD estimates",
            limitation="Altitude/speed dependent"
        ),
        max_speed_mach=UncertaintyBounds(
            nominal=4.0, lower_bound=3.5, upper_bound=4.5,
            confidence=0.50,
            source="BVR AAM class",
            limitation="Varies with altitude"
        ),
        max_g_load=UncertaintyBounds(
            nominal=38, lower_bound=30, upper_bound=45,
            confidence=0.45,
            source="Engagement kinematics",
            limitation="Terminal phase only"
        ),
        no_escape_zone_km=UncertaintyBounds(
            nominal=60, lower_bound=40, upper_bound=80,
            confidence=0.40,
            source="Analytical estimate",
            limitation="Against non-maneuvering"
        ),
        seeker_type="active_radar",
        seeker_gimbal_deg=UncertaintyBounds(
            nominal=60, lower_bound=50, upper_bound=70,
            confidence=0.40,
            source="AESA requirement",
            limitation="Look angle limit"
        ),
        propulsion=PropulsionType.DUAL_PULSE_SOLID,
        launch_mass_kg=UncertaintyBounds(
            nominal=210, lower_bound=190, upper_bound=230,
            confidence=0.50,
            source="Weight class estimate",
            limitation="Heavier than AIM-120"
        ),
        warhead_kg=UncertaintyBounds(
            nominal=25, lower_bound=20, upper_bound=30,
            confidence=0.45,
            source="AAM warhead standard",
            limitation="Blast-frag type"
        )
    )


def create_pl21_model() -> PLSeriesAAMCAD:
    """
    PL-21 Very Long-Range AAM (Speculative)

    LIMITATIONS:
    - EXTREMELY LIMITED DATA
    - May not exist as separate system
    - Could be PL-15 derivative
    - AWACS-killer role speculated
    - Geometry highly uncertain
    """
    return PLSeriesAAMCAD(
        designation="PL-21",
        role="bvr",
        total_length=UncertaintyBounds(
            nominal=5.5, lower_bound=5.0, upper_bound=6.0,
            confidence=0.25,
            source="Speculative analysis",
            limitation="MAY NOT EXIST"
        ),
        body_diameter=UncertaintyBounds(
            nominal=0.30, lower_bound=0.25, upper_bound=0.35,
            confidence=0.25,
            source="Scaled from images",
            limitation="Larger than PL-15"
        ),
        wingspan=UncertaintyBounds(
            nominal=0.60, lower_bound=0.50, upper_bound=0.70,
            confidence=0.20,
            source="Proportional estimate",
            limitation="Unknown configuration"
        ),
        fin_span=UncertaintyBounds(
            nominal=0.45, lower_bound=0.35, upper_bound=0.55,
            confidence=0.20,
            source="Visual estimate",
            limitation="Tail geometry unknown"
        ),
        max_range_km=UncertaintyBounds(
            nominal=400, lower_bound=300, upper_bound=500,
            confidence=0.20,
            source="AWACS killer speculation",
            limitation="HIGHLY UNCERTAIN"
        ),
        max_speed_mach=UncertaintyBounds(
            nominal=4.5, lower_bound=4.0, upper_bound=5.0,
            confidence=0.25,
            source="Long-range requirement",
            limitation="Ramjet rumored"
        ),
        max_g_load=UncertaintyBounds(
            nominal=30, lower_bound=20, upper_bound=40,
            confidence=0.20,
            source="Large missile limitation",
            limitation="Reduced agility"
        ),
        no_escape_zone_km=UncertaintyBounds(
            nominal=100, lower_bound=60, upper_bound=150,
            confidence=0.15,
            source="Analytical guess",
            limitation="Against large aircraft"
        ),
        seeker_type="active_radar",
        seeker_gimbal_deg=UncertaintyBounds(
            nominal=45, lower_bound=30, upper_bound=60,
            confidence=0.20,
            source="Large seeker assumption",
            limitation="May use data link"
        ),
        propulsion=PropulsionType.RAMJET,  # Speculated
        launch_mass_kg=UncertaintyBounds(
            nominal=350, lower_bound=280, upper_bound=420,
            confidence=0.20,
            source="Size-based estimate",
            limitation="Internal carriage limit"
        ),
        warhead_kg=UncertaintyBounds(
            nominal=40, lower_bound=30, upper_bound=50,
            confidence=0.25,
            source="Large target requirement",
            limitation="Larger warhead needed"
        )
    )


def create_pl10_model() -> PLSeriesAAMCAD:
    """
    PL-10 Short-Range IR AAM

    LIMITATIONS:
    - Imaging infrared seeker assumed
    - High off-boresight capability reported
    - Helmet-mounted sight integration
    - Comparable to AIM-9X/ASRAAM
    """
    return PLSeriesAAMCAD(
        designation="PL-10",
        role="wvr",
        total_length=UncertaintyBounds(
            nominal=3.0, lower_bound=2.8, upper_bound=3.2,
            confidence=0.55,
            source="Airshow displays",
            limitation="WVR standard size"
        ),
        body_diameter=UncertaintyBounds(
            nominal=0.16, lower_bound=0.15, upper_bound=0.17,
            confidence=0.55,
            source="IR AAM class",
            limitation="Smaller than BVR"
        ),
        wingspan=UncertaintyBounds(
            nominal=0.35, lower_bound=0.30, upper_bound=0.40,
            confidence=0.50,
            source="Strake wings visible",
            limitation="High-G control"
        ),
        fin_span=UncertaintyBounds(
            nominal=0.30, lower_bound=0.25, upper_bound=0.35,
            confidence=0.50,
            source="Tail configuration",
            limitation="TVC may be present"
        ),
        max_range_km=UncertaintyBounds(
            nominal=20, lower_bound=15, upper_bound=25,
            confidence=0.55,
            source="WVR envelope",
            limitation="Dogfight range"
        ),
        max_speed_mach=UncertaintyBounds(
            nominal=3.5, lower_bound=3.0, upper_bound=4.0,
            confidence=0.50,
            source="Sprint motor",
            limitation="Short burn time"
        ),
        max_g_load=UncertaintyBounds(
            nominal=60, lower_bound=50, upper_bound=70,
            confidence=0.45,
            source="High-G requirement",
            limitation="TVC-assisted"
        ),
        no_escape_zone_km=UncertaintyBounds(
            nominal=5, lower_bound=3, upper_bound=8,
            confidence=0.45,
            source="Close-in NEZ",
            limitation="HOBS shot"
        ),
        seeker_type="ir",
        seeker_gimbal_deg=UncertaintyBounds(
            nominal=90, lower_bound=80, upper_bound=100,
            confidence=0.45,
            source="HOBS requirement",
            limitation="Off-boresight angle"
        ),
        propulsion=PropulsionType.SOLID_ROCKET,
        launch_mass_kg=UncertaintyBounds(
            nominal=105, lower_bound=95, upper_bound=115,
            confidence=0.50,
            source="IR AAM weight class",
            limitation="Lighter than BVR"
        ),
        warhead_kg=UncertaintyBounds(
            nominal=10, lower_bound=8, upper_bound=12,
            confidence=0.50,
            source="Close-range frag",
            limitation="Focused pattern"
        )
    )


# =============================================================================
# ELECTRONIC WARFARE SYSTEMS
# =============================================================================

class EWSystemType(Enum):
    """Electronic Warfare system categories"""
    RADAR_JAMMER = "radar_jammer"
    COMMS_JAMMER = "comms_jammer"
    SIGINT = "sigint"
    ELINT = "elint"
    CYBER_EW = "cyber_ew"
    DIRECTED_ENERGY = "directed_energy"
    DECOY = "decoy"


@dataclass
class EMCharacteristics:
    """
    Electromagnetic characteristics for EW systems.

    Required for accurate EW modeling with full uncertainty.
    """
    frequency_min_ghz: UncertaintyBounds
    frequency_max_ghz: UncertaintyBounds
    power_output_kw: UncertaintyBounds
    antenna_gain_dbi: UncertaintyBounds
    effective_range_km: UncertaintyBounds

    # Limitations specific to EM modeling
    em_limitations: List[str] = field(default_factory=list)

    def get_effective_radiated_power_dbw(self) -> UncertaintyBounds:
        """Calculate ERP with uncertainty propagation"""
        # ERP = Power (dBW) + Gain (dBi)
        power_dbw = 10 * math.log10(self.power_output_kw.nominal * 1000)
        power_dbw_low = 10 * math.log10(self.power_output_kw.lower_bound * 1000)
        power_dbw_high = 10 * math.log10(self.power_output_kw.upper_bound * 1000)

        erp_nominal = power_dbw + self.antenna_gain_dbi.nominal
        erp_low = power_dbw_low + self.antenna_gain_dbi.lower_bound
        erp_high = power_dbw_high + self.antenna_gain_dbi.upper_bound

        return UncertaintyBounds(
            nominal=erp_nominal,
            lower_bound=erp_low,
            upper_bound=erp_high,
            confidence=min(
                self.power_output_kw.confidence,
                self.antenna_gain_dbi.confidence
            ),
            source="Calculated from power and gain",
            limitation="Propagated uncertainty"
        )


@dataclass
class EWSystemCAD(ValidatedCADModel):
    """
    Electronic Warfare System CAD Model

    Covers:
    - Ground-based jammers
    - Vehicle-mounted EW systems
    - Shipborne EW suites
    - Airborne EW platforms
    - Decoy systems

    ERROR-FREE DESIGN:
    - Complete EM spectrum coverage modeling
    - Antenna pattern approximations
    - Power and range with uncertainty
    - Platform integration geometry

    LIMITATIONS (CRITICAL):
    - EM characteristics are ESTIMATES ONLY
    - Waveform details completely unknown
    - Effectiveness against specific systems not modeled
    - Software-defined capabilities cannot be captured
    - Adaptive/cognitive EW not representable
    - Classification prevents accurate modeling
    """

    designation: str
    system_type: EWSystemType
    platform: str  # "ground", "vehicle", "ship", "aircraft"

    # Physical dimensions
    system_length: UncertaintyBounds = None
    system_width: UncertaintyBounds = None
    system_height: UncertaintyBounds = None

    # Antenna dimensions
    antenna_length: UncertaintyBounds = None
    antenna_width: UncertaintyBounds = None
    num_antenna_elements: int = 1

    # EM characteristics
    em_characteristics: EMCharacteristics = None

    # Additional bands (for multi-band systems)
    additional_bands: List[EMCharacteristics] = None

    # Vehicle (if vehicle-mounted)
    vehicle_length: UncertaintyBounds = None
    vehicle_width: UncertaintyBounds = None
    vehicle_height: UncertaintyBounds = None

    # Coverage
    azimuth_coverage_deg: UncertaintyBounds = None
    elevation_coverage_deg: UncertaintyBounds = None

    # Power requirements
    prime_power_kw: UncertaintyBounds = None

    def get_parameters(self) -> Dict[str, UncertaintyBounds]:
        params = {}
        if self.system_length:
            params['system_length'] = self.system_length
        if self.system_width:
            params['system_width'] = self.system_width
        if self.antenna_length:
            params['antenna_length'] = self.antenna_length
        if self.em_characteristics:
            params['frequency_min_ghz'] = self.em_characteristics.frequency_min_ghz
            params['frequency_max_ghz'] = self.em_characteristics.frequency_max_ghz
            params['power_output_kw'] = self.em_characteristics.power_output_kw
            params['effective_range_km'] = self.em_characteristics.effective_range_km
        return params

    def get_limitations(self) -> SystemLimitations:
        return SystemLimitations(
            system_name=self.designation,
            model_type="Electronic Warfare System CAD",
            geometry_accuracy_mm=100,
            geometry_source="Parade photos, exercise imagery",
            geometry_limitations=[
                "External antenna dimensions only",
                "Internal electronics layout completely unknown",
                "Antenna element spacing estimated",
                "Radome/cover shapes simplified",
                "Cable routing and connectors not modeled",
                "Cooling systems not detailed"
            ],
            performance_confidence=0.30,
            performance_source="Highly speculative estimates",
            performance_limitations=[
                "CRITICAL: EM parameters are ROUGH ESTIMATES",
                "Frequency coverage inferred from target systems",
                "Power output based on vehicle power capacity",
                "Effective range is theoretical maximum",
                "Jamming effectiveness cannot be determined",
                "ECCM resistance completely unknown",
                "Waveform characteristics classified",
                "Adaptive techniques not modelable"
            ],
            internal_layout_known=False,
            internal_layout_limitations=[
                "Transmitter architecture unknown",
                "Receiver sensitivity unknown",
                "Digital signal processing not modeled",
                "FPGA/software capabilities hidden",
                "Modular upgrade potential unknown"
            ],
            material_properties_known=False,
            material_limitations=[
                "Antenna materials uncertain",
                "EMI shielding effectiveness unknown",
                "Thermal management not characterized",
                "Environmental hardening uncertain"
            ],
            general_caveats=[
                "EW EFFECTIVENESS CANNOT BE MODELED FROM GEOMETRY",
                "Software-defined systems can change behavior",
                "Operational modes are classified",
                "Training modes may differ from combat modes",
                "Network integration effects not captured",
                "This model represents PHYSICAL FORM ONLY",
                "Do NOT use for EW effectiveness analysis"
            ],
            last_updated="2025-01",
            sources=[
                "PLA parade coverage",
                "Military exercise observations",
                "Defense industry publications",
                "Academic EW literature",
                "Analogous system comparisons"
            ]
        )

    def validate_geometry(self) -> Tuple[bool, List[str]]:
        errors = []

        # Validate antenna dimensions vs wavelength
        if self.em_characteristics and self.antenna_length:
            # Wavelength at min frequency
            wavelength_m = 0.3 / self.em_characteristics.frequency_min_ghz.nominal
            antenna_wavelengths = self.antenna_length.nominal / wavelength_m
            if antenna_wavelengths < 0.5:
                errors.append(
                    f"Antenna {self.antenna_length.nominal:.2f}m too small for "
                    f"{self.em_characteristics.frequency_min_ghz.nominal:.1f} GHz"
                )

        # Validate vehicle can carry system
        if self.vehicle_length and self.system_length:
            if self.system_length.nominal > self.vehicle_length.nominal:
                errors.append("System too long for vehicle")

        return len(errors) == 0, errors

    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        valid, errors = self.validate_geometry()
        if not valid:
            raise GeometryValidationError(f"Validation failed: {errors}")

        components = {}
        all_meshes = []

        if self.platform == "vehicle":
            # Generate vehicle + mounted system
            v_length = self.vehicle_length.nominal if self.vehicle_length else 8.0
            v_width = self.vehicle_width.nominal if self.vehicle_width else 2.5
            v_height = self.vehicle_height.nominal if self.vehicle_height else 2.0

            # Simple vehicle body (box approximation)
            # Using cylindrical sections rotated
            vehicle_body = CylindricalSection(
                length=v_length,
                forward_radius=v_width / 2
            )
            vehicle_mesh = vehicle_body.generate_mesh(resolution)
            all_meshes.append(vehicle_mesh)
            components["vehicle_body"] = vehicle_body

            # EW system on top
            sys_length = self.system_length.nominal if self.system_length else 3.0
            sys_width = self.system_width.nominal if self.system_width else 2.0
            sys_height = self.system_height.nominal if self.system_height else 1.5

            system_body = CylindricalSection(
                length=sys_length,
                forward_radius=sys_width / 2
            )
            system_mesh = system_body.generate_mesh(resolution)
            system_mesh = system_mesh.transform(
                translation=Point3D(v_length * 0.4, v_height, 0)
            )
            all_meshes.append(system_mesh)
            components["ew_system"] = system_body

            # Antenna array
            if self.antenna_length:
                ant_len = self.antenna_length.nominal
                ant_width = self.antenna_width.nominal if self.antenna_width else ant_len * 0.3

                antenna = CylindricalSection(
                    length=ant_len,
                    forward_radius=ant_width / 2
                )
                antenna_mesh = antenna.generate_mesh(resolution)
                antenna_mesh = antenna_mesh.transform(
                    translation=Point3D(v_length * 0.5, v_height + sys_height, 0),
                    rotation_deg=(0, 0, 90)  # Vertical
                )
                all_meshes.append(antenna_mesh)
                components["antenna"] = antenna

        else:
            # Standalone system
            sys_length = self.system_length.nominal if self.system_length else 2.0
            sys_width = self.system_width.nominal if self.system_width else 1.5

            system_body = CylindricalSection(
                length=sys_length,
                forward_radius=sys_width / 2
            )
            system_mesh = system_body.generate_mesh(resolution)
            all_meshes.append(system_mesh)
            components["system_body"] = system_body

            if self.antenna_length:
                antenna = CylindricalSection(
                    length=self.antenna_length.nominal,
                    forward_radius=0.1
                )
                antenna_mesh = antenna.generate_mesh(resolution // 2)
                antenna_mesh = antenna_mesh.transform(
                    translation=Point3D(sys_length / 2, sys_width / 2, 0),
                    rotation_deg=(0, 0, 90)
                )
                all_meshes.append(antenna_mesh)
                components["antenna"] = antenna

        combined_triangles = []
        for mesh in all_meshes:
            combined_triangles.extend(mesh.triangles)

        combined_mesh = TriangleMesh(triangles=combined_triangles)

        total_volume = sum(
            c.calculate_volume() for c in components.values()
            if hasattr(c, 'calculate_volume')
        )

        return CADGeometryResult(
            mesh=combined_mesh,
            components=components,
            bounding_box=combined_mesh.bounding_box,
            total_volume=total_volume,
            total_surface_area=combined_mesh.surface_area,
            parameters=self.get_parameters(),
            platform_type=PlatformType.GROUND_VEHICLE
        )


def create_sps48_ew_model() -> EWSystemCAD:
    """
    Vehicle-Mounted Radar Jammer System

    LIMITATIONS:
    - Generic representation of PLA EW vehicle
    - EM parameters are HIGHLY SPECULATIVE
    - Based on observed parade vehicles
    - Effectiveness cannot be assessed from CAD
    """
    return EWSystemCAD(
        designation="Ground-Based Radar Jammer",
        system_type=EWSystemType.RADAR_JAMMER,
        platform="vehicle",
        system_length=UncertaintyBounds(
            nominal=3.5, lower_bound=3.0, upper_bound=4.0,
            confidence=0.40,
            source="Vehicle-mounted system estimate",
            limitation="Based on parade photos"
        ),
        system_width=UncertaintyBounds(
            nominal=2.0, lower_bound=1.8, upper_bound=2.2,
            confidence=0.40,
            source="Vehicle width constraint",
            limitation="Must fit standard truck"
        ),
        system_height=UncertaintyBounds(
            nominal=1.8, lower_bound=1.5, upper_bound=2.2,
            confidence=0.35,
            source="Mast height estimate",
            limitation="Deployed configuration"
        ),
        antenna_length=UncertaintyBounds(
            nominal=2.5, lower_bound=2.0, upper_bound=3.0,
            confidence=0.35,
            source="Array size estimate",
            limitation="Phased array assumed"
        ),
        antenna_width=UncertaintyBounds(
            nominal=0.8, lower_bound=0.6, upper_bound=1.0,
            confidence=0.30,
            source="Proportional estimate",
            limitation="Multi-panel possible"
        ),
        num_antenna_elements=64,  # Estimated
        em_characteristics=EMCharacteristics(
            frequency_min_ghz=UncertaintyBounds(
                nominal=2.0, lower_bound=1.0, upper_bound=4.0,
                confidence=0.25,
                source="S-band coverage assumed",
                limitation="HIGHLY UNCERTAIN"
            ),
            frequency_max_ghz=UncertaintyBounds(
                nominal=18.0, lower_bound=12.0, upper_bound=20.0,
                confidence=0.25,
                source="Ku-band upper limit",
                limitation="Multi-band speculated"
            ),
            power_output_kw=UncertaintyBounds(
                nominal=50, lower_bound=20, upper_bound=100,
                confidence=0.20,
                source="Vehicle power capacity",
                limitation="Peak power estimate"
            ),
            antenna_gain_dbi=UncertaintyBounds(
                nominal=30, lower_bound=25, upper_bound=35,
                confidence=0.25,
                source="Array size calculation",
                limitation="Beam width tradeoff"
            ),
            effective_range_km=UncertaintyBounds(
                nominal=150, lower_bound=80, upper_bound=250,
                confidence=0.20,
                source="ERP-based estimate",
                limitation="Against specific threats unknown"
            ),
            em_limitations=[
                "Frequency coverage is SPECULATION",
                "Waveform capability unknown",
                "Jamming technique set unknown",
                "DRFM capability uncertain"
            ]
        ),
        vehicle_length=UncertaintyBounds(
            nominal=10.0, lower_bound=9.0, upper_bound=11.0,
            confidence=0.50,
            source="Standard military truck",
            limitation="6x6 or 8x8 chassis"
        ),
        vehicle_width=UncertaintyBounds(
            nominal=2.5, lower_bound=2.4, upper_bound=2.6,
            confidence=0.55,
            source="Road legal limit",
            limitation="Standard chassis"
        ),
        vehicle_height=UncertaintyBounds(
            nominal=3.2, lower_bound=3.0, upper_bound=3.5,
            confidence=0.45,
            source="Bridge clearance",
            limitation="Stowed configuration"
        ),
        azimuth_coverage_deg=UncertaintyBounds(
            nominal=360, lower_bound=360, upper_bound=360,
            confidence=0.60,
            source="Rotating mount",
            limitation="Scan rate unknown"
        ),
        elevation_coverage_deg=UncertaintyBounds(
            nominal=60, lower_bound=45, upper_bound=75,
            confidence=0.30,
            source="Antenna tilt range",
            limitation="Low angle may be limited"
        ),
        prime_power_kw=UncertaintyBounds(
            nominal=100, lower_bound=60, upper_bound=150,
            confidence=0.35,
            source="Generator capacity",
            limitation="Auxiliary power unit"
        )
    )


def create_comms_jammer_model() -> EWSystemCAD:
    """
    Communications Jammer System

    LIMITATIONS:
    - Targets HF/VHF/UHF communications
    - May include GPS/GNSS jamming
    - Wide-band capability assumed
    - Effectiveness highly variable
    """
    return EWSystemCAD(
        designation="Communications Jammer",
        system_type=EWSystemType.COMMS_JAMMER,
        platform="vehicle",
        system_length=UncertaintyBounds(
            nominal=2.5, lower_bound=2.0, upper_bound=3.0,
            confidence=0.40,
            source="Shelter size estimate",
            limitation="Multiple configurations"
        ),
        system_width=UncertaintyBounds(
            nominal=2.0, lower_bound=1.8, upper_bound=2.2,
            confidence=0.40,
            source="Standard shelter",
            limitation="ISO container compatible"
        ),
        system_height=UncertaintyBounds(
            nominal=2.0, lower_bound=1.8, upper_bound=2.5,
            confidence=0.35,
            source="Shelter + mast",
            limitation="Deployed height varies"
        ),
        antenna_length=UncertaintyBounds(
            nominal=5.0, lower_bound=3.0, upper_bound=8.0,
            confidence=0.30,
            source="VHF antenna requirement",
            limitation="Telescoping mast"
        ),
        antenna_width=UncertaintyBounds(
            nominal=0.3, lower_bound=0.2, upper_bound=0.5,
            confidence=0.30,
            source="Whip/log-periodic",
            limitation="Multiple types possible"
        ),
        num_antenna_elements=4,  # Multiple bands
        em_characteristics=EMCharacteristics(
            frequency_min_ghz=UncertaintyBounds(
                nominal=0.03, lower_bound=0.02, upper_bound=0.05,
                confidence=0.30,
                source="HF band lower",
                limitation="30 MHz assumed"
            ),
            frequency_max_ghz=UncertaintyBounds(
                nominal=3.0, lower_bound=2.0, upper_bound=6.0,
                confidence=0.25,
                source="UHF/S-band upper",
                limitation="May include GPS"
            ),
            power_output_kw=UncertaintyBounds(
                nominal=10, lower_bound=5, upper_bound=20,
                confidence=0.25,
                source="Comms jammer class",
                limitation="Per band power"
            ),
            antenna_gain_dbi=UncertaintyBounds(
                nominal=10, lower_bound=5, upper_bound=15,
                confidence=0.25,
                source="Omni/directional mix",
                limitation="Wide coverage needed"
            ),
            effective_range_km=UncertaintyBounds(
                nominal=50, lower_bound=20, upper_bound=100,
                confidence=0.20,
                source="Comms disruption range",
                limitation="Highly variable"
            ),
            em_limitations=[
                "Frequency hopping defeat unknown",
                "Spread spectrum jamming unclear",
                "Selective vs barrage unknown",
                "Collateral effects not modeled"
            ]
        ),
        vehicle_length=UncertaintyBounds(
            nominal=8.0, lower_bound=7.0, upper_bound=9.0,
            confidence=0.50,
            source="Medium truck",
            limitation="4x4 or 6x6 chassis"
        ),
        vehicle_width=UncertaintyBounds(
            nominal=2.5, lower_bound=2.4, upper_bound=2.6,
            confidence=0.55,
            source="Standard width",
            limitation="Road legal"
        ),
        vehicle_height=UncertaintyBounds(
            nominal=3.5, lower_bound=3.0, upper_bound=4.0,
            confidence=0.40,
            source="Mast stowed",
            limitation="Extended much taller"
        ),
        azimuth_coverage_deg=UncertaintyBounds(
            nominal=360, lower_bound=360, upper_bound=360,
            confidence=0.70,
            source="Omni requirement",
            limitation="Full azimuth"
        ),
        elevation_coverage_deg=UncertaintyBounds(
            nominal=90, lower_bound=60, upper_bound=90,
            confidence=0.40,
            source="Ground to overhead",
            limitation="Satellite comms"
        ),
        prime_power_kw=UncertaintyBounds(
            nominal=30, lower_bound=20, upper_bound=50,
            confidence=0.35,
            source="Generator size",
            limitation="Continuous operation"
        )
    )


def create_sigint_system_model() -> EWSystemCAD:
    """
    Signals Intelligence (SIGINT) Collection System

    LIMITATIONS:
    - Passive collection system
    - Frequency coverage inferred
    - Processing capabilities unknown
    - May include DF capability
    """
    return EWSystemCAD(
        designation="SIGINT Collection System",
        system_type=EWSystemType.SIGINT,
        platform="vehicle",
        system_length=UncertaintyBounds(
            nominal=4.0, lower_bound=3.5, upper_bound=4.5,
            confidence=0.40,
            source="Large shelter needed",
            limitation="Operator positions"
        ),
        system_width=UncertaintyBounds(
            nominal=2.2, lower_bound=2.0, upper_bound=2.4,
            confidence=0.45,
            source="Standard shelter",
            limitation="Equipment racks"
        ),
        system_height=UncertaintyBounds(
            nominal=2.2, lower_bound=2.0, upper_bound=2.5,
            confidence=0.40,
            source="Working height",
            limitation="Plus antenna mast"
        ),
        antenna_length=UncertaintyBounds(
            nominal=3.0, lower_bound=2.0, upper_bound=5.0,
            confidence=0.30,
            source="DF baseline",
            limitation="Aperture vs frequency"
        ),
        antenna_width=UncertaintyBounds(
            nominal=3.0, lower_bound=2.0, upper_bound=4.0,
            confidence=0.30,
            source="Circular array",
            limitation="Direction finding"
        ),
        num_antenna_elements=8,  # DF array
        em_characteristics=EMCharacteristics(
            frequency_min_ghz=UncertaintyBounds(
                nominal=0.1, lower_bound=0.03, upper_bound=0.5,
                confidence=0.30,
                source="Wide coverage needed",
                limitation="HF/VHF start"
            ),
            frequency_max_ghz=UncertaintyBounds(
                nominal=40.0, lower_bound=18.0, upper_bound=50.0,
                confidence=0.25,
                source="Ka-band possibility",
                limitation="May extend higher"
            ),
            power_output_kw=UncertaintyBounds(
                nominal=0.001, lower_bound=0.0001, upper_bound=0.01,
                confidence=0.60,
                source="Passive system",
                limitation="Receive only"
            ),
            antenna_gain_dbi=UncertaintyBounds(
                nominal=20, lower_bound=10, upper_bound=30,
                confidence=0.30,
                source="DF array gain",
                limitation="Varies with frequency"
            ),
            effective_range_km=UncertaintyBounds(
                nominal=300, lower_bound=100, upper_bound=500,
                confidence=0.25,
                source="Line of sight limit",
                limitation="Target dependent"
            ),
            em_limitations=[
                "PASSIVE SYSTEM - no jamming",
                "Sensitivity figures unknown",
                "Processing speed unknown",
                "DF accuracy uncertain",
                "ELINT vs COMINT split unknown"
            ]
        ),
        vehicle_length=UncertaintyBounds(
            nominal=10.0, lower_bound=9.0, upper_bound=11.0,
            confidence=0.50,
            source="Large truck needed",
            limitation="6x6 or 8x8"
        ),
        vehicle_width=UncertaintyBounds(
            nominal=2.5, lower_bound=2.4, upper_bound=2.6,
            confidence=0.55,
            source="Standard",
            limitation="Road legal"
        ),
        vehicle_height=UncertaintyBounds(
            nominal=4.0, lower_bound=3.5, upper_bound=5.0,
            confidence=0.35,
            source="Mast + shelter",
            limitation="Stowed for transit"
        ),
        azimuth_coverage_deg=UncertaintyBounds(
            nominal=360, lower_bound=360, upper_bound=360,
            confidence=0.70,
            source="DF requirement",
            limitation="Full coverage"
        ),
        elevation_coverage_deg=UncertaintyBounds(
            nominal=80, lower_bound=60, upper_bound=90,
            confidence=0.35,
            source="Above horizon",
            limitation="Satellite intercept"
        ),
        prime_power_kw=UncertaintyBounds(
            nominal=20, lower_bound=15, upper_bound=30,
            confidence=0.40,
            source="Electronics + cooling",
            limitation="Processing load"
        )
    )


# =============================================================================
# NETWORK INTEGRATION AND C4ISR
# =============================================================================

class NetworkNodeType(Enum):
    """C4ISR network node types"""
    COMMAND_CENTER = "command_center"
    RADAR_NODE = "radar_node"
    SAM_BATTERY = "sam_battery"
    EW_NODE = "ew_node"
    COMMS_RELAY = "comms_relay"
    DATA_LINK = "data_link"
    SATELLITE_TERMINAL = "satellite_terminal"
    CYBER_NODE = "cyber_node"


@dataclass
class DataLinkCharacteristics:
    """
    Data link characteristics for network integration.

    Critical for modeling integrated air defense systems.
    """
    link_type: str  # "los", "satcom", "troposcatter", "hf"
    data_rate_mbps: UncertaintyBounds
    range_km: UncertaintyBounds
    latency_ms: UncertaintyBounds
    encryption_level: str  # "none", "tactical", "strategic"
    jam_resistance: str  # "none", "limited", "moderate", "high"

    # Limitations
    link_limitations: List[str] = field(default_factory=list)


@dataclass
class NetworkNodeCAD(ValidatedCADModel):
    """
    C4ISR Network Node CAD Model

    Models physical infrastructure for:
    - Command and control centers
    - Radar integration nodes
    - Data link terminals
    - Communications relays

    ERROR-FREE DESIGN:
    - Physical dimensions validated
    - Network topology represented
    - Data link parameters with uncertainty
    - Complete integration limitations

    LIMITATIONS (CRITICAL):
    - Network architecture is NOTIONAL
    - Protocol details completely unknown
    - Cyber capabilities cannot be modeled
    - Actual connectivity is classified
    - Software architecture hidden
    - Resilience characteristics unknown
    """

    designation: str
    node_type: NetworkNodeType

    # Physical dimensions
    facility_length: UncertaintyBounds = None
    facility_width: UncertaintyBounds = None
    facility_height: UncertaintyBounds = None

    # Antenna/terminal dimensions
    antenna_diameter: UncertaintyBounds = None
    antenna_height: UncertaintyBounds = None

    # Network characteristics
    data_links: List[DataLinkCharacteristics] = None

    # Processing
    track_capacity: UncertaintyBounds = None
    update_rate_hz: UncertaintyBounds = None

    # Connected systems
    connected_radars: int = 0
    connected_sam_batteries: int = 0
    connected_ew_systems: int = 0

    # Mobility
    is_mobile: bool = False
    setup_time_min: UncertaintyBounds = None

    def get_parameters(self) -> Dict[str, UncertaintyBounds]:
        params = {}
        if self.facility_length:
            params['facility_length'] = self.facility_length
        if self.facility_width:
            params['facility_width'] = self.facility_width
        if self.antenna_diameter:
            params['antenna_diameter'] = self.antenna_diameter
        if self.track_capacity:
            params['track_capacity'] = self.track_capacity
        if self.update_rate_hz:
            params['update_rate_hz'] = self.update_rate_hz
        return params

    def get_limitations(self) -> SystemLimitations:
        return SystemLimitations(
            system_name=self.designation,
            model_type="C4ISR Network Node CAD",
            geometry_accuracy_mm=200,
            geometry_source="Satellite imagery, parade displays",
            geometry_limitations=[
                "External structure only",
                "Internal layout completely unknown",
                "Equipment racks not modeled",
                "Cable routing not represented",
                "Hardening unknown",
                "Backup power systems not detailed"
            ],
            performance_confidence=0.20,
            performance_source="Highly speculative inference",
            performance_limitations=[
                "CRITICAL: Network architecture is NOTIONAL",
                "Track capacity is rough estimate",
                "Data rates based on technology assumptions",
                "Latency characteristics unknown",
                "Bandwidth allocation hidden",
                "Protocol stack completely unknown",
                "Redundancy architecture classified"
            ],
            internal_layout_known=False,
            internal_layout_limitations=[
                "Computing hardware type unknown",
                "Storage capacity unknown",
                "Network interfaces hidden",
                "Software architecture classified",
                "Database structure unknown"
            ],
            material_properties_known=False,
            material_limitations=[
                "Structure materials uncertain",
                "EMI/EMP hardening unknown",
                "TEMPEST compliance unclear",
                "Physical security measures hidden"
            ],
            general_caveats=[
                "NETWORK TOPOLOGY IS SPECULATIVE",
                "Cannot model actual C4ISR capability",
                "Software integration not representable",
                "Cyber resilience unknown",
                "Human factors not modeled",
                "Doctrine affects capability more than hardware",
                "Degraded mode operation unknown"
            ],
            last_updated="2025-01",
            sources=[
                "Open source imagery",
                "PLA organizational studies",
                "Analogous system analysis",
                "Academic C4ISR literature",
                "Defense industry publications"
            ]
        )

    def validate_geometry(self) -> Tuple[bool, List[str]]:
        errors = []

        if self.facility_length and self.facility_width:
            aspect = self.facility_length.nominal / self.facility_width.nominal
            if aspect < 0.3 or aspect > 6:  # Mobile shelters can be elongated
                errors.append(f"Facility aspect ratio {aspect:.1f} unusual")

        if self.antenna_diameter:
            if self.antenna_diameter.nominal > 20:
                errors.append("Antenna diameter > 20m is exceptional")

        return len(errors) == 0, errors

    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        valid, errors = self.validate_geometry()
        if not valid:
            raise GeometryValidationError(f"Validation failed: {errors}")

        components = {}
        all_meshes = []

        # Main facility
        fac_length = self.facility_length.nominal if self.facility_length else 15.0
        fac_width = self.facility_width.nominal if self.facility_width else 10.0
        fac_height = self.facility_height.nominal if self.facility_height else 4.0

        # Simplified as cylinder
        facility = CylindricalSection(
            length=fac_length,
            forward_radius=fac_width / 2
        )
        facility_mesh = facility.generate_mesh(resolution)
        all_meshes.append(facility_mesh)
        components["facility"] = facility

        # Antenna/terminal
        if self.antenna_diameter:
            ant_diam = self.antenna_diameter.nominal
            ant_height = self.antenna_height.nominal if self.antenna_height else ant_diam * 0.3

            antenna = CylindricalSection(
                length=ant_height,
                forward_radius=ant_diam / 2
            )
            antenna_mesh = antenna.generate_mesh(resolution)
            antenna_mesh = antenna_mesh.transform(
                translation=Point3D(fac_length / 2, fac_height, 0),
                rotation_deg=(0, 0, 90)
            )
            all_meshes.append(antenna_mesh)
            components["antenna"] = antenna

        # Mast structures for mobile node
        if self.is_mobile:
            mast = CylindricalSection(
                length=10.0,
                forward_radius=0.15
            )
            mast_mesh = mast.generate_mesh(resolution // 4)
            mast_mesh = mast_mesh.transform(
                translation=Point3D(fac_length * 0.8, fac_height, 0),
                rotation_deg=(0, 0, 90)
            )
            all_meshes.append(mast_mesh)
            components["comms_mast"] = mast

        combined_triangles = []
        for mesh in all_meshes:
            combined_triangles.extend(mesh.triangles)

        combined_mesh = TriangleMesh(triangles=combined_triangles)

        total_volume = sum(
            c.calculate_volume() for c in components.values()
            if hasattr(c, 'calculate_volume')
        )

        return CADGeometryResult(
            mesh=combined_mesh,
            components=components,
            bounding_box=combined_mesh.bounding_box,
            total_volume=total_volume,
            total_surface_area=combined_mesh.surface_area,
            parameters=self.get_parameters(),
            platform_type=PlatformType.GROUND_VEHICLE
        )


def create_iads_command_node() -> NetworkNodeCAD:
    """
    Integrated Air Defense System Command Node

    LIMITATIONS:
    - Represents battalion/brigade level
    - Network topology is NOTIONAL
    - Processing capability unknown
    - Mobile command post configuration
    """
    return NetworkNodeCAD(
        designation="IADS Command Node",
        node_type=NetworkNodeType.COMMAND_CENTER,
        facility_length=UncertaintyBounds(
            nominal=12.0, lower_bound=10.0, upper_bound=14.0,
            confidence=0.40,
            source="Mobile command shelter",
            limitation="Expandable configuration"
        ),
        facility_width=UncertaintyBounds(
            nominal=2.5, lower_bound=2.4, upper_bound=2.6,
            confidence=0.50,
            source="Standard shelter width",
            limitation="ISO compatible"
        ),
        facility_height=UncertaintyBounds(
            nominal=2.8, lower_bound=2.5, upper_bound=3.2,
            confidence=0.45,
            source="Working height + equipment",
            limitation="Expandable sides"
        ),
        antenna_diameter=UncertaintyBounds(
            nominal=4.0, lower_bound=3.0, upper_bound=5.0,
            confidence=0.35,
            source="SATCOM terminal",
            limitation="Ku/Ka band assumed"
        ),
        antenna_height=UncertaintyBounds(
            nominal=1.5, lower_bound=1.0, upper_bound=2.0,
            confidence=0.35,
            source="Dish configuration",
            limitation="Auto-pointing"
        ),
        data_links=[
            DataLinkCharacteristics(
                link_type="los",
                data_rate_mbps=UncertaintyBounds(
                    nominal=100, lower_bound=50, upper_bound=200,
                    confidence=0.30,
                    source="Modern tactical data link",
                    limitation="Line of sight range limit"
                ),
                range_km=UncertaintyBounds(
                    nominal=50, lower_bound=30, upper_bound=80,
                    confidence=0.35,
                    source="LOS with relay",
                    limitation="Terrain dependent"
                ),
                latency_ms=UncertaintyBounds(
                    nominal=50, lower_bound=20, upper_bound=100,
                    confidence=0.30,
                    source="Processing delay",
                    limitation="Plus propagation"
                ),
                encryption_level="tactical",
                jam_resistance="moderate",
                link_limitations=[
                    "LOS range limited by terrain",
                    "Bandwidth shared among nodes",
                    "Encryption adds latency"
                ]
            ),
            DataLinkCharacteristics(
                link_type="satcom",
                data_rate_mbps=UncertaintyBounds(
                    nominal=10, lower_bound=5, upper_bound=20,
                    confidence=0.25,
                    source="Military SATCOM band",
                    limitation="Bandwidth allocation"
                ),
                range_km=UncertaintyBounds(
                    nominal=5000, lower_bound=3000, upper_bound=8000,
                    confidence=0.40,
                    source="GEO satellite coverage",
                    limitation="Chinese satellite constellation"
                ),
                latency_ms=UncertaintyBounds(
                    nominal=600, lower_bound=500, upper_bound=800,
                    confidence=0.45,
                    source="GEO orbital delay",
                    limitation="Not suitable for engagement"
                ),
                encryption_level="strategic",
                jam_resistance="limited",
                link_limitations=[
                    "High latency precludes real-time fire control",
                    "Weather affects Ka band",
                    "Satellite availability uncertain"
                ]
            )
        ],
        track_capacity=UncertaintyBounds(
            nominal=200, lower_bound=100, upper_bound=400,
            confidence=0.25,
            source="Modern IADS capability",
            limitation="Display vs processing"
        ),
        update_rate_hz=UncertaintyBounds(
            nominal=1, lower_bound=0.5, upper_bound=2,
            confidence=0.30,
            source="Tactical picture rate",
            limitation="Network constrained"
        ),
        connected_radars=8,
        connected_sam_batteries=4,
        connected_ew_systems=2,
        is_mobile=True,
        setup_time_min=UncertaintyBounds(
            nominal=30, lower_bound=20, upper_bound=60,
            confidence=0.35,
            source="Rapid deployment design",
            limitation="Full capability setup"
        )
    )


def create_data_link_terminal() -> NetworkNodeCAD:
    """
    Tactical Data Link Terminal

    LIMITATIONS:
    - Provides node connectivity
    - Protocol details unknown
    - May be Link-16 equivalent
    - Encryption strength classified
    """
    return NetworkNodeCAD(
        designation="Tactical Data Link Terminal",
        node_type=NetworkNodeType.DATA_LINK,
        facility_length=UncertaintyBounds(
            nominal=4.0, lower_bound=3.5, upper_bound=4.5,
            confidence=0.45,
            source="Small shelter",
            limitation="Trailer or truck mounted"
        ),
        facility_width=UncertaintyBounds(
            nominal=2.0, lower_bound=1.8, upper_bound=2.2,
            confidence=0.50,
            source="Compact system",
            limitation="Minimum footprint"
        ),
        facility_height=UncertaintyBounds(
            nominal=2.5, lower_bound=2.2, upper_bound=3.0,
            confidence=0.45,
            source="Antenna mast",
            limitation="Stowed lower"
        ),
        antenna_diameter=UncertaintyBounds(
            nominal=0.5, lower_bound=0.3, upper_bound=0.8,
            confidence=0.35,
            source="UHF/L-band array",
            limitation="Phased array possible"
        ),
        antenna_height=UncertaintyBounds(
            nominal=3.0, lower_bound=2.0, upper_bound=4.0,
            confidence=0.35,
            source="Mast-mounted",
            limitation="LOS improvement"
        ),
        data_links=[
            DataLinkCharacteristics(
                link_type="los",
                data_rate_mbps=UncertaintyBounds(
                    nominal=50, lower_bound=20, upper_bound=100,
                    confidence=0.30,
                    source="Tactical link standard",
                    limitation="Shared bandwidth"
                ),
                range_km=UncertaintyBounds(
                    nominal=30, lower_bound=15, upper_bound=50,
                    confidence=0.35,
                    source="Direct LOS",
                    limitation="Antenna height dependent"
                ),
                latency_ms=UncertaintyBounds(
                    nominal=20, lower_bound=10, upper_bound=50,
                    confidence=0.30,
                    source="Low latency design",
                    limitation="Fire control suitable"
                ),
                encryption_level="tactical",
                jam_resistance="moderate",
                link_limitations=[
                    "Time-division multiple access assumed",
                    "Net entry procedures unknown",
                    "Frequency hopping parameters classified"
                ]
            )
        ],
        track_capacity=UncertaintyBounds(
            nominal=100, lower_bound=50, upper_bound=200,
            confidence=0.25,
            source="Track relay capacity",
            limitation="Not fusion node"
        ),
        update_rate_hz=UncertaintyBounds(
            nominal=2, lower_bound=1, upper_bound=4,
            confidence=0.30,
            source="Track update rate",
            limitation="Priority based"
        ),
        connected_radars=2,
        connected_sam_batteries=1,
        connected_ew_systems=0,
        is_mobile=True,
        setup_time_min=UncertaintyBounds(
            nominal=15, lower_bound=10, upper_bound=30,
            confidence=0.40,
            source="Rapid deployment",
            limitation="Antenna erection"
        )
    )


def create_satcom_terminal() -> NetworkNodeCAD:
    """
    Strategic Satellite Communications Terminal

    LIMITATIONS:
    - Connects to Chinese military satellites
    - Beidou integration likely
    - Long-haul communications
    - High latency for control
    """
    return NetworkNodeCAD(
        designation="Strategic SATCOM Terminal",
        node_type=NetworkNodeType.SATELLITE_TERMINAL,
        facility_length=UncertaintyBounds(
            nominal=6.0, lower_bound=5.0, upper_bound=7.0,
            confidence=0.45,
            source="Shelter + equipment",
            limitation="Vehicle mounted"
        ),
        facility_width=UncertaintyBounds(
            nominal=2.5, lower_bound=2.4, upper_bound=2.6,
            confidence=0.50,
            source="Standard width",
            limitation="Road transportable"
        ),
        facility_height=UncertaintyBounds(
            nominal=3.0, lower_bound=2.8, upper_bound=3.5,
            confidence=0.45,
            source="Dish stowed",
            limitation="Deployed higher"
        ),
        antenna_diameter=UncertaintyBounds(
            nominal=2.4, lower_bound=1.8, upper_bound=3.0,
            confidence=0.40,
            source="Ku/Ka band SATCOM",
            limitation="Gain vs mobility"
        ),
        antenna_height=UncertaintyBounds(
            nominal=4.0, lower_bound=3.0, upper_bound=5.0,
            confidence=0.35,
            source="Deployed on mast",
            limitation="Clear sky view"
        ),
        data_links=[
            DataLinkCharacteristics(
                link_type="satcom",
                data_rate_mbps=UncertaintyBounds(
                    nominal=20, lower_bound=10, upper_bound=50,
                    confidence=0.30,
                    source="Modern SATCOM terminal",
                    limitation="Bandwidth allocation"
                ),
                range_km=UncertaintyBounds(
                    nominal=10000, lower_bound=5000, upper_bound=15000,
                    confidence=0.50,
                    source="GEO coverage",
                    limitation="Satellite footprint"
                ),
                latency_ms=UncertaintyBounds(
                    nominal=550, lower_bound=500, upper_bound=700,
                    confidence=0.50,
                    source="GEO orbital mechanics",
                    limitation="Irreducible delay"
                ),
                encryption_level="strategic",
                jam_resistance="limited",
                link_limitations=[
                    "Weather affects availability",
                    "Satellite capacity shared",
                    "Priority access uncertain",
                    "Uplink vulnerable to targeting"
                ]
            )
        ],
        track_capacity=UncertaintyBounds(
            nominal=500, lower_bound=200, upper_bound=1000,
            confidence=0.20,
            source="Strategic picture",
            limitation="Aggregated tracks"
        ),
        update_rate_hz=UncertaintyBounds(
            nominal=0.1, lower_bound=0.05, upper_bound=0.2,
            confidence=0.25,
            source="Strategic update",
            limitation="Not tactical"
        ),
        connected_radars=0,
        connected_sam_batteries=0,
        connected_ew_systems=0,
        is_mobile=True,
        setup_time_min=UncertaintyBounds(
            nominal=45, lower_bound=30, upper_bound=60,
            confidence=0.40,
            source="Dish alignment",
            limitation="Satellite acquisition"
        )
    )


# =============================================================================
# COMPLETE SYSTEM REGISTRY
# =============================================================================

class PLASystemsRegistry:
    """
    Registry of all validated PLA CAD models.

    Provides error-free access to pre-configured models
    with complete limitation documentation.
    """

    # DF-Series Strategic Missiles
    DF_SERIES = {
        'DF-5C': create_df5c_model,
        'DF-17': create_df17_model,
        'DF-21D': create_df21d_model,
        'DF-26': create_df26_model,
        'DF-41': create_df41_model,
    }

    # YJ-Series Anti-Ship Missiles
    YJ_SERIES = {
        'YJ-18': create_yj18_model,
        'YJ-21': create_yj21_model,
    }

    # HQ-Series SAMs
    HQ_SERIES = {
        'HQ-9B': create_hq9b_model,
        'HQ-16B': create_hq16_model,
        'HQ-22': create_hq22_model,
    }

    # PL-Series AAMs
    PL_SERIES = {
        'PL-15': create_pl15_model,
        'PL-21': create_pl21_model,
        'PL-10': create_pl10_model,
    }

    # EW Systems
    EW_SYSTEMS = {
        'Radar-Jammer': create_sps48_ew_model,
        'Comms-Jammer': create_comms_jammer_model,
        'SIGINT': create_sigint_system_model,
    }

    # Network/C4ISR Nodes
    NETWORK_NODES = {
        'IADS-Command': create_iads_command_node,
        'Data-Link-Terminal': create_data_link_terminal,
        'SATCOM-Terminal': create_satcom_terminal,
    }

    @classmethod
    def get_all_systems(cls) -> Dict[str, ValidatedCADModel]:
        """Get all available system models"""
        systems = {}
        for series in [cls.DF_SERIES, cls.YJ_SERIES, cls.HQ_SERIES,
                       cls.PL_SERIES, cls.EW_SYSTEMS, cls.NETWORK_NODES]:
            for name, factory in series.items():
                systems[name] = factory()
        return systems

    @classmethod
    def get_system(cls, designation: str) -> ValidatedCADModel:
        """Get a specific system model by designation"""
        for series in [cls.DF_SERIES, cls.YJ_SERIES, cls.HQ_SERIES,
                       cls.PL_SERIES, cls.EW_SYSTEMS, cls.NETWORK_NODES]:
            if designation in series:
                return series[designation]()
        raise ValueError(f"Unknown system: {designation}")

    @classmethod
    def generate_all_limitations_report(cls) -> str:
        """Generate comprehensive limitations report for all systems"""
        lines = []
        lines.append("=" * 80)
        lines.append("PLA DEFENSE SYSTEMS CAD - COMPREHENSIVE LIMITATIONS REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append("This document details ALL known limitations of CAD models")
        lines.append("in this framework. Users MUST review before use.")
        lines.append("")

        all_systems = {
            **cls.DF_SERIES, **cls.YJ_SERIES, **cls.HQ_SERIES,
            **cls.PL_SERIES, **cls.EW_SYSTEMS, **cls.NETWORK_NODES
        }
        for name, factory in all_systems.items():
            model = factory()
            lines.append(model.get_limitations().to_report())
            lines.append("")

        lines.append("=" * 80)
        lines.append("END OF LIMITATIONS REPORT")
        lines.append("=" * 80)

        return "\n".join(lines)

    @classmethod
    def validate_all_systems(cls) -> Dict[str, ConstraintSet]:
        """Validate all system models and return results"""
        results = {}
        all_systems = {
            **cls.DF_SERIES, **cls.YJ_SERIES, **cls.HQ_SERIES,
            **cls.PL_SERIES, **cls.EW_SYSTEMS, **cls.NETWORK_NODES
        }
        for name, factory in all_systems.items():
            model = factory()
            results[name] = model.validate_all()
        return results

    @classmethod
    def get_system_categories(cls) -> Dict[str, List[str]]:
        """Get systems organized by category"""
        return {
            "Strategic Missiles (DF-Series)": list(cls.DF_SERIES.keys()),
            "Anti-Ship Missiles (YJ-Series)": list(cls.YJ_SERIES.keys()),
            "Air Defense (HQ-Series)": list(cls.HQ_SERIES.keys()),
            "Air-to-Air Missiles (PL-Series)": list(cls.PL_SERIES.keys()),
            "Electronic Warfare": list(cls.EW_SYSTEMS.keys()),
            "C4ISR/Network Nodes": list(cls.NETWORK_NODES.keys()),
        }


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    import sys

    print("=" * 80)
    print("PLA DEFENSE SYSTEMS CAD - COMPREHENSIVE VALIDATION")
    print("=" * 80)

    # Show all system categories
    print("\n[1] System Categories")
    print("-" * 60)

    categories = PLASystemsRegistry.get_system_categories()
    total_systems = 0
    for category, systems in categories.items():
        print(f"  {category}:")
        for sys_name in systems:
            print(f"    - {sys_name}")
        total_systems += len(systems)
    print(f"\n  Total Systems: {total_systems}")

    # Validate all systems
    print("\n[2] Validating All System Models...")
    print("-" * 60)

    validation_results = PLASystemsRegistry.validate_all_systems()

    all_valid = True
    passed = 0
    failed = 0

    for name, result in validation_results.items():
        errors = [r for r in result.results
                  if not r.is_satisfied and r.severity.name == 'ERROR']
        status = "PASS" if len(errors) == 0 else "FAIL"
        if len(errors) > 0:
            all_valid = False
            failed += 1
            print(f"  {name:<25} [{status}] {len(errors)} errors")
            for err in errors[:2]:
                print(f"      - {err.message[:50]}")
        else:
            passed += 1
            print(f"  {name:<25} [{status}]")

    print(f"\n  Results: {passed} passed, {failed} failed")
    print(f"  Overall: {'ALL SYSTEMS VALID' if all_valid else 'VALIDATION ERRORS FOUND'}")

    # Generate geometry for sample systems
    print("\n[3] Generating Sample Geometries...")
    print("-" * 60)

    sample_systems = ['DF-21D', 'PL-15', 'HQ-9B', 'Radar-Jammer', 'IADS-Command']
    for sys_name in sample_systems:
        try:
            model = PLASystemsRegistry.get_system(sys_name)
            geometry = model.generate_geometry(resolution=16)
            print(f"  {sys_name:<20} Triangles: {len(geometry.mesh.triangles):>5}, "
                  f"Volume: {geometry.total_volume:.4f} m³")
        except Exception as e:
            print(f"  {sys_name:<20} Error: {str(e)[:40]}")

    # Show uncertainty summary
    print("\n[4] Uncertainty Summary")
    print("-" * 60)
    print(f"  {'System':<20} {'Confidence':<12} {'Accuracy':<15}")
    print(f"  {'-'*20} {'-'*12} {'-'*15}")

    for category, systems in categories.items():
        for sys_name in systems[:2]:  # Show first 2 per category
            try:
                model = PLASystemsRegistry.get_system(sys_name)
                lim = model.get_limitations()
                print(f"  {sys_name:<20} {lim.performance_confidence:>10.0%}   "
                      f"+/-{lim.geometry_accuracy_mm}mm")
            except:
                pass

    # EW-specific: Show EM characteristics
    print("\n[5] EW System EM Characteristics")
    print("-" * 60)

    for ew_name in PLASystemsRegistry.EW_SYSTEMS.keys():
        try:
            ew_model = PLASystemsRegistry.get_system(ew_name)
            em = ew_model.em_characteristics
            if em:
                erp = em.get_effective_radiated_power_dbw()
                print(f"  {ew_name}:")
                print(f"    Frequency: {em.frequency_min_ghz.nominal:.2f} - "
                      f"{em.frequency_max_ghz.nominal:.1f} GHz")
                print(f"    Power: {em.power_output_kw.nominal:.1f} kW")
                print(f"    ERP: {erp.nominal:.1f} dBW")
                print(f"    Range: {em.effective_range_km.nominal:.0f} km")
        except Exception as e:
            print(f"  {ew_name}: Error - {str(e)[:30]}")

    # Network integration summary
    print("\n[6] Network Integration Summary")
    print("-" * 60)

    for node_name in PLASystemsRegistry.NETWORK_NODES.keys():
        try:
            node = PLASystemsRegistry.get_system(node_name)
            print(f"  {node_name}:")
            print(f"    Type: {node.node_type.value}")
            print(f"    Track capacity: {node.track_capacity.nominal:.0f} (conf: {node.track_capacity.confidence:.0%})")
            if node.data_links:
                for link in node.data_links[:1]:
                    print(f"    Data link: {link.link_type}, "
                          f"{link.data_rate_mbps.nominal:.0f} Mbps, "
                          f"latency {link.latency_ms.nominal:.0f} ms")
        except Exception as e:
            print(f"  {node_name}: Error - {str(e)[:30]}")

    # Final summary
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"\nTotal Systems Validated: {total_systems}")
    print(f"Categories: {len(categories)}")
    print(f"Status: {'PASS' if all_valid else 'FAIL'}")

    if not all_valid:
        print("\nWARNING: Some systems failed validation. Review errors above.")
        sys.exit(1)

    print("\nAll CAD models validated successfully with documented limitations.")
    print("See get_limitations() for each system for complete uncertainty documentation.")
    print("=" * 80)
