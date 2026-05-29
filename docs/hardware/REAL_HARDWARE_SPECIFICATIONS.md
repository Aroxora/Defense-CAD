# Real Hardware Specifications CAD

## Document Purpose

This Computer-Aided Documentation (CAD) provides complete real hardware specifications for all 8 subsystems required for BVR precision engagement operations. Each subsystem includes physical hardware components, interface specifications, mounting requirements, and verification test procedures.

All specifications are derived from or equivalent to verified real-world hardware from:
- **American Systems:** F-35, F-22, E-3, EC-130H, ALQ-99/249 programs
- **Chinese Systems:** J-20, J-16D, KJ-500, Y-8G/GX platforms

**Classification:** Hardware Integration Reference
**Revision:** 1.1
**Date:** 2025-12-28

---

## Real Hardware Equivalents Summary

| Subsystem | US Reference System | Chinese Reference System |
|-----------|---------------------|--------------------------|
| HW-1 GPS Timing | Rockwell Collins GPS-4000S, Trimble Thunderbolt | BeiDou BD-3 MEO, CETC-54 GPSDO |
| HW-2 RF Sensors | ALR-94 (F-22), ASQ-239 EW (F-35) | CETC-14 KLC series, AVIC ESM |
| HW-3 Antenna Array | AN/APG-81 AESA (F-35), AN/APG-77 (F-22) | Type 1475 AESA (J-20), Type 1493 |
| HW-4 Datalink | MADL (F-35), Link-16 MIDS-JTRS | JIDS (Chinese Link-16 equiv), ACDL |
| HW-5 Weapon System | MIL-STD-1760 / AIM-120D | PL-15, PL-21 integration standard |
| HW-6 Tracking Processor | AN/APG-81 processor, BAE CMSP | CETC-14 mission computer |
| HW-7 EW Suite | AN/ALQ-249 NGJ, AN/ALQ-218 | CETC-29 jamming pod, SAC EW |
| HW-8 Power Management | F-35 EPGS (150 kVA), F-22 VSCF | WS-15 integrated power, J-20 EPGS |

---

## Table of Contents

