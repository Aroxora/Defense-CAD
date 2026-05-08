# SENTINEL - Manufacturing Specification

**System:** SENTINEL Distributed Passive Sensor Network
**Codename:** SENTINEL
**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Version:** 1.0
**Date:** 2026-01-02

---

## 1. SYSTEM OVERVIEW

### 1.1 Mission
Proliferated ground-based passive RF and acoustic sensors using TDOA/FDOA fusion to achieve 50m CEP tracking of aircraft and cruise missiles without emitting detectable signals.

### 1.2 Strategic Rationale
- Passive = undetectable, unjammable
- Low cost enables mass deployment
- Covert cueing for active shooters
- Survives first strike (distributed)
- Complements active radar networks

### 1.3 Key Performance Parameters
| Parameter | Requirement |
|-----------|-------------|
| Detection Range (ESM) | 400 km |
| Detection Range (Acoustic) | 50 km |
| Track Accuracy (fused) | 50 m CEP |
| Sensor Node Cost | < $1.5M |
| Nodes per Site | 4-8 |
| Data Latency | < 2 seconds |

---

## 2. BILL OF MATERIALS

### 2.1 Passive RF (ESM) Node

| Component | Unit Cost | Supplier |
|-----------|-----------|----------|
| Wideband Antenna Array | $185,000 | L3Harris |
| RF Front End | $245,000 | BAE Systems |
| Digital Receiver | $165,000 | Mercury Systems |
| Signal Processor | $285,000 | Leidos |
| Emitter Database | $85,000 | CACI |
| Timing System (GPS) | $45,000 | Trimble |
| Communications | $125,000 | L3Harris |
| Power System | $65,000 | Various |
| Shelter/Enclosure | $95,000 | HDT Global |
| Installation Kit | $45,000 | Various |
| **ESM Node Total** | **$1.34M** | - |

### 2.2 Acoustic Sensor Node

| Component | Unit Cost | Supplier |
|-----------|-----------|----------|
| Infrasound Microphone Array | $125,000 | PCB Piezotronics |
| Signal Conditioning | $45,000 | Bruel & Kjaer |
| Processing Unit | $85,000 | Custom |
| Weather Station | $28,000 | Vaisala |
| GPS Timing | $35,000 | Trimble |
| Communications | $65,000 | L3Harris |
| Power (solar/battery) | $42,000 | Various |
| Camouflaged Enclosure | $35,000 | Custom |
| **Acoustic Node Total** | **$460,000** | - |

### 2.3 Fusion Hub

| Component | Unit Cost | Supplier |
|-----------|-----------|----------|
| Server Rack | $185,000 | Dell |
| Fusion Processor | $420,000 | Custom |
| TDOA/FDOA Software | $285,000 | License |
| Database Server | $125,000 | HPE |
| Display System | $85,000 | Various |
| Network Equipment | $95,000 | Cisco |
| SATCOM Terminal | $380,000 | Viasat |
| Tactical Radio | $125,000 | L3Harris |
| S-788 Shelter | $280,000 | HDT Global |
| Generator | $145,000 | Caterpillar |
| **Fusion Hub Total** | **$2.125M** | - |

---

## 3. MANUFACTURING PROCESS

### 3.1 ESM Node Assembly

```
STAGE 1: Antenna Fabrication (Days 1-15)
├── Element fabrication
├── Array assembly
├── Radome integration
├── Pattern verification
└── Environmental sealing

STAGE 2: Electronics Integration (Days 16-35)
├── RF front end installation
├── Digital receiver mounting
├── Signal processor integration
├── Power distribution
├── Cooling system
└── EMI shielding

STAGE 3: Software/Configuration (Days 36-45)
├── Operating system load
├── Signal processing software
├── Emitter database installation
├── Network configuration
├── GPS synchronization
└── Calibration

STAGE 4: Test/Acceptance (Days 46-55)
├── RF performance verification
├── Direction finding accuracy
├── Emitter identification test
├── Environmental exposure
├── Network connectivity
└── Documentation
```

### 3.2 Acoustic Node Assembly

```
STAGE 1: Sensor Array (Days 1-10)
├── Microphone mounting
├── Pre-amplifier integration
├── Wind screen installation
├── Calibration
└── Weatherproofing

STAGE 2: Electronics (Days 11-20)
├── Signal conditioning
├── Processor installation
├── GPS receiver
├── Communications
├── Power system
└── Environmental enclosure

STAGE 3: Integration (Days 21-30)
├── System assembly
├── Software load
├── Calibration
├── Field test
└── Packaging
```

### 3.3 Production Quantities

| Item | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | Total |
|------|--------|--------|--------|--------|--------|-------|
| ESM Nodes | 40 | 80 | 80 | 80 | 40 | 320 |
| Acoustic Nodes | 60 | 120 | 120 | 120 | 60 | 480 |
| Fusion Hubs | 5 | 10 | 10 | 10 | 5 | 40 |

---

## 4. COMPONENT SPECIFICATIONS

### 4.1 ESM Sensor

| Specification | Value |
|--------------|-------|
| Frequency Range | 0.5-40 GHz |
| Sensitivity | -65 dBm |
| Dynamic Range | 70 dB |
| DF Accuracy | < 2° RMS |
| Pulse Width | 50 ns - CW |
| POI | > 99% (in band) |
| Identification | 95% (known emitters) |

### 4.2 Acoustic Sensor

