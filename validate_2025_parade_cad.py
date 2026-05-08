#!/usr/bin/env python3
"""
Validation Script for China 2025 Military Parade Systems CAD Integration

Verifies that all systems from the 2025 parade are properly integrated
into the CAD framework with correct contractor mappings.

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

from defense_contractor_registry import DefenseContractorRegistry


def validate_2025_parade_systems():
    """Validate all 2025 parade systems are CAD-enabled"""

    print("=" * 80)
    print("CHINA 2025 MILITARY PARADE SYSTEMS - CAD VALIDATION")
    print("=" * 80)
    print()

    registry = DefenseContractorRegistry()

    # Expected systems from 2025 parade
    expected_systems = {
        # Missiles & Nuclear Deterrence
        "DF61": "CASC",
        "DF5C": "CASC",
        "DF31": "CASC",
        "JL3": "CASC",
        "YJ15": "CASIC",
        "YJ17": "CASIC",
        "YJ19": "CASIC",
        "YJ20": "CASIC",
        "JingleiJL1": "CASIC",

        # Drones & Unmanned Systems
        "H6N": "AVIC",
        "GJ11": "AVIC",
        "WingLoong": "AVIC",
        "Rainbow": "CASC",
        "LoyalWingman": "AVIC",
        "AJX002": "CSSC",

        # Ground Unmanned Systems
        "RoboticWolves": "NORINCO",
        "ArmedGroundDrone": "NORINCO",
        "MineClearingRobot": "NORINCO",

        # Information Operations & EW
        "DataSpectrumMonitoring": "CETC",
        "SignalJammingVehicle": "CETC",
        "EMReconnaissanceVehicle": "CETC",
        "NetworkNodeVehicle": "CETC",
        "UAVDataRelay": "CASC",

        # Air Defense
        "HQ9C": "CASIC",
        "HQ11": "CASIC",
        "HQ16C": "CASIC",
        "HQ19": "CASIC",
        "HQ20": "CASIC",
        "LY1Ship": "CSIC",
        "LY1Truck": "CSIC",

        # Ground & Naval
        "Type100": "NORINCO",
        "HHQ9C": "CASIC",
        "HQ10": "CASIC",
    }

    # Validate each system
    missing_systems = []
    incorrect_contractors = []
    validated_systems = []

    for system_id, expected_contractor in expected_systems.items():
        model = registry.get_model(system_id)

        if model is None:
            missing_systems.append(system_id)
        elif model.contractor != expected_contractor:
            incorrect_contractors.append(
                f"{system_id}: expected {expected_contractor}, got {model.contractor}"
            )
        else:
            validated_systems.append(system_id)

    # Print results
    print(f"Total Expected Systems: {len(expected_systems)}")
    print(f"✓ Validated Systems: {len(validated_systems)}")
    print(f"✗ Missing Systems: {len(missing_systems)}")
    print(f"✗ Incorrect Contractors: {len(incorrect_contractors)}")
    print()

    # Print detailed results
    if validated_systems:
        print("VALIDATED SYSTEMS:")
        print("-" * 80)
        for system_id in validated_systems:
            model = registry.get_model(system_id)
            print(f"  ✓ {system_id:25s} | {model.contractor:12s} | {model.platform_name}")
        print()

    if missing_systems:
        print("MISSING SYSTEMS:")
        print("-" * 80)
        for system_id in missing_systems:
            print(f"  ✗ {system_id} (expected contractor: {expected_systems[system_id]})")
        print()

    if incorrect_contractors:
        print("INCORRECT CONTRACTOR MAPPINGS:")
        print("-" * 80)
        for error in incorrect_contractors:
            print(f"  ✗ {error}")
        print()

    # Validate contractors
    print("CONTRACTOR VALIDATION:")
    print("-" * 80)

    contractors_to_check = ["AVIC", "CASIC", "CASC", "CETC", "NORINCO", "CSSC", "CSIC"]
    for contractor_name in contractors_to_check:
        contractor = registry.get_contractor(contractor_name)
        if contractor:
            models = registry.get_contractor_models(contractor_name)
            print(f"  ✓ {contractor_name:12s} | {len(models):2d} models | {contractor.full_name}")
        else:
            print(f"  ✗ {contractor_name} - NOT FOUND")

    print()

    # Overall status
    print("=" * 80)
    if len(validated_systems) == len(expected_systems):
        print("✓ ALL SYSTEMS VALIDATED - CAD INTEGRATION COMPLETE")
        print("=" * 80)
        return True
    else:
        print(f"✗ VALIDATION FAILED - {len(missing_systems) + len(incorrect_contractors)} issues found")
        print("=" * 80)
        return False


def print_contractor_summary():
    """Print summary of all contractors and their systems"""

    print("\n")
    print("=" * 80)
    print("CONTRACTOR SUMMARY - 2025 PARADE SYSTEMS")
    print("=" * 80)
    print()

    registry = DefenseContractorRegistry()

    parade_contractors = ["CASC", "CASIC", "AVIC", "CETC", "NORINCO", "CSSC", "CSIC"]

    for contractor_name in parade_contractors:
        contractor = registry.get_contractor(contractor_name)
        if not contractor:
            continue

        models = registry.get_contractor_models(contractor_name)
        parade_models = [m for m in models if m.fielded_date >= 2010]  # Recent systems

        print(f"{contractor.name} - {contractor.full_name}")
        print(f"  Country: {contractor.country}")
        print(f"  Specialization: {contractor.specialization}")
        print(f"  Total Models: {len(parade_models)}")
        print(f"  Average Confidence: {sum(m.confidence for m in parade_models) / len(parade_models):.0%}")
        print(f"  Systems:")

        for model in sorted(parade_models, key=lambda m: m.fielded_date, reverse=True):
            print(f"    • {model.platform_name:35s} ({model.fielded_date}) - {model.confidence:.0%} confidence")

        print()


if __name__ == "__main__":
    # Run validation
    success = validate_2025_parade_systems()

    # Print contractor summary
    print_contractor_summary()

    # Exit with appropriate code
    exit(0 if success else 1)
