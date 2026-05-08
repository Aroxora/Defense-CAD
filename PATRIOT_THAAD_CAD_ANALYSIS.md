# Patriot & THAAD Air Defense Systems - CAD Analysis

**System:** Patriot Advanced Capability (PAC-3) & Terminal High Altitude Area Defense (THAAD)
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Analysis Date:** 2026-01-03
**Framework:** Integrated Air and Missile Defense (IAMD) Capability Assessment CAD

---

## EXECUTIVE SUMMARY

**VERDICT: ESSENTIAL BUT INSUFFICIENT for Peer Conflict Saturation**

Patriot and THAAD provide layered ballistic missile defense but face severe magazine depth limitations against PRC/Russia saturation attacks:

| System | Role | Intercept Range | Altitude | Pk (Est.) | Assessment |
|--------|------|-----------------|----------|-----------|------------|
| THAAD | Upper-tier BMD | 200+ km | 150 km | 0.90 | EXCELLENT |
| PAC-3 MSE | Lower-tier BMD | 35 km | 40 km | 0.85 | EXCELLENT |
| PAC-2 GEM-T | AAW/Cruise | 160 km | 24 km | 0.70 | GOOD |

| Critical Metric | Value | Assessment |
|-----------------|-------|------------|
| Patriot Battery Cost | $1.1B | HIGH |
| THAAD Battery Cost | $2.0B | VERY HIGH |
| PAC-3 MSE Missile | $5.0M | EXPENSIVE |
| THAAD Interceptor | $12.7M | VERY EXPENSIVE |
| Magazine Depth | 48-64 per battery | INSUFFICIENT |

---

## 1. SYSTEM SPECIFICATIONS

### 1.1 Patriot PAC-3 MSE

| Specification | Value | Source |
|--------------|-------|--------|
| System Cost (battery) | $1.1B | Army |
| Interceptor Cost (MSE) | $5.0M | Lockheed Martin |
| Interceptor Cost (PAC-2 GEM-T) | $3.0M | Raytheon |
| Radar (AN/MPQ-65A) | AESA | Raytheon |
| Detection Range | 180+ km | Raytheon |
| Track Capacity | 100+ targets | Raytheon |
| Engagement Range (MSE) | 35+ km | Lockheed Martin |
| Engagement Altitude (MSE) | 40 km | Lockheed Martin |
| Engagement Range (GEM-T) | 160 km (AAW) | Raytheon |
| Engagement Altitude (GEM-T) | 24 km | Raytheon |
| Launchers per Battery | 6-8 | Army |
| Missiles per Launcher | 16 (MSE) or 4 (GEM-T) | Army |
| Reload Time | 30 minutes | Army |
| Crew per Battery | 90 | Army |
| Setup Time | 30 minutes | Army |
| Mobility | Road-mobile | Army |

### 1.2 THAAD System

| Specification | Value | Source |
|--------------|-------|--------|
| System Cost (battery) | $2.0B | MDA |
| Interceptor Cost | $12.7M | Lockheed Martin |
| Radar (AN/TPY-2) | X-band AESA | Raytheon |
| Detection Range | 1,000+ km | Raytheon |
| Track Capacity | 200+ targets | Raytheon |
| Engagement Range | 200+ km | Lockheed Martin |
| Engagement Altitude | 150 km (exo-atmospheric) | Lockheed Martin |
| Launchers per Battery | 6 | Army |
| Missiles per Launcher | 8 | Army |
| Total Missiles per Battery | 48 | Army |
| Reload Time | 45 minutes | Army |
| Crew per Battery | 95 | Army |
| Setup Time | 2 hours | Army |
| Mobility | Road-mobile (C-17 transportable) | Army |

### 1.3 Layered Defense Architecture

