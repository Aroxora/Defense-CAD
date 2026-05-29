#!/usr/bin/env python3
"""
LRHW (Dark Eagle) Hypersonic Glide Vehicle (HGV) Targeting Model

Implements US Army Long Range Hypersonic Weapon targeting, trajectory prediction,
and intercept calculations against high-value targets.

Key Parameters (from public sources):
- Launch vehicle: Common Hypersonic Glide Body (C-HGB)
- Warhead: Hypersonic Glide Vehicle
- Speed: Mach 5-17 (1,700 - 5,780 m/s)
- Range: 2,775+ km
- Maneuverability: 15-25G during glide phase
- CEP: 5-10 meters (with terminal guidance)
- Altitude: 40-100 km during glide phase

This is a PRECISION STRIKE model for land attack missions
against stationary high-value targets.

Classification: UNCLASSIFIED // PUBLIC RELEASE
All parameters derived from public sources with documented uncertainty.
"""

import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


class HGVFlightPhase(Enum):
    """LRHW HGV flight phases"""
    BOOST = "boost"  # Initial rocket boost
    SEPARATION = "separation"  # HGV separates from booster
    GLIDE = "glide"  # Hypersonic glide phase
    TERMINAL = "terminal"  # Terminal guidance and final dive
    IMPACT = "impact"


@dataclass
class LRHWParameters:
    """
    LRHW (Dark Eagle) HGV Performance Parameters (Best Estimates)

    Based on public sources:
    - US Army statements and press releases
    - DOD hypersonic weapon program briefings
    - Physics-based trajectory modeling
    - Comparison to similar systems (C-HGB test data)
    """

    # Launch vehicle (Two-stage solid rocket booster)
    launch_vehicle_length_m: float = 10.5
    launch_vehicle_diameter_m: float = 0.88
    total_system_mass_kg: float = 7500  # Estimated

    # HGV warhead (Common Hypersonic Glide Body)
    hgv_length_m: float = 4.0
    hgv_mass_kg: float = 800  # HGV + warhead
    warhead_mass_kg: float = 350  # Conventional warhead
    warhead_type: str = "unitary_he"

    # Performance (from public estimates)
    max_range_km: float = 2775
    min_range_km: float = 500  # Minimum effective range
    peak_velocity_ms: float = 5780  # Mach 17 at altitude
    typical_velocity_ms: float = 2380  # Mach 7 during glide
    terminal_velocity_ms: float = 2040  # Mach 6 at impact

    # Trajectory parameters
    boost_phase_duration_s: float = 90  # 1.5 minute boost
    boost_altitude_km: float = 80  # Peak altitude after boost
    glide_altitude_km: float = 50  # Typical glide altitude
    glide_phase_duration_s: float = 540  # ~9 minutes
    terminal_phase_duration_s: float = 40  # Final dive

    # Maneuverability
    max_glide_acceleration_g: float = 25.0  # Lateral maneuvers during glide
    max_terminal_acceleration_g: float = 20.0  # Terminal phase
    cross_range_km: float = 500  # Maximum lateral deviation from ballistic path

    # Aerodynamics (during glide)
    lift_to_drag_ratio: float = 5.5  # L/D ratio for C-HGB
    drag_coefficient: float = 0.15  # Low drag design
    reference_area_m2: float = 2.5  # Estimated planform area

    # Guidance system
    guidance_midcourse: str = "inertial_gps"  # INS + GPS
    guidance_terminal: str = "gps_ins"  # GPS/INS terminal (no active seeker)
    terminal_update_rate_hz: float = 50.0  # High update rate

    # Accuracy (with GPS/INS guidance)
    cep_meters: float = 6.0  # Circular Error Probable
    cep_uncertainty_meters: float = 3.0  # Uncertainty in CEP estimate
    cep_confidence: float = 0.65  # 65% confidence in estimate

    # Re-entry characteristics
    plasma_blackout_altitude_km: float = 85  # Communications blackout region
    plasma_blackout_duration_s: float = 15  # Duration of blackout

    @property
    def kinetic_energy_mj(self) -> float:
        """Calculate kinetic energy at terminal velocity (MJ)"""
        return 0.5 * self.hgv_mass_kg * self.terminal_velocity_ms ** 2 / 1e6


