# Lockheed Martin Contractor Setup Guide
## F-35 Lightning II / F-22 Raptor / Hypersonic Programs

**Target Users:** Lockheed Martin engineers, USAF/USN analysts, F-35/F-22 program managers
**Systems Covered:** F-35A/B/C Lightning II, F-22A Raptor, AIM-260 JATM, LRHW, CPS
**Primary Applications:** Air superiority analysis, BVR engagement planning, J-20 threat assessment

---

## Quick Start (15 Minutes)

### Step 1: Download Repository

**Option A: Direct Clone**
```bash
# Clone from GitHub
git clone https://github.com/pseudonym-tbd/actual-f35-kill.git
cd actual-f35-kill
```

**Option B: Enterprise GitHub/GitLab Mirror**
```bash
# Clone to internal repository
git clone --mirror https://github.com/pseudonym-tbd/actual-f35-kill.git

# Push to internal server
git push --mirror https://gitlab.lockheedmartin.com/analysis/threat-assessment.git
```

### Step 2: Install Python Dependencies

**Check Python version** (3.9+ required):
```bash
python3 --version
# Should show: Python 3.9.x or higher
```

**Install dependencies:**
```bash
pip3 install numpy>=1.24.0 scipy>=1.10.0 matplotlib>=3.7.0 networkx>=3.0 pyyaml pytest>=7.0.0
```

**Or use requirements.txt:**
```bash
pip3 install -r requirements.txt
```

### Step 3: Verify Installation

**Run offline verification test:**
```bash
python3 -c "
from rcs_models import F35ARCSModel, F22RCSModel, J20RCSModel
from f22_radar_model import F22RadarModel
from aim260_targeting_model import AIM260TargetingModel

f35 = F35ARCSModel()
f22 = F22RCSModel()
j20 = J20RCSModel()
radar = F22RadarModel()
aim260 = AIM260TargetingModel()

print('✓ All Lockheed Martin models loaded successfully')
print(f'✓ F-35A frontal RCS: {f35.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
print(f'✓ F-22A frontal RCS: {f22.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
print(f'✓ J-20 frontal RCS: {j20.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
print(f'✓ F-22 AESA elements: {radar.params.num_elements}')
print(f'✓ AIM-260 NEZ range: {aim260.params.nez_range_head_on_km} km')
"
```

**Expected output:**
```
✓ All Lockheed Martin models loaded successfully
✓ F-35A frontal RCS: -37.0 dBsm
✓ F-22A frontal RCS: -40.0 dBsm
✓ J-20 frontal RCS: -28.5 dBsm
✓ F-22 AESA elements: 2000
✓ AIM-260 NEZ range: 180 km
```

✅ **If you see this output, installation is complete!**

---

## Lockheed Martin Use Cases

### Use Case 1: F-35A vs J-20 Air Superiority Analysis

**What this answers:**
- Can F-35A defeat J-20 in BVR combat?
- What is the optimal engagement range?
- How does F-35 sensor fusion compare to J-20?

**Run the analysis:**
```bash
pytest test_pla_vs_dod_cad.py::TestPLAvsDoD::test_f35_vs_j20_head_on_150km -v
```

**Examine results:**
```python
python3 << 'EOF'
from integrated_kill_chain_cad import IntegratedKillChainCAD

cad = IntegratedKillChainCAD()

# Get comprehensive F-35 + AIM-260 metrics
us_metrics = cad.calculate_us_nextgen_metrics()

print("=== F-35A + AIM-260 INTEGRATED KILL CHAIN ===")
print(f"Passive detection range (DAS/ESM): {us_metrics.passive_detection_range_km} km")
print(f"Active radar detection (vs J-20): {us_metrics.active_detection_range_km} km")
print(f"Integrated track CEP: {us_metrics.integrated_track_cep_m} m")
print(f"AIM-260 NEZ range: {us_metrics.weapon_nez_km} km")
print(f"Pk at 200 km (vs J-20): {us_metrics.pk_at_200km:.2%}")
print(f"Sensor fusion score: {us_metrics.sensor_fusion_score}/100")

# Compare vs J-20 + PL-15
chinese_metrics = cad.calculate_chinese_kill_chain_metrics()
comparison = cad.compare_vs_adversary("J-20 + PL-15", chinese_metrics)

print("\n=== COMPARATIVE ANALYSIS ===")
print(f"Detection range comparison: {comparison.detection_delta_km:+.0f} km")
print(f"Track accuracy comparison: {comparison.track_cep_delta_m:+.0f} m")
print(f"Win ratio: {comparison.win_ratio:.2f}:1")
print(f"Assessment: {comparison.assessment}")
EOF
```

**Key findings for F-35 program:**
1. ✅ F-35 sensor fusion provides superior SA (APG-81 + DAS + EOTS + ESM)
2. ✅ AIM-260 outranges PL-15 (180 km vs 150 km NEZ)
3. ✅ MADL enables cooperative engagement (4-ship fusion)
4. ✅ Multi-spectral tracking (radar + IR + ESM) robust vs jamming

