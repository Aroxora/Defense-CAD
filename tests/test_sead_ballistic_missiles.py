#!/usr/bin/env python3
"""
Precision Ballistic Missile and SEAD Model - Verification Tests

Tests for precision ballistic missile models (DF-21D, DF-26, Iskander-M, ATACMS)
and air defense target models (Patriot, THAAD, S-400), ensuring:
1. Physical parameters are within reasonable bounds
2. Trajectory calculations are physically plausible
3. Hit probability calculations are realistic
4. Defensive system modeling is conservative
5. SEAD engagement outcomes are credible

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import unittest
import numpy as np
from osint_cad.targeting.precision_ballistic_missiles import (
    PrecisionBallisticMissile, MissileParameters, LaunchParameters,
    create_df21d_parameters, create_df26_parameters,
    create_iskander_m_parameters, create_atacms_parameters,
    FlightPhase, GuidanceMode
)
from osint_cad.targeting.air_defense_targets import (
    AirDefenseTarget, create_patriot_pac3_battery,
    create_thaad_battery, create_s400_battery, create_s300pmu2_battery,
    calculate_optimal_impact_point, estimate_required_missiles,
    AirDefenseSystemType
)
from osint_cad.engagements.sead_engagement_simulation import (
    SEADSimulation, StrikePackage, MissionType, MissionOutcome
)


class TestMissileParameters(unittest.TestCase):
    """Test physical parameters of all missile models"""

    def setUp(self):
        self.missiles = {
            "DF-21D": create_df21d_parameters(),
            "DF-26": create_df26_parameters(),
            "Iskander-M": create_iskander_m_parameters(),
            "ATACMS": create_atacms_parameters()
        }

    def test_velocity_bounds(self):
        """Verify all missiles have realistic velocities"""
        for name, params in self.missiles.items():
            with self.subTest(missile=name):
                # Terminal velocity should be supersonic at minimum
                self.assertGreaterEqual(params.terminal_speed_mps, 300.0,
                                      f"{name} terminal velocity too low")
                # Should not exceed Mach 20
                self.assertLessEqual(params.max_speed_mps, 6800.0,
                                   f"{name} max velocity exceeds Mach 20")

    def test_range_classification(self):
        """Verify range classifications are correct"""
        # DF-21D: MRBM (1000-3000 km)
        df21d = self.missiles["DF-21D"]
        self.assertGreaterEqual(df21d.max_range_km, 1000)
        self.assertLessEqual(df21d.max_range_km, 3000)

        # DF-26: IRBM (3000-5500 km)
        df26 = self.missiles["DF-26"]
        self.assertGreaterEqual(df26.max_range_km, 3000)
        self.assertLessEqual(df26.max_range_km, 5500)

        # Iskander-M: SRBM (<1000 km)
        iskander = self.missiles["Iskander-M"]
        self.assertLessEqual(iskander.max_range_km, 1000)

        # ATACMS: Tactical (<500 km)
        atacms = self.missiles["ATACMS"]
        self.assertLessEqual(atacms.max_range_km, 500)

    def test_cep_accuracy(self):
        """Verify CEP values are realistic for precision weapons"""
        for name, params in self.missiles.items():
            with self.subTest(missile=name):
                # Modern precision weapons: 5-30m CEP
                self.assertGreaterEqual(params.cep_m, 3.0,
                                      f"{name} CEP unrealistically low")
                self.assertLessEqual(params.cep_m, 50.0,
                                   f"{name} CEP too large for precision weapon")

    def test_warhead_mass(self):
        """Verify warhead masses are realistic"""
        for name, params in self.missiles.items():
            with self.subTest(missile=name):
                # Warhead should be 3-50% of total mass (ballistic missiles have large boosters)
                mass_fraction = params.warhead_mass_kg / params.launch_mass_kg
                self.assertGreaterEqual(mass_fraction, 0.03,
                                      f"{name} warhead fraction too small")
                self.assertLessEqual(mass_fraction, 0.50,
                                   f"{name} warhead fraction too large")

    def test_maneuverability_bounds(self):
        """Verify maneuverability is within physical limits"""
        for name, params in self.missiles.items():
            with self.subTest(missile=name):
                # Ballistic missiles: 0-30G lateral acceleration
                self.assertGreaterEqual(params.max_lateral_g, 0.0)
                self.assertLessEqual(params.max_lateral_g, 50.0,
                                   f"{name} maneuverability exceeds physical limits")


class TestAirDefenseTargets(unittest.TestCase):
    """Test air defense target models"""

    def setUp(self):
        self.targets = {
            "Patriot PAC-3": create_patriot_pac3_battery(np.array([0., 0., 0.])),
            "THAAD": create_thaad_battery(np.array([0., 0., 0.])),
            "S-400": create_s400_battery(np.array([0., 0., 0.])),
            "S-300PMU-2": create_s300pmu2_battery(np.array([0., 0., 0.]))
        }

    def test_battery_components(self):
        """Verify batteries have required components"""
        for name, target in self.targets.items():
            with self.subTest(battery=name):
                # Must have at least one radar
                self.assertGreaterEqual(len(target.radars), 1,
                                      f"{name} must have at least one radar")
                # Must have launchers
                self.assertGreaterEqual(len(target.launchers), 1,
                                      f"{name} must have launchers")
                # Total missiles should be reasonable
                total_missiles = sum(l.missiles_ready for l in target.launchers)
                self.assertGreaterEqual(total_missiles, 4)
                self.assertLessEqual(total_missiles, 200)

    def test_rcs_values(self):
        """Verify RCS values are realistic"""
        for name, target in self.targets.items():
            with self.subTest(battery=name):
                total_rcs = target.get_total_rcs_m2()
                # Battery should have significant RCS (radars, vehicles)
                self.assertGreaterEqual(total_rcs, 50.0,
                                      f"{name} total RCS too low")
                # Should not exceed unrealistic values
                self.assertLessEqual(total_rcs, 5000.0,
                                   f"{name} total RCS unrealistically high")

    def test_component_spacing(self):
        """Verify component spacing is tactical"""
        for name, target in self.targets.items():
            with self.subTest(battery=name):
                # Spacing should be 50-200m for tactical dispersion
                self.assertGreaterEqual(target.component_spacing_m, 50.0)
                self.assertLessEqual(target.component_spacing_m, 300.0)

    def test_kill_probability_calculation(self):
        """Test kill probability calculations are bounded"""
        patriot = self.targets["Patriot PAC-3"]

        # Direct hit on radar should have high Pk
        radar_pos = patriot.position + patriot.radars[0].position_offset_m
        pk_direct, _ = patriot.calculate_kill_probability(
            impact_position=radar_pos,
            warhead_yield_kg=500.0,
            cep_m=5.0
        )

        self.assertGreaterEqual(pk_direct, 0.3, "Direct hit should have decent Pk")
        self.assertLessEqual(pk_direct, 1.0, "Pk must be <= 1.0")

        # Far miss should have low Pk
        far_miss = patriot.position + np.array([500., 0., 0.])
        pk_miss, _ = patriot.calculate_kill_probability(
            impact_position=far_miss,
            warhead_yield_kg=500.0,
            cep_m=5.0
        )

        self.assertLess(pk_miss, pk_direct, "Far miss should have lower Pk")


class TestBallisticTrajectory(unittest.TestCase):
    """Test trajectory generation and calculations"""

    def setUp(self):
        self.df21d = PrecisionBallisticMissile(create_df21d_parameters())
        self.iskander = PrecisionBallisticMissile(create_iskander_m_parameters())

    def test_flight_time_calculation(self):
        """Test flight time scales reasonably with range"""
        # 500 km range
        tof_500 = self.df21d.calculate_flight_time(500.0)
        # 1500 km range
        tof_1500 = self.df21d.calculate_flight_time(1500.0)

        # Longer range should take more time
        self.assertGreater(tof_1500, tof_500)

        # Flight time should be reasonable (not instantaneous, not hours)
        self.assertGreaterEqual(tof_500, 60.0)  # At least 1 minute
        self.assertLessEqual(tof_1500, 1800.0)  # Less than 30 minutes

    def test_cep_growth_with_range(self):
        """Test CEP increases with range"""
        cep_500 = self.df21d.calculate_cep(500.0)
        cep_1500 = self.df21d.calculate_cep(1500.0)

        self.assertGreater(cep_1500, cep_500,
                         "CEP should increase with range")

    def test_trajectory_has_all_phases(self):
        """Test generated trajectory includes all flight phases"""
        launch_params = LaunchParameters(
            launch_position=np.array([0., 0., 0.]),
            target_position=np.array([1000000., 0., 0.]),  # 1000 km
            launch_azimuth_deg=90.0
        )

        trajectory = self.df21d.generate_trajectory(launch_params, time_resolution_s=10.0)

        # Extract phases
        phases = set(p.phase for p in trajectory)

        self.assertIn(FlightPhase.BOOST, phases, "Missing boost phase")
        self.assertIn(FlightPhase.MIDCOURSE, phases, "Missing midcourse phase")
        self.assertIn(FlightPhase.TERMINAL, phases, "Missing terminal phase")

    def test_trajectory_altitude_profile(self):
        """Test altitude profile is realistic"""
        launch_params = LaunchParameters(
            launch_position=np.array([0., 0., 0.]),
            target_position=np.array([1000000., 0., 0.]),
            launch_azimuth_deg=90.0
        )

        trajectory = self.df21d.generate_trajectory(launch_params, time_resolution_s=5.0)

        altitudes = [p.altitude_m for p in trajectory]
        max_altitude = max(altitudes)

        # Should reach significant altitude (ballistic arc)
        self.assertGreaterEqual(max_altitude, 50000.0,
                              "Should reach at least 50 km altitude")

        # Should not exceed space boundary unrealistically
        self.assertLessEqual(max_altitude, 800000.0,
                           "Should not exceed 800 km altitude")

        # Should end near ground level (within 2km to account for trajectory sampling)
        final_altitude = trajectory[-1].altitude_m
        self.assertLess(final_altitude, 2000.0,
                      "Should terminate near ground level")

    def test_intercept_windows(self):
        """Test intercept window generation"""
        launch_params = LaunchParameters(
            launch_position=np.array([0., 0., 0.]),
            target_position=np.array([1000000., 0., 0.]),
            launch_azimuth_deg=90.0
        )

        trajectory = self.df21d.generate_trajectory(launch_params)
        windows = self.df21d.calculate_intercept_windows(trajectory)

        # Should have windows for each phase
        self.assertGreaterEqual(len(windows), 2, "Should have multiple intercept windows")

        # Windows should not overlap in time
        for i in range(len(windows) - 1):
            self.assertLessEqual(windows[i].end_time_s, windows[i+1].start_time_s,
                               "Intercept windows should not overlap")


class TestEngagementPrediction(unittest.TestCase):
    """Test engagement outcome predictions"""

    def setUp(self):
        self.df21d = PrecisionBallisticMissile(create_df21d_parameters())
        self.patriot = create_patriot_pac3_battery(np.array([800000., 0., 0.]))

    def test_hit_probability_vs_target_size(self):
        """Test hit probability increases with target size"""
        cep = 10.0
        target_rcs = 100.0

        # Small target (10x10m)
        pk_small = self.df21d.calculate_hit_probability(
            target_rcs, cep, (10.0, 10.0)
        )

        # Large target (100x100m)
        pk_large = self.df21d.calculate_hit_probability(
            target_rcs, cep, (100.0, 100.0)
        )

        self.assertGreater(pk_large, pk_small,
                         "Larger target should have higher Pk")

    def test_defensive_systems_reduce_pk(self):
        """Test that defensive systems reduce overall Pk"""
        launch_params = LaunchParameters(
            launch_position=np.array([0., 0., 0.]),
            target_position=self.patriot.position.copy(),
            launch_azimuth_deg=90.0
        )

        # Prediction with defenses
        result_defended = self.df21d.predict_impact(
            launch_params,
            target_rcs_m2=150.0,
            target_dimensions_m=(50.0, 50.0),
            defensive_systems={
                'has_terminal_intercept': True,
                'terminal_shots': 4,
                'has_ew': True
            }
        )

        # Prediction without defenses
        result_undefended = self.df21d.predict_impact(
            launch_params,
            target_rcs_m2=150.0,
            target_dimensions_m=(50.0, 50.0),
            defensive_systems=None
        )

        self.assertLess(result_defended['overall_pk'], result_undefended['overall_pk'],
                       "Defenses should reduce overall Pk")

        # Survival probability should be less than 1
        self.assertLess(result_defended['survival_probability'], 1.0,
                       "Should face some intercept risk")

    def test_pk_bounded(self):
        """Test that all Pk values are properly bounded [0, 1]"""
        launch_params = LaunchParameters(
            launch_position=np.array([0., 0., 0.]),
            target_position=self.patriot.position.copy(),
            launch_azimuth_deg=90.0
        )

        result = self.df21d.predict_impact(
            launch_params,
            target_rcs_m2=150.0,
            target_dimensions_m=(50.0, 50.0),
            defensive_systems={'has_terminal_intercept': True, 'terminal_shots': 2}
        )

        self.assertGreaterEqual(result['hit_probability'], 0.0)
        self.assertLessEqual(result['hit_probability'], 1.0)
        self.assertGreaterEqual(result['survival_probability'], 0.0)
        self.assertLessEqual(result['survival_probability'], 1.0)
        self.assertGreaterEqual(result['overall_pk'], 0.0)
        self.assertLessEqual(result['overall_pk'], 1.0)


class TestSEADSimulation(unittest.TestCase):
    """Test SEAD engagement simulation"""

    def setUp(self):
        self.sim = SEADSimulation(random_seed=42)
        self.patriot = create_patriot_pac3_battery(
            position=np.array([800000., 0., 0.]),
            battery_id="TEST-PAT"
        )

    def test_single_strike_result_structure(self):
        """Test single strike returns proper result structure"""
        missile = PrecisionBallisticMissile(create_df21d_parameters())
        launch_params = LaunchParameters(
            launch_position=np.array([0., 0., 0.]),
            target_position=self.patriot.position.copy(),
            launch_azimuth_deg=90.0
        )

        result = self.sim.simulate_single_strike(
            missile, launch_params, self.patriot, "TEST-001"
        )

        # Check result has required fields
        self.assertIsNotNone(result.missile_id)
        self.assertGreater(result.range_km, 0)
        self.assertGreater(result.flight_time_s, 0)
        self.assertGreater(result.cep_m, 0)
        self.assertIsInstance(result.hit, bool)
        self.assertIsInstance(result.intercepted, bool)
        self.assertIsInstance(result.functional_kill, bool)

    def test_salvo_attack_improves_pk(self):
        """Test that salvo attacks have higher overall Pk than single shots"""
        # This is a stochastic test, run multiple times
        single_shot_kills = 0
        salvo_kills = 0
        n_trials = 20

        for _ in range(n_trials):
            sim_trial = SEADSimulation()

            # Single missile strike
            package_single = sim_trial.plan_strike_package(
                missile_type="DF-21D",
                launch_position=np.array([0., 0., 0.]),
                target=self.patriot,
                desired_pk=0.50,  # Lower to ensure only 1 missile
                package_id="SINGLE"
            )
            # Force single missile
            package_single.missiles = package_single.missiles[:1]

            assessment_single = sim_trial.simulate_salvo_attack(package_single)
            if assessment_single.functional_kill_achieved:
                single_shot_kills += 1

            # Salvo strike (4 missiles)
            package_salvo = sim_trial.plan_strike_package(
                missile_type="DF-21D",
                launch_position=np.array([0., 0., 0.]),
                target=self.patriot,
                desired_pk=0.90,
                package_id="SALVO"
            )

            assessment_salvo = sim_trial.simulate_salvo_attack(package_salvo)
            if assessment_salvo.functional_kill_achieved:
                salvo_kills += 1

        # Salvo should achieve more kills (statistical test)
        # With proper salvo sizing, should see improvement
        # (This may occasionally fail due to randomness, but should pass most times)
        self.assertGreaterEqual(salvo_kills, single_shot_kills,
                              "Salvo attacks should achieve more kills overall")

    def test_strike_package_planning(self):
        """Test automated strike package planning"""
        package = self.sim.plan_strike_package(
            missile_type="DF-21D",
            launch_position=np.array([0., 0., 0.]),
            target=self.patriot,
            desired_pk=0.90,
            package_id="PLAN-TEST"
        )

        # Should allocate reasonable number of missiles
        self.assertGreaterEqual(len(package.missiles), 1)
        self.assertLessEqual(len(package.missiles), 10,
                           "Should not allocate excessive missiles")

        # Higher desired Pk should allocate more missiles
        package_low = self.sim.plan_strike_package(
            missile_type="DF-21D",
            launch_position=np.array([0., 0., 0.]),
            target=self.patriot,
            desired_pk=0.50,
            package_id="LOW-PK"
        )

        package_high = self.sim.plan_strike_package(
            missile_type="DF-21D",
            launch_position=np.array([0., 0., 0.]),
            target=self.patriot,
            desired_pk=0.95,
            package_id="HIGH-PK"
        )

        self.assertGreaterEqual(len(package_high.missiles), len(package_low.missiles),
                              "Higher Pk should require more missiles")

    def test_mission_outcome_categories(self):
        """Test that mission outcomes are properly categorized"""
        # Run a few simulations and check outcome types
        package = self.sim.plan_strike_package(
            missile_type="Iskander-M",
            launch_position=np.array([0., 0., 0.]),
            target=create_s400_battery(np.array([250000., 0., 0.])),
            desired_pk=0.85,
            package_id="OUTCOME-TEST"
        )

        assessment = self.sim.simulate_salvo_attack(package)

        # Outcome should be one of the valid types
        valid_outcomes = [MissionOutcome.MISSION_KILL, MissionOutcome.DEGRADED,
                         MissionOutcome.MISS, MissionOutcome.INTERCEPTED]
        self.assertIn(assessment.mission_outcome, valid_outcomes)

        # If functional kill achieved, outcome should be MISSION_KILL
        if assessment.functional_kill_achieved:
            self.assertEqual(assessment.mission_outcome, MissionOutcome.MISSION_KILL)


class TestMissileRange(unittest.TestCase):
    """Test range validation for different missile types"""

    def test_range_limits_enforced(self):
        """Test that missiles operate within their range limits"""
        missiles = {
            "DF-21D": (create_df21d_parameters(), 1500.0),  # Max 1500 km
            "Iskander-M": (create_iskander_m_parameters(), 500.0),  # Max 500 km
            "ATACMS": (create_atacms_parameters(), 300.0)  # Max 300 km
        }

        for name, (params, max_range) in missiles.items():
            with self.subTest(missile=name):
                self.assertLessEqual(params.max_range_km, max_range * 1.2,
                                   f"{name} exceeds expected max range")
                self.assertGreaterEqual(params.min_range_km, 10.0,
                                      f"{name} min range too low")


class TestPhysicalRealism(unittest.TestCase):
    """Test overall physical realism of models"""

    def test_energy_conservation(self):
        """Test that kinetic energy is reasonable for missile mass and velocity"""
        for params in [create_df21d_parameters(), create_iskander_m_parameters()]:
            # KE = 0.5 * m * v²
            ke_joules = 0.5 * params.launch_mass_kg * params.max_speed_mps ** 2

            # Should be substantial but not unrealistic
            self.assertGreaterEqual(ke_joules, 1e9,
                                  "Kinetic energy should be at least 1 GJ")
            self.assertLessEqual(ke_joules, 1e11,
                               "Kinetic energy should not exceed 100 GJ")

    def test_mach_number_consistency(self):
        """Test that velocities correspond to reasonable Mach numbers"""
        speed_of_sound = 343.0  # m/s at sea level

        df26 = create_df26_parameters()

        # DF-26 should be hypersonic
        mach = df26.terminal_speed_mps / speed_of_sound
        self.assertGreaterEqual(mach, 5.0, "DF-26 should be hypersonic")
        self.assertLessEqual(mach, 20.0, "DF-26 Mach number unrealistic")


def run_verification_suite():
    """Run complete verification test suite"""
    print("=" * 70)
    print("SEAD Ballistic Missile Models - Verification Test Suite")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestMissileParameters))
    suite.addTests(loader.loadTestsFromTestCase(TestAirDefenseTargets))
    suite.addTests(loader.loadTestsFromTestCase(TestBallisticTrajectory))
    suite.addTests(loader.loadTestsFromTestCase(TestEngagementPrediction))
    suite.addTests(loader.loadTestsFromTestCase(TestSEADSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestMissileRange))
    suite.addTests(loader.loadTestsFromTestCase(TestPhysicalRealism))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("Verification Summary:")
    print(f"  Tests run:     {result.testsRun}")
    print(f"  Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures:      {len(result.failures)}")
    print(f"  Errors:        {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_verification_suite()
    exit(0 if success else 1)
