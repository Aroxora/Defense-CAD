"""
Air Defense Target Models for Ground-to-Ground Precision Strike Simulations
===========================================================================

CLASSIFICATION: UNCLASSIFIED // PUBLIC RELEASE

This module defines air defense system targets (SAM sites, radar installations)
for precision ballistic missile engagement simulations.

All parameters are derived from publicly available sources with documented
confidence levels following the methodology in docs/METHODOLOGY.md.

Air Defense Systems Modeled:
- MIM-104 Patriot (PAC-2/PAC-3)
- THAAD (Terminal High Altitude Area Defense)
- S-400 Triumf
- S-300PMU2
- NASAMS (National Advanced Surface-to-Air Missile System)

Author: Claude (Anthropic)
Date: 2025-12-29
"""

from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class AirDefenseSystemType(Enum):
    """Enumeration of modeled air defense system types."""
    PATRIOT_PAC2 = "patriot_pac2"
    PATRIOT_PAC3 = "patriot_pac3"
    THAAD = "thaad"
    S400 = "s400"
    S300PMU2 = "s300pmu2"
    NASAMS = "nasams"


@dataclass
class RadarComponent:
    """
    Radar component of an air defense system.

    Attributes:
        radar_type: Type of radar (search, track, fire control)
        frequency_ghz: Operating frequency in GHz
        peak_power_kw: Peak transmit power in kilowatts
        antenna_diameter_m: Antenna diameter in meters
        rotation_period_s: Rotation period for search radars (None if stationary)
        elevation_coverage_deg: Elevation coverage (min, max) in degrees
        azimuth_coverage_deg: Azimuth coverage in degrees (360 for full coverage)
        detection_range_km: Detection range vs 1 m² RCS target
        rcs_m2: Radar cross-section of the radar itself
        position_offset_m: Position offset from battery center [x, y, z]
    """
    radar_type: str
    frequency_ghz: float
    peak_power_kw: float
    antenna_diameter_m: float
    rotation_period_s: float | None
    elevation_coverage_deg: tuple[float, float]
    azimuth_coverage_deg: float
    detection_range_km: float
    rcs_m2: float
    position_offset_m: np.ndarray = field(default_factory=lambda: np.array([0., 0., 0.]))


@dataclass
class LauncherComponent:
    """
    Missile launcher component of an air defense system.

    Attributes:
        launcher_id: Unique identifier
        missiles_ready: Number of missiles in ready-to-fire state
        reload_time_s: Time to reload missiles (seconds)
        max_elevation_deg: Maximum elevation angle
        slew_rate_deg_s: Launcher slew rate in degrees per second
        rcs_m2: Radar cross-section of the launcher
        position_offset_m: Position offset from battery center [x, y, z]
    """
    launcher_id: str
    missiles_ready: int
    reload_time_s: float
    max_elevation_deg: float
    slew_rate_deg_s: float
    rcs_m2: float
    position_offset_m: np.ndarray = field(default_factory=lambda: np.array([0., 0., 0.]))


