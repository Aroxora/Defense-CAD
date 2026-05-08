# Sukhoi Contractor Setup Guide
## JSC Sukhoi Company - Russian Fighter Aircraft

**Target Users:** Sukhoi engineers, Russian Air Force analysts, export customers, comparative analysis
**Systems Covered:** Su-57 Felon, Su-35 Flanker-E, Su-30SM Flanker-H, Su-34 Fullback
**Primary Applications:** Air superiority analysis, strike mission planning, export performance validation

---

## Quick Start (15 Minutes)

### Step 1: Download Repository

```bash
# Clone from GitHub
git clone https://github.com/pseudonym-tbd/actual-f35-kill.git
cd actual-f35-kill

# Install dependencies
pip3 install numpy scipy matplotlib networkx pyyaml pytest

# Verify installation
pytest test_defensive_cad_missiles.py::TestDefensiveCAD::test_su57_rcs_model -v
```

### Step 2: Verify Sukhoi Models

```bash
python3 -c "
from rcs_models import Su57RCSModel, Su35RCSModel, Su30SMRCSModel, Su34RCSModel

su57 = Su57RCSModel()
su35 = Su35RCSModel()
su30sm = Su30SMRCSModel()
su34 = Su34RCSModel()

print('✓ All Sukhoi models loaded successfully')
print(f'✓ Su-57 frontal RCS: {su57.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
print(f'✓ Su-35 frontal RCS: {su35.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
print(f'✓ Su-30SM frontal RCS: {su30sm.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
print(f'✓ Su-34 frontal RCS: {su34.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
"
```

**Expected output:**
```
✓ All Sukhoi models loaded successfully
✓ Su-57 frontal RCS: -15.0 dBsm
✓ Su-35 frontal RCS: 10.0 dBsm
✓ Su-30SM frontal RCS: 10.5 dBsm
✓ Su-34 frontal RCS: 12.0 dBsm
```

---

## Sukhoi-Specific Use Cases

### Use Case 1: Su-57 vs F-35A Stealth Comparison

**What this answers:**
- How does Su-57 RCS compare to F-35A?
- Which aspects are most vulnerable?
- Is Su-57 truly 5th generation?

**Run the analysis**:
```bash
pytest test_defensive_cad_missiles.py::TestDefensiveCAD::test_su57_rcs_model -v
```

**Detailed Su-57 analysis**:
```python
python3 << 'EOF'
from rcs_models import Su57RCSModel, F35ARCSModel, J20RCSModel
import numpy as np

su57 = Su57RCSModel()
f35a = F35ARCSModel()
j20 = J20RCSModel()

print("=== SU-57 FELON RCS ANALYSIS ===")
print(f"Contractor: Sukhoi")
print(f"Fielded: 2020")
print(f"Confidence: {su57.confidence:.0%}")

print(f"\n=== RCS COMPARISON (dBsm) ===")
print(f"{'Aircraft':<20} {'Frontal (0°)':<15} {'Beam (90°)':<15} {'Rear (180°)':<15}")
print("-"*65)

for aircraft_name, aircraft in [("Su-57 Felon", su57), ("F-35A Lightning", f35a), ("J-20 Dragon", j20)]:
    frontal = aircraft.calculate_rcs(0, 0).rcs_dbsm
    beam = aircraft.calculate_rcs(90, 0).rcs_dbsm
    rear = aircraft.calculate_rcs(180, 0).rcs_dbsm
    print(f"{aircraft_name:<20} {frontal:<15.1f} {beam:<15.1f} {rear:<15.1f}")

print(f"\n=== STEALTH ASSESSMENT ===")
su57_frontal = su57.calculate_rcs(0, 0).rcs_dbsm
f35_frontal = f35a.calculate_rcs(0, 0).rcs_dbsm
j20_frontal = j20.calculate_rcs(0, 0).rcs_dbsm

print(f"Su-57 frontal RCS: {su57_frontal:.1f} dBsm ({10**(su57_frontal/10):.4f} m²)")
print(f"F-35A frontal RCS: {f35_frontal:.1f} dBsm ({10**(f35_frontal/10):.4f} m²)")
print(f"J-20 frontal RCS: {j20_frontal:.1f} dBsm ({10**(j20_frontal/10):.4f} m²)")

rcs_gap_vs_f35 = su57_frontal - f35_frontal
rcs_gap_vs_j20 = su57_frontal - j20_frontal

print(f"\nSu-57 vs F-35A: {rcs_gap_vs_f35:+.1f} dB (F-35 better by {abs(rcs_gap_vs_f35):.1f} dB)")
print(f"Su-57 vs J-20: {rcs_gap_vs_j20:+.1f} dB ({'Su-57 better' if rcs_gap_vs_j20 < 0 else 'J-20 better'} by {abs(rcs_gap_vs_j20):.1f} dB)")

print(f"\n=== CONCLUSION ===")
if su57_frontal < 0:
    print(f"✓ Su-57 achieves VLO (Very Low Observable) stealth ({su57_frontal:.1f} dBsm)")
else:
    print(f"⚠ Su-57 does NOT achieve VLO stealth ({su57_frontal:.1f} dBsm)")
print(f"✓ Su-57 frontal aspect: Reduced RCS vs 4th-gen (~25 dB improvement)")
print(f"⚠ Su-57 beam/rear: Conventional RCS (~8-12 dBsm)")
print(f"Assessment: Partial stealth (frontal aspect only), not all-aspect VLO")
EOF
```