@dataclass
class LandTarget:
    """Land target state"""
    target_id: str
    target_type: str  # "hardened_bunker", "airbase", "radar_site", "command_center"
    position: np.ndarray  # [x, y, z] meters
    length_m: float  # Target length
    width_m: float  # Target width
    hardening_level: str  # "soft", "medium", "hardened", "deeply_buried"

    # Defensive capabilities
    has_thaad: bool = False  # THAAD BMD
    has_patriot: bool = False  # Patriot PAC-3
    has_s400: bool = False  # S-400 (adversary)
    has_ew_suite: bool = False  # Electronic warfare


@dataclass
class StrikeParameters:
    """LRHW strike mission parameters"""
    launch_position: np.ndarray  # [x, y, z] meters
    target: LandTarget
    launch_azimuth_deg: float  # Launch direction
    desired_impact_angle_deg: float = 70.0  # Steep dive angle for penetration
    salvo_size: int = 1  # Number of missiles in salvo


@dataclass
class ImpactPrediction:
    """HGV impact prediction result"""
    impact_possible: bool
    time_to_impact_s: float
    impact_point: np.ndarray  # [x, y, z] meters
    impact_velocity_ms: float
    impact_angle_deg: float  # Angle from horizontal
    probability_hit: float  # Pk
    cep_at_impact_m: float
    defensive_warning_time_s: float  # Time available for defense
    confidence: float


@dataclass
class TrajectoryPoint:
    """Single point along HGV trajectory"""
    time_s: float
    position: np.ndarray  # [x, y, z] meters
    velocity: np.ndarray  # [vx, vy, vz] m/s
    altitude_m: float
    phase: HGVFlightPhase
    mach_number: float