| Specification | Value |
|--------------|-------|
| Frequency Range | 0.1-50 Hz (infrasound) |
| Sensitivity | 10 mPa |
| Array Aperture | 100 m |
| DF Accuracy | < 5° |
| Detection Range | 50 km (jet aircraft) |
| False Alarm Rate | < 1/hour |

### 4.3 Fusion Performance

| Specification | Value |
|--------------|-------|
| TDOA Accuracy | < 100 ns |
| FDOA Accuracy | < 1 Hz |
| Geolocation (3 nodes) | 500 m CEP |
| Geolocation (6+ nodes) | 50 m CEP |
| Track Update Rate | 1 Hz |
| Track Correlation | > 98% |

---

## 5. QUALITY CONTROL

### 5.1 ESM Node Testing

| Test | Criteria |
|------|----------|
| Sensitivity | < -65 dBm |
| DF Accuracy | < 2° (8 cardinal) |
| Frequency Coverage | 100% of range |
| Emitter ID | > 90% (test set) |
| Environmental | MIL-STD-810 |

### 5.2 Acoustic Node Testing

| Test | Criteria |
|------|----------|
| Sensitivity | Response to 10 mPa |
| Noise Floor | < 0.1 mPa |
| DF Accuracy | < 5° (3 sources) |
| Weather Immunity | 30 mph wind |
| Power Autonomy | 30 days solar |

### 5.3 Fusion Hub Testing

| Test | Criteria |
|------|----------|
| Latency | < 500 ms processing |
| Accuracy | < 50 m (6 node baseline) |
| Throughput | 100 tracks simultaneous |
| Availability | 99.9% |

---

## 6. SUPPLY CHAIN

### 6.1 Critical Components

| Component | Supplier | Lead Time |
|-----------|----------|-----------|
| Wideband Antenna | L3Harris | 6 months |
| Digital Receiver | Mercury | 4 months |
| Infrasound Mic | PCB Piezo | 3 months |
| Signal Processor | Leidos | 5 months |
| GPS Timing | Trimble | 2 months |

### 6.2 Government Furnished

| Item | Source |
|------|--------|
| Emitter Database | NSA/DIA |
| Tactical Radios | Army CECOM |
| Crypto | NSA |
| Satellite Access | DISA |

---

## 7. FACILITY REQUIREMENTS

### 7.1 Manufacturing Locations

| Facility | Location | Product |
|----------|----------|---------|
| L3Harris | Rochester, NY | ESM Nodes |
| BAE Systems | Nashua, NH | RF Front End |
| Custom Integrator | TBD | Acoustic Nodes |
| Leidos | Arlington, VA | Fusion Hub |

### 7.2 Test Facilities

| Facility | Purpose |
|----------|---------|
| Anechoic Chamber | ESM antenna patterns |
| RF Lab | Receiver verification |
| Acoustic Range | Sensor calibration |
| Integration Lab | System-level test |

---

## 8. COST BREAKDOWN

### 8.1 Development

| Category | Cost |
|----------|------|
| ESM Sensor Development | $180M |
| Acoustic Development | $65M |
| Fusion Algorithm | $120M |
| Integration/Test | $85M |
| **Total Development** | **$450M** |

### 8.2 Production (5-Year)

| Item | Unit | Qty | Total |
|------|------|-----|-------|
| ESM Node | $1.34M | 320 | $429M |
| Acoustic Node | $0.46M | 480 | $221M |
| Fusion Hub | $2.13M | 40 | $85M |
| Site Installation | $0.25M | 80 | $20M |
| Spares (15%) | - | - | $113M |
| **Total Production** | - | - | **$868M** |

### 8.3 Total Program

| Category | Cost |
|----------|------|
| Development | $450M |
| Production | $868M |
| Program Mgmt | $82M |
| **Total** | **$1.4B** |

---

## 9. DEPLOYMENT CONCEPT

### 9.1 Site Configuration

```
           ESM #1                    ESM #2
             │                         │
             │     ┌─────────┐        │
             └────►│ FUSION  │◄───────┘
                   │   HUB   │
             ┌────►│         │◄───────┐
             │     └─────────┘        │
           ESM #3        ▲          ESM #4
                         │
    ┌────────────────────┼────────────────────┐
    │          │         │         │          │
  ACO#1     ACO#2     ACO#3     ACO#4     ACO#5
```

### 9.2 Baseline Configuration

| Element | Quantity | Spacing |
|---------|----------|---------|
| ESM Nodes | 4 | 50-100 km |
| Acoustic Nodes | 6 | 20 km |
| Fusion Hub | 1 | Central |
| Total Coverage | - | 150 km radius |

### 9.3 Deployment Locations

| Region | Sites | Coverage |
|--------|-------|----------|
| First Island Chain | 20 | Taiwan Strait |
| Europe | 15 | Baltic/Poland |
| CENTCOM | 10 | Gulf region |
| CONUS | 5 | Training |

---

## 10. PRODUCTION TIMELINE

```
2026 Q1: PDR complete
2026 Q3: CDR complete
2026 Q4: First article ESM

2027 Q2: First article Acoustic
2027 Q4: First fusion hub

2028 Q1: IOC (5 sites)
2028 Q4: OT complete

2029-2030: Full production
2030 Q4: FOC (50 sites)
```

---

**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Prepared By:** DOD System Proposal CAD
**Date:** 2026-01-02
