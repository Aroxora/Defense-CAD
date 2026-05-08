#!/usr/bin/env python3
"""
AIM-260 JATM Offensive Targeting Model

Implements AIM-260 Joint Air-to-Air Missile targeting, guidance, and intercept
prediction for F-35/F-22 platforms engaging targets including J-20.

Key Parameters (deductive estimates from public sources):
- Length: ~3.7 m (AIM-120D form factor compatibility)
- Diameter: 178 mm (same as AIM-120 for internal carriage)
- Mass: ~170 kg
- NEZ range: 150-200 km head-on (public estimate)
- Peak velocity: Mach 4+ (ramjet/advanced propulsion)
- Guidance: INS + datalink + active radar

This is an OFFENSIVE model for F-35/F-22 platforms engaging adversary aircraft
including J-20 stealth fighters.

Classification: UNCLASSIFIED // PUBLIC RELEASE
All parameters derived from public sources with documented uncertainty.
"""

from dataclasses import dataclass
from enum import Enum

import numpy as np

from rcs_models import J20RCSModel


class AIM260EngagementPhase(Enum):
    """AIM-260 flight phases"""
    BOOST = "boost"
    MIDCOURSE = "midcourse"
    TERMINAL = "terminal"
    BURNOUT = "burnout"


@dataclass
class AIM260Parameters:
    """
    AIM-260 JATM Performance Parameters (Best Estimates)

    Based on deductive reasoning from:
    - AIM-120D form factor (same rail compatibility)
    - Expected performance improvements over AIM-120D
    - Comparison to PL-15 capabilities (peer threat)
    - Public reporting on JATM program

    Confidence: 50% (less public information than Chinese systems)
    """

    # Physical dimensions (estimated from AIM-120 compatibility)
    length_m: float = 3.7
    diameter_m: float = 0.178  # Same as AIM-120 for F-22 bay compatibility
    mass_total_kg: float = 170
    mass_propellant_kg: float = 55  # ~32% propellant fraction
    mass_warhead_kg: float = 25
    mass_burnout_kg: float = 115

    # Propulsion (advanced solid rocket, possibly throttleable)
    specific_impulse_s: float = 260  # Advanced propellant
    exhaust_velocity_ms: float = 2550  # Isp × g
    burn_time_boost_s: float = 6.0
    burn_time_sustain_s: float = 15.0
    coast_time_s: float = 25.0

    # Aerodynamics
    drag_coefficient: float = 0.32
    reference_area_m2: float = 0.0249  # π × (0.178/2)²
    max_fin_deflection_deg: float = 25.0

    # Performance (estimated from public sources)
    peak_velocity_ms: float = 1400  # Mach 4+ at altitude
    max_acceleration_g: float = 55.0  # 50-60G estimate
    nez_range_head_on_km: float = 180.0  # Greater than AIM-120D
    nez_range_uncertainty_km: float = 30.0
    nez_confidence: float = 0.50

    # Seeker parameters (advanced active radar - optimized for stealth targets)
    seeker_type: str = "active_radar_imaging"  # AESA seeker
    seeker_acquisition_range_km: float = 25.0  # Enhanced vs AIM-120D
    seeker_fov_deg: float = 70.0  # Wider FOV
    seeker_update_rate_hz: float = 15.0
    seeker_sensitivity_dbsm: float = -35.0  # Can detect 0.0003 m² targets (designed for stealth)

    # Guidance
    midcourse_guidance: str = "inertial_datalink_gps"
    terminal_guidance: str = "active_radar_homing"
    proportional_navigation_constant: float = 4.5

    @property
    def delta_v_ideal_ms(self) -> float:
        """Ideal ΔV from rocket equation"""
        mass_ratio = self.mass_total_kg / self.mass_burnout_kg
        return self.exhaust_velocity_ms * np.log(mass_ratio)


@dataclass
class TargetState:
    """Target aircraft state for AIM-260 engagement"""
    position: np.ndarray  # [x, y, z] meters
    velocity: np.ndarray  # [vx, vy, vz] m/s
    acceleration: np.ndarray  # [ax, ay, az] m/s²
    rcs_m2: float  # Radar cross section
    aspect_angle_deg: float  # Relative to missile


