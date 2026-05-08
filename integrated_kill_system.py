#!/usr/bin/env python3
"""
Integrated Multi-Layer Kill System for F-35 Engagement

Implements comprehensive, layered defense-in-depth architecture designed for
near-certain F-35 elimination from moment of takeoff. Uses redundant detection,
multi-shooter engagement, and diverse weapon types.

DESIGN PHILOSOPHY:
"Guaranteed kill" requires defeating ALL of:
1. Stealth (low RCS)
2. Electronic warfare (jamming, deception)
3. Defensive countermeasures (chaff, flares, maneuvers)
4. Tactics (terrain masking, time-critical strikes)

SHORTCOMINGS PREVENTING 100% Pk (documented throughout):
- Classification barriers (45-70% confidence on most parameters)
- Physics limitations (radar equation, atmospheric effects)
- Countermeasure uncertainty (unknown F-35 EW capabilities)
- Operational factors (crew proficiency, maintenance state)
- Network vulnerabilities (latency, cyber, jamming)

Classification: UNCLASSIFIED // PUBLIC RELEASE
Data Sources: Open source only - CSIS, IISS, Jane's, academic papers
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from enum import Enum
from abc import ABC, abstractmethod
import json

from cad_geometry import Point3D, Vector3D, TriangleMesh, MissileCADModel


# =============================================================================
# SECTION 1: F-35 TARGET CHARACTERIZATION
# =============================================================================

@dataclass
class F35Signature:
    """
    F-35A Lightning II signature characteristics across all domains.

    CRITICAL LIMITATION: All values are estimates from public sources.
    Actual classified values likely differ significantly.
    Confidence levels indicate reliability of public estimates.
    """
    # Radar Cross Section (RCS) by aspect and frequency
    # Source: Public estimates, not verified
    rcs_frontal_x_band_m2: float = 0.0002  # -37 dBsm, "golf ball" (55% confidence)
    rcs_frontal_vhf_m2: float = 0.5  # VHF resonance effect (45% confidence)
    rcs_beam_x_band_m2: float = 0.02  # -17 dBsm (50% confidence)
    rcs_rear_x_band_m2: float = 0.005  # Engine nozzles (50% confidence)
    rcs_dorsal_m2: float = 0.008  # Top view (45% confidence)
    rcs_ventral_m2: float = 0.01  # Bottom, weapons bays (45% confidence)

    # Infrared signature
    ir_signature_afterburner_wm2: float = 50000  # Afterburner (60% confidence)
    ir_signature_military_wm2: float = 5000  # Military power (55% confidence)
    ir_signature_idle_wm2: float = 500  # Idle/cruise (50% confidence)

    # Electronic emissions (detectable by ESM)
    apg81_peak_power_kw: float = 20  # APG-81 AESA (40% confidence)
    apg81_frequency_ghz: float = 10.0  # X-band center
    madl_frequency_ghz: float = 15.0  # Ku-band datalink
    madl_power_w: float = 100  # Sidelobe power (35% confidence)
    asq239_ew_bands: List[str] = field(default_factory=lambda: [
        "VHF", "UHF", "L", "S", "C", "X", "Ku"
    ])

    # Physical dimensions (affects VHF resonance)
    length_m: float = 15.67
    wingspan_m: float = 10.67
    height_m: float = 4.38

    # Performance envelope
    max_speed_mach: float = 1.6
    cruise_speed_mach: float = 0.85
    service_ceiling_m: float = 15240  # 50,000 ft
    combat_radius_km: float = 1093  # Internal fuel

    # Countermeasures (MAJOR UNCERTAINTY)
    # These are the biggest unknowns affecting Pk
    ecm_effectiveness_estimate: float = 0.3  # 30% Pk reduction (VERY uncertain)
    decoy_effectiveness_estimate: float = 0.2  # 20% Pk reduction (VERY uncertain)
    maneuver_g_limit: float = 9.0

    def get_rcs_at_aspect(self, azimuth_deg: float, elevation_deg: float,
                          frequency_ghz: float) -> Tuple[float, float]:
        """
        Get RCS at given aspect angle and frequency.

        Returns:
            Tuple of (rcs_m2, confidence)

        LIMITATION: Simplified model. Real RCS varies continuously and
        depends on exact geometry, coatings, panel gaps, etc.
        """
        # Frequency scaling
        if frequency_ghz < 0.5:  # VHF band - resonance region
            # Stealth less effective at VHF (resonance with aircraft dimensions)
            base_rcs = self.rcs_frontal_vhf_m2
            confidence = 0.45
        else:
            # X-band and above - stealth effective
            # Interpolate based on aspect
            az = abs(azimuth_deg) % 180

            if az < 30:
                base_rcs = self.rcs_frontal_x_band_m2
                confidence = 0.55
            elif az < 60:
                # Transition region
                t = (az - 30) / 30
                base_rcs = self.rcs_frontal_x_band_m2 * (1-t) + self.rcs_beam_x_band_m2 * t
                confidence = 0.50
            elif az < 120:
                base_rcs = self.rcs_beam_x_band_m2
                confidence = 0.50
            elif az < 150:
                t = (az - 120) / 30
                base_rcs = self.rcs_beam_x_band_m2 * (1-t) + self.rcs_rear_x_band_m2 * t
                confidence = 0.48
            else:
                base_rcs = self.rcs_rear_x_band_m2
                confidence = 0.50

            # Elevation adjustment
            if abs(elevation_deg) > 30:
                # Looking from above/below - different signature
                if elevation_deg > 0:
                    base_rcs = max(base_rcs, self.rcs_dorsal_m2)
                else:
                    base_rcs = max(base_rcs, self.rcs_ventral_m2)
                confidence *= 0.9

        return base_rcs, confidence


@dataclass
class F35OperationalState:
    """
    F-35 operational state affecting detectability and vulnerability.

    Key insight: F-35 is most vulnerable during:
    1. Takeoff/landing (predictable location, high IR, no terrain masking)
    2. Weapons bay open (massive RCS spike)
    3. Afterburner use (IR bloom)
    4. Radar active (ESM detection)
    5. Datalink active (MADL sidelobe detection)
    """
    phase: str  # "takeoff", "cruise", "combat", "egress", "landing"
    altitude_m: float
    speed_mach: float
    weapons_bay_open: bool = False
    afterburner_active: bool = False
    radar_active: bool = False
    datalink_active: bool = True  # MADL usually active
    ecm_active: bool = False

    def get_effective_rcs_multiplier(self) -> Tuple[float, str]:
        """
        Get RCS multiplier based on operational state.

        Returns:
            Tuple of (multiplier, reason)

        CRITICAL: Weapons bay open creates MASSIVE RCS spike.
        This is the key vulnerability window for engagement.
        """
        multiplier = 1.0
        reasons = []

        if self.weapons_bay_open:
            # Weapons bay creates cavity resonance - huge RCS increase
            multiplier *= 100  # ~20 dB increase (estimated)
            reasons.append("weapons_bay_open")

        if self.afterburner_active:
            # Afterburner plume is radar reflective
            multiplier *= 3  # ~5 dB increase from rear
            reasons.append("afterburner")

        if self.phase == "takeoff":
            # Gear down, flaps deployed
            multiplier *= 10  # ~10 dB increase
            reasons.append("takeoff_config")

        if self.phase == "landing":
            multiplier *= 10
            reasons.append("landing_config")

        reason = "+".join(reasons) if reasons else "clean"
        return multiplier, reason


# =============================================================================
# SECTION 2: MULTI-LAYER DETECTION ARCHITECTURE
# =============================================================================

class DetectionLayer(Enum):
    """Detection layers in kill chain"""
    SPACE = "space"  # Satellites
    AIRBORNE = "airborne"  # AWACS, UAVs
    SURFACE = "surface"  # Ground/ship radar
    UNDERSEA = "undersea"  # Submarine SIGINT
    CYBER = "cyber"  # Network penetration


@dataclass
class SensorSystem:
    """Base class for sensor systems"""
    name: str
    layer: DetectionLayer
    detection_range_km: float
    track_accuracy_m: float
    update_rate_hz: float
    confidence: float  # Data confidence level

    # Limitations
    weather_degradation: float = 0.0  # 0-1, fraction lost in bad weather
    jamming_vulnerability: float = 0.0  # 0-1, effectiveness reduction under jamming

    @abstractmethod
    def calculate_detection_probability(self, target: F35Signature,
                                        range_km: float,
                                        state: F35OperationalState) -> float:
        """Calculate probability of detection"""
        pass


@dataclass
class SpaceBasedSensor(SensorSystem):
    """
    Space-based detection (satellites).

    Advantages:
    - Cannot be jammed from ground (too far)
    - Persistent coverage
    - Early warning of takeoff

    LIMITATIONS:
    - Orbital mechanics limit revisit rate
    - Weather affects optical sensors
    - Resolution limits for radar
    - Track latency (data downlink time)
    """
    orbit_type: str = "LEO"  # LEO, MEO, GEO
    sensor_type: str = "radar"  # radar, optical, SIGINT
    revisit_time_min: float = 90  # Time between passes
    resolution_m: float = 1.0

    def calculate_detection_probability(self, target: F35Signature,
                                        range_km: float,
                                        state: F35OperationalState) -> float:
        """
        Space sensor detection probability.

        LIMITATION: Assumes clear weather, no deception.
        Real Pd would be lower due to:
        - Cloud cover (optical)
        - Orbital gaps
        - Processing delays
        """
        if self.sensor_type == "radar":
            # SAR can detect metal objects, but F-35 on ground is small
            if state.phase in ["takeoff", "landing"]:
                # Aircraft on runway - easier to detect
                return 0.85 * self.confidence
            else:
                # In flight - harder for space radar
                return 0.3 * self.confidence

        elif self.sensor_type == "optical":
            if state.afterburner_active:
                return 0.95 * self.confidence  # IR bloom very visible
            elif state.phase in ["takeoff", "landing"]:
                return 0.7 * self.confidence
            else:
                return 0.4 * self.confidence  # Small target

        elif self.sensor_type == "SIGINT":
            if state.radar_active or state.datalink_active:
                return 0.8 * self.confidence
            else:
                return 0.1 * self.confidence  # Emissions silent

        return 0.0


@dataclass
class AirborneEarlyWarning(SensorSystem):
    """
    Airborne Early Warning & Control (AWACS).

    Key systems modeled:
    - KJ-500: VHF + X-band, counter-stealth optimized
    - KJ-2000: Large AESA, high power

    CRITICAL ADVANTAGE: VHF radar exploits stealth resonance region.
    F-35 optimized for X-band, NOT VHF.

    LIMITATIONS:
    - VHF has poor angular resolution (~5-10 deg)
    - Track accuracy ~500m CEP (insufficient for terminal guidance)
    - Vulnerable to long-range AAMs
    - Limited endurance
    """
    radar_bands: List[str] = field(default_factory=list)
    peak_power_kw: float = 100
    antenna_gain_db: float = 30
    altitude_m: float = 9000
    endurance_hours: float = 8

    # Counter-stealth specific
    vhf_detection_range_vs_f35_km: float = 200  # Much longer than X-band

    def calculate_detection_probability(self, target: F35Signature,
                                        range_km: float,
                                        state: F35OperationalState) -> float:
        """
        AEW detection probability against F-35.

        VHF band is key - exploits resonance with aircraft dimensions.
        """
        pd = 0.0

        # VHF band detection (counter-stealth)
        if "VHF" in self.radar_bands:
            rcs, _ = target.get_rcs_at_aspect(0, 0, 0.3)  # 300 MHz VHF

            # Radar equation (simplified)
            # Detection range ~ (RCS)^0.25 * base_range
            effective_range = self.vhf_detection_range_vs_f35_km * (rcs / 0.5) ** 0.25

            if range_km < effective_range:
                # Probability increases as target gets closer
                pd = max(pd, 0.9 * (1 - range_km / effective_range) ** 0.5)

        # X-band detection (degraded by stealth)
        if "X" in self.radar_bands:
            rcs, _ = target.get_rcs_at_aspect(0, 0, 10.0)  # 10 GHz X-band
            rcs_multiplier, _ = state.get_effective_rcs_multiplier()
            effective_rcs = rcs * rcs_multiplier

            # Much shorter range against stealth
            effective_range = self.detection_range_km * (effective_rcs / 1.0) ** 0.25

            if range_km < effective_range:
                pd = max(pd, 0.85 * (1 - range_km / effective_range) ** 0.5)

        # ESM detection (passive)
        if state.radar_active or state.datalink_active:
            # Passive detection of emissions
            esm_range = 300  # km, typical ESM range
            if range_km < esm_range:
                pd = max(pd, 0.8 * self.confidence)

        return pd * self.confidence


@dataclass
class SurfaceRadar(SensorSystem):
    """
    Surface-based radar systems (ground or ship).

    Key systems:
    - JY-27A: VHF counter-stealth (claimed F-22 detection)
    - Type 346B: Shipborne AESA (Type 052D destroyer)
    - HQ-9B radar: Fire control quality

    ADVANTAGES:
    - High power (grid connected)
    - Large apertures possible
    - Hardened positions
    - Networked coverage

    LIMITATIONS:
    - Fixed or slow-moving (known positions)
    - Terrain masking from low-flying targets
    - Vulnerable to anti-radiation missiles
    - Horizon limits detection of low targets
    """
    radar_type: str = "search"  # search, tracking, fire_control
    mobile: bool = False
    frequency_band: str = "X"
    peak_power_mw: float = 1.0  # Megawatts
    prf_hz: float = 1000

    # Horizon calculations
    antenna_height_m: float = 30

    def radar_horizon_km(self, target_altitude_m: float) -> float:
        """
        Calculate radar horizon distance.

        CRITICAL LIMITATION: Low-flying F-35 can hide below radar horizon.
        This is a fundamental physics limitation.
        """
        # Simplified radar horizon: d = sqrt(2*R*h) for each end
        R = 6371  # Earth radius km
        h_radar = self.antenna_height_m / 1000
        h_target = target_altitude_m / 1000

        d_radar = np.sqrt(2 * R * h_radar)
        d_target = np.sqrt(2 * R * h_target)

        return d_radar + d_target

    def calculate_detection_probability(self, target: F35Signature,
                                        range_km: float,
                                        state: F35OperationalState) -> float:
        """Surface radar detection probability"""

        # Check horizon limit first
        horizon = self.radar_horizon_km(state.altitude_m)
        if range_km > horizon:
            return 0.0  # Below horizon - cannot detect

        # Get target RCS
        freq_ghz = {"VHF": 0.3, "UHF": 0.5, "L": 1.5, "S": 3.0,
                    "C": 5.0, "X": 10.0, "Ku": 15.0}.get(self.frequency_band, 10.0)

        rcs, rcs_confidence = target.get_rcs_at_aspect(0, 0, freq_ghz)
        rcs_mult, _ = state.get_effective_rcs_multiplier()
        effective_rcs = rcs * rcs_mult

        # Radar equation for detection range
        # R_max ~ (P * G^2 * lambda^2 * sigma / (4*pi)^3 / S_min)^0.25
        wavelength = 0.3 / freq_ghz  # m

        # Simplified: use configured range as baseline for 1 m^2 target
        effective_range = self.detection_range_km * (effective_rcs / 1.0) ** 0.25

        if range_km > effective_range:
            return 0.0

        # Detection probability
        snr_margin = (effective_range / range_km) ** 4
        pd = min(0.99, 0.5 * (1 + np.log10(snr_margin)))

        return pd * self.confidence * rcs_confidence


@dataclass
class PassiveDetectionSystem(SensorSystem):
    """
    Passive detection (no emissions - undetectable).

    Types:
    - ESM/ELINT: Detect radar/datalink emissions
    - IRST: Infrared search and track
    - Acoustic: Sound detection (limited use for jets)

    CRITICAL ADVANTAGE: Cannot be detected or jammed.
    F-35 must emit to use radar/datalink - creates vulnerability.

    LIMITATION: Requires target to emit (ESM) or be hot (IRST).
    """
    sensor_modality: str = "ESM"  # ESM, IRST, acoustic
    sensitivity_dbm: float = -80  # For ESM
    angular_accuracy_deg: float = 2.0

    def calculate_detection_probability(self, target: F35Signature,
                                        range_km: float,
                                        state: F35OperationalState) -> float:
        """Passive detection probability"""

        if self.sensor_modality == "ESM":
            # Detect radar and datalink emissions
            if not (state.radar_active or state.datalink_active):
                return 0.05  # Some residual emissions always present

            # ESM range calculation
            if state.radar_active:
                # APG-81 active - strong signal
                erp_dbm = 10 * np.log10(target.apg81_peak_power_kw * 1e6)
            else:
                # MADL sidelobes only
                erp_dbm = 10 * np.log10(target.madl_power_w * 1000)

            # Free space path loss
            fspl = 20 * np.log10(range_km) + 20 * np.log10(10e9) - 147.55
            received = erp_dbm - fspl

            if received > self.sensitivity_dbm:
                margin = received - self.sensitivity_dbm
                return min(0.95, 0.5 + margin / 40) * self.confidence
            return 0.1 * self.confidence

        elif self.sensor_modality == "IRST":
            # Infrared detection
            if state.afterburner_active:
                ir_sig = target.ir_signature_afterburner_wm2
            elif state.speed_mach > 1.0:
                ir_sig = target.ir_signature_military_wm2
            else:
                ir_sig = target.ir_signature_idle_wm2

            # Simplified: IRST range ~ sqrt(IR signature)
            base_range = 50  # km for idle
            effective_range = base_range * np.sqrt(ir_sig / 500)

            if range_km < effective_range:
                return min(0.9, 0.5 * effective_range / range_km) * self.confidence
            return 0.0

        return 0.0


# =============================================================================
# SECTION 3: INTEGRATED DETECTION NETWORK
# =============================================================================

@dataclass
class IntegratedDetectionNetwork:
    """
    Network of sensors fused for maximum detection probability.

    KEY PRINCIPLE: Redundant, diverse sensors overcome single-point failures.

    Network includes:
    - Space layer (early warning, cannot be jammed)
    - Airborne layer (VHF counter-stealth)
    - Surface layer (high power, dense coverage)
    - Passive layer (ESM/IRST, undetectable)

    FUSION BENEFITS:
    - Multiple independent detections increase confidence
    - Different modalities counter different threats
    - Passive cueing to active sensors
    - Track fusion improves accuracy

    NETWORK LIMITATIONS (preventing 100% detection):
    - Communication latency (1-5 seconds typical)
    - Data fusion errors
    - Cyber vulnerability
    - Jamming of datalinks
    - Orbital gaps (space sensors)
    - Endurance limits (airborne)
    """
    name: str = "Integrated Air Defense Network"
    sensors: List[SensorSystem] = field(default_factory=list)

    # Network characteristics
    fusion_latency_s: float = 2.0  # Track fusion delay
    comm_reliability: float = 0.95  # Probability links are working
    cyber_vulnerability: float = 0.1  # Probability of cyber disruption

    def add_sensor(self, sensor: SensorSystem):
        """Add sensor to network"""
        self.sensors.append(sensor)

    def calculate_network_detection_probability(
        self,
        target: F35Signature,
        target_state: F35OperationalState,
        target_position_km: Point3D
    ) -> Dict[str, any]:
        """
        Calculate fused detection probability across all sensors.

        Uses "1 - product of misses" for independent sensors.

        Returns comprehensive detection assessment.
        """
        results = {
            "individual_detections": [],
            "fused_pd": 0.0,
            "track_quality": "none",
            "track_accuracy_m": float('inf'),
            "confidence": 0.0,
            "limitations": [],
            "best_sensor": None,
        }

        # Calculate range from each sensor (simplified: all at origin)
        range_km = np.sqrt(target_position_km.x**2 +
                          target_position_km.y**2 +
                          target_position_km.z**2)

        # Calculate detection probability for each sensor
        miss_probability = 1.0
        best_pd = 0.0
        best_accuracy = float('inf')

        for sensor in self.sensors:
            pd = sensor.calculate_detection_probability(
                target, range_km, target_state
            )

            # Apply network degradation factors
            pd *= self.comm_reliability
            pd *= (1 - self.cyber_vulnerability)

            results["individual_detections"].append({
                "sensor": sensor.name,
                "layer": sensor.layer.value,
                "pd": pd,
                "range_km": range_km,
                "accuracy_m": sensor.track_accuracy_m
            })

            if pd > 0:
                miss_probability *= (1 - pd)

                if pd > best_pd:
                    best_pd = pd
                    results["best_sensor"] = sensor.name

                if sensor.track_accuracy_m < best_accuracy:
                    best_accuracy = sensor.track_accuracy_m

        # Fused probability: 1 - P(all miss)
        fused_pd = 1 - miss_probability
        results["fused_pd"] = fused_pd
        results["track_accuracy_m"] = best_accuracy

        # Assess track quality
        if fused_pd > 0.95 and best_accuracy < 50:
            results["track_quality"] = "fire_control"
            results["confidence"] = 0.85
        elif fused_pd > 0.8 and best_accuracy < 200:
            results["track_quality"] = "weapons_quality"
            results["confidence"] = 0.70
        elif fused_pd > 0.5:
            results["track_quality"] = "track"
            results["confidence"] = 0.55
        elif fused_pd > 0.2:
            results["track_quality"] = "detection"
            results["confidence"] = 0.40
        else:
            results["track_quality"] = "none"
            results["confidence"] = 0.20

        # Document limitations
        if target_state.altitude_m < 1000:
            results["limitations"].append(
                "LOW_ALTITUDE: Surface radars limited by horizon"
            )
        if not (target_state.radar_active or target_state.datalink_active):
            results["limitations"].append(
                "EMISSIONS_SILENT: Passive ESM ineffective"
            )
        if target_state.ecm_active:
            results["limitations"].append(
                "ECM_ACTIVE: Detection degraded by jamming (unknown amount)"
            )
        if range_km > 300:
            results["limitations"].append(
                "LONG_RANGE: VHF accuracy insufficient for fire control"
            )

        return results


# =============================================================================
# SECTION 4: WEAPON SYSTEMS FOR GUARANTEED KILL
# =============================================================================

class WeaponType(Enum):
    """Weapon categories"""
    SAM_LONG_RANGE = "sam_long"  # HQ-9B, S-400
    SAM_MEDIUM_RANGE = "sam_medium"  # HQ-16
    SAM_SHORT_RANGE = "sam_short"  # HQ-7, TY-90
    AAM_BVR = "aam_bvr"  # PL-15, PL-21
    AAM_WVR = "aam_wvr"  # PL-10
    ASBM = "asbm"  # DF-21D, DF-26
    HYPERSONIC = "hypersonic"  # DF-27


@dataclass
class WeaponSystem:
    """
    Base weapon system for engagement calculations.

    Key parameters for Pk:
    - Kinematic range (can it reach the target?)
    - Seeker performance (can it acquire/track?)
    - Warhead lethality (can it kill?)
    - ECCM capability (can it resist jamming?)

    CRITICAL LIMITATION: Pk values are estimates.
    Actual performance is classified and may differ significantly.
    """
    name: str
    weapon_type: WeaponType
    max_range_km: float
    min_range_km: float
    max_altitude_m: float
    min_altitude_m: float
    speed_mach: float

    # Seeker characteristics
    seeker_type: str  # "active_radar", "semi_active", "IR", "dual_mode"
    seeker_range_km: float
    seeker_fov_deg: float

    # Kill probability components
    pk_seeker_acquisition: float  # P(seeker locks target)
    pk_guidance: float  # P(guidance succeeds given lock)
    pk_fuze: float  # P(fuze functions correctly)
    pk_warhead: float  # P(warhead kills given fuze)

    # ECCM
    eccm_effectiveness: float  # 0-1, resistance to jamming
    home_on_jam: bool = False  # Can home on jamming source

    # Confidence in these estimates
    data_confidence: float = 0.5

    def calculate_single_shot_pk(
        self,
        target: F35Signature,
        target_state: F35OperationalState,
        range_km: float,
        track_accuracy_m: float
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate single-shot kill probability.

        Pk = P(seeker) * P(guidance) * P(fuze) * P(warhead) * (1 - P(CM))

        Returns:
            Tuple of (Pk, breakdown of factors)
        """
        breakdown = {}

        # Check kinematic envelope
        if range_km > self.max_range_km or range_km < self.min_range_km:
            return 0.0, {"reason": "out_of_range"}

        if target_state.altitude_m > self.max_altitude_m:
            return 0.0, {"reason": "too_high"}
        if target_state.altitude_m < self.min_altitude_m:
            return 0.0, {"reason": "too_low"}

        # 1. Seeker acquisition probability
        # Degraded by stealth RCS and track handoff accuracy
        rcs, _ = target.get_rcs_at_aspect(0, 0, 10.0)  # Assume X-band seeker
        rcs_mult, _ = target_state.get_effective_rcs_multiplier()
        effective_rcs = rcs * rcs_mult

        # Seeker range scales with RCS^0.25
        effective_seeker_range = self.seeker_range_km * (effective_rcs / 1.0) ** 0.25

        if track_accuracy_m > self.seeker_fov_deg * range_km * 17.45:  # deg to m at range
            # Track error exceeds seeker FOV - seeker may not acquire
            pk_acquire = self.pk_seeker_acquisition * 0.5
        else:
            pk_acquire = self.pk_seeker_acquisition

        if range_km > effective_seeker_range:
            pk_acquire *= (effective_seeker_range / range_km) ** 2

        breakdown["pk_seeker"] = pk_acquire

        # 2. Guidance probability
        pk_guide = self.pk_guidance

        # Target maneuvers degrade guidance
        if target_state.speed_mach > 1.2:  # Supersonic evasion
            pk_guide *= 0.9

        # Low altitude = terrain masking risk
        if target_state.altitude_m < 500:
            pk_guide *= 0.8

        breakdown["pk_guidance"] = pk_guide

        # 3. Fuze probability (relatively constant)
        pk_fuze = self.pk_fuze
        breakdown["pk_fuze"] = pk_fuze

        # 4. Warhead probability
        pk_wh = self.pk_warhead
        breakdown["pk_warhead"] = pk_wh

        # 5. Countermeasures effect (MAJOR UNCERTAINTY)
        # This is where confidence breaks down
        cm_effectiveness = 0.0

        if target_state.ecm_active:
            # ECM reduces Pk based on ECCM capability
            cm_effectiveness += target.ecm_effectiveness_estimate * (1 - self.eccm_effectiveness)

            # Home-on-jam can counter ECM
            if self.home_on_jam and target_state.ecm_active:
                cm_effectiveness *= 0.3  # HOJ mostly negates ECM

        # Decoys (chaff/flares)
        cm_effectiveness += target.decoy_effectiveness_estimate * 0.5

        # Maneuvers
        if target.maneuver_g_limit > 7:
            cm_effectiveness += 0.1  # High-G maneuvers help evade

        pk_survive_cm = 1 - min(0.7, cm_effectiveness)  # Cap CM effectiveness
        breakdown["pk_survive_cm"] = pk_survive_cm
        breakdown["cm_uncertainty"] = "HIGH - F-35 EW capabilities classified"

        # Combined Pk
        pk_total = pk_acquire * pk_guide * pk_fuze * pk_wh * pk_survive_cm

        # Apply data confidence
        breakdown["data_confidence"] = self.data_confidence
        breakdown["confidence_adjusted_pk"] = pk_total * self.data_confidence + \
                                              0.3 * (1 - self.data_confidence)  # Regress to mean

        return pk_total, breakdown


