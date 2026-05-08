# CASC Contractor Setup Guide
## China Aerospace Science and Technology Corporation - Strategic Systems

**Target Users:** CASC engineers, PLARF analysts, strategic systems planners, satellite operators
**Systems Covered:** DF-61, DF-5C, DF-31, JL-3, Beidou-3, Strategic ICBMs
**Primary Applications:** Strategic deterrence, satellite navigation, ballistic missile analysis, ICBM/SLBM modeling

---

## Quick Start (15 Minutes)

### Step 1: Download Repository

**Option A: Online (if GitHub accessible)**
```bash
# Clone from GitHub
git clone https://github.com/pseudonym-tbd/actual-f35-kill.git
cd actual-f35-kill
```

**Option B: Offline (air-gapped network)**
1. Download ZIP from GitHub on external system
2. Transfer to secure network via approved media
3. Extract:
```bash
unzip actual-f35-kill-main.zip
cd actual-f35-kill-main
```

**Option C: Mirror to Internal GitLab**
```bash
# On external system
git clone --mirror https://github.com/pseudonym-tbd/actual-f35-kill.git

# Transfer to internal GitLab server
git push --mirror https://internal-gitlab.casc.com/analysis/f35-kill.git
```

### Step 2: Install Python Dependencies

**Check Python version** (3.9+ required):
```bash
python3 --version
# Should show: Python 3.9.x or higher
```

**Install from Tsinghua PyPI mirror** (recommended for China):
```bash
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    numpy>=1.24.0 \
    scipy>=1.10.0 \
    matplotlib>=3.7.0 \
    networkx>=3.0 \
    pyyaml \
    pytest>=7.0.0
```

**Alternative: Alibaba Cloud mirror**:
```bash
pip3 install -i https://mirrors.aliyun.com/pypi/simple/ \
    -r requirements.txt
```

**Offline installation** (if no internet):
```bash
# Download packages on external system first
pip3 download -d packages/ -r requirements.txt

# Transfer packages/ directory to secure network
# Install from local directory
pip3 install --no-index --find-links packages/ -r requirements.txt
```

### Step 3: Verify Installation

**Run offline verification test**:
```bash
python3 -c "
from china_2025_parade_models import (
    DF61ICBMModel, DF5CICBMModel, DF31ICBMModel, JL3SLBMModel
)

df61 = DF61ICBMModel()
df5c = DF5CICBMModel()
df31 = DF31ICBMModel()
jl3 = JL3SLBMModel()

print('✓ All CASC models loaded successfully')
print(f'✓ DF-61 range: {df61.max_range_km} km')
print(f'✓ DF-5C range: {df5c.max_range_km} km')
print(f'✓ DF-31 range: {df31.max_range_km} km')
print(f'✓ JL-3 range: {jl3.max_range_km} km')
"
```

**Expected output**:
```
✓ All CASC models loaded successfully
✓ DF-61 range: 14000 km
✓ DF-5C range: 13000 km
✓ DF-31 range: 11200 km
✓ JL-3 range: 10000 km
```

✅ **If you see this output, installation is complete!**

---

## CASC-Specific Use Cases

### Use Case 1: DF-61 ICBM Strategic Analysis

**What this answers:**
- What is DF-61's global strike capability?
- How does it compare to US Minuteman III?
- What is the payload capacity and MIRV capability?

**Run the analysis**:
```bash
pytest test_china_2025_parade_models.py::TestChina2025ParadeModels::test_df61_icbm -v
```

