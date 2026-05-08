# B-21 RAIDER with LRSO - Manufacturing Specification

**System:** B-21 RAIDER with LRSO Strike System
**Codename:** B21_LRSO
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Version:** 1.0
**Date:** 2026-01-02

---

## 1. SYSTEM OVERVIEW

### 1.1 Mission
Penetrating stealth bomber with Long-Range Standoff (LRSO) cruise missiles enabling global conventional strike from CONUS sanctuary bases.

### 1.2 Strategic Rationale
- B-21 operates from CONUS (Whiteman, Dyess, Ellsworth) - 10,000+ km from threat
- LRSO range: 2,500+ km enables standoff launch
- B-21 combat radius: 5,000+ km
- Total strike reach: 7,500+ km from CONUS
- Stealth allows penetration if standoff fails
- Nuclear-capable provides strategic deterrent value
- 20 B-21s with 16 LRSO each = 320 missiles per wave

### 1.3 Key Performance Parameters
| Parameter | Requirement |
|-----------|-------------|
| B-21 Combat Radius | 5,000+ km |
| LRSO Range | 2,500+ km |
| Payload Capacity | 16 LRSO internal |
| RCS | < -40 dBsm |
| Cruise Speed | Mach 0.85 |
| Service Ceiling | 50,000+ ft |
| Time on Station | 12+ hours (with refueling) |

---

## 2. BILL OF MATERIALS

### 2.1 B-21 Raider Airframe (Per Aircraft)

| Item | Quantity | Est. Cost | Supplier |
|------|----------|-----------|----------|
| Center Fuselage Section | 1 | $85M | Northrop Grumman |
| Wing Assembly (pair) | 1 | $125M | Northrop Grumman |
| Aft Fuselage Section | 1 | $42M | Northrop Grumman |
| Weapons Bay Structure | 2 | $28M | Spirit AeroSystems |
| Landing Gear Assembly | 1 | $18M | Collins Aerospace |
| Inlet Ducts | 2 | $35M | Northrop Grumman |
| Exhaust System | 2 | $48M | Pratt & Whitney |
| Flight Control Surfaces | 8 | $22M | Northrop Grumman |
| Canopy Assembly | 1 | $8.5M | PPG Aerospace |
| **Airframe Subtotal** | - | **$411.5M** | - |

### 2.2 B-21 Propulsion System

| Item | Quantity | Est. Cost | Supplier |
|------|----------|-----------|----------|
| F135-PW-XXX Engine | 2 | $45M each | Pratt & Whitney |
| Engine Integration Kit | 2 | $8M | Northrop/P&W |
| Fuel System | 1 | $15M | Cobham |
| APU | 1 | $4.5M | Honeywell |
| **Propulsion Subtotal** | - | **$125.5M** | - |

### 2.3 B-21 Avionics/Mission Systems

| Item | Quantity | Est. Cost | Supplier |
|------|----------|-----------|----------|
| AN/APQ-181 Derivative Radar | 1 | $42M | Northrop Grumman |
| EW Suite (AN/ALQ-XXX) | 1 | $65M | BAE Systems |
| DAS IR System | 1 | $28M | Northrop Grumman |
| Mission Computer | 2 | $15M | Northrop Grumman |
| Communications Suite | 1 | $32M | Rockwell Collins |
| Navigation System | 1 | $18M | Honeywell |
| Stores Management System | 1 | $22M | Harris |
| Cockpit Displays | 1 | $12M | Collins Aerospace |
| Data Link Terminal | 1 | $8.5M | L3Harris |
| **Avionics Subtotal** | - | **$242.5M** | - |

### 2.4 B-21 Unit Cost Summary

| Category | Cost |
|----------|------|
| Airframe | $411.5M |
| Propulsion | $125.5M |
| Avionics | $242.5M |
| Integration/Test | $120M |
| **Unit Flyaway Cost** | **~$900M** |

### 2.5 LRSO Cruise Missile Components

