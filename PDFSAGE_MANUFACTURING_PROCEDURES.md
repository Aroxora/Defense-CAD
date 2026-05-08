# PDFSAge Inc - Manufacturing Procedures Manual

## Defense Systems Production Procedures

**Contractor:** PDFSAge Inc
**Document Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY
**Document Number:** PDFSAGE-MFG-001
**Revision:** 1.0
**Date:** 2026-01-02

---

## TABLE OF CONTENTS

1. [Assembly Procedures](#1-assembly-procedures)
   - 1.1 Seabed Arsenal Pod
   - 1.2 Locust Scramjet
2. [Quality Assurance Procedures](#2-quality-assurance-procedures)
   - 2.1 Inspection Requirements
   - 2.2 Non-Conformance Procedures
   - 2.3 Calibration Program
3. [Regulatory Compliance](#3-regulatory-compliance)
   - 3.1 ITAR Compliance
   - 3.2 DFARS Compliance
   - 3.3 CMMC Certification
4. [Supplier Qualification](#4-supplier-qualification)
   - 4.1 Approved Supplier List
   - 4.2 Qualified Suppliers
   - 4.3 Traceability Requirements
5. [Test Procedures](#5-test-procedures)
   - 5.1 ATP - Seabed Arsenal Pod
   - 5.2 ATP - Locust Scramjet
6. [Safety Requirements](#6-safety-requirements)
   - 6.1 Explosive Safety
   - 6.2 General Safety
7. [Configuration Management](#7-configuration-management)

---

## 1. ASSEMBLY PROCEDURES

### 1.1 SEABED ARSENAL POD - ASSEMBLY SEQUENCE

```
WORK INSTRUCTION: SAP-1-ASSY-001
REVISION: A
EFFECTIVE DATE: 2026-01-02

STEP 1: PRESSURE HULL FABRICATION
├── 1.1 Receive Ti-6Al-4V plate stock (Cert: AMS 4911)
│   ├── Verify material certs match PO
│   ├── Perform PMI (Positive Material ID) on 100% of plates
│   ├── Record lot numbers in MES (Manufacturing Execution System)
│   └── Quarantine until QA release
├── 1.2 CNC machining of hull sections
│   ├── Load program SAP-HULL-CNC-001
│   ├── Tool wear check every 10 parts
│   ├── In-process dimensional inspection per dwg SAP-1001
│   └── Surface finish: 125 Ra max
├── 1.3 Electron beam welding (per WPS-EB-Ti-001)
│   ├── Qualified welder required (AWS D17.1)
│   ├── Joint prep: Machine to 0.002" gap max
│   ├── Weld parameters: 150kV, 45mA, 20 ipm
│   ├── Root pass + 2 fill passes
│   ├── Interpass temp: 300°F max
│   └── Post-weld stress relief: 1100°F x 2hr
├── 1.4 NDT inspection
│   ├── Visual: 100% per AWS D17.1
│   ├── Dye penetrant: 100% welds (ASTM E1417)
│   ├── Radiographic: 100% welds (ASTM E1742)
│   ├── Ultrasonic: Parent material (ASTM A388)
│   └── Acceptance criteria: Zero defects Class A
└── 1.5 Hydrostatic proof test
    ├── Fill with fresh water
    ├── Pressurize to 1.5x operating (1125 psi)
    ├── Hold 30 minutes
    ├── Inspect for leaks, distortion
    └── Record pressure chart in DHR

STEP 2: VLS TUBE INSTALLATION
├── 2.1 Receive Mk 41 derivative tubes
│   ├── Verify dimensions per dwg SAP-1015
│   ├── Check corrosion coating integrity
│   └── Verify launch rail alignment
├── 2.2 Tube-to-hull welding
│   ├── Fit tubes to hull cutouts (0.010" gap max)
│   ├── Tack weld at 4 positions
│   ├── Full penetration weld per WPS-GTAW-Ti-002
│   └── NDT: 100% PT + RT
├── 2.3 Launch mechanism installation
│   ├── Install cold gas ejection system
│   ├── Torque fasteners per dwg SAP-1016
│   ├── Connect gas lines (leak test @ 4500 psi)
│   └── Functional test: Dry fire each tube
└── 2.4 Door mechanism installation
    ├── Install hydraulic actuators
    ├── Install watertight seals
    ├── Cycle test: 100 open/close cycles
    └── Leak test: Submerge, verify zero bubbles

STEP 3: ELECTRICAL/ELECTRONICS INSTALLATION
├── 3.1 Battery pack installation
│   ├── ESD precautions required (wrist strap, mat)
│   ├── Install battery modules (8x 62.5 kWh)
│   ├── Torque connections per spec (25 ft-lb)
│   ├── Verify polarity before final connection
│   └── Initial charge to 50% SOC
├── 3.2 Communication system
│   ├── Install ELF antenna (external mount)
│   ├── Install acoustic transducers
│   ├── Install SATCOM buoy launcher
│   ├── Cable routing per dwg SAP-1030
│   └── Continuity/insulation resistance test
├── 3.3 Launch control computer
│   ├── Install in shock-mounted rack
│   ├── Load software ver SAP-SW-3.2.1
│   ├── Verify crypto module installed
│   └── Functional test per ATP-SAP-001
└── 3.4 Sensor installation
    ├── Depth sensor (calibrated cert required)
    ├── Attitude sensors (MEMS IMU)
    ├── Leak detection sensors
    └── Integration test: All sensors reporting

STEP 4: FINAL ASSEMBLY
├── 4.1 Apply corrosion protection
│   ├── Sacrificial zinc anodes (calculate from hull area)
│   ├── Epoxy coating: 2 coats, 10 mil DFT
│   ├── Cure: 72 hours @ 70°F min
│   └── Coating inspection per SSPC-PA 2
├── 4.2 Install mooring system
│   ├── Anchor attachment points
│   ├── Swivel assemblies
│   ├── Load test: 50,000 lbs
│   └── Corrosion protect all steel
├── 4.3 Final system integration test
│   ├── Full power-up sequence
│   ├── Communication check (all modes)
│   ├── Simulated launch sequence
│   └── 72-hour burn-in at operating temp
└── 4.4 Packaging for delivery
    ├── Drain all water
    ├── Purge with nitrogen
    ├── Install transportation fixtures
    ├── Prepare shipping container (humidity controlled)
    └── Final inspection per MIL-STD-1916

TOTAL ASSEMBLY TIME: 45 working days
LABOR HOURS PER UNIT: 4,500 hours
```

---

### 1.2 LOCUST SCRAMJET - ASSEMBLY SEQUENCE

```
WORK INSTRUCTION: LOCUST-ASSY-001
REVISION: A
EFFECTIVE DATE: 2026-01-02

STEP 1: AIRFRAME FABRICATION (5 days)
├── 1.1 Receive stamped steel panels
│   ├── Material: 17-4 PH stainless
│   ├── Verify heat treat cert (H900 condition)
│   └── Dimensional inspection: 10% sample
├── 1.2 Weld airframe sections
│   ├── Robotic GMAW (high-volume)
│   ├── 100% visual inspection
│   ├── 10% PT sampling
│   └── Straightness: 0.030"/ft max
├── 1.3 Machine mounting interfaces
│   ├── CNC mill critical surfaces
│   ├── Positional tolerance: 0.005"
│   └── Surface finish: 63 Ra
└── 1.4 Apply thermal protection
    ├── Plasma spray ceramic (zirconia)
    ├── Thickness: 0.015-0.020"
    └── Adhesion test: Pull test 500 psi

STEP 2: SCRAMJET ENGINE INSTALLATION (3 days)
├── 2.1 Receive engine assembly
│   ├── Verify acceptance test data
│   ├── Inspect inlet for FOD
│   └── Check fuel system cleanliness
├── 2.2 Mount engine to airframe
│   ├── Align to 0.002" TIR
│   ├── Torque mounting bolts: 45 ft-lb
│   └── Safety wire per MS33540
├── 2.3 Fuel system connection
│   ├── Connect feed lines (AN fittings)
│   ├── Pressure test: 500 psi
│   └── Flow test: Verify 2.5 lb/sec
└── 2.4 Ignition system
    ├── Install igniters
    ├── Wiring per schematic LOCUST-E-001
    └── Continuity check

STEP 3: GUIDANCE INSTALLATION (2 days)
├── 3.1 INS installation
│   ├── ESD precautions
│   ├── Boresight alignment: 0.1 mrad
│   └── Vibration isolation mounts
├── 3.2 GPS receiver
│   ├── Install antenna (nose section)
│   ├── Verify M-code capability
│   └── Acquisition test
├── 3.3 MMW seeker
│   ├── Install in nose cone
│   ├── Boresight to INS: 1 mrad
│   └── Functional test: Target sim
└── 3.4 Flight computer
    ├── Load mission software
    ├── Verify checksum
    └── BIT (Built-In Test) pass

STEP 4: WARHEAD & BOOSTER (2 days)
├── 4.1 Warhead installation (EXPLOSIVE AREA)
│   ├── Certified explosive handlers only
│   ├── Ground all equipment
│   ├── Install warhead section
│   ├── Connect fuze (safed)
│   └── Verify S&A device position
├── 4.2 Booster installation
│   ├── Inspect solid motor
│   ├── Install to aft section
│   ├── Connect umbilical
│   └── Verify igniter continuity
└── 4.3 Final close-out
    ├── Install access panels
    ├── Apply fastener torque stripe
    └── Final weight & CG check

STEP 5: ACCEPTANCE TEST (1 day)
├── 5.1 Guidance functional test
├── 5.2 Communication test
├── 5.3 Telemetry verification
├── 5.4 Final inspection
└── 5.5 Packaging & shipping

TOTAL ASSEMBLY TIME: 13 working days
LABOR HOURS PER UNIT: 380 hours
```

---

### 1.3 MAKO HYPERSONIC TORPEDO - ASSEMBLY SEQUENCE

```
WORK INSTRUCTION: MAKO-ASSY-001
REVISION: A
EFFECTIVE DATE: 2026-01-02

STEP 1: PRESSURE HULL FABRICATION (10 days)
├── 1.1 Receive Inconel 718 forgings
│   ├── Material cert: AMS 5662 or 5663
│   ├── 100% PMI verification
│   ├── Ultrasonic inspection (ASTM A388)
│   └── Record heat/lot in traveler
├── 1.2 CNC machining - external profile
│   ├── Rough machine to +0.050"
│   ├── Stress relieve: 1325°F x 1hr
│   ├── Finish machine to drawing
│   └── Surface finish: 63 Ra external, 125 Ra internal
├── 1.3 Supercavitating nose cone fabrication
│   ├── Material: Carbon-carbon composite
│   ├── Layup per spec MAKO-CC-001
│   ├── Autoclave cure: 350°F, 100 psi, 4hr
│   ├── NDT: Ultrasonic C-scan 100%
│   └── Machine to final contour
├── 1.4 Hull section welding
│   ├── Electron beam weld (vacuum chamber)
│   ├── Parameters: 140kV, 50mA, 15 ipm
│   ├── X-ray inspection: 100%
│   └── Acceptance: AWS D17.1 Class A
└── 1.5 Hydrostatic test
    ├── Test pressure: 1500 psi (3x operating depth)
    ├── Hold time: 30 minutes
    ├── Permanent deformation: <0.1%
    └── Document in DHR

STEP 2: PROPULSION SYSTEM INSTALLATION (8 days)
├── 2.1 Solid rocket motor installation
│   ├── Receive motor (certified lot)
│   ├── X-ray inspection for defects
│   ├── Install in aft section
│   ├── Torque mounting ring: 150 ft-lb
│   └── Connect igniter harness
├── 2.2 Scramjet engine installation
│   ├── Receive engine (acceptance test data)
│   ├── Inspect fuel injectors
│   ├── Mount to center section
│   ├── Align inlet to 0.005" TIR
│   └── Connect fuel feed lines
├── 2.3 Fuel system
│   ├── Install JP-10 tank (180 kg capacity)
│   ├── Pressure test: 750 psi
│   ├── Flow calibration test
│   └── Install fuel management computer
└── 2.4 Thermal protection system
    ├── Apply ablative coating (silicone-based)
    ├── Thickness: 0.25" ±0.02"
    ├── Bond test: Pull test 200 psi
    └── Inspect for voids/delamination

STEP 3: WATER EXIT SYSTEM (5 days)
├── 3.1 Gas generator installation
│   ├── Install drag reduction system
│   ├── Connect to control valves
│   ├── Leak test: 5000 psi helium
│   └── Functional test: Valve cycling
├── 3.2 Cavitator nose installation
│   ├── Install carbon-carbon nose cone
│   ├── Torque attachment ring: 75 ft-lb
│   ├── Seal test: Submerge 24hr
│   └── Gap inspection: <0.005"
├── 3.3 Blow-off seals
│   ├── Install inlet covers
│   ├── Install exhaust covers
│   ├── Verify explosive bolt continuity
│   └── Shear pin installation
└── 3.4 Buoyancy trim
    ├── Weigh assembly
    ├── Calculate ballast required
    ├── Install trim weights
    └── Verify neutral buoyancy ±2%

STEP 4: GUIDANCE & CONTROL (4 days)
├── 4.1 INS installation
│   ├── Navigation-grade IMU (Honeywell HG9900)
│   ├── Boresight to vehicle axis: 0.05 mrad
│   ├── Vibration isolators installed
│   └── Functional test: Alignment sequence
├── 4.2 Seeker installation
│   ├── Ka-band radar (active)
│   ├── IIR imaging (passive)
│   ├── Boresight to INS: 0.5 mrad
│   ├── Radome installation
│   └── Functional test: Target simulation
├── 4.3 Flight computer
│   ├── Install processor module
│   ├── Load flight software v2.1.0
│   ├── Verify checksum
│   └── BIT: All functions pass
└── 4.4 Control actuators
    ├── Install fin actuators (4x)
    ├── Connect hydraulic lines
    ├── Stroke test: Full deflection
    └── Rate test: 100°/sec minimum

STEP 5: WARHEAD INTEGRATION (3 days) [EXPLOSIVE AREA]
├── 5.1 Warhead section
│   ├── Receive shaped charge warhead (500 kg)
│   ├── X-ray inspection
│   ├── Install in forward section
│   └── Torque attachment: 200 ft-lb
├── 5.2 Safe & Arm device
│   ├── Install S&A mechanism
│   ├── Verify SAFE indication
│   ├── Interlock test: All conditions
│   └── Document serial number
├── 5.3 Fuze installation
│   ├── Install proximity fuze
│   ├── Install contact fuze (backup)
│   ├── Connect to S&A
│   └── Continuity test (safed)
└── 5.4 Warhead closeout
    ├── Final wiring connections
    ├── Apply potting compound
    ├── Install access covers
    └── Seal and safety wire

STEP 6: FINAL ASSEMBLY & TEST (5 days)
├── 6.1 Section mating
│   ├── Mate forward/center/aft sections
│   ├── Torque circumferential bolts
│   ├── Verify alignment: 0.010" TIR
│   └── Install o-ring seals
├── 6.2 Cabling & connections
│   ├── Connect all harnesses
│   ├── Continuity test: 100%
│   ├── Insulation resistance: >10 MΩ
│   └── Hi-pot test: 500V
├── 6.3 System integration test
│   ├── Power-up sequence
│   ├── All subsystems communicate
│   ├── Guidance simulation
│   ├── Propulsion simulation
│   └── 48-hour burn-in
├── 6.4 Pressure/leak test
│   ├── Submerge to 100m equivalent
│   ├── Hold 4 hours
│   ├── Verify zero leakage
│   └── Functional test submerged
└── 6.5 Final inspection & ship
    ├── Configuration audit
    ├── Documentation complete
    ├── Weight & CG verification
    ├── Package in shipping container
    └── Nitrogen purge, desiccant

TOTAL ASSEMBLY TIME: 35 working days
LABOR HOURS PER UNIT: 3,200 hours
```

---

### 1.4 WOLFPACK UUV - ASSEMBLY SEQUENCE

```
WORK INSTRUCTION: WOLFPACK-ASSY-001
REVISION: A
EFFECTIVE DATE: 2026-01-02

STEP 1: PRESSURE HULL FABRICATION (20 days)
├── 1.1 Receive HY-80 steel plate
│   ├── Material cert: MIL-S-16216
│   ├── Charpy impact test: -120°F
│   ├── 100% UT inspection
│   └── Traceability to heat number
├── 1.2 Roll and form hull sections
│   ├── Cold roll to cylinder
│   ├── Roundness: 0.5% of diameter
│   ├── Stress relieve: 1100°F x 1hr
│   └── Dimensional inspection
├── 1.3 Weld hull sections
│   ├── Submerged arc weld (SAW)
│   ├── WPS per MIL-STD-1689
│   ├── Preheat: 200°F minimum
│   ├── Interpass temp: 400°F max
│   └── PWHT: 1100°F x 1hr per inch
├── 1.4 NDT inspection
│   ├── Visual: 100%
│   ├── MT: 100% welds
│   ├── RT: 100% welds
│   ├── UT: 100% welds + base metal
│   └── Acceptance: MIL-STD-2035
├── 1.5 Hydrostatic test
│   ├── Test pressure: 675 psi (1.5x @ 300m)
│   ├── Hold time: 2 hours
│   ├── Strain gauge monitoring
│   └── Permanent set: <0.05%
└── 1.6 Hull coating
    ├── Blast to SSPC-SP 10
    ├── Apply epoxy primer: 3 mils
    ├── Apply polyurethane: 8 mils
    ├── Cure: 7 days
    └── Holiday test: 3000V

STEP 2: PROPULSION SYSTEM (15 days)
├── 2.1 Battery installation
│   ├── Li-ion modules (2 MWh total)
│   ├── Install in battery compartment
│   ├── Connect bus bars (torque: 50 ft-lb)
│   ├── BMS installation
│   └── Insulation test: 1000V megger
├── 2.2 Electric motor installation
│   ├── PM synchronous motor (500 kW)
│   ├── Align to 0.002" TIR
│   ├── Connect power cables
│   ├── Cooling system connection
│   └── Rotation test: Verify direction
├── 2.3 Rim-driven propulsor
│   ├── Install propulsor assembly
│   ├── Gap check: 0.020" ±0.005"
│   ├── Balance check: <0.1 oz-in
│   └── Seal integrity test
├── 2.4 Motor controller
│   ├── Install VFD cabinet
│   ├── Connect power/control cables
│   ├── Program parameters
│   └── Functional test: All speeds
└── 2.5 AIP system (optional)
    ├── Install fuel cell stack
    ├── LOX/H2 storage tanks
    ├── Piping installation
    ├── Leak test: Helium mass spec
    └── Functional test: 72 hours

STEP 3: SENSOR SYSTEMS (10 days)
├── 3.1 Passive sonar arrays
│   ├── Install flank arrays (port/stbd)
│   ├── Hydrophone elements: 256 per side
│   ├── Cable routing to processor
│   ├── Waterproof connector termination
│   └── Continuity/insulation test
├── 3.2 Active sonar
│   ├── Install bow transducer
│   ├── Align to vehicle axis
│   ├── Connect to transmitter
│   └── Functional test: Echo return
├── 3.3 Photonics mast
│   ├── Install non-hull-penetrating mast
│   ├── Camera/IR sensor installation
│   ├── ESM antenna installation
│   ├── Raise/lower mechanism test
│   └── Image quality verification
└── 3.4 Navigation sensors
    ├── Install INS (navigation grade)
    ├── Install Doppler velocity log
    ├── Install depth sensors (redundant)
    ├── GPS antenna (mast-mounted)
    └── Integration test: Nav solution

STEP 4: WEAPONS SYSTEM (8 days)
├── 4.1 Torpedo tube installation
│   ├── 4x 324mm tubes
│   ├── Weld to pressure hull
│   ├── NDT: 100% RT
│   ├── Muzzle door mechanism
│   └── Interlock system test
├── 4.2 Fire control system
│   ├── Install FCS computer
│   ├── Connect to sonar/nav
│   ├── Load software
│   └── Simulation test: Target solution
├── 4.3 Weapon handling
│   ├── Install loading rails
│   ├── Align to tubes: 0.010"
│   ├── Test with dummy weapons
│   └── Cycle time: <60 seconds
└── 4.4 Tube flood/drain
    ├── Install flood valves
    ├── Install drain pumps
    ├── Pressure test tubes
    └── Functional test: Full cycle

STEP 5: AI/AUTONOMY SYSTEMS (7 days)
├── 5.1 Computer installation
│   ├── Nvidia Orin AGX cluster
│   ├── Shock-mounted rack
│   ├── Cooling system connection
│   └── Power conditioning
├── 5.2 Software installation
│   ├── Shield AI Hivemind base
│   ├── Custom autonomy stack
│   ├── Behavior libraries
│   └── Version verification
├── 5.3 Sensor fusion integration
│   ├── Connect all sensor feeds
│   ├── Calibrate latencies
│   ├── Verify track correlation
│   └── Performance benchmark
├── 5.4 Communication systems
│   ├── Acoustic modem installation
│   ├── SATCOM buoy system
│   ├── Mesh network testing
│   └── Encryption verification
└── 5.5 Autonomy testing
    ├── Simulation: 1000+ scenarios
    ├── Hardware-in-loop test
    ├── Failure mode testing
    └── Human override verification

STEP 6: FINAL ASSEMBLY & SEA TRIALS (15 days)
├── 6.1 Hull closeout
│   ├── Install all hatches
│   ├── Verify watertight integrity
│   ├── Final weight/trim
│   └── CG verification
├── 6.2 Dock trials
│   ├── Power-up all systems
│   ├── Propulsion test (bollard)
│   ├── Sensor checkout
│   └── Emergency systems test
├── 6.3 Sea trials - surface
│   ├── Speed trials (all speeds)
│   ├── Maneuvering trials
│   ├── Navigation accuracy
│   └── Communication tests
├── 6.4 Sea trials - submerged
│   ├── Shallow dive (50m)
│   ├── Systems check submerged
│   ├── Deep dive (300m)
│   ├── Emergency blow test
│   └── Endurance run (72 hours)
├── 6.5 Weapons certification
│   ├── Tube flood/drain cycle
│   ├── Dummy weapon launch
│   ├── FCS tracking exercise
│   └── (Live fire: Government range)
└── 6.6 Delivery
    ├── Final inspection
    ├── Documentation package
    ├── Training for customer
    └── Transport to delivery point

TOTAL ASSEMBLY TIME: 75 working days
LABOR HOURS PER UNIT: 12,000 hours
```

---

### 1.5 CONTAINERIZED STRIKE (PANDORA) - ASSEMBLY SEQUENCE

```
WORK INSTRUCTION: PANDORA-ASSY-001
REVISION: A
EFFECTIVE DATE: 2026-01-02

STEP 1: CONTAINER MODIFICATION (5 days)
├── 1.1 Receive ISO container
│   ├── 40' high cube container
│   ├── Inspect for damage/corrosion
│   ├── Verify CSC plate current
│   └── Document container number
├── 1.2 Structural reinforcement
│   ├── Install internal frame (A36 steel)
│   ├── Weld per AWS D1.1
│   ├── Reinforce roof cut-out areas
│   └── Floor reinforcement for weight
├── 1.3 Roof mechanism cut-out
│   ├── Plasma cut roof panels
│   ├── Install hinge points
│   ├── Install hydraulic rams
│   └── Seal edges with EPDM gasket
├── 1.4 Disguise elements
│   ├── Install fake roof section
│   ├── Add non-functional AC unit
│   ├── Install concealed solar panels
│   └── Apply weathering/logos
└── 1.5 Corrosion protection
    ├── Treat all cut edges
    ├── Prime and paint interior
    ├── Install vapor barrier
    └── Dehumidifier connection points

STEP 2: LAUNCH SYSTEM INSTALLATION (4 days)
├── 2.1 Missile cradle installation
│   ├── Install shock-isolated cradles (4x)
│   ├── Align to vertical ±0.5°
│   ├── Torque mounting bolts
│   └── Load capacity test: 2x missile weight
├── 2.2 Roof opening mechanism
│   ├── Install hydraulic power unit
│   ├── Connect to rams
│   ├── Install position sensors
│   ├── Set limit switches
│   └── Cycle test: 50 cycles
├── 2.3 Environmental seals
│   ├── Install perimeter seal
│   ├── Water test: 2" standing water
│   ├── Install drain system
│   └── Verify seal compression
└── 2.4 Backup systems
    ├── Install explosive bolt backup
    ├── Connect to fire control
    ├── Test circuit continuity
    └── Safety interlock verification

STEP 3: ENVIRONMENTAL CONTROL (3 days)
├── 3.1 HVAC installation
│   ├── Install mil-spec AC unit
│   ├── Install heater elements
│   ├── Connect ductwork
│   └── Capacity test: 5-ton cooling
├── 3.2 Temperature control
│   ├── Install sensors (8 locations)
│   ├── Install controller
│   ├── Set parameters: 65°F ±5°F
│   └── Stability test: 24 hours
├── 3.3 Humidity control
│   ├── Install dehumidifier
│   ├── Install humidifier (optional)
│   ├── Target: 30-50% RH
│   └── Calibrate sensors
└── 3.4 Monitoring system
    ├── Install environmental logger
    ├── Connect to telemetry
    ├── Set alarm thresholds
    └── Test alert notification

STEP 4: POWER SYSTEM (2 days)
├── 4.1 Battery installation
│   ├── Li-ion 100 kWh system
│   ├── Install in floor compartment
│   ├── Connect BMS
│   └── Initial charge to 100%
├── 4.2 Solar array
│   ├── Install panels in fake roof
│   ├── Connect charge controller
│   ├── Verify 500W output
│   └── Weatherproof connections
├── 4.3 Power distribution
│   ├── Install breaker panel
│   ├── Wire all systems
│   ├── Ground/bond all metal
│   └── Insulation test: 1000V
└── 4.4 Shore power (optional)
    ├── Install inlet connector
    ├── Install transfer switch
    └── Test changeover

STEP 5: LAUNCH CONTROL & COMMUNICATIONS (3 days)
├── 5.1 Fire control computer
│   ├── Install ruggedized server
│   ├── Load control software
│   ├── Connect to all systems
│   └── BIT verification
├── 5.2 Communication systems
│   ├── Install Iridium transceiver
│   ├── Install HF radio
│   ├── Install GPS receiver
│   ├── Antenna routing (concealed)
│   └── Communication test
├── 5.3 Authentication system
│   ├── Install crypto module (NSA Type 1)
│   ├── Two-person enable device
│   ├── Code verification system
│   └── Tamper detection
└── 5.4 Targeting system
    ├── Mission planning interface
    ├── GPS coordinate entry
    ├── Flight plan upload
    └── Verification protocol

STEP 6: ACCEPTANCE TEST (3 days)
├── 6.1 Structural test
│   ├── Load test: Max missile weight
│   ├── Lift test: Crane/forklift
│   ├── Transport simulation
│   └── Inspect for damage
├── 6.2 Environmental test
│   ├── 72-hour temperature cycle
│   ├── Humidity stability
│   ├── Water intrusion test
│   └── All parameters logged
├── 6.3 Launch sequence test (dry)
│   ├── Full sequence simulation
│   ├── Roof open timing: <15 sec
│   ├── Abort sequence test
│   └── Emergency procedures
├── 6.4 Communication test
│   ├── SATCOM link verification
│   ├── HF communication test
│   ├── Crypto functionality
│   └── Authentication sequence
└── 6.5 Final inspection
    ├── Configuration verification
    ├── Documentation complete
    ├── Disguise effectiveness
    └── Ready for missile load

TOTAL ASSEMBLY TIME: 20 working days
LABOR HOURS PER UNIT: 650 hours
```

---

## 2. QUALITY ASSURANCE PROCEDURES

### 2.1 INSPECTION REQUIREMENTS

```
QUALITY PLAN: PDFSAGE-QP-001
APPLICABLE STANDARDS:
├── AS9100D (Aerospace Quality Management)
├── MIL-STD-1916 (Sampling Procedures)
├── MIL-I-45208 (Inspection System Requirements)
└── ANSI/NCSL Z540.3 (Calibration)

SOURCE INSPECTION:
├── All critical materials: 100% source inspection
├── Ti-6Al-4V: Government source inspection (GSI)
├── Energetics: DoD inspector required
├── Electronics: FAI on first article
└── Subassemblies: First article + periodic audit

RECEIVING INSPECTION:
├── Level I (Critical): 100% inspection
│   ├── Pressure vessel materials
│   ├── Propulsion components
│   ├── Guidance systems
│   └── Explosive components
├── Level II (Major): AQL 1.0 sampling
│   ├── Structural components
│   ├── Electrical assemblies
│   └── Mechanical parts
└── Level III (Minor): AQL 2.5 sampling
    ├── Hardware (fasteners)
    ├── Consumables
    └── Packaging materials

IN-PROCESS INSPECTION:
├── Weld inspection: 100% visual + NDT
├── Assembly inspection: Per work instruction
├── Dimensional: Statistical process control (Cpk > 1.33)
├── Torque verification: 100% critical, 10% non-critical
└── Electrical test: 100% continuity, insulation

FINAL INSPECTION:
├── Functional test: 100%
├── Dimensional verification: Critical features
├── Documentation review: 100%
├── Configuration audit: 100%
└── Packaging inspection: 100%
```

### 2.2 NON-CONFORMANCE PROCEDURES

```
PROCEDURE: PDFSAGE-QP-002
TITLE: Non-Conforming Material Control

DISCOVERY:
├── Stop work immediately
├── Segregate suspect material (red tag)
├── Notify QA within 1 hour
├── Document on NCR form (PDFSAGE-NCR-001)
└── Determine extent of condition

DISPOSITION:
├── USE-AS-IS: Engineering approval required
│   ├── Structural analysis
│   ├── Customer approval (if contractual)
│   └── Document rationale
├── REWORK: Return to conformance
│   ├── Rework procedure required
│   ├── Re-inspect after rework
│   └── Document in DHR
├── REPAIR: Does not meet original spec
│   ├── Engineering approval
│   ├── Repair procedure
│   ├── Customer approval required
│   └── Serial number tracking
└── SCRAP: Cannot be used
    ├── Render unusable (drill/cut)
    ├── Controlled disposal
    └── Update inventory

ROOT CAUSE ANALYSIS:
├── Required for all critical NCRs
├── 5-Why analysis minimum
├── Corrective action within 30 days
└── Effectiveness verification
```

### 2.3 CALIBRATION PROGRAM

```
PROCEDURE: PDFSAGE-QP-003
TITLE: Calibration Control

REQUIREMENTS:
├── All M&TE (Measuring & Test Equipment) calibrated
├── Traceability to NIST standards
├── Calibration interval based on usage/stability
├── Out-of-tolerance: Impact assessment required

CALIBRATION INTERVALS:
├── Torque wrenches: 6 months
├── Micrometers/calipers: 12 months
├── Pressure gauges: 12 months
├── Multimeters: 12 months
├── CMM: 6 months
├── Hardness testers: 6 months
└── NDT equipment: Per procedure

CALIBRATION STICKERS:
├── Green: Current calibration
├── Yellow: Limited use (specific application only)
├── Red: Out of calibration - DO NOT USE
└── Track in database: PDFSAGE-CAL-DB
```

### 2.4 FIRST ARTICLE INSPECTION (FAI)

```
PROCEDURE: PDFSAGE-QP-005
TITLE: First Article Inspection

PURPOSE:
├── Verify manufacturing process produces conforming product
├── Validate design meets requirements
├── Establish baseline for production
└── Required per AS9102

WHEN REQUIRED:
├── New part number (first production unit)
├── Design change affecting form/fit/function
├── Process change (new equipment, supplier, method)
├── Lapse in production >2 years
└── Customer request

FAI DOCUMENTATION (AS9102 Forms):
├── Form 1: Part Number Accountability
│   ├── Part number, revision, serial number
│   ├── Drawing/spec references
│   └── FAI reason code
├── Form 2: Product Accountability
│   ├── Material certifications
│   ├── Special process certifications
│   └── Functional test results
└── Form 3: Characteristic Accountability
    ├── All drawing dimensions
    ├── Measured values
    ├── Pass/fail determination
    └── Inspection equipment used

ACCEPTANCE:
├── All characteristics within tolerance
├── All material/process certs on file
├── Functional tests pass
├── Engineering review and approval
└── Customer approval (if required)

PARTIAL FAI:
├── Allowed for design changes
├── Only re-inspect affected characteristics
├── Reference original FAI
└── Document unchanged features
```

---

## 3. REGULATORY COMPLIANCE

### 3.1 ITAR COMPLIANCE

```
INTERNATIONAL TRAFFIC IN ARMS REGULATIONS (22 CFR 120-130)

REGISTRATION:
├── DDTC registration current (verify annually)
├── Registration number: M-XXXXX
└── Designated empowered official: [Name]

CONTROLLED ITEMS (USML Categories):
├── Category IV: Launch Vehicles, Guided Missiles
│   ├── Seabed Arsenal Pod: IV(a) - complete systems
│   ├── Locust Scramjet: IV(a) - complete missile
│   ├── Mako Torpedo: IV(a) - complete torpedo
│   └── Pandora Container: IV(a) - launch system
├── Category XI: Military Electronics
│   ├── ODIN software: XI(a)(3) - C4I software
│   ├── Guidance systems: XI(c) - navigation
│   └── Fire control: XI(a)(4)
└── Category XX: Submersible Vessels
    └── Wolfpack UUV: XX(a) - unmanned systems

EXPORT CONTROLS:
├── No foreign persons access without license
├── Visitors: Escort required, sign NDA
├── Electronic data: Encrypted storage, no cloud (public)
├── Shipping: Licensed freight forwarder only
└── Technology transfer: Prior DDTC approval required

COMPLIANCE PROCEDURES:
├── Employee training: Annual ITAR awareness
├── Foreign national screening: All hires
├── Visitor log: Maintained 5 years
├── Export license tracking: PDFSAGE-ITAR-LOG
└── Self-disclosure: Report violations within 60 days

PENALTIES:
├── Civil: Up to $1.2M per violation
├── Criminal: Up to $1M and 20 years imprisonment
├── Debarment from government contracting
└── Loss of export privileges
```

### 3.2 DFARS COMPLIANCE

```
DEFENSE FEDERAL ACQUISITION REGULATION SUPPLEMENT

KEY CLAUSES (FLOWDOWN REQUIRED):
├── 252.204-7012: Safeguarding Covered Defense Info
│   ├── NIST SP 800-171 compliance required
│   ├── Incident reporting within 72 hours
│   ├── Cloud: FedRAMP Moderate minimum
│   └── Applies to all subcontractors
├── 252.225-7001: Buy American Act
│   ├── Domestic components: >55% by cost
│   ├── Qualifying countries allowed
│   └── Waiver process for exceptions
├── 252.225-7009: Specialty Metals
│   ├── Titanium: US or qualifying country melt
│   ├── Steel: US or qualifying country melt
│   ├── Aluminum: US or qualifying country melt
│   └── Exceptions: De minimis (<2%), COTS
├── 252.225-7012: Preference for US/Canada
│   └── End products manufactured in US/Canada
├── 252.227-7013: Technical Data Rights
│   ├── Deliver unlimited rights data
│   ├── Mark limited rights data
│   └── Government purpose rights
├── 252.227-7014: Computer Software Rights
│   ├── Similar to technical data
│   └── Source code delivery requirements
└── 252.246-7007: Contractor Counterfeit Prevention
    ├── Risk-based counterfeit prevention program
    ├── Approved supplier list required
    ├── Traceability to OEM
    └── Quarantine/report suspect parts

REPORTING REQUIREMENTS:
├── SPRS: Supplier Performance Risk System
├── SAM: System for Award Management
├── DIBBS: DLA Internet Bid Board System
└── WAWF: Wide Area Workflow (invoicing)
```

### 3.3 CMMC CERTIFICATION

```
CYBERSECURITY MATURITY MODEL CERTIFICATION

REQUIRED LEVEL: Level 2 (Advanced)
├── 110 practices from NIST SP 800-171
├── Annual self-assessment required
├── Triennial third-party assessment (C3PAO)
├── Affirmation submitted to SPRS
└── Required for CUI contracts

KEY DOMAINS AND PRACTICES:

ACCESS CONTROL (AC): 22 practices
├── AC.L1-3.1.1: Limit system access to authorized users
├── AC.L1-3.1.2: Limit access to types of transactions
├── AC.L2-3.1.5: Employ least privilege principle
├── AC.L2-3.1.12: Monitor/control remote access
├── AC.L2-3.1.14: Route remote access via managed access points
└── AC.L2-3.1.18-19: Control mobile device connection

AUDIT AND ACCOUNTABILITY (AU): 9 practices
├── AU.L2-3.3.1: Create audit logs
├── AU.L2-3.3.2: Trace actions to users
└── AU.L2-3.3.5: Use audit log correlation

CONFIGURATION MANAGEMENT (CM): 9 practices
├── CM.L2-3.4.1: Establish baseline configurations
├── CM.L2-3.4.2: Employ security config settings
└── CM.L2-3.4.6: Employ least functionality

IDENTIFICATION & AUTHENTICATION (IA): 11 practices
├── IA.L1-3.5.1: Identify system users
├── IA.L1-3.5.2: Authenticate users
├── IA.L2-3.5.3: Use multifactor authentication
└── IA.L2-3.5.10: Store/transmit passwords cryptographically

INCIDENT RESPONSE (IR): 3 practices
├── IR.L2-3.6.1: Incident handling capability
├── IR.L2-3.6.2: Track/document/report incidents
└── Report to DC3/DIBNET within 72 hours

MAINTENANCE (MA): 6 practices
├── MA.L2-3.7.1: Perform maintenance
├── MA.L2-3.7.2: Control maintenance tools
└── MA.L2-3.7.5: Require MFA for remote maintenance

MEDIA PROTECTION (MP): 9 practices
├── MP.L1-3.8.3: Sanitize media before disposal
├── MP.L2-3.8.1: Protect (mark) CUI media
└── MP.L2-3.8.7: Control removable media use

PERSONNEL SECURITY (PS): 2 practices
├── PS.L2-3.9.1: Screen individuals
└── PS.L2-3.9.2: Protect CUI during termination

PHYSICAL PROTECTION (PE): 6 practices
├── PE.L1-3.10.1: Limit physical access
├── PE.L1-3.10.3: Escort visitors
└── PE.L2-3.10.6: Enforce safeguarding at alternate sites

RISK ASSESSMENT (RA): 3 practices
├── RA.L2-3.11.1: Periodically assess risk
├── RA.L2-3.11.2: Scan for vulnerabilities
└── RA.L2-3.11.3: Remediate vulnerabilities

SECURITY ASSESSMENT (CA): 4 practices
├── CA.L2-3.12.1: Assess security controls
├── CA.L2-3.12.2: Develop remediation plans
└── CA.L2-3.12.4: Monitor security controls

SYSTEM & COMMUNICATIONS (SC): 16 practices
├── SC.L1-3.13.1: Monitor communications at boundaries
├── SC.L2-3.13.11: Employ FIPS-validated cryptography
└── SC.L2-3.13.15: Protect authenticity of communications

SYSTEM & INFO INTEGRITY (SI): 7 practices
├── SI.L1-3.14.1: Identify/correct flaws timely
├── SI.L1-3.14.2: Provide malicious code protection
├── SI.L2-3.14.3: Monitor security alerts
└── SI.L2-3.14.6-7: Monitor system/communications

IT INFRASTRUCTURE REQUIREMENTS:
├── Network: Segmented CUI enclave
├── Endpoints: EDR, FDE (full disk encryption)
├── Email: O365 GCC High or equivalent
├── Backup: Air-gapped, encrypted
├── Logging: SIEM with 12-month retention
└── Boundary: Firewall, IDS/IPS
```

### 3.4 FACILITY CLEARANCE (FCL)

```
PROCEDURE: PDFSAGE-SEC-001
TITLE: Facility Security Requirements

FACILITY CLEARANCE LEVEL: SECRET (minimum)
├── Top Secret preferred for some programs
├── DCSA oversight
├── Sponsoring government agency required
└── Renewal: Every 5 years

KEY SECURITY OFFICER (KSO):
├── Designated in DD Form 441
├── Oversees all security matters
├── Signs classified contracts
├── Reports security incidents
└── Manages personnel clearances

PERSONNEL SECURITY:
├── SECRET clearance: Most employees
├── TOP SECRET: Engineers, program managers
├── TS/SCI: Certain compartmented programs
├── Processing: SF-86, e-QIP submission
└── Reinvestigation: 5 years (TS), 10 years (S)

PHYSICAL SECURITY:
├── Perimeter: Fenced, access controlled
├── Building: IDS (intrusion detection)
├── Classified storage: GSA-approved containers
├── SCIF: For compartmented information
├── Visitor control: Badge, escort
└── CCTV: Coverage of sensitive areas

INFORMATION SECURITY:
├── Marking: All classified documents
├── Transmission: Approved channels only
├── Storage: Approved containers, locked
├── Destruction: Cross-cut shred, burn
└── Spillage: Immediate reporting

REPORTING REQUIREMENTS:
├── Suspicious contacts: Within 1 business day
├── Security violations: Immediate
├── Foreign travel: 30 days prior
├── Changed circumstances: 30 days
└── Annual refresher training
```

---

## 4. SUPPLIER QUALIFICATION

### 4.1 APPROVED SUPPLIER LIST (ASL)

```
PROCEDURE: PDFSAGE-PUR-001
TITLE: Supplier Qualification

QUALIFICATION CRITERIA:
├── Quality system: AS9100D or equivalent
├── Financial stability: D&B rating (satisfactory)
├── Technical capability: Process audit
├── Delivery performance: >95% on-time
├── ITAR compliance: Registration verified
├── CMMC compliance: Flow-down capable
└── Counterfeit prevention: Program in place

SUPPLIER TIERS:
├── TIER 1 (Critical): On-site audit required
│   ├── Titanium suppliers
│   ├── Propulsion systems
│   ├── Guidance/seeker
│   ├── Explosive components
│   └── Annual re-audit required
├── TIER 2 (Major): Questionnaire + desk audit
│   ├── Electrical components
│   ├── Mechanical parts
│   ├── Raw materials (non-critical)
│   └── Audit every 2 years
└── TIER 3 (Standard): Self-certification
    ├── Commercial parts
    ├── Fasteners (with cert)
    ├── Office supplies
    └── Audit as needed

AUDIT CHECKLIST (TIER 1):
├── Quality management system review
├── Process capability verification
├── Calibration program review
├── Material traceability demonstration
├── Employee training records
├── Nonconformance handling
├── Corrective action system
├── Purchasing controls
├── Inspection methods
└── Packaging/shipping procedures
```

### 4.2 QUALIFIED SUPPLIERS

```
TITANIUM:
├── Titanium Metals Corporation (TIMET)
│   ├── Qualification #: PDFSAGE-SUP-001
│   ├── Products: Ti-6Al-4V plate, bar, forgings
│   ├── Location: Henderson, NV (US melt)
│   ├── Certifications: AS9100D, NADCAP
│   ├── Audit date: 2025-11-15
│   └── Status: APPROVED
├── ATI Specialty Materials
│   ├── Qualification #: PDFSAGE-SUP-002
│   ├── Products: Ti-6Al-4V, Ti-6Al-4V ELI, Ti-6Al-2Sn-4Zr-2Mo
│   ├── Location: Monroe, NC (US melt)
│   ├── Certifications: AS9100D, NADCAP
│   ├── Audit date: 2025-09-22
│   └── Status: APPROVED
├── Howmet Aerospace (formerly Alcoa)
│   ├── Qualification #: PDFSAGE-SUP-003
│   ├── Products: Ti forgings, castings
│   ├── Location: Cleveland, OH
│   ├── Audit date: 2025-08-10
│   └── Status: APPROVED
└── VSMPO-AVISMA: NOT APPROVED (Russian entity - sanctioned)

SPECIALTY STEEL:
├── Carpenter Technology
│   ├── Qualification #: PDFSAGE-SUP-005
│   ├── Products: 17-4 PH, 15-5 PH, Custom 465
│   ├── Location: Reading, PA
│   ├── Certifications: AS9100D
│   └── Status: APPROVED
├── Allegheny Technologies (ATI)
│   ├── Qualification #: PDFSAGE-SUP-006
│   ├── Products: Inconel 718, Waspaloy, Rene 41
│   ├── Location: Monroe, NC
│   └── Status: APPROVED
└── Haynes International
    ├── Qualification #: PDFSAGE-SUP-007
    ├── Products: Hastelloy, high-temp alloys
    ├── Location: Kokomo, IN
    └── Status: APPROVED

PROPULSION:
├── Aerojet Rocketdyne
│   ├── Qualification #: PDFSAGE-SUP-010
│   ├── Products: Scramjet engines, solid motors, liquid engines
│   ├── Location: Various (US)
│   ├── Certifications: AS9100D, government cleared
│   ├── Audit date: 2025-10-05
│   └── Status: APPROVED
├── Northrop Grumman (Propulsion)
│   ├── Qualification #: PDFSAGE-SUP-011
│   ├── Products: Solid rocket motors, boosters
│   ├── Location: Promontory, UT
│   ├── Audit date: 2025-08-18
│   └── Status: APPROVED
└── L3Harris (Aerojet integration)
    ├── Qualification #: PDFSAGE-SUP-012
    ├── Products: Solid motors
    └── Status: PENDING AUDIT - USE WITH CAUTION

GUIDANCE & NAVIGATION:
├── Honeywell Aerospace
│   ├── Qualification #: PDFSAGE-SUP-020
│   ├── Products: INS (HG9900, HG1700), GPS receivers, IMUs
│   ├── Location: Phoenix, AZ
│   ├── Certifications: AS9100D, ITAR registered
│   ├── Audit date: 2025-07-30
│   └── Status: APPROVED
├── Northrop Grumman (Navigation)
│   ├── Qualification #: PDFSAGE-SUP-021
│   ├── Products: LN-251, LN-270 INS, MEMS IMUs
│   ├── Location: Woodland Hills, CA
│   ├── Audit date: 2025-06-12
│   └── Status: APPROVED
├── Collins Aerospace (RTX)
│   ├── Qualification #: PDFSAGE-SUP-024
│   ├── Products: GPS/INS, navigation systems
│   ├── Location: Cedar Rapids, IA
│   └── Status: APPROVED
└── KVH Industries
    ├── Qualification #: PDFSAGE-SUP-025
    ├── Products: Fiber optic gyros, tactical IMUs
    ├── Location: Middletown, RI
    └── Status: APPROVED

SEEKERS & SENSORS:
├── Raytheon Missiles & Defense
│   ├── Qualification #: PDFSAGE-SUP-022
│   ├── Products: MMW seekers, IR seekers, radar
│   ├── Location: Tucson, AZ
│   ├── Certifications: AS9100D, facility cleared TS
│   ├── Audit date: 2025-09-08
│   └── Status: APPROVED
├── BAE Systems
│   ├── Qualification #: PDFSAGE-SUP-023
│   ├── Products: Seekers, EW components, targeting pods
│   ├── Location: Nashua, NH
│   ├── Audit date: 2025-05-20
│   └── Status: APPROVED
├── L3Harris
│   ├── Qualification #: PDFSAGE-SUP-026
│   ├── Products: EO/IR sensors, targeting systems
│   ├── Location: Melbourne, FL
│   └── Status: APPROVED
└── DRS Technologies (Leonardo DRS)
    ├── Qualification #: PDFSAGE-SUP-027
    ├── Products: IR sensors, coolers
    ├── Location: Dallas, TX
    └── Status: APPROVED

BATTERIES & POWER:
├── Saft America
│   ├── Qualification #: PDFSAGE-SUP-030
│   ├── Products: Li-ion battery packs, specialty batteries
│   ├── Location: Jacksonville, FL
│   ├── Certifications: AS9100D
│   ├── Audit date: 2025-04-15
│   └── Status: APPROVED
├── EaglePicher Technologies
│   ├── Qualification #: PDFSAGE-SUP-031
│   ├── Products: Custom battery systems, thermal batteries
│   ├── Location: Joplin, MO
│   ├── Audit date: 2025-03-22
│   └── Status: APPROVED
├── Ultralife Corporation
│   ├── Qualification #: PDFSAGE-SUP-032
│   ├── Products: Military batteries, chargers
│   ├── Location: Newark, NY
│   └── Status: APPROVED
└── Contemporary Amperex (CATL): NOT APPROVED (Chinese entity)
└── BYD Company: NOT APPROVED (Chinese entity)

ELECTRONICS & COMPUTING:
├── Mercury Systems
│   ├── Qualification #: PDFSAGE-SUP-040
│   ├── Products: Rugged computing, signal processing
│   ├── Location: Andover, MA
│   └── Status: APPROVED
├── Curtiss-Wright Defense
│   ├── Qualification #: PDFSAGE-SUP-041
│   ├── Products: Flight computers, VME/VPX boards
│   ├── Location: Ashburn, VA
│   └── Status: APPROVED
├── Elbit Systems of America
│   ├── Qualification #: PDFSAGE-SUP-042
│   ├── Products: Displays, computing, EW
│   ├── Location: Fort Worth, TX
│   └── Status: APPROVED (allied nation)
└── Abaco Systems
    ├── Qualification #: PDFSAGE-SUP-043
    ├── Products: SBCs, GPUs for defense
    ├── Location: Huntsville, AL
    └── Status: APPROVED

EXPLOSIVES & ORDNANCE:
├── General Dynamics OTS (Ordnance & Tactical Systems)
│   ├── Qualification #: PDFSAGE-SUP-050
│   ├── Products: Warheads, fuzes, propellants
│   ├── Location: Various (US)
│   └── Status: APPROVED
├── Nammo (US operations)
│   ├── Qualification #: PDFSAGE-SUP-051
│   ├── Products: Rocket motors, warheads
│   ├── Location: Mesa, AZ
│   └── Status: APPROVED (allied nation - Norway)
├── BAE Systems (Ordnance)
│   ├── Qualification #: PDFSAGE-SUP-052
│   ├── Products: Warheads, charges
│   ├── Location: Kingsport, TN
│   └── Status: APPROVED
└── Chemring Group
    ├── Qualification #: PDFSAGE-SUP-053
    ├── Products: Countermeasures, pyrotechnics
    ├── Location: Various (US/UK)
    └── Status: APPROVED (allied nation)
```

### 4.3 TRACEABILITY REQUIREMENTS

```
PROCEDURE: PDFSAGE-QP-004
TITLE: Material Traceability

CRITICAL MATERIALS (100% Traceability Required):
├── Titanium alloys
│   ├── Heat/lot number from mill
│   ├── Mill test report (MTR) - mechanical properties
│   ├── Chemical analysis certificate
│   ├── Track through all processing (cutting, machining, heat treat)
│   └── Record in DHR by unit serial number
├── Specialty steel alloys
│   ├── Heat number
│   ├── Melt source certification (US melt verification)
│   ├── Country of origin documentation
│   └── Chemistry/mechanical test reports
├── Nickel superalloys (Inconel, Waspaloy)
│   ├── Heat/lot number
│   ├── Grain size certification
│   ├── Cleanliness certification (inclusions)
│   └── Process traceability
├── Energetic materials (propellants, explosives)
│   ├── Lot number
│   ├── Date of manufacture
│   ├── Stability test results (accelerated aging)
│   ├── Sensitivity test results
│   └── Age life tracking (shelf life management)
├── Electronic components (critical)
│   ├── Date code
│   ├── Lot/batch number
│   ├── Authorized distributor certificate
│   ├── GIDEP alert verification
│   └── OCM (Original Component Manufacturer) traceability
└── Batteries (lithium-ion)
    ├── Cell lot numbers
    ├── Manufacturing date
    ├── Cycle life certification
    └── Safety test results

TRACEABILITY DOCUMENTATION:
├── Device History Record (DHR)
│   ├── Created at start of assembly
│   ├── Contains all material lot numbers
│   ├── All inspection records
│   ├── Test data
│   └── As-built configuration
├── Certificate of Conformance (C of C)
│   ├── Issued at shipment
│   ├── Certifies compliance to spec
│   ├── References DHR
│   └── Signed by QA
└── Material Test Reports (MTR)
    ├── Retained for life of contract + 10 years
    ├── Available for government audit
    └── Cross-referenced to unit serial numbers

COUNTERFEIT PREVENTION:
├── Procure from authorized sources only
├── Verify OCM traceability
├── Visual inspection for authenticity
├── Electrical test for critical parts
├── X-ray/decapsulation for suspect parts
├── Quarantine and report suspect parts
└── Report to GIDEP if counterfeit confirmed
```

---

## 5. TEST PROCEDURES

### 5.1 ACCEPTANCE TEST PROCEDURE - SEABED ARSENAL POD

```
TEST PROCEDURE: ATP-SAP-001
REVISION: A
CLASSIFICATION: UNCLASSIFIED
TEST LOCATION: PDFSAGE Test Facility, Building 3

PREREQUISITES:
├── Unit assembly complete per WI SAP-1-ASSY-001
├── All NCRs dispositioned and closed
├── All calibrated test equipment available (see equipment list)
├── Qualified test personnel assigned
├── Test facility available and configured
└── Customer notification (if witness point)

TEST EQUIPMENT REQUIRED:
├── Hydrostatic test pump (0-2000 psi)
├── Pressure gauge (0-1500 psi, 0.5% accuracy)
├── DC power supply (0-60V, 100A)
├── Digital multimeter (Fluke 87V or equiv)
├── Oscilloscope (100 MHz min)
├── ELF signal generator
├── Acoustic test tank (10m x 5m x 5m min)
├── Environmental chamber (-20°C to +50°C)
├── Data acquisition system
└── Calibration due dates verified

TEST 1: PRESSURE INTEGRITY
├── Equipment: Hydrostatic test stand, pressure transducers
├── Setup:
│   ├── Install test fittings on all penetrations
│   ├── Fill unit with fresh water (deionized)
│   ├── Bleed all air from system
│   └── Install strain gauges at critical locations
├── Procedure:
│   ├── 1.1 Zero all instruments
│   ├── 1.2 Pressurize to 100 psi, hold 5 min, inspect
│   ├── 1.3 Pressurize to 250 psi, hold 5 min, inspect
│   ├── 1.4 Pressurize to 500 psi (operating), hold 15 min
│   │   └── Record: pressure, strain, temp
│   ├── 1.5 Pressurize to 750 psi (proof), hold 15 min
│   │   └── Record: pressure, strain, temp
│   ├── 1.6 Inspect for leaks, deformation
│   ├── 1.7 Depressurize at 50 psi/min
│   └── 1.8 Drain and dry
├── Acceptance Criteria:
│   ├── No leakage at any pressure
│   ├── Pressure drop: <1% over 15 min hold
│   ├── Strain: Within calculated limits
│   └── No permanent deformation
└── Record: Test data sheet ATP-SAP-001-T1

TEST 2: ELECTRICAL SYSTEMS
├── Equipment: DC power supply, DMM, oscilloscope, load bank
├── Setup:
│   ├── Connect shore power simulator
│   ├── Batteries at 100% SOC
│   └── All covers installed
├── Procedure:
│   ├── 2.1 Verify battery voltage: 48V ±2V
│   ├── 2.2 Verify battery capacity: 500 kWh ±5%
│   │   └── Discharge test at rated current
│   ├── 2.3 Power up each subsystem sequentially
│   │   ├── Main controller
│   │   ├── Communication system
│   │   ├── Launch control
│   │   └── Sensors
│   ├── 2.4 Measure current draw (compare to spec)
│   │   ├── Standby: <50W
│   │   └── Active: <15 kW
│   ├── 2.5 Verify status indicators (LED panel)
│   ├── 2.6 Perform BIT on all LRUs
│   │   └── All BIT results: PASS
│   ├── 2.7 Measure power quality
│   │   ├── Ripple: <100mV p-p
│   │   └── Transients: <500mV
│   └── 2.8 Ground continuity test
├── Acceptance Criteria:
│   ├── All voltage rails within spec
│   ├── All BIT pass
│   ├── Current draw within spec
│   └── Ground continuity: <1 ohm
└── Record: Test data sheet ATP-SAP-001-T2

TEST 3: COMMUNICATION SYSTEMS
├── Equipment: ELF signal generator, acoustic modem tester, SATCOM simulator
├── Setup:
│   ├── Unit in RF shielded room OR submerged in test tank
│   ├── Connect to communication test set
│   └── Crypto keys loaded (test keys)
├── Procedure:
│   ├── 3.1 ELF receiver test
│   │   ├── Inject 76 Hz signal at -120 dBm
│   │   ├── Verify decode of standard message
│   │   └── Measure sensitivity threshold
│   ├── 3.2 Acoustic modem test
│   │   ├── Transmit/receive loopback
│   │   ├── Range test: 5 km equivalent
│   │   ├── Data rate: Verify 1200 bps
│   │   └── BER: <10^-6
│   ├── 3.3 SATCOM buoy deployment test (dry)
│   │   ├── Command deployment
│   │   ├── Verify ejection mechanism
│   │   ├── Verify antenna erection
│   │   └── Communication link test
│   ├── 3.4 Crypto initialization
│   │   ├── Load test keys
│   │   ├── Verify encryption active
│   │   └── Verify secure communication
│   └── 3.5 End-to-end message test
│       └── Send/receive standard message set
├── Acceptance Criteria:
│   ├── All communication modes functional
│   ├── Latency: <500ms (acoustic), <2s (SATCOM)
│   ├── BER: <10^-6
│   └── Crypto: Functional
└── Record: Test data sheet ATP-SAP-001-T3

TEST 4: LAUNCH SYSTEM (SIMULATED)
├── Equipment: Dummy missiles (instrumented), high-speed camera
├── Setup:
│   ├── Load dummy missiles in all 8 tubes
│   ├── Install ejection velocity sensors
│   ├── Connect gas supply (nitrogen, 3500 psi)
│   └── Position high-speed cameras
├── Procedure:
│   ├── 4.1 Pre-launch checks
│   │   ├── Verify gas pressure: 3000 ±100 psi
│   │   ├── Verify door mechanism functional
│   │   └── Verify launch computer initialized
│   ├── 4.2 Single tube launch sequence
│   │   ├── Command launch tube 1
│   │   ├── Measure: Door open time (<15 sec)
│   │   ├── Measure: Gas release
│   │   ├── Measure: Ejection velocity (>30 m/s)
│   │   ├── Measure: Door close time (<10 sec)
│   │   └── Verify seal integrity
│   ├── 4.3 Repeat for all tubes (1-8)
│   ├── 4.4 Salvo test (2 tubes rapid)
│   │   ├── Command tubes 3 & 4 rapid sequence
│   │   ├── Verify 2-second interval
│   │   └── Measure both ejection velocities
│   └── 4.5 Door cycling endurance
│       ├── Cycle each door 10x
│       └── Verify seal integrity after cycling
├── Acceptance Criteria:
│   ├── Ejection velocity: >30 m/s all tubes
│   ├── Door open: <15 seconds
│   ├── Door close: <10 seconds
│   ├── Seal integrity: Zero leakage
│   └── Salvo timing: 2.0 ±0.5 seconds
└── Record: Test data sheet ATP-SAP-001-T4, high-speed video

TEST 5: ENDURANCE (72-HOUR BURN-IN)
├── Equipment: Environmental chamber, data logger, monitoring station
├── Setup:
│   ├── Unit powered in operational configuration
│   ├── All telemetry connected
│   ├── Chamber set to 5°C (seabed temperature)
│   └── Continuous data logging enabled
├── Procedure:
│   ├── 5.1 Initialize burn-in
│   │   ├── Start time: ________
│   │   ├── Chamber temperature stable
│   │   └── All systems operational
│   ├── 5.2 Continuous monitoring (72 hours)
│   │   ├── Log all parameters every 60 seconds
│   │   ├── Cycle through operational modes (Q4H)
│   │   │   ├── Standby mode
│   │   │   ├── Alert mode
│   │   │   ├── Communication mode
│   │   │   └── Simulated launch mode
│   │   └── Record any anomalies immediately
│   ├── 5.3 Hourly checks
│   │   ├── Battery SOC
│   │   ├── Temperature distribution
│   │   ├── System status flags
│   │   └── Communication link quality
│   └── 5.4 End of burn-in
│       ├── Full functional test
│       ├── Compare to baseline
│       └── Document any degradation
├── Acceptance Criteria:
│   ├── No failures during 72 hours
│   ├── All parameters within spec continuously
│   ├── No unexpected resets or faults
│   └── Final functional test: PASS
└── Record: Continuous data log ATP-SAP-001-T5

FINAL DISPOSITION:
├── All tests PASS: Release to shipping
│   ├── Complete DD-250 (if government)
│   ├── Issue Certificate of Conformance
│   └── Package per shipping instructions
├── Any test FAIL:
│   ├── Document failure on NCR
│   ├── Determine root cause
│   ├── Repair/rework as required
│   ├── Re-test failed test + regression
│   └── Engineering disposition required
└── Sign-off required:
    ├── Test Engineer
    ├── QA Manager
    └── Program Manager
```

### 5.2 ACCEPTANCE TEST PROCEDURE - LOCUST SCRAMJET

```
TEST PROCEDURE: ATP-LOCUST-001
REVISION: A
CLASSIFICATION: UNCLASSIFIED // FOUO

PREREQUISITES:
├── Unit assembly complete per WI LOCUST-ASSY-001
├── All NCRs closed
├── Warhead section SAFED and verified
└── Test area cleared for explosive operations

TEST 1: STRUCTURAL INTEGRITY
├── Equipment: Load frame (10,000 lb capacity), strain gauges
├── Procedure:
│   ├── 1.1 Install in load frame
│   ├── 1.2 Apply axial load: 2g (1000 kg)
│   │   └── Hold 30 seconds, record strain
│   ├── 1.3 Apply lateral load: 5g (2500 kg)
│   │   └── Hold 30 seconds, record strain
│   ├── 1.4 Verify no permanent deformation
│   │   └── Measure critical dimensions
│   └── 1.5 Visual inspection for cracks/damage
├── Acceptance:
│   ├── Strain within FEA predictions ±10%
│   ├── No visible defects
│   └── Dimensions unchanged
└── Record: ATP-LOCUST-001-T1

TEST 2: PROPULSION FUNCTIONAL (NO IGNITION)
├── Equipment: Engine test stand, fuel flow meter, pressure transducers
├── Procedure:
│   ├── 2.1 Connect to test stand (captive)
│   ├── 2.2 Leak test fuel system
│   │   ├── Pressurize to 500 psi (N2)
│   │   ├── Hold 10 minutes
│   │   └── Leak rate: <0.1 scc/min
│   ├── 2.3 Verify igniter continuity
│   │   ├── Scramjet igniters: 1.2 ±0.2 ohms
│   │   └── Booster igniter: 0.8 ±0.1 ohms
│   ├── 2.4 Simulate engine controller sequence
│   │   ├── Verify valve timing
│   │   ├── Verify fuel flow rate: 2.5 lb/sec
│   │   └── Verify shutdown sequence
│   └── 2.5 Verify booster interface
│       ├── Umbilical connection
│       └── Separation system armed indicator
├── Acceptance: All checks pass per spec
└── Record: ATP-LOCUST-001-T2

TEST 3: GUIDANCE & NAVIGATION
├── Equipment: INS test set, GPS simulator (Spirent), seeker test target
├── Procedure:
│   ├── 3.1 INS alignment test
│   │   ├── Power up INS
│   │   ├── Perform 10-minute alignment
│   │   ├── Compare to surveyed position
│   │   └── Accuracy: <1 arcmin
│   ├── 3.2 GPS acquisition test
│   │   ├── Inject simulated GPS signals
│   │   ├── Verify acquisition: <60 seconds
│   │   ├── Verify position accuracy: <3m CEP
│   │   └── Verify M-code capability
│   ├── 3.3 Navigation accuracy (simulated flight)
│   │   ├── Run 500 km simulated trajectory
│   │   ├── GPS available, then denied
│   │   └── Final error: <15m CEP (INS only)
│   ├── 3.4 Seeker boresight verification
│   │   ├── Point at calibrated target
│   │   ├── Verify boresight: <1 mrad to INS
│   │   └── Track stability: <0.5 mrad jitter
│   └── 3.5 Flight computer BIT
│       ├── Run comprehensive BIT
│       └── All functions: PASS
├── Acceptance:
│   ├── Nav error: <15m CEP
│   ├── Seeker boresight: <1 mrad
│   └── All BIT pass
└── Record: ATP-LOCUST-001-T3

TEST 4: WARHEAD/FUZE SAFE & ARM
├── Equipment: S&A tester, X-ray machine
├── Location: Explosive-rated facility only
├── Procedure:
│   ├── 4.1 Verify S&A in SAFE position
│   │   ├── Visual indicator: SAFE
│   │   └── Electrical: Open circuit to detonator
│   ├── 4.2 X-ray inspection
│   │   ├── Verify internal configuration
│   │   ├── Rotor in safe position
│   │   └── No damage to explosive train
│   ├── 4.3 Command ARM sequence (inhibited)
│   │   ├── Apply all ARM permissives EXCEPT flight
│   │   ├── Verify S&A does NOT arm
│   │   └── Verify interlock function
│   ├── 4.4 Verify no arm without all interlocks
│   │   ├── All-fire: Requires all 4 interlocks
│   │   ├── Test each interlock individually
│   │   └── Document results
│   └── 4.5 Fuze functional test
│       ├── Proximity fuze: Radar check
│       └── Contact fuze: Continuity
├── Acceptance:
│   ├── S&A functions correctly
│   ├── All interlocks verified
│   └── X-ray: Configuration correct
└── Record: ATP-LOCUST-001-T4

TEST 5: ENVIRONMENTAL
├── Equipment: Thermal chamber, vibration table (shaker)
├── Procedure:
│   ├── 5.1 Thermal cycle
│   │   ├── Start: Ambient (25°C)
│   │   ├── Ramp to -40°C at 5°C/min
│   │   ├── Soak: 4 hours at -40°C
│   │   ├── Ramp to +60°C at 5°C/min
│   │   ├── Soak: 4 hours at +60°C
│   │   ├── Return to ambient
│   │   └── Repeat: 3 cycles total
│   ├── 5.2 Functional test (hot/cold)
│   │   ├── BIT at -40°C
│   │   └── BIT at +60°C
│   ├── 5.3 Vibration test
│   │   ├── Per MIL-STD-810H, Method 514.8
│   │   ├── Category 24: Jet aircraft, captive flight
│   │   ├── 3 axes, 60 min per axis
│   │   └── 10-2000 Hz sweep
│   ├── 5.4 Post-vibration functional test
│   │   ├── Full BIT
│   │   ├── Guidance test
│   │   └── Visual inspection
│   └── 5.5 Inspect for damage
│       ├── Check all fasteners
│       ├── Check electrical connectors
│       └── Check structural integrity
├── Acceptance:
│   ├── No failures during or after environmental
│   ├── All BIT pass post-test
│   └── No visible damage
└── Record: ATP-LOCUST-001-T5

FINAL DISPOSITION:
├── All tests PASS: Release to storage/shipping
├── Any test FAIL: NCR, disposition per MRB
└── Sign-off: QA, Manufacturing, Engineering
```

---

## 6. SAFETY REQUIREMENTS

### 6.1 EXPLOSIVE SAFETY

```
PROCEDURE: PDFSAGE-SAF-001
TITLE: Explosive Operations Safety

APPLICABLE STANDARDS:
├── DoD 4145.26-M (Contractors' Safety Manual for Ammunition and Explosives)
├── DoD 6055.09-M (DoD Ammunition and Explosives Safety Standards)
├── OSHA 29 CFR 1910.109 (Explosives and Blasting Agents)
├── NFPA 495 (Explosive Materials Code)
└── ATF 27 CFR Part 555 (Commerce in Explosives)

EXPLOSIVE FACILITY REQUIREMENTS:

QUANTITY-DISTANCE (Q-D):
├── Calculate NEW (Net Explosive Weight) for each operation
├── Operating building to:
│   ├── Public Traffic Route: Per DESR Table
│   ├── Inhabited Building: Per DESR Table
│   └── Other operating buildings: Per DESR Table
├── Magazine distances:
│   ├── Calculate based on NEW stored
│   └── Minimum: 1,100 ft to inhabited building
└── Site plan: PDFSAGE-FAC-001 (approved by DCMA)

LIGHTNING PROTECTION:
├── Lightning protection system (LPS) installed
│   ├── Air terminals (strike termination)
│   ├── Down conductors
│   └── Grounding system (<10 ohms)
├── Lightning warning system
│   ├── Electric field mill
│   ├── Alert at 8 kV/m
│   ├── Alarm at 4 miles
│   └── All-clear: 30 min after last strike
├── Personnel evacuation procedure
│   └── Move to non-explosive area within 10 min
└── Operations suspended during lightning warning

FIRE SUPPRESSION:
├── Assembly areas:
│   ├── Deluge system (automatic)
│   ├── Fusible link activation
│   └── Manual pull stations
├── Magazine buildings:
│   ├── No automatic suppression (thermal shock hazard)
│   ├── Rely on separation distance
│   └── Portable extinguishers outside
├── Portable extinguishers:
│   ├── ABC dry chemical
│   ├── Located at exits
│   └── Inspected monthly
└── Fire department coordination
    └── Pre-incident plan on file

CONSTRUCTION:
├── Blow-out walls (3 sides minimum)
│   ├── Frangible panels
│   └── Direct blast away from occupied areas
├── Flooring:
│   ├── Non-sparking (conductive)
│   ├── Grounded
│   └── Static-dissipative (10^5 to 10^9 ohms)
├── Electrical:
│   ├── Explosion-proof fixtures (Class II, Div 1)
│   ├── No open switches
│   └── Emergency shut-off outside building
├── Ventilation:
│   ├── 10 air changes per hour minimum
│   └── No recirculation
└── Static grounding:
    ├── All equipment bonded
    ├── Personnel grounding points
    └── Tested annually

PERSONNEL REQUIREMENTS:
├── Training:
│   ├── Initial: 40 hours (basic explosives safety)
│   ├── Annual refresher: 8 hours
│   ├── Specific explosives: As required
│   └── Certification card issued
├── Medical:
│   ├── No disqualifying conditions per DoD
│   ├── Drug testing: Random
│   └── Annual physical
├── Two-person rule:
│   ├── Never alone with exposed explosives
│   ├── Buddy system at all times
│   └── Visual contact maintained
└── PPE:
    ├── Cotton clothing (no synthetics)
    ├── Conductive footwear
    ├── No jewelry, watches
    ├── Safety glasses
    └── Hearing protection (if required)

OPERATIONAL REQUIREMENTS:
├── Authorized operations only (SOP approved)
├── Quantity limits per room (posted)
├── Compatibility groups respected (DoD 6055.09)
│   ├── Group A: With Group A only
│   ├── Group B: With B, C, D, E, F, G
│   └── (Reference full compatibility chart)
├── Surveillance: 100% of operations
├── Tools: Non-sparking (brass, beryllium copper)
├── No exposed explosive: <4 hours
└── Emergency procedures posted

EMERGENCY PROCEDURES:
├── Fire:
│   ├── Evacuate immediately
│   ├── Sound alarm
│   ├── Call 911 and security
│   └── Fight fire only if trained and safe
├── Accident (injury):
│   ├── Render safe if possible
│   ├── First aid
│   ├── Do not move injured if spinal
│   └── Call emergency services
├── Spill (propellant, etc.):
│   ├── Evacuate area
│   ├── Notify safety officer
│   ├── Cleanup by trained personnel only
│   └── Document incident
└── Suspicious item:
    ├── Do not touch
    ├── Evacuate area
    ├── Call EOD / bomb squad
    └── Establish 300 ft cordon
```

### 6.2 GENERAL SAFETY

```
PROCEDURE: PDFSAGE-SAF-002
TITLE: General Safety Program

HAZARD IDENTIFICATION:
├── Electrical hazards: >50V
│   ├── Lock-out/tag-out (LOTO) required
│   ├── NFPA 70E arc flash
│   └── Annual electrical safety training
├── Chemical hazards:
│   ├── SDS on file for all chemicals
│   ├── Proper storage (flammables, acids, etc.)
│   ├── Secondary containment
│   └── Hazard communication training
├── Mechanical hazards:
│   ├── Machine guarding per OSHA
│   ├── Pinch points identified
│   ├── Emergency stops
│   └── Lockout during maintenance
├── Pressure hazards:
│   ├── Pneumatic systems: <150 psi or guarded
│   ├── Hydraulic systems: Hose guards
│   └── Pressure relief devices
├── Thermal hazards:
│   ├── Hot surfaces marked
│   ├── PPE required (gloves, face shield)
│   └── Cool-down procedures
├── Radiation hazards:
│   ├── Laser: Class 3B/4 require controls
│   ├── RF: Power density limits
│   ├── Radioactive: NRC license if applicable
│   └── Radiation safety officer assigned
└── Ergonomic hazards:
    ├── Lifting limit: 50 lbs (one person)
    ├── Repetitive motion: Job rotation
    └── Workstation setup

REQUIRED TRAINING:
├── New hire safety orientation: 8 hours
│   ├── Company safety policy
│   ├── Emergency procedures
│   ├── Hazard communication
│   ├── PPE requirements
│   └── Reporting procedures
├── Job-specific hazards: 4 hours
│   ├── Specific to work area
│   ├── Before starting work
│   └── Documented acknowledgment
├── Annual refresher: 2 hours
│   ├── Policy updates
│   ├── Incident review
│   └── Re-certification
├── Specialized training (as required):
│   ├── Forklift certification (OSHA)
│   ├── Crane/hoist operation (OSHA)
│   ├── Confined space entry
│   ├── Hazardous waste handling (RCRA)
│   ├── Respiratory protection (fit test annual)
│   ├── Fall protection
│   └── First aid/CPR/AED
└── Documentation:
    ├── Training records maintained
    ├── Certification cards issued
    └── Matrix tracks requirements

PPE REQUIREMENTS BY AREA:
├── Manufacturing floor (general):
│   ├── Safety glasses (ANSI Z87.1)
│   ├── Steel-toe boots
│   ├── Long pants
│   └── Hearing protection (>85 dBA areas)
├── Clean room:
│   ├── Bunny suit or smock
│   ├── Booties
│   ├── Hair net/beard cover
│   └── Gloves (nitrile)
├── Propulsion test:
│   ├── Face shield
│   ├── Flame-resistant clothing (FRC)
│   ├── Heat-resistant gloves
│   └── Hearing protection (double)
├── Electronics assembly:
│   ├── ESD smock
│   ├── Wrist strap (tested)
│   ├── ESD-safe footwear
│   └── Safety glasses
├── Explosive operations:
│   ├── Cotton clothing only
│   ├── Conductive footwear
│   ├── No metal jewelry
│   └── Grounding straps
├── Welding:
│   ├── Welding hood (shade per process)
│   ├── Welding gloves
│   ├── Leather apron
│   ├── Steel-toe boots
│   └── Respiratory protection (if required)
└── Painting/coating:
    ├── Respirator (organic vapor)
    ├── Chemical-resistant gloves
    ├── Tyvek suit
    └── Safety glasses

INCIDENT REPORTING:
├── All injuries: Report immediately
│   ├── First aid administered
│   ├── Supervisor notification
│   └── Incident report within 24 hours
├── Near-misses: Report within 24 hours
│   ├── No injury occurred
│   ├── But could have
│   └── Used to prevent future incidents
├── Investigation:
│   ├── Within 48 hours of incident
│   ├── Root cause analysis
│   ├── Corrective actions identified
│   └── Follow-up verification
├── OSHA recordkeeping:
│   ├── OSHA 300 Log maintained
│   ├── OSHA 300A posted (Feb 1 - Apr 30)
│   └── Retained 5 years
└── Serious incidents:
    ├── Fatality: OSHA notification within 8 hours
    ├── Hospitalization: OSHA within 24 hours
    ├── Amputation: OSHA within 24 hours
    └── Loss of eye: OSHA within 24 hours
```

---

## 7. CONFIGURATION MANAGEMENT

### 7.1 CONFIGURATION CONTROL

```
PROCEDURE: PDFSAGE-CM-001
TITLE: Configuration Management

CONFIGURATION ITEMS:
├── Hardware: All deliverable hardware
├── Software: All embedded and support software
├── Documentation: Drawings, specs, procedures
├── Test equipment: Special test equipment (STE)
└── Firmware: All programmable devices

BASELINE MANAGEMENT:
├── Functional Baseline:
│   ├── System-level requirements
│   ├── Established at SRR
│   └── Controlled by customer
├── Allocated Baseline:
│   ├── Subsystem specifications
│   ├── Established at PDR
│   └── Controlled by CCB
├── Product Baseline:
│   ├── As-built configuration
│   ├── Established at CDR/production
│   └── Controlled by CCB
└── All baselines:
    ├── Under formal version control
    ├── Changes require CCB approval
    └── Audit trail maintained

CHANGE CONTROL PROCESS:

ENGINEERING CHANGE PROPOSAL (ECP):
├── Originator submits ECP form (PDFSAGE-CM-ECP)
├── Required information:
│   ├── Description of change
│   ├── Reason for change
│   ├── Affected documents/hardware
│   ├── Cost impact
│   ├── Schedule impact
│   └── Performance impact
├── Classification:
│   ├── Class I: Affects performance, cost, schedule - Customer approval required
│   └── Class II: Editorial, minor - Internal approval only
├── CCB review:
│   ├── Meets weekly (or as needed)
│   ├── Members: Engineering, QA, Production, PM
│   └── Decision: Approve, Reject, Defer, RFI
└── Customer approval (Class I):
    ├── Submit to customer
    ├── Await approval before implementation
    └── May require contract modification

ENGINEERING CHANGE ORDER (ECO):
├── Approved ECP becomes ECO
├── ECO contains:
│   ├── Change instructions
│   ├── Effectivity (serial numbers, date)
│   ├── Affected documents list
│   └── Implementation plan
├── Document updates:
│   ├── Drawings revised
│   ├── Specs updated
│   ├── BOMs updated
│   └── Procedures revised
└── Implementation:
    ├── Production notified
    ├── Retrofit plan (if applicable)
    └── Training updated

DEVIATION/WAIVER:
├── Deviation: Before production (anticipated nonconformance)
├── Waiver: After production (discovered nonconformance)
├── Request form: PDFSAGE-CM-DEV
├── Approval required:
│   ├── Engineering
│   ├── QA
│   └── Customer (if contractual)
├── Limitations:
│   ├── Time-limited or quantity-limited
│   └── Does not change baseline
└── Tracking:
    ├── Log maintained
    └── Reported to customer

DOCUMENT CONTROL:
├── Drawing control:
│   ├── All drawings in PLM system
│   ├── Release via formal process
│   ├── Revision control (A, B, C...)
│   └── Red-line prohibition (except shop copy)
├── Specification control:
│   ├── Numbered per PDFSAGE system
│   ├── Revision tracked
│   └── Controlled distribution
├── Procedure control:
│   ├── Approved before use
│   ├── Training on revisions
│   └── Obsolete removed from work areas
└── Obsolete documents:
    ├── Stamped "OBSOLETE"
    ├── Archived (not destroyed)
    └── Retained per contract requirements

AS-BUILT RECORDS:
├── Serial number:
│   ├── Assigned at start of assembly
│   ├── Unique identifier
│   └── Marked on nameplate
├── Component tracking:
│   ├── All serialized components recorded
│   ├── Lot numbers for batch items
│   └── Software versions
├── Deviations recorded:
│   ├── Any approved deviations
│   ├── Rework documented
│   └── Repair documented
├── Test data:
│   ├── All test results linked
│   ├── Pass/fail documented
│   └── Anomalies noted
└── Final configuration:
    ├── Configuration audit at delivery
    ├── Matches drawing revision
    └── Certificate of Conformance issued

CONFIGURATION AUDIT:
├── Functional Configuration Audit (FCA):
│   ├── Verifies performance meets spec
│   ├── Before Product Baseline
│   └── Customer participation
├── Physical Configuration Audit (PCA):
│   ├── Verifies as-built matches drawings
│   ├── Before delivery
│   └── Inspection of hardware
└── Audit discrepancies:
    ├── Documented
    ├── Resolved before delivery
    └── May require ECP
```

---

**Document Prepared For:** PDFSAge Inc
**Prepared By:** Manufacturing Engineering
**Document Number:** PDFSAGE-MFG-001
**Date:** 2026-01-02
**Next Review:** 2026-07-01

---

## REVISION HISTORY

| Rev | Date | Description | Author |
|-----|------|-------------|--------|
| 1.0 | 2026-01-02 | Initial release | Manufacturing Engineering |

---

## APPROVAL

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Director, Manufacturing | _____________ | _____________ | _____________ |
| Director, Quality | _____________ | _____________ | _____________ |
| Director, Engineering | _____________ | _____________ | _____________ |
| Program Manager | _____________ | _____________ | _____________ |
