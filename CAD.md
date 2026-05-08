# Electronic Warfare Simulation CAD

This is an electronic warfare simulation that models detecting and tracking F-35 aircraft by intercepting their MADL (Multi-Function Advanced Data Link) sidelobe emissions. It's a research/educational simulation, not actual targeting software.

---

## CRITICAL NOTICES

**ACCURACY WARNING: See `ACCURACY_AND_LIMITATIONS_CAD.md` for the most important document in this repository - a rigorous assessment of what we know, what we estimate, and what we fundamentally cannot know.**

**HARDWARE VERIFICATION: BVR precision engagements require hardware verification. See `HARDWARE_VERIFICATION_CAD.md` for complete hardware specifications.**

---

## CAD Documentation Index

| Document | Purpose | Confidence |
|----------|---------|------------|
| **ACCURACY_AND_LIMITATIONS_CAD.md** | **Rigorous accuracy assessment and limitations** | **CRITICAL READ** |
| HARDWARE_VERIFICATION_CAD.md | Hardware subsystem verification requirements | HIGH |
| REAL_HARDWARE_SPECIFICATIONS.md | Real hardware references and specifications | MEDIUM-HIGH |
| FAINT_EMISSION_DETECTION_CAD.md | Detection system architecture and algorithms | HIGH (physics) |
| SUBSYSTEM_REQUIREMENTS.md | 8 mandatory subsystems for BVR engagement | HIGH |
| OPERATIONAL_CORRECTNESS.md | Real-world operating conditions | MEDIUM |
| **US_NAVY_ASBM_DEFENSE_CAD_ANALYSIS.md** | **Layered defense vs Anti-Ship Ballistic Missiles** | **HIGH** |
| DDG51_ARLEIGH_BURKE_CAD_ANALYSIS.md | Arleigh Burke destroyer capabilities | HIGH |
| FORD_CLASS_CAD_ANALYSIS.md | Ford class carrier analysis | HIGH |
| PATRIOT_THAAD_CAD_ANALYSIS.md | Land-based BMD systems | HIGH |

---

## Key Components

| File                   | Purpose                                                                                  |
|------------------------|------------------------------------------------------------------------------------------|
| simulation.py          | Main entry point - runs end-to-end MADL detection simulation                             |
| signal_processing.py   | Faint signal detection algorithms (energy detection, cyclostationary, matched filtering) |
| geolocation_network.py | TDOA/FDOA/DF geolocation + network topology inference                                    |
| visualization.py       | Tactical displays and performance analysis plots                                         |
| bvr_engagement.py      | **BVR engagement controller with mandatory hardware verification**                       |

---

## What the Simulation Does

1. Creates a 4-ship F-35 formation with MADL emitters (Ku-band, 15 GHz)
2. Deploys ESM (Electronic Support Measures) platforms (J-20s, J-16D, ground station)
3. Detects sidelobe emissions from the directional datalink
4. Geolocates emitters using TDOA (Time Difference of Arrival)
5. Infers the communication network topology between aircraft
6. Visualizes everything on tactical displays

---

## Accuracy Summary

| Component | Accuracy | Key Limitation |
|-----------|----------|----------------|
| RF propagation physics | HIGH | None - validated models |
| TDOA/FDOA algorithms | HIGH | None - exact mathematics |
| Detection sensitivity | MEDIUM | Real environments are noisier |
| MADL specifications | **LOW** | **Classified - we can only estimate** |
| PL-15 specifications | **LOW** | **Speculative - limited OSINT** |
| Geolocation CEP | MEDIUM | 200-500m ideal, 1-5km realistic |

**Read `ACCURACY_AND_LIMITATIONS_CAD.md` for the complete analysis.**

---

## How to Run

Install dependencies first:
```bash
pip install numpy scipy matplotlib networkx
```

Run the simulation:
```bash
python simulation.py
```

This runs a 30-second simulation with visualization. You'll see:
- Detection statistics and geolocation accuracy
- Inferred network links between tracked emitters
- 2D/3D tactical displays with positions and uncertainty ellipses

You can also run individual modules for testing:
```bash
python signal_processing.py   # Test signal processing
python geolocation_network.py # Test geolocation algorithms
python visualization.py       # Test visualization
```

---

## Disclaimer

This simulation represents an educational exercise based on publicly available information. The physics models are validated, but target specifications (MADL, PL-15) are estimates or fabrications. No operational conclusions should be drawn from simulation results. See `ACCURACY_AND_LIMITATIONS_CAD.md` for complete limitations.