| Component | Quantity | Unit Cost | Supplier |
|-----------|----------|-----------|----------|
| Airframe (LO composite) | 1 | $285,000 | Raytheon |
| F107-WR-XXX Turbofan | 1 | $245,000 | Williams International |
| Guidance Section (GPS/INS) | 1 | $420,000 | Raytheon |
| TERCOM/DSMAC | 1 | $285,000 | Raytheon |
| Terminal Seeker (IIR/MMW) | 1 | $385,000 | Raytheon |
| Two-Way Datalink | 1 | $165,000 | L3Harris |
| Warhead Section | 1 | $125,000 | General Dynamics |
| Nuclear Arming (conventional disabled) | 1 | $0 | N/A |
| Fuel System | 1 | $68,000 | Cobham |
| Flight Control System | 1 | $145,000 | Moog Inc |
| LO Coatings/Treatments | 1 | $185,000 | Northrop Grumman |
| Integration/Test | 1 | $195,000 | Raytheon |
| **LRSO Unit Total** | - | **$2.503M** | - |

---

## 3. MANUFACTURING PROCESS

### 3.1 B-21 Assembly (Northrop Grumman Palmdale, CA)

```
STAGE 1: Major Assembly (Months 1-12)
├── Center Fuselage
│   ├── Composite skin layup (automated fiber placement)
│   ├── Structural bonding
│   ├── Weapons bay integration
│   └── Systems installation
├── Wing Assembly
│   ├── Spar fabrication
│   ├── Skin panels (AFP)
│   ├── Fuel cell integration
│   └── Leading edge installation
└── Aft Fuselage
    ├── Engine bay structure
    ├── Exhaust integration
    └── Empennage

STAGE 2: Major Join (Months 13-16)
├── Wing-to-fuselage mate
├── Aft fuselage join
├── Final structural bond
├── Fuel system leak test
└── Structural proof load

STAGE 3: Systems Installation (Months 17-24)
├── Propulsion
│   ├── Engine installation
│   ├── Inlet duct mating
│   ├── Exhaust system
│   └── Engine runs
├── Avionics
│   ├── Radar installation
│   ├── EW suite
│   ├── Mission computers
│   └── Displays/controls
├── Flight Controls
│   ├── Actuator installation
│   ├── Surface rigging
│   └── System checkout
└── Weapons
    ├── Bay mechanism
    ├── Stores pylons
    └── Weapons integration

STAGE 4: Final Assembly (Months 25-30)
├── Canopy installation
├── Landing gear
├── LO coating application
├── Seam sealing
├── Final paint
└── Weight and balance

STAGE 5: Ground Test (Months 31-34)
├── Power-on testing
├── Avionics verification
├── Engine runs
├── EMI/EMC
├── RCS measurement
└── Taxi tests

STAGE 6: Flight Test (Months 35-38)
├── First flight
├── Envelope expansion
├── Systems verification
├── Weapons separation
└── Delivery preparation
```

### 3.2 LRSO Assembly (Raytheon Tucson, AZ)

```
STAGE 1: Airframe Fabrication (Days 1-25)
├── Composite fuselage
│   ├── Carbon fiber layup (autoclave)
│   ├── LO treatment integration
│   └── Inlet fabrication
├── Wing panels
│   ├── Fold mechanism
│   └── Control surfaces
└── Exhaust fairing

STAGE 2: Propulsion (Days 26-40)
├── Engine receiving
├── Inlet integration
├── Fuel system
├── Engine mounts
└── Exhaust tailoring

STAGE 3: Guidance/Navigation (Days 41-60)
├── GPS/INS installation
├── TERCOM database load
├── DSMAC correlation
├── Terminal seeker
│   ├── IIR detector
│   ├── MMW antenna
│   └── Boresight
└── Flight computer

STAGE 4: Final Assembly (Days 61-80)
├── Warhead mating
├── Datalink
├── Thermal battery
├── LO treatments
├── Final sealing
└── Weight/balance

STAGE 5: Acceptance (Days 81-95)
├── Functional test
├── Guidance calibration
├── Environmental screening
├── RCS verification (sample)
└── Packaging
```

### 3.3 Production Rates

