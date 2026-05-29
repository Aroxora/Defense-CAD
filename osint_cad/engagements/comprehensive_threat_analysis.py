#!/usr/bin/env python3
"""
Comprehensive Threat Analysis for Chinese National Security

Analyzes all major threat platforms and their kill chain vulnerabilities:
- 5th Generation Fighters (F-35A/B/C, F-22)
- Strategic Bombers (B-2, B-21, B-1B)
- Attack Submarines (Virginia, Seawolf, Los Angeles)
- Ballistic Missile Submarines (Columbia, Ohio)
- Surface Combatants (DDG-51, CG-47, LCS)
- Cruise Missiles (Tomahawk, JASSM-ER, LRASM)
- Carrier Strike Groups
- Theater Ballistic Missiles (multiple)

For each threat:
- Physical/signature characteristics
- Detection methods and vulnerabilities
- Engagement options with PLA systems
- Kill probability analysis with uncertainty
- Defensive recommendations

Classification: UNCLASSIFIED // FOR ACADEMIC/RESEARCH USE
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import json
from datetime import datetime, timezone

from osint_cad.util.calculation_logger import CalculationLogger, OutputFormat, init_logger


# =============================================================================
# THREAT CATEGORIES
# =============================================================================

class ThreatCategory(Enum):
    """Major threat categories"""
    FIGHTER_5GEN = "5th Generation Fighter"
    FIGHTER_4GEN = "4th Generation Fighter"
    BOMBER_STRATEGIC = "Strategic Bomber"
    SUBMARINE_ATTACK = "Attack Submarine"
    SUBMARINE_BALLISTIC = "Ballistic Missile Submarine"
    SURFACE_COMBATANT = "Surface Combatant"
    CRUISE_MISSILE = "Cruise Missile"
    BALLISTIC_MISSILE = "Ballistic Missile"
    CARRIER_GROUP = "Carrier Strike Group"
    ISR_PLATFORM = "ISR Platform"


class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


# =============================================================================
# THREAT PLATFORM DEFINITIONS
# =============================================================================

@dataclass
class ThreatPlatform:
    """Base class for threat platforms"""
    name: str
    designation: str
    category: ThreatCategory
    threat_level: ThreatLevel
    country: str

    # Physical characteristics
    length_m: float
    displacement_tons: float = 0  # For ships/subs

    # Signatures
    rcs_frontal_dbsm: float = 0
    rcs_broadside_dbsm: float = 0
    acoustic_signature_db: float = 0  # For submarines
    ir_signature_w: float = 0

    # Performance
    max_speed: float = 0
    range_km: float = 0
    endurance_days: float = 0

    # Weapons
    primary_weapons: List[str] = field(default_factory=list)
    weapon_capacity: int = 0

    # Defensive systems
    defensive_systems: List[str] = field(default_factory=list)

    # Detection vulnerabilities
    detection_vulnerabilities: List[str] = field(default_factory=list)

    # Engagement recommendations
    engagement_systems: List[str] = field(default_factory=list)

    # Kill probability estimates
    pk_air_defense: float = 0  # Pk using air defense
    pk_submarine: float = 0     # Pk using submarines
    pk_surface: float = 0       # Pk using surface ships
    pk_integrated: float = 0    # Pk using integrated defense

    confidence: float = 0.5


# =============================================================================
# SUBMARINE THREATS
# =============================================================================

def create_virginia_class() -> ThreatPlatform:
    """Virginia Class SSN - Primary US attack submarine"""
    return ThreatPlatform(
        name="Virginia Class SSN",
        designation="SSN-774",
        category=ThreatCategory.SUBMARINE_ATTACK,
        threat_level=ThreatLevel.CRITICAL,
        country="USA",
        length_m=115,
        displacement_tons=7900,
        rcs_frontal_dbsm=0,  # Submerged
        acoustic_signature_db=95,  # Very quiet
        max_speed=25,  # knots submerged
        range_km=0,  # Nuclear unlimited
        endurance_days=90,
        primary_weapons=[
            "Mk 48 ADCAP torpedo",
            "Tomahawk TLAM",
            "Harpoon (legacy boats)",
            "UUV deployment"
        ],
        weapon_capacity=37,  # Torpedo tubes + VLS
        defensive_systems=[
            "AN/BQQ-10 sonar suite",
            "Acoustic countermeasures",
            "AN/WLY-1 acoustic intercept"
        ],
        detection_vulnerabilities=[
            "Periscope depth operations",
            "Communication mast exposure",
            "Thermal layer crossing",
            "Approaching shallow water",
            "High-speed transit noise",
            "VLF/ELF communication windows"
        ],
        engagement_systems=[
            "Type 093B SSN hunter-killer",
            "Y-8Q maritime patrol aircraft",
            "Type 056A corvette with towed array",
            "Shore-based SOSUS-type arrays",
            "Helicopter dipping sonar"
        ],
        pk_air_defense=0.0,
        pk_submarine=0.35,
        pk_surface=0.20,
        pk_integrated=0.45,
        confidence=0.35
    )


def create_seawolf_class() -> ThreatPlatform:
    """Seawolf Class SSN - Most capable US attack submarine"""
    return ThreatPlatform(
        name="Seawolf Class SSN",
        designation="SSN-21",
        category=ThreatCategory.SUBMARINE_ATTACK,
        threat_level=ThreatLevel.CRITICAL,
        country="USA",
        length_m=107,
        displacement_tons=9138,
        acoustic_signature_db=90,  # Quietest US sub
        max_speed=35,  # knots
        range_km=0,
        endurance_days=90,
        primary_weapons=[
            "Mk 48 ADCAP torpedo",
            "Tomahawk TLAM",
            "Harpoon",
            "Mines"
        ],
        weapon_capacity=50,
        defensive_systems=[
            "AN/BQQ-5D sonar",
            "TB-29A towed array",
            "Advanced acoustic countermeasures"
        ],
        detection_vulnerabilities=[
            "Limited numbers (only 3 built)",
            "Periscope operations",
            "Shallow water limitations",
            "Arctic operations noise"
        ],
        engagement_systems=[
            "Type 095 SSN",
            "Deep-water SOSUS arrays",
            "Maritime patrol coordination"
        ],
        pk_air_defense=0.0,
        pk_submarine=0.30,
        pk_surface=0.15,
        pk_integrated=0.40,
        confidence=0.30
    )


def create_columbia_class() -> ThreatPlatform:
    """Columbia Class SSBN - Next-gen US ballistic missile submarine"""
    return ThreatPlatform(
        name="Columbia Class SSBN",
        designation="SSBN-826",
        category=ThreatCategory.SUBMARINE_BALLISTIC,
        threat_level=ThreatLevel.CRITICAL,
        country="USA",
        length_m=171,
        displacement_tons=20810,
        acoustic_signature_db=88,  # Extremely quiet
        max_speed=20,
        range_km=0,
        endurance_days=77,  # Patrol duration
        primary_weapons=[
            "Trident II D5LE SLBM (16 tubes)",
            "W76-1/W88 warheads"
        ],
        weapon_capacity=16,  # Missile tubes
        defensive_systems=[
            "Next-gen sonar suite",
            "Advanced quieting",
            "Integrated countermeasures"
        ],
        detection_vulnerabilities=[
            "Departure/return from port",
            "Transit choke points",
            "Patrol area prediction",
            "Very deep operations limited"
        ],
        engagement_systems=[
            "Type 095/096 SSN patrol",
            "Deep-ocean surveillance network",
            "Attack during transit"
        ],
        pk_air_defense=0.0,
        pk_submarine=0.15,  # Very difficult
        pk_surface=0.05,
        pk_integrated=0.20,
        confidence=0.25
    )


def create_ohio_class() -> ThreatPlatform:
    """Ohio Class SSGN/SSBN"""
    return ThreatPlatform(
        name="Ohio Class SSGN",
        designation="SSGN-726",
        category=ThreatCategory.SUBMARINE_ATTACK,
        threat_level=ThreatLevel.HIGH,
        country="USA",
        length_m=170,
        displacement_tons=18750,
        acoustic_signature_db=100,  # Older design
        max_speed=20,
        range_km=0,
        endurance_days=70,
        primary_weapons=[
            "Tomahawk TLAM (154 missiles)",
            "Special operations capability",
            "Mk 48 torpedo"
        ],
        weapon_capacity=154,  # Massive TLAM capacity
        defensive_systems=[
            "AN/BQQ-6 sonar",
            "Countermeasures"
        ],
        detection_vulnerabilities=[
            "Larger acoustic signature",
            "Predictable patrol patterns",
            "SOF insertion operations"
        ],
        engagement_systems=[
            "Type 093 SSN",
            "Maritime patrol aircraft",
            "Coastal ASW network"
        ],
        pk_air_defense=0.0,
        pk_submarine=0.40,
        pk_surface=0.25,
        pk_integrated=0.50,
        confidence=0.40
    )


def create_los_angeles_class() -> ThreatPlatform:
    """Los Angeles Class SSN"""
    return ThreatPlatform(
        name="Los Angeles Class SSN",
        designation="SSN-688",
        category=ThreatCategory.SUBMARINE_ATTACK,
        threat_level=ThreatLevel.HIGH,
        country="USA",
        length_m=110,
        displacement_tons=6900,
        acoustic_signature_db=105,  # Older boats noisier
        max_speed=32,
        range_km=0,
        endurance_days=90,
        primary_weapons=[
            "Mk 48 ADCAP",
            "Tomahawk",
            "Harpoon"
        ],
        weapon_capacity=37,
        defensive_systems=[
            "AN/BQQ-5 sonar",
            "TB-16/TB-29 towed array"
        ],
        detection_vulnerabilities=[
            "Higher acoustic signature",
            "Aging platform",
            "Reactor noise"
        ],
        engagement_systems=[
            "Type 039B AIP submarine",
            "Y-8Q/Y-9 MPA",
            "Surface ASW groups"
        ],
        pk_air_defense=0.0,
        pk_submarine=0.45,
        pk_surface=0.30,
        pk_integrated=0.55,
        confidence=0.45
    )


# =============================================================================
# STRATEGIC BOMBER THREATS
# =============================================================================

def create_b2_spirit() -> ThreatPlatform:
    """B-2 Spirit stealth bomber"""
    return ThreatPlatform(
        name="B-2 Spirit",
        designation="B-2A",
        category=ThreatCategory.BOMBER_STRATEGIC,
        threat_level=ThreatLevel.CRITICAL,
        country="USA",
        length_m=21,
        rcs_frontal_dbsm=-40,
        rcs_broadside_dbsm=-30,
        ir_signature_w=50000,
        max_speed=630,  # knots
        range_km=11000,
        primary_weapons=[
            "B61 nuclear bomb",
            "B83 nuclear bomb",
            "GBU-57 MOP",
            "JASSM-ER",
            "GBU-31 JDAM"
        ],
        weapon_capacity=40000,  # lbs payload
        defensive_systems=[
            "AN/APQ-181 radar",
            "Defensive management system",
            "Signature reduction"
        ],
        detection_vulnerabilities=[
            "VHF/UHF radar detection",
            "Infrared exhaust signature",
            "Predictable flight corridors",
            "Tanker support requirements",
            "Limited numbers (20 aircraft)"
        ],
        engagement_systems=[
            "JY-27A VHF radar",
            "HQ-9B long-range SAM",
            "J-20 with PL-15",
            "Passive detection networks"
        ],
        pk_air_defense=0.70,
        pk_submarine=0.0,
        pk_surface=0.0,
        pk_integrated=0.70,
        confidence=0.40
    )


def create_b21_raider() -> ThreatPlatform:
    """B-21 Raider next-generation bomber"""
    return ThreatPlatform(
        name="B-21 Raider",
        designation="B-21A",
        category=ThreatCategory.BOMBER_STRATEGIC,
        threat_level=ThreatLevel.CRITICAL,
        country="USA",
        length_m=16,  # Estimated
        rcs_frontal_dbsm=-50,  # Estimated, more advanced than B-2
        rcs_broadside_dbsm=-40,
        ir_signature_w=30000,  # Improved exhaust shielding
        max_speed=600,
        range_km=9000,
        primary_weapons=[
            "B61-12 nuclear bomb",
            "JASSM-ER",
            "LRSO cruise missile",
            "Hypersonic weapons (future)"
        ],
        weapon_capacity=30000,
        defensive_systems=[
            "Next-gen defensive suite",
            "Advanced EW",
            "AI-assisted threat avoidance"
        ],
        detection_vulnerabilities=[
            "VHF/UHF resonance detection",
            "Space-based IR detection",
            "Network analysis",
            "Tanker tracking",
            "Development timeline uncertainty"
        ],
        engagement_systems=[
            "Next-gen VHF radar arrays",
            "Space-based sensor cueing",
            "J-20/J-35 intercept",
            "HQ-19 high-altitude SAM"
        ],
        pk_air_defense=0.55,
        pk_submarine=0.0,
        pk_surface=0.0,
        pk_integrated=0.55,
        confidence=0.30
    )


def create_b1b_lancer() -> ThreatPlatform:
    """B-1B Lancer supersonic bomber"""
    return ThreatPlatform(
        name="B-1B Lancer",
        designation="B-1B",
        category=ThreatCategory.BOMBER_STRATEGIC,
        threat_level=ThreatLevel.HIGH,
        country="USA",
        length_m=44.5,
        rcs_frontal_dbsm=10,  # Reduced but not stealth
        rcs_broadside_dbsm=25,
        ir_signature_w=500000,
        max_speed=900,  # Mach 1.25
        range_km=9400,
        primary_weapons=[
            "JASSM-ER (24)",
            "LRASM (24)",
            "GBU-31 JDAM",
            "Mines"
        ],
        weapon_capacity=75000,  # lbs
        defensive_systems=[
            "AN/ALQ-161 EW suite",
            "Terrain following radar"
        ],
        detection_vulnerabilities=[
            "Higher radar signature",
            "Large IR signature",
            "Afterburner use detectable",
            "Aging airframe"
        ],
        engagement_systems=[
            "HQ-9B/HQ-22 SAM",
            "J-11B/J-16 intercept",
            "Fighter CAP"
        ],
        pk_air_defense=0.80,
        pk_submarine=0.0,
        pk_surface=0.0,
        pk_integrated=0.80,
        confidence=0.55
    )


# =============================================================================
# CRUISE MISSILE THREATS
# =============================================================================

def create_tomahawk() -> ThreatPlatform:
    """Tomahawk cruise missile family"""
    return ThreatPlatform(
        name="Tomahawk TLAM",
        designation="BGM-109",
        category=ThreatCategory.CRUISE_MISSILE,
        threat_level=ThreatLevel.HIGH,
        country="USA",
        length_m=6.25,
        rcs_frontal_dbsm=-20,
        ir_signature_w=5000,
        max_speed=470,  # knots
        range_km=2500,
        primary_weapons=["1000 lb warhead or W80 nuclear"],
        weapon_capacity=1,
        defensive_systems=["Terrain following", "GPS/INS", "DSMAC"],
        detection_vulnerabilities=[
            "Low-altitude flight detectable by OTH",
            "Predictable terrain corridors",
            "Launch platform vulnerability",
            "Terminal pop-up detectable"
        ],
        engagement_systems=[
            "HQ-7B point defense",
            "Type 1130 CIWS",
            "J-10C intercept",
            "YLC-8E radar detection"
        ],
        pk_air_defense=0.75,
        pk_submarine=0.0,
        pk_surface=0.60,
        pk_integrated=0.80,
        confidence=0.55
    )


def create_jassm_er() -> ThreatPlatform:
    """JASSM-ER stealthy cruise missile"""
    return ThreatPlatform(
        name="JASSM-ER",
        designation="AGM-158B",
        category=ThreatCategory.CRUISE_MISSILE,
        threat_level=ThreatLevel.CRITICAL,
        country="USA",
        length_m=4.27,
        rcs_frontal_dbsm=-30,  # Very stealthy
        ir_signature_w=3000,
        max_speed=500,
        range_km=925,
        primary_weapons=["1000 lb penetrator warhead"],
        weapon_capacity=1,
        defensive_systems=["INS/GPS", "IR terminal seeker", "Autonomous target recognition"],
        detection_vulnerabilities=[
            "Aircraft launch platform",
            "IR signature in terminal",
            "Predictable approach corridors"
        ],
        engagement_systems=[
            "HQ-17A short-range",
            "PHL-03 gun system",
            "Radar-guided AAA"
        ],
        pk_air_defense=0.55,
        pk_submarine=0.0,
        pk_surface=0.45,
        pk_integrated=0.60,
        confidence=0.45
    )


def create_lrasm() -> ThreatPlatform:
    """LRASM anti-ship missile"""
    return ThreatPlatform(
        name="LRASM",
        designation="AGM-158C",
        category=ThreatCategory.CRUISE_MISSILE,
        threat_level=ThreatLevel.CRITICAL,
        country="USA",
        length_m=4.27,
        rcs_frontal_dbsm=-30,
        ir_signature_w=3500,
        max_speed=500,
        range_km=930,
        primary_weapons=["1000 lb penetrator - anti-ship"],
        weapon_capacity=1,
        defensive_systems=[
            "Autonomous targeting",
            "AI route planning",
            "Multi-ship discrimination",
            "Passive RF homing"
        ],
        detection_vulnerabilities=[
            "Launch platform (B-1B, F-18, P-8)",
            "Sea-skimming trajectory",
            "Final pop-up maneuver"
        ],
        engagement_systems=[
            "HQ-10 shipborne SAM",
            "Type 1130 CIWS",
            "FL-3000N",
            "Shipborne EW"
        ],
        pk_air_defense=0.0,
        pk_submarine=0.0,
        pk_surface=0.50,
        pk_integrated=0.55,
        confidence=0.40
    )


# =============================================================================
# FIGHTER THREATS
# =============================================================================

def create_f22_raptor() -> ThreatPlatform:
    """F-22 Raptor air superiority fighter"""
    return ThreatPlatform(
        name="F-22 Raptor",
        designation="F-22A",
        category=ThreatCategory.FIGHTER_5GEN,
        threat_level=ThreatLevel.CRITICAL,
        country="USA",
        length_m=18.9,
        rcs_frontal_dbsm=-40,
        rcs_broadside_dbsm=-20,
        ir_signature_w=80000,
        max_speed=1500,  # Mach 2.25
        range_km=2960,
        primary_weapons=[
            "AIM-120D AMRAAM (6)",
            "AIM-9X Sidewinder (2)",
            "GBU-32 JDAM"
        ],
        weapon_capacity=8,
        defensive_systems=[
            "AN/APG-77 AESA radar",
            "AN/ALR-94 EW suite",
            "Supercruise capability"
        ],
        detection_vulnerabilities=[
            "VHF/UHF radar",
            "IR from supercruise",
            "Limited numbers (186)",
            "High operational cost"
        ],
        engagement_systems=[
            "J-20 with PL-15",
            "HQ-9B SAM",
            "JY-27A VHF radar"
        ],
        pk_air_defense=0.65,
        pk_submarine=0.0,
        pk_surface=0.0,
        pk_integrated=0.65,
        confidence=0.40
    )


def create_f35_all() -> List[ThreatPlatform]:
    """F-35 Lightning II variants"""
    variants = []

    for var, des, rcs_f, rcs_b, notes in [
        ("F-35A", "CTOL", -40, -10, "Air Force conventional"),
        ("F-35B", "STOVL", -38, -8, "Marine Corps STOVL"),
        ("F-35C", "CV", -40, -8, "Navy carrier variant")
    ]:
        variants.append(ThreatPlatform(
            name=f"F-35 Lightning II ({var})",
            designation=var,
            category=ThreatCategory.FIGHTER_5GEN,
            threat_level=ThreatLevel.CRITICAL,
            country="USA",
            length_m=15.7,
            rcs_frontal_dbsm=rcs_f,
            rcs_broadside_dbsm=rcs_b,
            ir_signature_w=70000,
            max_speed=1200,
            range_km=1100,
            primary_weapons=[
                "AIM-120D AMRAAM",
                "AIM-9X Sidewinder",
                "GBU-31/32 JDAM",
                "JSM/JASSM"
            ],
            weapon_capacity=6,
            defensive_systems=[
                "AN/APG-81 AESA",
                "AN/ASQ-239 EW",
                "DAS 360° IR coverage"
            ],
            detection_vulnerabilities=[
                "VHF/UHF resonance",
                "IR from exhaust",
                f"{notes} specific signatures",
                "Radar emissions when active"
            ],
            engagement_systems=[
                "J-20 + PL-15",
                "HQ-9B",
                "JY-27A + YLC-8E",
                "Passive ESM network"
            ],
            pk_air_defense=0.70,
            pk_submarine=0.0,
            pk_surface=0.0,
            pk_integrated=0.70,
            confidence=0.45
        ))

    return variants


# =============================================================================
# SURFACE COMBATANT THREATS
# =============================================================================

def create_ddg51() -> ThreatPlatform:
    """Arleigh Burke class destroyer"""
    return ThreatPlatform(
        name="Arleigh Burke Class DDG",
        designation="DDG-51",
        category=ThreatCategory.SURFACE_COMBATANT,
        threat_level=ThreatLevel.HIGH,
        country="USA",
        length_m=155,
        displacement_tons=9700,
        rcs_frontal_dbsm=35,
        ir_signature_w=2e6,
        max_speed=30,
        range_km=8100,  # nm
        primary_weapons=[
            "SM-2/SM-6 SAM (96 VLS)",
            "Tomahawk TLAM",
            "Harpoon SSM",
            "Mk 46/54 torpedo"
        ],
        weapon_capacity=96,
        defensive_systems=[
            "AN/SPY-1D Aegis",
            "Phalanx CIWS",
            "AN/SLQ-32 EW",
            "Nixie decoy"
        ],
        detection_vulnerabilities=[
            "Large radar signature",
            "Persistent emissions",
            "Wake signature",
            "Helicopter operations"
        ],
        engagement_systems=[
            "YJ-12 supersonic ASCM",
            "YJ-18 ASCM",
            "DF-21D ASBM",
            "Type 093 SSN torpedo"
        ],
        pk_air_defense=0.0,
        pk_submarine=0.55,
        pk_surface=0.65,
        pk_integrated=0.75,
        confidence=0.50
    )


def create_carrier_group() -> ThreatPlatform:
    """Full Carrier Strike Group"""
    return ThreatPlatform(
        name="Carrier Strike Group",
        designation="CSG",
        category=ThreatCategory.CARRIER_GROUP,
        threat_level=ThreatLevel.CRITICAL,
        country="USA",
        length_m=337,  # Carrier
        displacement_tons=100000,
        rcs_frontal_dbsm=55,
        ir_signature_w=5e6,
        max_speed=30,
        range_km=0,  # Unlimited
        primary_weapons=[
            "F/A-18E/F air wing (44)",
            "F-35C (planned)",
            "E-2D Hawkeye",
            "Escort ship weapons"
        ],
        weapon_capacity=90,  # Aircraft
        defensive_systems=[
            "Aegis escorts (2-4 DDG)",
            "E-2D AEW",
            "CAP fighters",
            "ASW helicopters",
            "Submarine escort"
        ],
        detection_vulnerabilities=[
            "Massive radar/IR signature",
            "Air operations emit",
            "Predictable patterns",
            "Satellite tracking"
        ],
        engagement_systems=[
            "DF-21D/DF-26 ASBM",
            "H-6K with YJ-12",
            "Type 093 submarine",
            "Coordinated saturation"
        ],
        pk_air_defense=0.0,
        pk_submarine=0.40,
        pk_surface=0.55,
        pk_integrated=0.75,
        confidence=0.40
    )


# =============================================================================
# THREAT ANALYSIS ENGINE
# =============================================================================

class ThreatAnalyzer:
    """Comprehensive threat analysis engine"""

    def __init__(self, logger: CalculationLogger):
        self.logger = logger
        self.threats: List[ThreatPlatform] = []

    def add_threat(self, threat: ThreatPlatform):
        self.threats.append(threat)

    def analyze_threat(self, threat: ThreatPlatform) -> Dict:
        """Analyze single threat platform"""

        analysis = {
            "platform": threat.name,
            "designation": threat.designation,
            "category": threat.category.value,
            "threat_level": threat.threat_level.value,

            "signatures": {
                "rcs_frontal_dbsm": threat.rcs_frontal_dbsm,
                "rcs_broadside_dbsm": threat.rcs_broadside_dbsm,
                "acoustic_db": threat.acoustic_signature_db,
                "ir_signature_w": threat.ir_signature_w
            },

            "detection_options": threat.detection_vulnerabilities,
            "engagement_systems": threat.engagement_systems,

            "kill_probabilities": {
                "air_defense": threat.pk_air_defense,
                "submarine": threat.pk_submarine,
                "surface": threat.pk_surface,
                "integrated": threat.pk_integrated
            },

            "confidence": threat.confidence,

            "recommendations": self._generate_recommendations(threat)
        }

        return analysis

    def _generate_recommendations(self, threat: ThreatPlatform) -> List[str]:
        """Generate defensive recommendations"""

        recs = []

        if threat.category == ThreatCategory.SUBMARINE_ATTACK:
            recs.extend([
                "Deploy Type 093B SSN in likely transit areas",
                "Increase Y-8Q maritime patrol coverage",
                "Expand SOSUS-type seabed arrays",
                "Coordinate with surface ASW groups",
                "Monitor VLF/ELF communication windows"
            ])

        elif threat.category == ThreatCategory.SUBMARINE_BALLISTIC:
            recs.extend([
                "Maintain SSN patrol in Pacific approaches",
                "Track SSBN departures from ports",
                "Monitor likely patrol areas",
                "Coordinate space-based ocean surveillance"
            ])

        elif threat.category == ThreatCategory.BOMBER_STRATEGIC:
            if threat.rcs_frontal_dbsm < -30:
                recs.extend([
                    "Deploy JY-27A VHF radar arrays",
                    "Establish passive detection networks",
                    "Coordinate space-based IR detection",
                    "Position J-20 CAP with GCI support"
                ])
            else:
                recs.extend([
                    "Standard radar detection adequate",
                    "HQ-9B/HQ-22 engagement zones",
                    "Fighter intercept with PL-15"
                ])

        elif threat.category == ThreatCategory.CRUISE_MISSILE:
            recs.extend([
                "Multi-layer point defense deployment",
                "OTH radar for early warning",
                "Hardened C2 facilities",
                "Mobile SAM positioning"
            ])

        elif threat.category == ThreatCategory.FIGHTER_5GEN:
            recs.extend([
                "VHF/UHF radar cueing",
                "Multi-sensor fusion tracking",
                "J-20 counter-air with PL-15",
                "Exploit off-boresight engagements",
                "Passive ESM for EMCON targets"
            ])

        elif threat.category == ThreatCategory.CARRIER_GROUP:
            recs.extend([
                "Satellite reconnaissance for cueing",
                "DF-21D/DF-26 ASBM salvo",
                "H-6K standoff missile strikes",
                "Submarine barrier operations",
                "Coordinated multi-axis attack"
            ])

        return recs

    def generate_threat_matrix(self) -> str:
        """Generate threat assessment matrix"""

        lines = []
        lines.append("=" * 100)
        lines.append("COMPREHENSIVE THREAT ASSESSMENT MATRIX")
        lines.append("=" * 100)
        lines.append("")

        # Group by category
        categories = {}
        for threat in self.threats:
            cat = threat.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(threat)

        for category, threats in categories.items():
            lines.append(f"\n{'─' * 100}")
            lines.append(f"CATEGORY: {category}")
            lines.append(f"{'─' * 100}")

            lines.append(f"{'Platform':<30} {'Level':<12} {'RCS(f)':<10} {'Pk(Int)':<10} {'Confidence':<12}")
            lines.append("-" * 80)

            for t in threats:
                lines.append(
                    f"{t.name:<30} {t.threat_level.value:<12} "
                    f"{t.rcs_frontal_dbsm:>6} dBsm  {t.pk_integrated:>6.1%}    {t.confidence:>6.1%}"
                )

        return "\n".join(lines)

    def generate_full_report(self) -> str:
        """Generate comprehensive threat report"""

        lines = []
        lines.append("=" * 100)
        lines.append("COMPREHENSIVE THREAT ANALYSIS REPORT")
        lines.append("Chinese National Security Threat Assessment")
        lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
        lines.append("Classification: UNCLASSIFIED // FOR ACADEMIC/RESEARCH USE")
        lines.append("=" * 100)

        # Executive Summary
        lines.append("\n" + "=" * 100)
        lines.append("EXECUTIVE SUMMARY")
        lines.append("=" * 100)

        critical = [t for t in self.threats if t.threat_level == ThreatLevel.CRITICAL]
        high = [t for t in self.threats if t.threat_level == ThreatLevel.HIGH]

        lines.append(f"\nTotal Threats Analyzed: {len(self.threats)}")
        lines.append(f"  Critical: {len(critical)}")
        lines.append(f"  High: {len(high)}")
        lines.append(f"  Medium/Low: {len(self.threats) - len(critical) - len(high)}")

        # Average Pk by domain
        air_threats = [t for t in self.threats if t.pk_air_defense > 0]
        sub_threats = [t for t in self.threats if t.pk_submarine > 0]
        surface_threats = [t for t in self.threats if t.pk_surface > 0]

        if air_threats:
            avg_air_pk = np.mean([t.pk_integrated for t in air_threats])
            lines.append(f"\nAverage Integrated Pk vs Air Threats: {avg_air_pk:.1%}")
        if sub_threats:
            avg_sub_pk = np.mean([t.pk_integrated for t in sub_threats])
            lines.append(f"Average Integrated Pk vs Submarine Threats: {avg_sub_pk:.1%}")
        if surface_threats:
            avg_surf_pk = np.mean([t.pk_integrated for t in surface_threats])
            lines.append(f"Average Integrated Pk vs Surface Threats: {avg_surf_pk:.1%}")

        # Detailed Analysis by Category
        for cat in ThreatCategory:
            cat_threats = [t for t in self.threats if t.category == cat]
            if not cat_threats:
                continue

            lines.append("\n" + "=" * 100)
            lines.append(f"THREAT CATEGORY: {cat.value}")
            lines.append("=" * 100)

            for threat in cat_threats:
                lines.append(f"\n{'─' * 80}")
                lines.append(f"PLATFORM: {threat.name} ({threat.designation})")
                lines.append(f"Threat Level: {threat.threat_level.value}")
                lines.append(f"{'─' * 80}")

                lines.append("\n  PHYSICAL CHARACTERISTICS:")
                lines.append(f"    Length: {threat.length_m} m")
                if threat.displacement_tons > 0:
                    lines.append(f"    Displacement: {threat.displacement_tons} tons")

                lines.append("\n  SIGNATURES:")
                if threat.rcs_frontal_dbsm != 0:
                    lines.append(f"    RCS (frontal): {threat.rcs_frontal_dbsm} dBsm")
                    lines.append(f"    RCS (broadside): {threat.rcs_broadside_dbsm} dBsm")
                if threat.acoustic_signature_db > 0:
                    lines.append(f"    Acoustic: {threat.acoustic_signature_db} dB")
                if threat.ir_signature_w > 0:
                    lines.append(f"    IR Signature: {threat.ir_signature_w/1000:.1f} kW")

                lines.append("\n  PRIMARY WEAPONS:")
                for wpn in threat.primary_weapons[:5]:
                    lines.append(f"    • {wpn}")

                lines.append("\n  DETECTION VULNERABILITIES:")
                for vuln in threat.detection_vulnerabilities[:5]:
                    lines.append(f"    • {vuln}")

                lines.append("\n  RECOMMENDED ENGAGEMENT SYSTEMS:")
                for eng in threat.engagement_systems[:5]:
                    lines.append(f"    • {eng}")

                lines.append("\n  KILL PROBABILITY ASSESSMENT:")
                lines.append(f"    Air Defense Pk: {threat.pk_air_defense:.1%}")
                lines.append(f"    Submarine Pk: {threat.pk_submarine:.1%}")
                lines.append(f"    Surface Pk: {threat.pk_surface:.1%}")
                lines.append(f"    INTEGRATED Pk: {threat.pk_integrated:.1%}")
                lines.append(f"    Assessment Confidence: {threat.confidence:.1%}")

        # Key Findings
        lines.append("\n" + "=" * 100)
        lines.append("KEY FINDINGS AND RECOMMENDATIONS")
        lines.append("=" * 100)

        lines.append("""
