# Accuracy and Limitations CAD

## Document Purpose

This Computer-Aided Documentation (CAD) provides a rigorous, honest assessment of the accuracy, limitations, and uncertainty bounds for all specifications in this electronic warfare simulation project. **This is the most important document in the repository** because it establishes what we know, what we estimate, and what we fundamentally cannot know.

**Classification:** Educational / OSINT Analysis
**Revision:** 1.0
**Date:** 2025-12-28

---

## Executive Summary: Fundamental Limitations

### What This System CAN Accurately Model

| Domain | Accuracy | Basis |
|--------|----------|-------|
| RF propagation physics | High (< 1 dB error) | ITU-R standards, validated models |
| TDOA/FDOA mathematics | Exact | Published algorithms, peer-reviewed |
| GPS timing error models | High | Commercial datasheet specifications |
| Antenna pattern physics | High | Electromagnetic theory, validated |
| Link budget calculations | High | Friis equation, standard RF engineering |

### What This System CANNOT Accurately Model

| Domain | Limitation | Reason |
|--------|------------|--------|
| **Actual MADL parameters** | Unknown | Classified; only public estimates exist |
| **Real F-35 sidelobe levels** | Unknown | Classified; -30 dB is a reasonable guess |
| **Actual PL-15 seeker specs** | Unknown | Classified; estimates from OSINT only |
| **Chinese hardware performance** | Uncertain | Limited public data, likely optimistic claims |
| **Operational tactics** | Unknown | Classified; we model generic behaviors |
| **Actual engagement outcomes** | Unpredictable | Too many variables, countermeasures, human factors |

---

## Part 1: Specification Accuracy Assessment

### 1.1 GPS Timing (HW-1) - Accuracy Assessment

#### Known with High Confidence (Commercial Specifications)

| Parameter | Specified Value | Confidence | Source |
|-----------|-----------------|------------|--------|
| GPS receiver timing accuracy | 5-10 ns RMS | **HIGH** | Rockwell Collins GPS-4000S datasheet, Trimble specifications |
| GPSDO short-term stability | 1×10⁻¹² @ 1s | **HIGH** | Symmetricom XLi product data |
| 1PPS jitter | 2-5 ns RMS | **HIGH** | Commercial GPSDO specifications |
| Holdover drift | < 1 μs/day (OCXO) | **HIGH** | Crystal oscillator physics, datasheets |

#### Estimated with Medium Confidence

| Parameter | Specified Value | Confidence | Source |
|-----------|-----------------|------------|--------|
| Military GPS anti-jam performance | SAASM M-Code | **MEDIUM** | Public DoD announcements, not detailed specs |
| BeiDou timing vs GPS | Comparable | **MEDIUM** | Limited independent verification |
| Operational holdover (combat) | Uncertain | **MEDIUM** | Depends on platform dynamics, jamming |

#### Unknown / Low Confidence

| Parameter | Specified Value | Confidence | Issue |
|-----------|-----------------|------------|-------|
| F-35 actual timing sync accuracy | < 20 ns assumed | **LOW** | Classified system; we use reasonable engineering estimate |
| J-20 actual timing implementation | Unknown | **LOW** | No public specifications available |
| Timing under GPS jamming | Degraded | **LOW** | Depends on jamming power, waveform, ECCM |

#### Limitation: Timing Error Under Realistic Conditions

```
Ideal conditions (clear sky, no jamming):
  GPS receiver: 5 ns RMS
  GPSDO: 2 ns RMS
  Distribution: 0.5 ns RMS
  Total: ~6 ns RMS ✓

Realistic combat conditions:
  GPS receiver: 10-20 ns RMS (multipath, dynamics)
  GPSDO: 5 ns RMS (thermal stress)
  Platform motion: +5-10 ns (Sagnac, relativity)
  Jamming environment: +10-50 ns (degraded)
  Total: 20-80 ns RMS (highly variable)

CRITICAL LIMITATION:
  The 15-20 ns timing accuracy in our CAD represents IDEAL conditions.
  In contested environments, actual timing may be 2-5x worse.
  This directly impacts TDOA geolocation accuracy.
```

