# LSC-X Mechanical Engineering Specifications

**Classification: UNCLASSIFIED // CONCEPTUAL DESIGN**

## Hull Structure

### General Arrangement

| Section | Frame Numbers | Function |
|---------|---------------|----------|
| Bow | 0-30 | Sonar dome, anchor handling |
| Forward | 30-80 | Mk 41 VLS (64 cells), crew quarters |
| Midships | 80-140 | Propulsion, power generation, combat systems |
| Aft | 140-190 | Mk 41 VLS (64 cells), Mk 57 VLS (32 cells), hangar |
| Stern | 190-210 | Flight deck, THAAD launchers, PrSM containers |

### Structural Design

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Hull Material | HY-100 steel | Yield strength 100 ksi |
| Superstructure | Aluminum alloy 5456 | Weight savings |
| Deck Plating | 12-20 mm HY-80 | Mission-dependent |
| Frame Spacing | 600 mm | Standard naval practice |
| Longitudinal Framing | Yes | Improved hogging/sagging resistance |
| Double Bottom | Full length | Tank top at 2.5m |
| Collision Bulkhead | Frame 15 | 5% LOA from bow |
| Watertight Subdivisions | 14 compartments | 2-compartment standard |

### Stability Requirements

| Condition | Requirement | LSC-X Value |
|-----------|-------------|-------------|
| GM (metacentric height) | > 1.0 m | 1.8 m |
| GZ_max | > 0.20 m | 0.45 m |
| Range of stability | > 70° | 85° |
| Heel at max wind | < 16° | 12° |

---

## Propulsion System

### Prime Movers

| Component | Specification | Quantity |
|-----------|---------------|----------|
| Gas Turbine | GE LM2500+G4 | 4 |
| Power Output (each) | 25.2 MW | - |
| Thermal Efficiency | 37% | ISO conditions |
| Fuel Consumption | 0.211 kg/kWh | Full power |
| Inlet Air Temperature | -40°C to +45°C | Operating range |

### Integrated Power System (IPS)

```
                    ┌─────────────────────────────────────────────────────┐
                    │              MAIN SWITCHBOARD (4160V)               │
                    └─────────────────────────────────────────────────────┘
                           │         │         │         │
                    ┌──────┴──┐ ┌────┴────┐ ┌──┴──────┐ ┌┴──────────┐
                    │ GTG #1  │ │ GTG #2  │ │ GTG #3  │ │  GTG #4   │
                    │ 25 MW   │ │ 25 MW   │ │ 25 MW   │ │  25 MW    │
                    └─────────┘ └─────────┘ └─────────┘ └───────────┘
                           │         │         │         │
                    ┌──────┴─────────┴─────────┴─────────┴──────────┐
                    │           POWER MANAGEMENT SYSTEM             │
                    │         (Load shedding, fault isolation)       │
                    └───────────────────────────────────────────────┘
                           │                   │                   │
              ┌────────────┴───┐     ┌────────┴────────┐  ┌───────┴───────┐
              │   PROPULSION   │     │  SHIP SERVICE   │  │ COMBAT SYSTEMS│
              │    70 MW       │     │     16 MW       │  │    30 MW      │
              └────────────────┘     └─────────────────┘  └───────────────┘
                     │                      │                    │
              ┌──────┴──────┐        ┌──────┴──────┐      ┌──────┴──────┐
              │  AFT AWJ-21 │        │ 450V SWBD   │      │ SPY-7 RADAR │
              │  35 MW      │        │ Distribution│      │ 6 MW        │
              └─────────────┘        └─────────────┘      └─────────────┘
              ┌─────────────┐                             ┌─────────────┐
              │  FWD AWJ-21 │                             │ AN/TPY-2    │
              │  35 MW      │                             │ 0.6 MW      │
              └─────────────┘                             └─────────────┘
                                                          ┌─────────────┐
                                                          │ 150kW LASER │
                                                          │ x2 = 0.3 MW │
                                                          └─────────────┘
```

### Propulsors

| Component | Specification | Notes |
|-----------|---------------|-------|
| Type | Advanced Water Jet (AWJ-21) | Reduced acoustic signature |
| Quantity | 2 | Port and starboard |
| Power Rating | 35 MW each | 70 MW total |
| Design Speed | 28 knots | Sustained |
| Maximum Speed | 32 knots | Sprint, limited duration |
| Reversing Capability | Yes | Bucket-type reverser |

### Auxiliary Propulsion

| System | Specification | Purpose |
|--------|---------------|---------|
| Bow Thruster | 3 MW electric | Harbor maneuvering |
| Stern Thruster | 2 MW electric | Precision positioning |
| Emergency Propulsion | Diesel-direct | 8 knots capability |

---

## Mechanical Systems

