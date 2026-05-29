#!/usr/bin/env python3
"""
Electronic Order of Battle (EOB) Database

Comprehensive database of known emitter signatures, platforms,
and tactics for automated threat identification and classification.

Includes:
- Platform types (aircraft, ships, ground units)
- Emitter signatures (radar, datalink, communication)
- Threat assessment
- Tactical patterns
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
import json

# Import RCS models - ONLY operationally verified models
# EXCLUDED (not operationally verified):
#   - MQ28RCSModel (development, not deployed)
#   - SixthGenRCSModel (concept-level, not fielded)
from osint_cad.physics.rcs_models import (F35ARCSModel, RCSEstimate, calculate_detection_range)


class PlatformType(Enum):
    """Platform categories"""
    FIGHTER_4TH_GEN = "Fighter (4th Gen)"
    FIGHTER_5TH_GEN = "Fighter (5th Gen)"
    AWACS = "AWACS"
    EW_AIRCRAFT = "EW Aircraft"
    TRANSPORT = "Transport"
    UAV_TACTICAL = "UAV (Tactical)"
    UAV_HALE = "UAV (HALE)"
    UNKNOWN = "Unknown"


class ThreatLevel(Enum):
    """Threat assessment levels"""
    CRITICAL = 5  # Immediate lethal threat
    HIGH = 4  # Significant threat capability
    MEDIUM = 3  # Moderate threat
    LOW = 2  # Limited threat
    NEGLIGIBLE = 1  # Minimal threat
    UNKNOWN = 0


@dataclass
class EmitterSignature:
    """RF emitter signature"""
    emitter_id: str
    emitter_type: str  # "Radar", "Datalink", "Communication", "Jammer"
    frequency_min_ghz: float
    frequency_max_ghz: float
    bandwidth_mhz: float
    modulation: str
    prf_hz: Optional[float] = None  # Pulse repetition frequency (for radars)
    power_dbm: float = 0.0
    antenna_pattern: str = "Directional"
    polarization: str = "Vertical"


@dataclass
class PlatformEntry:
    """Platform EOB entry"""
    platform_id: str
    platform_name: str
    platform_type: PlatformType
    country: str
    threat_level: ThreatLevel

    # Physical characteristics
    max_speed_mps: float = 0.0  # meters per second
    max_altitude_m: float = 0.0
    rcs_dbsm: float = 0.0  # Legacy: Fixed RCS (dBsm) - deprecated

    # NEW: Aspect-dependent RCS model
    rcs_model: Optional[Callable] = None  # Function to calculate RCS from geometry

    # Emitter suite
    emitters: List[EmitterSignature] = field(default_factory=list)

    # Weapons
    weapons: List[str] = field(default_factory=list)

    # Tactical patterns
    typical_formations: List[str] = field(default_factory=list)
    typical_altitudes_m: List[float] = field(default_factory=list)

    # Additional info
    notes: str = ""

    def calculate_rcs(self,
                     radar_position: np.ndarray,
                     target_position: np.ndarray,
                     target_velocity: np.ndarray,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """
        Calculate aspect-dependent RCS

        Args:
            radar_position: Radar position [x, y, z] (meters)
            target_position: Target position [x, y, z] (meters)
            target_velocity: Target velocity [vx, vy, vz] (m/s)
            frequency_ghz: Radar frequency (GHz)

        Returns:
            RCSEstimate with aspect-dependent RCS value
        """
        if self.rcs_model is not None:
            # Use aspect-dependent model
            return self.rcs_model.calculate_rcs_from_vectors(
                radar_position, target_position, target_velocity, frequency_ghz)
        else:
            # Fallback to legacy fixed RCS
            from osint_cad.physics.rcs_models import RCSEstimate, rcs_dbsm_to_linear
            rcs_m2 = rcs_dbsm_to_linear(self.rcs_dbsm)
            return RCSEstimate(
                rcs_m2=rcs_m2,
                rcs_dbsm=self.rcs_dbsm,
                azimuth_deg=0.0,
                elevation_deg=0.0,
                confidence=0.3  # Low confidence for fixed RCS
            )


class EOBDatabase:
    """
    Electronic Order of Battle Database

    Stores and queries known emitter signatures and platform data.
    """

    def __init__(self):
        self.platforms: Dict[str, PlatformEntry] = {}
        self.emitters: Dict[str, EmitterSignature] = {}

        # Initialize with known platforms
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database with known platforms"""

        # F-35A Lightning II
        f35_madl = EmitterSignature(
            emitter_id="MADL-F35",
            emitter_type="Datalink",
            frequency_min_ghz=14.5,
            frequency_max_ghz=15.5,
            bandwidth_mhz=1000,
            modulation="DSSS/FHSS",
            power_dbm=30,
            antenna_pattern="Directional (±60°)",
            polarization="Circular"
        )

        f35_apg81 = EmitterSignature(
            emitter_id="APG-81-AESA",
            emitter_type="Radar",
            frequency_min_ghz=8.0,
            frequency_max_ghz=12.0,
            bandwidth_mhz=2000,
            modulation="LPI Waveform",
            prf_hz=100000,
            power_dbm=60,
            antenna_pattern="AESA (±60°)"
        )

        f35 = PlatformEntry(
            platform_id="F35A",
            platform_name="F-35A Lightning II",
            platform_type=PlatformType.FIGHTER_5TH_GEN,
            country="USA",
            threat_level=ThreatLevel.CRITICAL,
            max_speed_mps=590,  # Mach 1.6
            max_altitude_m=15000,
            rcs_dbsm=-37,  # Legacy fixed value (frontal aspect)
            rcs_model=F35ARCSModel,  # NEW: Aspect-dependent RCS model
            emitters=[f35_madl, f35_apg81],
            weapons=["AIM-120D", "AIM-9X", "JDAM", "SDB"],
            typical_formations=["4-ship finger-four", "2-ship element"],
            typical_altitudes_m=[9000, 12000, 15000],
            notes="Highly capable 5th gen multirole fighter. LPI/LPD characteristics. MADL datalink. RCS varies 10-100× with aspect angle."
        )

        # J-20 Mighty Dragon
        j20_acdl = EmitterSignature(
            emitter_id="ACDL-J20",
            emitter_type="Datalink",
            frequency_min_ghz=14.0,
            frequency_max_ghz=15.0,
            bandwidth_mhz=500,
            modulation="DSSS",
            power_dbm=28,
            antenna_pattern="Directional"
        )

        j20_aesa = EmitterSignature(
            emitter_id="Type-1475-AESA",
            emitter_type="Radar",
            frequency_min_ghz=8.5,
            frequency_max_ghz=11.5,
            bandwidth_mhz=1500,
            modulation="LPI Waveform",
            prf_hz=95000,
            power_dbm=58
        )

        j20 = PlatformEntry(
            platform_id="J20",
            platform_name="J-20 Mighty Dragon",
            platform_type=PlatformType.FIGHTER_5TH_GEN,
            country="China",
            threat_level=ThreatLevel.HIGH,
            max_speed_mps=610,  # Mach 1.8
            max_altitude_m=20000,
            rcs_dbsm=-30,
            emitters=[j20_acdl, j20_aesa],
            weapons=["PL-15", "PL-10", "PL-21"],
            typical_formations=["4-ship", "2-ship"],
            typical_altitudes_m=[10000, 13000, 16000]
        )

        # E-3 Sentry AWACS
        e3_radar = EmitterSignature(
            emitter_id="APY-2-RADAR",
            emitter_type="Radar",
            frequency_min_ghz=2.7,
            frequency_max_ghz=2.9,
            bandwidth_mhz=200,
            modulation="Pulse Doppler",
            prf_hz=2000,
            power_dbm=80,  # Very high power
            antenna_pattern="Rotating (360°)"
        )

        e3 = PlatformEntry(
            platform_id="E3",
            platform_name="E-3 Sentry",
            platform_type=PlatformType.AWACS,
            country="USA",
            threat_level=ThreatLevel.HIGH,
            max_speed_mps=200,
            max_altitude_m=12000,
            rcs_dbsm=40,  # Large RCS
            emitters=[e3_radar],
            typical_altitudes_m=[9000, 10000]
        )

        # EXCLUDED (not operationally verified):
        # - MQ-28 Ghost Bat: Still in development, NOT deployed operationally
        # - NGAD 6th-gen: Concept-level, NOT fielded (post-2030, 20% confidence)

        # Add ONLY operationally verified platforms to database
        self.add_platform(f35)   # Fielded since 2015
        self.add_platform(j20)   # Fielded since 2017
        self.add_platform(e3)    # Fielded, operational AWACS

    def add_platform(self, platform: PlatformEntry):
        """Add platform to database"""
        self.platforms[platform.platform_id] = platform

        # Index emitters
        for emitter in platform.emitters:
            self.emitters[emitter.emitter_id] = emitter

    def identify_emitter(self,
                        frequency_ghz: float,
                        bandwidth_mhz: float,
                        modulation: Optional[str] = None) -> List[PlatformEntry]:
        """
        Identify potential platforms from emitter characteristics

        Args:
            frequency_ghz: Observed frequency (GHz)
            bandwidth_mhz: Observed bandwidth (MHz)
            modulation: Optional modulation type

        Returns:
            List of matching platform entries (sorted by threat level)
        """
        matches = []

        for platform in self.platforms.values():
            for emitter in platform.emitters:
                # Check frequency match
                if (emitter.frequency_min_ghz <= frequency_ghz <= emitter.frequency_max_ghz):
                    # Check bandwidth (within 50% tolerance)
                    bw_ratio = bandwidth_mhz / emitter.bandwidth_mhz
                    if 0.5 <= bw_ratio <= 2.0:
                        # Check modulation if provided
                        if modulation is None or modulation in emitter.modulation:
                            matches.append(platform)
                            break  # Don't add same platform multiple times

        # Sort by threat level (descending)
        matches.sort(key=lambda p: p.threat_level.value, reverse=True)

        return matches

    def assess_threat(self,
                     platform_id: str,
                     range_km: float,
                     aspect_angle_deg: float) -> Dict[str, any]:
        """
        Assess threat level from identified platform

        Args:
            platform_id: Platform identifier
            range_km: Range to platform (km)
            aspect_angle_deg: Aspect angle (degrees, 0=nose-on)

        Returns:
            Threat assessment dictionary
        """
        if platform_id not in self.platforms:
            return {
                'threat_level': ThreatLevel.UNKNOWN,
                'engagement_range_km': 0,
                'time_to_weapons_range_s': float('inf'),
                'recommendations': ["Unknown platform - maintain surveillance"]
            }

        platform = self.platforms[platform_id]

        # Estimate engagement range based on weapons
        # Map each missile type to its maximum range (air-to-air only)
        missile_ranges = {
            # US missiles
            "AIM-260 JATM": 200,      # Next-gen long-range AAM
            "AIM-260": 200,            # Alternate designation
            "AIM-120D": 180,           # AMRAAM latest variant
            "AIM-120C": 120,           # AMRAAM earlier variant
            "AIM-120C/D": 180,         # Combined designation (use max)
            "AIM-9X": 35,              # Short-range IR missile
            "AIM-9X Block III": 35,    # Short-range IR missile (improved)
            # European missiles
            "Meteor": 200,             # Ramjet BVR missile
            # Chinese missiles
            "PL-15": 200,              # Long-range BVR missile
            "PL-21": 400,              # Very long-range missile
            "PL-10": 35,               # Short-range IR missile
            # Russian missiles
            "R-77M": 110,              # AA-12B long-range
            "R-77-1": 110,             # Alternate designation
            "R-77": 80,                # AA-12 baseline
            "R-73": 30,                # Short-range IR
        }

        # Find maximum air-to-air weapon range for this platform
        max_weapon_range_km = 0
        for weapon in platform.weapons:
            if weapon in missile_ranges:
                max_weapon_range_km = max(max_weapon_range_km, missile_ranges[weapon])

        # Adjust for aspect (rear aspect reduces range)
        aspect_factor = 1.0 - 0.3 * (abs(aspect_angle_deg) / 180.0)
        effective_range_km = max_weapon_range_km * aspect_factor

        # Time to weapons range
        closing_speed_mps = platform.max_speed_mps * np.cos(np.radians(aspect_angle_deg))
        range_margin_m = (range_km - effective_range_km) * 1000
        time_to_range_s = range_margin_m / closing_speed_mps if closing_speed_mps > 0 else float('inf')

        # Generate recommendations
        recommendations = []
        if range_km < effective_range_km:
            recommendations.append("IMMEDIATE: Within weapons range - execute defensive maneuvers")
            threat = ThreatLevel.CRITICAL
        elif time_to_range_s < 60:
            recommendations.append("WARNING: Approaching weapons range - prepare countermeasures")
            threat = ThreatLevel.HIGH
        elif range_km < max_weapon_range_km * 1.5:
            recommendations.append("CAUTION: Near weapons envelope - maintain awareness")
            threat = ThreatLevel.MEDIUM
        else:
            recommendations.append("MONITOR: Outside immediate threat range")
            threat = ThreatLevel.LOW

        return {
            'threat_level': threat,
            'base_threat': platform.threat_level,
            'engagement_range_km': effective_range_km,
            'time_to_weapons_range_s': time_to_range_s,
            'max_weapon_range_km': max_weapon_range_km,
            'recommendations': recommendations
        }

    def export_to_json(self, filename: str):
        """Export database to JSON file"""
        data = {
            'platforms': {
                pid: {
                    'name': p.platform_name,
                    'type': p.platform_type.value,
                    'country': p.country,
                    'threat': p.threat_level.value,
                    'emitters': [
                        {
                            'id': e.emitter_id,
                            'type': e.emitter_type,
                            'freq_min': e.frequency_min_ghz,
                            'freq_max': e.frequency_max_ghz
                        }
                        for e in p.emitters
                    ]
                }
                for pid, p in self.platforms.items()
            }
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


# Example usage
if __name__ == "__main__":
    print("Electronic Order of Battle Database")
    print("=" * 60)

    # Create EOB database
    eob = EOBDatabase()

    print(f"\nLoaded platforms: {len(eob.platforms)}")
    for platform_id, platform in eob.platforms.items():
        print(f"  [{platform_id}] {platform.platform_name}")
        print(f"    Type: {platform.platform_type.value}")
        print(f"    Threat: {platform.threat_level.name}")
        print(f"    Emitters: {len(platform.emitters)}")

    # Test emitter identification
    print(f"\n{'=' * 60}")
    print("Test: Identify emitter at 15.0 GHz, 1000 MHz bandwidth")

    matches = eob.identify_emitter(
        frequency_ghz=15.0,
        bandwidth_mhz=1000,
        modulation="DSSS"
    )

    print(f"  Matches: {len(matches)}")
    for match in matches:
        print(f"    - {match.platform_name} ({match.country})")
        print(f"      Threat: {match.threat_level.name}")

    # Test threat assessment
    print(f"\n{'=' * 60}")
    print("Test: Threat assessment for F-35A at 100 km, nose aspect")

    assessment = eob.assess_threat(
        platform_id="F35A",
        range_km=100,
        aspect_angle_deg=0
    )

    print(f"  Threat Level: {assessment['threat_level'].name}")
    print(f"  Engagement Range: {assessment['engagement_range_km']:.0f} km")
    print(f"  Time to Range: {assessment['time_to_weapons_range_s']:.0f} s")
    print(f"  Recommendations:")
    for rec in assessment['recommendations']:
        print(f"    - {rec}")

    # Export database
    print(f"\n{'=' * 60}")
    eob.export_to_json("eob_database.json")
    print("Database exported to eob_database.json")

    print("\n" + "=" * 60)
    print("EOB database demonstration complete.")
