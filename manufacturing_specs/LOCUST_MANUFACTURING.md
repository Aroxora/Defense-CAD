# LOCUST - Manufacturing Specification

**System:** LOCUST Scramjet Swarm Missile System
**Codename:** LOCUST
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Version:** 1.0
**Date:** 2026-01-02

---

## 1. SYSTEM OVERVIEW

### 1.1 Mission
Mach 5 scramjet cruise missiles for mass saturation attacks, featuring mesh-networked swarm coordination and autonomous target recognition (ATR) terminal guidance.

### 1.2 Strategic Rationale
- $3M per unit enables mass production (2,500 over 5 years)
- Mach 5 speed reduces defender reaction time
- Swarm coordination overwhelms point defenses
- 4:1 favorable cost exchange ratio
- Attritable design accepts losses

### 1.3 Key Performance Parameters
| Parameter | Requirement |
|-----------|-------------|
| Speed | Mach 5 (sustained) |
| Range | 800 km |
| CEP | < 5 m |
| Unit Cost | $3M (production) |
| Swarm Size | 20+ cooperative |
| Launch Platform | Ground mobile |

---

## 2. BILL OF MATERIALS

### 2.1 LOCUST Scramjet Missile

| Component | Quantity | Unit Cost | Supplier |
|-----------|----------|-----------|----------|
| Airframe (thermal protection) | 1 | $380,000 | Lockheed Martin |
| Scramjet Engine | 1 | $485,000 | Aerojet Rocketdyne |
| Solid Rocket Booster | 1 | $165,000 | Northrop Grumman |
| MEMS INS/GPS | 1 | $125,000 | Honeywell |
| MMW Seeker | 1 | $285,000 | Raytheon |
| ATR Processor | 1 | $195,000 | Anduril |
| Swarm Datalink | 1 | $145,000 | L3Harris |
| Flight Computer | 1 | $165,000 | BAE Systems |
| Warhead (blast/frag) | 1 | $85,000 | General Dynamics |
| Thermal Management | 1 | $220,000 | Cobham |
| Actuators (4) | 4 | $28,000 | Moog Inc |
| Power System | 1 | $68,000 | EaglePicher |
| Structure/Fins | 1 | $145,000 | Spirit AeroSystems |
| Integration/Test | 1 | $285,000 | Prime |
| **Missile Total** | - | **$2.876M** | - |

### 2.2 Ground Launch System (Per Battery)

| Component | Quantity | Unit Cost | Supplier |
|-----------|----------|-----------|----------|
| 4-Cell Launcher | 4 | $2.8M | Lockheed Martin |
| Prime Mover (HEMTT) | 4 | $580K | Oshkosh Defense |
| Fire Control Center | 1 | $8.5M | Northrop Grumman |
| Communications Suite | 1 | $2.2M | L3Harris |
| Power Generator | 2 | $185K | Caterpillar |
| Reload Trailer | 2 | $125K | Various |
| **Launch System Total** | - | **$24.3M** | - |

---

## 3. MANUFACTURING PROCESS

### 3.1 Scramjet Engine (Aerojet Rocketdyne)

```
STAGE 1: Combustor Fabrication (Days 1-20)
├── CMC liner fabrication
│   ├── SiC fiber layup
│   ├── CVI infiltration (7 days)
│   └── Final machining
├── Inconel outer shell
│   ├── Forging
│   ├── Machining
│   └── Cooling channel drilling
└── Fuel injector array
    ├── Additive manufacturing
    └── Flow calibration

STAGE 2: Inlet/Isolator (Days 21-35)
├── Titanium forging
├── 5-axis machining
├── Surface coating
├── Boundary layer bleed
└── Variable geometry actuators

STAGE 3: Nozzle Assembly (Days 36-45)
├── Carbon-carbon fabrication
├── Throat insert
├── Expansion section
└── TPS integration

STAGE 4: Integration (Days 46-60)
├── Combustor/inlet mate
├── Nozzle integration
├── Fuel system
├── Ignition system
├── Instrumentation
└── Acceptance test

STAGE 5: Test (Days 61-70)
├── Cold flow verification
├── Ground test (5 sec burn)
├── Performance validation
└── QA documentation
```

### 3.2 Airframe Fabrication

```
STAGE 1: Structure (Days 1-15)
├── Titanium frame machining
├── CMC leading edges
├── Thermal standoffs
└── Internal structure

STAGE 2: Thermal Protection (Days 16-30)
├── Ablative nose cone
├── CMC wing leading edges
├── Thermal blankets
├── Active cooling channels
└── Surface treatments

STAGE 3: Assembly (Days 31-50)
├── Frame integration
├── TPS installation
├── Actuator mounting
├── Wiring harness
└── Seal installation

STAGE 4: Systems (Days 51-70)
├── Engine installation
├── Avionics bay
├── Seeker mounting
├── Fuel tank installation
├── Warhead integration
└── Booster attachment

STAGE 5: Final/Test (Days 71-85)
├── Weight/balance
├── Functional test
├── Environmental screen
├── Final inspection
└── Packaging
```

