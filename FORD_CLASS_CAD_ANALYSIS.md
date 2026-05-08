# Ford Class Aircraft Carrier (CVN-78) - CAD Analysis

**System:** Ford Class Nuclear Aircraft Carrier (CVN-78+)
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Analysis Date:** 2026-01-03
**Framework:** Naval Platform Capability Assessment CAD

---

## EXECUTIVE SUMMARY

**VERDICT: HIGH VALUE / HIGH RISK in A2/AD Environments**

The Ford class represents the pinnacle of carrier aviation capability, but faces existential threats from modern anti-ship weapons:

| Metric | Value | Assessment |
|--------|-------|------------|
| Air Wing Capacity | 75+ aircraft | EXCELLENT |
| Sortie Generation | 160/day surge | EXCELLENT |
| Unit Cost | $13.3B | EXTREMELY HIGH |
| Survivability vs DF-21D | 40-60% | MARGINAL |
| Survivability vs DF-26 | 30-50% | POOR |
| Operating Distance Required | 1,500+ km | CONSTRAINING |

---

## 1. SYSTEM SPECIFICATIONS

### 1.1 CVN-78 Gerald R. Ford

| Specification | Value | Source |
|--------------|-------|--------|
| Unit Cost | $13.3B (FY2024) | GAO Report |
| Full Load Displacement | 100,000+ tons | USN |
| Length | 1,106 ft (337 m) | USN |
| Beam | 256 ft (78 m) | USN |
| Draft | 39 ft (12 m) | USN |
| Propulsion | 2x A1B nuclear reactors | USN |
| Speed | 30+ knots | USN |
| Range | Unlimited (nuclear) | USN |
| Crew | 4,539 (ship + air wing) | USN |
| Air Wing | 75+ aircraft | USN |
| Service Life | 50 years | USN |
| Catapults | 4x EMALS | USN |
| Arresting Gear | 3x AAG | USN |
| Weapons Elevators | 11 (Advanced) | USN |

### 1.2 Carrier Air Wing Composition (Typical)

| Aircraft | Quantity | Role |
|----------|----------|------|
| F/A-18E/F Super Hornet | 44 | Strike Fighter |
| F-35C Lightning II | 20 | Stealth Strike |
| EA-18G Growler | 5 | Electronic Attack |
| E-2D Advanced Hawkeye | 5 | AEW&C |
| CMV-22B Osprey | 2 | COD |
| MH-60R/S Seahawk | 8 | ASW/SAR |
| MQ-25 Stingray | 4-6 | Tanker/ISR |

### 1.3 Defensive Systems

| System | Quantity | Capability |
|--------|----------|------------|
| RIM-162 ESSM | 32 cells | Short-range AAW |
| RIM-116 RAM | 2 launchers | Point defense |
| Phalanx CIWS | 3 mounts | Last-ditch defense |
| AN/SLQ-32(V)6 SEWIP | 1 | Electronic warfare |
| AN/SPN-46 | 1 | Precision approach |
| AN/SPY-6(V)3 | 1 | Air search radar |

### 1.4 Cost Summary

| Component | Cost | Notes |
|-----------|------|-------|
| Hull Construction | $8.1B | Huntington Ingalls |
| Propulsion (A1B) | $2.2B | Bechtel Marine |
| Combat Systems | $1.8B | Various |
| Aircraft Elevators | $0.4B | Advanced design |
| EMALS/AAG | $0.8B | GA-EMS |
| **Total Ship Cost** | **$13.3B** | FY2024 |
| Air Wing Cost | $7.2B | 75+ aircraft |
| **Total Battle System** | **$20.5B** | Ship + Air Wing |

---

## 2. THREAT ENVIRONMENT ANALYSIS

### 2.1 Anti-Access/Area Denial (A2/AD) Threats to Carriers

| Threat | Type | Range | Quantity | Est. Cost |
|--------|------|-------|----------|-----------|
| DF-21D ASBM | Ballistic | 1,500 km | 200+ | $10-15M |
| DF-26 ASBM | Ballistic | 4,000 km | 100+ | $20M |
| YJ-21 | Hypersonic | 1,500 km | Unknown | $15M |
| YJ-18 | Cruise | 540 km | 1,000+ | $2M |
| CM-401 | Quasi-ballistic | 290 km | 500+ | $3M |
| Type 039C Submarine | SSK | 500+ km torpedo | 20+ | $350M |
| H-6K/N Bomber | LACM | 3,000 km | 180+ | $100M |

### 2.2 Carrier Operating Envelope