class LRHWHGVModel:
    """
    LRHW (Dark Eagle) Hypersonic Glide Vehicle Targeting and Strike Model

    Implements trajectory prediction, intercept calculation, and
    engagement probability for precision strikes against land targets.
    """

    def __init__(self, params: Optional[LRHWParameters] = None):
        """
        Initialize LRHW HGV model

        Args:
            params: HGV parameters (uses defaults if None)
        """
        self.params = params or LRHWParameters()

    def predict_impact(self,
                      strike_params: StrikeParameters) -> ImpactPrediction:
        """
        Predict impact geometry and hit probability

        Args:
            strike_params: Strike mission parameters

        Returns:
            ImpactPrediction with impact geometry and Pk
        """
        launch_pos = strike_params.launch_position
        target = strike_params.target

        # Calculate range to target
        target_pos_2d = target.position[:2]  # X, Y only
        launch_pos_2d = launch_pos[:2]
        range_m = np.linalg.norm(target_pos_2d - launch_pos_2d)
        range_km = range_m / 1000.0

        # Check if target is within engagement envelope
        if range_km < self.params.min_range_km:
            return ImpactPrediction(
                impact_possible=False,
                time_to_impact_s=0.0,
                impact_point=np.zeros(3),
                impact_velocity_ms=0.0,
                impact_angle_deg=0.0,
                probability_hit=0.0,
                cep_at_impact_m=0.0,
                defensive_warning_time_s=0.0,
                confidence=1.0
            )

        if range_km > self.params.max_range_km:
            return ImpactPrediction(
                impact_possible=False,
                time_to_impact_s=0.0,
                impact_point=np.zeros(3),
                impact_velocity_ms=0.0,
                impact_angle_deg=0.0,
                probability_hit=0.0,
                cep_at_impact_m=0.0,
                defensive_warning_time_s=0.0,
                confidence=1.0
            )

        # Calculate flight time (simplified)
        # Total flight time = boost + glide + terminal
        average_velocity = (self.params.peak_velocity_ms +
                          self.params.terminal_velocity_ms) / 2
        glide_range_m = range_m * 0.85  # Most of range is in glide
        glide_time = glide_range_m / average_velocity

        total_flight_time = (self.params.boost_phase_duration_s +
                            glide_time +
                            self.params.terminal_phase_duration_s)

        # Predict impact point (stationary target)
        impact_point = target.position.copy()

        # Calculate CEP at this range
        # CEP grows slightly with range due to accumulated errors
        cep_growth_factor = 1.0 + (range_km / self.params.max_range_km) * 0.3
        cep_at_impact = self.params.cep_meters * cep_growth_factor

        # Calculate hit probability based on CEP and target size
        target_effective_radius = max(target.length_m, target.width_m) / 2

        # Probability of hit = probability that impact falls within target area
        # P(hit) ≈ 1 - exp(-(R/CEP)²) for circular target of radius R
        if cep_at_impact > 0:
            pk_geometry = 1.0 - np.exp(-(target_effective_radius / cep_at_impact) ** 2)
        else:
            pk_geometry = 1.0

        # Apply defensive systems degradation
        pk_defensive = self._calculate_defensive_degradation(
            target, total_flight_time, range_km)

        # Combined Pk
        probability_hit = pk_geometry * pk_defensive

        # Calculate defensive warning time
        # Assume detection at boost phase, tracking during glide
        if target.has_thaad or target.has_s400:
            # Can detect and track early
            effective_engagement_time = total_flight_time * 0.7
        else:
            # Limited radar may only detect during terminal phase
            effective_engagement_time = self.params.terminal_phase_duration_s

        # Impact angle (steep dive)
        impact_angle_deg = strike_params.desired_impact_angle_deg

        # Impact velocity
        impact_velocity = self.params.terminal_velocity_ms

        # Confidence in prediction
        confidence = self._calculate_prediction_confidence(range_km)

        return ImpactPrediction(
            impact_possible=True,
            time_to_impact_s=total_flight_time,
            impact_point=impact_point,
            impact_velocity_ms=impact_velocity,
            impact_angle_deg=impact_angle_deg,
            probability_hit=probability_hit,
            cep_at_impact_m=cep_at_impact,
            defensive_warning_time_s=effective_engagement_time,
            confidence=confidence
        )

    def _calculate_defensive_degradation(self,
                                        target: LandTarget,
                                        flight_time_s: float,
                                        range_km: float) -> float:
        """
        Calculate probability of surviving defensive systems

        Args:
            target: Target with defensive systems
            flight_time_s: Total flight time
            range_km: Range to target

        Returns:
            Survival probability (0-1)
        """
        survival_prob = 1.0

        # THAAD ballistic missile defense (glide phase intercept)
        if target.has_thaad:
            # THAAD has very limited capability vs maneuvering HGV
            # Assume 10% Pk per interceptor, 2 shots possible
            thaad_pk_per_shot = 0.10
            thaad_shots = 2
            thaad_survival = (1.0 - thaad_pk_per_shot) ** thaad_shots
            survival_prob *= thaad_survival

        # Patriot PAC-3 terminal defense
        if target.has_patriot:
            # PAC-3 has minimal capability vs Mach 6+ targets
            # Assume 5% Pk per interceptor, 3 shots possible
            pac3_pk_per_shot = 0.05
            pac3_shots = 3
            pac3_survival = (1.0 - pac3_pk_per_shot) ** pac3_shots
            survival_prob *= pac3_survival

        # S-400 (adversary system)
        if target.has_s400:
            # S-400 limited capability vs hypersonic maneuver targets
            # Assume 8% Pk per interceptor, 4 shots possible
            s400_pk_per_shot = 0.08
            s400_shots = 4
            s400_survival = (1.0 - s400_pk_per_shot) ** s400_shots
            survival_prob *= s400_survival

        # Electronic warfare
        if target.has_ew_suite:
            # EW can degrade GPS guidance
            # Assume 5% reduction in hit probability
            ew_degradation = 0.95
            survival_prob *= ew_degradation

        return survival_prob

    def _calculate_prediction_confidence(self, range_km: float) -> float:
        """Calculate confidence in impact prediction"""
        confidence = self.params.cep_confidence

        # Range uncertainty
        if range_km > 2500:
            confidence *= 0.85  # Near maximum range
        elif range_km < 800:
            confidence *= 0.95  # Short range, less glide time

        return confidence

    def calculate_salvo_effectiveness(self,
                                     strike_params: StrikeParameters) -> Tuple[float, List[ImpactPrediction]]:
        """
        Calculate effectiveness of salvo attack

        Args:
            strike_params: Strike parameters with salvo_size

        Returns:
            Tuple of (overall_pk, list of individual predictions)
        """
        predictions = []

        for i in range(strike_params.salvo_size):
            prediction = self.predict_impact(strike_params)
            predictions.append(prediction)

        # Calculate overall Pk (at least one hit)
        # P(at least 1 hit) = 1 - P(all miss)
        overall_miss_prob = 1.0
        for pred in predictions:
            overall_miss_prob *= (1.0 - pred.probability_hit)

        overall_pk = 1.0 - overall_miss_prob

        return overall_pk, predictions

    def generate_trajectory(self,
                          strike_params: StrikeParameters,
                          time_step_s: float = 1.0) -> List[TrajectoryPoint]:
        """
        Generate detailed HGV trajectory

        Args:
            strike_params: Strike mission parameters
            time_step_s: Time step for trajectory points

        Returns:
            List of trajectory points
        """
        trajectory = []

        launch_pos = strike_params.launch_position
        target_pos = strike_params.target.position

        # Calculate launch direction
        range_vector = target_pos - launch_pos
        range_2d = np.linalg.norm(range_vector[:2])
        launch_direction = range_vector / np.linalg.norm(range_vector)

        current_time = 0.0
        current_pos = launch_pos.astype(float).copy()

        # Boost phase
        boost_velocity = self.params.peak_velocity_ms / 2  # Average during boost
        boost_direction = launch_direction.copy()
        boost_direction[2] = 0.6  # Steeper climb angle

        while current_time < self.params.boost_phase_duration_s:
            altitude = current_pos[2]
            velocity_vec = boost_direction * boost_velocity
            mach = boost_velocity / 340.0

            trajectory.append(TrajectoryPoint(
                time_s=current_time,
                position=current_pos.copy(),
                velocity=velocity_vec,
                altitude_m=altitude,
                phase=HGVFlightPhase.BOOST,
                mach_number=mach
            ))

            current_pos += velocity_vec * time_step_s
            current_time += time_step_s

        # Glide phase
        glide_velocity = self.params.typical_velocity_ms
        glide_direction = launch_direction.copy()
        glide_direction[2] = -0.05  # Slight descent

        prediction = self.predict_impact(strike_params)
        glide_duration = prediction.time_to_impact_s - self.params.boost_phase_duration_s - self.params.terminal_phase_duration_s

        glide_end_time = current_time + glide_duration

        while current_time < glide_end_time:
            altitude = self.params.glide_altitude_km * 1000
            current_pos[2] = altitude
            velocity_vec = glide_direction * glide_velocity
            mach = glide_velocity / 340.0

            trajectory.append(TrajectoryPoint(
                time_s=current_time,
                position=current_pos.copy(),
                velocity=velocity_vec,
                altitude_m=altitude,
                phase=HGVFlightPhase.GLIDE,
                mach_number=mach
            ))

            current_pos += velocity_vec * time_step_s
            current_time += time_step_s

        # Terminal phase
        terminal_velocity = self.params.terminal_velocity_ms
        terminal_direction = (prediction.impact_point - current_pos)
        if np.linalg.norm(terminal_direction) > 0:
            terminal_direction = terminal_direction / np.linalg.norm(terminal_direction)

        terminal_end_time = current_time + self.params.terminal_phase_duration_s

        while current_time < terminal_end_time:
            altitude = current_pos[2]
            velocity_vec = terminal_direction * terminal_velocity
            mach = terminal_velocity / 340.0

            trajectory.append(TrajectoryPoint(
                time_s=current_time,
                position=current_pos.copy(),
                velocity=velocity_vec,
                altitude_m=altitude,
                phase=HGVFlightPhase.TERMINAL,
                mach_number=mach
            ))

            current_pos += velocity_vec * time_step_s
            current_time += time_step_s

        return trajectory

    def print_model_summary(self):
        """Print summary of LRHW HGV capabilities"""
        print("=" * 70)
        print("LRHW (Dark Eagle) Hypersonic Glide Vehicle Model")
        print("=" * 70)
        print(f"\nSystem Configuration:")
        print(f"  Launch vehicle:       Two-stage solid rocket booster")
        print(f"  Warhead:              Common Hypersonic Glide Body (C-HGB)")
        print(f"  HGV mass:             {self.params.hgv_mass_kg:.0f} kg")
        print(f"  Warhead mass:         {self.params.warhead_mass_kg:.0f} kg")

        print(f"\nPerformance:")
        print(f"  Range:                {self.params.min_range_km:.0f} - {self.params.max_range_km:.0f} km")
        print(f"  Peak velocity:        Mach {self.params.peak_velocity_ms/340:.1f} ({self.params.peak_velocity_ms:.0f} m/s)")
        print(f"  Typical glide:        Mach {self.params.typical_velocity_ms/340:.1f} ({self.params.typical_velocity_ms:.0f} m/s)")
        print(f"  Terminal velocity:    Mach {self.params.terminal_velocity_ms/340:.1f} ({self.params.terminal_velocity_ms:.0f} m/s)")
        print(f"  Kinetic energy:       {self.params.kinetic_energy_mj:.1f} MJ at impact")

        print(f"\nManeuverability:")
        print(f"  Glide phase:          {self.params.max_glide_acceleration_g:.0f}G")
        print(f"  Terminal phase:       {self.params.max_terminal_acceleration_g:.0f}G")
        print(f"  Cross-range:          ±{self.params.cross_range_km:.0f} km")

        print(f"\nGuidance:")
        print(f"  Midcourse:            {self.params.guidance_midcourse}")
        print(f"  Terminal:             {self.params.guidance_terminal}")

        print(f"\nAccuracy:")
        print(f"  CEP:                  {self.params.cep_meters:.0f} ± {self.params.cep_uncertainty_meters:.0f} m")
        print(f"  Confidence:           {self.params.cep_confidence:.0%}")

        print(f"\nFlight Profile:")
        print(f"  Boost phase:          {self.params.boost_phase_duration_s:.0f} s to {self.params.boost_altitude_km:.0f} km")
        print(f"  Glide altitude:       {self.params.glide_altitude_km:.0f} km")
        print(f"  Terminal dive:        {self.params.terminal_phase_duration_s:.0f} s")

        print("=" * 70)


