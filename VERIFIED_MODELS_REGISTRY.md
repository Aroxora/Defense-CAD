# Operationally Verified Models Registry

**Classification**: UNCLASSIFIED // PUBLIC RELEASE

This document serves as the authoritative registry of which aircraft models, platforms, and pretrained models are **operationally verified** and therefore approved for use in CI/CD testing and Computer-Aided Deduction (CAD) assessments.

## Purpose

To ensure that all simulation, testing, and CAD workflows use **only** models based on:
- **Classified** best estimates derived from deductive reasoning
- **Operationally verified** platforms (fielded/deployed systems, not concepts)
- **Useful** scenarios that provide actionable intelligence

## Registry

### ✓ VERIFIED Models (Approved for CI/CD Testing)

These models are based on platforms that are **in operational service** and have sufficient publicly observable data to support deductive reasoning with acceptable confidence levels.

| Model | Platform | Status | Fielded Date | Confidence | Basis |
|-------|----------|--------|--------------|------------|-------|
| **F35ARCSModel** | F-35A Lightning II | VERIFIED | 2015 | 55% | Fielded by USAF, observable features, congressional testimony |
| **J20RCSModel** | J-20 Mighty Dragon | VERIFIED | 2017 | 50% | Fielded by PLAAF, public imagery, deductive canard analysis |
| **J20RadarModel** | J-20 AESA Radar | VERIFIED | 2017 | 85% | Element count deduced from aperture size (75 cm nose) |
| **PL15TargetingModel** | PL-15 Missile | VERIFIED | Fielded | 60% | Operational missile, rocket equation + drag model |
| **DF17HGVModel** | DF-17 Hypersonic Glide Vehicle | VERIFIED | 2019 | 55% | Fielded by PLARF, 2019 parade observations, physics-based trajectory model |
| **DF21DModel** | DF-21D Medium-Range Ballistic Missile | VERIFIED | 2010 | 55% | Fielded ASBM/land-attack variant, DoD reporting, physics-based trajectory |
| **DF26Model** | DF-26 Intermediate-Range Ballistic Missile | VERIFIED | 2016 | 50% | Fielded IRBM "Guam Killer", parade observations, range/accuracy estimates |
| **IskanderMModel** | 9K720 Iskander-M Short-Range Ballistic Missile | VERIFIED | 2006 | 65% | Extensively fielded, combat-proven in Syria/Ukraine, Russian disclosures |
| **ATACMSModel** | MGM-140 ATACMS Tactical Missile | VERIFIED | 1991 | 70% | US Army tactical missile, well-documented specifications, combat-proven |
| **J10CRCSModel** | J-10C Vigorous Dragon | VERIFIED | 2006/2015 | 55% | Delta-canard multirole fighter, fielded by PLAAF, observable features |
| **J11BRCSModel** | J-11B Flanker | VERIFIED | 2007 | 60% | Chinese Su-27 variant, large 4th-gen airframe, public imagery |
| **J15RCSModel** | J-15 Flying Shark | VERIFIED | 2013 | 55% | Carrier-capable J-11 variant, reinforced airframe, folding wings observed |
| **J16RCSModel** | J-16 Red Eagle | VERIFIED | 2015 | 55% | Strike fighter with RAM coatings, J-11BS basis, modern ECM |
| **Su35RCSModel** | Su-35 Flanker-E | VERIFIED | 2014/2018 | 65% | 4++ gen fighter, RCS reduction measures, well-documented Russian system |
| **H6KRCSModel** | H-6K Badger | VERIFIED | 2009 | 65% | Strategic bomber, modernized Tu-16, observable large airframe |
| **Su57RCSModel** | Su-57 Felon | VERIFIED | 2020 | 50% | 5th-gen stealth fighter, internal weapons bays, stealth shaping |
| **Su30SMRCSModel** | Su-30SM Flanker-H | VERIFIED | 2012 | 65% | Multirole fighter with canards, Su-27 basis, combat-proven |
| **MiG31RCSModel** | MiG-31 Foxhound | VERIFIED | 1981/2011 | 70% | Interceptor, long service history, well-documented, upgraded BM variant |
| **Su34RCSModel** | Su-34 Fullback | VERIFIED | 2014 | 65% | Strike aircraft, platypus nose, side-by-side seating, combat-proven |
| **Type052DModel** | Type 052D Destroyer (Luyang III) | VERIFIED | 2014 | 60% | PLA Navy multi-role destroyer, Type 346A AESA, HQ-9B SAM, public imagery |
| **Type052DModel_Enhanced** | Type 052D Enhanced (Loudi) | VERIFIED | 2026 | 60% | Enhanced variant with dual-face rotating AESA, improved coordination, Global Times reporting |