```
Distance from Chinese Coast:

0 km ────────── Coast
        │
500 km ─┼───── YJ-18 cruise missile range
        │
1,000 km┼───── H-6K with YJ-12 standoff
        │
1,500 km┼───── DF-21D ASBM range
        │      *** CARRIER MUST STAY OUTSIDE ***
        │
2,000 km┼───── F/A-18E/F combat radius (with tanking)
        │
3,000 km┼───── F-35C combat radius (with tanking)
        │
4,000 km┼───── DF-26 ASBM range
        │      *** EVEN GUAM AT RISK ***
```

### 2.3 The Targeting Problem

**Detection Methods:**
- OTH radar (3,000+ km detection)
- Satellite surveillance (optical, SAR, ELINT)
- Maritime patrol aircraft (Y-8/Y-9)
- Submarine pickets
- Fishing fleet intelligence

**Kill Chain:**
1. Detect carrier group (OTH, satellite)
2. Classify and track (MPA, submarine)
3. Develop targeting solution
4. Launch ASBM salvo
5. Mid-course guidance (satellite, UAV)
6. Terminal seeker acquisition
7. Impact

**Problem:** A carrier is a 100,000-ton heat source moving at 30 knots. It is NOT stealthy.

---

## 3. OPERATIONAL CAPABILITY ANALYSIS

### 3.1 Power Projection Capability

```
FORD CLASS STRIKE CAPABILITY

PHASE 1: POSITIONING
├── Transit to operating area
├── Establish CAP/ASW screen
├── Coordinate with CSG escorts
└── Receive targeting from national assets

PHASE 2: STRIKE GENERATION
├── EMALS launch cycle (45 sec per aircraft)
├── 160 sorties/day surge capability
├── 120 sorties/day sustained
├── Deck cycle time: 90 minutes
└── Aircraft turnaround: 4-6 hours

PHASE 3: STRIKE EXECUTION
├── F-35C: Penetrating strike (stealth)
├── F/A-18E/F: Standoff weapons (JASSM-ER)
├── EA-18G: Electronic attack support
├── E-2D: Battle management
└── MQ-25: Tanking support

PHASE 4: RECOVERY
├── AAG recovery operations
├── Aircraft servicing
├── Ordnance replenishment
└── Crew rest/rotation
```

### 3.2 Air Wing Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Max Sortie Rate (surge) | 160/day | 12-hour ops |
| Sustained Sortie Rate | 120/day | 30-day ops |
| Strike Range (internal) | 500 nm | F-35C |
| Strike Range (JASSM-ER) | 500 nm + 500 nm | Standoff |
| Time to Generate 20 Sorties | 2 hours | EMALS advantage |
| Ordnance Capacity | 3,600+ tons | Magazines |
| Aviation Fuel | 3.5M gallons | JP-5 |

### 3.3 EMALS/AAG Advantages

| System | Ford (EMALS/AAG) | Nimitz (Steam) | Improvement |
|--------|------------------|----------------|-------------|
| Catapult Cycles | 4,166/day (theoretical) | 1,600/day | +160% |
| Energy Efficiency | 90% | 5% | +1,700% |
| Peak Stress on Airframe | Reduced 30% | Baseline | Aircraft life |
| Maintenance Hours | -20% | Baseline | Availability |
| Launch Weight Range | 0-100,000 lb | 25,000-75,000 lb | Flexibility |

---

## 4. NETWORK INTEGRATION

### 4.1 Carrier as Network Node

| Capability | Rating | Notes |
|------------|--------|-------|
| Sensor Hub | Excellent | E-2D, SPY-6, F-35 |
| C2 Node | Excellent | NIFC-CA capable |
| Shooter | Excellent | Air wing provides |
| Data Fusion | Excellent | CEC integration |
| Communications | Excellent | Multi-band SATCOM |

### 4.2 Cooperative Engagement Capability (CEC)

```
                    ┌─────────────┐
                    │   SATELLITE │
                    │   (SATCOM)  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼────┐
   │   E-2D  │◄─────►│  CVN-78   │◄────►│  DDG    │
   │ Hawkeye │  CEC  │  FORD     │ CEC  │ (Aegis) │
   └────┬────┘       └─────┬─────┘      └────┬────┘
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼────┐
   │  F-35C  │       │  F/A-18E  │      │  SM-6   │
   │ Sensors │       │  Shooters │      │ Shooters│
   └─────────┘       └───────────┘      └─────────┘
```

### 4.3 NIFC-CA Kill Chain

| Component | Role | Link |
|-----------|------|------|
| E-2D Advanced Hawkeye | Track development | CEC |
| F-35C | Sensor/shooter | MADL/Link 16 |
| CVN-78 | Battle management | CEC |
| DDG (Aegis) | SM-6 shooter | CEC |
| Satellite | Communications relay | SATCOM |

---

## 5. SURVIVABILITY ASSESSMENT

### 5.1 Threat-Specific Survivability

