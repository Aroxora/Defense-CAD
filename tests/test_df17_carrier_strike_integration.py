#!/usr/bin/env python3
"""
DF-17 HGV Carrier Strike Group Integration Tests

Comprehensive integration tests that validate realistic ASBM scenarios
against carrier strike groups, including:
1. Full CSG formations
2. Multi-missile salvo attacks
3. Defensive system effectiveness
4. Mission success criteria

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import unittest
import numpy as np
from osint_cad.targeting.df17_hgv_model import (
    DF17HGVModel, DF17Parameters, SurfaceTarget, StrikeParameters,
    create_cvn_carrier, create_ddg_destroyer, create_cg_cruiser, create_fujian_carrier
)
from osint_cad.engagements.df17_engagement_simulation import CarrierStrikeGroup, DF17EngagementScenario


class TestCarrierStrikeGroupIntegration(unittest.TestCase):
    """Integration tests for DF-17 vs carrier strike groups"""

    def setUp(self):
        """Set up test scenario"""
        self.launch_position = np.array([0, 0, 100])
        self.csg_position = np.array([2000000, 0, 0])  # 2000 km
        self.csg = CarrierStrikeGroup(self.csg_position, heading_deg=270)

    def test_carrier_strike_group_formation(self):
        """Test CSG formation is realistic"""
        ships = self.csg.get_all_ships()

        # Should have 5 ships: 1 carrier, 2 cruisers, 2 destroyers
        self.assertEqual(len(ships), 5, "CSG should have 5 ships")

        # Verify ship types
        ship_types = [ship.target_type for ship in ships]
        self.assertIn("carrier", ship_types, "Should have carrier")
        self.assertEqual(ship_types.count("cruiser"), 2, "Should have 2 cruisers")
        self.assertEqual(ship_types.count("destroyer"), 2, "Should have 2 destroyers")

        # Verify all ships have defenses
        for ship in ships:
            if ship.target_type in ["carrier", "cruiser", "destroyer"]:
                self.assertTrue(ship.has_aegis, f"{ship.target_id} should have Aegis")
                self.assertTrue(ship.has_ciws, f"{ship.target_id} should have CIWS")

    def test_single_missile_vs_carrier(self):
        """Test single DF-17 strike against carrier"""
        scenario = DF17EngagementScenario()

        prediction = scenario.execute_single_strike(
            self.launch_position,
            self.csg.carrier,
            verbose=False
        )

        # Should be within range
        self.assertTrue(prediction.impact_possible, "Strike should be possible")

        # Pk should be reduced by defenses but non-zero
        self.assertGreater(prediction.probability_hit, 0.0, "Should have some hit probability")
        self.assertLess(prediction.probability_hit, 1.0, "Defenses should reduce Pk")

        # Should be hypersonic at impact
        impact_mach = prediction.impact_velocity_ms / 340.0
        self.assertGreaterEqual(impact_mach, 5.0, "Should be hypersonic at impact")

    def test_salvo_attack_vs_carrier(self):
        """Test multi-missile salvo against carrier"""
        scenario = DF17EngagementScenario()

        salvo_size = 6
        overall_pk, predictions = scenario.execute_salvo_strike(
            self.launch_position,
            self.csg.carrier,
            salvo_size=salvo_size,
            verbose=False
        )

        # Should have correct number of missiles
        self.assertEqual(len(predictions), salvo_size, "Should have all missiles")

        # Salvo Pk should be higher than single missile Pk
        single_pk = predictions[0].probability_hit
        self.assertGreater(overall_pk, single_pk, "Salvo Pk should exceed single Pk")

        # Salvo should have reasonable chance of success
        self.assertGreater(overall_pk, 0.5, "6-missile salvo should have >50% Pk vs carrier")

    def test_multi_target_engagement(self):
        """Test engagement of multiple CSG ships"""
        scenario = DF17EngagementScenario()

        # Attack carrier and two escorts
        targets = [
            self.csg.carrier,
            self.csg.cruiser1,
            self.csg.destroyer1
        ]

        predictions = []
        for target in targets:
            pred = scenario.execute_single_strike(
                self.launch_position,
                target,
                verbose=False
            )
            predictions.append(pred)

        # All should be within range
        for pred in predictions:
            self.assertTrue(pred.impact_possible, "All ships should be within range")

        # Should have fired 3 missiles
        self.assertEqual(len(scenario.missiles_fired), 3, "Should have 3 missiles")

    def test_defensive_systems_effectiveness(self):
        """Test that Aegis/SM-6 defenses significantly reduce Pk"""
        # Carrier with full defenses
        carrier_defended = create_cvn_carrier()
        carrier_defended.position = self.csg_position

        # Same target but without defenses (for comparison)
        carrier_undefended = create_cvn_carrier()
        carrier_undefended.position = self.csg_position
        carrier_undefended.has_aegis = False
        carrier_undefended.has_sm6 = False
        carrier_undefended.has_sm3 = False
        carrier_undefended.has_ciws = False

        df17 = DF17HGVModel()

        strike_defended = StrikeParameters(
            launch_position=self.launch_position,
            target=carrier_defended,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        strike_undefended = StrikeParameters(
            launch_position=self.launch_position,
            target=carrier_undefended,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        pred_defended = df17.predict_impact(strike_defended)
        pred_undefended = df17.predict_impact(strike_undefended)

        # Defenses should reduce Pk by at least 40%
        reduction = 1 - (pred_defended.probability_hit / pred_undefended.probability_hit)
        self.assertGreater(reduction, 0.4, "Defenses should reduce Pk by >40%")

    def test_saturation_attack_effectiveness(self):
        """Test that saturation attack (many missiles) overwhelms defenses"""
        df17 = DF17HGVModel()

        # Small salvo (2 missiles)
        strike_small = StrikeParameters(
            launch_position=self.launch_position,
            target=self.csg.carrier,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=2
        )

        # Large salvo (10 missiles)
        strike_large = StrikeParameters(
            launch_position=self.launch_position,
            target=self.csg.carrier,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=10
        )

        pk_small, _ = df17.calculate_salvo_effectiveness(strike_small)
        pk_large, _ = df17.calculate_salvo_effectiveness(strike_large)

        # Large salvo should have significantly higher Pk
        self.assertGreater(pk_large, pk_small, "Larger salvo should have higher Pk")

        # 10-missile salvo should have very high Pk
        self.assertGreater(pk_large, 0.8, "10-missile salvo should have >80% Pk")

    def test_range_limitations(self):
        """Test that targets beyond range are correctly identified"""
        df17 = DF17HGVModel()

        # Target beyond max range (3500 km)
        target_far = create_cvn_carrier()
        target_far.position = np.array([3500000, 0, 0])

        strike_far = StrikeParameters(
            launch_position=self.launch_position,
            target=target_far,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = df17.predict_impact(strike_far)

        # Should be beyond range
        self.assertFalse(prediction.impact_possible, "Should be beyond max range")

    def test_moving_csg_engagement(self):
        """Test engagement of moving carrier strike group"""
        df17 = DF17HGVModel()

        # Carrier moving at 30 knots (~15 m/s)
        moving_carrier = create_cvn_carrier()
        moving_carrier.position = self.csg_position
        moving_carrier.velocity = np.array([15, 0, 0])  # Moving east

        strike = StrikeParameters(
            launch_position=self.launch_position,
            target=moving_carrier,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = df17.predict_impact(strike)

        # Should predict lead on moving target
        self.assertTrue(prediction.impact_possible, "Should engage moving target")

        # Impact point should be ahead of current position
        self.assertGreater(prediction.impact_point[0], moving_carrier.position[0],
                          "Should predict lead on moving target")

    def test_fujian_carrier_strike(self):
        """Test DF-17 strike against Chinese Type 003 Fujian carrier

        Validates ASBM engagement against Fujian (commissioned Nov 2025).
        Tests different defensive characteristics compared to US CVN.

        Classification: UNCLASSIFIED // PUBLIC RELEASE
        Confidence: 65% (based on public specifications)
        """
        scenario = DF17EngagementScenario()

        # Create Fujian carrier at 1800km range
        fujian = create_fujian_carrier()
        fujian.position = np.array([1800000, 0, 0])  # 1800 km east

        # Single missile strike
        prediction_single = scenario.execute_single_strike(
            self.launch_position,
            fujian,
            verbose=False
        )

        # Should be within range
        self.assertTrue(prediction_single.impact_possible, "Strike should be possible")

        # Fujian has different defenses (HHQ-10/16, Type 1130 CIWS)
        # Pk should reflect this (no Aegis/SM-6)
        self.assertGreater(prediction_single.probability_hit, 0.0,
                          "Should have some hit probability")

        # Salvo attack test
        salvo_size = 6
        overall_pk, predictions = scenario.execute_salvo_strike(
            self.launch_position,
            fujian,
            salvo_size=salvo_size,
            verbose=False
        )

        # Salvo should have higher Pk than single missile
        self.assertGreater(overall_pk, prediction_single.probability_hit,
                          "Salvo should increase overall Pk")

        # Should be hypersonic at impact
        impact_mach = prediction_single.impact_velocity_ms / 340.0
        self.assertGreaterEqual(impact_mach, 5.0, "Should be hypersonic at impact")

        # Verify carrier characteristics match specifications
        self.assertEqual(fujian.target_id, "CV-18-FUJIAN",
                        "Should have correct designation")
        self.assertEqual(fujian.length_m, 316, "Should match public specs (316m)")
        self.assertEqual(fujian.beam_m, 76, "Should match public specs (76m)")
        self.assertFalse(fujian.has_aegis, "Fujian does not have Aegis system")
        self.assertFalse(fujian.has_sm6, "Fujian uses HHQ-16 instead of SM-6")
        self.assertTrue(fujian.has_ciws, "Fujian has Type 1130 CIWS")

        # IR signature should be lower than nuclear carriers (conventional propulsion)
        cvn = create_cvn_carrier()
        self.assertLess(fujian.ir_signature_kw, cvn.ir_signature_kw,
                       "Conventional carrier should have lower IR than nuclear")


class TestMissionRealism(unittest.TestCase):
    """Test realistic mission scenarios"""

    def test_coordinated_strike_mission(self):
        """Test coordinated multi-target strike mission"""
        launch_position = np.array([0, 0, 100])
        csg_position = np.array([2000000, 0, 0])
        csg = CarrierStrikeGroup(csg_position, heading_deg=270)

        scenario = DF17EngagementScenario()

        # Mission: Disable CSG with minimum missiles
        # Primary: 6x missiles vs carrier
        # Secondary: 2x missiles each vs 2 escorts

        # Primary strike
        pk_carrier, _ = scenario.execute_salvo_strike(
            launch_position, csg.carrier, salvo_size=6, verbose=False)

        # Secondary strikes
        pk_cruiser, _ = scenario.execute_salvo_strike(
            launch_position, csg.cruiser1, salvo_size=2, verbose=False)

        pk_destroyer, _ = scenario.execute_salvo_strike(
            launch_position, csg.destroyer1, salvo_size=2, verbose=False)

        # Total: 10 missiles
        total_missiles = len(scenario.missiles_fired)
        self.assertEqual(total_missiles, 10, "Should fire 10 total missiles")

        # Carrier strike should have high Pk
        self.assertGreater(pk_carrier, 0.5, "Carrier strike should have >50% Pk")

    def test_flight_time_vs_range(self):
        """Test that flight time scales appropriately with range"""
        df17 = DF17HGVModel()
        launch_position = np.array([0, 0, 100])

        ranges_km = [1500, 2000, 2500]
        flight_times = []

        for range_km in ranges_km:
            target = create_cvn_carrier()
            target.position = np.array([range_km * 1000, 0, 0])

            strike = StrikeParameters(
                launch_position=launch_position,
                target=target,
                launch_azimuth_deg=90,
                desired_impact_angle_deg=60,
                salvo_size=1
            )

            prediction = df17.predict_impact(strike)
            flight_times.append(prediction.time_to_impact_s)

        # Flight time should increase with range
        self.assertGreater(flight_times[1], flight_times[0],
                          "Flight time should increase with range")
        self.assertGreater(flight_times[2], flight_times[1],
                          "Flight time should increase with range")

    def test_physical_plausibility(self):
        """Test overall physical plausibility of scenarios"""
        df17 = DF17HGVModel()
        launch_position = np.array([0, 0, 100])

        target = create_cvn_carrier()
        target.position = np.array([2000000, 0, 0])  # 2000 km

        strike = StrikeParameters(
            launch_position=launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = df17.predict_impact(strike)
        trajectory = df17.generate_trajectory(strike, time_step_s=5.0)

        # Check trajectory has all phases
        from osint_cad.targeting.df17_hgv_model import HGVFlightPhase
        phases = set(p.phase for p in trajectory)
        self.assertIn(HGVFlightPhase.BOOST, phases, "Should have boost phase")
        self.assertIn(HGVFlightPhase.GLIDE, phases, "Should have glide phase")
        self.assertIn(HGVFlightPhase.TERMINAL, phases, "Should have terminal phase")

        # Check altitude profile is realistic
        max_alt = max(p.altitude_m for p in trajectory)
        self.assertGreater(max_alt, 40000, "Should reach >40km altitude")
        self.assertLess(max_alt, 100000, "Should stay <100km altitude")

        # Check all velocities are hypersonic
        for point in trajectory:
            self.assertGreaterEqual(point.mach_number, 5.0,
                                   "Should maintain hypersonic speed")


def run_integration_suite():
    """Run complete integration test suite"""
    print("=" * 70)
    print("DF-17 HGV Carrier Strike Group - Integration Test Suite")
    print("=" * 70)
    print("\nValidating realistic ASBM scenarios against carrier strike groups...")
    print()

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCarrierStrikeGroupIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestMissionRealism))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("Integration Test Summary:")
    print(f"  Tests run:     {result.testsRun}")
    print(f"  Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures:      {len(result.failures)}")
    print(f"  Errors:        {len(result.errors)}")
    print("=" * 70)

    if result.wasSuccessful():
        print("\n✅ All ASBM vs carrier strike group scenarios validated")
        print("\nKey validations:")
        print("  ✓ Carrier strike group formations are realistic")
        print("  ✓ Single missile strikes are physically plausible")
        print("  ✓ Salvo attacks have appropriate effectiveness")
        print("  ✓ Defensive systems significantly reduce Pk")
        print("  ✓ Saturation attacks overwhelm defenses")
        print("  ✓ Moving target engagement works correctly")
        print("  ✓ Coordinated multi-target missions are feasible")
        print("  ✓ Flight times and trajectories are realistic")
        print("\nUSEFUL CAD Contribution:")
        print("  - Validates ASBM threat to carrier strike groups")
        print("  - Informs defensive tactics for CSG protection")
        print("  - Provides actionable intelligence for BMD deployment")
        print("  - Complements air-to-air CAD scenarios")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_suite()
    exit(0 if success else 1)
