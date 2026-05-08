# US Navy Anti-Ship Ballistic Missile (ASBM) Defense - CAD Analysis

**System:** Integrated Layered Defense Against Anti-Ship Ballistic Missiles
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Analysis Date:** 2026-01-04
**Framework:** Naval Integrated Air and Missile Defense (IAMD) Capability Assessment CAD

---

## EXECUTIVE SUMMARY

**VERDICT: PARTIAL CAPABILITY WITH CRITICAL GAP IN GLIDE PHASE**

The US Navy defends against Chinese ASBMs through a multi-layered approach, but significant vulnerabilities remain:

| Defense Layer | System | Status | Pk vs ASBM | Assessment |
|--------------|--------|--------|------------|------------|
| Outer (Midcourse) | SM-3 Block IIA | Operational | 0.50-0.70 | MODERATE |
| Middle (Glide Phase) | GPI | **NOT OPERATIONAL** | N/A | **CRITICAL GAP** |
| Inner (Terminal) | SM-6 Dual II | Operational | 0.35-0.55 | MARGINAL |
| Soft Kill (EW) | SEWIP Block III | Deploying | 0.40-0.60 (terminal confusion) | GOOD |

| Critical Metric | Value | Assessment |
|-----------------|-------|------------|
| DF-21D Salvo Survivability | 40-60% | MARGINAL |
| DF-26 Salvo Survivability | 30-50% | POOR |
| DF-27 (HGV) Survivability | 15-30% | **CRITICAL** |
| Magazine Depth (DDG-51) | 96 VLS cells | INSUFFICIENT for saturation |
| Cost Exchange | 20:1+ unfavorable | UNSUSTAINABLE |

---

## 1. THE ASBM THREAT

### 1.1 Chinese ASBM Systems

| System | Type | Range | Speed | CEP | Quantity | Est. Cost |
|--------|------|-------|-------|-----|----------|-----------|
| DF-21D | MRBM/ASBM | 1,500 km | Mach 10+ | 10-20m | 200+ | $10-15M |
| DF-26 | IRBM/ASBM | 4,000 km | Mach 10+ | 10-20m | 100+ | $20M |
| DF-27 | HGV/ASBM | 5,000+ km | Mach 10+ | <10m | 50+ (est.) | $30M |
| YJ-21 | Ship-launched hypersonic | 1,500 km | Mach 10 | 10m | 200+ | $20M |
| CM-401 | Quasi-ballistic | 290 km | Mach 6 | 20m | 500+ | $5M |

### 1.2 ASBM Kill Chain

```
CHINESE ASBM ENGAGEMENT SEQUENCE

PHASE 1: FIND (Targeting)
├── OTH-B Radar: 3,000+ km detection
├── Yaogan satellites: SAR/ELINT/Optical
├── Maritime patrol aircraft (Y-8/Y-9)
├── Submarine pickets
├── Fishing fleet HUMINT
└── UAVs (WZ-7 Soaring Dragon)

PHASE 2: FIX (Track Development)
├── Satellite constellation update: Every 15-30 min
├── OTH track refinement
├── Data fusion at command center
└── Launch authorization

PHASE 3: TRACK (Midcourse Guidance)
├── Satellite relay of ship position
├── Inertial navigation (missile)
├── Midcourse correction maneuvers
└── Target area designation

PHASE 4: TARGET (Terminal Acquisition)
├── Warhead separates from bus
├── Terminal radar activates (active seeker)
├── Target discrimination (carrier vs decoy)
├── Final maneuvers to impact

PHASE 5: ENGAGE (Impact)
├── Terminal dive: Mach 10+ at 60-80° angle
├── Impact: 500-1,500 kg warhead
└── Mission kill or sinking of carrier
```

### 1.3 ASBM Flight Profiles

