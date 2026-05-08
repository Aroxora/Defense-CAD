#!/usr/bin/env python3
"""
F-35 Infrastructure Vulnerability Analysis and Strike Planning

Comprehensive analysis of F-35 operational dependencies:
- Forward Operating Bases (Japan, Korea, Guam, Philippines)
- Aerial Refueling Assets (KC-135, KC-46, KC-10)
- Airborne Early Warning (E-3, E-7)
- Command and Control nodes
- Logistics and maintenance facilities

Strike planning integrates:
- DF-17 HGV for runway denial
- DF-21D/DF-26 for large fixed targets
- CJ-20 cruise missiles for hardened targets
- PL-15 + J-20 for airborne assets

Kill Chain: Reconnaissance → Strike Planning → Coordinated Attack → BDA
"""

import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np

try:
    from calculation_logger import CalculationLogger
except ImportError:
    class CalculationLogger:
        def __init__(self, name): self.name = name
        def section(self, name): pass
        def log_calculation(self, **kwargs): pass
        def log_algorithm(self, **kwargs): pass
        def finalize(self): pass
        def generate_markdown_report(self): return ""


# ==============================================================================
# ENUMERATIONS
# ==============================================================================

class TargetCategory(Enum):
    """Target categories for strike planning"""
    RUNWAY = "runway"
    HARDENED_SHELTER = "hardened_shelter"
    FUEL_STORAGE = "fuel_storage"
    MUNITIONS_STORAGE = "munitions_storage"
    MAINTENANCE_FACILITY = "maintenance_facility"
    COMMAND_CENTER = "command_center"
    RADAR_SITE = "radar_site"
    TANKER_ORBIT = "tanker_orbit"
    AWACS_ORBIT = "awacs_orbit"
    CARRIER = "carrier"
    CARRIER_AWACS = "carrier_awacs"
    SUBMARINE = "submarine"
    PORT_FACILITY = "port_facility"
    ASW_AIRCRAFT = "asw_aircraft"


class WeaponSystem(Enum):
    """Available strike weapons"""
    DF17_HGV = "df17_hgv"
    DF21D_ASBM = "df21d_asbm"
    DF26_IRBM = "df26_irbm"
    CJ20_ALCM = "cj20_alcm"
    CJ10_LACM = "cj10_lacm"
    DF16_SRBM = "df16_srbm"
    PL15_AAM = "pl15_aam"
    YJ12_ASCM = "yj12_ascm"


