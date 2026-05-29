#!/usr/bin/env python3
"""
Type 052D Destroyer CAD Integration Tests

Verifies the Type 052D destroyer model's physics behavior in the CAD framework.

Tests include:
- Radar detection capabilities (dual-face rotating AESA)
- HQ-9B SAM engagement envelope
- Task force air defense coordination
- Comparison of baseline vs enhanced variants

SOURCE:
Based on Global Times article (2026-01-02):
"PLA Navy commissions new Type 052D destroyer with enhanced capabilities"

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import unittest
import numpy as np
from osint_cad.platforms.type052d_model import (
    Type052DModel,
    Type052DVariant,
    Type052DRadarParameters
)


class TestType052DRadarCapabilities(unittest.TestCase):
    """Test Type 052D radar detection capabilities"""

    def setUp(self):
        """Initialize destroyer models"""
        self.baseline = Type052DModel(variant=Type052DVariant.BASELINE)
        self.enhanced = Type052DModel(variant=Type052DVariant.ENHANCED)

    def test_enhanced_has_better_radar(self):
        """Test enhanced variant has improved radar specs"""
        baseline_range = self.baseline.specs.radar.detection_range_km
        enhanced_range = self.enhanced.specs.radar.detection_range_km

        self.assertGreater(
            enhanced_range, baseline_range,
            "Enhanced variant should have longer detection range"
        )

        baseline_tracks = self.baseline.specs.radar.track_capacity
        enhanced_tracks = self.enhanced.specs.radar.track_capacity

        self.assertGreater(
            enhanced_tracks, baseline_tracks,
            "Enhanced variant should track more targets"
        )

    def test_detection_range_vs_stealth_fighter(self):
        """Test detection range vs F-35A (0.005 m² RCS)"""
        # Enhanced variant
        detection_range = self.enhanced.calculate_radar_detection_range(
            target_rcs_m2=0.005
        )

        # Type 052D should detect stealth fighters at tactically useful range
        # S-band AESA has advantage vs VHF but not as good as X-band
        self.assertGreater(detection_range, 50,
                          "Should detect F-35 beyond 50 km")
        self.assertLess(detection_range, 250,
                       "Detection range should be realistic for S-band vs stealth")

    def test_detection_range_vs_conventional_fighter(self):
        """Test detection range vs conventional fighter (1.0 m² RCS)"""
        detection_range = self.enhanced.calculate_radar_detection_range(
            target_rcs_m2=1.0
        )

        # Should detect conventional fighters at long range
        self.assertGreater(detection_range, 200,
                          "Should detect conventional fighter beyond 200 km")

    def test_detection_range_vs_bomber(self):
        """Test detection range vs large bomber (100 m² RCS)"""
        detection_range = self.enhanced.calculate_radar_detection_range(
            target_rcs_m2=100
        )

        # Should detect large bombers at very long range
        self.assertGreater(detection_range, 400,
                          "Should detect bomber beyond 400 km")

    def test_detection_probability_affects_range(self):
        """Test that lower detection probability extends range"""
        # Pd = 0.90 (baseline)
        range_high_pd = self.enhanced.calculate_radar_detection_range(
            target_rcs_m2=1.0,
            detection_probability=0.90
        )

        # Pd = 0.50 (extended range, lower confidence)
        range_low_pd = self.enhanced.calculate_radar_detection_range(
            target_rcs_m2=1.0,
            detection_probability=0.50
        )

        self.assertGreater(
            range_low_pd, range_high_pd,
            "Lower Pd should extend detection range"
        )


class TestType052DHQ9BEngagement(unittest.TestCase):
    """Test Type 052D HQ-9B SAM engagement capabilities"""

    def setUp(self):
        """Initialize enhanced destroyer model"""
        self.destroyer = Type052DModel(variant=Type052DVariant.ENHANCED)

    def test_hq9b_baseline_envelope(self):
        """Test HQ-9B engagement envelope vs standard fighter"""
        envelope = self.destroyer.calculate_hq9b_engagement_envelope(
            target_altitude_km=10,
            target_speed_mach=1.2,
            target_rcs_m2=1.0
        )

        self.assertGreater(envelope['max_range_km'], 200,
                          "HQ-9B should engage beyond 200 km")
        self.assertGreater(envelope['pk'], 0.70,
                          "Should have high Pk vs conventional fighter")

    def test_hq9b_vs_stealth_fighter(self):
        """Test HQ-9B engagement vs F-35A"""
        envelope = self.destroyer.calculate_hq9b_engagement_envelope(
            target_altitude_km=8,
            target_speed_mach=0.9,  # Subsonic stealth ingress
            target_rcs_m2=0.005
        )

        # Stealth should degrade performance
        self.assertLess(envelope['max_range_km'], 250,
                       "Stealth should reduce max range")
        self.assertLess(envelope['pk'], 0.85,
                       "Stealth should reduce Pk")

    def test_hq9b_vs_high_altitude_target(self):
        """Test HQ-9B vs high-altitude target"""
        envelope = self.destroyer.calculate_hq9b_engagement_envelope(
            target_altitude_km=35,  # Above rated ceiling
            target_speed_mach=1.5,
            target_rcs_m2=10
        )

        # High altitude should reduce effective range
        baseline_envelope = self.destroyer.calculate_hq9b_engagement_envelope(
            target_altitude_km=10,
            target_speed_mach=1.5,
            target_rcs_m2=10
        )

        self.assertLess(
            envelope['max_range_km'],
            baseline_envelope['max_range_km'],
            "High altitude should reduce engagement range"
        )

    def test_hq9b_vs_supersonic_target(self):
        """Test HQ-9B vs high-speed supersonic target"""
        envelope = self.destroyer.calculate_hq9b_engagement_envelope(
            target_altitude_km=12,
            target_speed_mach=2.8,  # High-speed dash
            target_rcs_m2=5.0
        )

        # High speed should reduce effectiveness
        baseline_envelope = self.destroyer.calculate_hq9b_engagement_envelope(
            target_altitude_km=12,
            target_speed_mach=1.5,  # Subsonic/low supersonic
            target_rcs_m2=5.0
        )

        self.assertLessEqual(
            envelope['pk'],
            baseline_envelope['pk'],
            "High-speed target should reduce Pk"
        )


class TestType052DTaskForceDefense(unittest.TestCase):
    """Test Type 052D task force air defense capabilities"""

    def setUp(self):
        """Initialize enhanced destroyer model"""
        self.destroyer = Type052DModel(variant=Type052DVariant.ENHANCED)

    def test_single_ship_coverage(self):
        """Test single Type 052D air defense coverage"""
        coverage = self.destroyer.calculate_task_force_air_defense_coverage(
            num_type052d=1,
            formation_radius_km=0
        )

        # Single ship should provide basic coverage
        self.assertGreater(coverage['coverage_area_km2'], 100000,
                          "Should cover significant area")
        self.assertEqual(coverage['defense_layers'], 3,
                        "Should have 3 defense layers")

    def test_task_force_coverage_scaling(self):
        """Test that multiple destroyers increase coverage"""
        single_ship = self.destroyer.calculate_task_force_air_defense_coverage(
            num_type052d=1
        )

        task_force = self.destroyer.calculate_task_force_air_defense_coverage(
            num_type052d=4
        )

        # Task force should have at least 4x coverage with coordination bonus
        coverage_ratio = (
            task_force['coverage_area_km2'] / single_ship['coverage_area_km2']
        )
        self.assertGreaterEqual(coverage_ratio, 4.0,
                          "Task force should scale linearly with coordination bonus")

    def test_enhanced_coordination_bonus(self):
        """Test enhanced variant has better coordination"""
        baseline = Type052DModel(variant=Type052DVariant.BASELINE)

        baseline_coverage = baseline.calculate_task_force_air_defense_coverage(
            num_type052d=4
        )

        enhanced_coverage = self.destroyer.calculate_task_force_air_defense_coverage(
            num_type052d=4
        )

        self.assertGreater(
            enhanced_coverage['coordination_factor'],
            baseline_coverage['coordination_factor'],
            "Enhanced variant should have better coordination"
        )

    def test_simultaneous_engagement_capacity(self):
        """Test task force simultaneous engagement capacity"""
        coverage = self.destroyer.calculate_task_force_air_defense_coverage(
            num_type052d=4
        )

        # 4x enhanced Type 052D should handle large raid
        expected_capacity = 4 * self.destroyer.specs.radar.simultaneous_engagement
        self.assertEqual(
            coverage['simultaneous_engagements'],
            expected_capacity,
            "Should aggregate engagement capacity"
        )

        # Should handle realistic threat saturation
        self.assertGreater(coverage['simultaneous_engagements'], 30,
                          "Task force should handle 30+ simultaneous threats")


class TestType052DVariantComparison(unittest.TestCase):
    """Test comparison between Type 052D variants"""

    def setUp(self):
        """Initialize both variants"""
        self.baseline = Type052DModel(variant=Type052DVariant.BASELINE)
        self.enhanced = Type052DModel(variant=Type052DVariant.ENHANCED)

    def test_variant_specifications(self):
        """Test variants have correct specifications"""
        # Baseline (Kunming, 2014)
        self.assertEqual(self.baseline.specs.ship_name, "Kunming")
        self.assertEqual(self.baseline.specs.hull_number, "172")
        self.assertEqual(self.baseline.specs.commissioned_date, 2014)

        # Enhanced (Loudi, 2026)
        self.assertEqual(self.enhanced.specs.ship_name, "Loudi")
        self.assertEqual(self.enhanced.specs.hull_number, "176")
        self.assertEqual(self.enhanced.specs.commissioned_date, 2026)

    def test_enhanced_improvements(self):
        """Test enhanced variant has documented improvements"""
        # Radar improvements
        self.assertGreater(
            self.enhanced.specs.radar.detection_range_km,
            self.baseline.specs.radar.detection_range_km,
            "Enhanced should have better radar range"
        )

        # Track capacity improvements
        self.assertGreater(
            self.enhanced.specs.radar.track_capacity,
            self.baseline.specs.radar.track_capacity,
            "Enhanced should track more targets"
        )

        # Engagement improvements
        self.assertGreater(
            self.enhanced.specs.radar.simultaneous_engagement,
            self.baseline.specs.radar.simultaneous_engagement,
            "Enhanced should engage more simultaneous targets"
        )

    def test_weapon_improvements(self):
        """Test weapon system improvements in enhanced variant"""
        # HQ-9B range improvement
        self.assertGreater(
            self.enhanced.specs.weapons.hq9b_range_km,
            self.baseline.specs.weapons.hq9b_range_km,
            "Enhanced should have longer-range SAMs"
        )

        # YJ-18 improvements
        self.assertGreater(
            self.enhanced.specs.weapons.yj18_range_km,
            self.baseline.specs.weapons.yj18_range_km,
            "Enhanced should have extended anti-ship range"
        )

    def test_confidence_levels(self):
        """Test both variants have acceptable confidence"""
        self.assertGreaterEqual(self.baseline.specs.overall_confidence, 0.50)
        self.assertGreaterEqual(self.enhanced.specs.overall_confidence, 0.50)


class TestType052DReportGeneration(unittest.TestCase):
    """Test Type 052D report generation"""

    def test_specification_report_generation(self):
        """Test specification report can be generated"""
        destroyer = Type052DModel(variant=Type052DVariant.ENHANCED)
        report = destroyer.generate_specification_report()

        # Report should contain key information
        self.assertIn("TYPE 052D DESTROYER CAD MODEL", report)
        self.assertIn("Loudi", report)
        self.assertIn("Hull Number: 176", report)
        self.assertIn("Dual-face rotating AESA", report)
        self.assertIn("HQ-9B", report)
        self.assertIn("YJ-18", report)
        self.assertIn("ENHANCED CAPABILITIES", report)
        self.assertIn("UNCLASSIFIED // PUBLIC RELEASE", report)


def run_integration_demonstration():
    """Run integration demonstration"""
    print("=" * 80)
    print("TYPE 052D DESTROYER CAD INTEGRATION DEMONSTRATION")
    print("=" * 80)
    print()

    # Test CAD capabilities
    print("1. CAD CAPABILITIES DEMONSTRATION")
    print("-" * 80)
    destroyer = Type052DModel(variant=Type052DVariant.ENHANCED)

    print("Detection Range vs Targets:")
    targets = [
        ("F-35A (stealth)", 0.005),
        ("F/A-18E (conventional)", 1.0),
        ("B-52 (bomber)", 100)
    ]
    for name, rcs in targets:
        range_km = destroyer.calculate_radar_detection_range(rcs)
        print(f"  {name:25s}: {range_km:6.1f} km")

    print()
    print("Task Force Air Defense:")
    coverage = destroyer.calculate_task_force_air_defense_coverage(num_type052d=4)
    print(f"  4x Type 052D Enhanced Formation")
    print(f"  Coverage Area: {coverage['coverage_area_km2']:,.0f} km²")
    print(f"  Max Range: {coverage['max_engagement_range_km']:.0f} km")
    print(f"  Simultaneous Engagements: {coverage['simultaneous_engagements']}")
    print()


if __name__ == "__main__":
    # Run integration demonstration
    run_integration_demonstration()

    # Run unit tests
    print("\n\n" + "=" * 80)
    print("RUNNING UNIT TESTS")
    print("=" * 80)
    unittest.main(argv=[''], verbosity=2)
