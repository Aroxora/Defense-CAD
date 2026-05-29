#!/usr/bin/env python3
"""
DF-17 HGV Engagement Simulation

Complete simulation of DF-17 hypersonic glide vehicle strikes against
high-value surface targets including aircraft carriers, naval vessels,
and land targets.

Demonstrates:
1. Single missile strikes vs different target types
2. Salvo attacks vs carrier strike groups
3. Trajectory visualization
4. Defensive system effectiveness
5. Multi-target engagement scenarios

Classification: UNCLASSIFIED // PUBLIC RELEASE
Educational simulation based on public sources only.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
from osint_cad.targeting.df17_hgv_model import (
    DF17HGVModel, DF17Parameters, SurfaceTarget, StrikeParameters,
    create_cvn_carrier, create_ddg_destroyer, create_cg_cruiser, create_land_target,
    InterceptPrediction, TrajectoryPoint
)


class CarrierStrikeGroup:
    """
    US Navy Carrier Strike Group (CSG) formation

    Typical composition:
    - 1x Aircraft carrier (CVN)
    - 2x Guided missile cruisers (CG)
    - 2x Guided missile destroyers (DDG)
    - 1x Attack submarine (not modeled here - submerged)
    """

    def __init__(self, center_position: np.ndarray, heading_deg: float = 0):
        """
        Create carrier strike group

        Args:
            center_position: CSG center position [x, y, z]
            heading_deg: Formation heading
        """
        self.heading_deg = heading_deg
        self.center_position = center_position

        # Create formation (positions relative to carrier)
        # Carrier at center
        self.carrier = create_cvn_carrier()
        self.carrier.target_id = "CVN-77-USS-GHW-Bush"
        self.carrier.position = center_position.copy()
        self.carrier.heading_deg = heading_deg

        # Cruisers on flanks (8 km separation)
        self.cruiser1 = create_cg_cruiser()
        self.cruiser1.target_id = "CG-73-USS-Port-Royal"
        self.cruiser1.position = center_position + np.array([0, -8000, 0])
        self.cruiser1.heading_deg = heading_deg

        self.cruiser2 = create_cg_cruiser()
        self.cruiser2.target_id = "CG-72-USS-Vella-Gulf"
        self.cruiser2.position = center_position + np.array([0, 8000, 0])
        self.cruiser2.heading_deg = heading_deg

        # Destroyers forward and aft (10 km)
        self.destroyer1 = create_ddg_destroyer()
        self.destroyer1.target_id = "DDG-114-USS-Ralph-Johnson"
        self.destroyer1.position = center_position + np.array([10000, 0, 0])
        self.destroyer1.heading_deg = heading_deg

        self.destroyer2 = create_ddg_destroyer()
        self.destroyer2.target_id = "DDG-112-USS-Michael-Murphy"
        self.destroyer2.position = center_position + np.array([-10000, 0, 0])
        self.destroyer2.heading_deg = heading_deg

        # Set velocities (all ships move together)
        formation_velocity = np.array([
            15 * np.cos(np.radians(heading_deg)),  # 30 knots ~ 15 m/s
            15 * np.sin(np.radians(heading_deg)),
            0
        ])

        for ship in self.get_all_ships():
            ship.velocity = formation_velocity

    def get_all_ships(self) -> List[SurfaceTarget]:
        """Get all ships in strike group"""
        return [
            self.carrier,
            self.cruiser1,
            self.cruiser2,
            self.destroyer1,
            self.destroyer2
        ]

    def update_positions(self, dt: float):
        """Update all ship positions"""
        for ship in self.get_all_ships():
            ship.position += ship.velocity * dt


class DF17EngagementScenario:
    """
    Complete DF-17 engagement scenario manager

    Handles multiple missiles engaging multiple targets with
    realistic timing, defensive responses, and outcome calculation.
    """

    def __init__(self):
        self.df17_model = DF17HGVModel()
        self.missiles_fired: List[Tuple[StrikeParameters, InterceptPrediction]] = []
        self.targets_destroyed: List[str] = []
        self.simulation_time: float = 0.0

    def execute_single_strike(self,
                            launch_position: np.ndarray,
                            target: SurfaceTarget,
                            verbose: bool = True) -> InterceptPrediction:
        """
        Execute single DF-17 strike

        Args:
            launch_position: Launch position [x, y, z]
            target: Surface target
            verbose: Print strike details

        Returns:
            InterceptPrediction result
        """
        strike_params = StrikeParameters(
            launch_position=launch_position,
            target=target,
            launch_azimuth_deg=0,  # Will be calculated
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = self.df17_model.predict_impact(strike_params)
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
                           target: SurfaceTarget,
                           salvo_size: int = 4,
                           verbose: bool = True) -> Tuple[float, List[InterceptPrediction]]:
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
            desired_impact_angle_deg=60,
            salvo_size=salvo_size
        )

        overall_pk, predictions = self.df17_model.calculate_salvo_effectiveness(strike_params)

        for pred in predictions:
            self.missiles_fired.append((strike_params, pred))

        if verbose:
            print(f"\n  Salvo Strike ({salvo_size}x DF-17) on {target.target_id}:")
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
                        target: SurfaceTarget,
                        prediction: InterceptPrediction,
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
            'o', color='red', markersize=12, label='Launch Position')

    # Target position
    ax1.plot(target.position[0]/1000, target.position[1]/1000,
            's', color='blue', markersize=15, label=f'Target: {target.target_id}')

    # Target size circle
    target_radius = max(target.length_m, target.beam_m) / 2 / 1000  # km
    circle = plt.Circle((target.position[0]/1000, target.position[1]/1000),
                       target_radius, color='blue', fill=False, linestyle='--')
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
                color = 'red'
            elif trajectory[i].phase.value == 'glide':
                color = '#00ff00'
            elif trajectory[i].phase.value == 'terminal':
                color = 'yellow'
            else:
                color = 'gray'

            ax2.plot(traj_range[i:i+2], traj_alt[i:i+2], '-', color=color, linewidth=3)

    # Target position
    target_range = np.linalg.norm(target.position[:2] - launch_position[:2])/1000
    ax2.plot([0, target_range], [0, 0], 'b-', linewidth=3, label='Sea Level')
    ax2.plot(target_range, 0, 's', color='blue', markersize=15)

    ax2.set_xlabel('Range (km)', color='white')
    ax2.set_ylabel('Altitude (km)', color='white')
    ax2.set_title('Altitude Profile', color='white', fontweight='bold')
    ax2.grid(True, alpha=0.3, color='#00ff00', linestyle=':')
    ax2.tick_params(colors='white')
    ax2.set_ylim(bottom=0)

    # Legend for phases
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='red', label='Boost Phase'),
        Patch(facecolor='#00ff00', label='Glide Phase'),
        Patch(facecolor='yellow', label='Terminal Phase')
    ]
    ax2.legend(handles=legend_elements, facecolor='#1a1a1a',
              edgecolor='white', labelcolor='white')

    plt.tight_layout()
    return fig


def run_carrier_strike_group_scenario(visualize: bool = True):
    """
    Scenario: DF-17 salvo attack on US Carrier Strike Group

    Demonstrates coordinated multi-missile attack on high-value
    naval formation with layered defenses.
    """
    print("=" * 80)
    print("SCENARIO: DF-17 Salvo Attack on US Carrier Strike Group")
    print("=" * 80)

    # Create carrier strike group at 2000 km range
    csg_position = np.array([2000000, 0, 0])  # 2000 km east
    csg = CarrierStrikeGroup(csg_position, heading_deg=270)  # Heading west

    print("\n[1] Carrier Strike Group Composition:")
    for ship in csg.get_all_ships():
        print(f"  - {ship.target_id:30s} ({ship.target_type:10s}) at {ship.position/1000}")
        print(f"    Defenses: Aegis={ship.has_aegis}, SM-6={ship.has_sm6}, SM-3={ship.has_sm3}, CIWS={ship.has_ciws}")

    # Launch position (mainland China)
    launch_position = np.array([0, 0, 100])

    # Create scenario
    scenario = DF17EngagementScenario()

    print("\n[2] DF-17 Strike Plan:")
    print("  Mission: Disable carrier strike group")
    print("  Strategy: Saturation attack with multiple missiles")
    print("  Primary target: Aircraft carrier (CVN)")
    print("  Secondary targets: Aegis escorts")

    # Execute strikes
    print("\n[3] Executing Strikes:")

    # Primary strike: 6x DF-17 vs carrier (overwhelm defenses)
    print("\n  --- PRIMARY STRIKE ---")
    overall_pk, _ = scenario.execute_salvo_strike(
        launch_position, csg.carrier, salvo_size=6, verbose=True)

    # Secondary strikes: 2x DF-17 per escort
    print("\n  --- SECONDARY STRIKES ---")
    for escort in [csg.cruiser1, csg.destroyer1]:
        scenario.execute_salvo_strike(
            launch_position, escort, salvo_size=2, verbose=True)

    # Summary
    print("\n[4] Strike Summary:")
    print(f"  Total missiles fired:   {len(scenario.missiles_fired)}")
    print(f"  Targets destroyed:      {len(scenario.targets_destroyed)}")
    print(f"  Destroyed ships:")
    for ship_id in scenario.targets_destroyed:
        print(f"    - {ship_id}")

    # Calculate mission success
    carrier_destroyed = csg.carrier.target_id in scenario.targets_destroyed
    escorts_destroyed = sum(1 for ship in [csg.cruiser1, csg.cruiser2,
                                          csg.destroyer1, csg.destroyer2]
                          if ship.target_id in scenario.targets_destroyed)

    print(f"\n[5] Mission Assessment:")
    if carrier_destroyed:
        print(f"  PRIMARY OBJECTIVE:      *** SUCCESS *** - Carrier destroyed")
    else:
        print(f"  PRIMARY OBJECTIVE:      FAILED - Carrier survived")

    print(f"  SECONDARY OBJECTIVE:    {escorts_destroyed}/4 escorts destroyed")

    if carrier_destroyed and escorts_destroyed >= 2:
        print(f"\n  OVERALL:                *** MISSION SUCCESS ***")
        print(f"                          Strike group combat ineffective")
    elif carrier_destroyed:
        print(f"\n  OVERALL:                PARTIAL SUCCESS")
        print(f"                          Carrier destroyed but escorts remain")
    else:
        print(f"\n  OVERALL:                MISSION FAILURE")
        print(f"                          Strike group remains combat effective")

    print("\n" + "=" * 80)

    return scenario, csg


def run_multi_target_scenario(visualize: bool = True):
    """
    Scenario: DF-17 strikes on multiple target types

    Demonstrates effectiveness against different targets:
    - Aircraft carrier (hardest - layered defenses)
    - Destroyer (medium - Aegis system)
    - Land target (easiest - no mobile defenses)
    """
    print("=" * 80)
    print("SCENARIO: DF-17 Multi-Target Strike Comparison")
    print("=" * 80)

    launch_position = np.array([0, 0, 100])
    scenario = DF17EngagementScenario()

    # Create targets at similar ranges
    targets = [
        ("Aircraft Carrier", create_cvn_carrier(), np.array([2000000, 0, 0])),
        ("Aegis Destroyer", create_ddg_destroyer(), np.array([2000000, 50000, 0])),
        ("Land Airbase", create_land_target(), np.array([2000000, 100000, 0]))
    ]

    print("\n[1] Target Set:")
    for name, target, pos in targets:
        target.position = pos
        print(f"  - {name:20s} at {np.linalg.norm(pos)/1000:.0f} km")

    print("\n[2] Executing Single-Missile Strikes:")

    results = []
    for name, target, _ in targets:
        print(f"\n  --- {name} ---")
        prediction = scenario.execute_single_strike(launch_position, target, verbose=True)
        results.append((name, prediction))

    print("\n[3] Comparative Analysis:")
    print(f"  {'Target Type':<20s} {'Pk (Single)':<12s} {'CEP (m)':<10s} {'Defenses':<15s}")
    print(f"  {'-'*60}")

    for (name, target, _), (_, prediction) in zip(targets, results):
        defenses = "Full" if target.has_aegis else "None"
        print(f"  {name:<20s} {prediction.probability_hit:<12.1%} {prediction.cep_at_impact_m:<10.1f} {defenses:<15s}")

    print("\n" + "=" * 80)

    return scenario


def main():
    """Run all DF-17 engagement scenarios"""
    print("\n" + "=" * 80)
    print("DF-17 HYPERSONIC GLIDE VEHICLE - ENGAGEMENT SIMULATION SUITE")
    print("=" * 80)
    print("\nClassification: UNCLASSIFIED // PUBLIC RELEASE")
    print("Educational simulation based on public sources only.")
    print("\n" + "=" * 80)

    # Scenario 1: Multi-target comparison
    print("\n\n")
    scenario1 = run_multi_target_scenario(visualize=True)

    # Scenario 2: Carrier strike group
    print("\n\n")
    scenario2, csg = run_carrier_strike_group_scenario(visualize=True)

    # Generate visualization for carrier strike
    print("\n\nGenerating trajectory visualization...")
    df17 = DF17HGVModel()

    # Generate trajectory for carrier strike
    strike_params = StrikeParameters(
        launch_position=np.array([0, 0, 100]),
        target=csg.carrier,
        launch_azimuth_deg=90,
        desired_impact_angle_deg=60,
        salvo_size=1
    )

    trajectory = df17.generate_trajectory(strike_params, time_step_s=5.0)
    prediction = df17.predict_impact(strike_params)

    plot_strike_geometry(strike_params.launch_position, csg.carrier,
                        prediction, trajectory)

    print("\nVisualization complete. Close plot windows to exit.")
    plt.show()

    print("\n" + "=" * 80)
    print("All scenarios complete.")
    print("=" * 80)


if __name__ == "__main__":
    main()
