#!/usr/bin/env python3
"""
PL-15 Offensive Targeting Model

Implements PL-15 missile targeting, guidance, and intercept prediction based on
deductive reasoning from physical observables and missile performance models.

Key Parameters (from reasoning_chains/pl15_nez_range.yaml):
- Length: 4.0 m
- Diameter: 203 mm
- Mass: 210 kg
- Propellant: 63 kg (30% of total)
- NEZ range: 100 ± 20 km head-on (confidence: 60%)
- Peak velocity: Mach 4.5 (1530 m/s)
- Maneuverability: 40-60G

This is an OFFENSIVE model - helps PL-15 predict intercept geometry,
lead angles, and engagement probability against targets.

Classification: UNCLASSIFIED // PUBLIC RELEASE
All parameters derived from public sources with documented uncertainty.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class EngagementPhase(Enum):
    """PL-15 flight phases"""
    BOOST = "boost"
    MIDCOURSE = "midcourse"
    TERMINAL = "terminal"
    BURNOUT = "burnout"


@dataclass
class PL15Parameters:
    """
    PL-15 Missile Performance Parameters (Best Estimates)

    Based on deductive reasoning from:
    - Observable dimensions from parade photos
    - Rocket equation physics
    - Comparison to AIM-120D/R-77M
    """

    # Physical dimensions (from public photos)
    length_m: float = 4.0
    diameter_m: float = 0.203
    mass_total_kg: float = 210
    mass_propellant_kg: float = 63  # 30% propellant fraction
    mass_warhead_kg: float = 40
    mass_burnout_kg: float = 147  # Total - propellant

    # Propulsion (dual-pulse solid rocket)
    specific_impulse_s: float = 250  # HTPB solid propellant
    exhaust_velocity_ms: float = 2452  # Isp × g
    burn_time_boost_s: float = 5.0  # First pulse
    burn_time_sustain_s: float = 12.0  # Second pulse
    coast_time_s: float = 20.0  # Between pulses

    # Aerodynamics
    drag_coefficient: float = 0.35  # Streamlined body
    reference_area_m2: float = 0.0324  # π × (0.203/2)²
    lift_coefficient: float = 2.5  # Max L/D
    max_fin_deflection_deg: float = 20.0

    # Performance (from reasoning chains)
    peak_velocity_ms: float = 1530  # Mach 4.5 at altitude
    max_acceleration_g: float = 50.0  # 40-60G estimate
    nez_range_head_on_km: float = 100.0
    nez_range_uncertainty_km: float = 20.0
    nez_confidence: float = 0.60

    # Seeker parameters
    seeker_type: str = "active_radar"  # Active radar terminal
    seeker_acquisition_range_km: float = 20.0  # Terminal acquisition
    seeker_fov_deg: float = 60.0  # Field of view
    seeker_update_rate_hz: float = 10.0  # Guidance update rate

    # Guidance
    midcourse_guidance: str = "inertial_datalink"  # INS + datalink updates
    terminal_guidance: str = "active_radar_homing"  # Active radar seeker
    proportional_navigation_constant: float = 4.0  # N = 4 typical

    @property
    def delta_v_ideal_ms(self) -> float:
        """Ideal ΔV from rocket equation"""
        mass_ratio = self.mass_total_kg / self.mass_burnout_kg
        return self.exhaust_velocity_ms * np.log(mass_ratio)


@dataclass
class TargetState:
    """Target aircraft state"""
    position: np.ndarray  # [x, y, z] meters
    velocity: np.ndarray  # [vx, vy, vz] m/s
    acceleration: np.ndarray  # [ax, ay, az] m/s²
    rcs_m2: float  # Radar cross section
    aspect_angle_deg: float  # Relative to missile


@dataclass
class InterceptPrediction:
    """Intercept prediction result"""
    intercept_possible: bool
    time_to_intercept_s: float
    intercept_point: np.ndarray  # [x, y, z] meters
    lead_angle_deg: float
    closure_velocity_ms: float
    probability_kill: float
    energy_margin: float  # 0-1, remaining energy at intercept
    confidence: float


class PL15TargetingModel:
    """
    PL-15 Offensive Targeting and Intercept Prediction Model

    Implements proportional navigation guidance, intercept geometry,
    and engagement probability calculations.
    """

    def __init__(self, params: Optional[PL15Parameters] = None):
        """
        Initialize PL-15 targeting model

        Args:
            params: Missile parameters (uses defaults if None)
        """
        self.params = params or PL15Parameters()

    def predict_intercept(self,
                         missile_position: np.ndarray,
                         missile_velocity: np.ndarray,
                         target: TargetState,
                         phase: EngagementPhase = EngagementPhase.MIDCOURSE) -> InterceptPrediction:
        """
        Predict intercept geometry and probability

        Args:
            missile_position: Missile position [x, y, z] (meters)
            missile_velocity: Missile velocity [vx, vy, vz] (m/s)
            target: Target state
            phase: Current flight phase

        Returns:
            InterceptPrediction with intercept geometry and Pk
        """
        # Calculate relative geometry
        relative_position = target.position - missile_position
        range_m = np.linalg.norm(relative_position)

        if range_m < 1.0:
            # Already at intercept
            return InterceptPrediction(
                intercept_possible=True,
                time_to_intercept_s=0.0,
                intercept_point=missile_position.copy(),
                lead_angle_deg=0.0,
                closure_velocity_ms=0.0,
                probability_kill=1.0,
                energy_margin=1.0,
                confidence=1.0
            )

        # Relative velocity
        relative_velocity = target.velocity - missile_velocity
        closure_velocity_ms = -np.dot(relative_velocity, relative_position) / range_m

        # Check if closing
        if closure_velocity_ms <= 0:
            # Opening geometry - no intercept
            return InterceptPrediction(
                intercept_possible=False,
                time_to_intercept_s=np.inf,
                intercept_point=np.zeros(3),
                lead_angle_deg=0.0,
                closure_velocity_ms=closure_velocity_ms,
                probability_kill=0.0,
                energy_margin=0.0,
                confidence=1.0
            )

        # First-order intercept point estimate (assume constant velocities)
        time_to_intercept_s = self._calculate_time_to_intercept(
            missile_position, missile_velocity,
            target.position, target.velocity)

        if time_to_intercept_s <= 0 or time_to_intercept_s > 300:
            # No valid intercept or too far in future
            return InterceptPrediction(
                intercept_possible=False,
                time_to_intercept_s=time_to_intercept_s,
                intercept_point=np.zeros(3),
                lead_angle_deg=0.0,
                closure_velocity_ms=closure_velocity_ms,
                probability_kill=0.0,
                energy_margin=0.0,
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

        # Calculate energy margin (remaining ΔV / required ΔV)
        energy_margin = self._calculate_energy_margin(
            missile_velocity, target.velocity, time_to_intercept_s, phase)

        # Calculate probability of kill
        probability_kill = self._calculate_pk(
            range_m / 1000.0,  # Convert to km
            target.aspect_angle_deg,
            target.rcs_m2,
            energy_margin,
            phase
        )

        # Confidence based on range and geometry
        confidence = self._calculate_confidence(
            range_m / 1000.0, lead_angle_deg, energy_margin)

        return InterceptPrediction(
            intercept_possible=energy_margin > 0.2,
            time_to_intercept_s=time_to_intercept_s,
            intercept_point=intercept_point,
            lead_angle_deg=lead_angle_deg,
            closure_velocity_ms=closure_velocity_ms,
            probability_kill=probability_kill,
            energy_margin=energy_margin,
            confidence=confidence
        )

    def _calculate_time_to_intercept(self,
                                     missile_pos: np.ndarray,
                                     missile_vel: np.ndarray,
                                     target_pos: np.ndarray,
                                     target_vel: np.ndarray) -> float:
        """
        Calculate time to intercept using quadratic solution

        Solves: |target_pos + target_vel*t - (missile_pos + missile_vel*t)| = 0
        """
        # Relative position and velocity
        rel_pos = target_pos - missile_pos
        rel_vel = target_vel - missile_vel

        # Quadratic equation coefficients: a*t² + b*t + c = 0
        a = np.dot(rel_vel, rel_vel)
        b = 2 * np.dot(rel_pos, rel_vel)
        c = np.dot(rel_pos, rel_pos)

        if a < 1e-6:
            # Relative velocity too small
            if b < 0:
                return -c / b  # Linear solution
            else:
                return np.inf

        # Quadratic solution
        discriminant = b**2 - 4*a*c

        if discriminant < 0:
            # No intercept
            return np.inf

        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)

        # Return smallest positive time
        if t1 > 0:
            return t1
        elif t2 > 0:
            return t2
        else:
            return np.inf

    def _calculate_energy_margin(self,
                                 missile_velocity: np.ndarray,
                                 target_velocity: np.ndarray,
                                 time_to_intercept_s: float,
                                 phase: EngagementPhase) -> float:
        """
        Calculate remaining energy margin (0-1)

        Energy margin = (available ΔV) / (required ΔV for intercept)
        """
        # Required velocity change for intercept
        velocity_error = np.linalg.norm(target_velocity - missile_velocity)

        # Available ΔV depends on phase
        if phase == EngagementPhase.BOOST:
            # Most propellant remaining
            available_dv = self.params.delta_v_ideal_ms * 0.9
        elif phase == EngagementPhase.MIDCOURSE:
            # Some propellant used, second pulse available
            available_dv = self.params.delta_v_ideal_ms * 0.5
        elif phase == EngagementPhase.TERMINAL:
            # Limited maneuvering energy
            available_dv = 200.0  # ~200 m/s for terminal maneuvers
        else:
            # Burnout - no propellant
            available_dv = 0.0

        # Energy margin with drag losses
        drag_factor = 0.7  # Assume 30% energy loss to drag
        effective_dv = available_dv * drag_factor

        if velocity_error > 0:
            energy_margin = effective_dv / velocity_error
        else:
            energy_margin = 1.0

        return np.clip(energy_margin, 0.0, 1.0)

    def _calculate_pk(self,
                     range_km: float,
                     aspect_deg: float,
                     target_rcs_m2: float,
                     energy_margin: float,
                     phase: EngagementPhase) -> float:
        """
        Calculate probability of kill (Pk)

        Factors:
        - Range (closer = higher Pk)
        - Aspect angle (head-on = higher Pk)
        - Target RCS (larger = easier to track)
        - Energy margin (more energy = more maneuvering)
        - Flight phase (terminal = higher Pk)
        """
        # Base Pk curve vs range (assumes head-on, ideal conditions)
        # Updated for PL-15 with AESA seeker and improved guidance
        if range_km <= 10:
            pk_range = 0.98
        elif range_km <= 40:
            pk_range = 0.95
        elif range_km <= 80:
            pk_range = 0.95 - (range_km - 40) * 0.002  # Very gradual decay within NEZ
        elif range_km <= 120:
            pk_range = 0.87 - (range_km - 80) * 0.005  # Decay beyond optimal range
        else:
            pk_range = max(0.10, 0.67 - (range_km - 120) * 0.004)

        # Aspect factor (head-on best, beam/tail worse)
        if aspect_deg <= 30:
            aspect_factor = 1.0  # Head-on
        elif aspect_deg <= 60:
            aspect_factor = 0.9  # Forward quarter
        elif aspect_deg <= 120:
            aspect_factor = 0.65  # Beam
        elif aspect_deg <= 150:
            aspect_factor = 0.45  # Rear quarter
        else:
            aspect_factor = 0.35  # Tail chase

        # RCS factor (small RCS = harder to track in terminal)
        # Modern AESA seekers maintain good performance against stealthy targets
        if target_rcs_m2 < 0.0005:
            rcs_factor = 0.80  # Very stealthy (improved seeker sensitivity)
        elif target_rcs_m2 < 0.005:
            rcs_factor = 0.90  # Stealthy
        else:
            rcs_factor = 1.0  # Normal target

        # Energy margin factor
        if energy_margin < 0.3:
            energy_factor = 0.5  # Low energy
        elif energy_margin < 0.6:
            energy_factor = 0.8
        else:
            energy_factor = 1.0  # Plenty of energy

        # Phase factor
        if phase == EngagementPhase.TERMINAL:
            phase_factor = 1.0  # Active seeker
        elif phase == EngagementPhase.MIDCOURSE:
            phase_factor = 0.9  # Datalink guidance
        else:
            phase_factor = 0.7  # Boost/burnout

        # Combined Pk
        pk = pk_range * aspect_factor * rcs_factor * energy_factor * phase_factor

        return np.clip(pk, 0.0, 1.0)

    def _calculate_confidence(self,
                            range_km: float,
                            lead_angle_deg: float,
                            energy_margin: float) -> float:
        """Calculate confidence in intercept prediction"""
        confidence = self.params.nez_confidence

        # Range uncertainty
        if range_km > 100:
            confidence *= 0.7  # Beyond NEZ range
        elif range_km > 60:
            confidence *= 0.85

        # Geometry uncertainty
        if lead_angle_deg > 60:
            confidence *= 0.8  # Large lead angle

        # Energy uncertainty
        if energy_margin < 0.4:
            confidence *= 0.75  # Marginal energy

        return confidence

    def calculate_launch_acceptability(self,
                                      missile_position: np.ndarray,
                                      missile_velocity: np.ndarray,
                                      target: TargetState) -> Tuple[bool, str, float]:
        """
        Determine if launch conditions are acceptable

        Args:
            missile_position: Launch position [x, y, z] (meters)
            missile_velocity: Initial velocity (platform velocity) [vx, vy, vz] (m/s)
            target: Target state

        Returns:
            Tuple of (acceptable, reason, confidence)
        """
        # Predict intercept
        intercept = self.predict_intercept(
            missile_position, missile_velocity, target,
            phase=EngagementPhase.BOOST)

        # Check range
        range_km = np.linalg.norm(target.position - missile_position) / 1000.0

        if range_km < 5:
            return False, "Minimum range violation (< 5 km)", 1.0

        if range_km > self.params.nez_range_head_on_km + self.params.nez_range_uncertainty_km:
            return False, f"Beyond maximum range (> {self.params.nez_range_head_on_km + self.params.nez_range_uncertainty_km:.0f} km)", 0.9

        # Check intercept feasibility
        if not intercept.intercept_possible:
            return False, "No valid intercept geometry", intercept.confidence

        # Check Pk threshold
        if intercept.probability_kill < 0.3:
            return False, f"Pk too low ({intercept.probability_kill:.2f} < 0.3)", intercept.confidence

        # Check energy margin
        if intercept.energy_margin < 0.4:
            return False, f"Insufficient energy margin ({intercept.energy_margin:.2f})", intercept.confidence

        # All checks passed
        return True, "Launch acceptable", intercept.confidence

    def print_targeting_summary(self):
        """Print summary of PL-15 targeting capabilities"""
        print("=" * 70)
        print("PL-15 Offensive Targeting Model - Pre-Trained Parameters")
        print("=" * 70)
        print(f"\nMissile Configuration:")
        print(f"  Length:               {self.params.length_m:.1f} m")
        print(f"  Diameter:             {self.params.diameter_m*1000:.0f} mm")
        print(f"  Total mass:           {self.params.mass_total_kg:.0f} kg")
        print(f"  Propellant mass:      {self.params.mass_propellant_kg:.0f} kg ({self.params.mass_propellant_kg/self.params.mass_total_kg*100:.0f}%)")
        print(f"  Warhead mass:         {self.params.mass_warhead_kg:.0f} kg")

        print(f"\nPropulsion:")
        print(f"  Type:                 Dual-pulse solid rocket")
        print(f"  Specific impulse:     {self.params.specific_impulse_s:.0f} s")
        print(f"  Exhaust velocity:     {self.params.exhaust_velocity_ms:.0f} m/s")
        print(f"  Ideal ΔV:             {self.params.delta_v_ideal_ms:.0f} m/s")
        print(f"  Peak velocity:        Mach {self.params.peak_velocity_ms/340:.1f} ({self.params.peak_velocity_ms:.0f} m/s)")

        print(f"\nPerformance (from reasoning chains):")
        print(f"  NEZ range (head-on):  {self.params.nez_range_head_on_km:.0f} ± {self.params.nez_range_uncertainty_km:.0f} km")
        print(f"  Confidence:           {self.params.nez_confidence:.0%}")
        print(f"  Max acceleration:     {self.params.max_acceleration_g:.0f}G")

        print(f"\nGuidance:")
        print(f"  Midcourse:            {self.params.midcourse_guidance}")
        print(f"  Terminal:             {self.params.terminal_guidance}")
        print(f"  Seeker acquisition:   {self.params.seeker_acquisition_range_km:.0f} km")
        print(f"  Seeker FOV:           ±{self.params.seeker_fov_deg/2:.0f}°")

        print("=" * 70)


# Example usage and validation
if __name__ == "__main__":
    # Create PL-15 targeting model
    pl15 = PL15TargetingModel()

    # Print targeting summary
    pl15.print_targeting_summary()

    # Test intercept prediction
    print("\n[TEST] Intercept Prediction vs Target Aspect:")
    print("-" * 70)

    # PL-15 launch conditions
    missile_pos = np.array([0, 0, 12000])  # 12 km altitude
    missile_vel = np.array([450, 0, 0])  # Mach 1.5 heading east

    # Target scenarios
    test_scenarios = [
        ("Head-on", np.array([80000, 0, 12000]), np.array([-250, 0, 0]), 0.0002, 0),
        ("Beam", np.array([80000, 0, 12000]), np.array([0, -250, 0]), 0.02, 90),
        ("Tail chase", np.array([80000, 0, 12000]), np.array([250, 0, 0]), 0.005, 180),
        ("Close head-on", np.array([30000, 0, 12000]), np.array([-250, 0, 0]), 0.0002, 0),
    ]

    for name, tgt_pos, tgt_vel, rcs, aspect in test_scenarios:
        target = TargetState(
            position=tgt_pos,
            velocity=tgt_vel,
            acceleration=np.zeros(3),
            rcs_m2=rcs,
            aspect_angle_deg=aspect
        )

        intercept = pl15.predict_intercept(
            missile_pos, missile_vel, target,
            phase=EngagementPhase.MIDCOURSE)

        range_km = np.linalg.norm(tgt_pos - missile_pos) / 1000.0

        print(f"  {name:15s}: Range = {range_km:5.1f} km, "
              f"TTC = {intercept.time_to_intercept_s:5.1f} s, "
              f"Pk = {intercept.probability_kill:.2f}, "
              f"Lead = {intercept.lead_angle_deg:5.1f}°")

    # Test launch acceptability
    print("\n[TEST] Launch Acceptability:")
    print("-" * 70)

    for name, tgt_pos, tgt_vel, rcs, aspect in test_scenarios:
        target = TargetState(
            position=tgt_pos,
            velocity=tgt_vel,
            acceleration=np.zeros(3),
            rcs_m2=rcs,
            aspect_angle_deg=aspect
        )

        acceptable, reason, confidence = pl15.calculate_launch_acceptability(
            missile_pos, missile_vel, target)

        range_km = np.linalg.norm(tgt_pos - missile_pos) / 1000.0

        status = "✓ ACCEPT" if acceptable else "✗ REJECT"
        print(f"  {name:15s}: {status:10s} - {reason} (conf: {confidence:.0%})")

    print("\n" + "=" * 70)
    print("PL-15 targeting model validation complete.")
    print("=" * 70)
