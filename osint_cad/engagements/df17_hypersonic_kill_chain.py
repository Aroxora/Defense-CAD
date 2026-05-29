#!/usr/bin/env python3
"""
DF-17 Hypersonic Glide Vehicle Integrated Kill Chain

Optimizes kill probability through integrated sensor-to-shooter chain:
- AWACS (KJ-500/KJ-2000) initial target cueing
- Beidou satellite constellation midcourse guidance
- DF-17 HGV trajectory optimization
- Terminal maneuvering and seeker acquisition

Kill Chain: AWACS → Launch → Beidou Midcourse → Terminal Acquisition → Impact
"""

import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np

# Import calculation logger for CI/CD integration
try:
    from osint_cad.util.calculation_logger import CalculationLogger
except ImportError:
    # Fallback minimal logger
    class CalculationLogger:
        def __init__(self, name): self.name = name
        def section(self, name): pass
        def log_calculation(self, **kwargs): pass
        def log_algorithm(self, **kwargs): pass
        def log_validation(self, **kwargs): pass
        def complete(self): return {"algorithms": 0, "calculations": 0}
        def export_report(self, *args): pass


# ==============================================================================
# ENUMERATIONS AND CONSTANTS
# ==============================================================================

class TargetType(Enum):
    """Target categories for DF-17 engagement"""
    CARRIER_STRIKE_GROUP = "carrier_strike_group"
    THAAD_BATTERY = "thaad_battery"
    AEGIS_ASHORE = "aegis_ashore"
    AIRBASE_HARDENED = "airbase_hardened"
    AIRBASE_SOFT = "airbase_soft"
    C4ISR_NODE = "c4isr_node"
    PORT_FACILITY = "port_facility"


class GlidePhase(Enum):
    """DF-17 flight phases"""
    BOOST = "boost"
    SEPARATION = "separation"
    PULL_UP = "pull_up"
    GLIDE = "glide"
    TERMINAL_DIVE = "terminal_dive"
    IMPACT = "impact"


# Physical constants
EARTH_RADIUS_KM = 6371.0
G0 = 9.80665  # m/s^2
GAMMA = 1.4  # Air specific heat ratio
R_AIR = 287.05  # J/(kg·K)


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class DF17Characteristics:
    """DF-17 hypersonic glide vehicle physical parameters"""
    name: str = "DF-17"

    # Boost phase (DF-ZF glide vehicle on DF-16B booster)
    booster_range_km: float = 1800.0  # Maximum range
    min_range_km: float = 500.0  # Minimum effective range
    boost_burnout_altitude_km: float = 60.0
    boost_burnout_velocity_ms: float = 2000.0  # ~Mach 6 at burnout

    # Glide vehicle parameters
    glide_l_d_ratio: float = 3.5  # Lift-to-drag ratio (estimated)
    glide_mass_kg: float = 600.0  # Warhead + guidance mass
    cross_range_capability_km: float = 400.0  # Lateral maneuver

    # Terminal phase
    terminal_velocity_mach: float = 5.0  # Minimum terminal Mach
    terminal_maneuver_g: float = 20.0  # G-loading capability
    terminal_dive_angle_deg: float = 45.0  # Steep terminal dive

    # Guidance system
    ins_drift_m_per_s: float = 0.5  # Inertial drift rate
    seeker_acquisition_range_km: float = 30.0
    seeker_fov_deg: float = 15.0

    # Kill probability components
    cep_m: float = 15.0  # With terminal guidance
    pk_given_hit: float = 0.95  # Against most targets


@dataclass
class BeidouConstellation:
    """Beidou-3 satellite navigation and data relay"""
    name: str = "Beidou-3"

    # Constellation parameters
    meo_satellites: int = 24  # Medium Earth Orbit
    igso_satellites: int = 3  # Inclined Geosynchronous
    geo_satellites: int = 3  # Geostationary

    # Accuracy (Asia-Pacific region)
    position_accuracy_m: float = 2.5  # Horizontal
    velocity_accuracy_ms: float = 0.1
    timing_accuracy_ns: float = 20.0

    # Short Message Service for datalink
    sms_capacity_chars: int = 1200  # Per message
    sms_latency_s: float = 1.0

    # Coverage and availability
    asia_pacific_availability: float = 0.995
    global_availability: float = 0.98

    # Update rate for midcourse guidance
    position_update_rate_hz: float = 10.0

    def get_position_update_accuracy(self, target_velocity_ms: float) -> float:
        """Calculate position uncertainty after Beidou update"""
        # Position error plus velocity integration over latency
        velocity_error = self.velocity_accuracy_ms * self.sms_latency_s
        return math.sqrt(self.position_accuracy_m**2 + velocity_error**2)


@dataclass
class AWACSPlatform:
    """AWACS platform for initial target cueing"""
    name: str
    radar_type: str
    detection_range_km: float
    track_accuracy_m: float
    datalink_latency_s: float
    availability: float
    altitude_m: float
    endurance_hours: float


@dataclass
class TargetCharacteristics:
    """Target platform characteristics for engagement"""
    target_type: TargetType
    name: str
    length_m: float
    width_m: float
    velocity_kts: float  # 0 for stationary
    hardening_factor: float  # 1.0 = soft, 10.0 = hardened bunker
    defense_systems: List[str]
    defense_pk_per_interceptor: float
    interceptor_salvo_size: int
    reaction_time_s: float  # Time to launch interceptors


@dataclass
class GlideTrajectoryPoint:
    """Single point in glide trajectory"""
    time_s: float
    altitude_km: float
    downrange_km: float
    crossrange_km: float
    velocity_ms: float
    mach: float
    phase: GlidePhase
    position_error_m: float  # Accumulated INS error


