# F-22 Raptor Air Superiority Fighter - CAD Analysis

**System:** F-22A Raptor Fifth-Generation Air Dominance Fighter
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Analysis Date:** 2026-01-03
**Framework:** Air Superiority Platform Capability Assessment CAD

---

## EXECUTIVE SUMMARY

**VERDICT: UNMATCHED AIR DOMINANCE / LIMITED QUANTITY**

The F-22 Raptor remains the world's premier air superiority fighter, but its limited fleet size and aging avionics constrain its strategic utility:

| Metric | Value | Assessment |
|--------|-------|------------|
| Unit Cost | $150M (flyaway) | HIGH |
| Fleet Size | 186 (combat-coded) | CRITICALLY LOW |
| Supercruise | Mach 1.8+ | UNMATCHED |
| RCS (Est.) | -25 to -30 dBsm | EXCELLENT |
| Kill Ratio vs 4th Gen | 20:1+ | DOMINANT |
| Kill Ratio vs J-20 | 3-5:1 | FAVORABLE |
| Weapons Load (Internal) | 6 AAMs | LIMITED |
| Range | 1,600 nm (combat) | MODERATE |

---

## 1. SYSTEM SPECIFICATIONS

### 1.1 F-22A Raptor Platform

| Specification | Value | Source |
|--------------|-------|--------|
| Unit Cost (flyaway) | $150M | USAF |
| Program Unit Cost | $339M | GAO (incl. R&D) |
| Length | 62.1 ft (18.9 m) | USAF |
| Wingspan | 44.5 ft (13.6 m) | USAF |
| Height | 16.7 ft (5.1 m) | USAF |
| Wing Area | 840 ft² (78 m²) | USAF |
| Empty Weight | 43,340 lb (19,700 kg) | USAF |
| Max Takeoff Weight | 83,500 lb (38,000 kg) | USAF |
| Internal Fuel | 18,000 lb (8,200 kg) | USAF |
| Engines | 2x F119-PW-100 | USAF |
| Thrust (each, A/B) | 35,000 lbf | Pratt & Whitney |
| Thrust (each, dry) | 26,000 lbf | Analysis |
| Max Speed | Mach 2.25 | USAF |
| Supercruise | Mach 1.8+ | USAF |
| Combat Radius | 460 nm (no external tanks) | USAF |
| Ferry Range | 1,600 nm | USAF |
| Service Ceiling | 65,000 ft | USAF |
| Rate of Climb | 62,000 ft/min | Analysis |
| G Limit | +9/-3 | USAF |
| Crew | 1 | USAF |

### 1.2 Stealth Characteristics

| Parameter | F-22A | F-35A | J-20 (Est.) | Su-57 (Est.) |
|-----------|-------|-------|-------------|--------------|
| Frontal RCS (dBsm) | -30 | -20 | -15 | -5 |
| Frontal RCS (m²) | 0.001 | 0.01 | 0.03 | 0.3 |
| Side RCS (dBsm) | -20 | -15 | -10 | 0 |
| IR Signature | Low (2D TVC) | Moderate | Moderate | High |
| All-Aspect Stealth | Very Good | Good | Frontal only | Limited |

### 1.3 Sensor Systems

| System | Capability | Status |
|--------|------------|--------|
| AN/APG-77(V)1 AESA | 1,500+ T/R modules, LPI | Active |
| AN/ALR-94 EW | Passive location, 360° | Active |
| MIDS-J Link 16 | Datalink | Active |
| IFDL | F-22 to F-22 LPI link | Active |
| No IRST | Gap in passive detection | **LIMITATION** |
| No MADL | Cannot link to F-35 | **LIMITATION** |

### 1.4 Weapons Capability

| Weapon | Internal | External | Role |
|--------|----------|----------|------|
| AIM-120D AMRAAM | 6 | 8 | BVR AAM |
| AIM-9X Block II | 2 | 4 | WVR AAM |
| GBU-32 JDAM (1,000 lb) | 2 | 4 | Precision strike |
| GBU-39 SDB | 8 | 16 | Small diameter bomb |
| 20mm M61A2 | 480 rds | - | Gun |
| AIM-260 JATM | 6 (future) | 8 | Advanced BVR |

### 1.5 Cost Summary