@dataclass
class AirDefenseTarget:
    """
    Complete air defense battery/system as a targetable entity.

    This represents a complete air defense site including radars, launchers,
    command post, and support vehicles. Designed to be engaged by precision
    ballistic missiles.

    Attributes:
        target_id: Unique identifier
        system_type: Type of air defense system
        position: Center position [lat, lon, alt] or [x, y, z] in meters
        heading_deg: Battery orientation (degrees, 0=North)

        # Components
        radars: List of radar components
        launchers: List of launcher components
        command_post_rcs_m2: RCS of command post vehicle

        # Vulnerability parameters
        component_spacing_m: Typical spacing between components
        hardening_level: 0.0 (soft) to 1.0 (hardened)
        camouflage_effectiveness: 0.0 (exposed) to 1.0 (concealed)

        # Operational status
        is_active: Whether system is currently active
        alert_level: 0.0 (peacetime) to 1.0 (wartime alert)
        reaction_time_s: Time from detection to engagement

        # Defensive capabilities
        has_ciws: Whether site has close-in weapon system
        has_ew_suite: Whether site has EW jammers
        has_smoke_obscurants: Whether site can deploy smoke
    """
    target_id: str
    system_type: AirDefenseSystemType
    position: np.ndarray
    heading_deg: float

    radars: list[RadarComponent] = field(default_factory=list)
    launchers: list[LauncherComponent] = field(default_factory=list)
    command_post_rcs_m2: float = 50.0

    component_spacing_m: float = 100.0
    hardening_level: float = 0.0
    camouflage_effectiveness: float = 0.0

    is_active: bool = True
    alert_level: float = 0.5
    reaction_time_s: float = 30.0

    has_ciws: bool = False
    has_ew_suite: bool = True
    has_smoke_obscurants: bool = False

    def get_total_rcs_m2(self) -> float:
        """
        Calculate total RCS of the battery (all components).

        Returns:
            Total RCS in m²
        """
        total_rcs = self.command_post_rcs_m2
        for radar in self.radars:
            total_rcs += radar.rcs_m2
        for launcher in self.launchers:
            total_rcs += launcher.rcs_m2
        return total_rcs

    def get_component_positions(self) -> list[tuple[str, np.ndarray, float]]:
        """
        Get positions and RCS of all components for damage assessment.

        Returns:
            List of (component_name, position, rcs_m2) tuples
        """
        components = []

        # Command post at center
        components.append(("command_post", self.position.copy(), self.command_post_rcs_m2))

        # Radars
        for i, radar in enumerate(self.radars):
            pos = self.position + radar.position_offset_m
            components.append((f"radar_{i}_{radar.radar_type}", pos, radar.rcs_m2))

        # Launchers
        for i, launcher in enumerate(self.launchers):
            pos = self.position + launcher.position_offset_m
            components.append((f"launcher_{i}", pos, launcher.rcs_m2))

        return components

    def calculate_kill_probability(self, impact_position: np.ndarray,
                                   warhead_yield_kg: float,
                                   cep_m: float) -> tuple[float, dict]:
        """
        Calculate probability of functional kill given impact position and warhead.

        A functional kill means the battery can no longer perform its mission,
        which typically requires destroying the primary radar or multiple launchers.

        Args:
            impact_position: Impact point [x, y, z] in meters
            warhead_yield_kg: Warhead explosive yield in kg TNT equivalent
            cep_m: Circular error probable in meters

        Returns:
            Tuple of (overall_kill_probability, component_damage_dict)
        """
        # Lethal radius estimation (simplified)
        # Rule of thumb: lethal radius ≈ 15 * (yield_kg)^(1/3) meters for soft targets
        base_lethal_radius = 15.0 * (warhead_yield_kg ** (1/3))

        # Adjust for hardening
        lethal_radius = base_lethal_radius * (1.0 - 0.5 * self.hardening_level)

        component_damage = {}
        critical_components_destroyed = 0
        _total_critical_components = len(self.radars) + 1  # Radars + command post

        # Assess damage to each component
        components = self.get_component_positions()
        for comp_name, comp_pos, _comp_rcs in components:
            distance = np.linalg.norm(impact_position - comp_pos)

            # Probability of destruction based on distance and CEP
            # Using exponential decay model
            if distance < lethal_radius:
                base_pk = np.exp(-distance / (lethal_radius / 3.0))
            else:
                base_pk = 0.1 * np.exp(-(distance - lethal_radius) / lethal_radius)

            # CEP affects precision
            cep_factor = 1.0 / (1.0 + cep_m / lethal_radius)
            pk = base_pk * cep_factor

            component_damage[comp_name] = {
                'distance_m': distance,
                'kill_probability': pk
            }

            # Track critical component kills
            if ('radar' in comp_name or 'command_post' in comp_name) and pk > 0.5:
                critical_components_destroyed += 1

        # Functional kill probability
        # Need to destroy primary radar OR command post + launcher
        primary_radar_pk = max([component_damage[k]['kill_probability']
                               for k in component_damage if 'radar' in k],
                              default=0.0)
        command_post_pk = component_damage.get('command_post', {}).get('kill_probability', 0.0)

        # Functional kill = primary radar destroyed OR (command post AND any launcher)
        functional_kill_prob = primary_radar_pk + (1 - primary_radar_pk) * command_post_pk * 0.5

        # Adjust for camouflage and concealment
        functional_kill_prob *= (1.0 - 0.3 * self.camouflage_effectiveness)

        return functional_kill_prob, component_damage


