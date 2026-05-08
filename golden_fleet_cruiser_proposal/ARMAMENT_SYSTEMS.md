# LSC-X Full Armament Systems Specification

**Classification: UNCLASSIFIED // CONCEPTUAL DESIGN**

## 1. Armament Overview

### 1.1 Weapons Summary

| Category | System | Quantity | Status |
|----------|--------|----------|--------|
| **VLS Missiles** | Mk 41 Strike-Length | 128 cells | Existing |
| | Mk 57 Peripheral | 32 cells | Existing |
| **BMD Interceptors** | THAAD-ER (Marinized) | 16 | **NEW DEVELOPMENT** |
| **Army Integration** | Containerized PrSM | 16 | **NEW INTEGRATION** |
| **Directed Energy** | 150 kW HELIOS Laser | 2 | Existing (scaled) |
| | 600 kW High-Energy Laser | 1 | **NEW DEVELOPMENT** |
| **Guns** | 155mm AGS (Modified) | 1 | Existing (modified) |
| | 57mm Mk 110 | 2 | Existing |
| | 30mm Mk 46 GWS | 4 | Existing |
| **CIWS** | Mk 15 Phalanx Block 1B | 2 | Existing |
| | SeaRAM | 2 | Existing |
| **Torpedoes** | Mk 32 SVTT | 2 (triple) | Existing |
| **Decoys** | Mk 36 SRBOC | 4 | Existing |
| | NULKA | 4 | Existing |
| | AN/SLQ-25 Nixie | 2 | Existing |

---

## 2. Vertical Launch Systems

### 2.1 Mk 41 VLS (128 Cells)

```
FORWARD VLS FARM (64 cells)
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ 01 │ 02 │ 03 │ 04 │ 05 │ 06 │ 07 │ 08 │  Module A1-A8
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 09 │ 10 │ 11 │ 12 │ 13 │ 14 │ 15 │ 16 │  Module B1-B8
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 17 │ 18 │ 19 │ 20 │ 21 │ 22 │ 23 │ 24 │  Module C1-C8
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 25 │ 26 │ 27 │ 28 │ 29 │ 30 │ 31 │ 32 │  Module D1-D8
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 33 │ 34 │ 35 │ 36 │ 37 │ 38 │ 39 │ 40 │  Module E1-E8
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 41 │ 42 │ 43 │ 44 │ 45 │ 46 │ 47 │ 48 │  Module F1-F8
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 49 │ 50 │ 51 │ 52 │ 53 │ 54 │ 55 │ 56 │  Module G1-G8
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 57 │ 58 │ 59 │ 60 │ 61 │ 62 │ 63 │ 64 │  Module H1-H8
└────┴────┴────┴────┴────┴────┴────┴────┘

AFT VLS FARM (64 cells) - Mirror layout
```

### 2.2 Mk 41 Loadout Options

| Configuration | AAW | BMD | Strike | ASW | Notes |
|---------------|-----|-----|--------|-----|-------|
| **Baseline** | 64 SM-6 | 16 SM-3 IIA | 32 TLAM | 16 VLA | Balanced |
| **Air Defense** | 96 SM-6 | 16 SM-3 IIA | 0 | 16 VLA | Carrier escort |
| **Strike** | 32 SM-6 | 8 SM-3 IIA | 72 TLAM | 16 VLA | Land attack |
| **ASW Heavy** | 48 SM-6 | 8 SM-3 IIA | 24 TLAM | 48 VLA | Sub hunting |

### 2.3 Mk 57 Peripheral VLS (32 Cells)

| Location | Cells | Primary Load |
|----------|-------|--------------|
| Port side (amidships) | 16 | SM-3 Block IIA |
| Starboard side (amidships) | 16 | SM-3 Block IIA / CPS |

**Mk 57 Advantages**:
- Larger cell volume (vs Mk 41)
- Peripheral mounting reduces magazine vulnerability
- Accommodates future hypersonic weapons

### 2.4 VLS Missile Specifications

| Missile | Length | Diameter | Weight | Range | Role |
|---------|--------|----------|--------|-------|------|
| SM-2 Block IIIC | 4.72 m | 343 mm | 708 kg | 170 km | Area AAW |
| SM-6 Block IA | 6.55 m | 533 mm | 1,500 kg | 370+ km | Extended AAW/ASuW |
| SM-3 Block IIA | 6.55 m | 533 mm | 1,500 kg | 2,500 km | BMD exo |
| TLAM Block V | 6.25 m | 518 mm | 1,300 kg | 1,600 km | Land attack |
| LRASM | 4.27 m | 533 mm | 1,020 kg | 930+ km | Anti-ship |
| VL-ASROC | 4.85 m | 343 mm | 635 kg | 28 km | ASW |
| ESSM Block 2 | 3.66 m | 254 mm | 280 kg | 50 km | Point defense (quad-pack) |