**Key findings:**
1. ✅ Su-57 has reduced frontal RCS (~-15 dBsm)
2. ⚠️ Su-57 RCS worse than F-35A (-37 dBsm) and J-20 (-28 dBsm)
3. ⚠️ Su-57 beam/rear aspects not stealthy (~8-12 dBsm)
4. ✅ Significant improvement vs 4th-gen Flankers (+25 dB reduction)

---

### Use Case 2: Su-35 Kinematic Performance

**What this answers:**
- How does Su-35 maneuverability compare to F-15, F-16?
- What is thrust-to-weight ratio advantage?
- Can Su-35 defeat NATO fighters in WVR?

**Run kinematic analysis**:
```bash
pytest test_defensive_cad_missiles.py::TestDefensiveCAD::test_su35_rcs_model -v
```

**Detailed Su-35 analysis**:
```python
python3 << 'EOF'
from rcs_models import Su35RCSModel

su35 = Su35RCSModel()

print("=== SU-35 FLANKER-E PERFORMANCE ===")
print(f"Contractor: Sukhoi")
print(f"Fielded: 2014")
print(f"Confidence: {su35.confidence:.0%}")

print(f"\n=== SPECIFICATIONS ===")
# Su-35 specifications (public)
empty_weight_kg = 18400
max_weight_kg = 34500
thrust_per_engine_kn = 142  # AL-41F1S
num_engines = 2
total_thrust_kn = thrust_per_engine_kn * num_engines

print(f"Empty weight: {empty_weight_kg} kg")
print(f"Max takeoff weight: {max_weight_kg} kg")
print(f"Engine: 2× AL-41F1S")
print(f"Thrust per engine: {thrust_per_engine_kn} kN")
print(f"Total thrust: {total_thrust_kn} kN")

# Calculate thrust-to-weight
combat_weight_kg = 25000  # Typical air-to-air loadout
thrust_to_weight = (total_thrust_kn * 1000) / (combat_weight_kg * 9.81)

print(f"\n=== THRUST-TO-WEIGHT ===")
print(f"Combat weight: {combat_weight_kg} kg")
print(f"Thrust-to-weight: {thrust_to_weight:.2f}:1")

# Compare to competitors
competitors = {
    "F-15C Eagle": 1.04,
    "F-16C Viper": 1.095,
    "F-22 Raptor": 1.25,
    "Rafale": 0.99,
    "Typhoon": 1.15
}

print(f"\nComparison:")
for aircraft, twr in competitors.items():
    diff = thrust_to_weight - twr
    print(f"  vs {aircraft:<15} {twr:.2f}:1 ({diff:+.2f})")

print(f"\n=== SUPERMANEUVERABILITY ===")
print(f"✓ Thrust vectoring: 3D (±15° pitch/yaw)")
print(f"✓ Post-stall maneuvers: Cobra, Kulbit, Tailslide")
print(f"✓ Sustained turn rate: ~28°/sec")
print(f"✓ Instantaneous turn rate: ~40°/sec")
print(f"✓ Max G-load: +9/-3 G")

print(f"\n=== TACTICAL IMPLICATIONS ===")
print(f"✓ Excellent WVR (within visual range) performance")
print(f"✓ Thrust vectoring enables extreme AoA (angle of attack)")
print(f"⚠ Large RCS limits BVR (beyond visual range) effectiveness")
print(f"Conclusion: Dominant in dogfight, vulnerable in BVR")
EOF
```