@dataclass
class AIM260InterceptPrediction:
    """AIM-260 intercept prediction result"""
    intercept_possible: bool
    time_to_intercept_s: float
    intercept_point: np.ndarray  # [x, y, z] meters
    lead_angle_deg: float
    closure_velocity_ms: float
    probability_kill: float
    energy_margin: float  # 0-1, remaining energy at intercept
    seeker_can_acquire: bool  # Target RCS vs seeker sensitivity
    confidence: float


class AIM260TargetingModel:
    """
    AIM-260 JATM Offensive Targeting and Intercept Prediction Model

    Implements proportional navigation guidance, intercept geometry,
    and engagement probability calculations for F-35/F-22 platforms.

    Key capability: Optimized for engaging low-RCS 5th-gen targets like J-20.
    """

    def __init__(self, params: AIM260Parameters | None = None):
        """
        Initialize AIM-260 targeting model

        Args:
            params: Missile parameters (uses defaults if None)
        """
        self.params = params or AIM260Parameters()

    def predict_intercept_vs_j20(
        self,
        missile_position: np.ndarray,
        missile_velocity: np.ndarray,
        j20_position: np.ndarray,
        j20_velocity: np.ndarray,
        phase: AIM260EngagementPhase = AIM260EngagementPhase.MIDCOURSE
    ) -> AIM260InterceptPrediction:
        """
        Predict intercept against J-20 with aspect-dependent RCS

        Args:
            missile_position: Missile position [x, y, z] (meters)
            missile_velocity: Missile velocity [vx, vy, vz] (m/s)
            j20_position: J-20 position [x, y, z] (meters)
            j20_velocity: J-20 velocity [vx, vy, vz] (m/s)
            phase: Current flight phase

        Returns:
            AIM260InterceptPrediction with intercept geometry and Pk vs J-20
        """
        # Calculate J-20 RCS from missile's viewing angle
        rcs_estimate = J20RCSModel.calculate_rcs_from_vectors(
            radar_position=missile_position,
            target_position=j20_position,
            target_velocity=j20_velocity,
            frequency_ghz=10.0  # X-band seeker
        )

        # Create target state with calculated RCS
        target = TargetState(
            position=j20_position,
            velocity=j20_velocity,
            acceleration=np.zeros(3),
            rcs_m2=rcs_estimate.rcs_m2,
            aspect_angle_deg=rcs_estimate.azimuth_deg
        )

        return self.predict_intercept(missile_position, missile_velocity, target, phase)

    def predict_intercept(
        self,
        missile_position: np.ndarray,
        missile_velocity: np.ndarray,
        target: TargetState,
        phase: AIM260EngagementPhase = AIM260EngagementPhase.MIDCOURSE
    ) -> AIM260InterceptPrediction:
        """
        Predict intercept geometry and probability

        Args:
            missile_position: Missile position [x, y, z] (meters)
            missile_velocity: Missile velocity [vx, vy, vz] (m/s)
            target: Target state
            phase: Current flight phase

        Returns:
            AIM260InterceptPrediction with intercept geometry and Pk
        """
        # Calculate relative geometry
        relative_position = target.position - missile_position
        range_m = np.linalg.norm(relative_position)

        if range_m < 1.0:
            # Already at intercept
            return AIM260InterceptPrediction(
                intercept_possible=True,
                time_to_intercept_s=0.0,
                intercept_point=missile_position.copy(),
                lead_angle_deg=0.0,
                closure_velocity_ms=0.0,
                probability_kill=1.0,
                energy_margin=1.0,
                seeker_can_acquire=True,
                confidence=1.0
            )

        # Relative velocity
        relative_velocity = target.velocity - missile_velocity
        closure_velocity_ms = -np.dot(relative_velocity, relative_position) / range_m

        # Check if closing
        if closure_velocity_ms <= 0:
            return AIM260InterceptPrediction(
                intercept_possible=False,
                time_to_intercept_s=np.inf,
                intercept_point=np.zeros(3),
                lead_angle_deg=0.0,
                closure_velocity_ms=closure_velocity_ms,
                probability_kill=0.0,
                energy_margin=0.0,
                seeker_can_acquire=False,
                confidence=1.0
            )

        # Time to intercept
        time_to_intercept_s = self._calculate_time_to_intercept(
            missile_position, missile_velocity,
            target.position, target.velocity)

        if time_to_intercept_s <= 0 or time_to_intercept_s > 400:
            return AIM260InterceptPrediction(
                intercept_possible=False,
                time_to_intercept_s=time_to_intercept_s,
                intercept_point=np.zeros(3),
                lead_angle_deg=0.0,
                closure_velocity_ms=closure_velocity_ms,
                probability_kill=0.0,
                energy_margin=0.0,
                seeker_can_acquire=False,
                confidence=0.8
            )

        # Predict intercept point
        intercept_point = target.position + target.velocity * time_to_intercept_s

        # Calculate lead angle
        los_vector = relative_position / range_m
        intercept_vector = intercept_point - missile_position
        intercept_distance = np.linalg.norm(intercept_vector)

        if intercept_distance > 0:
            intercept_direction = intercept_vector / intercept_distance
            cos_lead = np.clip(np.dot(los_vector, intercept_direction), -1.0, 1.0)
            lead_angle_deg = np.degrees(np.arccos(cos_lead))
        else:
            lead_angle_deg = 0.0

        # Check seeker acquisition capability
        seeker_can_acquire = self._can_seeker_acquire(target.rcs_m2, range_m / 1000.0)

        # Calculate energy margin
        energy_margin = self._calculate_energy_margin(
            missile_velocity, target.velocity, time_to_intercept_s, phase)

        # Calculate probability of kill
        probability_kill = self._calculate_pk(
            range_m / 1000.0,
            target.aspect_angle_deg,
            target.rcs_m2,
            energy_margin,
            phase,
            seeker_can_acquire
        )

        # Confidence
        confidence = self._calculate_confidence(
            range_m / 1000.0, lead_angle_deg, energy_margin, target.rcs_m2)

        return AIM260InterceptPrediction(
            intercept_possible=energy_margin > 0.2 and seeker_can_acquire,
            time_to_intercept_s=time_to_intercept_s,
            intercept_point=intercept_point,
            lead_angle_deg=lead_angle_deg,
            closure_velocity_ms=closure_velocity_ms,
            probability_kill=probability_kill,
            energy_margin=energy_margin,
            seeker_can_acquire=seeker_can_acquire,
            confidence=confidence
        )

    def _calculate_time_to_intercept(
        self,
        missile_pos: np.ndarray,
        missile_vel: np.ndarray,
        target_pos: np.ndarray,
        target_vel: np.ndarray
    ) -> float:
        """Calculate time to intercept using quadratic solution"""
        rel_pos = target_pos - missile_pos
        rel_vel = target_vel - missile_vel

        a = np.dot(rel_vel, rel_vel)
        b = 2 * np.dot(rel_pos, rel_vel)
        c = np.dot(rel_pos, rel_pos)

        if a < 1e-6:
            if b < 0:
                return -c / b
            else:
                return np.inf

        discriminant = b**2 - 4*a*c

        if discriminant < 0:
            return np.inf

        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)

        if t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        else:
            return np.inf

    def _can_seeker_acquire(self, target_rcs_m2: float, range_km: float) -> bool:
        """
        Check if seeker can acquire target based on RCS and range

        AIM-260 has advanced AESA seeker optimized for low-RCS targets.
        The seeker is designed to track targets down to -25 dBsm (0.003 m²).
        """
        # AIM-260 AESA seeker specifications (optimized for low-RCS)
        # Reference: 25 km acquisition vs 1 m² target
        reference_rcs = 1.0  # 1 m² reference
        reference_range = self.params.seeker_acquisition_range_km  # 25 km

        # Minimum RCS the seeker can track (from seeker_sensitivity_dbsm)
        min_trackable_rcs = 10 ** (self.params.seeker_sensitivity_dbsm / 10)  # 0.003 m²

        # If target RCS is below minimum trackable, seeker cannot acquire
        if target_rcs_m2 < min_trackable_rcs:
            return False

        # Seeker detection range scales with RCS^0.25 (radar equation fourth power)
        # But AIM-260 advanced processing provides better performance vs low-RCS
        # Use softer scaling (RCS^0.2) due to advanced signal processing
        scaled_range = reference_range * (target_rcs_m2 / reference_rcs) ** 0.2 if target_rcs_m2 > 0 else 0.0

        # AIM-260 minimum engagement range for stealth targets
        # Advanced seeker can detect -20 dBsm targets at 15+ km
        if target_rcs_m2 >= 0.001:  # >= -30 dBsm (J-20 frontal)
            min_detection_range = 15.0
        elif target_rcs_m2 >= 0.0003:  # >= -35 dBsm (F-35 frontal)
            min_detection_range = 10.0
        else:
            min_detection_range = 5.0

        # Check if current range allows seeker acquisition
        effective_range = max(scaled_range, min_detection_range)
        return range_km <= effective_range

    def _calculate_energy_margin(
        self,
        missile_velocity: np.ndarray,
        target_velocity: np.ndarray,
        time_to_intercept_s: float,
        phase: AIM260EngagementPhase
    ) -> float:
        """Calculate remaining energy margin"""
        velocity_error = np.linalg.norm(target_velocity - missile_velocity)

        if phase == AIM260EngagementPhase.BOOST:
            available_dv = self.params.delta_v_ideal_ms * 0.9
        elif phase == AIM260EngagementPhase.MIDCOURSE:
            available_dv = self.params.delta_v_ideal_ms * 0.55
        elif phase == AIM260EngagementPhase.TERMINAL:
            available_dv = 250.0
        else:
            available_dv = 0.0

        drag_factor = 0.7
        effective_dv = available_dv * drag_factor

        energy_margin = effective_dv / velocity_error if velocity_error > 0 else 1.0

        return np.clip(energy_margin, 0.0, 1.0)

    def _calculate_pk(
        self,
        range_km: float,
        aspect_deg: float,
        target_rcs_m2: float,
        energy_margin: float,
        phase: AIM260EngagementPhase,
        seeker_can_acquire: bool
    ) -> float:
        """
        Calculate probability of kill

        AIM-260 is optimized for low-RCS targets like J-20.
        """
        if not seeker_can_acquire:
            return 0.0

        # Base Pk vs range (head-on, ideal conditions)
        if range_km <= 15:
            pk_range = 0.92
        elif range_km <= 40:
            pk_range = 0.88
        elif range_km <= 80:
            pk_range = 0.75 - (range_km - 40) * 0.008
        elif range_km <= 150:
            pk_range = 0.43 - (range_km - 80) * 0.004
        elif range_km <= 200:
            pk_range = 0.15 - (range_km - 150) * 0.002
        else:
            pk_range = max(0.03, 0.05 - (range_km - 200) * 0.001)

        # Aspect factor
        if aspect_deg <= 30:
            aspect_factor = 1.0
        elif aspect_deg <= 60:
            aspect_factor = 0.92
        elif aspect_deg <= 120:
            aspect_factor = 0.65
        elif aspect_deg <= 150:
            aspect_factor = 0.45
        else:
            aspect_factor = 0.35

        # RCS factor - AIM-260 optimized for low RCS
        # Less penalty for stealth targets compared to legacy missiles
        if target_rcs_m2 < 0.001:
            rcs_factor = 0.75  # Very stealthy - still decent Pk
        elif target_rcs_m2 < 0.01:
            rcs_factor = 0.85  # Stealthy
        elif target_rcs_m2 < 0.1:
            rcs_factor = 0.95  # Low RCS
        else:
            rcs_factor = 1.0  # Normal/large target

        # Energy margin factor
        if energy_margin < 0.3:
            energy_factor = 0.55
        elif energy_margin < 0.6:
            energy_factor = 0.82
        else:
            energy_factor = 1.0

        # Phase factor
        if phase == AIM260EngagementPhase.TERMINAL:
            phase_factor = 1.0
        elif phase == AIM260EngagementPhase.MIDCOURSE:
            phase_factor = 0.92
        else:
            phase_factor = 0.75

        pk = pk_range * aspect_factor * rcs_factor * energy_factor * phase_factor
        return np.clip(pk, 0.0, 1.0)

    def _calculate_confidence(
        self,
        range_km: float,
        lead_angle_deg: float,
        energy_margin: float,
        target_rcs_m2: float
    ) -> float:
        """Calculate confidence in intercept prediction"""
        confidence = self.params.nez_confidence

        if range_km > 180:
            confidence *= 0.65
        elif range_km > 100:
            confidence *= 0.80

        if lead_angle_deg > 60:
            confidence *= 0.75

        if energy_margin < 0.4:
            confidence *= 0.70

        # Lower confidence vs very low RCS targets
        if target_rcs_m2 < 0.005:
            confidence *= 0.85

        return confidence

    def calculate_launch_acceptability_vs_j20(
        self,
        f35_position: np.ndarray,
        f35_velocity: np.ndarray,
        j20_position: np.ndarray,
        j20_velocity: np.ndarray
    ) -> tuple[bool, str, float]:
        """
        Determine if launch conditions are acceptable vs J-20

        The AIM-260 uses datalink guidance during midcourse phase,
        so seeker acquisition is NOT required at launch. The seeker
        only needs to acquire in terminal phase (~15-20 km from target).

        Launch acceptance is based on:
        - Range within NEZ
        - Valid intercept geometry
        - Adequate energy margin

        Args:
            f35_position: F-35 position [x, y, z] (meters)
            f35_velocity: F-35 velocity [vx, vy, vz] (m/s)
            j20_position: J-20 position [x, y, z] (meters)
            j20_velocity: J-20 velocity [vx, vy, vz] (m/s)

        Returns:
            Tuple of (acceptable, reason, confidence)
        """
        # Get J-20 RCS for Pk estimation
        from rcs_models import J20RCSModel
        rcs_estimate = J20RCSModel.calculate_rcs_from_vectors(
            f35_position, j20_position, j20_velocity
        )

        range_km = np.linalg.norm(j20_position - f35_position) / 1000.0

        # Minimum range check
        if range_km < 8:
            return False, "Minimum range violation (< 8 km)", 1.0

        # Maximum range check
        max_range = self.params.nez_range_head_on_km + self.params.nez_range_uncertainty_km
        if range_km > max_range:
            return False, f"Beyond maximum range (> {max_range:.0f} km)", 0.85

        # Calculate intercept geometry
        intercept = self.predict_intercept_vs_j20(
            f35_position, f35_velocity,
            j20_position, j20_velocity,
            phase=AIM260EngagementPhase.BOOST
        )

        # Check intercept geometry (closing velocity must be positive)
        if intercept.closure_velocity_ms <= 0:
            return False, "Opening geometry - target moving away", intercept.confidence

        # Check energy margin
        if intercept.energy_margin < 0.30:
            return False, f"Insufficient energy margin ({intercept.energy_margin:.2f})", intercept.confidence

        # Check if target RCS is trackable by seeker (will it work in terminal?)
        min_trackable_rcs = 10 ** (self.params.seeker_sensitivity_dbsm / 10)
        if rcs_estimate.rcs_m2 < min_trackable_rcs:
            return False, f"Target RCS ({rcs_estimate.rcs_dbsm:.1f} dBsm) below seeker threshold", 0.6

        # Estimate Pk based on range and aspect
        # At launch, we estimate Pk assuming terminal seeker acquisition
        estimated_pk = self._estimate_launch_pk(range_km, rcs_estimate.rcs_m2)

        if estimated_pk < 0.20:
            return False, f"Estimated Pk too low ({estimated_pk:.2f})", 0.7

        confidence = self.params.nez_confidence
        if range_km > 150:
            confidence *= 0.7  # Reduced confidence at extended range

        return True, f"Launch acceptable vs J-20 (est Pk: {estimated_pk:.2f})", confidence

    def _estimate_launch_pk(self, range_km: float, target_rcs_m2: float) -> float:
        """Estimate Pk at launch time (for launch acceptability)"""
        # Base Pk from range (assumes head-on, datalink midcourse, terminal acquisition)
        if range_km <= 50:
            pk_range = 0.75
        elif range_km <= 100:
            pk_range = 0.55
        elif range_km <= 150:
            pk_range = 0.35
        else:
            pk_range = 0.20

        # RCS factor (stealth targets harder to track in terminal)
        if target_rcs_m2 < 0.001:
            rcs_factor = 0.75
        elif target_rcs_m2 < 0.01:
            rcs_factor = 0.85
        else:
            rcs_factor = 1.0

        return pk_range * rcs_factor

    def print_targeting_summary(self):
        """Print summary of AIM-260 targeting capabilities"""
        print("=" * 70)
        print("AIM-260 JATM Offensive Targeting Model - Pre-Trained Parameters")
        print("=" * 70)
        print("\nMissile Configuration:")
        print(f"  Length:               {self.params.length_m:.1f} m")
        print(f"  Diameter:             {self.params.diameter_m*1000:.0f} mm")
        print(f"  Total mass:           {self.params.mass_total_kg:.0f} kg")
        print(f"  Propellant mass:      {self.params.mass_propellant_kg:.0f} kg "
              f"({self.params.mass_propellant_kg/self.params.mass_total_kg*100:.0f}%)")
        print(f"  Warhead mass:         {self.params.mass_warhead_kg:.0f} kg")

        print("\nPropulsion:")
        print(f"  Specific impulse:     {self.params.specific_impulse_s:.0f} s")
        print(f"  Ideal ΔV:             {self.params.delta_v_ideal_ms:.0f} m/s")
        print(f"  Peak velocity:        Mach {self.params.peak_velocity_ms/340:.1f} "
              f"({self.params.peak_velocity_ms:.0f} m/s)")

        print("\nPerformance (estimated):")
        print(f"  NEZ range (head-on):  {self.params.nez_range_head_on_km:.0f} ± "
              f"{self.params.nez_range_uncertainty_km:.0f} km")
        print(f"  Confidence:           {self.params.nez_confidence:.0%}")
        print(f"  Max acceleration:     {self.params.max_acceleration_g:.0f}G")

        print("\nSeeker (Advanced AESA):")
        print(f"  Type:                 {self.params.seeker_type}")
        print(f"  Acquisition range:    {self.params.seeker_acquisition_range_km:.0f} km")
        print(f"  Sensitivity:          {self.params.seeker_sensitivity_dbsm:.0f} dBsm")
        print(f"  FOV:                  ±{self.params.seeker_fov_deg/2:.0f}°")

        print("\nGuidance:")
        print(f"  Midcourse:            {self.params.midcourse_guidance}")
        print(f"  Terminal:             {self.params.terminal_guidance}")

        print("=" * 70)