@dataclass
class EngagementResult:
    """Results of DF-17 engagement calculation"""
    target_name: str
    target_type: TargetType
    range_km: float

    # Kill chain probabilities
    p_awacs_track: float
    p_launch_success: float
    p_beidou_update: float
    p_midcourse_guidance: float
    p_terminal_acquire: float
    p_penetrate_defense: float
    p_hit: float
    p_kill_given_hit: float

    # Total kill probability
    total_pk: float

    # Optimal parameters
    optimal_trajectory: List[GlideTrajectoryPoint] = field(default_factory=list)
    optimal_dive_angle: float = 45.0
    time_of_flight_s: float = 0.0

    # Salvo analysis
    salvo_size: int = 1
    salvo_pk: float = 0.0


# ==============================================================================
# SENSOR AND PLATFORM DEFINITIONS
# ==============================================================================

def create_kj500_awacs() -> AWACSPlatform:
    """KJ-500 AWACS with AESA radar"""
    return AWACSPlatform(
        name="KJ-500",
        radar_type="Type AESA (3-face array)",
        detection_range_km=470.0,  # Against fighter-sized
        track_accuracy_m=150.0,
        datalink_latency_s=2.0,
        availability=0.85,
        altitude_m=10000.0,
        endurance_hours=8.0
    )


def create_kj2000_awacs() -> AWACSPlatform:
    """KJ-2000 AWACS with phased array"""
    return AWACSPlatform(
        name="KJ-2000",
        radar_type="Type H/LJG-346 Phased Array",
        detection_range_km=400.0,
        track_accuracy_m=200.0,
        datalink_latency_s=2.5,
        availability=0.80,
        altitude_m=10000.0,
        endurance_hours=6.0
    )


def create_carrier_target(carrier_class: str) -> TargetCharacteristics:
    """Create carrier strike group target"""
    if carrier_class == "Ford":
        return TargetCharacteristics(
            target_type=TargetType.CARRIER_STRIKE_GROUP,
            name="USS Gerald R. Ford (CVN-78)",
            length_m=337.0,
            width_m=78.0,  # Flight deck
            velocity_kts=30.0,
            hardening_factor=1.0,
            defense_systems=["SM-3 Block IIA", "SM-6", "ESSM", "SeaRAM", "CIWS"],
            defense_pk_per_interceptor=0.15,  # Against HGV
            interceptor_salvo_size=4,
            reaction_time_s=30.0
        )
    else:  # Nimitz
        return TargetCharacteristics(
            target_type=TargetType.CARRIER_STRIKE_GROUP,
            name="Nimitz Class CVN",
            length_m=332.8,
            width_m=76.8,
            velocity_kts=30.0,
            hardening_factor=1.0,
            defense_systems=["SM-3 Block IA", "SM-6", "ESSM", "CIWS"],
            defense_pk_per_interceptor=0.12,
            interceptor_salvo_size=4,
            reaction_time_s=35.0
        )


def create_thaad_target() -> TargetCharacteristics:
    """THAAD battery as target"""
    return TargetCharacteristics(
        target_type=TargetType.THAAD_BATTERY,
        name="THAAD Battery",
        length_m=15.0,  # Launcher
        width_m=5.0,
        velocity_kts=0.0,
        hardening_factor=1.2,
        defense_systems=["THAAD interceptor", "Patriot PAC-3"],
        defense_pk_per_interceptor=0.25,  # Against HGV in glide
        interceptor_salvo_size=2,
        reaction_time_s=15.0
    )


def create_aegis_ashore_target() -> TargetCharacteristics:
    """Aegis Ashore installation"""
    return TargetCharacteristics(
        target_type=TargetType.AEGIS_ASHORE,
        name="Aegis Ashore (Romania/Poland type)",
        length_m=50.0,
        width_m=50.0,
        velocity_kts=0.0,
        hardening_factor=2.0,
        defense_systems=["SM-3 Block IIA", "SM-6"],
        defense_pk_per_interceptor=0.20,
        interceptor_salvo_size=4,
        reaction_time_s=20.0
    )


def create_airbase_target(hardened: bool) -> TargetCharacteristics:
    """Airbase target (hardened or soft)"""
    if hardened:
        return TargetCharacteristics(
            target_type=TargetType.AIRBASE_HARDENED,
            name="Hardened Aircraft Shelter",
            length_m=40.0,
            width_m=25.0,
            velocity_kts=0.0,
            hardening_factor=8.0,  # Reinforced concrete
            defense_systems=["Patriot PAC-3", "NASAMS"],
            defense_pk_per_interceptor=0.15,
            interceptor_salvo_size=2,
            reaction_time_s=20.0
        )
    else:
        return TargetCharacteristics(
            target_type=TargetType.AIRBASE_SOFT,
            name="Airbase Runway/Taxiway",
            length_m=3000.0,
            width_m=60.0,
            velocity_kts=0.0,
            hardening_factor=1.0,
            defense_systems=["Patriot PAC-3"],
            defense_pk_per_interceptor=0.15,
            interceptor_salvo_size=2,
            reaction_time_s=25.0
        )


# ==============================================================================
# TRAJECTORY OPTIMIZATION
# ==============================================================================