| Threat | Detection Prob | Targeting Prob | Pk (single) | Survivability |
|--------|----------------|----------------|-------------|---------------|
| DF-21D (salvo of 6) | 95% | 70% | 0.15 | 40% |
| DF-26 (salvo of 4) | 90% | 60% | 0.20 | 35% |
| YJ-21 (salvo of 8) | 90% | 75% | 0.10 | 50% |
| Type 039C Torpedo | 60% | 50% | 0.40 | 88% |
| Submarine-Launched YJ-18 | 70% | 65% | 0.12 | 60% |

### 5.2 Defensive Layer Effectiveness

| Layer | Range | Threats Engaged | Pk |
|-------|-------|-----------------|-----|
| CAP (F/A-18E/F) | 200+ nm | Bombers, cruise missiles | 0.85 |
| E-2D + SM-6 | 150+ nm | ASBMs (terminal), cruise missiles | 0.70 |
| ESSM | 30 nm | Cruise missiles, ASCMs | 0.80 |
| RAM | 5 nm | Leakers | 0.70 |
| Phalanx CIWS | 1 nm | Last ditch | 0.50 |

### 5.3 Damage Tolerance

| Damage Scenario | Ship Status | Air Ops |
|-----------------|-------------|---------|
| 1 ASCM hit (1,000 lb) | Mission capable | Degraded |
| 2 ASCM hits | Mission kill likely | Suspended |
| 1 ASBM hit | Mission kill | Impossible |
| Torpedo hit (533mm) | Possible sinking | Impossible |

**Key Finding:** The Ford class cannot survive a successful hit from a DF-21D or DF-26 ASBM. The cost of a successful hit ($20M missile vs $13.3B carrier) represents catastrophic cost exchange.

---

## 6. STRATEGIC VIABILITY ASSESSMENT

### 6.1 Against PRC A2/AD

| Criterion | Requirement | Ford Class | Status |
|-----------|-------------|------------|--------|
| Operating Distance | >1,500 km from coast | 1,500+ km | MARGINAL |
| Strike Range | >1,000 km | 500-1,000 km | MARGINAL |
| Survivability | >90% | 40-60% | **FAIL** |
| Sortie Generation | 100+/day | 120-160/day | PASS |
| Cost Exchange | Favorable | Unfavorable | **FAIL** |

### 6.2 Cost Exchange Analysis

**Scenario: Carrier Lost to ASBM Salvo**

| US Loss | Cost |
|---------|------|
| CVN-78 Ford | $13.3B |
| Air Wing (75 aircraft) | $7.2B |
| Ordnance | $0.5B |
| Personnel (4,500+) | Incalculable |
| **Total Loss** | **$21.0B+** |

| PRC Expenditure | Cost |
|-----------------|------|
| DF-21D salvo (6 missiles) | $90M |
| Targeting support | $10M |
| **Total Expenditure** | **$100M** |

**Cost Exchange Ratio: 210:1 UNFAVORABLE**

### 6.3 Operational Constraints

```
SAFE OPERATING ZONE (Beyond DF-21D Range)

CHINA ────────────────────────────────────────────► 4,000 km
     0 km                      1,500 km            (DF-26 range)

     ├──── DF-21D ────────────┤
                              │
                              ▼ CARRIER MUST STAY HERE
                              │
              F-35C Strike ───┤──► 500 nm combat radius
                              │
              With JASSM-ER ──┤──► +500 nm standoff
                              │
                         ═════╪══════════════════════
                              │ COVERAGE GAP
                         ═════╪══════════════════════
                              │
                    Mainland China
```

**Problem:** Even from 1,500 km standoff, F-35C strike range is insufficient for most mainland targets without standoff weapons.

---

## 7. LIMITATIONS

### 7.1 Fundamental Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Size** | Cannot hide; always detected | Deception, EMCON |
| **Cost** | Cannot afford to lose | Don't operate in A2/AD |
| **Basing** | Floating airbase is targetable | Distance, mobility |
| **Air Wing Range** | Limited without tanking | MQ-25 Stingray |

### 7.2 Operational Limitations

| Limitation | Details |
|------------|---------|
| Replenishment | Requires UNREP every 7-10 days |
| Maintenance | Major repairs require port |
| Crew Fatigue | 18-hour ops sustainable ~7 days |
| Weather | Flight ops degraded in storms |
| Damage Control | Major damage = mission kill |

### 7.3 Technological Limitations

| System | Limitation | Impact |
|--------|------------|--------|
| EMALS | Still maturing; reliability issues | Sortie rate |
| AAG | Energy absorption variations | Recovery ops |
| Weapons Elevators | Complex; maintenance intensive | Rearming speed |
| A1B Reactor | First-of-class issues | Long-term availability |

---

## 8. COMPARISON WITH ALTERNATIVES

### 8.1 Carrier Class Comparison

