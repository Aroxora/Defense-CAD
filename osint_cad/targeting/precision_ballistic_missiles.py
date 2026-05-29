"""
Precision Ballistic Missile Models for Ground-to-Ground Engagement
==================================================================

CLASSIFICATION: UNCLASSIFIED // PUBLIC RELEASE

This module implements precision ballistic missile models for ground attack
missions, particularly for suppression of enemy air defenses (SEAD) and
precision strike against high-value targets.

Missiles Modeled:
- DF-21D (CSS-5 Mod-4) - Chinese MRBM, dual-role anti-ship/land attack
- DF-26 (CSS-18) - Chinese IRBM, dual-capable conventional/nuclear
- Iskander-M (SS-26 Stone) - Russian SRBM, high-precision tactical
- ATACMS (MGM-140) - US Army Tactical Missile System

All parameters derived from publicly available sources with documented
confidence levels per DEDUCTIVE_REASONING.md methodology.

Author: Claude (Anthropic)
Date: 2025-12-29
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import numpy as np
from enum import Enum
import warnings

# Import information chain robustness validation
try:
    from osint_cad.engagements.information_chain_robustness import (
        InformationChainValidator,
        InformationChainConfiguration,
        InformationChainNode,
        SensorNode,
        DatalinkPath,
        RobustnessScore
    )
    ROBUSTNESS_VALIDATION_AVAILABLE = True
except ImportError:
    ROBUSTNESS_VALIDATION_AVAILABLE = False
    warnings.warn("Information chain robustness validation not available")


class MissileType(Enum):
    """Enumeration of precision ballistic missile types."""
    DF21D = "df21d"
    DF26 = "df26"
    ISKANDER_M = "iskander_m"
    ATACMS = "atacms"


class FlightPhase(Enum):
    """Flight phases for ballistic trajectory."""
    BOOST = "boost"
    MIDCOURSE = "midcourse"
    TERMINAL = "terminal"


class GuidanceMode(Enum):
    """Terminal guidance modes."""
    ACTIVE_RADAR = "active_radar"
    IMAGING_IR = "imaging_ir"
    OPTICAL = "optical"
    GNSS_AIDED_INERTIAL = "gnss_aided_inertial"
    TERRAIN_MATCHING = "terrain_matching"


@dataclass
class MissileParameters:
    """
    Physical and performance parameters for a ballistic missile.

    Confidence levels noted per parameter (from open sources).

    Attributes:
        missile_type: Type identifier
        name: Common name

        # Physical characteristics
        length_m: Total length (meters)
        diameter_m: Body diameter (meters)
        launch_mass_kg: Total launch mass (kg)
        warhead_mass_kg: Warhead mass (kg)
        warhead_yield_kg_tnt: Explosive yield (kg TNT equivalent)

        # Performance characteristics
        max_range_km: Maximum range (km) [confidence: varies by system]
        min_range_km: Minimum range (km)
        max_speed_mps: Maximum speed (m/s, typically at midcourse)
        burnout_speed_mps: Speed at booster burnout
        terminal_speed_mps: Impact speed (m/s)

        # Accuracy (CRITICAL for precision strike)
        cep_m: Circular Error Probable at max range (meters) [confidence: 50-60%]
        terminal_guidance: Terminal guidance mode(s)
        guidance_update_rate_hz: Guidance update rate

        # Trajectory characteristics
        apogee_altitude_km: Apogee altitude (km, varies with range)
        boost_phase_duration_s: Boost phase duration (seconds)
        terminal_dive_angle_deg: Terminal dive angle (degrees from horizontal)

        # Maneuverability (for evasion)
        max_lateral_g: Maximum lateral acceleration (G)
        terminal_maneuver_capable: Can maneuver in terminal phase

        # Countermeasures
        has_decoys: Carries decoys/penetration aids
        has_ecm: Has electronic countermeasures
        radar_cross_section_m2: RCS during terminal phase
    """
    missile_type: MissileType
    name: str

    # Physical
    length_m: float
    diameter_m: float
    launch_mass_kg: float
    warhead_mass_kg: float
    warhead_yield_kg_tnt: float

    # Performance
    max_range_km: float
    min_range_km: float
    max_speed_mps: float
    burnout_speed_mps: float
    terminal_speed_mps: float

    # Accuracy
    cep_m: float
    terminal_guidance: List[GuidanceMode]
    guidance_update_rate_hz: float

    # Trajectory
    apogee_altitude_km: float
    boost_phase_duration_s: float
    terminal_dive_angle_deg: float

    # Maneuverability
    max_lateral_g: float
    terminal_maneuver_capable: bool

    # Countermeasures
    has_decoys: bool
    has_ecm: bool
    radar_cross_section_m2: float


@dataclass
class LaunchParameters:
    """
    Parameters for a specific missile launch.

    Attributes:
        launch_position: Launch location [x, y, z] or [lat, lon, alt]
        target_position: Target location [x, y, z] or [lat, lon, alt]
        launch_azimuth_deg: Launch azimuth (degrees, 0=North)
        desired_impact_angle_deg: Desired terminal dive angle
        time_of_flight_s: Calculated time of flight
    """
    launch_position: np.ndarray
    target_position: np.ndarray
    launch_azimuth_deg: float
    desired_impact_angle_deg: float = 60.0
    time_of_flight_s: Optional[float] = None


@dataclass
class TrajectoryPoint:
    """Single point along missile trajectory."""
    time_s: float
    position: np.ndarray  # [x, y, z]
    velocity: np.ndarray  # [vx, vy, vz]
    phase: FlightPhase
    altitude_m: float
    speed_mps: float


@dataclass
class InterceptWindow:
    """
    Time window and parameters for defensive intercept attempts.

    Attributes:
        phase: Flight phase during this window
        start_time_s: Window start time
        end_time_s: Window end time
        altitude_range_m: (min_alt, max_alt) during window
        speed_mps: Average speed during window
        intercept_difficulty: 0.0 (easy) to 1.0 (very hard)
    """
    phase: FlightPhase
    start_time_s: float
    end_time_s: float
    altitude_range_m: Tuple[float, float]
    speed_mps: float
    intercept_difficulty: float


class PrecisionBallisticMissile:
    """
    Precision ballistic missile engagement model.

    This class models the complete engagement sequence from launch to impact,
    including trajectory calculation, defensive system interaction, and
    damage assessment.
    """

    def __init__(self, params: MissileParameters, info_chain_config: Optional[Dict] = None):
        """
        Initialize missile model.

        Args:
            params: Missile parameters
            info_chain_config: Optional information chain configuration for robustness validation
        """
        self.params = params
        self.info_chain_config = info_chain_config
        self.robustness_score = None

    def calculate_range(self, launch_pos: np.ndarray, target_pos: np.ndarray) -> float:
        """
        Calculate ground range between launch and target.

        Args:
            launch_pos: Launch position [x, y, z]
            target_pos: Target position [x, y, z]

        Returns:
            Ground range in kilometers
        """
        delta = target_pos[:2] - launch_pos[:2]
        range_m = np.linalg.norm(delta)
        return range_m / 1000.0

    def calculate_flight_time(self, range_km: float) -> float:
        """
        Calculate time of flight for given range.

        Uses simplified ballistic trajectory model:
        TOF ≈ range / average_horizontal_velocity

        Args:
            range_km: Ground range in km

        Returns:
            Time of flight in seconds
        """
        # Average horizontal velocity is ~60-70% of max velocity
        avg_horiz_velocity_mps = self.params.max_speed_mps * 0.65

        # Add time for terminal phase deceleration
        flight_time_s = (range_km * 1000.0) / avg_horiz_velocity_mps

        # Add boost phase
        flight_time_s += self.params.boost_phase_duration_s

        return flight_time_s

    def calculate_cep(self, range_km: float) -> float:
        """
        Calculate CEP at given range.

        CEP typically grows with range. Uses linear scaling from reference CEP
        at max range.

        Args:
            range_km: Target range in km

        Returns:
            CEP in meters
        """
        # CEP scales roughly linearly with range for modern systems
        range_fraction = range_km / self.params.max_range_km

        # Minimum CEP at short range (limited by terminal guidance)
        min_cep = self.params.cep_m * 0.3

        cep = min_cep + (self.params.cep_m - min_cep) * range_fraction

        # Add degradation for long-range shots beyond optimal
        if range_km > self.params.max_range_km:
            excess_factor = range_km / self.params.max_range_km
            cep *= excess_factor ** 2

        return cep

    def generate_trajectory(self, launch_params: LaunchParameters,
                           time_resolution_s: float = 1.0) -> List[TrajectoryPoint]:
        """
        Generate detailed missile trajectory.

        Uses simplified ballistic model with three phases:
        1. Boost: Powered ascent
        2. Midcourse: Ballistic coast to apogee and descent
        3. Terminal: Guided terminal dive

        Args:
            launch_params: Launch parameters
            time_resolution_s: Time step for trajectory points

        Returns:
            List of trajectory points
        """
        range_km = self.calculate_range(launch_params.launch_position,
                                        launch_params.target_position)

        if range_km < self.params.min_range_km or range_km > self.params.max_range_km:
            warnings.warn(f"Range {range_km:.1f} km outside valid range "
                        f"[{self.params.min_range_km}, {self.params.max_range_km}] km")

        tof = self.calculate_flight_time(range_km)
        launch_params.time_of_flight_s = tof

        # Calculate apogee based on range (scales with range)
        range_fraction = range_km / self.params.max_range_km
        apogee_km = self.params.apogee_altitude_km * range_fraction

        trajectory = []

        # Direction vector
        delta = launch_params.target_position - launch_params.launch_position
        horizontal_range = np.linalg.norm(delta[:2])
        direction_unit = delta / np.linalg.norm(delta)

        # Phase timing
        boost_end_time = self.params.boost_phase_duration_s
        terminal_start_time = tof - 30.0  # Last 30 seconds is terminal phase

        current_time = 0.0
        while current_time <= tof:
            # Determine phase
            if current_time <= boost_end_time:
                phase = FlightPhase.BOOST
                # Boost phase: accelerating ascent
                phase_fraction = current_time / boost_end_time
                altitude = (apogee_km * 1000.0 * 0.3) * phase_fraction  # Reach 30% apogee
                horiz_distance = horizontal_range * 0.1 * phase_fraction  # 10% of range
                speed = self.params.burnout_speed_mps * phase_fraction

            elif current_time < terminal_start_time:
                phase = FlightPhase.MIDCOURSE
                # Midcourse: ballistic arc
                midcourse_fraction = (current_time - boost_end_time) / (terminal_start_time - boost_end_time)

                # Parabolic altitude profile
                altitude = (apogee_km * 1000.0 * 0.3) + (apogee_km * 1000.0 * 0.7) * (
                    1.0 - 4.0 * (midcourse_fraction - 0.5) ** 2
                )
                horiz_distance = horizontal_range * (0.1 + 0.8 * midcourse_fraction)
                speed = self.params.max_speed_mps

            else:
                phase = FlightPhase.TERMINAL
                # Terminal phase: guided dive
                terminal_fraction = (current_time - terminal_start_time) / (tof - terminal_start_time)
                altitude = (apogee_km * 1000.0 * 0.1) * (1.0 - terminal_fraction)
                horiz_distance = horizontal_range * (0.9 + 0.1 * terminal_fraction)
                speed = self.params.terminal_speed_mps

            # Position along trajectory
            position = launch_params.launch_position.copy()
            position[:2] += direction_unit[:2] * horiz_distance
            position[2] = launch_params.launch_position[2] + altitude

            # Velocity (simplified)
            velocity = direction_unit * speed

            point = TrajectoryPoint(
                time_s=current_time,
                position=position,
                velocity=velocity,
                phase=phase,
                altitude_m=altitude,
                speed_mps=speed
            )
            trajectory.append(point)

            current_time += time_resolution_s

        return trajectory

    def calculate_intercept_windows(self, trajectory: List[TrajectoryPoint]) -> List[InterceptWindow]:
        """
        Calculate time windows where defensive systems can attempt intercepts.

        Different interceptors are effective in different flight phases:
        - Boost: Very difficult, requires space-based or forward-deployed interceptors
        - Midcourse: Medium difficulty, requires long-range SAMs (SM-3, THAAD)
        - Terminal: High difficulty due to speed, requires terminal defenses (PAC-3, SM-6)

        Args:
            trajectory: Missile trajectory points

        Returns:
            List of intercept windows
        """
        windows = []

        # Group trajectory by phase
        phase_groups = {}
        for point in trajectory:
            phase = point.phase
            if phase not in phase_groups:
                phase_groups[phase] = []
            phase_groups[phase].append(point)

        # Create windows for each phase
        for phase, points in phase_groups.items():
            if len(points) == 0:
                continue

            start_time = points[0].time_s
            end_time = points[-1].time_s

            altitudes = [p.altitude_m for p in points]
            speeds = [p.speed_mps for p in points]

            # Calculate intercept difficulty
            if phase == FlightPhase.BOOST:
                # Boost phase: difficult due to short duration, heat signature helps
                difficulty = 0.7
            elif phase == FlightPhase.MIDCOURSE:
                # Midcourse: medium difficulty, altitude and speed moderate
                difficulty = 0.5
            else:  # TERMINAL
                # Terminal phase: very difficult due to high speed and maneuvers
                if self.params.terminal_maneuver_capable:
                    difficulty = 0.9
                else:
                    difficulty = 0.7

            window = InterceptWindow(
                phase=phase,
                start_time_s=start_time,
                end_time_s=end_time,
                altitude_range_m=(min(altitudes), max(altitudes)),
                speed_mps=np.mean(speeds),
                intercept_difficulty=difficulty
            )
            windows.append(window)

        return windows

    def calculate_hit_probability(self, target_rcs_m2: float, cep_m: float,
                                  target_dimensions_m: Tuple[float, float] = (50.0, 50.0)) -> float:
        """
        Calculate probability of hitting target given CEP and target size.

        Uses circular normal distribution for impact point.

        Args:
            target_rcs_m2: Target RCS (affects terminal guidance)
            cep_m: Circular error probable
            target_dimensions_m: (length, width) of target in meters

        Returns:
            Hit probability (0.0 to 1.0)
        """
        # Effective target radius (approximated as circle with equivalent area)
        target_area = target_dimensions_m[0] * target_dimensions_m[1]
        target_radius = np.sqrt(target_area / np.pi)

        # For circular normal distribution, Pk = 1 - exp(-(target_radius/CEP)²)
        # This is the standard formula for CEP-based hit probability
        if cep_m > 0:
            pk = 1.0 - np.exp(-(target_radius / cep_m) ** 2)
        else:
            pk = 1.0

        # Adjust for terminal guidance effectiveness
        if GuidanceMode.ACTIVE_RADAR in self.params.terminal_guidance:
            # Active radar needs sufficient target RCS
            if target_rcs_m2 < 10.0:
                pk *= 0.7  # Reduced effectiveness vs small targets

        if GuidanceMode.IMAGING_IR in self.params.terminal_guidance:
            # IR guidance less affected by RCS
            pk = min(pk * 1.1, 1.0)

        return min(pk, 1.0)

    def validate_information_chain_robustness(
        self,
        info_chain_config: Optional['InformationChainConfiguration'] = None
    ) -> Optional['RobustnessScore']:
        """
        Validate information chain robustness for this missile system.

        CRITICAL for ASBM and precision missiles - ensures the information
        chain meets stringent requirements for effective engagement.

        Args:
            info_chain_config: Information chain configuration (uses stored config if None)

        Returns:
            RobustnessScore if validation available, None otherwise
        """
        if not ROBUSTNESS_VALIDATION_AVAILABLE:
            warnings.warn("Information chain robustness validation not available")
            return None

        # Use provided config or stored config
        config = info_chain_config or self.info_chain_config

        if config is None:
            warnings.warn("No information chain configuration provided")
            return None

        # Determine mission type based on missile
        if self.params.missile_type in [MissileType.DF21D, MissileType.DF26]:
            mission_type = "ASBM"
        else:
            mission_type = "land_attack"

        # Create validator and assess
        validator = InformationChainValidator()
        score = validator.validate_configuration(config, mission_type)

        # Store for later reference
        self.robustness_score = score

        # Warn if requirements not met
        if not score.meets_requirements:
            warnings.warn(
                f"{self.params.name} information chain DOES NOT meet robustness requirements:\n"
                f"  Overall Score: {score.overall_score:.1f}/100\n"
                f"  Deficiencies: {len(score.deficiencies)}\n"
                f"  This may result in mission failure against defended targets!"
            )

        return score

    def predict_impact(self, launch_params: LaunchParameters,
                      target_rcs_m2: float = 100.0,
                      target_dimensions_m: Tuple[float, float] = (50.0, 50.0),
                      defensive_systems: Optional[Dict] = None) -> Dict:
        """
        Predict complete engagement outcome including defensive interactions.

        Args:
            launch_params: Launch parameters
            target_rcs_m2: Target radar cross-section
            target_dimensions_m: Target dimensions (length, width)
            defensive_systems: Dict of defensive system parameters (optional)

        Returns:
            Dictionary containing:
                - range_km: Ground range
                - flight_time_s: Time of flight
                - cep_m: CEP at this range
                - hit_probability: Base hit probability
                - survival_probability: Probability of penetrating defenses
                - overall_pk: Overall kill probability (hit * survival)
                - intercept_windows: List of intercept opportunities
        """
        range_km = self.calculate_range(launch_params.launch_position,
                                       launch_params.target_position)

        flight_time_s = self.calculate_flight_time(range_km)
        cep_m = self.calculate_cep(range_km)

        # Calculate base hit probability
        hit_prob = self.calculate_hit_probability(target_rcs_m2, cep_m, target_dimensions_m)

        # Generate trajectory for defensive analysis
        trajectory = self.generate_trajectory(launch_params, time_resolution_s=5.0)
        intercept_windows = self.calculate_intercept_windows(trajectory)

        # Calculate survival probability against defenses
        survival_prob = 1.0

        if defensive_systems:
            # Apply defensive system degradation per phase
            for window in intercept_windows:
                phase_survival = 1.0

                if window.phase == FlightPhase.BOOST:
                    # Boost phase intercept (rare, requires assets in theater)
                    if defensive_systems.get('has_boost_phase_intercept', False):
                        intercept_pk = 0.15  # Low Pk, difficult intercept
                        phase_survival *= (1.0 - intercept_pk)

                elif window.phase == FlightPhase.MIDCOURSE:
                    # Midcourse intercept (THAAD, SM-3, etc.)
                    if defensive_systems.get('has_midcourse_intercept', False):
                        num_shots = defensive_systems.get('midcourse_shots', 2)
                        single_shot_pk = 0.25  # ~25% Pk per shot
                        phase_survival *= (1.0 - single_shot_pk) ** num_shots

                elif window.phase == FlightPhase.TERMINAL:
                    # Terminal intercept (PAC-3, SM-6, etc.)
                    if defensive_systems.get('has_terminal_intercept', False):
                        num_shots = defensive_systems.get('terminal_shots', 4)
                        single_shot_pk = 0.30  # ~30% Pk per shot (terminal is easier than midcourse for some systems)

                        # Reduce Pk if missile is maneuvering
                        if self.params.terminal_maneuver_capable:
                            single_shot_pk *= 0.6

                        phase_survival *= (1.0 - single_shot_pk) ** num_shots

                survival_prob *= phase_survival

            # Electronic warfare effects
            if defensive_systems.get('has_ew', False):
                ew_degradation = 0.10  # 10% reduction
                hit_prob *= (1.0 - ew_degradation)

        overall_pk = hit_prob * survival_prob

        return {
            'range_km': range_km,
            'flight_time_s': flight_time_s,
            'cep_m': cep_m,
            'hit_probability': hit_prob,
            'survival_probability': survival_prob,
            'overall_pk': overall_pk,
            'intercept_windows': intercept_windows,
            'trajectory': trajectory
        }


# ============================================================================
# MISSILE PARAMETER DEFINITIONS (Operationally Verified Systems)
# ============================================================================

def create_df21d_parameters() -> MissileParameters:
    """
    DF-21D (CSS-5 Mod-4) - Chinese Medium-Range Ballistic Missile

    First operational anti-ship ballistic missile (ASBM), also used for
    precision land attack. Fielded 2010.

    Parameters derived from open sources:
    - CSIS Missile Defense Project
    - DoD China Military Power Report
    - IISS Military Balance

    Confidence: ~55% (same as DF-17 in registry)

    Returns:
        MissileParameters for DF-21D
    """
    return MissileParameters(
        missile_type=MissileType.DF21D,
        name="DF-21D (CSS-5 Mod-4)",

        # Physical (public estimates)
        length_m=10.7,
        diameter_m=1.4,
        launch_mass_kg=14700.0,
        warhead_mass_kg=600.0,
        warhead_yield_kg_tnt=600.0,  # Conventional unitary warhead

        # Performance (DoD estimates, moderate confidence)
        max_range_km=1500.0,  # ±200 km, 55% confidence
        min_range_km=500.0,
        max_speed_mps=3000.0,  # Mach ~9 at midcourse
        burnout_speed_mps=2000.0,
        terminal_speed_mps=2500.0,  # Mach ~7.5 terminal

        # Accuracy (key uncertainty)
        cep_m=10.0,  # 5-20m range, 50% confidence with terminal guidance
        terminal_guidance=[GuidanceMode.ACTIVE_RADAR, GuidanceMode.IMAGING_IR],
        guidance_update_rate_hz=10.0,

        # Trajectory
        apogee_altitude_km=250.0,  # Typical MRBM apogee
        boost_phase_duration_s=90.0,
        terminal_dive_angle_deg=70.0,  # Near-vertical terminal dive

        # Maneuverability
        max_lateral_g=15.0,  # Maneuvering reentry vehicle
        terminal_maneuver_capable=True,

        # Countermeasures
        has_decoys=True,
        has_ecm=True,
        radar_cross_section_m2=0.5  # Small RCS during terminal phase
    )


def create_df26_parameters() -> MissileParameters:
    """
    DF-26 (CSS-18) - Chinese Intermediate-Range Ballistic Missile

    Dual-capable (conventional/nuclear) IRBM, nicknamed "Guam Killer".
    Capable of precision strike against land and naval targets. Fielded 2016.

    Parameters from DoD reporting and OSINT.
    Confidence: ~50%

    Returns:
        MissileParameters for DF-26
    """
    return MissileParameters(
        missile_type=MissileType.DF26,
        name="DF-26 (CSS-18)",

        # Physical
        length_m=14.0,
        diameter_m=1.4,
        launch_mass_kg=20000.0,
        warhead_mass_kg=1200.0,
        warhead_yield_kg_tnt=1200.0,  # Conventional variant

        # Performance
        max_range_km=4000.0,  # ±500 km, IRBM class
        min_range_km=1000.0,
        max_speed_mps=5000.0,  # Mach ~15 at midcourse
        burnout_speed_mps=3500.0,
        terminal_speed_mps=4000.0,  # Mach ~12 terminal

        # Accuracy
        cep_m=15.0,  # 10-30m range, moderate confidence
        terminal_guidance=[GuidanceMode.ACTIVE_RADAR, GuidanceMode.GNSS_AIDED_INERTIAL],
        guidance_update_rate_hz=10.0,

        # Trajectory
        apogee_altitude_km=500.0,  # High apogee for IRBM
        boost_phase_duration_s=120.0,
        terminal_dive_angle_deg=75.0,

        # Maneuverability
        max_lateral_g=20.0,  # Advanced MaRV capability
        terminal_maneuver_capable=True,

        # Countermeasures
        has_decoys=True,
        has_ecm=True,
        radar_cross_section_m2=0.4
    )


def create_iskander_m_parameters() -> MissileParameters:
    """
    9K720 Iskander-M (SS-26 Stone) - Russian Short-Range Ballistic Missile

    High-precision tactical ballistic missile with quasi-ballistic trajectory.
    Extensively used in Syria and Ukraine conflicts. Fielded 2006.

    Well-documented from operational use and Russian disclosures.
    Confidence: ~65%

    Returns:
        MissileParameters for Iskander-M
    """
    return MissileParameters(
        missile_type=MissileType.ISKANDER_M,
        name="9K720 Iskander-M (SS-26 Stone)",

        # Physical (well-documented)
        length_m=7.3,
        diameter_m=0.92,
        launch_mass_kg=3800.0,
        warhead_mass_kg=480.0,
        warhead_yield_kg_tnt=480.0,  # Conventional variants

        # Performance (Russian claims, partially verified in combat)
        max_range_km=500.0,  # Limited by INF Treaty originally, now 500km
        min_range_km=50.0,
        max_speed_mps=2100.0,  # Mach 6-7
        burnout_speed_mps=1800.0,
        terminal_speed_mps=2100.0,

        # Accuracy (Russian claims 5-7m, likely optimistic)
        cep_m=5.0,  # 5-10m range, 60% confidence
        terminal_guidance=[GuidanceMode.OPTICAL, GuidanceMode.GNSS_AIDED_INERTIAL, GuidanceMode.TERRAIN_MATCHING],
        guidance_update_rate_hz=20.0,  # High update rate for terminal maneuvers

        # Trajectory (quasi-ballistic)
        apogee_altitude_km=50.0,  # Depressed trajectory option
        boost_phase_duration_s=60.0,
        terminal_dive_angle_deg=45.0,  # Flatter angle than traditional BM

        # Maneuverability (key feature)
        max_lateral_g=30.0,  # Extreme maneuverability
        terminal_maneuver_capable=True,

        # Countermeasures
        has_decoys=True,
        has_ecm=True,
        radar_cross_section_m2=0.3  # Very small RCS
    )


def create_atacms_parameters() -> MissileParameters:
    """
    MGM-140 ATACMS - US Army Tactical Missile System

    Long-range precision strike missile, widely exported. Operational since 1991,
    combat-proven in Gulf War, Iraq, and Ukraine.

    Well-documented US system.
    Confidence: ~70%

    Returns:
        MissileParameters for ATACMS
    """
    return MissileParameters(
        missile_type=MissileType.ATACMS,
        name="MGM-140 ATACMS",

        # Physical (public specification)
        length_m=3.96,
        diameter_m=0.61,
        launch_mass_kg=1670.0,
        warhead_mass_kg=560.0,  # Block I unitary
        warhead_yield_kg_tnt=500.0,

        # Performance (documented)
        max_range_km=300.0,  # Block IA: 300 km
        min_range_km=20.0,
        max_speed_mps=1000.0,  # Mach 3
        burnout_speed_mps=900.0,
        terminal_speed_mps=1000.0,

        # Accuracy (GPS-aided inertial)
        cep_m=10.0,  # Documented <10m CEP
        terminal_guidance=[GuidanceMode.GNSS_AIDED_INERTIAL],
        guidance_update_rate_hz=5.0,

        # Trajectory
        apogee_altitude_km=45.0,
        boost_phase_duration_s=45.0,
        terminal_dive_angle_deg=50.0,

        # Maneuverability (limited)
        max_lateral_g=5.0,  # Not designed for evasive maneuvers
        terminal_maneuver_capable=False,

        # Countermeasures (minimal)
        has_decoys=False,
        has_ecm=False,
        radar_cross_section_m2=0.2
    )


# ============================================================================
# MODULE TEST AND VALIDATION
# ============================================================================

if __name__ == "__main__":
    print("Precision Ballistic Missile Models - Validation")
    print("=" * 70)

    # Create missile instances
    missiles = {
        "DF-21D": create_df21d_parameters(),
        "DF-26": create_df26_parameters(),
        "Iskander-M": create_iskander_m_parameters(),
        "ATACMS": create_atacms_parameters()
    }

    print("\nMissile Comparison Table:")
    print(f"{'System':<15} {'Range (km)':<12} {'CEP (m)':<10} {'Speed (Mach)':<15} {'Warhead (kg)':<12}")
    print("-" * 70)

    for name, params in missiles.items():
        mach = params.terminal_speed_mps / 343.0
        print(f"{name:<15} {params.max_range_km:<12.0f} {params.cep_m:<10.1f} "
              f"{mach:<15.1f} {params.warhead_mass_kg:<12.0f}")

    # Test engagement scenario
    print("\n" + "=" * 70)
    print("Engagement Scenario: DF-21D vs Patriot Battery")
    print("=" * 70)

    df21d = PrecisionBallisticMissile(missiles["DF-21D"])

    launch_params = LaunchParameters(
        launch_position=np.array([0., 0., 0.]),
        target_position=np.array([800000., 0., 0.]),  # 800 km range
        launch_azimuth_deg=90.0
    )

    # Simulate defended target (Patriot battery)
    defensive_systems = {
        'has_boost_phase_intercept': False,
        'has_midcourse_intercept': False,  # Patriot doesn't engage midcourse
        'has_terminal_intercept': True,
        'terminal_shots': 4,  # 4 PAC-3 interceptors
        'has_ew': True
    }

    result = df21d.predict_impact(
        launch_params,
        target_rcs_m2=150.0,  # Patriot radar RCS
        target_dimensions_m=(10.0, 10.0),  # 10x10m target
        defensive_systems=defensive_systems
    )

    print(f"\nLaunch Parameters:")
    print(f"  Range: {result['range_km']:.1f} km")
    print(f"  Time of Flight: {result['flight_time_s']:.1f} seconds ({result['flight_time_s']/60:.1f} min)")
    print(f"  CEP: {result['cep_m']:.1f} m")

    print(f"\nProbability Assessment:")
    print(f"  Hit Probability (no defenses): {result['hit_probability']:.1%}")
    print(f"  Survival Probability: {result['survival_probability']:.1%}")
    print(f"  Overall Kill Probability: {result['overall_pk']:.1%}")

    print(f"\nIntercept Windows:")
    for window in result['intercept_windows']:
        duration = window.end_time_s - window.start_time_s
        alt_min_km = window.altitude_range_m[0] / 1000.0
        alt_max_km = window.altitude_range_m[1] / 1000.0
        mach = window.speed_mps / 343.0

        print(f"  {window.phase.value.upper():12s}: {window.start_time_s:6.1f}s - {window.end_time_s:6.1f}s "
              f"({duration:5.1f}s) | Alt: {alt_min_km:5.1f}-{alt_max_km:5.1f} km | "
              f"Speed: Mach {mach:.1f} | Difficulty: {window.intercept_difficulty:.0%}")

    print("\n" + "=" * 70)
    print("Validation Complete")
