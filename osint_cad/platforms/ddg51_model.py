#!/usr/bin/env python3
"""
DDG-51 Arleigh Burke-class Destroyer CAD Model

Implements the US Navy Arleigh Burke-class guided missile destroyer
with Aegis Combat System and integrated air/missile defense capabilities.

PLATFORM OVERVIEW:
- Designation: DDG-51 (Arleigh Burke-class)
- Operator: US Navy
- Role: Multi-role guided missile destroyer
- First commissioned: 1991 (USS Arleigh Burke, DDG-51)
- Flight III variant: 2024+ (improved radar and power)

KEY SYSTEMS (Flight III - 2024+):
- Radar: AN/SPY-6(V)1 AMDR (Air and Missile Defense Radar)
- Air Defense: SM-2, SM-3, SM-6 missiles (VLS)
- Anti-Ship: Harpoon, Naval Strike Missile (NSM)
- ASW: MK 46/54 torpedoes, SQS-53 sonar
- CIWS: Phalanx 20mm, SeaRAM (on some ships)

VARIANTS:
- Flight I/II (DDG-51 to DDG-78): AN/SPY-1D radar
- Flight IIA (DDG-79 to DDG-124): Helicopter hangars, improved systems
- Flight III (DDG-125+): AN/SPY-6 AMDR, enhanced power

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class DDG51Variant(Enum):
    """DDG-51 Arleigh Burke destroyer variants"""
    FLIGHT_I = "flight_i"      # DDG-51 to DDG-71 (1991-1999)
    FLIGHT_II = "flight_ii"    # DDG-72 to DDG-78 (1998-2001)
    FLIGHT_IIA = "flight_iia"  # DDG-79 to DDG-124 (2000-2022)
    FLIGHT_III = "flight_iii"  # DDG-125+ (2024+)


@dataclass
class DDG51RadarParameters:
    """
    DDG-51 radar system parameters

    FLIGHT I/II/IIA (AN/SPY-1D):
    - Four fixed phased array panels (S-band)
    - Detection range: ~500 km vs 1 m² RCS (85% conf)
    - Track capacity: 200+ targets

    FLIGHT III (AN/SPY-6 AMDR):
    - Four fixed AESA panels (S-band)
    - Detection range: ~600 km vs 1 m² RCS (80% conf)
    - Track capacity: 500+ targets
    - 30x sensitivity improvement over SPY-1D
    """
    variant: DDG51Variant
    radar_type: str
    frequency_ghz: float  # S-band (3-4 GHz)
    peak_power_kw: float
    aperture_area_m2: float  # Per face
    detection_range_km: float  # vs 1 m² RCS
    track_capacity: int
    simultaneous_engagement: int
    tracking_accuracy_deg: float  # Angular accuracy (1-sigma)
    confidence: float


@dataclass
class DDG51WeaponParameters:
    """DDG-51 weapon systems"""
    # VLS (90-96 cells depending on variant)
    vls_cells: int
    sm2_range_km: float  # SM-2 Block IIIA/C
    sm3_range_km: float  # SM-3 Block IIA (BMD)
    sm6_range_km: float  # SM-6 Dual I/II
    sm6_pk_vs_fighter: float  # vs 4th-gen fighter
    sm6_pk_vs_cruise_missile: float

    # Harpoon/NSM anti-ship
    harpoon_range_km: float
    nsm_range_km: float
    nsm_pk_vs_ship: float

    # Phalanx CIWS
    ciws_range_km: float
    ciws_fire_rate_rpm: int
    ciws_pk_vs_missile: float  # Single engagement


@dataclass
class DDG51Specifications:
    """DDG-51 destroyer specifications"""
    variant: DDG51Variant
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
    radar: DDG51RadarParameters
    weapons: DDG51WeaponParameters

    # Confidence
    overall_confidence: float


class DDG51Model:
    """
    DDG-51 Arleigh Burke-class destroyer CAD model.

    Implements radar detection, weapons engagement, and air defense
    capabilities for US Navy DDG-51 destroyers.
    """

    def __init__(self, variant: DDG51Variant = DDG51Variant.FLIGHT_III):
        """
        Initialize DDG-51 model

        Args:
            variant: Destroyer variant (flight_i, flight_ii, flight_iia, flight_iii)
        """
        self.variant = variant
        self.specs = self._initialize_specifications(variant)

    def _initialize_specifications(
        self,
        variant: DDG51Variant
    ) -> DDG51Specifications:
        """Initialize specifications for given variant"""

        if variant == DDG51Variant.FLIGHT_III:
            # DDG-125 Jack H. Lucas - 2024 Flight III variant
            radar = DDG51RadarParameters(
                variant=DDG51Variant.FLIGHT_III,
                radar_type="AN/SPY-6(V)1 AMDR",
                frequency_ghz=3.3,  # S-band
                peak_power_kw=6000,  # Significantly more power
                aperture_area_m2=14,  # Larger AESA arrays
                detection_range_km=600,  # vs 1 m² RCS
                track_capacity=500,
                simultaneous_engagement=30,  # Enhanced capability
                tracking_accuracy_deg=0.3,  # Improved
                confidence=0.75  # Based on public reporting
            )

            weapons = DDG51WeaponParameters(
                vls_cells=96,
                sm2_range_km=170,  # SM-2 Block IIIC
                sm3_range_km=2500,  # SM-3 Block IIA (exoatmospheric)
                sm6_range_km=370,  # SM-6 Dual II
                sm6_pk_vs_fighter=0.90,
                sm6_pk_vs_cruise_missile=0.95,
                harpoon_range_km=0,  # Flight III uses NSM instead
                nsm_range_km=185,  # Naval Strike Missile
                nsm_pk_vs_ship=0.85,
                ciws_range_km=3.6,
                ciws_fire_rate_rpm=4500,  # Phalanx 1B
                ciws_pk_vs_missile=0.85
            )

            return DDG51Specifications(
                variant=DDG51Variant.FLIGHT_III,
                hull_number="DDG-125",
                ship_name="Jack H. Lucas",
                commissioned_date=2024,
                length_m=155,
                beam_m=20,
                draft_m=9.4,
                displacement_tons=9800,
                max_speed_knots=30,
                cruise_speed_knots=20,
                range_nm=4400,
                radar=radar,
                weapons=weapons,
                overall_confidence=0.75
            )

        elif variant == DDG51Variant.FLIGHT_IIA:
            # DDG-79 Oscar Austin - Flight IIA variant
            radar = DDG51RadarParameters(
                variant=DDG51Variant.FLIGHT_IIA,
                radar_type="AN/SPY-1D(V)",
                frequency_ghz=3.3,
                peak_power_kw=4000,
                aperture_area_m2=12,  # Four-face PESA
                detection_range_km=500,  # vs 1 m² RCS
                track_capacity=200,
                simultaneous_engagement=18,
                tracking_accuracy_deg=0.5,
                confidence=0.85  # Well-documented system
            )

            weapons = DDG51WeaponParameters(
                vls_cells=96,
                sm2_range_km=167,  # SM-2 Block IIIA
                sm3_range_km=700,  # SM-3 Block IA
                sm6_range_km=240,  # SM-6 Dual I
                sm6_pk_vs_fighter=0.85,
                sm6_pk_vs_cruise_missile=0.90,
                harpoon_range_km=124,  # Harpoon Block II
                nsm_range_km=0,  # Not on Flight IIA
                nsm_pk_vs_ship=0.0,
                ciws_range_km=3.6,
                ciws_fire_rate_rpm=4500,
                ciws_pk_vs_missile=0.85
            )

            return DDG51Specifications(
                variant=DDG51Variant.FLIGHT_IIA,
                hull_number="DDG-79",
                ship_name="Oscar Austin",
                commissioned_date=2000,
                length_m=155,
                beam_m=20,
                draft_m=9.4,
                displacement_tons=9200,
                max_speed_knots=30,
                cruise_speed_knots=20,
                range_nm=4400,
                radar=radar,
                weapons=weapons,
                overall_confidence=0.85
            )

        elif variant == DDG51Variant.FLIGHT_I:
            # DDG-51 Arleigh Burke - Flight I variant
            radar = DDG51RadarParameters(
                variant=DDG51Variant.FLIGHT_I,
                radar_type="AN/SPY-1D",
                frequency_ghz=3.3,
                peak_power_kw=4000,
                aperture_area_m2=12,
                detection_range_km=450,  # vs 1 m² RCS
                track_capacity=100,
                simultaneous_engagement=12,
                tracking_accuracy_deg=0.6,
                confidence=0.90  # Very well documented
            )

            weapons = DDG51WeaponParameters(
                vls_cells=90,
                sm2_range_km=166,  # SM-2 Block III
                sm3_range_km=0,  # Not on Flight I
                sm6_range_km=0,  # Not on Flight I
                sm6_pk_vs_fighter=0.0,
                sm6_pk_vs_cruise_missile=0.0,
                harpoon_range_km=124,
                nsm_range_km=0,
                nsm_pk_vs_ship=0.0,
                ciws_range_km=3.6,
                ciws_fire_rate_rpm=3000,  # Phalanx 1A
                ciws_pk_vs_missile=0.80
            )

            return DDG51Specifications(
                variant=DDG51Variant.FLIGHT_I,
                hull_number="DDG-51",
                ship_name="Arleigh Burke",
                commissioned_date=1991,
                length_m=154,
                beam_m=20,
                draft_m=9.4,
                displacement_tons=8300,
                max_speed_knots=30,
                cruise_speed_knots=20,
                range_nm=4400,
                radar=radar,
                weapons=weapons,
                overall_confidence=0.90
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

        Uses radar range equation with DDG-51 Aegis parameters.

        Args:
            target_rcs_m2: Target RCS (m²)
            detection_probability: Required detection probability

        Returns:
            Detection range (km)
        """
        radar = self.specs.radar

        # Reference: 600 km vs 1 m² RCS (Flight III)
        reference_range_km = radar.detection_range_km
        reference_rcs_m2 = 1.0

        # Radar range equation: R ~ (RCS)^(1/4)
        range_km = reference_range_km * (target_rcs_m2 / reference_rcs_m2) ** 0.25

        # Adjust for detection probability
        # Pd = 0.90 is baseline, Pd = 0.50 extends range by ~20%
        pd_factor = (0.90 / detection_probability) ** 0.25
        range_km *= pd_factor

        return range_km

    def calculate_sm6_engagement_envelope(
        self,
        target_altitude_km: float,
        target_speed_mach: float,
        target_rcs_m2: float
    ) -> Dict[str, float]:
        """
        Calculate SM-6 SAM engagement envelope vs target.

        Args:
            target_altitude_km: Target altitude (km)
            target_speed_mach: Target speed (Mach)
            target_rcs_m2: Target RCS (m²)

        Returns:
            Dict with max_range_km, min_range_km, pk
        """
        if self.variant in [DDG51Variant.FLIGHT_I, DDG51Variant.FLIGHT_II]:
            # SM-6 not available on Flight I/II
            return {
                "max_range_km": 0,
                "min_range_km": 0,
                "pk": 0.0,
                "available": False
            }

        weapons = self.specs.weapons

        # Base envelope
        max_range_km = weapons.sm6_range_km
        min_range_km = 10  # Minimum engagement range

        # Altitude constraints (SM-6 has excellent high-altitude performance)
        if target_altitude_km > 33:
            max_range_km *= 0.8  # Reduced range at very high altitude
        elif target_altitude_km < 0.1:
            max_range_km *= 0.7  # Sea-skimming targets harder

        # Speed penalties
        if target_speed_mach > 3.0:
            max_range_km *= 0.75  # High-speed targets

        # RCS factor (SM-6 has excellent seeker)
        if target_rcs_m2 < 0.1:
            max_range_km *= 0.85

        # Pk calculation
        pk = weapons.sm6_pk_vs_fighter

        # Adjust for target characteristics
        if target_rcs_m2 < 0.01:
            pk *= 0.80  # Stealth target
        if target_speed_mach > 2.5:
            pk *= 0.85  # Supersonic maneuvering target
        if target_altitude_km < 0.05:
            pk *= 0.75  # Sea-skimmer

        return {
            "max_range_km": max_range_km,
            "min_range_km": min_range_km,
            "pk": pk,
            "available": True
        }

    def calculate_sm3_bmd_envelope(
        self,
        threat_type: str,
        threat_range_km: float
    ) -> Dict[str, float]:
        """
        Calculate SM-3 Ballistic Missile Defense envelope.

        Args:
            threat_type: "srbm", "mrbm", "irbm", "icbm"
            threat_range_km: Range of incoming missile

        Returns:
            Dict with intercept_range_km, pk, available
        """
        if self.variant == DDG51Variant.FLIGHT_I:
            return {"intercept_range_km": 0, "pk": 0.0, "available": False}

        weapons = self.specs.weapons

        if weapons.sm3_range_km == 0:
            return {"intercept_range_km": 0, "pk": 0.0, "available": False}

        # SM-3 engagement envelope
        base_range = weapons.sm3_range_km

        # Pk based on threat type
        if threat_type == "srbm":
            pk = 0.85
            max_range = min(base_range, 500)
        elif threat_type == "mrbm":
            pk = 0.75
            max_range = min(base_range, 1500)
        elif threat_type == "irbm":
            pk = 0.60
            max_range = min(base_range, 2500)
        else:  # ICBM
            pk = 0.45
            max_range = base_range

        return {
            "intercept_range_km": max_range,
            "pk": pk,
            "available": True
        }

    def calculate_carrier_strike_group_defense(
        self,
        num_ddg51: int = 2,
        formation_radius_km: float = 50
    ) -> Dict[str, float]:
        """
        Calculate air defense coverage for Carrier Strike Group.

        DDG-51 provides primary air defense for CSG with
        Aegis Combat System coordination.

        Args:
            num_ddg51: Number of DDG-51 destroyers in CSG
            formation_radius_km: CSG formation radius

        Returns:
            Dict with coverage metrics
        """
        weapons = self.specs.weapons

        # Single ship coverage (SM-6 range)
        sm6_range = weapons.sm6_range_km if weapons.sm6_range_km > 0 else weapons.sm2_range_km
        single_ship_coverage_km2 = np.pi * sm6_range ** 2

        # Cooperative Engagement Capability (CEC) bonus
        if self.variant in [DDG51Variant.FLIGHT_IIA, DDG51Variant.FLIGHT_III]:
            cec_factor = 1.4  # 40% improvement with CEC
        else:
            cec_factor = 1.15  # Basic coordination

        total_coverage_km2 = (
            single_ship_coverage_km2 * num_ddg51 * cec_factor
        )

        # Layered defense depth
        max_engagement_range_km = sm6_range
        min_engagement_range_km = weapons.ciws_range_km
        defense_layers = 4  # SM-6 outer, SM-2 middle, ESSM inner, CIWS point

        # Simultaneous engagement capacity
        total_engagement_capacity = (
            self.specs.radar.simultaneous_engagement * num_ddg51
        )

        # Magazine depth
        total_vls_cells = weapons.vls_cells * num_ddg51

        return {
            "coverage_area_km2": total_coverage_km2,
            "max_engagement_range_km": max_engagement_range_km,
            "min_engagement_range_km": min_engagement_range_km,
            "defense_layers": defense_layers,
            "simultaneous_engagements": total_engagement_capacity,
            "total_vls_cells": total_vls_cells,
            "cec_factor": cec_factor
        }

    def generate_specification_report(self) -> str:
        """Generate detailed specification report"""
        report = []
        report.append("=" * 80)
        report.append("DDG-51 ARLEIGH BURKE-CLASS DESTROYER CAD MODEL")
        report.append("=" * 80)
        report.append("")
        report.append(f"Variant: {self.specs.variant.value.upper()}")
        report.append(f"Hull Number: {self.specs.hull_number}")
        report.append(f"Ship Name: USS {self.specs.ship_name}")
        report.append(f"Commissioned: {self.specs.commissioned_date}")
        report.append(f"Overall Confidence: {self.specs.overall_confidence:.0%}")
        report.append("")

        report.append("PHYSICAL CHARACTERISTICS")
        report.append("-" * 80)
        report.append(f"Length: {self.specs.length_m} m")
        report.append(f"Beam: {self.specs.beam_m} m")
        report.append(f"Draft: {self.specs.draft_m} m")
        report.append(f"Displacement: {self.specs.displacement_tons:,} tons")
        report.append(f"Max Speed: {self.specs.max_speed_knots} knots")
        report.append(f"Range: {self.specs.range_nm:,} nm @ {self.specs.cruise_speed_knots} knots")
        report.append("")

        report.append("RADAR SYSTEM")
        report.append("-" * 80)
        report.append(f"Type: {self.specs.radar.radar_type}")
        report.append(f"Frequency: {self.specs.radar.frequency_ghz:.1f} GHz (S-band)")
        report.append(f"Peak Power: {self.specs.radar.peak_power_kw:,} kW")
        report.append(f"Detection Range: {self.specs.radar.detection_range_km} km (vs 1 m² RCS)")
        report.append(f"Track Capacity: {self.specs.radar.track_capacity}+ targets")
        report.append(f"Simultaneous Engagement: {self.specs.radar.simultaneous_engagement} targets")
        report.append(f"Tracking Accuracy: {self.specs.radar.tracking_accuracy_deg}° (1-sigma)")
        report.append(f"Confidence: {self.specs.radar.confidence:.0%}")
        report.append("")

        report.append("WEAPON SYSTEMS")
        report.append("-" * 80)
        report.append(f"VLS Cells: {self.specs.weapons.vls_cells} (Mk 41)")
        report.append("")
        report.append("Surface-to-Air Missiles:")
        report.append(f"  SM-2: {self.specs.weapons.sm2_range_km} km range")
        if self.specs.weapons.sm3_range_km > 0:
            report.append(f"  SM-3: {self.specs.weapons.sm3_range_km} km (BMD)")
        if self.specs.weapons.sm6_range_km > 0:
            report.append(f"  SM-6: {self.specs.weapons.sm6_range_km} km range")
            report.append(f"        Pk vs Fighter: {self.specs.weapons.sm6_pk_vs_fighter:.0%}")
            report.append(f"        Pk vs Cruise Missile: {self.specs.weapons.sm6_pk_vs_cruise_missile:.0%}")
        report.append("")
        report.append("Anti-Ship Missiles:")
        if self.specs.weapons.harpoon_range_km > 0:
            report.append(f"  Harpoon: {self.specs.weapons.harpoon_range_km} km range")
        if self.specs.weapons.nsm_range_km > 0:
            report.append(f"  NSM: {self.specs.weapons.nsm_range_km} km range")
            report.append(f"       Pk vs Ship: {self.specs.weapons.nsm_pk_vs_ship:.0%}")
        report.append("")
        report.append("Phalanx CIWS:")
        report.append(f"  Range: {self.specs.weapons.ciws_range_km} km")
        report.append(f"  Fire Rate: {self.specs.weapons.ciws_fire_rate_rpm:,} rpm")
        report.append(f"  Pk vs Missile: {self.specs.weapons.ciws_pk_vs_missile:.0%}")
        report.append("")

        # Flight III specific enhancements
        if self.specs.variant == DDG51Variant.FLIGHT_III:
            report.append("FLIGHT III ENHANCEMENTS")
            report.append("-" * 80)
            report.append("✓ AN/SPY-6(V)1 AMDR (30x sensitivity vs SPY-1D)")
            report.append("✓ Increased power generation (integrated power system)")
            report.append("✓ SM-3 Block IIA BMD capability")
            report.append("✓ Naval Strike Missile integration")
            report.append("✓ Enhanced distributed maritime operations")
            report.append("")

        report.append("=" * 80)
        report.append("Classification: UNCLASSIFIED // PUBLIC RELEASE")
        report.append("Source: US Navy public affairs, open-source reporting")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Demonstration of DDG-51 model"""

    # Flight III variant (latest)
    destroyer_flight_iii = DDG51Model(variant=DDG51Variant.FLIGHT_III)
    print(destroyer_flight_iii.generate_specification_report())

    print("\n\n" + "=" * 80)
    print("DETECTION RANGE EXAMPLES")
    print("=" * 80)

    test_targets = [
        ("J-20 Mighty Dragon", 0.0014),  # Stealth fighter
        ("Su-57 Felon", 0.1),            # 5th-gen (less stealthy)
        ("Su-35 Flanker-E", 3.0),        # 4th-gen fighter
        ("H-6 Badger", 50),              # Large bomber
    ]

    for target_name, rcs in test_targets:
        detection_range = destroyer_flight_iii.calculate_radar_detection_range(
            target_rcs_m2=rcs
        )
        print(f"{target_name:25s} (RCS {rcs:6.4f} m²): {detection_range:6.1f} km")

    print("\n\n" + "=" * 80)
    print("SM-6 ENGAGEMENT ENVELOPE EXAMPLES")
    print("=" * 80)

    test_engagements = [
        ("J-20 (stealth, subsonic)", 12, 0.9, 0.0014),
        ("Su-35 (conventional)", 10, 1.8, 3.0),
        ("YJ-18 cruise missile", 0.05, 2.8, 0.1),
        ("DF-21D ASBM (terminal)", 30, 4.0, 0.5),
    ]

    for target_name, alt_km, speed_mach, rcs in test_engagements:
        envelope = destroyer_flight_iii.calculate_sm6_engagement_envelope(
            target_altitude_km=alt_km,
            target_speed_mach=speed_mach,
            target_rcs_m2=rcs
        )
        print(f"\n{target_name}:")
        print(f"  Max Range: {envelope['max_range_km']:.1f} km")
        print(f"  Min Range: {envelope['min_range_km']:.1f} km")
        print(f"  Pk: {envelope['pk']:.0%}")

    print("\n\n" + "=" * 80)
    print("CARRIER STRIKE GROUP AIR DEFENSE")
    print("=" * 80)

    csg_defense = destroyer_flight_iii.calculate_carrier_strike_group_defense(
        num_ddg51=2,
        formation_radius_km=50
    )

    print(f"CSG Configuration: 2x DDG-51 Flight III")
    print(f"Formation Radius: 50 km")
    print("")
    print(f"Total Coverage Area: {csg_defense['coverage_area_km2']:,.0f} km²")
    print(f"Max Engagement Range: {csg_defense['max_engagement_range_km']:.0f} km")
    print(f"Defense Layers: {csg_defense['defense_layers']}")
    print(f"Simultaneous Engagements: {csg_defense['simultaneous_engagements']}")
    print(f"Total VLS Cells: {csg_defense['total_vls_cells']}")
    print(f"CEC Factor: {csg_defense['cec_factor']:.2f}x")

    # Compare Flight IIA
    print("\n\n" + "=" * 80)
    print("FLIGHT IIA vs FLIGHT III COMPARISON")
    print("=" * 80)

    destroyer_iia = DDG51Model(variant=DDG51Variant.FLIGHT_IIA)

    print(f"{'Metric':<30s} {'Flight IIA':<15s} {'Flight III':<15s}")
    print("-" * 60)
    print(f"{'Radar':<30s} {'AN/SPY-1D(V)':<15s} {'AN/SPY-6(V)1':<15s}")
    print(f"{'Detection Range (1m² RCS)':<30s} {destroyer_iia.specs.radar.detection_range_km:<15.0f} {destroyer_flight_iii.specs.radar.detection_range_km:<15.0f}")
    print(f"{'Track Capacity':<30s} {destroyer_iia.specs.radar.track_capacity:<15d} {destroyer_flight_iii.specs.radar.track_capacity:<15d}")
    print(f"{'Simultaneous Engagements':<30s} {destroyer_iia.specs.radar.simultaneous_engagement:<15d} {destroyer_flight_iii.specs.radar.simultaneous_engagement:<15d}")
    print(f"{'SM-6 Range (km)':<30s} {destroyer_iia.specs.weapons.sm6_range_km:<15.0f} {destroyer_flight_iii.specs.weapons.sm6_range_km:<15.0f}")


if __name__ == "__main__":
    main()
