# F-35 Integrated EW + Tracking + AIM-260 Datalink Operations

## Executive Summary

This document describes **single-platform** operations where an F-35A/B/C simultaneously:
1. Tracks stealth targets via integrated sensor suite (APG-81 + DAS + EOTS)
2. Jams enemy sensors/datalinks using ASQ-239 EW suite
3. Maintains AIM-260/AIM-120D mid-course guidance datalink (MADL)
4. Manages shared aperture and power resources

**Key Challenge:** Resource allocation across competing functions on shared hardware

---

## Part 1: F-35 Integrated System Architecture

### 1.1 Hardware Configuration

```
F-35 Integrated Sensor/Effector Suite:
┌────────────────────────────────────────────────────────────────┐
│              AN/APG-81 AESA Radar (Nose)                       │
│  - X-band (9.5-10.5 GHz)                                       │
│  - 1676 T/R elements                                           │
│  - Modes: Search, Track, SAR, GMTI, EW                         │
│  - Peak Power: 15-20 kW                                        │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│           AN/AAQ-37 Distributed Aperture System (DAS)          │
│  - 6× IR sensors (360° coverage)                               │
│  - Missile warning                                             │
│  - IRST targeting                                              │
│  - Passive track of aircraft/missiles                          │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│           AN/AAQ-40 Electro-Optical Targeting System (EOTS)    │
│  - Forward-looking FLIR                                        │
│  - Laser designation                                           │
│  - Passive targeting (IR)                                      │
│  - Long-range ID                                               │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│           AN/ASQ-239 Electronic Warfare Suite                  │
│  - 10× RF apertures (distributed)                              │
│  - ESM: 0.5-40 GHz coverage                                    │
│  - EA: Active jamming capability                               │
│  - RWR: Threat warning                                         │
│  - Geolocation: Passive targeting                              │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│           MADL (Multifunction Advanced Data Link)              │
│  - Directional Ku-band (14.5-15.5 GHz)                         │
│  - Low probability of intercept                                │
│  - Weapon datalink for AIM-260/AIM-120D                        │
│  - F-35 to F-35 sensor fusion                                  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│         Central Integrated Core Processor (ICP)                │
│  - Sensor fusion (all sensors + offboard data)                 │
│  - Track file management (1000+ tracks)                        │
│  - EW mission management                                       │
│  - Weapon datalink control                                     │
│  - Resource scheduler                                          │
└────────────────────────────────────────────────────────────────┘
```

### 1.2 Resource Allocation Problem

**Shared Resources:**
1. **Aperture Time:** APG-81 AESA can't transmit and receive simultaneously
2. **Processing Power:** ICP limited (but very capable)
3. **Electrical Power:** 160+ kW available (IPP)
4. **Thermal Budget:** Integrated cooling system
5. **EM Spectrum:** Frequency bands must be coordinated

**Example Power Budget:**