---

## 3. NEW SYSTEM: THAAD-ER Maritime (TEM)

### 3.1 Development Requirement

**Current Gap**: No sea-based terminal-phase BMD capability exists for endo-atmospheric intercepts of MRBMs/IRBMs above SM-6 engagement envelope.

### 3.2 TEM System Specifications

| Parameter | Land THAAD | TEM (Marinized) | Notes |
|-----------|------------|-----------------|-------|
| Interceptor | THAAD | THAAD-ER | Extended range variant |
| Launcher | M1075 PLS | Deck-mounted trainable | **NEW DESIGN** |
| Cells per launcher | 8 | 8 | Same canister |
| Launchers | N/A | 2 | 16 total interceptors |
| Radar | AN/TPY-2 | AN/TPY-2M | Marinized, ship power |
| Fire Control | THAAD FC | AEGIS integrated | **NEW INTEGRATION** |

### 3.3 TEM Launcher Design

```
                    THAAD-ER MARITIME LAUNCHER
                    ═══════════════════════════

     ┌─────────────────────────────────────────────────┐
     │  ╔═══════════════════════════════════════════╗  │
     │  ║  CANISTER 1  ║  CANISTER 2  ║  CANISTER 3 ║  │
     │  ╠═════════════╬═════════════╬═════════════╣  │
     │  ║  CANISTER 4  ║  CANISTER 5  ║  CANISTER 6 ║  │
     │  ╠═════════════╬═════════════╬═════════════╣  │
     │  ║  CANISTER 7  ║  CANISTER 8  ║   (SPARE)   ║  │
     │  ╚═══════════════════════════════════════════╝  │
     └─────────────────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │   ELEVATION DRIVE   │
              │   0° to 90°         │
              └──────────┬──────────┘
                         │
              ┌──────────┴──────────┐
              │   AZIMUTH RING      │
              │   360° rotation     │
              └──────────┬──────────┘
                         │
              ┌──────────┴──────────┐
              │   DECK FOUNDATION   │
              │   Shock isolated    │
              └─────────────────────┘
```

### 3.4 TEM Development Program

| Phase | Duration | Cost Est. | Deliverables |
|-------|----------|-----------|--------------|
| Phase 0: Study | 12 months | $50M | Feasibility, requirements |
| Phase 1: Design | 24 months | $300M | Detailed design, CDR |
| Phase 2: Prototype | 36 months | $800M | 2 launchers, integration |
| Phase 3: Test | 24 months | $400M | DT/OT, live fire |
| Phase 4: Production | 36 months | $200M/ship set | LRIP |
| **Total** | **~10 years** | **~$2B** | IOC |

### 3.5 THAAD-ER Interceptor

| Parameter | THAAD | THAAD-ER | Improvement |
|-----------|-------|----------|-------------|
| Range | 200 km | 350 km | +75% |
| Altitude | 150 km | 200 km | +33% |
| Velocity | Mach 8+ | Mach 10+ | +25% |
| Seeker | Single-color IR | Dual-color IR | Better discrimination |
| Propulsion | Single-stage | Extended burn | Longer powered flight |

---

## 4. NEW SYSTEM: Containerized Army Fires

### 4.1 PrSM Maritime Integration

**Concept**: Employ Army Precision Strike Missile (PrSM) from containerized launchers for long-range anti-ship and land attack.

### 4.2 Container Launcher System

```
     ISO 20' CONTAINER LAUNCHER (4x PrSM)
     ════════════════════════════════════

     ┌─────────────────────────────────────────────┐
     │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
     │  │ CELL 1  │ │ CELL 2  │ │ CELL 3  │ │ CELL 4  │  │
     │  │  PrSM   │ │  PrSM   │ │  PrSM   │ │  PrSM   │  │
     │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
     │  ════════════════════════════════════════════    │
     │       LAUNCH CONTROL UNIT    │    POWER UNIT     │
     └─────────────────────────────────────────────────┘
           │                              │
           └──── CANbus to Ship FCS ──────┘
```

### 4.3 PrSM Specifications