---

### 1.2 RF Sensors (HW-2) - Accuracy Assessment

#### Known with High Confidence

| Parameter | Specified Value | Confidence | Source |
|-----------|-----------------|------------|--------|
| Receiver noise figure | 2-4 dB | **HIGH** | LNA technology limits, commercial products |
| ADC resolution | 12-14 bit | **HIGH** | Commercially available (AD9680, etc.) |
| Instantaneous bandwidth | 1-2 GHz | **HIGH** | State of art RF digitizers |

#### Estimated with Medium Confidence

| Parameter | Specified Value | Confidence | Source |
|-----------|-----------------|------------|--------|
| ALR-94 sensitivity | -120 to -130 dBm | **MEDIUM** | Published estimates, not official specs |
| Chinese ESM sensitivity | -115 to -120 dBm | **MEDIUM** | Inferred from technology generation |
| Calibration accuracy | ±1 dB | **MEDIUM** | Achievable with proper cal sources |

#### Unknown / Low Confidence

| Parameter | Specified Value | Confidence | Issue |
|-----------|-----------------|------------|-------|
| Actual F-35 ASQ-239 specs | Unknown | **LOW** | Classified; estimates only |
| Chinese CETC-14 actual performance | Unknown | **LOW** | Optimistic claims, no verification |
| Performance vs. sophisticated jamming | Degraded | **LOW** | Highly scenario-dependent |

#### Limitation: Sensitivity vs. Real-World Conditions

```
Laboratory sensitivity (datasheets):
  Noise figure: 3 dB
  Bandwidth: 10 MHz
  Sensitivity: -174 + 3 + 10log10(10e6) = -101 dBm (instantaneous)
  With integration (1s): -121 dBm ✓

Real-world sensitivity (combat):
  Noise figure: 4-5 dB (aging, temperature)
  Interference: +10-30 dB floor (dense RF environment)
  Platform noise: +3-10 dB (own-ship RFI)
  Effective sensitivity: -90 to -110 dBm (10-30 dB worse)

CRITICAL LIMITATION:
  The -120 dBm sensitivity in our CAD is the BEST CASE.
  Real environments have orders of magnitude more noise.
  Sidelobe detection range may be 2-10x shorter than calculated.
```

---

### 1.3 MADL/LPI Datalink Parameters (Target) - Accuracy Assessment

#### This is the Most Critical Unknown

| Parameter | Our Estimate | Confidence | Source |
|-----------|--------------|------------|--------|
| MADL frequency | 14.5-15.5 GHz | **MEDIUM** | Congressional testimony, industry publications |
| MADL transmit power | 1-10 W | **LOW** | Speculation; could be 0.1-50 W |
| MADL antenna gain | 30-35 dBi | **MEDIUM** | Reasonable for stated beamwidth |
| MADL beamwidth | 2-5 degrees | **MEDIUM** | Industry publications, antenna physics |
| MADL sidelobe level | -30 dB | **LOW** | Pure speculation; could be -20 to -45 dB |
| MADL duty cycle | 1-10% | **LOW** | Unknown; burst comm typical |
| MADL burst duration | 50-150 μs | **LOW** | Speculation based on similar systems |

#### Why MADL Parameters are Unknowable

```
MADL (Multifunction Advanced Data Link) is a classified system.
No official specifications have been publicly released.

Our estimates are based on:
1. Congressional testimony mentioning "Ku-band" and "directional"
2. Industry publications describing LPI datalink concepts
3. Physics-based reasoning about antenna size/beamwidth
4. Comparison to known systems (Link 16, IFDL, CDL)

THE HONEST TRUTH:
  - MADL sidelobe level could be -20 dB or -50 dB
  - At -20 dB: Detection range ~200 km (easily detected)
  - At -50 dB: Detection range ~5 km (virtually undetectable)
  - We use -30 dB as middle ground, but this is A GUESS

This uncertainty propagates through ALL detection calculations.
Our 75 km detection range could actually be 15 km or 250 km.
```

