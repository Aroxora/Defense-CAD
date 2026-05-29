#!/usr/bin/env python3
"""
F-35 Integrated Kill Chain Analysis

Maximizes kill probability against F-35A/B/C variants using:
- KJ-500/KJ-2000 AWACS detection and cueing
- J-20 Type 1475/1476 AESA radar
- J-20 EW/ESM suite for passive detection
- PL-15 long-range AAM with active radar seeker
- Ground-based radar network (YLC-8E, JY-27A)
- Bi-static/multi-static radar exploitation

Analysis includes:
- Aspect-dependent RCS modeling for each F-35 variant
- Sensor fusion algorithms
- Kill chain optimization
- Uncertainty quantification

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
# F-35 VARIANT CHARACTERISTICS
# =============================================================================

class F35Variant(Enum):
    """F-35 variants with different characteristics"""
    F35A = "F-35A"  # CTOL - Conventional
    F35B = "F-35B"  # STOVL - Lift fan
    F35C = "F-35C"  # CV - Carrier variant


@dataclass
class F35Signature:
    """
    F-35 radar and IR signature model by aspect angle.

    RCS varies significantly with aspect angle and frequency.
    Stealth optimization is primarily frontal aspect.

    Sources: Open literature, academic papers, defense analysis
    All values are ESTIMATES with documented uncertainty.
    """
    variant: F35Variant

    # RCS by aspect angle (dBsm) - X-band (8-12 GHz)
    # Format: {azimuth_deg: rcs_dbsm}
    rcs_x_band: Dict[int, float] = field(default_factory=dict)

    # RCS at different frequencies
    rcs_vhf: float = 0.0      # VHF band (30-300 MHz) - much higher
    rcs_uhf: float = 0.0      # UHF band (300-1000 MHz)
    rcs_l_band: float = 0.0   # L-band (1-2 GHz)
    rcs_s_band: float = 0.0   # S-band (2-4 GHz)

    # IR signature
    ir_front: float = 0.0     # W/sr frontal
    ir_rear: float = 0.0      # W/sr rear (exhaust)

    # Physical characteristics affecting detection
    wingspan_m: float = 0.0
    length_m: float = 0.0

    # Operational limits
    max_speed_mach: float = 0.0
    combat_radius_km: float = 0.0

    # EW capabilities
    ew_suite: str = ""

    # Confidence in estimates
    rcs_confidence: float = 0.0


def create_f35a_signature() -> F35Signature:
    """F-35A CTOL - Air Force variant"""
    sig = F35Signature(variant=F35Variant.F35A)

    # X-band RCS by aspect (estimates from open sources)
    # Frontal optimization, sides/rear less stealthy
    sig.rcs_x_band = {
        0: -40,      # Nose-on (best case, design point)
        15: -35,
        30: -28,
        45: -20,     # Quarter aspect - significantly higher
        60: -15,
        90: -10,     # Broadside - much higher RCS
        120: -12,
        135: -15,
        150: -18,
        180: -25     # Tail-on (nozzle treatment)
    }

    # Lower frequency bands - stealth less effective
    sig.rcs_vhf = 1.0       # ~1 m² at VHF (resonance effects)
    sig.rcs_uhf = -5.0      # dBsm
    sig.rcs_l_band = -15.0  # dBsm
    sig.rcs_s_band = -25.0  # dBsm

    # IR signature
    sig.ir_front = 50       # W/sr (low due to buried engine)
    sig.ir_rear = 800       # W/sr (significant from exhaust)

    # Physical
    sig.wingspan_m = 10.7
    sig.length_m = 15.7
    sig.max_speed_mach = 1.6
    sig.combat_radius_km = 1093

    sig.ew_suite = "AN/ASQ-239 EW Suite"
    sig.rcs_confidence = 0.45  # High uncertainty

    return sig


def create_f35b_signature() -> F35Signature:
    """F-35B STOVL - Marine Corps variant"""
    sig = F35Signature(variant=F35Variant.F35B)

    # Lift fan door affects RCS
    # Generally similar to A but with some compromises
    sig.rcs_x_band = {
        0: -38,      # Slightly higher due to lift fan door
        15: -33,
        30: -26,
        45: -18,     # Lift fan doors visible
        60: -12,
        90: -8,      # Higher broadside due to doors
        120: -10,
        135: -14,
        150: -17,
        180: -22     # Different nozzle configuration
    }

    sig.rcs_vhf = 2.0       # Larger due to lift fan structure
    sig.rcs_uhf = -3.0
    sig.rcs_l_band = -12.0
    sig.rcs_s_band = -22.0

    sig.ir_front = 60       # Slightly higher (lift fan)
    sig.ir_rear = 900       # Higher exhaust signature

    sig.wingspan_m = 10.7
    sig.length_m = 15.6
    sig.max_speed_mach = 1.6
    sig.combat_radius_km = 935  # Shorter range

    sig.ew_suite = "AN/ASQ-239 EW Suite"
    sig.rcs_confidence = 0.40

    return sig


def create_f35c_signature() -> F35Signature:
    """F-35C CV - Navy carrier variant"""
    sig = F35Signature(variant=F35Variant.F35C)

    # Larger wings for carrier ops
    # Wing fold mechanism affects signature
    sig.rcs_x_band = {
        0: -40,      # Similar frontal to A
        15: -34,
        30: -25,
        45: -17,     # Larger wing area visible
        60: -12,
        90: -8,      # Larger broadside (bigger wings)
        120: -10,
        135: -13,
        150: -16,
        180: -23
    }

    sig.rcs_vhf = 1.5       # Larger wing resonance
    sig.rcs_uhf = -4.0
    sig.rcs_l_band = -13.0
    sig.rcs_s_band = -23.0

    sig.ir_front = 55
    sig.ir_rear = 850

    sig.wingspan_m = 13.1   # Larger wingspan for carrier ops
    sig.length_m = 15.7
    sig.max_speed_mach = 1.6
    sig.combat_radius_km = 1130  # Longest range

    sig.ew_suite = "AN/ASQ-239 EW Suite"
    sig.rcs_confidence = 0.42

    return sig


# =============================================================================
# CHINESE SENSOR SYSTEMS
# =============================================================================

@dataclass
class AWACSSystem:
    """Airborne Warning and Control System"""
    name: str
    radar_type: str
    frequency_band: str
    detection_range_km: Dict[float, float]  # RCS (m²) -> range (km)
    track_capacity: int
    altitude_m: float
    endurance_hours: float
    datalink_range_km: float

    # Detection probabilities
    pd_clear: float = 0.0      # P(detect) clear weather
    pd_jamming: float = 0.0    # P(detect) under jamming

    # Track accuracy
    range_accuracy_m: float = 0.0
    azimuth_accuracy_deg: float = 0.0

    confidence: float = 0.0


def create_kj500() -> AWACSSystem:
    """KJ-500 - Primary PLAAF AWACS"""
    return AWACSSystem(
        name="KJ-500",
        radar_type="AESA (3-sided rotating array)",
        frequency_band="S-band (2-4 GHz)",
        detection_range_km={
            1.0: 470,    # 1 m² target
            0.1: 280,    # 0.1 m² target
            0.01: 165,   # 0.01 m² target (stealth)
            0.001: 95,   # 0.001 m² target (very low RCS)
        },
        track_capacity=60,
        altitude_m=10000,
        endurance_hours=8,
        datalink_range_km=400,
        pd_clear=0.85,
        pd_jamming=0.55,
        range_accuracy_m=500,
        azimuth_accuracy_deg=0.5,
        confidence=0.50
    )


def create_kj2000() -> AWACSSystem:
    """KJ-2000 - Large AWACS on IL-76 platform"""
    return AWACSSystem(
        name="KJ-2000",
        radar_type="AESA (fixed array, 360° coverage)",
        frequency_band="L/S-band",
        detection_range_km={
            1.0: 520,
            0.1: 310,
            0.01: 185,
            0.001: 105,
        },
        track_capacity=100,
        altitude_m=11000,
        endurance_hours=10,
        datalink_range_km=450,
        pd_clear=0.88,
        pd_jamming=0.52,
        range_accuracy_m=400,
        azimuth_accuracy_deg=0.4,
        confidence=0.48
    )


@dataclass
class FighterRadar:
    """Fighter aircraft radar system"""
    name: str
    platform: str
    radar_type: str
    frequency_band: str
    aperture_size_m: float

    # Detection ranges
    detection_range_km: Dict[float, float]  # RCS -> range
    track_while_scan: int
    simultaneous_engage: int

    # Track accuracy
    range_accuracy_m: float
    angle_accuracy_deg: float

    # Low probability of intercept features
    lpi_capability: bool
    frequency_agility: bool

    confidence: float = 0.0


def create_j20_radar() -> FighterRadar:
    """J-20 Type 1475 AESA Radar"""
    return FighterRadar(
        name="Type 1475 AESA",
        platform="J-20",
        radar_type="Active Electronically Scanned Array",
        frequency_band="X-band",
        aperture_size_m=0.9,  # Estimated large aperture
        detection_range_km={
            1.0: 280,
            0.1: 155,
            0.01: 85,      # Against stealth at X-band
            0.001: 48,
            0.0001: 27,    # Against F-35 frontal
        },
        track_while_scan=20,
        simultaneous_engage=6,
        range_accuracy_m=50,
        angle_accuracy_deg=0.3,
        lpi_capability=True,
        frequency_agility=True,
        confidence=0.45
    )


@dataclass
class EWSystem:
    """Electronic Warfare System"""
    name: str
    platform: str

    # ESM (Electronic Support Measures)
    esm_frequency_range: Tuple[float, float]  # GHz
    esm_sensitivity_dbm: float
    esm_detection_range_km: float
    esm_aoa_accuracy_deg: float

    # ECM (Electronic Countermeasures)
    ecm_power_w: float
    ecm_techniques: List[str]

    # ELINT
    emitter_identification: bool

    confidence: float = 0.0


def create_j20_ew() -> EWSystem:
    """J-20 Integrated EW Suite"""
    return EWSystem(
        name="J-20 Integrated EW Suite",
        platform="J-20",
        esm_frequency_range=(0.5, 40.0),
        esm_sensitivity_dbm=-65,
        esm_detection_range_km=450,  # Can detect emissions at long range
        esm_aoa_accuracy_deg=2.0,
        ecm_power_w=5000,
        ecm_techniques=[
            "Noise jamming",
            "Deceptive jamming",
            "Range gate pull-off",
            "Velocity gate pull-off",
            "Cross-eye jamming"
        ],
        emitter_identification=True,
        confidence=0.40
    )


@dataclass
class GroundRadar:
    """Ground-based radar system"""
    name: str
    radar_type: str
    frequency_band: str

    detection_range_km: Dict[float, float]
    altitude_coverage_m: Tuple[float, float]

    # Special capabilities
    anti_stealth: bool
    vhf_resonance: bool

    confidence: float = 0.0


def create_ylc8e() -> GroundRadar:
    """YLC-8E Anti-Stealth Radar"""
    return GroundRadar(
        name="YLC-8E",
        radar_type="UHF AESA",
        frequency_band="UHF (300-1000 MHz)",
        detection_range_km={
            1.0: 550,
            0.1: 380,
            0.01: 260,    # Can detect stealth at UHF
            0.001: 175,
        },
        altitude_coverage_m=(500, 30000),
        anti_stealth=True,
        vhf_resonance=False,
        confidence=0.50
    )


def create_jy27a() -> GroundRadar:
    """JY-27A VHF Anti-Stealth Radar"""
    return GroundRadar(
        name="JY-27A",
        radar_type="VHF AESA",
        frequency_band="VHF (30-300 MHz)",
        detection_range_km={
            1.0: 500,
            0.1: 420,     # VHF effectiveness against stealth
            0.01: 350,    # Much better than X-band
            0.001: 280,   # Resonance region
        },
        altitude_coverage_m=(1000, 25000),
        anti_stealth=True,
        vhf_resonance=True,  # Exploits resonance at VHF
        confidence=0.55
    )


# =============================================================================
# PL-15 MISSILE SYSTEM
# =============================================================================

@dataclass
class PL15Missile:
    """PL-15 Long-Range Air-to-Air Missile"""
    name: str = "PL-15"

    # Physical
    length_m: float = 4.0
    diameter_m: float = 0.203
    weight_kg: float = 210

    # Performance
    max_range_km: float = 200      # Estimated maximum
    effective_range_km: float = 150  # Against maneuvering target
    min_range_km: float = 5
    max_speed_mach: float = 4.5

    # Seeker
    seeker_type: str = "Active Radar (AESA)"
    seeker_range_km: float = 25    # Autonomous terminal guidance
    seeker_fov_deg: float = 60
    seeker_frequency: str = "X/Ku-band"

    # Guidance
    midcourse_guidance: str = "INS + Datalink update"
    terminal_guidance: str = "Active radar homing"
    datalink_capability: bool = True
    home_on_jam: bool = True

    # Warhead
    warhead_kg: float = 25
    warhead_type: str = "HE fragmentation"
    fuze_type: str = "Proximity/impact"

    # Kill probability components
    pk_seeker_lock: float = 0.85    # P(seeker acquires)
    pk_guidance: float = 0.80       # P(guidance success)
    pk_fuze: float = 0.90           # P(fuze functions)
    pk_warhead: float = 0.85        # P(warhead kills given hit)

    confidence: float = 0.45


# =============================================================================
# SENSOR FUSION AND DETECTION
# =============================================================================

@dataclass
class DetectionResult:
    """Result of sensor detection attempt"""
    sensor_name: str
    target_variant: F35Variant
    detected: bool
    detection_range_km: float
    track_quality: float  # 0-1
    position_error_m: float
    velocity_error_mps: float
    confidence: float


class SensorFusion:
    """Multi-sensor fusion for detection and tracking"""

    def __init__(self, logger: CalculationLogger):
        self.logger = logger

    def calculate_detection_range(
        self,
        sensor_ranges: Dict[float, float],  # RCS -> range
        target_rcs_dbsm: float,
        frequency_band: str
    ) -> float:
        """Calculate detection range for given RCS"""

        # Convert dBsm to m²
        rcs_m2 = 10 ** (target_rcs_dbsm / 10)

        # Interpolate detection range
        rcs_values = sorted(sensor_ranges.keys())

        if rcs_m2 >= max(rcs_values):
            return max(sensor_ranges.values())
        if rcs_m2 <= min(rcs_values):
            # Extrapolate using radar equation (R^4 proportional to RCS)
            min_rcs = min(rcs_values)
            min_range = sensor_ranges[min_rcs]
            return min_range * (rcs_m2 / min_rcs) ** 0.25

        # Linear interpolation in log space
        for i in range(len(rcs_values) - 1):
            if rcs_values[i] <= rcs_m2 <= rcs_values[i + 1]:
                r1, r2 = sensor_ranges[rcs_values[i]], sensor_ranges[rcs_values[i + 1]]
                rcs1, rcs2 = rcs_values[i], rcs_values[i + 1]

                # Log interpolation
                log_ratio = np.log10(rcs_m2 / rcs1) / np.log10(rcs2 / rcs1)
                return r1 + (r2 - r1) * log_ratio

        return 0.0

    def detect_target(
        self,
        awacs: AWACSSystem,
        target: F35Signature,
        aspect_deg: float,
        range_km: float
    ) -> DetectionResult:
        """Attempt detection with AWACS"""

        # Get RCS at aspect angle
        aspect_rounded = min(target.rcs_x_band.keys(),
                            key=lambda x: abs(x - aspect_deg % 360))

        # AWACS typically uses S-band
        rcs_dbsm = target.rcs_s_band

        # Calculate detection range
        detection_range = self.calculate_detection_range(
            awacs.detection_range_km,
            rcs_dbsm,
            awacs.frequency_band
        )

        # Detection probability based on range
        range_ratio = range_km / detection_range if detection_range > 0 else float('inf')

        if range_ratio <= 1.0:
            pd = awacs.pd_clear * (1 - 0.3 * range_ratio ** 2)
        else:
            pd = awacs.pd_clear * np.exp(-2 * (range_ratio - 1) ** 2)

        detected = np.random.random() < pd

        return DetectionResult(
            sensor_name=awacs.name,
            target_variant=target.variant,
            detected=detected,
            detection_range_km=detection_range,
            track_quality=0.7 if detected else 0.0,
            position_error_m=awacs.range_accuracy_m if detected else float('inf'),
            velocity_error_mps=50 if detected else float('inf'),
            confidence=awacs.confidence
        )

    def detect_with_fighter_radar(
        self,
        radar: FighterRadar,
        target: F35Signature,
        aspect_deg: float,
        range_km: float
    ) -> DetectionResult:
        """Attempt detection with fighter radar"""

        # Fighter radar X-band - use aspect-dependent RCS
        aspect_rounded = min(target.rcs_x_band.keys(),
                            key=lambda x: abs(x - aspect_deg))
        rcs_dbsm = target.rcs_x_band[aspect_rounded]

        detection_range = self.calculate_detection_range(
            radar.detection_range_km,
            rcs_dbsm,
            radar.frequency_band
        )

        # Fighter radar typically higher Pd at short range
        range_ratio = range_km / detection_range if detection_range > 0 else float('inf')

        if range_ratio <= 1.0:
            pd = 0.90 * (1 - 0.2 * range_ratio ** 2)
        else:
            pd = 0.90 * np.exp(-3 * (range_ratio - 1) ** 2)

        detected = np.random.random() < pd

        return DetectionResult(
            sensor_name=radar.name,
            target_variant=target.variant,
            detected=detected,
            detection_range_km=detection_range,
            track_quality=0.85 if detected else 0.0,
            position_error_m=radar.range_accuracy_m if detected else float('inf'),
            velocity_error_mps=20 if detected else float('inf'),
            confidence=radar.confidence
        )

    def detect_with_ground_radar(
        self,
        radar: GroundRadar,
        target: F35Signature,
        range_km: float
    ) -> DetectionResult:
        """Attempt detection with ground-based anti-stealth radar"""

        # VHF/UHF radars exploit resonance - use appropriate RCS
        if "VHF" in radar.frequency_band:
            rcs_dbsm = 10 * np.log10(target.rcs_vhf)  # Convert m² to dBsm
        else:
            rcs_dbsm = target.rcs_uhf

        detection_range = self.calculate_detection_range(
            radar.detection_range_km,
            rcs_dbsm,
            radar.frequency_band
        )

        range_ratio = range_km / detection_range if detection_range > 0 else float('inf')

        # Ground radar Pd
        if range_ratio <= 1.0:
            pd = 0.88 * (1 - 0.25 * range_ratio ** 2)
        else:
            pd = 0.88 * np.exp(-2.5 * (range_ratio - 1) ** 2)

        detected = np.random.random() < pd

        return DetectionResult(
            sensor_name=radar.name,
            target_variant=target.variant,
            detected=detected,
            detection_range_km=detection_range,
            track_quality=0.65 if detected else 0.0,  # Lower accuracy at VHF
            position_error_m=1500 if detected else float('inf'),
            velocity_error_mps=80 if detected else float('inf'),
            confidence=radar.confidence
        )

    def passive_detection_esm(
        self,
        ew: EWSystem,
        target: F35Signature,
        target_emitting: bool,
        range_km: float
    ) -> DetectionResult:
        """Passive detection using ESM"""

        if not target_emitting:
            return DetectionResult(
                sensor_name=ew.name + " ESM",
                target_variant=target.variant,
                detected=False,
                detection_range_km=0,
                track_quality=0.0,
                position_error_m=float('inf'),
                velocity_error_mps=float('inf'),
                confidence=ew.confidence
            )

        # ESM detection range depends on target emissions
        detection_range = ew.esm_detection_range_km

        range_ratio = range_km / detection_range

        if range_ratio <= 1.0:
            pd = 0.92
        else:
            pd = 0.92 * np.exp(-2 * (range_ratio - 1) ** 2)

        detected = np.random.random() < pd

        return DetectionResult(
            sensor_name=ew.name + " ESM",
            target_variant=target.variant,
            detected=detected,
            detection_range_km=detection_range,
            track_quality=0.5 if detected else 0.0,  # Bearing only
            position_error_m=range_km * np.tan(np.radians(ew.esm_aoa_accuracy_deg)) * 1000 if detected else float('inf'),
            velocity_error_mps=float('inf'),  # No velocity from ESM
            confidence=ew.confidence
        )

    def fuse_detections(
        self,
        detections: List[DetectionResult]
    ) -> Tuple[bool, float, float]:
        """
        Fuse multiple sensor detections.

        Returns: (detected, track_quality, position_error_m)
        """

        # Filter to successful detections
        good_detections = [d for d in detections if d.detected]

        if not good_detections:
            return False, 0.0, float('inf')

        # Track quality improves with more sensors
        # Using weighted average based on individual quality
        total_quality = sum(d.track_quality * d.confidence for d in good_detections)
        total_weight = sum(d.confidence for d in good_detections)

        fused_quality = total_quality / total_weight if total_weight > 0 else 0

        # Multi-sensor improves quality (diminishing returns)
        n_sensors = len(good_detections)
        quality_bonus = 1 + 0.15 * np.log(n_sensors) if n_sensors > 1 else 1
        fused_quality = min(0.95, fused_quality * quality_bonus)

        # Position error reduces with fusion (inverse square combination)
        position_errors = [d.position_error_m for d in good_detections if d.position_error_m < float('inf')]
        if position_errors:
            inv_sq_sum = sum(1 / (e ** 2) for e in position_errors)
            fused_error = 1 / np.sqrt(inv_sq_sum)
        else:
            fused_error = float('inf')

        return True, fused_quality, fused_error


# =============================================================================
# KILL PROBABILITY CALCULATION
# =============================================================================

class KillChainCalculator:
    """Calculate kill probability for F-35 engagement"""

    def __init__(self, logger: CalculationLogger):
        self.logger = logger
        self.fusion = SensorFusion(logger)

    def calculate_engagement_pk(
        self,
        target: F35Signature,
        missile: PL15Missile,
        launch_range_km: float,
        awacs_cue: bool,
        datalink_active: bool,
        target_maneuvering: bool,
        target_jamming: bool,
        aspect_deg: float
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate single-shot Pk for engagement.

        Returns: (pk, breakdown)
        """

        breakdown = {}

        # 1. Launch envelop check
        if launch_range_km > missile.max_range_km:
            return 0.0, {"reason": "Out of range"}
        if launch_range_km < missile.min_range_km:
            return 0.0, {"reason": "Inside minimum range"}

        # 2. P(missile reaches acquisition range)
        # Depends on target maneuvers and missile energy
        range_ratio = launch_range_km / missile.max_range_km

        if range_ratio < 0.5:
            p_reach = 0.95
        elif range_ratio < 0.8:
            p_reach = 0.90 - 0.1 * (range_ratio - 0.5) / 0.3
        else:
            p_reach = 0.75 - 0.25 * (range_ratio - 0.8) / 0.2

        if target_maneuvering:
            p_reach *= 0.85  # Maneuvers extend range requirement

        breakdown["p_reach_acquisition"] = p_reach

        # 3. P(seeker acquires target)
        # Get target RCS at aspect
        aspect_rounded = min(target.rcs_x_band.keys(),
                            key=lambda x: abs(x - aspect_deg))
        rcs_dbsm = target.rcs_x_band[aspect_rounded]
        rcs_m2 = 10 ** (rcs_dbsm / 10)

        # Seeker acquisition depends on RCS
        # Normalize to reference (1 m²)
        rcs_factor = np.sqrt(rcs_m2)  # Square root law for acquisition

        p_acquire = missile.pk_seeker_lock * min(1.0, rcs_factor * 3)

        if target_jamming:
            if missile.home_on_jam:
                p_acquire = max(p_acquire, 0.70)  # HOJ mode
            else:
                p_acquire *= 0.5

        if datalink_active and awacs_cue:
            p_acquire = min(0.95, p_acquire * 1.15)  # Datalink helps

        breakdown["p_seeker_acquire"] = p_acquire

        # 4. P(guidance to intercept)
        p_guidance = missile.pk_guidance

        if target_maneuvering:
            # High-G maneuvers reduce Pk
            p_guidance *= 0.75

        if datalink_active:
            p_guidance = min(0.95, p_guidance * 1.1)

        breakdown["p_guidance"] = p_guidance

        # 5. P(fuze functions)
        p_fuze = missile.pk_fuze

        if target_maneuvering:
            # Miss distance increases, but proximity fuze helps
            p_fuze *= 0.95

        breakdown["p_fuze"] = p_fuze

        # 6. P(warhead effect)
        p_warhead = missile.pk_warhead

        breakdown["p_warhead"] = p_warhead

        # Total single-shot Pk
        pk = p_reach * p_acquire * p_guidance * p_fuze * p_warhead

        breakdown["pk_total"] = pk

        return pk, breakdown

    def calculate_salvo_pk(
        self,
        single_pk: float,
        salvo_size: int,
        correlation: float = 0.25
    ) -> Tuple[float, float]:
        """
        Calculate salvo Pk with correlation.

        Returns: (salvo_pk, n_effective)
        """

        # Effective number of independent shots
        n_effective = 1 + (salvo_size - 1) * (1 - correlation)

        # Salvo Pk
        salvo_pk = 1 - (1 - single_pk) ** n_effective

        return salvo_pk, n_effective

    def optimize_engagement(
        self,
        target: F35Signature,
        scenario_name: str
    ) -> Dict:
        """
        Optimize engagement parameters for maximum Pk.
        """

        # Create sensors
        kj500 = create_kj500()
        kj2000 = create_kj2000()
        j20_radar = create_j20_radar()
        j20_ew = create_j20_ew()
        ylc8e = create_ylc8e()
        jy27a = create_jy27a()
        pl15 = PL15Missile()

        results = {
            "scenario": scenario_name,
            "target": target.variant.value,
            "sensors": [],
            "engagements": [],
            "optimized_pk": 0.0
        }

        self.logger.log_calculation(
            name=f"{scenario_name} Target Characteristics",
            formula="F-35 RCS profile",
            inputs={
                "variant": target.variant.value,
                "frontal_rcs_dbsm": target.rcs_x_band[0],
                "broadside_rcs_dbsm": target.rcs_x_band[90],
                "vhf_rcs_m2": target.rcs_vhf
            },
            result=target.rcs_x_band[0],
            unit="dBsm",
            confidence=target.rcs_confidence
        )

        # Simulate engagement scenarios
        engagement_range = 120  # km, typical BVR engagement

        # Test different aspect angles
        aspects_to_test = [0, 30, 45, 60, 90]

        best_pk = 0.0
        best_config = {}

        for aspect in aspects_to_test:
            # Multi-sensor detection
            detections = []

            # AWACS detection
            det_kj500 = self.fusion.detect_target(kj500, target, aspect, engagement_range)
            det_kj2000 = self.fusion.detect_target(kj2000, target, aspect, engagement_range)
            detections.extend([det_kj500, det_kj2000])

            # Ground radar (VHF anti-stealth)
            det_jy27a = self.fusion.detect_with_ground_radar(jy27a, target, engagement_range)
            det_ylc8e = self.fusion.detect_with_ground_radar(ylc8e, target, engagement_range)
            detections.extend([det_jy27a, det_ylc8e])

            # J-20 radar
            det_j20 = self.fusion.detect_with_fighter_radar(j20_radar, target, aspect, engagement_range)
            detections.append(det_j20)

            # Fuse detections
            fused_detected, track_quality, position_error = self.fusion.fuse_detections(detections)

            if not fused_detected:
                continue

            # Calculate engagement Pk
            for target_maneuvering in [False, True]:
                for target_jamming in [False, True]:

                    pk, breakdown = self.calculate_engagement_pk(
                        target=target,
                        missile=pl15,
                        launch_range_km=engagement_range,
                        awacs_cue=det_kj500.detected or det_kj2000.detected,
                        datalink_active=True,
                        target_maneuvering=target_maneuvering,
                        target_jamming=target_jamming,
                        aspect_deg=aspect
                    )

                    # Salvo engagement (4 missiles)
                    salvo_pk, n_eff = self.calculate_salvo_pk(pk, 4)

                    config = {
                        "aspect_deg": aspect,
                        "maneuvering": target_maneuvering,
                        "jamming": target_jamming,
                        "single_pk": pk,
                        "salvo_pk": salvo_pk,
                        "track_quality": track_quality,
                        "breakdown": breakdown
                    }

                    results["engagements"].append(config)

                    if salvo_pk > best_pk:
                        best_pk = salvo_pk
                        best_config = config

        results["optimized_pk"] = best_pk
        results["best_config"] = best_config

        # Log sensor effectiveness
        for det in detections:
            results["sensors"].append({
                "name": det.sensor_name,
                "detection_range_km": det.detection_range_km,
                "detected": det.detected,
                "track_quality": det.track_quality
            })

        return results


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def run_f35_kill_chain_analysis():
    """Run comprehensive F-35 kill chain analysis"""

    logger = init_logger(
        name="F35-Kill-Chain",
        output_formats=[OutputFormat.CONSOLE, OutputFormat.GITHUB_ACTIONS],
        log_file="f35_kill_chain_log.txt",
        verbose=True
    )

    calculator = KillChainCalculator(logger)

    # Create F-35 variants
    f35a = create_f35a_signature()
    f35b = create_f35b_signature()
    f35c = create_f35c_signature()

    all_results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "analysis": "F-35 Kill Chain Optimization",
        "variants": {},
        "summary": {}
    }

    print("=" * 80)
    print("F-35 INTEGRATED KILL CHAIN ANALYSIS")
    print("Maximizing Pk using AWACS + J-20 + PL-15 + Ground Radar")
    print("=" * 80)

    # Analyze each variant
    for target, name in [(f35a, "F-35A CTOL"), (f35b, "F-35B STOVL"), (f35c, "F-35C CV")]:
        print(f"\n{'─' * 80}")
        print(f"ANALYZING: {name}")
        print(f"{'─' * 80}")

        with logger.section(f"Analysis: {name}"):
            results = calculator.optimize_engagement(target, name)

            # Log key results
            logger.log_calculation(
                name=f"{name} Optimized Kill Probability",
                formula="Multi-sensor fusion + PL-15 salvo",
                inputs={
                    "sensors": len(results["sensors"]),
                    "salvo_size": 4,
                    "best_aspect": results["best_config"].get("aspect_deg", 0)
                },
                result=results["optimized_pk"],
                unit="probability",
                confidence=0.45,
                notes=f"Best case: aspect={results['best_config'].get('aspect_deg', 0)}°, "
                      f"maneuver={results['best_config'].get('maneuvering', False)}, "
                      f"jam={results['best_config'].get('jamming', False)}"
            )

            all_results["variants"][name] = results

            # Print summary
            print(f"\n  OPTIMIZED CONFIGURATION:")
            print(f"    Best aspect angle: {results['best_config'].get('aspect_deg', 'N/A')}°")
            print(f"    Single-shot Pk: {results['best_config'].get('single_pk', 0):.4f}")
            print(f"    Salvo Pk (4 missiles): {results['best_config'].get('salvo_pk', 0):.4f}")
            print(f"    Track quality: {results['best_config'].get('track_quality', 0):.2f}")

            print(f"\n  BREAKDOWN:")
            breakdown = results['best_config'].get('breakdown', {})
            for key, val in breakdown.items():
                if isinstance(val, float):
                    print(f"    {key}: {val:.4f}")

    # Generate detailed engagement matrix
    print("\n" + "=" * 80)
    print("ENGAGEMENT MATRIX: PK BY ASPECT AND CONDITIONS")
    print("=" * 80)

    pl15 = PL15Missile()

    for target, name in [(f35a, "F-35A"), (f35b, "F-35B"), (f35c, "F-35C")]:
        print(f"\n{name}:")
        print("  Aspect |  Clean  | Maneuver | Jamming | Both")
        print("  -------|---------|----------|---------|------")

        for aspect in [0, 30, 45, 60, 90]:
            pks = []
            for maneuver, jam in [(False, False), (True, False), (False, True), (True, True)]:
                pk, _ = calculator.calculate_engagement_pk(
                    target, pl15, 120, True, True, maneuver, jam, aspect
                )
                salvo_pk, _ = calculator.calculate_salvo_pk(pk, 4)
                pks.append(salvo_pk)

            print(f"  {aspect:3d}°   | {pks[0]:6.1%} | {pks[1]:7.1%} | {pks[2]:6.1%} | {pks[3]:5.1%}")

    # Summary statistics
    all_results["summary"] = {
        "f35a_max_pk": all_results["variants"]["F-35A CTOL"]["optimized_pk"],
        "f35b_max_pk": all_results["variants"]["F-35B STOVL"]["optimized_pk"],
        "f35c_max_pk": all_results["variants"]["F-35C CV"]["optimized_pk"],
        "average_max_pk": np.mean([
            all_results["variants"]["F-35A CTOL"]["optimized_pk"],
            all_results["variants"]["F-35B STOVL"]["optimized_pk"],
            all_results["variants"]["F-35C CV"]["optimized_pk"]
        ]),
        "key_findings": [
            "VHF/UHF ground radar provides early warning against stealth",
            "Off-boresight aspects significantly increase detection and Pk",
            "Multi-sensor fusion improves track quality by 15-25%",
            "PL-15 datalink + AWACS cueing critical for BVR engagement",
            "Target countermeasures reduce Pk by 25-40%",
            "100% Pk remains impossible due to fundamental uncertainties"
        ]
    }

    logger.finalize()

    # Write results
    with open("f35_kill_chain_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print("\nWrote: f35_kill_chain_results.json")

    md_report = logger.generate_markdown_report()
    with open("f35_kill_chain_report.md", "w") as f:
        f.write(md_report)
    print("Wrote: f35_kill_chain_report.md")

    print("\n" + "=" * 80)
    print("F-35 KILL CHAIN ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nMAXIMUM ACHIEVABLE PK (4-missile salvo, optimal conditions):")
    print(f"  F-35A: {all_results['summary']['f35a_max_pk']:.1%}")
    print(f"  F-35B: {all_results['summary']['f35b_max_pk']:.1%}")
    print(f"  F-35C: {all_results['summary']['f35c_max_pk']:.1%}")
    print(f"\nKEY LIMITATIONS PREVENTING 100% PK:")
    for finding in all_results["summary"]["key_findings"]:
        print(f"  • {finding}")

    return all_results


if __name__ == "__main__":
    run_f35_kill_chain_analysis()