```python
class F35PowerBudget:
    """
    Manages electrical power allocation across F-35 systems
    """

    TOTAL_AVAILABLE_POWER_KW = 160  # Integrated Power Package (IPP)

    BASELINE_LOADS = {
        'flight_control': 15,      # kW
        'avionics': 25,
        'cooling': 30,
        'other': 15
    }

    SENSOR_EFFECTOR_MODES = {
        'apg81_search': 25,        # kW average (full scan)
        'apg81_track': 12,         # Lower duty cycle
        'apg81_sar': 20,           # Synthetic aperture
        'apg81_gmti': 18,          # Ground moving target
        'apg81_jam': 35,           # High power EA transmit
        'asq239_esm': 8,           # Passive (processing power)
        'asq239_jam': 25,          # Active jamming
        'das_active': 5,           # DAS processing
        'eots_active': 3,          # EOTS processing
        'madl_datalink': 5,        # Weapon datalink + friendly
    }

    def compute_available_power(self, active_modes: List[str]) -> float:
        """
        Calculate remaining power budget

        Returns: Available power in kW
        """
        baseline = sum(self.BASELINE_LOADS.values())  # 85 kW
        sensor_load = sum([self.SENSOR_EFFECTOR_MODES[mode] for mode in active_modes])

        available = self.TOTAL_AVAILABLE_POWER_KW - baseline - sensor_load
        # Available for sensors: ~75 kW

        return available

    def select_optimal_modes(self,
                           engagement_phase: str,
                           threat_level: str) -> List[str]:
        """
        Select sensor/effector modes based on engagement phase

        Prioritization:
        1. Weapon datalink (mission critical during mid-course)
        2. Track maintenance (must maintain lock)
        3. Self-protection jamming (if under attack)
        4. Passive sensors (DAS, EOTS for SA)
        """

        if engagement_phase == 'DETECTION':
            # Passive detection priority, low emissions
            modes = ['das_active', 'eots_active', 'asq239_esm', 'madl_datalink']

        elif engagement_phase == 'TRACK_REFINEMENT':
            # Multi-sensor fusion + LPI radar
            modes = ['apg81_track', 'das_active', 'asq239_esm', 'madl_datalink']

        elif engagement_phase == 'PRE_LAUNCH':
            # Active track + fire control
            modes = ['apg81_track', 'das_active', 'asq239_esm']
            if threat_level == 'HIGH':
                modes.append('asq239_jam')  # Self-protection

        elif engagement_phase == 'MID_COURSE':
            # CRITICAL: Weapon datalink is priority
            modes = ['madl_datalink', 'apg81_track', 'das_active', 'asq239_esm']

            # Add jamming if power available
            power_used = sum([self.SENSOR_EFFECTOR_MODES[m] for m in modes])
            if (self.TOTAL_AVAILABLE_POWER_KW - sum(self.BASELINE_LOADS.values()) - power_used) > 30:
                modes.append('asq239_jam')  # Offensive/defensive jamming

        elif engagement_phase == 'TERMINAL':
            # Missile autonomous, maximize jamming
            modes = ['apg81_track', 'asq239_jam', 'das_active']

        return modes
```

---

## Part 2: Time-Shared Aperture Management

### 2.1 APG-81 AESA Time Slicing

**Problem:** Single AESA can't track, jam, and search simultaneously

**Solution:** Rapid time-division multiplexing with priority scheduling

```
Time Frame: 100 ms (10 Hz update rate)
┌──────────────────────────────────────────────────────────┐
│  0-15ms: Passive ESM (ASQ-239 listening)                 │
│          APG-81: OFF (reduced signature)                 │
│          DAS: Continuous IR surveillance                 │
│          → Passive threat detection                      │
├──────────────────────────────────────────────────────────┤
│  15-25ms: LPI Radar Pulse (APG-81 transmit)              │
│           Short burst, frequency-agile waveform          │
│           Low sidelobes, narrow beam                     │
│           → Target illumination                          │
├──────────────────────────────────────────────────────────┤
│  25-40ms: Radar Receive (APG-81 receive)                 │
│           Matched filter processing                      │
│           Clutter cancellation                           │
│           → Target detection + tracking                  │
├──────────────────────────────────────────────────────────┤
│  40-50ms: Track Update (ICP processing)                  │
│           Fuse APG-81 + DAS + EOTS + ESM                 │
│           Update Kalman filter                           │
│           → Position/velocity/ID estimate                │
├──────────────────────────────────────────────────────────┤
│  50-60ms: AIM-260 Datalink Update (MADL transmit)        │
│           Mid-course correction                          │
│           Ku-band directional antenna                    │
│           → Weapon guidance update                       │
├──────────────────────────────────────────────────────────┤
│  60-100ms: EW Window (if needed)                         │
│            ASQ-239: Active jamming (X/Ku-band)           │
│            APG-81: Can contribute EA if power available  │
│            → Suppress enemy radar/datalink               │
└──────────────────────────────────────────────────────────┘

Duty Cycles:
  Passive ESM: 15% + continuous DAS/EOTS
  Active Radar: 25% (LPI mode)
  Jamming: 40% (when threat present)
  Datalink: 10%
  Processing: 10%
```

---

## Part 3: Integrated Track-While-Jam

### 3.1 Frequency Separation Strategy

**Key Insight:** F-35 uses different sensors and frequencies for tracking vs. jamming

```
TRACKING (Multi-Sensor):
  APG-81: X-band (9.5-10.5 GHz) - Active radar
  DAS: IR spectrum (3-5 µm, 8-12 µm) - Passive
  EOTS: IR/Visible - Passive
  ASQ-239 ESM: RF geolocation - Passive
  → Fused track from multiple phenomenologies

JAMMING (Active EA):
  ASQ-239: Responsive jamming on threat frequencies
  APG-81 EA mode: High-power spot jamming (if needed)
  → Frequency-agile to match threat

KEY: Passive sensors (DAS, EOTS) provide CONTINUOUS track
     even when radar/ESM is busy jamming
     → No self-interference
```