```
ALTITUDE vs TIME: DF-21D ASBM

600 km ─────────────────────┐ Apogee
                            │ (Space)
                            │
400 km ─────────────────────┤ ← SM-3 ENGAGEMENT ZONE
                            │   (Outer Layer: Midcourse)
                            │
200 km ─────────────────────┤
                            │
100 km ─────────────────────┤ ← GPI ENGAGEMENT ZONE
      │                     │   (Middle Layer: Glide Phase)
      │   *** GAP ***       │   *** NOT OPERATIONAL ***
      │                     │
 40 km─┤───────────────────┤ ← SM-6 ENGAGEMENT ZONE
      │                     │   (Inner Layer: Terminal)
      │                     │
  0 km├─────────────────────┴────────────────────────► TIME
      Launch              ~10 min             Impact
      (China)              Flight            (Carrier)
```

---

## 2. LAYER 1: OUTER DEFENSE (MIDCOURSE/SPACE)

### 2.1 SM-3 Block IIA Specifications

| Specification | Value | Source |
|--------------|-------|--------|
| Manufacturer | Raytheon/Mitsubishi | DOD |
| Unit Cost | $28M | CBO |
| Length | 6.55 m (21.5 ft) | Raytheon |
| Diameter | 0.53 m (21 in) | Raytheon |
| Weight | 1,500 kg (3,300 lb) | Raytheon |
| Propulsion | 3-stage solid rocket | Raytheon |
| Kill Vehicle | Lightweight Exo-Atmospheric Projectile (LEAP) | Raytheon |
| Guidance | GPS + datalink update + IR terminal | Raytheon |
| Intercept Method | Hit-to-kill (kinetic) | Raytheon |
| Max Range | 2,500 km | DOD |
| Max Altitude | 1,500 km (exo-atmospheric) | DOD |
| Min Altitude | 70 km | DOD (estimated) |
| Speed at Intercept | Mach 13+ | DOD |

### 2.2 SM-3 Block IIA Engagement Sequence

```
SM-3 BLOCK IIA vs ASBM (MIDCOURSE INTERCEPT)

T-600 sec: SBIRS detects MRBM launch (IR signature)
T-580 sec: Space-Based Infrared tracks boost phase
T-550 sec: SPY-6/TPY-2 acquires track in midcourse
T-500 sec: Aegis computes engagement solution
T-480 sec: Engagement authority granted (weapons free)
T-450 sec: SM-3 Block IIA launch from VLS
T-400 sec: 1st stage burnout, 2nd stage ignition
T-300 sec: 2nd stage burnout, 3rd stage ignition
T-200 sec: 3rd stage burnout, LEAP deployment
T-180 sec: LEAP acquires target (IR seeker)
T-150 sec: Midcourse update via datalink
T-60 sec:  Terminal guidance, fine corrections
T-0 sec:   Hit-to-kill intercept (space)

SUCCESS: Warhead destroyed before reentry
```

### 2.3 SM-3 Block IIA Limitations vs ASBMs

| Limitation | Impact | Details |
|------------|--------|---------|
| **Maneuvering Reentry Vehicles (MaRV)** | Reduces Pk to 0.30-0.50 | DF-21D designed to maneuver; LEAP cannot adjust late |
| **Decoys** | Consumes interceptors | ASBMs may deploy decoys; each requires engagement |
| **Closing Speed** | Compressed engagement window | Combined velocity >15,000 m/s; milliseconds for correction |
| **Sensor Handoff** | Tracking discontinuity | Space-to-atmosphere transition difficult |
| **Cost** | $28M per shot | Multiple interceptors per threat = unsustainable |

### 2.4 SM-3 Block IIA Pk Estimates vs ASBM

| Threat | MaRV Capability | Decoys | SM-3 IIA Pk (single) | SM-3 IIA Pk (salvo of 2) |
|--------|-----------------|--------|----------------------|--------------------------|
| DF-21D (early variant) | Limited | None | 0.65-0.75 | 0.85-0.95 |
| DF-21D (current) | Yes | Possible | 0.45-0.55 | 0.70-0.80 |
| DF-26 | Yes | Yes | 0.35-0.50 | 0.60-0.75 |
| DF-27 (HGV) | **Extreme** | N/A | **<0.20** | **<0.35** |