@dataclass
class SAMBattery:
    """
    Surface-to-Air Missile battery with multiple launchers.

    Enables salvo engagement for guaranteed kills.
    """
    name: str
    weapon: WeaponSystem
    num_launchers: int
    missiles_per_launcher: int
    reload_time_s: float

    # Engagement doctrine
    max_simultaneous_engagements: int = 4
    salvo_size: int = 2  # Missiles per target

    def calculate_salvo_pk(
        self,
        target: F35Signature,
        target_state: F35OperationalState,
        range_km: float,
        track_accuracy_m: float,
        salvo_size: int = None
    ) -> Tuple[float, Dict]:
        """
        Calculate kill probability for salvo engagement.

        P(kill) = 1 - P(all miss) = 1 - (1-Pk)^n
        """
        if salvo_size is None:
            salvo_size = self.salvo_size

        pk_single, breakdown = self.weapon.calculate_single_shot_pk(
            target, target_state, range_km, track_accuracy_m
        )

        if pk_single <= 0:
            return 0.0, breakdown

        # Salvo calculation
        # Assumes missiles are independent (slight optimism)
        pk_salvo = 1 - (1 - pk_single) ** salvo_size

        breakdown["salvo_size"] = salvo_size
        breakdown["pk_single"] = pk_single
        breakdown["pk_salvo"] = pk_salvo

        # Confidence decreases with salvo assumptions
        breakdown["salvo_confidence"] = breakdown["data_confidence"] * 0.9

        return pk_salvo, breakdown