**Spectral Allocation:**

```python
class F35SpectrumManager:
    """
    Manages frequency allocation to prevent self-jamming
    """

    def __init__(self):
        self.protected_bands = []  # Frequencies we're using
        self.jamming_bands = []

    def allocate_engagement_spectrum(self) -> Dict[str, List[Tuple[float, float]]]:
        """
        Allocate spectrum for simultaneous track + jam
        """

        allocation = {
            # TRACKING (must protect from own jamming)
            'apg81_radar': [(9.5e9, 10.5e9)],     # X-band
            'madl_datalink': [(14.5e9, 15.5e9)],  # Ku-band

            # JAMMING (active transmit on threat bands)
            'jam_j20_radar': [
                (9.0e9, 9.5e9),     # Below our radar
                (10.5e9, 12.0e9)    # Above our radar
            ],
            'jam_enemy_datalink': [
                (12.0e9, 14.5e9),   # Below MADL
                (15.5e9, 18.0e9)    # Above MADL
            ],

            # ALWAYS AVAILABLE (passive)
            'das_ir': 'infrared (passive)',
            'eots_ir': 'infrared (passive)',
            'esm_receive': [(0.5e9, 40e9)]  # Wideband receive
        }

        # Verify no overlap
        self._verify_no_overlap(
            allocation['apg81_radar'] + allocation['madl_datalink'],
            allocation['jam_j20_radar'] + allocation['jam_enemy_datalink']
        )

        return allocation
```

### 3.2 Sensor Fusion for Continuous Track

**Problem:** If APG-81 is jamming, how do we maintain target track?

**Solution:** DAS + EOTS provide continuous passive tracking

```python
class F35SensorFusion:
    """
    Fuses multiple F-35 sensors for robust target tracking
    """

    def __init__(self):
        self.sensors = {
            'APG81': {'type': 'radar', 'active': True, 'priority': 1},
            'DAS': {'type': 'IR', 'active': False, 'priority': 2},
            'EOTS': {'type': 'IR', 'active': False, 'priority': 3},
            'ASQ239': {'type': 'ESM', 'active': False, 'priority': 4},
        }

    def maintain_track_while_jamming(self,
                                    target_track: TargetTrack,
                                    jamming_active: bool) -> TargetTrack:
        """
        Maintain target track even when APG-81 is in EA mode

        When jamming:
        - APG-81: Unavailable for tracking (EA mode)
        - DAS: Provides IR track (continuous)
        - EOTS: Provides narrow-FOV IR track
        - ASQ-239: Provides RF geolocation (target emissions)

        Returns: Fused track from available sensors
        """

        available_sensors = []

        if not jamming_active:
            available_sensors.append('APG81')

        # Passive sensors always available
        available_sensors.extend(['DAS', 'EOTS', 'ASQ239'])

        # Weight sensors by availability and accuracy
        weights = {
            'APG81': 0.5 if not jamming_active else 0.0,
            'DAS': 0.25,
            'EOTS': 0.15,
            'ASQ239': 0.10
        }

        # Fuse tracks with appropriate weights
        fused_position = np.zeros(3)
        fused_velocity = np.zeros(3)
        total_weight = 0.0

        for sensor in available_sensors:
            sensor_track = self._get_sensor_track(sensor, target_track)
            if sensor_track is not None:
                w = weights[sensor]
                fused_position += w * sensor_track.position
                fused_velocity += w * sensor_track.velocity
                total_weight += w

        if total_weight > 0:
            fused_position /= total_weight
            fused_velocity /= total_weight

        # Update track
        target_track.position = fused_position
        target_track.velocity = fused_velocity
        target_track.confidence = total_weight / sum(weights.values())

        return target_track
```

---

## Part 4: Multi-Ship Coordinated Operations

### 4.1 Formation EW/Track Coordination

**F-35 4-Ship Division of Labor:**