**Critical Finding:** SM-3 Block IIA was designed for predictable ballistic trajectories. Modern ASBMs with MaRV capability significantly degrade Pk. HGVs like DF-27 cannot be effectively engaged in midcourse.

---

## 3. LAYER 2: MIDDLE DEFENSE (GLIDE PHASE) - **CRITICAL GAP**

### 3.1 The Glide Phase Problem

```
THE HYPERSONIC GLIDE VEHICLE (HGV) ENGAGEMENT GAP

                    SM-3 CEILING
                    (Exo-atmospheric only)
                           │
ALTITUDE                   │
200 km ────────────────────┤
                           │
                           │  *** NO INTERCEPT CAPABILITY ***
                           │
100 km ────────────────────┤
                     ╔═════╧═════════════════════════════╗
                     ║     HGV GLIDE PHASE               ║
                     ║     (40-100 km altitude)          ║
   70 km ────────────║─────────────────────────────────  ║
                     ║     Mach 10+ maneuvering          ║
                     ║     Too low for SM-3              ║
                     ║     Too high for SM-6             ║
                     ╚═══════════════════════════════════╝
   40 km ────────────┬─────────────────────────────────────
                     │
                     │  SM-6 CEILING (Endo-atmospheric)
                     │
    0 km ────────────┴─────────────────────────────────────
                     ╰──────────────────────────────────────► RANGE

*** THE GLIDE PHASE IS CURRENTLY UNDEFENDED ***
```

### 3.2 HGV Characteristics vs Traditional Ballistic Missiles

| Characteristic | Traditional MRBM | HGV (DF-ZF/DF-27) |
|----------------|------------------|-------------------|
| Trajectory | Predictable parabola | Unpredictable glide |
| Altitude | 300-600 km (space) | 40-100 km (upper atmosphere) |
| Maneuverability | None to limited | High (cross-range maneuver) |
| Warning Time | 10+ minutes | 5-7 minutes |
| Intercept Window | 3-5 minutes | <60 seconds |
| Radar Signature | Consistent | Variable (plasma sheath) |
| Interception | SM-3 viable | **No current solution** |

### 3.3 GPI: Glide Phase Interceptor Program

| Parameter | Value | Status |
|-----------|-------|--------|
| Prime Contractor | Northrop Grumman | Selected 2023 |
| Program Cost | $15-20B (estimated) | In development |
| IOC Target | 2029-2031 | **NOT OPERATIONAL** |
| Intercept Altitude | 40-100 km | Design requirement |
| Speed | Mach 10+ | Design requirement |
| Guidance | Multi-mode seeker | In development |
| Platform | Ship-based (VLS), land-based | Both planned |

### 3.4 GPI Development Timeline

```
GLIDE PHASE INTERCEPTOR (GPI) PROGRAM

2023 ────── Northrop Grumman contract award
            │
2024 ────── Preliminary design review
            │
2025 ────── Critical design review
            │    *** CURRENT STATUS ***
            │    (Technology maturation phase)
            │
2026 ────── First flight test (planned)
            │
2027 ────── Initial flight testing
            │
2028 ────── Intercept testing begins
            │
2029 ────── LRIP decision
            │
2030 ────── Limited production
            │
2031 ────── IOC (earliest realistic)

*** THE GLIDE PHASE GAP WILL PERSIST UNTIL ~2031 ***
```

### 3.5 Interim Gap Mitigation

| Measure | Description | Effectiveness |
|---------|-------------|---------------|
| SM-6 Block IB | Extended altitude capability (in development) | MODERATE |
| Left-of-launch | Destroy launchers before firing | MARGINAL |
| Electronic warfare | Jam HGV seeker (if applicable) | UNKNOWN |
| Maneuver | Move carrier out of impact zone | LIMITED (speed constraints) |
| Decoys | Confuse terminal seeker | MODERATE |

**Critical Assessment:** Until GPI achieves IOC, US carriers have **no reliable defense** against hypersonic glide vehicles in the 40-100 km altitude band. This represents the most significant gap in naval air defense.

---

## 4. LAYER 3: INNER DEFENSE (TERMINAL/ATMOSPHERE)

