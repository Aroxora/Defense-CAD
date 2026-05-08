# Additional Defense Contractors Setup Guide

## Overview

This document provides setup instructions for additional defense contractors not covered in dedicated guides. These contractors have either:
- Limited models in the framework (CETC, NORINCO, CSSC, CSIC)
- Specialized roles (MiG interceptors, Almaz air defense)
- Lower confidence levels due to data availability

For complete setup guides, see:
- `AVIC_CONTRACTOR_SETUP.md` - Chinese aviation (J-20, J-10C, etc.)
- `CASIC_CONTRACTOR_SETUP.md` - Chinese missiles (PL-15, DF-17, etc.)
- `CASC_CONTRACTOR_SETUP.md` - Chinese strategic systems (DF-61, JL-3, etc.)
- `SUKHOI_CONTRACTOR_SETUP.md` - Russian aviation (Su-57, Su-35, etc.)

**Classification:** UNCLASSIFIED // PUBLIC RELEASE

---

## Table of Contents

1. [MiG (Russian Aircraft Corporation)](#mig-russian-aircraft-corporation)
2. [CETC (China Electronics Technology Group)](#cetc-china-electronics-technology-group)
3. [NORINCO (China North Industries Corporation)](#norinco-china-north-industries-corporation)
4. [CSSC (China State Shipbuilding Corporation)](#cssc-china-state-shipbuilding-corporation)
5. [CSIC (China Shipbuilding Industry Corporation)](#csic-china-shipbuilding-industry-corporation)
6. [Almaz (JSC Almaz-Antey)](#almaz-jsc-almaz-antey)

---

## MiG (Russian Aircraft Corporation)

**Full Name:** Russian Aircraft Corporation MiG
**Established:** 1939
**Specialization:** Interceptors, multirole fighters
**Systems Covered:** MiG-31 Foxhound
**Confidence:** 70%

### Quick Start

```bash
# Verify MiG-31 model
python3 -c "
from rcs_models import MiG31RCSModel

mig31 = MiG31RCSModel()
print('✓ MiG-31 model loaded')
print(f'✓ MiG-31 frontal RCS: {mig31.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
print(f'✓ Confidence: {mig31.confidence:.0%}')
"

# Run tests
pytest test_defensive_cad_missiles.py::TestDefensiveCAD::test_mig31_rcs_model -v
```

### MiG-31 Use Case: High-Speed Interceptor

**Specifications:**
- Max speed: Mach 2.83
- Interceptor role: Long-range, high-altitude
- Radar: Zaslon-M PESA (upgraded)
- Weapons: R-37M long-range AAM (400 km)

**Analysis:**
```python
from rcs_models import MiG31RCSModel

mig31 = MiG31RCSModel()

print("=== MiG-31 FOXHOUND INTERCEPTOR ===")
print(f"Contractor: MiG")
print(f"Fielded: 2011 (BM upgrade)")
print(f"Confidence: {mig31.confidence:.0%}")

# RCS analysis
rcs_frontal = mig31.calculate_rcs(0, 0).rcs_dbsm
print(f"\nFrontal RCS: {rcs_frontal:.1f} dBsm")
print(f"Role: Long-range interceptor (not stealth)")
print(f"Primary mission: AWACS/tanker denial")
print(f"Weapon: R-37M (400 km range)")
```

**Key Findings:**
- ✅ Excellent high-speed, high-altitude performance
- ✅ Very long-range missiles (R-37M: 400 km)
- ⚠️ Large RCS (~15 dBsm) - not stealthy
- ✅ Effective AWACS killer role

### Integration Shortcomings

**Issue 1: Limited Modernization Data**
- MiG-31BM upgrade details partially classified
- Zaslon-M PESA radar specs estimated
- Confidence: 65% (vs 70% for baseline)

**Issue 2: R-37M Missile Not Modeled**
- Long-range AAM not in framework
- Would enhance analysis of AWACS engagement scenarios
- Workaround: Note capability qualitatively

---

## CETC (China Electronics Technology Group)

**Full Name:** China Electronics Technology Group Corporation
**Established:** 2002
**Specialization:** Electronics, radars, EW systems, C4ISR
**Systems Covered:** ISF EW vehicles, Data Spectrum Monitoring, Signal Jamming, Network Nodes
**Confidence:** 40% (LOWEST - limited public data)

### Quick Start

```bash
# Verify CETC models
python3 -c "
from china_2025_parade_models import (
    DataSpectrumMonitoringModel,
    SignalJammingVehicleModel,
    EMReconnaissanceVehicleModel,
    NetworkNodeVehicleModel
)

dsm = DataSpectrumMonitoringModel()
print('✓ CETC models loaded')
print(f'✓ Data Spectrum Monitoring confidence: {dsm.confidence:.0%}')
print('⚠ WARNING: CETC models have very limited data')
"
```

### CETC Use Case: Electronic Warfare Systems

**Models Available:**
1. Data Spectrum Monitoring Vehicle
2. Signal Jamming Vehicle
3. EM Reconnaissance Vehicle
4. Network Node Vehicle

**Critical Limitation:**
```python
# CETC models are framework-only with minimal specifications
dsm = DataSpectrumMonitoringModel()

print("=== CETC ELECTRONIC WARFARE SYSTEMS ===")
print(f"Confidence: {dsm.confidence:.0%}")  # Very low (30-40%)
print("\n⚠ WARNING: CETC systems highly classified")
print("Limited public data available")
print("Use for qualitative assessment only")
```

### Integration Shortcomings

**Issue 1: EW Systems Almost Completely Opaque**
- Jamming power unknown (EIRP not public)
- Frequency coverage unknown
- Effectiveness metrics unavailable
- Confidence: 30-35% (very low)

**Issue 2: No Test Coverage**
- Zero tests for CETC systems
- Cannot validate correctness
- Accepted limitation (data unavailable)

**Workaround:**
- Use for qualitative analysis only
- Compare to US/Russian EW systems for context
- Flag all estimates as highly uncertain
- Document as "reference models only"

---

## NORINCO (China North Industries Corporation)

**Full Name:** China North Industries Corporation
**Established:** 1999
**Specialization:** Ground vehicles, artillery, unmanned ground systems
**Systems Covered:** Type-100, Robotic Wolves, Armed UGVs, Mine-Clearing Robots
**Confidence:** 45%

### Quick Start

```bash
# Verify NORINCO models
python3 -c "
from china_2025_parade_models import (
    Type100VehicleModel,
    RoboticWolvesUGVModel,
    ArmedGroundDroneModel,
    MineClearingRobotModel
)

type100 = Type100VehicleModel()
print('✓ NORINCO models loaded')
print(f'✓ Type-100 confidence: {type100.confidence:.0%}')
"
```

### NORINCO Use Case: Unmanned Ground Systems

**Models Available:**
1. Type-100 IFV/APC
2. Robotic Wolves UGV
3. Armed Ground Drone
4. Mine-Clearing Robot

**Analysis:**
```python
from china_2025_parade_models import RoboticWolvesUGVModel

wolves = RoboticWolvesUGVModel()

print("=== NORINCO ROBOTIC WOLVES UGV ===")
print(f"Contractor: NORINCO")
print(f"Fielded: 2023")
print(f"Confidence: {wolves.confidence:.0%}")

print("\nRole: Autonomous reconnaissance, patrol")
print("Note: Outside primary air combat scope")
```

### Integration Shortcomings

**Issue 1: Ground Systems Outside Primary Scope**
- Framework designed for air combat
- Ground vehicles not integrated into kill chain
- Limited usefulness for air superiority analysis

**Issue 2: No Test Coverage**
- Zero tests for NORINCO systems
- Accepted limitation (not core capability)

**Workaround:**
- Use for ground systems analysis separately
- Not required for air combat scenarios
- Document as "future expansion" for combined arms

---

## CSSC (China State Shipbuilding Corporation)

**Full Name:** China State Shipbuilding Corporation
**Established:** 2019
**Specialization:** Naval vessels, unmanned maritime systems
**Systems Covered:** Type 052D Destroyer, Type 055, Type 003 Carrier, AJX002 UUV
**Confidence:** 35-60% (varies by system)

### Quick Start

```bash
# Verify CSSC models
python3 -c "
from type052d_model import Type052DModel, Type052DVariant
from china_2025_parade_models import AJX002UUVModel

type052d = Type052DModel(variant=Type052DVariant.STANDARD)
uuv = AJX002UUVModel()

print('✓ CSSC models loaded')
print(f'✓ Type 052D confidence: {type052d.confidence:.0%}')
print(f'⚠ AJX002 UUV confidence: {uuv.confidence:.0%} (very low)')
"

# Run tests
pytest test_type052d_integration.py -v
```

### CSSC Use Case: Type 052D Destroyer

**Specifications:**
- Class: Luyang III-class guided missile destroyer
- Displacement: ~7,500 tons
- Weapons: HHQ-9C SAM, YJ-18 ASM, ASW torpedoes
- Radar: Type 346A AESA

**Analysis:**
```python
from type052d_model import Type052DModel, Type052DVariant

destroyer = Type052DModel(variant=Type052DVariant.STANDARD)

print("=== TYPE 052D DESTROYER (LUYANG III) ===")
print(f"Contractor: CSSC")
print(f"Fielded: 2014")
print(f"Confidence: {destroyer.confidence:.0%}")

print("\n✓ HHQ-9C SAM integrated (long-range air defense)")
print("✓ Type 346A AESA radar (multi-function)")
print("✓ YJ-18 ASM (anti-ship, supersonic terminal)")
```

### Integration Shortcomings

**Issue 1: Limited to Single Variant**
- Multiple Type 052D variants exist
- Only standard variant fully modeled
- Type 052DL (longer), Type 055 (larger) not modeled

**Issue 2: AJX002 UUV Minimal Detail**
- Framework only (30% confidence)
- Missing propulsion, sensors, weapons data
- Avoid using for operational planning

**Workaround:**
- Use Type 052D as representative PLAN destroyer
- Note variant limitations in documentation
- Document AJX002 as "concept model only"

---

## CSIC (China Shipbuilding Industry Corporation)

**Full Name:** China Shipbuilding Industry Corporation
**Established:** 1999
**Specialization:** Naval weapons, directed energy weapons
**Systems Covered:** LY-1 Laser (Ship/Truck variants)
**Confidence:** 40%

### Quick Start

```bash
# Verify CSIC models
python3 -c "
from china_2025_parade_models import LY1LaserShipModel, LY1LaserTruckModel

laser_ship = LY1LaserShipModel()
laser_truck = LY1LaserTruckModel()

print('✓ CSIC laser models loaded')
print(f'⚠ Confidence: {laser_ship.confidence:.0%} (very low)')
print('WARNING: Directed energy weapons highly speculative')
"
```

### CSIC Use Case: LY-1 Directed Energy Weapon

**Analysis:**
```python
from china_2025_parade_models import LY1LaserShipModel

laser = LY1LaserShipModel()

print("=== LY-1 LASER DIRECTED ENERGY WEAPON ===")
print(f"Contractor: CSIC")
print(f"Fielded: 2024")
print(f"Confidence: {laser.confidence:.0%}") # 35%

print("\n⚠ WARNING: Highly speculative estimates")
print("Laser power: 100-150 kW (estimated, unverified)")
print("Effective range: 3-5 km (estimated, unverified)")
print("Compare to US Navy LaWS: 30 kW (confirmed)")
```

### Integration Shortcomings

**Issue 1: Directed Energy Weapons Highly Speculative**
- Very limited public data
- Power levels estimated (100-150 kW unverified)
- Effective range estimated (3-5 km unverified)
- Confidence: 35% (very low)

**Issue 2: Cannot Assess Effectiveness**
- Burn-through time unknown
- Weather/atmospheric limitations unknown
- Cannot model reliably

**Workaround:**
- Use as "technology demonstrator" only
- Compare to US LaWS (30 kW confirmed) for context
- Flag all estimates as highly uncertain
- Avoid operational planning use

---

## Almaz (JSC Almaz-Antey)

**Full Name:** JSC Almaz-Antey
**Established:** 2002
**Specialization:** Air defense systems, anti-ballistic missiles
**Systems Referenced:** S-400 Triumf, S-300PMU-2 Favorit
**Confidence:** 70% (good, but NOT IMPLEMENTED)

### Status

**CRITICAL: S-400 and S-300 models NOT implemented**

```bash
# This will FAIL - models not implemented
python3 -c "
from s400_model import S400Model  # Does not exist!
"
```

### Integration Shortcomings

**Issue 1: SAM Systems NOT Implemented**
- S-400, S-300 referenced in registry
- Code implementations DO NOT exist
- Scope limitation (focus on aircraft/missiles)

**Issue 2: Cannot Model Air Defense Scenarios**
- Russian integrated air defense not available
- Chinese HQ-9/HQ-16 also not integrated
- Major gap for defensive scenarios

**Workaround:**
- Document as "future enhancement"
- S-400 export data available (could be added)
- Users can integrate separately if needed

**Recommendation:**
- High priority for future development
- Good public data available (70% confidence)
- Would enable defensive scenario modeling

---

## Summary of Contractor Status

| Contractor | Models | Test Coverage | Confidence | Integration | Recommendation |
|------------|--------|---------------|------------|-------------|----------------|
| **MiG** | 1 (MiG-31) | ⚠️ Limited | 70% | ✅ Good | Use for interceptor analysis |
| **CETC** | 4 (EW vehicles) | ❌ None | 40% | ❌ Minimal | Qualitative only |
| **NORINCO** | 4 (UGVs) | ❌ None | 45% | ❌ Minimal | Ground systems only |
| **CSSC** | 2 (Type 052D, UUV) | ⚠️ Limited | 35-60% | ⚠️ Partial | Naval analysis only |
| **CSIC** | 2 (Lasers) | ❌ None | 40% | ❌ Minimal | Technology demonstrator |
| **Almaz** | 0 (referenced) | ❌ N/A | 70% (potential) | ❌ Not implemented | Future priority |

### Key Takeaways

**Good for Analysis:**
- ✅ MiG-31 interceptor modeling
- ✅ Type 052D destroyer modeling

**Limited Use:**
- ⚠️ CETC EW systems (qualitative only)
- ⚠️ NORINCO ground systems (outside scope)
- ⚠️ CSIC lasers (highly speculative)
- ⚠️ CSSC UUV (concept only)

**Not Available:**
- ❌ Almaz S-400/S-300 (not implemented)

### Recommendations

1. **For Air Combat Analysis:**
   - Use AVIC, CASIC, CASC, Sukhoi (primary contractors)
   - MiG-31 for interceptor scenarios
   - Avoid CETC, NORINCO, CSIC for quantitative analysis

2. **For Naval Analysis:**
   - Use Type 052D destroyer
   - Avoid AJX002 UUV (insufficient data)
   - Avoid LY-1 laser (highly speculative)

3. **Future Priorities:**
   - Implement S-400/S-300 models (good data available)
   - Improve CETC EW modeling (if data becomes available)
   - Expand naval systems (Type 055, Type 003)

---

## Support

### GitHub Issues
https://github.com/pseudonym-tbd/actual-f35-kill/issues

### Documentation
- `INTEGRATION_SHORTCOMINGS.md` - Comprehensive limitations analysis
- `DEFENSE_CONTRACTOR_INTEGRATION.md` - Integration framework
- `VERIFIED_MODELS_REGISTRY.md` - All verified models

---

## Classification and Distribution

**Repository Classification:** UNCLASSIFIED // PUBLIC RELEASE

**Safe to Use:**
- ✅ No violation of export control laws
- ✅ Public release, no restrictions
- ✅ Can be modified with contractor internal data (keep local)

**Restrictions:**
- ❌ DO NOT upload classified data to public GitHub
- ❌ DO NOT share modified models with classified parameters

---

**Last Updated:** 2026-01-02
**Version:** 1.0
**Classification:** UNCLASSIFIED // PUBLIC RELEASE
**Status:** Supplemental guide for additional contractors