```
Scenario: 4-ship F-35 formation engaging J-20 flight

F-35 #1 (Flight Lead / Shooter):
  Primary Role: Track + AIM-260 guidance
  - APG-81: Active tracking (reduced EA)
  - DAS/EOTS: Continuous SA
  - MADL: Weapon datalink active
  - Jamming: Self-protection only

F-35 #2 (Wingman / Primary Jammer):
  Primary Role: Offensive EW support
  - APG-81: EA mode (high-power jamming)
  - ASQ-239: Responsive jamming
  - DAS: Backup tracking
  - MADL: Receive track data from #1

F-35 #3 (Element Lead / Backup Shooter):
  Primary Role: Track + backup weapons
  - APG-81: Active tracking
  - DAS/EOTS: Continuous SA
  - MADL: Share track data
  - Jamming: Minimal

F-35 #4 (Wingman / Secondary Jammer):
  Primary Role: Flank coverage + EW
  - APG-81: Split mode (track + EA)
  - ASQ-239: Sector jamming
  - DAS: 360° coverage
  - MADL: Share SA data

Advantage: Role specialization allows maximum jamming
           while maintaining clean tracks for weapons
```

### 4.2 MADL Cooperative Engagement

```python
class F35MADLCoordination:
    """
    Coordinates F-35 formation via MADL for cooperative engagement
    """

    def __init__(self, flight_members: List[str]):
        self.members = flight_members
        self.shared_track_file = {}

    def execute_cooperative_engagement(self,
                                      target_tracks: List[TargetTrack]) -> Dict:
        """
        Execute coordinated engagement using MADL fusion

        MADL enables:
        - Real-time track sharing (position, velocity, ID)
        - Cooperative engagement (F-35 #2 shoots on #1's track)
        - Launch-on-remote (weapon uses another F-35's sensor)
        - Coordinated jamming (frequency deconfliction)
        """

        engagement_plan = {
            'shared_tracks': [],
            'shooter_assignments': {},
            'jammer_assignments': {},
            'weapon_allocations': {}
        }

        # Fuse all member tracks via MADL
        for track in target_tracks:
            fused_track = self._fuse_madl_tracks(track)
            engagement_plan['shared_tracks'].append(fused_track)

        # Assign shooters (those with best geometry)
        engagement_plan['shooter_assignments'] = self._assign_shooters(
            engagement_plan['shared_tracks'])

        # Assign jammers (maximize separation from shooters)
        engagement_plan['jammer_assignments'] = self._assign_jammers(
            engagement_plan['shooter_assignments'])

        # Allocate weapons
        engagement_plan['weapon_allocations'] = self._allocate_weapons(
            engagement_plan['shared_tracks'],
            engagement_plan['shooter_assignments'])

        return engagement_plan

    def _fuse_madl_tracks(self, track: TargetTrack) -> TargetTrack:
        """
        Fuse track data from all MADL-linked F-35s

        Each F-35 contributes:
        - APG-81 radar track (if available)
        - DAS IR track
        - EOTS precision track
        - ASQ-239 geolocation

        Result: Superior accuracy from 4× sensor contributors
        """

        contributions = []

        for member in self.members:
            member_track = self._get_member_contribution(member, track)
            if member_track:
                contributions.append(member_track)

        # Weighted fusion (more contributors = better accuracy)
        fused = self._weighted_fusion(contributions)

        # Accuracy improvement from MADL fusion
        # 4 aircraft contributing: ~50% CEP improvement
        fused.cep_m = track.cep_m * (1.0 / np.sqrt(len(contributions)))

        return fused
```

---

## Part 5: Operational Employment

### 5.1 Single-Ship Engagement Timeline (F-35 Solo vs J-20)