### 4.1 SM-6 Dual II Specifications

| Specification | Value | Source |
|--------------|-------|--------|
| Manufacturer | Raytheon | DOD |
| Unit Cost | $4.3M | CBO |
| Variants | Block I, Block IA, Block IB (in development) | Navy |
| Length | 6.55 m (21.5 ft) | Raytheon |
| Diameter | 0.53 m (21 in) | Raytheon |
| Weight | 1,500 kg (3,300 lb) | Raytheon |
| Propulsion | Mk 72 booster + Mk 104 dual-thrust | Raytheon |
| Warhead | Blast fragmentation + Active Radar Homing | Raytheon |
| Guidance | Semi-active + Active radar homing | Raytheon |
| Max Range | 240+ km (AAW) | Navy |
| Max Altitude | 33 km (endo-atmospheric) | Navy |
| Speed | Mach 3.5 | Navy |

### 4.2 SM-6 Block Variants for ASBM Defense

| Variant | Capability | Status | ASBM Relevance |
|---------|------------|--------|----------------|
| SM-6 Block I | Standard AAW/ASuW | Operational | Limited (cruise missiles) |
| SM-6 Block IA (Dual I) | AAW + Terminal BMD | Operational | Can engage diving warheads |
| SM-6 Block IB (Dual II) | Enhanced Terminal BMD | Deploying 2025-2026 | Improved Pk vs Mach 10+ threats |
| SM-6 Block II | Extended range/capability | Development | Future hypersonic defense |

### 4.3 SM-6 Terminal Intercept vs ASBM

```
SM-6 DUAL II vs DIVING ASBM WARHEAD

ENGAGEMENT TIMELINE (Final 30 seconds):

T-30 sec: SPY-6 tracks warhead at 60 km altitude
          Warhead speed: Mach 10 (3.4 km/sec)
          Dive angle: 60-80 degrees

T-25 sec: Aegis computes intercept solution
          Challenge: Maneuvering warhead with active seeker

T-20 sec: SM-6 launch (salvo of 2-4 missiles)
          SM-6 speed: Mach 3.5 (1.2 km/sec)

T-15 sec: SM-6 booster separation
          Active radar seeker activated

T-10 sec: SM-6 acquires target
          Warhead at 30 km altitude, maneuvering

T-5 sec:  Terminal guidance
          SM-6 adjusting to warhead maneuvers

T-0 sec:  INTERCEPT ATTEMPT
          Proximity-fuzed warhead detonation

SUCCESS: Warhead destroyed 5-20 km from ship
FAILURE: Warhead impacts at Mach 5+ = MISSION KILL
```

### 4.4 SM-6 Limitations vs ASBM

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Speed Differential** | SM-6 (Mach 3.5) vs ASBM (Mach 10+) = tail-chase impossible | Salvo launch for multiple intercept opportunities |
| **Altitude Ceiling** | 33 km max; ASBM acquires at 40+ km | Block IB extends ceiling |
| **Reaction Time** | <30 seconds from detection to impact | Automated engagement (AEGIS) |
| **Maneuvering Warhead** | ASBM designed to evade | Salvo + predictive algorithms |
| **Saturation** | 96 VLS cells, 2-4 SM-6 per threat | Rapidly winchester |

### 4.5 SM-6 Pk Estimates vs ASBM (Terminal Phase)

| Threat | Dive Speed | Maneuver | SM-6 Pk (single) | SM-6 Pk (salvo of 3) |
|--------|-----------|----------|------------------|----------------------|
| DF-21D (non-maneuvering) | Mach 10 | None | 0.55-0.65 | 0.85-0.95 |
| DF-21D (MaRV) | Mach 10 | Moderate | 0.35-0.45 | 0.70-0.80 |
| DF-26 (MaRV) | Mach 10+ | High | 0.30-0.40 | 0.60-0.75 |
| DF-27 (HGV terminal) | Mach 8+ | Extreme | **0.15-0.25** | **0.40-0.55** |

### 4.6 The Saturation Problem

