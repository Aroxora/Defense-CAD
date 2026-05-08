# AEGIS ANYWHERE - Manufacturing Specification

**System:** AEGIS ANYWHERE Mobile Naval Air Defense
**Codename:** AEGIS_ANYWHERE
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Version:** 1.0
**Date:** 2026-01-02

---

## 1. SYSTEM OVERVIEW

### 1.1 Mission
Distributed AEGIS capability with mobile SPY-6 radars, Typhon launchers, and E-7 AWACS integration providing full CEC engage-on-remote with shoot-and-scoot survivability.

### 1.2 Strategic Rationale
- Extends AEGIS capability to ground-mobile platforms
- Survivable through mobility (30-minute displacement)
- Full CEC integration enables remote engagement
- Leverages mature Navy systems
- E-7 backup guidance maintains engagement if radar lost

### 1.3 Key Performance Parameters
| Parameter | Requirement |
|-----------|-------------|
| Radar Detection Range | 500 km (fighter) |
| SM-6 Range | 370 km |
| Tomahawk Range | 1,600 km |
| Displacement Time | < 30 minutes |
| Setup Time | < 45 minutes |
| CEC Latency | < 1 second |

---

## 2. BILL OF MATERIALS

### 2.1 Mobile SPY-6(V)2 Radar System

| Component | Unit Cost | Supplier |
|-----------|-----------|----------|
| SPY-6(V)2 Array (containerized) | $95M | Raytheon |
| Radar Control Cabinet | $12M | Raytheon |
| Signal/Data Processor | $18M | Raytheon |
| Power Amplifiers | $8.5M | Raytheon |
| Cooling System | $2.4M | Carrier |
| Prime Power (1.5MW) | $1.8M | Caterpillar |
| Transport Trailer (array) | $420K | Custom |
| Transport Trailer (equipment) | $280K | Custom |
| Prime Movers (3) | $1.65M | Oshkosh |
| Camouflage System | $185K | Saab |
| **SPY-6 Mobile Total** | **$140.2M** | - |

### 2.2 Typhon SM-6 Launcher Battery

| Component | Unit Cost | Supplier |
|-----------|-----------|----------|
| Mk 41 4-Cell Module | $8.5M | BAE Systems |
| Prime Mover (HEMTT) | $580K | Oshkosh |
| Launch Control Unit | $12.5M | Lockheed Martin |
| Power Generator | $185K | Caterpillar |
| Communications Suite | $2.2M | L3Harris |
| IBCS Integration Kit | $4.8M | Northrop Grumman |
| **Battery (4 launchers) Total** | **$54.8M** | - |

### 2.3 AEGIS Engagement Center (Mobile)

| Component | Unit Cost | Supplier |
|-----------|-----------|----------|
| Combat System Equipment | $45M | Lockheed Martin |
| Display Consoles (6) | $1.2M | Various |
| CEC Equipment | $8.5M | Raytheon |
| Communications Suite | $4.2M | L3Harris |
| Crypto Equipment | $850K | General Dynamics |
| S-788 Shelter (2) | $560K | HDT Global |
| Power/HVAC | $420K | Various |
| Vehicles | $380K | Oshkosh |
| **Engagement Center Total** | **$61.1M** | - |

### 2.4 SM-6 Block IB Missile

| Component | Unit Cost | Supplier |
|-----------|-----------|----------|
| Airframe/Sustainer | $485K | Raytheon |
| Mk 72 Booster | $165K | Aerojet |
| Guidance Section | $680K | Raytheon |
| Active Radar Seeker | $890K | Raytheon |
| Warhead | $125K | General Dynamics |
| Mk 104 Motor | $385K | Aerojet |
| Thermal Battery | $24K | EaglePicher |
| Canister | $95K | BAE Systems |
| Software | $185K | Raytheon |
| **SM-6 Total** | **$3.034M** | - |

### 2.5 Tomahawk Block V (Land Attack)

| Component | Unit Cost | Supplier |
|-----------|-----------|----------|
| Complete Round | $1.48M | Raytheon |

---

## 3. MANUFACTURING PROCESS

### 3.1 Mobile SPY-6 Integration