**Platform Database Entries (Verified):**
- **F35A**: F-35A Lightning II (USA, fielded 2015)
- **J20**: J-20 Mighty Dragon (China, fielded 2017)
- **E3**: E-3 Sentry AWACS (USA, operational)
- **DF17**: DF-17 HGV (China, fielded 2019)

**Weapons (Verified):**
- AIM-120D, AIM-9X (USA, fielded)
- PL-15, PL-21, PL-10 (China, fielded)
- DF-17 HGV (China, fielded 2019 - ASBM/precision strike)
- DF-21D MRBM (China, fielded 2010 - ASBM/land-attack)
- DF-26 IRBM (China, fielded 2016 - dual-capable precision strike)
- Iskander-M SRBM (Russia, fielded 2006 - high-precision tactical)
- ATACMS (USA, fielded 1991 - tactical ballistic missile)
- Meteor (Europe, fielded)

**Target Platforms (Verified for defensive CAD):**
- CVN Aircraft Carriers (Nimitz/Ford class - USA, operational since 1975/2017)
- Type 003 Fujian Aircraft Carrier (China, commissioned November 2025)
- DDG Destroyers with Aegis BMD (Arleigh Burke class - USA, operational since 1991)
- CG Cruisers with Aegis (Ticonderoga class - USA, operational since 1983)
- Type 052D Destroyers (Luyang III-class - China, operational since 2014)
- Type 052D Enhanced Destroyers (Loudi variant - China, operational since 2026)
- Land targets (Fixed infrastructure, generic facilities)

**Excluded Target Platforms (Not Approved for DF-17 ASBM Testing):**
- DDG-1000 Zumwalt-class (limited deployment, not typical CSG composition)
- LCS Littoral Combat Ships (Freedom/Independence class - not ASBM targets)
- SSN/SSBN Submarines (not useful for ASBM surface strike scenarios)
- Concept/experimental platforms (future ships, not operationally verified)
- CVN Aircraft Carriers (Nimitz/Ford class - USA)
- DDG Destroyers with Aegis BMD (Arleigh Burke class - USA)
- Patriot PAC-3 SAM batteries (USA/Allied - air defense targets)
- THAAD BMD batteries (USA - ballistic missile defense targets)
- S-400 SAM batteries (Russia - air defense targets)
- S-300PMU-2 SAM batteries (Russia/Export - air defense targets)

---

### ✗ EXCLUDED Models (Not Approved for CI/CD Testing)

These models are based on platforms that are **not operationally fielded** or are concept-level systems with insufficient observable data. They are defined in the codebase for research purposes but **must not** be used in CI/CD tests or operational CAD assessments.

| Model | Platform | Status | Reason for Exclusion | Confidence |
|-------|----------|--------|----------------------|------------|
| **SixthGenRCSModel** | NGAD 6th-Gen Fighter | EXCLUDED | Concept-level, not fielded, post-2030 timeframe | 20% |
| **MQ28RCSModel** | MQ-28 Ghost Bat | EXCLUDED | Development phase, not deployed operationally | 40% |

**Platform Database (Excluded):**
- **NGAD**: 6th-generation fighter (concept, not fielded)
- **MQ28**: MQ-28 Ghost Bat (development, not deployed)

---

## Verification Criteria

For a model to be **VERIFIED** and approved for CI/CD testing, it must meet **ALL** of the following criteria:

### 1. Fielded/Deployed Status
- Platform must be **in operational service** (not in development, not concept)
- Must have **fielded examples** in active military use
- Examples:
  - ✓ F-35A: In service since 2015 across multiple countries
  - ✓ J-20: Fielded since 2017 by PLAAF
  - ✗ NGAD: Post-2030 concept, no fielded examples
  - ✗ MQ-28: Still in development, not operationally deployed

### 2. Observable Data Availability
- Confidence must be **≥ 40%** from publicly available data
- Observable from:
  - Public photographs/imagery
  - Congressional testimony
  - Manufacturer technical specifications
  - OSINT (Open Source Intelligence)
  - Physics-based deduction from measurable features