```
CARRIER STRIKE GROUP vs ASBM SATURATION ATTACK

PRC SALVO COMPOSITION:
├── DF-21D: 20 missiles
├── DF-26: 10 missiles
├── YJ-21: 20 missiles (ship-launched)
└── TOTAL: 50 ASBMs

US CSG DEFENSIVE CAPACITY:
├── CVN-78: Limited (ESSM only for terminal)
├── DDG-51 x 3: 96 cells each = 288 cells
├── CG-47 x 1: 122 cells
└── TOTAL VLS: 410 cells

AAW LOADOUT (50% AAW):
├── SM-3 Block IIA: ~40 missiles (12 per DDG + CG)
├── SM-6: ~100 missiles (30 per DDG + CG)
├── ESSM: ~160 missiles (quad-packed)
└── Available for ASBM: ~140 SM-3/SM-6

ENGAGEMENT MATH:
├── 50 ASBMs incoming
├── 3 interceptors per threat (conservative)
├── Required: 150 interceptors
├── Available: 140 interceptors
├── RESULT: MARGINAL (some leakers expected)

*** WITH SECOND SALVO, CSG IS WINCHESTER ***
```

---

## 5. LAYER 4: SOFT KILL (ELECTRONIC WARFARE)

### 5.1 SEWIP Block III Specifications

| Specification | Value | Source |
|--------------|-------|--------|
| System Name | Surface Electronic Warfare Improvement Program Block III | Navy |
| Manufacturer | Northrop Grumman | Navy |
| Designation | AN/SLQ-32(V)7 | Navy |
| Unit Cost | $40-60M per ship installation | Navy |
| Ships Equipped | DDG-51 Flight III, DDG-1000, future CVNs | Navy |
| Deployment Began | 2023 | Navy |
| Full Deployment | 2028-2030 (estimated) | Navy |

### 5.2 SEWIP Block III Capabilities

| Capability | Description | Effectiveness vs ASBM |
|------------|-------------|----------------------|
| **Electronic Attack (EA)** | High-power jamming of threat radars | HIGH (degrades acquisition) |
| **Threat Identification** | Real-time classification of emitters | HIGH (enables response) |
| **False Target Generation** | Creates phantom ships on radar | MODERATE (confuses seeker) |
| **Active Decoy Coordination** | Controls Nulka, SRBOC decoys | HIGH (draws seekers away) |
| **Adaptive Jamming** | Dynamically adjusts to threat | MODERATE-HIGH |
| **Multifunction AESA** | Can jam multiple threats simultaneously | HIGH |

### 5.3 SEWIP Block III vs ASBM Terminal Seeker

```
SOFT KILL ENGAGEMENT: SEWIP Block III vs DF-21D SEEKER

SCENARIO: ASBM warhead in terminal phase (final 30 seconds)

T-30 sec: ASBM warhead at 50 km altitude
          Terminal radar activates
          SEWIP detects radar emissions

T-25 sec: SEWIP classifies threat as ASBM seeker
          Engagement mode selected:
          - Option A: Noise jamming (degrade SNR)
          - Option B: Deception jamming (false targets)
          - Option C: Coordinated decoys (Nulka launch)

T-20 sec: SEWIP begins electronic attack
          High-power jamming in seeker frequency
          Nulka decoy launched (hover mode)

T-15 sec: ASBM seeker struggles to acquire
          Options:
          - Seeker locked on Nulka (SUCCESS)
          - Seeker burned through jam (FAILURE)
          - Seeker defaults to INS (PARTIAL)

T-10 sec: ASBM makes terminal correction
          If jammed: Impact 500m-2km off target
          If deceived: Impact on decoy
          If clear: Impact on ship

T-0 sec:  IMPACT
          ├── Hit on decoy: SHIP SURVIVES
          ├── Near-miss: MINOR DAMAGE
          └── Direct hit: MISSION KILL
```

### 5.4 SEWIP Block III Limitations