# ============================================================================
# FACTORY FUNCTIONS FOR STANDARD AIR DEFENSE CONFIGURATIONS
# ============================================================================

def create_patriot_pac3_battery(position: np.ndarray,
                                battery_id: str = "PAT-001",
                                heading_deg: float = 0.0) -> AirDefenseTarget:
    """
    Create a standard Patriot PAC-3 battery configuration.

    Configuration based on publicly available doctrine:
    - 1x AN/MPQ-65 radar
    - 4-8x M901 launchers (16 missiles each for PAC-3)
    - 1x ECS (Engagement Control Station)

    Parameters derived from open sources with ~60% confidence.

    Args:
        position: Battery center position [x, y, z] in meters
        battery_id: Unique battery identifier
        heading_deg: Battery orientation (0 = North)

    Returns:
        AirDefenseTarget representing Patriot PAC-3 battery
    """
    # AN/MPQ-65 radar (phased array)
    mpq65_radar = RadarComponent(
        radar_type="multifunction",
        frequency_ghz=5.6,  # C-band (5.2-5.9 GHz range)
        peak_power_kw=200.0,  # Estimated from phased array
        antenna_diameter_m=3.7,  # Square array ~3.7m per side
        rotation_period_s=None,  # Electronic scanning, no rotation
        elevation_coverage_deg=(0.0, 80.0),
        azimuth_coverage_deg=120.0,  # Per sector, battery has 360° coverage
        detection_range_km=170.0,  # Vs 1 m² target
        rcs_m2=150.0,  # Large phased array radar
        position_offset_m=np.array([0., 0., 3.0])  # Radar on elevated platform
    )

    # Create launcher array (6 launchers in standard configuration)
    launchers = []
    launcher_positions = [
        np.array([80., 0., 0.]),    # Front
        np.array([40., 60., 0.]),   # Front-right
        np.array([40., -60., 0.]),  # Front-left
        np.array([-40., 60., 0.]),  # Rear-right
        np.array([-40., -60., 0.]), # Rear-left
        np.array([-80., 0., 0.]),   # Rear
    ]

    for i, offset in enumerate(launcher_positions):
        launcher = LauncherComponent(
            launcher_id=f"M901-{i+1}",
            missiles_ready=16,  # PAC-3 MSE: 16 per launcher
            reload_time_s=600.0,  # ~10 minutes estimated
            max_elevation_deg=85.0,
            slew_rate_deg_s=45.0,
            rcs_m2=30.0,  # M901 launcher vehicle
            position_offset_m=offset
        )
        launchers.append(launcher)

    battery = AirDefenseTarget(
        target_id=battery_id,
        system_type=AirDefenseSystemType.PATRIOT_PAC3,
        position=position.copy(),
        heading_deg=heading_deg,
        radars=[mpq65_radar],
        launchers=launchers,
        command_post_rcs_m2=50.0,  # ECS vehicle
        component_spacing_m=80.0,
        hardening_level=0.2,  # Some protection, not fully hardened
        camouflage_effectiveness=0.3,  # Moderate concealment
        is_active=True,
        alert_level=0.7,
        reaction_time_s=25.0,  # PAC-3 has fast reaction time
        has_ciws=False,
        has_ew_suite=True,
        has_smoke_obscurants=True
    )

    return battery