| Item | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
|------|--------|--------|--------|--------|--------|
| B-21 Aircraft | 4 | 8 | 12 | 12 | 12 |
| LRSO Missiles | 100 | 200 | 300 | 300 | 300 |

---

## 4. COMPONENT SPECIFICATIONS

### 4.1 B-21 Raider Performance

| Specification | Value |
|--------------|-------|
| Wingspan | ~172 ft (estimated) |
| Length | ~69 ft (estimated) |
| Max Takeoff Weight | ~350,000 lb |
| Empty Weight | ~180,000 lb |
| Fuel Capacity | ~150,000 lb |
| Max Speed | Mach 0.95 |
| Service Ceiling | 50,000+ ft |
| Combat Radius | 5,000+ km |
| Range (unrefueled) | 6,000+ nm |
| Crew | 2 |

### 4.2 LRSO Missile Performance

| Specification | Value |
|--------------|-------|
| Length | 14 ft |
| Wingspan (deployed) | 10 ft |
| Weight | 2,500 lb |
| Range | 2,500+ km |
| Speed | Mach 0.85 subsonic |
| Altitude | 50-50,000 ft |
| CEP | < 3 m |
| RCS | < -30 dBsm |
| Warhead | 500 lb class |

### 4.3 AN/APQ-181 Derivative Radar

| Specification | Value |
|--------------|-------|
| Type | AESA, LPI |
| Frequency | Ku-band |
| Detection Range | 300+ km (fighter) |
| Track Capacity | 100+ targets |
| SAR Resolution | < 1 m |
| GMTI Capability | Yes |
| Modes | Air-to-air, air-to-ground, SAR, GMTI |

### 4.4 F107-WR-XXX Turbofan (LRSO)

| Specification | Value |
|--------------|-------|
| Thrust | 800 lbf |
| SFC | 0.60 lb/hr/lbf |
| Weight | 150 lb |
| Diameter | 12 in |
| Length | 32 in |
| Altitude Rating | 50,000 ft |
| Fuel | JP-8 |

---

## 5. QUALITY CONTROL

### 5.1 B-21 Critical Inspections

| Stage | Inspection | Method | Accept Criteria |
|-------|------------|--------|-----------------|
| Composite Layup | Void content | Ultrasonic | < 1% |
| Structural Bond | Bond strength | Lap shear | > 4,000 psi |
| LO Coating | Thickness | Eddy current | Per spec |
| RCS | Signature | Chamber test | < -40 dBsm |
| Systems | Functional | BIT/ATP | All pass |
| Final | Flight safety | Comprehensive | Airworthy |

### 5.2 LRSO Critical Inspections

| Stage | Inspection | Accept Criteria |
|-------|------------|-----------------|
| Airframe | NDT (100%) | Zero critical defects |
| Guidance | Alignment | < 0.3 mrad |
| Seeker | Performance | NETD < 20 mK |
| RCS | Sample test | < -30 dBsm |
| Engine | Performance | Per Williams spec |
| Final | ATP | All BIT pass |

### 5.3 Flight Test Requirements

**B-21:**
- First flight: 4 hours envelope expansion
- Flight test program: 1,500 hours total
- Weapons separation: 50+ events
- RCS validation: Multiple chamber sessions

**LRSO:**
- Captive carry: 20 flights
- Powered flight: 15 tests
- Terminal guidance: 10 live fire
- Lot acceptance: 1 per 50 missiles

---

## 6. SUPPLY CHAIN

### 6.1 B-21 Critical Suppliers

| Component | Supplier | Location | Lead Time |
|-----------|----------|----------|-----------|
| Engines | Pratt & Whitney | East Hartford, CT | 24 months |
| Radar | Northrop Grumman | Baltimore, MD | 18 months |
| EW Suite | BAE Systems | Nashua, NH | 18 months |
| Canopy | PPG Aerospace | Huntsville, AL | 12 months |
| Landing Gear | Collins | Troy, OH | 15 months |
| Carbon Fiber | Hexcel/Toray | Various | 6 months |

