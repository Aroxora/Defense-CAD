#!/usr/bin/env python3
"""
LRHW (Dark Eagle) Engagement Simulation

Complete simulation of LRHW hypersonic weapon strikes against
high-value land targets including command centers, airbases,
and hardened bunkers.

Demonstrates:
1. Single missile strikes vs different target types
2. Salvo attacks vs defended targets
3. Trajectory visualization
4. Defensive system effectiveness
5. Multi-target engagement scenarios

Classification: UNCLASSIFIED // PUBLIC RELEASE
Educational simulation based on public sources only.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
from osint_cad.targeting.lrhw_hgv_model import (
    LRHWHGVModel, LRHWParameters, LandTarget, StrikeParameters,
    create_hardened_bunker, create_airbase, create_radar_site, create_command_center,
    ImpactPrediction, TrajectoryPoint
)


class IntegratedAirDefenseSystem:
    """
    Integrated Air Defense System (IADS) protecting high-value targets

    Typical composition:
    - Long-range BMD (THAAD equivalent)
    - Medium-range SAM (S-400 equivalent)
    - Point defense (Patriot/S-300)
    - EW systems
    """

    def __init__(self, center_position: np.ndarray, defense_type: str = "layered"):
        """
        Create IADS

        Args:
            center_position: Defense center position [x, y, z]
            defense_type: "layered", "point", or "area"
        """
        self.center_position = center_position
        self.defense_type = defense_type

        # Configure defensive layers based on type
        if defense_type == "layered":
            self.has_long_range_bmd = True
            self.has_medium_range_sam = True
            self.has_point_defense = True
            self.has_ew = True
            self.engagement_range_km = 400
        elif defense_type == "point":
            self.has_long_range_bmd = False
            self.has_medium_range_sam = False
            self.has_point_defense = True
            self.has_ew = True
            self.engagement_range_km = 40
        else:  # area
            self.has_long_range_bmd = False
            self.has_medium_range_sam = True
            self.has_point_defense = True
            self.has_ew = True
            self.engagement_range_km = 200

    def calculate_intercept_probability(self,
                                       incoming_velocity_ms: float,
                                       altitude_km: float,
                                       target_distance_km: float) -> float:
        """
        Calculate probability of intercepting incoming hypersonic weapon

        Args:
            incoming_velocity_ms: Incoming weapon velocity
            altitude_km: Current altitude of weapon
            target_distance_km: Distance to protected target

        Returns:
            Intercept probability (0-1)
        """
        total_pk = 0.0

        # Hypersonic weapons are very difficult to intercept
        # Base difficulty factor based on Mach number
        mach_number = incoming_velocity_ms / 340.0
        difficulty_factor = max(0.1, 1.0 - (mach_number / 20.0))

        # Long-range BMD engagement (if in range and altitude)
        if self.has_long_range_bmd and altitude_km > 40:
            if target_distance_km < 300:
                bmd_pk = 0.15 * difficulty_factor  # THAAD equivalent
                total_pk = 1 - (1 - total_pk) * (1 - bmd_pk)

        # Medium-range SAM engagement
        if self.has_medium_range_sam and altitude_km < 50:
            if target_distance_km < 100:
                sam_pk = 0.10 * difficulty_factor
                total_pk = 1 - (1 - total_pk) * (1 - sam_pk)

        # Point defense engagement (terminal phase only)
        if self.has_point_defense and altitude_km < 20:
            if target_distance_km < 30:
                pd_pk = 0.08 * difficulty_factor
                total_pk = 1 - (1 - total_pk) * (1 - pd_pk)

        # EW can degrade guidance
        if self.has_ew:
            # GPS jamming effectiveness
            ew_degradation = 0.95  # 5% reduction in accuracy
            total_pk *= (1 + (1 - ew_degradation) * 0.1)  # Slightly reduces impact

        return min(total_pk, 0.5)  # Cap at 50% - hypersonics are very hard to stop


class LRHWEngagementScenario:
    """
    Complete LRHW engagement scenario manager

    Handles multiple missiles engaging multiple targets with
    realistic timing, defensive responses, and outcome calculation.
    """

    def __init__(self):
        self.lrhw_model = LRHWHGVModel()
        self.missiles_fired: List[Tuple[StrikeParameters, ImpactPrediction]] = []
        self.targets_destroyed: List[str] = []
        self.simulation_time: float = 0.0

    def execute_single_strike(self,
                            launch_position: np.ndarray,
                            target: LandTarget,
                            verbose: bool = True) -> ImpactPrediction:
        """
        Execute single LRHW strike

        Args:
            launch_position: Launch position [x, y, z]
            target: Land target
            verbose: Print strike details

        Returns:
            ImpactPrediction result
        """
        strike_params = StrikeParameters(
            launch_position=launch_position,
            target=target,
            launch_azimuth_deg=0,  # Will be calculated
            desired_impact_angle_deg=70,
            salvo_size=1
        )

        prediction = self.lrhw_model.predict_impact(strike_params)
        self.missiles_fired.append((strike_params, prediction))

        if verbose:
            print(f"\n  Strike on {target.target_id} ({target.target_type}):")
            print(f"    Range:              {np.linalg.norm(target.position - launch_position)/1000:.0f} km")
            print(f"    Time to impact:     {prediction.time_to_impact_s:.1f} s ({prediction.time_to_impact_s/60:.1f} min)")
            print(f"    Impact velocity:    Mach {prediction.impact_velocity_ms/340:.1f}")
            print(f"    CEP:                {prediction.cep_at_impact_m:.1f} m")
            print(f"    Pk (single shot):   {prediction.probability_hit:.1%}")

            # Determine outcome
            roll = np.random.random()
            if roll < prediction.probability_hit:
                print(f"    RESULT:             *** HIT *** (rolled {roll:.3f} < {prediction.probability_hit:.3f})")
                self.targets_destroyed.append(target.target_id)
            else:
                print(f"    RESULT:             MISS (rolled {roll:.3f} >= {prediction.probability_hit:.3f})")

        return prediction

    def execute_salvo_strike(self,
                           launch_position: np.ndarray,
                           target: LandTarget,
                           salvo_size: int = 2,
                           verbose: bool = True) -> Tuple[float, List[ImpactPrediction]]:
        """
        Execute salvo strike (multiple missiles)

        Args:
            launch_position: Launch position
            target: Target
            salvo_size: Number of missiles
            verbose: Print details

        Returns:
            Tuple of (overall_pk, individual_predictions)
        """
        strike_params = StrikeParameters(
            launch_position=launch_position,
            target=target,
            launch_azimuth_deg=0,
            desired_impact_angle_deg=70,
            salvo_size=salvo_size
        )

        overall_pk, predictions = self.lrhw_model.calculate_salvo_effectiveness(strike_params)

        for pred in predictions:
            self.missiles_fired.append((strike_params, pred))

        if verbose:
            print(f"\n  Salvo Strike ({salvo_size}x LRHW) on {target.target_id}:")
            print(f"    Range:              {np.linalg.norm(target.position - launch_position)/1000:.0f} km")
            print(f"    Individual Pk:      {predictions[0].probability_hit:.1%}")
            print(f"    Salvo overall Pk:   {overall_pk:.1%}")
            print(f"    Expected hits:      {overall_pk * salvo_size:.2f} / {salvo_size}")

            # Simulate hits
            hits = 0
            for i, pred in enumerate(predictions, 1):
                roll = np.random.random()
                if roll < pred.probability_hit:
                    hits += 1
                    print(f"    Missile #{i}:         HIT")
                else:
                    print(f"    Missile #{i}:         MISS")

            if hits > 0:
                print(f"    RESULT:             *** {hits} HIT(S) - TARGET DESTROYED ***")
                self.targets_destroyed.append(target.target_id)
            else:
                print(f"    RESULT:             All missiles missed")

        return overall_pk, predictions


def plot_strike_geometry(launch_position: np.ndarray,
                        target: LandTarget,
                        prediction: ImpactPrediction,
                        trajectory: List[TrajectoryPoint] = None):
    """
    Plot 2D strike geometry

    Args:
        launch_position: Launch position
        target: Target
        prediction: Impact prediction
        trajectory: Optional detailed trajectory
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('#1a1a1a')

    # --- Top-down view ---
    ax1.set_facecolor('#0a0a0a')

    # Launch position
    ax1.plot(launch_position[0]/1000, launch_position[1]/1000,
            '^', color='blue', markersize=12, label='Launch Position')

    # Target position
    ax1.plot(target.position[0]/1000, target.position[1]/1000,
            's', color='red', markersize=15, label=f'Target: {target.target_id}')

    # Target size circle
    target_radius = max(target.length_m, target.width_m) / 2 / 1000  # km
    circle = plt.Circle((target.position[0]/1000, target.position[1]/1000),
                       target_radius, color='red', fill=False, linestyle='--')
    ax1.add_patch(circle)

    # CEP circle
    cep_circle = plt.Circle((prediction.impact_point[0]/1000, prediction.impact_point[1]/1000),
                           prediction.cep_at_impact_m/1000, color='yellow',
                           fill=False, linestyle=':', linewidth=2, label='CEP')
    ax1.add_patch(cep_circle)

    # Trajectory
    if trajectory:
        traj_x = [p.position[0]/1000 for p in trajectory]
        traj_y = [p.position[1]/1000 for p in trajectory]
        ax1.plot(traj_x, traj_y, '-', color='#00ff00', linewidth=2, label='Trajectory')
    else:
        # Simple line
        ax1.plot([launch_position[0]/1000, prediction.impact_point[0]/1000],
                [launch_position[1]/1000, prediction.impact_point[1]/1000],
                '-', color='#00ff00', linewidth=2, label='Flight Path')

    # Impact point
    ax1.plot(prediction.impact_point[0]/1000, prediction.impact_point[1]/1000,
            'x', color='yellow', markersize=15, markeredgewidth=3, label='Predicted Impact')

    ax1.set_xlabel('East (km)', color='white')
    ax1.set_ylabel('North (km)', color='white')
    ax1.set_title('Top-Down View', color='white', fontweight='bold')
    ax1.grid(True, alpha=0.3, color='#00ff00', linestyle=':')
    ax1.legend(facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
    ax1.tick_params(colors='white')
    ax1.set_aspect('equal')

    # --- Altitude profile ---
    ax2.set_facecolor('#0a0a0a')

    if trajectory:
        traj_range = [np.linalg.norm(p.position[:2] - launch_position[:2])/1000 for p in trajectory]
        traj_alt = [p.altitude_m/1000 for p in trajectory]
        ax2.plot(traj_range, traj_alt, '-', color='#00ff00', linewidth=2)

        # Color-code by phase
        for i in range(len(trajectory)-1):
            if trajectory[i].phase.value == 'boost':
                color = 'blue'
            elif trajectory[i].phase.value == 'glide':
                color = '#00ff00'
            elif trajectory[i].phase.value == 'terminal':
                color = 'yellow'
            else:
                color = 'gray'

            ax2.plot(traj_range[i:i+2], traj_alt[i:i+2], '-', color=color, linewidth=3)

    # Target position
    target_range = np.linalg.norm(target.position[:2] - launch_position[:2])/1000
    ax2.plot([0, target_range], [0, 0], 'r-', linewidth=3, label='Ground Level')
    ax2.plot(target_range, 0, 's', color='red', markersize=15)

    ax2.set_xlabel('Range (km)', color='white')
    ax2.set_ylabel('Altitude (km)', color='white')
    ax2.set_title('Altitude Profile', color='white', fontweight='bold')
    ax2.grid(True, alpha=0.3, color='#00ff00', linestyle=':')
    ax2.tick_params(colors='white')
    ax2.set_ylim(bottom=0)

    # Legend for phases
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='blue', label='Boost Phase'),
        Patch(facecolor='#00ff00', label='Glide Phase'),
        Patch(facecolor='yellow', label='Terminal Phase')
    ]
    ax2.legend(handles=legend_elements, facecolor='#1a1a1a',
              edgecolor='white', labelcolor='white')

    plt.tight_layout()
    return fig