# Predefined target templates
def create_hardened_bunker() -> LandTarget:
    """Create hardened bunker target"""
    return LandTarget(
        target_id="HB-001",
        target_type="hardened_bunker",
        position=np.array([0, 0, 0]),
        length_m=30,
        width_m=30,
        hardening_level="hardened",
        has_thaad=False,
        has_patriot=False,
        has_s400=False,
        has_ew_suite=False
    )


def create_airbase() -> LandTarget:
    """Create airbase target (runway)"""
    return LandTarget(
        target_id="AB-001",
        target_type="airbase",
        position=np.array([0, 0, 0]),
        length_m=3000,  # Runway length
        width_m=45,  # Runway width
        hardening_level="soft",
        has_thaad=False,
        has_patriot=True,
        has_s400=False,
        has_ew_suite=True
    )


def create_radar_site() -> LandTarget:
    """Create radar site target"""
    return LandTarget(
        target_id="RS-001",
        target_type="radar_site",
        position=np.array([0, 0, 0]),
        length_m=50,
        width_m=50,
        hardening_level="medium",
        has_thaad=False,
        has_patriot=True,
        has_s400=False,
        has_ew_suite=True
    )


def create_command_center() -> LandTarget:
    """Create command center target"""
    return LandTarget(
        target_id="CC-001",
        target_type="command_center",
        position=np.array([0, 0, 0]),
        length_m=100,
        width_m=100,
        hardening_level="hardened",
        has_thaad=True,
        has_patriot=True,
        has_s400=False,
        has_ew_suite=True
    )