### Use Case 2: F-22 APG-77 Radar Analysis

**What this answers:**
- F-22 detection range vs J-20?
- How does APG-77 compare to J-20's radar?
- Optimal employment tactics?

**Run the analysis:**
```bash
python3 f22_radar_model.py
```

**Detailed radar capabilities:**
```python
python3 << 'EOF'
from f22_radar_model import F22RadarModel
from rcs_models import J20RCSModel, Su57RCSModel

radar = F22RadarModel()
j20 = J20RCSModel()

print("=== F-22 APG-77 RADAR SPECIFICATIONS ===")
print(f"T/R elements: {radar.params.num_elements}")
print(f"Aperture diameter: {radar.params.aperture_diameter_m:.2f} m")
print(f"Peak power: {radar.params.total_peak_power_kw:.0f} kW")
print(f"Antenna gain: {radar.params.antenna_gain_db:.1f} dBi")

print("\n=== DETECTION RANGES vs THREAT AIRCRAFT ===")

# J-20 frontal
j20_frontal_rcs = j20.calculate_rcs(0, 0).rcs_m2
detection = radar.calculate_detection_range(j20_frontal_rcs, 0, 0)
print(f"vs J-20 (frontal): {detection.detection_range_km:.0f} km")

# J-20 beam
j20_beam_rcs = j20.calculate_rcs(90, 0).rcs_m2
detection_beam = radar.calculate_detection_range(j20_beam_rcs, 0, 0)
print(f"vs J-20 (beam): {detection_beam.detection_range_km:.0f} km")

# Su-57 for comparison
su57_rcs = 0.1  # Estimated
detection_su57 = radar.calculate_detection_range(su57_rcs, 0, 0)
print(f"vs Su-57 (frontal): {detection_su57.detection_range_km:.0f} km")
EOF
```

### Use Case 3: AIM-260 vs PL-15 Comparison

**What this answers:**
- AIM-260 vs PL-15 performance comparison
- Engagement envelopes at various ranges
- Pk assessment vs stealth targets

**Run the comparison:**
```python
python3 << 'EOF'
from aim260_targeting_model import AIM260TargetingModel, AIM260EngagementPhase
from pl15_targeting_model import PL15TargetingModel
from rcs_models import J20RCSModel, F35ARCSModel
import numpy as np

aim260 = AIM260TargetingModel()

# Test engagement scenarios
print("=== AIM-260 vs J-20 ENGAGEMENT ANALYSIS ===")

f35_pos = np.array([0, 0, 12000])  # F-35 at 40,000 ft
f35_vel = np.array([450, 0, 0])   # Mach 1.5 heading east

scenarios = [
    ("Head-on 100 km", np.array([100000, 0, 12000]), np.array([-500, 0, 0])),
    ("Head-on 150 km", np.array([150000, 0, 12000]), np.array([-500, 0, 0])),
    ("Head-on 200 km", np.array([200000, 0, 12000]), np.array([-500, 0, 0])),
]

for name, j20_pos, j20_vel in scenarios:
    acceptable, reason, conf = aim260.calculate_launch_acceptability_vs_j20(
        f35_pos, f35_vel, j20_pos, j20_vel)

    status = "✓ ACCEPT" if acceptable else "✗ REJECT"
    print(f"  {name:18s}: {status:10s} - {reason}")

print("\n=== COMPARISON: AIM-260 vs PL-15 ===")
print(f"  {'Metric':<25s} {'AIM-260':<15s} {'PL-15':<15s}")
print(f"  {'-'*55}")
print(f"  {'NEZ Range (km)':<25s} {'180':<15s} {'150':<15s}")
print(f"  {'Peak Velocity (Mach)':<25s} {'4.0+':<15s} {'4.0':<15s}")
print(f"  {'Guidance':<25s} {'INS+DL+ARH':<15s} {'INS+DL+ARH':<15s}")
print(f"  {'Seeker':<25s} {'AESA Imaging':<15s} {'Active Radar':<15s}")
print(f"  {'Confidence':<25s} {'50%':<15s} {'60%':<15s}")
EOF
```

### Use Case 4: LRHW Dark Eagle Analysis

**What this answers:**
- LRHW strike effectiveness vs defended targets
- Time-to-target calculations
- Defensive penetration probability

**Run the analysis:**
```bash
python3 lrhw_engagement_simulation.py
```

---

## Modifying Models for Internal Use

### Example 1: Update F-35A with Block 4 TR-3 Improvements