---

### 1.4 Antenna Array (HW-3) - Accuracy Assessment

#### Known with High Confidence

| Parameter | Specified Value | Confidence | Source |
|-----------|-----------------|------------|--------|
| Phased array physics | Exact | **HIGH** | Electromagnetic theory, textbooks |
| Element spacing effects | Exact | **HIGH** | Array theory (λ/2 spacing) |
| Beamwidth formula | Exact | **HIGH** | θ ≈ 0.886λ/(N×d) |
| Sidelobe theory | Exact | **HIGH** | Fourier analysis, Taylor weighting |

#### Estimated with Medium Confidence

| Parameter | Specified Value | Confidence | Source |
|-----------|-----------------|------------|--------|
| T/R module performance | 5-10 W, 2-3 dB NF | **MEDIUM** | GaN technology state of art |
| Digital beamformer capability | 4-16 nulls | **MEDIUM** | COTS processor capabilities |
| F-35 APG-81 element count | ~1200 | **MEDIUM** | Industry estimates |

#### Unknown / Low Confidence

| Parameter | Specified Value | Confidence | Issue |
|-----------|-----------------|------------|-------|
| J-20 Type 1475 actual specs | Unknown | **LOW** | No verified public data |
| Adaptive null depth in practice | 20-45 dB | **LOW** | Scenario-dependent |
| Element failure rates in combat | Unknown | **LOW** | No combat data available |

#### Limitation: Array Performance Under Stress

```
Ideal array performance:
  64 elements: 18 dBi gain
  Sidelobe level: -30 dB (Taylor weighted)
  Null depth: 40 dB (4 nulls)

Combat degradation factors:
  Element failures (5%): -0.4 dB gain, +1.5 dB sidelobes
  Phase calibration drift: +0.5-2 dB sidelobes
  Thermal effects: Variable phase errors
  Physical damage: Unpredictable

LIMITATION:
  Our CAD assumes near-ideal array performance.
  Real combat performance will be degraded.
  Sidelobe levels may be 5-15 dB worse than nominal.
```

---

### 1.5 Weapon Datalink (HW-4) - Accuracy Assessment

#### Known with High Confidence

| Parameter | Specified Value | Confidence | Source |
|-----------|-----------------|------------|--------|
| Link budget math | Exact | **HIGH** | Friis equation, RF engineering |
| Atmospheric attenuation | < 1 dB @ 100 km | **HIGH** | ITU-R P.676 standard |
| AIM-120 has datalink | Yes | **HIGH** | Public DoD announcements |

#### Estimated with Medium Confidence

| Parameter | Specified Value | Confidence | Source |
|-----------|-----------------|------------|--------|
| AIM-120D data rate | 16-64 kbps | **MEDIUM** | Industry estimates |
| AIM-120D update rate | 0.5-2 Hz | **MEDIUM** | Reasonable for mid-course |
| Two-way datalink | Yes | **MEDIUM** | Implied by "D" variant improvements |

#### Unknown / Low Confidence

| Parameter | Specified Value | Confidence | Issue |
|-----------|-----------------|------------|-------|
| **PL-15 datalink specs** | Unknown | **LOW** | Speculative; based on missile capability claims |
| **PL-15 AESA seeker** | Unknown | **LOW** | Chinese claims, no verification |
| **PL-15 range** | 200+ km claim | **LOW** | Marketing; actual NEZ unknown |
| **Message formats** | Fabricated | **VERY LOW** | We created plausible formats; not real |

#### Critical Limitation: PL-15 Specifications

