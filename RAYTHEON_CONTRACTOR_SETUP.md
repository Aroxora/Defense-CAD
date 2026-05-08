# Raytheon (RTX) Contractor Setup Guide
## Missiles and Air Defense Systems

**Target Users:** Raytheon engineers, DoD analysts, SAM/AAM program managers
**Systems Covered:** AIM-120D AMRAAM, AIM-9X Sidewinder, SM-6, SM-3, THAAD, Patriot
**Primary Applications:** BVR missile analysis, air defense planning, BMD assessment

---

## Quick Start (15 Minutes)

### Step 1: Download Repository

```bash
# Clone from GitHub
git clone https://github.com/pseudonym-tbd/actual-f35-kill.git
cd actual-f35-kill
```

### Step 2: Install Python Dependencies

```bash
python3 --version  # Requires 3.9+
pip3 install numpy>=1.24.0 scipy>=1.10.0 matplotlib>=3.7.0 pyyaml pytest>=7.0.0
```

### Step 3: Verify Installation

```bash
python3 -c "
from us_2025_defense_systems import (
    AIM120DModel, AIM9XBlock3Model, SM6Model, SM3BlockIIAModel,
    THAADModel, PatriotPAC3MSEModel
)

aim120d = AIM120DModel()
sm6 = SM6Model()
thaad = THAADModel()

print('✓ All Raytheon models loaded successfully')
print(f'✓ AIM-120D range: {aim120d.get_parameters()[\"range_km\"]} km')
print(f'✓ SM-6 range: {sm6.get_parameters()[\"range_km\"]} km')
print(f'✓ THAAD intercept range: {thaad.get_parameters()[\"intercept_range_km\"]} km')
"
```

**Expected output:**
```
✓ All Raytheon models loaded successfully
✓ AIM-120D range: 160 km
✓ SM-6 range: 370 km
✓ THAAD intercept range: 200 km
```

---

## Raytheon Use Cases

### Use Case 1: AIM-120D vs PL-15 Comparison

**What this answers:**
- How does AIM-120D compare to PL-15?
- Engagement envelopes and Pk
- Future improvement needs

**Run the analysis:**
```python
python3 << 'EOF'
from us_2025_defense_systems import AIM120DModel, AIM9XBlock3Model
from pl15_targeting_model import PL15TargetingModel

aim120d = AIM120DModel()
pl15 = PL15TargetingModel()

print("=== AIM-120D vs PL-15 COMPARISON ===")
print(f"{'Metric':<25s} {'AIM-120D':<15s} {'PL-15':<15s}")
print(f"{'-'*55}")

aim_params = aim120d.get_parameters()
print(f"{'Range (km)':<25s} {aim_params['range_km']:<15} {pl15.params.nez_range_head_on_km:<15}")
print(f"{'Speed (Mach)':<25s} {aim_params['speed_mach']:<15} {pl15.params.peak_velocity_ms/340:.1f}")
print(f"{'Warhead (kg)':<25s} {aim_params['warhead_kg']:<15} {pl15.params.mass_warhead_kg}")
print(f"{'Guidance':<25s} {aim_params['guidance']:<15}")
print(f"{'Confidence':<25s} {aim_params['confidence']:.0%}")
EOF
```

### Use Case 2: SM-6 Multi-Role Analysis

**What this answers:**
- SM-6 performance vs air targets
- SM-6 anti-ship capability
- Engagement envelopes

**Run the analysis:**
```python
python3 << 'EOF'
from us_2025_defense_systems import SM6Model
from ddg51_model import DDG51Model, DDG51Variant

sm6 = SM6Model()
ddg = DDG51Model(variant=DDG51Variant.FLIGHT_III)

print("=== SM-6 DUAL II MULTI-ROLE ANALYSIS ===")
params = sm6.get_parameters()
for key, value in params.items():
    print(f"  {key}: {value}")

print("\n=== SM-6 ENGAGEMENT ENVELOPES (DDG-51 Flight III) ===")

# vs Fighter aircraft
envelope = ddg.calculate_sm6_engagement_envelope(
    target_altitude_km=12,
    target_speed_mach=1.5,
    target_rcs_m2=3.0  # 4th-gen fighter
)
print(f"\nvs 4th-Gen Fighter (12km alt, Mach 1.5):")
print(f"  Max Range: {envelope['max_range_km']:.0f} km")
print(f"  Pk: {envelope['pk']:.0%}")

# vs Cruise missile
envelope_cm = ddg.calculate_sm6_engagement_envelope(
    target_altitude_km=0.05,  # Sea-skimmer
    target_speed_mach=2.8,
    target_rcs_m2=0.1
)
print(f"\nvs Sea-Skimming Cruise Missile:")
print(f"  Max Range: {envelope_cm['max_range_km']:.0f} km")
print(f"  Pk: {envelope_cm['pk']:.0%}")

# vs Stealth fighter
envelope_stealth = ddg.calculate_sm6_engagement_envelope(
    target_altitude_km=10,
    target_speed_mach=1.0,
    target_rcs_m2=0.001  # J-20 frontal
)
print(f"\nvs Stealth Fighter (J-20 class):")
print(f"  Max Range: {envelope_stealth['max_range_km']:.0f} km")
print(f"  Pk: {envelope_stealth['pk']:.0%}")
EOF
```

### Use Case 3: THAAD BMD Analysis

