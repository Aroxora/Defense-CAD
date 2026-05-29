#!/usr/bin/env python3
"""
Parade Weapon Systems CAD Module

Advanced parametric CAD models for PLA parade/operational weapon systems.
Includes strategic missiles, air defense systems, naval platforms, and
aerospace vehicles displayed at military parades.

Systems Modeled:
1. STRATEGIC MISSILES: DF-31AG, DF-41, DF-27 (hypersonic), JL-3 SLBM
2. AIR DEFENSE: HQ-9B, HQ-22, HQ-17A
3. ANTI-SHIP: YJ-21 (hypersonic), YJ-18, DF-21D ASBM
4. AIRCRAFT: J-20, J-35, H-20 (conceptual)
5. NAVAL: Type 055, Type 052D, Type 076

Each model includes:
- Parametric geometry with validation
- RCS calculation integration
- Kill chain integration points
- Data confidence levels
- Documented limitations

Classification: UNCLASSIFIED // PUBLIC RELEASE
Data Sources: CSIS, IISS, Jane's, DOD reports, academic papers
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
from abc import ABC, abstractmethod

from osint_cad.geometry.cad_geometry import (
    Point3D, Vector3D, TriangleMesh, Triangle, BoundingBox,
    OgiveNose, SearsHaackBody, CylindricalSection, WingGeometry,
    FinGeometry, NozzleGeometry, MissileCADModel, CADGeometryResult,
    GeometryComponent, PlatformType
)


# =============================================================================
# SECTION 1: STRATEGIC MISSILE SYSTEMS
# =============================================================================

class MissileCategory(Enum):
    """Strategic missile categories"""
    ICBM = "icbm"
    IRBM = "irbm"
    MRBM = "mrbm"
    SLBM = "slbm"
    HYPERSONIC = "hypersonic"
    CRUISE = "cruise"
    ASBM = "asbm"  # Anti-ship ballistic missile


@dataclass
class StrategicMissileSpecs:
    """
    Specifications for strategic missiles.

    CONFIDENCE LEVELS:
    - Dimensions: 60-80% (observable in parades)
    - Range: 40-60% (classified, estimates vary widely)
    - Payload: 30-50% (highly classified)
    - Accuracy: 30-50% (classified)
    """
    name: str
    designation: str
    category: MissileCategory

    # Dimensions (observable from parade photos)
    length_m: float
    diameter_m: float
    launch_weight_kg: float

    # Performance (estimates)
    range_km: float
    max_speed_mach: float
    payload_kg: float
    cep_m: float  # Circular Error Probable

    # Configuration
    num_stages: int
    fuel_type: str  # "solid", "liquid", "hybrid"
    launch_platform: str  # "road_mobile", "silo", "submarine", "rail"
    num_warheads: int = 1
    mirv_capable: bool = False

    # Data confidence
    dimension_confidence: float = 0.70
    performance_confidence: float = 0.45
    overall_confidence: float = 0.50

    # Documented limitations in data
    limitations: List[str] = field(default_factory=list)


@dataclass
class StrategicMissileCAD(MissileCADModel):
    """
    Parametric CAD model for strategic missiles.

    Extends base MissileCADModel with multi-stage capability,
    post-boost vehicle modeling, and re-entry vehicle geometry.
    """
    specs: StrategicMissileSpecs = None

    # Stage configuration
    stage_lengths: List[float] = field(default_factory=list)
    stage_diameters: List[float] = field(default_factory=list)
    interstage_lengths: List[float] = field(default_factory=list)

    # Re-entry vehicle
    rv_length: float = 0.0
    rv_base_diameter: float = 0.0
    rv_nose_radius: float = 0.0  # Blunt nose for re-entry heating

    # Post-boost vehicle (for MIRV)
    pbv_length: float = 0.0
    pbv_diameter: float = 0.0

    def __post_init__(self):
        """Initialize from specs if provided"""
        if self.specs:
            self.name = self.specs.name
            self.total_length = self.specs.length_m
            self.body_diameter = self.specs.diameter_m

            # Auto-configure stages
            if not self.stage_lengths and self.specs.num_stages > 0:
                self._configure_stages()

        # Call parent post_init
        super().__post_init__()

    def _configure_stages(self):
        """Auto-configure stage geometry from specs"""
        n = self.specs.num_stages
        total = self.total_length

        if n == 1:
            # Single stage
            self.stage_lengths = [total * 0.85]
            self.stage_diameters = [self.body_diameter]
            self.nose_length = total * 0.15

        elif n == 2:
            # Two stage (typical MRBM/IRBM)
            self.stage_lengths = [total * 0.45, total * 0.35]
            self.stage_diameters = [self.body_diameter, self.body_diameter * 0.9]
            self.interstage_lengths = [total * 0.05]
            self.nose_length = total * 0.15

        elif n == 3:
            # Three stage (typical ICBM)
            self.stage_lengths = [total * 0.35, total * 0.25, total * 0.20]
            self.stage_diameters = [
                self.body_diameter,
                self.body_diameter * 0.85,
                self.body_diameter * 0.70
            ]
            self.interstage_lengths = [total * 0.03, total * 0.02]
            self.nose_length = total * 0.15

            # Add PBV for MIRV
            if self.specs.mirv_capable:
                self.pbv_length = total * 0.08
                self.pbv_diameter = self.body_diameter * 0.5

        # Configure RV
        self.rv_length = self.nose_length * 0.8
        self.rv_base_diameter = self.body_diameter * 0.4
        self.rv_nose_radius = 0.05  # Blunt for re-entry

    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        """Generate multi-stage missile geometry"""
        components = {}
        all_meshes = []

        x_offset = 0.0

        # Generate nose/RV
        if self.rv_nose_radius > 0:
            # Blunt re-entry vehicle nose
            nose = OgiveNose(
                length=self.rv_length,
                base_radius=self.rv_base_diameter / 2
            )
        else:
            nose = OgiveNose(
                length=self.nose_length,
                base_radius=self.body_diameter / 2
            )

        nose_mesh = nose.generate_mesh(resolution)
        all_meshes.append(nose_mesh)
        components["nose"] = nose
        x_offset = self.nose_length

        # Generate stages
        for i, (length, diameter) in enumerate(
            zip(self.stage_lengths, self.stage_diameters)
        ):
            # Stage body
            if i > 0:
                prev_diameter = self.stage_diameters[i - 1]
            else:
                prev_diameter = diameter

            stage = CylindricalSection(
                length=length,
                forward_radius=prev_diameter / 2 if i > 0 else diameter / 2,
                aft_radius=diameter / 2
            )
            stage_mesh = stage.generate_mesh(resolution)
            stage_mesh = stage_mesh.transform(translation=Point3D(x_offset, 0, 0))
            all_meshes.append(stage_mesh)
            components[f"stage_{i + 1}"] = stage
            x_offset += length

            # Add interstage adapter if not last stage
            if i < len(self.interstage_lengths):
                adapter_len = self.interstage_lengths[i]
                next_diameter = self.stage_diameters[i + 1] if i + 1 < len(self.stage_diameters) else diameter * 0.8

                adapter = CylindricalSection(
                    length=adapter_len,
                    forward_radius=diameter / 2,
                    aft_radius=next_diameter / 2
                )
                adapter_mesh = adapter.generate_mesh(resolution // 2)
                adapter_mesh = adapter_mesh.transform(translation=Point3D(x_offset, 0, 0))
                all_meshes.append(adapter_mesh)
                components[f"interstage_{i + 1}"] = adapter
                x_offset += adapter_len

        # Add nozzle
        if self.stage_diameters:
            final_diameter = self.stage_diameters[-1]
            nozzle = NozzleGeometry(
                throat_radius=final_diameter * 0.15,
                exit_radius=final_diameter * 0.35,
                length=final_diameter * 0.5
            )
            nozzle_mesh = nozzle.generate_mesh(resolution)
            nozzle_mesh = nozzle_mesh.transform(translation=Point3D(x_offset, 0, 0))
            all_meshes.append(nozzle_mesh)
            components["nozzle"] = nozzle

        # Combine meshes
        combined_triangles = []
        for mesh in all_meshes:
            combined_triangles.extend(mesh.triangles)
        combined_mesh = TriangleMesh(triangles=combined_triangles)

        return CADGeometryResult(
            mesh=combined_mesh,
            components=components,
            bounding_box=combined_mesh.bounding_box,
            total_volume=sum(c.calculate_volume() for c in components.values()),
            total_surface_area=combined_mesh.surface_area,
            parameters=self.get_all_parameters(),
            platform_type=PlatformType.MISSILE
        )


# Pre-configured strategic missile models
def create_df41_model() -> StrategicMissileCAD:
    """
    DF-41 ICBM - China's most advanced road-mobile ICBM.

    LIMITATIONS:
    - Range estimates vary: 12,000-15,000 km
    - MIRV payload unknown (3-10 warheads estimated)
    - CEP estimates highly uncertain (100-500m)
    """
    specs = StrategicMissileSpecs(
        name="DF-41",
        designation="Dong Feng 41",
        category=MissileCategory.ICBM,
        length_m=21.0,  # Estimated from parade photos
        diameter_m=2.25,
        launch_weight_kg=80000,  # Estimated
        range_km=14000,  # Upper estimate
        max_speed_mach=25,  # Re-entry
        payload_kg=2500,
        cep_m=200,  # Estimated
        num_stages=3,
        fuel_type="solid",
        num_warheads=10,  # Maximum estimate
        mirv_capable=True,
        launch_platform="road_mobile",
        dimension_confidence=0.75,
        performance_confidence=0.40,
        overall_confidence=0.45,
        limitations=[
            "MIRV count classified - estimates range from 3 to 10",
            "Actual CEP unknown - could be 100-500m",
            "Penetration aids unknown",
            "Range depends on payload configuration"
        ]
    )

    return StrategicMissileCAD(
        name="DF-41",
        total_length=specs.length_m,
        body_diameter=specs.diameter_m,
        nose_length=3.5,
        specs=specs
    )


def create_df27_model() -> StrategicMissileCAD:
    """
    DF-27 Hypersonic Glide Vehicle (HGV) carrier.

    China's newest HGV system - combines ballistic boost with
    hypersonic maneuvering glide phase.

    CRITICAL FOR F-35 ENGAGEMENT:
    - Can engage moving targets (unlike traditional ballistic missiles)
    - Terminal maneuverability defeats missile defense
    - Hypersonic speed reduces reaction time

    LIMITATIONS:
    - Very limited public data
    - Glide vehicle dimensions highly uncertain
    - Guidance system unknown
    - Actual operational status unclear
    """
    specs = StrategicMissileSpecs(
        name="DF-27",
        designation="Dong Feng 27",
        category=MissileCategory.HYPERSONIC,
        length_m=12.0,  # Estimated
        diameter_m=1.4,
        launch_weight_kg=15000,  # Estimated
        range_km=5000,  # With glide phase
        max_speed_mach=15,  # Hypersonic glide
        payload_kg=1500,
        cep_m=30,  # Precision strike capability
        num_stages=2,
        fuel_type="solid",
        num_warheads=1,  # Single HGV
        mirv_capable=False,
        launch_platform="road_mobile",
        dimension_confidence=0.50,
        performance_confidence=0.30,
        overall_confidence=0.35,
        limitations=[
            "EXTREMELY limited public data",
            "Glide vehicle shape unknown",
            "Guidance method classified",
            "Terminal maneuvering capability unknown",
            "May not yet be fully operational"
        ]
    )

    return StrategicMissileCAD(
        name="DF-27",
        total_length=specs.length_m,
        body_diameter=specs.diameter_m,
        nose_length=2.0,
        specs=specs
    )


def create_jl3_model() -> StrategicMissileCAD:
    """
    JL-3 SLBM - Submarine-Launched Ballistic Missile.

    Deployed on Type 094A and future Type 096 SSBNs.
    Key component of sea-based nuclear deterrent.

    LIMITATIONS:
    - Submarine launch adds complexity
    - Range/payload tradeoff uncertain
    - Actual deployment status unclear
    """
    specs = StrategicMissileSpecs(
        name="JL-3",
        designation="Julang 3",
        category=MissileCategory.SLBM,
        length_m=13.0,
        diameter_m=2.2,
        launch_weight_kg=45000,
        range_km=10000,  # Estimated
        max_speed_mach=23,
        payload_kg=2000,
        cep_m=300,
        num_stages=3,
        fuel_type="solid",
        num_warheads=6,  # Estimated MIRV
        mirv_capable=True,
        launch_platform="submarine",
        dimension_confidence=0.60,
        performance_confidence=0.35,
        overall_confidence=0.40,
        limitations=[
            "Submarine tube dimensions constrain missile size",
            "Underwater launch trajectory different from land-based",
            "Actual range depends on patrol location",
            "CEP may be worse due to submarine position uncertainty"
        ]
    )

    return StrategicMissileCAD(
        name="JL-3",
        total_length=specs.length_m,
        body_diameter=specs.diameter_m,
        nose_length=2.2,
        specs=specs
    )


# =============================================================================
# SECTION 2: AIR DEFENSE MISSILE SYSTEMS
# =============================================================================

@dataclass
class AirDefenseSystemSpecs:
    """
    Air defense system specifications.

    Note: These are SYSTEM specs (launcher + radar + missile).
    """
    name: str
    missile_name: str

    # Missile dimensions
    missile_length_m: float
    missile_diameter_m: float
    missile_weight_kg: float

    # Performance
    max_range_km: float
    min_range_km: float
    max_altitude_m: float
    min_altitude_m: float
    max_speed_mach: float
    max_target_speed_mach: float
    max_target_g: float

    # Seeker
    seeker_type: str  # "active_radar", "semi_active", "IR", "command"
    seeker_range_km: float = 20.0

    # Kill probability
    pk_aerodynamic: float = 0.70  # vs maneuvering aircraft
    pk_ballistic: float = 0.85  # vs ballistic missiles
    pk_cruise: float = 0.80  # vs cruise missiles

    # System
    missiles_per_launcher: int = 4
    reload_time_s: float = 300
    reaction_time_s: float = 10  # Time from track to launch

    # Confidence
    confidence: float = 0.55


@dataclass
class AirDefenseMissileCAD(MissileCADModel):
    """
    Parametric CAD for air defense missiles.

    Includes control surfaces, seeker window, and motor sections.
    """
    specs: AirDefenseSystemSpecs = None

    # Seeker
    seeker_window_diameter_m: float = 0.0
    seeker_window_type: str = "ogive"  # "ogive", "hemispherical", "flat"

    # Control surfaces
    control_type: str = "canard"  # "canard", "tail", "thrust_vector"
    canard_span_m: float = 0.0
    canard_chord_m: float = 0.0

    def __post_init__(self):
        if self.specs:
            self.name = self.specs.missile_name
            self.total_length = self.specs.missile_length_m
            self.body_diameter = self.specs.missile_diameter_m

            # Auto-configure
            self.nose_length = self.body_diameter * 2.5
            self.seeker_window_diameter_m = self.body_diameter * 0.6

            if self.control_type == "canard":
                self.canard_span_m = self.body_diameter * 0.8
                self.canard_chord_m = self.body_diameter * 0.4

        super().__post_init__()


def create_hq9b_model() -> Tuple[AirDefenseMissileCAD, AirDefenseSystemSpecs]:
    """
    HQ-9B - China's primary long-range SAM.

    Comparable to S-300PMU2/S-400.
    Key system for F-35 engagement at range.

    LIMITATIONS:
    - Pk against F-35 UNKNOWN - estimates vary widely
    - Active seeker may struggle with 0.0002 m² RCS
    - HOJ mode effectiveness classified
    """
    specs = AirDefenseSystemSpecs(
        name="HQ-9B",
        missile_name="HQ-9B",
        missile_length_m=6.8,
        missile_diameter_m=0.47,
        missile_weight_kg=1300,
        max_range_km=250,
        min_range_km=15,
        max_altitude_m=27000,
        min_altitude_m=500,
        max_speed_mach=4.2,
        max_target_speed_mach=3.0,
        max_target_g=9,
        seeker_type="active_radar",
        seeker_range_km=35,
        pk_aerodynamic=0.65,  # Degraded vs stealth
        pk_ballistic=0.70,
        pk_cruise=0.75,
        missiles_per_launcher=4,
        reload_time_s=300,
        reaction_time_s=12,
        confidence=0.50
    )

    cad = AirDefenseMissileCAD(
        name="HQ-9B",
        total_length=specs.missile_length_m,
        body_diameter=specs.missile_diameter_m,
        nose_length=1.2,
        specs=specs,
        control_type="tail"
    )

    return cad, specs


def create_hq22_model() -> Tuple[AirDefenseMissileCAD, AirDefenseSystemSpecs]:
    """
    HQ-22 - Export version of HQ-16 family.

    Medium-range SAM bridging gap between HQ-9 and SHORAD.

    LIMITATIONS:
    - Semi-active radar guidance requires illuminator
    - Vulnerable to ARM attack on guidance radar
    - Limited simultaneous engagement capability
    """
    specs = AirDefenseSystemSpecs(
        name="HQ-22",
        missile_name="HQ-22",
        missile_length_m=5.2,
        missile_diameter_m=0.40,
        missile_weight_kg=800,
        max_range_km=100,
        min_range_km=5,
        max_altitude_m=18000,
        min_altitude_m=100,
        max_speed_mach=3.5,
        max_target_speed_mach=2.5,
        max_target_g=12,
        seeker_type="semi_active",
        seeker_range_km=15,
        pk_aerodynamic=0.70,
        pk_ballistic=0.60,
        pk_cruise=0.80,
        missiles_per_launcher=6,
        reload_time_s=180,
        reaction_time_s=8,
        confidence=0.60
    )

    cad = AirDefenseMissileCAD(
        name="HQ-22",
        total_length=specs.missile_length_m,
        body_diameter=specs.missile_diameter_m,
        nose_length=0.9,
        specs=specs,
        control_type="canard"
    )

    return cad, specs


def create_hq17a_model() -> Tuple[AirDefenseMissileCAD, AirDefenseSystemSpecs]:
    """
    HQ-17A - Short-range point defense SAM.

    Chinese development of Tor-M1 technology.
    Final layer before CIWS.

    CRITICAL FOR F-35:
    - Best chance at very short range
    - IR seeker not affected by stealth
    - Multiple missiles per target doctrine
    """
    specs = AirDefenseSystemSpecs(
        name="HQ-17A",
        missile_name="HQ-17A",
        missile_length_m=2.9,
        missile_diameter_m=0.23,
        missile_weight_kg=165,
        max_range_km=15,
        min_range_km=0.5,
        max_altitude_m=8000,
        min_altitude_m=10,
        max_speed_mach=2.8,
        max_target_speed_mach=2.0,
        max_target_g=12,
        seeker_type="command",  # Radio command with terminal IR
        seeker_range_km=5,
        pk_aerodynamic=0.75,
        pk_ballistic=0.50,
        pk_cruise=0.85,
        missiles_per_launcher=16,  # Vertical launch
        reload_time_s=120,
        reaction_time_s=5,
        confidence=0.65
    )

    cad = AirDefenseMissileCAD(
        name="HQ-17A",
        total_length=specs.missile_length_m,
        body_diameter=specs.missile_diameter_m,
        nose_length=0.4,
        specs=specs,
        control_type="tail"
    )

    return cad, specs


# =============================================================================
# SECTION 3: ANTI-SHIP WEAPONS
# =============================================================================

@dataclass
class AntiShipMissileSpecs:
    """Anti-ship missile specifications"""
    name: str
    designation: str

    length_m: float
    diameter_m: float
    wingspan_m: float
    weight_kg: float
    warhead_kg: float

    range_km: float
    cruise_speed_mach: float
    terminal_speed_mach: float
    cruise_altitude_m: float
    terminal_altitude_m: float

    seeker_type: str  # "radar", "IR", "dual", "synthetic_aperture"
    guidance: str  # "inertial_terminal", "datalink", "autonomous"

    launch_platform: List[str]  # "ship", "aircraft", "submarine", "shore"

    # Confidence
    confidence: float = 0.50

    # F-35 engagement relevance
    can_engage_aircraft: bool = False  # True for hypersonic variants


def create_yj21_model() -> StrategicMissileCAD:
    """
    YJ-21 - Hypersonic Anti-Ship Ballistic Missile (air-launched).

    Potentially the most threatening anti-ship weapon.
    Hypersonic terminal speed makes interception extremely difficult.

    F-35 RELEVANCE:
    - Could potentially be adapted for air-to-air role
    - Demonstrates hypersonic technology maturity
    - Defense against carrier battle groups

    LIMITATIONS:
    - Very limited public data
    - Terminal guidance unknown
    - Actual test results classified
    """
    specs = StrategicMissileSpecs(
        name="YJ-21",
        designation="Ying Ji 21",
        category=MissileCategory.HYPERSONIC,
        length_m=7.5,  # Estimated for air-launch
        diameter_m=0.7,
        launch_weight_kg=3500,
        range_km=1500,
        max_speed_mach=10,  # Terminal
        payload_kg=500,
        cep_m=20,  # Precision
        num_stages=1,  # Scramjet sustainer
        fuel_type="solid+scramjet",
        num_warheads=1,
        mirv_capable=False,
        launch_platform="aircraft",
        dimension_confidence=0.45,
        performance_confidence=0.30,
        overall_confidence=0.35,
        limitations=[
            "VERY limited data - recently revealed",
            "Scramjet sustainer unconfirmed",
            "Terminal guidance method unknown",
            "Sea-skimming vs high-dive profile unclear"
        ]
    )

    return StrategicMissileCAD(
        name="YJ-21",
        total_length=specs.length_m,
        body_diameter=specs.diameter_m,
        nose_length=1.2,
        specs=specs
    )


def create_df21d_model() -> StrategicMissileCAD:
    """
    DF-21D - "Carrier Killer" ASBM.

    First operational ASBM. Key A2/AD weapon.

    LIMITATIONS:
    - Complex kill chain required (detection -> tracking -> targeting)
    - Moving target engagement is very difficult
    - Re-entry vehicle control at hypersonic speed challenging
    - Test results against moving targets unknown
    """
    specs = StrategicMissileSpecs(
        name="DF-21D",
        designation="Dong Feng 21D",
        category=MissileCategory.ASBM,
        length_m=10.7,
        diameter_m=1.4,
        launch_weight_kg=14700,
        range_km=1800,
        max_speed_mach=10,
        payload_kg=600,
        cep_m=50,  # Against stationary target
        num_stages=2,
        fuel_type="solid",
        num_warheads=1,
        mirv_capable=False,
        launch_platform="road_mobile",
        dimension_confidence=0.70,
        performance_confidence=0.40,
        overall_confidence=0.45,
        limitations=[
            "CEP against moving carrier much worse than stated",
            "Requires external targeting (OTH radar, satellites)",
            "Kill chain time may exceed target movement",
            "Terminal guidance effectiveness unproven"
        ]
    )

    return StrategicMissileCAD(
        name="DF-21D",
        total_length=specs.length_m,
        body_diameter=specs.diameter_m,
        nose_length=2.0,
        specs=specs
    )


# =============================================================================
# SECTION 4: AIRCRAFT MODELS
# =============================================================================

@dataclass
class FighterAircraftSpecs:
    """Fifth-generation fighter specifications"""
    name: str
    designation: str

    # Dimensions
    length_m: float
    wingspan_m: float
    height_m: float
    wing_area_m2: float
    empty_weight_kg: float
    max_takeoff_weight_kg: float

    # Performance
    max_speed_mach: float
    cruise_speed_mach: float
    combat_radius_km: float
    service_ceiling_m: float
    max_g: float

    # Stealth
    frontal_rcs_m2: float
    rcs_confidence: float

    # Weapons
    internal_weapons: List[str]
    num_internal_hardpoints: int
    num_external_hardpoints: int

    # Sensors
    radar_name: str
    radar_range_km: float
    irst_equipped: bool

    # Data confidence
    overall_confidence: float


@dataclass
class FighterAircraftCAD:
    """
    Parametric CAD for fighter aircraft.

    Full geometry including:
    - Fuselage (stealth shaping)
    - Wings with control surfaces
    - Vertical stabilizers (canted for stealth)
    - Intakes (DSI or caret)
    - Weapons bays
    - Engine nozzles
    """
    specs: FighterAircraftSpecs
    resolution: int = 32

    # Stealth features
    chine_angle_deg: float = 15.0  # Fuselage chine angle
    stabilizer_cant_deg: float = 15.0  # All-moving vertical stab cant
    intake_type: str = "dsi"  # "dsi", "caret", "conventional"

    def generate_simplified_geometry(self) -> CADGeometryResult:
        """
        Generate simplified fighter geometry.

        Full stealth shaping requires classified edge alignment rules.
        This is a simplified parametric model.
        """
        components = {}
        all_meshes = []

        # Fuselage - approximated as blended body
        fuselage_length = self.specs.length_m
        fuselage_width = self.specs.wingspan_m * 0.3
        fuselage_height = self.specs.height_m * 0.6

        # Create fuselage as series of sections
        sections = 10
        for i in range(sections):
            x_start = i * fuselage_length / sections
            x_end = (i + 1) * fuselage_length / sections

            # Vary width along fuselage (area ruling)
            if i < 2:
                # Nose section
                width_fwd = fuselage_width * (i / 2) * 0.7
                width_aft = fuselage_width * ((i + 1) / 2) * 0.7
            elif i < 7:
                # Main body
                width_fwd = fuselage_width
                width_aft = fuselage_width
            else:
                # Tail section
                t = (i - 7) / 3
                width_fwd = fuselage_width * (1 - t * 0.5)
                width_aft = fuselage_width * (1 - (t + 0.33) * 0.5)

            section = CylindricalSection(
                length=(x_end - x_start),
                forward_radius=width_fwd / 2,
                aft_radius=width_aft / 2
            )
            mesh = section.generate_mesh(self.resolution // 2)
            mesh = mesh.transform(translation=Point3D(x_start, 0, 0))
            all_meshes.append(mesh)
            components[f"fuselage_{i}"] = section

        # Wings
        wing = WingGeometry(
            root_chord=self.specs.length_m * 0.35,
            tip_chord=self.specs.length_m * 0.1,
            span=self.specs.wingspan_m,
            sweep_angle_deg=45,  # Typical 5th gen
            dihedral_deg=-3,  # Slight anhedral
            thickness_ratio=0.04
        )
        wing_mesh = wing.generate_mesh(self.resolution // 2)
        wing_mesh = wing_mesh.transform(
            translation=Point3D(self.specs.length_m * 0.4, 0, 0)
        )
        all_meshes.append(wing_mesh)
        components["wings"] = wing

        # Vertical stabilizers (canted)
        for side in [-1, 1]:
            vstab = FinGeometry(
                root_chord=self.specs.length_m * 0.2,
                tip_chord=self.specs.length_m * 0.08,
                span=self.specs.height_m * 0.8,
                sweep_angle_deg=50,
                thickness=0.1,
                cant_angle_deg=self.stabilizer_cant_deg * side
            )
            vstab_mesh = vstab.generate_mesh(self.resolution // 4)
            vstab_mesh = vstab_mesh.transform(
                translation=Point3D(
                    self.specs.length_m * 0.75,
                    side * fuselage_width * 0.3,
                    0
                )
            )
            all_meshes.append(vstab_mesh)
            components[f"vstab_{side}"] = vstab

        # Combine meshes
        combined_triangles = []
        for mesh in all_meshes:
            combined_triangles.extend(mesh.triangles)
        combined_mesh = TriangleMesh(triangles=combined_triangles)

        return CADGeometryResult(
            mesh=combined_mesh,
            components=components,
            bounding_box=combined_mesh.bounding_box,
            total_volume=sum(c.calculate_volume() for c in components.values()),
            total_surface_area=combined_mesh.surface_area,
            parameters={
                "name": self.specs.name,
                "length": self.specs.length_m,
                "wingspan": self.specs.wingspan_m
            },
            platform_type=PlatformType.FIGHTER
        )


def create_j20_model() -> FighterAircraftCAD:
    """
    J-20 "Mighty Dragon" - China's 5th generation fighter.

    Primary air superiority fighter for F-35 engagement.

    CRITICAL CAPABILITIES:
    - Canard-delta configuration for high maneuverability
    - DSI intakes for stealth
    - Long-range PL-15/PL-21 missiles
    - IRST for passive detection

    LIMITATIONS:
    - RCS estimates vary widely (0.001-0.05 m² frontal)
    - Engine performance (WS-15) status unclear
    - Limited production numbers
    - Pilot training vs USAF unknown
    """
    specs = FighterAircraftSpecs(
        name="J-20",
        designation="Chengdu J-20",
        length_m=20.4,
        wingspan_m=13.0,
        height_m=4.45,
        wing_area_m2=73.0,
        empty_weight_kg=19400,
        max_takeoff_weight_kg=37000,
        max_speed_mach=2.0,
        cruise_speed_mach=1.2,  # Supercruise with WS-15
        combat_radius_km=1100,
        service_ceiling_m=20000,
        max_g=9,
        frontal_rcs_m2=0.005,  # Estimated
        rcs_confidence=0.45,
        internal_weapons=["PL-15", "PL-10"],
        num_internal_hardpoints=6,
        num_external_hardpoints=4,
        radar_name="Type 1475 AESA",
        radar_range_km=200,
        irst_equipped=True,
        overall_confidence=0.50
    )

    return FighterAircraftCAD(
        specs=specs,
        intake_type="dsi",
        stabilizer_cant_deg=15
    )


def create_j35_model() -> FighterAircraftCAD:
    """
    J-35 (FC-31 evolved) - Naval 5th generation fighter.

    For PLAN carriers (Type 003+).

    LIMITATIONS:
    - Even less data than J-20
    - Naval requirements affect design
    - Export potential (J-35E)
    """
    specs = FighterAircraftSpecs(
        name="J-35",
        designation="Shenyang J-35",
        length_m=17.3,
        wingspan_m=11.5,
        height_m=4.8,
        wing_area_m2=52.0,
        empty_weight_kg=15000,
        max_takeoff_weight_kg=28000,
        max_speed_mach=1.8,
        cruise_speed_mach=1.1,
        combat_radius_km=850,
        service_ceiling_m=18000,
        max_g=9,
        frontal_rcs_m2=0.003,  # Estimated, similar to F-35
        rcs_confidence=0.35,
        internal_weapons=["PL-15", "PL-10"],
        num_internal_hardpoints=4,
        num_external_hardpoints=6,
        radar_name="Unknown AESA",
        radar_range_km=150,
        irst_equipped=True,
        overall_confidence=0.40
    )

    return FighterAircraftCAD(
        specs=specs,
        intake_type="dsi",
        stabilizer_cant_deg=20
    )


# =============================================================================
# SECTION 5: NAVAL PLATFORM MODELS
# =============================================================================

@dataclass
class NavalPlatformSpecs:
    """Surface combatant specifications"""
    name: str
    hull_number: str
    class_name: str

    # Dimensions
    length_m: float
    beam_m: float
    draft_m: float
    displacement_tons: float

    # Propulsion
    max_speed_knots: float
    range_nm: float

    # Weapons
    vls_cells: int
    main_gun_mm: int
    ciws_count: int
    ssm_launchers: int
    asw_weapons: List[str]

    # Sensors
    radar_systems: List[str]
    sonar_systems: List[str]

    # Confidence
    confidence: float = 0.65


def create_type055_specs() -> NavalPlatformSpecs:
    """
    Type 055 "Renhai" class cruiser.

    China's most powerful surface combatant.
    Key component of carrier battle group defense.

    CAPABILITIES FOR F-35 DEFENSE:
    - 112-cell VLS (largest in world for destroyer/cruiser)
    - Multi-function phased array radar
    - Can launch HQ-9B, YJ-18, CJ-10

    LIMITATIONS:
    - Small class size (8 planned)
    - Radar performance vs stealth unknown
    - Network integration effectiveness unclear
    """
    return NavalPlatformSpecs(
        name="Type 055",
        hull_number="Various",
        class_name="Renhai",
        length_m=180.0,
        beam_m=20.0,
        draft_m=6.6,
        displacement_tons=13000,
        max_speed_knots=30,
        range_nm=5000,
        vls_cells=112,
        main_gun_mm=130,
        ciws_count=2,  # Type 1130
        ssm_launchers=0,  # VLS launched
        asw_weapons=["Yu-8", "rocket_torpedo"],
        radar_systems=["Type 346B", "Type 518", "Fire control"],
        sonar_systems=["Bow sonar", "Towed array"],
        confidence=0.60
    )


def create_type052d_specs() -> NavalPlatformSpecs:
    """
    Type 052D "Luyang III" class destroyer.

    Backbone of PLAN destroyer force.
    Most numerous modern destroyer class.
    """
    return NavalPlatformSpecs(
        name="Type 052D",
        hull_number="Various",
        class_name="Luyang III",
        length_m=157.0,
        beam_m=18.0,
        draft_m=6.0,
        displacement_tons=7500,
        max_speed_knots=30,
        range_nm=4500,
        vls_cells=64,
        main_gun_mm=130,
        ciws_count=1,
        ssm_launchers=0,
        asw_weapons=["Yu-8"],
        radar_systems=["Type 346A", "Type 518"],
        sonar_systems=["Bow sonar"],
        confidence=0.65
    )


# =============================================================================
# SECTION 6: INTEGRATED SYSTEM SUMMARY
# =============================================================================

def generate_parade_systems_report() -> str:
    """Generate comprehensive report on all parade weapon systems"""

    lines = []
    lines.append("=" * 80)
    lines.append("PLA PARADE WEAPON SYSTEMS - CAD AND CAPABILITY ASSESSMENT")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Classification: UNCLASSIFIED // PUBLIC RELEASE")
    lines.append("Data Sources: Open source only")
    lines.append("")

    # Strategic missiles
    lines.append("=" * 80)
    lines.append("SECTION 1: STRATEGIC MISSILES")
    lines.append("=" * 80)

    missiles = [
        ("DF-41 ICBM", create_df41_model()),
        ("DF-27 HGV", create_df27_model()),
        ("JL-3 SLBM", create_jl3_model()),
        ("YJ-21 Hypersonic ASBM", create_yj21_model()),
        ("DF-21D ASBM", create_df21d_model()),
    ]

    for name, model in missiles:
        lines.append(f"\n{name}")
        lines.append("-" * 40)
        if model.specs:
            lines.append(f"  Length: {model.specs.length_m:.1f} m")
            lines.append(f"  Diameter: {model.specs.diameter_m:.2f} m")
            lines.append(f"  Range: {model.specs.range_km:.0f} km")
            lines.append(f"  Max Speed: Mach {model.specs.max_speed_mach:.0f}")
            lines.append(f"  CEP: {model.specs.cep_m:.0f} m")
            lines.append(f"  Data Confidence: {model.specs.overall_confidence:.0%}")
            if model.specs.limitations:
                lines.append("  LIMITATIONS:")
                for lim in model.specs.limitations:
                    lines.append(f"    - {lim}")

    # Air defense
    lines.append("\n" + "=" * 80)
    lines.append("SECTION 2: AIR DEFENSE SYSTEMS")
    lines.append("=" * 80)

    ad_systems = [
        create_hq9b_model(),
        create_hq22_model(),
        create_hq17a_model(),
    ]

    for cad, specs in ad_systems:
        lines.append(f"\n{specs.name}")
        lines.append("-" * 40)
        lines.append(f"  Missile Length: {specs.missile_length_m:.1f} m")
        lines.append(f"  Max Range: {specs.max_range_km:.0f} km")
        lines.append(f"  Max Altitude: {specs.max_altitude_m:.0f} m")
        lines.append(f"  Max Speed: Mach {specs.max_speed_mach:.1f}")
        lines.append(f"  Seeker: {specs.seeker_type}")
        lines.append(f"  Pk vs Aircraft: {specs.pk_aerodynamic:.0%}")
        lines.append(f"  Data Confidence: {specs.confidence:.0%}")

    # Aircraft
    lines.append("\n" + "=" * 80)
    lines.append("SECTION 3: FIGHTER AIRCRAFT")
    lines.append("=" * 80)

    aircraft = [
        create_j20_model(),
        create_j35_model(),
    ]

    for ac in aircraft:
        lines.append(f"\n{ac.specs.name}")
        lines.append("-" * 40)
        lines.append(f"  Length: {ac.specs.length_m:.1f} m")
        lines.append(f"  Wingspan: {ac.specs.wingspan_m:.1f} m")
        lines.append(f"  Max Speed: Mach {ac.specs.max_speed_mach:.1f}")
        lines.append(f"  Combat Radius: {ac.specs.combat_radius_km:.0f} km")
        lines.append(f"  Frontal RCS: {ac.specs.frontal_rcs_m2:.4f} m²")
        lines.append(f"  RCS Confidence: {ac.specs.rcs_confidence:.0%}")
        lines.append(f"  Overall Confidence: {ac.specs.overall_confidence:.0%}")

    # Naval
    lines.append("\n" + "=" * 80)
    lines.append("SECTION 4: NAVAL PLATFORMS")
    lines.append("=" * 80)

    naval = [
        create_type055_specs(),
        create_type052d_specs(),
    ]

    for ship in naval:
        lines.append(f"\n{ship.name} ({ship.class_name} class)")
        lines.append("-" * 40)
        lines.append(f"  Length: {ship.length_m:.0f} m")
        lines.append(f"  Displacement: {ship.displacement_tons:.0f} tons")
        lines.append(f"  VLS Cells: {ship.vls_cells}")
        lines.append(f"  Max Speed: {ship.max_speed_knots:.0f} knots")
        lines.append(f"  Data Confidence: {ship.confidence:.0%}")

    # Shortcomings summary
    lines.append("\n" + "=" * 80)
    lines.append("CRITICAL SHORTCOMINGS PREVENTING PERFECT MODELING")
    lines.append("=" * 80)
    lines.append("""