- Examples:
  - ✓ J-20 AESA element count: Deduced from 75 cm nose diameter (observable)
  - ✓ F-35 RCS: Observable fuselage features + VLO design principles
  - ✗ NGAD RCS: No observable prototype, purely speculative

### 3. Classified Best Estimates Available
- Must have documented reasoning chain in `CLASSIFIED_BEST_ESTIMATES.md`
- Must include uncertainty quantification (± ranges)
- Must have explicit confidence percentage
- All estimates derived through deductive reasoning (not guessing)

### 4. Deductive Reasoning Chain
- Must be derivable through pure logic from:
  - Observable facts (100% certain)
  - Physical laws (100% certain)
  - Engineering constraints (high certainty)
- Documented in `reasoning_chains/` directory as YAML files
- Verified by `reasoning_chains/validate.py`

### 5. Operational Utility
- Model must produce **actionable intelligence** for defensive CAD
- Must be relevant to current or near-term threat assessments
- Must have tactical/strategic value for mission planning

---

## CI/CD Enforcement

The CI/CD workflow (`simulation-accuracy-check.yml`) **automatically enforces** this registry through:

### 1. Comprehensive File Scanning
- Scans **all Python files** for imports or usage of excluded models
- Checks for platform references (NGAD, MQ-28, etc.)
- Allows excluded models only in:
  - `rcs_models.py` (definition file)
  - Comments explaining exclusion

### 2. Test Filtering
- `test_defensive_cad_missiles.py`: Tests ONLY F-35A, J-20, E-3
- `test_pretrained_models.py`: Tests ONLY J-20 and F-35 models
- `test_pla_vs_dod_cad.py`: Tests ONLY J-20 vs F-35A scenarios
- `test_df17_hypersonic.py`: Tests ONLY DF-17 HGV vs CVN/DDG/CG/land targets
- `test_df17_carrier_strike_integration.py`: Tests ONLY realistic CSG formations
- `test_df17_hypersonic.py`: Tests ONLY DF-17 HGV vs carrier/land targets
- `test_sead_ballistic_missiles.py`: Tests ONLY DF-21D, DF-26, Iskander-M, ATACMS vs air defense targets
- No tests for NGAD or MQ-28
- No tests for non-useful targets (LCS, SSN, Zumwalt)

### 3. Database Filtering
- `eob_database.py`: Includes ONLY verified platforms
- Comments explicitly state exclusions:
  ```python
  # EXCLUDED (not operationally verified):
  #   - MQ28RCSModel (development, not deployed)
  #   - SixthGenRCSModel (concept-level, not fielded)
  ```

### 4. Validation Steps
- Workflow step: "Verify only operationally verified models are tested"
  - Scans all Python files for violations
  - **FAILS** CI/CD if non-verified models are imported or used
- Workflow step: "Verify DF-17 targets are operationally verified and useful"
  - Validates all DF-17 target creation functions
  - Checks for excluded target types (LCS, SSN, Zumwalt, concept platforms)
  - **FAILS** CI/CD if non-useful targets are defined or used

---

## Usage Guidelines

### For Developers

**DO:**
- ✓ Use F35ARCSModel, J20RCSModel, DF17HGVModel, DF21DModel, DF26Model for CAD assessments
- ✓ Test scenarios with F-35A, J-20, E-3, CVN carriers, DDG destroyers, air defense batteries
- ✓ Reference PL-15, AIM-120D, DF-17 HGV, DF-21D, DF-26, Iskander-M, ATACMS missiles in simulations
- ✓ Test USEFUL scenarios: air-to-air (J-20/F-35), anti-ship (DF-17/CVN), SEAD (ballistic missiles/SAMs)
- ✓ Add new models ONLY if platform is operationally verified
- ✓ Document confidence levels and uncertainty bounds

**DO NOT:**
- ✗ Import SixthGenRCSModel or MQ28RCSModel in tests
- ✗ Add NGAD or MQ-28 to EOB database
- ✗ Create test scenarios for non-fielded platforms
- ✗ Use concept platforms in CI/CD workflows
- ✗ Guess parameters without deductive reasoning

### For Reviewers

