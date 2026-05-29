#!/usr/bin/env python3
"""
Type 052D Destroyer CAD Model

Implements the PLA Navy Type 052D guided missile destroyer (Luyang III-class)
with enhanced capabilities including dual-face rotating AESA radar system.

PLATFORM OVERVIEW:
- Designation: Type 052D (NATO: Luyang III-class)
- Operator: PLA Navy
- Role: Multi-role guided missile destroyer
- First commissioned: 2014 (Kunming, hull 172)
- Enhanced variant: 2026 (Loudi, hull 176)

KEY SYSTEMS (Enhanced Variant - 2026):
- Radar: Dual-face rotating AESA radar (Type 346B variant)
- Air Defense: HQ-9B long-range SAM (VLS)
- Anti-Ship: YJ-18 supersonic cruise missile
- ASW: Yu-8 anti-submarine rocket, towed sonar
- CIWS: Type 1130 11-barrel 30mm gatling gun

ENHANCEMENTS (Loudi, 2026):
- New dual-face rotating AESA radar on main mast
- Improved air defense, sea attack, and task force command
- Enhanced long-range assault and strike capabilities
- Better defense coordination for allied vessels

SOURCE:
Based on Global Times article (2026-01-02):
"PLA Navy commissions new Type 052D destroyer with enhanced capabilities"
- https://www.globaltimes.cn/page/202601/1352031.shtml

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Type052DVariant(Enum):
    """Type 052D destroyer variants"""
    BASELINE = "baseline"  # 2014-2019 (Hull 172-175)
    IMPROVED = "improved"  # 2020-2025 (Hull 117-175)
    ENHANCED = "enhanced"  # 2026+ (Hull 176+, Loudi)


@dataclass
class Type052DRadarParameters:
    """
    Type 052D radar system parameters

    BASELINE (Type 346A):
    - Four fixed AESA panels (S-band)
    - Detection range: ~450 km vs 5 m² RCS (80% conf)
    - Track capacity: 100+ targets

    ENHANCED (Type 346B dual-face rotating):
    - Two rotating AESA faces (S-band)
    - Detection range: ~500 km vs 5 m² RCS (70% conf, estimated)
    - Track capacity: 200+ targets (improved processing)
    - Enhanced multi-target engagement
    """
    variant: Type052DVariant
    frequency_ghz: float  # S-band (3-4 GHz)
    peak_power_kw: float  # Per face
    aperture_area_m2: float  # Per face
    detection_range_km: float  # vs 5 m² RCS
    track_capacity: int
    simultaneous_engagement: int
    tracking_accuracy_deg: float  # Angular accuracy (1-sigma)
    confidence: float


@dataclass
class Type052DWeaponParameters:
    """Type 052D weapon systems"""
    # VLS (64 cells, universal)
    vls_cells: int
    hq9b_range_km: float  # HQ-9B long-range SAM
    hq9b_intercept_altitude_km: float
    hq9b_pk_vs_fighter: float  # vs 4th-gen fighter

    # YJ-18 anti-ship cruise missile
    yj18_range_km: float
    yj18_speed_mach: float  # Terminal phase
    yj18_pk_vs_destroyer: float

    # Type 1130 CIWS
    ciws_range_km: float
    ciws_fire_rate_rpm: int
    ciws_pk_vs_missile: float  # Single engagement


@dataclass
class Type052DSpecifications:
    """Type 052D destroyer specifications"""
    variant: Type052DVariant
    hull_number: str
    ship_name: str
    commissioned_date: int

    # Physical characteristics
    length_m: float
    beam_m: float
    draft_m: float
    displacement_tons: float

    # Performance
    max_speed_knots: float
    cruise_speed_knots: float
    range_nm: float  # At cruise speed

    # Systems
    radar: Type052DRadarParameters
    weapons: Type052DWeaponParameters

    # Confidence
    overall_confidence: float


class Type052DModel:
    """
    Type 052D destroyer CAD model.

    Implements radar detection, weapons engagement, and air defense
    capabilities for PLA Navy Type 052D destroyers.
    """

    def __init__(self, variant: Type052DVariant = Type052DVariant.ENHANCED):
        """
        Initialize Type 052D model

        Args:
            variant: Destroyer variant (baseline, improved, enhanced)
        """
        self.variant = variant
        self.specs = self._initialize_specifications(variant)

    def _initialize_specifications(
        self,
        variant: Type052DVariant
    ) -> Type052DSpecifications:
        """Initialize specifications for given variant"""

        if variant == Type052DVariant.ENHANCED:
            # Loudi (Hull 176) - 2026 Enhanced variant
            radar = Type052DRadarParameters(
                variant=Type052DVariant.ENHANCED,
                frequency_ghz=3.3,  # S-band
                peak_power_kw=180,  # Estimated per face
                aperture_area_m2=12,  # Dual-face rotating
                detection_range_km=500,  # vs 5 m² RCS (estimated improvement)
                track_capacity=200,
                simultaneous_engagement=12,  # Enhanced capability
                tracking_accuracy_deg=0.5,  # Improved
                confidence=0.60  # Based on public reporting
            )

            weapons = Type052DWeaponParameters(
                vls_cells=64,
                hq9b_range_km=250,  # HQ-9B long-range
                hq9b_intercept_altitude_km=30,
                hq9b_pk_vs_fighter=0.85,
                yj18_range_km=540,  # YJ-18A extended range
                yj18_speed_mach=3.0,  # Terminal supersonic
                yj18_pk_vs_destroyer=0.75,
                ciws_range_km=3.5,
                ciws_fire_rate_rpm=11000,  # Type 1130
                ciws_pk_vs_missile=0.90  # Per engagement
            )

            return Type052DSpecifications(
                variant=Type052DVariant.ENHANCED,
                hull_number="176",
                ship_name="Loudi",
                commissioned_date=2026,
                length_m=157,
                beam_m=18,
                draft_m=6.5,
                displacement_tons=7500,
                max_speed_knots=30,
                cruise_speed_knots=18,
                range_nm=4500,
                radar=radar,
                weapons=weapons,
                overall_confidence=0.60
            )

        elif variant == Type052DVariant.BASELINE:
            # Kunming (Hull 172) - 2014 Baseline variant
            radar = Type052DRadarParameters(
                variant=Type052DVariant.BASELINE,
                frequency_ghz=3.3,
                peak_power_kw=150,
                aperture_area_m2=10,  # Fixed four-face
                detection_range_km=450,  # vs 5 m² RCS
                track_capacity=100,
                simultaneous_engagement=8,
                tracking_accuracy_deg=0.8,
                confidence=0.65
            )

            weapons = Type052DWeaponParameters(
                vls_cells=64,
                hq9b_range_km=200,  # HQ-9 baseline
                hq9b_intercept_altitude_km=27,
                hq9b_pk_vs_fighter=0.80,
                yj18_range_km=400,  # YJ-18 baseline
                yj18_speed_mach=2.5,
                yj18_pk_vs_destroyer=0.70,
                ciws_range_km=3.0,
                ciws_fire_rate_rpm=10000,
                ciws_pk_vs_missile=0.85
            )

            return Type052DSpecifications(
                variant=Type052DVariant.BASELINE,
                hull_number="172",
                ship_name="Kunming",
                commissioned_date=2014,
                length_m=157,
                beam_m=18,
                draft_m=6.5,
                displacement_tons=7200,
                max_speed_knots=30,
                cruise_speed_knots=18,
                range_nm=4000,
                radar=radar,
                weapons=weapons,
                overall_confidence=0.65
            )

        else:
            raise ValueError(f"Unsupported variant: {variant}")

    def calculate_radar_detection_range(
        self,
        target_rcs_m2: float,
        detection_probability: float = 0.90
    ) -> float:
        """
        Calculate radar detection range vs target.

        Uses radar range equation with Type 052D AESA parameters.

        Args:
            target_rcs_m2: Target RCS (m²)
            detection_probability: Required detection probability

        Returns:
            Detection range (km)
        """
        radar = self.specs.radar

        # Reference: 500 km vs 5 m² RCS (enhanced variant)
        reference_range_km = radar.detection_range_km
        reference_rcs_m2 = 5.0

        # Radar range equation: R ~ (RCS)^(1/4)
        range_km = reference_range_km * (target_rcs_m2 / reference_rcs_m2) ** 0.25

        # Adjust for detection probability
        # Pd = 0.90 is baseline, Pd = 0.50 extends range by ~20%
        pd_factor = (0.90 / detection_probability) ** 0.25
        range_km *= pd_factor

        return range_km

    def calculate_hq9b_engagement_envelope(
        self,
        target_altitude_km: float,
        target_speed_mach: float,
        target_rcs_m2: float
    ) -> Dict[str, float]:
        """
        Calculate HQ-9B SAM engagement envelope vs target.

        Args:
            target_altitude_km: Target altitude (km)
            target_speed_mach: Target speed (Mach)
            target_rcs_m2: Target RCS (m²)

        Returns:
            Dict with max_range_km, min_range_km, pk
        """
        weapons = self.specs.weapons

        # Base envelope
        max_range_km = weapons.hq9b_range_km
        min_range_km = 5  # Minimum engagement range

        # Altitude constraints
        if target_altitude_km > weapons.hq9b_intercept_altitude_km:
            max_range_km *= 0.6  # Reduced range at high altitude

        # Speed penalties (difficult engagement vs fast targets)
        if target_speed_mach > 2.0:
            max_range_km *= 0.8

        # RCS factor (easier to engage large RCS targets)
        if target_rcs_m2 < 1.0:
            max_range_km *= 0.85

        # Pk calculation
        pk = weapons.hq9b_pk_vs_fighter

        # Adjust for target characteristics
        if target_rcs_m2 < 0.1:
            pk *= 0.75  # Stealth target
        if target_speed_mach > 2.5:
            pk *= 0.85  # Supersonic maneuvering target

        return {
            "max_range_km": max_range_km,
            "min_range_km": min_range_km,
            "pk": pk
        }

    def calculate_task_force_air_defense_coverage(
        self,
        num_type052d: int = 4,
        formation_radius_km: float = 30
    ) -> Dict[str, float]:
        """
        Calculate air defense coverage for Type 052D task force.

        Based on Global Times reporting that enhanced Type 052D can
        "defend allied vessels" with improved coordination.

        Args:
            num_type052d: Number of Type 052D destroyers in task force
            formation_radius_km: Task force formation radius

        Returns:
            Dict with coverage metrics
        """
        weapons = self.specs.weapons

        # Single ship coverage
        single_ship_coverage_km2 = np.pi * weapons.hq9b_range_km ** 2

        # Task force overlapping coverage (coordination bonus)
        if self.variant == Type052DVariant.ENHANCED:
            coordination_factor = 1.3  # Enhanced coordination capability
        else:
            coordination_factor = 1.15  # Baseline coordination

        total_coverage_km2 = (
            single_ship_coverage_km2 * num_type052d * coordination_factor
        )

        # Layered defense depth
        max_engagement_range_km = weapons.hq9b_range_km
        min_engagement_range_km = weapons.ciws_range_km
        defense_layers = 3  # Long-range SAM, medium-range SAM, CIWS

        # Simultaneous engagement capacity
        total_engagement_capacity = (
            self.specs.radar.simultaneous_engagement * num_type052d
        )

        return {
            "coverage_area_km2": total_coverage_km2,
            "max_engagement_range_km": max_engagement_range_km,
            "min_engagement_range_km": min_engagement_range_km,
            "defense_layers": defense_layers,
            "simultaneous_engagements": total_engagement_capacity,
            "coordination_factor": coordination_factor
        }

    def generate_specification_report(self) -> str:
        """Generate detailed specification report"""
        report = []
        report.append("=" * 80)
        report.append("TYPE 052D DESTROYER CAD MODEL")
        report.append("=" * 80)
        report.append("")
        report.append(f"Variant: {self.specs.variant.value.upper()}")
        report.append(f"Hull Number: {self.specs.hull_number}")
        report.append(f"Ship Name: {self.specs.ship_name}")
        report.append(f"Commissioned: {self.specs.commissioned_date}")
        report.append(f"Overall Confidence: {self.specs.overall_confidence:.0%}")
        report.append("")

        report.append("PHYSICAL CHARACTERISTICS")
        report.append("-" * 80)
        report.append(f"Length: {self.specs.length_m} m")
        report.append(f"Beam: {self.specs.beam_m} m")
        report.append(f"Draft: {self.specs.draft_m} m")
        report.append(f"Displacement: {self.specs.displacement_tons} tons")
        report.append(f"Max Speed: {self.specs.max_speed_knots} knots")
        report.append(f"Range: {self.specs.range_nm} nm @ {self.specs.cruise_speed_knots} knots")
        report.append("")

        report.append("RADAR SYSTEM")
        report.append("-" * 80)
        if self.specs.radar.variant == Type052DVariant.ENHANCED:
            report.append("Type: Dual-face rotating AESA (Type 346B variant)")
        else:
            report.append("Type: Four-face fixed AESA (Type 346A)")
        report.append(f"Frequency: {self.specs.radar.frequency_ghz:.1f} GHz (S-band)")
        report.append(f"Detection Range: {self.specs.radar.detection_range_km} km (vs 5 m² RCS)")
        report.append(f"Track Capacity: {self.specs.radar.track_capacity}+ targets")
        report.append(f"Simultaneous Engagement: {self.specs.radar.simultaneous_engagement} targets")
        report.append(f"Tracking Accuracy: {self.specs.radar.tracking_accuracy_deg}° (1-sigma)")
        report.append(f"Confidence: {self.specs.radar.confidence:.0%}")
        report.append("")

        report.append("WEAPON SYSTEMS")
        report.append("-" * 80)
        report.append(f"VLS Cells: {self.specs.weapons.vls_cells} (universal)")
        report.append("")
        report.append("HQ-9B Long-Range SAM:")
        report.append(f"  Range: {self.specs.weapons.hq9b_range_km} km")
        report.append(f"  Intercept Altitude: {self.specs.weapons.hq9b_intercept_altitude_km} km")
        report.append(f"  Pk vs Fighter: {self.specs.weapons.hq9b_pk_vs_fighter:.0%}")
        report.append("")
        report.append("YJ-18 Anti-Ship Cruise Missile:")
        report.append(f"  Range: {self.specs.weapons.yj18_range_km} km")
        report.append(f"  Terminal Speed: Mach {self.specs.weapons.yj18_speed_mach}")
        report.append(f"  Pk vs Destroyer: {self.specs.weapons.yj18_pk_vs_destroyer:.0%}")
        report.append("")
        report.append("Type 1130 CIWS:")
        report.append(f"  Range: {self.specs.weapons.ciws_range_km} km")
        report.append(f"  Fire Rate: {self.specs.weapons.ciws_fire_rate_rpm:,} rpm")
        report.append(f"  Pk vs Missile: {self.specs.weapons.ciws_pk_vs_missile:.0%}")
        report.append("")

        # Enhanced capabilities (Loudi variant)
        if self.specs.variant == Type052DVariant.ENHANCED:
            report.append("ENHANCED CAPABILITIES (2026)")
            report.append("-" * 80)
            report.append("✓ Dual-face rotating AESA radar (improved detection)")
            report.append("✓ Enhanced air defense coordination")
            report.append("✓ Improved long-range assault and strike missions")
            report.append("✓ Better task force command capabilities")
            report.append("✓ Enhanced defense of allied vessels")
            report.append("")

        report.append("=" * 80)
        report.append("Classification: UNCLASSIFIED // PUBLIC RELEASE")
        report.append("Source: Global Times (2026-01-02), open-source reporting")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Demonstration of Type 052D model"""

    # Enhanced variant (Loudi, 2026)
    destroyer_enhanced = Type052DModel(variant=Type052DVariant.ENHANCED)
    print(destroyer_enhanced.generate_specification_report())

    print("\n\n" + "=" * 80)
    print("DETECTION RANGE EXAMPLES")
    print("=" * 80)

    test_targets = [
        ("F-35A Lightning II", 0.005),  # Stealth fighter
        ("F/A-18E Super Hornet", 1.0),  # 4th-gen fighter
        ("B-52 Stratofortress", 100),   # Large bomber
    ]

    for target_name, rcs in test_targets:
        detection_range = destroyer_enhanced.calculate_radar_detection_range(
            target_rcs_m2=rcs
        )
        print(f"{target_name:25s} (RCS {rcs:6.3f} m²): {detection_range:6.1f} km")

    print("\n\n" + "=" * 80)
    print("HQ-9B ENGAGEMENT ENVELOPE EXAMPLES")
    print("=" * 80)

    test_engagements = [
        ("F-35A (stealth, subsonic)", 10, 0.8, 0.005),
        ("F/A-18E (conventional)", 8, 1.2, 1.0),
        ("B-1B (high-speed bomber)", 12, 1.8, 10),
    ]

    for target_name, alt_km, speed_mach, rcs in test_engagements:
        envelope = destroyer_enhanced.calculate_hq9b_engagement_envelope(
            target_altitude_km=alt_km,
            target_speed_mach=speed_mach,
            target_rcs_m2=rcs
        )
        print(f"\n{target_name}:")
        print(f"  Max Range: {envelope['max_range_km']:.1f} km")
        print(f"  Min Range: {envelope['min_range_km']:.1f} km")
        print(f"  Pk: {envelope['pk']:.0%}")

    print("\n\n" + "=" * 80)
    print("TASK FORCE AIR DEFENSE COVERAGE")
    print("=" * 80)

    task_force = destroyer_enhanced.calculate_task_force_air_defense_coverage(
        num_type052d=4,
        formation_radius_km=30
    )

    print(f"Task Force Configuration: 4x Type 052D (Enhanced)")
    print(f"Formation Radius: 30 km")
    print("")
    print(f"Total Coverage Area: {task_force['coverage_area_km2']:,.0f} km²")
    print(f"Max Engagement Range: {task_force['max_engagement_range_km']:.0f} km")
    print(f"Defense Layers: {task_force['defense_layers']}")
    print(f"Simultaneous Engagements: {task_force['simultaneous_engagements']}")
    print(f"Coordination Factor: {task_force['coordination_factor']:.2f}x")


if __name__ == "__main__":
    main()