def create_thaad_battery(position: np.ndarray,
                        battery_id: str = "THAAD-001",
                        heading_deg: float = 0.0) -> AirDefenseTarget:
    """
    Create a standard THAAD battery configuration.

    Configuration:
    - 1x AN/TPY-2 X-band radar
    - 6-9x M1075 launchers (8 missiles each)
    - 1x TFCC (THAAD Fire Control and Communication)

    Args:
        position: Battery center position [x, y, z]
        battery_id: Unique battery identifier
        heading_deg: Battery orientation

    Returns:
        AirDefenseTarget representing THAAD battery
    """
    # AN/TPY-2 radar (X-band)
    tpy2_radar = RadarComponent(
        radar_type="fire_control",
        frequency_ghz=9.6,  # X-band
        peak_power_kw=80.0,  # Estimated
        antenna_diameter_m=9.2,  # Large X-band array
        rotation_period_s=None,  # Phased array
        elevation_coverage_deg=(0.0, 85.0),
        azimuth_coverage_deg=120.0,
        detection_range_km=1000.0,  # Exceptional range for ballistic missiles
        rcs_m2=200.0,  # Very large radar array
        position_offset_m=np.array([0., 0., 5.0])
    )

    # Create 6 launchers
    launchers = []
    for i in range(6):
        angle_rad = (i * 60.0) * np.pi / 180.0
        offset = np.array([100. * np.cos(angle_rad), 100. * np.sin(angle_rad), 0.])

        launcher = LauncherComponent(
            launcher_id=f"M1075-{i+1}",
            missiles_ready=8,
            reload_time_s=900.0,
            max_elevation_deg=90.0,
            slew_rate_deg_s=30.0,
            rcs_m2=40.0,
            position_offset_m=offset
        )
        launchers.append(launcher)

    battery = AirDefenseTarget(
        target_id=battery_id,
        system_type=AirDefenseSystemType.THAAD,
        position=position.copy(),
        heading_deg=heading_deg,
        radars=[tpy2_radar],
        launchers=launchers,
        command_post_rcs_m2=50.0,
        component_spacing_m=100.0,
        hardening_level=0.3,
        camouflage_effectiveness=0.4,
        is_active=True,
        alert_level=0.7,
        reaction_time_s=30.0,
        has_ciws=False,
        has_ew_suite=True,
        has_smoke_obscurants=False
    )

    return battery


def create_s400_battery(position: np.ndarray,
                       battery_id: str = "S400-001",
                       heading_deg: float = 0.0) -> AirDefenseTarget:
    """
    Create a standard S-400 Triumf battery configuration.

    Configuration:
    - 1x 91N6E (Big Bird) search radar
    - 1x 92N6E (Grave Stone) fire control radar
    - 6-8x 5P85 launchers (4 missiles each)

    Args:
        position: Battery center position [x, y, z]
        battery_id: Unique battery identifier
        heading_deg: Battery orientation

    Returns:
        AirDefenseTarget representing S-400 battery
    """
    # 91N6E search radar
    search_radar = RadarComponent(
        radar_type="search",
        frequency_ghz=1.0,  # L-band
        peak_power_kw=150.0,
        antenna_diameter_m=7.0,
        rotation_period_s=12.0,  # Rotating radar
        elevation_coverage_deg=(0.0, 65.0),
        azimuth_coverage_deg=360.0,
        detection_range_km=600.0,
        rcs_m2=180.0,
        position_offset_m=np.array([-50., 0., 4.0])
    )

    # 92N6E fire control radar
    fc_radar = RadarComponent(
        radar_type="fire_control",
        frequency_ghz=10.0,  # X-band
        peak_power_kw=100.0,
        antenna_diameter_m=3.0,
        rotation_period_s=None,
        elevation_coverage_deg=(0.0, 85.0),
        azimuth_coverage_deg=120.0,
        detection_range_km=400.0,
        rcs_m2=100.0,
        position_offset_m=np.array([50., 0., 3.0])
    )

    # Create 8 launchers (mix of 48N6, 40N6 missiles)
    launchers = []
    for i in range(8):
        angle_rad = (i * 45.0) * np.pi / 180.0
        offset = np.array([120. * np.cos(angle_rad), 120. * np.sin(angle_rad), 0.])

        launcher = LauncherComponent(
            launcher_id=f"5P85-{i+1}",
            missiles_ready=4,  # 4 missiles per TEL
            reload_time_s=300.0,
            max_elevation_deg=85.0,
            slew_rate_deg_s=50.0,
            rcs_m2=35.0,
            position_offset_m=offset
        )
        launchers.append(launcher)

    battery = AirDefenseTarget(
        target_id=battery_id,
        system_type=AirDefenseSystemType.S400,
        position=position.copy(),
        heading_deg=heading_deg,
        radars=[search_radar, fc_radar],
        launchers=launchers,
        command_post_rcs_m2=45.0,
        component_spacing_m=120.0,
        hardening_level=0.15,
        camouflage_effectiveness=0.4,
        is_active=True,
        alert_level=0.8,
        reaction_time_s=20.0,
        has_ciws=False,
        has_ew_suite=True,
        has_smoke_obscurants=True
    )

    return battery