1. [HW-1: GPS Timing Synchronization](#hw-1-gps-timing-synchronization)
2. [HW-2: RF Sensors](#hw-2-rf-sensors)
3. [HW-3: Antenna Array](#hw-3-antenna-array)
4. [HW-4: Datalink](#hw-4-datalink)
5. [HW-5: Weapon System](#hw-5-weapon-system)
6. [HW-6: Tracking Processor](#hw-6-tracking-processor)
7. [HW-7: EW Suite](#hw-7-ew-suite)
8. [HW-8: Power Management](#hw-8-power-management)
9. [Integration Matrix](#integration-matrix)
10. [Hardware Verification Procedures](#hardware-verification-procedures)

---

## HW-1: GPS Timing Synchronization

### 1.1 System Overview

Provides nanosecond-precision time synchronization across all platform subsystems for TDOA geolocation and coherent sensor fusion.

**Real Hardware Equivalents:**
- **US:** Rockwell Collins GPS-4000S (F-22/F-35), Trimble Thunderbolt E, Symmetricom XLi
- **China:** BeiDou BD-3 MEO chipset, CETC-54 Institute GPSDO, UniStrong UB4B0 receiver

### 1.2 Primary Components

#### 1.2.1 GPS/BeiDou Receiver Module

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | Rockwell Collins GPS-4000S | CETC-54 BD3-MSA |
| **Type** | Multi-constellation GNSS | BeiDou-3 + GPS/GLONASS |
| **Constellations** | GPS L1/L2/L5 + GLONASS | BeiDou B1C/B2a/B3I + GPS |
| **Channels** | 184 concurrent | 128 concurrent |
| **Position Accuracy** | 1.5 m CEP | 2.0 m CEP |
| **Timing Accuracy** | < 5 ns RMS to UTC | < 10 ns RMS to BDT/UTC |
| **1PPS Output** | 10 ns RMS jitter | 15 ns RMS jitter |
| **Anti-Jam** | SAASM M-Code capable | BeiDou regional auth signal |
| **Update Rate** | 10 Hz nav, 100 Hz raw | 10 Hz nav, 50 Hz raw |
| **Operating Temp** | -40°C to +85°C | -40°C to +80°C |
| **Power** | 1.2W @ 3.3V | 1.5W @ 3.3V |
| **Interface** | RS-422, PPS (50Ω) | RS-422, PPS (50Ω) |

#### 1.2.2 GPS-Disciplined Oscillator (GPSDO)

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | Symmetricom/Microsemi XLi | CETC-10 BDO-100 |
| **Type** | OCXO + Rubidium hybrid | OCXO with BeiDou discipline |
| **Output Frequency** | 10 MHz, 100 MHz | 10 MHz, 100 MHz |
| **Short-term Stability** | 1 × 10⁻¹² @ 1s | 5 × 10⁻¹² @ 1s |
| **Long-term Stability** | 1 × 10⁻¹⁴ @ 1 day | 5 × 10⁻¹⁴ @ 1 day |
| **Holdover Drift** | < 1 μs/day | < 5 μs/day |
| **Phase Noise** | -110 dBc/Hz @ 10 Hz | -105 dBc/Hz @ 10 Hz |
| **1PPS Output** | < 2 ns RMS | < 5 ns RMS |
| **Lock Time** | < 5 minutes | < 8 minutes |
| **Power** | 8W steady, 15W warmup | 12W steady, 20W warmup |
| **Operating Temp** | -40°C to +75°C | -40°C to +70°C |

#### 1.2.3 Time Distribution Unit (TDU)

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | Spectracom SecureSync | CETC-54 TDU-200 |
| **Type** | IEEE 1588v2 grandmaster | IEEE 1588v2 / BeiDou sync |
| **Fanout** | 16x 1PPS, 8x 10 MHz | 12x 1PPS, 6x 10 MHz |
| **Added Jitter** | < 500 ps | < 1 ns |
| **Skew Between Outputs** | < 100 ps | < 200 ps |
| **Network Sync** | PTP (< 100 ns) | PTP (< 200 ns) |
| **Power** | 25W @ 28 VDC | 35W @ 28 VDC |
| **Form Factor** | 3U VME / 1/2 ATR | 3U CPCI / 1/2 ATR |

### 1.3 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GPS TIMING SUBSYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ GPS Antenna │───▶│ GPS Receiver│───▶│ GPSDO               │  │
│  │ (L1/L2/L5)  │    │ Module      │    │ (10 MHz Master Ref) │  │
│  └─────────────┘    └─────────────┘    └─────────┬───────────┘  │
│                                                   │              │
│                                                   ▼              │
│                                        ┌─────────────────────┐  │
│                                        │ Time Distribution   │  │
│                                        │ Unit (TDU)          │  │
│                                        └─────────┬───────────┘  │
│                                                   │              │
│         ┌─────────────────────────────────────────┼──────┐      │
│         │                     │                   │      │      │
│         ▼                     ▼                   ▼      ▼      │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  ┌─────────┐  │
│  │ RF Sensors  │  │ Antenna     │  │ Tracking  │  │ Datalink│  │
│  │ (1PPS+10MHz)│  │ Array       │  │ Processor │  │         │  │
│  └─────────────┘  └─────────────┘  └───────────┘  └─────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 Interface Specifications

| Signal | Type | Level | Impedance | Connector |
|--------|------|-------|-----------|-----------|
| GPS Antenna | RF | -130 to -120 dBm | 50 Ω | TNC female |
| 1PPS Master | Digital | 3.3V LVTTL | 50 Ω | SMA female |
| 10 MHz Master | Sine | 7 dBm ±1 dB | 50 Ω | SMA female |
| 1PPS Fanout (×16) | Digital | RS-422 differential | 100 Ω | D-sub 37 |
| 10 MHz Fanout (×8) | Sine | 7 dBm | 50 Ω | SMA female |
| PTP Network | Ethernet | 1000BASE-T | 100 Ω | RJ-45 |
| Serial Control | RS-232/422 | ±5V/±3V | 100 Ω | D-sub 9 |

### 1.5 Performance Verification

| Test | Procedure | Pass Criteria |
|------|-----------|---------------|
| Timing Accuracy | Compare 1PPS to USNO reference | < 20 ns RMS |
| Holdover Test | Remove GPS for 1 hour, measure drift | < 10 μs total |
| Fanout Skew | Measure all 1PPS outputs simultaneously | < 500 ps max skew |
| Phase Noise | Spectrum analyzer @ 10 MHz | < -110 dBc/Hz @ 10 Hz |
| Temperature Cycle | -40°C to +70°C, measure timing | Spec maintained |

---

## HW-2: RF Sensors

### 2.1 System Overview

High-sensitivity RF receivers for detection and characterization of target emissions in the Ku-band (14-15 GHz) and supporting frequency ranges.

**Real Hardware Equivalents:**
- **US:** AN/ALR-94 (F-22), AN/ASQ-239 Barracuda (F-35), BAE Systems DRS
- **China:** CETC-14 KLC-7 series, AVIC Leihua ESM, CETC-29 receivers

### 2.2 Primary Components

#### 2.2.1 Wideband RF Front-End

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | BAE ALR-94 derivative | CETC-14 KLC-7A |
| **Frequency Range** | 0.5-40 GHz (full) | 2-18 GHz (primary) |
| **Instantaneous BW** | 2 GHz | 1 GHz |
| **Noise Figure** | 3.0 dB | 4.0 dB |
| **Sensitivity** | -125 dBm (10 MHz) | -120 dBm (10 MHz) |
| **Dynamic Range** | 95 dB SFDR | 85 dB SFDR |
| **IP3 (Input)** | +15 dBm | +10 dBm |
| **Gain** | 50 dB (AGC) | 45 dB (AGC) |
| **LO Frequency** | Multi-synth, 100 ns tune | Multi-synth, 500 ns tune |
| **Power** | 10W @ 28 VDC | 15W @ 28 VDC |
| **Operating Temp** | -54°C to +71°C | -40°C to +70°C |

#### 2.2.2 Digital IF Processor

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | Mercury RFSoC | CETC-38 DSP platform |
| **IF Input Range** | DC-6 GHz direct | 2-4 GHz IF |
| **ADC Resolution** | 14-bit, 8 GSPS | 12-bit, 5 GSPS |
| **Digital Channels** | 16 concurrent DDC | 8 concurrent DDC |
| **Channel Bandwidth** | 10-1000 MHz | 20-500 MHz |
| **Spurious-Free DR** | 78 dB | 72 dB |
| **Processing** | Xilinx Versal AI Core | Xilinx UltraScale+ / domestic FPGA |
| **Latency** | < 2 μs | < 5 μs |
| **Power** | 40W @ 28 VDC | 50W @ 28 VDC |
| **Interface** | 100GbE, PCIe Gen5 | 40GbE, PCIe Gen4 |

#### 2.2.3 Calibration Subsystem

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | Built-in (ALR-94 style) | CETC internal cal system |
| **Calibration Source** | Noise diode + DRFM | Noise diode + CW |
| **Noise Diode ENR** | 18 dB @ 18 GHz | 15 dB @ 15 GHz |
| **CW Reference Accuracy** | ±0.3 dB traceable | ±0.5 dB traceable |
| **Calibration Cycle** | < 15 seconds | < 30 seconds |
| **Cal Injection** | Pre-LNA coupler | Pre-LNA coupler |
| **Validity Period** | 10 minutes | 5 minutes |

### 2.3 System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                       RF SENSOR SUBSYSTEM                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────┐    ┌────────────────────────────────────────┐   │
│  │ Antenna Port │───▶│ RF Front-End Assembly                  │   │
│  │ (Ku-band)    │    │ ┌─────┐  ┌─────┐  ┌─────┐  ┌────────┐ │   │
│  └──────────────┘    │ │ LNA │─▶│ BPF │─▶│Mixer│─▶│IF Amp  │ │   │
│         ▲            │ └─────┘  └─────┘  └──┬──┘  └───┬────┘ │   │
│         │            │                      │         │      │   │
│  ┌──────┴───────┐    │              ┌───────┴───┐     │      │   │
│  │ Calibration  │───▶│              │ LO Synth  │     │      │   │
│  │ Injection    │    │              │ 10-16 GHz │     │      │   │
│  └──────────────┘    │              └───────────┘     │      │   │
│                      └────────────────────────────────┼──────┘   │
│                                                       │          │
│                      ┌────────────────────────────────▼──────┐   │
│                      │ Digital IF Processor                  │   │
│                      │ ┌─────┐  ┌─────┐  ┌─────┐  ┌────────┐ │   │
│                      │ │ ADC │─▶│ DDC │─▶│ FFT │─▶│Detector│ │   │
│                      │ │6.4G │  │ ×8  │  │     │  │        │ │   │
│                      │ └─────┘  └─────┘  └─────┘  └───┬────┘ │   │
│                      └───────────────────────────────────────┘   │
│                                                       │          │
│                                                       ▼          │
│                                              ┌───────────────┐   │
│                                              │ Detection     │   │
│                                              │ Output to     │   │
│                                              │ Tracking Proc │   │
│                                              └───────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 2.4 Interface Specifications

| Signal | Type | Level | Impedance | Connector |
|--------|------|-------|-----------|-----------|
| RF Input (Ku-band) | RF | -120 to -30 dBm | 50 Ω | SMA female |
| IF Output | RF | 0 to +10 dBm | 50 Ω | SMA female |
| 10 MHz Reference | Sine | 7 dBm | 50 Ω | SMA female |
| 1PPS Sync | Digital | RS-422 | 100 Ω | D-sub 9 |
| 10GbE Data | Ethernet | 10GBASE-SR | 50/125 μm | LC duplex |
| Control/Status | Ethernet | 1000BASE-T | 100 Ω | RJ-45 |
| Cal Enable | Digital | 5V TTL | 1 kΩ | SMA female |

### 2.5 Performance Verification

| Test | Procedure | Pass Criteria |
|------|-----------|---------------|
| Sensitivity | Inject -120 dBm CW, measure detection | POD > 95% |
| Dynamic Range | Two-tone test, measure SFDR | > 85 dB |
| Calibration Accuracy | Compare to traceable power meter | ±1 dB |
| Frequency Accuracy | Inject known CW, verify measurement | ±100 Hz |
| Noise Figure | Y-factor with calibrated noise source | < 4 dB |

---

## HW-3: Antenna Array

### 3.1 System Overview

64-element phased array antenna for directional reception, angle-of-arrival measurement, and adaptive null steering.

**Real Hardware Equivalents:**
- **US:** AN/APG-81 AESA (F-35), AN/APG-77 (F-22), AN/APG-83 SABR (F-16V)
- **China:** Type 1475 KLJ-7A (J-10C), Type 1493 (J-20), CETC-14 arrays

### 3.2 Primary Components

#### 3.2.1 Array Aperture

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | AN/APG-81 (F-35) | Type 1475/1493 (J-20) |
| **Configuration** | 1200+ T/R modules | 1000-1800 T/R modules |
| **Element Type** | GaN MMIC dual-pol | GaAs/GaN hybrid |
| **Element Spacing** | λ/2 optimized | λ/2 standard |
| **Aperture Size** | ~0.8m diameter | ~0.9m diameter |
| **Frequency Range** | 8-12 GHz (X-band) | 8-12 GHz (X-band) |
| **Polarization** | Dual-linear adaptive | Dual-linear |
| **Array Gain** | 35-38 dBi | 33-36 dBi |
| **Beamwidth (3 dB)** | 2.5° × 2.5° | 3.0° × 3.0° |
| **Scan Range** | ±60° Az, ±60° El | ±60° Az, ±50° El |
| **Sidelobe Level** | -40 dB (adaptive) | -35 dB (standard) |
| **Cross-pol Isolation** | > 30 dB | > 25 dB |

#### 3.2.2 T/R Modules

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | Raytheon GaN MMIC | CETC-13/55 GaAs/GaN |
| **Frequency** | 8-12 GHz (X-band) | 8-12 GHz (X-band) |
| **Peak TX Power** | 10W per element | 5-8W per element |
| **Receive NF** | 2.0 dB | 2.8 dB |
| **Phase Shifter** | 7-bit (2.8° res) | 6-bit (5.625° res) |
| **Attenuator** | 6-bit (0.25 dB) | 5-bit (0.5 dB) |
| **Phase Accuracy** | ±2° RMS | ±4° RMS |
| **Amplitude Accuracy** | ±0.25 dB RMS | ±0.4 dB RMS |
| **Switching Speed** | < 100 ns | < 500 ns |
| **Power per Module** | 1.2W (RX), 15W (TX) | 1.0W (RX), 12W (TX) |
| **MTBF** | > 150,000 hours | > 80,000 hours |

#### 3.2.3 Beamformer Controller

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | Northrop Grumman DBF | CETC-14 digital BF |
| **Type** | Full digital beamformer | Hybrid analog/digital |
| **Beam Update Rate** | 100 kHz (10 μs) | 20 kHz (50 μs) |
| **Simultaneous Beams** | 8 independent | 4 independent |
| **Null Steering** | 16 adaptive nulls | 8 adaptive nulls |
| **Null Depth** | > 45 dB | > 30 dB |
| **Null Convergence** | < 1 ms | < 10 ms |
| **Algorithm** | MVDR + AI-adaptive | SMI, MVDR |
| **Power** | 50W | 35W |

### 3.3 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANTENNA ARRAY SUBSYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 8 × 8 Element Array                      │   │
│  │  ┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐              │   │
│  │  │T/R││T/R││T/R││T/R││T/R││T/R││T/R││T/R│  Row 1       │   │
│  │  └───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘              │   │
│  │  ┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐┌───┐              │   │
│  │  │T/R││T/R││T/R││T/R││T/R││T/R││T/R││T/R│  Row 2       │   │
│  │  └───┘└───┘└───┘└───┘└───┘└───┘└───┘└───┘              │   │
│  │                    ... (×8 rows)                         │   │
│  └─────────────────────────────┬───────────────────────────┘   │
│                                │                                │
│                 ┌──────────────┴──────────────┐                │
│                 │   64-Channel RF Combiner    │                │
│                 │   (Σ, Δaz, Δel outputs)     │                │
│                 └──────────────┬──────────────┘                │
│                                │                                │
│         ┌──────────────────────┼──────────────────────┐        │
│         ▼                      ▼                      ▼        │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐  │
│  │ Sum Channel │       │ Δ Azimuth   │       │ Δ Elevation │  │
│  │ (Main Beam) │       │ (Monopulse) │       │ (Monopulse) │  │
│  └──────┬──────┘       └──────┬──────┘       └──────┬──────┘  │
│         │                     │                     │          │
│         └─────────────────────┼─────────────────────┘          │
│                               ▼                                 │
│                    ┌─────────────────────┐                     │
│                    │ Beamformer          │                     │
│                    │ Controller          │◀── Beam Commands    │
│                    │ (FPGA + DSP)        │                     │
│                    └─────────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 Interface Specifications

| Signal | Type | Level | Impedance | Connector |
|--------|------|-------|-----------|-----------|
| Sum RF Out | RF | 0 to +10 dBm | 50 Ω | SMA female |
| Delta Az RF | RF | -10 to +5 dBm | 50 Ω | SMA female |
| Delta El RF | RF | -10 to +5 dBm | 50 Ω | SMA female |
| 10 MHz Reference | Sine | 7 dBm | 50 Ω | SMA female |
| 1PPS Sync | Digital | RS-422 | 100 Ω | D-sub 9 |
| Beam Control | Ethernet | 1000BASE-T | 100 Ω | RJ-45 |
| Element Data | PCIe | Gen3 x4 | Differential | PCIE x4 |
| Power (28V) | DC | 28 VDC ±2V | - | MS27467T |

### 3.5 Performance Verification

| Test | Procedure | Pass Criteria |
|------|-----------|---------------|
| Element Health | Built-in test of all 64 elements | > 98% operational |
| Beam Pointing | Measure pattern on antenna range | ±0.5° accuracy |
| Null Depth | Insert interferer, measure null | > 30 dB |
| Sidelobe Level | Full pattern measurement | < -25 dB |
| Gain Calibration | Measure gain vs. reference horn | ±0.5 dB |

---

## HW-4: Datalink

### 4.1 System Overview

Integrated weapon datalink for mid-course guidance updates and two-way target data exchange.

**Real Hardware Equivalents:**
- **F-35 / AIM-120D:** MADL (Multi-function Advanced Data Link) for intra-flight + dedicated weapon uplink via AN/APG-81
- **J-20 / PL-15:** ACDL (Air Combat Data Link) + integrated PL-15 two-way datalink via Type 1475 AESA

### 4.2 Primary Components

#### 4.2.1 Intra-Flight Datalink (Platform-to-Platform)

| Parameter | F-35 MADL | J-20 ACDL |
|-----------|-----------|-----------|
| **Designation** | MADL (Northrop Grumman) | ACDL (CETC-10) |
| **Frequency** | Ku-band (14.5-15.5 GHz) | Ku-band (estimated similar) |
| **Waveform** | Directional LPI/LPD | Directional LPI |
| **TX Power** | 2W (+33 dBm) | 5W (+37 dBm) |
| **Antenna** | 6 distributed apertures | 4 conformal apertures |
| **Beamwidth** | 2-5° (steered) | 3-6° (steered) |
| **Sidelobe Level** | -30 dB (adaptive null) | -25 dB |
| **Data Rate** | 10-100 Mbps | 2-50 Mbps (est.) |
| **Range** | 200+ km (clear LOS) | 150+ km (est.) |
| **Latency** | < 10 ms | < 20 ms (est.) |
| **Nodes Supported** | 4-ship standard, up to 8 | 4-ship standard |
| **Encryption** | NSA Type 1 | SM4/ZUC Chinese standard |

#### 4.2.2 Weapon Datalink (Platform-to-Missile)

| Parameter | F-35 to AIM-120D | J-20 to PL-15 |
|-----------|------------------|---------------|
| **Designation** | AN/APG-81 integrated uplink | Type 1475 integrated uplink |
| **Frequency** | X-band (via radar) | C/X-band (dedicated) |
| **TX Power** | 10W (+40 dBm) effective | 10W (+40 dBm) |
| **Modulation** | BPSK + TDM | OQPSK + FH |
| **Data Rate** | 16-64 kbps uplink | 100 kbps uplink |
| **Update Rate** | 2 Hz (mid-course) | 1-2 Hz (mid-course) |
| **Range** | 160+ km | 200+ km |
| **Two-Way** | Yes (AIM-120D seeker data) | Yes (PL-15 AESA data) |
| **Downlink Data** | Seeker track, status | Seeker track, target class |
| **Link Margin** | > 10 dB @ max range | > 10 dB @ max range |

#### 4.2.3 Weapon Datalink Message Content

| Field | AIM-120D Uplink | PL-15 Uplink |
|-------|-----------------|--------------|
| **Target Position** | ECEF (24 bytes) | WGS-84/CGCS2000 (24 bytes) |
| **Target Velocity** | NED vector (12 bytes) | ENU vector (12 bytes) |
| **Covariance** | Diagonal (12 bytes) | Full 3x3 (36 bytes) |
| **Time Tag** | GPS TOW (4 bytes) | BeiDou/GPS (4 bytes) |
| **Target ID** | Track number (2 bytes) | Track number (2 bytes) |
| **Mode Command** | Seeker on/off (1 byte) | Seeker/autonomy (2 bytes) |
| **Self-Destruct** | Yes (encrypted) | Yes (encrypted) |
| **Total Size** | ~64 bytes + FEC | ~100 bytes + FEC |

#### 4.2.4 Weapon Datalink Downlink (Missile-to-Platform)

| Field | AIM-120D Downlink | PL-15 Downlink |
|-------|-------------------|----------------|
| **Seeker Status** | Lock/search/track | Lock/search/track/classify |
| **Target Position** | Seeker-derived | AESA-derived multi-target |
| **Target RCS** | Estimated (coarse) | Estimated (fine) |
| **Missile State** | INS position, fuel | INS position, fuel, health |
| **Data Rate** | 8-16 kbps | 50 kbps (est.) |
| **Latency** | < 100 ms | < 100 ms |

#### 4.2.5 Link Controller

| Parameter | F-35 System | J-20 System |
|-----------|-------------|-------------|
| **Integration** | ICP-embedded | Dedicated processor |
| **Protocol** | MIL-STD-1553B + fiber | 1553B-compatible |
| **Update Latency** | < 25 ms end-to-end | < 50 ms end-to-end |
| **Encryption** | AES-256 (Type 1) | SM4-GCM (Chinese) |
| **Authentication** | HMAC-SHA384 | HMAC-SM3 |
| **Anti-Jam** | DSSS (30 dB gain) | FH + DSSS (23 dB gain) |
| **Jam Detection** | Automatic w/ report | Automatic |
| **Handoff** | Cooperative (MADL) | Cooperative (ACDL) |

### 4.3 System Architecture

#### F-35 / AIM-120D Integrated Datalink Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                F-35 / AIM-120D DATALINK SYSTEM                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                 F-35 AIRCRAFT                               ││
│  │                                                             ││
│  │  ┌───────────────┐    ┌───────────────────────────────┐    ││
│  │  │     ICP       │───▶│ AN/APG-81 AESA RADAR          │    ││
│  │  │ (Mission      │    │ ┌─────────────────────────┐   │    ││
│  │  │  Computer)    │    │ │ Weapon Datalink Mode    │   │    ││
│  │  │               │    │ │ - X-band uplink         │   │    ││
│  │  │ Track data ───│───▶│ │ - TDM multiplexed       │   │    ││
│  │  │ Target update │    │ │ - 10W effective TX      │   │    ││
│  │  └───────────────┘    │ └─────────────────────────┘   │    ││
│  │                       └───────────────┬───────────────┘    ││
│  │                                       │                    ││
│  │  ┌───────────────┐                    │                    ││
│  │  │ MADL (6x)     │─── Intra-flight ───┼── (to other F-35s) ││
│  │  │ Ku-band LPI   │    comm + CEC      │                    ││
│  │  └───────────────┘                    │                    ││
│  └───────────────────────────────────────┼────────────────────┘│
│                                          │                      │
│                       X-band Weapon Uplink (16-64 kbps)        │
│                       + Two-way data (seeker telemetry)        │
│                                          │                      │
│  ┌───────────────────────────────────────▼────────────────────┐│
│  │                 AIM-120D AMRAAM                             ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐ ││
│  │  │ Datalink     │─▶│ Guidance     │─▶│ Active Radar      │ ││
│  │  │ Receiver/TX  │  │ Computer     │  │ Seeker (X-band)   │ ││
│  │  │ (X-band)     │◀─│ (Mid-course) │◀─│ (Terminal)        │ ││
│  │  └──────────────┘  └──────────────┘  └───────────────────┘ ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

#### J-20 / PL-15 Integrated Datalink Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 J-20 / PL-15 DATALINK SYSTEM                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                 J-20 AIRCRAFT                               ││
│  │                                                             ││
│  │  ┌───────────────┐    ┌───────────────────────────────┐    ││
│  │  │ Mission       │───▶│ Type 1475 AESA RADAR          │    ││
│  │  │ Computer      │    │ ┌─────────────────────────┐   │    ││
│  │  │ (CETC-14)     │    │ │ Weapon Datalink Mode    │   │    ││
│  │  │               │    │ │ - C/X-band uplink       │   │    ││
│  │  │ Track data ───│───▶│ │ - OQPSK + FH modulation │   │    ││
│  │  │ BeiDou time   │    │ │ - 10W TX power          │   │    ││
│  │  └───────────────┘    │ └─────────────────────────┘   │    ││
│  │                       └───────────────┬───────────────┘    ││
│  │                                       │                    ││
│  │  ┌───────────────┐                    │                    ││
│  │  │ ACDL (4x)     │─── Intra-flight ───┼── (to other J-20s) ││
│  │  │ Ku-band LPI   │    comm + CEC      │                    ││
│  │  └───────────────┘                    │                    ││
│  └───────────────────────────────────────┼────────────────────┘│
│                                          │                      │
│                       C/X-band Weapon Uplink (100 kbps)        │
│                       + Two-way data (AESA seeker data)        │
│                                          │                      │
│  ┌───────────────────────────────────────▼────────────────────┐│
│  │                 PL-15 AAM                                   ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐ ││
│  │  │ Datalink     │─▶│ Guidance     │─▶│ Active AESA       │ ││
│  │  │ Transceiver  │  │ Computer     │  │ Seeker            │ ││
│  │  │ (C/X-band)   │◀─│ (Mid-course) │◀─│ (Multi-target)    │ ││
│  │  └──────────────┘  └──────────────┘  └───────────────────┘ ││
│  │                                                             ││
│  │  PL-15 AESA Seeker Advantages:                              ││
│  │  - Multi-target tracking (up to 4 simultaneous)            ││
│  │  - Target classification data sent to launch platform      ││
│  │  - Extended no-escape zone via datalink updates            ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 Link Budget Comparison

#### F-35 to AIM-120D (X-band via AN/APG-81)

```
F-35 → AIM-120D UPLINK:

Transmit Power (effective):        +40 dBm (10W shared w/ radar)
Transmit Antenna Gain:             +35 dBi (AESA main beam)
EIRP:                              +75 dBm (directional)

Path Loss @ 150 km, 10 GHz:        -156.0 dB
Atmospheric Loss:                  -0.3 dB
Total Path Loss:                   -156.3 dB

Receive Antenna Gain:              +5 dBi (conformal)
Received Power:                    -76.3 dBm

Receiver Noise Floor (64 kbps):    -126 dBm
Link Margin:                       +49.7 dB ✓ (robust)

AIM-120D → F-35 DOWNLINK:
  TX Power: +30 dBm (1W)
  Link Margin: +25 dB (adequate for status telemetry)
```

#### J-20 to PL-15 (C/X-band via Type 1475)

```
J-20 → PL-15 UPLINK:

Transmit Power:                    +40 dBm (10W dedicated)
Transmit Antenna Gain:             +33 dBi (AESA beam)
EIRP:                              +73 dBm (directional)

Path Loss @ 200 km, 8 GHz:         -155.0 dB
Atmospheric Loss:                  -0.4 dB
Total Path Loss:                   -155.4 dB

Receive Antenna Gain:              +6 dBi (conformal array)
Received Power:                    -76.4 dBm

Receiver Noise Floor (100 kbps):   -124 dBm
Link Margin:                       +47.6 dB ✓ (robust)

PL-15 → J-20 DOWNLINK:
  TX Power: +33 dBm (2W, AESA capable)
  Data Rate: 50 kbps (seeker imagery, multi-target)
  Link Margin: +30 dB (supports rich telemetry)
```

### 4.5 Interface Specifications

| Signal | Type | Level | Impedance | Connector |
|--------|------|-------|-----------|-----------|
| RF Output (C-band) | RF | +40 dBm max | 50 Ω | N-type female |
| Antenna Interface | RF | +40 dBm | 50 Ω | N-type female |
| MIL-STD-1553B | Differential | ±9-14 Vpk | 70-85 Ω | Twinax |
| Discrete I/O | Digital | 28V/Open | - | MS27467T |
| Serial Data | RS-422 | ±5V | 100 Ω | D-sub 9 |
| 10 MHz Ref | Sine | 7 dBm | 50 Ω | SMA |
| Power | DC | 28 VDC | - | MS27467T |

### 4.6 Weapon Datalink Protocol Specifications

#### 4.6.1 AIM-120D Weapon Datalink Protocol

| Parameter | Specification |
|-----------|---------------|
| **Designation** | AN/AWG-20 derivative (classified) |
| **Protocol Type** | Time-Division Multiplex (TDM) |
| **Frame Structure** | 50 ms frames, 10 slots |
| **Uplink Slot** | 5 ms per weapon (up to 4 weapons) |
| **Downlink Slot** | 2 ms per weapon |
| **Guard Time** | 1 ms between slots |
| **Sync Word** | 32-bit Barker code |
| **Data Encoding** | Convolutional (rate 1/2, K=7) |
| **Interleaving** | Block (10 ms depth) |
| **Error Correction** | Viterbi decoding (soft decision) |
| **CRC** | 16-bit CRC-CCITT |

**AIM-120D Uplink Message Format:**
```
┌────────────────────────────────────────────────────────────┐
│ SYNC │ MSG ID │ TARGET DATA │ WEAPON CMD │ CRC │ TAIL    │
│ 32b  │  8b    │   256b      │    32b     │ 16b │  16b    │
└────────────────────────────────────────────────────────────┘

TARGET DATA (256 bits):
  - Target ECEF X:     32b (0.1m resolution)
  - Target ECEF Y:     32b (0.1m resolution)
  - Target ECEF Z:     32b (0.1m resolution)
  - Target Vx:         16b (0.1 m/s resolution)
  - Target Vy:         16b (0.1 m/s resolution)
  - Target Vz:         16b (0.1 m/s resolution)
  - Target Ax:         12b (0.01 m/s² resolution)
  - Target Ay:         12b (0.01 m/s² resolution)
  - Target Az:         12b (0.01 m/s² resolution)
  - Time tag:          32b (GPS TOW, μs)
  - Quality flag:       8b (track quality metrics)
  - Reserved:          28b

WEAPON CMD (32 bits):
  - Seeker mode:        4b (off/standby/search/track)
  - Autonomy level:     4b (full/mid/terminal)
  - Handoff command:    4b (not used/prepare/execute)
  - Self-destruct:      4b (arm/safe/initiate)
  - Reserved:          16b
```

**AIM-120D Downlink Message Format:**
```
┌──────────────────────────────────────────────────────────┐
│ SYNC │ MSG ID │ SEEKER DATA │ STATUS │ CRC │ TAIL      │
│ 32b  │  8b    │   128b      │  32b   │ 16b │  16b      │
└──────────────────────────────────────────────────────────┘

SEEKER DATA (128 bits):
  - Track status:       4b (searching/acquiring/locked)
  - Target bearing:    16b (0.01° resolution)
  - Target elevation:  16b (0.01° resolution)
  - Target range:      20b (1m resolution, seeker-derived)
  - Target RCS:        12b (dBsm estimate)
  - Doppler:           16b (1 Hz resolution)
  - SNR:               12b (0.1 dB resolution)
  - Confidence:        16b (track quality)
  - Reserved:          16b

STATUS (32 bits):
  - Missile state:      4b (armed/flight/terminal)
  - Fuel remaining:     8b (% of initial)
  - INS drift:          8b (estimated error)
  - Seeker health:      4b (nominal/degraded/failed)
  - Datalink quality:   4b (link margin indicator)
  - Reserved:           4b
```

#### 4.6.2 PL-15 Weapon Datalink Protocol

| Parameter | Specification |
|-----------|---------------|
| **Designation** | SAC/CPMIEC proprietary |
| **Protocol Type** | Frequency Hopping + TDM hybrid |
| **Hop Rate** | 50 hops/second |
| **Hop Pattern** | Pseudo-random (SM4 derived) |
| **Frame Structure** | 100 ms superframe |
| **Uplink Slot** | 20 ms per weapon |
| **Downlink Slot** | 10 ms per weapon |
| **Sync Word** | 64-bit (extended for FH acquisition) |
| **Data Encoding** | Turbo code (rate 1/3) |
| **Interleaving** | Convolutional (20 ms depth) |
| **Error Correction** | Iterative turbo decoding |
| **CRC** | 32-bit CRC-32 |

**PL-15 Uplink Message Format:**
```
┌────────────────────────────────────────────────────────────────┐
│ SYNC │ FH SEQ │ MSG ID │ TARGET DATA │ MULTI-TGT │ CMD │ CRC │
│ 64b  │  16b   │  8b    │   320b      │   128b    │ 32b │ 32b │
└────────────────────────────────────────────────────────────────┘

TARGET DATA (320 bits) - Primary Target:
  - Target WGS-84 Lat:  32b (10 nano-degree resolution)
  - Target WGS-84 Lon:  32b (10 nano-degree resolution)
  - Target Altitude:    24b (0.1m resolution, MSL)
  - Target Ve:          16b (0.1 m/s East)
  - Target Vn:          16b (0.1 m/s North)
  - Target Vu:          16b (0.1 m/s Up)
  - Target Ae:          12b (acceleration)
  - Target An:          12b (acceleration)
  - Target Au:          12b (acceleration)
  - Covariance P11:     16b (position uncertainty)
  - Covariance P22:     16b
  - Covariance P33:     16b
  - Covariance P12:     12b
  - Covariance P13:     12b
  - Covariance P23:     12b
  - BeiDou/GPS time:    32b (nanoseconds)
  - Quality metrics:    16b
  - Reserved:           24b

MULTI-TARGET (128 bits) - Secondary Targets:
  - Num secondary:       4b (0-4 additional targets)
  - Target 2 offset:    31b (delta from primary)
  - Target 3 offset:    31b
  - Target 4 offset:    31b
  - Priority flags:     16b
  - Reserved:           15b

CMD (32 bits):
  - Seeker mode:         4b
  - Autonomy:            4b
  - Target priority:     4b (which target to prosecute)
  - Handoff:             4b
  - Self-destruct:       4b
  - Sensor fusion cmd:   4b (use seeker + datalink)
  - Reserved:            8b
```

**PL-15 Downlink Message Format (AESA Seeker Data):**
```
┌────────────────────────────────────────────────────────────────┐
│ SYNC │ FH SEQ │ MSG ID │ SEEKER DATA │ MULTI-TGT │ STATUS │CRC│
│ 64b  │  16b   │  8b    │   256b      │   192b    │  64b   │32b│
└────────────────────────────────────────────────────────────────┘

SEEKER DATA (256 bits) - Primary Track:
  - Track status:        4b (search/acquire/track/classify)
  - Target class:        8b (fighter/transport/drone/decoy)
  - Target bearing:     16b (0.001° resolution)
  - Target elevation:   16b (0.001° resolution)
  - Target range:       24b (0.5m resolution, AESA)
  - Range rate:         16b (0.1 m/s resolution)
  - Target RCS:         16b (0.1 dBsm resolution)
  - RCS variance:       12b (for classification)
  - Doppler spectrum:   32b (compressed)
  - Track SNR:          12b (0.1 dB)
  - Glint angle:        16b (for aimpoint)
  - J/S ratio:          12b (jam-to-signal)
  - ECCM status:        8b (countermeasure response)
  - Confidence:         16b
  - Reserved:           48b

MULTI-TARGET (192 bits) - Up to 4 simultaneous tracks:
  - Num tracks:          4b
  - Track 1 summary:    47b (bearing, range, class, SNR)
  - Track 2 summary:    47b
  - Track 3 summary:    47b
  - Track 4 summary:    47b

STATUS (64 bits):
  - Missile state:       4b
  - Fuel remaining:     10b (0.1% resolution)
  - INS quality:         8b
  - AESA health:         4b (elements operational)
  - Datalink quality:    4b
  - Thermal:             8b (seeker temp)
  - Time to impact:     16b (seconds, estimated)
  - Reserved:           10b
```

### 4.7 Weapon Datalink Timing Diagram

```
AIM-120D Frame (50 ms):
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│SYNC │UL-1 │UL-2 │UL-3 │UL-4 │GUARD│DL-1 │DL-2 │DL-3 │DL-4 │
│ 3ms │ 5ms │ 5ms │ 5ms │ 5ms │ 5ms │ 5ms │ 5ms │ 5ms │ 7ms │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
         ↑                              ↑
    F-35 to AIM-120D              AIM-120D to F-35

PL-15 Superframe (100 ms):
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│SYNC │ UL-1      │ UL-2      │GUARD│ DL-1      │ DL-2      │
│10ms │   20ms    │   20ms    │10ms │   20ms    │   20ms    │
└─────┴───────────┴───────────┴─────┴───────────┴───────────┘
         ↑                              ↑
    J-20 to PL-15                 PL-15 to J-20
                                  (rich AESA data)
```

### 4.8 Performance Verification

| Test | Procedure | Pass Criteria |
|------|-----------|---------------|
| Link Quality | End-to-end message test | > 90% delivery |
| Range Test | Measure at max range (250 km) | > 6 dB margin |
| Latency | Timestamp round-trip message | < 50 ms one-way |
| Hop Acquisition | Time to sync after hop | < 10 ms |
| Encryption | Verify crypto operation | FIPS 140-2 / Chinese equiv |
| Multi-target | Track 4 targets, verify updates | All tracks current |
| Handoff | Platform-to-platform transfer | < 500 ms complete |

---

## HW-5: Weapon System

### 5.1 System Overview

Long-range air-to-air missile integration including launch authorization, self-test, and guidance interface.

**Real Hardware Equivalents:**
- **US:** AIM-120D AMRAAM, AIM-260 JATM, MIL-STD-1760 stores interface
- **China:** PL-15, PL-21, Chinese equivalent stores management

### 5.2 Primary Components

#### 5.2.1 Fire Control Computer Interface

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | Raytheon AMRAAM SMS | SAC/Luoyang PL-15 SMS |
| **Interface Type** | MIL-STD-1760 Class II | Chinese equivalent standard |
| **Data Bus** | MIL-STD-1553B dual | 1553B-compatible |
| **Discrete Signals** | 28V DC logic | 27V DC logic |
| **Power Transfer** | 28 VDC, 270 VDC | 27 VDC primary |
| **Message Rate** | 20 Hz weapon status | 10 Hz weapon status |
| **Command Latency** | < 5 ms | < 10 ms |
| **Safety Interlocks** | Triple-redundant | Dual-redundant |

#### 5.2.2 Weapon Self-Test Monitor

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | AIM-120D BIT | PL-15 CBIT/IBIT |
| **Test Duration** | < 20 seconds | < 30 seconds |
| **Tested Subsystems** | 8 critical | 7 critical |
| **Test Coverage** | > 98% fault detection | > 95% fault detection |
| **False Alarm Rate** | < 0.05% | < 0.1% |
| **Power for BIT** | 45W internal | 50W internal |

**US AIM-120D Self-Test:** Seeker RF, seeker gimbal, guidance, INS, motor, datalink, control, fuze
**PL-15 Self-Test:** Seeker, guidance computer, INS, motor igniter, datalink, actuators, fuze

#### 5.2.3 Weapon Specifications

| Parameter | AIM-120D (US) | PL-15 (China) |
|-----------|---------------|---------------|
| **Range** | 160+ km (est.) | 200+ km (est.) |
| **Speed** | Mach 4+ | Mach 4+ |
| **Guidance** | Inertial + datalink + ARH | Inertial + datalink + ARH |
| **Seeker** | Active radar, ±60° gimbal | Active AESA, ±60° gimbal |
| **Warhead** | 23 kg HE-frag | 20+ kg HE-frag |
| **Weight** | 162 kg | ~200 kg |
| **Length** | 3.66 m | ~4.0 m |
| **Datalink** | Two-way | Two-way |

#### 5.2.4 Launch Sequencer

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Pre-Launch** | 1.5 seconds | 2.0 seconds |
| **Release Command** | 28V pulse, 50 ms | 27V pulse, 100 ms |
| **Motor Ignition** | 0.3 s post-separation | 0.5 s post-separation |
| **Abort Capability** | T-0.3 seconds | T-0.5 seconds |
| **Jettison Mode** | Unarmed release | Unarmed release |

### 5.3 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEAPON SYSTEM INTERFACE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                 FIRE CONTROL SYSTEM                         ││
│  │  ┌─────────────┐    ┌─────────────┐    ┌────────────────┐ ││
│  │  │ Mission     │───▶│ Weapon      │───▶│ Launch         │ ││
│  │  │ Computer    │    │ Manager     │    │ Sequencer      │ ││
│  │  └─────────────┘    └─────────────┘    └───────┬────────┘ ││
│  │                                                 │          ││
│  │         ┌───────────────────────────────────────┘          ││
│  │         │                                                  ││
│  │         ▼                                                  ││
│  │  ┌─────────────────────────────────────────────────────┐  ││
│  │  │              MIL-STD-1760 INTERFACE                 │  ││
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  ││
│  │  │  │ 1553B    │  │ Discrete │  │ Power            │  │  ││
│  │  │  │ Data Bus │  │ I/O (28V)│  │ (28V/270V)       │  │  ││
│  │  │  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │  ││
│  │  └───────┼─────────────┼─────────────────┼────────────┘  ││
│  └──────────┼─────────────┼─────────────────┼───────────────┘│
│             │             │                 │                │
│  ═══════════╪═════════════╪═════════════════╪════════════════│
│  UMBILICAL  │             │                 │                │
│  ═══════════╪═════════════╪═════════════════╪════════════════│
│             │             │                 │                │
│  ┌──────────┼─────────────┼─────────────────┼───────────────┐│
│  │          ▼             ▼                 ▼               ││
│  │  ┌─────────────────────────────────────────────────────┐ ││
│  │  │                 PL-15 WEAPON                        │ ││
│  │  │  ┌────────────┐  ┌────────────┐  ┌───────────────┐  │ ││
│  │  │  │ Guidance   │  │ Self-Test  │  │ Power         │  │ ││
│  │  │  │ Computer   │  │ Controller │  │ Conditioning  │  │ ││
│  │  │  └──────┬─────┘  └──────┬─────┘  └───────────────┘  │ ││
│  │  │         │               │                           │ ││
│  │  │         │    ┌──────────┴──────────┐                │ ││
│  │  │         │    │                     │                │ ││
│  │  │         ▼    ▼                     ▼                │ ││
│  │  │  ┌───────────────┐  ┌─────────┐  ┌────────────────┐ │ ││
│  │  │  │ Seeker        │  │ INS     │  │ Motor/Fuze     │ │ ││
│  │  │  │ (Radar+Gimbal)│  │         │  │ Arm Circuit    │ │ ││
│  │  │  └───────────────┘  └─────────┘  └────────────────┘ │ ││
│  │  └─────────────────────────────────────────────────────┘ ││
│  │                       PL-15 MISSILE                       ││
│  └───────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 Self-Test Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 0x00 | NOT_TESTED | Self-test not yet run |
| 0x01 | TESTING | Self-test in progress |
| 0x10 | PASS | All subsystems nominal |
| 0x20 | PARTIAL | Minor warnings, mission capable |
| 0x30 | DEGRADED | Reduced capability |
| 0x40 | FAIL_SEEKER | Seeker fault |
| 0x41 | FAIL_GUIDANCE | Guidance computer fault |
| 0x42 | FAIL_INS | INS fault |
| 0x43 | FAIL_MOTOR | Motor igniter fault |
| 0x44 | FAIL_DATALINK | Datalink receiver fault |
| 0x45 | FAIL_ACTUATOR | Control actuator fault |
| 0x46 | FAIL_FUZE | Fuze circuit fault |
| 0xFF | COMM_FAULT | Communication lost |

### 5.5 Performance Verification

| Test | Procedure | Pass Criteria |
|------|-----------|---------------|
| Self-Test | Run full BIT sequence | Status = 0x10 or 0x20 |
| 1553 Comm | Verify message exchange | < 1% message errors |
| INS Alignment | Verify alignment to aircraft | < 0.1° error |
| Discrete I/O | Verify all discrete signals | All signals nominal |
| Power | Measure power draw | Within ±10% spec |

---

## HW-6: Tracking Processor

### 6.1 System Overview

Real-time multi-target tracking processor with sensor fusion, Kalman filtering, and multiple hypothesis tracking (MHT).

**Real Hardware Equivalents:**
- **US:** F-35 ICP (Integrated Core Processor), BAE CMSP, Northrop Grumman mission computers
- **China:** CETC-14 Mission Computer, AVIC Chengdu FC avionics, integrated J-20 processor

### 6.2 Primary Components

#### 6.2.1 Main Processing Unit

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | F-35 ICP (L3Harris) | CETC-14 MC-500 series |
| **Processor Type** | Intel Xeon + Xilinx FPGA | Loongson/Phytium + domestic FPGA |
| **CPU Cores** | 24 cores @ 3.4 GHz | 16 cores @ 2.5 GHz |
| **FPGA** | Xilinx Versal Premium | Xilinx UltraScale+ / Gowin |
| **AI Accelerator** | 500+ AI TOPS | 200 AI TOPS |
| **Memory** | 512 GB DDR5 ECC | 256 GB DDR4 ECC |
| **Storage** | 8 TB NVMe RAID | 4 TB NVMe |
| **Processing Rate** | > 50 TFLOPS | > 20 TFLOPS |
| **Power** | 400W @ 28 VDC | 350W @ 28 VDC |
| **Cooling** | Liquid cold plate | Forced air + liquid |

#### 6.2.2 Tracker Software

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Reference** | MHT-based (US standard) | Similar MHT approach |
| **Update Rate** | 20 Hz (50 ms cycle) | 10 Hz (100 ms cycle) |
| **Track Capacity** | 200 simultaneous | 100 simultaneous |
| **Filter Type** | UKF/EKF adaptive | Extended Kalman (EKF) |
| **State Vector** | 12-state (with jerk) | 9-state (pos/vel/acc) |
| **Association** | MHT + ML-enhanced | MHT with N-scan |
| **Hypothesis Limit** | 5000 per cluster | 1000 per cluster |
| **Fusion Latency** | < 25 ms | < 50 ms |
| **Output Latency** | < 10 ms | < 20 ms |

#### 6.2.3 Sensor Interface

| Parameter | US Specification | Chinese Specification |
|-----------|------------------|----------------------|
| **Sensor Inputs** | Up to 16 concurrent | Up to 8 concurrent |
| **Data Rate** | Up to 100 Gbps total | Up to 40 Gbps total |
| **Protocol** | Link-16/MADL/custom | JIDS/custom UDP |
| **Time Alignment** | < 50 ns (GPS-synced) | < 100 ns (BeiDou-synced) |
| **Coordinate System** | WGS-84, ECEF, ENU | WGS-84, CGCS2000, ENU |

### 6.3 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRACKING PROCESSOR                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 SENSOR INPUTS                            │   │
│  │  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  │   │
│  │  │RF Sens│  │Antenna│  │ AESA  │  │Datalink│ │External│  │   │
│  │  │(ESM)  │  │(AoA)  │  │(Range)│  │(Track) │ │(CEC)   │  │   │
│  │  └───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘  │   │
│  │      │          │          │          │          │       │   │
│  │      └──────────┴────┬─────┴──────────┴──────────┘       │   │
│  │                      │                                    │   │
│  │                      ▼                                    │   │
│  │         ┌────────────────────────────┐                   │   │
│  │         │     SENSOR PREPROCESSOR    │                   │   │
│  │         │  - Time alignment          │                   │   │
│  │         │  - Coordinate transform    │                   │   │
│  │         │  - Detection formatting    │                   │   │
│  │         └───────────┬────────────────┘                   │   │
│  └─────────────────────┼───────────────────────────────────┘   │
│                        │                                        │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 TRACK PROCESSING CORE                    │   │
│  │                                                          │   │
│  │  ┌────────────────┐    ┌────────────────────────────┐   │   │
│  │  │ Detection-to-  │───▶│ Multiple Hypothesis        │   │   │
│  │  │ Track Assoc.   │    │ Tracker (MHT)              │   │   │
│  │  └────────────────┘    │  - Hypothesis generation   │   │   │
│  │                        │  - Scoring & pruning       │   │   │
│  │                        │  - Track confirmation      │   │   │
│  │                        └──────────┬─────────────────┘   │   │
│  │                                   │                      │   │
│  │                                   ▼                      │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │            EXTENDED KALMAN FILTER                  │ │   │
│  │  │  - 9-state estimation (pos/vel/accel)              │ │   │
│  │  │  - Covariance propagation                          │ │   │
│  │  │  - Adaptive noise tuning                           │ │   │
│  │  └────────────────────────┬───────────────────────────┘ │   │
│  │                           │                              │   │
│  │                           ▼                              │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │            TRACK MANAGEMENT                        │ │   │
│  │  │  - Track ID assignment                             │ │   │
│  │  │  - Track quality scoring                           │ │   │
│  │  │  - Track coast / drop logic                        │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  │                                                          │   │
│  └──────────────────────────────┬───────────────────────────┘   │
│                                 │                                │
│                                 ▼                                │
│                    ┌────────────────────────┐                   │
│                    │ TRACK OUTPUT           │                   │
│                    │ - Position (WGS-84)    │                   │
│                    │ - Velocity vector      │                   │
│                    │ - Covariance matrix    │                   │
│                    │ - Track quality        │                   │
│                    │ - Update rate: 10 Hz   │                   │
│                    └────────────────────────┘                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 6.4 Latency Budget

| Processing Stage | Nominal | Maximum |
|------------------|---------|---------|
| Sensor Detection | 5 ms | 10 ms |
| Preprocessing | 5 ms | 10 ms |
| Association | 15 ms | 25 ms |
| MHT Processing | 20 ms | 35 ms |
| Kalman Update | 10 ms | 15 ms |
| Track Management | 5 ms | 10 ms |
| Output Formatting | 5 ms | 10 ms |
| **Total** | **65 ms** | **115 ms** |

### 6.5 Interface Specifications

| Signal | Type | Level | Rate | Connector |
|--------|------|-------|------|-----------|
| Sensor Data (×8) | 10GbE | 10GBASE-SR | 10 Gbps | LC duplex |
| Track Output | 10GbE | 10GBASE-SR | 10 Gbps | LC duplex |
| 10 MHz Reference | Sine | 7 dBm | - | SMA |
| 1PPS Sync | Digital | RS-422 | 1 Hz | D-sub 9 |
| Control | Ethernet | 1000BASE-T | - | RJ-45 |
| Power | DC | 28 VDC | 350W | MS27467T |

### 6.6 Performance Verification

| Test | Procedure | Pass Criteria |
|------|-----------|---------------|
| Latency | End-to-end timing measurement | < 120 ms total |
| Track Accuracy | Compare to truth data | < 5% RMS error |
| Association | Multi-target crossing scenario | > 99% correct |
| Capacity | 100 simultaneous targets | No dropped tracks |
| CPU Load | Monitor during stress test | < 80% utilization |

---

## HW-7: EW Suite

### 7.1 System Overview

Electronic warfare suite for jamming coordination, self-protection, and track-while-jam operations.

**Real Hardware Equivalents:**
- **F-35:** AN/ASQ-239 Barracuda EW Suite (BAE Systems) - integrated apertures, DRFM
- **J-20:** Integrated EW suite with side-mounted ESM arrays (CETC-29/AVIC) - believed L/X/Ku-band

### 7.2 Primary Components

#### 7.2.1 Jamming Transmitter

| Parameter | F-35 AN/ASQ-239 | J-20 EW Suite (estimated) |
|-----------|------------------|---------------------------|
| **Designation** | AN/ASQ-239 Barracuda | CETC-29 derivative |
| **Frequency Range** | 2-40 GHz full spectrum | 2-18 GHz primary |
| **Instantaneous BW** | 4 GHz | 2 GHz |
| **Output Power** | 1 kW peak per aperture | 2 kW peak |
| **EIRP** | 60-70 dBm | 55-65 dBm |
| **Duty Cycle** | 50% (distributed) | 25% |
| **Waveforms** | DRFM, noise, deception | DRFM, noise, barrage |
| **Response Time** | < 10 ns (DRFM) | < 100 ns (DRFM) |
| **Apertures** | 10 distributed | 4-6 conformal |
| **Power** | Integrated with EPGS | 3 kW @ 270 VDC |
| **Cooling** | Liquid (aircraft loop) | Liquid (PAO) |

#### 7.2.2 Threat Receiver (ESM)

| Parameter | F-35 AN/ASQ-239 | J-20 ESM (estimated) |
|-----------|------------------|----------------------|
| **Designation** | ASQ-239 integrated | CETC-14/29 derivative |
| **Frequency Range** | 0.5-40 GHz | 2-18 GHz |
| **Sensitivity** | -85 dBm | -70 dBm |
| **Dynamic Range** | 90 dB | 75 dB |
| **AoA Accuracy** | ±0.5° RMS | ±2° RMS |
| **Frequency Accuracy** | ±100 kHz | ±1 MHz |
| **Pulse Density** | > 10M PPS | > 2M PPS |
| **Threat ID Time** | < 10 ms | < 100 ms |
| **Library Size** | > 50,000 emitters | > 15,000 emitters |
| **Geolocation** | Yes (multi-aperture) | Yes (baseline) |

#### 7.2.3 EW Controller

| Parameter | F-35 AN/ASQ-239 | J-20 EW Controller |
|-----------|------------------|---------------------|
| **Processing** | ICP-integrated | Dedicated FPGA + DSP |
| **Jamming Techniques** | > 200 stored | > 80 stored |
| **Null Steering** | 16 simultaneous | 8 simultaneous |
| **Null Depth** | > 45 dB | > 30 dB |
| **Coordination** | Automatic sensor fusion | Semi-automatic |
| **Response Time** | < 1 ms threat to jam | < 10 ms threat to jam |
| **Mode Selection** | Fully automatic + manual | Automatic / Manual |
| **CEC Integration** | Yes (MADL) | Yes (ACDL) |

### 7.3 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EW SUITE SUBSYSTEM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 THREAT DETECTION                         │   │
│  │  ┌──────────────┐    ┌──────────────┐                   │   │
│  │  │ Wideband     │───▶│ Threat       │───▶ Threat Data   │   │
│  │  │ Receiver     │    │ Processor    │    to Controller  │   │
│  │  │ (2-18 GHz)   │    │ (ID + Track) │                   │   │
│  │  └──────────────┘    └──────────────┘                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                 │                               │
│                                 ▼                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 EW CONTROLLER                            │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  - Threat prioritization                          │   │   │
│  │  │  - Jamming technique selection                    │   │   │
│  │  │  - Null steering computation                      │   │   │
│  │  │  - Coordination with tracking processor           │   │   │
│  │  │  - Track-while-jam management                     │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                          │                               │   │
│  │         ┌────────────────┼────────────────┐              │   │
│  │         │                │                │              │   │
│  │         ▼                ▼                ▼              │   │
│  │  ┌───────────┐   ┌───────────┐   ┌───────────────────┐  │   │
│  │  │ Jammer    │   │ Null      │   │ Track-While-Jam   │  │   │
│  │  │ Commands  │   │ Steering  │   │ Coordination      │  │   │
│  │  │           │   │ Commands  │   │                   │  │   │
│  │  └─────┬─────┘   └─────┬─────┘   └─────────┬─────────┘  │   │
│  └────────┼───────────────┼───────────────────┼────────────┘   │
│           │               │                   │                 │
│           ▼               ▼                   ▼                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 JAMMING SYSTEM                           │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │   │
│  │  │ Waveform     │───▶│ High-Power   │───▶│ Steerable  │ │   │
│  │  │ Generator    │    │ Amplifier    │    │ Antenna    │ │   │
│  │  │ (DRFM+DDS)   │    │ (2 kW)       │    │ (Nulls)    │ │   │
│  │  └──────────────┘    └──────────────┘    └────────────┘ │   │
│  │                                                          │   │
│  │  Jamming Modes:                                          │   │
│  │  - NOISE: Broadband power denial                        │   │
│  │  - SPOT: Narrow-band high power                          │   │
│  │  - BARRAGE: Swept frequency                              │   │
│  │  - DRFM: Coherent false targets                          │   │
│  │  - TRACK_WHILE_JAM: Null-protected friendly             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.4 Operating Modes

| Mode | Description | Power | Null Steering |
|------|-------------|-------|---------------|
| SILENT | Receive only, no emissions | 0W | N/A |
| STANDBY | Ready to jam, not transmitting | 0W | Pre-computed |
| NOISE | Broadband noise jamming | 500W avg | Active |
| SPOT | Narrow-band focused | 2 kW peak | Active |
| BARRAGE | Swept frequency | 1 kW avg | Active |
| DRFM | False target generation | 100W | Active |
| TRACK_WHILE_JAM | Protected tracking | 500W avg | **Required** |

### 7.5 Interface Specifications

| Signal | Type | Level | Rate | Connector |
|--------|------|-------|------|-----------|
| Threat Receiver RF | RF | -65 to +10 dBm | 2-18 GHz | SMA ×4 |
| Jammer RF Output | RF | +60 dBm max | 8-18 GHz | WR-75 waveguide |
| Tracker Data In | 10GbE | 10GBASE-SR | 10 Gbps | LC duplex |
| EW Status Out | Ethernet | 1000BASE-T | - | RJ-45 |
| 10 MHz Reference | Sine | 7 dBm | - | SMA |
| Power (270V) | DC | 270 VDC ±10% | 3 kW | MS27467T |
| Cooling (PAO) | Liquid | 10°C inlet | 5 GPM | Quick-disconnect |

### 7.6 Performance Verification

| Test | Procedure | Pass Criteria |
|------|-----------|---------------|
| Jammer Power | Measure at antenna port | > 55 dBm EIRP |
| Null Depth | Inject test signal, measure null | > 30 dB |
| Response Time | Threat to jam timing | < 100 ms |
| Track Coordination | Verify nulls protect friendly | No track disruption |
| Threat ID | Library test signals | > 95% correct ID |

---

## HW-8: Power Management

### 8.1 System Overview

Aircraft power generation, distribution, and management for all subsystems with load prioritization and reserve monitoring.

**Real Hardware Equivalents:**
- **F-35:** Integrated Power Package (IPP) by Honeywell, EPGS (Electrical Power Generation System)
- **J-20:** WS-10C/WS-15 integrated IDG, power system by AVIC Engine Research Institute

### 8.2 Primary Components

#### 8.2.1 Main Generator

| Parameter | F-35 EPGS | J-20 Power System |
|-----------|-----------|-------------------|
| **Designation** | Honeywell IPP | WS-15 IDG system |
| **Type** | Variable Speed Constant Freq | Integrated Drive Generator |
| **Rating** | 160 kVA per engine | 150 kVA per engine (est.) |
| **Total Capacity** | 320 kVA (dual engine) | 300 kVA (dual engine) |
| **Primary Voltage** | 270 VDC HVDC | 270 VDC / 115 VAC |
| **Secondary Voltage** | 28 VDC, 115 VAC | 27 VDC, 115 VAC 400Hz |
| **Regulation** | ±1% voltage | ±2% voltage |
| **Power Factor** | 0.85-1.0 | 0.75-1.0 |
| **Efficiency** | > 95% at rated | > 90% at rated |
| **Overload** | 200% for 5 seconds | 150% for 5 minutes |
| **Cooling** | Fuel-cooled heat exchanger | Oil-spray, fuel-cooled |

#### 8.2.2 Power Distribution Unit (PDU)

| Parameter | F-35 PDU | J-20 PDU |
|-----------|----------|----------|
| **Designation** | Hamilton Sundstrand RLMU | AVIC power distribution |
| **Primary Bus** | 270 VDC (main) | 270 VDC / 115 VAC |
| **DC Outputs** | 270 VDC (60 kW), 28 VDC (15 kW) | 27 VDC (10 kW) |
| **AC Outputs** | 115 VAC 400Hz (20 kW) | 115 VAC 400Hz (50 kW) |
| **Protection** | SSPC integrated | SSPC / mechanical hybrid |
| **Monitoring** | Full digital health mgmt | Per-channel monitoring |
| **Bus Tie** | Automatic with priority | Automatic transfer |
| **Efficiency** | > 98% | > 95% |

#### 8.2.3 Power Management Computer (PMC)

| Parameter | F-35 PMC | J-20 PMC |
|-----------|----------|----------|
| **Designation** | Part of ICP/VMS | Dedicated PMC unit |
| **Processing** | Triple-redundant | Dual-redundant |
| **Monitored Channels** | 128+ load channels | 64 load channels |
| **Sample Rate** | 10 kHz per channel | 1 kHz per channel |
| **Load Shedding** | Automatic AI-assisted | Automatic priority-based |
| **Response Time** | < 1 ms to fault | < 10 ms to fault |
| **Reserve Calc** | Real-time, 10 Hz | Real-time, 1 Hz |
| **Interface** | Fiber/ARINC 664 | ARINC 429 / 1553B |

### 8.3 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    POWER MANAGEMENT SUBSYSTEM                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                 POWER GENERATION                            ││
│  │  ┌─────────────────┐    ┌─────────────────┐                ││
│  │  │ Engine 1        │    │ Engine 2        │                ││
│  │  │ Generator       │    │ Generator       │                ││
│  │  │ (150 kVA)       │    │ (150 kVA)       │                ││
│  │  └────────┬────────┘    └────────┬────────┘                ││
│  │           │                      │                          ││
│  │           └──────────┬───────────┘                          ││
│  │                      │                                      ││
│  │                      ▼                                      ││
│  │           ┌─────────────────────┐                          ││
│  │           │ Generator Control   │                          ││
│  │           │ Unit (GCU)          │                          ││
│  │           │ - Voltage/Freq reg  │                          ││
│  │           │ - Load sharing      │                          ││
│  │           │ - Fault protection  │                          ││
│  │           └──────────┬──────────┘                          ││
│  └──────────────────────┼─────────────────────────────────────┘│
│                         │                                       │
│                         ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                 POWER DISTRIBUTION                          ││
│  │                                                             ││
│  │    115/200 VAC                   270 VDC                    ││
│  │    400 Hz Bus                    HVDC Bus                   ││
│  │        │                             │                      ││
│  │        ▼                             ▼                      ││
│  │  ┌───────────────────────────────────────────────────────┐ ││
│  │  │           POWER DISTRIBUTION UNIT (PDU)               │ ││
│  │  │                                                       │ ││
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │ ││
│  │  │  │ SSPC    │  │ SSPC    │  │ TRU     │  │ TRU     │  │ ││
│  │  │  │ 115 VAC │  │ 26 VAC  │  │ 270 VDC │  │ 28 VDC  │  │ ││
│  │  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  │ ││
│  │  └───────┼────────────┼────────────┼────────────┼────────┘ ││
│  └──────────┼────────────┼────────────┼────────────┼──────────┘│
│             │            │            │            │            │
│             ▼            ▼            ▼            ▼            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                 LOAD DISTRIBUTION                            ││
│  │                                                              ││
│  │  Priority 1 (Critical):    Priority 2 (Mission):            ││
│  │  ┌─────────────────────┐  ┌─────────────────────┐           ││
│  │  │ Flight Control  15kW│  │ AESA Radar      15kW│           ││
│  │  │ Avionics        20kW│  │ ESM Suite        5kW│           ││
│  │  │ Fuel/Hydraulic  10kW│  │ Datalink         2kW│           ││
│  │  │ Cooling         25kW│  │ Tracking Proc    1kW│           ││
│  │  └─────────────────────┘  └─────────────────────┘           ││
│  │                                                              ││
│  │  Priority 3 (Engagement):  Priority 4 (Non-Essential):      ││
│  │  ┌─────────────────────┐  ┌─────────────────────┐           ││
│  │  │ EW Suite        40kW│  │ Cabin Systems    5kW│           ││
│  │  │ Weapon Power     5kW│  │ Recording        2kW│           ││
│  │  │ Additional Sens  5kW│  │ Lighting         1kW│           ││
│  │  └─────────────────────┘  └─────────────────────┘           ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                 POWER MANAGEMENT COMPUTER                    ││
│  │  ┌─────────────────────────────────────────────────────┐   ││
│  │  │  Real-Time Load Monitoring                           │   ││
│  │  │  - Total load:        82 kW (nominal engagement)     │   ││
│  │  │  - Available:        150 kW                          │   ││
│  │  │  - Reserve:           68 kW (45%)                    │   ││
│  │  │  - Min required:      15% (22.5 kW)                  │   ││
│  │  │  - Status: VERIFIED                                  │   ││
│  │  └─────────────────────────────────────────────────────┘   ││
│  │                                                             ││
│  │  Load Shedding Priority (auto if reserve < 10%):           ││
│  │    Shed P4 → P3 → P2 → (never shed P1)                     ││
│  │                                                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.4 Power Budget

#### F-35 Power Budget (320 kVA available)

| Subsystem | Priority | Nominal (kW) | Peak (kW) |
|-----------|----------|--------------|-----------|
| Flight Control (FCS) | P1 | 20 | 30 |
| Avionics/ICP | P1 | 25 | 35 |
| Environmental/Cooling | P1 | 35 | 45 |
| Fuel/Hydraulic | P1 | 15 | 20 |
| **P1 Total** | - | **95** | **130** |
| AN/APG-81 AESA | P2 | 25 | 45 |
| AN/ASQ-239 EW | P2 | 15 | 25 |
| MADL/CNI | P2 | 5 | 10 |
| DAS/EOTS | P2 | 8 | 12 |
| **P2 Total** | - | **53** | **92** |
| Full EW Jamming | P3 | 30 | 50 |
| Weapon Power | P3 | 8 | 15 |
| **P3 Total** | - | **38** | **65** |
| Pilot Systems | P4 | 5 | 8 |
| **GRAND TOTAL** | - | **191** | **295** |
| **Available** | - | **240** | **320 (burst)** |

#### J-20 Power Budget (300 kVA available estimated)

| Subsystem | Priority | Nominal (kW) | Peak (kW) |
|-----------|----------|--------------|-----------|
| Flight Control | P1 | 15 | 20 |
| Avionics | P1 | 20 | 25 |
| Cooling | P1 | 25 | 30 |
| Fuel/Hydraulic | P1 | 10 | 15 |
| **P1 Total** | - | **70** | **90** |
| Type 1475 AESA | P2 | 15 | 30 |
| ESM Suite | P2 | 5 | 8 |
| Datalink | P2 | 2 | 5 |
| Tracking Processor | P2 | 1 | 2 |
| **P2 Total** | - | **23** | **45** |
| EW Jamming | P3 | 40 | 60 |
| PL-15 Power | P3 | 5 | 10 |
| **P3 Total** | - | **45** | **70** |
| Cabin/Recording | P4 | 8 | 10 |
| **P4 Total** | - | **8** | **10** |
| **GRAND TOTAL** | - | **146** | **215** |
| **Available** | - | **180** | **225 (5 min)** |

### 8.5 Interface Specifications

| Signal | Type | Level | Rate | Connector |
|--------|------|-------|------|-----------|
| Generator AC | 3-phase | 115/200 VAC 400Hz | 150 kVA | MS27467T |
| 270 VDC Bus | DC | 270 VDC ±10% | 30 kW | MS27467T |
| 28 VDC Bus | DC | 28 VDC ±2V | 10 kW | MS27467T |
| 115 VAC Bus | Single-phase | 115 VAC 400Hz | 50 kW | MS27467T |
| ARINC 429 | Serial | ±10V | 100 kbps | D-sub 15 |
| 1553B | Differential | ±9-14V | 1 Mbps | Twinax |
| Status Discrete | Digital | 28V/Open | - | MS27467T |

### 8.6 Performance Verification

| Test | Procedure | Pass Criteria |
|------|-----------|---------------|
| Reserve Calculation | Measure all loads, verify reserve | ±2% accuracy |
| Load Shedding | Simulate overload, verify response | < 100 ms response |
| Generator Transfer | Switch generators, verify continuity | < 50 ms gap |
| Thermal | Monitor under full load | All within spec |
| Fault Protection | Inject faults, verify isolation | Correct isolation |

---

## Integration Matrix

### Subsystem Interconnections

| From \ To | GPS | RF Sens | Antenna | Datalink | Weapon | Track | EW | Power |
|-----------|-----|---------|---------|----------|--------|-------|----|----|
| **GPS** | - | 1PPS+10M | 1PPS+10M | 1PPS+10M | - | 1PPS+10M | 1PPS+10M | - |
| **RF Sens** | - | - | RF In | - | - | Det | - | 28V |
| **Antenna** | - | RF Out | - | - | - | AoA | Null Cmd | 28V |
| **Datalink** | - | - | - | - | Uplink | Track | Coord | 28V |
| **Weapon** | - | - | - | Cmd | - | - | - | 28V |
| **Track** | - | - | - | Track | Target | - | Track | 28V |
| **EW** | - | - | Null | Coord | - | Track | - | 270V |
| **Power** | - | Pwr | Pwr | Pwr | Pwr | Pwr | Pwr | - |

### Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                 SYSTEM INTEGRATION OVERVIEW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│         ┌─────────────┐                                        │
│         │ GPS TIMING  │                                        │
│         │ (HW-1)      │                                        │
│         └──────┬──────┘                                        │
│                │ 1PPS + 10 MHz (to all subsystems)             │
│    ┌───────────┼───────────┬───────────┬───────────┐           │
│    ▼           ▼           ▼           ▼           ▼           │
│ ┌──────┐  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐          │
│ │RF    │  │Antenna│   │Track │   │Data- │   │ EW   │          │
│ │Sensor│──│Array  │───│Proc  │───│link  │───│Suite │          │
│ │(HW-2)│  │(HW-3) │   │(HW-6)│   │(HW-4)│   │(HW-7)│          │
│ └──────┘  └──────┘   └──────┘   └───┬──┘   └──────┘          │
│                          │          │                          │
│                          ▼          ▼                          │
│                    ┌─────────────────────┐                     │
│                    │   WEAPON SYSTEM     │                     │
│                    │      (HW-5)         │                     │
│                    └─────────────────────┘                     │
│                                                                 │
│    ┌─────────────────────────────────────────────────────┐     │
│    │              POWER MANAGEMENT (HW-8)                 │     │
│    │         Provides 28V/270V to all subsystems          │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Hardware Verification Procedures

### Master Verification Checklist

| Step | Subsystem | Test | Duration | Pass Criteria |
|------|-----------|------|----------|---------------|
| 1 | Power (HW-8) | Generator start, bus voltages | 30s | All buses nominal |
| 2 | GPS (HW-1) | Acquire lock, verify timing | 60s | < 20 ns RMS |
| 3 | RF Sensors (HW-2) | Calibration sequence | 30s | < 1 dB error |
| 4 | Antenna (HW-3) | Element health, null test | 45s | > 98% elements |
| 5 | Tracking (HW-6) | Latency test | 30s | < 120 ms |
| 6 | Datalink (HW-4) | Link quality check | 30s | > 90% quality |
| 7 | Weapon (HW-5) | Self-test sequence | 30s | Status = PASS |
| 8 | EW Suite (HW-7) | Operational check | 30s | All modes ready |
| **Total** | - | - | **~5 min** | All pass |

### Verification State Diagram

```
                          Power-On
                             │
                             ▼
                     ┌───────────────┐
                     │  UNVERIFIED   │
                     └───────┬───────┘
                             │
                     Run Verification
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌─────────┐    ┌──────────┐    ┌────────┐
        │ VERIFIED│    │ DEGRADED │    │ FAILED │
        │         │    │          │    │        │
        │ All 8   │    │ 1-2 warn │    │ Any    │
        │ pass    │    │ non-crit │    │ crit   │
        └────┬────┘    └────┬─────┘    └────┬───┘
             │              │               │
             ▼              ▼               ▼
      ENGAGEMENT      LIMITED OPS     NO ENGAGEMENT
      AUTHORIZED      (with caveats)  (re-verify req)
```

### Continuous Monitoring

| Parameter | Monitor Rate | Alert Threshold | Critical Threshold |
|-----------|--------------|-----------------|-------------------|
| GPS Timing Error | 1 Hz | > 15 ns | > 20 ns |
| RF Calibration Age | 1 Hz | > 4 min | > 5 min |
| Antenna Elements | 10 Hz | 1 failure | 2 failures |
| Datalink Quality | 10 Hz | < 95% | < 90% |
| Tracking Latency | 10 Hz | > 100 ms | > 120 ms |
| EW Status | 1 Hz | Degraded mode | Non-operational |
| Power Reserve | 10 Hz | < 20% | < 15% |

---

## Document Revision History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2025-12-28 | Initial real hardware specifications for all 8 subsystems |
| 1.1 | 2025-12-28 | Added F-35/J-20/PL-15 specific real hardware references |
| 1.2 | 2025-12-28 | Added comprehensive global hardware comparison (12 nations) |

---

## Precision CAD Simulation Interface Specifications

### Purpose

This section defines precision hardware-accurate parameters for simulation use. All values are derived from real hardware systems and can be used directly in high-fidelity simulation environments.

### Simulation Parameter Precision Requirements

| Subsystem | Parameter | Precision | Real Hardware Basis |
|-----------|-----------|-----------|---------------------|
| GPS Timing | 1PPS accuracy | ≤ 10 ns | GPS-4000S / CETC-54 BD3 |
| GPS Timing | 10 MHz stability | 1×10⁻¹² @ 1s | Symmetricom XLi |
| GPS Timing | Holdover drift | 1 μs/day | Rubidium oscillator |
| RF Sensors | Noise figure | 0.1 dB resolution | ALR-94 / KLC-7 series |
| RF Sensors | Sensitivity | 1 dB resolution | -120 to -125 dBm |
| RF Sensors | Frequency accuracy | 100 Hz | Digital IF processor |
| Antenna Array | Phase accuracy | 0.1° resolution | 7-bit phase shifter |
| Antenna Array | Amplitude accuracy | 0.1 dB resolution | 6-bit attenuator |
| Antenna Array | Beam update rate | 10 μs | APG-81 / Type 1475 |
| Datalink | Uplink data rate | 1 kbps resolution | 16-100 kbps |
| Datalink | Latency | 1 ms resolution | 10-50 ms |
| Datalink | Link margin | 0.1 dB resolution | 10+ dB @ max range |
| Weapon System | Position accuracy | 0.1 m resolution | ECEF/WGS-84 |
| Weapon System | Velocity accuracy | 0.1 m/s resolution | 16-bit encoding |
| Weapon System | Acceleration accuracy | 0.01 m/s² resolution | 12-bit encoding |
| Tracking Processor | Track update rate | 10 Hz | AN/APG-81 / Type 1475 |
| Tracking Processor | Track capacity | Integer | 20-30 tracks |
| Tracking Processor | Position error | 1 m CEP | Kalman filter output |
| EW Suite | RWR sensitivity | 1 dB resolution | -75 to -85 dBm |
| EW Suite | Jamming power | 1 W resolution | 50-200W |
| EW Suite | AoA accuracy | 0.1° resolution | Interferometer |
| Power Management | Total power | 1 kVA resolution | 70-150 kVA |
| Power Management | Voltage | 1 V resolution | 115 VAC / 270 VDC |
| Power Management | Reserve margin | 1% resolution | 15-20% minimum |

### Real Hardware Model Parameters

#### AESA Radar Simulation Parameters

```
# F-35 AN/APG-81 Equivalent
radar_f35:
  frequency_hz: 10.0e9          # X-band center
  bandwidth_hz: 2.0e9           # Instantaneous
  peak_power_w: 20000           # 20 kW peak
  avg_power_w: 5000             # 5 kW average
  antenna_gain_dbi: 35.0        # Main beam
  antenna_elements: 1200        # T/R modules
  beamwidth_deg: 2.5            # 3 dB beamwidth
  scan_rate_hz: 100000          # 10 μs update
  sidelobe_dB: -40              # Adaptive null
  noise_figure_dB: 2.0          # Receiver
  detection_range_1sqm_km: 150  # vs 1m² RCS

# J-20 Type 1475 Equivalent
radar_j20:
  frequency_hz: 10.0e9          # X-band center
  bandwidth_hz: 1.5e9           # Instantaneous
  peak_power_w: 18000           # 18 kW peak
  avg_power_w: 4500             # 4.5 kW average
  antenna_gain_dbi: 33.0        # Main beam
  antenna_elements: 1400        # T/R modules (est.)
  beamwidth_deg: 3.0            # 3 dB beamwidth
  scan_rate_hz: 20000           # 50 μs update
  sidelobe_dB: -35              # Standard
  noise_figure_dB: 2.8          # Receiver
  detection_range_1sqm_km: 150  # vs 1m² RCS

# Su-57 N036 Byelka Equivalent
radar_su57:
  frequency_hz: 10.0e9          # X-band center
  bandwidth_hz: 1.5e9           # Instantaneous
  peak_power_w: 20000           # 20 kW peak
  avg_power_w: 5000             # 5 kW average
  antenna_gain_dbi: 34.0        # Main beam
  antenna_elements: 1552        # T/R modules
  beamwidth_deg: 2.8            # 3 dB beamwidth
  scan_rate_hz: 50000           # 20 μs update
  sidelobe_dB: -35              # Standard
  noise_figure_dB: 2.5          # Receiver
  detection_range_1sqm_km: 150  # vs 1m² RCS
```

#### BVR Missile Simulation Parameters

```
# AIM-120D AMRAAM
missile_aim120d:
  max_range_km: 160             # Max kinematic range
  max_speed_mach: 4.0           # Terminal velocity
  seeker_freq_hz: 10.0e9        # X-band seeker
  seeker_detection_km: 20       # Active acquisition
  seeker_fov_deg: ±30           # Gimbal limits
  datalink_uplink_kbps: 64      # Update rate
  datalink_downlink_kbps: 16    # Telemetry
  guidance: "INS_GPS_ARH"       # Mid-course + terminal
  warhead_kg: 23                # HE-Frag
  weight_kg: 162                # Launch weight

# PL-15
missile_pl15:
  max_range_km: 200             # Max kinematic range
  max_speed_mach: 4.5           # Terminal velocity
  seeker_freq_hz: 9.0e9         # C/X-band AESA
  seeker_detection_km: 30       # AESA acquisition
  seeker_fov_deg: ±45           # Wide angle AESA
  seeker_tracks: 4              # Multi-target
  datalink_uplink_kbps: 100     # Update rate
  datalink_downlink_kbps: 50    # Rich telemetry
  guidance: "INS_BeiDou_AESA"   # Mid-course + terminal
  warhead_kg: 25                # HE-Frag (est.)
  weight_kg: 210                # Launch weight (est.)

# Meteor (MBDA)
missile_meteor:
  max_range_km: 150             # Max kinematic range
  nez_km: 100                   # No-escape zone
  max_speed_mach: 4.0           # Variable thrust
  propulsion: "ramjet"          # Throttleable ducted rocket
  seeker_freq_hz: 10.0e9        # X-band (MICA derivative)
  seeker_detection_km: 25       # Active acquisition
  datalink_uplink_kbps: 50      # Update rate
  guidance: "INS_GPS_ARH"       # Mid-course + terminal
  warhead_kg: 25                # HE-Frag
  weight_kg: 190                # Launch weight

# R-37M (Russian)
missile_r37m:
  max_range_km: 300             # Max kinematic range
  max_speed_mach: 6.0           # High altitude
  seeker_freq_hz: 10.0e9        # Active radar
  seeker_detection_km: 35       # Large aperture
  datalink_uplink_kbps: 32      # Update rate
  guidance: "INS_GLONASS_ARH"   # Mid-course + terminal
  warhead_kg: 60                # HE-Frag
  weight_kg: 510                # Launch weight
```

#### Datalink Simulation Parameters

```
# F-35 MADL
datalink_madl:
  frequency_hz: 15.0e9          # Ku-band
  tx_power_w: 2                 # Low power directional
  antenna_gain_dbi: 20          # Steered beam
  beamwidth_deg: 3.0            # Narrow for LPI
  data_rate_mbps: 100           # Max throughput
  latency_ms: 10                # End-to-end
  max_range_km: 200             # Clear LOS
  nodes_max: 8                  # Flight size
  encryption: "AES-256"         # Type 1

# J-20 ACDL
datalink_acdl:
  frequency_hz: 15.0e9          # Ku-band (est.)
  tx_power_w: 5                 # Slightly higher power
  antenna_gain_dbi: 18          # Steered beam
  beamwidth_deg: 4.0            # Moderate
  data_rate_mbps: 50            # Max throughput
  latency_ms: 20                # End-to-end
  max_range_km: 150             # Clear LOS
  nodes_max: 8                  # Flight size
  encryption: "SM4"             # Chinese standard

# Weapon Uplink (F-35 to AIM-120D)
weapon_link_f35:
  frequency_hz: 10.0e9          # X-band via radar
  tx_power_w: 10                # Effective power
  antenna_gain_dbi: 35          # AESA main beam
  data_rate_kbps: 64            # Uplink
  update_rate_hz: 2             # Mid-course updates
  link_margin_dB: 10            # @ max range
  max_range_km: 160             # Weapon range

# Weapon Uplink (J-20 to PL-15)
weapon_link_j20:
  frequency_hz: 9.0e9           # C/X-band
  tx_power_w: 10                # Dedicated power
  antenna_gain_dbi: 33          # AESA beam
  data_rate_kbps: 100           # Uplink
  update_rate_hz: 2             # Mid-course updates
  link_margin_dB: 10            # @ max range
  max_range_km: 200             # Weapon range
```

#### EW Suite Simulation Parameters

```
# F-35 AN/ASQ-239 Barracuda
ew_f35:
  rwr_freq_min_hz: 2.0e9        # Low band
  rwr_freq_max_hz: 40.0e9       # High band
  rwr_sensitivity_dBm: -85      # High sensitivity
  rwr_aoa_accuracy_deg: 1.0     # Interferometer
  ecm_power_w: 100              # Solid state
  ecm_bandwidth_hz: 2.0e9       # Instantaneous
  drfm_channels: 16             # Simultaneous
  drfm_fidelity_bits: 14        # ADC resolution

# J-20 Internal EW
ew_j20:
  rwr_freq_min_hz: 2.0e9        # Low band
  rwr_freq_max_hz: 18.0e9       # Typical band
  rwr_sensitivity_dBm: -75      # Standard
  rwr_aoa_accuracy_deg: 2.0     # Standard
  ecm_power_w: 50               # Internal only
  ecm_bandwidth_hz: 1.0e9       # Instantaneous
  drfm_channels: 8              # Simultaneous
  drfm_fidelity_bits: 12        # ADC resolution

# Rafale SPECTRA
ew_rafale:
  rwr_freq_min_hz: 2.0e9        # Low band
  rwr_freq_max_hz: 40.0e9       # Wide band
  rwr_sensitivity_dBm: -75      # Standard
  rwr_aoa_accuracy_deg: 1.0     # High accuracy
  ecm_power_w: 100              # Phased array
  ecm_bandwidth_hz: 2.0e9       # Wideband
  drfm_channels: 12             # Simultaneous
  drfm_fidelity_bits: 14        # ADC resolution
```

### Simulation Validation Criteria

| Test | Parameter | Pass Criteria | Real Hardware Reference |
|------|-----------|---------------|-------------------------|
| Radar Detection | Range accuracy | ±5% of spec | APG-81 flight test data |
| Radar Detection | RCS estimation | ±3 dB | Calibrated target data |
| Missile Kinematics | Max range | ±10% of spec | Manufacturer data |
| Missile Kinematics | Terminal velocity | ±5% of spec | Flight test |
| Datalink | Throughput | ≥95% of spec | Lab test data |
| Datalink | Latency | ≤spec + 20% | Real-time test |
| EW | Detection sensitivity | ±3 dB of spec | Calibrated injection |
| EW | AoA accuracy | ≤spec × 2 | Anechoic chamber |
| GPS | Timing accuracy | ≤spec × 2 | USNO reference |
| GPS | Holdover | ≤spec × 3 | Lab characterization |

---

## References

### Military Standards
1. MIL-STD-1553B: Digital Time Division Command/Response Multiplex Data Bus
2. MIL-STD-1760: Aircraft/Store Electrical Interconnection System
3. MIL-STD-464: Electromagnetic Environmental Effects
4. MIL-PRF-38534: Hybrid Microcircuits, General Specification
5. IEEE 1588-2019: Precision Time Protocol (PTP)
6. ARINC 429: Digital Information Transfer System
7. ARINC 664 (AFDX): Aircraft Data Network

### F-35 Lightning II References
8. Lockheed Martin F-35 Lightning II: Technical Overview (Public Release)
9. Northrop Grumman AN/APG-81 AESA Radar Product Description
10. BAE Systems AN/ASQ-239 EW Suite Overview
11. Pratt & Whitney F135 Engine Integrated Power Package (Honeywell)
12. L3Harris F-35 Integrated Core Processor (ICP) Documentation
13. Northrop Grumman MADL Multi-Function Advanced Data Link

### J-20 Mighty Dragon References
14. AVIC Chengdu J-20 (Open Source Intelligence Analysis)
15. CETC-14 Nanjing Research Institute AESA Development
16. AVIC Engine Research: WS-10C/WS-15 Turbofan Specifications
17. BeiDou Navigation System B3I Signal ICD (Public)
18. Chinese EW Development: Academic Papers (NUDT, Beihang)

### PL-15 / Weapon System References
19. Luoyang Electro-Optical Equipment Research Institute: PL-15 (OSINT)
20. CPMIEC Air-to-Air Missile Product Line Analysis
21. Active Radar Homing Seeker Technology (Chinese Academic Sources)
22. Long-Range AAM Datalink Requirements (General Literature)

### Technical References
23. Skolnik: Radar Handbook (3rd Edition) - McGraw-Hill
24. Adamy: EW 101 - First Course in Electronic Warfare (Artech House)
25. Van Trees: Detection, Estimation, and Modulation Theory
26. Poisel: Electronic Warfare Target Location Methods
27. ITU-R P.676: Attenuation by Atmospheric Gases
28. ITU-R P.838: Specific Attenuation Model for Rain

### GPS/BeiDou Timing References
29. GPS ICD-200: Global Positioning System Interface Control Document
30. BeiDou ICD-2.0: BeiDou Navigation Satellite System Signal ICD
31. USNO: Naval Observatory GPS Timing Reference

### Russian Systems References
32. NIIP Tikhomirov N036 Byelka Development (KRET publications)
33. Sukhoi Su-57 PAK FA Technical Analysis (OSINT)
34. Vympel R-37M (AA-13 Axehead) Specifications
35. KRET L402 Himalayas EW System Overview
36. GLONASS-K ICD: Navigation Signal Interface

### European Systems References
37. MBDA Meteor BVRAAM Product Brochure (Public)
38. Thales RBE2-AA AESA Radar Specifications
39. SPECTRA EW System: Thales/MBDA Technical Data
40. Eurofighter Captor-E AESA Development
41. Saab PS-05/A Mk7 Gripen E Radar
42. Galileo PRS Signal ICD

### Japanese Systems References
43. Mitsubishi Electric AAM-4B (Type 99) Specifications
44. IHI XF9-1 Engine Technical Data
45. Japan F-3 Development Program (MOD)
46. QZSS L6E Timing Signal Specifications

### Israeli Systems References
47. Rafael I-Derby ER Product Sheet
48. ELTA EW Suite Development
49. Israel Aerospace Industries AESA Technology

### Indian Systems References
50. DRDO Astra Mk-2 BVRAAM Specifications
51. LRDE Uttam AESA Radar Development
52. ISRO NavIC ICD (L5/S-band)
53. HAL Tejas Mk2 Technical Program

### Korean/Turkish Systems References
54. KAI KF-21 Boramae Development Program
55. ASELSAN AESA Radar Development (KAAN)
56. Roketsan Gökdoğan BVR Missile

---

## Global Hardware Comparison

This section provides accurate specifications for BVR engagement hardware from all major military aviation nations. All specifications are derived from open-source intelligence, manufacturer publications, and defense analysis reports.

### Fighter Aircraft AESA Radar Comparison

| Nation | Platform | Radar | T/R Modules | Freq | Range (vs 1m² RCS) | Detection Range | Tracks |
|--------|----------|-------|-------------|------|---------------------|-----------------|--------|
| **USA** | F-35A | AN/APG-81 | 1,200+ | X-band | 150+ km | 250+ km | 20+ |
| **USA** | F-22A | AN/APG-77(v)1 | 2,000 | X-band | 200+ km | 400+ km | 20+ |
| **USA** | F-15EX | AN/APG-82(v)1 | 1,100 | X-band | 180+ km | 300+ km | 20+ |
| **China** | J-20 | Type 1475 | 1,000-1,800 | X-band | 150+ km | 300+ km | 15+ |
| **China** | J-16 | Type 1493 | 1,200+ | X-band | 180+ km | 320+ km | 18+ |
| **Russia** | Su-57 | N036 Byelka | 1,552 | X-band | 150 km | 350+ km | 30+ |
| **Russia** | Su-35S | N035 Irbis-E | 1,064 PESA | X-band | 200 km | 400 km | 30 |
| **EU** | Rafale F4 | RBE2-AA | 838 | X-band | 130 km | 250 km | 40 |
| **EU** | Typhoon | Captor-E | 1,425 | X-band | 150 km | 300 km | 24 |
| **Sweden** | Gripen E | PS-05/A Mk7 | 1,000 | X-band | 120 km | 200 km | 20 |
| **Japan** | F-3 (dev) | Mitsubishi AESA | 1,800+ | X-band | 180+ km | 350+ km | 20+ |
| **Korea** | KF-21 | AESA (dev) | 1,088 | X-band | 150 km | 250+ km | 15+ |
| **Turkey** | KAAN | ASELSAN AESA | 1,000+ | X-band | 150 km (est.) | 300+ km | 20+ |
| **India** | Tejas Mk2 | Uttam AESA | 780+ | X-band | 100+ km | 200+ km | 15 |

### BVR Missile Comparison (Active Radar Guided)

| Nation | Designation | Range | Speed | Seeker | Datalink | Guidance |
|--------|-------------|-------|-------|--------|----------|----------|
| **USA** | AIM-120D | 160+ km | Mach 4 | Active Radar | Two-way X-band | INS/GPS + ARH |
| **USA** | AIM-260 JATM | 200+ km | Mach 5+ | AESA | Two-way | INS/GPS + AESA |
| **China** | PL-15 | 200+ km | Mach 4+ | Active AESA | Two-way C/X | INS/BeiDou + AESA |
| **China** | PL-21 | 400+ km | Mach 6 | Active AESA | Two-way | Ramjet + AESA |
| **Russia** | R-77-1 | 110 km | Mach 4 | Active Radar | One-way | INS/GLONASS + ARH |
| **Russia** | R-37M | 300+ km | Mach 6 | Active Radar | Two-way | INS/GLONASS + ARH |
| **EU (UK)** | Meteor | 150+ km | Mach 4+ | Active Radar | Two-way | Ramjet + ARH |
| **EU (FR)** | MICA NG | 80+ km | Mach 4 | Active Radar/IR | One-way | INS + dual seeker |
| **Israel** | Derby ER | 100+ km | Mach 4 | Active Radar | One-way | INS + ARH |
| **Israel** | I-Derby ER | 100+ km | Mach 4 | Active Radar | Two-way | INS + ARH |
| **Japan** | AAM-4B | 120+ km | Mach 4+ | Active AESA | One-way | INS + AESA |
| **Japan** | JNAAM | 150+ km | Mach 4+ | Active Radar | Two-way | INS + ARH (Meteor-derived) |
| **India** | Astra Mk-2 | 100+ km | Mach 4 | Active Radar | Two-way | INS + ARH |
| **Turkey** | Gökdoğan | 65 km | Mach 4 | Active Radar | One-way | INS + ARH |
| **S. Korea** | KSS-2 | 100+ km | Mach 4 | Active Radar | TBD | INS + ARH |

### Intra-Flight Datalink Comparison

| Nation | System | Freq | Range | Data Rate | Nodes | LPI/LPD | Encryption |
|--------|--------|------|-------|-----------|-------|---------|------------|
| **USA** | MADL | Ku-band | 200+ km | 100 Mbps | 8 | High (directional) | Type 1 AES-256 |
| **USA** | Link-16 | L-band | 500+ km | 238 kbps | 128 | Low | Type 1 |
| **USA** | TTNT | UHF/C | 300+ km | 10 Mbps | 200+ | Medium | Type 1 |
| **China** | ACDL | Ku-band | 150+ km | 50 Mbps | 4-8 | High (directional) | SM4/ZUC |
| **China** | JIDS | UHF | 400+ km | 250 kbps | 100+ | Low | SM4 |
| **Russia** | S-111 | UHF | 300+ km | 256 kbps | 50+ | Low | Russian military |
| **Russia** | TKS-2 | Ku-band | 200+ km | 2+ Mbps | 8 | Medium | GOST encrypted |
| **NATO** | Link-16 | L-band | 500+ km | 238 kbps | 128 | Low | KY-58/Type 1 |
| **NATO** | MIDS-JTRS | L-band | 500+ km | 1+ Mbps | 128 | Medium | Type 1 |
| **UK** | MADL (F-35) | Ku-band | 200+ km | 100 Mbps | 8 | High | NSA Type 1 |
| **Japan** | JALN | UHF/SHF | 400+ km | 1+ Mbps | 100+ | Medium | Japanese military |
| **India** | SDR-Tactical | UHF | 200+ km | 256 kbps | 50+ | Low | AES-256 |

### EW Suite Comparison

| Nation | Platform | EW System | Freq Coverage | RWR Sensitivity | Jamming Power | DRFM |
|--------|----------|-----------|---------------|-----------------|---------------|------|
| **USA** | F-35 | AN/ASQ-239 | 2-40 GHz | -85 dBm | 100W+ | Yes |
| **USA** | F-22 | AN/ALR-94 | 0.5-40 GHz | -80 dBm | 50W | Yes |
| **USA** | F-15EX | EPAWSS | 2-18 GHz | -80 dBm | 100W+ | Yes (NextGen) |
| **China** | J-20 | Internal ESM/ECM | 2-18 GHz | -75 dBm | 50W+ | Yes |
| **China** | J-16D | CETC EW pod | 0.5-40 GHz | -80 dBm | 500W+ | Yes |
| **Russia** | Su-57 | L402 Himalayas | 2-18 GHz | -75 dBm | 200W+ | Yes |
| **Russia** | Su-35S | L265 Khibiny | 2-18 GHz | -70 dBm | 100W+ | Yes |
| **EU** | Rafale | SPECTRA | 2-40 GHz | -75 dBm | 100W+ | Yes |
| **EU** | Typhoon | DASS | 0.5-40 GHz | -75 dBm | 100W | Yes |
| **Sweden** | Gripen E | Arexis | 0.5-40 GHz | -80 dBm | 100W+ | Yes |
| **Japan** | F-2A | J/APR-4B | 2-18 GHz | -70 dBm | Pod only | Yes |
| **India** | Tejas Mk2 | Uttam EW | 2-18 GHz | -70 dBm | 50W | Planned |

### GPS/GNSS Timing Systems

| Nation | Constellation | Satellites | Military Signal | Timing Accuracy | Anti-Jam |
|--------|---------------|------------|-----------------|-----------------|----------|
| **USA** | GPS Block III | 31 | M-Code | < 5 ns | SAASM, MGUE |
| **China** | BeiDou-3 | 35+ | B3I Authorized | < 10 ns | Regional auth |
| **Russia** | GLONASS-K | 24+ | High-Accuracy | < 10 ns | Limited |
| **EU** | Galileo | 30 | PRS | < 5 ns | PRS encryption |
| **Japan** | QZSS | 7 | L6E | < 10 ns | Regional |
| **India** | NavIC | 9 | Restricted | < 20 ns | L5/S band |

### Power Management Systems

| Nation | Platform | Generator | Total Power | Voltage | APU |
|--------|----------|-----------|-------------|---------|-----|
| **USA** | F-35 | F135 IEPS | 150 kVA | 270 VDC | Honeywell APU |
| **USA** | F-22 | F119 + VSCF | 90 kVA | 270 VDC | Allied Signal APU |
| **China** | J-20 | WS-10C/WS-15 | 120+ kVA | 270 VDC (est.) | Domestic APU |
| **Russia** | Su-57 | AL-41F1 | 100+ kVA | 270 VDC | Russian APU |
| **EU** | Typhoon | EJ200 + IDG | 80 kVA | 115 VAC | Microturbo |
| **EU** | Rafale | M88 + IDG | 70 kVA | 115 VAC | Microturbo |
| **Sweden** | Gripen E | F414G | 65 kVA | 270 VDC | Single-engine |
| **Japan** | F-3 | XF9-1 | 120+ kVA | 270 VDC | TBD |

### Detailed Russian Systems (Su-57 Felon)

#### N036 Byelka AESA Radar System

| Parameter | Specification |
|-----------|---------------|
| **Designation** | N036 Byelka (Squirrel) |
| **Manufacturer** | NIIP Tikhomirov (part of KRET) |
| **Main Array** | 1,552 T/R modules (X-band) |
| **Side Arrays** | 2 × N036B (X-band, 358 modules each) |
| **L-band Arrays** | N036L wing-mounted arrays |
| **Detection Range** | 350+ km (vs 3m² RCS) |
| **Track Capacity** | 30 simultaneous, 8 engagement |
| **Scan Rate** | Electronic + mechanical |
| **Modes** | Air-to-air, air-to-ground, SAR/GMTI |
| **Power** | 5 kW average, 20 kW peak |

#### R-37M (AA-13 Axehead) Long-Range AAM

| Parameter | Specification |
|-----------|---------------|
| **Designation** | R-37M (Izdeliye 610M) |
| **Range** | 300+ km (some sources 400 km) |
| **Speed** | Mach 6 |
| **Length** | 4.06 m |
| **Weight** | 510 kg |
| **Warhead** | 60 kg HE-Frag |
| **Seeker** | 9B-1103M-350 active radar |
| **Datalink** | Onboard update capability |
| **Guidance** | INS + GLONASS + ARH terminal |
| **Primary Target** | AWACS, tankers, bombers |

### Detailed European Systems

#### MBDA Meteor BVRAAM

| Parameter | Specification |
|-----------|---------------|
| **Designation** | MBDA Meteor |
| **Users** | UK, France, Germany, Italy, Spain, Sweden |
| **Range** | 150+ km (200 km NEZ claimed) |
| **Speed** | Mach 4+ |
| **Length** | 3.65 m |
| **Weight** | 190 kg |
| **Propulsion** | Ramjet (throttleable ducted rocket) |
| **Seeker** | Active radar (derived from MICA) |
| **Datalink** | Two-way (with Rafale/Typhoon/Gripen) |
| **NEZ** | 3× AIM-120C (manufacturer claim) |
| **Key Advantage** | Sustained energy in terminal phase |

#### Rafale SPECTRA EW Suite

| Parameter | Specification |
|-----------|---------------|
| **Designation** | SPECTRA (Système de Protection et d'Évitement des Conduites de Tir du Rafale) |
| **Manufacturer** | Thales/MBDA |
| **Coverage** | 360° azimuth, ±60° elevation |
| **RWR Bands** | 2-40 GHz |
| **ESM Accuracy** | < 1° AoA |
| **Jamming** | Solid-state phased array |
| **DRFM** | Yes (coherent jamming) |
| **Decoys** | Flares, chaff, towed decoy |
| **Integration** | Fully integrated with RBE2 radar |

### Detailed Japanese Systems

#### AAM-4B (Type 99) BVR Missile

| Parameter | Specification |
|-----------|---------------|
| **Designation** | AAM-4B (Type 99 Mod.2) |
| **Manufacturer** | Mitsubishi Electric |
| **Range** | 120+ km |
| **Speed** | Mach 4+ |
| **Length** | 3.67 m |
| **Weight** | 224 kg |
| **Seeker** | Active AESA (unique feature) |
| **Datalink** | One-way update |
| **Guidance** | INS + AESA terminal |
| **Key Feature** | First AAM with AESA seeker |

#### XF9-1 Engine (F-3 Fighter)

| Parameter | Specification |
|-----------|---------------|
| **Designation** | XF9-1 |
| **Manufacturer** | IHI Corporation |
| **Thrust (dry)** | 11,000+ kgf |
| **Thrust (A/B)** | 15,000+ kgf |
| **Bypass Ratio** | 0.3 (low) |
| **TIT** | 1,800°C+ |
| **Power Extraction** | 180 kVA (designed for DEW) |
| **Status** | Testing complete, F-3 production planned |

### Detailed Israeli Systems

#### I-Derby ER BVRAAM

| Parameter | Specification |
|-----------|---------------|
| **Designation** | I-Derby ER (Extended Range) |
| **Manufacturer** | Rafael Advanced Defense |
| **Range** | 100+ km |
| **Speed** | Mach 4 |
| **Length** | 3.62 m |
| **Weight** | 118 kg |
| **Seeker** | Active radar (dual pulse Doppler) |
| **Datalink** | Two-way (optional) |
| **Guidance** | INS + GPS + ARH |
| **Key Feature** | Dual-pulse rocket motor |
| **Users** | Israel, Singapore, India (evaluation) |

### Detailed Indian Systems

#### Astra Mk-2 BVRAAM

| Parameter | Specification |
|-----------|---------------|
| **Designation** | Astra Mk-2 |
| **Manufacturer** | DRDO |
| **Range** | 100+ km (head-on) |
| **Speed** | Mach 4+ |
| **Length** | 3.8 m |
| **Weight** | 154 kg |
| **Seeker** | Active radar (indigenous) |
| **Datalink** | Two-way update |
| **Guidance** | INS + NavIC/GPS + ARH |
| **Status** | In production, deployed on Su-30MKI |

#### Uttam AESA Radar

| Parameter | Specification |
|-----------|---------------|
| **Designation** | Uttam (means "Best" in Sanskrit) |
| **Developer** | DRDO LRDE |
| **T/R Modules** | 780+ (GaN technology) |
| **Frequency** | X-band |
| **Detection Range** | 200+ km (vs 2m² RCS) |
| **Track Capacity** | 15 simultaneous |
| **Modes** | Air-to-air, air-to-ground, SAR |
| **Platform** | Tejas Mk1A, Mk2 |
| **Status** | Flight testing, production 2025+ |

### Global Capability Matrix Summary

| Nation | 5th Gen | AESA Radar | AESA AAM | Ramjet AAM | LPI Datalink | DRFM EW |
|--------|---------|------------|----------|------------|--------------|---------|
| **USA** | ✓ F-22, F-35 | ✓ | ✓ AIM-260 | ✗ | ✓ MADL | ✓ |
| **China** | ✓ J-20, J-31 | ✓ | ✓ PL-15 | ✓ PL-21 | ✓ ACDL | ✓ |
| **Russia** | ✓ Su-57 | ✓ | ✗ | ✗ | ○ | ✓ |
| **UK** | ✓ F-35B | ✓ | ✗ | ✓ Meteor | ✓ MADL | ✓ |
| **France** | ○ Rafale F5 | ✓ | ✗ | ✓ Meteor | ○ | ✓ |
| **Germany** | ✗ (FCAS dev) | ✓ Typhoon | ✗ | ✓ Meteor | ○ | ✓ |
| **Japan** | ○ F-3 dev | ✓ | ✓ AAM-4B | ○ JNAAM | ○ | ✓ |
| **Korea** | ○ KF-21 dev | ✓ | ✗ | ✗ | ○ | ○ |
| **India** | ○ AMCA dev | ✓ Uttam | ✗ | ✗ | ○ | ○ |
| **Israel** | ✓ F-35I | ✓ | ✗ | ✗ | ✓ (via F-35) | ✓ |
| **Turkey** | ○ KAAN dev | ✓ | ✗ | ✗ | ✗ | ○ |
| **Sweden** | ✗ | ✓ | ✗ | ✓ Meteor | ○ | ✓ |

Legend: ✓ = Operational | ○ = In Development | ✗ = Not Available

---

## Platform Summary

| Platform | Manufacturer | Role | Primary Sensors |
|----------|--------------|------|-----------------|
| **F-35A Lightning II** | Lockheed Martin | Multi-role stealth | AN/APG-81, AN/ASQ-239, AN/AAQ-37 DAS |
| **F-22A Raptor** | Lockheed Martin | Air superiority stealth | AN/APG-77, AN/ALR-94 |
| **J-20 Mighty Dragon** | AVIC Chengdu | Air superiority stealth | Type 1475 AESA, side ESM arrays |
| **Su-57 Felon** | Sukhoi/UAC | Multi-role stealth | N036 Byelka, L402 Himalayas |
| **Rafale F4** | Dassault | Multi-role | RBE2-AA, SPECTRA |
| **Typhoon Tranche 4** | Eurofighter | Multi-role | Captor-E, DASS |
| **Gripen E** | Saab | Multi-role | PS-05/A Mk7, Arexis |
| **PL-15** | CPMIEC/Luoyang | BVR AAM | Active AESA seeker, datalink |
| **AIM-120D AMRAAM** | Raytheon | BVR AAM | Active radar seeker, two-way datalink |
| **Meteor** | MBDA | BVR AAM | Active radar seeker, ramjet |
| **R-37M** | Vympel | Long-range AAM | Active radar seeker |

---

**HARDWARE VERIFICATION IS MANDATORY**

All 8 subsystems must pass verification before BVR precision engagement authorization.

**This document represents best-estimate specifications based on open-source intelligence, academic literature, and publicly available manufacturer data. Actual classified specifications may differ.**