def run_precision_strike_scenario(visualize: bool = True):
    """
    Scenario: LRHW precision strike on defended command center

    Demonstrates precision strike against hardened target
    protected by layered air defenses.
    """
    print("=" * 80)
    print("SCENARIO: LRHW Precision Strike on Defended Command Center")
    print("=" * 80)

    # Create defended command center at 2000 km range
    target_position = np.array([2000000, 0, 0])  # 2000 km east
    command_center = create_command_center()
    command_center.position = target_position

    print("\n[1] Target Information:")
    print(f"  - Target ID: {command_center.target_id}")
    print(f"  - Target Type: {command_center.target_type}")
    print(f"  - Hardening: {command_center.hardening_level}")
    print(f"  - Defenses: THAAD={command_center.has_thaad}, PAC-3={command_center.has_patriot}")

    # Launch position (forward deployed battery)
    launch_position = np.array([0, 0, 100])

    # Create scenario
    scenario = LRHWEngagementScenario()

    print("\n[2] LRHW Strike Plan:")
    print("  Mission: Neutralize adversary command and control")
    print("  Strategy: Precision strike with single LRHW")
    print("  Target: Hardened underground command center")

    # Execute strike
    print("\n[3] Executing Strike:")
    prediction = scenario.execute_single_strike(launch_position, command_center, verbose=True)

    # Summary
    print("\n[4] Strike Summary:")
    print(f"  Total missiles fired:   {len(scenario.missiles_fired)}")
    print(f"  Targets destroyed:      {len(scenario.targets_destroyed)}")

    # Mission assessment
    target_destroyed = command_center.target_id in scenario.targets_destroyed

    print(f"\n[5] Mission Assessment:")
    if target_destroyed:
        print(f"  OBJECTIVE:              *** SUCCESS *** - Command center destroyed")
    else:
        print(f"  OBJECTIVE:              FAILED - Target survived")

    print("\n" + "=" * 80)

    return scenario