### 6.2 LRSO Critical Suppliers

| Component | Supplier | Location | Lead Time |
|-----------|----------|----------|-----------|
| Engine | Williams Int'l | Ogden, UT | 18 months |
| Guidance | Raytheon | Tucson, AZ | 12 months |
| Seeker | Raytheon | Tucson, AZ | 15 months |
| Warhead | General Dynamics | Garland, TX | 12 months |
| LO Materials | Northrop | Palmdale, CA | 9 months |

### 6.3 Security Requirements

| Classification | Requirement |
|----------------|-------------|
| Program | SAP (Special Access Program) |
| Facility | TS/SCI SCIF |
| Personnel | TS/SCI + SAP access |
| Transport | Armed escort, secure containers |
| Foreign Disclosure | NO FORN |

---

## 7. FACILITY REQUIREMENTS

### 7.1 Northrop Grumman Palmdale (B-21)

| Area | Size (sq ft) | Purpose | Classification |
|------|--------------|---------|----------------|
| Final Assembly | 180,000 | Aircraft build | SAP |
| Composite Fabrication | 85,000 | Structures | SAP |
| Avionics Integration | 35,000 | Systems | TS/SCI |
| LO Facility | 45,000 | Coatings | SAP |
| Paint/Finish | 25,000 | Final coating | SAP |
| Flight Test | 20,000 | Ground test | SAP |
| RCS Range | 150 acres | Signature test | SAP |

### 7.2 Raytheon Tucson (LRSO)

| Area | Size (sq ft) | Purpose | Classification |
|------|--------------|---------|----------------|
| Missile Assembly | 65,000 | Build | Secret |
| Clean Room | 18,000 | Guidance | TS/SCI |
| Engine Integration | 15,000 | Propulsion | Secret |
| Environmental Test | 12,000 | Qual/screen | Secret |
| LO Treatment | 8,000 | Coatings | SAP |
| ATP | 10,000 | Acceptance | Secret |

### 7.3 Capital Equipment (New)