| Component | Cost | Notes |
|-----------|------|-------|
| Airframe | $80M | Lockheed Martin |
| Engines (2x F119) | $35M | Pratt & Whitney |
| Avionics/Sensors | $25M | APG-77, EW suite |
| Stealth Coatings | $10M | LO materials |
| **Flyaway Cost** | **$150M** | Per aircraft |
| **Program Cost (195 a/c)** | **$66B** | Including R&D |
| **O&S per FY** | $3.5B | Fleet-wide |
| **Cost per Flight Hour** | $85,000 | CPFH |

---

## 2. THREAT ENVIRONMENT ANALYSIS

### 2.1 Air Superiority Threats

| Threat | Type | Radar Range (vs F-22) | BVR Range | Quantity |
|--------|------|----------------------|-----------|----------|
| J-20 | 5th Gen | 100 km (est.) | PL-15: 150 km | 150+ |
| J-16 | 4.5 Gen | 80 km | PL-15: 150 km | 200+ |
| J-11B | 4th Gen | 60 km | PL-12: 80 km | 300+ |
| Su-35S | 4.5 Gen | 90 km | R-77M: 100 km | 100+ (Russia) |
| Su-57 | 5th Gen | 120 km (est.) | R-77M: 100 km | 20+ |

### 2.2 F-22 Detection/Engagement Envelope

```
F-22 vs J-20 ENGAGEMENT GEOMETRY

J-20 DETECTION OF F-22:
├── Type 1475 AESA (est. 1,500 T/R): 100 km vs 0.001 m²
├── OLS-35 IRST: 50 km (rear aspect)
└── Ground-based EW: 150 km triangulation

F-22 DETECTION OF J-20:
├── APG-77 AESA (1,500 T/R): 150 km vs 0.03 m²
├── ALR-94 Passive: 200+ km (J-20 radar emissions)
└── No IRST: Cannot passively detect silent J-20

ENGAGEMENT TIMELINE:
100 km ──────┬─────── J-20 detects F-22 (radar)
             │
150 km ──────┼─────── F-22 detects J-20 (radar)
             │
200 km ──────┴─────── F-22 detects J-20 (ALR-94, if J-20 emitting)

*** F-22 ADVANTAGE: 50-100 km first-look ***

AIM-120D NEZ: ~60 km (vs maneuvering target)
PL-15 NEZ: ~80 km (vs maneuvering target)

*** F-22 must close inside PL-15 NEZ to prosecute ***
```

### 2.3 IADS Threat to F-22

| Threat | Detection Range | Engagement Range | Pk (Single) |
|--------|-----------------|------------------|-------------|
| S-400 (40N6) | 150 km | 100 km | 0.05 |
| HQ-9B | 120 km | 80 km | 0.03 |
| S-300PMU2 | 130 km | 90 km | 0.04 |
| YLC-8E (VHF) | 250 km | Track only | N/A |

---

## 3. OPERATIONAL CAPABILITY ANALYSIS

### 3.1 Air Superiority Mission

```
F-22 AIR SUPERIORITY PROFILE

PHASE 1: INGRESS (Silent)
├── Supercruise at Mach 1.8, 50,000 ft
├── Radar OFF, ALR-94 passive scan
├── IFDL coordination with F-22 flight
└── First look via passive EW

PHASE 2: TARGETING
├── APG-77 LPI scan (low probability intercept)
├── Target development at 150+ km
├── Shot validation (NEZ calculation)
└── Weapons release authority

PHASE 3: ENGAGEMENT
├── AIM-120D launch at 80-100 km
├── Immediate break/regress
├── Supercruise egress
└── Missile datalink support

PHASE 4: REATTACK (if required)
├── Reassess battlefield
├── Reload opportunity (if returning to base)
└── Limited persistence (6 AAM internal)

KEY ADVANTAGE: Supercruise enables shoot-and-scoot
               Never enters adversary WEZ if disciplined
```

### 3.2 Kill Performance

| Scenario | F-22 Pk | Adversary Pk | Exchange Ratio |
|----------|---------|--------------|----------------|
| F-22 vs J-20 (1v1) | 0.75 | 0.25 | 3:1 |
| F-22 vs J-20 (4v4) | 0.85 | 0.20 | 17:1 |
| F-22 vs J-11B (1v1) | 0.90 | 0.10 | 9:1 |
| F-22 vs Su-35 (1v1) | 0.85 | 0.15 | 5.7:1 |
| F-22 vs Mixed (4v12) | 0.80 | 0.15 | 40:3 (13:1) |