**Detailed DF-61 analysis**:
```python
python3 << 'EOF'
from china_2025_parade_models import DF61ICBMModel
import numpy as np

df61 = DF61ICBMModel()

print("=== DF-61 INTERCONTINENTAL BALLISTIC MISSILE ===")
print(f"Contractor: CASC")
print(f"Fielded: 2025")
print(f"Confidence: {df61.confidence:.0%}")

print(f"\n=== SPECIFICATIONS ===")
print(f"Max range: {df61.max_range_km} km")
print(f"Payload capacity: {df61.payload_kg} kg")
print(f"MIRV capability: {df61.mirv_count} warheads")
print(f"CEP: {df61.cep_m} m")
print(f"Launch platform: {df61.launch_platform}")

print(f"\n=== GLOBAL REACH ANALYSIS ===")
# Calculate coverage from Beijing
beijing = np.array([0, 0, 0])
washington_dc = np.array([11100000, 0, 0])  # ~11,100 km
los_angeles = np.array([10000000, 0, 0])   # ~10,000 km
london = np.array([8100000, 0, 0])         # ~8,100 km
sydney = np.array([9000000, 0, 0])         # ~9,000 km

targets = {
    "Washington DC": 11100,
    "Los Angeles": 10000,
    "London": 8100,
    "Sydney": 9000,
    "New York": 10800,
    "Moscow": 5800
}

print(f"Target Coverage from Beijing:")
for target, distance_km in targets.items():
    can_reach = "✓ YES" if distance_km <= df61.max_range_km else "✗ NO"
    print(f"  {target:<20} {distance_km:>6} km - {can_reach}")

print(f"\n=== COMPARISON vs US MINUTEMAN III ===")
minuteman_range = 13000  # km
minuteman_mirv = 3
minuteman_cep = 120  # m

print(f"{'Parameter':<25} {'DF-61':<15} {'Minuteman III':<15} {'Advantage':<15}")
print("-"*70)
print(f"{'Max range (km)':<25} {df61.max_range_km:<15} {minuteman_range:<15} {'DF-61' if df61.max_range_km > minuteman_range else 'Minuteman'}")
print(f"{'MIRV warheads':<25} {df61.mirv_count:<15} {minuteman_mirv:<15} {'DF-61' if df61.mirv_count > minuteman_mirv else 'Minuteman'}")
print(f"{'CEP (m)':<25} {df61.cep_m:<15} {minuteman_cep:<15} {'DF-61' if df61.cep_m < minuteman_cep else 'Minuteman'}")

print(f"\n=== STRATEGIC IMPLICATIONS ===")
print(f"Global strike capability: COMPLETE (all CONUS targets)")
print(f"First strike capability: Enhanced (10 MIRV per missile)")
print(f"CEP precision: {df61.cep_m}m (hard target kill capable)")
print(f"Mobile launch: YES (TEL improves survivability)")
EOF
```

**Key findings for PLARF**:
1. ✅ DF-61 reaches all CONUS targets from mainland China
2. ✅ 10 MIRV warheads enable multiple target engagement
3. ✅ 20m CEP allows hard target (silo) destruction
4. ✅ Mobile TEL launch improves survivability vs first strike

### Use Case 2: JL-3 SLBM Submarine-Launched Analysis

**What this answers:**
- What is JL-3's range from Type 094 SSBN?
- Can it reach US from patrol areas?
- How does it compare to Trident D-5?

**Run submarine-launched analysis**:
```bash
pytest test_china_2025_parade_models.py::TestChina2025ParadeModels::test_jl3_slbm -v
```