```
THE PL-15 SPECIFICATIONS IN THIS CAD ARE LARGELY FABRICATED.

What we know (public sources):
  - PL-15 exists and is operational
  - It has "very long range" (200+ km claimed)
  - It likely has an AESA seeker (photos suggest large seeker)
  - It has a datalink (standard for modern AAMs)

What we made up (plausible engineering estimates):
  - 100 kbps uplink (guess)
  - Multi-target AESA seeker (inference from size)
  - Specific message formats (entirely fabricated)
  - Two-way datalink details (assumed based on technology)

HONESTY STATEMENT:
  The PL-15 sections represent "what a modern missile might have"
  not "what the PL-15 actually has." Actual specs are classified
  and may be significantly different.
```

---

### 1.6 Geolocation Accuracy - Accuracy Assessment

#### Known with High Confidence (Mathematics)

| Algorithm | Theoretical Accuracy | Confidence | Source |
|-----------|---------------------|------------|--------|
| TDOA geometry | Exact | **HIGH** | Hyperbolic positioning theory |
| FDOA formulas | Exact | **HIGH** | Doppler physics |
| Cramér-Rao bounds | Exact | **HIGH** | Information theory |
| GDOP calculations | Exact | **HIGH** | GPS navigation theory |

#### Estimated with Medium Confidence

| Parameter | Specified Value | Confidence | Source |
|-----------|-----------------|------------|--------|
| TDOA CEP (4 platforms) | 200-500 m | **MEDIUM** | Achievable with 10 ns timing |
| Combined TDOA+DF CEP | < 100 m | **MEDIUM** | Fusion improves accuracy |
| DF accuracy (Ku-band) | 1-2 degrees | **MEDIUM** | Interferometer physics |

#### Geolocation Error Budget - Realistic Assessment

```
IDEAL CONDITIONS (lab/simulation):

  Timing error: 10 ns
  Position error: c × 10 ns = 3 meters
  GDOP: 2.0 (good geometry)
  Measurement noise: 10 ns RMS
  TDOA CEP: √(2) × 3m × 2 = ~8 meters per baseline
  4-platform TDOA: ~200 meters CEP ✓

REALISTIC CONDITIONS (combat):

  Timing error: 30-50 ns (GPS degraded, jamming)
  Position error: 9-15 meters
  GDOP: 3-10 (constrained geometry)
  Measurement noise: 50-100 ns (weak signal, multipath)
  Atmospheric effects: +50-200 ns (ionosphere, weather)
  TDOA CEP: 500-3000 meters

CRITICAL LIMITATIONS:

1. GEOMETRY DEPENDENCY
   - Our CAD assumes favorable geometry (GDOP ~2)
   - Real scenarios may have GDOP 5-20
   - CEP scales linearly with GDOP
   - 1 km CEP at GDOP 2 becomes 5 km CEP at GDOP 10

2. TIMING SYNCHRONIZATION
   - Our CAD assumes 15-20 ns sync
   - GPS jamming can degrade to 100+ ns
   - Each 10 ns error adds ~3 m position error

3. SIGNAL WEAKNESS
   - Sidelobe detection at edge of sensitivity
   - SNR may be 0-3 dB (barely detectable)
   - Low SNR degrades ToA measurement by 10-100×

4. PROPAGATION EFFECTS
   - Ionospheric delay: Variable (10-100 ns at Ku-band)
   - Tropospheric: 3-10 ns/km at low elevation
   - Rain: Adds multipath and attenuation

HONEST ASSESSMENT:
  The 200-500 m CEP in our CAD is OPTIMISTIC.
  Realistic combat CEP may be 1-5 km.
  In degraded conditions, CEP could exceed 10 km.
```

---

## Part 2: Source Classification and Confidence Levels

### 2.1 Source Taxonomy