class HypersonicTrajectoryOptimizer:
    """Optimizes DF-17 glide trajectory for maximum Pk"""

    def __init__(self, df17: DF17Characteristics, beidou: BeidouConstellation):
        self.df17 = df17
        self.beidou = beidou

    def calculate_atmospheric_density(self, altitude_km: float) -> float:
        """Standard atmosphere density model"""
        if altitude_km < 11:
            T = 288.15 - 6.5 * altitude_km
            p = 101325 * (T / 288.15) ** 5.2559
        elif altitude_km < 25:
            T = 216.65
            p = 22632 * math.exp(-0.00015769 * (altitude_km - 11) * 1000)
        else:
            T = 216.65 + (altitude_km - 25) * 2.8
            p = 2488.6 * (T / 216.65) ** (-11.388)

        return p / (R_AIR * T)  # kg/m³

    def calculate_mach_number(self, velocity_ms: float, altitude_km: float) -> float:
        """Calculate Mach number at altitude"""
        if altitude_km < 11:
            T = 288.15 - 6.5 * altitude_km
        elif altitude_km < 25:
            T = 216.65
        else:
            T = 216.65 + (altitude_km - 25) * 2.8

        speed_of_sound = math.sqrt(GAMMA * R_AIR * T)
        return velocity_ms / speed_of_sound

    def optimize_glide_trajectory(
        self,
        range_km: float,
        target: TargetCharacteristics
    ) -> Tuple[List[GlideTrajectoryPoint], float]:
        """
        Calculate optimal glide trajectory for given range

        Returns trajectory points and optimal terminal dive angle
        """
        trajectory = []
        dt = 1.0  # Time step (seconds)

        # Initial conditions at boost burnout
        altitude = self.df17.boost_burnout_altitude_km
        velocity = self.df17.boost_burnout_velocity_ms
        downrange = 0.0
        crossrange = 0.0
        time = 0.0
        position_error = 0.0

        # Pull-up maneuver to establish glide
        phase = GlidePhase.PULL_UP
        pull_up_duration = 10.0  # seconds

        while time < pull_up_duration:
            mach = self.calculate_mach_number(velocity, altitude)
            trajectory.append(GlideTrajectoryPoint(
                time_s=time,
                altitude_km=altitude,
                downrange_km=downrange,
                crossrange_km=crossrange,
                velocity_ms=velocity,
                mach=mach,
                phase=phase,
                position_error_m=position_error
            ))

            # Simple pull-up model - altitude increase, velocity decrease
            altitude += velocity * 0.1 * dt / 1000  # Climb
            velocity -= 20 * dt  # Drag loss
            downrange += velocity * 0.99 * dt / 1000
            position_error += self.df17.ins_drift_m_per_s * dt
            time += dt

        # Glide phase - maximize range with periodic Beidou updates
        phase = GlidePhase.GLIDE
        glide_angle = math.atan(1 / self.df17.glide_l_d_ratio)  # Optimal glide
        beidou_update_interval = 30.0  # seconds
        last_beidou_update = time

        target_downrange = range_km - 50  # Start terminal 50km out

        while downrange < target_downrange and altitude > 25:
            mach = self.calculate_mach_number(velocity, altitude)

            # Beidou update reduces position error
            if time - last_beidou_update >= beidou_update_interval:
                beidou_accuracy = self.beidou.get_position_update_accuracy(velocity)
                position_error = min(position_error, beidou_accuracy * 3)
                last_beidou_update = time

            trajectory.append(GlideTrajectoryPoint(
                time_s=time,
                altitude_km=altitude,
                downrange_km=downrange,
                crossrange_km=crossrange,
                velocity_ms=velocity,
                mach=mach,
                phase=phase,
                position_error_m=position_error
            ))

            # Glide dynamics
            rho = self.calculate_atmospheric_density(altitude)
            drag_decel = 0.5 * rho * velocity**2 * 0.3 * 0.5 / self.df17.glide_mass_kg

            # Descend at optimal glide angle
            altitude -= velocity * math.sin(glide_angle) * dt / 1000
            velocity -= drag_decel * dt
            downrange += velocity * math.cos(glide_angle) * dt / 1000
            position_error += self.df17.ins_drift_m_per_s * dt
            time += dt

            # Prevent infinite loops
            if time > 600:
                break

        # Terminal dive phase
        phase = GlidePhase.TERMINAL_DIVE

        # Calculate optimal dive angle based on target type
        if target.velocity_kts > 0:  # Moving target
            optimal_dive_angle = 35.0  # Shallower for tracking
        else:  # Stationary
            optimal_dive_angle = 60.0  # Steeper for penetration

        dive_angle_rad = math.radians(optimal_dive_angle)

        while altitude > 0.1 and downrange < range_km:
            mach = self.calculate_mach_number(velocity, altitude)

            trajectory.append(GlideTrajectoryPoint(
                time_s=time,
                altitude_km=altitude,
                downrange_km=downrange,
                crossrange_km=crossrange,
                velocity_ms=velocity,
                mach=mach,
                phase=phase,
                position_error_m=position_error
            ))

            # Steep dive - velocity increases due to gravity
            rho = self.calculate_atmospheric_density(altitude)
            drag_decel = 0.5 * rho * velocity**2 * 0.3 * 0.3 / self.df17.glide_mass_kg
            gravity_accel = G0 * math.sin(dive_angle_rad)

            altitude -= velocity * math.sin(dive_angle_rad) * dt / 1000
            velocity += (gravity_accel - drag_decel) * dt
            downrange += velocity * math.cos(dive_angle_rad) * dt / 1000

            # Seeker acquisition reduces error
            if altitude < self.df17.seeker_acquisition_range_km:
                position_error *= 0.9  # Seeker correction

            position_error += self.df17.ins_drift_m_per_s * 0.5 * dt  # Reduced in terminal
            time += dt

            if time > 700:
                break

        # Final impact point
        trajectory.append(GlideTrajectoryPoint(
            time_s=time,
            altitude_km=0.0,
            downrange_km=range_km,
            crossrange_km=crossrange,
            velocity_ms=velocity,
            mach=self.calculate_mach_number(velocity, 0),
            phase=GlidePhase.IMPACT,
            position_error_m=position_error
        ))

        return trajectory, optimal_dive_angle