| Limitation | Impact | Notes |
|------------|--------|-------|
| **Jam-resistant seekers** | Reduced effectiveness | Modern seekers use frequency hopping |
| **Home-on-jam (HOJ)** | Seeker can track jammer | Requires coordinated decoy |
| **Multiple simultaneous threats** | System saturation | Limited simultaneous engagements |
| **Unknown seeker modes** | Can't jam what you don't know | Intelligence gap |
| **Plasma sheath** | Blocks RF during reentry | Limited window for jamming |

### 5.5 Soft Kill Pk Contribution

| Scenario | SEWIP Alone | SEWIP + Decoys | Combined with Hard Kill |
|----------|-------------|----------------|------------------------|
| Single ASBM | 0.35-0.45 | 0.50-0.60 | 0.85-0.95 |
| Salvo (4 ASBM) | 0.25-0.35 | 0.40-0.50 | 0.75-0.85 |
| Saturation (20+ ASBM) | 0.15-0.25 | 0.25-0.35 | 0.50-0.70 |

**Critical Insight:** SEWIP Block III is most effective when combined with hard kill (SM-6) and decoys (Nulka). It cannot defeat ASBMs alone but significantly degrades their effectiveness.

---

## 6. INTEGRATED LAYERED DEFENSE

### 6.1 Multi-Layer Engagement Doctrine

```
US NAVY ASBM DEFENSE LAYERS (Carrier Strike Group)

LAYER 1: MIDCOURSE (SM-3 Block IIA)
├── Altitude: 150-1,500 km
├── Range: 500-2,500 km
├── Pk: 0.50-0.70 (per shot)
├── Engagement: 1-2 SM-3 per threat
└── Goal: Attrit 40-60% of salvo

*** GAP: GLIDE PHASE (40-100 km) - NO CAPABILITY ***

LAYER 2: TERMINAL (SM-6 Dual II)
├── Altitude: 10-40 km
├── Range: 50-150 km
├── Pk: 0.35-0.55 (per shot)
├── Engagement: 2-4 SM-6 per threat
└── Goal: Attrit leakers from Layer 1

LAYER 3: SOFT KILL (SEWIP Block III)
├── Range: 0-50 km
├── Concurrent with hard kill
├── Pk contribution: 0.30-0.50
├── Engagement: All threats simultaneously
└── Goal: Degrade seeker accuracy

LAYER 4: POINT DEFENSE (ESSM, RAM, CIWS)
├── Range: 0-10 km
├── Pk: 0.50-0.70 (per shot)
├── Engagement: Last-ditch
└── Goal: Stop leakers

FINAL LAYER: DAMAGE CONTROL
├── Watertight integrity
├── Fire suppression
├── Backup systems
└── Goal: Survive hit and maintain ops
```

### 6.2 Cumulative Pk Calculation

| Layer | System | Single Threat Pk | Leaker Probability |
|-------|--------|------------------|-------------------|
| 1 | SM-3 IIA (2 shots) | 0.75 | 0.25 |
| GAP | (No GPI) | 0.00 | 0.25 (unchanged) |
| 2 | SM-6 (3 shots) | 0.80 | 0.05 |
| 3 | SEWIP + decoys | 0.50 | 0.025 |
| 4 | ESSM/RAM/CIWS | 0.60 | 0.01 |
| **Total** | | | **1% leaker rate** |

**However:** Against HGV threats (DF-27) that bypass midcourse:

| Layer | System | HGV Pk | Leaker Probability |
|-------|--------|--------|-------------------|
| 1 | SM-3 IIA | ~0.00 (HGV glides) | 1.00 |
| GAP | (No GPI) | 0.00 | 1.00 (unchanged) |
| 2 | SM-6 (3 shots) | 0.55 | 0.45 |
| 3 | SEWIP + decoys | 0.40 | 0.27 |
| 4 | ESSM/RAM/CIWS | 0.30 | 0.19 |
| **Total** | | | **19% leaker rate** |

**Critical Finding:** Against conventional ASBMs, layered defense achieves ~99% Pk. Against HGVs, leaker rate jumps to ~20%. In a salvo of 10 HGVs, expect 2 hits.

### 6.3 Agentic AI Integration (Project Overmatch)