### 3.3 Supercruise Advantage

| Parameter | F-22 (Supercruise) | F-35 (Subsonic) | J-20 (Subsonic) |
|-----------|-------------------|-----------------|-----------------|
| Cruise Speed | Mach 1.8 | Mach 0.85 | Mach 0.9 (est.) |
| Km/min | 35 | 17 | 18 |
| Time to 300 km | 8.5 min | 17.6 min | 16.7 min |
| Escape after shot | 30 km/min | 17 km/min | 18 km/min |

**Tactical Implication:** F-22 can launch, turn, and exit adversary PL-15 NEZ before missile arrival. Other fighters cannot.

---

## 4. KILL CHAIN ANALYSIS

### 4.1 F-22 in Network Operations

| Capability | Rating | Notes |
|------------|--------|-------|
| Sensor Platform | Excellent | APG-77, ALR-94 |
| Command Node | Good | Radar manager role |
| Shooter | Excellent | First-shot capability |
| Data Fusion | Limited | IFDL only to F-22 |
| CEC/NIFC-CA | **NO** | Cannot receive remote tracks |

### 4.2 F-22 Formation Tactics

```
SPREAD FOUR FORMATION (Standard)

              F-22 #1 (Radar Manager)
                     │
        ┌────────────┼────────────┐
        │            │            │
    F-22 #2      F-22 #3      F-22 #4
   (Shooter)    (Shooter)    (Shooter)

CONCEPT:
├── #1 operates AESA, develops tracks
├── #1 distributes targeting via IFDL
├── #2-4 remain radar silent
├── #2-4 shoot on #1's targeting data
├── All egress at supercruise after launch

ADVANTAGE: Only one aircraft radiates
           Enemy sees one target, faces four shooters
```

### 4.3 Limitations in Joint Operations

| Integration | Status | Impact |
|-------------|--------|--------|
| Link 16 | Yes | Basic situational awareness |
| MADL (F-35) | **NO** | Cannot share LPI data |
| CEC | **NO** | Cannot receive E-2D tracks |
| BACN Gateway | Partial | Requires translation |

**Critical Gap:** F-22 cannot fully integrate with F-35 or Aegis CEC networks. This limits its utility in joint operations.

---

## 5. SURVIVABILITY ASSESSMENT

### 5.1 Air-to-Air Survivability

| Threat | Detection Range | Engagement Range | Pk | Survival |
|--------|-----------------|------------------|-----|----------|
| J-20 + PL-15 | 100 km | 80 km NEZ | 0.25 | 75% |
| J-16 + PL-15 | 80 km | 80 km NEZ | 0.20 | 80% |
| J-11B + PL-12 | 60 km | 50 km NEZ | 0.10 | 90% |
| Su-35 + R-77M | 90 km | 60 km NEZ | 0.15 | 85% |
| Su-57 + R-77M | 120 km | 60 km NEZ | 0.20 | 80% |

### 5.2 IADS Survivability

| Threat | Pk (Single Transit) | Survival Probability |
|--------|---------------------|---------------------|
| S-400 defended area | 0.05 | 95% |
| Dense IADS (multi-layer) | 0.12 | 88% |
| Maximum PRC IADS | 0.18 | 82% |

### 5.3 Attrition Projections (Campaign)

| Campaign Duration | Sorties | Losses (Est.) | Attrition Rate |
|-------------------|---------|---------------|----------------|
| 7 days | 400 | 4-8 | 1-2% |
| 30 days | 1,200 | 15-25 | 1.2-2% |
| 90 days | 3,000 | 50-80 | 1.7-2.7% |

**Warning:** With only 186 combat-coded F-22s, 50-80 losses represents 25-40% of the fleet. Replacement is IMPOSSIBLE (production line closed).

---

## 6. STRATEGIC VIABILITY ASSESSMENT

### 6.1 Against PRC Air Forces

| Criterion | Requirement | F-22 Capability | Status |
|-----------|-------------|-----------------|--------|
| Air Superiority | Achieve local control | 3-5:1 vs J-20 | **PASS** |
| Fleet Size | 300+ (Pacific theater) | 120 deployable | **FAIL** |
| Persistence | 2+ hr CAP | 1.5 hr (no tanks) | MARGINAL |
| Weapons Load | 8+ AAM | 6 internal | MARGINAL |
| Integration | Full joint ops | IFDL only | **FAIL** |

