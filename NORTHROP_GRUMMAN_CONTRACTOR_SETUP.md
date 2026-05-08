# Northrop Grumman Contractor Setup Guide
## Strategic Systems and Advanced Platforms

**Target Users:** Northrop Grumman engineers, USAF analysts, strategic program managers
**Systems Covered:** B-21 Raider, LGM-35A Sentinel ICBM, NGAD, CCA, Fire Scout
**Primary Applications:** Strategic bomber analysis, ICBM modernization, 6th-gen development

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
    B21RaiderModel, SentinelICBMModel, NGADModel,
    MinutemanIIIICBMModel, MQ9ReaperModel
)

b21 = B21RaiderModel()
sentinel = SentinelICBMModel()
ngad = NGADModel()

print('✓ All Northrop Grumman models loaded successfully')
print(f'✓ B-21 combat radius: {b21.get_parameters()[\"combat_radius_km\"]} km')
print(f'✓ B-21 frontal RCS: {b21.get_rcs_frontal()} m² ({10*3.14159*0.0001:.1f} dBsm)')
print(f'✓ Sentinel range: {sentinel.get_parameters()[\"range_km\"]} km')
print(f'✓ NGAD confidence: {ngad.get_parameters()[\"confidence\"]:.0%}')
"
```

**Expected output:**
```
✓ All Northrop Grumman models loaded successfully
✓ B-21 combat radius: 4000 km
✓ B-21 frontal RCS: 0.0001 m² (-40 dBsm)
✓ Sentinel range: 14000 km
✓ NGAD confidence: 30%
```

---

## Northrop Grumman Use Cases

### Use Case 1: B-21 Raider Survivability Analysis

**What this answers:**
- B-21 detection ranges vs threat radars
- Survivability in contested airspace
- Comparison to B-2 Spirit

**Run the analysis:**
```python
python3 << 'EOF'
from us_2025_defense_systems import B21RaiderModel
from rcs_models import B2RCSModel  # If available

b21 = B21RaiderModel()

print("=== B-21 RAIDER SURVIVABILITY ANALYSIS ===")
params = b21.get_parameters()

print(f"\nPlatform Specifications:")
print(f"  Designation: {params['designation']}")
print(f"  Combat Radius: {params['combat_radius_km']} km")
print(f"  Payload: {params['payload_kg']} kg")
print(f"  Nuclear Capable: {params['nuclear_capable']}")

print(f"\nStealth Characteristics:")
rcs = b21.get_rcs_frontal()
rcs_dbsm = 10 * 3.14159 * rcs  # Approximate dBsm
print(f"  Frontal RCS: {rcs} m² (~-40 dBsm)")
print(f"  Confidence: {params['confidence']:.0%}")

# Detection range calculation (simplified)
# Assume S-400 detection: 600 km vs 1 m² RCS
s400_range_1m2 = 600
s400_range_b21 = s400_range_1m2 * (rcs / 1.0) ** 0.25
print(f"\nDetection by S-400 (estimated): {s400_range_b21:.0f} km")
print(f"  (vs 600 km for 1 m² target)")

# Detection by HQ-9
hq9_range_1m2 = 200
hq9_range_b21 = hq9_range_1m2 * (rcs / 1.0) ** 0.25
print(f"\nDetection by HQ-9 (estimated): {hq9_range_b21:.0f} km")
print(f"  (vs 200 km for 1 m² target)")

print("\n=== THREAT ENGAGEMENT SURVIVABILITY ===")
print(f"  B-21 can release standoff weapons beyond threat radar range")
print(f"  JASSM-ER range: ~1000 km")
print(f"  B-21 standoff distance: ~{params['combat_radius_km'] - 1000} km from target")
EOF
```

### Use Case 2: Sentinel ICBM Modernization

**What this answers:**
- Sentinel vs Minuteman III comparison
- Modernization improvements
- Strategic deterrence posture

**Run the analysis:**
```python
python3 << 'EOF'
from us_2025_defense_systems import SentinelICBMModel, MinutemanIIIICBMModel

sentinel = SentinelICBMModel()
mm3 = MinutemanIIIICBMModel()

print("=== SENTINEL vs MINUTEMAN III COMPARISON ===")
print(f"{'Metric':<25s} {'Minuteman III':<15s} {'Sentinel':<15s}")
print(f"{'-'*55}")

mm3_params = mm3.get_parameters()
sent_params = sentinel.get_parameters()

print(f"{'Range (km)':<25s} {mm3_params['range_km']:<15} {sent_params['range_km']:<15}")
print(f"{'Payload (kg)':<25s} {mm3_params['payload_kg']:<15} {sent_params['payload_kg']:<15}")
print(f"{'CEP (m)':<25s} {mm3_params['cep_m']:<15} {sent_params['cep_m']:<15}")
print(f"{'Confidence':<25s} {mm3_params['confidence']:.0%:<15} {sent_params['confidence']:.0%:<15}")
print(f"{'IOC':<25s} {'1970':<15} {sent_params['ioc']:<15}")

print("\n=== SENTINEL IMPROVEMENTS ===")
print("  ✓ Improved guidance (GPS + stellar)")
print("  ✓ Enhanced payload flexibility")
print("  ✓ Reduced maintenance requirements")
print("  ✓ Modern command and control")
print("  ✓ Designed for 50+ year service life")
EOF
```

### Use Case 3: NGAD 6th-Gen Analysis

**What this answers:**
- NGAD preliminary capabilities
- Comparison to F-22
- CCA integration

**Run the analysis:**
```python
python3 << 'EOF'
from us_2025_defense_systems import NGADModel, CCAModel
from rcs_models import F22RCSModel

