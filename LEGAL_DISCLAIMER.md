# Legal Disclaimer and Classification Boundaries

## Document Purpose

This document explicitly defines the legal and classification boundaries of this project to ensure all content remains UNCLASSIFIED and complies with US export control and classification laws.

**Status:** UNCLASSIFIED // PUBLIC RELEASE
**Date:** 2025-12-28

---

## Legal Status

### Classification Level

**ALL CONTENT IN THIS REPOSITORY IS UNCLASSIFIED**

This project contains:
- ✅ Publicly available information (OSINT)
- ✅ Academic research and published papers
- ✅ Physics-based calculations (fundamental laws)
- ✅ Educated guesses based on similar declassified systems
- ✅ Software implementations of well-known algorithms

This project does NOT contain:
- ❌ Classified information
- ❌ Proprietary data from defense contractors
- ❌ Information obtained through unauthorized access
- ❌ Export-controlled technical data (ITAR/EAR)
- ❌ Intelligence sources or methods

---

## Source Classification

### Allowed Sources (Used in This Project)

**1. Open Source Intelligence (OSINT):**
- Congressional testimony (public record)
- GAO reports (publicly released)
- Aviation Week, Jane's Defense (journalism)
- Academic papers (peer-reviewed, published)
- Contractor marketing materials (public)
- ITU-R standards (international public standards)
- Component datasheets (commercial products)