def run_multi_target_scenario(visualize: bool = True):
    """
    Scenario: LRHW strikes on multiple target types

    Demonstrates effectiveness against different targets:
    - Command center (hardened, defended)
    - Airbase (large, lightly defended)
    - Radar site (medium, defended)
    - Hardened bunker (small, undefended)
    """
    print("=" * 80)
    print("SCENARIO: LRHW Multi-Target Strike Comparison")
    print("=" * 80)

    launch_position = np.array([0, 0, 100])
    scenario = LRHWEngagementScenario()

    # Create targets at similar ranges
    targets = [
        ("Command Center (defended)", create_command_center(), np.array([2000000, 0, 0])),
        ("Airbase (light defense)", create_airbase(), np.array([2000000, 50000, 0])),
        ("Radar Site (defended)", create_radar_site(), np.array([1800000, 100000, 0])),
        ("Hardened Bunker (undefended)", create_hardened_bunker(), np.array([2200000, 0, 0]))
    ]

    print("\n[1] Target Set:")
    for name, target, pos in targets:
        target.position = pos
        print(f"  - {name:30s} at {np.linalg.norm(pos)/1000:.0f} km")

    print("\n[2] Executing Single-Missile Strikes:")

    results = []
    for name, target, _ in targets:
        print(f"\n  --- {name} ---")
        prediction = scenario.execute_single_strike(launch_position, target, verbose=True)
        results.append((name, prediction))

    print("\n[3] Comparative Analysis:")
    print(f"  {'Target Type':<30s} {'Pk (Single)':<12s} {'CEP (m)':<10s} {'Defenses':<15s}")
    print(f"  {'-'*70}")

    for (name, target, _), (_, prediction) in zip(targets, results):
        defenses = "Yes" if target.has_thaad or target.has_patriot else "No"
        print(f"  {name:<30s} {prediction.probability_hit:<12.1%} {prediction.cep_at_impact_m:<10.1f} {defenses:<15s}")

    print("\n" + "=" * 80)

    return scenario


