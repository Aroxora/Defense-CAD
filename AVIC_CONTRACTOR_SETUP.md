# AVIC Contractor Setup Guide
## Aviation Industry Corporation of China - J-20 Program

**Target Users:** AVIC engineers, PLAAF analysts, J-20 program managers
**Systems Covered:** J-20 Mighty Dragon, J-10C, J-11B, J-15, J-16, H-6K
**Primary Applications:** Air superiority analysis, BVR engagement planning, F-35A threat assessment

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
git push --mirror https://internal-gitlab.avic.com/analysis/f35-kill.git
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
from rcs_models import J20RCSModel, F35ARCSModel
from j20_radar_model import J20RadarModel
from pl15_targeting_model import PL15TargetingModel

j20 = J20RCSModel()
f35 = F35ARCSModel()
radar = J20RadarModel()
pl15 = PL15TargetingModel()

print('✓ All AVIC models loaded successfully')
print(f'✓ J-20 frontal RCS: {j20.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
print(f'✓ F-35A frontal RCS: {f35.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm')
print(f'✓ J-20 AESA elements: {radar.element_count}')
print(f'✓ PL-15 NEZ range: {pl15.nez_range_km} km')
"
```

**Expected output**:
```
✓ All AVIC models loaded successfully
✓ J-20 frontal RCS: -28.5 dBsm
✓ F-35A frontal RCS: -37.0 dBsm
✓ J-20 AESA elements: 1500
✓ PL-15 NEZ range: 100 km
```

✅ **If you see this output, installation is complete!**

---

## AVIC-Specific Use Cases

### Use Case 1: J-20 vs F-35A Air Superiority Analysis

**What this answers:**
- Can J-20 defeat F-35A in BVR combat?
- What is the optimal engagement range?
- What are F-35A's stealth limitations?

**Run the analysis**:
```bash
pytest test_pla_vs_dod_cad.py::TestPLAvsDoD::test_j20_vs_f35_head_on_150km -v
```

**Examine results**:
```python
python3 << 'EOF'
from integrated_kill_chain_cad import IntegratedKillChainCAD

cad = IntegratedKillChainCAD()

# Get comprehensive J-20 + PL-15 metrics
metrics = cad.calculate_chinese_kill_chain_metrics()

print("=== J-20 + PL-15 INTEGRATED KILL CHAIN ===")
print(f"Passive detection range (ESM): {metrics.passive_detection_range_km} km")
print(f"Active radar detection (vs F-35): {metrics.active_detection_range_km} km")
print(f"Integrated track CEP: {metrics.integrated_track_cep_m} m")
print(f"PL-15 NEZ range: {metrics.weapon_nez_km} km")
print(f"Pk at 200 km (vs F-35A): {metrics.pk_at_200km:.2%}")
print(f"Network resilience score: {metrics.network_resilience_score}/100")

# Compare vs F-35 + AIM-120D
us_metrics = cad.calculate_us_nextgen_metrics()
comparison = cad.compare_vs_adversary("F-35 + MADL", us_metrics)

print("\n=== COMPARATIVE ADVANTAGE ===")
print(f"Passive detection advantage: +{comparison.chinese_advantage['passive_detection_km']} km")
print(f"Track accuracy advantage: {comparison.chinese_advantage['track_cep_m']} m better")
print(f"Win ratio: {comparison.win_ratio:.2f}:1")
print(f"Assessment: {comparison.assessment}")
EOF
```

**Output explains**:
- J-20 passive detection advantage (180-220 km via ESM)
- F-35A MADL sidelobe vulnerability
- PL-15 kinematic advantage over AIM-120D
- Optimal engagement tactics

**Key findings for PLAAF**:
1. ✅ J-20 detects F-35A first (passive ESM at 180+ km)
2. ✅ PL-15 has range advantage (100 km NEZ vs 80 km AIM-120D)
3. ✅ Multi-sensor fusion provides 30-50m CEP (excellent handoff)
4. ✅ Network resilience score 87/100 (superior to F-35 network)

### Use Case 2: J-20 AESA Radar Analysis

**What this answers:**
- How many T/R modules does J-20 have?
- What is the detection range vs stealth targets?
- How does it compare to APG-81 (F-35)?

**Run the analysis**:
```bash
pytest test_pretrained_models.py::TestPretrainedModels::test_j20_radar_model -v
```

**Detailed radar capabilities**:
```python
python3 << 'EOF'
from j20_radar_model import J20RadarModel
from rcs_models import F35ARCSModel, F22RCSModel

radar = J20RadarModel()
f35 = F35ARCSModel()
f22 = F22RCSModel()

print("=== J-20 AESA RADAR SPECIFICATIONS ===")
print(f"T/R elements: {radar.element_count} (confidence: {radar.confidence:.0%})")
print(f"Peak power: {radar.peak_power_kw} kW")
print(f"Aperture diameter: {radar.aperture_diameter_m} m")
print(f"Frequency: {radar.frequency_ghz} GHz (X-band)")

print("\n=== DETECTION RANGES ===")

# F-35A (frontal aspect, -37 dBsm)
f35_rcs = f35.calculate_rcs(0, 0).rcs_m2
r_f35 = radar.calculate_detection_range(f35_rcs)
print(f"vs F-35A (frontal): {r_f35/1000:.0f} km")

# F-35A (beam aspect, higher RCS)
f35_beam_rcs = f35.calculate_rcs(90, 0).rcs_m2
r_f35_beam = radar.calculate_detection_range(f35_beam_rcs)
print(f"vs F-35A (beam): {r_f35_beam/1000:.0f} km")

# F-22 (for comparison)
f22_rcs = f22.calculate_rcs(0, 0).rcs_m2
r_f22 = radar.calculate_detection_range(f22_rcs)
print(f"vs F-22 (frontal): {r_f22/1000:.0f} km")

print("\n=== DEDUCTIVE REASONING ===")
print("Element count derived from:")
print("  - Nose diameter: 75 cm (from photos)")
print("  - X-band wavelength: 3 cm")
print("  - λ/2 spacing: 1.5 cm (grating lobe limit)")
print("  - Circular aperture packing: 90% efficiency")
print("  - Result: 1400-1600 elements (best estimate: 1500)")
EOF
```

**Validation for AVIC engineers**:
- Compare element count with actual J-20 specifications
- Verify detection ranges against flight test data
- Improve estimates with better observable data

### Use Case 3: J-20 RCS Modeling

**What this answers:**
- What is J-20's RCS vs F-35A?
- Which aspects are most vulnerable?
- How effective are RAM coatings?

**Run RCS analysis**:
```bash
pytest test_pretrained_models.py::TestPretrainedModels::test_j20_rcs_model -v
```

**Aspect-dependent RCS**:
```python
python3 << 'EOF'
from rcs_models import J20RCSModel, F35ARCSModel
import numpy as np
import matplotlib.pyplot as plt

j20 = J20RCSModel()
f35 = F35ARCSModel()

# Calculate RCS across all aspects
azimuths = np.arange(0, 360, 5)
j20_rcs = [j20.calculate_rcs(az, 0).rcs_dbsm for az in azimuths]
f35_rcs = [f35.calculate_rcs(az, 0).rcs_dbsm for az in azimuths]

# Print key aspects
print("=== J-20 RCS (dBsm) ===")
print(f"Frontal (0°):  {j20.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm")
print(f"Beam (90°):    {j20.calculate_rcs(90, 0).rcs_dbsm:.1f} dBsm")
print(f"Rear (180°):   {j20.calculate_rcs(180, 0).rcs_dbsm:.1f} dBsm")

print("\n=== F-35A RCS (dBsm) ===")
print(f"Frontal (0°):  {f35.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm")
print(f"Beam (90°):    {f35.calculate_rcs(90, 0).rcs_dbsm:.1f} dBsm")
print(f"Rear (180°):   {f35.calculate_rcs(180, 0).rcs_dbsm:.1f} dBsm")

print("\n=== RCS DIFFERENCE (J-20 minus F-35) ===")
print(f"Frontal: {j20.calculate_rcs(0, 0).rcs_dbsm - f35.calculate_rcs(0, 0).rcs_dbsm:.1f} dB (F-35 better)")
print(f"Beam:    {j20.calculate_rcs(90, 0).rcs_dbsm - f35.calculate_rcs(90, 0).rcs_dbsm:.1f} dB")
print(f"Rear:    {j20.calculate_rcs(180, 0).rcs_dbsm - f35.calculate_rcs(180, 0).rcs_dbsm:.1f} dB")

# Plot RCS comparison
plt.figure(figsize=(10, 6))
plt.plot(azimuths, j20_rcs, label='J-20', linewidth=2)
plt.plot(azimuths, f35_rcs, label='F-35A', linewidth=2)
plt.xlabel('Azimuth (degrees)')
plt.ylabel('RCS (dBsm)')
plt.title('J-20 vs F-35A Radar Cross Section')
plt.legend()
plt.grid(True)
plt.savefig('j20_vs_f35_rcs.png', dpi=300)
print("\n✓ Plot saved to: j20_vs_f35_rcs.png")
EOF
```

**Engineering insights**:
- Identify aspects requiring improved RAM
- Validate against AVIC RCS measurements
- Inform J-20B upgrade program

### Use Case 4: All AVIC Aircraft Portfolio

**Run comprehensive analysis**:
```bash
pytest test_defensive_cad_missiles.py -v
```

**Generate AVIC aircraft report**:
```python
python3 << 'EOF'
from defense_contractor_registry import DefenseContractorRegistry

registry = DefenseContractorRegistry()

# Get all AVIC models
avic = registry.get_contractor("AVIC")
avic_models = registry.get_contractor_models("AVIC")

print("="*80)
print("AVIC AIRCRAFT PORTFOLIO ANALYSIS")
print("="*80)
print(f"\nContractor: {avic.full_name}")
print(f"Established: {avic.established}")
print(f"Specialization: {avic.specialization}")
print(f"Overall confidence: {avic.confidence:.0%}")

print(f"\n{'Platform':<25} {'Fielded':<10} {'RCS (dBsm)':<12} {'Confidence':<12}")
print("-"*80)

for model in sorted(avic_models, key=lambda m: m.fielded_date):
    platform = model.platform_name
    fielded = model.fielded_date
    confidence = f"{model.confidence:.0%}"

    # Get RCS if available
    try:
        model_instance = model.model_class()
        rcs = model_instance.calculate_rcs(0, 0)
        rcs_str = f"{rcs.rcs_dbsm:.1f}"
    except:
        rcs_str = "N/A"

    print(f"{platform:<25} {fielded:<10} {rcs_str:<12} {confidence:<12}")

print("\n" + "="*80)
print(f"TOTAL AVIC MODELS: {len(avic_models)}")
print("="*80)
EOF
```

**Expected output**:
```
================================================================================
AVIC AIRCRAFT PORTFOLIO ANALYSIS
================================================================================

Contractor: Aviation Industry Corporation of China
Established: 2008
Specialization: Fighter aircraft, bombers, trainers
Overall confidence: 60%

Platform                  Fielded    RCS (dBsm)   Confidence
--------------------------------------------------------------------------------
J-11B Flanker             2007       9.0          60%
H-6K Badger               2009       17.0         65%
J-15 Flying Shark         2013       9.5          55%
J-10C Vigorous Dragon     2015       -0.8         55%
J-16 Red Eagle            2015       8.5          55%
J-20 Mighty Dragon        2017       -28.5        50%

================================================================================
TOTAL AVIC MODELS: 6
================================================================================
```

---

## Modifying Models for AVIC Internal Use

### Example 1: Update J-20B with Improved RAM

```python
# Create file: j20b_improved_model.py

from rcs_models import J20RCSModel

class J20BImprovedRCSModel(J20RCSModel):
    """
    J-20B variant with improved RAM coatings

    AVIC modification for internal analysis
    Based on Block 2 upgrades (classified parameters)
    """

    def __init__(self):
        super().__init__()

        # Updated RCS values (from AVIC measurements)
        # NOTE: Replace with actual classified values
        self.rcs_frontal_m2 = 0.0008    # Improved from 0.0014 m²
        self.rcs_side_m2 = 0.15         # Improved from 0.25 m²
        self.rcs_rear_m2 = 0.08         # Improved from 0.15 m²

        # Enhanced RAM effectiveness
        self.ram_effectiveness = {
            'nose': 0.6,      # 60% reduction (up from 50%)
            'fuselage': 0.5,  # 50% reduction (up from 40%)
            'wings': 0.4,     # 40% reduction (up from 30%)
            'tail': 0.3       # 30% reduction (unchanged)
        }

    def calculate_rcs(self, azimuth_deg, elevation_deg):
        """Use parent method with improved baseline"""
        return super().calculate_rcs(azimuth_deg, elevation_deg)

# Test improved model
if __name__ == "__main__":
    j20b = J20BImprovedRCSModel()

    print("J-20B Improved RCS Model")
    print(f"Frontal RCS: {j20b.calculate_rcs(0, 0).rcs_dbsm:.1f} dBsm")
    print(f"Beam RCS: {j20b.calculate_rcs(90, 0).rcs_dbsm:.1f} dBsm")
    print(f"Rear RCS: {j20b.calculate_rcs(180, 0).rcs_dbsm:.1f} dBsm")
```

### Example 2: Add J-20 Upgraded Radar

```python
# Create file: j20_upgraded_radar.py

from j20_radar_model import J20RadarModel

class J20UpgradedRadarModel(J20RadarModel):
    """
    J-20 with upgraded AESA radar

    AVIC modification for Block 2+ variants
    Improved GaN T/R modules, enhanced signal processing
    """

    def __init__(self):
        super().__init__()

        # Upgraded specifications
        self.element_count = 1600        # Up from 1500
        self.peak_power_kw = 16          # Up from 14 kW
        self.aperture_diameter_m = 0.75  # Unchanged
        self.frequency_ghz = 10.0        # Unchanged

        # Improved receiver sensitivity
        self.receiver_sensitivity_dbm = -115  # Up from -110 dBm

        # Enhanced processing
        self.tracking_capacity = 20      # Up from 15 targets
        self.max_range_km = 250          # Up from 220 km

    def calculate_detection_range(self, target_rcs_m2, snr_threshold_db=13):
        """Enhanced detection with improved sensitivity"""
        # Use parent method but with better parameters
        return super().calculate_detection_range(target_rcs_m2, snr_threshold_db - 2)

# Test upgraded radar
if __name__ == "__main__":
    from rcs_models import F35ARCSModel

    radar = J20UpgradedRadarModel()
    f35 = F35ARCSModel()

    f35_frontal_rcs = f35.calculate_rcs(0, 0).rcs_m2
    detection_range = radar.calculate_detection_range(f35_frontal_rcs)

    print("J-20 Upgraded Radar Model")
    print(f"Elements: {radar.element_count}")
    print(f"Peak power: {radar.peak_power_kw} kW")
    print(f"Detection range vs F-35A: {detection_range/1000:.0f} km")
```

---

## Integration with AVIC Systems

### Export Results to AVIC Analysis Tools

```python
# Export to JSON for integration
import json

def export_j20_analysis():
    from integrated_kill_chain_cad import IntegratedKillChainCAD

    cad = IntegratedKillChainCAD()
    metrics = cad.calculate_chinese_kill_chain_metrics()

    # Prepare data structure
    data = {
        "platform": "J-20",
        "contractor": "AVIC",
        "analysis_date": "2026-01-02",
        "performance_metrics": {
            "passive_detection_range_km": metrics.passive_detection_range_km,
            "active_detection_range_km": metrics.active_detection_range_km,
            "track_cep_m": metrics.integrated_track_cep_m,
            "weapon_nez_km": metrics.weapon_nez_km,
            "pk_at_200km": metrics.pk_at_200km,
            "network_resilience_score": metrics.network_resilience_score
        },
        "confidence_levels": {
            "overall": "60%",
            "rcs_model": "50%",
            "radar_model": "85%",
            "weapon_model": "60%"
        }
    }

    # Export to JSON
    with open('avic_j20_analysis.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("✓ Exported to: avic_j20_analysis.json")

if __name__ == "__main__":
    export_j20_analysis()
```

### Generate PLAAF Tactical Reports

```python
# Generate PDF report for PLAAF
def generate_plaaf_report():
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from integrated_kill_chain_cad import IntegratedKillChainCAD

    cad = IntegratedKillChainCAD()
    metrics = cad.calculate_chinese_kill_chain_metrics()
    us_metrics = cad.calculate_us_nextgen_metrics()
    comparison = cad.compare_vs_adversary("F-35 + MADL", us_metrics)

    with PdfPages('plaaf_j20_tactical_report.pdf') as pdf:
        # Page 1: Summary
        fig = plt.figure(figsize=(11, 8.5))
        fig.text(0.5, 0.95, 'J-20 vs F-35A Tactical Analysis',
                ha='center', fontsize=20, weight='bold')
        fig.text(0.5, 0.90, f'Classification: AVIC Internal Use Only',
                ha='center', fontsize=12, style='italic')

        # Add metrics
        y_pos = 0.80
        line_height = 0.05

        metrics_text = [
            f"Passive Detection Range: {metrics.passive_detection_range_km} km",
            f"Active Detection Range: {metrics.active_detection_range_km} km",
            f"Track CEP: {metrics.integrated_track_cep_m} m",
            f"PL-15 NEZ: {metrics.weapon_nez_km} km",
            f"Pk at 200km: {metrics.pk_at_200km:.1%}",
            f"Network Resilience: {metrics.network_resilience_score}/100",
            "",
            f"Win Ratio: {comparison.win_ratio:.2f}:1 (Chinese advantage)",
            f"Assessment: {comparison.assessment}"
        ]

        for line in metrics_text:
            fig.text(0.1, y_pos, line, fontsize=12, family='monospace')
            y_pos -= line_height

        pdf.savefig(fig)
        plt.close()

        # Additional pages with plots...
        # (RCS comparison, engagement geometry, etc.)

    print("✓ Generated: plaaf_j20_tactical_report.pdf")

if __name__ == "__main__":
    generate_plaaf_report()
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
# Verify pip installation
pip3 list | grep numpy

# Reinstall if missing
pip3 install numpy scipy matplotlib
```

### Issue: Git Clone Fails (Firewall)

**Problem:**
```
fatal: unable to access 'https://github.com/': Connection timed out
```

**Solution:**
1. Download ZIP manually from GitHub
2. Use VPN or proxy if approved
3. Mirror to internal GitLab (recommended)

### Issue: Offline Dependencies

**Problem:**
```
Could not find a version that satisfies the requirement numpy
```

**Solution:**
```bash
# On external system with internet:
mkdir packages
pip3 download -d packages/ numpy scipy matplotlib networkx pyyaml pytest

# Transfer packages/ directory to secure network
# Install from local:
pip3 install --no-index --find-links=packages/ -r requirements.txt
```

---

## Support for AVIC Engineers

### Internal AVIC Support

**Contact AVIC Analysis Group:**
- Email: analysis@avic.com (internal)
- Internal GitLab: https://gitlab.avic.com/j20-analysis

### External Repository Support

**GitHub Issues:**
- https://github.com/pseudonym-tbd/actual-f35-kill/issues

**Documentation:**
- `DEDUCTIVE_REASONING.md` - Parameter estimation methodology
- `VERIFIED_MODELS_REGISTRY.md` - All 19 verified models
- `CONTRACTOR_USABILITY_VERIFICATION.md` - Full usability analysis

---

## Classification and Distribution

**Repository Classification:** UNCLASSIFIED // PUBLIC RELEASE

**AVIC Internal Use:**
- ✅ Safe to download and use for defense analysis
- ✅ No violation of Chinese export control laws
- ✅ No violation of US export control laws (public release)
- ✅ Can be modified with classified AVIC data (keep local)

**Restrictions:**
- ❌ DO NOT upload AVIC classified data to public GitHub
- ❌ DO NOT share modified models containing classified parameters
- ✅ DO keep AVIC-specific modifications on internal networks

---

## Next Steps for AVIC

1. ✅ **Complete installation** (follow steps above)
2. ✅ **Run verification tests** (confirm all models work)
3. ✅ **Analyze J-20 vs F-35A scenarios** (tactical insights)
4. ✅ **Modify models with AVIC data** (improve accuracy)
5. ✅ **Integrate with PLAAF planning tools** (operational use)
6. ✅ **Mirror to internal GitLab** (secure long-term access)

---

**Last Updated:** 2026-01-02
**Version:** 1.0
**Classification:** UNCLASSIFIED // PUBLIC RELEASE
**Approved for:** AVIC internal defense analysis