1. SUBMARINE THREATS (Most Difficult to Counter):
   - Virginia/Seawolf SSNs pose significant ASW challenge
   - Columbia SSBN extremely difficult to detect and track
   - Recommended: Expand deep-water SOSUS arrays, increase SSN patrols
   - Average Pk: 35-45% (significant uncertainty)

2. 5TH GENERATION FIGHTER THREATS:
   - F-22/F-35 require VHF/UHF radar for reliable detection
   - Off-boresight engagements significantly increase Pk
   - Recommended: Multi-sensor fusion, J-20 counter-air
   - Average Pk: 65-70% with optimal conditions

3. STRATEGIC BOMBER THREATS:
   - B-2/B-21 require specialized detection methods
   - B-1B conventional threats more detectable
   - Recommended: VHF radar arrays, space-based IR
   - Average Pk: 55-80% depending on platform

4. CRUISE MISSILE THREATS:
   - Saturation attacks difficult to defeat completely
   - JASSM-ER/LRASM stealth significant challenge
   - Recommended: Multi-layer point defense, hardening
   - Average Pk: 55-80% per missile

5. CARRIER STRIKE GROUP THREATS:
   - Detection relatively easy, engagement complex
   - Aegis defense layers reduce ASBM effectiveness
   - Recommended: Large salvos (12+), coordinated attacks
   - Average Pk: 70-75% with optimal conditions

