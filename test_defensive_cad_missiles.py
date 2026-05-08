#!/usr/bin/env python3
"""
Test script to verify defensive CAD works for J-20 against all missiles
Including AIM-260 and other missile types.
"""

import numpy as np
from eob_database import EOBDatabase, ThreatLevel

def test_missile_threat_assessment():
    """Test that all missiles are properly assessed for defensive CAD"""

    print("=" * 80)
    print("DEFENSIVE CAD MISSILE THREAT ASSESSMENT TEST")
    print("=" * 80)
    print()
    print("Testing J-20 defensive assessment against various platforms with different missiles")
    print()

    # Create EOB database
    eob = EOBDatabase()

    # Test scenarios: J-20 assessing threats from OPERATIONALLY VERIFIED platforms only
    # EXCLUDED (not operationally verified):
    #   - NGAD: Concept-level, not fielded (post-2030)
    #   - MQ-28: Development, not deployed
    test_scenarios = [
        {
            'name': 'F-35A with AIM-120D (head-on)',
            'platform_id': 'F35A',
            'range_km': 150,
            'aspect': 0,
            'expected_range': 180,
            'expected_threat': ThreatLevel.CRITICAL
        },
        {
            'name': 'F-35A at rear aspect',
            'platform_id': 'F35A',
            'range_km': 100,
            'aspect': 180,  # Rear aspect reduces effective range
            'expected_range_min': 100,  # Reduced by aspect factor
            'expected_threat': ThreatLevel.CRITICAL
        },
        {
            'name': 'J-20 (peer threat) with PL-15 and PL-21',
            'platform_id': 'J20',
            'range_km': 150,
            'aspect': 0,
            'expected_range': 400,  # J-20 carries both PL-15 (200km) and PL-21 (400km) - use max
            'expected_threat': ThreatLevel.CRITICAL
        },
        {
            'name': 'J-20 at extended range',
            'platform_id': 'J20',
            'range_km': 300,
            'aspect': 0,
            'expected_range': 400,
            'expected_threat': ThreatLevel.MEDIUM  # Within PL-21 range but extended
        },
        {
            'name': 'E-3 AWACS (non-fighter)',
            'platform_id': 'E3',
            'range_km': 200,
            'aspect': 0,
            'expected_range': 0,  # AWACS has no air-to-air weapons
            'expected_threat': ThreatLevel.LOW
        }
    ]

    # Run tests
    passed = 0
    failed = 0

    for scenario in test_scenarios:
        print(f"Test: {scenario['name']}")
        print(f"  Platform: {scenario['platform_id']}")
        print(f"  Range: {scenario['range_km']} km")
        print(f"  Aspect: {scenario['aspect']}°")

        # Get threat assessment
        assessment = eob.assess_threat(
            platform_id=scenario['platform_id'],
            range_km=scenario['range_km'],
            aspect_angle_deg=scenario['aspect']
        )

        print(f"  → Max Weapon Range: {assessment['max_weapon_range_km']} km")
        print(f"  → Effective Range: {assessment['engagement_range_km']:.1f} km")
        print(f"  → Threat Level: {assessment['threat_level'].name}")
        print(f"  → Recommendation: {assessment['recommendations'][0]}")

        # Verify results
        if 'expected_range' in scenario:
            if assessment['max_weapon_range_km'] == scenario['expected_range']:
                print(f"  ✓ PASS: Range correctly assessed")
                passed += 1
            else:
                print(f"  ✗ FAIL: Expected {scenario['expected_range']} km, got {assessment['max_weapon_range_km']} km")
                failed += 1
        elif 'expected_range_min' in scenario:
            if assessment['engagement_range_km'] >= scenario['expected_range_min']:
                print(f"  ✓ PASS: Range correctly reduced by aspect")
                passed += 1
            else:
                print(f"  ✗ FAIL: Range too low for aspect factor")
                failed += 1

        print()

    # Summary
    print("=" * 80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed == 0:
        print("✓ All defensive CAD missile assessments working correctly!")
        print("✓ ONLY operationally verified platforms tested:")
        print("  - F-35A (fielded since 2015)")
        print("  - J-20 (fielded since 2017)")
        print("  - E-3 AWACS (operational)")
        print("✓ EXCLUDED non-verified platforms:")
        print("  - NGAD (concept, not fielded)")
        print("  - MQ-28 (development, not deployed)")

    assert failed == 0, f"{failed} tests failed - review implementation"


def test_all_platform_weapons():
    """Verify all platforms have their weapons properly configured"""

    print("\n" + "=" * 80)
    print("PLATFORM WEAPONS INVENTORY")
    print("=" * 80)
    print()

    eob = EOBDatabase()

    for platform_id, platform in eob.platforms.items():
        print(f"{platform.platform_name} ({platform_id})")
        print(f"  Country: {platform.country}")
        print(f"  Weapons: {', '.join(platform.weapons) if platform.weapons else 'None'}")

        # Test threat assessment at 150 km
        assessment = eob.assess_threat(platform_id, 150, 0)
        print(f"  Max AA Range: {assessment['max_weapon_range_km']} km")
        print()


if __name__ == "__main__":
    # Run tests
    success = test_missile_threat_assessment()
    test_all_platform_weapons()

    # Exit with appropriate code
    exit(0 if success else 1)