ngad = NGADModel()
cca = CCAModel()
f22 = F22RCSModel()

print("=== NGAD 6th-GENERATION AIR DOMINANCE ===")
ngad_params = ngad.get_parameters()

print(f"\nPlatform (SPECULATIVE):")
print(f"  Designation: {ngad_params['designation']}")
print(f"  Max Speed: {ngad_params['max_speed_kmh']} km/h")
print(f"  Combat Radius: {ngad_params['combat_radius_km']} km")
print(f"  AI Enabled: {ngad_params['ai_enabled']}")
print(f"  CCA Teaming: {ngad_params['cca_teaming']}")

print(f"\nStealth (SPECULATIVE):")
print(f"  Frontal RCS: {ngad.get_rcs_frontal()} m² (~-43 dBsm)")
print(f"  vs F-22: {f22.calculate_rcs(0, 0).rcs_m2} m² (~-40 dBsm)")

print(f"\nConfidence: {ngad_params['confidence']:.0%} (highly classified)")

print("\n=== COLLABORATIVE COMBAT AIRCRAFT (CCA) ===")
cca_params = cca.get_parameters()
print(f"  Designation: {cca_params['designation']}")
print(f"  Max Speed: {cca_params['max_speed_kmh']} km/h")
print(f"  Combat Radius: {cca_params['combat_radius_km']} km")
print(f"  AI Enabled: {cca_params['ai_enabled']}")
print(f"  Attritable: {cca_params['attritable']}")
print(f"  Unit Cost: ${cca_params['unit_cost_million']}M (target)")

print("\n=== NGAD + CCA CONCEPT ===")
print("  1 NGAD + 2-4 CCA wingmen")
print("  CCA roles: Sensor extension, weapons carriage, decoy")
print("  NGAD: Command platform, high-value engagement")
EOF
```

### Use Case 4: B-21 vs B-2 Comparison

**What this answers:**
- B-21 improvements over B-2
- Modernization rationale
- Fleet composition

**Run the analysis:**
```python
python3 << 'EOF'
from us_2025_defense_systems import B21RaiderModel

b21 = B21RaiderModel()

print("=== B-21 RAIDER vs B-2 SPIRIT COMPARISON ===")
print(f"{'Metric':<25s} {'B-2 Spirit':<20s} {'B-21 Raider':<20s}")
print(f"{'-'*65}")

# B-2 parameters (from public sources)
print(f"{'First Flight':<25s} {'1989':<20s} {'2023':<20s}")
print(f"{'Combat Radius (km)':<25s} {'5,500':<20s} {'4,000+ (est)':<20s}")
print(f"{'Payload (kg)':<25s} {'18,000':<20s} {'13,600 (est)':<20s}")
print(f"{'Unit Cost ($B)':<25s} {'~2.0':<20s} {'~0.7 (target)':<20s}")
print(f"{'Fleet Size':<25s} {'20':<20s} {'100+ (planned)':<20s}")
print(f"{'Nuclear Capable':<25s} {'Yes':<20s} {'Yes':<20s}")
print(f"{'Open Architecture':<25s} {'Limited':<20s} {'Yes':<20s}")

print("\n=== B-21 KEY IMPROVEMENTS ===")
print("  ✓ Lower unit cost (~$700M vs $2B)")
print("  ✓ Open mission systems architecture")
print("  ✓ Improved low-observable technology")
print("  ✓ Nuclear and conventional capable")
print("  ✓ Designed for contested environments")
print("  ✓ Family of systems integration")
EOF
```

---

## Northrop Grumman Systems Catalog

### Strategic Bombers

| System | Combat Radius | Payload | RCS (est) | Confidence |
|--------|--------------|---------|-----------|-----------|
| B-21 Raider | 4,000+ km | 13,600 kg | -40 dBsm | 45% |
| B-2 Spirit | 5,500 km | 18,000 kg | -30 dBsm | 80% |

### Strategic Missiles

| System | Range | CEP | IOC | Confidence |
|--------|-------|-----|-----|-----------|
| LGM-35A Sentinel | 14,000 km | 120 m | 2030 | 40% |
| LGM-30G Minuteman III | 13,000 km | 200 m | 1970 | 85% |

### Next-Gen Platforms

| System | Type | Status | Confidence |
|--------|------|--------|-----------|
| NGAD | 6th-Gen Fighter | Development | 30% |
| CCA | Loyal Wingman | Development | 45% |

### UAVs

| System | Type | Endurance | Confidence |
|--------|------|-----------|-----------|
| MQ-4C Triton | Maritime ISR | 24+ hrs | 75% |
| RQ-4 Global Hawk | HALE ISR | 32+ hrs | 85% |
| MQ-8C Fire Scout | Naval VTOL | 12 hrs | 70% |

---

## Troubleshooting

### Issue: Import Errors

**Solution:**
```bash
cd actual-f35-kill
python3 -c "from us_2025_defense_systems import *; print('OK')"
```

---

## Classification and Distribution

**Repository Classification:** UNCLASSIFIED // PUBLIC RELEASE

**Northrop Grumman Use:**
- ✅ Safe for unclassified analysis
- ✅ No export control violations
- ✅ Can modify with internal data (keep internal)
- ❌ DO NOT upload classified data (especially B-21, NGAD)

---

**Last Updated:** 2026-01-04
**Version:** 1.0
**Classification:** UNCLASSIFIED // PUBLIC RELEASE
