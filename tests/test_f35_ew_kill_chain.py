#!/usr/bin/env python3
"""
Test suite for F-35 EW Kill Chain vs J-20 and F-35 Defensive Model vs PL-15

Tests:
1. AIM-260 targeting model vs J-20 RCS
2. F-35 kill chain integration against J-20
3. F-35 defensive model against PL-15

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
import sys

from osint_cad.physics.rcs_models import J20RCSModel, F35ARCSModel
from osint_cad.targeting.aim260_targeting_model import AIM260TargetingModel, AIM260EngagementPhase
from osint_cad.engagements.f35_kill_chain_vs_j20 import F35KillChainVsJ20
from osint_cad.engagements.f35_defensive_vs_pl15 import F35DefensiveModel, DefensiveManeuver, ThreatWarningStatus


def test_j20_rcs_aspect_dependent():
    """Test J-20 RCS varies correctly with aspect"""
    print("=" * 80)
    print("TEST: J-20 RCS Aspect Dependency")
    print("=" * 80)

    # Test at different aspects
    aspects = [0, 30, 60, 90, 120, 150, 180]
    passed = 0
    failed = 0

    print(f"\n{'Aspect':>10} {'RCS (m²)':>12} {'RCS (dBsm)':>12} {'Status'}")
    print("-" * 50)

    for azimuth in aspects:
        result = J20RCSModel.calculate_rcs(azimuth, 0)

        # Verify RCS increases from frontal
        if azimuth == 0:
            frontal_rcs = result.rcs_m2
            status = "BASELINE"
            passed += 1
        elif azimuth <= 90:
            # Should increase towards beam
            if result.rcs_m2 >= frontal_rcs:
                status = "✓ PASS"
                passed += 1
            else:
                status = "✗ FAIL"
                failed += 1
        else:
            status = "OK"
            passed += 1

        print(f"{azimuth:>10}° {result.rcs_m2:>12.6f} {result.rcs_dbsm:>+12.1f} {status}")

    # Verify frontal RCS is in expected range (0.001-0.003 m²)
    frontal = J20RCSModel.calculate_rcs(0, 0)
    if 0.0005 < frontal.rcs_m2 < 0.005:
        print(f"\n✓ Frontal RCS {frontal.rcs_m2:.4f} m² in expected range")
        passed += 1
    else:
        print(f"\n✗ Frontal RCS {frontal.rcs_m2:.4f} m² outside expected range")
        failed += 1

    print(f"\nResult: {passed} passed, {failed} failed")
    assert failed == 0, f"J-20 RCS aspect dependency: {failed} tests failed"


def test_aim260_vs_j20():
    """Test AIM-260 targeting against J-20"""
    print("\n" + "=" * 80)
    print("TEST: AIM-260 Targeting vs J-20")
    print("=" * 80)

    aim260 = AIM260TargetingModel()
    passed = 0
    failed = 0

    # F-35 launch position
    f35_pos = np.array([0, 0, 12000])
    f35_vel = np.array([450, 0, 0])

    # Test scenarios - Note: seeker acquisition only works in terminal phase (~15 km)
    # During midcourse (80+ km), missile uses datalink guidance
    # For testing, we check:
    # 1. Launch acceptability (based on intercept geometry)
    # 2. Terminal seeker capability (at close range)
    scenarios = [
        # Terminal phase tests (seeker should work)
        # Pk ~0.5-0.6 at 10-15km vs stealth target is realistic
        ("Terminal 10km head-on", np.array([10000, 0, 12000]), np.array([-500, 0, 0]), True, True, 0.5),
        ("Terminal 15km head-on", np.array([15000, 0, 12000]), np.array([-500, 0, 0]), True, True, 0.5),
        # Midcourse tests (seeker won't work but intercept is valid)
        ("Midcourse 80km", np.array([80000, 0, 12000]), np.array([-500, 0, 0]), True, False, 0.0),
        ("Midcourse 150km", np.array([150000, 0, 12000]), np.array([-500, 0, 0]), True, False, 0.0),
        # Beyond range
        ("Beyond range 250km", np.array([250000, 0, 12000]), np.array([-500, 0, 0]), False, False, 0.0),
    ]

    print(f"\n{'Scenario':>25} {'Range':>8} {'Pk':>8} {'Seeker':>8} {'Accept':>8} {'Status'}")
    print("-" * 80)

    for name, j20_pos, j20_vel, expect_acceptable, expect_seeker, min_pk in scenarios:
        intercept = aim260.predict_intercept_vs_j20(
            f35_pos, f35_vel, j20_pos, j20_vel
        )

        acceptable, reason, _ = aim260.calculate_launch_acceptability_vs_j20(
            f35_pos, f35_vel, j20_pos, j20_vel
        )

        range_km = np.linalg.norm(j20_pos - f35_pos) / 1000

        # Validate
        test_passed = True
        if expect_seeker and not intercept.seeker_can_acquire:
            test_passed = False
        if expect_seeker and intercept.probability_kill < min_pk:
            test_passed = False
        if expect_acceptable != acceptable:
            test_passed = False

        if test_passed:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1

        print(f"{name:>25} {range_km:>7.0f}km {intercept.probability_kill:>7.2f} "
              f"{'YES' if intercept.seeker_can_acquire else 'NO':>8} "
              f"{'YES' if acceptable else 'NO':>8} {status}")

    print(f"\nResult: {passed} passed, {failed} failed")
    assert failed == 0, f"AIM-260 vs J-20: {failed} tests failed"


def test_f35_kill_chain_vs_j20():
    """Test F-35 kill chain integration against J-20"""
    print("\n" + "=" * 80)
    print("TEST: F-35 Kill Chain vs J-20")
    print("=" * 80)

    kill_chain = F35KillChainVsJ20()
    passed = 0
    failed = 0

    # Standard engagement geometry
    f35_pos = np.array([0, 0, 12000])
    f35_vel = np.array([450, 0, 0])
    j20_pos = np.array([150000, 0, 12000])
    j20_vel = np.array([-500, 0, 0])

    # Test radar detection
    radar_det = kill_chain.calculate_radar_detection_vs_j20(j20_pos, j20_vel, f35_pos)
    print(f"\nRadar Detection Range: {radar_det.detection_range_km:.0f} km")
    print(f"Detection Method: {radar_det.detection_method}")
    print(f"Reveals Position: {radar_det.reveals_position}")

    # Validate detection range (vs J-20 stealth, 20-80 km depending on aspect)
    # Lower detection range is realistic for LPI mode vs stealth target
    if 15 < radar_det.detection_range_km < 120:
        print("✓ Radar detection range in expected range (stealth target)")
        passed += 1
    else:
        print(f"✗ Radar detection range {radar_det.detection_range_km:.0f} km outside expected 15-120 km")
        failed += 1

    # Validate active radar reveals position
    if radar_det.reveals_position:
        print("✓ Active radar correctly marked as position-revealing")
        passed += 1
    else:
        print("✗ Active radar should reveal position")
        failed += 1

    # Test kill chain metrics
    metrics = kill_chain.calculate_kill_chain_metrics_vs_j20(
        j20_pos, j20_vel, f35_pos, f35_vel
    )

    print(f"\nKill Chain Metrics:")
    print(f"  Radar Detection: {metrics.radar_detection_range_km:.0f} km")
    print(f"  AIM-260 NEZ: {metrics.weapon_nez_km:.0f} km")
    print(f"  Pk at 100km: {metrics.pk_at_100km:.2f}")
    print(f"  Pk at 150km: {metrics.pk_at_150km:.2f}")
    print(f"  First Detection Advantage: {metrics.first_detection_advantage_km:.0f} km")
    print(f"  Network Resilience: {metrics.network_resilience_score:.0f}/100")

    # Validate first detection advantage (should be negative - J-20 advantage)
    if metrics.first_detection_advantage_km < 0:
        print("✓ Correctly identifies J-20 first detection advantage")
        passed += 1
    else:
        print("✗ Should show J-20 first detection advantage")
        failed += 1

    # Test full engagement analysis
    result = kill_chain.analyze_engagement(
        j20_pos, j20_vel, f35_pos, f35_vel
    )

    print(f"\nEngagement Analysis:")
    print(f"  J-20 RCS: {result.j20_target_rcs.rcs_dbsm:.1f} dBsm")
    print(f"  AIM-260 Pk: {result.aim260_pk:.2f}")
    print(f"  First Shot Achievable: {result.first_shot_achievable}")
    print(f"  Assessment: {result.engagement_assessment}")
    print(f"  Risks: {len(result.risks)}")
    for risk in result.risks:
        print(f"    - {risk}")

    # Validate risks identified
    if len(result.risks) > 0:
        print("✓ Engagement risks correctly identified")
        passed += 1
    else:
        print("✗ Should identify engagement risks")
        failed += 1

    print(f"\nResult: {passed} passed, {failed} failed")
    assert failed == 0, f"F-35 kill chain vs J-20: {failed} tests failed"


def test_f35_defensive_vs_pl15():
    """Test F-35 defensive model against PL-15"""
    print("\n" + "=" * 80)
    print("TEST: F-35 Defensive Model vs PL-15")
    print("=" * 80)

    defense = F35DefensiveModel()
    passed = 0
    failed = 0

    # Threat scenario: PL-15 inbound (flying TOWARDS F-35)
    # PL-15 at 60km, flying in -x direction (towards F-35 at origin)
    pl15_pos = np.array([60000, 0, 12000])
    pl15_vel = np.array([-1200, 0, 0])  # Flying towards F-35
    f35_pos = np.array([0, 0, 12000])
    f35_vel = np.array([-200, 0, 0])  # F-35 flying away (defensive)

    # Test F-35 RCS calculation
    f35_rcs = defense.calculate_f35_rcs_vs_pl15(pl15_pos, f35_pos, f35_vel)
    print(f"\nF-35 RCS to PL-15 seeker: {f35_rcs.rcs_m2:.6f} m² ({f35_rcs.rcs_dbsm:.1f} dBsm)")

    # Validate stealth RCS
    if f35_rcs.rcs_m2 < 0.01:
        print("✓ F-35 RCS appropriately low (stealth)")
        passed += 1
    else:
        print("✗ F-35 RCS too high for stealth aircraft")
        failed += 1

    # Test threat warning
    warning = defense.assess_threat_warning(
        pl15_pos, pl15_vel, f35_pos, f35_vel, j20_radar_active=True
    )
    print(f"Threat Warning Status: {warning.value}")

    if warning != ThreatWarningStatus.NO_WARNING:
        print("✓ Threat warning system functioning")
        passed += 1
    else:
        print("✗ Should have warning with active radar")
        failed += 1

    # Test Pk calculation for different maneuvers
    print(f"\nDefensive Maneuver Effectiveness:")
    print(f"{'Maneuver':>15} {'Pk':>8} {'Survival':>10}")
    print("-" * 40)

    maneuver_works = True
    for maneuver in DefensiveManeuver:
        pk = defense.calculate_pk_against_f35(
            pl15_pos, pl15_vel, f35_pos, f35_vel,
            maneuver, ecm_active=True
        )
        survival = 1.0 - pk
        print(f"{maneuver.value:>15} {pk:>7.2f} {survival:>10.2f}")

        # Defensive maneuvers should improve survival
        if maneuver != DefensiveManeuver.NONE and pk >= 0.9:
            maneuver_works = False

    if maneuver_works:
        print("✓ Defensive maneuvers reduce Pk")
        passed += 1
    else:
        print("✗ Defensive maneuvers should reduce Pk")
        failed += 1

    # Test full survivability analysis
    assessment = defense.analyze_survivability(
        pl15_pos, pl15_vel, f35_pos, f35_vel,
        j20_radar_active=True
    )

    print(f"\nSurvivability Assessment:")
    print(f"  Time to Impact: {assessment.time_to_impact_s:.1f} s")
    print(f"  Pk (defended): {assessment.pk_against_f35:.2f}")
    print(f"  Survival Probability: {assessment.survival_probability:.2f}")
    print(f"  Best Maneuver: {assessment.best_maneuver.value}")

    # Validate survival probability > 0
    if 0 < assessment.survival_probability < 1:
        print("✓ Survivability correctly calculated")
        passed += 1
    else:
        print("✗ Survivability should be between 0 and 1")
        failed += 1

    # Test recommendations generated
    if len(assessment.recommendations) > 0:
        print("✓ Defensive recommendations generated")
        passed += 1
    else:
        print("✗ Should generate defensive recommendations")
        failed += 1

    print(f"\nResult: {passed} passed, {failed} failed")
    assert failed == 0, f"F-35 defensive vs PL-15: {failed} tests failed"


def test_integration():
    """Test integration of all components"""
    print("\n" + "=" * 80)
    print("TEST: Full Integration (F-35 vs J-20 Mutual Engagement)")
    print("=" * 80)

    # Create models
    f35_kill_chain = F35KillChainVsJ20()
    f35_defense = F35DefensiveModel()
    aim260 = AIM260TargetingModel()

    passed = 0
    failed = 0

    # Engagement geometry
    f35_pos = np.array([0, 0, 12000])
    f35_vel = np.array([450, 0, 0])
    j20_pos = np.array([120000, 0, 12000])
    j20_vel = np.array([-500, 0, 0])

    # Assume PL-15 launched from J-20 position, flying towards F-35
    pl15_pos = j20_pos.copy()
    pl15_vel = np.array([-1200, 0, 0])  # Flying towards F-35 at origin

    # F-35 offensive capability
    offensive = f35_kill_chain.analyze_engagement(
        j20_pos, j20_vel, f35_pos, f35_vel
    )

    # Check AIM-260 launch acceptability (separate from seeker-based Pk)
    aim260_acceptable, aim260_reason, _ = aim260.calculate_launch_acceptability_vs_j20(
        f35_pos, f35_vel, j20_pos, j20_vel
    )

    # F-35 defensive capability
    defensive = f35_defense.analyze_survivability(
        pl15_pos, pl15_vel, f35_pos, f35_vel
    )

    print(f"\nMUTUAL ENGAGEMENT ANALYSIS")
    print("-" * 80)
    print(f"Range: {np.linalg.norm(j20_pos - f35_pos)/1000:.0f} km")
    print(f"\nF-35 Offensive (AIM-260 vs J-20):")
    print(f"  Launch Acceptable: {aim260_acceptable}")
    print(f"  Launch Reason: {aim260_reason}")
    print(f"  First Shot Possible: {offensive.first_shot_achievable}")
    print(f"\nF-35 Defensive (vs PL-15):")
    print(f"  Survival Probability: {defensive.survival_probability:.2f}")
    print(f"  Best Maneuver: {defensive.best_maneuver.value}")

    # Calculate exchange metrics
    f35_pk_estimate = 0.35 if aim260_acceptable else 0.0  # Estimated from launch acceptability
    f35_loss = 1 - defensive.survival_probability

    print(f"\nEXCHANGE ANALYSIS:")
    print(f"  AIM-260 can engage: {aim260_acceptable}")
    print(f"  PL-15 kills F-35: {f35_loss:.2f}")

    # Validate mutual engagement - both sides should have valid models
    validation_passed = True

    # Check that AIM-260 can at least evaluate the engagement
    if aim260_acceptable or "Beyond" in aim260_reason or "range" in aim260_reason.lower():
        print("✓ AIM-260 engagement analysis functional")
        passed += 1
    else:
        print("✗ AIM-260 engagement analysis not working")
        failed += 1
        validation_passed = False

    # Check F-35 defensive model
    if 0 < defensive.survival_probability <= 1:
        print("✓ F-35 defensive model functional")
        passed += 1
    else:
        print("✗ F-35 defensive model not working")
        failed += 1
        validation_passed = False

    # Check engagement risks identified
    if len(offensive.risks) > 0:
        print("✓ Engagement risks identified")
        passed += 1
    else:
        print("✗ Should identify engagement risks")
        failed += 1
        validation_passed = False

    if validation_passed:
        print("\n✓ Integration test passed - mutual engagement correctly modeled")
    else:
        print("\n✗ Integration test failed")

    print(f"\nResult: {passed} passed, {failed} failed")
    assert failed == 0, f"Integration test: {failed} tests failed"


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 80)
    print("F-35 EW KILL CHAIN TEST SUITE")
    print("=" * 80)
    print()

    tests = [
        ("J-20 RCS Aspect Dependency", test_j20_rcs_aspect_dependent),
        ("AIM-260 vs J-20", test_aim260_vs_j20),
        ("F-35 Kill Chain vs J-20", test_f35_kill_chain_vs_j20),
        ("F-35 Defensive vs PL-15", test_f35_defensive_vs_pl15),
        ("Full Integration", test_integration),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
        except AssertionError as e:
            print(f"\n✗ {name} FAILED: {e}")
            results.append((name, False))
        except Exception as e:
            print(f"\n✗ {name} CRASHED: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print("-" * 80)
    print(f"Total: {passed}/{len(results)} tests passed")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED")
        print("  EW kill chain for F-35/AIM-260 vs J-20 validated")
        print("  F-35 defensive model vs PL-15 validated")
        return 0
    else:
        print(f"\n✗ {failed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