### HVAC System

| Zone | Supply (m³/min) | Temperature Range | Humidity |
|------|-----------------|-------------------|----------|
| Combat Information Center | 1500 | 20-24°C | 45-55% |
| Machinery Spaces | 3000 | 15-35°C | N/A |
| Crew Quarters | 2000 | 21-25°C | 40-60% |
| Magazine | 800 | 10-21°C | < 50% |
| Electronics Rooms | 1200 | 18-22°C | 45-55% |

### Fuel System

| Parameter | Value | Notes |
|-----------|-------|-------|
| Fuel Type | F-76 / DFM | NATO standard |
| Total Capacity | 4,200 m³ | ~3,500 tons |
| Daily Consumption (cruise) | 85 tons/day | 18 knots |
| Daily Consumption (max) | 280 tons/day | 28 knots |
| Endurance | 8,000 nm | At 18 knots |
| RAS Capability | Yes | Dual-station |

### Fresh Water System

| System | Capacity | Notes |
|--------|----------|-------|
| Storage Tanks | 400 m³ | 10 days potable |
| Distillation Plants | 2 x 100 m³/day | Vapor compression |
| Reverse Osmosis | 2 x 150 m³/day | Primary production |

---

## Deck Machinery

### Anchor Handling

| Component | Specification |
|-----------|---------------|
| Anchor Type | Stockless, high-holding-power |
| Anchor Weight | 12,000 kg each |
| Chain Size | 76 mm stud-link |
| Chain Length | 14 shackles (385 m) |
| Windlass | Electric-hydraulic, 25 ton |

### Weapons Handling

| System | Capacity | Purpose |
|--------|----------|---------|
| Mk 41 Strikedown | 8 missiles/hour | Forward magazines |
| Mk 57 Strikedown | 4 missiles/hour | Aft magazines |
| THAAD Reload Crane | 15 ton SWL | Pierside reload |
| PrSM Container Crane | 25 ton SWL | Containerized reload |

### Aviation Facilities

| Component | Specification |
|-----------|---------------|
| Flight Deck | 32m x 20m |
| Hangar | 24m x 18m x 6.5m |
| Aircraft Capacity | 2 x MH-60R/S |
| RAST System | Yes |
| FLIR | Yes |
| JP-5 Storage | 200 m³ |

---

## Shock and Vibration

### Shock Qualification

| System Category | Grade | Requirement |
|-----------------|-------|-------------|
| Combat Systems | A | Full shock qualification |
| Propulsion | A | Full shock qualification |
| Hotel Systems | B | Essential services only |

### Vibration Limits

| Location | Limit (mm/s) | Frequency Range |
|----------|--------------|-----------------|
| CIC | 2.0 | 1-80 Hz |
| Crew Quarters | 4.0 | 1-80 Hz |
| Machinery Spaces | 18.0 | 1-80 Hz |

---

## Weight Summary

| Group | Weight (tons) | % of Full Load |
|-------|---------------|----------------|
| Group 1 - Hull Structure | 5,200 | 22.6% |
| Group 2 - Propulsion | 2,800 | 12.2% |
| Group 3 - Electric Plant | 1,100 | 4.8% |
| Group 4 - Command/Surveillance | 850 | 3.7% |
| Group 5 - Auxiliary Systems | 1,600 | 7.0% |
| Group 6 - Outfit/Furnishings | 900 | 3.9% |
| Group 7 - Armament | 2,400 | 10.4% |
| Loads (fuel, water, stores) | 5,800 | 25.2% |
| Margins | 2,350 | 10.2% |
| **Full Load Displacement** | **23,000** | **100%** |

---

## Manufacturing Considerations

### Critical Path Items

| Item | Lead Time | Supplier Base |
|------|-----------|---------------|
| LM2500+G4 Gas Turbines | 36 months | GE Marine |
| AWJ-21 Waterjets | 30 months | Rolls-Royce |
| HY-100 Steel Plate | 18 months | Domestic mills |
| Reduction Gears | 24 months | Philadelphia Gear |
| Main Switchboards | 20 months | L3Harris |

### Construction Sequence

1. **Block Construction** (24 months)
   - Fabricate 45 super-blocks at weight < 500 tons
   - Maximum lift capacity: 600 tons

2. **Block Assembly** (12 months)
   - Grand blocks formed from 4-6 super-blocks
   - Hull erected on building ways

3. **Integration** (18 months)
   - Combat systems installation
   - Propulsion alignment
   - Cable runs and piping

4. **Test and Trials** (12 months)
   - Builder's trials
   - Navy acceptance trials
   - Post-shakedown availability

**Total Build Time**: 66 months (5.5 years) for lead ship

---

**Classification: UNCLASSIFIED // CONCEPTUAL DESIGN**