**What this answers:**
- THAAD intercept envelopes
- Effectiveness vs different ballistic missile types
- Integration with Aegis

**Run the analysis:**
```python
python3 << 'EOF'
from us_2025_defense_systems import THAADModel, SM3BlockIIAModel, PatriotPAC3MSEModel
from ddg51_model import DDG51Model, DDG51Variant

thaad = THAADModel()
sm3 = SM3BlockIIAModel()
pac3 = PatriotPAC3MSEModel()
ddg = DDG51Model(variant=DDG51Variant.FLIGHT_III)

print("=== LAYERED BMD ANALYSIS ===")

print("\n[Layer 1] SM-3 Block IIA (Exoatmospheric):")
params = sm3.get_parameters()
print(f"  Intercept Range: {params['intercept_range_km']} km")
print(f"  Max Altitude: {params['max_altitude_km']} km")
print(f"  Confidence: {params['confidence']:.0%}")

print("\n[Layer 2] THAAD (Terminal High Altitude):")
params = thaad.get_parameters()
print(f"  Intercept Range: {params['intercept_range_km']} km")
print(f"  Max Altitude: {params['max_altitude_km']} km")
print(f"  Confidence: {params['confidence']:.0%}")

print("\n[Layer 3] Patriot PAC-3 MSE (Terminal):")
params = pac3.get_parameters()
print(f"  Range: {params['range_km']} km")
print(f"  Max Altitude: {params['max_altitude_m']/1000:.0f} km")
print(f"  Confidence: {params['confidence']:.0%}")

# BMD envelope from DDG-51
print("\n=== DDG-51 BMD ENVELOPES ===")
threat_types = ["srbm", "mrbm", "irbm"]

for threat in threat_types:
    envelope = ddg.calculate_sm3_bmd_envelope(threat, threat_range_km=1000)
    if envelope['available']:
        print(f"\nvs {threat.upper()}:")
        print(f"  Intercept Range: {envelope['intercept_range_km']:.0f} km")
        print(f"  Pk: {envelope['pk']:.0%}")
EOF
```

### Use Case 4: Integrated Air Defense Coverage

**What this answers:**
- Combined CSG air defense capability
- Layered defense depth
- Magazine capacity

**Run the analysis:**
```python
python3 << 'EOF'
from ddg51_model import DDG51Model, DDG51Variant

# Create Flight III destroyer
ddg = DDG51Model(variant=DDG51Variant.FLIGHT_III)

print("=== CARRIER STRIKE GROUP AIR DEFENSE (2x DDG-51 Flight III) ===")

coverage = ddg.calculate_carrier_strike_group_defense(
    num_ddg51=2,
    formation_radius_km=50
)

print(f"\nDefense Coverage:")
print(f"  Total Coverage Area: {coverage['coverage_area_km2']:,.0f} km²")
print(f"  Max Engagement Range: {coverage['max_engagement_range_km']:.0f} km")
print(f"  Defense Layers: {coverage['defense_layers']}")
print(f"  Simultaneous Engagements: {coverage['simultaneous_engagements']}")
print(f"  Total VLS Cells: {coverage['total_vls_cells']}")
print(f"  CEC Factor: {coverage['cec_factor']:.2f}x")

print("\n=== MAGAZINE BREAKDOWN (per DDG) ===")
print(f"  VLS Cells: 96")
print(f"  Typical Load:")
print(f"    - SM-6: 24 (air defense)")
print(f"    - SM-3: 8 (BMD)")
print(f"    - ESSM: 32 (point defense, quad-packed)")
print(f"    - TLAM: 16 (land attack)")
print(f"    - LRASM/NSM: 8 (anti-ship)")
print(f"    - ASROC: 8 (ASW)")
EOF
```

---

## Raytheon Systems Catalog

### Air-to-Air Missiles

| System | Range (km) | Guidance | Confidence |
|--------|-----------|----------|-----------|
| AIM-120D AMRAAM | 160+ | INS+GPS+DL+ARH | 85% |
| AIM-9X Block III | 35+ | Imaging IR+DL | 80% |
| AIM-260 JATM* | 200+ | INS+DL+AESA | 50% |

*Developed with Lockheed Martin

### Naval Air Defense

| System | Range (km) | Type | Confidence |
|--------|-----------|------|-----------|
| SM-6 Dual II | 370+ | Multi-Role SAM | 75% |
| SM-3 Block IIA | 2500+ | Exo BMD | 70% |
| ESSM Block 2 | 50+ | Point Defense | 80% |

### Ground-Based Air Defense

| System | Range (km) | Type | Confidence |
|--------|-----------|------|-----------|
| THAAD | 200+ | Terminal BMD | 75% |
| Patriot PAC-3 MSE | 35+ | SAM/BMD | 80% |

---

## Troubleshooting

### Issue: Model Import Errors

**Problem:**
```
ImportError: cannot import name 'SM6Model'
```

**Solution:**
```bash
cd actual-f35-kill
python3 us_2025_defense_systems.py  # Verify models work
```

---

## Classification and Distribution

**Repository Classification:** UNCLASSIFIED // PUBLIC RELEASE

**Raytheon Use:**
- ✅ Safe for unclassified analysis
- ✅ No export control violations
- ✅ Can modify with internal data (keep internal)
- ❌ DO NOT upload classified data

---

**Last Updated:** 2026-01-04
**Version:** 1.0
**Classification:** UNCLASSIFIED // PUBLIC RELEASE