### 3.3 Production Rate

| Year | Missiles | Launchers | Notes |
|------|----------|-----------|-------|
| 2029 | 100 | 20 | LRIP |
| 2030 | 300 | 30 | Ramp-up |
| 2031 | 500 | 0 | Full rate |
| 2032 | 500 | 0 | Full rate |
| 2033 | 500 | 0 | Full rate |
| **Total** | **1,900** | **50** | - |

---

## 4. COMPONENT SPECIFICATIONS

### 4.1 Scramjet Engine

| Specification | Value |
|--------------|-------|
| Type | Dual-mode scramjet |
| Fuel | JP-10 |
| Thrust (Mach 5) | 2,500 lbf |
| SFC | 1.2 lb/hr/lbf |
| Operating Mach | 4.0-6.0 |
| Combustor Temp | 4,500°F |
| Weight | 185 lb |
| Burn Time | 300+ sec |
| Start Altitude | 60,000 ft |

### 4.2 Thermal Protection System

| Component | Material | Max Temp |
|-----------|----------|----------|
| Nose Cone | C-C composite | 3,500°F |
| Leading Edges | CMC (SiC/SiC) | 3,000°F |
| Body Panels | Inconel 718 | 1,800°F |
| Aft Section | Titanium + ablative | 1,200°F |

### 4.3 MMW Seeker

| Specification | Value |
|--------------|-------|
| Frequency | Ka-band (35 GHz) |
| Range | 30 km |
| FOV | 10° x 10° |
| Resolution | 0.3 m |
| Target Types | Ships, vehicles, structures |
| ATR Database | 500+ target templates |

### 4.4 Swarm Datalink

| Specification | Value |
|--------------|-------|
| Frequency | UHF mesh |
| Range | 100 km (swarm-to-swarm) |
| Data Rate | 1 Mbps |
| Nodes | Up to 100 |
| Latency | < 50 ms |
| Jam Resistance | DSSS + freq hopping |

---

## 5. QUALITY CONTROL

### 5.1 Scramjet Engine Testing

| Test | Accept Criteria | Method |
|------|-----------------|--------|
| Hot Section NDT | Zero defects | X-ray, CT |
| Flow Calibration | ±2% from nominal | Flow bench |
| Ground Test | 5 sec at Mach 5 conditions | Test cell |
| Thermal Cycle | 10 cycles, no degradation | Oven |

### 5.2 Missile Acceptance

| Test | Criteria |
|------|----------|
| Weight/Balance | Within 2% |
| Functional | All BIT pass |
| Seeker | NETD < 30 mK, boresight < 1 mrad |
| Datalink | < 10^-5 BER |
| Environmental | -40 to +160°F, 8 Grms |

### 5.3 Lot Testing

- **Lot Size**: 50 missiles
- **Flight Test**: 2 per lot
- **Success Criteria**: Both hit target
- **Reject Criteria**: Root cause, 100% screening

---

## 6. SUPPLY CHAIN

### 6.1 Critical Materials

| Material | Annual Need | Supplier | Risk |
|----------|-------------|----------|------|
| SiC Fiber | 25,000 lb | COI Ceramics | High |
| JP-10 Fuel | 150,000 gal | DLA | Medium |
| Inconel 718 | 180,000 lb | ATI | Low |
| Titanium | 95,000 lb | TIMET | Low |
| Carbon-Carbon | 8,000 lb | Goodrich | High |

### 6.2 Key Suppliers

| Component | Supplier | Alternate |
|-----------|----------|-----------|
| Scramjet | Aerojet Rocketdyne | None (sole source) |
| Airframe | Lockheed Martin | Northrop (qualified) |
| Seeker | Raytheon | L3Harris (in work) |
| ATR Software | Anduril | Palantir (in work) |

### 6.3 Industrial Base Concerns

1. **Scramjet Production**: Only Aerojet Rocketdyne has production capability; recommend second source development ($500M investment)
2. **CMC Materials**: Limited domestic capacity; recommend DPA Title III investment
3. **JP-10 Fuel**: Single refinery; recommend strategic reserve

---

## 7. FACILITY REQUIREMENTS

### 7.1 Aerojet Rocketdyne (Scramjet)

| Area | Size | Purpose |
|------|------|---------|
| CMC Fabrication | 35,000 sq ft | Ceramic matrix composites |
| Machining | 25,000 sq ft | Metallic components |
| Assembly | 18,000 sq ft | Engine build |
| Test Cells | 3 cells | Ground qualification |

### 7.2 Lockheed Martin (Airframe)