def run_saturation_strike_scenario(visualize: bool = True):
    """
    Scenario: LRHW saturation strike against heavily defended target

    Demonstrates use of multiple LRHWs to overwhelm defenses.
    """
    print("=" * 80)
    print("SCENARIO: LRHW Saturation Strike vs Layered Defense")
    print("=" * 80)

    # Create heavily defended target
    target_position = np.array([2500000, 0, 0])  # 2500 km
    command_center = create_command_center()
    command_center.position = target_position
    command_center.has_thaad = True
    command_center.has_patriot = True
    command_center.has_ew_suite = True

    print("\n[1] Target Information:")
    print(f"  - Target: {command_center.target_id} (Critical C2 Node)")
    print(f"  - Range: {np.linalg.norm(target_position)/1000:.0f} km")
    print(f"  - Defenses: Full layered IADS (THAAD + PAC-3 + EW)")

    # Launch position
    launch_position = np.array([0, 0, 100])

    # Create scenario
    scenario = LRHWEngagementScenario()

    print("\n[2] Strike Plan:")
    print("  Strategy: Salvo attack to saturate defenses")
    print("  Missiles: 4x LRHW (Dark Eagle)")
    print("  Impact timing: Near-simultaneous")

    # Execute salvo strike
    print("\n[3] Executing Saturation Strike:")
    overall_pk, predictions = scenario.execute_salvo_strike(
        launch_position, command_center, salvo_size=4, verbose=True)

    # Summary
    print("\n[4] Strike Summary:")
    print(f"  Missiles fired:         {len(scenario.missiles_fired)}")
    print(f"  Individual Pk:          {predictions[0].probability_hit:.1%}")
    print(f"  Salvo overall Pk:       {overall_pk:.1%}")
    print(f"  Targets destroyed:      {len(scenario.targets_destroyed)}")

    # Cost-effectiveness analysis
    print("\n[5] Cost-Effectiveness Analysis:")
    print(f"  Estimated missile cost: ~$40M per LRHW (public estimate)")
    print(f"  Total salvo cost:       ~$160M")
    print(f"  Target value:           Critical C2 node (strategic)")
    print(f"  Pk achieved:            {overall_pk:.1%}")

    print("\n" + "=" * 80)

    return scenario