class ThreatLevel(Enum):
    """Target priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class GeoLocation:
    """Geographic coordinates"""
    latitude: float
    longitude: float
    name: str = ""

    def distance_to(self, other: 'GeoLocation') -> float:
        """Calculate great circle distance in km"""
        R = 6371  # Earth radius km
        lat1, lat2 = math.radians(self.latitude), math.radians(other.latitude)
        dlat = math.radians(other.latitude - self.latitude)
        dlon = math.radians(other.longitude - self.longitude)

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c


@dataclass
class Airbase:
    """Military airbase characteristics"""
    name: str
    location: GeoLocation
    country: str
    runway_length_m: float
    runway_count: int
    hardened_shelters: int
    fuel_capacity_gallons: int
    f35_capable: bool
    f35_deployed: int  # Current F-35 deployment
    other_aircraft: List[str]
    defense_systems: List[str]
    distance_to_taiwan_km: float = 0.0
    threat_level: ThreatLevel = ThreatLevel.HIGH

    def __post_init__(self):
        # Calculate distance to Taiwan (Taipei)
        taipei = GeoLocation(25.033, 121.565, "Taipei")
        self.distance_to_taiwan_km = self.location.distance_to(taipei)


@dataclass
class AerialAsset:
    """Airborne refueling or AWACS asset"""
    name: str
    aircraft_type: str
    typical_orbit: GeoLocation
    orbit_radius_km: float
    orbit_altitude_ft: float
    endurance_hours: float
    fuel_offload_lbs: int  # For tankers
    radar_range_km: float  # For AWACS
    escort_requirement: bool
    operating_bases: List[str]
    vulnerability_window_hours: float  # Time exposed in orbit


@dataclass
class StrikeTarget:
    """Target for strike planning"""
    name: str
    category: TargetCategory
    location: GeoLocation
    hardening_factor: float  # 1.0 = soft, 10.0 = hardened bunker
    area_m2: float
    defense_systems: List[str]
    defense_pk: float  # Combined defense Pk against incoming
    operational_impact: str  # Description of effect if destroyed
    regeneration_time_hours: float  # Time to restore capability
    threat_level: ThreatLevel


@dataclass
class WeaponCharacteristics:
    """Weapon system parameters"""
    name: str
    weapon_type: WeaponSystem
    range_km: float
    cep_m: float
    warhead_kg: float
    speed_terminal: str
    pk_vs_soft: float
    pk_vs_hardened: float
    pk_vs_airborne: float
    cost_estimate_musd: float
    inventory_estimate: int


@dataclass
class StrikePackage:
    """Strike package against a target"""
    target: StrikeTarget
    weapon: WeaponCharacteristics
    quantity: int
    pk_single: float
    pk_salvo: float
    expected_damage: str
    weapons_cost_musd: float


@dataclass
class CampaignResult:
    """Results of strike campaign analysis"""
    total_targets: int
    targets_by_category: Dict[str, int]
    total_weapons_required: int
    weapons_by_type: Dict[str, int]
    total_cost_musd: float
    expected_f35_grounded: int
    runway_denial_hours: float
    refueling_denial_probability: float
    key_findings: List[str]


# ==============================================================================
# WEAPONS DATABASE
# ==============================================================================

def create_weapons_database() -> Dict[WeaponSystem, WeaponCharacteristics]:
    """Create database of available strike weapons"""
    return {
        WeaponSystem.DF17_HGV: WeaponCharacteristics(
            name="DF-17 HGV",
            weapon_type=WeaponSystem.DF17_HGV,
            range_km=1800,
            cep_m=15,
            warhead_kg=600,
            speed_terminal="Mach 5+",
            pk_vs_soft=0.95,
            pk_vs_hardened=0.35,
            pk_vs_airborne=0.0,  # Not for air targets
            cost_estimate_musd=15.0,
            inventory_estimate=100
        ),
        WeaponSystem.DF21D_ASBM: WeaponCharacteristics(
            name="DF-21D ASBM",
            weapon_type=WeaponSystem.DF21D_ASBM,
            range_km=1500,
            cep_m=20,
            warhead_kg=600,
            speed_terminal="Mach 10",
            pk_vs_soft=0.90,
            pk_vs_hardened=0.40,
            pk_vs_airborne=0.0,
            cost_estimate_musd=12.0,
            inventory_estimate=200
        ),
        WeaponSystem.DF26_IRBM: WeaponCharacteristics(
            name="DF-26 IRBM",
            weapon_type=WeaponSystem.DF26_IRBM,
            range_km=4000,
            cep_m=30,
            warhead_kg=1200,
            speed_terminal="Mach 8",
            pk_vs_soft=0.85,
            pk_vs_hardened=0.50,
            pk_vs_airborne=0.0,
            cost_estimate_musd=20.0,
            inventory_estimate=150
        ),
        WeaponSystem.CJ20_ALCM: WeaponCharacteristics(
            name="CJ-20 ALCM",
            weapon_type=WeaponSystem.CJ20_ALCM,
            range_km=2000,
            cep_m=10,
            warhead_kg=500,
            speed_terminal="Mach 0.8",
            pk_vs_soft=0.85,
            pk_vs_hardened=0.60,  # Penetrator variant
            pk_vs_airborne=0.0,
            cost_estimate_musd=3.0,
            inventory_estimate=500
        ),
        WeaponSystem.CJ10_LACM: WeaponCharacteristics(
            name="CJ-10 LACM",
            weapon_type=WeaponSystem.CJ10_LACM,
            range_km=1500,
            cep_m=10,
            warhead_kg=500,
            speed_terminal="Mach 0.8",
            pk_vs_soft=0.85,
            pk_vs_hardened=0.55,
            pk_vs_airborne=0.0,
            cost_estimate_musd=2.5,
            inventory_estimate=800
        ),
        WeaponSystem.DF16_SRBM: WeaponCharacteristics(
            name="DF-16 SRBM",
            weapon_type=WeaponSystem.DF16_SRBM,
            range_km=1000,
            cep_m=10,
            warhead_kg=500,
            speed_terminal="Mach 6",
            pk_vs_soft=0.90,
            pk_vs_hardened=0.40,
            pk_vs_airborne=0.0,
            cost_estimate_musd=8.0,
            inventory_estimate=300
        ),
        WeaponSystem.PL15_AAM: WeaponCharacteristics(
            name="PL-15 AAM",
            weapon_type=WeaponSystem.PL15_AAM,
            range_km=200,
            cep_m=5,
            warhead_kg=30,
            speed_terminal="Mach 4",
            pk_vs_soft=0.0,
            pk_vs_hardened=0.0,
            pk_vs_airborne=0.85,
            cost_estimate_musd=1.5,
            inventory_estimate=2000
        ),
        WeaponSystem.YJ12_ASCM: WeaponCharacteristics(
            name="YJ-12 ASCM",
            weapon_type=WeaponSystem.YJ12_ASCM,
            range_km=400,
            cep_m=10,
            warhead_kg=400,
            speed_terminal="Mach 3",
            pk_vs_soft=0.80,
            pk_vs_hardened=0.30,
            pk_vs_airborne=0.0,
            cost_estimate_musd=2.0,
            inventory_estimate=400
        ),
    }


# ==============================================================================
# AIRBASES DATABASE - F-35 CAPABLE FACILITIES
# ==============================================================================

def create_japan_airbases() -> List[Airbase]:
    """US and JASDF bases in Japan capable of F-35 operations"""
    return [
        # US Air Force Bases
        Airbase(
            name="Kadena Air Base",
            location=GeoLocation(26.3516, 127.7692, "Kadena"),
            country="Japan (US)",
            runway_length_m=3688,
            runway_count=2,
            hardened_shelters=15,
            fuel_capacity_gallons=50_000_000,
            f35_capable=True,
            f35_deployed=0,  # Currently F-15C/D
            other_aircraft=["F-15C/D", "KC-135", "E-3", "HH-60"],
            defense_systems=["Patriot PAC-3", "THAAD"],
            threat_level=ThreatLevel.CRITICAL
        ),
        Airbase(
            name="Misawa Air Base",
            location=GeoLocation(40.7032, 141.3686, "Misawa"),
            country="Japan (US/JASDF)",
            runway_length_m=3050,
            runway_count=1,
            hardened_shelters=12,
            fuel_capacity_gallons=30_000_000,
            f35_capable=True,
            f35_deployed=12,  # F-35A deployed
            other_aircraft=["F-16C/D", "F-35A (JASDF)"],
            defense_systems=["Patriot PAC-3"],
            threat_level=ThreatLevel.CRITICAL
        ),
        Airbase(
            name="Yokota Air Base",
            location=GeoLocation(35.7485, 139.3485, "Yokota"),
            country="Japan (US)",
            runway_length_m=3353,
            runway_count=1,
            hardened_shelters=8,
            fuel_capacity_gallons=40_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["C-130J", "C-12", "UH-1N"],
            defense_systems=["Patriot PAC-3"],
            threat_level=ThreatLevel.HIGH
        ),
        Airbase(
            name="Iwakuni MCAS",
            location=GeoLocation(34.1439, 132.2356, "Iwakuni"),
            country="Japan (US)",
            runway_length_m=2440,
            runway_count=1,
            hardened_shelters=10,
            fuel_capacity_gallons=25_000_000,
            f35_capable=True,
            f35_deployed=16,  # F-35B VMFA-121
            other_aircraft=["F-35B", "F/A-18", "EA-18G"],
            defense_systems=["Patriot PAC-2"],
            threat_level=ThreatLevel.CRITICAL
        ),

        # JASDF Bases with F-35
        Airbase(
            name="Misawa (JASDF)",
            location=GeoLocation(40.6878, 141.3819, "Misawa JASDF"),
            country="Japan",
            runway_length_m=3050,
            runway_count=1,
            hardened_shelters=18,
            fuel_capacity_gallons=20_000_000,
            f35_capable=True,
            f35_deployed=20,  # JASDF F-35A
            other_aircraft=["F-35A"],
            defense_systems=["Patriot PAC-3", "Type 03 SAM"],
            threat_level=ThreatLevel.CRITICAL
        ),
        Airbase(
            name="Komatsu Air Base",
            location=GeoLocation(36.3947, 136.4069, "Komatsu"),
            country="Japan",
            runway_length_m=2700,
            runway_count=1,
            hardened_shelters=12,
            fuel_capacity_gallons=15_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["F-15J"],
            defense_systems=["Type 03 SAM"],
            threat_level=ThreatLevel.HIGH
        ),
        Airbase(
            name="Hyakuri Air Base",
            location=GeoLocation(36.1811, 140.4147, "Hyakuri"),
            country="Japan",
            runway_length_m=2700,
            runway_count=1,
            hardened_shelters=14,
            fuel_capacity_gallons=18_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["F-15J", "RF-4E"],
            defense_systems=["Type 03 SAM"],
            threat_level=ThreatLevel.HIGH
        ),
        Airbase(
            name="Chitose Air Base",
            location=GeoLocation(42.7944, 141.6664, "Chitose"),
            country="Japan",
            runway_length_m=3000,
            runway_count=2,
            hardened_shelters=16,
            fuel_capacity_gallons=20_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["F-15J"],
            defense_systems=["Type 03 SAM"],
            threat_level=ThreatLevel.MEDIUM
        ),
        Airbase(
            name="Naha Air Base",
            location=GeoLocation(26.1958, 127.6461, "Naha"),
            country="Japan",
            runway_length_m=3000,
            runway_count=1,
            hardened_shelters=10,
            fuel_capacity_gallons=15_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["F-15J"],
            defense_systems=["Type 03 SAM", "Patriot PAC-3"],
            threat_level=ThreatLevel.CRITICAL
        ),
        Airbase(
            name="Tsuiki Air Base",
            location=GeoLocation(33.6847, 131.0394, "Tsuiki"),
            country="Japan",
            runway_length_m=2400,
            runway_count=1,
            hardened_shelters=12,
            fuel_capacity_gallons=12_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["F-2"],
            defense_systems=["Type 03 SAM"],
            threat_level=ThreatLevel.HIGH
        ),
        Airbase(
            name="Nyutabaru Air Base",
            location=GeoLocation(32.0836, 131.4503, "Nyutabaru"),
            country="Japan",
            runway_length_m=2700,
            runway_count=1,
            hardened_shelters=10,
            fuel_capacity_gallons=14_000_000,
            f35_capable=True,
            f35_deployed=14,  # F-35A 301 Sqn
            other_aircraft=["F-35A", "F-15J"],
            defense_systems=["Type 03 SAM"],
            threat_level=ThreatLevel.CRITICAL
        ),
    ]


def create_korea_airbases() -> List[Airbase]:
    """US and ROKAF bases in South Korea"""
    return [
        Airbase(
            name="Osan Air Base",
            location=GeoLocation(37.0903, 127.0306, "Osan"),
            country="South Korea (US)",
            runway_length_m=2743,
            runway_count=1,
            hardened_shelters=20,
            fuel_capacity_gallons=35_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["F-16C/D", "A-10C", "U-2"],
            defense_systems=["Patriot PAC-3", "THAAD"],
            threat_level=ThreatLevel.HIGH
        ),
        Airbase(
            name="Kunsan Air Base",
            location=GeoLocation(35.9039, 126.6158, "Kunsan"),
            country="South Korea (US)",
            runway_length_m=2743,
            runway_count=1,
            hardened_shelters=18,
            fuel_capacity_gallons=30_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["F-16C/D"],
            defense_systems=["Patriot PAC-2"],
            threat_level=ThreatLevel.HIGH
        ),
        Airbase(
            name="Cheongju Air Base",
            location=GeoLocation(36.7167, 127.4986, "Cheongju"),
            country="South Korea",
            runway_length_m=2750,
            runway_count=1,
            hardened_shelters=24,
            fuel_capacity_gallons=25_000_000,
            f35_capable=True,
            f35_deployed=40,  # ROKAF F-35A
            other_aircraft=["F-35A"],
            defense_systems=["Patriot PAC-3", "KM-SAM"],
            threat_level=ThreatLevel.CRITICAL
        ),
        Airbase(
            name="Daegu Air Base",
            location=GeoLocation(35.8964, 128.6589, "Daegu"),
            country="South Korea",
            runway_length_m=2750,
            runway_count=1,
            hardened_shelters=16,
            fuel_capacity_gallons=20_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["F-15K"],
            defense_systems=["Patriot PAC-2"],
            threat_level=ThreatLevel.HIGH
        ),
    ]


def create_guam_airbases() -> List[Airbase]:
    """US bases in Guam"""
    return [
        Airbase(
            name="Andersen Air Force Base",
            location=GeoLocation(13.5839, 144.9244, "Andersen"),
            country="Guam (US)",
            runway_length_m=3413,
            runway_count=2,
            hardened_shelters=8,
            fuel_capacity_gallons=66_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=["B-52H", "B-2A", "B-1B", "KC-135"],
            defense_systems=["THAAD", "Patriot PAC-3"],
            threat_level=ThreatLevel.CRITICAL
        ),
    ]


def create_philippines_airbases() -> List[Airbase]:
    """Philippine bases with EDCA access"""
    return [
        Airbase(
            name="Basa Air Base",
            location=GeoLocation(15.1833, 120.5333, "Basa"),
            country="Philippines",
            runway_length_m=3000,
            runway_count=1,
            hardened_shelters=4,
            fuel_capacity_gallons=5_000_000,
            f35_capable=True,  # EDCA facility
            f35_deployed=0,
            other_aircraft=["FA-50"],
            defense_systems=["SPYDER"],
            threat_level=ThreatLevel.HIGH
        ),
        Airbase(
            name="Antonio Bautista Air Base",
            location=GeoLocation(9.7428, 118.7589, "Bautista"),
            country="Philippines",
            runway_length_m=2500,
            runway_count=1,
            hardened_shelters=2,
            fuel_capacity_gallons=3_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=[],
            defense_systems=[],
            threat_level=ThreatLevel.MEDIUM
        ),
        Airbase(
            name="Laoag International (EDCA)",
            location=GeoLocation(18.1781, 120.5317, "Laoag"),
            country="Philippines",
            runway_length_m=2500,
            runway_count=1,
            hardened_shelters=0,
            fuel_capacity_gallons=2_000_000,
            f35_capable=True,
            f35_deployed=0,
            other_aircraft=[],
            defense_systems=[],
            threat_level=ThreatLevel.MEDIUM
        ),
    ]


# ==============================================================================
# AERIAL REFUELING AND AWACS ASSETS
# ==============================================================================

def create_tanker_assets() -> List[AerialAsset]:
    """Aerial refueling tanker assets"""
    return [
        AerialAsset(
            name="KC-135 Stratotanker (Kadena)",
            aircraft_type="KC-135R",
            typical_orbit=GeoLocation(25.5, 125.0, "East China Sea Track"),
            orbit_radius_km=150,
            orbit_altitude_ft=25000,
            endurance_hours=12,
            fuel_offload_lbs=120000,
            radar_range_km=0,
            escort_requirement=True,
            operating_bases=["Kadena"],
            vulnerability_window_hours=8
        ),
        AerialAsset(
            name="KC-135 Stratotanker (Yokota)",
            aircraft_type="KC-135R",
            typical_orbit=GeoLocation(33.0, 133.0, "Philippine Sea Track"),
            orbit_radius_km=150,
            orbit_altitude_ft=25000,
            endurance_hours=12,
            fuel_offload_lbs=120000,
            radar_range_km=0,
            escort_requirement=True,
            operating_bases=["Yokota"],
            vulnerability_window_hours=8
        ),
        AerialAsset(
            name="KC-46 Pegasus (Guam)",
            aircraft_type="KC-46A",
            typical_orbit=GeoLocation(18.0, 138.0, "Western Pacific Track"),
            orbit_radius_km=200,
            orbit_altitude_ft=30000,
            endurance_hours=14,
            fuel_offload_lbs=207000,
            radar_range_km=0,
            escort_requirement=True,
            operating_bases=["Andersen"],
            vulnerability_window_hours=10
        ),
        AerialAsset(
            name="KC-46 Pegasus (Japan)",
            aircraft_type="KC-46A",
            typical_orbit=GeoLocation(30.0, 130.0, "East China Sea South"),
            orbit_radius_km=180,
            orbit_altitude_ft=28000,
            endurance_hours=14,
            fuel_offload_lbs=207000,
            radar_range_km=0,
            escort_requirement=True,
            operating_bases=["Yokota", "Kadena"],
            vulnerability_window_hours=10
        ),
    ]


def create_awacs_assets() -> List[AerialAsset]:
    """Airborne early warning assets"""
    return [
        AerialAsset(
            name="E-3 Sentry (Kadena)",
            aircraft_type="E-3B/C",
            typical_orbit=GeoLocation(26.0, 126.0, "Okinawa AWACS Track"),
            orbit_radius_km=200,
            orbit_altitude_ft=30000,
            endurance_hours=10,
            fuel_offload_lbs=0,
            radar_range_km=400,
            escort_requirement=True,
            operating_bases=["Kadena"],
            vulnerability_window_hours=8
        ),
        AerialAsset(
            name="E-767 AWACS (JASDF)",
            aircraft_type="E-767",
            typical_orbit=GeoLocation(32.0, 130.0, "Japan AWACS Track"),
            orbit_radius_km=180,
            orbit_altitude_ft=32000,
            endurance_hours=12,
            fuel_offload_lbs=0,
            radar_range_km=450,
            escort_requirement=True,
            operating_bases=["Hamamatsu"],
            vulnerability_window_hours=10
        ),
        AerialAsset(
            name="E-7A Wedgetail (ROKAF)",
            aircraft_type="E-7A",
            typical_orbit=GeoLocation(35.0, 127.0, "Korea AWACS Track"),
            orbit_radius_km=160,
            orbit_altitude_ft=30000,
            endurance_hours=11,
            fuel_offload_lbs=0,
            radar_range_km=370,
            escort_requirement=True,
            operating_bases=["Gimhae"],
            vulnerability_window_hours=9
        ),
    ]


# ==============================================================================
# CARRIER STRIKE GROUP ASSETS
# ==============================================================================

@dataclass
class CarrierStrikeGroup:
    """Carrier Strike Group characteristics"""
    name: str
    carrier_class: str
    hull_number: str
    homeport: str
    air_wing: str
    f35c_squadron: bool
    f35c_count: int
    fa18_count: int
    e2d_count: int
    typical_operating_area: GeoLocation
    escort_ships: List[str]
    defense_systems: List[str]
    sortie_rate_per_day: int
    vulnerability_factors: List[str]


@dataclass
class SubmarineThreat:
    """US submarine threat characteristics"""
    name: str
    sub_class: str
    hull_numbers: List[str]
    homeport: str
    tomahawk_capacity: int
    torpedo_tubes: int
    acoustic_signature_db: float
    patrol_areas: List[GeoLocation]
    mission_types: List[str]
    threat_level: ThreatLevel
    detection_difficulty: str  # easy, moderate, difficult, very_difficult


def create_carrier_strike_groups() -> List[CarrierStrikeGroup]:
    """Pacific Fleet Carrier Strike Groups"""
    return [
        CarrierStrikeGroup(
            name="CSG-1 (Carl Vinson)",
            carrier_class="Nimitz",
            hull_number="CVN-70",
            homeport="San Diego",
            air_wing="CVW-2",
            f35c_squadron=True,
            f35c_count=10,  # VFA-147 Argonauts
            fa18_count=34,
            e2d_count=5,
            typical_operating_area=GeoLocation(22.0, 130.0, "Philippine Sea"),
            escort_ships=["CG-52", "DDG-x2", "SSN"],
            defense_systems=["SM-6", "ESSM", "SeaRAM", "CIWS"],
            sortie_rate_per_day=120,
            vulnerability_factors=[
                "Large radar signature",
                "IR signature from operations",
                "Communication emissions",
                "Predictable operating patterns"
            ]
        ),
        CarrierStrikeGroup(
            name="CSG-3 (Abraham Lincoln)",
            carrier_class="Nimitz",
            hull_number="CVN-72",
            homeport="San Diego",
            air_wing="CVW-9",
            f35c_squadron=True,
            f35c_count=10,
            fa18_count=34,
            e2d_count=5,
            typical_operating_area=GeoLocation(20.0, 125.0, "South China Sea"),
            escort_ships=["CG-54", "DDG-x2", "SSN"],
            defense_systems=["SM-6", "ESSM", "SeaRAM", "CIWS"],
            sortie_rate_per_day=120,
            vulnerability_factors=[
                "Large radar signature",
                "IR signature from operations",
                "Communication emissions"
            ]
        ),
        CarrierStrikeGroup(
            name="CSG-5 (Ronald Reagan)",
            carrier_class="Nimitz",
            hull_number="CVN-76",
            homeport="Yokosuka, Japan",
            air_wing="CVW-5",
            f35c_squadron=False,  # Currently F/A-18
            f35c_count=0,
            fa18_count=44,
            e2d_count=5,
            typical_operating_area=GeoLocation(25.0, 128.0, "East China Sea"),
            escort_ships=["CG-62", "DDG-85", "DDG-89", "SSN"],
            defense_systems=["SM-6", "ESSM", "SeaRAM", "CIWS"],
            sortie_rate_per_day=120,
            vulnerability_factors=[
                "Forward deployed - reduced reaction time",
                "Predictable Yokosuka port calls",
                "High operational tempo"
            ]
        ),
        CarrierStrikeGroup(
            name="CSG-11 (Theodore Roosevelt)",
            carrier_class="Nimitz",
            hull_number="CVN-71",
            homeport="San Diego",
            air_wing="CVW-11",
            f35c_squadron=True,
            f35c_count=10,
            fa18_count=34,
            e2d_count=5,
            typical_operating_area=GeoLocation(18.0, 135.0, "Western Pacific"),
            escort_ships=["CG-57", "DDG-x2", "SSN"],
            defense_systems=["SM-6", "ESSM", "SeaRAM", "CIWS"],
            sortie_rate_per_day=120,
            vulnerability_factors=[
                "Long transit from CONUS",
                "Chokepoints at Malacca/Lombok"
            ]
        ),
        CarrierStrikeGroup(
            name="USS Gerald R. Ford",
            carrier_class="Ford",
            hull_number="CVN-78",
            homeport="Norfolk",
            air_wing="CVW-8",
            f35c_squadron=True,
            f35c_count=12,  # Planned
            fa18_count=32,
            e2d_count=5,
            typical_operating_area=GeoLocation(15.0, 140.0, "Central Pacific"),
            escort_ships=["DDG-1000", "DDG-x2", "SSN"],
            defense_systems=["SM-6", "ESSM", "SeaRAM", "CIWS"],
            sortie_rate_per_day=160,  # EMALS advantage
            vulnerability_factors=[
                "New systems - potential reliability issues",
                "Extended transit from Atlantic"
            ]
        ),
    ]


def create_submarine_threats() -> List[SubmarineThreat]:
    """US submarine threats in Pacific"""
    return [
        SubmarineThreat(
            name="Virginia Class SSN (Block III+)",
            sub_class="Virginia",
            hull_numbers=["SSN-784", "SSN-785", "SSN-786", "SSN-787", "SSN-788"],
            homeport="Pearl Harbor / Guam",
            tomahawk_capacity=12,  # VLS
            torpedo_tubes=4,
            acoustic_signature_db=95,  # Estimated
            patrol_areas=[
                GeoLocation(22.0, 120.0, "Taiwan Strait approaches"),
                GeoLocation(25.0, 125.0, "First Island Chain"),
                GeoLocation(20.0, 118.0, "South China Sea")
            ],
            mission_types=["ISR", "Land attack", "ASW", "Special ops"],
            threat_level=ThreatLevel.CRITICAL,
            detection_difficulty="very_difficult"
        ),
        SubmarineThreat(
            name="Virginia Class SSN (Block V)",
            sub_class="Virginia Block V",
            hull_numbers=["SSN-794", "SSN-796", "SSN-798"],
            homeport="Pearl Harbor",
            tomahawk_capacity=40,  # VPM
            torpedo_tubes=4,
            acoustic_signature_db=92,
            patrol_areas=[
                GeoLocation(24.0, 122.0, "Taiwan East Coast"),
                GeoLocation(18.0, 116.0, "Luzon Strait")
            ],
            mission_types=["Land attack (VPM)", "ISR", "ASW"],
            threat_level=ThreatLevel.CRITICAL,
            detection_difficulty="very_difficult"
        ),
        SubmarineThreat(
            name="Seawolf Class SSN",
            sub_class="Seawolf",
            hull_numbers=["SSN-21", "SSN-22", "SSN-23"],
            homeport="Bangor, WA",
            tomahawk_capacity=8,
            torpedo_tubes=8,
            acoustic_signature_db=90,  # Quietest US sub
            patrol_areas=[
                GeoLocation(26.0, 126.0, "Ryukyu Islands"),
                GeoLocation(22.0, 124.0, "Bashi Channel")
            ],
            mission_types=["ASW hunter-killer", "Special ops", "ISR"],
            threat_level=ThreatLevel.CRITICAL,
            detection_difficulty="very_difficult"
        ),
        SubmarineThreat(
            name="Los Angeles Class SSN (688i)",
            sub_class="Los Angeles Improved",
            hull_numbers=["SSN-751", "SSN-752", "SSN-753", "SSN-754", "SSN-755"],
            homeport="Pearl Harbor / Guam",
            tomahawk_capacity=12,
            torpedo_tubes=4,
            acoustic_signature_db=105,
            patrol_areas=[
                GeoLocation(20.0, 130.0, "Philippine Sea"),
                GeoLocation(15.0, 120.0, "South China Sea")
            ],
            mission_types=["Land attack", "ASW", "ISR"],
            threat_level=ThreatLevel.HIGH,
            detection_difficulty="difficult"
        ),
        SubmarineThreat(
            name="Ohio Class SSGN",
            sub_class="Ohio SSGN",
            hull_numbers=["SSGN-726", "SSGN-727", "SSGN-728", "SSGN-729"],
            homeport="Bangor, WA",
            tomahawk_capacity=154,  # Massive strike capability
            torpedo_tubes=4,
            acoustic_signature_db=100,
            patrol_areas=[
                GeoLocation(16.0, 135.0, "Mariana Islands"),
                GeoLocation(20.0, 140.0, "Pacific approaches")
            ],
            mission_types=["Mass land attack", "Special ops", "ISR"],
            threat_level=ThreatLevel.CRITICAL,
            detection_difficulty="difficult"
        ),
    ]


def create_carrier_awacs() -> List[AerialAsset]:
    """E-2D Hawkeye carrier-based AWACS"""
    return [
        AerialAsset(
            name="E-2D Hawkeye (CVW-2)",
            aircraft_type="E-2D",
            typical_orbit=GeoLocation(23.0, 128.0, "CSG-1 AWACS"),
            orbit_radius_km=100,
            orbit_altitude_ft=25000,
            endurance_hours=6,
            fuel_offload_lbs=0,
            radar_range_km=550,  # APY-9 radar
            escort_requirement=True,
            operating_bases=["CVN-70"],
            vulnerability_window_hours=5
        ),
        AerialAsset(
            name="E-2D Hawkeye (CVW-5)",
            aircraft_type="E-2D",
            typical_orbit=GeoLocation(26.0, 126.0, "CSG-5 AWACS"),
            orbit_radius_km=100,
            orbit_altitude_ft=25000,
            endurance_hours=6,
            fuel_offload_lbs=0,
            radar_range_km=550,
            escort_requirement=True,
            operating_bases=["CVN-76"],
            vulnerability_window_hours=5
        ),
        AerialAsset(
            name="E-2D Hawkeye (CVW-9)",
            aircraft_type="E-2D",
            typical_orbit=GeoLocation(21.0, 123.0, "CSG-3 AWACS"),
            orbit_radius_km=100,
            orbit_altitude_ft=25000,
            endurance_hours=6,
            fuel_offload_lbs=0,
            radar_range_km=550,
            escort_requirement=True,
            operating_bases=["CVN-72"],
            vulnerability_window_hours=5
        ),
    ]


def create_asw_assets() -> List[AerialAsset]:
    """P-8 Poseidon and other ASW aircraft"""
    return [
        AerialAsset(
            name="P-8A Poseidon (VP-4)",
            aircraft_type="P-8A",
            typical_orbit=GeoLocation(24.0, 122.0, "Taiwan Strait Patrol"),
            orbit_radius_km=300,
            orbit_altitude_ft=30000,
            endurance_hours=10,
            fuel_offload_lbs=0,
            radar_range_km=200,  # APY-10 radar
            escort_requirement=False,
            operating_bases=["Kadena", "Misawa"],
            vulnerability_window_hours=8
        ),
        AerialAsset(
            name="P-8A Poseidon (VP-47)",
            aircraft_type="P-8A",
            typical_orbit=GeoLocation(20.0, 118.0, "South China Sea Patrol"),
            orbit_radius_km=350,
            orbit_altitude_ft=28000,
            endurance_hours=10,
            fuel_offload_lbs=0,
            radar_range_km=200,
            escort_requirement=False,
            operating_bases=["Kadena"],
            vulnerability_window_hours=8
        ),
    ]


# ==============================================================================
# STRIKE PLANNING ENGINE
# ==============================================================================

class F35InfrastructureStrikePlanner:
    """Plans coordinated strikes against F-35 infrastructure"""

    def __init__(self, logger: Optional[CalculationLogger] = None):
        self.logger = logger or CalculationLogger("F35-Infrastructure-Strike")
        self.weapons = create_weapons_database()
        self.airbases = (
            create_japan_airbases() +
            create_korea_airbases() +
            create_guam_airbases() +
            create_philippines_airbases()
        )
        self.tankers = create_tanker_assets()
        self.awacs = create_awacs_assets()
        self.carrier_groups = create_carrier_strike_groups()
        self.carrier_awacs = create_carrier_awacs()
        self.submarines = create_submarine_threats()
        self.asw_aircraft = create_asw_assets()

        # Reference point for range calculations
        self.launch_point = GeoLocation(25.0, 119.0, "Eastern China")

        self.strike_packages: List[StrikePackage] = []
        self.targets: List[StrikeTarget] = []

    def generate_airbase_targets(self) -> List[StrikeTarget]:
        """Generate strike targets from airbases"""
        targets = []

        for base in self.airbases:
            range_km = self.launch_point.distance_to(base.location)

            # Skip bases beyond weapon range
            if range_km > 4000:
                continue

            # Runway targets
            targets.append(StrikeTarget(
                name=f"{base.name} - Runway",
                category=TargetCategory.RUNWAY,
                location=base.location,
                hardening_factor=1.5,  # Concrete but repairable
                area_m2=base.runway_length_m * 45,  # Standard width
                defense_systems=base.defense_systems,
                defense_pk=self._calculate_defense_pk(base.defense_systems, "ballistic"),
                operational_impact=f"Denies {base.f35_deployed + 20} aircraft operations",
                regeneration_time_hours=24 if base.runway_count > 1 else 72,
                threat_level=base.threat_level
            ))

            # Hardened aircraft shelters
            if base.hardened_shelters > 0:
                targets.append(StrikeTarget(
                    name=f"{base.name} - HAS Complex",
                    category=TargetCategory.HARDENED_SHELTER,
                    location=base.location,
                    hardening_factor=8.0,  # Reinforced concrete
                    area_m2=base.hardened_shelters * 400,  # Per shelter
                    defense_systems=base.defense_systems,
                    defense_pk=self._calculate_defense_pk(base.defense_systems, "cruise"),
                    operational_impact=f"Destroys {base.hardened_shelters} sheltered aircraft",
                    regeneration_time_hours=168,  # 1 week minimum
                    threat_level=base.threat_level
                ))

            # Fuel storage
            targets.append(StrikeTarget(
                name=f"{base.name} - Fuel Storage",
                category=TargetCategory.FUEL_STORAGE,
                location=base.location,
                hardening_factor=1.2,
                area_m2=5000,
                defense_systems=base.defense_systems,
                defense_pk=self._calculate_defense_pk(base.defense_systems, "cruise"),
                operational_impact=f"Eliminates {base.fuel_capacity_gallons:,} gallons capacity",
                regeneration_time_hours=720,  # 1 month
                threat_level=ThreatLevel.HIGH if base.threat_level == ThreatLevel.CRITICAL else ThreatLevel.MEDIUM
            ))

            # Maintenance facilities
            if base.f35_capable:
                targets.append(StrikeTarget(
                    name=f"{base.name} - Maintenance",
                    category=TargetCategory.MAINTENANCE_FACILITY,
                    location=base.location,
                    hardening_factor=2.0,
                    area_m2=8000,
                    defense_systems=base.defense_systems,
                    defense_pk=self._calculate_defense_pk(base.defense_systems, "cruise"),
                    operational_impact="Eliminates F-35 maintenance capability",
                    regeneration_time_hours=2160,  # 3 months
                    threat_level=ThreatLevel.HIGH
                ))

        return targets

    def generate_aerial_targets(self) -> List[StrikeTarget]:
        """Generate targets from tankers and AWACS"""
        targets = []

        # Tanker orbits
        for tanker in self.tankers:
            targets.append(StrikeTarget(
                name=f"{tanker.name} - Orbit",
                category=TargetCategory.TANKER_ORBIT,
                location=tanker.typical_orbit,
                hardening_factor=0.0,  # Aircraft
                area_m2=500,  # Aircraft size
                defense_systems=["Fighter escort", "Self-defense"],
                defense_pk=0.30,  # Escort effectiveness
                operational_impact=f"Denies {tanker.fuel_offload_lbs:,} lbs fuel offload",
                regeneration_time_hours=48,  # Replacement aircraft
                threat_level=ThreatLevel.CRITICAL
            ))

        # Land-based AWACS orbits
        for awacs in self.awacs:
            targets.append(StrikeTarget(
                name=f"{awacs.name} - Orbit",
                category=TargetCategory.AWACS_ORBIT,
                location=awacs.typical_orbit,
                hardening_factor=0.0,
                area_m2=600,
                defense_systems=["Fighter escort", "Jamming"],
                defense_pk=0.35,
                operational_impact=f"Denies {awacs.radar_range_km} km radar coverage",
                regeneration_time_hours=72,
                threat_level=ThreatLevel.CRITICAL
            ))

        # Carrier-based E-2D AWACS
        for hawkeye in self.carrier_awacs:
            targets.append(StrikeTarget(
                name=f"{hawkeye.name}",
                category=TargetCategory.CARRIER_AWACS,
                location=hawkeye.typical_orbit,
                hardening_factor=0.0,
                area_m2=400,
                defense_systems=["CAP escort", "Carrier SAM umbrella"],
                defense_pk=0.40,  # Better protected near carrier
                operational_impact=f"Denies carrier AEW - {hawkeye.radar_range_km} km coverage",
                regeneration_time_hours=24,  # Can launch replacement
                threat_level=ThreatLevel.CRITICAL
            ))

        # P-8 ASW aircraft
        for asw in self.asw_aircraft:
            targets.append(StrikeTarget(
                name=f"{asw.name}",
                category=TargetCategory.ASW_AIRCRAFT,
                location=asw.typical_orbit,
                hardening_factor=0.0,
                area_m2=500,
                defense_systems=["Self-defense", "Unpredictable patterns"],
                defense_pk=0.20,  # Less escorted
                operational_impact="Degrades ASW coverage - enables submarine operations",
                regeneration_time_hours=48,
                threat_level=ThreatLevel.HIGH
            ))

        return targets

    def generate_carrier_targets(self) -> List[StrikeTarget]:
        """Generate targets from carrier strike groups"""
        targets = []

        for csg in self.carrier_groups:
            # Carrier itself
            targets.append(StrikeTarget(
                name=f"{csg.name} - {csg.hull_number}",
                category=TargetCategory.CARRIER,
                location=csg.typical_operating_area,
                hardening_factor=1.5,  # Large but vulnerable
                area_m2=25000,  # Flight deck area
                defense_systems=csg.defense_systems,
                defense_pk=0.35,  # Multi-layer defense
                operational_impact=f"Eliminates {csg.f35c_count} F-35C + {csg.fa18_count} F/A-18 + {csg.e2d_count} E-2D",
                regeneration_time_hours=8760,  # 1 year+ to replace
                threat_level=ThreatLevel.CRITICAL
            ))

        return targets

    def generate_submarine_interdiction(self) -> List[StrikeTarget]:
        """Generate submarine threat analysis (ASW required)"""
        targets = []

        for sub in self.submarines:
            for i, patrol_area in enumerate(sub.patrol_areas):
                targets.append(StrikeTarget(
                    name=f"{sub.name} - Patrol Area {i+1}",
                    category=TargetCategory.SUBMARINE,
                    location=patrol_area,
                    hardening_factor=0.0,  # Underwater
                    area_m2=1000,  # Effective search area
                    defense_systems=["Stealth", "Deep diving", "Countermeasures"],
                    defense_pk=0.0,  # Different engagement method
                    operational_impact=f"Neutralizes {sub.tomahawk_capacity} TLAM threat",
                    regeneration_time_hours=720,  # 1 month patrol rotation
                    threat_level=sub.threat_level
                ))

        return targets

    def _calculate_defense_pk(self, systems: List[str], attack_type: str) -> float:
        """Calculate combined defense Pk"""
        base_pk = 0.0

        for system in systems:
            if "THAAD" in system:
                if attack_type == "ballistic":
                    base_pk = max(base_pk, 0.25)  # Against HGV
            elif "PAC-3" in system:
                if attack_type == "ballistic":
                    base_pk = max(base_pk, 0.15)
                elif attack_type == "cruise":
                    base_pk = max(base_pk, 0.30)
            elif "PAC-2" in system:
                if attack_type == "cruise":
                    base_pk = max(base_pk, 0.20)
            elif "Type 03" in system or "KM-SAM" in system:
                if attack_type == "cruise":
                    base_pk = max(base_pk, 0.25)

        return base_pk

    def select_weapon(self, target: StrikeTarget, range_km: float) -> WeaponCharacteristics:
        """Select optimal weapon for target"""

        # Airborne targets - use PL-15
        if target.category in [TargetCategory.TANKER_ORBIT, TargetCategory.AWACS_ORBIT,
                               TargetCategory.CARRIER_AWACS, TargetCategory.ASW_AIRCRAFT]:
            return self.weapons[WeaponSystem.PL15_AAM]

        # Submarines - special case (ASW weapons not modeled, use proxy)
        if target.category == TargetCategory.SUBMARINE:
            # Return a proxy weapon representing ASW capability
            return WeaponCharacteristics(
                name="Type 093B SSN + Yu-6 Torpedo",
                weapon_type=WeaponSystem.YJ12_ASCM,  # Proxy
                range_km=50,
                cep_m=10,
                warhead_kg=300,
                speed_terminal="45 kts",
                pk_vs_soft=0.0,
                pk_vs_hardened=0.0,
                pk_vs_airborne=0.0,
                cost_estimate_musd=50.0,  # SSN patrol cost
                inventory_estimate=12  # SSN fleet
            )

        # Carriers - use DF-21D or DF-26 ASBM
        if target.category == TargetCategory.CARRIER:
            if range_km <= 1500:
                return self.weapons[WeaponSystem.DF21D_ASBM]
            else:
                return self.weapons[WeaponSystem.DF26_IRBM]

        # Runway - use DF-17 HGV for speed and precision
        if target.category == TargetCategory.RUNWAY:
            if range_km <= 1800:
                return self.weapons[WeaponSystem.DF17_HGV]
            elif range_km <= 4000:
                return self.weapons[WeaponSystem.DF26_IRBM]

        # Hardened targets - use penetrator cruise missiles
        if target.category == TargetCategory.HARDENED_SHELTER:
            if range_km <= 1500:
                return self.weapons[WeaponSystem.CJ10_LACM]
            else:
                return self.weapons[WeaponSystem.CJ20_ALCM]

        # Soft targets - use most cost-effective
        if target.hardening_factor < 2.0:
            if range_km <= 1000:
                return self.weapons[WeaponSystem.DF16_SRBM]
            elif range_km <= 1500:
                return self.weapons[WeaponSystem.CJ10_LACM]
            else:
                return self.weapons[WeaponSystem.DF26_IRBM]

        # Default - DF-21D for medium range
        if range_km <= 1500:
            return self.weapons[WeaponSystem.DF21D_ASBM]
        return self.weapons[WeaponSystem.DF26_IRBM]

    def calculate_strike_pk(
        self,
        weapon: WeaponCharacteristics,
        target: StrikeTarget,
        quantity: int
    ) -> Tuple[float, float]:
        """Calculate single and salvo Pk"""

        # Base weapon Pk
        if target.category in [TargetCategory.TANKER_ORBIT, TargetCategory.AWACS_ORBIT]:
            base_pk = weapon.pk_vs_airborne
        elif target.hardening_factor > 3.0:
            base_pk = weapon.pk_vs_hardened
        else:
            base_pk = weapon.pk_vs_soft

        # Adjust for defenses
        p_penetrate = 1 - target.defense_pk
        pk_single = base_pk * p_penetrate

        # CEP adjustment for target size
        target_radius = math.sqrt(target.area_m2 / math.pi)
        if weapon.cep_m > 0:
            cep_factor = 1 - 0.5 ** ((target_radius / weapon.cep_m) ** 2)
            pk_single *= cep_factor

        pk_single = min(0.95, max(0.05, pk_single))

        # Salvo Pk with correlation
        correlation = 0.2  # Some correlation in attack
        n_effective = 1 + (quantity - 1) * (1 - correlation)
        pk_salvo = 1 - (1 - pk_single) ** n_effective

        return pk_single, pk_salvo

    def calculate_required_quantity(
        self,
        weapon: WeaponCharacteristics,
        target: StrikeTarget,
        target_pk: float = 0.90
    ) -> int:
        """Calculate weapons needed to achieve target Pk"""

        for qty in range(1, 25):
            _, pk_salvo = self.calculate_strike_pk(weapon, target, qty)
            if pk_salvo >= target_pk:
                return qty

        return 24  # Maximum

    def plan_strikes(self, target_pk: float = 0.90) -> List[StrikePackage]:
        """Plan strike packages for all targets"""

        self.logger.section("Strike Planning")

        # Generate all targets
        self.targets = (
            self.generate_airbase_targets() +
            self.generate_aerial_targets() +
            self.generate_carrier_targets() +
            self.generate_submarine_interdiction()
        )
        self.strike_packages = []

        for target in self.targets:
            range_km = self.launch_point.distance_to(target.location)

            # Select weapon
            weapon = self.select_weapon(target, range_km)

            # Calculate quantity needed
            quantity = self.calculate_required_quantity(weapon, target, target_pk)

            # Calculate Pk
            pk_single, pk_salvo = self.calculate_strike_pk(weapon, target, quantity)

            # Create strike package
            package = StrikePackage(
                target=target,
                weapon=weapon,
                quantity=quantity,
                pk_single=pk_single,
                pk_salvo=pk_salvo,
                expected_damage=target.operational_impact,
                weapons_cost_musd=quantity * weapon.cost_estimate_musd
            )

            self.strike_packages.append(package)

            self.logger.log_calculation(
                name=f"Strike: {target.name}",
                formula="Salvo Pk calculation",
                inputs={
                    "weapon": weapon.name,
                    "quantity": quantity,
                    "range_km": range_km,
                    "target_hardening": target.hardening_factor,
                    "defense_pk": target.defense_pk
                },
                result=pk_salvo,
                unit="probability",
                confidence=50
            )

        return self.strike_packages

    def calculate_campaign_results(self) -> CampaignResult:
        """Calculate overall campaign results"""

        self.logger.section("Campaign Analysis")

        # Count targets by category
        targets_by_cat = {}
        for pkg in self.strike_packages:
            cat = pkg.target.category.value
            targets_by_cat[cat] = targets_by_cat.get(cat, 0) + 1

        # Count weapons by type
        weapons_by_type = {}
        total_weapons = 0
        total_cost = 0.0

        for pkg in self.strike_packages:
            wtype = pkg.weapon.name
            weapons_by_type[wtype] = weapons_by_type.get(wtype, 0) + pkg.quantity
            total_weapons += pkg.quantity
            total_cost += pkg.weapons_cost_musd

        # Calculate F-35s grounded
        f35_grounded = 0
        runway_denial_hours = 0.0

        for pkg in self.strike_packages:
            if pkg.target.category == TargetCategory.RUNWAY:
                if pkg.pk_salvo > 0.7:
                    runway_denial_hours = max(runway_denial_hours, pkg.target.regeneration_time_hours)
                    # Estimate F-35s per base
                    for base in self.airbases:
                        if base.name in pkg.target.name:
                            f35_grounded += base.f35_deployed + 10  # Plus potential deployments

        # Calculate refueling denial
        tanker_strikes = [p for p in self.strike_packages
                        if p.target.category == TargetCategory.TANKER_ORBIT]
        if tanker_strikes:
            refuel_denial = sum(p.pk_salvo for p in tanker_strikes) / len(tanker_strikes)
        else:
            refuel_denial = 0.0

        # Calculate carrier strike effectiveness
        carrier_strikes = [p for p in self.strike_packages
                         if p.target.category == TargetCategory.CARRIER]
        carrier_denial = sum(p.pk_salvo for p in carrier_strikes) / len(carrier_strikes) if carrier_strikes else 0

        # Calculate submarine interdiction (ASW)
        sub_targets = [p for p in self.strike_packages
                      if p.target.category == TargetCategory.SUBMARINE]
        total_tlam_threat = sum(s.tomahawk_capacity for s in self.submarines)

        # Key findings
        findings = [
            f"Total of {len(self.targets)} critical targets identified across {len(self.airbases)} airbases",
            f"Strike campaign requires {total_weapons} weapons at estimated cost of ${total_cost:.1f}M",
            f"Runway denial expected for {runway_denial_hours:.0f} hours minimum",
            f"Estimated {f35_grounded}+ F-35s grounded due to infrastructure damage",
            f"Tanker denial probability: {refuel_denial:.1%} - forces F-35 to operate at reduced radius",
            f"AWACS denial eliminates beyond-visual-range engagement capability",
            f"{len(self.carrier_groups)} carrier strike groups identified - {sum(c.f35c_count for c in self.carrier_groups)} F-35C total",
            f"Carrier strike probability: {carrier_denial:.1%} with ASBM salvos",
            f"{len(self.submarines)} submarine patrol areas - {total_tlam_threat} TLAM threat capacity",
            f"Submarine interdiction requires sustained ASW operations",
            f"Hardened shelters require penetrator weapons - higher cost per target",
            f"Guam strikes extend campaign to strategic depth"
        ]

        result = CampaignResult(
            total_targets=len(self.targets),
            targets_by_category=targets_by_cat,
            total_weapons_required=total_weapons,
            weapons_by_type=weapons_by_type,
            total_cost_musd=total_cost,
            expected_f35_grounded=f35_grounded,
            runway_denial_hours=runway_denial_hours,
            refueling_denial_probability=refuel_denial,
            key_findings=findings
        )

        self.logger.log_calculation(
            name="Campaign Summary",
            formula="Aggregate strike analysis",
            inputs={
                "total_targets": len(self.targets),
                "total_weapons": total_weapons,
                "total_cost_musd": total_cost
            },
            result=f35_grounded,
            unit="aircraft grounded",
            confidence=45
        )

        return result


# ==============================================================================
# COMPREHENSIVE ANALYSIS
# ==============================================================================

class F35VulnerabilityAnalysis:
    """Complete F-35 infrastructure vulnerability analysis"""

    def __init__(self):
        self.logger = CalculationLogger("F35-Infrastructure-Vulnerability")
        self.planner = F35InfrastructureStrikePlanner(self.logger)
        self.strike_packages = []
        self.campaign_result = None

    def run_analysis(self):
        """Run complete analysis"""

        print("=" * 80)
        print("F-35 INFRASTRUCTURE VULNERABILITY ANALYSIS")
        print("Runway Denial, Tanker Interdiction, AWACS Elimination")
        print("=" * 80)
        print()

        # Plan strikes
        self.strike_packages = self.planner.plan_strikes(target_pk=0.90)

        # Calculate campaign results
        self.campaign_result = self.planner.calculate_campaign_results()

        # Display results
        self._display_airbases()
        self._display_aerial_assets()
        self._display_carrier_threats()
        self._display_submarine_threats()
        self._display_strike_packages()
        self._display_campaign_summary()

        return self.campaign_result

    def _display_airbases(self):
        """Display airbase analysis"""

        print("\n" + "=" * 80)
        print("F-35 CAPABLE AIRBASES")
        print("=" * 80)

        # Sort by distance to Taiwan
        sorted_bases = sorted(self.planner.airbases, key=lambda b: b.distance_to_taiwan_km)

        print(f"\n{'Base':<30} {'Country':<15} {'Dist (km)':<10} {'F-35s':<8} {'Threat':<10}")
        print("-" * 80)

        for base in sorted_bases[:15]:  # Top 15 closest
            print(f"{base.name:<30} {base.country:<15} {base.distance_to_taiwan_km:<10.0f} "
                  f"{base.f35_deployed:<8} {base.threat_level.value:<10}")

        print(f"\nTotal F-35 capable bases: {len(self.planner.airbases)}")
        total_f35 = sum(b.f35_deployed for b in self.planner.airbases)
        print(f"Total F-35s currently deployed: {total_f35}")

    def _display_aerial_assets(self):
        """Display tanker and AWACS vulnerabilities"""

        print("\n" + "=" * 80)
        print("AERIAL REFUELING VULNERABILITY ANALYSIS")
        print("=" * 80)

        print("\nTanker Assets:")
        print(f"{'Asset':<35} {'Type':<12} {'Fuel Offload':<15} {'Vulnerability':<12}")
        print("-" * 80)

        for tanker in self.planner.tankers:
            print(f"{tanker.name:<35} {tanker.aircraft_type:<12} "
                  f"{tanker.fuel_offload_lbs:>12,} lbs  {tanker.vulnerability_window_hours:.0f} hrs")

        print("\nCRITICAL: Without tanker support, F-35A combat radius reduced from")
        print("         ~1,100 nm to ~670 nm - insufficient for Taiwan Strait operations")
        print("         from Japan mainland bases")

        print("\n" + "=" * 80)
        print("AWACS VULNERABILITY ANALYSIS")
        print("=" * 80)

        print("\nAWACS Assets:")
        print(f"{'Asset':<35} {'Type':<12} {'Radar Range':<15} {'Endurance':<12}")
        print("-" * 80)

        for awacs in self.planner.awacs:
            print(f"{awacs.name:<35} {awacs.aircraft_type:<12} "
                  f"{awacs.radar_range_km:>10.0f} km   {awacs.endurance_hours:.0f} hrs")

        print("\nCRITICAL: AWACS elimination denies F-35 beyond-visual-range (BVR)")
        print("         engagement capability - forces visual-range combat where")
        print("         PL-15 + J-20 integration provides advantage")

    def _display_carrier_threats(self):
        """Display carrier strike group analysis"""

        print("\n" + "=" * 80)
        print("CARRIER STRIKE GROUP THREATS")
        print("=" * 80)

        print(f"\n{'CSG':<25} {'Carrier':<12} {'F-35C':<8} {'F/A-18':<8} {'E-2D':<6} {'Homeport':<15}")
        print("-" * 80)

        total_f35c = 0
        total_fa18 = 0
        for csg in self.planner.carrier_groups:
            total_f35c += csg.f35c_count
            total_fa18 += csg.fa18_count
            print(f"{csg.name:<25} {csg.hull_number:<12} {csg.f35c_count:<8} "
                  f"{csg.fa18_count:<8} {csg.e2d_count:<6} {csg.homeport:<15}")

        print(f"\nTotal Carrier-Based Aircraft Threat:")
        print(f"  - F-35C: {total_f35c}")
        print(f"  - F/A-18E/F: {total_fa18}")
        print(f"  - E-2D Hawkeye: {sum(c.e2d_count for c in self.planner.carrier_groups)}")

        print("\nCRITICAL: Each CSG can generate 120+ sorties/day")
        print("         Forward-deployed CVN-76 (Yokosuka) is highest priority")
        print("         E-2D provides 550km AEW coverage - must be neutralized")

    def _display_submarine_threats(self):
        """Display submarine threat analysis"""

        print("\n" + "=" * 80)
        print("SUBMARINE THREAT ANALYSIS")
        print("=" * 80)

        print(f"\n{'Class':<30} {'TLAM':<8} {'Acoustic':<10} {'Detection':<15} {'Threat':<10}")
        print("-" * 80)

        total_tlam = 0
        for sub in self.planner.submarines:
            total_tlam += sub.tomahawk_capacity * len(sub.hull_numbers)
            print(f"{sub.name[:30]:<30} {sub.tomahawk_capacity:<8} "
                  f"{sub.acoustic_signature_db:.0f} dB    {sub.detection_difficulty:<15} {sub.threat_level.value:<10}")

        print(f"\nTotal Submarine-Launched TLAM Capacity: {total_tlam}+")
        print(f"\nPatrol Areas of Concern:")
        for sub in self.planner.submarines[:3]:
            for area in sub.patrol_areas[:2]:
                print(f"  - {area.name}: {area.latitude:.1f}°N, {area.longitude:.1f}°E")

        print("\nCRITICAL: Virginia Block V with VPM carries 40 TLAM each")
        print("         Ohio SSGN carries 154 TLAM - mass strike capability")
        print("         ASW barrier operations essential in First Island Chain")

    def _display_strike_packages(self):
        """Display strike package summary"""

        print("\n" + "=" * 80)
        print("STRIKE PACKAGES BY CATEGORY")
        print("=" * 80)

        categories = {}
        for pkg in self.strike_packages:
            cat = pkg.target.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(pkg)

        for cat, packages in categories.items():
            print(f"\n### {cat.upper().replace('_', ' ')}")
            print(f"{'Target':<40} {'Weapon':<15} {'Qty':<5} {'Pk':<8} {'Cost':<10}")
            print("-" * 80)

            for pkg in sorted(packages, key=lambda p: p.target.threat_level.value)[:10]:
                print(f"{pkg.target.name[:40]:<40} {pkg.weapon.name:<15} "
                      f"{pkg.quantity:<5} {pkg.pk_salvo:.1%}   ${pkg.weapons_cost_musd:.1f}M")

    def _display_campaign_summary(self):
        """Display campaign summary"""

        print("\n" + "=" * 80)
        print("CAMPAIGN SUMMARY")
        print("=" * 80)

        result = self.campaign_result

        print(f"\nTotal Targets: {result.total_targets}")
        print(f"Total Weapons Required: {result.total_weapons_required}")
        print(f"Estimated Cost: ${result.total_cost_musd:.1f}M")
        print(f"\nExpected Results:")
        print(f"  - F-35s Grounded: {result.expected_f35_grounded}+")
        print(f"  - Runway Denial: {result.runway_denial_hours:.0f} hours minimum")
        print(f"  - Tanker Denial: {result.refueling_denial_probability:.1%}")

        print(f"\nWeapons by Type:")
        for wtype, qty in sorted(result.weapons_by_type.items(), key=lambda x: -x[1]):
            print(f"  - {wtype}: {qty}")

        print(f"\nTargets by Category:")
        for cat, count in sorted(result.targets_by_category.items(), key=lambda x: -x[1]):
            print(f"  - {cat}: {count}")

        print("\nKey Findings:")
        for finding in result.key_findings:
            print(f"  • {finding}")

    def export_results(self, prefix: str = "f35_infrastructure"):
        """Export results to files"""

        self.logger.finalize()

        # Prepare export data
        output = {
            "generated": datetime.now().isoformat(),
            "analysis": "F-35 Infrastructure Vulnerability Assessment",
            "airbases": [
                {
                    "name": b.name,
                    "country": b.country,
                    "location": {"lat": b.location.latitude, "lon": b.location.longitude},
                    "distance_to_taiwan_km": b.distance_to_taiwan_km,
                    "f35_deployed": b.f35_deployed,
                    "f35_capable": b.f35_capable,
                    "runway_length_m": b.runway_length_m,
                    "hardened_shelters": b.hardened_shelters,
                    "threat_level": b.threat_level.value
                }
                for b in self.planner.airbases
            ],
            "tankers": [
                {
                    "name": t.name,
                    "type": t.aircraft_type,
                    "orbit": {"lat": t.typical_orbit.latitude, "lon": t.typical_orbit.longitude},
                    "fuel_offload_lbs": t.fuel_offload_lbs,
                    "vulnerability_hours": t.vulnerability_window_hours
                }
                for t in self.planner.tankers
            ],
            "awacs": [
                {
                    "name": a.name,
                    "type": a.aircraft_type,
                    "orbit": {"lat": a.typical_orbit.latitude, "lon": a.typical_orbit.longitude},
                    "radar_range_km": a.radar_range_km,
                    "vulnerability_hours": a.vulnerability_window_hours
                }
                for a in self.planner.awacs
            ],
            "carrier_strike_groups": [
                {
                    "name": c.name,
                    "carrier_class": c.carrier_class,
                    "hull_number": c.hull_number,
                    "homeport": c.homeport,
                    "f35c_count": c.f35c_count,
                    "fa18_count": c.fa18_count,
                    "e2d_count": c.e2d_count,
                    "operating_area": {"lat": c.typical_operating_area.latitude, "lon": c.typical_operating_area.longitude},
                    "sortie_rate": c.sortie_rate_per_day,
                    "vulnerabilities": c.vulnerability_factors
                }
                for c in self.planner.carrier_groups
            ],
            "submarines": [
                {
                    "name": s.name,
                    "class": s.sub_class,
                    "tlam_capacity": s.tomahawk_capacity,
                    "acoustic_signature_db": s.acoustic_signature_db,
                    "detection_difficulty": s.detection_difficulty,
                    "threat_level": s.threat_level.value,
                    "patrol_areas": [{"name": p.name, "lat": p.latitude, "lon": p.longitude} for p in s.patrol_areas]
                }
                for s in self.planner.submarines
            ],
            "strike_packages": [
                {
                    "target": pkg.target.name,
                    "category": pkg.target.category.value,
                    "weapon": pkg.weapon.name,
                    "quantity": pkg.quantity,
                    "pk_single": pkg.pk_single,
                    "pk_salvo": pkg.pk_salvo,
                    "cost_musd": pkg.weapons_cost_musd,
                    "operational_impact": pkg.expected_damage
                }
                for pkg in self.strike_packages
            ],
            "campaign_summary": {
                "total_targets": self.campaign_result.total_targets,
                "total_weapons": self.campaign_result.total_weapons_required,
                "total_cost_musd": self.campaign_result.total_cost_musd,
                "f35_grounded": self.campaign_result.expected_f35_grounded,
                "runway_denial_hours": self.campaign_result.runway_denial_hours,
                "tanker_denial_probability": self.campaign_result.refueling_denial_probability,
                "weapons_by_type": self.campaign_result.weapons_by_type,
                "targets_by_category": self.campaign_result.targets_by_category,
                "key_findings": self.campaign_result.key_findings
            }
        }

        # JSON output
        json_path = f"{prefix}_results.json"
        with open(json_path, "w") as f:
            json.dump(output, f, indent=2)

        # Markdown report
        md_path = f"{prefix}_report.md"
        self._write_markdown_report(md_path, output)

        print(f"\nResults exported to:")
        print(f"  • {json_path}")
        print(f"  • {md_path}")

        return json_path, md_path

    def _write_markdown_report(self, path: str, data: dict):
        """Write detailed markdown report"""

        report = f"""# F-35 Infrastructure Vulnerability Analysis

