#!/usr/bin/env python3
"""
DF-17 Hypersonic Glide Vehicle Model - Verification Tests

Tests for DF-17 HGV targeting model accuracy, ensuring:
1. Physical parameters are within reasonable bounds
2. Trajectory calculations are physically plausible
3. Hit probability calculations are realistic
4. Defensive system modeling is conservative

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import unittest
import numpy as np
from df17_hgv_model import (
    DF17HGVModel, DF17Parameters, SurfaceTarget, StrikeParameters,
    create_cvn_carrier, create_ddg_destroyer, create_land_target,
    InterceptPrediction
)


class TestDF17Parameters(unittest.TestCase):
    """Test DF-17 physical parameters"""

    def setUp(self):
        self.params = DF17Parameters()

    def test_velocity_bounds(self):
        """Verify velocities are within hypersonic regime (Mach 5+)"""
        # Hypersonic is Mach 5+ (~1700 m/s at sea level)
        self.assertGreaterEqual(self.params.peak_velocity_ms, 1700,
                               "Peak velocity should be hypersonic (>Mach 5)")
        self.assertLessEqual(self.params.peak_velocity_ms, 4000,
                            "Peak velocity should not exceed Mach 12")

        self.assertGreaterEqual(self.params.terminal_velocity_ms, 1700,
                               "Terminal velocity should be hypersonic")

    def test_range_bounds(self):
        """Verify range is consistent with MRBM classification"""
        # Medium-range ballistic missile: 1000-3000 km
        self.assertGreaterEqual(self.params.max_range_km, 1500,
                               "Max range should be at least 1500 km")
        self.assertLessEqual(self.params.max_range_km, 3000,
                            "Max range should not exceed 3000 km (MRBM)")

    def test_cep_accuracy(self):
        """Verify CEP is realistic for precision-guided HGV"""
        # Modern precision weapons: 5-20m CEP
        self.assertGreaterEqual(self.params.cep_meters, 5,
                               "CEP should be at least 5m")
        self.assertLessEqual(self.params.cep_meters, 20,
                            "CEP should not be better than 5m (too optimistic)")

    def test_maneuverability(self):
        """Verify maneuverability is within physical limits"""
        # HGV can maneuver but not like air-breathing missiles
        self.assertLessEqual(self.params.max_glide_acceleration_g, 30,
                            "Glide acceleration should not exceed 30G")
        self.assertGreaterEqual(self.params.max_glide_acceleration_g, 10,
                               "Glide acceleration should be at least 10G")

    def test_kinetic_energy(self):
        """Verify kinetic energy is physically plausible"""
        # 1000 kg at Mach 5+ should have substantial KE
        ke_mj = self.params.kinetic_energy_mj
        self.assertGreaterEqual(ke_mj, 1000,
                               "Kinetic energy should be at least 1 GJ")
        self.assertLessEqual(ke_mj, 10000,
                            "Kinetic energy should be less than 10 GJ")


class TestDF17Targeting(unittest.TestCase):
    """Test DF-17 targeting calculations"""

    def setUp(self):
        self.df17 = DF17HGVModel()
        self.launch_position = np.array([0, 0, 100])

    def test_target_within_range(self):
        """Test engagement of target within range"""
        target = create_cvn_carrier()
        target.position = np.array([2000000, 0, 0])  # 2000 km

        strike_params = StrikeParameters(
            launch_position=self.launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = self.df17.predict_impact(strike_params)

        self.assertTrue(prediction.impact_possible,
                       "Impact should be possible at 2000 km")
        self.assertGreater(prediction.probability_hit, 0.0,
                          "Pk should be greater than 0")
        self.assertLess(prediction.probability_hit, 1.0,
                       "Pk should be less than 1 (defenses present)")

    def test_target_too_far(self):
        """Test target beyond maximum range"""
        target = create_land_target()
        target.position = np.array([3000000, 0, 0])  # 3000 km (beyond max)

        strike_params = StrikeParameters(
            launch_position=self.launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = self.df17.predict_impact(strike_params)

        self.assertFalse(prediction.impact_possible,
                        "Impact should not be possible beyond max range")

    def test_target_too_close(self):
        """Test target below minimum range"""
        target = create_land_target()
        target.position = np.array([500000, 0, 0])  # 500 km (below min)

        strike_params = StrikeParameters(
            launch_position=self.launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = self.df17.predict_impact(strike_params)

        self.assertFalse(prediction.impact_possible,
                        "Impact should not be possible below min range")

    def test_moving_target_prediction(self):
        """Test prediction accounts for target motion"""
        target = create_cvn_carrier()
        target.position = np.array([2000000, 0, 0])
        target.velocity = np.array([15, 0, 0])  # 30 knots

        strike_params = StrikeParameters(
            launch_position=self.launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = self.df17.predict_impact(strike_params)

        # Impact point should be ahead of current position
        self.assertNotEqual(prediction.impact_point[0], target.position[0],
                          "Impact point should account for target motion")

        # Impact point should be downrange from current target position
        self.assertGreater(prediction.impact_point[0], target.position[0],
                          "Impact point should be ahead of moving target")

    def test_cep_growth_with_range(self):
        """Test that CEP grows with range (accumulated errors)"""
        target1 = create_land_target()
        target1.position = np.array([1500000, 0, 0])  # 1500 km

        target2 = create_land_target()
        target2.position = np.array([2500000, 0, 0])  # 2500 km

        strike1 = StrikeParameters(
            launch_position=self.launch_position,
            target=target1,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        strike2 = StrikeParameters(
            launch_position=self.launch_position,
            target=target2,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        pred1 = self.df17.predict_impact(strike1)
        pred2 = self.df17.predict_impact(strike2)

        self.assertGreater(pred2.cep_at_impact_m, pred1.cep_at_impact_m,
                          "CEP should grow with range")


class TestDefensiveSystems(unittest.TestCase):
    """Test defensive system effectiveness modeling"""

    def setUp(self):
        self.df17 = DF17HGVModel()
        self.launch_position = np.array([0, 0, 100])

    def test_carrier_defenses_reduce_pk(self):
        """Test that carrier defenses significantly reduce Pk"""
        # Carrier with full defenses
        carrier_defended = create_cvn_carrier()
        carrier_defended.position = np.array([2000000, 0, 0])

        # Land target with no defenses
        land_target = create_land_target()
        land_target.position = np.array([2000000, 0, 0])

        strike_defended = StrikeParameters(
            launch_position=self.launch_position,
            target=carrier_defended,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        strike_undefended = StrikeParameters(
            launch_position=self.launch_position,
            target=land_target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        pred_defended = self.df17.predict_impact(strike_defended)
        pred_undefended = self.df17.predict_impact(strike_undefended)

        self.assertLess(pred_defended.probability_hit, pred_undefended.probability_hit,
                       "Defended target should have lower Pk")

        # Defenses should reduce Pk by at least 30%
        reduction_factor = pred_defended.probability_hit / pred_undefended.probability_hit
        self.assertLess(reduction_factor, 0.7,
                       "Defensive systems should reduce Pk by at least 30%")

    def test_aegis_system_effectiveness(self):
        """Test Aegis-equipped ships have lower vulnerability"""
        destroyer_with_aegis = create_ddg_destroyer()
        destroyer_with_aegis.position = np.array([2000000, 0, 0])

        destroyer_no_aegis = create_ddg_destroyer()
        destroyer_no_aegis.position = np.array([2000000, 0, 0])
        destroyer_no_aegis.has_aegis = False
        destroyer_no_aegis.has_sm6 = False
        destroyer_no_aegis.has_sm3 = False

        strike_with_aegis = StrikeParameters(
            launch_position=self.launch_position,
            target=destroyer_with_aegis,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        strike_no_aegis = StrikeParameters(
            launch_position=self.launch_position,
            target=destroyer_no_aegis,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        pred_with_aegis = self.df17.predict_impact(strike_with_aegis)
        pred_no_aegis = self.df17.predict_impact(strike_no_aegis)

        self.assertLess(pred_with_aegis.probability_hit, pred_no_aegis.probability_hit,
                       "Aegis should reduce Pk")


class TestSalvoEffectiveness(unittest.TestCase):
    """Test salvo attack calculations"""

    def setUp(self):
        self.df17 = DF17HGVModel()
        self.launch_position = np.array([0, 0, 100])

    def test_salvo_pk_greater_than_single(self):
        """Test that salvo Pk is greater than single missile Pk"""
        target = create_cvn_carrier()
        target.position = np.array([2000000, 0, 0])

        strike_params = StrikeParameters(
            launch_position=self.launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=4
        )

        overall_pk, individual_preds = self.df17.calculate_salvo_effectiveness(strike_params)

        single_pk = individual_preds[0].probability_hit

        self.assertGreater(overall_pk, single_pk,
                          "Salvo Pk should be greater than single missile Pk")

    def test_salvo_pk_bounded(self):
        """Test that salvo Pk is properly bounded [0, 1]"""
        target = create_land_target()
        target.position = np.array([2000000, 0, 0])

        strike_params = StrikeParameters(
            launch_position=self.launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=10
        )

        overall_pk, _ = self.df17.calculate_salvo_effectiveness(strike_params)

        self.assertGreaterEqual(overall_pk, 0.0, "Pk should be >= 0")
        self.assertLessEqual(overall_pk, 1.0, "Pk should be <= 1")


class TestTrajectoryGeneration(unittest.TestCase):
    """Test trajectory generation"""

    def setUp(self):
        self.df17 = DF17HGVModel()
        self.launch_position = np.array([0, 0, 100])

    def test_trajectory_phases(self):
        """Test trajectory includes all flight phases"""
        target = create_cvn_carrier()
        target.position = np.array([2000000, 0, 0])

        strike_params = StrikeParameters(
            launch_position=self.launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        trajectory = self.df17.generate_trajectory(strike_params, time_step_s=5.0)

        # Check all phases are present
        phases_present = set(p.phase for p in trajectory)
        from df17_hgv_model import HGVFlightPhase

        self.assertIn(HGVFlightPhase.BOOST, phases_present,
                     "Trajectory should include boost phase")
        self.assertIn(HGVFlightPhase.GLIDE, phases_present,
                     "Trajectory should include glide phase")
        self.assertIn(HGVFlightPhase.TERMINAL, phases_present,
                     "Trajectory should include terminal phase")

    def test_trajectory_altitude_profile(self):
        """Test trajectory altitude profile is realistic"""
        target = create_cvn_carrier()
        target.position = np.array([2000000, 0, 0])

        strike_params = StrikeParameters(
            launch_position=self.launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        trajectory = self.df17.generate_trajectory(strike_params, time_step_s=1.0)

        # Find maximum altitude
        max_altitude = max(p.altitude_m for p in trajectory)

        # Should reach at least 40 km altitude (glide phase)
        self.assertGreaterEqual(max_altitude, 40000,
                               "Trajectory should reach at least 40 km altitude")

        # Should not exceed 100 km (space boundary)
        self.assertLessEqual(max_altitude, 100000,
                            "Trajectory should not exceed 100 km")

    def test_trajectory_velocity_profile(self):
        """Test velocity profile is realistic"""
        target = create_cvn_carrier()
        target.position = np.array([2000000, 0, 0])

        strike_params = StrikeParameters(
            launch_position=self.launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        trajectory = self.df17.generate_trajectory(strike_params, time_step_s=1.0)

        # All velocities should be hypersonic (Mach 5+)
        for point in trajectory:
            self.assertGreaterEqual(point.mach_number, 5.0,
                                   f"Velocity should be hypersonic at t={point.time_s}s")


class TestPhysicalRealism(unittest.TestCase):
    """Test overall physical realism of model"""

    def setUp(self):
        self.df17 = DF17HGVModel()

    def test_flight_time_realistic(self):
        """Test flight times are realistic for given ranges"""
        launch_position = np.array([0, 0, 100])

        # 2000 km range
        target = create_land_target()
        target.position = np.array([2000000, 0, 0])

        strike_params = StrikeParameters(
            launch_position=launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = self.df17.predict_impact(strike_params)

        # Flight time should be reasonable (5-15 minutes for 2000 km)
        self.assertGreaterEqual(prediction.time_to_impact_s, 300,
                               "Flight time should be at least 5 minutes")
        self.assertLessEqual(prediction.time_to_impact_s, 900,
                            "Flight time should not exceed 15 minutes")

    def test_impact_velocity_hypersonic(self):
        """Test impact velocity is hypersonic"""
        launch_position = np.array([0, 0, 100])
        target = create_land_target()
        target.position = np.array([2000000, 0, 0])

        strike_params = StrikeParameters(
            launch_position=launch_position,
            target=target,
            launch_azimuth_deg=90,
            desired_impact_angle_deg=60,
            salvo_size=1
        )

        prediction = self.df17.predict_impact(strike_params)

        # Impact velocity should be hypersonic (Mach 5+)
        impact_mach = prediction.impact_velocity_ms / 340.0
        self.assertGreaterEqual(impact_mach, 5.0,
                               "Impact velocity should be hypersonic")


def run_verification_suite():
    """Run complete verification test suite"""
    print("=" * 70)
    print("DF-17 HGV Model - Verification Test Suite")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDF17Parameters))
    suite.addTests(loader.loadTestsFromTestCase(TestDF17Targeting))
    suite.addTests(loader.loadTestsFromTestCase(TestDefensiveSystems))
    suite.addTests(loader.loadTestsFromTestCase(TestSalvoEffectiveness))
    suite.addTests(loader.loadTestsFromTestCase(TestTrajectoryGeneration))
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