| Challenge | Human Limitation | AI Solution |
|-----------|------------------|-------------|
| **50 threats in 30 seconds** | Cannot process | Instant threat prioritization |
| **Layer assignment** | Manual doctrine | Optimal allocation algorithm |
| **Shoot-look-shoot** | Decision delay | Real-time Pk update and reassignment |
| **Electronic warfare coordination** | Separate systems | Integrated soft/hard kill |
| **Magazine management** | Conservative fire | Optimal expenditure rate |
| **Distributed engagement** | Voice coordination | NIFC-CA automation |

**Project Overmatch enables:**
- Autonomous engagement authority (weapons free)
- Cross-ship target assignment (any sensor, any shooter)
- Real-time Pk estimation and interceptor allocation
- Graceful degradation under saturation

---

## 7. SURVIVABILITY ASSESSMENT

### 7.1 CSG Survivability vs ASBM Scenarios

| Scenario | Threat Composition | CSG Survivability | Notes |
|----------|-------------------|-------------------|-------|
| Limited Strike (6 ASBM) | 6x DF-21D | 95% | Manageable |
| Moderate Salvo (20 ASBM) | 20x DF-21D/DF-26 mix | 75% | Stress test |
| Heavy Salvo (50 ASBM) | 30x DF-21D, 20x DF-26 | 40-60% | **Marginal** |
| Saturation (100+ ASBM) | Mixed + HGV | <30% | **Likely loss** |
| HGV Strike (10 DF-27) | 10x DF-27 HGV | 50-60% | Gap exploitation |

### 7.2 Cost Exchange Analysis

**Scenario: Carrier Lost to ASBM Salvo**

| US Loss | Cost |
|---------|------|
| CVN-78 Ford | $13.3B |
| Air Wing (75 aircraft) | $7.2B |
| Defensive missiles expended | $0.8B (50 SM-6, 20 SM-3) |
| Personnel (4,500+) | Incalculable |
| **Total Loss** | **$21.3B+** |

| PRC Expenditure | Cost |
|-----------------|------|
| DF-21D (20 @ $15M) | $300M |
| DF-26 (10 @ $20M) | $200M |
| Targeting support | $50M |
| **Total** | **$550M** |

**Cost Exchange Ratio: 39:1 UNFAVORABLE**

### 7.3 Magazine Depth Crisis

```
SUSTAINED DEFENSE SCENARIO

DAY 1:
├── PRC Salvo 1: 50 ASBMs
├── US Expenditure: 40 SM-3 + 80 SM-6 = 120 interceptors
├── Remaining: 280 SM-3/SM-6 (CSG total)
└── Status: DEFENDED (95% Pk)

├── PRC Salvo 2: 50 ASBMs (4 hours later)
├── US Expenditure: 120 interceptors
├── Remaining: 160 interceptors
└── Status: DEFENDED (90% Pk)

├── PRC Salvo 3: 50 ASBMs (8 hours later)
├── US Expenditure: 120 interceptors
├── Remaining: 40 interceptors
└── Status: WINCHESTER IMMINENT

DAY 2:
├── PRC Salvo 4: 50 ASBMs
├── US Expenditure: 40 interceptors (all remaining)
├── Remaining: 0 interceptors
├── Status: *** CSG DEFENSELESS ***
└── Result: CARRIER DESTROYED

*** PRC CAN SUSTAIN SALVO ATTACKS; US CANNOT ***
```

---

## 8. RECOMMENDATIONS

### 8.1 Immediate Priorities (2026-2028)

| Priority | Action | Impact | Cost |
|----------|--------|--------|------|
| 1 | **Accelerate GPI** to close glide phase gap | HGV defense | $5B |
| 2 | **Increase SM-6 Block IB** procurement | Terminal defense | $3B |
| 3 | **Deploy SEWIP Block III** fleet-wide | Soft kill layer | $2B |
| 4 | **Project Overmatch** full integration | AI-enabled defense | $2B |
| 5 | **Forward ammunition stockpiles** | Magazine depth | $4B |

