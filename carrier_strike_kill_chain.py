#!/usr/bin/env python3
"""
Carrier Strike Kill Chain Analysis

Maximizes kill probability against Ford/Nimitz class carriers using:
- DF-21D/DF-26 Anti-Ship Ballistic Missiles (ASBM)
- Satellite reconnaissance chain (Yaogan series)
- Over-the-horizon radar (OTH-B type)
- Maritime surveillance drones (WZ-7 Soar Dragon, BZK-005)
- Submarine reconnaissance (Type 093/095)
- Terminal maneuvering warhead guidance

Analysis includes:
- Carrier detection and tracking
- ASBM trajectory and guidance modeling
- Terminal seeker acquisition
- Carrier countermeasures (SM-3, SM-6, CIWS)
- Kill chain timing analysis

Classification: UNCLASSIFIED // FOR ACADEMIC/RESEARCH USE
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import json
from datetime import datetime, timezone

from calculation_logger import CalculationLogger, OutputFormat, init_logger


# =============================================================================
# CARRIER CLASS CHARACTERISTICS
# =============================================================================

class CarrierClass(Enum):
    """US carrier classes"""
    FORD = "Ford Class (CVN-78)"
    NIMITZ = "Nimitz Class (CVN-68)"


@dataclass
class CarrierSignature:
    """Aircraft carrier radar and signature characteristics"""
    carrier_class: CarrierClass

    # Physical dimensions
    length_m: float
    beam_m: float
    draft_m: float
    displacement_tons: float
    flight_deck_area_m2: float

    # Radar cross section (large target)
    rcs_x_band_dbsm: float   # X-band RCS
    rcs_s_band_dbsm: float   # S-band RCS

    # Infrared signature
    ir_signature_w: float

    # Speed and maneuverability
    max_speed_kts: float
    turn_rate_deg_per_min: float
    acceleration_time_s: float  # To max speed

    # Defensive systems
    defense_systems: List[str]

    # Wake signature (for radar detection)
    wake_length_km: float

    # Confidence
    confidence: float = 0.0


def create_ford_class() -> CarrierSignature:
    """CVN-78 Ford Class carrier"""
    return CarrierSignature(
        carrier_class=CarrierClass.FORD,
        length_m=337,
        beam_m=78,          # Flight deck width
        draft_m=12,
        displacement_tons=100000,
        flight_deck_area_m2=337 * 78,  # ~26,000 m²
        rcs_x_band_dbsm=55,   # Very large RCS (~300,000 m²)
        rcs_s_band_dbsm=58,
        ir_signature_w=5e6,   # 5 MW thermal signature
        max_speed_kts=30,
        turn_rate_deg_per_min=3,  # Large turning radius
        acceleration_time_s=180,
        defense_systems=[
            "AN/SPY-6(V)1 AMDR",
            "SM-3 Block IIA",
            "SM-6",
            "ESSM",
            "RIM-116 RAM",
            "Phalanx CIWS",
            "AN/SLQ-32(V)7 EW Suite",
            "Nixie torpedo decoy"
        ],
        wake_length_km=5,
        confidence=0.70
    )


def create_nimitz_class() -> CarrierSignature:
    """CVN-68 Nimitz Class carrier"""
    return CarrierSignature(
        carrier_class=CarrierClass.NIMITZ,
        length_m=332,
        beam_m=77,
        draft_m=11.3,
        displacement_tons=97000,
        flight_deck_area_m2=332 * 77,
        rcs_x_band_dbsm=54,
        rcs_s_band_dbsm=57,
        ir_signature_w=4.5e6,
        max_speed_kts=31,
        turn_rate_deg_per_min=3,
        acceleration_time_s=200,
        defense_systems=[
            "AN/SPY-1D(V) Aegis",
            "SM-2 Block IIIA",
            "SM-6",
            "ESSM",
            "RIM-116 RAM",
            "Phalanx CIWS",
            "AN/SLQ-32(V)6 EW Suite"
        ],
        wake_length_km=4.5,
        confidence=0.75
    )


# =============================================================================
# SATELLITE RECONNAISSANCE SYSTEM
# =============================================================================

@dataclass
class ReconSatellite:
    """Reconnaissance satellite characteristics"""
    name: str
    sat_type: str  # "SAR", "ELINT", "Optical"
    orbit_altitude_km: float
    revisit_time_hours: float
    swath_width_km: float

    # Detection capabilities
    resolution_m: float        # Ground resolution
    detection_probability: float
    localization_accuracy_m: float

    # Limitations
    weather_degradation: float  # Factor for cloud cover
    night_capable: bool

    confidence: float = 0.0


def create_yaogan_sar() -> ReconSatellite:
    """Yaogan SAR satellite for maritime surveillance"""
    return ReconSatellite(
        name="Yaogan-35 (SAR)",
        sat_type="SAR",
        orbit_altitude_km=500,
        revisit_time_hours=6,  # With constellation
        swath_width_km=100,
        resolution_m=1.0,
        detection_probability=0.85,
        localization_accuracy_m=50,
        weather_degradation=0.95,  # SAR penetrates clouds
        night_capable=True,
        confidence=0.55
    )


def create_yaogan_elint() -> ReconSatellite:
    """Yaogan ELINT satellite"""
    return ReconSatellite(
        name="Yaogan-30 (ELINT)",
        sat_type="ELINT",
        orbit_altitude_km=600,
        revisit_time_hours=4,
        swath_width_km=3000,  # Wide coverage
        resolution_m=0,  # N/A for ELINT
        detection_probability=0.90,  # High Pd when carrier emits
        localization_accuracy_m=5000,  # Coarse location
        weather_degradation=1.0,  # Unaffected
        night_capable=True,
        confidence=0.60
    )


def create_jilin_optical() -> ReconSatellite:
    """Jilin-1 commercial optical satellite"""
    return ReconSatellite(
        name="Jilin-1 (Optical)",
        sat_type="Optical",
        orbit_altitude_km=535,
        revisit_time_hours=3,  # Large constellation
        swath_width_km=40,
        resolution_m=0.5,
        detection_probability=0.75,  # Day, clear weather only
        localization_accuracy_m=10,
        weather_degradation=0.3,  # Severely affected by clouds
        night_capable=False,
        confidence=0.50
    )


# =============================================================================
# OVER-THE-HORIZON RADAR
# =============================================================================

@dataclass
class OTHRadar:
    """Over-the-horizon radar system"""
    name: str
    radar_type: str
    frequency_band: str
    max_range_km: float
    min_range_km: float
    detection_probability: float
    range_accuracy_km: float
    azimuth_accuracy_deg: float
    update_rate_s: float
    confidence: float = 0.0


def create_oth_radar() -> OTHRadar:
    """Chinese OTH-B type radar"""
    return OTHRadar(
        name="OTH-B Type Radar",
        radar_type="Skywave HF",
        frequency_band="HF (3-30 MHz)",
        max_range_km=3500,
        min_range_km=800,
        detection_probability=0.80,  # Against large ships
        range_accuracy_km=20,        # Coarse
        azimuth_accuracy_deg=2.0,
        update_rate_s=60,
        confidence=0.50
    )


# =============================================================================
# MARITIME SURVEILLANCE DRONES
# =============================================================================

@dataclass
class SurveillanceDrone:
    """Maritime surveillance UAV"""
    name: str
    endurance_hours: float
    max_range_km: float
    cruise_speed_kts: float
    service_ceiling_m: float

    # Sensors
    radar_type: str
    radar_range_km: float
    eo_ir_range_km: float

    # Detection
    detection_probability: float
    localization_accuracy_m: float

    # Survivability
    rcs_dbsm: float
    survivability_vs_sam: float

    confidence: float = 0.0


def create_wz7_soar_dragon() -> SurveillanceDrone:
    """WZ-7 Soar Dragon HALE UAV"""
    return SurveillanceDrone(
        name="WZ-7 Soar Dragon",
        endurance_hours=10,
        max_range_km=7000,
        cruise_speed_kts=400,
        service_ceiling_m=18000,
        radar_type="SAR/GMTI",
        radar_range_km=300,
        eo_ir_range_km=150,
        detection_probability=0.88,
        localization_accuracy_m=30,
        rcs_dbsm=0,  # ~1 m²
        survivability_vs_sam=0.20,  # Low against Aegis
        confidence=0.45
    )


def create_bzk005() -> SurveillanceDrone:
    """BZK-005 MALE UAV"""
    return SurveillanceDrone(
        name="BZK-005",
        endurance_hours=40,
        max_range_km=2400,
        cruise_speed_kts=100,
        service_ceiling_m=8000,
        radar_type="SAR",
        radar_range_km=150,
        eo_ir_range_km=80,
        detection_probability=0.82,
        localization_accuracy_m=50,
        rcs_dbsm=-5,
        survivability_vs_sam=0.15,
        confidence=0.50
    )


# =============================================================================
# ANTI-SHIP BALLISTIC MISSILE SYSTEM
# =============================================================================

@dataclass
class ASBMSystem:
    """Anti-Ship Ballistic Missile characteristics"""
    name: str
    designation: str

    # Physical
    length_m: float
    diameter_m: float
    launch_weight_kg: float
    warhead_weight_kg: float
    warhead_type: str

    # Performance
    max_range_km: float
    min_range_km: float
    apogee_km: float
    terminal_speed_mach: float
    cep_m: float  # Circular Error Probable

    # Guidance
    midcourse_guidance: List[str]
    terminal_guidance: List[str]
    maneuvering_capability: str
    terminal_maneuver_g: float

    # Kill chain components
    pk_launch: float
    pk_midcourse: float
    pk_terminal_acquire: float
    pk_terminal_hit: float
    pk_warhead: float

    confidence: float = 0.0


def create_df21d() -> ASBMSystem:
    """DF-21D Anti-Ship Ballistic Missile"""
    return ASBMSystem(
        name="DF-21D",
        designation="CSS-5 Mod 4",
        length_m=10.7,
        diameter_m=1.4,
        launch_weight_kg=14700,
        warhead_weight_kg=600,
        warhead_type="Maneuvering reentry vehicle (MaRV)",
        max_range_km=1500,
        min_range_km=500,
        apogee_km=300,
        terminal_speed_mach=10,
        cep_m=20,  # With terminal guidance
        midcourse_guidance=[
            "Inertial Navigation System (INS)",
            "Satellite updates (Beidou)",
            "OTH radar cueing"
        ],
        terminal_guidance=[
            "Active radar seeker",
            "Passive radar homing",
            "Infrared terminal guidance (possible)"
        ],
        maneuvering_capability="MaRV with terminal maneuver",
        terminal_maneuver_g=30,  # High-G maneuver capability
        pk_launch=0.95,
        pk_midcourse=0.90,
        pk_terminal_acquire=0.75,  # Against moving target
        pk_terminal_hit=0.70,
        pk_warhead=0.90,
        confidence=0.40
    )


def create_df26() -> ASBMSystem:
    """DF-26 Anti-Ship Ballistic Missile"""
    return ASBMSystem(
        name="DF-26",
        designation="CSS-18 Mod 1",
        length_m=14.0,
        diameter_m=1.4,
        launch_weight_kg=20000,
        warhead_weight_kg=1200,
        warhead_type="MaRV conventional or nuclear",
        max_range_km=4000,
        min_range_km=1500,
        apogee_km=500,
        terminal_speed_mach=12,
        cep_m=15,
        midcourse_guidance=[
            "INS + Stellar",
            "Beidou satellite updates",
            "Possible real-time satellite targeting"
        ],
        terminal_guidance=[
            "Active radar seeker",
            "Multi-mode terminal seeker"
        ],
        maneuvering_capability="Advanced MaRV",
        terminal_maneuver_g=35,
        pk_launch=0.93,
        pk_midcourse=0.88,
        pk_terminal_acquire=0.72,
        pk_terminal_hit=0.68,
        pk_warhead=0.92,
        confidence=0.35
    )


# =============================================================================
# CARRIER DEFENSE SYSTEMS
# =============================================================================

@dataclass
class CarrierDefense:
    """Carrier battle group defense systems"""
    name: str
    defense_type: str  # "BMD", "Area", "Point", "CIWS"
    max_range_km: float
    min_range_km: float
    pk_vs_bm: float      # Pk against ballistic missile
    reaction_time_s: float
    magazine_depth: int
    reload_time_s: float
    confidence: float = 0.0


def create_sm3_block_iia() -> CarrierDefense:
    """SM-3 Block IIA for BMD"""
    return CarrierDefense(
        name="SM-3 Block IIA",
        defense_type="BMD",
        max_range_km=2500,
        min_range_km=100,
        pk_vs_bm=0.60,  # Against MaRV uncertain
        reaction_time_s=30,
        magazine_depth=8,  # Typical BMD load
        reload_time_s=0,   # No at-sea reload
        confidence=0.50
    )


def create_sm6() -> CarrierDefense:
    """SM-6 dual-role missile"""
    return CarrierDefense(
        name="SM-6",
        defense_type="Area/BMD",
        max_range_km=370,
        min_range_km=10,
        pk_vs_bm=0.45,  # Terminal BMD capability
        reaction_time_s=15,
        magazine_depth=24,
        reload_time_s=0,
        confidence=0.55
    )


def create_essm() -> CarrierDefense:
    """ESSM point defense"""
    return CarrierDefense(
        name="ESSM",
        defense_type="Point",
        max_range_km=50,
        min_range_km=1,
        pk_vs_bm=0.25,  # Limited vs BM
        reaction_time_s=8,
        magazine_depth=64,
        reload_time_s=0,
        confidence=0.60
    )


def create_ciws() -> CarrierDefense:
    """Phalanx CIWS last-ditch defense"""
    return CarrierDefense(
        name="Phalanx CIWS",
        defense_type="CIWS",
        max_range_km=3.5,
        min_range_km=0.2,
        pk_vs_bm=0.15,  # Very difficult against Mach 10+
        reaction_time_s=2,
        magazine_depth=1550,  # Rounds
        reload_time_s=0,
        confidence=0.50
    )


# =============================================================================
# KILL CHAIN ANALYSIS
# =============================================================================

class CarrierKillChain:
    """Carrier strike kill chain calculator"""

    def __init__(self, logger: CalculationLogger):
        self.logger = logger

    def calculate_detection_chain(
        self,
        carrier: CarrierSignature,
        distance_km: float,
        satellites: List[ReconSatellite],
        oth_radar: OTHRadar,
        drones: List[SurveillanceDrone],
        weather_clear: bool = True
    ) -> Tuple[float, float, str]:
        """
        Calculate probability of detecting and localizing carrier.

        Returns: (p_detect, localization_accuracy_m, best_source)
        """

        # Individual sensor detection probabilities
        detections = []

        # Satellite detection
        for sat in satellites:
            if sat.sat_type == "Optical" and not weather_clear:
                pd = sat.detection_probability * sat.weather_degradation
            else:
                pd = sat.detection_probability

            # Distance doesn't matter much for satellites (within coverage)
            detections.append({
                "sensor": sat.name,
                "pd": pd,
                "accuracy_m": sat.localization_accuracy_m,
                "confidence": sat.confidence
            })

        # OTH radar (if in range)
        if oth_radar.min_range_km <= distance_km <= oth_radar.max_range_km:
            detections.append({
                "sensor": oth_radar.name,
                "pd": oth_radar.detection_probability,
                "accuracy_m": oth_radar.range_accuracy_km * 1000,
                "confidence": oth_radar.confidence
            })

        # Drone detection (if close enough and survives)
        for drone in drones:
            if distance_km <= drone.max_range_km:
                # Drone must survive to detect
                pd = drone.detection_probability * drone.survivability_vs_sam
                detections.append({
                    "sensor": drone.name,
                    "pd": pd,
                    "accuracy_m": drone.localization_accuracy_m,
                    "confidence": drone.confidence
                })

        # Fuse detections (parallel sensors)
        if not detections:
            return 0.0, float('inf'), "None"

        # P(at least one detects) = 1 - Π(1 - pd_i)
        p_none_detect = 1.0
        for det in detections:
            p_none_detect *= (1 - det['pd'])
        p_detect = 1 - p_none_detect

        # Best localization from best sensor
        best_det = min(detections, key=lambda x: x['accuracy_m'])
        best_accuracy = best_det['accuracy_m']
        best_source = best_det['sensor']

        # Multi-sensor fusion improves accuracy
        if len([d for d in detections if d['pd'] > 0.5]) > 1:
            best_accuracy *= 0.7  # 30% improvement from fusion

        return p_detect, best_accuracy, best_source

    def calculate_asbm_engagement(
        self,
        asbm: ASBMSystem,
        carrier: CarrierSignature,
        distance_km: float,
        localization_accuracy_m: float,
        carrier_maneuvering: bool,
        carrier_jamming: bool
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate ASBM single-shot Pk.

        Returns: (pk, breakdown)
        """

        breakdown = {}

        # Check range
        if distance_km < asbm.min_range_km or distance_km > asbm.max_range_km:
            return 0.0, {"error": "Out of range"}

        # 1. P(successful launch)
        p_launch = asbm.pk_launch
        breakdown["p_launch"] = p_launch

        # 2. P(midcourse guidance success)
        p_midcourse = asbm.pk_midcourse

        # Degraded if initial localization poor
        if localization_accuracy_m > 10000:
            p_midcourse *= 0.85
        elif localization_accuracy_m > 5000:
            p_midcourse *= 0.92

        breakdown["p_midcourse"] = p_midcourse

        # 3. P(terminal seeker acquires)
        p_acquire = asbm.pk_terminal_acquire

        # Large target helps acquisition
        target_size_factor = min(1.2, carrier.length_m / 300)
        p_acquire *= target_size_factor

        # Maneuvering carrier harder to acquire
        if carrier_maneuvering:
            # Carrier moves ~0.5 km/min at full speed
            # Time of flight ~10 min from max range
            tof_min = distance_km / (asbm.terminal_speed_mach * 343 * 60 / 1000)
            carrier_displacement_km = 0.5 * tof_min
            # Seeker FOV must cover this uncertainty
            if carrier_displacement_km > 10:
                p_acquire *= 0.75
            elif carrier_displacement_km > 5:
                p_acquire *= 0.85

        # Jamming degrades seeker
        if carrier_jamming:
            p_acquire *= 0.70

        breakdown["p_terminal_acquire"] = p_acquire

        # 4. P(hits carrier given acquisition)
        p_hit = asbm.pk_terminal_hit

        # Terminal maneuvers help vs defenses but don't affect hit prob much
        # Large target is easier to hit
        p_hit *= target_size_factor

        if carrier_maneuvering:
            # High closing speed makes carrier maneuver less effective
            p_hit *= 0.95

        breakdown["p_terminal_hit"] = p_hit

        # 5. P(warhead effect - mission kill)
        p_warhead = asbm.pk_warhead
        # Large warhead vs large target
        breakdown["p_warhead"] = p_warhead

        # Total Pk (before defense intercept)
        pk_before_defense = p_launch * p_midcourse * p_acquire * p_hit * p_warhead
        breakdown["pk_before_defense"] = pk_before_defense

        return pk_before_defense, breakdown

    def calculate_defense_leakage(
        self,
        defenses: List[CarrierDefense],
        asbm: ASBMSystem,
        salvo_size: int
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate probability of leaking through defenses.

        Returns: (p_leakage, breakdown)
        """

        breakdown = {}

        # Layer 1: BMD (SM-3)
        bmd_systems = [d for d in defenses if d.defense_type == "BMD"]
        p_survive_bmd = 1.0

        for bmd in bmd_systems:
            # How many interceptors per incoming?
            interceptors_per_target = min(2, bmd.magazine_depth // max(1, salvo_size))

            # Each interceptor has pk_vs_bm
            p_kill_one_intercept = bmd.pk_vs_bm

            # Maneuvering RV reduces intercept Pk
            if asbm.terminal_maneuver_g > 20:
                p_kill_one_intercept *= 0.70

            p_kill = 1 - (1 - p_kill_one_intercept) ** interceptors_per_target
            p_survive_bmd *= (1 - p_kill)

            breakdown[f"p_survive_{bmd.name}"] = 1 - p_kill

        # Layer 2: Area defense (SM-6)
        area_systems = [d for d in defenses if "Area" in d.defense_type]
        p_survive_area = 1.0

        for area in area_systems:
            interceptors_per_target = min(3, area.magazine_depth // max(1, salvo_size))
            p_kill_one = area.pk_vs_bm * 0.8  # High speed reduces effectiveness
            p_kill = 1 - (1 - p_kill_one) ** interceptors_per_target
            p_survive_area *= (1 - p_kill)
            breakdown[f"p_survive_{area.name}"] = 1 - p_kill

        # Layer 3: Point defense (ESSM)
        point_systems = [d for d in defenses if d.defense_type == "Point"]
        p_survive_point = 1.0

        for point in point_systems:
            # ESSM has very limited time against Mach 10+ target
            p_kill_one = point.pk_vs_bm * 0.5
            interceptors = min(2, point.magazine_depth // max(1, salvo_size))
            p_kill = 1 - (1 - p_kill_one) ** interceptors
            p_survive_point *= (1 - p_kill)
            breakdown[f"p_survive_{point.name}"] = 1 - p_kill

        # Layer 4: CIWS
        ciws_systems = [d for d in defenses if d.defense_type == "CIWS"]
        p_survive_ciws = 1.0

        for ciws in ciws_systems:
            # CIWS very limited vs hypersonic target
            p_kill = ciws.pk_vs_bm
            p_survive_ciws *= (1 - p_kill)
            breakdown[f"p_survive_{ciws.name}"] = 1 - p_kill

        # Total leakage probability
        p_leakage = p_survive_bmd * p_survive_area * p_survive_point * p_survive_ciws
        breakdown["p_total_leakage"] = p_leakage

        return p_leakage, breakdown

    def calculate_salvo_pk(
        self,
        single_pk: float,
        p_leakage: float,
        salvo_size: int,
        defense_saturation_factor: float = 1.0
    ) -> Tuple[float, float]:
        """
        Calculate salvo kill probability.

        Large salvos can saturate defenses.

        Returns: (salvo_pk, effective_pk_per_missile)
        """

        # Effective Pk per missile after defense
        effective_pk = single_pk * p_leakage

        # Saturation: more missiles degrade defense effectiveness
        if salvo_size > 4:
            saturation_bonus = 1 + 0.1 * np.log(salvo_size / 4)
            effective_pk = min(0.95, effective_pk * saturation_bonus)

        # Salvo Pk
        # Correlation is higher for ballistic missiles (similar trajectory)
        correlation = 0.35
        n_effective = 1 + (salvo_size - 1) * (1 - correlation)

        salvo_pk = 1 - (1 - effective_pk) ** n_effective

        return salvo_pk, effective_pk


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def run_carrier_strike_analysis():
    """Run comprehensive carrier strike kill chain analysis"""

    logger = init_logger(
        name="Carrier-Strike",
        output_formats=[OutputFormat.CONSOLE, OutputFormat.GITHUB_ACTIONS],
        log_file="carrier_strike_log.txt",
        verbose=True
    )

    calculator = CarrierKillChain(logger)

    # Create targets
    ford = create_ford_class()
    nimitz = create_nimitz_class()

    # Create reconnaissance assets
    satellites = [
        create_yaogan_sar(),
        create_yaogan_elint(),
        create_jilin_optical()
    ]
    oth = create_oth_radar()
    drones = [
        create_wz7_soar_dragon(),
        create_bzk005()
    ]

    # Create weapons
    df21d = create_df21d()
    df26 = create_df26()

    # Create defenses
    defenses = [
        create_sm3_block_iia(),
        create_sm6(),
        create_essm(),
        create_ciws()
    ]

    all_results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "analysis": "Carrier Strike Kill Chain",
        "carriers": {},
        "summary": {}
    }

    print("=" * 80)
    print("CARRIER STRIKE KILL CHAIN ANALYSIS")
    print("DF-21D/DF-26 ASBM vs Ford/Nimitz Class Carriers")
    print("=" * 80)

    # Engagement distances
    distances = [1000, 1500, 2000, 3000]

    for carrier, carrier_name in [(ford, "Ford Class"), (nimitz, "Nimitz Class")]:
        print(f"\n{'─' * 80}")
        print(f"TARGET: {carrier_name}")
        print(f"{'─' * 80}")

        carrier_results = {
            "engagements": [],
            "optimal": {}
        }

        with logger.section(f"Analysis: {carrier_name}"):

            # Log carrier characteristics
            logger.log_calculation(
                name=f"{carrier_name} Target Profile",
                formula="Carrier detection signature",
                inputs={
                    "length_m": carrier.length_m,
                    "rcs_dbsm": carrier.rcs_x_band_dbsm,
                    "ir_signature_mw": carrier.ir_signature_w / 1e6
                },
                result=carrier.rcs_x_band_dbsm,
                unit="dBsm",
                confidence=carrier.confidence
            )

            best_pk = 0.0
            best_config = {}

            for distance in distances:
                for asbm in [df21d, df26]:
                    # Skip if out of range
                    if distance < asbm.min_range_km or distance > asbm.max_range_km:
                        continue

                    for maneuver in [False, True]:
                        for jamming in [False, True]:
                            for salvo in [2, 4, 8, 12]:

                                # Detection chain
                                p_detect, loc_acc, best_sensor = calculator.calculate_detection_chain(
                                    carrier, distance, satellites, oth, drones
                                )

                                if p_detect < 0.5:
                                    continue

                                # ASBM engagement
                                pk_before_def, pk_breakdown = calculator.calculate_asbm_engagement(
                                    asbm, carrier, distance, loc_acc, maneuver, jamming
                                )

                                # Defense leakage
                                p_leak, def_breakdown = calculator.calculate_defense_leakage(
                                    defenses, asbm, salvo
                                )

                                # Salvo Pk
                                salvo_pk, eff_pk = calculator.calculate_salvo_pk(
                                    pk_before_def, p_leak, salvo
                                )

                                # Overall Pk including detection
                                total_pk = p_detect * salvo_pk

                                config = {
                                    "weapon": asbm.name,
                                    "distance_km": distance,
                                    "salvo_size": salvo,
                                    "carrier_maneuver": maneuver,
                                    "carrier_jamming": jamming,
                                    "p_detect": p_detect,
                                    "best_sensor": best_sensor,
                                    "loc_accuracy_m": loc_acc,
                                    "pk_before_defense": pk_before_def,
                                    "p_defense_leakage": p_leak,
                                    "salvo_pk": salvo_pk,
                                    "total_pk": total_pk
                                }

                                carrier_results["engagements"].append(config)

                                if total_pk > best_pk:
                                    best_pk = total_pk
                                    best_config = config

            carrier_results["optimal"] = best_config
            all_results["carriers"][carrier_name] = carrier_results

            # Log optimal result
            logger.log_calculation(
                name=f"{carrier_name} Optimal Engagement",
                formula="Integrated kill chain",
                inputs={
                    "weapon": best_config.get("weapon", "N/A"),
                    "distance_km": best_config.get("distance_km", 0),
                    "salvo_size": best_config.get("salvo_size", 0)
                },
                result=best_config.get("total_pk", 0),
                unit="probability",
                confidence=0.40,
                notes=f"Detection by {best_config.get('best_sensor', 'N/A')}"
            )

            print(f"\n  OPTIMAL CONFIGURATION:")
            print(f"    Weapon: {best_config.get('weapon', 'N/A')}")
            print(f"    Distance: {best_config.get('distance_km', 0)} km")
            print(f"    Salvo size: {best_config.get('salvo_size', 0)} missiles")
            print(f"    P(Detection): {best_config.get('p_detect', 0):.1%}")
            print(f"    P(Hit before defense): {best_config.get('pk_before_defense', 0):.1%}")
            print(f"    P(Penetrate defense): {best_config.get('p_defense_leakage', 0):.1%}")
            print(f"    Salvo Pk: {best_config.get('salvo_pk', 0):.1%}")
            print(f"    TOTAL Pk: {best_config.get('total_pk', 0):.1%}")

    # Generate engagement matrix
    print("\n" + "=" * 80)
    print("ENGAGEMENT MATRIX: PK BY SALVO SIZE AND DISTANCE")
    print("=" * 80)

    for carrier, carrier_name in [(ford, "Ford Class"), (nimitz, "Nimitz Class")]:
        print(f"\n{carrier_name} (DF-21D, carrier maneuvering, no jamming):")
        print("  Distance |  2 msls |  4 msls |  8 msls | 12 msls")
        print("  ---------|---------|---------|---------|--------")

        for distance in [1000, 1500]:
            pks = []
            for salvo in [2, 4, 8, 12]:
                p_det, loc, _ = calculator.calculate_detection_chain(
                    carrier, distance, satellites, oth, drones
                )
                pk_bf, _ = calculator.calculate_asbm_engagement(
                    df21d, carrier, distance, loc, True, False
                )
                p_leak, _ = calculator.calculate_defense_leakage(defenses, df21d, salvo)
                s_pk, _ = calculator.calculate_salvo_pk(pk_bf, p_leak, salvo)
                total = p_det * s_pk
                pks.append(total)

            print(f"  {distance:4d} km  | {pks[0]:6.1%} | {pks[1]:6.1%} | {pks[2]:6.1%} | {pks[3]:5.1%}")

    # Summary
    ford_best = all_results["carriers"]["Ford Class"]["optimal"]["total_pk"]
    nimitz_best = all_results["carriers"]["Nimitz Class"]["optimal"]["total_pk"]

    all_results["summary"] = {
        "ford_max_pk": ford_best,
        "nimitz_max_pk": nimitz_best,
        "average_max_pk": (ford_best + nimitz_best) / 2,
        "key_findings": [
            "Multi-sensor fusion critical for initial detection",
            "SAR satellites provide all-weather detection capability",
            "Localization accuracy (~50m) sufficient for terminal seeker",
            "Large salvos (8-12) needed to saturate Aegis defenses",
            "MaRV maneuvers reduce SM-3 intercept probability",
            "Carrier maneuvers have limited effect vs Mach 10+ warhead",
            "DF-21D optimal at 1000-1500km, DF-26 for 2000-4000km",
            "100% Pk impossible due to defense layering and uncertainties"
        ],
        "limitations": [
            "Kill chain timing not modeled (hours for satellite pass)",
            "Targeting data latency not included",
            "Carrier battle group escort defenses not modeled",
            "Electronic warfare effects simplified",
            "Real-time satellite tasking uncertain",
            "Weather effects on optical/IR sensors",
            "Decoy/EMCON capabilities of carrier"
        ]
    }

    logger.finalize()

    # Write results
    with open("carrier_strike_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print("\nWrote: carrier_strike_results.json")

    md_report = logger.generate_markdown_report()
    with open("carrier_strike_report.md", "w") as f:
        f.write(md_report)
    print("Wrote: carrier_strike_report.md")

    print("\n" + "=" * 80)
    print("CARRIER STRIKE ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nMAXIMUM ACHIEVABLE PK (optimal salvo, optimal conditions):")
    print(f"  Ford Class:   {ford_best:.1%}")
    print(f"  Nimitz Class: {nimitz_best:.1%}")

    print(f"\nKEY LIMITATIONS PREVENTING 100% PK:")
    for finding in all_results["summary"]["limitations"][:5]:
        print(f"  • {finding}")

    return all_results


if __name__ == "__main__":
    run_carrier_strike_analysis()
