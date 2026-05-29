#!/usr/bin/env python3
"""
Aspect-Dependent Radar Cross Section (RCS) Models

Implements realistic RCS calculations for stealth aircraft based on viewing
geometry. RCS varies dramatically (10-100×) depending on aspect angle.

Key Insight:
- Frontal RCS: Highly optimized, minimum value
- Beam RCS: Flat fuselage sides, 10-50× larger
- Rear RCS: Engine nozzles, moderate values

Models Defined in this File:

✓ OPERATIONALLY VERIFIED (Approved for CI/CD Testing):
  - F35ARCSModel:     F-35A Lightning II (fielded 2015, 55% confidence)
  - J20RCSModel:      J-20 Mighty Dragon (fielded 2017, 50% confidence)

✗ NOT OPERATIONALLY VERIFIED (Excluded from CI/CD Testing):
  - MQ28RCSModel:     MQ-28 Ghost Bat (development, not deployed, 40% confidence)
  - SixthGenRCSModel: NGAD 6th-Gen Fighter (concept, not fielded, 20% confidence)

IMPORTANT: Only F35ARCSModel and J20RCSModel should be imported and used in
tests, simulations, and operational CAD assessments. The excluded models are
defined for research purposes only.

See VERIFIED_MODELS_REGISTRY.md for the authoritative list of approved models
and verification criteria.

Classification: UNCLASSIFIED // PUBLIC RELEASE
All RCS values are estimates from public sources with uncertainty quantification.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class RCSEstimate:
    """RCS calculation result with uncertainty"""
    rcs_m2: float  # RCS in square meters
    rcs_dbsm: float  # RCS in dBsm
    azimuth_deg: float  # Viewing azimuth angle
    elevation_deg: float  # Viewing elevation angle
    confidence: float  # 0-1, confidence in estimate


def rcs_linear_to_dbsm(rcs_m2: float) -> float:
    """
    Convert RCS from m² to dBsm.

    Args:
        rcs_m2: RCS in square meters (must be positive for valid conversion)

    Returns:
        RCS in dBsm. Returns -100.0 for non-positive inputs.

    Raises:
        ValueError: If rcs_m2 is NaN
    """
    if np.isnan(rcs_m2):
        raise ValueError("RCS value cannot be NaN")
    if rcs_m2 <= 0:
        return -100.0
    return 10 * np.log10(rcs_m2)


def rcs_dbsm_to_linear(rcs_dbsm: float) -> float:
    """
    Convert RCS from dBsm to m².

    Args:
        rcs_dbsm: RCS in dBsm

    Returns:
        RCS in square meters (always positive)

    Raises:
        ValueError: If rcs_dbsm is NaN
    """
    if np.isnan(rcs_dbsm):
        raise ValueError("RCS value cannot be NaN")
    return 10 ** (rcs_dbsm / 10.0)


def calculate_aspect_angles(radar_position: np.ndarray,
                           target_position: np.ndarray,
                           target_velocity: np.ndarray) -> Tuple[float, float]:
    """
    Calculate aspect angles from radar to target

    Args:
        radar_position: Radar position [x, y, z] in world frame (meters)
        target_position: Target position [x, y, z] in world frame (meters)
        target_velocity: Target velocity [vx, vy, vz] in world frame (m/s)

    Returns:
        Tuple of (azimuth_deg, elevation_deg)
        - azimuth: 0° = nose-on, 90° = beam, 180° = tail-on
        - elevation: 0° = level, +90° = top view, -90° = bottom view
    """
    # Line-of-sight vector from target to radar
    los_vector = radar_position - target_position
    los_range = np.linalg.norm(los_vector)

    if los_range < 1.0:  # Avoid division by zero
        return 0.0, 0.0

    los_unit = los_vector / los_range

    # Target heading (velocity direction)
    target_speed = np.linalg.norm(target_velocity)

    if target_speed < 1.0:  # Target nearly stationary
        # Use LOS azimuth relative to north
        azimuth_rad = np.arctan2(los_vector[1], los_vector[0])
        azimuth_deg = np.degrees(azimuth_rad)
    else:
        target_heading = target_velocity / target_speed

        # Azimuth: angle between target heading and LOS
        # Clamp dot product to [-1, 1] to avoid numerical errors
        dot_product = np.clip(np.dot(target_heading, los_unit), -1.0, 1.0)
        azimuth_rad = np.arccos(dot_product)
        azimuth_deg = np.degrees(azimuth_rad)

    # Elevation: angle above/below horizontal
    los_horizontal = np.array([los_unit[0], los_unit[1], 0])
    los_horizontal_mag = np.linalg.norm(los_horizontal)

    if los_horizontal_mag > 0.001:
        elevation_rad = np.arctan2(-los_unit[2], los_horizontal_mag)  # Note: -z because +z is down
        elevation_deg = np.degrees(elevation_rad)
    else:
        # Radar directly above or below target
        elevation_deg = 90.0 if los_unit[2] < 0 else -90.0

    return azimuth_deg, elevation_deg


class F35ARCSModel:
    """
    Aspect-dependent RCS model for F-35A Lightning II

    Based on public sources:
    - Frontal: 0.0001-0.0005 m² ("golf ball sized")
    - Beam: 0.01-0.05 m² (flat fuselage sides)
    - Rear: 0.003-0.01 m² (engine nozzle partially shielded)

    Confidence: 55% (wide uncertainty due to classification)
    """

    # Reference RCS values (m²) - best estimates
    RCS_FRONTAL = 0.0002  # -37 dBsm
    RCS_BEAM = 0.02       # -17 dBsm
    RCS_REAR = 0.005      # -23 dBsm
    RCS_DORSAL = 0.008    # -21 dBsm (top view)
    RCS_VENTRAL = 0.01    # -20 dBsm (bottom, weapon bays)

    # Uncertainty bounds (±1 sigma)
    RCS_FRONTAL_UNCERTAINTY = 0.0002  # ±100%
    RCS_BEAM_UNCERTAINTY = 0.015      # ±75%
    RCS_REAR_UNCERTAINTY = 0.0035     # ±70%

    # Frequency scaling
    FREQUENCY_SCALING_EXPONENT = 0.5  # RCS ∝ f^0.5
    REFERENCE_FREQUENCY_GHZ = 10.0

    @classmethod
    def calculate_rcs(cls,
                     azimuth_deg: float,
                     elevation_deg: float,
                     frequency_ghz: float = 10.0,
                     polarization: str = 'vertical') -> RCSEstimate:
        """
        Calculate F-35A RCS for given viewing geometry

        Args:
            azimuth_deg: Horizontal angle from nose (0° = head-on, 180° = tail)
            elevation_deg: Vertical angle (0° = level, +90° = top, -90° = bottom)
            frequency_ghz: Radar frequency (GHz)
            polarization: 'vertical' or 'horizontal'

        Returns:
            RCSEstimate with RCS value and confidence
        """
        # Normalize azimuth to [0, 180]
        azimuth = np.abs(azimuth_deg) % 360
        if azimuth > 180:
            azimuth = 360 - azimuth

        # Clamp elevation to [-90, 90]
        elevation = np.clip(elevation_deg, -90, 90)

        # Horizontal plane RCS (elevation = 0°)
        rcs_horizontal, confidence_h = cls._calculate_horizontal_rcs(azimuth)

        # Vertical correction
        rcs, confidence_v = cls._apply_vertical_correction(
            rcs_horizontal, elevation)

        # Combine confidence factors
        confidence = confidence_h * confidence_v * 0.55  # Base confidence 55%

        # Frequency scaling
        freq_factor = (frequency_ghz / cls.REFERENCE_FREQUENCY_GHZ) ** cls.FREQUENCY_SCALING_EXPONENT
        rcs *= freq_factor

        # Polarization factor
        if polarization == 'horizontal':
            rcs *= 0.5  # -3 dB for cross-pol
            confidence *= 0.8

        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(
            rcs_m2=rcs,
            rcs_dbsm=rcs_dbsm,
            azimuth_deg=azimuth,
            elevation_deg=elevation,
            confidence=confidence
        )

    @classmethod
    def _calculate_horizontal_rcs(cls, azimuth: float) -> Tuple[float, float]:
        """Calculate RCS in horizontal plane, return (rcs, confidence)"""
        if azimuth <= 30:
            # Frontal sector (0-30°) - highly optimized
            rcs = cls.RCS_FRONTAL
            confidence = 0.8

        elif azimuth <= 60:
            # Forward quarter (30-60°) - transition to beam
            t = (azimuth - 30) / 30.0
            rcs = cls.RCS_FRONTAL * (1 - t) + cls.RCS_BEAM * 0.3 * t
            confidence = 0.7

        elif azimuth <= 120:
            # Beam aspect (60-120°) - maximum RCS
            t = (azimuth - 60) / 60.0
            # Sinusoidal peak around 90°
            beam_factor = 0.3 + 0.7 * np.sin(t * np.pi)
            rcs = cls.RCS_BEAM * beam_factor
            confidence = 0.6

        elif azimuth <= 150:
            # Rear quarter (120-150°) - transition to rear
            t = (azimuth - 120) / 30.0
            rcs = cls.RCS_BEAM * 0.3 * (1 - t) + cls.RCS_REAR * t
            confidence = 0.5

        else:
            # Rear sector (150-180°) - engine nozzles
            rcs = cls.RCS_REAR
            confidence = 0.5

        return rcs, confidence

    @classmethod
    def _apply_vertical_correction(cls, rcs_horizontal: float,
                                   elevation: float) -> Tuple[float, float]:
        """Apply vertical angle correction, return (rcs, confidence)"""
        abs_elevation = np.abs(elevation)

        if abs_elevation < 30:
            # Near horizontal - use horizontal plane RCS
            return rcs_horizontal, 1.0

        elif abs_elevation < 60:
            # Oblique angle - interpolate toward dorsal/ventral
            t = (abs_elevation - 30) / 30.0

            if elevation > 0:
                rcs_vertical = cls.RCS_DORSAL
            else:
                rcs_vertical = cls.RCS_VENTRAL

            rcs = rcs_horizontal * (1 - t) + rcs_vertical * t
            confidence = 1.0 - 0.2 * t  # Slightly less confident off-level

            return rcs, confidence

        else:
            # Near vertical (top or bottom view)
            if elevation > 0:
                rcs = cls.RCS_DORSAL
            else:
                rcs = cls.RCS_VENTRAL

            return rcs, 0.7  # Lower confidence for vertical aspects

    @classmethod
    def calculate_rcs_from_vectors(cls,
                                   radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """
        Calculate F-35A RCS from 3D position/velocity vectors

        Args:
            radar_position: Radar position [x, y, z] (meters)
            target_position: F-35 position [x, y, z] (meters)
            target_velocity: F-35 velocity [vx, vy, vz] (m/s)
            frequency_ghz: Radar frequency (GHz)

        Returns:
            RCSEstimate
        """
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)

        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class MQ28RCSModel:
    """
    Aspect-dependent RCS model for MQ-28A Ghost Bat

    Estimates based on:
    - Smaller size than F-35 (11m vs 15.7m)
    - Unmanned design (simpler shaping constraints)
    - Less mature stealth technology

    Estimated RCS:
    - Frontal: 0.001-0.005 m²
    - Beam: 0.05-0.1 m²
    - Rear: 0.01-0.02 m²

    Confidence: 40% (very limited public data)
    """

    # Reference RCS values (m²)
    RCS_FRONTAL = 0.002   # -27 dBsm
    RCS_BEAM = 0.07       # -11.5 dBsm
    RCS_REAR = 0.015      # -18 dBsm
    RCS_DORSAL = 0.03     # -15 dBsm
    RCS_VENTRAL = 0.04    # -14 dBsm

    FREQUENCY_SCALING_EXPONENT = 0.3  # Smaller size → less frequency dependence
    REFERENCE_FREQUENCY_GHZ = 10.0

    @classmethod
    def calculate_rcs(cls,
                     azimuth_deg: float,
                     elevation_deg: float,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate MQ-28 RCS (similar structure to F35ARCSModel)"""

        azimuth = np.abs(azimuth_deg) % 360
        if azimuth > 180:
            azimuth = 360 - azimuth
        elevation = np.clip(elevation_deg, -90, 90)

        # Simplified model (less public data available)
        if azimuth <= 45:
            rcs_horizontal = cls.RCS_FRONTAL
            confidence = 0.5
        elif azimuth <= 135:
            # Beam aspect dominant
            t = (azimuth - 45) / 90.0
            rcs_horizontal = cls.RCS_FRONTAL + (cls.RCS_BEAM - cls.RCS_FRONTAL) * t
            confidence = 0.4
        else:
            # Rear aspect
            t = (azimuth - 135) / 45.0
            rcs_horizontal = cls.RCS_BEAM + (cls.RCS_REAR - cls.RCS_BEAM) * t
            confidence = 0.3

        # Vertical correction
        abs_elevation = np.abs(elevation)
        if abs_elevation > 45:
            t = (abs_elevation - 45) / 45.0
            rcs_vertical = cls.RCS_DORSAL if elevation > 0 else cls.RCS_VENTRAL
            rcs = rcs_horizontal * (1 - t) + rcs_vertical * t
            confidence *= 0.8
        else:
            rcs = rcs_horizontal

        # Frequency scaling
        freq_factor = (frequency_ghz / cls.REFERENCE_FREQUENCY_GHZ) ** cls.FREQUENCY_SCALING_EXPONENT
        rcs *= freq_factor

        # Apply base confidence factor
        confidence *= 0.40  # Base confidence 40%

        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(
            rcs_m2=rcs,
            rcs_dbsm=rcs_dbsm,
            azimuth_deg=azimuth,
            elevation_deg=elevation,
            confidence=confidence
        )

    @classmethod
    def calculate_rcs_from_vectors(cls,
                                   radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate MQ-28 RCS from 3D vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)

        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class SixthGenRCSModel:
    """
    Aspect-dependent RCS model for 6th-generation fighter (NGAD concept)

    Speculative estimates for next-generation stealth:
    - Post-2030 technology
    - Tailless design (reduces rear RCS)
    - Advanced metamaterials
    - Larger size (F-22 class or bigger)

    Estimated RCS (highly speculative):
    - Frontal: 0.00005-0.0001 m²
    - Beam: 0.005-0.01 m²
    - Rear: 0.001-0.002 m²

    Confidence: 20% (concept-level, not fielded)
    """

    # Reference RCS values (m²) - HIGHLY SPECULATIVE
    RCS_FRONTAL = 0.00008  # -41 dBsm
    RCS_BEAM = 0.008       # -21 dBsm
    RCS_REAR = 0.0015      # -28 dBsm
    RCS_DORSAL = 0.003     # -25 dBsm
    RCS_VENTRAL = 0.004    # -24 dBsm

    FREQUENCY_SCALING_EXPONENT = 0.4
    REFERENCE_FREQUENCY_GHZ = 10.0

    @classmethod
    def calculate_rcs(cls,
                     azimuth_deg: float,
                     elevation_deg: float,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate 6th-gen fighter RCS"""

        azimuth = np.abs(azimuth_deg) % 360
        if azimuth > 180:
            azimuth = 360 - azimuth
        elevation = np.clip(elevation_deg, -90, 90)

        # Advanced shaping → smoother transition
        if azimuth <= 40:
            rcs_horizontal = cls.RCS_FRONTAL
            confidence = 0.3
        elif azimuth <= 70:
            t = (azimuth - 40) / 30.0
            rcs_horizontal = cls.RCS_FRONTAL + (cls.RCS_BEAM * 0.4 - cls.RCS_FRONTAL) * t
            confidence = 0.25
        elif azimuth <= 110:
            # Beam aspect (lower peak than legacy stealth)
            t = (azimuth - 70) / 40.0
            rcs_horizontal = cls.RCS_BEAM * (0.4 + 0.6 * np.sin(t * np.pi))
            confidence = 0.2
        elif azimuth <= 140:
            t = (azimuth - 110) / 30.0
            rcs_horizontal = cls.RCS_BEAM * 0.4 * (1 - t) + cls.RCS_REAR * t
            confidence = 0.15
        else:
            rcs_horizontal = cls.RCS_REAR
            confidence = 0.15

        # Vertical correction
        abs_elevation = np.abs(elevation)
        if abs_elevation > 40:
            t = (abs_elevation - 40) / 50.0
            rcs_vertical = cls.RCS_DORSAL if elevation > 0 else cls.RCS_VENTRAL
            rcs = rcs_horizontal * (1 - t) + rcs_vertical * t
            confidence *= 0.7
        else:
            rcs = rcs_horizontal

        # Frequency scaling
        freq_factor = (frequency_ghz / cls.REFERENCE_FREQUENCY_GHZ) ** cls.FREQUENCY_SCALING_EXPONENT
        rcs *= freq_factor

        # Apply base confidence factor
        confidence *= 0.20  # Base confidence 20%

        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(
            rcs_m2=rcs,
            rcs_dbsm=rcs_dbsm,
            azimuth_deg=azimuth,
            elevation_deg=elevation,
            confidence=confidence
        )

    @classmethod
    def calculate_rcs_from_vectors(cls,
                                   radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate 6th-gen fighter RCS from 3D vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)

        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class J20RCSModel:
    """
    Aspect-dependent RCS model for J-20 Mighty Dragon (Chinese 5th-gen)

    Based on public sources and observable features:
    - Larger than F-35 (20.3m length, canard-delta configuration)
    - Canards increase frontal and beam RCS compared to conventional designs
    - Forward-swept intake edges (some radar blocker visible)
    - Serrated edges on control surfaces
    - Less mature RAM (Radar Absorbent Material) than US equivalents

    Observable facts from public imagery:
    - Canard span: ~4m, area ~3m² per side
    - Intake size: ~0.8m x 1.0m
    - Overall length: 20.3m (vs F-35: 15.7m)
    - Wing area: ~78m² (larger planform)

    Estimated RCS (based on scaling from F-35 with canard penalty):
    - Frontal: 0.001-0.003 m² (canards add ~3-5× over tailless)
    - Beam: 0.05-0.15 m² (large flat fuselage + canards)
    - Rear: 0.008-0.02 m² (exposed engine nozzles)

    Confidence: 50% (moderate public data, some observables available)

    Deductive reasoning:
    1. Canard RCS contribution (frontal): ~0.0005 m² per canard @ 10 GHz
    2. Intake RCS (without perfect blocker): ~0.0003 m²
    3. Fuselage faceting: Similar to F-35 but larger → 1.5× scaling
    4. RAM effectiveness: Estimated 80-90% of US capability → 1.2× RCS
    5. Total frontal: 0.0002 (baseline) × 1.5 (size) × 1.2 (RAM) + 0.001 (canards) = 0.0014 m²
    """

    # Reference RCS values (m²) - best estimates
    RCS_FRONTAL = 0.0014   # -28.5 dBsm (includes canard contribution)
    RCS_BEAM = 0.08        # -11 dBsm (large fuselage + canards)
    RCS_REAR = 0.012       # -19 dBsm (partially shielded nozzles)
    RCS_DORSAL = 0.02      # -17 dBsm (top view, canards visible)
    RCS_VENTRAL = 0.025    # -16 dBsm (bottom, weapon bays)

    # Uncertainty bounds (±1 sigma)
    RCS_FRONTAL_UNCERTAINTY = 0.001    # ±71%
    RCS_BEAM_UNCERTAINTY = 0.04        # ±50%
    RCS_REAR_UNCERTAINTY = 0.006       # ±50%

    # Frequency scaling (larger aircraft → more frequency dependent)
    FREQUENCY_SCALING_EXPONENT = 0.6
    REFERENCE_FREQUENCY_GHZ = 10.0

    @classmethod
    def calculate_rcs(cls,
                     azimuth_deg: float,
                     elevation_deg: float,
                     frequency_ghz: float = 10.0,
                     polarization: str = 'vertical') -> RCSEstimate:
        """
        Calculate J-20 RCS for given viewing geometry

        Args:
            azimuth_deg: Horizontal angle from nose (0° = head-on, 180° = tail)
            elevation_deg: Vertical angle (0° = level, +90° = top, -90° = bottom)
            frequency_ghz: Radar frequency (GHz)
            polarization: 'vertical' or 'horizontal'

        Returns:
            RCSEstimate with RCS value and confidence
        """
        # Normalize azimuth to [0, 180]
        azimuth = np.abs(azimuth_deg) % 360
        if azimuth > 180:
            azimuth = 360 - azimuth

        # Clamp elevation to [-90, 90]
        elevation = np.clip(elevation_deg, -90, 90)

        # Horizontal plane RCS (elevation = 0°)
        rcs_horizontal, confidence_h = cls._calculate_horizontal_rcs(azimuth)

        # Vertical correction
        rcs, confidence_v = cls._apply_vertical_correction(
            rcs_horizontal, elevation)

        # Combine confidence factors
        confidence = confidence_h * confidence_v * 0.50  # Base confidence 50%

        # Frequency scaling
        freq_factor = (frequency_ghz / cls.REFERENCE_FREQUENCY_GHZ) ** cls.FREQUENCY_SCALING_EXPONENT
        rcs *= freq_factor

        # Polarization factor
        if polarization == 'horizontal':
            rcs *= 0.6  # -2.2 dB for cross-pol (canards affect polarization)
            confidence *= 0.85

        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(
            rcs_m2=rcs,
            rcs_dbsm=rcs_dbsm,
            azimuth_deg=azimuth,
            elevation_deg=elevation,
            confidence=confidence
        )

    @classmethod
    def _calculate_horizontal_rcs(cls, azimuth: float) -> Tuple[float, float]:
        """Calculate RCS in horizontal plane, return (rcs, confidence)"""
        if azimuth <= 25:
            # Frontal sector (0-25°) - canards dominate
            rcs = cls.RCS_FRONTAL
            confidence = 0.75

        elif azimuth <= 55:
            # Forward quarter (25-55°) - transition to beam, canards at angle
            t = (azimuth - 25) / 30.0
            # Canards contribute more at oblique angles
            canard_factor = 1.0 + 0.5 * t
            rcs = cls.RCS_FRONTAL * (1 - t) * canard_factor + cls.RCS_BEAM * 0.2 * t
            confidence = 0.65

        elif azimuth <= 125:
            # Beam aspect (55-125°) - maximum RCS from fuselage + canards
            t = (azimuth - 55) / 70.0
            # Peak RCS at 90° beam aspect
            beam_factor = 0.2 + 0.8 * np.sin(t * np.pi)
            rcs = cls.RCS_BEAM * beam_factor
            confidence = 0.55

        elif azimuth <= 155:
            # Rear quarter (125-155°) - transition to rear
            t = (azimuth - 125) / 30.0
            rcs = cls.RCS_BEAM * 0.2 * (1 - t) + cls.RCS_REAR * t
            confidence = 0.45

        else:
            # Rear sector (155-180°) - engine nozzles visible
            rcs = cls.RCS_REAR
            confidence = 0.45

        return rcs, confidence

    @classmethod
    def _apply_vertical_correction(cls, rcs_horizontal: float,
                                   elevation: float) -> Tuple[float, float]:
        """Apply vertical angle correction, return (rcs, confidence)"""
        abs_elevation = np.abs(elevation)

        if abs_elevation < 25:
            # Near horizontal - use horizontal plane RCS
            return rcs_horizontal, 1.0

        elif abs_elevation < 55:
            # Oblique angle - interpolate toward dorsal/ventral
            t = (abs_elevation - 25) / 30.0

            if elevation > 0:
                # Top view - canards very visible
                rcs_vertical = cls.RCS_DORSAL
            else:
                # Bottom view - weapon bays
                rcs_vertical = cls.RCS_VENTRAL

            rcs = rcs_horizontal * (1 - t) + rcs_vertical * t
            confidence = 1.0 - 0.25 * t  # Less confident for oblique angles

            return rcs, confidence

        else:
            # Near vertical (top or bottom view)
            if elevation > 0:
                # Top view - canards add significant RCS
                rcs = cls.RCS_DORSAL
            else:
                # Bottom view
                rcs = cls.RCS_VENTRAL

            return rcs, 0.65  # Moderate confidence for vertical aspects

    @classmethod
    def calculate_rcs_from_vectors(cls,
                                   radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """
        Calculate J-20 RCS from 3D position/velocity vectors

        Args:
            radar_position: Radar position [x, y, z] (meters)
            target_position: J-20 position [x, y, z] (meters)
            target_velocity: J-20 velocity [vx, vy, vz] (m/s)
            frequency_ghz: Radar frequency (GHz)

        Returns:
            RCSEstimate
        """
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)

        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class J10CRCSModel:
    """
    J-10C Vigorous Dragon RCS Model

    Operational Status: VERIFIED - Fielded 2006 (J-10A), upgraded J-10C 2015
    Confidence: 55%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: Delta-canard configuration analysis from public imagery and deductive reasoning

    See docs/PARAMETER_ESTIMATES.md Part 7.1 for detailed parameter derivation
    """

    # Frontal RCS estimates (clean configuration)
    RCS_FRONTAL = 1.2e-0  # 1.2 m² (-0.8 dBsm) - conventional fighter with canards
    RCS_BEAM = 5.0e-0  # 5.0 m² (7.0 dBsm) - beam aspect (wings)
    RCS_TAIL = 3.0e-0  # 3.0 m² (4.8 dBsm) - tail aspect (engine nozzle)
    RCS_DORSAL = 4.0e-0  # 4.0 m² (6.0 dBsm) - top view
    RCS_VENTRAL = 3.5e-0  # 3.5 m² (5.4 dBsm) - bottom view

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate J-10C RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            # Horizontal aspects (azimuth dominant)
            if azimuth < 30 or azimuth > 330:
                # Frontal aspect
                return cls.RCS_FRONTAL, 0.55
            elif 150 < azimuth < 210:
                # Tail aspect
                return cls.RCS_TAIL, 0.60
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                # Beam aspect
                return cls.RCS_BEAM, 0.60
            else:
                # Oblique aspects - interpolate
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.50
        else:
            # Vertical aspects
            if elevation > 0:
                return cls.RCS_DORSAL, 0.55
            else:
                return cls.RCS_VENTRAL, 0.55

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate J-10C RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class J11BRCSModel:
    """
    J-11B Flanker RCS Model (Chinese Su-27 variant)

    Operational Status: VERIFIED - Fielded 2007
    Confidence: 60%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: Large 4th-gen airframe analysis, similar to Su-27

    See docs/PARAMETER_ESTIMATES.md Part 7.2 for detailed parameter derivation
    """

    RCS_FRONTAL = 8.0e-0  # 8 m² (9.0 dBsm) - large airframe, twin intakes
    RCS_BEAM = 25.0e-0  # 25 m² (14.0 dBsm) - very large beam aspect
    RCS_TAIL = 12.0e-0  # 12 m² (10.8 dBsm) - twin engines
    RCS_DORSAL = 20.0e-0  # 20 m² (13.0 dBsm) - top view
    RCS_VENTRAL = 15.0e-0  # 15 m² (11.8 dBsm) - bottom view

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate J-11B RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            if azimuth < 30 or azimuth > 330:
                return cls.RCS_FRONTAL, 0.60
            elif 150 < azimuth < 210:
                return cls.RCS_TAIL, 0.65
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                return cls.RCS_BEAM, 0.65
            else:
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.55
        else:
            if elevation > 0:
                return cls.RCS_DORSAL, 0.60
            else:
                return cls.RCS_VENTRAL, 0.60

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate J-11B RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class J15RCSModel:
    """
    J-15 Flying Shark RCS Model (Carrier fighter)

    Operational Status: VERIFIED - Fielded 2013
    Confidence: 55%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: Carrier-capable J-11 variant with reinforced airframe

    See docs/PARAMETER_ESTIMATES.md Part 7.3 for detailed parameter derivation
    """

    RCS_FRONTAL = 9.0e-0  # 9 m² (9.5 dBsm) - larger than J-11B
    RCS_BEAM = 28.0e-0  # 28 m² (14.5 dBsm) - folding wings add complexity
    RCS_TAIL = 13.0e-0  # 13 m² (11.1 dBsm) - arresting hook
    RCS_DORSAL = 22.0e-0  # 22 m² (13.4 dBsm)
    RCS_VENTRAL = 18.0e-0  # 18 m² (12.6 dBsm)

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate J-15 RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            if azimuth < 30 or azimuth > 330:
                return cls.RCS_FRONTAL, 0.55
            elif 150 < azimuth < 210:
                return cls.RCS_TAIL, 0.60
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                return cls.RCS_BEAM, 0.60
            else:
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.50
        else:
            if elevation > 0:
                return cls.RCS_DORSAL, 0.55
            else:
                return cls.RCS_VENTRAL, 0.55

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate J-15 RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class J16RCSModel:
    """
    J-16 Red Eagle RCS Model (Strike fighter)

    Operational Status: VERIFIED - Fielded 2015
    Confidence: 55%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: J-11BS airframe with RAM coatings and modernization

    See docs/PARAMETER_ESTIMATES.md Part 7.4 for detailed parameter derivation
    """

    RCS_FRONTAL = 7.0e-0  # 7 m² (8.5 dBsm) - RAM coatings reduce RCS
    RCS_BEAM = 22.0e-0  # 22 m² (13.4 dBsm)
    RCS_TAIL = 11.0e-0  # 11 m² (10.4 dBsm)
    RCS_DORSAL = 18.0e-0  # 18 m² (12.6 dBsm)
    RCS_VENTRAL = 14.0e-0  # 14 m² (11.5 dBsm)

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate J-16 RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            if azimuth < 30 or azimuth > 330:
                return cls.RCS_FRONTAL, 0.60
            elif 150 < azimuth < 210:
                return cls.RCS_TAIL, 0.65
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                return cls.RCS_BEAM, 0.65
            else:
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.55
        else:
            if elevation > 0:
                return cls.RCS_DORSAL, 0.60
            else:
                return cls.RCS_VENTRAL, 0.60

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate J-16 RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class Su35RCSModel:
    """
    Su-35 Flanker-E RCS Model (4++ Generation)

    Operational Status: VERIFIED - Fielded 2014 (Russia), 2018 (China import)
    Confidence: 65%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: Advanced Su-27 variant with RCS reduction measures

    See docs/PARAMETER_ESTIMATES.md Part 7.5 for detailed parameter derivation
    """

    RCS_FRONTAL = 1.0e-0  # 1.0 m² (0.0 dBsm) - RAM coatings, improved design
    RCS_BEAM = 8.0e-0  # 8 m² (9.0 dBsm) - still large airframe
    RCS_TAIL = 5.0e-0  # 5 m² (7.0 dBsm) - improved engine nozzles
    RCS_DORSAL = 6.0e-0  # 6 m² (7.8 dBsm)
    RCS_VENTRAL = 5.0e-0  # 5 m² (7.0 dBsm)

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate Su-35 RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            if azimuth < 30 or azimuth > 330:
                return cls.RCS_FRONTAL, 0.65
            elif 150 < azimuth < 210:
                return cls.RCS_TAIL, 0.70
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                return cls.RCS_BEAM, 0.70
            else:
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.65
        else:
            if elevation > 0:
                return cls.RCS_DORSAL, 0.65
            else:
                return cls.RCS_VENTRAL, 0.65

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate Su-35 RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class H6KRCSModel:
    """
    H-6K Badger RCS Model (Strategic bomber)

    Operational Status: VERIFIED - Fielded 2009
    Confidence: 65%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: Large 1950s-era bomber with modern RAM coatings

    See docs/PARAMETER_ESTIMATES.md Part 7.6 for detailed parameter derivation
    """

    RCS_FRONTAL = 50.0e-0  # 50 m² (17.0 dBsm) - large bomber
    RCS_BEAM = 100.0e-0  # 100 m² (20.0 dBsm) - massive beam aspect
    RCS_TAIL = 60.0e-0  # 60 m² (17.8 dBsm) - twin engines
    RCS_DORSAL = 80.0e-0  # 80 m² (19.0 dBsm)
    RCS_VENTRAL = 70.0e-0  # 70 m² (18.5 dBsm)

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate H-6K RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            if azimuth < 30 or azimuth > 330:
                return cls.RCS_FRONTAL, 0.65
            elif 150 < azimuth < 210:
                return cls.RCS_TAIL, 0.70
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                return cls.RCS_BEAM, 0.70
            else:
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.65
        else:
            if elevation > 0:
                return cls.RCS_DORSAL, 0.65
            else:
                return cls.RCS_VENTRAL, 0.65

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate H-6K RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class Su57RCSModel:
    """
    Su-57 Felon RCS Model (5th Generation)

    Operational Status: VERIFIED - Fielded 2020
    Confidence: 50%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: Stealth fighter with internal weapons bays, less optimized than F-35

    See docs/PARAMETER_ESTIMATES.md Part 8.1 for detailed parameter derivation
    """

    RCS_FRONTAL = 0.3e-0  # 0.3 m² (-5.2 dBsm) - stealth but less than F-35
    RCS_BEAM = 2.0e-0  # 2.0 m² (3.0 dBsm) - stealth shaping
    RCS_TAIL = 1.5e-0  # 1.5 m² (1.8 dBsm) - round nozzles increase RCS
    RCS_DORSAL = 1.0e-0  # 1.0 m² (0.0 dBsm)
    RCS_VENTRAL = 0.8e-0  # 0.8 m² (-1.0 dBsm)

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate Su-57 RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            if azimuth < 30 or azimuth > 330:
                return cls.RCS_FRONTAL, 0.50
            elif 150 < azimuth < 210:
                return cls.RCS_TAIL, 0.55
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                return cls.RCS_BEAM, 0.55
            else:
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.45
        else:
            if elevation > 0:
                return cls.RCS_DORSAL, 0.50
            else:
                return cls.RCS_VENTRAL, 0.50

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate Su-57 RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class Su30SMRCSModel:
    """
    Su-30SM Flanker-H RCS Model (Multirole fighter)

    Operational Status: VERIFIED - Fielded 2012
    Confidence: 65%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: Su-27 airframe with canards

    See docs/PARAMETER_ESTIMATES.md Part 8.3 for detailed parameter derivation
    """

    RCS_FRONTAL = 6.0e-0  # 6 m² (7.8 dBsm) - canards increase frontal RCS
    RCS_BEAM = 20.0e-0  # 20 m² (13.0 dBsm)
    RCS_TAIL = 10.0e-0  # 10 m² (10.0 dBsm)
    RCS_DORSAL = 18.0e-0  # 18 m² (12.6 dBsm)
    RCS_VENTRAL = 14.0e-0  # 14 m² (11.5 dBsm)

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate Su-30SM RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            if azimuth < 30 or azimuth > 330:
                return cls.RCS_FRONTAL, 0.65
            elif 150 < azimuth < 210:
                return cls.RCS_TAIL, 0.70
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                return cls.RCS_BEAM, 0.70
            else:
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.60
        else:
            if elevation > 0:
                return cls.RCS_DORSAL, 0.65
            else:
                return cls.RCS_VENTRAL, 0.65

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate Su-30SM RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class MiG31RCSModel:
    """
    MiG-31 Foxhound RCS Model (Interceptor)

    Operational Status: VERIFIED - Fielded 1981, upgraded MiG-31BM 2011
    Confidence: 70%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: Large 1970s interceptor, designed for speed not stealth

    See docs/PARAMETER_ESTIMATES.md Part 8.4 for detailed parameter derivation
    """

    RCS_FRONTAL = 15.0e-0  # 15 m² (11.8 dBsm) - massive radar nose
    RCS_BEAM = 35.0e-0  # 35 m² (15.4 dBsm) - very large airframe
    RCS_TAIL = 18.0e-0  # 18 m² (12.6 dBsm) - twin engines
    RCS_DORSAL = 30.0e-0  # 30 m² (14.8 dBsm)
    RCS_VENTRAL = 25.0e-0  # 25 m² (14.0 dBsm)

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate MiG-31 RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            if azimuth < 30 or azimuth > 330:
                return cls.RCS_FRONTAL, 0.70
            elif 150 < azimuth < 210:
                return cls.RCS_TAIL, 0.75
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                return cls.RCS_BEAM, 0.75
            else:
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.70
        else:
            if elevation > 0:
                return cls.RCS_DORSAL, 0.70
            else:
                return cls.RCS_VENTRAL, 0.70

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate MiG-31 RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


class Su34RCSModel:
    """
    Su-34 Fullback RCS Model (Strike fighter)

    Operational Status: VERIFIED - Fielded 2014
    Confidence: 65%

    Classification: UNCLASSIFIED // PUBLIC RELEASE
    Basis: Large strike aircraft with platypus nose

    See docs/PARAMETER_ESTIMATES.md Part 8.5 for detailed parameter derivation
    """

    RCS_FRONTAL = 10.0e-0  # 10 m² (10.0 dBsm) - platypus nose
    RCS_BEAM = 30.0e-0  # 30 m² (14.8 dBsm) - large airframe
    RCS_TAIL = 14.0e-0  # 14 m² (11.5 dBsm)
    RCS_DORSAL = 25.0e-0  # 25 m² (14.0 dBsm)
    RCS_VENTRAL = 20.0e-0  # 20 m² (13.0 dBsm)

    @classmethod
    def calculate_rcs(cls, azimuth_deg: float, elevation_deg: float = 0.0,
                     frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate Su-34 RCS for given aspect angles"""
        azimuth = abs(azimuth_deg) % 360
        elevation = elevation_deg

        rcs, confidence = cls._calculate_rcs_aspect(azimuth, elevation)
        rcs_dbsm = rcs_linear_to_dbsm(rcs)

        return RCSEstimate(rcs, rcs_dbsm, azimuth, elevation, confidence)

    @classmethod
    def _calculate_rcs_aspect(cls, azimuth: float, elevation: float) -> Tuple[float, float]:
        """Calculate RCS for specific aspect (internal)"""
        if abs(elevation) < 30:
            if azimuth < 30 or azimuth > 330:
                return cls.RCS_FRONTAL, 0.65
            elif 150 < azimuth < 210:
                return cls.RCS_TAIL, 0.70
            elif 60 < azimuth < 120 or 240 < azimuth < 300:
                return cls.RCS_BEAM, 0.70
            else:
                if azimuth < 180:
                    t = (azimuth - 30) / 60
                    rcs = cls.RCS_FRONTAL + t * (cls.RCS_BEAM - cls.RCS_FRONTAL)
                else:
                    t = (azimuth - 210) / 60
                    rcs = cls.RCS_TAIL + t * (cls.RCS_BEAM - cls.RCS_TAIL)
                return rcs, 0.65
        else:
            if elevation > 0:
                return cls.RCS_DORSAL, 0.65
            else:
                return cls.RCS_VENTRAL, 0.65

    @classmethod
    def calculate_rcs_from_vectors(cls, radar_position: np.ndarray,
                                   target_position: np.ndarray,
                                   target_velocity: np.ndarray,
                                   frequency_ghz: float = 10.0) -> RCSEstimate:
        """Calculate Su-34 RCS from 3D position/velocity vectors"""
        azimuth_deg, elevation_deg = calculate_aspect_angles(
            radar_position, target_position, target_velocity)
        return cls.calculate_rcs(azimuth_deg, elevation_deg, frequency_ghz)


def calculate_detection_range(peak_power_kw: float,
                              antenna_gain_db: float,
                              frequency_ghz: float,
                              target_rcs_m2: float,
                              noise_figure_db: float = 3.0,
                              bandwidth_mhz: float = 1.0,
                              snr_threshold_db: float = 13.0) -> float:
    """
    Calculate radar detection range using radar range equation.

    Uses the standard radar range equation:
    R = [(Pt * G² * λ² * σ) / ((4π)³ * Pmin)]^(1/4)

    Args:
        peak_power_kw: Radar peak transmit power (kW), must be positive
        antenna_gain_db: Antenna gain (dBi)
        frequency_ghz: Radar frequency (GHz), must be positive
        target_rcs_m2: Target RCS (m²), must be positive
        noise_figure_db: Receiver noise figure (dB), default 3.0
        bandwidth_mhz: Receiver bandwidth (MHz), must be positive, default 1.0
        snr_threshold_db: Required SNR for detection (dB), default 13.0

    Returns:
        Detection range (km). Returns 0.0 if calculation is invalid.

    Raises:
        ValueError: If any required positive parameter is non-positive or NaN
    """
    # Input validation
    if peak_power_kw <= 0:
        raise ValueError(f"Peak power must be positive, got {peak_power_kw} kW")
    if frequency_ghz <= 0:
        raise ValueError(f"Frequency must be positive, got {frequency_ghz} GHz")
    if target_rcs_m2 <= 0:
        raise ValueError(f"Target RCS must be positive, got {target_rcs_m2} m²")
    if bandwidth_mhz <= 0:
        raise ValueError(f"Bandwidth must be positive, got {bandwidth_mhz} MHz")

    # Convert to linear units
    peak_power_w = peak_power_kw * 1000
    antenna_gain_linear = 10 ** (antenna_gain_db / 10.0)

    # Wavelength
    wavelength_m = 0.3 / frequency_ghz

    # Noise power
    k_boltzmann = 1.38e-23  # J/K
    temperature_k = 290  # Standard temperature
    noise_figure_linear = 10 ** (noise_figure_db / 10.0)
    bandwidth_hz = bandwidth_mhz * 1e6

    noise_power_w = k_boltzmann * temperature_k * bandwidth_hz * noise_figure_linear

    # Required received power
    snr_linear = 10 ** (snr_threshold_db / 10.0)
    required_rx_power_w = noise_power_w * snr_linear

    # Radar range equation: R = [(Pt * G² * λ² * σ) / ((4π)³ * Pmin)]^(1/4)
    numerator = peak_power_w * (antenna_gain_linear ** 2) * (wavelength_m ** 2) * target_rcs_m2
    denominator = ((4 * np.pi) ** 3) * required_rx_power_w

    if numerator / denominator > 0:
        range_m = (numerator / denominator) ** 0.25
    else:
        range_m = 0

    range_km = range_m / 1000.0

    return range_km


# Example usage and validation
if __name__ == "__main__":
    print("=" * 70)
    print("Aspect-Dependent RCS Models - Validation Tests")
    print("=" * 70)

    # Test 1: F-35 RCS vs aspect angle
    print("\n[TEST 1] F-35A RCS vs Aspect Angle:")
    print("-" * 70)

    aspects = [0, 30, 60, 90, 120, 150, 180]  # Degrees
    for azimuth in aspects:
        result = F35ARCSModel.calculate_rcs(azimuth, elevation_deg=0)
        print(f"  Azimuth {azimuth:3d}°: RCS = {result.rcs_m2:.6f} m² "
              f"({result.rcs_dbsm:+5.1f} dBsm), "
              f"Confidence = {result.confidence:.0%}")

    # Test 2: Detection range variation
    print("\n[TEST 2] J-20 Detection Range vs F-35 Aspect:")
    print("-" * 70)

    j20_peak_power = 14  # kW
    j20_antenna_gain = 35  # dBi
    j20_frequency = 10.0  # GHz

    for azimuth in aspects:
        result = F35ARCSModel.calculate_rcs(azimuth, elevation_deg=0)
        detection_range = calculate_detection_range(
            peak_power_kw=j20_peak_power,
            antenna_gain_db=j20_antenna_gain,
            frequency_ghz=j20_frequency,
            target_rcs_m2=result.rcs_m2
        )
        print(f"  Azimuth {azimuth:3d}°: Detection range = {detection_range:.1f} km "
              f"(RCS = {result.rcs_dbsm:+5.1f} dBsm)")

    # Test 3: Compare aircraft types at beam aspect
    print("\n[TEST 3] Beam Aspect RCS Comparison (90° azimuth):")
    print("-" * 70)

    f35_beam = F35ARCSModel.calculate_rcs(90, 0)
    mq28_beam = MQ28RCSModel.calculate_rcs(90, 0)
    sixthgen_beam = SixthGenRCSModel.calculate_rcs(90, 0)

    print(f"  F-35A:      {f35_beam.rcs_m2:.6f} m² ({f35_beam.rcs_dbsm:+5.1f} dBsm), "
          f"Confidence = {f35_beam.confidence:.0%}")
    print(f"  MQ-28:      {mq28_beam.rcs_m2:.6f} m² ({mq28_beam.rcs_dbsm:+5.1f} dBsm), "
          f"Confidence = {mq28_beam.confidence:.0%}")
    print(f"  6th-Gen:    {sixthgen_beam.rcs_m2:.6f} m² ({sixthgen_beam.rcs_dbsm:+5.1f} dBsm), "
          f"Confidence = {sixthgen_beam.confidence:.0%}")

    # Test 4: Vector-based calculation
    print("\n[TEST 4] RCS from 3D Position Vectors:")
    print("-" * 70)

    # J-20 at origin, heading east
    j20_pos = np.array([0, 0, 12000])

    # F-35 scenarios
    scenarios = [
        ("Head-on", np.array([100000, 0, 12000]), np.array([-250, 0, 0])),
        ("Beam aspect", np.array([100000, 0, 12000]), np.array([0, -250, 0])),
        ("Tail-on", np.array([100000, 0, 12000]), np.array([250, 0, 0])),
    ]

    for name, f35_pos, f35_vel in scenarios:
        result = F35ARCSModel.calculate_rcs_from_vectors(
            j20_pos, f35_pos, f35_vel, frequency_ghz=10.0)

        detection_range = calculate_detection_range(
            14, 35, 10.0, result.rcs_m2)

        print(f"  {name:15s}: Azimuth = {result.azimuth_deg:5.1f}°, "
              f"RCS = {result.rcs_m2:.6f} m² ({result.rcs_dbsm:+5.1f} dBsm), "
              f"Range = {detection_range:.1f} km")

    print("\n" + "=" * 70)
    print("Validation tests complete.")
    print("=" * 70)