**Generated:** {data['generated']}
**Analysis:** Runway Denial, Tanker Interdiction, AWACS Elimination

## Executive Summary

This analysis identifies critical vulnerabilities in the F-35 operational infrastructure
that supports potential operations against Taiwan. Key findings:

- **{data['campaign_summary']['total_targets']} critical targets** identified
- **{data['campaign_summary']['total_weapons']} weapons** required for campaign
- **${data['campaign_summary']['total_cost_musd']:.1f}M** estimated cost
- **{data['campaign_summary']['f35_grounded']}+ F-35s** potentially grounded

## Critical Vulnerabilities

### 1. Runway Dependency

F-35A requires 8,000+ ft runways for safe operations. Limited basing options create
concentrated targets:

| Base | Country | Distance to Taiwan | F-35s | Threat Level |
|------|---------|-------------------|-------|--------------|
"""

        sorted_bases = sorted(data['airbases'], key=lambda b: b['distance_to_taiwan_km'])
        for base in sorted_bases[:12]:
            report += f"| {base['name']} | {base['country']} | {base['distance_to_taiwan_km']:.0f} km | "
            report += f"{base['f35_deployed']} | {base['threat_level']} |\n"

        report += """
### 2. Aerial Refueling Dependency

**CRITICAL VULNERABILITY:** F-35A combat radius is ~1,100 nm with tanker support but
only ~670 nm without. Tanker denial forces F-35 to either:
- Operate from forward bases (higher vulnerability)
- Accept reduced combat persistence
- Abort missions mid-flight