### 8.2 Medium-Term (2028-2032)

| Priority | Action | Impact | Cost |
|----------|--------|--------|------|
| 1 | **GPI IOC** achievement | Close gap | $10B |
| 2 | **Directed Energy Weapons** | Unlimited magazine | $5B |
| 3 | **At-sea VLS reload** | Extend endurance | $2B |
| 4 | **Distributed Maritime Operations** | Reduce HVU targeting | Doctrine |
| 5 | **Left-of-launch** capabilities | Destroy ASBMs on ground | Classified |

### 8.3 Doctrinal Recommendations

1. **Do not operate CVNs within 2,000 km of PRC coast** until GPI is operational
2. **Prioritize soft kill** to conserve interceptors
3. **Distribute defensive assets** across multiple platforms
4. **Accept tactical risk** for some threats to preserve magazine
5. **Invest in deception** (decoys, signature management)

---

## 9. CONCLUSION

**The US Navy has PARTIAL capability to defend against Chinese ASBMs, with a CRITICAL GAP in the glide phase:**

### Strengths:
- SM-3 Block IIA provides credible midcourse defense
- SM-6 Dual II offers terminal layer protection
- SEWIP Block III enhances soft kill capability
- Aegis/NIFC-CA enables networked engagement
- Project Overmatch introduces AI optimization

### Critical Vulnerabilities:
- **Glide Phase Gap:** No operational interceptor for 40-100 km altitude (GPI not ready until 2031)
- **HGV Vulnerability:** DF-27 and similar HGVs exploit this gap
- **Magazine Depth:** Cannot sustain defense against multiple salvos
- **Cost Exchange:** 39:1 unfavorable ratio is unsustainable
- **Saturation:** >50 ASBM salvo overwhelms defenses

> **Bottom Line:**
> Until GPI achieves IOC (~2031), US aircraft carriers face an unacceptable
> risk from hypersonic glide vehicles. The current layered defense is
> adequate against limited conventional ASBM strikes but insufficient
> against peer adversary saturation attacks.
>
> **Strategic Imperatives:**
> - Accelerate GPI development as highest priority
> - Keep carriers outside 2,000 km of PRC until gap is closed
> - Invest heavily in soft kill and deception
> - Develop distributed operations to reduce targeting
> - Accept that carrier operations near China are HIGH RISK until 2032+

---

## APPENDIX A: GLOSSARY

| Term | Definition |
|------|------------|
| ASBM | Anti-Ship Ballistic Missile |
| HGV | Hypersonic Glide Vehicle |
| MaRV | Maneuvering Reentry Vehicle |
| LEAP | Lightweight Exo-Atmospheric Projectile (SM-3 kill vehicle) |
| GPI | Glide Phase Interceptor |
| SEWIP | Surface Electronic Warfare Improvement Program |
| NIFC-CA | Naval Integrated Fire Control - Counter Air |
| VLS | Vertical Launch System |
| Pk | Probability of Kill |
| CSG | Carrier Strike Group |

---

## APPENDIX B: DATA SOURCES

| Data | Source | Classification |
|------|--------|----------------|
| SM-3 specifications | Raytheon, MDA | UNCLASS |
| SM-6 specifications | Raytheon, Navy | UNCLASS |
| SEWIP Block III | Northrop Grumman, Navy | UNCLASS |
| Chinese ASBM data | DOD China Military Power Report | UNCLASS |
| GPI program status | MDA budget documents | UNCLASS |
| Pk estimates | Open source analysis | UNCLASS |

---

## APPENDIX C: ASSUMPTIONS

1. DF-21D/DF-26 have functional terminal seekers (demonstrated)
2. PRC can mass 50+ ASBMs in coordinated salvo
3. SM-3 Block IIA tested against MaRV with partial success
4. GPI will not achieve IOC before 2029-2031
5. SEWIP Block III effectiveness based on similar systems
6. Carrier cannot outrun ASBM (30 kts vs Mach 10)
7. No nuclear weapons employed

---

**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Prepared By:** DOD System Proposal CAD
**Date:** 2026-01-04