```
INTEGRATED AIR AND MISSILE DEFENSE (IAMD) LAYERS

UPPER TIER (THAAD - Exo-atmospheric):
├── Target: MRBMs, IRBMs (DF-21, DF-26)
├── Intercept: 40-150 km altitude
├── Range: 200+ km
└── Pk: 0.85-0.95

LOWER TIER (PAC-3 MSE - Endo-atmospheric):
├── Target: SRBMs, TBMs, cruise missiles
├── Intercept: 15-40 km altitude
├── Range: 35 km
└── Pk: 0.80-0.90

AAW LAYER (PAC-2 GEM-T):
├── Target: Aircraft, cruise missiles
├── Intercept: 5-24 km altitude
├── Range: 160 km (AAW), 20 km (TBM)
└── Pk: 0.70-0.85

POINT DEFENSE (Future):
├── IFPC-HEL (Directed Energy)
├── Counter-UAS
└── RAM/Cruise missile terminal
```

### 1.4 Cost Summary

| Component | Patriot Battery | THAAD Battery |
|-----------|-----------------|---------------|
| Radar System | $250M | $550M |
| Fire Control | $150M | $200M |
| Launchers (6) | $120M | $300M |
| Interceptors (48) | $240M (MSE) | $610M |
| Support Equipment | $100M | $150M |
| C2/Communications | $80M | $100M |
| Training/Spares | $100M | $90M |
| **Total Battery** | **$1.1B** | **$2.0B** |
| **Annual O&S** | $50M | $75M |

---

## 2. THREAT ENVIRONMENT ANALYSIS

### 2.1 Ballistic Missile Threats

| Threat | Type | Range | CEP | Quantity | Cost Est. |
|--------|------|-------|-----|----------|-----------|
| DF-11 | SRBM | 300 km | 150m | 200+ | $3M |
| DF-15 | SRBM | 600 km | 50m | 300+ | $5M |
| DF-16 | MRBM | 1,000 km | 10m | 200+ | $8M |
| DF-21D | MRBM/ASBM | 1,500 km | 10m | 200+ | $15M |
| DF-26 | IRBM | 4,000 km | 10m | 100+ | $20M |
| DF-17 | HGV | 2,000 km | 10m | 100+ | $30M |
| Iskander-M | SRBM | 500 km | 5m | 500+ | $8M |
| KN-23 (NK) | SRBM | 600 km | 50m | 100+ | $5M |

### 2.2 Cruise Missile Threats

| Threat | Type | Range | Speed | Quantity | Cost Est. |
|--------|------|-------|-------|----------|-----------|
| YJ-18 | LACM | 540 km | Mach 3 (terminal) | 1,000+ | $2M |
| CJ-10 | LACM | 1,500 km | Subsonic | 500+ | $3M |
| DH-10 | LACM | 1,500 km | Subsonic | 500+ | $3M |
| Kalibr | LACM | 1,500 km | Mach 2.9 (terminal) | 500+ | $3M |

### 2.3 Hypersonic Threats (Emerging)

| Threat | Type | Range | Speed | Intercept Difficulty |
|--------|------|-------|-------|---------------------|
| DF-17 | HGV | 2,000 km | Mach 10+ | EXTREME |
| DF-ZF | HGV | 2,500 km | Mach 10+ | EXTREME |
| Avangard | HGV | Global | Mach 20+ | IMPOSSIBLE (current) |
| Kinzhal | ALBM | 2,000 km | Mach 10 | VERY DIFFICULT |

### 2.4 Saturation Attack Scenario

```
PRC SALVO vs US PACIFIC BASE (Guam)

THREAT COMPOSITION:
├── DF-26 IRBMs: 24 missiles
├── DF-17 HGVs: 12 missiles
├── CJ-10 LACMs: 48 missiles
├── H-6K launched YJ-12: 24 missiles
└── TOTAL: 108 missiles

US DEFENSE (Guam):
├── THAAD Battery (1): 48 interceptors
├── Patriot Batteries (2): 96 PAC-3 MSE
├── TOTAL: 144 interceptors

ENGAGEMENT MATH:
├── THAAD vs DF-26: 24 threats x 2 shots = 48 interceptors (EXPENDED)
├── THAAD vs DF-17: 12 HGVs (CANNOT INTERCEPT - too maneuverable)
├── Patriot vs LACM: 72 threats x 2 shots = 144 interceptors (EXPENDED)
└── RESULT: 12 HGVs + leakers = SIGNIFICANT BASE DAMAGE

*** MAGAZINE DEPTH IS CRITICAL LIMITATION ***
```

---