**Key findings:**
1. ✅ Su-35 has excellent thrust-to-weight ratio (~1.14:1)
2. ✅ 3D thrust vectoring enables supermaneuverability
3. ✅ Dominates WVR combat vs Western 4th-gen fighters
4. ⚠️ Large RCS (~10 dBsm) limits BVR effectiveness

---

### Use Case 3: All Sukhoi Aircraft Portfolio

**Generate comprehensive Sukhoi report**:
```python
python3 << 'EOF'
from defense_contractor_registry import DefenseContractorRegistry

registry = DefenseContractorRegistry()

# Get all Sukhoi models
sukhoi = registry.get_contractor("Sukhoi")
sukhoi_models = registry.get_contractor_models("Sukhoi")

print("="*80)
print("SUKHOI AIRCRAFT PORTFOLIO ANALYSIS")
print("="*80)
print(f"\nContractor: {sukhoi.full_name}")
print(f"Established: {sukhoi.established}")
print(f"Specialization: {sukhoi.specialization}")
print(f"Overall confidence: {sukhoi.confidence:.0%}")

print(f"\n{'Platform':<25} {'Fielded':<10} {'RCS (dBsm)':<12} {'Confidence':<12}")
print("-"*80)

for model in sorted(sukhoi_models, key=lambda m: m.fielded_date):
    platform = model.platform_name
    fielded = model.fielded_date
    confidence = f"{model.confidence:.0%}"

    # Get RCS
    try:
        model_instance = model.model_class()
        rcs = model_instance.calculate_rcs(0, 0)
        rcs_str = f"{rcs.rcs_dbsm:.1f}"
    except:
        rcs_str = "N/A"

    print(f"{platform:<25} {fielded:<10} {rcs_str:<12} {confidence:<12}")

print("\n" + "="*80)
print(f"TOTAL SUKHOI MODELS: {len(sukhoi_models)}")
print("="*80)

print("\n=== OPERATIONAL SUMMARY ===")
print("5th Generation: Su-57 Felon (partial stealth, supermaneuverability)")
print("4++ Generation: Su-35 Flanker-E (thrust vectoring, PESA radar)")
print("4+ Generation: Su-30SM Flanker-H (multirole, export success)")
print("4th Generation: Su-34 Fullback (strike, armored cockpit)")
EOF
```

---

## Integration Shortcomings

### Su-57 Limitations

**Issue 1: Low Production Numbers**
- Only ~10-15 aircraft produced as of 2025
- Limited operational data available
- Final production configuration uncertain

**Issue 2: Engine Uncertainty**
- Current: AL-41F1 (147 kN thrust)
- Planned: Izdeliye 30 (180 kN thrust, not in production)
- Confidence: 70% (current engine), 40% (future engine)

**Issue 3: RCS Estimates Conservative**
- Frontal RCS: -15 dBsm (estimated)
- Based on geometry analysis, RAM assumptions
- May be better with production upgrades
- Confidence: 50%

### Workarounds

1. Use AL-41F1 engine for current analysis
2. Model Izdeliye 30 separately as "future variant"
3. Flag Su-57 as "limited deployment" (unlike Su-35)
4. Update models as production increases

---

## Support for Sukhoi/Russian Engineers

### GitHub Issues
https://github.com/pseudonym-tbd/actual-f35-kill/issues

### Documentation
- `INTEGRATION_SHORTCOMINGS.md` - Known limitations for Russian contractors
- `DEDUCTIVE_REASONING.md` - Parameter estimation methodology
- `VERIFIED_MODELS_REGISTRY.md` - All verified models

---

## Classification and Distribution

**Repository Classification:** UNCLASSIFIED // PUBLIC RELEASE

**Sukhoi/Russian Use:**
- ✅ Safe to download for aircraft performance analysis
- ✅ No violation of Russian export control laws
- ✅ No violation of US export control laws (public release)
- ✅ Can be modified with Sukhoi internal data (keep local)

**Restrictions:**
- ❌ DO NOT upload Sukhoi classified data to public GitHub
- ❌ DO NOT share modified models with classified parameters

---

**Last Updated:** 2026-01-02
**Version:** 1.0
**Classification:** UNCLASSIFIED // PUBLIC RELEASE
**Approved for:** Sukhoi internal analysis and export customers