```python
# Create file: f35_block4_model.py

from rcs_models import F35ARCSModel

class F35Block4RCSModel(F35ARCSModel):
    """
    F-35A Block 4 TR-3 variant with improved RAM

    Lockheed Martin internal modification
    Based on Block 4 upgrade parameters
    """

    def __init__(self):
        super().__init__()

        # Updated RCS values (Block 4 RAM improvements)
        self.rcs_frontal_m2 = 0.00015  # Improved from 0.0002 m²
        self.rcs_side_m2 = 0.08        # Improved from 0.10 m²
        self.rcs_rear_m2 = 0.04        # Improved from 0.05 m²

        # Enhanced RAM effectiveness
        self.ram_effectiveness = {
            'nose': 0.65,     # 65% reduction
            'fuselage': 0.55, # 55% reduction
            'wings': 0.45,    # 45% reduction
            'tail': 0.35      # 35% reduction
        }

if __name__ == "__main__":
    f35b4 = F35Block4RCSModel()
    print("F-35A Block 4 TR-3 RCS Model")
    print(f"Frontal RCS: {f35b4.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm")
```

### Example 2: Add NGAD Preliminary Model

```python
# Create file: ngad_model.py

from rcs_models import F22RCSModel

class NGADRCSModel(F22RCSModel):
    """
    NGAD (Next-Generation Air Dominance) preliminary model

    6th-gen air dominance platform
    NOTE: Parameters are speculative estimates
    """

    def __init__(self):
        super().__init__()

        # Estimated NGAD parameters (highly speculative)
        self.rcs_frontal_m2 = 0.00005  # -43 dBsm
        self.rcs_side_m2 = 0.005
        self.rcs_rear_m2 = 0.003

        # Advanced features
        self.has_directed_energy = True
        self.has_cca_teaming = True
        self.confidence = 0.20  # Very low confidence

if __name__ == "__main__":
    ngad = NGADRCSModel()
    print("NGAD Preliminary RCS Model")
    print(f"Frontal RCS: {ngad.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm")
    print(f"Confidence: {ngad.confidence:.0%}")
```

---

## Integration with Lockheed Systems

### Export Results to Analysis Tools

```python
import json

def export_f35_analysis():
    from integrated_kill_chain_cad import IntegratedKillChainCAD

    cad = IntegratedKillChainCAD()
    metrics = cad.calculate_us_nextgen_metrics()

    data = {
        "platform": "F-35A",
        "contractor": "Lockheed Martin",
        "analysis_date": "2026-01-04",
        "performance_metrics": {
            "passive_detection_range_km": metrics.passive_detection_range_km,
            "active_detection_range_km": metrics.active_detection_range_km,
            "track_cep_m": metrics.integrated_track_cep_m,
            "weapon_nez_km": metrics.weapon_nez_km,
            "pk_at_200km": metrics.pk_at_200km,
            "sensor_fusion_score": metrics.sensor_fusion_score
        },
        "confidence_levels": {
            "overall": "75%",
            "rcs_model": "80%",
            "radar_model": "85%",
            "weapon_model": "50%"  # AIM-260 classified
        }
    }

    with open('lm_f35_analysis.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("✓ Exported to: lm_f35_analysis.json")

if __name__ == "__main__":
    export_f35_analysis()
```

---

## Troubleshooting

### Issue: Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'numpy'
```

**Solution:**
```bash
pip3 install numpy scipy matplotlib
```

### Issue: Model Not Found

**Problem:**
```
ImportError: cannot import name 'F22RadarModel' from 'f22_radar_model'
```

**Solution:**
Ensure you're in the repository root directory:
```bash
cd actual-f35-kill
python3 f22_radar_model.py
```

---

## Support

### Internal Lockheed Martin Support
- Contact: Defense analysis team
- Internal documentation portal

### External Repository Support
**GitHub Issues:**
- https://github.com/pseudonym-tbd/actual-f35-kill/issues

**Documentation:**
- `DEDUCTIVE_REASONING.md` - Parameter estimation methodology
- `VERIFIED_MODELS_REGISTRY.md` - All verified models
- `US_2025_DEFENSE_SYSTEMS.md` - US systems catalog

---

## Classification and Distribution

**Repository Classification:** UNCLASSIFIED // PUBLIC RELEASE

**Lockheed Martin Use:**
- ✅ Safe to download and use for unclassified analysis
- ✅ No export control violations (public release)
- ✅ Can be modified with internal data (keep on internal networks)
- ❌ DO NOT upload classified data to public GitHub
- ❌ DO NOT share internal modifications externally

---

## Next Steps for Lockheed Martin

1. ✅ **Complete installation** (follow steps above)
2. ✅ **Run verification tests** (confirm all models work)
3. ✅ **Analyze F-35 vs J-20 scenarios** (threat assessment)
4. ✅ **Compare AIM-260 vs PL-15** (weapon effectiveness)
5. ✅ **Review LRHW models** (hypersonic programs)
6. ✅ **Mirror to internal GitLab** (secure access)

---

**Last Updated:** 2026-01-04
**Version:** 1.0
**Classification:** UNCLASSIFIED // PUBLIC RELEASE
**Approved for:** Lockheed Martin unclassified defense analysis