## 3. OPERATIONAL CAPABILITY ANALYSIS

### 3.1 Patriot PAC-3 MSE Performance

```
PAC-3 MSE ENGAGEMENT SEQUENCE

T-300 sec: AN/MPQ-65A detects ballistic threat
T-280 sec: Track established, threat classification
T-250 sec: Engagement decision (automatic or manual)
T-240 sec: Launcher selected, missile assigned
T-230 sec: MSE launch (hot launch from canister)
T-180 sec: Missile acquires target (active radar)
T-0 sec:   Hit-to-kill intercept

PERFORMANCE ENVELOPE:
├── Max Range: 35+ km
├── Max Altitude: 40 km
├── Min Altitude: 15 km
├── Min Range: 3 km
├── Velocity at Impact: Mach 5+
└── Maneuverability: 50+ g

TARGET SET:
├── SRBMs: HIGH Pk (0.85-0.95)
├── TBMs: HIGH Pk (0.80-0.90)
├── MRBMs: MODERATE Pk (0.70-0.85) - limited time
├── Cruise Missiles: MODERATE Pk (0.70-0.80)
├── Aircraft: HIGH Pk (0.85-0.95)
└── HGVs: LOW Pk (0.30-0.50) - maneuvering target
```

### 3.2 THAAD Performance

```
THAAD ENGAGEMENT SEQUENCE

T-600 sec: AN/TPY-2 detects MRBM/IRBM in boost phase
T-550 sec: Track development, trajectory prediction
T-500 sec: Engagement decision (THAAD vs Aegis allocation)
T-450 sec: THAAD interceptor launch
T-300 sec: Interceptor receives midcourse update
T-60 sec:  Interceptor acquires target (IR seeker)
T-0 sec:   Hit-to-kill intercept (exo-atmospheric)

PERFORMANCE ENVELOPE:
├── Max Range: 200+ km
├── Max Altitude: 150 km (exo-atmospheric)
├── Min Altitude: 40 km
├── Velocity at Impact: Mach 8+
└── Maneuverability: Very High (exo-atmospheric)

TARGET SET:
├── MRBMs: HIGH Pk (0.85-0.95)
├── IRBMs: HIGH Pk (0.80-0.90)
├── SRBMs (high apogee): MODERATE Pk (0.70-0.85)
├── HGVs: LOW Pk (0.20-0.40) - glide phase unpredictable
└── Cruise Missiles: NO CAPABILITY (too low)
```

### 3.3 Layered Defense Effectiveness

| Threat Type | THAAD Pk | PAC-3 MSE Pk | Combined Pk | Leaker Prob |
|-------------|----------|--------------|-------------|-------------|
| SRBM (500 km) | N/A | 0.85 | 0.85 | 15% |
| MRBM (1,500 km) | 0.90 | 0.70 | 0.97 | 3% |
| IRBM (3,000 km) | 0.85 | 0.50 | 0.925 | 7.5% |
| HGV | 0.30 | 0.40 | 0.58 | 42% |
| Cruise Missile | N/A | 0.75 | 0.75 | 25% |

**Critical Finding:** Current systems have LOW Pk against hypersonic glide vehicles. This is the emerging gap.

---

## 4. NETWORK INTEGRATION

### 4.1 IBCS (Integrated Battle Command System)

| Capability | Pre-IBCS | With IBCS | Improvement |
|------------|----------|-----------|-------------|
| Sensor-Shooter Pairing | Same battery | Any shooter | Flexible |
| Track Sharing | Limited | Real-time | Full integration |
| Engagement Optimization | Manual | Automatic | Efficiency |
| Patriot + THAAD | Separate | Integrated | Layered defense |
| Aegis Integration | Limited | Full CEC | Joint BMD |

### 4.2 JADC2 Architecture

```
             ┌────────────────────┐
             │     SPACE LAYER    │
             │  SBIRS, DSP, SDA   │
             └─────────┬──────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │ AN/TPY-2│   │ SPY-6   │   │ LRDR    │
    │ (THAAD) │   │ (Aegis) │   │ (CONUS) │
    └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │
         └──────┬──────┴──────┬──────┘
                │    IBCS     │
         ┌──────┴──────┬──────┴──────┐
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │  THAAD  │   │ PAC-3   │   │  SM-3   │
    │Launcher │   │Launcher │   │ (DDG)   │
    └─────────┘   └─────────┘   └─────────┘
```