def create_s300pmu2_battery(position: np.ndarray,
                           battery_id: str = "S300-001",
                           heading_deg: float = 0.0) -> AirDefenseTarget:
    """
    Create a standard S-300PMU-2 battery configuration.

    Configuration:
    - 1x 64N6E (Big Bird) search radar
    - 1x 30N6E (Flap Lid) fire control radar
    - 6x 5P85 launchers (4 missiles each)

    Args:
        position: Battery center position [x, y, z]
        battery_id: Unique battery identifier
        heading_deg: Battery orientation

    Returns:
        AirDefenseTarget representing S-300PMU-2 battery
    """
    search_radar = RadarComponent(
        radar_type="search",
        frequency_ghz=1.2,  # L-band
        peak_power_kw=120.0,
        antenna_diameter_m=6.0,
        rotation_period_s=12.0,
        elevation_coverage_deg=(0.0, 60.0),
        azimuth_coverage_deg=360.0,
        detection_range_km=300.0,
        rcs_m2=150.0,
        position_offset_m=np.array([-40., 0., 3.5])
    )

    fc_radar = RadarComponent(
        radar_type="fire_control",
        frequency_ghz=10.0,  # X-band
        peak_power_kw=80.0,
        antenna_diameter_m=2.5,
        rotation_period_s=None,
        elevation_coverage_deg=(0.0, 82.0),
        azimuth_coverage_deg=120.0,
        detection_range_km=200.0,
        rcs_m2=90.0,
        position_offset_m=np.array([40., 0., 2.5])
    )

    launchers = []
    for i in range(6):
        angle_rad = (i * 60.0) * np.pi / 180.0
        offset = np.array([100. * np.cos(angle_rad), 100. * np.sin(angle_rad), 0.])

        launcher = LauncherComponent(
            launcher_id=f"5P85-{i+1}",
            missiles_ready=4,
            reload_time_s=360.0,
            max_elevation_deg=82.0,
            slew_rate_deg_s=45.0,
            rcs_m2=32.0,
            position_offset_m=offset
        )
        launchers.append(launcher)

    battery = AirDefenseTarget(
        target_id=battery_id,
        system_type=AirDefenseSystemType.S300PMU2,
        position=position.copy(),
        heading_deg=heading_deg,
        radars=[search_radar, fc_radar],
        launchers=launchers,
        command_post_rcs_m2=40.0,
        component_spacing_m=100.0,
        hardening_level=0.1,
        camouflage_effectiveness=0.35,
        is_active=True,
        alert_level=0.7,
        reaction_time_s=25.0,
        has_ciws=False,
        has_ew_suite=True,
        has_smoke_obscurants=True
    )

    return battery


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_optimal_impact_point(battery: AirDefenseTarget,
                                   attack_azimuth_deg: float = 0.0) -> np.ndarray:
    """
    Calculate optimal impact point to maximize battery kill probability.

    Strategy: Target the primary radar or command post, as these are
    critical components for battery functionality.

    Args:
        battery: Target battery
        attack_azimuth_deg: Direction of attack (degrees, 0=North)

    Returns:
        Optimal impact point [x, y, z]
    """
    # Prioritize primary radar (typically first radar in list)
    if len(battery.radars) > 0:
        return battery.position + battery.radars[0].position_offset_m
    else:
        # Fall back to command post
        return battery.position.copy()