| Source Type | Confidence | Description | Examples |
|-------------|------------|-------------|----------|
| **PHYSICS** | VERY HIGH | Fundamental laws, cannot be wrong | Maxwell's equations, Friis, Doppler |
| **STANDARDS** | HIGH | Validated industry/government specs | ITU-R, MIL-STD, IEEE |
| **DATASHEETS** | HIGH | Commercial product specifications | Symmetricom GPSDO, Analog Devices ADC |
| **ACADEMIC** | MEDIUM-HIGH | Peer-reviewed publications | IEEE Trans, AIAA papers |
| **OSINT** | MEDIUM | Open source intelligence | Jane's, Aviation Week, Congressional testimony |
| **INFERENCE** | LOW-MEDIUM | Derived from physics + partial data | Antenna size → beamwidth |
| **SPECULATION** | LOW | Educated guessing | MADL sidelobe levels |
| **FABRICATION** | VERY LOW | Made up but plausible | PL-15 message formats |

### 2.2 Specification Source Mapping

| Specification | Primary Source | Confidence |
|---------------|----------------|------------|
| GPS timing 5 ns | Datasheets (Trimble, Symmetricom) | HIGH |
| RF receiver 3 dB NF | Commercial LNA specs | HIGH |
| TDOA algorithm | Academic (IEEE papers) | VERY HIGH |
| MADL 15 GHz | Congressional testimony | MEDIUM |
| MADL sidelobe -30 dB | Speculation | LOW |
| MADL burst 100 μs | Inference from LPI design | LOW |
| PL-15 200 km range | Chinese press releases | LOW |
| PL-15 AESA seeker | Photo analysis, inference | LOW |
| PL-15 datalink protocol | Fabrication | VERY LOW |
| F-35 EW suite specs | Speculation + physics | LOW |
| J-20 radar specs | Speculation + inference | LOW |

---

## Part 3: Error Propagation Analysis

### 3.1 End-to-End Error Chain

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR PROPAGATION CHAIN                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
│  │ TIMING ERROR │──▶│ DETECTION    │──▶│ GEOLOCATION  │──▶│ ENGAGEMENT   │ │
│  │              │   │ ERROR        │   │ ERROR        │   │ ERROR        │ │
│  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘ │
│                                                                              │
│  Input: 10-50 ns    Input: Unknown    Input: All prior    Output: Miss     │
│                     sidelobe level    errors              distance         │
│                                                                              │
│  Effect:            Effect:           Effect:             Effect:           │
│  3-15 m baseline    Unknown det.      100-3000 m CEP      Pk degradation   │
│  error              range                                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Monte Carlo Uncertainty Analysis

```python
# Conceptual error propagation model

import numpy as np

def estimate_engagement_uncertainty():
    """
    Monte Carlo analysis of end-to-end uncertainty
    """
    n_samples = 10000

    # Input distributions (representing our uncertainty)
    timing_error_ns = np.random.uniform(10, 80, n_samples)  # 10-80 ns
    sidelobe_level_dB = np.random.uniform(-40, -20, n_samples)  # Unknown
    geometry_gdop = np.random.uniform(2, 10, n_samples)  # Varies
    snr_dB = np.random.uniform(0, 20, n_samples)  # Depends on range

    # Error propagation
    timing_position_error = timing_error_ns * 0.3  # ~0.3 m per ns
    detection_range_variation = 10 ** (sidelobe_level_dB / 20)  # Linear
    geolocation_cep = timing_position_error * geometry_gdop * (10 / snr_dB)

    # Results
    cep_5th = np.percentile(geolocation_cep, 5)
    cep_50th = np.percentile(geolocation_cep, 50)
    cep_95th = np.percentile(geolocation_cep, 95)

    return {
        'best_case_cep': f"{cep_5th:.0f} m",
        'typical_cep': f"{cep_50th:.0f} m",
        'worst_case_cep': f"{cep_95th:.0f} m"
    }

# Illustrative results:
# Best case: ~100 m CEP
# Typical: ~800 m CEP
# Worst case: ~5000 m CEP
```

### 3.3 Sensitivity Analysis

| Error Source | Baseline | +50% Degradation | Impact on CEP |
|--------------|----------|------------------|---------------|
| Timing sync | 15 ns | 22 ns | +50% CEP |
| GDOP | 2.5 | 3.75 | +50% CEP |
| SNR | 10 dB | 5 dB | +200% CEP |
| Sidelobe level | -30 dB | -25 dB | Detection range +78% |
| Atmospheric | 0 dB | 3 dB | Detection range -30% |