### 4.3 Engagement Authority Levels

| Level | Authority | Typical Use |
|-------|-----------|-------------|
| Weapons Free | Automatic engagement | Ballistic missile attack |
| Weapons Tight | Crew decision | High-value area defense |
| Weapons Hold | Manual only | Civilian airspace nearby |
| Centralized | Higher HQ | Strategic control |

---

## 5. SURVIVABILITY ASSESSMENT

### 5.1 Battery Survivability vs Strikes

| Threat | Detection | Pk (Battery Destroyed) | Notes |
|--------|-----------|------------------------|-------|
| DF-11/15 SRBM | Radar signature | 0.60 | Single warhead |
| DF-21D (conventional) | Radar signature | 0.80 | Penetrating warhead |
| CM-401 Swarm | Radar signature | 0.90 | Saturation attack |
| YJ-12 ASCM | Radar, heat | 0.70 | Mach 4 impact |
| Special Forces | HUMINT | 0.50 | Sabotage |

### 5.2 Battery Dispersion Options

| Configuration | Defended Area | Survivability | Trade-off |
|---------------|---------------|---------------|-----------|
| Concentrated | 50 km radius | Low | Best coverage |
| Dispersed | 30 km radius | Medium | Reduced overlap |
| Hide Sites | N/A (relocating) | High | Reduced availability |
| Decoys | N/A | Medium | Consumes enemy missiles |

### 5.3 Soft-Kill Measures

| Measure | Effectiveness | Status |
|---------|---------------|--------|
| Decoy Launchers | High | Deployed |
| Radar Emission Control | Moderate | Doctrine |
| Camouflage | Moderate | Deployed |
| Hardened C2 | High | Planned |
| Active Protection | Limited | Development |

---

## 6. STRATEGIC VIABILITY ASSESSMENT

### 6.1 Against PRC Missile Arsenal

| Criterion | Requirement | Patriot/THAAD | Status |
|-----------|-------------|---------------|--------|
| SRBM Defense | Pk >0.80 | 0.85 (MSE) | **PASS** |
| MRBM Defense | Pk >0.80 | 0.90 (THAAD) | **PASS** |
| IRBM Defense | Pk >0.70 | 0.85 (THAAD) | **PASS** |
| HGV Defense | Pk >0.70 | 0.30-0.40 | **FAIL** |
| Magazine Depth | 200+ missiles | 48-96 | **FAIL** |
| Reload Speed | <15 min | 30-45 min | **FAIL** |

### 6.2 Cost Exchange Analysis

**Scenario: Defense of Guam Against MRBM Salvo**

| US Expenditure | Cost |
|----------------|------|
| THAAD interceptors (24 @ $12.7M) | $305M |
| PAC-3 MSE (48 @ $5M) | $240M |
| **Total Defensive Expenditure** | **$545M** |

| Threat Intercepted | Value (Est.) |
|-------------------|--------------|
| DF-26 IRBMs (12 destroyed) | $240M |
| DF-21D MRBMs (12 destroyed) | $180M |
| **Total Threat Destroyed** | **$420M** |

**Cost Exchange Ratio: 1.3:1 UNFAVORABLE**

**However:** If 4 missiles leak and destroy $2B runway/facilities, cost exchange becomes **20:1 UNFAVORABLE** for US.

### 6.3 Magazine Depth Crisis

```
GUAM DEFENSE SCENARIO (Day 1)

PRC First Salvo:      100 ballistic missiles
US Interceptors:      144 (THAAD + Patriot)
Interceptors Used:    200 (2-shot doctrine)
Result:               WINCHESTER (out of ammo)

Reload Time:          4-6 hours (if supplies available)
PRC Second Salvo:     100 ballistic missiles
US Interceptors:      0 (reloading)
Result:               BASE DESTROYED

*** MAGAZINE DEPTH IS THE #1 LIMITATION ***
```

---

## 7. LIMITATIONS

