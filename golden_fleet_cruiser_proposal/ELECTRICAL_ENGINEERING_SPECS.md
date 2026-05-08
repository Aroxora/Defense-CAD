# LSC-X Electrical Engineering Specifications

**Classification: UNCLASSIFIED // CONCEPTUAL DESIGN**

## Power Generation Overview

### Total Installed Capacity

| Source | Rating | Quantity | Total |
|--------|--------|----------|-------|
| LM2500+G4 GTG | 25 MW | 4 | 100 MW |
| Emergency Diesel Gen | 4 MW | 4 | 16 MW |
| **Total Generation** | - | - | **116 MW** |

### Power Budget (Maximum Demand)

| Consumer | Power (MW) | Priority |
|----------|------------|----------|
| Propulsion | 70 | 1 |
| Combat Systems | 30 | 1 |
| Ship Service | 12 | 2 |
| HVAC | 4 | 2 |
| **Total Demand** | **116** | - |

---

## Distribution Architecture

### Medium Voltage System (4160V, 60 Hz)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RING BUS TOPOLOGY                                  │
│                                                                              │
│     GTG #1 ──┬── SWBD 1 ══════════════════════════════════ SWBD 2 ──┬── GTG #2     │
│              │                                                       │              │
│              │     ╔═══════════════════════════════════════════╗     │              │
│              │     ║        CROSS-CONNECT BUS                  ║     │              │
│              │     ╚═══════════════════════════════════════════╝     │              │
│              │                                                       │              │
│     GTG #3 ──┴── SWBD 3 ══════════════════════════════════ SWBD 4 ──┴── GTG #4     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