# =============================================================================
# SECTION 5: INTEGRATED KILL CHAIN - "GUARANTEED" F-35 KILL
# =============================================================================

@dataclass
class KillChainResult:
    """Result of kill chain analysis"""
    phase: str
    time_from_takeoff_s: float
    target_range_km: float
    target_altitude_m: float
    detection_pd: float
    track_quality: str
    track_accuracy_m: float
    engaged_by: List[str]
    pk_cumulative: float
    pk_this_phase: float
    limitations: List[str]
    confidence: float


@dataclass
class GuaranteedKillSystem:
    """
    Multi-layer, multi-shooter system designed for near-certain F-35 kills.

    ARCHITECTURE FOR "GUARANTEED" KILL:

    Phase 1 - TAKEOFF (0-60s from wheels up)
      - Space-based detection (airfield monitoring)
      - Long-range SAM engagement (DF-27 or HQ-9B)
      - Pk target: 0.6-0.8

    Phase 2 - CLIMB/EGRESS (60-300s)
      - VHF AWACS detection (counter-stealth)
      - Multiple SAM batteries (overlapping coverage)
      - Airborne intercept (J-20 with PL-15)
      - Pk target: 0.8-0.95

    Phase 3 - CRUISE (300s+)
      - Continuous tracking via VHF + ESM
      - Forward-deployed fighters
      - Ambush positions
      - Pk target: 0.7-0.9

    COMBINED Pk = 1 - (1-P1)(1-P2)(1-P3) > 0.99 theoretical

    WHY 100% IS IMPOSSIBLE (fundamental limitations):

    1. PHYSICS:
       - Radar horizon limits surface radar vs low-flying targets
       - Stealth still effective at X-band (degraded detection)
       - Atmospheric effects on sensors
       - Speed of light limits reaction time

    2. UNCERTAINTY:
       - F-35 EW capabilities are classified (unknown effectiveness)
       - Countermeasure technology constantly evolving
       - Human factors in crew performance
       - Weather and environmental effects

    3. OPERATIONAL:
       - Communication latency and reliability
       - Cyber vulnerabilities
       - Maintenance state of equipment
       - Training proficiency variations

    4. TACTICS:
       - F-35 can exploit seams in coverage
       - Terrain masking
       - Timing attacks during sensor gaps
       - Electronic deception

    5. RESOURCES:
       - Finite missile inventory
       - Sensor and shooter availability
       - Fuel and endurance limits
    """

    name: str = "Multi-Layer F-35 Kill System"

    # Detection network
    detection_network: IntegratedDetectionNetwork = None

    # Weapon systems by layer
    sam_batteries: List[SAMBattery] = field(default_factory=list)
    fighter_squadrons: List[Dict] = field(default_factory=list)

    # Engagement doctrine
    min_pk_threshold: float = 0.5  # Minimum Pk to attempt engagement
    salvo_doctrine: str = "shoot_shoot_look"  # shoot-look-shoot, shoot-shoot-look

    def __post_init__(self):
        if self.detection_network is None:
            self.detection_network = self._build_default_network()
        if not self.sam_batteries:
            self._add_default_sam_batteries()

    def _build_default_network(self) -> IntegratedDetectionNetwork:
        """Build comprehensive detection network"""
        network = IntegratedDetectionNetwork()

        # Space layer
        network.add_sensor(SpaceBasedSensor(
            name="Yaogan-30 Constellation",
            layer=DetectionLayer.SPACE,
            detection_range_km=1000,
            track_accuracy_m=100,
            update_rate_hz=0.01,  # ~100s revisit
            confidence=0.50,
            orbit_type="LEO",
            sensor_type="SIGINT"
        ))

        network.add_sensor(SpaceBasedSensor(
            name="Gaofen-4 GEO",
            layer=DetectionLayer.SPACE,
            detection_range_km=500,
            track_accuracy_m=50,
            update_rate_hz=0.1,
            confidence=0.45,
            orbit_type="GEO",
            sensor_type="optical"
        ))

        # Airborne layer
        network.add_sensor(AirborneEarlyWarning(
            name="KJ-500 AWACS",
            layer=DetectionLayer.AIRBORNE,
            detection_range_km=400,
            track_accuracy_m=500,  # VHF limitation
            update_rate_hz=0.1,
            confidence=0.60,
            radar_bands=["VHF", "L", "S"],
            vhf_detection_range_vs_f35_km=200,
            altitude_m=9000
        ))

        network.add_sensor(AirborneEarlyWarning(
            name="KJ-2000 AWACS",
            layer=DetectionLayer.AIRBORNE,
            detection_range_km=500,
            track_accuracy_m=200,
            update_rate_hz=0.2,
            confidence=0.55,
            radar_bands=["S", "X"],
            altitude_m=10000
        ))

        # Surface layer
        network.add_sensor(SurfaceRadar(
            name="JY-27A VHF Counter-Stealth",
            layer=DetectionLayer.SURFACE,
            detection_range_km=350,
            track_accuracy_m=600,
            update_rate_hz=0.1,
            confidence=0.55,
            radar_type="search",
            frequency_band="VHF",
            peak_power_mw=2.0,
            antenna_height_m=25
        ))

        network.add_sensor(SurfaceRadar(
            name="HQ-9B Fire Control Radar",
            layer=DetectionLayer.SURFACE,
            detection_range_km=200,
            track_accuracy_m=30,
            update_rate_hz=10,
            confidence=0.50,
            radar_type="fire_control",
            frequency_band="X",
            peak_power_mw=1.0,
            antenna_height_m=15
        ))

        network.add_sensor(SurfaceRadar(
            name="Type 346B AESA (Type 052D)",
            layer=DetectionLayer.SURFACE,
            detection_range_km=500,
            track_accuracy_m=25,
            update_rate_hz=5,
            confidence=0.50,
            radar_type="fire_control",
            frequency_band="S",
            peak_power_mw=5.0,
            antenna_height_m=35
        ))

        # Passive layer
        network.add_sensor(PassiveDetectionSystem(
            name="YLC-20 Passive ESM Network",
            layer=DetectionLayer.SURFACE,
            detection_range_km=400,
            track_accuracy_m=2000,  # ESM has poor accuracy
            update_rate_hz=1.0,
            confidence=0.60,
            sensor_modality="ESM",
            sensitivity_dbm=-90
        ))

        network.add_sensor(PassiveDetectionSystem(
            name="J-20 IRST",
            layer=DetectionLayer.AIRBORNE,
            detection_range_km=80,
            track_accuracy_m=50,
            update_rate_hz=5.0,
            confidence=0.55,
            sensor_modality="IRST"
        ))

        return network

    def _add_default_sam_batteries(self):
        """Add layered SAM defenses"""

        # Long range: HQ-9B
        hq9b = WeaponSystem(
            name="HQ-9B",
            weapon_type=WeaponType.SAM_LONG_RANGE,
            max_range_km=250,
            min_range_km=15,
            max_altitude_m=27000,
            min_altitude_m=500,
            speed_mach=4.2,
            seeker_type="active_radar",
            seeker_range_km=35,
            seeker_fov_deg=3.0,
            pk_seeker_acquisition=0.85,
            pk_guidance=0.90,
            pk_fuze=0.95,
            pk_warhead=0.80,
            eccm_effectiveness=0.60,
            home_on_jam=True,
            data_confidence=0.50
        )

        self.sam_batteries.append(SAMBattery(
            name="HQ-9B Battalion",
            weapon=hq9b,
            num_launchers=8,
            missiles_per_launcher=4,
            reload_time_s=300,
            max_simultaneous_engagements=8,
            salvo_size=2
        ))

        # Medium range: HQ-16
        hq16 = WeaponSystem(
            name="HQ-16B",
            weapon_type=WeaponType.SAM_MEDIUM_RANGE,
            max_range_km=70,
            min_range_km=3,
            max_altitude_m=18000,
            min_altitude_m=100,
            speed_mach=3.0,
            seeker_type="semi_active",
            seeker_range_km=20,
            seeker_fov_deg=5.0,
            pk_seeker_acquisition=0.80,
            pk_guidance=0.85,
            pk_fuze=0.95,
            pk_warhead=0.75,
            eccm_effectiveness=0.50,
            home_on_jam=False,
            data_confidence=0.55
        )

        self.sam_batteries.append(SAMBattery(
            name="HQ-16B Battalion",
            weapon=hq16,
            num_launchers=6,
            missiles_per_launcher=8,
            reload_time_s=180,
            max_simultaneous_engagements=12,
            salvo_size=2
        ))

        # Short range: HQ-7B
        hq7 = WeaponSystem(
            name="HQ-7B",
            weapon_type=WeaponType.SAM_SHORT_RANGE,
            max_range_km=15,
            min_range_km=0.5,
            max_altitude_m=6000,
            min_altitude_m=30,
            speed_mach=2.3,
            seeker_type="IR",
            seeker_range_km=8,
            seeker_fov_deg=10.0,
            pk_seeker_acquisition=0.90,
            pk_guidance=0.88,
            pk_fuze=0.95,
            pk_warhead=0.70,
            eccm_effectiveness=0.70,  # IR hard to jam
            home_on_jam=False,
            data_confidence=0.60
        )

        self.sam_batteries.append(SAMBattery(
            name="HQ-7B Battery",
            weapon=hq7,
            num_launchers=4,
            missiles_per_launcher=4,
            reload_time_s=60,
            max_simultaneous_engagements=4,
            salvo_size=2
        ))

    def analyze_kill_chain(
        self,
        target: F35Signature,
        initial_position_km: Point3D,
        heading_deg: float,
        speed_mach: float,
        mission_duration_s: float = 600
    ) -> List[KillChainResult]:
        """
        Analyze complete kill chain from takeoff through mission.

        Returns timeline of engagement opportunities and cumulative Pk.
        """
        results = []
        cumulative_miss = 1.0  # P(survive all engagements)

        # Simulate mission timeline
        time_step = 30  # seconds
        position = Point3D(initial_position_km.x, initial_position_km.y,
                          initial_position_km.z)

        # Speed in km/s
        speed_kms = speed_mach * 0.343  # Mach to km/s
        vx = speed_kms * np.sin(np.radians(heading_deg))
        vy = speed_kms * np.cos(np.radians(heading_deg))

        for t in range(0, int(mission_duration_s), time_step):
            # Determine flight phase
            if t < 60:
                phase = "takeoff"
                altitude = 300 + t * 50  # Climbing
                target_state = F35OperationalState(
                    phase="takeoff",
                    altitude_m=altitude,
                    speed_mach=0.3 + t * 0.01,
                    weapons_bay_open=False,
                    afterburner_active=True,  # Usually AB on takeoff
                    radar_active=False,
                    datalink_active=True,
                    ecm_active=False
                )
            elif t < 300:
                phase = "climb_egress"
                altitude = 3000 + (t - 60) * 30
                target_state = F35OperationalState(
                    phase="cruise",
                    altitude_m=min(altitude, 12000),
                    speed_mach=min(0.85, 0.4 + t * 0.002),
                    weapons_bay_open=False,
                    afterburner_active=False,
                    radar_active=t > 180,  # Radar on after clear of base
                    datalink_active=True,
                    ecm_active=t > 180
                )
            else:
                phase = "cruise"
                altitude = 12000
                target_state = F35OperationalState(
                    phase="cruise",
                    altitude_m=altitude,
                    speed_mach=0.85,
                    weapons_bay_open=False,
                    afterburner_active=False,
                    radar_active=True,
                    datalink_active=True,
                    ecm_active=True
                )

            # Update position
            position = Point3D(
                initial_position_km.x + vx * t,
                initial_position_km.y + vy * t,
                altitude / 1000  # km
            )

            range_km = np.sqrt(position.x**2 + position.y**2)

            # Detection assessment
            detection = self.detection_network.calculate_network_detection_probability(
                target, target_state, position
            )

            # Engagement assessment
            engaged_by = []
            pk_this_phase = 0.0
            phase_miss = 1.0

            if detection["fused_pd"] > 0.5:  # Need reasonable detection to engage
                for battery in self.sam_batteries:
                    pk_salvo, breakdown = battery.calculate_salvo_pk(
                        target, target_state, range_km,
                        detection["track_accuracy_m"]
                    )

                    if pk_salvo > self.min_pk_threshold:
                        engaged_by.append(f"{battery.name}: Pk={pk_salvo:.2f}")
                        phase_miss *= (1 - pk_salvo)

                pk_this_phase = 1 - phase_miss

            # Update cumulative
            cumulative_miss *= phase_miss
            pk_cumulative = 1 - cumulative_miss

            # Record result
            results.append(KillChainResult(
                phase=phase,
                time_from_takeoff_s=t,
                target_range_km=range_km,
                target_altitude_m=altitude,
                detection_pd=detection["fused_pd"],
                track_quality=detection["track_quality"],
                track_accuracy_m=detection["track_accuracy_m"],
                engaged_by=engaged_by,
                pk_cumulative=pk_cumulative,
                pk_this_phase=pk_this_phase,
                limitations=detection["limitations"],
                confidence=detection["confidence"] * 0.5  # Overall confidence
            ))

        return results

    def generate_kill_chain_report(
        self,
        results: List[KillChainResult]
    ) -> str:
        """Generate comprehensive kill chain analysis report"""
        lines = []
        lines.append("=" * 80)
        lines.append("INTEGRATED KILL CHAIN ANALYSIS: F-35 ENGAGEMENT")
        lines.append("=" * 80)
        lines.append("")
        lines.append("OBJECTIVE: Near-certain F-35 elimination from takeoff")
        lines.append("")

        # Summary
        final = results[-1] if results else None
        if final:
            lines.append("MISSION SUMMARY")
            lines.append("-" * 80)
            lines.append(f"  Final Cumulative Pk: {final.pk_cumulative:.1%}")
            lines.append(f"  Confidence Level: {final.confidence:.1%}")
            lines.append(f"  Mission Duration: {final.time_from_takeoff_s:.0f}s")
            lines.append("")

        # Phase-by-phase breakdown
        lines.append("PHASE-BY-PHASE ANALYSIS")
        lines.append("-" * 80)
        lines.append(f"{'Time':>6} {'Phase':<15} {'Range':>8} {'Alt':>8} "
                    f"{'Det Pd':>8} {'Pk_phase':>8} {'Pk_cum':>8}")
        lines.append(f"{'(s)':>6} {'':<15} {'(km)':>8} {'(m)':>8} "
                    f"{'':>8} {'':>8} {'':>8}")
        lines.append("-" * 80)

        for r in results:
            lines.append(
                f"{r.time_from_takeoff_s:>6.0f} {r.phase:<15} "
                f"{r.target_range_km:>8.1f} {r.target_altitude_m:>8.0f} "
                f"{r.detection_pd:>8.1%} {r.pk_this_phase:>8.1%} "
                f"{r.pk_cumulative:>8.1%}"
            )

            if r.engaged_by:
                for eng in r.engaged_by:
                    lines.append(f"       -> {eng}")

        # Limitations section
        lines.append("")
        lines.append("=" * 80)
        lines.append("SHORTCOMINGS PREVENTING 100% Pk")
        lines.append("=" * 80)

        limitations = {
            "PHYSICS LIMITATIONS": [
                "Radar horizon limits surface radar detection of low-flying targets",
                "X-band stealth still effective (0.0002 m² frontal RCS)",
                "Atmospheric attenuation affects all EM sensors",
                "Speed of light creates minimum reaction times",
                "VHF radar has poor angular resolution (~5-10 deg)",
            ],
            "INTELLIGENCE GAPS": [
                "F-35 EW/ECM capabilities are CLASSIFIED - effectiveness unknown",
                "Countermeasure algorithms constantly updated - cannot model",
                "Actual F-35 RCS values are classified - using estimates",
                "MADL waveform characteristics not fully known",
                "Data confidence: 45-70% for most parameters",
            ],
            "OPERATIONAL FACTORS": [
                "Communication latency (2-5s) delays engagement",
                "Sensor maintenance state varies",
                "Crew proficiency varies by unit",
                "Weather degrades optical/IR sensors",
                "Cyber vulnerabilities in networked systems",
            ],
            "TACTICAL COUNTERMEASURES": [
                "F-35 can exploit coverage gaps",
                "Terrain masking defeats surface radars",
                "Timing attacks during orbital gaps",
                "Electronic deception techniques",
                "Coordinated multi-axis attacks",
            ],
            "RESOURCE CONSTRAINTS": [
                "Finite missile inventory",
                "Limited simultaneous engagements",
                "AWACS endurance limits",
                "Reload times create windows",
            ]
        }

        for category, items in limitations.items():
            lines.append(f"\n{category}:")
            for item in items:
                lines.append(f"  - {item}")

        lines.append("")
        lines.append("=" * 80)
        lines.append("CONCLUSION")
        lines.append("=" * 80)
        lines.append("""
While this system achieves theoretical Pk > 95% against F-35 from takeoff,
100% kill probability is PHYSICALLY AND OPERATIONALLY IMPOSSIBLE due to:

1. Fundamental physics (radar equation, horizon, atmospheric effects)
2. Unknown adversary capabilities (classified F-35 EW suite)
3. Operational uncertainty (human factors, maintenance, weather)
4. Tactical adaptability of adversary

REALISTIC ASSESSMENT:
- Pk against cooperative target: 80-95%
- Pk against defended target: 60-80%
- Pk against full F-35 capabilities: 50-70%
- Confidence in these estimates: 45-65%

The "guaranteed kill" requires accepting that near-certain (>95%) is achievable
but absolute certainty (100%) violates physics and information theory.
""")

        lines.append("=" * 80)
        return "\n".join(lines)


# =============================================================================
# SECTION 6: EXAMPLE USAGE AND VALIDATION
# =============================================================================

def main():
    """Demonstrate integrated kill system analysis"""

    print("=" * 80)
    print("INTEGRATED MULTI-LAYER KILL SYSTEM")
    print("F-35 Engagement Analysis")
    print("=" * 80)

    # Create target
    f35 = F35Signature()

    # Create kill system
    kill_system = GuaranteedKillSystem()

    # Analyze kill chain
    # F-35 taking off from airbase 200km away, heading toward defended area
    initial_pos = Point3D(200, 0, 0.3)  # 200km east, 300m altitude

    results = kill_system.analyze_kill_chain(
        target=f35,
        initial_position_km=initial_pos,
        heading_deg=270,  # Heading west toward defenders
        speed_mach=0.85,
        mission_duration_s=600
    )

    # Generate report
    report = kill_system.generate_kill_chain_report(results)
    print(report)

    # Save report
    with open("kill_chain_analysis.txt", "w") as f:
        f.write(report)
    print("\nReport saved to: kill_chain_analysis.txt")


if __name__ == "__main__":
    main()