**Key Finding:** SNR is the most sensitive parameter. A 5 dB SNR reduction triples geolocation error.

---

## Part 4: What We Fundamentally Cannot Know

### 4.1 Classification Barriers

The following are classified and will likely remain unknown:

| System | Classification | Implication |
|--------|---------------|-------------|
| MADL waveform details | TS/SCI (US) | Cannot know detection signature |
| F-35 EW suite specs | TS/SCI (US) | Cannot verify Chinese claims |
| J-20 actual radar specs | SECRET (PRC) | Cannot verify capabilities |
| PL-15 guidance details | SECRET (PRC) | Cannot verify engagement envelope |
| Actual engagement results | TS (both) | No ground truth for validation |

### 4.2 Unknowable Operational Variables

| Variable | Why Unknown | Impact |
|----------|-------------|--------|
| Pilot skill | Human factor | Large variance in outcomes |
| Maintenance state | Classified | Unknown real-world reliability |
| Countermeasure effectiveness | Classified + scenario-dependent | Could change everything |
| Actual tactics | Classified | Our assumptions may be wrong |
| Environmental conditions | Mission-specific | Rain, terrain, ionosphere vary |

### 4.3 Simulation vs. Reality Gap

```
FUNDAMENTAL LIMITATION:

This simulation models PHYSICS and ALGORITHMS.
It cannot model:
  - Human decision-making
  - Equipment failures
  - Unknown countermeasures
  - Classified capabilities
  - Psychological factors
  - Communication breakdowns
  - Fratricide prevention
  - Rules of engagement
  - Weather (realistically)
  - Terrain masking (fully)

A real engagement involves factors we cannot simulate.
Any claimed "probability of kill" or "engagement success rate"
is MEANINGLESS without classified validation data.

WE DO NOT CLAIM:
  - This system would work
  - These tactics would succeed
  - These specifications are accurate
  - China could defeat the F-35
  - Any specific engagement outcome

WE DO CLAIM:
  - The physics models are correct
  - The algorithms are sound
  - The hardware specs are reasonable
  - The limitations are real
```

---

## Part 5: Accuracy Improvements and Validation Path

### 5.1 What Would Improve Accuracy

| Improvement | Feasibility | Impact |
|-------------|-------------|--------|
| Measure MADL sidelobes directly | Impossible (classified) | Would eliminate largest uncertainty |
| Field test with friendly LPI systems | Possible | Would validate detection algorithms |
| Access to military GPS timing | Possible (with authorization) | Would validate timing assumptions |
| Independent J-20 assessment | Difficult | Would verify Chinese claims |
| Combat data analysis | Impossible | Would provide ground truth |

### 5.2 Validation Approach (What We CAN Do)

```
TESTABLE COMPONENTS:

1. RF Propagation Models
   - Compare ITU-R predictions to measurements
   - Validate with commercial RF test equipment
   - Achievable accuracy: < 1 dB

2. TDOA Algorithms
   - Test with known emitter positions
   - Use commercial COTS GPS and RTK
   - Achievable CEP: Verify to < 1 m

3. Signal Processing
   - Test detection algorithms on synthetic signals
   - Measure Pd vs. SNR curve
   - Validate with RF signal generators

4. Timing Distribution
   - Measure actual GPSDO performance
   - Verify TDU skew and jitter
   - Compare to datasheet specs

UNTESTABLE COMPONENTS:

1. MADL interception (would require access to F-35)
2. PL-15 datalink (would require access to missile)
3. Combat effectiveness (would require war)
```

---

## Part 6: Honest System Assessment

### 6.1 Overall System Confidence