### 7.1 Fundamental Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Magazine Depth** | 48-96 missiles exhausted rapidly | More launchers, faster reload |
| **HGV Defense** | Pk <0.50 against DF-17 | Glide Phase Interceptor (GPI) |
| **Reload Time** | 30-45 min, battery vulnerable | At-battery reload system |
| **Cost Exchange** | Interceptors cost more than threats | Directed energy, volume fires |
| **Mobility** | Hours to relocate | Pre-surveyed positions |

### 7.2 Operational Limitations

| Limitation | Details |
|------------|---------|
| Battery Footprint | 2+ km², easily targeted |
| Radar Signature | AN/TPY-2 is major emitter |
| Supply Chain | MSE missiles require special handling |
| Maintenance | 10+ maintenance personnel per launcher |
| Weather | Heavy rain degrades radar performance |

### 7.3 Doctrine Limitations

| Issue | Impact |
|-------|--------|
| 2-Shot Doctrine | Doubles interceptor expenditure |
| Human-in-Loop | Slows engagement in saturation |
| Airspace Coordination | Complex in joint environment |
| Rules of Engagement | May delay response |

---

## 8. COMPARISON WITH ALTERNATIVES

### 8.1 Air Defense System Comparison

| System | Range | Altitude | Pk (BM) | Cost (Battery) | Status |
|--------|-------|----------|---------|----------------|--------|
| THAAD | 200 km | 150 km | 0.90 | $2.0B | Active |
| PAC-3 MSE | 35 km | 40 km | 0.85 | $1.1B | Active |
| SM-3 IIA | 1,350 km | 1,000 km | 0.80 | $28M/missile | Active |
| S-400 | 380 km | 30 km | 0.75 | $500M | Active |
| Iron Dome | 70 km | 10 km | 0.90 | $50M | Active |
| David's Sling | 300 km | 15 km | 0.85 | $150M | Active |

### 8.2 BMD Layer Comparison

| Layer | System | Target Set | Pk | Cost/Shot |
|-------|--------|------------|-----|-----------|
| Boost | SM-3 Block IIA | ICBM/IRBM | 0.40 | $28M |
| Midcourse | GMD | ICBM | 0.50 | $75M |
| Terminal (High) | THAAD | MRBM/IRBM | 0.90 | $12.7M |
| Terminal (Low) | PAC-3 MSE | SRBM/TBM | 0.85 | $5M |
| Point | C-RAM | Rockets | 0.80 | $30K |

### 8.3 Cost-Effectiveness Ranking

| System | Cost per Kill | Defended Area | Verdict |
|--------|---------------|---------------|---------|
| Iron Dome | $100K | 20 km | EXCELLENT (short range) |
| PAC-3 MSE | $6M | 35 km | GOOD |
| THAAD | $14M | 200 km | GOOD |
| SM-3 IIA | $35M | 1,350 km | EXPENSIVE |
| GMD | $150M | CONUS | VERY EXPENSIVE |

---

## 9. RECOMMENDATIONS

### 9.1 Employment Guidance

1. **Prioritize Defense of:**
   - Airbases (enable power projection)
   - Ports (logistics)
   - C2 nodes (battle management)
   - Allied population centers (coalition support)

2. **Layered Defense Doctrine:**
   - THAAD as outer layer (MRBM/IRBM)
   - PAC-3 as inner layer (leakers, SRBM)
   - Future: Directed energy for volume threats

3. **Pre-Positioning:**
   - 2 THAAD batteries per major base (Guam, Japan, Korea)
   - 4 Patriot batteries per THAAD battery
   - Forward ammunition stockpiles

### 9.2 Capability Enhancement Priorities

| Priority | Enhancement | Impact | Cost |
|----------|-------------|--------|------|
| 1 | Glide Phase Interceptor (GPI) | Defeat HGVs | $5B |
| 2 | PAC-3 MSE capacity increase | More interceptors | $3B |
| 3 | IBCS full deployment | Integrated fire control | $2B |
| 4 | Directed Energy (IFPC-HEL) | Unlimited magazine | $4B |
| 5 | Rapid reload system | Reduce vulnerability | $1B |

### 9.3 Force Structure Recommendations