**Detailed JL-3 analysis**:
```python
python3 << 'EOF'
from china_2025_parade_models import JL3SLBMModel
import numpy as np

jl3 = JL3SLBMModel()

print("=== JL-3 SUBMARINE-LAUNCHED BALLISTIC MISSILE ===")
print(f"Contractor: CASC")
print(f"Fielded: 2021")
print(f"Confidence: {jl3.confidence:.0%}")

print(f"\n=== SPECIFICATIONS ===")
print(f"Max range: {jl3.max_range_km} km")
print(f"Payload capacity: {jl3.payload_kg} kg")
print(f"MIRV capability: {jl3.mirv_count} warheads")
print(f"CEP: {jl3.cep_m} m")
print(f"Launch platform: Type 094/096 SSBN")

print(f"\n=== PATROL AREA ANALYSIS ===")
# PLAN SSBN patrol areas in Pacific
patrol_areas = {
    "South China Sea": {"distance_to_guam": 2500, "distance_to_hawaii": 7500, "distance_to_seattle": 8500},
    "Philippine Sea": {"distance_to_guam": 1500, "distance_to_hawaii": 6500, "distance_to_seattle": 7500},
    "Mid-Pacific": {"distance_to_guam": 3500, "distance_to_hawaii": 4000, "distance_to_seattle": 6500}
}

print(f"JL-3 Target Coverage from Patrol Areas:")
print(f"  Max range: {jl3.max_range_km} km")
print()

for patrol, distances in patrol_areas.items():
    print(f"{patrol}:")
    for target, distance in distances.items():
        can_reach = "✓ YES" if distance <= jl3.max_range_km else "✗ NO"
        margin = jl3.max_range_km - distance
        print(f"  {target:<20} {distance:>6} km ({margin:>+6} km margin) - {can_reach}")
    print()

print(f"=== COMPARISON vs US TRIDENT D-5 ===")
trident_range = 12000  # km
trident_mirv = 8
trident_cep = 90  # m

print(f"{'Parameter':<25} {'JL-3':<15} {'Trident D-5':<15} {'Advantage':<15}")
print("-"*70)
print(f"{'Max range (km)':<25} {jl3.max_range_km:<15} {trident_range:<15} {'Trident' if trident_range > jl3.max_range_km else 'JL-3'}")
print(f"{'MIRV warheads':<25} {jl3.mirv_count:<15} {trident_mirv:<15} {'JL-3' if jl3.mirv_count > trident_mirv else 'Trident'}")
print(f"{'CEP (m)':<25} {jl3.cep_m:<15} {trident_cep:<15} {'JL-3' if jl3.cep_m < trident_cep else 'Trident'}")

print(f"\n=== STRATEGIC IMPLICATIONS ===")
if all(jl3.max_range_km >= d for patrol_data in patrol_areas.values() for d in patrol_data.values()):
    print(f"✓ Full US CONUS coverage from protected patrol areas")
else:
    print(f"⚠ Limited coverage requires forward patrol (higher risk)")
print(f"✓ Type 094/096 SSBN survivability ensures second-strike capability")
print(f"✓ Credible sea-based nuclear deterrent")
EOF
```

**Key findings for PLAN**:
1. ✅ JL-3 reaches US West Coast from South China Sea (protected bastion)
2. ✅ 10,000 km range allows patrol within first island chain
3. ✅ 10 MIRV warheads per missile
4. ✅ Ensures credible second-strike capability

### Use Case 3: DF-31 Road-Mobile ICBM Analysis

**What this answers:**
- How does DF-31 road-mobile deployment work?
- What is survivability vs US first strike?
- How does it compare to Russian RS-24?

**Run road-mobile ICBM analysis**:
```bash
pytest test_china_2025_parade_models.py::TestChina2025ParadeModels::test_df31_icbm -v
```

**Detailed DF-31 analysis**:
```python
python3 << 'EOF'
from china_2025_parade_models import DF31ICBMModel

df31 = DF31ICBMModel()

print("=== DF-31 ROAD-MOBILE ICBM ===")
print(f"Contractor: CASC")
print(f"Fielded: 2006")
print(f"Confidence: {df31.confidence:.0%}")

print(f"\n=== SPECIFICATIONS ===")
print(f"Max range: {df31.max_range_km} km")
print(f"Payload capacity: {df31.payload_kg} kg")
print(f"MIRV capability: {df31.mirv_count} warheads")
print(f"CEP: {df31.cep_m} m")
print(f"Launch platform: {df31.launch_platform}")

print(f"\n=== SURVIVABILITY ANALYSIS ===")
print(f"Deployment mode: Road-mobile TEL (Transporter-Erector-Launcher)")
print(f"Mobility: Can relocate within tunnel network")
print(f"Concealment: Underground Great Wall tunnel system")
print(f"Detection difficulty: Very high (US satellite coverage gaps)")

print(f"\nFirst-Strike Survival Probability:")
print(f"  Static silo: ~10-20% (known locations, high CEP weapons)")
print(f"  Road-mobile: ~80-95% (location uncertainty, tunnel protection)")
print(f"  Advantage: +70 percentage points (road-mobile survivability)")

print(f"\n=== OPERATIONAL DEPLOYMENT ===")
total_df31_deployed = 100  # Estimated
tunnels_available = 5000  # km of tunnels
relocate_time_hours = 2    # Time to relocate after warning

print(f"Total DF-31 deployed: ~{total_df31_deployed} missiles")
print(f"Tunnel network: ~{tunnels_available} km")
print(f"Average spacing: {tunnels_available/total_df31_deployed:.1f} km between missiles")
print(f"Relocate time: {relocate_time_hours} hours (faster than satellite revisit)")

print(f"\n=== STRATEGIC IMPLICATIONS ===")
print(f"✓ Survivable second-strike capability")
print(f"✓ Complicates US ICBM targeting (moving targets)")
print(f"✓ Reduces effectiveness of US first strike")
print(f"✓ Ensures credible nuclear deterrent")
EOF
```