Zone Electrical Distribution:
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ ZONE 1  │  │ ZONE 2  │  │ ZONE 3  │  │ ZONE 4  │  │ ZONE 5  │
│ FWD     │  │ FWD-MID │  │ MIDSHIP │  │ AFT-MID │  │ AFT     │
│ VLS     │  │ BRIDGE  │  │ CIC     │  │ VLS     │  │ HANGAR  │
└─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘
```

### Low Voltage System (450V, 60 Hz)

| Transformer | Rating | Location | Loads |
|-------------|--------|----------|-------|
| T1 | 3 MVA | Zone 1 | Forward VLS, anchor windlass |
| T2 | 2 MVA | Zone 2 | Bridge, navigation |
| T3 | 4 MVA | Zone 3 | CIC, radar power supplies |
| T4 | 3 MVA | Zone 4 | Aft VLS, missile handling |
| T5 | 2 MVA | Zone 5 | Flight deck, hangar |

### Ship Service Distribution (120/208V, 60 Hz)

| Panel | Load (kW) | Purpose |
|-------|-----------|---------|
| Lighting | 400 | Ship-wide illumination |
| Receptacles | 200 | General use |
| Electronics | 600 | Non-combat systems |
| Galley | 300 | Food service |
| Laundry | 150 | Crew services |

---

## Combat Systems Power

### Radar Power Requirements

| System | Peak Power | Average Power | Voltage | Notes |
|--------|------------|---------------|---------|-------|
| AN/SPY-7(V)1 | 8 MW | 6 MW | 4160V | Dual-face AESA |
| AN/TPY-2 (marinized) | 800 kW | 600 kW | 480V | X-band BMD |
| AN/SPQ-9B | 150 kW | 100 kW | 450V | Horizon search |
| AN/SPS-73 | 25 kW | 20 kW | 450V | Navigation |

### Directed Energy Weapons

| System | Electrical Input | Efficiency | Cooling Load |
|--------|------------------|------------|--------------|
| 150 kW Laser #1 | 500 kW | 30% | 350 kW thermal |
| 150 kW Laser #2 | 500 kW | 30% | 350 kW thermal |
| Power Conditioning | 100 kW | 95% | 5 kW thermal |
| **Total DEW** | **1.1 MW** | - | **705 kW** |

### EW Systems

| System | Power | Notes |
|--------|-------|-------|
| AN/SLQ-32(V)7 | 200 kW | ESM/EA suite |
| SEWIP Block III | 150 kW | Upgraded EA |
| Decoy Launchers | 50 kW | NULKA, chaff |
| **Total EW** | **400 kW** | - |

---

## Power Quality Requirements

### Voltage Specifications

| Parameter | Requirement | Notes |
|-----------|-------------|-------|
| Nominal Voltage | 4160V ± 5% | Medium voltage |
| Frequency | 60 Hz ± 0.5% | Under all loads |
| Voltage Unbalance | < 3% | Phase-to-phase |
| THD (voltage) | < 5% | Total harmonic distortion |
| THD (current) | < 8% | Individual harmonics < 5% |

### Transient Limits

| Event | Limit | Recovery |
|-------|-------|----------|
| Load Step (10%) | ± 10% voltage | 1.5 seconds |
| Load Step (25%) | ± 15% voltage | 3.0 seconds |
| Load Rejection | +20% voltage | 2.0 seconds |
| Frequency Deviation | ± 4% | 5.0 seconds |

---

## Energy Storage Systems

### Pulse Power Capacitor Banks

| System | Energy | Purpose | Location |
|--------|--------|---------|----------|
| SPY-7 Pulse Forming | 50 MJ | Radar pulse shaping | Deck 2, Zone 3 |
| DEW Capacitor Bank | 100 MJ | Laser power buffer | Deck 3, Zone 4 |
| EW Jammer Bank | 20 MJ | EA pulse power | Deck 2, Zone 3 |

### Battery Systems (UPS)

| System | Capacity | Purpose | Runtime |
|--------|----------|---------|---------|
| CIC UPS | 500 kWh | Combat continuity | 30 min |
| Navigation UPS | 100 kWh | Safe navigation | 60 min |
| Comms UPS | 200 kWh | Communications | 45 min |
| Emergency Lighting | 50 kWh | Egress | 120 min |

---

## Grounding and EMI/EMC

### Grounding System

| Type | Resistance | Purpose |
|------|------------|---------|
| Hull Ground | < 1 Ω | Primary reference |
| Signal Ground | Isolated | Electronics protection |
| RF Ground | < 0.1 Ω | Antenna/radar systems |
| Lightning Protection | < 10 Ω | Weather protection |

### EMI/EMC Requirements (MIL-STD-461G)

| Emission | Limit | Test |
|----------|-------|------|
| CE102 | Class A | Conducted, 10 kHz - 10 MHz |
| RE102 | Class A | Radiated, 10 kHz - 18 GHz |
| CS101 | Class A | Conducted susceptibility |
| RS103 | Class A | Radiated susceptibility |

### Electromagnetic Compatibility Zones

| Zone | Shielding | Systems |
|------|-----------|---------|
| Zone A | > 80 dB | SPY-7 antenna room |
| Zone B | > 60 dB | CIC, electronics |
| Zone C | > 40 dB | General ship areas |

---

## Cabling and Wiring

### Cable Types

| Application | Type | Rating | Standard |
|-------------|------|--------|----------|
| Power (MV) | XLPE/EPR | 5/8 kV | IEEE 1580 |
| Power (LV) | XLPE | 600V | MIL-C-24640 |
| Control | Shielded twisted pair | 300V | MIL-C-24643 |
| Fiber Optic | Single-mode | N/A | MIL-PRF-85045 |
| Coaxial | RG-214 | 50Ω | MIL-C-17 |

### Cable Routing

| Route | Length (km) | Weight (tons) |
|-------|-------------|---------------|
| Power Cables | 45 | 180 |
| Control Cables | 120 | 95 |
| Fiber Optic | 80 | 8 |
| Coaxial | 25 | 15 |
| **Total** | **270** | **298** |

---

## Power Conversion Equipment

### Motor Drives (Variable Frequency)

| Application | Rating | Type | Efficiency |
|-------------|--------|------|------------|
| Propulsion VFD | 35 MW x 2 | PWM inverter | 98% |
| Pump Motors | 500 kW | AFE drive | 96% |
| Fan Motors | 200 kW | Standard VFD | 95% |
| Crane Motors | 100 kW | Regenerative | 94% |

### DC Power Systems

| System | Voltage | Power | Purpose |
|--------|---------|-------|---------|
| Combat Systems DC | 270 VDC | 2 MW | Radar exciters |
| Electronics DC | 28 VDC | 500 kW | Legacy systems |
| Emergency DC | 24 VDC | 100 kW | Backup systems |

---

## Protection and Control

### Protective Devices

| Level | Device | Setting | Purpose |
|-------|--------|---------|---------|
| Generator | 87G, 40, 32 | Per USCG | Differential, loss of field |
| Bus | 50/51, 27/59 | Coordinated | Over/under voltage |
| Feeder | 50/51 | Inverse time | Overcurrent |
| Motor | 49, 50 | Motor HP | Thermal, instantaneous |

### Automation and Control

| System | Protocol | Notes |
|--------|----------|-------|
| Power Management | IEC 61850 | GOOSE messaging |
| Load Shedding | Automatic | < 100 ms response |
| Generator Sync | Auto-sync | Voltage, frequency, phase |
| Fault Isolation | Zone selective | Minimize outage |

---

## Survivability Features

### Battle Short Capability

| System | Normal | Battle Short |
|--------|--------|--------------|
| Generator Trip | Enabled | Bypassed |
| Thermal Limits | Enforced | 150% for 15 min |
| Load Shedding | Automatic | Manual only |
| Fault Isolation | Coordinated | Fast trip |

### Damage Control Electrical

| Feature | Capability |
|---------|------------|
| Split-plant Operation | Full power on 2 GTGs |
| Zone Isolation | Any 2 adjacent zones |
| Emergency Power Transfer | < 30 seconds |
| Vital Load Priority | Automated load shed |

---

## Cooling Systems for Electronics

### Liquid Cooling

| System | Heat Load | Coolant | Flow Rate |
|--------|-----------|---------|-----------|
| SPY-7 Transmitters | 2 MW | PAO | 1000 L/min |
| AN/TPY-2 | 200 kW | Glycol/water | 200 L/min |
| Laser Systems | 700 kW | Deionized water | 500 L/min |

### Air Cooling

| Space | Heat Load | Supply Temp | Return Temp |
|-------|-----------|-------------|-------------|
| CIC | 400 kW | 15°C | 24°C |
| Radar Equipment | 200 kW | 12°C | 22°C |
| Computer Room | 300 kW | 14°C | 23°C |

---

## Installation Standards

### Workmanship Standards

- NAVSEA S9074-AS-GIB-010/278 (Welding)
- NAVSEA T9074-AD-GIB-010/1688 (Fabrication)
- MIL-STD-2003 (Electric Plant Installation)
- MIL-STD-1399 (Interface Standard)

### Testing Requirements

| Test | Standard | When |
|------|----------|------|
| Factory Acceptance | MIL-STD-1399 | Pre-delivery |
| Dock Trials | NAVSEA | Post-installation |
| Sea Trials | INSURV | Acceptance |
| Full Power | NAVSEA | Final acceptance |

---

**Classification: UNCLASSIFIED // CONCEPTUAL DESIGN**