| Tanker Asset | Type | Fuel Offload | Vulnerability Window |
|--------------|------|--------------|---------------------|
"""

        for tanker in data['tankers']:
            report += f"| {tanker['name']} | {tanker['type']} | {tanker['fuel_offload_lbs']:,} lbs | "
            report += f"{tanker['vulnerability_hours']:.0f} hrs |\n"

        report += f"""
**Tanker Denial Probability:** {data['campaign_summary']['tanker_denial_probability']:.1%}

### 3. AWACS Dependency

Without AWACS support, F-35 loses:
- Beyond-visual-range (BVR) engagement capability
- Situational awareness beyond onboard radar
- Coordinated multi-ship tactics

| AWACS Asset | Type | Radar Range | Vulnerability Window |
|-------------|------|-------------|---------------------|
"""

        for awacs in data['awacs']:
            report += f"| {awacs['name']} | {awacs['type']} | {awacs['radar_range_km']:.0f} km | "
            report += f"{awacs['vulnerability_hours']:.0f} hrs |\n"

        report += """
## Strike Campaign Plan

### Weapons Allocation

| Weapon System | Quantity | Primary Targets |
|---------------|----------|-----------------|
"""

        for weapon, qty in sorted(data['campaign_summary']['weapons_by_type'].items(), key=lambda x: -x[1]):
            if "DF-17" in weapon:
                targets = "Runways, soft infrastructure"
            elif "PL-15" in weapon:
                targets = "Tankers, AWACS"
            elif "CJ" in weapon:
                targets = "Hardened shelters, maintenance"
            elif "DF-26" in weapon:
                targets = "Guam facilities, deep targets"
            else:
                targets = "Various"
            report += f"| {weapon} | {qty} | {targets} |\n"

        report += """