**2. Fundamental Physics:**
- Electromagnetic theory (Maxwell's equations)
- Radar range equation (textbook)
- Information theory (Shannon's theorem)
- Rocket equation (Tsiolkovsky)
- Statistical estimation (Cramér-Rao bounds)

**3. Analogous Systems:**
- Link 16 specifications (declassified)
- Commercial GPS specifications (public)
- Software-defined radio (COTS products)
- Published algorithm descriptions

### Prohibited Sources (NOT Used)

**1. Classified Information:**
- Technical manuals marked CONFIDENTIAL or higher
- Intelligence assessments
- Operational data from military exercises
- Specific capability statements from cleared individuals
- Information marked with classification banners

**2. Proprietary Information:**
- Contractor internal documents (not public)
- Non-public test results
- Proprietary algorithms or source code
- Trade secrets

**3. Export-Controlled Data:**
- ITAR-restricted technical data
- EAR-controlled software with encryption
- Missile Technology Control Regime (MTCR) data

---

## Estimate Methodology Boundaries

### Legal: Physics-Based Inference

```
ALLOWED:
"The antenna aperture is 15 cm (observable). At 14 GHz, the
beamwidth must be approximately θ = 70λ/D = 4° (physics)."

Reasoning: Observable dimension + fundamental physics
Source: None needed (first principles)
Legal: ✅ Unclassified calculation
```

### Legal: Comparison to Declassified Systems

```
ALLOWED:
"MADL is likely similar to TTNT (Tactical Targeting Network Technology),
which uses Ku-band at 10-100 Mbps. We estimate 50 Mbps for MADL."

Reasoning: Published TTNT specifications + similar mission
Source: TTNT white papers (public), Congressional testimony
Legal: ✅ Analogy to known system
```

### Legal: Bounded Uncertainty Ranges

```
ALLOWED:
"MADL sidelobe level is unknown but must be between -20 dB (poor)
and -40 dB (excellent) based on phased array technology limits.
We estimate -30 dB as the midpoint."

Reasoning: Technology constraints + bracketing approach
Source: Phased array textbooks, industry knowledge
Legal: ✅ Uncertainty quantification
```

### ILLEGAL: Specific Classified Values

```
PROHIBITED:
"MADL sidelobe level is exactly -32.5 dB at 14.45 GHz."

Reasoning: Implies access to classified specification
Source: Would require classified document or cleared disclosure
Legal: ❌ Would violate classification laws if true
```

### ILLEGAL: Operational Intelligence

```
PROHIBITED:
"During Exercise Red Flag 21-2, F-35s were detected at 73 km
using the technique described in this repository."

Reasoning: Implies access to operational test data
Source: Would require classified after-action report
Legal: ❌ Operational security violation
```

---

## Export Control Compliance

### ITAR (International Traffic in Arms Regulations)

**What ITAR Controls:**
- Detailed design data for military systems
- Source code directly usable in weapons
- Specific performance characteristics of classified systems

**Why This Project is NOT ITAR-Controlled:**

```
22 CFR 120.10(a)(1) - Public Domain Exception:
"Information which is published and which is generally accessible
or available to the public through sales at newsstands and bookstores,
subscription, libraries, patents... or at conferences, meetings, seminars,
trade shows, or exhibitions generally open to the public."

This project is:
✅ Published on GitHub (public)
✅ Based on public sources (documented)
✅ Educational in nature (stated purpose)
✅ Not specific weapon system design data

Conclusion: Falls under Public Domain Exception
```

**What We Do NOT Include (ITAR-Controlled):**

- ❌ Actual F-35 source code
- ❌ Classified radar waveforms
- ❌ Cryptographic key generation algorithms (EAR-controlled)
- ❌ Specific missile guidance logic (proprietary)

### EAR (Export Administration Regulations)

**Encryption Export Rules (EAR 740.17):**

This project uses:
- Standard cryptography libraries (PyCryptodome)
- Publicly available algorithms (AES, Reed-Solomon)
- Educational/research purpose

Status: **TSU Exception (Technology and Software Unrestricted)**

No export license required because:
- Source code is publicly available
- Uses standard cryptographic libraries (FOSS exception)
- No specific encryption > 64-bit without public notification

---

## "Born Classified" Concerns

### What is "Born Classified"?

Under Atomic Energy Act and Executive Orders, certain information is
"classified at birth" - meaning it's automatically classified even if
independently derived.

**Born Classified Categories:**
1. Nuclear weapon designs (Atomic Energy Act)
2. Specific intelligence sources and methods
3. Certain cryptographic systems
4. Vulnerabilities in national security systems

### Why This Project is NOT "Born Classified"

**1. Not Nuclear:**
- No nuclear weapon data (not Restricted Data under AEA)

**2. Not Intelligence Methods:**
- TDOA geolocation is published openly (GPS, commercial)
- RF direction finding is civilian technology (fox hunting, aviation)

**3. Not Cryptographic Vulnerabilities:**
- No cryptanalysis of classified systems
- Uses commercial crypto libraries (AES, RSA)

**4. Not Specific Vulnerabilities:**
- Sidelobe detection is known weakness (published in journals)
- No new vulnerabilities discovered
- Theoretical analysis only (no actual system testing)

### Legal Precedent

Similar projects that remained unclassified:
- **GPS Civilian Service**: Initially classified, declassified for public use
- **Radar Cross Section (RCS) Simulation**: Available in academic software (FEKO, CST)
- **Link 16 Documentation**: Now publicly available (MIL-STD-6016)
- **Spread Spectrum**: Declassified in 1980s (Hedy Lamarr patent)

---

## Specific Parameter Justifications

### MADL Sidelobe Level: -30 dB (Estimate)

**Why This is Legal:**

```
Source Methodology:
1. Phased array textbook: "Sidelobes typically -13 dB without weighting"
2. Taylor weighting achieves: "-25 to -30 dB for moderate arrays"
3. Adaptive nulling adds: "+5 to +10 dB improvement"
4. Conclusion: -30 dB is midpoint of reasonable range

Legal Analysis:
✅ Based on published array theory (Mailloux, "Phased Array Handbook")
✅ No classified source accessed
✅ Wide uncertainty range (±10 dB) acknowledges guess
✅ Explicitly stated as "best estimate, not ground truth"

Classification Review:
- If actual value is -32 dB: Close guess, no harm (info still classified)
- If actual value is -28 dB: Close guess, no harm
- We did NOT disclose actual value (don't know it)
- Disclosure of an uncertainty range is not classification violation
```

**Precedent:**
- Declassified F-117 RCS: Estimates published before declassification were ±10 dB
- Those estimates did not violate classification laws
- Actual values remained classified despite public guesses

### F-35 RCS: 0.0001 m² (Estimate)

**Why This is Legal:**

```
Source Methodology:
1. Lockheed Martin: "Significantly stealthier than F-22"
2. F-22 RCS estimates: ~0.0001-0.0005 m² (published estimates)
3. Scaling logic: F-35 is smaller, newer → similar or better
4. Conclusion: 0.0001-0.0002 m² reasonable range

Legal Analysis:
✅ Based on contractor marketing claims (public)
✅ Comparison to F-22 estimates (widely published)
✅ No specific measurement data (don't have access)
✅ Uncertainty acknowledged (order of magnitude range)

Actual Value:
- Remains classified (we don't know exact value)
- Our estimate could be wrong by 5-10×
- Publishing an estimate does not declassify actual value
```

### PL-15 Range: 200 km / NEZ 100 km (Estimate)

**Why This is Legal:**

```
Source Methodology:
1. Chinese state media: "Over 200 km range"
2. Rocket equation: ΔV calculation from estimated propellant mass
3. Comparison to AIM-120D: Similar size/technology generation
4. Conclusion: 200 km max, 100 km NEZ plausible

Legal Analysis:
✅ Chinese claims are public (state media)
✅ Physics-based calculation (rocket equation)
✅ Comparison to declassified US missile (AIM-120D public range)
✅ We have no access to actual test data

US Classification:
- US intelligence assessment of PL-15 is likely classified
- We do NOT have that assessment
- Independent analysis from public sources is legal
```

---

## Automated Compliance Checks

This repository includes CI/CD checks to prevent classification violations:

### Pre-Commit Hooks

```bash
# .github/workflows/classification-check.yml

Checks:
1. No classification markings (CONFIDENTIAL, SECRET, TOP SECRET)
2. No ITAR/EAR violation keywords
3. No specific numerical values without uncertainty
4. All sources documented (bibliography check)
5. Disclaimer present in all technical documents
```

### Prohibited Content Patterns

```yaml
Regex Patterns (Auto-Rejected):
- "CONFIDENTIAL//.*"
- "SECRET//.*"
- "TOP SECRET//.*"
- "For Official Use Only"
- "ITAR-controlled"
- "Export controlled"
- "Actual measured value: [0-9]+"
- "During [Exercise|Operation] [A-Z]+"
```

### Required Disclaimers

All technical documents must include:

```
**Classification:** UNCLASSIFIED // PUBLIC RELEASE
**Sources:** [List of public sources]
**Confidence:** [Explicit uncertainty quantification]
```

---

## Responsible Disclosure

If classified information is accidentally included:

**Immediate Actions:**
1. Do NOT confirm or deny classification status
2. Contact: GitHub security team (security@github.com)
3. Contact: DoD Vulnerability Disclosure Program
4. Remove content immediately (force push)
5. Document incident (for legal protection)

**What NOT to Do:**
- ❌ Discuss on public forums whether info is classified
- ❌ Ask cleared individuals to review (could confirm classification)
- ❌ Attempt to verify accuracy (could constitute investigation)

---

## Educational Use Statement

**Purpose of This Project:**

This repository is created solely for **educational purposes** to demonstrate:
- Electronic warfare concepts
- Signal processing algorithms
- Geolocation mathematics
- System integration principles

**NOT Created For:**
- Actual weapon development
- Intelligence collection
- Operational use
- Providing advantage to foreign adversaries

**Legal Protection:**

Under 18 U.S.C. § 798 (Espionage Act), disclosure of classified information
requires:
1. Unauthorized possession of classified information (we have none)
2. Intent to harm the United States or benefit foreign nation (educational purpose)
3. Willful disclosure (we only publish unclassified analysis)

This project meets none of these criteria.

---

## User Agreement

By using this repository, you agree:

1. **You will NOT attempt to verify these estimates against actual classified systems**
   - No testing against F-35 MADL
   - No measurements of J-20 radar
   - No interception of military communications

2. **You will NOT share this with adversary nations for military purposes**
   - Educational sharing: OK
   - Research collaboration: OK
   - Providing to foreign military for operational use: ILLEGAL

3. **You will comply with export control laws**
   - US: ITAR, EAR compliance
   - EU: Dual-Use Regulation
   - Other jurisdictions: Local laws

4. **You acknowledge all estimates are unverified guesses**
   - Not ground truth
   - Not intelligence assessments
   - Not operational data

---

## Legal Review

**Attorney Consultation:** Recommended before operational use

**Classification Review:** Not required for public GitHub project using only
public sources, but available upon request from appropriate authority.

**Export License:** Not required under Public Domain Exception (22 CFR 120.11)

**Date of Last Review:** 2025-12-28

---

## Contact

**Questions about classification:**
- Do NOT send potentially classified information
- Email: [repository maintainer - public email only]
- Describe question in general terms only

**Report potential violation:**
- GitHub: security@github.com
- DoD: vdp@dc3.mil (Vulnerability Disclosure Program)

---

**DISTRIBUTION STATEMENT A:** Approved for public release; distribution is unlimited.

**Classification:** UNCLASSIFIED // PUBLIC RELEASE
**Date:** 2025-12-28