```
STAGE 1: Array Containerization (Weeks 1-16)
├── Radar Modular Assembly (RMA) installation
│   ├── 37 RMA modules per array
│   ├── Cooling manifolds
│   ├── Power distribution
│   └── Fiber interconnects
├── Container structural mods
├── Environmental control
├── Shock/vibration isolation
└── Transport interface

STAGE 2: Support Equipment (Weeks 17-28)
├── Radar control cabinet integration
├── Signal processor installation
├── Power system assembly
├── Cooling system integration
├── Generator packaging
└── Trailer fabrication

STAGE 3: System Integration (Weeks 29-40)
├── Array to cabinet connection
├── Cooling loop commissioning
├── Power system checkout
├── Software load
├── Calibration
└── Pattern verification

STAGE 4: Mobility Test (Weeks 41-48)
├── Transport trials
├── Setup/teardown drills
├── Road march test
├── Environmental exposure
└── Operational demonstration
```

### 3.2 Engagement Center Build

```
STAGE 1: Shelter Preparation (Weeks 1-8)
├── S-788 modifications
├── EMI shielding
├── HVAC installation
├── Power conditioning
├── Cable penetrations
└── TEMPEST certification

STAGE 2: Combat System (Weeks 9-20)
├── Console installation
├── Server racks
├── Network equipment
├── CEC integration
├── Display systems
└── Operator interfaces

STAGE 3: Communications (Weeks 21-28)
├── SATCOM terminal
├── Tactical radios
├── Data links
├── Crypto installation
├── Antenna systems
└── Testing

STAGE 4: Integration (Weeks 29-36)
├── System software load
├── Database initialization
├── Radar interface test
├── CEC verification
├── Full system exercise
└── Acceptance
```

### 3.3 Production Quantities (5-Year)

| Item | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | Total |
|------|--------|--------|--------|--------|--------|-------|
| Mobile SPY-6 | 2 | 4 | 4 | 4 | 2 | 16 |
| Typhon Battery | 4 | 8 | 8 | 8 | 4 | 32 |
| Engagement Center | 2 | 4 | 4 | 4 | 2 | 16 |
| SM-6 | 96 | 192 | 192 | 192 | 96 | 768 |
| Tomahawk | 64 | 128 | 128 | 128 | 64 | 512 |

---

## 4. COMPONENT SPECIFICATIONS

### 4.1 SPY-6(V)2 Radar

| Specification | Value |
|--------------|-------|
| Type | S-band AESA |
| Array Size | 4 m x 4 m (containerized) |
| Elements | ~5,000 T/R modules |
| Detection Range (fighter) | 500+ km |
| Detection Range (cruise missile) | 300+ km |
| Track Accuracy | 30 m CEP |
| Track Capacity | 1,000+ |
| Simultaneous Engagements | 30+ |
| Prime Power | 1.5 MW |
| Cooling | 400 tons |

### 4.2 CEC System

| Specification | Value |
|--------------|-------|
| Data Rate | 10 Mbps |
| Range | 200 km (LOS) |
| Latency | < 1 second |
| Track Sharing | Full composite |
| Engagement Mode | Launch-on-remote |
| Weapons Guidance | Active/semi-active |

### 4.3 IBCS Integration

| Specification | Value |
|--------------|-------|
| Track Sources | 12+ sensor types |
| Track Capacity | 1,200 |
| Engagement Zones | 48 |
| Latency | < 2 seconds |
| Datalinks | Link 16, CEC, IBCS |

---

## 5. QUALITY CONTROL

### 5.1 Radar Acceptance

| Test | Criteria |
|------|----------|
| Transmit Power | > 95% of spec |
| Receive Sensitivity | Per RMA spec |
| Pattern (sidelobes) | < -25 dB |
| MTBF | > 200 hours |
| Setup Time | < 45 minutes |

### 5.2 System Integration

| Test | Criteria |
|------|----------|
| CEC Connectivity | 100% track correlation |
| Engagement Sim | 10/10 simulated kills |
| Displacement | < 30 min teardown |
| Environmental | MIL-STD-810G |

### 5.3 Missile Acceptance

| Test | Criteria |
|------|----------|
| SM-6 ATP | Per Navy ATP |
| Tomahawk ATP | Per Navy ATP |
| Lot Test (1 per 24) | Flight success |

---

## 6. SUPPLY CHAIN

### 6.1 Critical Components