```
T-200s: Initial Detection (Passive)
  - DAS detects J-20 IR signature (afterburner or contrail)
  - ASQ-239 ESM detects J-20 radar emissions
  - NO F-35 emissions (covert approach)
  - Track confidence: 40%

T-150s: Track Refinement (LPI Radar)
  - APG-81 LPI scan (low power, frequency agile)
  - DAS continues IR track
  - EOTS slaved to target for ID
  - Track confidence: 70%

T-90s: Target Identification
  - EOTS provides visual ID
  - ASQ-239 confirms J-20 radar signature
  - APG-81 track refined
  - Track confidence: 85%

T-45s: Pre-Launch (Fire Control)
  - APG-81 weapon-quality track
  - Fire control solution computed
  - Assess AIM-260 Pk: 65%+
  - Track confidence: 95%

T-15s: Weapon Employment
  - AIM-260 launch
  - Immediately begin MADL datalink updates
  - Reduce APG-81 power (maintain track)
  - Enable ASQ-239 self-protection EA

T+0 to T+120s: Mid-Course Guidance
  Time budget (100 ms frame):
    - 0-15ms: Passive sensors (DAS, ESM)
    - 15-40ms: APG-81 track update (reduced duty)
    - 40-50ms: ICP fusion + prediction
    - 50-60ms: MADL datalink to AIM-260
    - 60-100ms: ASQ-239 jamming (if needed)

  Update rate: Every 2 seconds
  Track accuracy maintained: <15m CEP (sensor fusion)

T+120s: Terminal Handoff
  - Final MADL update (position + velocity)
  - AIM-260 seeker activates
  - F-35 increases jamming power

T+130s: Impact (expected)
  - F-35 continues jamming (deny J-20 countermeasures)
  - DAS monitors for secondary targets
  - Prepare for next engagement or egress
```

### 5.2 4-Ship Coordinated Timeline

```
T-180s: Initial Detection (Lead F-35)
  - Lead F-35 detects J-20 via passive sensors
  - MADL shares contact with flight

T-150s: Multi-Ship Track (All F-35s)
  - All 4 F-35s contribute sensor data via MADL
  - Fused track significantly more accurate
  - Flight assigns roles (2 shooters, 2 jammers)

T-90s: Pre-Launch Preparation
  - Shooters (#1, #3) refine fire control solutions
  - Jammers (#2, #4) prepare EA programs
  - Frequency deconfliction via MADL

T-45s: Salvo Launch
  - F-35 #1 launches AIM-260 at J-20 #1
  - F-35 #3 launches AIM-260 at J-20 #2
  - F-35 #2, #4 begin full-power jamming

T+0 to T+120s: Mid-Course Phase
  - Shooters maintain track + datalink
  - Jammers provide cover (J-20 radar/datalink degraded)
  - MADL coordinates all activities

T+120s: Terminal Phase
  - AIM-260 seekers active
  - All F-35s shift to maximum jamming
  - DAS monitors for additional threats

T+130s: Impact / BDA
  - DAS confirms hits via IR signature
  - MADL shares battle damage assessment
  - Flight reforms for next engagement
```

---

## Part 6: Performance Summary

### Single F-35 Capabilities

| Metric | Performance |
|--------|-------------|
| Detection Range (APG-81 vs J-20) | 120-150 km |
| Detection Range (DAS IR) | 80-120 km |
| Track Accuracy (Radar Only) | 20-40m CEP |
| Track Accuracy (Fused) | 10-20m CEP |
| AIM-260 Mid-Course Update Rate | 0.5 Hz (every 2 sec) |
| Jamming Power (ASQ-239) | 20-25 kW EIRP |
| Jamming Power (APG-81 EA) | 30 kW EIRP |
| Self-Jamming Risk | <-40 dB (negligible) |

### 4-Ship Coordinated

| Metric | Performance |
|--------|-------------|
| Detection Range (Fused) | 150-200 km |
| Track Accuracy (4-ship MADL fusion) | 8-12m CEP |
| Jamming Power (Combined) | 80 kW EIRP |
| Simultaneous Engagements | 4+ targets |
| Cooperative Pk (per target) | 0.85+ |
| BVR Pk (200km, 4-ship salvo) | 0.95+ (vs 2 J-20s) |

---

## Conclusion

**Single F-35 can execute integrated track + jam + AIM-260 guidance** through:

1. **Time-Division Multiplexing:** 100ms frames with prioritized slots
2. **Multi-Sensor Fusion:** APG-81 + DAS + EOTS + ESM provides redundancy
3. **Frequency Separation:** Tracking and jamming use different bands
4. **Passive Sensors:** DAS/EOTS maintain track even during heavy jamming

**4-Ship coordination provides:**
- **Role specialization:** Shooters track, jammers cover
- **4× sensor contributors:** 8-12m CEP (vs 15-20m single-ship)
- **Combined jamming power:** 80 kW (vs 25 kW single-ship)
- **Higher Pk:** 0.95+ salvo vs 0.65 single-ship

**Enables true BVR precision engagement against stealth targets at 150-250 km range.**