def main():
    """Run all LRHW engagement scenarios"""
    print("\n" + "=" * 80)
    print("LRHW (DARK EAGLE) - ENGAGEMENT SIMULATION SUITE")
    print("=" * 80)
    print("\nClassification: UNCLASSIFIED // PUBLIC RELEASE")
    print("Educational simulation based on public sources only.")
    print("\n" + "=" * 80)

    # Scenario 1: Multi-target comparison
    print("\n\n")
    scenario1 = run_multi_target_scenario(visualize=True)

    # Scenario 2: Precision strike
    print("\n\n")
    scenario2 = run_precision_strike_scenario(visualize=True)

    # Scenario 3: Saturation strike
    print("\n\n")
    scenario3 = run_saturation_strike_scenario(visualize=True)

    # Generate visualization for command center strike
    print("\n\nGenerating trajectory visualization...")
    lrhw = LRHWHGVModel()

    # Generate trajectory for command center strike
    command_center = create_command_center()
    command_center.position = np.array([2000000, 0, 0])

    strike_params = StrikeParameters(
        launch_position=np.array([0, 0, 100]),
        target=command_center,
        launch_azimuth_deg=90,
        desired_impact_angle_deg=70,
        salvo_size=1
    )

    trajectory = lrhw.generate_trajectory(strike_params, time_step_s=5.0)
    prediction = lrhw.predict_impact(strike_params)

    plot_strike_geometry(strike_params.launch_position, command_center,
                        prediction, trajectory)

    print("\nVisualization complete. Close plot windows to exit.")
    plt.show()

    print("\n" + "=" * 80)
    print("All scenarios complete.")
    print("=" * 80)


if __name__ == "__main__":
    main()