### Target Categories

| Category | Count | Primary Weapon |
|----------|-------|----------------|
"""

        for cat, count in sorted(data['campaign_summary']['targets_by_category'].items(), key=lambda x: -x[1]):
            if "runway" in cat:
                weapon = "DF-17 HGV"
            elif "shelter" in cat:
                weapon = "CJ-10/CJ-20"
            elif "tanker" in cat or "awacs" in cat:
                weapon = "PL-15 AAM"
            else:
                weapon = "Various"
            report += f"| {cat.replace('_', ' ').title()} | {count} | {weapon} |\n"

        report += """
## Operational Concept

### Phase 1: SEAD/DEAD (H-0 to H+2)
- Saturate air defense radars with decoys
- DF-17 strikes on Patriot/THAAD batteries
- Suppress runway defenses

### Phase 2: Runway Denial (H+2 to H+6)
- DF-17/DF-16 strikes on all F-35 capable runways
- Crater intersections and taxiways
- Target fuel storage and maintenance

### Phase 3: Aerial Asset Interdiction (H+4 to H+12)
- J-20 + PL-15 CAP against tanker orbits
- Long-range intercept of AWACS
- Force aerial assets to withdraw

### Phase 4: Sustained Denial (H+12 onwards)
- Re-strike repaired runways
- Maintain tanker/AWACS denial
- Attrit any forward-deployed F-35s

## Key Findings

"""

        for finding in data['campaign_summary']['key_findings']:
            report += f"- {finding}\n"

        report += """
## Limitations

- Classified basing and deployment data not available
- Defense effectiveness estimates from open sources
- Electronic warfare effects not fully modeled
- Assumes pre-conflict reconnaissance successful
- Does not account for US reinforcement from CONUS
- Assessment confidence: 40-55%

## Recommendations

1. **Prioritize tanker interdiction** - Maximum impact on F-35 operational capability
2. **Coordinate runway strikes** - Simultaneous attacks prevent dispersal
3. **Maintain AWACS denial** - Forces close-range combat favorable to PL-15
4. **Plan for re-strikes** - Runways can be repaired in 24-72 hours
5. **Target maintenance facilities** - Long-term degradation of F-35 readiness

---
*Analysis generated by F-35 Infrastructure Strike Planner*
"""

        with open(path, "w") as f:
            f.write(report)


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main(output_dir: str = "."):
    """Run F-35 infrastructure vulnerability analysis"""

    analysis = F35VulnerabilityAnalysis()
    result = analysis.run_analysis()
    analysis.export_results(prefix=f"{output_dir}/f35_infrastructure")

    return analysis


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    main(output_dir)