# ==============================================================================
# KILL CHAIN CALCULATOR
# ==============================================================================

class DF17KillChainCalculator:
    """Calculates integrated kill probability for DF-17 engagements"""

    def __init__(
        self,
        df17: DF17Characteristics,
        beidou: BeidouConstellation,
        awacs: AWACSPlatform,
        logger: Optional[CalculationLogger] = None
    ):
        self.df17 = df17
        self.beidou = beidou
        self.awacs = awacs
        self.trajectory_optimizer = HypersonicTrajectoryOptimizer(df17, beidou)
        self.logger = logger or CalculationLogger("DF17-Kill-Chain")

    def calculate_awacs_track_probability(
        self,
        target: TargetCharacteristics,
        range_km: float
    ) -> float:
        """Calculate probability of detecting and tracking target

        Uses AWACS for air/close targets, satellite constellation for
        distant maritime targets (carriers).
        """

        # Surface targets always detected by other means
        if target.velocity_kts == 0:
            return 0.98  # Pre-planned targets

        # Maritime targets (carriers) - use satellite constellation instead of AWACS
        if target.target_type == TargetType.CARRIER_STRIKE_GROUP:
            # Yaogan/Jilin satellite constellation detection
            # Similar to carrier_strike_kill_chain.py model
            p_satellite_detect = 0.85  # SAR/optical coverage
            p_oth_radar = 0.80  # OTH-B type radar backup
            p_drone_track = 0.70  # WZ-7/BZK-005 surveillance

            # Multi-sensor fusion
            p_detect_any = 1 - (1 - p_satellite_detect) * (1 - p_oth_radar) * (1 - p_drone_track)

            # Track accuracy degrades with target maneuver
            track_quality = 0.90  # Carrier limited maneuverability

            p_track = p_detect_any * track_quality

            self.logger.log_calculation(
                name="Maritime Target Track (Satellite+OTH+Drone)",
                formula="1 - (1-P_sat)(1-P_oth)(1-P_drone) × track_quality",
                inputs={
                    "p_satellite": p_satellite_detect,
                    "p_oth_radar": p_oth_radar,
                    "p_drone": p_drone_track,
                    "target_velocity_kts": target.velocity_kts
                },
                result=p_track,
                unit="probability"
            )
            return p_track

        # Air/land targets - use AWACS
        detection_range_ratio = range_km / self.awacs.detection_range_km

        if detection_range_ratio > 1.5:
            p_detect = 0.3  # Beyond reliable range
        elif detection_range_ratio > 1.0:
            p_detect = 0.7
        else:
            p_detect = 0.95

        # Track quality factor
        track_quality = min(1.0, self.awacs.detection_range_km / range_km)

        p_track = p_detect * track_quality * self.awacs.availability

        self.logger.log_calculation(
            name=f"AWACS Track ({self.awacs.name})",
            formula="P(detect) × track_quality × availability",
            inputs={
                "range_km": range_km,
                "detection_range_km": self.awacs.detection_range_km,
                "target_velocity_kts": target.velocity_kts
            },
            result=p_track,
            unit="probability"
        )

        return p_track

    def calculate_launch_success(self, range_km: float) -> float:
        """Calculate probability of successful launch"""

        if range_km < self.df17.min_range_km:
            p_launch = 0.0  # Below minimum range
        elif range_km > self.df17.booster_range_km:
            p_launch = 0.0  # Beyond maximum range
        else:
            # Optimal range band
            range_ratio = range_km / self.df17.booster_range_km
            if 0.4 < range_ratio < 0.8:
                p_launch = 0.98  # Optimal
            else:
                p_launch = 0.95  # Suboptimal but feasible

        self.logger.log_calculation(
            name="DF-17 Launch Success",
            formula="Range band optimization",
            inputs={
                "range_km": range_km,
                "min_range_km": self.df17.min_range_km,
                "max_range_km": self.df17.booster_range_km
            },
            result=p_launch,
            unit="probability"
        )

        return p_launch

    def calculate_beidou_guidance(
        self,
        trajectory: List[GlideTrajectoryPoint],
        target: TargetCharacteristics
    ) -> float:
        """Calculate Beidou midcourse guidance effectiveness"""

        # Count successful update opportunities
        glide_points = [p for p in trajectory if p.phase == GlidePhase.GLIDE]

        if not glide_points:
            return 0.9  # Minimal guidance needed for short range

        glide_duration = glide_points[-1].time_s - glide_points[0].time_s
        update_opportunities = glide_duration / 30.0  # Updates every 30s

        # Each update has availability probability
        p_all_updates = self.beidou.asia_pacific_availability ** update_opportunities

        # At least one update success
        p_at_least_one = 1 - (1 - self.beidou.asia_pacific_availability) ** max(1, update_opportunities)

        # Weighted combination
        p_guidance = 0.3 * p_all_updates + 0.7 * p_at_least_one

        # Moving targets need more updates
        if target.velocity_kts > 0:
            p_guidance *= 0.95  # Slightly harder

        self.logger.log_calculation(
            name="Beidou Midcourse Guidance",
            formula="P(updates) weighted by necessity",
            inputs={
                "glide_duration_s": glide_duration,
                "update_opportunities": update_opportunities,
                "beidou_availability": self.beidou.asia_pacific_availability
            },
            result=p_guidance,
            unit="probability"
        )

        return p_guidance

    def calculate_terminal_acquisition(
        self,
        trajectory: List[GlideTrajectoryPoint],
        target: TargetCharacteristics
    ) -> float:
        """Calculate terminal seeker acquisition probability"""

        # Get position error at terminal phase start
        terminal_points = [p for p in trajectory if p.phase == GlidePhase.TERMINAL_DIVE]
        if not terminal_points:
            terminal_error = 500.0  # Assume worst case
        else:
            terminal_error = terminal_points[0].position_error_m

        # Target size factor
        target_area = target.length_m * target.width_m
        seeker_footprint = math.pi * (self.df17.seeker_fov_deg / 2 *
                                       self.df17.seeker_acquisition_range_km * 1000 / 57.3) ** 2

        # Probability target is within seeker FOV
        error_sigma = terminal_error / 2  # 2-sigma error bound

        if target.velocity_kts > 0:
            # Moving target - need to predict position
            prediction_time = 30.0  # Seconds of prediction
            velocity_ms = target.velocity_kts * 0.5144
            position_uncertainty = velocity_ms * prediction_time * 0.1  # 10% velocity error
            error_sigma = math.sqrt(error_sigma**2 + position_uncertainty**2)

        # Seeker acquisition probability
        p_in_fov = math.exp(-(error_sigma / 1000)**2 / (2 * (seeker_footprint / target_area)))
        p_in_fov = min(0.98, max(0.4, p_in_fov))  # Bound reasonably

        # Seeker lock probability given in FOV
        p_lock = 0.92 if target.velocity_kts == 0 else 0.85

        p_acquire = p_in_fov * p_lock

        self.logger.log_calculation(
            name="Terminal Seeker Acquisition",
            formula="P(in_FOV) × P(lock)",
            inputs={
                "terminal_error_m": terminal_error,
                "target_area_m2": target_area,
                "target_moving": target.velocity_kts > 0
            },
            result=p_acquire,
            unit="probability"
        )

        return p_acquire

    def calculate_defense_penetration(
        self,
        target: TargetCharacteristics,
        trajectory: List[GlideTrajectoryPoint]
    ) -> float:
        """Calculate probability of penetrating target defenses"""

        # Get terminal velocity
        terminal_velocity = trajectory[-1].velocity_ms if trajectory else 1500
        terminal_mach = trajectory[-1].mach if trajectory else 5.0

        # HGV defense difficulty factor
        # Higher Mach = harder to intercept
        mach_factor = min(1.0, terminal_mach / 5.0)  # Baseline at Mach 5

        # Maneuvering factor
        maneuver_factor = min(1.0, self.df17.terminal_maneuver_g / 15.0)

        # Base intercept difficulty
        base_pk_intercept = target.defense_pk_per_interceptor

        # Adjust for HGV characteristics
        adjusted_pk = base_pk_intercept * (1 - 0.3 * mach_factor) * (1 - 0.2 * maneuver_factor)

        # Multiple interceptor engagement
        n_interceptors = target.interceptor_salvo_size

        # Defense leakage (probability of getting through)
        p_survive_single = 1 - adjusted_pk
        p_penetrate = p_survive_single ** n_interceptors

        # Add reaction time factor - may not have time to engage
        engagement_window = trajectory[-1].time_s if trajectory else 300
        if engagement_window < target.reaction_time_s:
            p_penetrate = 0.95  # Defense has no time

        self.logger.log_calculation(
            name="Defense Penetration",
            formula="(1 - Pk_intercept)^N_interceptors",
            inputs={
                "terminal_mach": terminal_mach,
                "maneuver_g": self.df17.terminal_maneuver_g,
                "n_interceptors": n_interceptors,
                "base_pk_intercept": base_pk_intercept,
                "adjusted_pk_intercept": adjusted_pk
            },
            result=p_penetrate,
            unit="probability"
        )

        return p_penetrate

    def calculate_hit_probability(
        self,
        target: TargetCharacteristics,
        trajectory: List[GlideTrajectoryPoint]
    ) -> float:
        """Calculate probability of hitting target given penetration"""

        # Final CEP
        final_cep = self.df17.cep_m

        # Target dimensions
        target_radius = math.sqrt(target.length_m * target.width_m / math.pi)

        # Hit probability using CEP formula
        # P(hit) = 1 - 0.5^((R/CEP)^2) for circular target
        p_hit = 1 - 0.5 ** ((target_radius / final_cep) ** 2)

        # Moving target adjustment
        if target.velocity_kts > 0:
            # Prediction error reduces hit probability
            p_hit *= 0.9

        self.logger.log_calculation(
            name="Hit Probability",
            formula="1 - 0.5^((R/CEP)^2)",
            inputs={
                "cep_m": final_cep,
                "target_radius_m": target_radius,
                "target_moving": target.velocity_kts > 0
            },
            result=p_hit,
            unit="probability"
        )

        return p_hit

    def calculate_kill_given_hit(self, target: TargetCharacteristics) -> float:
        """Calculate kill probability given a hit"""

        # Hardening factor reduces Pk|hit
        base_pk_hit = self.df17.pk_given_hit

        pk_hit = base_pk_hit / math.sqrt(target.hardening_factor)
        pk_hit = min(0.98, max(0.3, pk_hit))

        self.logger.log_calculation(
            name="Kill Given Hit",
            formula="base_pk / sqrt(hardening)",
            inputs={
                "base_pk_hit": base_pk_hit,
                "hardening_factor": target.hardening_factor
            },
            result=pk_hit,
            unit="probability"
        )

        return pk_hit

    def calculate_salvo_pk(
        self,
        single_pk: float,
        salvo_size: int,
        correlation: float = 0.3
    ) -> float:
        """Calculate salvo kill probability with correlation"""

        if salvo_size <= 1:
            return single_pk

        # Effective independent shots
        n_effective = 1 + (salvo_size - 1) * (1 - correlation)

        # Salvo Pk
        p_survive_all = (1 - single_pk) ** n_effective
        salvo_pk = 1 - p_survive_all

        return salvo_pk

    def calculate_engagement(
        self,
        target: TargetCharacteristics,
        range_km: float,
        salvo_size: int = 1
    ) -> EngagementResult:
        """Calculate complete kill chain for target engagement"""

        # Optimize trajectory
        trajectory, optimal_dive = self.trajectory_optimizer.optimize_glide_trajectory(
            range_km, target
        )

        # Calculate each kill chain element
        p_awacs = self.calculate_awacs_track_probability(target, range_km)
        p_launch = self.calculate_launch_success(range_km)
        p_beidou = self.calculate_beidou_guidance(trajectory, target)
        p_midcourse = p_launch * p_beidou  # Combined midcourse
        p_terminal = self.calculate_terminal_acquisition(trajectory, target)
        p_penetrate = self.calculate_defense_penetration(target, trajectory)
        p_hit = self.calculate_hit_probability(target, trajectory)
        p_kill_hit = self.calculate_kill_given_hit(target)

        # Total single-shot Pk
        total_pk = (p_awacs * p_launch * p_beidou * p_terminal *
                   p_penetrate * p_hit * p_kill_hit)

        # Salvo Pk
        salvo_pk = self.calculate_salvo_pk(total_pk, salvo_size)

        # Time of flight
        tof = trajectory[-1].time_s if trajectory else 0

        result = EngagementResult(
            target_name=target.name,
            target_type=target.target_type,
            range_km=range_km,
            p_awacs_track=p_awacs,
            p_launch_success=p_launch,
            p_beidou_update=p_beidou,
            p_midcourse_guidance=p_midcourse,
            p_terminal_acquire=p_terminal,
            p_penetrate_defense=p_penetrate,
            p_hit=p_hit,
            p_kill_given_hit=p_kill_hit,
            total_pk=total_pk,
            optimal_trajectory=trajectory,
            optimal_dive_angle=optimal_dive,
            time_of_flight_s=tof,
            salvo_size=salvo_size,
            salvo_pk=salvo_pk
        )

        self.logger.log_calculation(
            name=f"DF-17 vs {target.name} Total Pk",
            formula="P(track)×P(launch)×P(beidou)×P(terminal)×P(penetrate)×P(hit)×P(kill|hit)",
            inputs={
                "range_km": range_km,
                "salvo_size": salvo_size,
                "p_awacs": p_awacs,
                "p_launch": p_launch,
                "p_beidou": p_beidou,
                "p_terminal": p_terminal,
                "p_penetrate": p_penetrate,
                "p_hit": p_hit,
                "p_kill_hit": p_kill_hit
            },
            result=total_pk,
            unit="probability",
            confidence=45  # Moderate confidence
        )

        return result

    def find_optimal_salvo(
        self,
        target: TargetCharacteristics,
        range_km: float,
        target_pk: float = 0.9,
        max_salvo: int = 12
    ) -> Tuple[int, float]:
        """Find minimum salvo size to achieve target Pk"""

        for salvo_size in range(1, max_salvo + 1):
            result = self.calculate_engagement(target, range_km, salvo_size)
            if result.salvo_pk >= target_pk:
                return salvo_size, result.salvo_pk

        # Max salvo result
        result = self.calculate_engagement(target, range_km, max_salvo)
        return max_salvo, result.salvo_pk