**Current:**
- 15 Patriot battalions (60 batteries)
- 7 THAAD batteries

**Recommended:**
- **Double THAAD batteries** to 14 (cover Guam, Japan, Korea, Gulf)
- **Increase PAC-3 MSE inventory** by 50%
- **Deploy IBCS** across all units by 2027
- **Accelerate GPI development** for HGV defense
- **Invest in directed energy** for magazine depth

---

## 10. CONCLUSION

Patriot and THAAD are **essential but insufficient** for the peer conflict threat environment:

**Strengths:**
- High Pk against conventional ballistic missiles
- Proven combat performance (Ukraine, Gulf states)
- Mobile and deployable
- Integration improving via IBCS
- Layered defense provides multiple engagement opportunities

**Critical Weaknesses:**
- **Magazine depth insufficient** for PRC saturation attacks
- **Cannot defeat hypersonic glide vehicles** (DF-17, DF-ZF)
- **Cost exchange unfavorable** ($5-12M interceptors vs $5-20M threats)
- **Reload time excessive** (30-45 min in combat)
- **Fixed sites vulnerable** to precision strike

> **Bottom Line:**
> Patriot and THAAD provide essential point defense but cannot protect
> against determined saturation attacks from a peer adversary. Magazine
> depth is the #1 limitation.
>
> **Strategic Imperatives:**
> - GPI must reach IOC by 2028 to address HGV gap
> - Directed energy is essential for cost-effective volume defense
> - Pre-positioned ammunition stockpiles are critical
> - Dispersion and mobility must be prioritized over concentration
>
> **Without significant investment in magazine depth and HGV defense,
> critical Pacific bases cannot be adequately defended against PRC
> first-strike capabilities.**

The current air defense posture is adequate for regional threats but critically insufficient for peer conflict.

---

## APPENDIX A: DATA SOURCES

| Data | Source | Classification |
|------|--------|----------------|
| Patriot specifications | Army, Raytheon | UNCLASS |
| THAAD specifications | MDA, Lockheed Martin | UNCLASS |
| Missile costs | CBO, GAO | UNCLASS |
| Pk estimates | Open source analysis | UNCLASS |
| PRC missile inventory | DOD China Military Power | UNCLASS |

---

## APPENDIX B: ASSUMPTIONS

1. PAC-3 MSE Pk of 0.85 based on test record and Ukraine combat
2. THAAD Pk of 0.90 based on test record (no combat use yet)
3. Two-shot doctrine (2 interceptors per threat) assumed
4. PRC able to mass 100+ missiles per salvo against single target
5. Reload operations assume uncontested airspace
6. IBCS full deployment by 2027 per Army schedule

---

## APPENDIX C: GLOBAL DEPLOYMENT

| Region | Patriot Batteries | THAAD Batteries | Notes |
|--------|-------------------|-----------------|-------|
| Korea | 8 | 1 | North Korea threat |
| Japan | 8 | 2 | PRC, Russia, NK |
| Guam | 4 | 1 | Critical base defense |
| Gulf States | 12 | 2 | Iran threat |
| Europe | 8 | 0 | Russia threat (increasing) |
| Israel | 4 (coproduction) | 0 | Arrow supplement |
| CONUS | 8 | 1 | Strategic reserve |
| **Total** | **52** | **7** | |

---

## APPENDIX D: INTERCEPTOR INVENTORY REQUIREMENTS

| Scenario | Threat Missiles | Interceptors Req'd | Current Inventory | Shortfall |
|----------|-----------------|-------------------|-------------------|-----------|
| Korea Crisis | 500 SRBM | 1,000 PAC-3 | 700 | 300 |
| Taiwan Conflict | 1,500 BM + CM | 3,000 PAC-3 + 500 THAAD | 700 + 200 | SEVERE |
| Gulf Conflict | 300 BM | 600 PAC-3 | 700 | None |
| Ukraine Support | Ongoing | Ongoing | Depleting | Resupply critical |

**Critical Finding:** Current interceptor production (PAC-3: ~500/year, THAAD: ~50/year) cannot sustain high-intensity conflict.

---

**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Prepared By:** DOD System Proposal CAD
**Date:** 2026-01-03