| Subsystem | Technical Accuracy | Operational Validity | Overall |
|-----------|-------------------|---------------------|---------|
| GPS Timing | HIGH | MEDIUM | MEDIUM-HIGH |
| RF Sensors | HIGH | MEDIUM | MEDIUM |
| Antenna Array | HIGH | MEDIUM | MEDIUM |
| Detection Algorithms | HIGH | LOW (untested on MADL) | MEDIUM |
| Geolocation | HIGH | MEDIUM | MEDIUM |
| Network Inference | MEDIUM | LOW | LOW-MEDIUM |
| Weapon Datalink | MEDIUM | LOW (specs unknown) | LOW |
| PL-15 Integration | LOW | VERY LOW | LOW |
| Overall System | MEDIUM | LOW | **LOW** |

### 6.2 What This CAD Actually Represents

```
THIS SIMULATION IS:
  ✓ A technically rigorous educational exercise
  ✓ Based on sound physics and engineering
  ✓ Representative of real EW challenges
  ✓ Useful for understanding concepts
  ✓ Honest about its limitations

THIS SIMULATION IS NOT:
  ✗ An operational weapon system
  ✗ Based on classified intelligence
  ✗ Validated against real targets
  ✗ A prediction of combat outcomes
  ✗ Proof that any system "works"

APPROPRIATE USES:
  - Education about EW concepts
  - Understanding detection physics
  - Studying geolocation algorithms
  - Exploring system trade-offs
  - Research and analysis

INAPPROPRIATE USES:
  - Claiming operational capability
  - Predicting engagement outcomes
  - Intelligence assessments
  - Actual weapon development
  - Strategic planning
```

### 6.3 Key Takeaways

1. **The largest uncertainties are in the target (MADL) specifications.** Everything downstream depends on sidelobe levels we cannot know.

2. **Geolocation accuracy varies enormously** with conditions. The 200-500 m CEP is optimistic; 1-5 km is realistic.

3. **PL-15 specifications are largely fabricated** based on plausible engineering. They should not be cited as fact.

4. **The simulation correctly models physics** but cannot model operational realities.

5. **Any claimed "kill probability" would be meaningless** without classified validation.

---

## Appendix A: Uncertainty Quantification Summary

| Parameter | Best Estimate | Uncertainty Range | Distribution |
|-----------|---------------|-------------------|--------------|
| MADL frequency | 15 GHz | 14-16 GHz | Uniform |
| MADL power | 3 W | 0.5-20 W | Log-uniform |
| MADL sidelobe | -30 dB | -20 to -45 dB | Uniform |
| Detection range | 75 km | 15-250 km | Depends on sidelobe |
| TDOA CEP | 400 m | 100-3000 m | Log-normal |
| Timing error | 20 ns | 10-100 ns | Log-normal |
| PL-15 range | 200 km | 150-300 km | Triangular |

## Appendix B: References for Verifiable Specifications

### Physics and Standards (VERIFIED)
- ITU-R P.676 (Gaseous attenuation) - International standard
- ITU-R P.838 (Rain attenuation) - International standard
- MIL-STD-1553 (Digital databus) - Public military standard
- IEEE 1588 (Precision time protocol) - Commercial standard

### Commercial Datasheets (VERIFIED)
- Symmetricom XLi GPSDO - Product data sheet
- Trimble Thunderbolt E - Product data sheet
- Analog Devices AD9680 - ADC data sheet
- Xilinx RFSoC - Product specifications

### Open Source Intelligence (PARTIALLY VERIFIED)
- Congressional testimony on F-35 capabilities
- Aviation Week articles on MADL
- Jane's Defence on J-20 and PL-15

### Estimates and Speculation (UNVERIFIED)
- MADL sidelobe levels - Engineering estimate
- PL-15 seeker specifications - Inference
- Chinese hardware performance - Claims

---

*This document represents an honest assessment of what we know and don't know. Users should understand these limitations before drawing any conclusions from simulation results.*

**Document Classification:** UNCLASSIFIED // EDUCATIONAL
**Prepared for:** Technical analysis and education only
**Date:** 2025-12-28