| Area | Size | Purpose |
|------|------|---------|
| TPS Fabrication | 28,000 sq ft | Thermal protection |
| Structure Assembly | 45,000 sq ft | Airframe build |
| Avionics Integration | 15,000 sq ft | Systems |
| Final Assembly | 35,000 sq ft | Complete missile |
| Environmental Test | 12,000 sq ft | Qual/acceptance |

### 7.3 New Equipment Required

| Equipment | Quantity | Cost |
|-----------|----------|------|
| CVI Furnace | 2 | $8M each |
| Scramjet Test Cell | 1 | $45M |
| CMC Layup Machine | 4 | $2.5M each |
| 5-axis Mill (large) | 6 | $4M each |
| Thermal Vacuum Chamber | 2 | $3.5M each |

---

## 8. TESTING PROCEDURES

### 8.1 Development Test

| Phase | Tests | Duration |
|-------|-------|----------|
| Scramjet Ground | 50 burns | 18 months |
| Captive Carry | 15 flights | 6 months |
| Boost-to-Scramjet | 10 flights | 12 months |
| Full Mission | 15 flights | 12 months |
| Swarm Demo | 5 events (20 missiles) | 6 months |

### 8.2 Operational Test

| Test | Quantity | Success |
|------|----------|---------|
| Land Attack | 10 | 8/10 |
| Maritime | 8 | 6/8 |
| Swarm Attack | 3 (60 missiles) | 80% hit |
| Adverse Weather | 4 | 3/4 |

### 8.3 Production Acceptance

```
Acceptance Sequence (16 hours):
1. Receiving/Visual (1 hr)
2. Dimensional (2 hr)
3. Weight/Balance (1 hr)
4. Electrical/Continuity (2 hr)
5. Scramjet Cold Flow (1 hr)
6. Seeker Calibration (2 hr)
7. ATR Database Verify (1 hr)
8. Datalink Test (1 hr)
9. Environmental Screen (4 hr)
   - Thermal: -40 to +160°F (2 cycles)
   - Vibration: 8 Grms (30 min)
10. Final Inspection (1 hr)
```

---

## 9. COST BREAKDOWN

### 9.1 Development Costs

| Category | Cost |
|----------|------|
| Scramjet Development | $1.2B |
| Airframe/TPS | $480M |
| Guidance/Seeker | $320M |
| Swarm Software | $280M |
| Test & Evaluation | $520M |
| **Total Development** | **$2.8B** |

### 9.2 Production Costs

| Item | Unit Cost | Qty | Total |
|------|-----------|-----|-------|
| LOCUST Missile | $2.88M | 1,900 | $5,472M |
| Launch System | $24.3M | 50 | $1,215M |
| Spares (15%) | - | - | $1,003M |
| **Total Production** | - | - | **$7.69B** |

### 9.3 Total Program

| Category | Cost |
|----------|------|
| Development | $2.8B |
| Production | $7.69B |
| Program Mgmt | $0.51B |
| **Total** | **$11.0B** |

---

## 10. PRODUCTION TIMELINE

```
2026 Q1: Scramjet CDR
2026 Q4: First ground test
2027 Q2: Captive carry start
2027 Q4: First free flight

2028 Q2: EMD complete
2028 Q4: LRIP decision

2029 Q1: LRIP start (100/year)
2029 Q4: IOC

2030 Q2: Full rate decision
2030 Q4: 300/year production

2031-2033: Full rate (500/year)
2032 Q4: FOC
```

---

## 11. OPERATIONAL CONCEPT

### 11.1 Swarm Attack Sequence

```
T-0:    Launch command received
T+5s:   Booster burnout, scramjet start
T+15s:  Mach 5 achieved, cruise
T+180s: Swarm formation established
T+200s: Target area approach
T+210s: Swarm coordination (task allocation)
T+220s: Terminal attack begins
T+225s: Simultaneous impact (10+ missiles)
```

### 11.2 Swarm Coordination

| Mode | Description |
|------|-------------|
| Spread | Maximum coverage, single targets |
| Concentrate | Multiple missiles per target |
| Sequential | Suppress then strike |
| Adaptive | AI-directed reallocation |

### 11.3 Countermeasures

| Threat | Mitigation |
|--------|------------|
| SAM | Speed, low altitude terminal |
| CIWS | Saturation (>10 simultaneous) |
| EW/Jamming | INS backup, ATR |
| Decoys | Multi-sensor ATR |

---

## APPENDIX: RISK ASSESSMENT

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scramjet performance | Medium | High | Extensive ground test |
| TPS durability | Medium | High | Material qualification |
| Unit cost growth | High | Medium | Design-to-cost |
| Second source | Low | Medium | Qualification program |
| CMC supply | Medium | High | DPA investment |

---

**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Prepared By:** DOD System Proposal CAD
**Date:** 2026-01-02
