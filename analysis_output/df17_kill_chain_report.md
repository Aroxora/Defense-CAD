# DF-17 Hypersonic Glide Vehicle Kill Chain Analysis

**Generated:** 2026-01-15T14:56:44.935645
**System:** DF-17 with Beidou-3 Guidance
**AWACS Cueing:** KJ-500

## Executive Summary

The DF-17 hypersonic glide vehicle, integrated with Beidou-3 midcourse guidance and
AWACS target cueing, presents a significant capability against both moving and stationary
high-value targets. Analysis indicates:

- **Average Single-Shot Pk:** 31.9%
- **Targets Analyzed:** 6
- **Primary Advantage:** Terminal velocity Mach 5+ severely limits defensive options

## System Characteristics

### DF-17 Hypersonic Glide Vehicle

| Parameter | Value |
|-----------|-------|
| Maximum Range | 1800 km |
| Minimum Range | 500 km |
| Boost Burnout Altitude | 60 km |
| Terminal Velocity | Mach 5.0+ |
| Terminal Maneuver | 20 G |
| Cross-Range Capability | 400 km |
| CEP (estimated) | 15 m |

### Beidou-3 Guidance

| Parameter | Value |
|-----------|-------|
| Position Accuracy | 2.5 m |
| Velocity Accuracy | 0.10 m/s |
| Asia-Pacific Availability | 99.5% |
| Update Rate | 10 Hz |

### AWACS Platforms

| Platform | Detection Range | Track Accuracy |
|----------|-----------------|----------------|
| KJ-500 | 470 km | 150 m |
| KJ-2000 | 400 km | 200 m |

## Target Engagement Results

| Target | Type | Range | Single Pk | Salvo (90% Pk) | Salvo Pk |
|--------|------|-------|-----------|----------------|----------|
| USS Gerald R. Ford (CVN-78) | carrier_strike_group | 1000 km | 37.2% | 7 | 91.1% |
| Nimitz Class CVN | carrier_strike_group | 1000 km | 41.0% | 6 | 90.7% |
| THAAD Battery | thaad_battery | 800 km | 3.6% | 12 | 27.5% |
| Aegis Ashore (Romania/Poland type) | aegis_ashore | 800 km | 29.1% | 10 | 91.9% |
| Hardened Aircraft Shelter | airbase_hardened | 800 km | 14.5% | 12 | 74.5% |
| Airbase Runway/Taxiway | airbase_soft | 800 km | 65.8% | 3 | 92.4% |

## Kill Chain Breakdown

The DF-17 kill chain follows the sequence:

```
AWACS Detection → Launch → Beidou Midcourse → Terminal Dive → Seeker Lock → Impact
```

### Kill Chain Probabilities by Target

#### USS Gerald R. Ford (CVN-78)

| Phase | Probability |
|-------|-------------|
| AWACS Track | 89.2% |
| Launch Success | 98.0% |
| Beidou Guidance | 94.6% |
| Terminal Acquire | 83.3% |
| Defense Penetration | 63.1% |
| Hit | 90.0% |
| Kill Given Hit | 95.0% |
| **Total Single Pk** | **37.2%** |

#### Nimitz Class CVN

| Phase | Probability |
|-------|-------------|
| AWACS Track | 89.2% |
| Launch Success | 98.0% |
| Beidou Guidance | 94.6% |
| Terminal Acquire | 83.3% |
| Defense Penetration | 69.5% |
| Hit | 90.0% |
| Kill Given Hit | 95.0% |
| **Total Single Pk** | **41.0%** |

#### THAAD Battery

| Phase | Probability |
|-------|-------------|
| AWACS Track | 98.0% |
| Launch Success | 98.0% |
| Beidou Guidance | 99.6% |
| Terminal Acquire | 90.2% |
| Defense Penetration | 68.3% |
| Hit | 7.1% |
| Kill Given Hit | 86.7% |
| **Total Single Pk** | **3.6%** |

#### Aegis Ashore (Romania/Poland type)

| Phase | Probability |
|-------|-------------|
| AWACS Track | 98.0% |
| Launch Success | 98.0% |
| Beidou Guidance | 99.6% |
| Terminal Acquire | 90.2% |
| Defense Penetration | 55.0% |
| Hit | 91.4% |
| Kill Given Hit | 67.2% |
| **Total Single Pk** | **29.1%** |

#### Hardened Aircraft Shelter

| Phase | Probability |
|-------|-------------|
| AWACS Track | 98.0% |
| Launch Success | 98.0% |
| Beidou Guidance | 99.6% |
| Terminal Acquire | 90.2% |
| Defense Penetration | 80.3% |
| Hit | 62.5% |
| Kill Given Hit | 33.6% |
| **Total Single Pk** | **14.5%** |

#### Airbase Runway/Taxiway

| Phase | Probability |
|-------|-------------|
| AWACS Track | 98.0% |
| Launch Success | 98.0% |
| Beidou Guidance | 99.6% |
| Terminal Acquire | 90.2% |
| Defense Penetration | 80.3% |
| Hit | 100.0% |
| Kill Given Hit | 95.0% |
| **Total Single Pk** | **65.8%** |

## Key Findings

- DF-17 achieves average single-shot Pk of 31.9% across all targets
- Highest Pk: 65.8% against Airbase Runway/Taxiway
- Lowest Pk: 3.6% against THAAD Battery
- Moving targets (carriers) require larger salvos due to prediction uncertainty
- Hardened targets require multiple hits for assured destruction
- Beidou constellation provides reliable midcourse updates (99.5% availability)
- Terminal Mach 5+ severely degrades interceptor effectiveness
- Cross-range maneuver capability allows attack from unexpected angles

## Recommendations

- Use 4-6 missile salvos against carrier strike groups
- Time attacks to minimize CSG reaction time
- Coordinate with EW assets to degrade Aegis radar
- Pre-position reconnaissance for real-time target updates
- Maintain Beidou signal integrity during conflict

## Limitations and Uncertainties

- Terminal seeker performance against moving targets uncertain
- Defense capabilities may exceed open-source estimates
- Electronic warfare effects not fully modeled
- Actual CEP classified - estimates from open sources
- Multi-layer defense coordination not fully modeled

## Conclusion

The DF-17 HGV with integrated Beidou guidance and AWACS cueing provides a potent
precision strike capability. Key advantages include:

1. **Speed**: Terminal Mach 5+ reduces defensive engagement windows
2. **Maneuverability**: 20G terminal maneuvers complicate intercept solutions
3. **Guidance**: Beidou midcourse + seeker terminal provides high accuracy
4. **Range**: 500-1800 km range covers first island chain and beyond

Primary limitations remain terminal seeker performance against moving targets and
defense penetration against multi-layer systems. Salvo tactics recommended for
high-value targets.

---
*Analysis generated by DF-17 Kill Chain Calculator*