def estimate_required_missiles(battery: AirDefenseTarget,
                               missile_cep_m: float,
                               warhead_yield_kg: float,
                               desired_pk: float = 0.9) -> int:
    """
    Estimate number of missiles required to achieve desired kill probability.

    Uses Poisson statistics for salvo sizing.

    Args:
        battery: Target battery
        missile_cep_m: Missile circular error probable
        warhead_yield_kg: Warhead yield in kg TNT
        desired_pk: Desired overall kill probability (0.0-1.0)

    Returns:
        Number of missiles required
    """
    # Calculate single-shot Pk
    optimal_impact = calculate_optimal_impact_point(battery)
    single_shot_pk, _ = battery.calculate_kill_probability(
        optimal_impact, warhead_yield_kg, missile_cep_m
    )

    if single_shot_pk >= desired_pk:
        return 1

    # Salvo calculation: 1 - (1 - Pk_single)^n >= desired_pk
    # Solve for n: n >= log(1 - desired_pk) / log(1 - Pk_single)
    n = int(np.ceil(np.log(1 - desired_pk) / np.log(1 - single_shot_pk)))

    return max(1, min(n, 10))  # Cap at 10 missiles


if __name__ == "__main__":
    # Example usage and validation
    print("Air Defense Target Model - Example Usage")
    print("=" * 60)

    # Create a Patriot battery
    patriot = create_patriot_pac3_battery(
        position=np.array([0., 0., 0.]),
        battery_id="PAT-001"
    )

    print(f"\nPatriot PAC-3 Battery: {patriot.target_id}")
    print(f"  Position: {patriot.position}")
    print(f"  Total RCS: {patriot.get_total_rcs_m2():.1f} m²")
    print(f"  Radars: {len(patriot.radars)}")
    print(f"  Launchers: {len(patriot.launchers)}")
    print(f"  Total missiles: {sum(lnch.missiles_ready for lnch in patriot.launchers)}")

    # Simulate a precision strike
    impact_point = calculate_optimal_impact_point(patriot)
    pk, damage = patriot.calculate_kill_probability(
        impact_position=impact_point,
        warhead_yield_kg=500.0,  # 500 kg warhead
        cep_m=5.0  # 5-meter CEP
    )

    print("\n Precision Strike Analysis:")
    print(f"  Optimal impact point: {impact_point}")
    print("  Warhead: 500 kg, CEP: 5 m")
    print(f"  Functional Kill Probability: {pk:.1%}")
    print("\n  Component Damage Assessment:")
    for comp, dmg in damage.items():
        print(f"    {comp:25s}: {dmg['kill_probability']:5.1%} (distance: {dmg['distance_m']:5.1f} m)")

    # Missile requirement estimation
    n_missiles = estimate_required_missiles(
        battery=patriot,
        missile_cep_m=5.0,
        warhead_yield_kg=500.0,
        desired_pk=0.95
    )
    print(f"\n  Missiles required for 95% Pk: {n_missiles}")

    # Create other systems for comparison
    print("\n" + "=" * 60)
    thaad = create_thaad_battery(np.array([10000., 0., 0.]))
    s400 = create_s400_battery(np.array([20000., 0., 0.]))

    systems = [
        ("Patriot PAC-3", patriot),
        ("THAAD", thaad),
        ("S-400", s400)
    ]

    print("\nAir Defense System Comparison:")
    print(f"{'System':<20} {'Radars':<10} {'Launchers':<12} {'Missiles':<10} {'Total RCS (m²)':<15}")
    print("-" * 75)
    for name, sys in systems:
        total_missiles = sum(lnch.missiles_ready for lnch in sys.launchers)
        print(f"{name:<20} {len(sys.radars):<10} {len(sys.launchers):<12} "
              f"{total_missiles:<10} {sys.get_total_rcs_m2():<15.1f}")