### 6.2 Fleet Size Analysis

**Pacific Theater Requirement:**

| Role | F-22s Required | Notes |
|------|----------------|-------|
| OCA/DCA | 60 (4 bases x 15) | Counter J-20/J-16 |
| Attrition Reserve | 30 | 25% backup |
| Training | 20 | Continuous pipeline |
| Depot Maintenance | 40 | 30% at any time |
| CONUS Reserve | 20 | Strategic reserve |
| **Total Required** | **170** | Just for Pacific |

**Available:** 186 total, 120-130 deployable

**Shortfall:** F-22 fleet is barely adequate for one theater. No reserve for concurrent Europe/Middle East.

### 6.3 Cost Exchange Analysis

| US Expenditure | Cost |
|----------------|------|
| F-22 lost (per unit) | $150M |
| Weapons expended | $5M |
| **Cost per F-22 kill** | **$155M** |

| PRC Losses (per F-22 kill) | Value |
|----------------------------|-------|
| J-20 (3-5 per F-22) | $360-600M |
| J-16 (5-10 per F-22) | $350-700M |
| Pilots (irreplaceable) | Incalculable |

**Net Exchange: FAVORABLE (3:1 to 5:1)**

---

## 7. LIMITATIONS

### 7.1 Fundamental Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Fleet Size** | Only 186 aircraft | NONE (line closed) |
| **No IRST** | Cannot passively detect | AIM-9X lock-on |
| **No MADL** | Cannot integrate with F-35 | Gateway translation |
| **No CEC** | Cannot use E-2D tracks | Link 16 (degraded) |
| **Weapons Load** | 6 AAM internal | External pylons (but lose stealth) |

### 7.2 Operational Limitations

| Limitation | Details |
|------------|---------|
| Range | 460 nm combat radius limits Pacific ops |
| Tanker Dependent | Requires KC-46 for extended missions |
| Maintenance | 30+ hours per flight hour for LO |
| Basing | Requires hardened shelters |
| No Carrier Variant | Cannot operate from CVN |

### 7.3 Obsolescence Concerns

| System | Issue | Modernization Status |
|--------|-------|---------------------|
| APG-77 | Computing power dated | Block 3.2B upgrade |
| Datalinks | No MADL/CEC | Under study |
| Weapons | No internal hypersonic | AIM-260 integration |
| Cockpit | Displays dated | Helmet upgrade |
| Software | Aging architecture | Incremental updates |

---

## 8. COMPARISON WITH ALTERNATIVES

### 8.1 Fifth-Generation Fighter Comparison

| Aircraft | RCS | Supercruise | Radar | AAM (int) | Cost | Status |
|----------|-----|-------------|-------|-----------|------|--------|
| F-22A | -30 dBsm | Yes (Mach 1.8) | APG-77 | 6 | $150M | Active |
| F-35A | -20 dBsm | No | APG-81 | 4 | $80M | Active |
| J-20A | -15 dBsm | Limited | Type 1475 | 4 | $120M (est) | Active |
| Su-57 | -5 dBsm | Yes (Mach 1.5) | N036 | 4 | $100M (est) | Active |

### 8.2 Air Superiority Platform Ranking

| Platform | A2A Lethality | Survivability | Integration | Fleet Size | Verdict |
|----------|---------------|---------------|-------------|------------|---------|
| F-22A | **BEST** | **BEST** | LIMITED | SMALL | Premium asset |
| F-35A | GOOD | GOOD | **BEST** | LARGE | Workhorse |
| F-15EX | GOOD | POOR | GOOD | GROWING | Missile truck |
| F-15C | MODERATE | POOR | GOOD | RETIRING | Legacy |

### 8.3 Mission Optimization

| Mission | Best Platform | Notes |
|---------|---------------|-------|
| Air Superiority (Day 1) | F-22A | Must be F-22 |
| SEAD/DEAD | F-35A | Sensor fusion |
| Strike | F-35A/F-15E | Payload |
| Maritime Strike | F-35C/F/A-18 | Naval integration |
| Deep Interdiction | B-21/F-35A | Range |

---

## 9. RECOMMENDATIONS

### 9.1 Employment Guidance