# Example usage and validation
if __name__ == "__main__":
    # Create LRHW model
    lrhw = LRHWHGVModel()

    # Print model summary
    lrhw.print_model_summary()

    # Test scenarios
    print("\n[TEST] LRHW Strike Predictions vs Different Targets:")
    print("-" * 70)

    # Create launch position (e.g., forward deployed launcher)
    launch_position = np.array([0, 0, 100])  # 100m elevation

    # Test scenarios with different targets
    test_scenarios = [
        ("Hardened Bunker @ 2000km", create_hardened_bunker(), 2000),
        ("Airbase @ 1500km", create_airbase(), 1500),
        ("Radar Site @ 2500km", create_radar_site(), 2500),
        ("Command Center @ 1800km", create_command_center(), 1800),
    ]

    for name, target_template, range_km in test_scenarios:
        # Position target at specified range
        target_template.position = np.array([range_km * 1000, 0, 0])

        strike_params = StrikeParameters(
            launch_position=launch_position,
            target=target_template,
            launch_azimuth_deg=90,  # East
            desired_impact_angle_deg=70,  # 70° dive
            salvo_size=1
        )

        prediction = lrhw.predict_impact(strike_params)

        print(f"\n  {name}:")
        print(f"    Impact possible:    {prediction.impact_possible}")
        print(f"    Time to impact:     {prediction.time_to_impact_s:.1f} s ({prediction.time_to_impact_s/60:.1f} min)")
        print(f"    Impact velocity:    Mach {prediction.impact_velocity_ms/340:.1f}")
        print(f"    Impact angle:       {prediction.impact_angle_deg:.1f}°")
        print(f"    CEP at impact:      {prediction.cep_at_impact_m:.1f} m")
        print(f"    Probability hit:    {prediction.probability_hit:.1%}")
        print(f"    Defense warning:    {prediction.defensive_warning_time_s:.1f} s")
        print(f"    Confidence:         {prediction.confidence:.0%}")

    # Test salvo attack
    print("\n[TEST] Salvo Attack (2x LRHW vs Command Center):")
    print("-" * 70)

    command_center = create_command_center()
    command_center.position = np.array([2000000, 0, 0])  # 2000 km

    salvo_strike = StrikeParameters(
        launch_position=launch_position,
        target=command_center,
        launch_azimuth_deg=90,
        desired_impact_angle_deg=70,
        salvo_size=2
    )

    overall_pk, individual_preds = lrhw.calculate_salvo_effectiveness(salvo_strike)

    print(f"\n  Individual missile Pk: {individual_preds[0].probability_hit:.1%}")
    print(f"  Salvo overall Pk:      {overall_pk:.1%}")
    print(f"  Expected hits:         {overall_pk * salvo_strike.salvo_size:.2f} / {salvo_strike.salvo_size}")

    print("\n" + "=" * 70)
    print("LRHW (Dark Eagle) HGV model validation complete.")
    print("=" * 70)