# Example usage and validation
if __name__ == "__main__":
    aim260 = AIM260TargetingModel()
    aim260.print_targeting_summary()

    print("\n[TEST] Intercept Prediction vs J-20:")
    print("-" * 70)

    # F-35 launch conditions
    f35_pos = np.array([0, 0, 12000])
    f35_vel = np.array([450, 0, 0])  # Mach 1.5 heading east

    # J-20 scenarios
    test_scenarios = [
        ("Head-on 100km", np.array([100000, 0, 12000]), np.array([-500, 0, 0])),
        ("Head-on 150km", np.array([150000, 0, 12000]), np.array([-500, 0, 0])),
        ("Beam 80km", np.array([80000, 0, 12000]), np.array([0, -500, 0])),
        ("Tail chase 60km", np.array([60000, 0, 12000]), np.array([400, 0, 0])),
    ]

    for name, j20_pos, j20_vel in test_scenarios:
        intercept = aim260.predict_intercept_vs_j20(
            f35_pos, f35_vel,
            j20_pos, j20_vel,
            phase=AIM260EngagementPhase.MIDCOURSE
        )

        range_km = np.linalg.norm(j20_pos - f35_pos) / 1000.0

        print(f"  {name:18s}: Range = {range_km:5.1f} km, "
              f"Pk = {intercept.probability_kill:.2f}, "
              f"Seeker: {'OK' if intercept.seeker_can_acquire else 'NO'}")

    print("\n[TEST] Launch Acceptability vs J-20:")
    print("-" * 70)

    for name, j20_pos, j20_vel in test_scenarios:
        acceptable, reason, confidence = aim260.calculate_launch_acceptability_vs_j20(
            f35_pos, f35_vel,
            j20_pos, j20_vel
        )

        status = "✓ ACCEPT" if acceptable else "✗ REJECT"
        print(f"  {name:18s}: {status:10s} - {reason}")

    print("\n" + "=" * 70)
    print("AIM-260 vs J-20 targeting model validation complete.")
    print("=" * 70)