When reviewing PRs, verify:
1. No imports of SixthGenRCSModel or MQ28RCSModel outside rcs_models.py
2. No platform database entries for NGAD or MQ-28
3. All new models have fielded status + confidence ≥ 40%
4. Test scenarios use only verified platforms
5. CI/CD checks pass (comprehensive verification)

---

## Model Confidence Levels

| Confidence Range | Classification | Usage |
|------------------|----------------|-------|
| **≥ 70%** | High | Operational parameters, well-deduced values |
| **50-70%** | Medium | Classified best estimates, moderate uncertainty |
| **40-50%** | Low-Medium | Acceptable for verified platforms with limited data |
| **< 40%** | Low | **NOT APPROVED** for CI/CD testing |

---

## Adding New Models

To add a new model to the VERIFIED registry:

1. **Verify Operational Status**
   - Confirm platform is fielded/deployed (not development or concept)
   - Find public sources confirming operational service
   - Document fielding date

2. **Establish Observable Data**
   - Gather public imagery, specifications, testimony
   - Ensure confidence can reach ≥ 40%
   - Document observable features

3. **Create Reasoning Chain**
   - Write YAML reasoning chain in `reasoning_chains/`
   - Show deductive steps from observables → estimate
   - Quantify uncertainty at each step
   - Run `reasoning_chains/validate.py`

4. **Document in CLASSIFIED_BEST_ESTIMATES.md**
   - Add parameter estimates with ± ranges
   - Include confidence percentages
   - Cite sources (public only)

5. **Update This Registry**
   - Add entry to VERIFIED table above
   - Document confidence and basis
   - Update CI/CD enforcement notes if needed

6. **Update CI/CD Workflow**
   - Add model to verified list in workflow
   - Ensure comprehensive check includes it
   - Test that CI/CD passes

---

## Rationale

### Why Exclude Concept Platforms?

**NGAD (6th-Gen Fighter):**
- No fielded examples (post-2030 timeframe)
- No observable prototypes
- RCS estimates purely speculative (20% confidence)
- Using NGAD in assessments would undermine credibility
- Cannot deductively reason about non-existent aircraft

**MQ-28 Ghost Bat:**
- Still in development (test flights only)
- Not deployed operationally
- Limited public data (40% confidence)
- Capabilities unproven in operational context
- Including would conflate "possible" with "fielded"

### Why This Matters

**Scientific Integrity:**
- Deductive reasoning requires observable facts
- Speculation ≠ deduction
- Confidence levels must reflect reality

**Operational Utility:**
- CAD assessments inform real mission planning
- Must be based on actual threats (not hypothetical)
- Fielded platforms have proven capabilities

**Legal/Classification:**
- Speculative estimates about concepts could imply classified knowledge
- Limiting to fielded systems ensures all data is public/deducible
- Maintains UNCLASSIFIED // PUBLIC RELEASE status

---

## Changelog

- **2025-12-29**: Added ground-to-ground precision ballistic missile models
  - Added 4 VERIFIED ballistic missile models (DF-21D, DF-26, Iskander-M, ATACMS)
  - Added 4 VERIFIED air defense target systems (Patriot PAC-3, THAAD, S-400, S-300PMU-2)
  - Added SEAD engagement simulation and test suite
  - All models based on fielded systems with 50-70% confidence from public sources

- **2024-XX-XX**: Initial registry created
  - Defined verification criteria (fielded status, confidence ≥ 40%, deductive reasoning)
  - Listed 4 VERIFIED models (F-35A, J-20 RCS/Radar, PL-15)
  - Listed 2 EXCLUDED models (NGAD, MQ-28)
  - Added CI/CD enforcement mechanisms
  - Established comprehensive file scanning validation

---

## Related Documents

- `CLASSIFIED_BEST_ESTIMATES.md`: Parameter estimates with confidence levels
- `DEDUCTIVE_REASONING.md`: Methodology for deriving estimates
- `ACCURACY_AND_LIMITATIONS_CAD.md`: CAD accuracy analysis
- `reasoning_chains/*.yaml`: Deductive reasoning chains for each parameter
- `.github/workflows/simulation-accuracy-check.yml`: CI/CD enforcement

---

**VERIFICATION STATUS**: This registry is automatically enforced by CI/CD.
**LAST VALIDATED**: Every git push (automated check in workflow)

**Classification**: UNCLASSIFIED // PUBLIC RELEASE
**Distribution**: Approved for public release, no restrictions