| Equipment | Quantity | Cost | Location |
|-----------|----------|------|----------|
| AFP Machine (large) | 2 | $25M each | Palmdale |
| Autoclave (30' dia) | 1 | $18M | Palmdale |
| RCS Chamber (large) | 1 | $45M | Palmdale |
| LO Spray System | 4 | $3.5M each | Palmdale |
| 7-axis Mill | 3 | $8M each | Palmdale |
| IR Scene Projector | 2 | $4.5M each | Tucson |

---

## 8. TESTING PROCEDURES

### 8.1 B-21 Development Test

| Phase | Tests | Duration |
|-------|-------|----------|
| Ground Test | Structural, systems | 12 months |
| Flight Test (envelope) | 50 flights | 12 months |
| Flight Test (mission) | 100 flights | 18 months |
| Weapons Integration | 25 flights | 6 months |
| RCS Validation | 20 chamber sessions | 12 months |
| OT&E | 75 flights | 18 months |

### 8.2 LRSO Development Test

| Phase | Tests | Duration |
|-------|-------|----------|
| Component Qualification | All subsystems | 12 months |
| Captive Carry | 20 flights | 6 months |
| Free Flight (guidance) | 10 shots | 6 months |
| Free Flight (terminal) | 10 shots | 6 months |
| Warhead Lethality | 8 shots | 4 months |
| OT&E | 12 shots | 9 months |

### 8.3 Production Acceptance

**B-21 ATP (3 weeks):**
1. Systems power-up and BIT
2. Avionics functional test
3. Flight control checkout
4. Engine runs (ground)
5. Taxi test
6. Acceptance flight (4 hours)
7. Post-flight inspection
8. RCS spot check (sample)
9. Documentation review
10. Government acceptance

**LRSO ATP (12 hours):**
1. Visual/dimensional inspection
2. Electrical continuity
3. Guidance calibration
4. Seeker performance test
5. Engine simulation
6. Environmental screen (abbreviated)
7. Weight and balance
8. Packaging/shipping prep

---

## 9. INTEGRATION REQUIREMENTS

### 9.1 B-21 to LRSO Interface

| Interface | Protocol | Description |
|-----------|----------|-------------|
| Power | 270 VDC | Missile power until release |
| Data | MIL-STD-1760 | Targeting, BIT, status |
| Cooling | Conditioned air | Seeker cooldown |
| Release | Pneumatic ejector | 5g separation |
| Time Sync | PPS | GPS time transfer |

### 9.2 Mission Planning

| System | Interface | Function |
|--------|-----------|----------|
| AFMSS | SIPRNET | Route planning |
| JMPS | JWICS | Target data |
| PFPS | Local | Preflight load |
| Datalink | EHF SATCOM | In-flight update |

### 9.3 C2 Integration

| Network | Purpose | Classification |
|---------|---------|----------------|
| STRATCOM | Tasking | TS/SCI |
| ACC | Execution | Secret |
| Link 16 | Air picture | Secret |
| SATCOM | Beyond LOS | TS/SCI |

---

## 10. COST BREAKDOWN

### 10.1 B-21 Program Costs

| Category | Cost |
|----------|------|
| Development (RDT&E) | $23.5B (sunk) |
| EMD Aircraft (6) | $5.4B |
| Production (48 aircraft) | $43.2B |
| Military Construction | $2.1B |
| **Total B-21 Program** | **$74.2B** |

### 10.2 LRSO Program Costs

| Category | Cost |
|----------|------|
| Development | $2.8B |
| Production (1,200 missiles) | $3.6B |
| Spares (15%) | $540M |
| **Total LRSO Program** | **$6.94B** |

### 10.3 Combined System Cost (This Proposal)

| Item | Unit Cost | Quantity | Total |
|------|-----------|----------|-------|
| B-21 Aircraft | $900M | 20 | $18,000M |
| LRSO Missile | $2.5M | 500 | $1,250M |
| Integration | - | - | $280M |
| Spares (12%) | - | - | $2,300M |
| **Proposal Total** | - | - | **$21,830M** |

---

## 11. PRODUCTION TIMELINE

```
B-21:
2023 Q4: First flight (complete)
2025 Q2: LRIP decision
2026 Q1: First LRIP delivery
2027 Q2: IOC (initial squadron)
2028 Q4: FOC (full squadron)
2030: Full rate production

LRSO:
2024 Q1: EMD contract award
2026 Q3: First flight test
2027 Q4: LRIP start
2028 Q2: IOC
2029 Q4: FOC
2030: Full rate production (300/year)

Combined System:
2028 Q2: First B-21 + LRSO operational
2029 Q4: Full capability (20 B-21, 320 LRSO)
```

---

## 12. BASING AND OPERATIONS

### 12.1 Operating Bases

| Base | Location | Aircraft | Mission |
|------|----------|----------|---------|
| Whiteman AFB | Missouri | 10 | Primary strike |
| Dyess AFB | Texas | 6 | Secondary |
| Ellsworth AFB | S. Dakota | 4 | Training/reserve |

### 12.2 Sortie Generation

| Phase | Sorties/Day | Missiles |
|-------|-------------|----------|
| Surge (Day 1-3) | 10 | 160 |
| Sustained | 4 | 64 |
| Maximum Effort | 15 | 240 |

### 12.3 Logistics Requirements

| Item | Quantity |
|------|----------|
| LRSO War Reserve | 640 (4 loads) |
| JP-8 (per sortie) | 150,000 lb |
| Maintenance (per sortie) | 45 man-hours |
| Turnaround Time | 12 hours |

---

## APPENDIX A: SECURITY CLASSIFICATION GUIDE

| Information | Classification |
|-------------|----------------|
| B-21 existence | UNCLASSIFIED |
| B-21 performance | SECRET |
| B-21 RCS | TOP SECRET/SAP |
| LRSO existence | UNCLASSIFIED |
| LRSO guidance | SECRET |
| LRSO LO features | TOP SECRET/SAP |
| Combined operations | SECRET |

---

**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Prepared By:** DOD System Proposal CAD
**Date:** 2026-01-02
