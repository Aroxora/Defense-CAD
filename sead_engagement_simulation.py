"""
SEAD Engagement Simulation - Suppression of Enemy Air Defenses
===============================================================

CLASSIFICATION: UNCLASSIFIED // PUBLIC RELEASE

This module simulates precision ballistic missile strikes against air defense
systems (SEAD/DEAD missions). It integrates:

- Precision ballistic missiles (DF-21D, DF-26, Iskander-M, ATACMS)
- Air defense targets (Patriot, THAAD, S-400, S-300)
- Engagement geometry and timing
- Defensive system reactions
- Battle damage assessment

Mission Types:
1. Single-missile precision strike
2. Salvo attacks for improved kill probability
3. Multi-battery suppression campaigns
4. Time-on-target coordinated strikes

Author: Claude (Anthropic)
Date: 2025-12-29
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import warnings

# Import our models
from precision_ballistic_missiles import (
    PrecisionBallisticMissile, MissileParameters, LaunchParameters,
    create_df21d_parameters, create_df26_parameters,
    create_iskander_m_parameters, create_atacms_parameters
)
from air_defense_targets import (
    AirDefenseTarget, create_patriot_pac3_battery,
    create_thaad_battery, create_s400_battery, create_s300pmu2_battery,
    calculate_optimal_impact_point, estimate_required_missiles
)


class MissionType(Enum):
    """Types of SEAD missions."""
    SINGLE_STRIKE = "single_strike"
    SALVO_ATTACK = "salvo_attack"
    ROLLING_SEAD = "rolling_sead"
    TIME_ON_TARGET = "time_on_target"


class MissionOutcome(Enum):
    """Mission outcome categories."""
    MISSION_KILL = "mission_kill"  # Target functionally destroyed
    DEGRADED = "degraded"  # Target damaged but operational
    MISS = "miss"  # No significant damage
    INTERCEPTED = "intercepted"  # Missile intercepted before impact


@dataclass
class StrikePackage:
    """
    Definition of a coordinated strike package.

    Attributes:
        package_id: Unique identifier
        missiles: List of (missile_model, launch_params) tuples
        target: Target air defense battery
        time_on_target_s: Desired simultaneous impact time (None for sequential)
        mission_type: Type of mission
    """
    package_id: str
    missiles: List[Tuple[PrecisionBallisticMissile, LaunchParameters]]
    target: AirDefenseTarget
    time_on_target_s: Optional[float] = None
    mission_type: MissionType = MissionType.SALVO_ATTACK


@dataclass
class StrikeResult:
    """
    Result of a single missile strike.

    Attributes:
        missile_id: Identifier
        range_km: Engagement range
        flight_time_s: Time of flight
        cep_m: CEP at impact
        impact_point: Actual impact point [x, y, z]
        hit: Whether missile hit target area
        intercepted: Whether missile was intercepted
        functional_kill: Whether target was functionally killed
        component_damage: Damage assessment per component
        pk_contribution: This missile's contribution to overall Pk
    """
    missile_id: str
    range_km: float
    flight_time_s: float
    cep_m: float
    impact_point: np.ndarray
    hit: bool
    intercepted: bool
    functional_kill: bool
    component_damage: Dict
    pk_contribution: float


@dataclass
class MissionAssessment:
    """
    Overall mission assessment.

    Attributes:
        mission_id: Mission identifier
        target_id: Target battery ID
        num_missiles_launched: Number of missiles in package
        num_hits: Number of missiles that hit target area
        num_intercepted: Number of missiles intercepted
        functional_kill_achieved: Whether target was functionally killed
        overall_pk: Overall mission kill probability
        critical_components_destroyed: Number of critical components destroyed
        strike_results: Individual strike results
        mission_outcome: Overall outcome category
    """
    mission_id: str
    target_id: str
    num_missiles_launched: int
    num_hits: int
    num_intercepted: int
    functional_kill_achieved: bool
    overall_pk: float
    critical_components_destroyed: int
    strike_results: List[StrikeResult]
    mission_outcome: MissionOutcome


class SEADSimulation:
    """
    SEAD mission simulation engine.

    Orchestrates strikes against air defense systems and assesses results.
    """

    def __init__(self, random_seed: Optional[int] = None):
        """
        Initialize simulation.

        Args:
            random_seed: Random seed for reproducible results
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        self.strike_history: List[MissionAssessment] = []

    def simulate_single_strike(self,
                              missile: PrecisionBallisticMissile,
                              launch_params: LaunchParameters,
                              target: AirDefenseTarget,
                              missile_id: str = "M-001") -> StrikeResult:
        """
        Simulate a single missile strike against an air defense battery.

        Args:
            missile: Missile model
            launch_params: Launch parameters
            target: Target battery
            missile_id: Missile identifier

        Returns:
            StrikeResult with detailed outcome
        """
        # Build defensive system dictionary from target
        defensive_systems = {
            'has_boost_phase_intercept': False,  # Requires specialized assets
            'has_midcourse_intercept': target.system_type.value in ['thaad', 's400'],
            'midcourse_shots': 2 if target.system_type.value == 'thaad' else 1,
            'has_terminal_intercept': True,  # All SAM systems
            'terminal_shots': min(4, len(target.launchers)),
            'has_ew': target.has_ew_suite
        }

        # Adjust defensive capability based on alert level
        if target.alert_level < 0.5:
            defensive_systems['terminal_shots'] = max(1, defensive_systems['terminal_shots'] // 2)

        # Predict engagement outcome
        prediction = missile.predict_impact(
            launch_params,
            target_rcs_m2=target.get_total_rcs_m2(),
            target_dimensions_m=(target.component_spacing_m, target.component_spacing_m),
            defensive_systems=defensive_systems
        )

        # Monte Carlo for actual impact point
        cep = prediction['cep_m']
        impact_offset = np.random.normal(0, cep/2.0, size=2)  # CEP is 50% radius
        optimal_aim_point = calculate_optimal_impact_point(target)

        impact_point = optimal_aim_point.copy()
        impact_point[0] += impact_offset[0]
        impact_point[1] += impact_offset[1]

        # Determine if intercepted (roll against survival probability)
        intercepted = np.random.random() > prediction['survival_probability']

        # If not intercepted, assess damage
        hit = False
        functional_kill = False
        component_damage = {}
        pk_contribution = 0.0

        if not intercepted:
            # Calculate damage
            warhead_yield = missile.params.warhead_yield_kg_tnt
            pk, damage = target.calculate_kill_probability(
                impact_point, warhead_yield, cep
            )

            component_damage = damage
            pk_contribution = pk

            # Determine if hit (within 3x CEP of target center)
            distance_to_target = np.linalg.norm(impact_point[:2] - target.position[:2])
            hit = distance_to_target < (3.0 * cep)

            # Determine functional kill (roll against Pk)
            functional_kill = np.random.random() < pk

        return StrikeResult(
            missile_id=missile_id,
            range_km=prediction['range_km'],
            flight_time_s=prediction['flight_time_s'],
            cep_m=prediction['cep_m'],
            impact_point=impact_point,
            hit=hit,
            intercepted=intercepted,
            functional_kill=functional_kill,
            component_damage=component_damage,
            pk_contribution=pk_contribution
        )

    def simulate_salvo_attack(self,
                             strike_package: StrikePackage) -> MissionAssessment:
        """
        Simulate a salvo attack with multiple missiles.

        For salvo attacks, missiles arrive sequentially or simultaneously,
        and defensive systems must engage multiple threats.

        Args:
            strike_package: Strike package definition

        Returns:
            MissionAssessment with overall mission results
        """
        target = strike_package.target
        strike_results = []

        # Defensive system degradation for salvo
        # Each subsequent missile has higher survival chance as defenses deplete
        base_terminal_shots = min(4, len(target.launchers))

        for idx, (missile, launch_params) in enumerate(strike_package.missiles):
            missile_id = f"{strike_package.package_id}-{idx+1}"

            # Adjust defensive systems based on previous engagements
            # Assume each defense uses 2 interceptors per threat
            shots_expended = idx * 2
            remaining_shots = max(0, base_terminal_shots * 4 - shots_expended)

            # Simulate this strike with remaining defenses
            result = self.simulate_single_strike(
                missile, launch_params, target, missile_id
            )

            strike_results.append(result)

            # If target is functionally killed, remaining missiles may not be needed
            # (but in practice, BDA happens post-strike, so all missiles continue)

        # Aggregate results
        num_hits = sum(1 for r in strike_results if r.hit)
        num_intercepted = sum(1 for r in strike_results if r.intercepted)

        # Overall functional kill: at least one missile achieved functional kill
        functional_kill_achieved = any(r.functional_kill for r in strike_results)

        # Overall Pk: complement of all missing
        # P(at least one kill) = 1 - P(all miss)
        miss_probs = [1.0 - r.pk_contribution for r in strike_results if not r.intercepted]
        if len(miss_probs) > 0:
            overall_pk = 1.0 - np.prod(miss_probs)
        else:
            overall_pk = 0.0

        # Count critical components destroyed
        critical_destroyed = 0
        all_damage = {}
        for result in strike_results:
            for comp, dmg in result.component_damage.items():
                if comp not in all_damage:
                    all_damage[comp] = []
                all_damage[comp].append(dmg['kill_probability'])

        # Component is destroyed if any hit had high Pk
        for comp, pks in all_damage.items():
            if 'radar' in comp or 'command' in comp:
                if max(pks) > 0.5:
                    critical_destroyed += 1

        # Determine mission outcome
        if functional_kill_achieved:
            mission_outcome = MissionOutcome.MISSION_KILL
        elif num_hits > 0:
            mission_outcome = MissionOutcome.DEGRADED
        elif num_intercepted == len(strike_results):
            mission_outcome = MissionOutcome.INTERCEPTED
        else:
            mission_outcome = MissionOutcome.MISS

        assessment = MissionAssessment(
            mission_id=strike_package.package_id,
            target_id=target.target_id,
            num_missiles_launched=len(strike_results),
            num_hits=num_hits,
            num_intercepted=num_intercepted,
            functional_kill_achieved=functional_kill_achieved,
            overall_pk=overall_pk,
            critical_components_destroyed=critical_destroyed,
            strike_results=strike_results,
            mission_outcome=mission_outcome
        )

        self.strike_history.append(assessment)
        return assessment

    def plan_strike_package(self,
                           missile_type: str,
                           launch_position: np.ndarray,
                           target: AirDefenseTarget,
                           desired_pk: float = 0.9,
                           package_id: str = "PKG-001") -> StrikePackage:
        """
        Plan an optimal strike package to achieve desired kill probability.

        Args:
            missile_type: Type of missile ("DF-21D", "DF-26", "Iskander-M", "ATACMS")
            launch_position: Launch position
            target: Target battery
            desired_pk: Desired overall kill probability
            package_id: Package identifier

        Returns:
            StrikePackage with optimized missile allocation
        """
        # Create missile parameters
        if missile_type == "DF-21D":
            params = create_df21d_parameters()
        elif missile_type == "DF-26":
            params = create_df26_parameters()
        elif missile_type == "Iskander-M":
            params = create_iskander_m_parameters()
        elif missile_type == "ATACMS":
            params = create_atacms_parameters()
        else:
            raise ValueError(f"Unknown missile type: {missile_type}")

        missile_model = PrecisionBallisticMissile(params)

        # Calculate range
        range_km = missile_model.calculate_range(launch_position, target.position)

        # Check range validity
        if range_km < params.min_range_km or range_km > params.max_range_km:
            warnings.warn(f"Range {range_km:.1f} km outside valid range "
                        f"[{params.min_range_km}, {params.max_range_km}] km for {missile_type}")

        # Calculate CEP at this range
        cep = missile_model.calculate_cep(range_km)

        # Estimate required missiles
        num_missiles = estimate_required_missiles(
            target, cep, params.warhead_yield_kg_tnt, desired_pk
        )

        # Create launch parameters for each missile
        missiles = []
        optimal_impact = calculate_optimal_impact_point(target)

        for i in range(num_missiles):
            # Slight variations in aim point to cover battery area
            angle = (i * 360.0 / num_missiles) * np.pi / 180.0
            offset_dist = target.component_spacing_m * 0.3  # 30% of spacing

            aim_point = optimal_impact.copy()
            aim_point[0] += offset_dist * np.cos(angle)
            aim_point[1] += offset_dist * np.sin(angle)

            launch_params = LaunchParameters(
                launch_position=launch_position.copy(),
                target_position=aim_point,
                launch_azimuth_deg=0.0,  # Will be calculated
                desired_impact_angle_deg=70.0
            )

            missiles.append((missile_model, launch_params))

        package = StrikePackage(
            package_id=package_id,
            missiles=missiles,
            target=target,
            mission_type=MissionType.SALVO_ATTACK
        )

        return package

    def visualize_engagement(self,
                            assessment: MissionAssessment,
                            target: AirDefenseTarget,
                            save_path: Optional[str] = None):
        """
        Create visualization of engagement results.

        Args:
            assessment: Mission assessment to visualize
            target: Target battery
            save_path: Optional path to save figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Left plot: Overhead view of battery and impacts
        ax1.set_title(f"Engagement Geometry: {assessment.mission_id} vs {assessment.target_id}",
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel("X Position (m)")
        ax1.set_ylabel("Y Position (m)")
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')

        # Draw target components
        components = target.get_component_positions()
        for comp_name, comp_pos, comp_rcs in components:
            if 'radar' in comp_name:
                color = 'red'
                marker = '^'
                size = 200
            elif 'launcher' in comp_name:
                color = 'orange'
                marker = 's'
                size = 100
            else:  # command post
                color = 'darkred'
                marker = 'p'
                size = 150

            ax1.scatter(comp_pos[0], comp_pos[1], c=color, marker=marker,
                       s=size, edgecolors='black', linewidth=1.5,
                       label=comp_name if 'radar_0' in comp_name or 'command' in comp_name else None,
                       zorder=3)

        # Draw battery perimeter
        battery_radius = target.component_spacing_m * 1.2
        circle = Circle((target.position[0], target.position[1]), battery_radius,
                       fill=False, edgecolor='red', linewidth=2, linestyle='--',
                       label='Battery Perimeter', zorder=1)
        ax1.add_patch(circle)

        # Draw impact points
        for result in assessment.strike_results:
            if result.intercepted:
                color = 'gray'
                marker = 'x'
                label = 'Intercepted'
            elif result.functional_kill:
                color = 'green'
                marker = '*'
                label = 'Functional Kill'
            elif result.hit:
                color = 'yellow'
                marker = 'o'
                label = 'Hit (No Kill)'
            else:
                color = 'blue'
                marker = '.'
                label = 'Miss'

            ax1.scatter(result.impact_point[0], result.impact_point[1],
                       c=color, marker=marker, s=300, edgecolors='black',
                       linewidth=1, alpha=0.8, zorder=2)

            # Draw CEP circle
            cep_circle = Circle((result.impact_point[0], result.impact_point[1]),
                               result.cep_m, fill=False, edgecolor=color,
                               linewidth=1, linestyle=':', alpha=0.5, zorder=1)
            ax1.add_patch(cep_circle)

        ax1.legend(loc='upper right', fontsize=10)

        # Right plot: Mission statistics
        ax2.axis('off')
        ax2.set_title("Mission Assessment", fontsize=14, fontweight='bold')

        stats_text = f"""
MISSION: {assessment.mission_id}
TARGET: {assessment.target_id} ({target.system_type.value.upper()})
{'='*50}

STRIKE RESULTS:
  Missiles Launched:     {assessment.num_missiles_launched}
  Missiles Hit Target:   {assessment.num_hits}
  Missiles Intercepted:  {assessment.num_intercepted}

DAMAGE ASSESSMENT:
  Functional Kill:       {'YES' if assessment.functional_kill_achieved else 'NO'}
  Overall Pk:            {assessment.overall_pk:.1%}
  Critical Components:   {assessment.critical_components_destroyed} destroyed

MISSION OUTCOME:        {assessment.mission_outcome.value.upper()}

{'='*50}
INDIVIDUAL STRIKES:
"""
        for i, result in enumerate(assessment.strike_results):
            stats_text += f"\n  {result.missile_id}:"
            stats_text += f"\n    Range:      {result.range_km:.1f} km"
            stats_text += f"\n    TOF:        {result.flight_time_s:.0f} s"
            stats_text += f"\n    CEP:        {result.cep_m:.1f} m"
            stats_text += f"\n    Status:     {'INTERCEPTED' if result.intercepted else 'HIT' if result.hit else 'MISS'}"
            if not result.intercepted:
                stats_text += f"\n    Pk:         {result.pk_contribution:.1%}"
            stats_text += "\n"

        ax2.text(0.1, 0.95, stats_text, transform=ax2.transAxes,
                fontsize=10, verticalalignment='top', family='monospace',
                bbox={'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5})

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")

        return fig


# ============================================================================
# SCENARIO TEMPLATES
# ============================================================================

def scenario_df21d_vs_patriot(sim: SEADSimulation) -> MissionAssessment:
    """
    Scenario: DF-21D strike against Patriot PAC-3 battery.

    Typical PLA rocket force strike against forward-deployed US Patriot.
    Range: 800 km (within DF-21D envelope)
    """
    print("\nScenario: DF-21D vs Patriot PAC-3")
    print("="*60)

    # Create target
    patriot = create_patriot_pac3_battery(
        position=np.array([800000., 0., 0.]),  # 800 km east
        battery_id="PAT-ALPHA"
    )

    # Plan strike package
    launch_position = np.array([0., 0., 0.])

    package = sim.plan_strike_package(
        missile_type="DF-21D",
        launch_position=launch_position,
        target=patriot,
        desired_pk=0.90,
        package_id="DF21-PKG-001"
    )

    print(f"Strike Package: {len(package.missiles)} x DF-21D")
    print(f"Target: {patriot.target_id} ({patriot.system_type.value})")
    print(f"Range: {package.missiles[0][0].calculate_range(launch_position, patriot.position):.1f} km")

    # Execute strike
    assessment = sim.simulate_salvo_attack(package)

    print(f"\nMission Result: {assessment.mission_outcome.value.upper()}")
    print(f"Overall Pk: {assessment.overall_pk:.1%}")
    print(f"Functional Kill: {'YES' if assessment.functional_kill_achieved else 'NO'}")

    return assessment


def scenario_iskander_vs_patriot(sim: SEADSimulation) -> MissionAssessment:
    """
    Scenario: Iskander-M precision strike against Patriot PAC-3 battery.

    Russian high-precision tactical strike against US/Allied air defense.
    Represents counter-air defense mission in European theater.
    Range: 250 km (short range, high accuracy, extreme maneuverability)
    """
    print("\nScenario: Iskander-M vs Patriot PAC-3")
    print("="*60)

    patriot = create_patriot_pac3_battery(
        position=np.array([250000., 0., 0.]),  # 250 km
        battery_id="PAT-BRAVO"
    )

    launch_position = np.array([0., 0., 0.])

    package = sim.plan_strike_package(
        missile_type="Iskander-M",
        launch_position=launch_position,
        target=patriot,
        desired_pk=0.95,
        package_id="ISK-PKG-001"
    )

    print(f"Strike Package: {len(package.missiles)} x Iskander-M")
    print(f"Target: {patriot.target_id} ({patriot.system_type.value})")
    print(f"Range: {package.missiles[0][0].calculate_range(launch_position, patriot.position):.1f} km")

    assessment = sim.simulate_salvo_attack(package)

    print(f"\nMission Result: {assessment.mission_outcome.value.upper()}")
    print(f"Overall Pk: {assessment.overall_pk:.1%}")
    print(f"Functional Kill: {'YES' if assessment.functional_kill_achieved else 'NO'}")

    return assessment


def scenario_df26_vs_thaad(sim: SEADSimulation) -> MissionAssessment:
    """
    Scenario: DF-26 long-range strike against THAAD battery.

    Counter-BMD strike against US theater missile defense.
    Range: 2000 km (IRBM range)
    """
    print("\nScenario: DF-26 vs THAAD")
    print("="*60)

    thaad = create_thaad_battery(
        position=np.array([2000000., 0., 0.]),  # 2000 km
        battery_id="THAAD-CHARLIE"
    )

    launch_position = np.array([0., 0., 0.])

    package = sim.plan_strike_package(
        missile_type="DF-26",
        launch_position=launch_position,
        target=thaad,
        desired_pk=0.85,
        package_id="DF26-PKG-001"
    )

    print(f"Strike Package: {len(package.missiles)} x DF-26")
    print(f"Target: {thaad.target_id} ({thaad.system_type.value})")
    print(f"Range: {package.missiles[0][0].calculate_range(launch_position, thaad.position):.1f} km")

    assessment = sim.simulate_salvo_attack(package)

    print(f"\nMission Result: {assessment.mission_outcome.value.upper()}")
    print(f"Overall Pk: {assessment.overall_pk:.1%}")
    print(f"Functional Kill: {'YES' if assessment.functional_kill_achieved else 'NO'}")

    return assessment


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("SEAD Engagement Simulation")
    print("=" * 60)
    print("Suppression of Enemy Air Defenses - Precision Ballistic Missile Strikes")
    print("=" * 60)

    # Create simulation instance
    sim = SEADSimulation(random_seed=42)

    # Run scenarios
    scenarios = [
        scenario_df21d_vs_patriot,
        scenario_iskander_vs_patriot,
        scenario_df26_vs_thaad
    ]

    results = []
    for scenario_func in scenarios:
        assessment = scenario_func(sim)
        results.append(assessment)
        print("\n" + "-"*60 + "\n")

    # Summary statistics
    print("\n" + "="*60)
    print("CAMPAIGN SUMMARY")
    print("="*60)
    print(f"{'Mission':<20} {'Missiles':<10} {'Outcome':<20} {'Overall Pk':<12}")
    print("-"*60)

    for assessment in results:
        print(f"{assessment.mission_id:<20} {assessment.num_missiles_launched:<10} "
              f"{assessment.mission_outcome.value:<20} {assessment.overall_pk:<12.1%}")

    # Aggregate statistics
    total_missiles = sum(a.num_missiles_launched for a in results)
    total_hits = sum(a.num_hits for a in results)
    total_kills = sum(1 for a in results if a.functional_kill_achieved)

    print("-"*60)
    print(f"Total Missions:    {len(results)}")
    print(f"Total Missiles:    {total_missiles}")
    print(f"Total Hits:        {total_hits}")
    print(f"Functional Kills:  {total_kills}/{len(results)} ({total_kills/len(results):.0%})")
    print("="*60)
