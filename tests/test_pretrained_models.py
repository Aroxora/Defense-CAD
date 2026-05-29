#!/usr/bin/env python3
"""
Pre-Trained Model Validation Tests

Tests for J-20 defensive models and PL-15 offensive models to ensure they
produce results within expected bounds and maintain consistency with
deductive reasoning chains.

Test Coverage:
- J-20 RCS model (defensive awareness)
- J-20 radar detection model (defensive sensor)
- PL-15 targeting model (offensive engagement)
- PL-15 intercept geometry (offensive prediction)

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
import unittest
from osint_cad.physics.rcs_models import J20RCSModel, F35ARCSModel, rcs_linear_to_dbsm
from osint_cad.sensors.j20_radar_model import J20RadarModel, J20RadarParameters
from osint_cad.targeting.pl15_targeting_model import PL15TargetingModel, PL15Parameters, TargetState, EngagementPhase


class TestJ20RCSModel(unittest.TestCase):
    """Test J-20 defensive RCS model"""

    def setUp(self):
        """Set up test fixtures"""
        self.j20_rcs = J20RCSModel()

    def test_frontal_rcs_range(self):
        """Test J-20 frontal RCS is within expected bounds"""
        result = self.j20_rcs.calculate_rcs(azimuth_deg=0, elevation_deg=0)

        # Expected: 0.001-0.003 m² (frontal)
        self.assertGreater(result.rcs_m2, 0.0005, "J-20 frontal RCS too small")
        self.assertLess(result.rcs_m2, 0.005, "J-20 frontal RCS too large")
        self.assertAlmostEqual(result.rcs_m2, 0.0014, delta=0.002, msg="J-20 frontal RCS not near estimate")

    def test_beam_rcs_larger_than_frontal(self):
        """Test beam RCS is significantly larger than frontal"""
        frontal = self.j20_rcs.calculate_rcs(azimuth_deg=0, elevation_deg=0)
        beam = self.j20_rcs.calculate_rcs(azimuth_deg=90, elevation_deg=0)

        self.assertGreater(beam.rcs_m2, frontal.rcs_m2 * 10, "Beam RCS should be >10× frontal")
        self.assertLess(beam.rcs_m2, frontal.rcs_m2 * 100, "Beam RCS should be <100× frontal")

    def test_canard_contribution(self):
        """Test that J-20 RCS is higher than F-35 due to canards"""
        j20_frontal = self.j20_rcs.calculate_rcs(azimuth_deg=0, elevation_deg=0)
        f35_frontal = F35ARCSModel.calculate_rcs(azimuth_deg=0, elevation_deg=0)

        # J-20 should have 3-7× larger frontal RCS due to canards
        self.assertGreater(j20_frontal.rcs_m2, f35_frontal.rcs_m2 * 2,
                          "J-20 frontal RCS should be larger than F-35")
        self.assertLess(j20_frontal.rcs_m2, f35_frontal.rcs_m2 * 10,
                       "J-20 frontal RCS shouldn't be 10× larger than F-35")

    def test_rcs_confidence_levels(self):
        """Test confidence levels are reasonable"""
        aspects = [0, 30, 90, 180]
        for azimuth in aspects:
            result = self.j20_rcs.calculate_rcs(azimuth_deg=azimuth, elevation_deg=0)
            self.assertGreater(result.confidence, 0.1, f"Confidence too low at {azimuth}°")
            self.assertLess(result.confidence, 1.0, f"Confidence too high at {azimuth}°")

    def test_frequency_scaling(self):
        """Test RCS scales with frequency"""
        rcs_x_band = self.j20_rcs.calculate_rcs(azimuth_deg=0, elevation_deg=0, frequency_ghz=10.0)
        rcs_s_band = self.j20_rcs.calculate_rcs(azimuth_deg=0, elevation_deg=0, frequency_ghz=3.0)

        # Lower frequency should have smaller RCS (negative frequency dependence)
        self.assertLess(rcs_s_band.rcs_m2, rcs_x_band.rcs_m2,
                       "S-band RCS should be smaller than X-band")

    def test_rcs_dbsm_conversion(self):
        """Test RCS dBsm values are correct"""
        result = self.j20_rcs.calculate_rcs(azimuth_deg=0, elevation_deg=0)

        # Verify dBsm conversion
        expected_dbsm = 10 * np.log10(result.rcs_m2)
        self.assertAlmostEqual(result.rcs_dbsm, expected_dbsm, places=1)

        # Frontal should be around -28 dBsm
        self.assertGreater(result.rcs_dbsm, -32, "J-20 frontal RCS (dBsm) too small")
        self.assertLess(result.rcs_dbsm, -25, "J-20 frontal RCS (dBsm) too large")


class TestJ20RadarModel(unittest.TestCase):
    """Test J-20 defensive radar detection model"""

    def setUp(self):
        """Set up test fixtures"""
        self.j20_radar = J20RadarModel()

    def test_radar_parameters(self):
        """Test radar parameters match reasoning chain estimates"""
        params = self.j20_radar.params

        # Element count: 1800 ± 150 (updated for modernized Type 1475 AESA)
        self.assertEqual(params.num_elements, 1800, "Element count mismatch")
        self.assertEqual(params.num_elements_uncertainty, 150, "Element uncertainty mismatch")
        self.assertEqual(params.element_count_confidence, 0.80, "Confidence mismatch")

        # Aperture size (updated measurement)
        self.assertAlmostEqual(params.aperture_diameter_m, 0.80, delta=0.05,
                              msg="Aperture diameter mismatch")

    def test_detection_range_vs_rcs(self):
        """Test detection range scales correctly with RCS"""
        # Small RCS (F-35 frontal)
        detection_small = self.j20_radar.calculate_detection_range(
            target_rcs_m2=0.0002, azimuth_deg=0, elevation_deg=0)

        # Large RCS (F-35 beam)
        detection_large = self.j20_radar.calculate_detection_range(
            target_rcs_m2=0.02, azimuth_deg=0, elevation_deg=0)

        # Range should scale as RCS^0.25
        expected_ratio = (0.02 / 0.0002) ** 0.25  # ~3.16×
        actual_ratio = detection_large.detection_range_km / detection_small.detection_range_km

        self.assertAlmostEqual(actual_ratio, expected_ratio, delta=0.5,
                              msg="Detection range doesn't scale correctly with RCS")

    def test_f35_frontal_detection_range(self):
        """Test F-35 frontal detection range is reasonable"""
        f35_frontal_rcs = 0.0002  # m²
        detection = self.j20_radar.calculate_detection_range(
            target_rcs_m2=f35_frontal_rcs, azimuth_deg=0, elevation_deg=0)

        # Should detect F-35 frontal at roughly 60-100 km
        self.assertGreater(detection.detection_range_km, 50,
                          "F-35 frontal detection range too short")
        self.assertLess(detection.detection_range_km, 120,
                       "F-35 frontal detection range too long")

    def test_scan_angle_losses(self):
        """Test detection range decreases with scan angle"""
        target_rcs = 0.02  # m²

        detection_boresight = self.j20_radar.calculate_detection_range(
            target_rcs, azimuth_deg=0, elevation_deg=0)

        detection_30deg = self.j20_radar.calculate_detection_range(
            target_rcs, azimuth_deg=30, elevation_deg=0)

        detection_60deg = self.j20_radar.calculate_detection_range(
            target_rcs, azimuth_deg=60, elevation_deg=0)

        # Range should decrease with scan angle
        self.assertGreater(detection_boresight.detection_range_km,
                          detection_30deg.detection_range_km,
                          "Range should decrease at 30°")
        self.assertGreater(detection_30deg.detection_range_km,
                          detection_60deg.detection_range_km,
                          "Range should decrease at 60°")

    def test_beyond_scan_limits(self):
        """Test detection fails beyond scan limits"""
        detection = self.j20_radar.calculate_detection_range(
            target_rcs_m2=1.0, azimuth_deg=70, elevation_deg=0)

        self.assertEqual(detection.detection_range_km, 0.0,
                        "Should have zero range beyond scan limits")
        self.assertEqual(detection.confidence, 0.0,
                        "Should have zero confidence beyond scan limits")

    def test_power_levels(self):
        """Test transmit power is within reasonable bounds"""
        params = self.j20_radar.params

        # Peak power: 25-50 kW for modern GaN AESA with 1800 elements
        self.assertGreater(params.total_peak_power_kw, 25, "Peak power too low")
        self.assertLess(params.total_peak_power_kw, 50, "Peak power too high")

        # Average power should be ~12.5% of peak (GaN allows higher duty cycle)
        power_ratio = params.total_average_power_kw / params.total_peak_power_kw
        self.assertAlmostEqual(power_ratio, 0.125, delta=0.03,
                              msg="Average/peak power ratio incorrect")


class TestPL15TargetingModel(unittest.TestCase):
    """Test PL-15 offensive targeting model"""

    def setUp(self):
        """Set up test fixtures"""
        self.pl15 = PL15TargetingModel()

    def test_missile_parameters(self):
        """Test missile parameters match reasoning chain estimates"""
        params = self.pl15.params

        # Physical dimensions
        self.assertEqual(params.length_m, 4.0, "Length mismatch")
        self.assertEqual(params.diameter_m, 0.203, "Diameter mismatch")
        self.assertEqual(params.mass_total_kg, 210, "Mass mismatch")

        # NEZ range: 100 ± 20 km
        self.assertEqual(params.nez_range_head_on_km, 100, "NEZ range mismatch")
        self.assertEqual(params.nez_range_uncertainty_km, 20, "NEZ uncertainty mismatch")
        self.assertEqual(params.nez_confidence, 0.60, "NEZ confidence mismatch")

    def test_delta_v_calculation(self):
        """Test rocket equation ΔV is reasonable"""
        params = self.pl15.params
        delta_v = params.delta_v_ideal_ms

        # Should be around 900-1000 m/s based on mass ratio
        self.assertGreater(delta_v, 800, "ΔV too low")
        self.assertLess(delta_v, 1100, "ΔV too high")

        # Verify rocket equation
        mass_ratio = params.mass_total_kg / params.mass_burnout_kg
        expected_dv = params.exhaust_velocity_ms * np.log(mass_ratio)
        self.assertAlmostEqual(delta_v, expected_dv, places=1)

    def test_intercept_head_on(self):
        """Test intercept prediction for head-on engagement"""
        missile_pos = np.array([0, 0, 12000])
        missile_vel = np.array([450, 0, 0])  # Mach 1.5

        target = TargetState(
            position=np.array([80000, 0, 12000]),  # 80 km ahead
            velocity=np.array([-250, 0, 0]),  # Head-on at Mach 0.8
            acceleration=np.zeros(3),
            rcs_m2=0.0002,
            aspect_angle_deg=0
        )

        intercept = self.pl15.predict_intercept(
            missile_pos, missile_vel, target,
            phase=EngagementPhase.MIDCOURSE)

        # Should have valid intercept
        self.assertTrue(intercept.intercept_possible, "Head-on intercept should be possible")
        self.assertGreater(intercept.probability_kill, 0.5, "Pk should be high for head-on")
        self.assertGreater(intercept.energy_margin, 0.3, "Should have sufficient energy")

    def test_intercept_tail_chase(self):
        """Test intercept prediction for tail chase (harder)"""
        missile_pos = np.array([0, 0, 12000])
        missile_vel = np.array([450, 0, 0])

        target = TargetState(
            position=np.array([80000, 0, 12000]),  # 80 km ahead
            velocity=np.array([250, 0, 0]),  # Running away
            acceleration=np.zeros(3),
            rcs_m2=0.005,
            aspect_angle_deg=180
        )

        intercept = self.pl15.predict_intercept(
            missile_pos, missile_vel, target,
            phase=EngagementPhase.MIDCOURSE)

        # Tail chase should have lower Pk
        self.assertLess(intercept.probability_kill, 0.7, "Pk should be lower for tail chase")

    def test_no_intercept_opening_geometry(self):
        """Test no intercept for opening geometry"""
        missile_pos = np.array([0, 0, 12000])
        missile_vel = np.array([450, 0, 0])  # Heading east

        target = TargetState(
            position=np.array([-50000, 0, 12000]),  # 50 km west
            velocity=np.array([-250, 0, 0]),  # Heading west
            acceleration=np.zeros(3),
            rcs_m2=1.0,
            aspect_angle_deg=0
        )

        intercept = self.pl15.predict_intercept(
            missile_pos, missile_vel, target,
            phase=EngagementPhase.MIDCOURSE)

        # Should not have valid intercept (opening)
        self.assertFalse(intercept.intercept_possible, "Opening geometry should not intercept")
        self.assertLessEqual(intercept.probability_kill, 0.1, "Pk should be very low")

    def test_pk_vs_range(self):
        """Test Pk decreases with range"""
        missile_pos = np.array([0, 0, 12000])
        missile_vel = np.array([450, 0, 0])

        ranges_km = [30, 60, 100]
        pks = []

        for range_km in ranges_km:
            target = TargetState(
                position=np.array([range_km * 1000, 0, 12000]),
                velocity=np.array([-250, 0, 0]),
                acceleration=np.zeros(3),
                rcs_m2=0.02,
                aspect_angle_deg=0
            )

            intercept = self.pl15.predict_intercept(
                missile_pos, missile_vel, target,
                phase=EngagementPhase.MIDCOURSE)
            pks.append(intercept.probability_kill)

        # Pk should decrease with range
        self.assertGreater(pks[0], pks[1], "Pk should decrease from 30 to 60 km")
        self.assertGreater(pks[1], pks[2], "Pk should decrease from 60 to 100 km")

    def test_launch_acceptability(self):
        """Test launch acceptability logic"""
        missile_pos = np.array([0, 0, 12000])
        missile_vel = np.array([450, 0, 0])

        # Good target: head-on, medium range
        good_target = TargetState(
            position=np.array([60000, 0, 12000]),
            velocity=np.array([-250, 0, 0]),
            acceleration=np.zeros(3),
            rcs_m2=0.02,
            aspect_angle_deg=0
        )

        acceptable, reason, confidence = self.pl15.calculate_launch_acceptability(
            missile_pos, missile_vel, good_target)

        self.assertTrue(acceptable, f"Good target should be acceptable: {reason}")

        # Too far target
        far_target = TargetState(
            position=np.array([150000, 0, 12000]),  # 150 km
            velocity=np.array([-250, 0, 0]),
            acceleration=np.zeros(3),
            rcs_m2=0.02,
            aspect_angle_deg=0
        )

        acceptable, reason, confidence = self.pl15.calculate_launch_acceptability(
            missile_pos, missile_vel, far_target)

        self.assertFalse(acceptable, "Far target should not be acceptable")
        self.assertIn("range", reason.lower(), "Reason should mention range")

    def test_energy_margin_by_phase(self):
        """Test energy margin varies by flight phase"""
        missile_pos = np.array([0, 0, 12000])
        missile_vel = np.array([450, 0, 0])

        target = TargetState(
            position=np.array([60000, 0, 12000]),
            velocity=np.array([-250, 0, 0]),
            acceleration=np.zeros(3),
            rcs_m2=0.02,
            aspect_angle_deg=0
        )

        # Test different phases
        boost = self.pl15.predict_intercept(
            missile_pos, missile_vel, target, phase=EngagementPhase.BOOST)

        terminal = self.pl15.predict_intercept(
            missile_pos, missile_vel, target, phase=EngagementPhase.TERMINAL)

        burnout = self.pl15.predict_intercept(
            missile_pos, missile_vel, target, phase=EngagementPhase.BURNOUT)

        # Boost should have highest energy margin
        self.assertGreater(boost.energy_margin, terminal.energy_margin,
                          "Boost should have more energy than terminal")
        self.assertGreater(terminal.energy_margin, burnout.energy_margin,
                          "Terminal should have more energy than burnout")


class TestModelIntegration(unittest.TestCase):
    """Test integration between J-20 and PL-15 models"""

    def setUp(self):
        """Set up test fixtures"""
        self.j20_radar = J20RadarModel()
        self.pl15 = PL15TargetingModel()

    def test_j20_detects_and_pl15_engages(self):
        """Test J-20 radar detection followed by PL-15 engagement"""
        # J-20 position and velocity
        j20_pos = np.array([0, 0, 12000])
        j20_vel = np.array([450, 0, 0])

        # F-35 target
        f35_pos = np.array([80000, 0, 12000])  # 80 km ahead
        f35_vel = np.array([-250, 0, 0])  # Head-on

        # Calculate F-35 RCS
        f35_rcs = F35ARCSModel.calculate_rcs_from_vectors(
            j20_pos, f35_pos, f35_vel, frequency_ghz=10.0)

        # J-20 radar detection
        detection = self.j20_radar.calculate_detection_range(
            target_rcs_m2=f35_rcs.rcs_m2, azimuth_deg=0, elevation_deg=0)

        # Verify J-20 can detect F-35
        range_to_target_km = 80.0
        self.assertGreater(detection.detection_range_km, range_to_target_km,
                          "J-20 should detect F-35 at 80 km")

        # PL-15 launch feasibility
        target = TargetState(
            position=f35_pos,
            velocity=f35_vel,
            acceleration=np.zeros(3),
            rcs_m2=f35_rcs.rcs_m2,
            aspect_angle_deg=f35_rcs.azimuth_deg
        )

        acceptable, reason, confidence = self.pl15.calculate_launch_acceptability(
            j20_pos, j20_vel, target)

        self.assertTrue(acceptable, f"PL-15 should be able to engage: {reason}")

    def test_stealthy_target_challenge(self):
        """Test engagement difficulty against stealthy target"""
        j20_pos = np.array([0, 0, 12000])
        j20_vel = np.array([450, 0, 0])

        # F-35 at long range, frontal aspect
        f35_pos = np.array([100000, 0, 12000])  # 100 km
        f35_vel = np.array([-250, 0, 0])

        f35_rcs = F35ARCSModel.calculate_rcs_from_vectors(
            j20_pos, f35_pos, f35_vel, frequency_ghz=10.0)

        # Detection should be marginal
        detection = self.j20_radar.calculate_detection_range(
            target_rcs_m2=f35_rcs.rcs_m2, azimuth_deg=0, elevation_deg=0)

        # PL-15 engagement at NEZ edge
        target = TargetState(
            position=f35_pos,
            velocity=f35_vel,
            acceleration=np.zeros(3),
            rcs_m2=f35_rcs.rcs_m2,
            aspect_angle_deg=0
        )

        intercept = self.pl15.predict_intercept(
            j20_pos, j20_vel, target, phase=EngagementPhase.BOOST)

        # Pk should be lower for stealthy target at long range
        self.assertLess(intercept.probability_kill, 0.8,
                       "Pk should be reduced for stealthy target at long range")


def run_all_tests():
    """Run all pre-trained model tests"""
    print("=" * 70)
    print("PRE-TRAINED MODEL VALIDATION TESTS")
    print("=" * 70)
    print("\nRunning comprehensive validation of J-20 and PL-15 models...")
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestJ20RCSModel))
    suite.addTests(loader.loadTestsFromTestCase(TestJ20RadarModel))
    suite.addTests(loader.loadTestsFromTestCase(TestPL15TargetingModel))
    suite.addTests(loader.loadTestsFromTestCase(TestModelIntegration))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED - Pre-trained models validated successfully")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - Review failures above")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    exit(exit_code)