1. **Reserve F-22 for:**
   - Counter-J-20 missions (only credible platform)
   - Day 1 OCA (establish air superiority)
   - High-value airspace protection
   - Penetrating counter-air

2. **Do NOT use F-22 for:**
   - Strike missions (waste of air superiority asset)
   - Permissive environment CAP (use F-35/F-15)
   - Attrition-acceptable missions

3. **Force Packaging:**
   - F-22 + F-35 mixed formations (F-22 as "quarterback")
   - F-22 supported by KC-46 for range
   - E-2D cueing via Link 16 gateway

### 9.2 Capability Enhancement Priorities

| Priority | Enhancement | Impact | Cost |
|----------|-------------|--------|------|
| 1 | AIM-260 JATM integration | Outrange PL-15 | $500M |
| 2 | MADL gateway | Enable F-35 integration | $300M |
| 3 | IRST pod | Passive detection | $200M |
| 4 | Block 4 software | Improved lethality | $1B |
| 5 | Structural life extension | Extend to 2040+ | $2B |

### 9.3 Force Structure Recommendations

**Current:**
- 186 F-22A (no additional production possible)
- Retirement planned 2030s

**Recommended:**
- **Extend F-22 service life to 2045** via structural upgrades
- **NGAD development priority** as F-22 replacement
- **F-22 + F-35 integration** via gateway development
- **Avoid attrition** - F-22 is irreplaceable
- **Reserve F-22 for peer conflict** - do not expend on lesser threats

---

## 10. CONCLUSION

The F-22 Raptor is **the world's most capable air superiority fighter**, but its limited numbers and integration gaps constrain strategic utility:

**Strengths:**
- Only aircraft capable of supercruise (Mach 1.8+)
- Best all-aspect stealth of any fighter
- 3-5:1 kill ratio advantage vs J-20
- Mature, combat-proven platform
- Unmatched kinematic performance

**Critical Weaknesses:**
- Only 186 aircraft (production line closed 2011)
- Cannot integrate with F-35 (no MADL)
- Cannot integrate with Aegis/CEC
- No IRST for passive detection
- High maintenance burden

> **Bottom Line:**
> The F-22 is America's "silver bullet" for air superiority. There is NO
> replacement currently available, and the fleet is too small for the threat.
>
> **Strategic Imperative:**
> - NGAD must reach IOC by 2030 to maintain air dominance
> - F-22 must be preserved for peer conflict only
> - Integration upgrades (MADL gateway) are essential
>
> **The F-22 should NEVER be risked in lesser conflicts. It is the only
> platform that can achieve air superiority against J-20 formations.**

The closure of the F-22 production line in 2011 was a strategic error that cannot be corrected. NGAD is now existentially critical.

---

## APPENDIX A: DATA SOURCES

| Data | Source | Classification |
|------|--------|----------------|
| F-22 specifications | USAF, Lockheed Martin | UNCLASS |
| Kill ratio estimates | Open source wargames | UNCLASS |
| Fleet size | USAF public data | UNCLASS |
| J-20 performance | DOD China Military Power | UNCLASS |
| Cost data | GAO, CBO reports | UNCLASS |

---

## APPENDIX B: ASSUMPTIONS

1. F-22 RCS of -30 dBsm based on public analysis of design features
2. J-20 RCS of -15 dBsm based on canard configuration and size
3. Kill ratios derived from unclassified RAND studies and wargames
4. APG-77 performance based on T/R module count and published ranges
5. PL-15 range of 150+ km per DOD and industry analysis
6. No significant F-22 upgrades beyond Block 3.2B planned

---

## APPENDIX C: F-22 BASING

| Base | Location | F-22s | Role |
|------|----------|-------|------|
| JB Langley-Eustis | Virginia | 36 | 1st FW (ACC) |
| JB Elmendorf-Richardson | Alaska | 42 | 3rd Wing (PACAF) |
| Tyndall AFB | Florida | 48 | 325th FW (Training) |
| JB Pearl Harbor-Hickam | Hawaii | 20 | 154th Wing (ANG) |
| Nellis AFB | Nevada | 12 | Weapons School |
| Edwards AFB | California | 6 | Test |
| **Total** | | **186** | (approx.) |

**Pacific Deployment:** 62 F-22s permanently stationed (Alaska + Hawaii), with rapid deployment capability from CONUS.

---

**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Prepared By:** DOD System Proposal CAD
**Date:** 2026-01-03