| Class | Displacement | Air Wing | Sortie Rate | Cost | Status |
|-------|--------------|----------|-------------|------|--------|
| Ford (CVN-78) | 100,000 | 75+ | 160/day | $13.3B | Building |
| Nimitz (CVN-68) | 97,000 | 75+ | 120/day | $8.5B | Operational |
| Queen Elizabeth | 65,000 | 40 | 72/day | $3.5B | Operational |
| Fujian (Type 003) | 80,000 | 60+ | 100/day (est) | $5B (est) | Fitting out |

### 8.2 Alternative Force Structures

| Option | Cost | Strike Capacity | Survivability |
|--------|------|-----------------|---------------|
| 1 Ford CSG | $25B | 160 sorties/day | 40-60% |
| 100 B-21 sorties | $15B | 200 JASSM-XR | 95% |
| 500 Tomahawk (SSGN) | $1B | 500 missiles | 98% |
| 50 Rapid Dragon | $0.5B | 500 JASSM | 90% |

### 8.3 Cost-Effectiveness Ranking

| System | Cost/Strike Sortie | Survivability | Verdict |
|--------|-------------------|---------------|---------|
| SSGN Tomahawk | $2.0M | 98% | **BEST** |
| Rapid Dragon | $2.5M | 90% | Excellent |
| B-21 + JASSM-XR | $10M | 95% | Good |
| Ford CSG | $45M | 50% | Poor in A2/AD |

---

## 9. RECOMMENDATIONS

### 9.1 Employment Guidance

1. **DO NOT operate within DF-21D range** (1,500 km) of PRC in peer conflict
2. **Use for:**
   - Sea control outside A2/AD
   - Power projection vs. lesser threats
   - Humanitarian/disaster response
   - Presence/deterrence operations
3. **Maximize standoff weapons:**
   - JASSM-ER on F/A-18E/F
   - LRASM for maritime strike
   - Future hypersonic weapons

### 9.2 Capability Enhancement Priorities

| Priority | Enhancement | Impact | Cost |
|----------|-------------|--------|------|
| 1 | MQ-25 Stingray integration | +50% strike range | $4B |
| 2 | Hypersonic anti-ship weapon | Standoff strike | $2B |
| 3 | Enhanced BMD capability | ASBM defense | $1B |
| 4 | Directed energy weapons | ASCM defense | $0.5B |
| 5 | CCA integration | Extend sensor/shooter | $3B |

### 9.3 Force Mix Recommendations

**Current Carrier-Centric:**
- 11 carriers (risk concentrated)
- High value / high vulnerability

**Recommended Distributed:**
- 8-9 carriers (reduce to sustainable)
- Invest savings in:
  - B-21 Raiders
  - SSGNs with Tomahawk/hypersonic
  - Rapid Dragon pallets
  - Unmanned surface vessels

---

## 10. CONCLUSION

The Ford class is an **engineering marvel** that is **strategically vulnerable** in the primary threat environment:

**Strengths:**
- Unmatched sortie generation capacity
- Most capable air wing in the world
- Excellent C2 and network integration
- EMALS/AAG enable future aircraft

**Fatal Weaknesses:**
- $13.3B target that cannot hide
- Must stay 1,500+ km from PRC coast
- Air wing range insufficient for standoff strike
- **Single ASBM hit = $21B loss**

**Bottom Line:**
> The Ford class carrier is the most capable warship ever built, but it
> represents a concentration of national treasure that the nation cannot
> afford to lose. Against a peer adversary with mature A2/AD, the carrier
> must operate at such distance that its strike capability is marginalized.
>
> **The carrier remains essential for lesser contingencies and sea control,
> but should not be the primary strike platform against PRC A2/AD.**

Investment should shift toward distributed, survivable platforms (SSGNs, B-21, unmanned systems) that can achieve favorable cost exchange while preserving carriers for missions where they remain dominant.

---

## APPENDIX A: DATA SOURCES

| Data | Source | Classification |
|------|--------|----------------|
| CVN-78 specifications | US Navy, GAO | UNCLASS |
| Air wing composition | USN public | UNCLASS |
| ASBM ranges | DOD China Military Power | UNCLASS |
| Cost data | CBO, GAO reports | UNCLASS |
| Survivability estimates | Open source analysis | UNCLASS |

---

## APPENDIX B: ASSUMPTIONS

1. PRC ASBM kill chain is functional (demonstrated capability)
2. Carrier cannot evade coordinated satellite/OTH surveillance
3. Defensive systems cannot achieve 100% intercept vs saturation attack
4. DF-21D/DF-26 Pk estimates based on unclassified analysis
5. No nuclear weapons employed
6. PRC willing to attack US carrier in peer conflict scenario

---

**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Prepared By:** DOD System Proposal CAD
**Date:** 2026-01-03