| Variant | Range | Seeker | Target Set |
|---------|-------|--------|------------|
| Increment 1 | 500 km | GPS/INS | Fixed land |
| Increment 2 | 500 km | GPS/INS + SAL | Moving land |
| Increment 3 | 500 km | GPS/INS + MMW | Land/maritime |
| **Increment 4** | **1,000+ km** | **Multi-mode** | **Anti-ship primary** |

### 4.4 Container Positions

| Location | Containers | Missiles | Notes |
|----------|------------|----------|-------|
| Aft flight deck | 2 | 8 | Removable for helo ops |
| Amidships (port) | 1 | 4 | Fixed position |
| Amidships (stbd) | 1 | 4 | Fixed position |
| **Total** | **4** | **16** | Reloadable pierside |

### 4.5 Integration Requirements

| Requirement | Solution | Status |
|-------------|----------|--------|
| Fire control link | AEGIS interface adapter | **NEW DEVELOPMENT** |
| Targeting data | Link 16 / CEC | Existing |
| Power | 480V ship power | Standard |
| Deck reinforcement | 40-ton rated pads | Hull modification |

---

## 5. NEW SYSTEM: 600 kW High-Energy Laser

### 5.1 System Overview

**Requirement**: Provide hard-kill capability against cruise missiles, UAV swarms, and fast attack craft at ranges exceeding current 150 kW systems.

### 5.2 Specifications

| Parameter | 150 kW HELIOS | 600 kW HEL | Notes |
|-----------|---------------|------------|-------|
| Output Power | 150 kW | 600 kW | 4x increase |
| Engagement Range (CM) | 3 km | 8 km | Hard kill |
| Engagement Range (UAV) | 5 km | 15 km | Hard kill |
| Engagement Range (FIAC) | 2 km | 5 km | Hard kill |
| Magazine Depth | Unlimited | Unlimited | Power limited |
| Slew Rate | 30°/s | 45°/s | Faster tracking |
| Beam Director | 30 cm | 50 cm | Larger aperture |

### 5.3 600 kW HEL Architecture

```
                    600 kW HIGH-ENERGY LASER SYSTEM
                    ════════════════════════════════

    ┌─────────────────────────────────────────────────────────┐
    │                    BEAM DIRECTOR                         │
    │              ┌─────────────────────┐                     │
    │              │   50cm PRIMARY      │                     │
    │              │   MIRROR            │◄──── Elevation ±85° │
    │              └─────────────────────┘                     │
    │                       │                                  │
    │              ┌────────┴────────┐                         │
    │              │  COUDE PATH     │◄──── Azimuth 360°       │
    │              └────────┬────────┘                         │
    └───────────────────────┼──────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    │ FIBER COMBINER │
                    │   (Spectral)   │
                    └───────┬───────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    ┌─────┴─────┐     ┌─────┴─────┐     ┌─────┴─────┐
    │ 200 kW    │     │ 200 kW    │     │ 200 kW    │
    │ SSL MODULE│     │ SSL MODULE│     │ SSL MODULE│
    └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
          │                 │                 │
    ┌─────┴─────────────────┴─────────────────┴─────┐
    │          THERMAL MANAGEMENT SYSTEM            │
    │          1.5 MW cooling capacity              │
    └───────────────────────┬───────────────────────┘
                            │
    ┌───────────────────────┴───────────────────────┐
    │           POWER CONDITIONING UNIT             │
    │    2 MW input → 600 kW optical output         │
    │           (30% wall-plug efficiency)          │
    └───────────────────────────────────────────────┘
```

### 5.4 Development Program

| Milestone | TRL | Date | Funding |
|-----------|-----|------|---------|
| Component Demo | 4 | 2024 | $100M |
| Subsystem Test | 5 | 2026 | $200M |
| System Integration | 6 | 2028 | $300M |
| Ship Integration | 7 | 2030 | $250M |
| IOT&E | 8 | 2032 | $150M |
| **IOC** | **9** | **2034** | - |
| **Total** | - | - | **$1B** |

---

## 6. Gun Systems

### 6.1 155mm Advanced Gun System (Modified)

| Parameter | DDG-1000 AGS | LSC-X AGS-M | Notes |
|-----------|--------------|-------------|-------|
| Caliber | 155mm/62 | 155mm/62 | Same barrel |
| Rate of Fire | 10 rpm | 10 rpm | Same |
| Range (LRLAP) | 154 km | Cancelled | - |
| Range (Excalibur N5) | 70 km | 70 km | GPS guided |
| Range (HVP) | 40 km | 40 km | Hypervelocity |
| Magazine | 600 rds | 400 rds | Reduced |
| Ammunition Handling | Automated | Automated | Same |