OVERALL ASSESSMENT:
- No threat can be countered with 100% probability
- Multi-domain, integrated defense essential
- Continued investment in detection systems required
- Uncertainty in estimates ranges 25-55%
""")

        # Limitations
        lines.append("\n" + "=" * 100)
        lines.append("ANALYSIS LIMITATIONS")
        lines.append("=" * 100)
        lines.append("""
1. All signatures are estimates from open sources
2. Actual capabilities may differ significantly
3. Electronic warfare effects not fully modeled
4. Human factors and training not quantified
5. Environmental conditions simplified
6. Operational tactics may invalidate assumptions
7. Classified capabilities unknown
8. Future upgrades not considered
""")

        return "\n".join(lines)


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def run_comprehensive_threat_analysis():
    """Run full threat analysis for CI/CD pipeline"""

    logger = init_logger(
        name="Threat-Analysis",
        output_formats=[OutputFormat.CONSOLE, OutputFormat.GITHUB_ACTIONS],
        log_file="threat_analysis_log.txt",
        verbose=True
    )

    analyzer = ThreatAnalyzer(logger)

    print("=" * 100)
    print("COMPREHENSIVE THREAT ANALYSIS - CHINESE NATIONAL SECURITY")
    print("=" * 100)

    # Add all threats
    print("\nLoading threat platforms...")

    # Submarines
    with logger.section("Submarine Threats"):
        for sub in [create_virginia_class(), create_seawolf_class(),
                    create_columbia_class(), create_ohio_class(),
                    create_los_angeles_class()]:
            analyzer.add_threat(sub)
            logger.log_calculation(
                name=f"{sub.name} Threat Assessment",
                formula="Integrated detection and engagement",
                inputs={
                    "acoustic_sig_db": sub.acoustic_signature_db,
                    "pk_submarine": sub.pk_submarine,
                    "pk_integrated": sub.pk_integrated
                },
                result=sub.pk_integrated,
                unit="probability",
                confidence=sub.confidence
            )
        print(f"  Loaded {5} submarine platforms")

    # Strategic Bombers
    with logger.section("Strategic Bomber Threats"):
        for bomber in [create_b2_spirit(), create_b21_raider(), create_b1b_lancer()]:
            analyzer.add_threat(bomber)
            logger.log_calculation(
                name=f"{bomber.name} Threat Assessment",
                formula="Air defense engagement",
                inputs={
                    "rcs_frontal_dbsm": bomber.rcs_frontal_dbsm,
                    "pk_air_defense": bomber.pk_air_defense
                },
                result=bomber.pk_integrated,
                unit="probability",
                confidence=bomber.confidence
            )
        print(f"  Loaded {3} strategic bomber platforms")

    # Cruise Missiles
    with logger.section("Cruise Missile Threats"):
        for cm in [create_tomahawk(), create_jassm_er(), create_lrasm()]:
            analyzer.add_threat(cm)
            logger.log_calculation(
                name=f"{cm.name} Threat Assessment",
                formula="Point defense engagement",
                inputs={
                    "rcs_dbsm": cm.rcs_frontal_dbsm,
                    "speed_kts": cm.max_speed
                },
                result=cm.pk_integrated,
                unit="probability",
                confidence=cm.confidence
            )
        print(f"  Loaded {3} cruise missile types")

    # Fighters
    with logger.section("Fighter Threats"):
        analyzer.add_threat(create_f22_raptor())
        for f35 in create_f35_all():
            analyzer.add_threat(f35)
        print(f"  Loaded {4} fighter platforms")

    # Surface Combatants
    with logger.section("Surface Combatant Threats"):
        analyzer.add_threat(create_ddg51())
        analyzer.add_threat(create_carrier_group())
        print(f"  Loaded {2} surface combatant types")

    # Generate threat matrix
    print("\n" + analyzer.generate_threat_matrix())

    # Generate full report
    full_report = analyzer.generate_full_report()

    # Finalize logger
    logger.finalize()

    # Write outputs
    with open("threat_analysis_report.txt", "w") as f:
        f.write(full_report)
    print("\nWrote: threat_analysis_report.txt")

    # JSON output
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "threats_analyzed": len(analyzer.threats),
        "platforms": [analyzer.analyze_threat(t) for t in analyzer.threats],
        "summary": {
            "critical_threats": len([t for t in analyzer.threats if t.threat_level == ThreatLevel.CRITICAL]),
            "high_threats": len([t for t in analyzer.threats if t.threat_level == ThreatLevel.HIGH]),
            "average_pk_integrated": np.mean([t.pk_integrated for t in analyzer.threats]),
            "average_confidence": np.mean([t.confidence for t in analyzer.threats])
        }
    }

    with open("threat_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("Wrote: threat_analysis_results.json")

    # Markdown report
    md_report = logger.generate_markdown_report()
    with open("threat_analysis_report.md", "w") as f:
        f.write(md_report)
    print("Wrote: threat_analysis_report.md")

    print("\n" + "=" * 100)
    print("THREAT ANALYSIS COMPLETE")
    print("=" * 100)

    # Print summary for CI/CD output
    print(f"\n{'─' * 60}")
    print("SUMMARY FOR CI/CD PIPELINE")
    print(f"{'─' * 60}")
    print(f"Total Platforms Analyzed: {len(analyzer.threats)}")
    print(f"Critical Threats: {results['summary']['critical_threats']}")
    print(f"High Threats: {results['summary']['high_threats']}")
    print(f"Average Integrated Pk: {results['summary']['average_pk_integrated']:.1%}")
    print(f"Average Assessment Confidence: {results['summary']['average_confidence']:.1%}")

    return results


if __name__ == "__main__":
    run_comprehensive_threat_analysis()