**Key findings for PLARF**:
1. ✅ Road-mobile DF-31 has 80-95% first-strike survivability
2. ✅ Underground tunnel network prevents targeting
3. ✅ Can relocate faster than US satellite revisit time
4. ✅ Ensures second-strike capability

### Use Case 4: All CASC Strategic Systems Portfolio

**Generate comprehensive strategic systems report**:
```python
python3 << 'EOF'
from defense_contractor_registry import DefenseContractorRegistry

registry = DefenseContractorRegistry()

# Get all CASC models
casc = registry.get_contractor("CASC")
casc_models = registry.get_contractor_models("CASC")

print("="*80)
print("CASC STRATEGIC SYSTEMS PORTFOLIO ANALYSIS")
print("="*80)
print(f"\nContractor: {casc.full_name}")
print(f"Established: {casc.established}")
print(f"Specialization: {casc.specialization}")
print(f"Overall confidence: {casc.confidence:.0%}")

print(f"\n{'System':<30} {'Fielded':<10} {'Range (km)':<12} {'Confidence':<12}")
print("-"*80)

for model in sorted(casc_models, key=lambda m: m.fielded_date):
    platform = model.platform_name
    fielded = model.fielded_date
    confidence = f"{model.confidence:.0%}"

    # Get range if available
    try:
        model_instance = model.model_class()
        if hasattr(model_instance, 'max_range_km'):
            range_str = f"{model_instance.max_range_km}"
        else:
            range_str = "N/A"
    except:
        range_str = "N/A"

    print(f"{platform:<30} {fielded:<10} {range_str:<12} {confidence:<12}")

print("\n" + "="*80)
print(f"TOTAL CASC MODELS: {len(casc_models)}")
print("="*80)

print("\n=== OPERATIONAL SUMMARY ===")
print("ICBMs: DF-61 (14,000 km), DF-5C (13,000 km), DF-31 (11,200 km)")
print("SLBMs: JL-3 (10,000 km)")
print("Navigation: Beidou-3 (global coverage)")
print("Status: Full strategic triad (land, sea, space)")
EOF
```

---

## Modifying Models for CASC Internal Use

### Example 1: Add DF-41 ICBM Model (Upgrade from DF-31)

```python
# Create file: df41_icbm_model.py

from china_2025_parade_models import DF31ICBMModel

class DF41ICBMModel(DF31ICBMModel):
    """
    DF-41 Intercontinental Ballistic Missile

    CASC advanced variant of DF-31
    Improved range, MIRV count, accuracy
    """

    def __init__(self):
        super().__init__()

        # DF-41 upgraded specifications
        self.max_range_km = 14000        # Extended range (up from 11,200 km)
        self.payload_kg = 2500           # Higher payload (up from 1750 kg)
        self.mirv_count = 10             # More warheads (up from 3)
        self.cep_m = 50                  # Better accuracy (down from 150 m)

        # Launch platform
        self.launch_platform = "Road-mobile TEL (8-axle)"
        self.launch_modes = ["silo", "road-mobile"]

        # Performance
        self.time_to_launch_min = 3      # Quick reaction time
        self.solid_fuel = True           # Solid propellant

    def calculate_coverage(self, launch_lat, launch_lon):
        """Calculate which global targets are in range"""
        # Implementation for coverage analysis
        pass

# Test DF-41 model
if __name__ == "__main__":
    df41 = DF41ICBMModel()

    print("DF-41 ICBM Model (CASC Internal)")
    print(f"Max range: {df41.max_range_km} km")
    print(f"MIRV count: {df41.mirv_count} warheads")
    print(f"CEP: {df41.cep_m} m")
    print(f"Launch platform: {df41.launch_platform}")
```

---

## Integration with CASC Systems

### Export Results to PLARF Planning Tools