### 6.2 57mm Mk 110

| Parameter | Specification |
|-----------|---------------|
| Caliber | 57mm/70 |
| Rate of Fire | 220 rpm |
| Range (effective) | 8.5 km surface, 4 km air |
| Ammunition | Programmable 3P |
| Mount | Stealth cupola |
| Quantity | 2 (fwd, aft) |

### 6.3 30mm Mk 46 Gun Weapon System

| Parameter | Specification |
|-----------|---------------|
| Caliber | 30mm |
| Rate of Fire | 200 rpm |
| Range | 2.5 km |
| Stabilization | 2-axis |
| Sensor | EO/IR |
| Quantity | 4 (corners) |

---

## 7. Close-In Weapon Systems

### 7.1 Mk 15 Phalanx Block 1B

| Parameter | Specification |
|-----------|---------------|
| Caliber | 20mm |
| Rate of Fire | 4,500 rpm |
| Range | 1.5 km |
| Sensor | Ku-band radar + FLIR |
| Quantity | 2 |
| Location | Fwd superstructure, aft hangar roof |

### 7.2 SeaRAM

| Parameter | Specification |
|-----------|---------------|
| Missile | RAM Block 2 |
| Capacity | 11 missiles |
| Range | 10 km |
| Sensor | RF/IR dual-mode |
| Quantity | 2 |
| Location | Port/Stbd amidships |

### 7.3 CIWS Layered Defense

```
THREAT APPROACH →

│ 15 km │ 10 km │  5 km  │  2 km  │  1 km  │ 500m │
├───────┼───────┼────────┼────────┼────────┼──────┤
│       │       │        │        │        │      │
│  600 kW HEL   │        │        │        │      │ ← Cruise Missile
│       │ SeaRAM│        │        │        │      │
│       │       │ 150 kW │        │        │      │
│       │       │  HELIOS│ Phalanx│        │      │
│       │       │        │        │  30mm  │      │
│       │       │        │        │        │ Last │
│       │       │        │        │        │ Ditch│
```

---

## 8. Anti-Submarine Warfare

### 8.1 Torpedo Systems

| System | Quantity | Tubes | Torpedo |
|--------|----------|-------|---------|
| Mk 32 SVTT | 2 | 3 per side | Mk 54 Mod 1 |

### 8.2 Mk 54 Lightweight Torpedo

| Parameter | Specification |
|-----------|---------------|
| Length | 2.72 m |
| Diameter | 324 mm |
| Weight | 276 kg |
| Speed | 40+ knots |
| Range | 10+ km |
| Depth | 600+ m |
| Guidance | Active/passive acoustic |

### 8.3 VL-ASROC

| Parameter | Specification |
|-----------|---------------|
| Range | 28 km |
| Payload | Mk 54 torpedo |
| VLS Compatible | Mk 41 |
| Loadout | 16 (baseline) |

---

## 9. Countermeasures

### 9.1 Decoy Systems

| System | Type | Quantity | Coverage |
|--------|------|----------|----------|
| Mk 36 SRBOC | Chaff/flare | 4 x 6-tube | 360° |
| NULKA | Active decoy | 4 launchers | Anti-ship missile |
| AN/SLQ-25C Nixie | Towed torpedo decoy | 2 | Stern arc |

### 9.2 Electronic Warfare

| System | Function | Power |
|--------|----------|-------|
| AN/SLQ-32(V)7 | ESM/EA | 200 kW |
| SEWIP Block III | Advanced EA | 150 kW |
| AN/SLQ-59 | Torpedo defense | 50 kW |

---

## 10. Ammunition Storage

### 10.1 Magazine Layout

| Magazine | Location | Contents | Capacity |
|----------|----------|----------|----------|
| Forward VLS | Decks 2-4, FR 35-55 | Mk 41 missiles | 64 cells |
| Aft VLS | Decks 2-4, FR 155-175 | Mk 41 missiles | 64 cells |
| Peripheral VLS | Deck 2, amidships | Mk 57 missiles | 32 cells |
| THAAD Ready | Deck 1, aft | THAAD-ER | 16 rounds |
| Gun Magazine | Deck 4, FR 25-35 | 155mm projectiles | 400 rounds |
| 57mm Ready | Below mounts | 57mm rounds | 1,000 per gun |
| Small Arms | Deck 3, midships | 30mm, 20mm | 20,000 rounds |
| Torpedo | Deck 2, amidships | Mk 54 | 24 torpedoes |