| Component | Supplier | Lead Time | Risk |
|-----------|----------|-----------|------|
| SPY-6 RMAs | Raytheon | 24 months | High |
| CEC Equipment | Raytheon | 18 months | Medium |
| Mk 41 VLS | BAE Systems | 12 months | Low |
| SM-6 Seeker | Raytheon | 18 months | Medium |
| IBCS Software | Northrop | 6 months | Low |

### 6.2 Integration Sites

| Facility | Product |
|----------|---------|
| Raytheon Andover | SPY-6 integration |
| BAE Minneapolis | Mk 41 VLS |
| Lockheed Martin | Engagement center |
| Northrop Huntsville | IBCS nodes |

---

## 7. COST BREAKDOWN

### 7.1 Development

| Category | Cost |
|----------|------|
| SPY-6 Mobilization | $480M |
| CEC Ground Integration | $220M |
| IBCS/AEGIS Integration | $180M |
| Test & Evaluation | $285M |
| **Total Development** | **$1.165B** |

### 7.2 Production (5-Year)

| Item | Unit | Qty | Total |
|------|------|-----|-------|
| Mobile SPY-6 | $140.2M | 16 | $2,243M |
| Typhon Battery | $54.8M | 32 | $1,754M |
| Engagement Ctr | $61.1M | 16 | $978M |
| SM-6 | $3.03M | 768 | $2,327M |
| Tomahawk | $1.48M | 512 | $758M |
| Spares (15%) | - | - | $1,209M |
| **Total Production** | - | - | **$9,269M** |

### 7.3 Total Program

| Category | Cost |
|----------|------|
| Development | $1.17B |
| Production | $9.27B |
| Program Mgmt | $0.68B |
| **Total** | **$11.12B** |

---

## 8. PRODUCTION TIMELINE

```
2025 Q1: PDR (SPY-6 mobile)
2025 Q3: CDR complete
2026 Q1: First SPY-6 mobile integration
2026 Q3: First engagement center

2027 Q1: IOC (1 site operational)
2027 Q2: CEC integration test
2027 Q4: OT complete

2028-2030: Full rate production
2029 Q4: FOC (8 sites operational)
```

---

## 9. OPERATIONAL CONCEPT

### 9.1 Site Configuration

```
                    ┌─────────────┐
                    │   E-7       │
                    │  AWACS      │◄── Backup guidance
                    └──────┬──────┘
                           │ CEC
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼────┐
   │  SPY-6  │       │ ENGAGEMENT│      │  SPY-6  │
   │ RADAR 1 │◄─────►│  CENTER   │◄────►│ RADAR 2 │
   └────┬────┘       └─────┬─────┘      └────┬────┘
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌────▼────┐
   │ TYPHON  │       │  TYPHON   │      │ TYPHON  │
   │BATTERY 1│       │ BATTERY 2 │      │BATTERY 3│
   └─────────┘       └───────────┘      └─────────┘
```

### 9.2 Engagement Modes

| Mode | Description |
|------|-------------|
| Autonomous | Local radar tracks, local engagement |
| Launch-on-Remote | E-7 tracks, local launch |
| Engage-on-Remote | E-7 tracks, E-7 guides |
| CEC Composite | Best track from any sensor |

### 9.3 Deployment Sites

| Location | Sites | Coverage |
|----------|-------|----------|
| Japan | 4 | East China Sea |
| Philippines | 4 | South China Sea |
| Guam | 2 | Central Pacific |
| Poland | 3 | Baltic/Eastern Europe |
| Gulf | 3 | Arabian Gulf |

---

## 10. SURVIVABILITY

### 10.1 Mobility Timeline

| Action | Time |
|--------|------|
| Shutdown | 5 min |
| Array stow | 10 min |
| Disconnect | 5 min |
| Load | 5 min |
| Depart | 5 min |
| **Total Teardown** | **30 min** |

### 10.2 Hardening

| Measure | Description |
|---------|-------------|
| Dispersal | 5-10 km between elements |
| Camouflage | Radar absorbing nets |
| Decoys | Inflatable SPY-6 decoys |
| Mobility | 3 pre-surveyed positions |
| EMCON | Passive mode capability |

---

**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Prepared By:** DOD System Proposal CAD
**Date:** 2026-01-02