# ==============================================================================
# INTEGRATED KILL CHAIN ANALYSIS
# ==============================================================================

class IntegratedDF17Analysis:
    """Complete DF-17 kill chain analysis with optimization"""

    def __init__(self):
        self.df17 = DF17Characteristics()
        self.beidou = BeidouConstellation()
        self.awacs_options = [create_kj500_awacs(), create_kj2000_awacs()]
        self.logger = CalculationLogger("DF17-Hypersonic-Kill-Chain")

        self.results = {}
        self.summary = {}

    def run_analysis(self):
        """Run complete analysis against all target types"""

        # Use KJ-500 as primary AWACS
        primary_awacs = self.awacs_options[0]
        calculator = DF17KillChainCalculator(
            self.df17, self.beidou, primary_awacs, self.logger
        )

        # Define targets and engagement parameters
        targets_config = [
            (create_carrier_target("Ford"), 1200.0),
            (create_carrier_target("Nimitz"), 1200.0),
            (create_thaad_target(), 800.0),
            (create_aegis_ashore_target(), 1000.0),
            (create_airbase_target(hardened=True), 900.0),
            (create_airbase_target(hardened=False), 900.0),
        ]

        all_results = []

        for target, base_range in targets_config:
            self.logger.section(f"DF-17 vs {target.name}")

            # Find optimal range
            best_result = None
            best_pk = 0

            for range_offset in [-200, -100, 0, 100, 200]:
                test_range = base_range + range_offset
                if test_range < self.df17.min_range_km or test_range > self.df17.booster_range_km:
                    continue

                result = calculator.calculate_engagement(target, test_range, salvo_size=1)
                if result.total_pk > best_pk:
                    best_pk = result.total_pk
                    best_result = result

            # Calculate optimal salvo for 90% Pk
            optimal_salvo, salvo_pk = calculator.find_optimal_salvo(
                target, base_range, target_pk=0.9
            )

            # Store with optimal salvo
            if best_result:
                best_result.salvo_size = optimal_salvo
                best_result.salvo_pk = salvo_pk
                all_results.append(best_result)

                self.results[target.name] = {
                    "target_type": target.target_type.value,
                    "range_km": best_result.range_km,
                    "single_pk": best_result.total_pk,
                    "optimal_salvo": optimal_salvo,
                    "salvo_pk": salvo_pk,
                    "time_of_flight_s": best_result.time_of_flight_s,
                    "optimal_dive_angle": best_result.optimal_dive_angle,
                    "kill_chain": {
                        "p_awacs_track": best_result.p_awacs_track,
                        "p_launch_success": best_result.p_launch_success,
                        "p_beidou_guidance": best_result.p_beidou_update,
                        "p_terminal_acquire": best_result.p_terminal_acquire,
                        "p_defense_penetration": best_result.p_penetrate_defense,
                        "p_hit": best_result.p_hit,
                        "p_kill_given_hit": best_result.p_kill_given_hit
                    }
                }

        # Generate summary
        self._generate_summary(all_results)

        return all_results

    def _generate_summary(self, results: List[EngagementResult]):
        """Generate analysis summary"""

        if not results:
            return

        avg_pk = sum(r.total_pk for r in results) / len(results)
        max_pk_result = max(results, key=lambda r: r.total_pk)
        min_pk_result = min(results, key=lambda r: r.total_pk)

        # Key findings
        findings = [
            f"DF-17 achieves average single-shot Pk of {avg_pk:.1%} across all targets",
            f"Highest Pk: {max_pk_result.total_pk:.1%} against {max_pk_result.target_name}",
            f"Lowest Pk: {min_pk_result.total_pk:.1%} against {min_pk_result.target_name}",
            "Moving targets (carriers) require larger salvos due to prediction uncertainty",
            "Hardened targets require multiple hits for assured destruction",
            f"Beidou constellation provides reliable midcourse updates ({self.beidou.asia_pacific_availability:.1%} availability)",
            "Terminal Mach 5+ severely degrades interceptor effectiveness",
            "Cross-range maneuver capability allows attack from unexpected angles"
        ]

        # Recommendations
        recommendations = [
            "Use 4-6 missile salvos against carrier strike groups",
            "Time attacks to minimize CSG reaction time",
            "Coordinate with EW assets to degrade Aegis radar",
            "Pre-position reconnaissance for real-time target updates",
            "Maintain Beidou signal integrity during conflict"
        ]

        # Limitations
        limitations = [
            "Terminal seeker performance against moving targets uncertain",
            "Defense capabilities may exceed open-source estimates",
            "Electronic warfare effects not fully modeled",
            "Actual CEP classified - estimates from open sources",
            "Multi-layer defense coordination not fully modeled"
        ]

        self.summary = {
            "targets_analyzed": len(results),
            "average_single_pk": avg_pk,
            "max_pk": max_pk_result.total_pk,
            "max_pk_target": max_pk_result.target_name,
            "min_pk": min_pk_result.total_pk,
            "min_pk_target": min_pk_result.target_name,
            "key_findings": findings,
            "recommendations": recommendations,
            "limitations": limitations,
            "awacs_platform": self.awacs_options[0].name,
            "beidou_availability": self.beidou.asia_pacific_availability
        }

    def export_results(self, prefix: str = "df17_kill_chain"):
        """Export results to files"""

        # Finalize logging session
        self.logger.finalize()

        output = {
            "generated": datetime.now().isoformat(),
            "system": "DF-17 Hypersonic Glide Vehicle",
            "guidance": "Beidou-3 + Terminal Seeker",
            "cueing": "KJ-500/KJ-2000 AWACS",
            "targets": self.results,
            "summary": self.summary
        }

        # JSON output
        json_path = f"{prefix}_results.json"
        with open(json_path, "w") as f:
            json.dump(output, f, indent=2)

        # Markdown report
        md_path = f"{prefix}_report.md"
        self._write_markdown_report(md_path)

        # Log file with calculation details
        log_path = f"{prefix}_log.txt"
        with open(log_path, "w") as f:
            f.write(self.logger.generate_markdown_report())

        return json_path, md_path

    def _write_markdown_report(self, path: str):
        """Write detailed markdown report"""

        report = f"""# DF-17 Hypersonic Glide Vehicle Kill Chain Analysis

**Generated:** {datetime.now().isoformat()}
**System:** DF-17 with Beidou-3 Guidance
**AWACS Cueing:** {self.awacs_options[0].name}

## Executive Summary

The DF-17 hypersonic glide vehicle, integrated with Beidou-3 midcourse guidance and
AWACS target cueing, presents a significant capability against both moving and stationary
high-value targets. Analysis indicates:

- **Average Single-Shot Pk:** {self.summary.get('average_single_pk', 0):.1%}
- **Targets Analyzed:** {self.summary.get('targets_analyzed', 0)}
- **Primary Advantage:** Terminal velocity Mach 5+ severely limits defensive options

## System Characteristics

### DF-17 Hypersonic Glide Vehicle

| Parameter | Value |
|-----------|-------|
| Maximum Range | {self.df17.booster_range_km:.0f} km |
| Minimum Range | {self.df17.min_range_km:.0f} km |
| Boost Burnout Altitude | {self.df17.boost_burnout_altitude_km:.0f} km |
| Terminal Velocity | Mach {self.df17.terminal_velocity_mach:.1f}+ |
| Terminal Maneuver | {self.df17.terminal_maneuver_g:.0f} G |
| Cross-Range Capability | {self.df17.cross_range_capability_km:.0f} km |
| CEP (estimated) | {self.df17.cep_m:.0f} m |

### Beidou-3 Guidance

| Parameter | Value |
|-----------|-------|
| Position Accuracy | {self.beidou.position_accuracy_m:.1f} m |
| Velocity Accuracy | {self.beidou.velocity_accuracy_ms:.2f} m/s |
| Asia-Pacific Availability | {self.beidou.asia_pacific_availability:.1%} |
| Update Rate | {self.beidou.position_update_rate_hz:.0f} Hz |

### AWACS Platforms

| Platform | Detection Range | Track Accuracy |
|----------|-----------------|----------------|
| KJ-500 | {self.awacs_options[0].detection_range_km:.0f} km | {self.awacs_options[0].track_accuracy_m:.0f} m |
| KJ-2000 | {self.awacs_options[1].detection_range_km:.0f} km | {self.awacs_options[1].track_accuracy_m:.0f} m |

## Target Engagement Results

| Target | Type | Range | Single Pk | Salvo (90% Pk) | Salvo Pk |
|--------|------|-------|-----------|----------------|----------|
"""

        for name, data in self.results.items():
            report += f"| {name} | {data['target_type']} | {data['range_km']:.0f} km | "
            report += f"{data['single_pk']:.1%} | {data['optimal_salvo']} | {data['salvo_pk']:.1%} |\n"

        report += """
## Kill Chain Breakdown

The DF-17 kill chain follows the sequence:

```
AWACS Detection → Launch → Beidou Midcourse → Terminal Dive → Seeker Lock → Impact
```

### Kill Chain Probabilities by Target

"""

        for name, data in self.results.items():
            kc = data['kill_chain']
            report += f"""#### {name}

| Phase | Probability |
|-------|-------------|
| AWACS Track | {kc['p_awacs_track']:.1%} |
| Launch Success | {kc['p_launch_success']:.1%} |
| Beidou Guidance | {kc['p_beidou_guidance']:.1%} |
| Terminal Acquire | {kc['p_terminal_acquire']:.1%} |
| Defense Penetration | {kc['p_defense_penetration']:.1%} |
| Hit | {kc['p_hit']:.1%} |
| Kill Given Hit | {kc['p_kill_given_hit']:.1%} |
| **Total Single Pk** | **{data['single_pk']:.1%}** |

"""

        report += """## Key Findings

"""
        for finding in self.summary.get('key_findings', []):
            report += f"- {finding}\n"

        report += """
## Recommendations

"""
        for rec in self.summary.get('recommendations', []):
            report += f"- {rec}\n"

        report += """
## Limitations and Uncertainties

"""
        for lim in self.summary.get('limitations', []):
            report += f"- {lim}\n"

        report += """
## Conclusion

The DF-17 HGV with integrated Beidou guidance and AWACS cueing provides a potent
precision strike capability. Key advantages include:

1. **Speed**: Terminal Mach 5+ reduces defensive engagement windows
2. **Maneuverability**: 20G terminal maneuvers complicate intercept solutions
3. **Guidance**: Beidou midcourse + seeker terminal provides high accuracy
4. **Range**: 500-1800 km range covers first island chain and beyond

Primary limitations remain terminal seeker performance against moving targets and
defense penetration against multi-layer systems. Salvo tactics recommended for
high-value targets.

---
*Analysis generated by DF-17 Kill Chain Calculator*
"""

        with open(path, "w") as f:
            f.write(report)


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Run DF-17 hypersonic kill chain analysis"""

    print("=" * 80)
    print("DF-17 HYPERSONIC GLIDE VEHICLE KILL CHAIN ANALYSIS")
    print("Integrated AWACS + Beidou + Terminal Guidance")
    print("=" * 80)
    print()

    analysis = IntegratedDF17Analysis()
    results = analysis.run_analysis()

    # Display results
    print("\n" + "=" * 80)
    print("ENGAGEMENT RESULTS")
    print("=" * 80)

    for result in results:
        print(f"\n{result.target_name}")
        print("-" * 40)
        print(f"  Range: {result.range_km:.0f} km")
        print(f"  Single-Shot Pk: {result.total_pk:.1%}")
        print(f"  Optimal Salvo: {result.salvo_size} missiles")
        print(f"  Salvo Pk: {result.salvo_pk:.1%}")
        print(f"  Time of Flight: {result.time_of_flight_s:.0f} s")
        print(f"  Terminal Dive: {result.optimal_dive_angle:.0f}°")
        print(f"  Kill Chain:")
        print(f"    P(AWACS): {result.p_awacs_track:.1%}")
        print(f"    P(Launch): {result.p_launch_success:.1%}")
        print(f"    P(Beidou): {result.p_beidou_update:.1%}")
        print(f"    P(Terminal): {result.p_terminal_acquire:.1%}")
        print(f"    P(Penetrate): {result.p_penetrate_defense:.1%}")
        print(f"    P(Hit): {result.p_hit:.1%}")
        print(f"    P(Kill|Hit): {result.p_kill_given_hit:.1%}")

    # Export results
    json_path, md_path = analysis.export_results()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTargets Analyzed: {analysis.summary['targets_analyzed']}")
    print(f"Average Single-Shot Pk: {analysis.summary['average_single_pk']:.1%}")
    print(f"Highest Pk: {analysis.summary['max_pk']:.1%} ({analysis.summary['max_pk_target']})")
    print(f"Lowest Pk: {analysis.summary['min_pk']:.1%} ({analysis.summary['min_pk_target']})")

    print("\nKey Findings:")
    for finding in analysis.summary['key_findings'][:5]:
        print(f"  • {finding}")

    print(f"\nResults exported to:")
    print(f"  • {json_path}")
    print(f"  • {md_path}")

    return analysis


if __name__ == "__main__":
    main()
