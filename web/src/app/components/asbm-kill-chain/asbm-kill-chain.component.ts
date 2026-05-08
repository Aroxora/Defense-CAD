import { Component, signal, computed, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import * as d3 from 'd3';

import {
  MissileSystem,
  KillChainPhase,
  SensorNode,
  CounterTargetingParam,
  MonteCarloScenario,
  Countermeasure,
  MissileId,
  TechnicalDerivation,
  SignalProcessingBlock,
  EngagementGeometry,
  MissilePlatformData,
  SubsystemDetail,
  SubsystemCategory
} from './asbm-kill-chain.interfaces';

import { DF21D_SUBSYSTEMS, DF26_SUBSYSTEMS, DF17_SUBSYSTEMS } from './asbm-kill-chain.missile-subsystems';
import { ISR_C2_SUBSYSTEMS } from './asbm-kill-chain.isr-subsystems';

@Component({
  selector: 'app-asbm-kill-chain',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './asbm-kill-chain.component.html',
  styleUrl: './asbm-kill-chain.component.scss'
})
export class AsbmKillChainComponent implements OnInit, AfterViewInit {
  authenticated = false;
  passwordInput = '';
  passwordError = false;

  checkPassword(): void {
    if (this.passwordInput === 'SecretPlanGoldenFleet12)') {
      this.authenticated = true;
      this.passwordError = false;
    } else {
      this.passwordError = true;
    }
  }

  @ViewChild('killChainTimeline') killChainTimeline!: ElementRef;
  @ViewChild('sensorNetworkChart') sensorNetworkChart!: ElementRef;
  @ViewChild('monteCarloChart') monteCarloChart!: ElementRef;
  @ViewChild('trajectoryChart') trajectoryChart!: ElementRef;
  @ViewChild('platformComparisonChart') platformComparisonChart!: ElementRef;
  @ViewChild('signalProcessingChart') signalProcessingChart!: ElementRef;

  readonly Math = Math;
  readonly Object = Object;

  activeKillChainPhase = signal<number>(0);
  selectedMissile = signal<MissileId>('df17');
  showEquations = signal(false);
  activeDerivationSection = signal<string>('trajectory');
  activeProcessingStep = signal<number>(0);

  missileSystemsData = signal<MissileSystem[]>([
    {
      name: 'DF-21D',
      designation: 'CSS-5 Mod 4',
      range_km: 1500,
      warhead: 'Conventional / Nuclear',
      cep_m: '20-40',
      guidance: 'INS / Radar seeker terminal',
      speed: 'Mach 10 reentry',
      launch_platform: 'TEL (road-mobile)',
      classification: 'ESTIMATED'
    },
    {
      name: 'DF-26',
      designation: 'CSS-18',
      range_km: 4000,
      warhead: 'Conventional / Nuclear',
      cep_m: '30-50',
      guidance: 'INS / Stellar-aided / Radar seeker',
      speed: 'Mach 18 reentry',
      launch_platform: 'TEL (road-mobile)',
      classification: 'ESTIMATED'
    },
    {
      name: 'DF-17',
      designation: 'CSS-22',
      range_km: '1800-2500',
      warhead: 'Conventional (HGV)',
      cep_m: '10-20',
      guidance: 'INS / Radar seeker + Glide control',
      speed: 'Mach 10+ glide',
      launch_platform: 'TEL (road-mobile)',
      classification: 'ESTIMATED'
    }
  ]);

  killChainPhases = signal<KillChainPhase[]>([
    {
      phase: 'Wide-Area Surveillance',
      time_min: 'T+0',
      system: 'OTH-B Skywave radar, Yaogan/Jilin satellites, maritime patrol',
      description: 'Broad-area search for carrier strike group using over-the-horizon radar, space-based ISR, and maritime patrol aircraft.',
      sensors: ['OTH-B radar', 'Yaogan SAR', 'Jilin-1 optical', 'Y-8Q MPA'],
      vulnerabilities: ['ASAT', 'Cyber attack on ground stations', 'OTH-B jamming']
    },
    {
      phase: 'Detection & Cueing',
      time_min: 'T+5',
      system: 'Initial detection of carrier group, track file initiation',
      description: 'Initial detection of carrier group, track file initiation. OTH-B provides rough position cue to satellite tasking.',
      sensors: ['OTH-B', 'ELINT satellites', 'Fishing fleet reports'],
      vulnerabilities: ['EMCON discipline', 'Emissions deception']
    },
    {
      phase: 'Target Discrimination',
      time_min: 'T+10',
      system: 'SAR satellite imagery analysis',
      description: 'Separating carrier from escorts/decoys, SAR satellite passes. Identifying the high-value unit within the strike group.',
      sensors: ['Yaogan SAR triplets', 'Yaogan ELINT'],
      vulnerabilities: ['Decoys', 'Formation spacing', 'SAR satellite revisit gaps']
    },
    {
      phase: 'Track Refinement',
      time_min: 'T+15',
      system: 'Multi-source data fusion',
      description: 'Multi-source fusion combining satellite, OTH-B, SIGINT, and maritime militia reports to refine carrier position and course.',
      sensors: ['BeiDou navigation', 'Data fusion center', 'Maritime militia HUMINT'],
      vulnerabilities: ['Kill chain disruption', 'Time-late data', 'Carrier maneuver']
    },
    {
      phase: 'Launch Authorization',
      time_min: 'T+18',
      system: 'Command and control chain',
      description: 'Command chain authorization, targeting data package assembly, TEL coordinates uploaded to missile.',
      sensors: ['C2 network', 'BeiDou'],
      vulnerabilities: ['Decapitation strike', 'Cyber attack on C2', 'Decision paralysis']
    },
    {
      phase: 'Boost Phase',
      time_min: 'T+20',
      system: 'Ballistic launch',
      description: 'Ballistic launch from TEL, initial guidance via INS. Missile ascends through atmosphere on ballistic trajectory.',
      sensors: ['INS (ring laser gyro)'],
      vulnerabilities: ['Boost-phase intercept (theoretical)', 'Launch site detection by satellite']
    },
    {
      phase: 'Midcourse',
      time_min: 'T+25',
      system: 'INS + stellar navigation + datalink',
      description: 'INS + stellar navigation + datalink updates; DF-17 HGV separation and glide phase begins. Midcourse corrections applied.',
      sensors: ['Stellar nav sensor', 'BeiDou datalink', 'Ground radar updates'],
      vulnerabilities: ['SM-3 Block IIA midcourse intercept', 'Datalink jamming']
    },
    {
      phase: 'Terminal',
      time_min: 'T+28-30',
      system: 'Onboard seeker acquisition',
      description: 'Onboard seeker acquisition (radar/IR), terminal maneuver, impact. Seeker searches for carrier-sized target and homes in.',
      sensors: ['Onboard radar seeker', 'Possible IR seeker'],
      vulnerabilities: ['SM-6 terminal intercept', 'Nulka/SRBOC decoys', 'CIWS last-ditch']
    }
  ]);

  sensorArchitecture = signal<SensorNode[]>([
    {
      id: 'othb',
      name: 'OTH-B Radar',
      type: 'radar',
      range_km: 3000,
      description: 'Over-the-horizon backscatter radar for wide-area maritime surveillance',
      coverage: 'Western Pacific arc 60° sector'
    },
    {
      id: 'yaogan',
      name: 'Yaogan Constellation',
      type: 'satellite',
      range_km: 'global',
      description: 'SAR/ELINT/Optical satellite triplets for maritime ISR',
      coverage: 'SAR/ELINT/Optical triplets, ~20 satellites'
    },
    {
      id: 'beidou',
      name: 'BeiDou Navigation',
      type: 'satellite',
      range_km: 'global',
      description: 'Position, Navigation, and Timing service for missile guidance',
      coverage: 'PNT service, 35 satellites, centimeter accuracy'
    },
    {
      id: 'militia',
      name: 'Maritime Militia',
      type: 'humint',
      range_km: 500,
      description: 'Civilian fishing fleet providing surveillance and reporting',
      coverage: 'South China Sea, East China Sea fishing fleets'
    },
    {
      id: 'subsigint',
      name: 'Submarine SIGINT',
      type: 'sigint',
      range_km: 200,
      description: 'Forward-deployed submarines conducting passive signals collection',
      coverage: 'Forward-deployed SSN/SSK passive collection'
    },
    {
      id: 'wz7',
      name: 'WZ-7 Soaring Dragon',
      type: 'uav',
      range_km: 2000,
      description: 'High-altitude long-endurance ISR UAV with SAR/ELINT payload',
      coverage: 'High-altitude ISR, SAR/ELINT payload'
    }
  ]);

  hgvTechnicalData = signal({
    glideDynamics: {
      liftToDrag: '3.5-4.5',
      glideRange_km: '1800-2500',
      maxSpeed_mach: 10,
      cruiseAltitude_km: '40-60',
      pullUpAltitude_km: '20-30',
      terminalDiveAngle_deg: '30-60'
    },
    heatShield: {
      maxTemp_C: 2000,
      material: 'Carbon-carbon composite / UHTC',
      noseRadius_m: 0.15
    },
    maneuverEnvelope: {
      maxLateralAccel_g: '5-10',
      crossRange_km: '±400',
      skipGlide: false,
      boostGlide: true
    },
    seekerAcquisition: {
      type: 'Active radar + possible IR',
      acquisitionRange_km: '30-50',
      scanCone_deg: 30
    },
    bmdDefeat: {
      description: 'HGV defeats SM-3/SM-6/THAAD by flying a depressed trajectory below SM-3 engagement altitude, maintaining high maneuverability (5-10g lateral) that exceeds interceptor divert capability, and cruising at 40-60km altitude — too low for exoatmospheric interceptors (SM-3) and too fast/maneuverable for endoatmospheric interceptors (SM-6). THAAD is designed for ballistic reentry vehicles and lacks the seeker agility to track a maneuvering glider.'
    }
  });

  counterTargetingData = signal<CounterTargetingParam[]>([
    {
      name: 'CEP vs Ship Speed',
      value: 'V_ship = 30 kts (15.4 m/s), t_stale = 15 min (900 s), σ_position = V_ship × t_stale = 13.9 km. With 30 min stale: 27.7 km',
      unit: 'km',
      description: 'Position uncertainty grows linearly with time since last fix. A carrier at flank speed can move ~14 km in 15 minutes, making stale targeting data useless for precision strike.'
    },
    {
      name: 'Required Update Rate',
      value: 'For CEP < 1 km, need t_update < V_ship / σ_required = 15.4 / 1000 ≈ 65 s. Must refresh track every ~1 minute',
      unit: 's',
      description: 'To achieve weapons-quality targeting (CEP < 1 km) against a maneuvering carrier, the kill chain must deliver targeting updates approximately every 65 seconds.'
    },
    {
      name: 'OTH Radar Accuracy',
      value: 'OTH-B CEP ~10-30 km. NOT weapons-quality. Must be refined by satellite SAR',
      unit: 'km',
      description: 'Over-the-horizon radar provides detection and rough cueing but lacks the precision for direct weapons targeting. SAR satellite refinement is mandatory.'
    },
    {
      name: 'Satellite Revisit Gap',
      value: 'Yaogan constellation revisit ~4-8 hours. During gap, must rely on OTH + HUMINT. Critical vulnerability',
      unit: 'hours',
      description: 'The Yaogan satellite constellation cannot provide continuous coverage. Gaps of 4-8 hours between passes create windows where the kill chain relies on degraded OTH and HUMINT sources.'
    }
  ]);

  monteCarloScenarios = signal<MonteCarloScenario[]>([
    {
      scenario: 'Single DF-21D, no BMD',
      pk: 0.45,
      pk_std: 0.06,
      trials: 10000,
      description: 'Single missile engagement against carrier with no ballistic missile defense active. Assumes functional kill chain with 15-minute-old targeting data.'
    },
    {
      scenario: 'Salvo (4x DF-21D), with Aegis BMD',
      pk: 0.65,
      pk_std: 0.05,
      trials: 10000,
      description: 'Four-missile salvo against carrier defended by Aegis BMD (SM-3 + SM-6). Salvo designed to saturate BMD capacity.'
    },
    {
      scenario: 'DF-17 HGV, vs SM-6',
      pk: 0.70,
      pk_std: 0.04,
      trials: 10000,
      description: 'Single DF-17 hypersonic glide vehicle engagement. SM-6 has limited intercept window due to HGV depressed trajectory and maneuverability.'
    },
    {
      scenario: 'Mixed salvo (2x DF-21D + 2x DF-17), full BMD',
      pk: 0.55,
      pk_std: 0.05,
      trials: 10000,
      description: 'Mixed salvo combining ballistic and HGV threats to complicate BMD engagement. Full Aegis BMD suite active including SM-3 and SM-6.'
    }
  ]);

  usCountermeasures = signal<Countermeasure[]>([
    {
      name: 'SM-3 Block IIA',
      system: 'Aegis BMD',
      description: 'Midcourse intercept of ballistic trajectory. Exoatmospheric kinetic kill vehicle with 2500+ km range.',
      effectiveness: 'Moderate vs DF-21D/DF-26 ballistic phase; ineffective vs DF-17 HGV'
    },
    {
      name: 'SM-6 Dual I/II',
      system: 'Aegis',
      description: 'Terminal intercept, dual seeker (active radar + semi-active). Capable of engaging targets at extended range in BMD mode.',
      effectiveness: 'Limited vs HGV due to speed/maneuver; moderate vs ballistic reentry'
    },
    {
      name: 'EMCON & Emissions Deception',
      system: 'Fleet-wide',
      description: 'Minimize RF emissions across the strike group, use decoy emitters to create false electronic signatures.',
      effectiveness: 'High — degrades OTH-B and ELINT detection'
    },
    {
      name: 'Nulka/SRBOC Decoys',
      system: 'Ship self-defense',
      description: 'Offboard active decoys (Nulka) and chaff/flare dispensing (SRBOC) to seduce or confuse incoming missile seekers.',
      effectiveness: 'Moderate — confuse terminal radar seeker'
    },
    {
      name: 'Maneuver Doctrine (Sprint-and-Drift)',
      system: 'Carrier operations',
      description: 'Carrier changes course and speed unpredictably during estimated missile time-of-flight to maximize position uncertainty.',
      effectiveness: 'High — exploits stale targeting data, increases miss distance'
    },
    {
      name: 'Kill Chain Disruption (ASAT/Cyber/SEAD)',
      system: 'Offensive/joint operations',
      description: 'Degrade ISR constellation via ASAT, conduct cyber attacks on C2 networks, SEAD missions against OTH-B radar sites.',
      effectiveness: 'Very High if executed — removes sensor inputs from kill chain'
    }
  ]);

  // ─── Platform-Specific Comprehensive Data ───────────────────────────────────

  missilePlatforms = signal<MissilePlatformData[]>([
    // DF-21D
    {
      id: 'df21d',
      name: 'DF-21D',
      designation: 'CSS-5 Mod 4',
      description: 'First-generation anti-ship ballistic missile. Medium-range system designed for theater-level carrier interdiction within the first island chain.',
      specs: {
        name: 'DF-21D',
        designation: 'CSS-5 Mod 4',
        range_km: 1500,
        warhead: 'Conventional / Nuclear',
        cep_m: '20-40',
        guidance: 'INS / Radar seeker terminal',
        speed: 'Mach 10 reentry',
        launch_platform: 'TEL (road-mobile)',
        classification: 'ESTIMATED'
      },
      killChain: [
        { phase: 'Wide-Area Surveillance', time_min: 'T+0', system: 'OTH-B + Yaogan', description: 'Initial detection via OTH-B radar and Yaogan satellites', sensors: ['OTH-B', 'Yaogan SAR'], vulnerabilities: ['OTH-B jamming', 'ASAT'] },
        { phase: 'Detection & Cueing', time_min: 'T+5', system: 'Data Fusion Center', description: 'Track file initiated from multi-source inputs', sensors: ['ELINT', 'Maritime militia'], vulnerabilities: ['EMCON discipline'] },
        { phase: 'Target Discrimination', time_min: 'T+12', system: 'SAR Analysis', description: 'Carrier identified from SAR imagery', sensors: ['Yaogan SAR triplets'], vulnerabilities: ['Decoys', 'Revisit gaps'] },
        { phase: 'Track Refinement', time_min: 'T+18', system: 'Multi-Source Fusion', description: 'Position refined to weapons-quality accuracy', sensors: ['BeiDou', 'Submarine SIGINT'], vulnerabilities: ['Stale data', 'Carrier maneuver'] },
        { phase: 'Launch Authorization', time_min: 'T+20', system: 'C2 Chain', description: 'Command authorization and targeting upload', sensors: ['C2 network'], vulnerabilities: ['Decapitation', 'Cyber attack'] },
        { phase: 'Boost Phase', time_min: 'T+22', system: 'Solid rocket motor', description: 'Ballistic launch from TEL', sensors: ['INS'], vulnerabilities: ['Boost-phase intercept (theoretical)'] },
        { phase: 'Midcourse', time_min: 'T+27', system: 'INS + Stellar', description: 'Ballistic trajectory with stellar updates', sensors: ['Stellar nav', 'BeiDou'], vulnerabilities: ['SM-3 midcourse intercept'] },
        { phase: 'Terminal', time_min: 'T+30', system: 'Radar seeker', description: 'Terminal homing on carrier radar signature', sensors: ['Onboard radar'], vulnerabilities: ['SM-6', 'Nulka decoys'] }
      ],
      monteCarloResults: [
        { scenario: 'DF-21D Single, No BMD', pk: 0.45, pk_std: 0.06, trials: 10000, description: 'Single missile, undefended target, 15-min old data' },
        { scenario: 'DF-21D Single, Aegis BMD', pk: 0.25, pk_std: 0.05, trials: 10000, description: 'Single missile against SM-3/SM-6 defense' },
        { scenario: 'DF-21D Salvo (4x), Aegis BMD', pk: 0.65, pk_std: 0.05, trials: 10000, description: 'Four-missile salvo to saturate BMD' }
      ],
      engagementGeometries: [
        {
          name: 'First Island Chain Interdiction',
          description: 'DF-21D engagement against CSG operating within 1500 km of Chinese coast',
          parameters: [
            { name: 'Launch Range', value: 1200, unit: 'km' },
            { name: 'Missile TOF', value: 12, unit: 'min' },
            { name: 'CSG Speed', value: 30, unit: 'kts' },
            { name: 'Target Maneuver', value: 9.3, unit: 'km displacement' }
          ],
          calculation: 'At 30 kts, CSG moves 15.4 m/s × 720 s = 11.1 km during TOF. With 20-40m CEP and seeker acquisition at 50 km, terminal correction can compensate for ~10 km position uncertainty.',
          result: [
            { metric: 'Engagement Window', value: '< 1500', unit: 'km' },
            { metric: 'Target Displacement', value: 11.1, unit: 'km' },
            { metric: 'Seeker Acquisition Range', value: 50, unit: 'km' },
            { metric: 'Pk (undefended)', value: '0.45', unit: '' }
          ]
        }
      ],
      trajectoryProfile: [
        { altitude_km: 0, range_km: 0, phase: 'Launch' },
        { altitude_km: 150, range_km: 200, phase: 'Boost' },
        { altitude_km: 400, range_km: 500, phase: 'Apogee' },
        { altitude_km: 300, range_km: 800, phase: 'Midcourse' },
        { altitude_km: 100, range_km: 1200, phase: 'Reentry' },
        { altitude_km: 30, range_km: 1400, phase: 'Terminal' },
        { altitude_km: 0, range_km: 1500, phase: 'Impact' }
      ],
      subsystems: DF21D_SUBSYSTEMS
    },
    // DF-26
    {
      id: 'df26',
      name: 'DF-26',
      designation: 'CSS-18',
      description: 'Intermediate-range dual-capable ASBM with extended reach to Second Island Chain. Can strike Guam and moving naval targets at 4000 km.',
      specs: {
        name: 'DF-26',
        designation: 'CSS-18',
        range_km: 4000,
        warhead: 'Conventional / Nuclear',
        cep_m: '30-50',
        guidance: 'INS / Stellar-aided / Radar seeker',
        speed: 'Mach 18 reentry',
        launch_platform: 'TEL (road-mobile)',
        classification: 'ESTIMATED'
      },
      killChain: [
        { phase: 'Strategic ISR', time_min: 'T+0', system: 'Deep-space tracking + Yaogan', description: 'Long-range surveillance for Second Island Chain targets', sensors: ['Yaogan global', 'OTH-B extended'], vulnerabilities: ['ASAT', 'Satellite revisit gaps'] },
        { phase: 'Target Detection', time_min: 'T+8', system: 'Space-based ISR', description: 'Initial detection at extended range', sensors: ['Yaogan constellation', 'Gaofen satellites'], vulnerabilities: ['Constellation gaps', 'EMCON'] },
        { phase: 'Track Development', time_min: 'T+15', system: 'Multi-source fusion', description: 'Track file from satellite and SIGINT', sensors: ['ELINT satellites', 'Maritime SIGINT'], vulnerabilities: ['Track file staleness'] },
        { phase: 'Targeting Update', time_min: 'T+22', system: 'Near real-time update', description: 'Final targeting update before launch', sensors: ['BeiDou', 'Relay satellite'], vulnerabilities: ['Data latency', 'Jamming'] },
        { phase: 'Launch', time_min: 'T+25', system: 'Two-stage solid motor', description: 'Launch from deep inland TEL', sensors: ['INS'], vulnerabilities: ['Pre-launch detection'] },
        { phase: 'Boost Phase', time_min: 'T+27', system: 'Solid propulsion', description: 'High-energy boost to IRBM trajectory', sensors: ['INS'], vulnerabilities: ['Boost-phase intercept (very limited)'] },
        { phase: 'Midcourse', time_min: 'T+35', system: 'INS + Stellar + Datalink', description: 'Extended midcourse with stellar updates and possible relay datalink', sensors: ['Stellar nav', 'Relay satellite'], vulnerabilities: ['SM-3 IIA at extended range'] },
        { phase: 'Terminal', time_min: 'T+45', system: 'Maneuvering RV + seeker', description: 'Mach 18 reentry with terminal maneuver and radar homing', sensors: ['Onboard radar seeker'], vulnerabilities: ['THAAD (land)', 'SM-6 (limited)'] }
      ],
      monteCarloResults: [
        { scenario: 'DF-26 Single, vs Guam', pk: 0.55, pk_std: 0.06, trials: 10000, description: 'Single missile against fixed Guam target (no BMD)' },
        { scenario: 'DF-26 Single, vs CSG', pk: 0.35, pk_std: 0.07, trials: 10000, description: 'Single missile against maneuvering carrier at 4000 km' },
        { scenario: 'DF-26 Salvo (6x), vs CSG + BMD', pk: 0.60, pk_std: 0.06, trials: 10000, description: 'Six-missile salvo against defended CSG' }
      ],
      engagementGeometries: [
        {
          name: 'Second Island Chain Strike',
          description: 'DF-26 engagement against CSG near Guam at ~3500 km range',
          parameters: [
            { name: 'Launch Range', value: 3500, unit: 'km' },
            { name: 'Missile TOF', value: 25, unit: 'min' },
            { name: 'CSG Speed', value: 30, unit: 'kts' },
            { name: 'Target Maneuver', value: 23.1, unit: 'km displacement' }
          ],
          calculation: 'At 25-minute TOF, CSG can displace 23.1 km. DF-26 CEP of 30-50m requires seeker acquisition and terminal correction. Longer flight time creates greater targeting uncertainty.',
          result: [
            { metric: 'Engagement Range', value: 3500, unit: 'km' },
            { metric: 'Target Displacement', value: 23.1, unit: 'km' },
            { metric: 'Required Seeker FoV', value: '>30', unit: 'km radius' },
            { metric: 'Pk (with BMD)', value: '0.35', unit: '' }
          ]
        },
        {
          name: 'Guam Base Strike',
          description: 'DF-26 strike against fixed military installations on Guam',
          parameters: [
            { name: 'Range to Guam', value: 2800, unit: 'km' },
            { name: 'Missile TOF', value: 20, unit: 'min' },
            { name: 'Target Type', value: 'Fixed', unit: '' },
            { name: 'THAAD Defense', value: 1, unit: 'battery' }
          ],
          calculation: 'Fixed target eliminates position uncertainty. THAAD terminal intercept window limited against Mach 18 reentry. Multiple missiles required to saturate single THAAD battery.',
          result: [
            { metric: 'Target Uncertainty', value: 0, unit: 'km' },
            { metric: 'THAAD Pk (per missile)', value: '0.7-0.9', unit: '' },
            { metric: 'Salvo Size for 90% Pk', value: 4, unit: 'missiles' },
            { metric: 'Effective Pk (4x salvo)', value: '0.85', unit: '' }
          ]
        }
      ],
      trajectoryProfile: [
        { altitude_km: 0, range_km: 0, phase: 'Launch' },
        { altitude_km: 200, range_km: 300, phase: 'Boost' },
        { altitude_km: 800, range_km: 1000, phase: 'Apogee' },
        { altitude_km: 600, range_km: 2000, phase: 'Midcourse' },
        { altitude_km: 300, range_km: 3000, phase: 'Reentry' },
        { altitude_km: 80, range_km: 3800, phase: 'Terminal' },
        { altitude_km: 0, range_km: 4000, phase: 'Impact' }
      ],
      subsystems: DF26_SUBSYSTEMS
    },
    // DF-17 HGV
    {
      id: 'df17',
      name: 'DF-17',
      designation: 'CSS-22',
      description: 'Hypersonic glide vehicle weapon system. Boost-glide trajectory defeats traditional BMD by flying too low for exoatmospheric interceptors and too fast/maneuverable for endoatmospheric systems.',
      specs: {
        name: 'DF-17',
        designation: 'CSS-22',
        range_km: '1800-2500',
        warhead: 'Conventional (HGV)',
        cep_m: '10-20',
        guidance: 'INS / Radar seeker + Glide control',
        speed: 'Mach 10+ glide',
        launch_platform: 'TEL (road-mobile)',
        classification: 'ESTIMATED'
      },
      killChain: [
        { phase: 'Wide-Area Surveillance', time_min: 'T+0', system: 'OTH-B + Space ISR', description: 'Initial detection and gross positioning', sensors: ['OTH-B', 'Yaogan SAR', 'Jilin-1'], vulnerabilities: ['ASAT', 'OTH-B jamming'] },
        { phase: 'Detection & Cueing', time_min: 'T+5', system: 'Data Fusion Center', description: 'Track file initiation with multi-source correlation', sensors: ['ELINT', 'Maritime militia', 'Submarine SIGINT'], vulnerabilities: ['EMCON', 'Deception'] },
        { phase: 'Target Discrimination', time_min: 'T+10', system: 'High-res SAR', description: 'Carrier identification and characterization', sensors: ['Yaogan SAR triplets'], vulnerabilities: ['Decoys', 'Satellite revisit'] },
        { phase: 'Track Refinement', time_min: 'T+15', system: 'Real-time fusion', description: 'Weapons-quality track with prediction', sensors: ['BeiDou', 'WZ-7 UAV'], vulnerabilities: ['Track latency', 'UAV attrition'] },
        { phase: 'Launch Authorization', time_min: 'T+18', system: 'PLARF C2', description: 'Command authorization and HGV targeting upload', sensors: ['C2 network'], vulnerabilities: ['Decapitation', 'Cyber'] },
        { phase: 'Boost Phase', time_min: 'T+20', system: 'Solid booster', description: 'Boost to HGV release altitude (~60 km)', sensors: ['INS'], vulnerabilities: ['Boost detection', 'Very limited intercept window'] },
        { phase: 'HGV Separation', time_min: 'T+22', system: 'HGV release', description: 'Glide vehicle separates, begins depressed glide trajectory', sensors: ['INS', 'Stellar'], vulnerabilities: ['SM-3 cannot engage (too low)'] },
        { phase: 'Glide Phase', time_min: 'T+24', system: 'Aerodynamic control', description: 'Sustained Mach 10+ glide at 40-60 km altitude with maneuver capability', sensors: ['INS', 'BeiDou datalink'], vulnerabilities: ['Datalink jamming'] },
        { phase: 'Terminal', time_min: 'T+28', system: 'Seeker + Pull-up dive', description: 'Radar seeker acquisition, terminal pull-up and dive', sensors: ['Onboard radar seeker'], vulnerabilities: ['SM-6 (very limited)', 'CIWS last-ditch'] }
      ],
      monteCarloResults: [
        { scenario: 'DF-17 HGV Single, No BMD', pk: 0.70, pk_std: 0.04, trials: 10000, description: 'Single HGV against undefended carrier' },
        { scenario: 'DF-17 HGV Single, vs Aegis', pk: 0.55, pk_std: 0.05, trials: 10000, description: 'Single HGV against full Aegis BMD suite' },
        { scenario: 'DF-17 + DF-21D Mixed Salvo', pk: 0.75, pk_std: 0.04, trials: 10000, description: 'Combined HGV + ballistic to complicate BMD' },
        { scenario: 'DF-17 Swarm (4x HGV)', pk: 0.90, pk_std: 0.03, trials: 10000, description: 'Four HGVs from different azimuths' }
      ],
      engagementGeometries: [
        {
          name: 'Depressed Trajectory Attack',
          description: 'DF-17 HGV exploits gap between SM-3 (exo) and SM-6 (endo) engagement envelopes',
          parameters: [
            { name: 'Glide Altitude', value: '40-60', unit: 'km' },
            { name: 'Glide Speed', value: 'Mach 10+', unit: '' },
            { name: 'Cross-Range Maneuver', value: '±400', unit: 'km' },
            { name: 'Terminal Dive Angle', value: '30-60', unit: 'degrees' }
          ],
          calculation: 'SM-3 designed for exoatmospheric intercept above 100 km. HGV cruises at 40-60 km. SM-6 endoatmospheric range ~50 km altitude max. HGV flies in "seam" between interceptor envelopes while maintaining 5-10g maneuver capability that exceeds SM-6 divert.',
          result: [
            { metric: 'SM-3 Engagement', value: 'Not Possible', unit: '(too low)' },
            { metric: 'SM-6 Engagement Window', value: '< 30', unit: 'seconds' },
            { metric: 'SM-6 Pk vs HGV', value: '< 0.2', unit: '' },
            { metric: 'HGV Maneuver Advantage', value: '3-5x', unit: 'vs interceptor' }
          ]
        },
        {
          name: 'Multi-Axis Saturation Attack',
          description: 'Multiple DF-17s launched from dispersed TELs attack from different azimuths',
          parameters: [
            { name: 'Number of HGVs', value: 4, unit: '' },
            { name: 'Azimuth Spread', value: 120, unit: 'degrees' },
            { name: 'Time-on-Target', value: '±30', unit: 'seconds' },
            { name: 'Aegis Coverage', value: 180, unit: 'degrees per ship' }
          ],
          calculation: 'CSG with 2 Aegis cruisers can engage in ~180° sectors each. 4 HGVs from 120° spread force Aegis to split engagement capacity. Each HGV has independent seeker — no single point of failure after launch.',
          result: [
            { metric: 'Aegis Engagement Capacity', value: 2, unit: 'simultaneous per sector' },
            { metric: 'Leakers (expected)', value: 2, unit: 'HGVs' },
            { metric: 'Combined Salvo Pk', value: '0.90+', unit: '' },
            { metric: 'CSG Survival Probability', value: '< 10%', unit: '' }
          ]
        }
      ],
      trajectoryProfile: [
        { altitude_km: 0, range_km: 0, phase: 'Launch' },
        { altitude_km: 60, range_km: 150, phase: 'Boost' },
        { altitude_km: 60, range_km: 300, phase: 'HGV Separation' },
        { altitude_km: 55, range_km: 800, phase: 'Glide Cruise' },
        { altitude_km: 50, range_km: 1500, phase: 'Glide Maneuver' },
        { altitude_km: 40, range_km: 2000, phase: 'Terminal Approach' },
        { altitude_km: 25, range_km: 2300, phase: 'Pull-up' },
        { altitude_km: 0, range_km: 2500, phase: 'Impact' }
      ],
      subsystems: DF17_SUBSYSTEMS
    }
  ]);

  // ─── Subsystem Deep-Dive State ──────────────────────────────────────────────

  isrSubsystems = signal<SubsystemDetail[]>(ISR_C2_SUBSYSTEMS);
  selectedSubsystemCategory = signal<'missile' | 'isr'>('missile');
  selectedSubsystemId = signal<string | null>(null);
  expandedComponentId = signal<string | null>(null);

  // Technical Derivations
  technicalDerivations = signal<TechnicalDerivation[]>([
    {
      id: 'trajectory',
      title: 'Trajectory & Flight Mechanics',
      category: 'trajectory',
      equations: [
        {
          name: 'Ballistic Range Equation',
          latex: 'R = (V₀² × sin(2θ)) / g × (1 + h/R_e)',
          description: 'Maximum range of ballistic missile as function of launch velocity and angle, with Earth curvature correction',
          variables: [
            { symbol: 'R', meaning: 'Range', unit: 'm' },
            { symbol: 'V₀', meaning: 'Launch velocity', unit: 'm/s' },
            { symbol: 'θ', meaning: 'Launch angle', unit: 'rad' },
            { symbol: 'g', meaning: 'Gravitational acceleration', unit: 'm/s²' },
            { symbol: 'R_e', meaning: 'Earth radius', unit: 'm' }
          ],
          derivation: [
            'For DF-21D: V₀ ≈ 4,000 m/s (Mach 12 at burnout)',
            'Optimal angle θ ≈ 45° for max range',
            'R = (4000² × sin(90°)) / 9.81 = 1,631 km (vacuum)',
            'With drag and Earth curvature: R ≈ 1,500 km'
          ],
          numericalExample: {
            inputs: { 'V₀': 4000, 'θ': 45, 'g': 9.81 },
            calculation: 'R = (4000² × 1) / 9.81 = 1,631,397 m',
            result: '~1,500 km (with atmospheric drag)'
          }
        },
        {
          name: 'HGV Glide Range',
          latex: 'R_glide = (V² × L/D) / g',
          description: 'Glide range for hypersonic glide vehicle based on energy-height relationship',
          variables: [
            { symbol: 'R_glide', meaning: 'Glide range', unit: 'm' },
            { symbol: 'V', meaning: 'Velocity', unit: 'm/s' },
            { symbol: 'L/D', meaning: 'Lift-to-drag ratio', unit: 'dimensionless' },
            { symbol: 'g', meaning: 'Gravitational acceleration', unit: 'm/s²' }
          ],
          derivation: [
            'For DF-17 HGV: V ≈ 3,400 m/s (Mach 10), L/D ≈ 4',
            'R_glide = (3400² × 4) / 9.81 = 4,713 km (theoretical)',
            'Actual range reduced by maneuvering and thermal limits',
            'Practical range: 1,800-2,500 km'
          ],
          numericalExample: {
            inputs: { 'V': 3400, 'L/D': 4, 'g': 9.81 },
            calculation: 'R = (3400² × 4) / 9.81 = 4,713,149 m',
            result: '~2,500 km (practical with maneuver margin)'
          }
        },
        {
          name: 'Reentry Velocity',
          latex: 'V_reentry = √(V_apogee² + 2gh)',
          description: 'Terminal velocity at sea level based on apogee velocity and altitude',
          variables: [
            { symbol: 'V_reentry', meaning: 'Reentry velocity', unit: 'm/s' },
            { symbol: 'V_apogee', meaning: 'Velocity at apogee', unit: 'm/s' },
            { symbol: 'g', meaning: 'Gravitational acceleration', unit: 'm/s²' },
            { symbol: 'h', meaning: 'Apogee altitude', unit: 'm' }
          ],
          derivation: [
            'For DF-26: Apogee ~800 km, V_apogee ≈ 3,000 m/s',
            'V_reentry = √(3000² + 2 × 9.81 × 800,000)',
            'V_reentry = √(9,000,000 + 15,696,000) = √24,696,000',
            'V_reentry ≈ 4,970 m/s ≈ Mach 15 (at altitude)'
          ]
        }
      ]
    },
    {
      id: 'guidance',
      title: 'Guidance & Navigation',
      category: 'guidance',
      equations: [
        {
          name: 'INS Drift Error',
          latex: 'σ_INS = σ_gyro × t + σ_accel × t²/2',
          description: 'Inertial navigation system position error growth over time',
          variables: [
            { symbol: 'σ_INS', meaning: 'Position error', unit: 'm' },
            { symbol: 'σ_gyro', meaning: 'Gyroscope drift rate', unit: 'rad/hr' },
            { symbol: 'σ_accel', meaning: 'Accelerometer bias', unit: 'm/s²' },
            { symbol: 't', meaning: 'Time', unit: 's' }
          ],
          derivation: [
            'Modern ring laser gyro: σ_gyro ≈ 0.001 °/hr',
            'Navigation-grade accelerometer: σ_accel ≈ 10 μg',
            'After 10 minutes: σ_INS ≈ 50-100 m drift',
            'Stellar nav correction reduces error to < 20 m'
          ]
        },
        {
          name: 'Proportional Navigation Guidance',
          latex: 'a_c = N × V_c × λ_dot',
          description: 'Terminal guidance law for seeker-based homing',
          variables: [
            { symbol: 'a_c', meaning: 'Commanded acceleration', unit: 'm/s²' },
            { symbol: 'N', meaning: 'Navigation constant', unit: 'dimensionless' },
            { symbol: 'V_c', meaning: 'Closing velocity', unit: 'm/s' },
            { symbol: 'λ_dot', meaning: 'Line-of-sight rate', unit: 'rad/s' }
          ],
          derivation: [
            'Typical N = 3-5 for effective guidance',
            'For DF-21D terminal: V_c ≈ 3,400 m/s',
            'With λ_dot = 0.01 rad/s and N = 4:',
            'a_c = 4 × 3400 × 0.01 = 136 m/s² ≈ 14g'
          ]
        },
        {
          name: 'Miss Distance (Zero-Effort-Miss)',
          latex: 'ZEM = R × λ_dot × t_go',
          description: 'Predicted miss distance if no further guidance commands',
          variables: [
            { symbol: 'ZEM', meaning: 'Zero-effort miss', unit: 'm' },
            { symbol: 'R', meaning: 'Range to target', unit: 'm' },
            { symbol: 'λ_dot', meaning: 'LOS rate', unit: 'rad/s' },
            { symbol: 't_go', meaning: 'Time to go', unit: 's' }
          ]
        }
      ]
    },
    {
      id: 'terminal',
      title: 'Terminal Phase & Seeker',
      category: 'terminal',
      equations: [
        {
          name: 'Radar Seeker Range',
          latex: 'R_seeker = (P_t × G² × σ × λ² / ((4π)³ × k × T × B × SNR))^(1/4)',
          description: 'Maximum seeker acquisition range against target RCS',
          variables: [
            { symbol: 'R_seeker', meaning: 'Seeker acquisition range', unit: 'm' },
            { symbol: 'P_t', meaning: 'Transmit power', unit: 'W' },
            { symbol: 'G', meaning: 'Antenna gain', unit: 'dimensionless' },
            { symbol: 'σ', meaning: 'Target RCS', unit: 'm²' },
            { symbol: 'SNR', meaning: 'Required signal-to-noise', unit: 'dimensionless' }
          ],
          derivation: [
            'Carrier RCS ≈ 50,000 m² (large target)',
            'Seeker power ≈ 100 W, gain ≈ 30 dB',
            'R_seeker ≈ 50-70 km against carrier',
            'Sufficient for terminal correction of ~20 km position error'
          ],
          numericalExample: {
            inputs: { 'P_t': 100, 'G_dBi': 30, 'σ': 50000, 'SNR_dB': 15 },
            calculation: 'R = (100 × 1000² × 50000 × 0.03² / (4π)³ × kTB × 31.6)^0.25',
            result: '~60 km acquisition range'
          }
        },
        {
          name: 'Terminal Maneuver Authority',
          latex: 'Δ_position = a × t² / 2',
          description: 'Position correction capability in terminal phase',
          variables: [
            { symbol: 'Δ_position', meaning: 'Position change', unit: 'm' },
            { symbol: 'a', meaning: 'Lateral acceleration', unit: 'm/s²' },
            { symbol: 't', meaning: 'Time available', unit: 's' }
          ],
          derivation: [
            'HGV with 10g lateral capability: a = 100 m/s²',
            'Terminal phase duration: t ≈ 15 s',
            'Δ_position = 100 × 15² / 2 = 11,250 m',
            'Can correct for ~11 km target displacement'
          ]
        },
        {
          name: 'Impact CEP',
          latex: 'CEP = √(σ_guidance² + σ_seeker² + σ_fuze²)',
          description: 'Circular error probable from combined error sources',
          variables: [
            { symbol: 'CEP', meaning: 'Circular error probable', unit: 'm' },
            { symbol: 'σ_guidance', meaning: 'Guidance error', unit: 'm' },
            { symbol: 'σ_seeker', meaning: 'Seeker tracking error', unit: 'm' },
            { symbol: 'σ_fuze', meaning: 'Fuze timing error', unit: 'm' }
          ]
        }
      ]
    },
    {
      id: 'engagement',
      title: 'Engagement Probability',
      category: 'engagement',
      equations: [
        {
          name: 'Single-Shot Kill Probability',
          latex: 'Pk = P_launch × P_flight × P_guidance × P_terminal × P_warhead',
          description: 'Kill chain probability decomposition for ASBM',
          variables: [
            { symbol: 'P_launch', meaning: 'Successful launch probability', unit: '' },
            { symbol: 'P_flight', meaning: 'Flight reliability', unit: '' },
            { symbol: 'P_guidance', meaning: 'Guidance accuracy', unit: '' },
            { symbol: 'P_terminal', meaning: 'Terminal acquisition', unit: '' },
            { symbol: 'P_warhead', meaning: 'Warhead effectiveness', unit: '' }
          ],
          derivation: [
            'P_launch = 0.95 (TEL reliability)',
            'P_flight = 0.90 (structural/propulsion)',
            'P_guidance = 0.85 (mid-course accuracy)',
            'P_terminal = 0.70 (seeker acquisition vs decoys)',
            'P_warhead = 0.90 (warhead function)',
            'Pk = 0.95 × 0.90 × 0.85 × 0.70 × 0.90 = 0.46'
          ],
          numericalExample: {
            inputs: { 'P_launch': 0.95, 'P_flight': 0.90, 'P_guidance': 0.85, 'P_terminal': 0.70, 'P_warhead': 0.90 },
            calculation: 'Pk = 0.95 × 0.90 × 0.85 × 0.70 × 0.90',
            result: 'Pk = 0.46 (single shot vs undefended)'
          }
        },
        {
          name: 'Salvo Pk',
          latex: 'Pk_salvo = 1 - (1 - Pk_single)^n',
          description: 'Cumulative kill probability for n-missile salvo',
          variables: [
            { symbol: 'Pk_salvo', meaning: 'Salvo kill probability', unit: '' },
            { symbol: 'Pk_single', meaning: 'Single-shot Pk', unit: '' },
            { symbol: 'n', meaning: 'Number of missiles', unit: '' }
          ],
          derivation: [
            'For 4-missile salvo with Pk_single = 0.45:',
            'Pk_salvo = 1 - (1 - 0.45)^4',
            'Pk_salvo = 1 - (0.55)^4 = 1 - 0.0915',
            'Pk_salvo = 0.91 (without BMD)'
          ]
        },
        {
          name: 'BMD Leakage Rate',
          latex: 'P_leak = (1 - P_intercept)^n_intercept',
          description: 'Probability of missile leaking through BMD layer',
          variables: [
            { symbol: 'P_leak', meaning: 'Leakage probability', unit: '' },
            { symbol: 'P_intercept', meaning: 'Single intercept Pk', unit: '' },
            { symbol: 'n_intercept', meaning: 'Number of intercept attempts', unit: '' }
          ]
        }
      ]
    },
    {
      id: 'propagation',
      title: 'Targeting & Propagation',
      category: 'propagation',
      equations: [
        {
          name: 'Target Position Uncertainty',
          latex: 'σ_position = V_target × t_stale',
          description: 'Position uncertainty growth due to target motion',
          variables: [
            { symbol: 'σ_position', meaning: 'Position uncertainty', unit: 'm' },
            { symbol: 'V_target', meaning: 'Target velocity', unit: 'm/s' },
            { symbol: 't_stale', meaning: 'Data staleness', unit: 's' }
          ],
          derivation: [
            'Carrier at 30 knots = 15.4 m/s',
            'With 15 min stale data: σ = 15.4 × 900 = 13,860 m',
            'With 30 min stale data: σ = 15.4 × 1800 = 27,720 m',
            'Seeker FoV must encompass this uncertainty'
          ],
          numericalExample: {
            inputs: { 'V_target': 15.4, 't_stale_min': 15 },
            calculation: 'σ = 15.4 m/s × 900 s',
            result: 'σ = 13.9 km (must be within seeker acquisition range)'
          }
        },
        {
          name: 'OTH Radar Accuracy',
          latex: 'σ_OTH ≈ c / (2 × B × SNR^0.5)',
          description: 'Over-the-horizon radar range resolution',
          variables: [
            { symbol: 'σ_OTH', meaning: 'OTH range accuracy', unit: 'm' },
            { symbol: 'c', meaning: 'Speed of light', unit: 'm/s' },
            { symbol: 'B', meaning: 'Bandwidth', unit: 'Hz' },
            { symbol: 'SNR', meaning: 'Signal-to-noise ratio', unit: '' }
          ],
          derivation: [
            'OTH-B bandwidth ≈ 100 kHz',
            'Range resolution ≈ c/(2B) = 1.5 km',
            'With ionospheric effects: 10-30 km accuracy',
            'NOT weapons-quality — requires SAR refinement'
          ]
        },
        {
          name: 'SAR Resolution',
          latex: 'δ_azimuth = λ × R / (2 × L_synthetic)',
          description: 'Synthetic aperture radar azimuth resolution',
          variables: [
            { symbol: 'δ_azimuth', meaning: 'Azimuth resolution', unit: 'm' },
            { symbol: 'λ', meaning: 'Wavelength', unit: 'm' },
            { symbol: 'R', meaning: 'Slant range', unit: 'm' },
            { symbol: 'L_synthetic', meaning: 'Synthetic aperture length', unit: 'm' }
          ],
          derivation: [
            'Yaogan SAR: X-band (λ ≈ 0.03 m)',
            'Orbit altitude: 500 km, slant range ~600 km',
            'Spotlight mode: δ ≈ 1-3 m resolution',
            'Sufficient to identify carrier from destroyer'
          ]
        }
      ]
    }
  ]);

  // Signal Processing Chain for Kill Chain
  signalProcessingChain = signal<SignalProcessingBlock[]>([
    {
      name: 'OTH-B Signal Processing',
      function: 'Wide-area maritime detection via ionospheric propagation',
      inputs: ['Backscatter returns (3-30 MHz)', 'Ionospheric state model', 'Sea clutter model'],
      outputs: ['Target detections', 'Bearing estimates (±2°)', 'Range cells (10-30 km)'],
      algorithm: 'Doppler processing + CFAR detection',
      pseudocode: [
        'FOR each range-Doppler cell:',
        '  signal = FFT(backscatter_return)',
        '  clutter = estimate_sea_clutter(range, sea_state)',
        '  threshold = CFAR(clutter, P_fa)',
        '  IF |signal|² > threshold:',
        '    detection = {range, bearing, doppler}',
        '    apply_ionospheric_correction(detection)',
        '    EMIT detection to fusion center'
      ]
    },
    {
      name: 'SAR Image Formation',
      function: 'High-resolution ship detection and classification',
      inputs: ['Raw SAR echo data', 'Platform motion data', 'Ocean surface model'],
      outputs: ['Focused SAR image', 'Ship detections', 'Ship classification'],
      algorithm: 'Range-Doppler algorithm + ML classifier',
      pseudocode: [
        'raw_data = receive_sar_echo()',
        'range_compressed = matched_filter(raw_data, chirp_ref)',
        'azimuth_compressed = FFT_azimuth(range_compressed)',
        'image = motion_compensate(azimuth_compressed)',
        'FOR each detection in CFAR(image):',
        '  features = extract_ship_features(detection)',
        '  class = CNN_classifier(features)  // carrier, destroyer, tanker',
        '  IF class == "CARRIER":',
        '    EMIT high_priority_track(position, confidence)'
      ]
    },
    {
      name: 'Multi-Source Data Fusion',
      function: 'Combine OTH, SAR, ELINT, HUMINT into unified track',
      inputs: ['OTH detections', 'SAR detections', 'ELINT intercepts', 'HUMINT reports'],
      outputs: ['Fused track file', 'Position estimate', 'Velocity estimate', 'Track quality'],
      algorithm: 'Extended Kalman Filter with multiple measurement types',
      pseudocode: [
        'state = [x, y, vx, vy]  // target state vector',
        'P = initial_covariance()',
        'FOR each measurement:',
        '  IF measurement.source == "OTH":',
        '    H = OTH_observation_matrix(state)',
        '    R = OTH_noise_covariance()  // large, 10-30 km',
        '  ELIF measurement.source == "SAR":',
        '    H = SAR_observation_matrix(state)',
        '    R = SAR_noise_covariance()  // small, 10-50 m',
        '  // Kalman update',
        '  K = P × Hᵀ × (H × P × Hᵀ + R)⁻¹',
        '  state = state + K × (measurement - H × state)',
        '  P = (I - K × H) × P',
        '  track_quality = compute_CEP(P)'
      ]
    },
    {
      name: 'Targeting Package Assembly',
      function: 'Generate weapons-quality targeting data for missile',
      inputs: ['Fused track file', 'Track prediction model', 'Missile performance data'],
      outputs: ['Aim point coordinates', 'Target velocity vector', 'Seeker search box'],
      algorithm: 'Track extrapolation + uncertainty propagation',
      pseudocode: [
        'current_track = get_latest_track(target_id)',
        't_flight = estimate_missile_tof(current_track.position)',
        '// Predict target position at impact',
        'predicted_pos = current_track.position + current_track.velocity × t_flight',
        '// Compute uncertainty at impact time',
        'σ_impact = current_track.CEP + current_track.velocity × t_flight × uncertainty_growth',
        '// Generate seeker search box',
        'search_box = 3 × σ_impact  // 99% containment',
        'EMIT targeting_package(predicted_pos, search_box, current_track.velocity)'
      ]
    },
    {
      name: 'Missile Guidance Processor',
      function: 'Onboard guidance from launch to terminal',
      inputs: ['INS measurements', 'Stellar fixes', 'Datalink updates', 'Seeker returns'],
      outputs: ['Guidance commands', 'Estimated position', 'Time-to-go'],
      algorithm: 'Optimal guidance law (proportional navigation)',
      pseudocode: [
        '// Midcourse phase',
        'WHILE altitude > terminal_altitude:',
        '  position = INS_propagate()',
        '  IF stellar_fix_available():',
        '    position = correct_with_stellar(position)',
        '  IF datalink_update_received():',
        '    target_estimate = update_target(datalink)',
        '  guidance_cmd = compute_midcourse(position, target_estimate)',
        '',
        '// Terminal phase',
        'WHILE NOT impact:',
        '  seeker_return = radar_seeker_search()',
        '  IF seeker_return.valid:',
        '    LOS_rate = compute_LOS_rate(seeker_return)',
        '    guidance_cmd = N × closing_velocity × LOS_rate',
        '  execute_guidance(guidance_cmd)'
      ]
    },
    {
      name: 'Terminal Seeker Processing',
      function: 'Acquire and track carrier in terminal phase',
      inputs: ['Radar returns', 'Search box from guidance', 'Target model'],
      outputs: ['Target lock', 'Aim point', 'Tracking quality'],
      algorithm: 'Centroid tracking + size discrimination',
      pseudocode: [
        'search_pattern = generate_spiral(search_box)',
        'FOR each beam_position in search_pattern:',
        '  returns = radar_scan(beam_position)',
        '  detections = CFAR_detect(returns)',
        '  FOR each detection:',
        '    size = estimate_target_size(detection)',
        '    IF size > CARRIER_THRESHOLD:',
        '      aim_point = compute_centroid(detection)',
        '      LOCK_TARGET(aim_point)',
        '      BREAK',
        '',
        '// Track maintenance',
        'WHILE tracking:',
        '  update = radar_track_update()',
        '  aim_point = refine_aim_point(update)',
        '  EMIT guidance_command(aim_point)'
      ]
    }
  ]);

  // Platform comparison data
  readonly platformComparison = computed(() => [
    { id: 'df21d' as MissileId, name: 'DF-21D', range: 1500, speed: 'Mach 10', cep: '20-40 m', trajectory: 'Ballistic', bmdVulnerable: 'Yes (SM-3)', pk: 0.45 },
    { id: 'df26' as MissileId, name: 'DF-26', range: 4000, speed: 'Mach 18', cep: '30-50 m', trajectory: 'Ballistic', bmdVulnerable: 'Partial', pk: 0.55 },
    { id: 'df17' as MissileId, name: 'DF-17 HGV', range: 2500, speed: 'Mach 10+', cep: '10-20 m', trajectory: 'Boost-Glide', bmdVulnerable: 'No', pk: 0.70 }
  ]);

  // Active platform computed signals
  readonly activePlatformData = computed<MissilePlatformData | null>(() => {
    return this.missilePlatforms().find(p => p.id === this.selectedMissile()) || null;
  });

  readonly activeKillChainData = computed(() => {
    const platform = this.activePlatformData();
    return platform ? platform.killChain : this.killChainPhases();
  });

  readonly activeMonteCarloData = computed(() => {
    const platform = this.activePlatformData();
    return platform ? platform.monteCarloResults : this.monteCarloScenarios();
  });

  readonly activeEngagementGeometries = computed(() => {
    const platform = this.activePlatformData();
    return platform ? platform.engagementGeometries : [];
  });

  readonly activeTrajectory = computed(() => {
    const platform = this.activePlatformData();
    return platform ? platform.trajectoryProfile : [];
  });

  // Computed signals for subsystem deep-dive
  readonly availableSubsystems = computed<SubsystemDetail[]>(() => {
    if (this.selectedSubsystemCategory() === 'missile') {
      const platform = this.activePlatformData();
      return platform ? platform.subsystems : [];
    } else {
      return this.isrSubsystems();
    }
  });

  readonly activeSubsystem = computed<SubsystemDetail | null>(() => {
    const id = this.selectedSubsystemId();
    if (!id) return null;
    return this.availableSubsystems().find(s => s.id === id) || null;
  });

  // Subsystem methods
  selectSubsystemCategory(category: 'missile' | 'isr'): void {
    this.selectedSubsystemCategory.set(category);
    this.selectedSubsystemId.set(null);
    this.expandedComponentId.set(null);
  }

  selectSubsystem(id: string): void {
    this.selectedSubsystemId.set(id);
    this.expandedComponentId.set(null);
  }

  toggleComponent(componentName: string): void {
    if (this.expandedComponentId() === componentName) {
      this.expandedComponentId.set(null);
    } else {
      this.expandedComponentId.set(componentName);
    }
  }

  getCategoryLabel(category: SubsystemCategory): string {
    const labels: Record<SubsystemCategory, string> = {
      navigation: 'Navigation',
      seeker: 'Seeker',
      guidance: 'Guidance & Control',
      propulsion: 'Propulsion',
      warhead: 'Warhead & Fuzing',
      datalink: 'Datalink',
      isr: 'ISR Sensor',
      fusion: 'Data Fusion',
      c2: 'Command & Control'
    };
    return labels[category] || category;
  }

  selectPlatform(id: MissileId): void {
    this.selectedMissile.set(id);
    this.activeKillChainPhase.set(0);
    // Reset subsystem selection when changing platform
    if (this.selectedSubsystemCategory() === 'missile') {
      this.selectedSubsystemId.set(null);
      this.expandedComponentId.set(null);
    }
    setTimeout(() => {
      this.drawKillChainTimeline();
      this.drawMonteCarloChart();
      this.drawTrajectoryChart();
      this.drawPlatformComparisonChart();
    }, 50);
  }

  selectPhase(index: number): void {
    this.activeKillChainPhase.set(index);
  }

  selectMissile(id: MissileId): void {
    this.selectedMissile.set(id);
    this.activeKillChainPhase.set(0);
    setTimeout(() => {
      this.drawKillChainTimeline();
      this.drawMonteCarloChart();
      this.drawTrajectoryChart();
    }, 50);
  }

  toggleEquations(): void {
    this.showEquations.update(v => !v);
  }

  getSelectedMissile(): MissileSystem | undefined {
    const platform = this.activePlatformData();
    return platform ? platform.specs : this.missileSystemsData()[2]; // default DF-17
  }

  selectDerivation(id: string): void {
    this.activeDerivationSection.set(id);
  }

  getActiveDerivation(): TechnicalDerivation | undefined {
    return this.technicalDerivations().find(d => d.id === this.activeDerivationSection());
  }

  selectProcessingStep(index: number): void {
    this.activeProcessingStep.set(index);
  }

  getActiveProcessingBlock(): SignalProcessingBlock | undefined {
    return this.signalProcessingChain()[this.activeProcessingStep()];
  }

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.drawKillChainTimeline();
      this.drawSensorNetwork();
      this.drawMonteCarloChart();
      this.drawTrajectoryChart();
      this.drawPlatformComparisonChart();
      this.drawSignalProcessingFlow();
    }, 100);
  }

  drawKillChainTimeline(): void {
    const element = this.killChainTimeline?.nativeElement;
    if (!element) return;

    const width = 900;
    const height = 220;
    const margin = { top: 60, right: 40, bottom: 40, left: 40 };

    d3.select(element).selectAll('*').remove();

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('max-width', '100%');

    const phases = this.activeKillChainData();
    const innerWidth = width - margin.left - margin.right;
    const xScale = d3.scaleLinear()
      .domain([0, phases.length - 1])
      .range([margin.left, margin.left + innerWidth]);

    const yMid = height / 2 + 10;

    // Timeline line
    svg.append('line')
      .attr('x1', margin.left)
      .attr('y1', yMid)
      .attr('x2', margin.left + innerWidth)
      .attr('y2', yMid)
      .attr('stroke', '#c9a227')
      .attr('stroke-width', 2);

    // Phase nodes
    const phaseGroups = svg.selectAll('.phase-group')
      .data(phases)
      .enter()
      .append('g')
      .attr('class', 'phase-group')
      .attr('transform', (d: KillChainPhase, i: number) => `translate(${xScale(i)}, ${yMid})`);

    phaseGroups.append('circle')
      .attr('r', 8)
      .attr('fill', '#c9a227')
      .attr('stroke', '#0a1628')
      .attr('stroke-width', 2);

    // Phase names above
    phaseGroups.append('text')
      .attr('y', -20)
      .attr('text-anchor', 'middle')
      .attr('fill', '#c9a227')
      .attr('font-size', '9px')
      .attr('font-weight', 'bold')
      .text((d: KillChainPhase) => d.phase);

    // Time below
    phaseGroups.append('text')
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('fill', '#8899aa')
      .attr('font-size', '9px')
      .text((d: KillChainPhase) => d.time_min);
  }

  drawSensorNetwork(): void {
    const element = this.sensorNetworkChart?.nativeElement;
    if (!element) return;

    const width = 700;
    const height = 500;

    d3.select(element).selectAll('*').remove();

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('max-width', '100%');

    const sensors = this.sensorArchitecture();

    const nodeColorMap: Record<string, string> = {
      radar: '#e74c3c',
      satellite: '#3498db',
      sigint: '#9b59b6',
      humint: '#27ae60',
      uav: '#e67e22'
    };

    interface SimNode extends d3.SimulationNodeDatum {
      id: string;
      name: string;
      color: string;
      radius: number;
    }

    interface SimLink extends d3.SimulationLinkDatum<SimNode> {
      source: string | SimNode;
      target: string | SimNode;
    }

    const nodes: SimNode[] = [
      { id: 'csg', name: 'Carrier Strike Group', color: '#e74c3c', radius: 20 },
      ...sensors.map(s => ({
        id: s.id,
        name: s.name,
        color: nodeColorMap[s.type] || '#ffffff',
        radius: 14
      }))
    ];

    const links: SimLink[] = sensors.map(s => ({
      source: s.id,
      target: 'csg'
    }));

    const simulation = d3.forceSimulation<SimNode>(nodes)
      .force('link', d3.forceLink<SimNode, SimLink>(links).id((d: SimNode) => d.id).distance(150))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#334455')
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '4,4');

    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', (d: SimNode) => d.radius)
      .attr('fill', (d: SimNode) => d.color)
      .attr('stroke', '#0a1628')
      .attr('stroke-width', 2);

    const labels = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', (d: SimNode) => d.radius + 14)
      .attr('fill', '#c9a227')
      .attr('font-size', '10px')
      .text((d: SimNode) => d.name);

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      labels
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });
  }

  drawMonteCarloChart(): void {
    const element = this.monteCarloChart?.nativeElement;
    if (!element) return;

    const width = 700;
    const height = 350;
    const margin = { top: 30, right: 30, bottom: 100, left: 60 };

    d3.select(element).selectAll('*').remove();

    const svg = d3.select(element)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('max-width', '100%');

    const scenarios = this.activeMonteCarloData();
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const xScale = d3.scaleBand()
      .domain(scenarios.map(s => s.scenario))
      .range([margin.left, margin.left + innerWidth])
      .padding(0.3);

    const yScale = d3.scaleLinear()
      .domain([0, 1])
      .range([margin.top + innerHeight, margin.top]);

    // Y axis
    svg.append('g')
      .attr('transform', `translate(${margin.left}, 0)`)
      .call(d3.axisLeft(yScale).ticks(5).tickFormat(d3.format('.0%')))
      .selectAll('text')
      .attr('fill', '#8899aa');

    svg.selectAll('.domain, .tick line').attr('stroke', '#334455');

    // X axis
    svg.append('g')
      .attr('transform', `translate(0, ${margin.top + innerHeight})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .attr('fill', '#8899aa')
      .attr('font-size', '9px')
      .attr('text-anchor', 'end')
      .attr('transform', 'rotate(-25)');

    // Bars
    svg.selectAll('.bar')
      .data(scenarios)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', (d: MonteCarloScenario) => xScale(d.scenario)!)
      .attr('y', (d: MonteCarloScenario) => yScale(d.pk))
      .attr('width', xScale.bandwidth())
      .attr('height', (d: MonteCarloScenario) => margin.top + innerHeight - yScale(d.pk))
      .attr('fill', '#c9a227')
      .attr('rx', 3);

    // Error bars
    scenarios.forEach(d => {
      const x = xScale(d.scenario)! + xScale.bandwidth() / 2;
      svg.append('line')
        .attr('x1', x)
        .attr('y1', yScale(d.pk - d.pk_std))
        .attr('x2', x)
        .attr('y2', yScale(d.pk + d.pk_std))
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 1.5);
    });

    // Pk labels
    svg.selectAll('.pk-label')
      .data(scenarios)
      .enter()
      .append('text')
      .attr('x', (d: MonteCarloScenario) => xScale(d.scenario)! + xScale.bandwidth() / 2)
      .attr('y', (d: MonteCarloScenario) => yScale(d.pk) - 8)
      .attr('text-anchor', 'middle')
      .attr('fill', '#c9a227')
      .attr('font-size', '11px')
      .attr('font-weight', 'bold')
      .text((d: MonteCarloScenario) => `${(d.pk * 100).toFixed(0)}%`);

    // Y axis label
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -(margin.top + innerHeight / 2))
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('fill', '#8899aa')
      .attr('font-size', '12px')
      .text('P(kill)');

    // Title
    const platform = this.activePlatformData();
    const title = platform ? `${platform.name} Monte Carlo Pk (N=10,000)` : 'ASBM Monte Carlo Pk (N=10,000)';
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 18)
      .attr('text-anchor', 'middle')
      .attr('fill', '#c9a227')
      .attr('font-size', '13px')
      .attr('font-weight', 'bold')
      .text(title);
  }

  private drawTrajectoryChart(): void {
    if (!this.trajectoryChart?.nativeElement) return;
    const container = this.trajectoryChart.nativeElement;
    const width = 700;
    const height = 350;
    const margin = { top: 40, right: 30, bottom: 50, left: 70 };

    d3.select(container).selectAll('*').remove();

    const trajectories = this.missilePlatforms();
    if (trajectories.length === 0) return;

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('max-width', '100%');

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear().domain([0, 4200]).range([0, innerWidth]);
    const y = d3.scaleLinear().domain([0, 900]).range([innerHeight, 0]);

    // Grid
    [200, 400, 600, 800].forEach(v => {
      g.append('line').attr('x1', 0).attr('x2', innerWidth).attr('y1', y(v)).attr('y2', y(v))
        .attr('stroke', '#1a3a5c').attr('stroke-dasharray', '3,3');
    });

    // SM-3 engagement ceiling
    g.append('rect')
      .attr('x', 0).attr('y', y(500)).attr('width', innerWidth).attr('height', y(100) - y(500))
      .attr('fill', 'rgba(52, 152, 219, 0.08)');
    g.append('text').attr('x', innerWidth - 5).attr('y', y(300) + 4)
      .attr('text-anchor', 'end').attr('fill', '#3498db').attr('font-size', '9px').text('SM-3 Engagement Zone');

    // SM-6 engagement ceiling
    g.append('rect')
      .attr('x', 0).attr('y', y(50)).attr('width', innerWidth).attr('height', y(0) - y(50))
      .attr('fill', 'rgba(39, 174, 96, 0.08)');
    g.append('text').attr('x', innerWidth - 5).attr('y', y(25) + 4)
      .attr('text-anchor', 'end').attr('fill', '#27ae60').attr('font-size', '9px').text('SM-6 Zone');

    const colors: Record<string, string> = { df21d: '#e74c3c', df26: '#3498db', df17: '#c9a227' };
    const lineGen = d3.line<{ altitude_km: number; range_km: number }>()
      .x(d => x(d.range_km)).y(d => y(d.altitude_km)).curve(d3.curveCardinal);

    trajectories.forEach(t => {
      const isActive = this.selectedMissile() === t.id;
      g.append('path')
        .datum(t.trajectoryProfile)
        .attr('fill', 'none')
        .attr('stroke', colors[t.id])
        .attr('stroke-width', isActive ? 3 : 1.5)
        .attr('stroke-dasharray', isActive ? '' : '5,5')
        .attr('opacity', isActive ? 1 : 0.5)
        .attr('d', lineGen);

      // Phase labels for active
      if (isActive) {
        t.trajectoryProfile.forEach(p => {
          g.append('circle').attr('cx', x(p.range_km)).attr('cy', y(p.altitude_km)).attr('r', 4)
            .attr('fill', colors[t.id]).attr('stroke', '#0a1628').attr('stroke-width', 1.5);
        });
      }
    });

    // Axes
    g.append('g').attr('transform', `translate(0,${innerHeight})`).call(d3.axisBottom(x).tickValues([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]))
      .selectAll('text').attr('fill', '#95a5a6');
    g.append('g').call(d3.axisLeft(y).tickValues([0, 100, 200, 400, 600, 800]))
      .selectAll('text').attr('fill', '#95a5a6');

    svg.append('text').attr('x', width / 2).attr('y', height - 8).attr('text-anchor', 'middle')
      .attr('fill', '#95a5a6').attr('font-size', '12px').text('Range (km)');
    svg.append('text').attr('transform', 'rotate(-90)').attr('x', -height / 2).attr('y', 15)
      .attr('text-anchor', 'middle').attr('fill', '#95a5a6').attr('font-size', '12px').text('Altitude (km)');
    svg.append('text').attr('x', width / 2).attr('y', 22).attr('text-anchor', 'middle')
      .attr('fill', '#c9a227').attr('font-size', '14px').attr('font-weight', 'bold')
      .text('Missile Trajectory Profiles vs BMD Envelopes');

    // Legend
    const legend = svg.append('g').attr('transform', `translate(${margin.left + 10}, ${margin.top + 10})`);
    Object.entries(colors).forEach(([id, color], i) => {
      const name = id === 'df21d' ? 'DF-21D' : id === 'df26' ? 'DF-26' : 'DF-17 HGV';
      legend.append('line').attr('x1', 0).attr('x2', 20).attr('y1', i * 18).attr('y2', i * 18)
        .attr('stroke', color).attr('stroke-width', 2);
      legend.append('text').attr('x', 25).attr('y', i * 18 + 4).attr('fill', '#95a5a6').attr('font-size', '10px').text(name);
    });
  }

  private drawPlatformComparisonChart(): void {
    if (!this.platformComparisonChart?.nativeElement) return;
    const container = this.platformComparisonChart.nativeElement;
    const width = 700;
    const height = 300;
    const margin = { top: 40, right: 120, bottom: 60, left: 60 };

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg').attr('width', width).attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`).style('max-width', '100%');

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const data = this.platformComparison();
    const x = d3.scaleBand().domain(data.map(d => d.name)).range([0, innerWidth]).padding(0.3);
    const y = d3.scaleLinear().domain([0, 4500]).range([innerHeight, 0]);
    const colors = ['#e74c3c', '#3498db', '#c9a227'];

    // Grid
    [1000, 2000, 3000, 4000].forEach(v => {
      g.append('line').attr('x1', 0).attr('x2', innerWidth).attr('y1', y(v)).attr('y2', y(v))
        .attr('stroke', '#1a3a5c').attr('stroke-dasharray', '3,3');
    });

    // Bars
    g.selectAll('.bar').data(data).join('rect')
      .attr('x', d => x(d.name) || 0).attr('y', d => y(d.range))
      .attr('width', x.bandwidth()).attr('height', d => innerHeight - y(d.range))
      .attr('fill', (_, i) => colors[i]).attr('rx', 4)
      .attr('opacity', d => this.selectedMissile() === d.id ? 1 : 0.6);

    // Labels
    g.selectAll('.val-label').data(data).join('text')
      .attr('x', d => (x(d.name) || 0) + x.bandwidth() / 2)
      .attr('y', d => y(d.range) - 8).attr('text-anchor', 'middle')
      .attr('fill', '#fff').attr('font-size', '11px').attr('font-weight', 'bold')
      .text(d => `${d.range} km`);

    // Pk annotation
    g.selectAll('.pk-label').data(data).join('text')
      .attr('x', d => (x(d.name) || 0) + x.bandwidth() / 2)
      .attr('y', d => y(d.range) + 20).attr('text-anchor', 'middle')
      .attr('fill', '#fff').attr('font-size', '10px')
      .text(d => `Pk: ${(d.pk * 100).toFixed(0)}%`);

    g.append('g').attr('transform', `translate(0,${innerHeight})`).call(d3.axisBottom(x))
      .selectAll('text').attr('fill', '#95a5a6').attr('font-size', '11px');
    g.append('g').call(d3.axisLeft(y).tickValues([0, 1000, 2000, 3000, 4000]))
      .selectAll('text').attr('fill', '#95a5a6');

    svg.append('text').attr('transform', 'rotate(-90)').attr('x', -height / 2).attr('y', 15)
      .attr('text-anchor', 'middle').attr('fill', '#95a5a6').attr('font-size', '12px').text('Max Range (km)');
    svg.append('text').attr('x', width / 2).attr('y', 22).attr('text-anchor', 'middle')
      .attr('fill', '#c9a227').attr('font-size', '14px').attr('font-weight', 'bold')
      .text('ASBM Platform Range & Pk Comparison');

    // Info column
    const info = svg.append('g').attr('transform', `translate(${width - margin.right + 10}, ${margin.top})`);
    data.forEach((d, i) => {
      info.append('text').attr('x', 0).attr('y', i * 40).attr('fill', colors[i]).attr('font-size', '10px').attr('font-weight', 'bold').text(d.name);
      info.append('text').attr('x', 0).attr('y', i * 40 + 14).attr('fill', '#95a5a6').attr('font-size', '9px').text(d.speed);
      info.append('text').attr('x', 0).attr('y', i * 40 + 26).attr('fill', '#95a5a6').attr('font-size', '9px').text(`CEP: ${d.cep}`);
    });
  }

  private drawSignalProcessingFlow(): void {
    if (!this.signalProcessingChart?.nativeElement) return;
    const container = this.signalProcessingChart.nativeElement;
    const width = 800;
    const height = 120;

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg').attr('width', width).attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`).style('max-width', '100%');

    const steps = this.signalProcessingChain();
    const boxWidth = 105;
    const boxHeight = 50;
    const gap = (width - steps.length * boxWidth) / (steps.length + 1);
    const colors = ['#e74c3c', '#c9a227', '#3498db', '#27ae60', '#9b59b6', '#e67e22'];

    // Arrowhead marker
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead-sp')
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 8).attr('refY', 5)
      .attr('markerWidth', 6).attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path').attr('d', 'M 0 0 L 10 5 L 0 10 z').attr('fill', '#c9a227');

    steps.forEach((step, i) => {
      const xPos = gap + i * (boxWidth + gap);
      const yPos = (height - boxHeight) / 2;

      svg.append('rect')
        .attr('x', xPos).attr('y', yPos).attr('width', boxWidth).attr('height', boxHeight)
        .attr('fill', 'rgba(26, 42, 74, 0.8)').attr('stroke', colors[i % colors.length])
        .attr('stroke-width', 2).attr('rx', 6).style('cursor', 'pointer');

      svg.append('text')
        .attr('x', xPos + boxWidth / 2).attr('y', yPos + boxHeight / 2 + 4)
        .attr('text-anchor', 'middle').attr('fill', '#fff').attr('font-size', '8px').attr('font-weight', 'bold')
        .text(step.name);

      if (i < steps.length - 1) {
        const arrowX = xPos + boxWidth + 2;
        svg.append('line')
          .attr('x1', arrowX).attr('x2', arrowX + gap - 4).attr('y1', height / 2).attr('y2', height / 2)
          .attr('stroke', '#c9a227').attr('stroke-width', 2).attr('marker-end', 'url(#arrowhead-sp)');
      }
    });
  }
}