### 10.2 Ammunition Weights

| Type | Unit Weight | Quantity | Total Weight |
|------|-------------|----------|--------------|
| SM-6 | 1,500 kg | 64 | 96,000 kg |
| SM-3 IIA | 1,500 kg | 32 | 48,000 kg |
| TLAM | 1,300 kg | 32 | 41,600 kg |
| ESSM (quad) | 1,120 kg | 16 packs | 17,920 kg |
| THAAD-ER | 900 kg | 16 | 14,400 kg |
| PrSM | 500 kg | 16 | 8,000 kg |
| 155mm | 47 kg | 400 | 18,800 kg |
| Misc | - | - | 50,000 kg |
| **Total** | - | - | **~295,000 kg** |

---

## 11. Fire Control Systems

### 11.1 AEGIS Baseline 12+

| Capability | Enhancement |
|------------|-------------|
| BMD | SM-3 IIA + THAAD integration |
| AAW | SM-6 dual-mode, ESSM Block 2 |
| ASuW | SM-6/LRASM integrated |
| Strike | TLAM Block V mission planning |
| DEW | Laser weapon integration |

### 11.2 Cooperative Engagement Capability (CEC)

| Link | Data Rate | Latency | Purpose |
|------|-----------|---------|---------|
| CEC | 100 Mbps | < 10 ms | Fire control quality tracks |
| Link 16 | 1 Mbps | < 100 ms | Tactical data |
| MADL (F-35) | TBD | < 50 ms | 5th gen integration |
| Link 22 | 12 Mbps | < 50 ms | Allied interop |

---

## 12. Sensor Integration for Weapons

### 12.1 Primary Sensors

| Sensor | Type | Role | Weapons Supported |
|--------|------|------|-------------------|
| AN/SPY-7(V)1 | S-band AESA | Volume search, BMD | SM-6, SM-3, ESSM |
| AN/TPY-2M | X-band | BMD discrimination | THAAD-ER |
| AN/SPQ-9B | X-band | Horizon search | SM-6, guns |
| AN/SQQ-89 | Hull/towed sonar | ASW | VL-ASROC, Mk 54 |
| AN/SLQ-32(V)7 | ESM | Passive targeting | LRASM, SM-6 |

### 12.2 Fire Control Radar

| Radar | Band | Function |
|-------|------|----------|
| AN/SPG-62 | X-band | SM-2 terminal illumination |
| AMDR-X | X-band | Multi-function FC |

---

## 13. New Systems Development Summary

| System | Development Cost | Timeline | Risk |
|--------|------------------|----------|------|
| THAAD-ER Maritime | $2.0B | 10 years | Medium |
| 600 kW HEL | $1.0B | 10 years | Medium-High |
| PrSM Maritime Integration | $200M | 3 years | Low |
| AEGIS-THAAD Integration | $500M | 5 years | Medium |
| AGS-M Modification | $100M | 2 years | Low |
| **Total New Development** | **$3.8B** | - | - |

---

## 14. Combat System Weight/Power Summary

| System | Weight (kg) | Power (kW) |
|--------|-------------|------------|
| Mk 41 VLS (128) | 180,000 | 200 |
| Mk 57 VLS (32) | 65,000 | 100 |
| THAAD-ER Launcher (2) | 45,000 | 150 |
| PrSM Containers (4) | 32,000 | 50 |
| 600 kW HEL | 35,000 | 2,000 |
| 150 kW HELIOS (2) | 22,000 | 1,000 |
| 155mm AGS-M | 95,000 | 100 |
| 57mm Mk 110 (2) | 14,000 | 50 |
| 30mm GWS (4) | 6,000 | 40 |
| Phalanx (2) | 12,000 | 80 |
| SeaRAM (2) | 12,000 | 20 |
| Mk 32 SVTT (2) | 1,500 | 10 |
| Decoys/EW | 8,000 | 400 |
| Ammunition | 295,000 | - |
| Fire Control | 25,000 | 500 |
| Cabling/Support | 40,000 | - |
| **Total** | **~890,000 kg** | **~4,700 kW** |

---

**Classification: UNCLASSIFIED // CONCEPTUAL DESIGN**