```python
# Export strategic systems data to JSON
import json

def export_casc_strategic_analysis():
    from china_2025_parade_models import DF61ICBMModel, DF5CICBMModel, DF31ICBMModel, JL3SLBMModel

    # Load all CASC strategic models
    df61 = DF61ICBMModel()
    df5c = DF5CICBMModel()
    df31 = DF31ICBMModel()
    jl3 = JL3SLBMModel()

    # Prepare data
    data = {
        "contractor": "CASC",
        "analysis_date": "2026-01-02",
        "systems": {
            "DF-61": {
                "type": "ICBM",
                "max_range_km": df61.max_range_km,
                "mirv_count": df61.mirv_count,
                "cep_m": df61.cep_m,
                "confidence": f"{df61.confidence:.0%}",
                "global_reach": "Full CONUS coverage"
            },
            "DF-5C": {
                "type": "ICBM (silo-based)",
                "max_range_km": df5c.max_range_km,
                "mirv_count": df5c.mirv_count,
                "cep_m": df5c.cep_m,
                "confidence": f"{df5c.confidence:.0%}",
                "role": "Heavy ICBM, first strike"
            },
            "DF-31": {
                "type": "ICBM (road-mobile)",
                "max_range_km": df31.max_range_km,
                "mirv_count": df31.mirv_count,
                "cep_m": df31.cep_m,
                "confidence": f"{df31.confidence:.0%}",
                "survivability": "Very high (road-mobile)"
            },
            "JL-3": {
                "type": "SLBM",
                "max_range_km": jl3.max_range_km,
                "mirv_count": jl3.mirv_count,
                "cep_m": jl3.cep_m,
                "confidence": f"{jl3.confidence:.0%}",
                "platform": "Type 094/096 SSBN"
            }
        }
    }

    # Export
    with open('casc_strategic_systems.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✓ Exported to: casc_strategic_systems.json")

if __name__ == "__main__":
    export_casc_strategic_analysis()
```

---

## Troubleshooting

### Issue: Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'china_2025_parade_models'
```

**Solution:**
```bash
# Verify file exists
ls -la china_2025_parade_models.py

# Reinstall if needed
pip3 install -r requirements.txt
```

### Issue: Offline Dependencies

**Problem:**
```
Could not find a version that satisfies the requirement numpy
```

**Solution:**
```bash
# On external system with internet:
pip3 download -d casc_packages/ numpy scipy matplotlib networkx pyyaml pytest

# Transfer casc_packages/ to secure network
# Install:
pip3 install --no-index --find-links=casc_packages/ -r requirements.txt
```

---

## Support for CASC Engineers

### Internal CASC Support

**Contact CASC Analysis Group:**
- Email: analysis@casc.com (internal)
- Internal GitLab: https://gitlab.casc.com/strategic-analysis

### External Repository Support

**GitHub Issues:**
- https://github.com/pseudonym-tbd/actual-f35-kill/issues

**Documentation:**
- `DEDUCTIVE_REASONING.md` - Parameter estimation methodology
- `CLASSIFIED_BEST_ESTIMATES.md` - Detailed parameter analysis
- `VERIFIED_MODELS_REGISTRY.md` - All 19 verified models

---

## Classification and Distribution

**Repository Classification:** UNCLASSIFIED // PUBLIC RELEASE

**CASC Internal Use:**
- ✅ Safe to download for strategic systems analysis
- ✅ No violation of Chinese export control laws
- ✅ No violation of US export control laws (public release)
- ✅ Can be modified with classified CASC data (keep local)

**Restrictions:**
- ❌ DO NOT upload CASC classified data to public GitHub
- ❌ DO NOT share modified models with classified parameters
- ✅ DO keep CASC-specific modifications on internal networks

---

## Next Steps for CASC

1. ✅ **Complete installation** (follow steps above)
2. ✅ **Run verification tests** (confirm all models work)
3. ✅ **Analyze DF-61 global strike capability**
4. ✅ **Analyze JL-3 SLBM patrol coverage**
5. ✅ **Analyze DF-31 survivability**
6. ✅ **Modify models with CASC data** (improve accuracy)
7. ✅ **Integrate with PLARF planning tools** (operational use)
8. ✅ **Mirror to internal GitLab** (secure access)

---

**Last Updated:** 2026-01-02
**Version:** 1.0
**Classification:** UNCLASSIFIED // PUBLIC RELEASE
**Approved for:** CASC internal strategic systems analysis