1. CLASSIFICATION BARRIERS
   - Actual performance data is classified (both Chinese and US)
   - RCS values are estimates with wide uncertainty bounds
   - Kill probability calculations are theoretical
   - Countermeasure effectiveness unknown on both sides

2. PHYSICS LIMITATIONS
   - Radar equation fundamentals limit detection vs stealth
   - Atmospheric effects vary with conditions
   - Hypersonic guidance in plasma sheath unverified
   - Seeker performance at extreme speeds uncertain

3. OPERATIONAL UNKNOWNS
   - Crew training and proficiency varies
   - Maintenance state affects availability
   - Network latency and reliability varies
   - Doctrine and tactics classified

4. TECHNOLOGY GAPS
   - Latest variants not yet in public domain
   - Upgrades happen faster than public knowledge
   - Software/firmware capabilities hidden
   - Integration effectiveness unmeasurable

5. ADVERSARY ADAPTATION
   - F-35 EW suite constantly updated
   - Tactics evolve based on intelligence
   - Countermeasure effectiveness improves
   - Cannot model adversary response to our systems
""")

    lines.append("=" * 80)
    return "\n".join(lines)


if __name__ == "__main__":
    report = generate_parade_systems_report()
    print(report)

    # Save report
    with open("parade_systems_report.txt", "w") as f:
        f.write(report)

    print("\nReport saved to: parade_systems_report.txt")

    # Generate CAD examples
    print("\nGenerating CAD models...")

    df41 = create_df41_model()
    geometry = df41.generate_geometry(resolution=24)
    print(f"DF-41 CAD: {len(geometry.mesh.triangles)} triangles")

    hq9b_cad, hq9b_specs = create_hq9b_model()
    hq9b_geom = hq9b_cad.generate_geometry(resolution=24)
    print(f"HQ-9B CAD: {len(hq9b_geom.mesh.triangles)} triangles")

    j20 = create_j20_model()
    j20_geom = j20.generate_simplified_geometry()
    print(f"J-20 CAD: {len(j20_geom.mesh.triangles)} triangles")

    print("\nCAD generation complete.")
