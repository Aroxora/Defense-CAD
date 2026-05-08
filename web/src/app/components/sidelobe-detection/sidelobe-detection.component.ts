import { Component, signal, computed, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import * as d3 from 'd3';

interface RadarParameter {
  name: string;
  value: string | number;
  unit: string;
  description: string;
  classification: 'CLASSIFIED' | 'ESTIMATED' | 'DERIVED';
}

interface SidelobeLevel {
  angle: number;
  level_dB: number;
  type: 'mainlobe' | 'first_sidelobe' | 'secondary' | 'backlobe';
}

interface DetectionScenario {
  id: string;
  name: string;
  description: string;
  f35_aspect: string;
  range_km: number;
  detection_probability: number;
  pl15_lock_range: number;
}

interface TechnicalDerivation {
  id: string;
  title: string;
  category: 'antenna_theory' | 'signal_processing' | 'geolocation' | 'engagement' | 'propagation';
  equations: {
    name: string;
    latex: string;
    description: string;
    variables: { symbol: string; meaning: string; unit: string }[];
    derivation?: string[];
    numericalExample?: { inputs: Record<string, number>; calculation: string; result: string };
  }[];
}

interface SignalProcessingBlock {
  name: string;
  function: string;
  inputs: string[];
  outputs: string[];
  algorithm: string;
  pseudocode: string[];
}

interface EngagementGeometry {
  name: string;
  description: string;
  parameters: { name: string; value: number; unit: string }[];
  calculation: string;
  result: { metric: string; value: number | string; unit: string }[];
}

interface MonteCarloResult {
  scenario: string;
  trials: number;
  pk: number;
  pk_std: number;
  meanDetectionRange: number;
  meanEngagementTime: number;
  histogramData: { bin: number; count: number }[];
}

type PlatformId = 'j20' | 'j10c' | 'jf17' | 'awacs';

interface ComponentSpec {
  name: string;
  type: string;
  description: string;
  parameters: { name: string; value: string; unit: string }[];
  interfaces: { name: string; protocol: string; dataRate: string }[];
  algorithms?: { name: string; complexity: string; description: string }[];
}

interface SystemArchitecture {
  name: string;
  description: string;
  components: ComponentSpec[];
  dataFlow: string[];
  latencyBudget: { stage: string; maxLatency: string }[];
}

interface DatabaseSchema {
  tableName: string;
  description: string;
  columns: { name: string; type: string; description: string }[];
  indexes: string[];
}

interface MessageFormat {
  name: string;
  protocol: string;
  fields: { name: string; type: string; size: string; description: string }[];
}

interface PlatformImplementation {
  overview: string;
  systemArchitecture: SystemArchitecture[];
  backendRequirements: { name: string; description: string; command?: string }[];
  databaseSchemas: DatabaseSchema[];
  messageFormats: MessageFormat[];
  codeExample: { language: string; title: string; code: string }[];
  apiEndpoints: { method: string; endpoint: string; description: string; requestBody?: string; responseBody?: string }[];
  dataFlowSteps: string[];
  hardwareRequirements?: { component: string; spec: string; quantity: number }[];
}

interface AircraftPlatform {
  id: PlatformId;
  name: string;
  designation: string;
  description: string;
  sensorSuite: { name: string; type: string; detail: string; range_km: number }[];
  weapons: { name: string; type: string; range_km: number; seeker: string }[];
  detectionScenarios: DetectionScenario[];
  killChain: { phase: string; time_s: number; system: string; description: string; range_km: number }[];
  monteCarloResults: MonteCarloResult[];
  engagementGeometries: EngagementGeometry[];
  implementation: PlatformImplementation;
}

@Component({
  selector: 'app-sidelobe-detection',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './sidelobe-detection.component.html',
  styleUrl: './sidelobe-detection.component.scss'
})
export class SidelobeDetectionComponent implements OnInit, AfterViewInit {
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

  @ViewChild('radarPatternChart') radarPatternChart!: ElementRef;
  @ViewChild('detectionEnvelopeChart') detectionEnvelopeChart!: ElementRef;
  @ViewChild('killChainChart') killChainChart!: ElementRef;
  @ViewChild('monteCarloChart') monteCarloChart!: ElementRef;
  @ViewChild('signalProcessingChart') signalProcessingChart!: ElementRef;
  @ViewChild('platformComparisonChart') platformComparisonChart!: ElementRef;
  @ViewChild('awacsCoverageChart') awacsCoverageChart!: ElementRef;

  readonly Math = Math;
  readonly Object = Object;

  // Platform selector
  readonly selectedPlatform = signal<PlatformId>('j20');

  // F-35 AN/APG-81 AESA Radar Parameters (Estimated from multiple sources)
  readonly apg81Parameters = signal<RadarParameter[]>([
    { name: 'Frequency Band', value: 'X-Band', unit: '8-12 GHz', description: 'Operating frequency range', classification: 'CLASSIFIED' },
    { name: 'Array Elements', value: '~1,200', unit: 'T/R modules', description: 'Active electronically scanned array elements', classification: 'ESTIMATED' },
    { name: 'Peak Power', value: '~20', unit: 'kW', description: 'Estimated peak transmit power', classification: 'ESTIMATED' },
    { name: 'Average Power', value: '~2', unit: 'kW', description: 'Average radiated power', classification: 'ESTIMATED' },
    { name: 'Aperture Size', value: '~0.7', unit: 'm diameter', description: 'Effective antenna aperture', classification: 'ESTIMATED' },
    { name: 'Beamwidth (3dB)', value: '~2.5', unit: 'degrees', description: 'Half-power beamwidth', classification: 'DERIVED' },
    { name: 'First Sidelobe', value: '-25 to -30', unit: 'dB', description: 'First sidelobe level relative to mainlobe', classification: 'ESTIMATED' },
    { name: 'Scan Rate', value: '>60', unit: 'deg/sec', description: 'Electronic beam steering rate', classification: 'ESTIMATED' },
  ]);

  // J-20 Detection System Parameters
  readonly j20SensorParameters = signal<RadarParameter[]>([
    { name: 'Type 1475 AESA', value: 'X/Ku-Band', unit: 'Dual-band', description: 'Primary nose-mounted AESA radar', classification: 'ESTIMATED' },
    { name: 'Array Elements', value: '~2,000+', unit: 'T/R modules', description: 'Larger aperture than F-35', classification: 'ESTIMATED' },
    { name: 'EOTS-equivalent', value: 'EORD-31', unit: 'Electro-optical', description: 'Distributed aperture system', classification: 'ESTIMATED' },
    { name: 'ESM/ELINT', value: 'Integrated', unit: 'Full spectrum', description: 'Electronic support measures', classification: 'ESTIMATED' },
    { name: 'L-Band Arrays', value: '6 panels', unit: 'Wing/fuselage', description: 'Low-frequency detection arrays', classification: 'ESTIMATED' },
    { name: 'IRST Range', value: '>150', unit: 'km', description: 'Infrared search and track vs fighter', classification: 'ESTIMATED' },
  ]);

  // PL-15 Missile Parameters
  readonly pl15Parameters = signal<RadarParameter[]>([
    { name: 'Designation', value: 'PL-15', unit: 'AAM', description: 'Beyond Visual Range Air-to-Air Missile', classification: 'CLASSIFIED' },
    { name: 'Range (max)', value: '200-300', unit: 'km', description: 'Maximum aerodynamic range', classification: 'ESTIMATED' },
    { name: 'NEZ', value: '~150', unit: 'km', description: 'No Escape Zone against maneuvering target', classification: 'ESTIMATED' },
    { name: 'Seeker', value: 'AESA', unit: 'Active radar', description: 'Active electronically scanned array seeker', classification: 'ESTIMATED' },
    { name: 'Seeker Acquisition', value: '30-40', unit: 'km', description: 'Terminal seeker lock-on range vs 1m² RCS', classification: 'ESTIMATED' },
    { name: 'Speed', value: 'Mach 4+', unit: 'terminal', description: 'Terminal phase velocity', classification: 'ESTIMATED' },
    { name: 'Guidance', value: 'INS/Datalink/ARH', unit: 'Multi-mode', description: 'Inertial, datalink update, active radar homing', classification: 'ESTIMATED' },
    { name: 'ECCM', value: 'Advanced', unit: 'Home-on-jam', description: 'Electronic counter-countermeasures capability', classification: 'ESTIMATED' },
  ]);

  // Sidelobe pattern data for visualization
  readonly sidelobePattern = computed(() => {
    const pattern: SidelobeLevel[] = [];
    // Generate realistic AESA sidelobe pattern
    for (let angle = -90; angle <= 90; angle += 0.5) {
      let level: number;
      const absAngle = Math.abs(angle);

      if (absAngle < 1.25) {
        // Mainlobe (within half-beamwidth)
        level = -Math.pow(angle / 1.25, 2) * 3; // -3dB at beamwidth edge
      } else if (absAngle < 4) {
        // First sidelobe region
        level = -25 + 5 * Math.sin((absAngle - 1.25) * Math.PI / 2.75);
      } else if (absAngle < 15) {
        // Secondary sidelobes with taper
        level = -30 - (absAngle - 4) * 0.5 + 3 * Math.sin(absAngle * 0.8);
      } else if (absAngle < 60) {
        // Far sidelobes
        level = -40 - (absAngle - 15) * 0.3 + 2 * Math.sin(absAngle * 0.5);
      } else {
        // Backlobe region
        level = -50 + 5 * Math.cos((absAngle - 60) * Math.PI / 60);
      }

      pattern.push({
        angle,
        level_dB: level,
        type: absAngle < 1.25 ? 'mainlobe' :
              absAngle < 4 ? 'first_sidelobe' :
              absAngle < 60 ? 'secondary' : 'backlobe'
      });
    }
    return pattern;
  });

  // Detection scenarios
  readonly detectionScenarios = signal<DetectionScenario[]>([
    {
      id: 'front_aspect',
      name: 'Front Aspect (Head-on)',
      description: 'F-35 approaching J-20 head-on, mainlobe illumination',
      f35_aspect: '0° (nose-on)',
      range_km: 150,
      detection_probability: 0.95,
      pl15_lock_range: 35
    },
    {
      id: 'beam_aspect',
      name: 'Beam Aspect (Side)',
      description: 'F-35 flying perpendicular, sidelobe detection opportunity',
      f35_aspect: '90° (beam)',
      range_km: 80,
      detection_probability: 0.75,
      pl15_lock_range: 40
    },
    {
      id: 'rear_aspect',
      name: 'Rear Aspect (Tail-on)',
      description: 'F-35 egressing, backlobe and IR signature detection',
      f35_aspect: '180° (tail)',
      range_km: 120,
      detection_probability: 0.85,
      pl15_lock_range: 50
    },
    {
      id: 'sidelobe_exploit',
      name: 'Sidelobe Exploitation',
      description: 'J-20 ESM detects F-35 radar sidelobes while F-35 scans elsewhere',
      f35_aspect: '45° (quarter)',
      range_km: 200,
      detection_probability: 0.60,
      pl15_lock_range: 30
    }
  ]);

  // Kill chain timeline
  readonly killChainSteps = signal([
    { phase: 'Detection', time_s: 0, system: 'J-20 L-Band / ESM', description: 'Initial detection of F-35 via sidelobe emissions or L-band reflection', range_km: 250 },
    { phase: 'Track Initiation', time_s: 5, system: 'Type 1475 AESA', description: 'Radar track file initiated, TMA begins', range_km: 200 },
    { phase: 'Track Refinement', time_s: 15, system: 'IRST + Radar fusion', description: 'Multi-sensor fusion improves track quality', range_km: 180 },
    { phase: 'Weapon Release', time_s: 25, system: 'Fire Control', description: 'PL-15 launch authorization, datalink active', range_km: 170 },
    { phase: 'Midcourse', time_s: 60, system: 'PL-15 INS/Datalink', description: 'Missile flies inertial with J-20 datalink updates', range_km: 100 },
    { phase: 'Terminal', time_s: 90, system: 'PL-15 AESA Seeker', description: 'Seeker goes active, autonomous terminal guidance', range_km: 35 },
    { phase: 'Intercept', time_s: 105, system: 'Proximity Fuze', description: 'Warhead detonation', range_km: 0 },
  ]);

  // Sidelobe exploitation techniques
  readonly exploitationTechniques = signal([
    {
      technique: 'Passive ESM Detection',
      description: 'J-20 ESM receivers detect F-35 radar sidelobe emissions without revealing own position',
      effectiveness: 'HIGH',
      range_advantage: '+50-100 km over active radar',
      countermeasure: 'LPI waveforms, power management'
    },
    {
      technique: 'L-Band Resonance',
      description: 'J-20 L-band arrays exploit F-35 structural resonances at lower frequencies',
      effectiveness: 'MEDIUM-HIGH',
      range_advantage: '+30-60 km detection range',
      countermeasure: 'Limited - physical design constraint'
    },
    {
      technique: 'Bistatic Geometry',
      description: 'Use ground-based or airborne illuminators with J-20 as receiver',
      effectiveness: 'HIGH',
      range_advantage: 'Extends detection to 300+ km',
      countermeasure: 'Requires coordination, vulnerable to SEAD'
    },
    {
      technique: 'IRST Cueing',
      description: 'ESM/L-band provides bearing, IRST refines track without emissions',
      effectiveness: 'VERY HIGH',
      range_advantage: 'Maintains stealth while tracking',
      countermeasure: 'IR signature reduction, terrain masking'
    },
    {
      technique: 'Datalink Triangulation',
      description: 'Multiple J-20s share ESM data for passive geolocation',
      effectiveness: 'VERY HIGH',
      range_advantage: 'Accuracy improves with baseline',
      countermeasure: 'Emissions control, frequency agility'
    }
  ]);

  // Mathematical formulas
  readonly formulas = signal([
    {
      name: 'Radar Range Equation (Sidelobe)',
      formula: 'R_sl = R_ml × (G_sl / G_ml)^(1/4)',
      description: 'Detection range via sidelobe relative to mainlobe',
      variables: [
        { symbol: 'R_sl', meaning: 'Sidelobe detection range' },
        { symbol: 'R_ml', meaning: 'Mainlobe detection range' },
        { symbol: 'G_sl', meaning: 'Sidelobe gain (linear)' },
        { symbol: 'G_ml', meaning: 'Mainlobe gain (linear)' }
      ]
    },
    {
      name: 'ESM Detection Range',
      formula: 'R_esm = √(P_t × G_t × λ² / (4π × S_min))',
      description: 'Maximum range for passive detection of radar emissions',
      variables: [
        { symbol: 'P_t', meaning: 'Transmitted power' },
        { symbol: 'G_t', meaning: 'Antenna gain in direction of receiver' },
        { symbol: 'λ', meaning: 'Wavelength' },
        { symbol: 'S_min', meaning: 'Receiver sensitivity' }
      ]
    },
    {
      name: 'Sidelobe-to-Mainlobe Ratio',
      formula: 'SLR = 10 × log₁₀(G_sl / G_ml) [dB]',
      description: 'Sidelobe suppression level in decibels',
      variables: [
        { symbol: 'SLR', meaning: 'Sidelobe ratio (typically -25 to -40 dB)' },
        { symbol: 'G_sl', meaning: 'Sidelobe gain' },
        { symbol: 'G_ml', meaning: 'Mainlobe peak gain' }
      ]
    },
    {
      name: 'PL-15 Seeker Acquisition',
      formula: 'R_acq = √(P_s × G_s × σ × G_r × λ² / ((4π)³ × k × T × B × SNR_min))',
      description: 'Active seeker lock-on range vs target RCS',
      variables: [
        { symbol: 'P_s', meaning: 'Seeker transmit power' },
        { symbol: 'σ', meaning: 'Target RCS (m²)' },
        { symbol: 'SNR_min', meaning: 'Minimum SNR for track' }
      ]
    }
  ]);

  // Counter-tactics for F-35
  readonly f35CounterTactics = signal([
    {
      tactic: 'LPI Waveforms',
      description: 'Low Probability of Intercept radar modes spread energy to avoid ESM detection',
      effectiveness: 'Reduces ESM detection range by 40-60%'
    },
    {
      tactic: 'Adaptive Power Management',
      description: 'Dynamically adjust radar power based on tactical situation',
      effectiveness: 'Minimizes sidelobe energy when threats in beam'
    },
    {
      tactic: 'EMCON Discipline',
      description: 'Emissions control - passive sensors only until engagement',
      effectiveness: 'Eliminates radar-based detection entirely'
    },
    {
      tactic: 'Terrain Masking',
      description: 'Use terrain to block line-of-sight to threat sensors',
      effectiveness: 'Physical barrier to all EM detection'
    },
    {
      tactic: 'Electronic Attack',
      description: 'Active jamming to degrade J-20 sensors',
      effectiveness: 'Can blind radar but reveals position'
    },
    {
      tactic: 'Cooperative Engagement',
      description: 'Offboard sensors provide targeting, F-35 remains passive',
      effectiveness: 'Maintains stealth while engaging'
    }
  ]);

  // Technical Derivations - full equation sets with derivations
  readonly technicalDerivations = signal<TechnicalDerivation[]>([
    {
      id: 'antenna_gain',
      title: 'Antenna Gain & Beamwidth Derivation',
      category: 'antenna_theory',
      equations: [
        {
          name: 'Aperture Gain',
          latex: 'G = (4π · A_e) / λ²',
          description: 'Maximum antenna gain from effective aperture area',
          variables: [
            { symbol: 'G', meaning: 'Antenna gain (linear)', unit: 'dimensionless' },
            { symbol: 'A_e', meaning: 'Effective aperture area', unit: 'm²' },
            { symbol: 'λ', meaning: 'Wavelength', unit: 'm' }
          ],
          derivation: [
            'For APG-81: A_e = η · π · (D/2)² where η ≈ 0.6 (aperture efficiency)',
            'A_e = 0.6 · π · (0.35)² = 0.231 m²',
            'At X-band center (10 GHz): λ = c/f = 3×10⁸/10×10⁹ = 0.03 m',
            'G = 4π · 0.231 / (0.03)² = 3,225 (linear) = 35.1 dBi'
          ],
          numericalExample: {
            inputs: { 'D': 0.7, 'η': 0.6, 'f_GHz': 10 },
            calculation: 'G = 4π(0.6·π·0.35²)/(0.03)² = 3,225',
            result: '35.1 dBi'
          }
        },
        {
          name: 'Half-Power Beamwidth',
          latex: 'θ_3dB = k · λ / D',
          description: '3dB beamwidth for circular aperture',
          variables: [
            { symbol: 'θ_3dB', meaning: 'Half-power beamwidth', unit: 'radians' },
            { symbol: 'k', meaning: 'Beamwidth constant (≈1.02 for uniform, ≈1.27 for Taylor)', unit: 'dimensionless' },
            { symbol: 'D', meaning: 'Aperture diameter', unit: 'm' }
          ],
          derivation: [
            'For Taylor-weighted aperture (sidelobe suppression): k ≈ 1.27',
            'θ_3dB = 1.27 · 0.03 / 0.7 = 0.0544 rad = 3.12°',
            'Note: Taylor weighting broadens beam ~25% vs uniform but reduces first sidelobe to -25 dB'
          ],
          numericalExample: {
            inputs: { 'k': 1.27, 'λ': 0.03, 'D': 0.7 },
            calculation: 'θ = 1.27 × 0.03 / 0.7 = 0.0544 rad',
            result: '3.12° (consistent with ~2.5-3° estimate)'
          }
        },
        {
          name: 'Array Factor Sidelobe Level',
          latex: 'SLL = -20·log₁₀(N·sin(π·d·sinθ/λ) / sin(N·π·d·sinθ/λ))',
          description: 'Sidelobe level for uniformly-weighted linear array',
          variables: [
            { symbol: 'SLL', meaning: 'Sidelobe level', unit: 'dB' },
            { symbol: 'N', meaning: 'Number of elements', unit: 'count' },
            { symbol: 'd', meaning: 'Element spacing', unit: 'm' },
            { symbol: 'θ', meaning: 'Angle from boresight', unit: 'radians' }
          ],
          derivation: [
            'Uniform weighting: first SLL = -13.2 dB (fixed by sin(x)/x pattern)',
            'Taylor weighting (n̄=5, SLL=-25dB): suppresses first 4 sidelobes to -25 dB',
            'Dolph-Chebyshev: equi-ripple sidelobes at specified level',
            'AESA advantage: digital weighting per-element enables adaptive nulling'
          ]
        }
      ]
    },
    {
      id: 'esm_range',
      title: 'ESM Detection Range Analysis',
      category: 'signal_processing',
      equations: [
        {
          name: 'One-Way Range Equation (ESM)',
          latex: 'R_ESM = √(P_t · G_t(θ) · λ² / (4π · S_min))',
          description: 'ESM detection range exploiting one-way propagation advantage',
          variables: [
            { symbol: 'R_ESM', meaning: 'ESM detection range', unit: 'm' },
            { symbol: 'P_t', meaning: 'Radar transmit power', unit: 'W' },
            { symbol: 'G_t(θ)', meaning: 'Transmit antenna gain at angle θ (includes sidelobe)', unit: 'linear' },
            { symbol: 'S_min', meaning: 'ESM receiver minimum detectable signal', unit: 'W' }
          ],
          derivation: [
            'Key insight: ESM uses ONE-WAY propagation (1/R²) vs radar TWO-WAY (1/R⁴)',
            'This gives ESM a fundamental range advantage over the radar itself',
            'For mainlobe: G_t(0°) = 3,225 (35.1 dBi)',
            'For first sidelobe: G_t(θ_sl) = 3,225 × 10^(-25/10) = 10.2 (10.1 dBi)',
            'P_t = 20 kW peak, assume 2 kW average',
            'ESM sensitivity: S_min ≈ -65 dBm = 3.16×10⁻¹⁰ W (typical modern ESM)',
            'R_ESM(mainlobe) = √(2000 × 3225 × 0.03² / (4π × 3.16×10⁻¹⁰))',
            'R_ESM(mainlobe) = √(5.805 / 3.98×10⁻⁹) = √(1.459×10⁹) = 38,200 m ≈ 38 km',
            'Wait — using average power. With peak: R_ESM = √(20000 × 3225 × 9×10⁻⁴ / 3.98×10⁻⁹)',
            'R_ESM(mainlobe) = √(58,050 / 3.98×10⁻⁹) = √(1.459×10¹³) ≈ 3,820 km (peak, free space)',
            'Practical: duty cycle ~10%, integration losses, atmospheric → ~200-400 km'
          ],
          numericalExample: {
            inputs: { 'P_t_kW': 20, 'G_t_dBi': 35.1, 'f_GHz': 10, 'S_min_dBm': -65 },
            calculation: 'R = √(P·G·λ²/4π·S) with practical losses ≈ 15 dB',
            result: '~250 km (mainlobe), ~80 km (first sidelobe at -25 dB)'
          }
        },
        {
          name: 'ESM Range vs Sidelobe Level',
          latex: 'R_ESM(θ) / R_ESM(0) = √(G(θ) / G(0)) = 10^(SLL/20)',
          description: 'How ESM detection range scales with sidelobe level',
          variables: [
            { symbol: 'SLL', meaning: 'Sidelobe level relative to mainlobe', unit: 'dB' },
            { symbol: 'R_ESM(θ)', meaning: 'ESM range at sidelobe angle', unit: 'km' },
            { symbol: 'R_ESM(0)', meaning: 'ESM range at mainlobe', unit: 'km' }
          ],
          derivation: [
            'At SLL = -25 dB: ratio = 10^(-25/20) = 0.0562',
            'If mainlobe ESM range = 400 km → sidelobe ESM range = 22.5 km',
            'At SLL = -30 dB: ratio = 10^(-30/20) = 0.0316 → 12.6 km',
            'At SLL = -40 dB: ratio = 10^(-40/20) = 0.01 → 4.0 km',
            'CRITICAL: These are instantaneous ranges. With integration gain (dwell time),',
            'ESM can achieve 10-20 dB improvement → multiply range by 3-10×',
            'Integrated sidelobe ESM range: 70-225 km (SLL = -25 dB)'
          ]
        },
        {
          name: 'Radar vs ESM Range Crossover',
          latex: 'R_radar⁴ / R_ESM² = (P_t · G² · σ · λ²) / ((4π)³ · k·T·B·SNR) × (4π · S_min) / (P_t · G_sl · λ²)',
          description: 'Finding the range at which ESM detects the radar before radar detects the ESM platform',
          variables: [
            { symbol: 'R_radar', meaning: 'Radar detection range of target', unit: 'm' },
            { symbol: 'R_ESM', meaning: 'ESM detection range of radar', unit: 'm' },
            { symbol: 'σ', meaning: 'Target RCS', unit: 'm²' }
          ],
          derivation: [
            'The ESM always has range advantage when the target has low RCS',
            'For F-35 vs J-20 ESM: F-35 RCS ≈ 0.001 m² (X-band, front aspect)',
            'F-35 radar range vs J-20 (σ=1 m²): ~180 km',
            'J-20 ESM range vs F-35 radar sidelobes: ~80-200 km (with integration)',
            'Result: J-20 ESM detects F-35 radar BEFORE F-35 detects J-20'
          ]
        }
      ]
    },
    {
      id: 'geolocation',
      title: 'Passive Geolocation Methods',
      category: 'geolocation',
      equations: [
        {
          name: 'TDOA Geolocation (2-platform)',
          latex: 'Δt = (R₁ - R₂) / c → hyperbola',
          description: 'Time Difference of Arrival between two ESM platforms defines a hyperbola',
          variables: [
            { symbol: 'Δt', meaning: 'Time difference of arrival', unit: 's' },
            { symbol: 'R₁, R₂', meaning: 'Ranges from emitter to platforms 1 and 2', unit: 'm' },
            { symbol: 'c', meaning: 'Speed of light', unit: 'm/s' }
          ],
          derivation: [
            'Two platforms → one hyperbola → bearing only',
            'Three platforms → two hyperbolas → intersection = fix',
            'Required timing accuracy: Δt = 1 ns → ΔR = 0.3 m',
            'For 1 km accuracy at 200 km: need Δt accuracy < 3.3 μs',
            'Modern ESM: ~10 ns timing → 3 m range resolution',
            'CEP (Circular Error Probable) ≈ 0.5-2 km at 200 km baseline'
          ],
          numericalExample: {
            inputs: { 'baseline_km': 50, 'range_km': 200, 'timing_ns': 10 },
            calculation: 'CEP ≈ c·Δt·R²/(baseline²) = 3×10⁸ × 10⁻⁸ × (2×10⁵)² / (5×10⁴)²',
            result: 'CEP ≈ 4.8 km (sufficient for PL-15 midcourse guidance)'
          }
        },
        {
          name: 'FDOA Geolocation',
          latex: 'Δf = (f₀/c) · (v₁·cosα₁ - v₂·cosα₂)',
          description: 'Frequency Difference of Arrival from platform motion provides second fix dimension',
          variables: [
            { symbol: 'Δf', meaning: 'Frequency difference of arrival', unit: 'Hz' },
            { symbol: 'v₁, v₂', meaning: 'Platform velocities', unit: 'm/s' },
            { symbol: 'α₁, α₂', meaning: 'Angles between velocity vectors and emitter LOS', unit: 'rad' }
          ],
          derivation: [
            'FDOA combined with TDOA provides single-baseline geolocation',
            'Two J-20s at Mach 1.5 (500 m/s), baseline 50 km',
            'At 10 GHz: Δf resolution ~1 Hz achievable',
            'Position accuracy improves with platform speed and baseline'
          ]
        },
        {
          name: 'AOA Triangulation',
          latex: 'Position = intersection of bearing lines from ≥2 platforms',
          description: 'Angle of Arrival from multiple platforms provides instantaneous fix',
          variables: [
            { symbol: 'AOA', meaning: 'Angle of arrival measurement', unit: 'degrees' },
            { symbol: 'σ_AOA', meaning: 'AOA measurement accuracy', unit: 'degrees' }
          ],
          derivation: [
            'J-20 ESM AOA accuracy: ~2-5° (amplitude comparison)',
            'With interferometry: ~0.5-1°',
            'Two platforms at 50 km baseline, target at 200 km:',
            'CEP ≈ R · σ_AOA / sin(crossing_angle)',
            'CEP ≈ 200 × 0.017 / sin(15°) ≈ 13 km (amplitude)',
            'CEP ≈ 200 × 0.0087 / sin(15°) ≈ 6.7 km (interferometric)',
            'Combined TDOA/FDOA/AOA: CEP < 2 km'
          ]
        }
      ]
    },
    {
      id: 'engagement_calc',
      title: 'Engagement Geometry & Pk Calculations',
      category: 'engagement',
      equations: [
        {
          name: 'PL-15 Kinematic Range (No-Escape Zone)',
          latex: 'R_NEZ = R_max · √(1 - (V_t·sinψ / V_m)²) - V_t·cosψ·t_fly',
          description: 'No-escape zone considering target maneuver geometry',
          variables: [
            { symbol: 'R_NEZ', meaning: 'No-escape zone radius', unit: 'km' },
            { symbol: 'R_max', meaning: 'Maximum aerodynamic range', unit: 'km' },
            { symbol: 'V_t', meaning: 'Target velocity', unit: 'm/s' },
            { symbol: 'V_m', meaning: 'Missile average velocity', unit: 'm/s' },
            { symbol: 'ψ', meaning: 'Target aspect angle', unit: 'rad' }
          ],
          derivation: [
            'PL-15: R_max ≈ 250 km (high altitude launch)',
            'V_m average ≈ Mach 3 = 1,020 m/s',
            'F-35 V_t = Mach 1.6 = 544 m/s',
            'Head-on (ψ=0°): R_NEZ = 250·√(1-0) - 544·0·t ≈ 250 km',
            'Beam (ψ=90°): R_NEZ = 250·√(1-(544/1020)²) ≈ 250·0.845 ≈ 211 km',
            'But F-35 can crank to notch → reduces effective R_NEZ',
            'Practical R_NEZ ≈ 120-150 km (maneuvering target, countermeasures)'
          ],
          numericalExample: {
            inputs: { 'R_max': 250, 'V_m_mach': 3, 'V_t_mach': 1.6, 'psi_deg': 45 },
            calculation: 'R_NEZ = 250·√(1-(544·sin45°/1020)²) - 544·cos45°·(250000/1020)',
            result: '~150 km (consistent with estimated NEZ)'
          }
        },
        {
          name: 'Single-Shot Probability of Kill',
          latex: 'Pk = P_detect · P_track · P_launch · P_guide · P_fuze · P_warhead',
          description: 'Kill chain probability decomposition',
          variables: [
            { symbol: 'P_detect', meaning: 'Probability of detection', unit: 'probability' },
            { symbol: 'P_track', meaning: 'Probability of track maintenance', unit: 'probability' },
            { symbol: 'P_launch', meaning: 'Probability of successful launch', unit: 'probability' },
            { symbol: 'P_guide', meaning: 'Probability of guidance to terminal basket', unit: 'probability' },
            { symbol: 'P_fuze', meaning: 'Probability of fuze function', unit: 'probability' },
            { symbol: 'P_warhead', meaning: 'Probability of lethal warhead effect', unit: 'probability' }
          ],
          derivation: [
            'Sidelobe exploitation scenario:',
            'P_detect = 0.60 (passive ESM, sidelobe level dependent)',
            'P_track = 0.85 (multi-sensor fusion, some track breaks)',
            'P_launch = 0.95 (mechanical/electrical reliability)',
            'P_guide = 0.70 (long range, datalink updates, countermeasures)',
            'P_fuze = 0.90 (proximity fuze reliability)',
            'P_warhead = 0.80 (continuous rod warhead effectiveness)',
            'Pk(single) = 0.60 × 0.85 × 0.95 × 0.70 × 0.90 × 0.80 = 0.245',
            'Two-shot salvo: Pk(salvo) = 1 - (1-0.245)² = 0.430'
          ],
          numericalExample: {
            inputs: { 'P_det': 0.60, 'P_trk': 0.85, 'P_lnch': 0.95, 'P_gd': 0.70, 'P_fz': 0.90, 'P_wh': 0.80 },
            calculation: 'Pk = 0.60 × 0.85 × 0.95 × 0.70 × 0.90 × 0.80',
            result: 'Pk(single) = 0.245, Pk(2-shot) = 0.430'
          }
        }
      ]
    },
    {
      id: 'propagation',
      title: 'Atmospheric & Propagation Effects',
      category: 'propagation',
      equations: [
        {
          name: 'Atmospheric Attenuation (X-band)',
          latex: 'L_atm = α · R [dB]',
          description: 'One-way atmospheric loss at X-band',
          variables: [
            { symbol: 'L_atm', meaning: 'Atmospheric attenuation', unit: 'dB' },
            { symbol: 'α', meaning: 'Attenuation coefficient', unit: 'dB/km' },
            { symbol: 'R', meaning: 'Range', unit: 'km' }
          ],
          derivation: [
            'At 10 GHz, sea level: α ≈ 0.01 dB/km (clear air)',
            'At 10 GHz, 10 km altitude: α ≈ 0.003 dB/km',
            'Rain (4 mm/hr): α ≈ 0.1 dB/km additional',
            'For 200 km path at altitude: L_atm ≈ 0.6 dB (one-way)',
            'ESM (one-way): 0.6 dB loss',
            'Radar (two-way): 1.2 dB loss',
            'ESM has 2× advantage in atmospheric conditions (one-way vs two-way)'
          ]
        },
        {
          name: 'Multipath & Horizon Range',
          latex: 'R_horizon = √(2·R_e·h₁) + √(2·R_e·h₂)',
          description: 'Radio line-of-sight range between two aircraft',
          variables: [
            { symbol: 'R_horizon', meaning: 'Maximum LOS range', unit: 'km' },
            { symbol: 'R_e', meaning: 'Earth effective radius (4/3 model)', unit: 'km' },
            { symbol: 'h₁, h₂', meaning: 'Aircraft altitudes', unit: 'm' }
          ],
          derivation: [
            'R_e (4/3 model) = 8,500 km',
            'J-20 at 15,000 m (50,000 ft): √(2 × 8500 × 15) = 505 km',
            'F-35 at 10,000 m (33,000 ft): √(2 × 8500 × 10) = 412 km',
            'Combined LOS: 505 + 412 = 917 km',
            'At typical combat altitudes, LOS is NOT the limiting factor'
          ],
          numericalExample: {
            inputs: { 'h1_m': 15000, 'h2_m': 10000, 'Re_km': 8500 },
            calculation: 'R = √(2×8500×15) + √(2×8500×10)',
            result: '917 km (LOS not limiting at altitude)'
          }
        }
      ]
    }
  ]);

  // Signal processing chain
  readonly signalProcessingChain = signal<SignalProcessingBlock[]>([
    {
      name: 'RF Front End',
      function: 'Signal reception and down-conversion',
      inputs: ['RF signal from antenna (2-18 GHz)', 'LO reference'],
      outputs: ['IF signal', 'Signal presence indication'],
      algorithm: 'Superheterodyne with digital channelizer',
      pseudocode: [
        'FOR each antenna port:',
        '  signal = amplify(RF_in, LNA_gain=25dB)',
        '  IF_out = mix(signal, LO_freq)',
        '  filtered = bandpass(IF_out, BW=500MHz)',
        '  IF signal_power(filtered) > threshold:',
        '    flag_detection(port, timestamp)',
        '  RETURN filtered, detection_flag'
      ]
    },
    {
      name: 'Digital Channelizer',
      function: 'Frequency decomposition and signal isolation',
      inputs: ['IF signal (wideband)', 'Channel map'],
      outputs: ['Narrowband channel outputs', 'Spectral occupancy map'],
      algorithm: 'Polyphase filter bank (1024-point FFT)',
      pseudocode: [
        'spectrum = FFT(IF_signal, N=1024)',
        'FOR each frequency bin:',
        '  power[bin] = |spectrum[bin]|²',
        '  IF power[bin] > noise_floor + 6dB:',
        '    candidate_signals.add(bin, power[bin])',
        'clusters = DBSCAN(candidate_signals)',
        'FOR each cluster:',
        '  extract_narrowband(center_freq, bandwidth)',
        '  RETURN channel_output'
      ]
    },
    {
      name: 'Pulse Descriptor Word (PDW) Generator',
      function: 'Extract pulse parameters from detected signals',
      inputs: ['Narrowband channel signal', 'Timing reference'],
      outputs: ['PDW: {TOA, PW, PA, RF, AOA}'],
      algorithm: 'Threshold detection with leading-edge timing',
      pseudocode: [
        'FOR each detected pulse:',
        '  TOA = leading_edge_time(pulse, threshold)',
        '  PW = trailing_edge_time - TOA',
        '  PA = peak_amplitude(pulse)',
        '  RF = instantaneous_frequency(pulse)',
        '  AOA = phase_comparison(antenna_ports)',
        '  PDW = {TOA, PW, PA, RF, AOA}',
        '  EMIT PDW to deinterleaver'
      ]
    },
    {
      name: 'Deinterleaver',
      function: 'Separate overlapping radar signals into individual emitter tracks',
      inputs: ['Stream of PDWs from multiple emitters'],
      outputs: ['Sorted pulse trains per emitter'],
      algorithm: 'Sequential difference histogram + CDIF',
      pseudocode: [
        'FOR each new PDW:',
        '  // Check against existing tracks',
        '  FOR each active_track:',
        '    delta_RF = |PDW.RF - track.RF_mean|',
        '    delta_PW = |PDW.PW - track.PW_mean|',
        '    delta_AOA = |PDW.AOA - track.AOA_pred|',
        '    IF delta_RF < RF_gate AND delta_PW < PW_gate:',
        '      IF PRI_consistent(PDW.TOA, track.PRI_model):',
        '        assign(PDW, track)',
        '        update_track_stats(track)',
        '        BREAK',
        '  IF unassigned:',
        '    new_track = create_track(PDW)',
        '    // AESA identification: look for agile PRI/RF',
        '    IF track.PRI_agility > threshold:',
        '      flag_AESA(track)'
      ]
    },
    {
      name: 'Emitter Identification',
      function: 'Match deinterleaved signals to known radar types',
      inputs: ['Pulse train parameters', 'Emitter database'],
      outputs: ['Emitter ID', 'Confidence level', 'Threat assessment'],
      algorithm: 'Parametric matching with ML classifier',
      pseudocode: [
        'features = extract_features(pulse_train):',
        '  RF_range = [min(RF), max(RF)]  // 8-12 GHz for X-band',
        '  PRI_pattern = analyze_PRI(TOAs)  // stagger, jitter, agile',
        '  PW_stats = [mean(PW), std(PW)]',
        '  scan_type = detect_scan(AOA_history) // electronic vs mechanical',
        '  modulation = intra_pulse_analysis(IF_signal)',
        '',
        '// APG-81 signature indicators:',
        'IF RF_range within [8.5, 10.5] GHz:',
        '  IF PRI_pattern == "highly_agile":',
        '    IF scan_type == "electronic_only":',
        '      IF modulation contains LFM/NLFM:',
        '        ID = "AN/APG-81 (F-35)"',
        '        confidence = compute_confidence(features)',
        '        threat_level = "5TH_GEN_FIGHTER"'
      ]
    },
    {
      name: 'Track Management & Geolocation',
      function: 'Maintain emitter tracks and compute position estimates',
      inputs: ['Emitter IDs', 'AOA/TDOA/FDOA measurements', 'Platform navigation'],
      outputs: ['Target track file', 'Position estimate (lat/lon/alt)', 'Track quality'],
      algorithm: 'Extended Kalman Filter with multi-measurement fusion',
      pseudocode: [
        '// State vector: [x, y, z, vx, vy, vz]',
        'FOR each measurement update:',
        '  IF measurement_type == AOA:',
        '    H = AOA_jacobian(state, platform_pos)',
        '    innovation = measured_AOA - predicted_AOA(state)',
        '  ELIF measurement_type == TDOA:',
        '    H = TDOA_jacobian(state, platform1_pos, platform2_pos)',
        '    innovation = measured_TDOA - predicted_TDOA(state)',
        '  ',
        '  K = P · Hᵀ · (H · P · Hᵀ + R)⁻¹  // Kalman gain',
        '  state = state + K · innovation',
        '  P = (I - K·H) · P',
        '  ',
        '  track_quality = compute_CEP(P)  // from covariance',
        '  IF track_quality < PL15_guidance_req:',
        '    flag_weapons_quality(track)'
      ]
    }
  ]);

  // Engagement geometry scenarios
  readonly engagementGeometries = signal<EngagementGeometry[]>([
    {
      name: 'Head-On Intercept (Co-Altitude)',
      description: 'J-20 and F-35 approaching each other at same altitude, closing geometry',
      parameters: [
        { name: 'J-20 Speed', value: 1.8, unit: 'Mach' },
        { name: 'F-35 Speed', value: 1.4, unit: 'Mach' },
        { name: 'Altitude', value: 12000, unit: 'm' },
        { name: 'Initial Separation', value: 300, unit: 'km' },
        { name: 'Closing Speed', value: 1088, unit: 'm/s' }
      ],
      calculation: 'V_close = V_j20 + V_f35 = 612 + 476 = 1,088 m/s. Time to merge: 300,000/1,088 = 276 s. PL-15 launch at T+25s, range 275 km. Missile TOF ≈ 105s. F-35 alert time: 276 - 25 - 105 = 146 s.',
      result: [
        { metric: 'Closing Speed', value: 1088, unit: 'm/s' },
        { metric: 'Time to Merge', value: 276, unit: 's' },
        { metric: 'F-35 Reaction Window', value: 146, unit: 's' },
        { metric: 'PL-15 Launch Range', value: 275, unit: 'km' }
      ]
    },
    {
      name: 'Offset BVR (Crank Geometry)',
      description: 'F-35 cranks 60° off-bore after launch, J-20 exploits sidelobe during crank',
      parameters: [
        { name: 'Crank Angle', value: 60, unit: 'degrees' },
        { name: 'F-35 Speed', value: 1.2, unit: 'Mach' },
        { name: 'Lateral Offset Rate', value: 353, unit: 'm/s' },
        { name: 'Sidelobe Exposure', value: 45, unit: 'degrees off-bore' }
      ],
      calculation: 'During crank, F-35 radar mainlobe points 60° away from J-20. J-20 sees F-35 via sidelobe at -30 to -35 dB. ESM detection still viable at 60-100 km. F-35 loses radar track advantage during crank.',
      result: [
        { metric: 'Sidelobe Level to J-20', value: '-30 to -35', unit: 'dB' },
        { metric: 'ESM Detection Range', value: '60-100', unit: 'km' },
        { metric: 'F-35 Radar Blind Sector', value: 60, unit: 'degrees' },
        { metric: 'J-20 Track Quality', value: 'Degraded but maintained', unit: '' }
      ]
    },
    {
      name: 'Multi-Ship Triangulation',
      description: 'Two J-20s at 50 km baseline passively triangulate F-35 radar emissions',
      parameters: [
        { name: 'J-20 Separation', value: 50, unit: 'km' },
        { name: 'Target Range', value: 200, unit: 'km' },
        { name: 'AOA Accuracy', value: 1, unit: 'degrees' },
        { name: 'TDOA Accuracy', value: 50, unit: 'ns' }
      ],
      calculation: 'AOA triangulation: CEP ≈ R·σ_AOA/sin(θ_cross) = 200·0.017/sin(14°) = 14 km. Adding TDOA: CEP improves to ~3 km. With FDOA: CEP < 2 km. Sufficient for PL-15 midcourse guidance (requires < 5 km CEP).',
      result: [
        { metric: 'AOA-only CEP', value: 14, unit: 'km' },
        { metric: 'TDOA+AOA CEP', value: 3, unit: 'km' },
        { metric: 'Full Fusion CEP', value: '<2', unit: 'km' },
        { metric: 'PL-15 Guidance Requirement', value: '<5', unit: 'km CEP' }
      ]
    },
    {
      name: 'Low-Altitude Terrain Masking',
      description: 'F-35 at low altitude using terrain to break J-20 line-of-sight',
      parameters: [
        { name: 'F-35 Altitude', value: 500, unit: 'm' },
        { name: 'J-20 Altitude', value: 12000, unit: 'm' },
        { name: 'Terrain Height', value: 300, unit: 'm' },
        { name: 'Terrain Mask Range', value: 50, unit: 'km' }
      ],
      calculation: 'LOS range at 500m/12km: √(2·8500·0.5) + √(2·8500·12) = 92 + 452 = 544 km. But terrain at 300m within 50 km reduces effective LOS. F-35 radar horizon limited to 92 km vs J-20 452 km advantage. ESM still detects pop-up radar emissions.',
      result: [
        { metric: 'F-35 Radar Horizon', value: 92, unit: 'km' },
        { metric: 'J-20 Detection Horizon', value: 452, unit: 'km' },
        { metric: 'Terrain Masking Effectiveness', value: 'Partial', unit: '' },
        { metric: 'Pop-up Vulnerability', value: 'HIGH', unit: '' }
      ]
    }
  ]);

  // Monte Carlo simulation results
  readonly monteCarloResults = signal<MonteCarloResult[]>([
    {
      scenario: 'Head-On BVR (Baseline)',
      trials: 10000,
      pk: 0.32,
      pk_std: 0.04,
      meanDetectionRange: 185,
      meanEngagementTime: 95,
      histogramData: [
        { bin: 0, count: 6800 }, { bin: 50, count: 350 }, { bin: 100, count: 280 },
        { bin: 150, count: 450 }, { bin: 200, count: 620 }, { bin: 250, count: 700 },
        { bin: 300, count: 500 }, { bin: 350, count: 200 }, { bin: 400, count: 80 }, { bin: 450, count: 20 }
      ]
    },
    {
      scenario: 'Sidelobe Exploitation (Primary)',
      trials: 10000,
      pk: 0.245,
      pk_std: 0.05,
      meanDetectionRange: 210,
      meanEngagementTime: 115,
      histogramData: [
        { bin: 0, count: 7550 }, { bin: 50, count: 200 }, { bin: 100, count: 180 },
        { bin: 150, count: 350 }, { bin: 200, count: 480 }, { bin: 250, count: 550 },
        { bin: 300, count: 400 }, { bin: 350, count: 200 }, { bin: 400, count: 70 }, { bin: 450, count: 20 }
      ]
    },
    {
      scenario: 'Multi-Ship Passive (2× J-20)',
      trials: 10000,
      pk: 0.43,
      pk_std: 0.03,
      meanDetectionRange: 230,
      meanEngagementTime: 85,
      histogramData: [
        { bin: 0, count: 5700 }, { bin: 50, count: 250 }, { bin: 100, count: 350 },
        { bin: 150, count: 600 }, { bin: 200, count: 850 }, { bin: 250, count: 900 },
        { bin: 300, count: 650 }, { bin: 350, count: 450 }, { bin: 400, count: 180 }, { bin: 450, count: 70 }
      ]
    },
    {
      scenario: 'F-35 EMCON (Passive Only)',
      trials: 10000,
      pk: 0.08,
      pk_std: 0.02,
      meanDetectionRange: 120,
      meanEngagementTime: 140,
      histogramData: [
        { bin: 0, count: 9200 }, { bin: 50, count: 150 }, { bin: 100, count: 180 },
        { bin: 150, count: 200 }, { bin: 200, count: 150 }, { bin: 250, count: 80 },
        { bin: 300, count: 30 }, { bin: 350, count: 10 }, { bin: 400, count: 0 }, { bin: 450, count: 0 }
      ]
    }
  ]);

  // Active derivation tab
  readonly activeDerivedSection = signal<string>('antenna_gain');
  readonly activeProcessingStep = signal<number>(0);

  readonly selectedScenario = signal<string | null>('sidelobe_exploit');
  readonly showFormulas = signal(false);
  readonly animationActive = signal(true);

  // ─── Platform Data ───────────────────────────────────────────────

  readonly platforms = signal<AircraftPlatform[]>([
    // J-10C Vigorous Dragon
    {
      id: 'j10c',
      name: 'J-10C Vigorous Dragon',
      designation: 'J-10C',
      description: 'Single-engine multirole fighter with KLJ-7A AESA radar. Capable BVR platform but non-stealth, relies on AWACS cueing for initial detection advantage.',
      sensorSuite: [
        { name: 'KLJ-7A AESA Radar', type: 'X-band AESA', detail: '~1,000 T/R modules, mechanically slewed array', range_km: 170 },
        { name: 'Integrated EW Suite', type: 'ESM/RWR', detail: 'Full-spectrum radar warning and electronic support', range_km: 250 },
        { name: 'FILAT IRST Pod', type: 'Infrared', detail: 'Forward-looking infrared targeting pod capability', range_km: 80 },
      ],
      weapons: [
        { name: 'PL-15', type: 'BVR AAM', range_km: 200, seeker: 'AESA ARH' },
        { name: 'PL-12', type: 'BVR AAM', range_km: 100, seeker: 'Active Radar' },
        { name: 'PL-10', type: 'WVR AAM', range_km: 20, seeker: 'Imaging IR' },
      ],
      detectionScenarios: [
        { id: 'j10c_headon', name: 'Head-On (AWACS Cued)', description: 'J-10C vectored by KJ-500, radar search in narrow sector', f35_aspect: '0° (nose-on)', range_km: 130, detection_probability: 0.80, pl15_lock_range: 30 },
        { id: 'j10c_beam', name: 'Beam Aspect', description: 'F-35 crossing perpendicular, ESM detects sidelobe emissions', f35_aspect: '90° (beam)', range_km: 70, detection_probability: 0.55, pl15_lock_range: 35 },
        { id: 'j10c_sidelobe', name: 'Sidelobe Exploitation', description: 'Passive ESM detection of APG-81 sidelobes, no active emission', f35_aspect: '45° (quarter)', range_km: 160, detection_probability: 0.45, pl15_lock_range: 25 },
      ],
      killChain: [
        { phase: 'AWACS Cueing', time_s: 0, system: 'KJ-500 Datalink', description: 'KJ-500 detects F-35 via L/S-band, cues J-10C via datalink', range_km: 350 },
        { phase: 'ESM Confirmation', time_s: 8, system: 'Integrated EW', description: 'J-10C ESM confirms bearing from APG-81 sidelobe emissions', range_km: 200 },
        { phase: 'Radar Acquisition', time_s: 18, system: 'KLJ-7A AESA', description: 'Directed search in narrow sector from AWACS cue', range_km: 130 },
        { phase: 'Weapon Release', time_s: 30, system: 'Fire Control', description: 'PL-15 launch with datalink, AWACS provides midcourse updates', range_km: 120 },
        { phase: 'Midcourse', time_s: 70, system: 'PL-15 INS/Datalink', description: 'Missile on inertial with J-10C/AWACS datalink corrections', range_km: 60 },
        { phase: 'Terminal', time_s: 95, system: 'PL-15 AESA Seeker', description: 'Seeker acquires autonomously', range_km: 30 },
        { phase: 'Intercept', time_s: 110, system: 'Proximity Fuze', description: 'Warhead detonation', range_km: 0 },
      ],
      monteCarloResults: [
        { scenario: 'J-10C Head-On (AWACS Cued)', trials: 10000, pk: 0.28, pk_std: 0.04, meanDetectionRange: 160, meanEngagementTime: 100, histogramData: [{ bin: 0, count: 7200 }, { bin: 50, count: 300 }, { bin: 100, count: 250 }, { bin: 150, count: 400 }, { bin: 200, count: 550 }, { bin: 250, count: 600 }, { bin: 300, count: 400 }, { bin: 350, count: 200 }, { bin: 400, count: 80 }, { bin: 450, count: 20 }] },
        { scenario: 'J-10C Sidelobe Exploit', trials: 10000, pk: 0.18, pk_std: 0.05, meanDetectionRange: 180, meanEngagementTime: 120, histogramData: [{ bin: 0, count: 8200 }, { bin: 50, count: 200 }, { bin: 100, count: 180 }, { bin: 150, count: 300 }, { bin: 200, count: 400 }, { bin: 250, count: 350 }, { bin: 300, count: 220 }, { bin: 350, count: 100 }, { bin: 400, count: 40 }, { bin: 450, count: 10 }] },
        { scenario: 'J-10C Multi-Ship (2×, AWACS)', trials: 10000, pk: 0.35, pk_std: 0.04, meanDetectionRange: 200, meanEngagementTime: 90, histogramData: [{ bin: 0, count: 6500 }, { bin: 50, count: 280 }, { bin: 100, count: 320 }, { bin: 150, count: 500 }, { bin: 200, count: 700 }, { bin: 250, count: 750 }, { bin: 300, count: 500 }, { bin: 350, count: 280 }, { bin: 400, count: 130 }, { bin: 450, count: 40 }] },
      ],
      engagementGeometries: [
        {
          name: 'BVR Stand-Off (AWACS Cued)',
          description: 'J-10C launches PL-15 at max range with AWACS providing midcourse guidance, then cranks to avoid counter-fire',
          parameters: [
            { name: 'J-10C Speed', value: 1.6, unit: 'Mach' },
            { name: 'F-35 Speed', value: 1.4, unit: 'Mach' },
            { name: 'AWACS Range', value: 350, unit: 'km' },
            { name: 'Launch Range', value: 120, unit: 'km' },
            { name: 'Crank Angle', value: 70, unit: 'degrees' },
          ],
          calculation: 'J-10C launches at 120 km with AWACS cueing, immediately cranks 70° to minimize RCS exposure. AWACS maintains midcourse datalink to PL-15. J-10C non-stealth RCS (~3 m²) means F-35 detects at ~200 km, but PL-15 is already in flight.',
          result: [
            { metric: 'PL-15 TOF', value: 95, unit: 's' },
            { metric: 'J-10C RCS', value: '~3', unit: 'm²' },
            { metric: 'F-35 Detection of J-10C', value: 200, unit: 'km' },
            { metric: 'AWACS Datalink Update Rate', value: 2, unit: 'Hz' },
          ]
        },
        {
          name: 'Multi-Ship Pincer (2× J-10C)',
          description: 'Two J-10C approach from different azimuths, AWACS provides common picture, forcing F-35 to split attention',
          parameters: [
            { name: 'J-10C Separation', value: 80, unit: 'km' },
            { name: 'Target Range', value: 150, unit: 'km' },
            { name: 'Angle Spread', value: 60, unit: 'degrees' },
            { name: 'AWACS Baseline', value: 200, unit: 'km behind' },
          ],
          calculation: 'F-35 must track two threats at 60° spread. Defensive cranking against one exposes beam to the other. Combined ESM from both J-10C improves geolocation to ~5 km CEP.',
          result: [
            { metric: 'Combined Pk (salvo)', value: '0.52', unit: '' },
            { metric: 'F-35 Defensive Dilemma', value: 'Severe', unit: '' },
            { metric: 'ESM Geolocation CEP', value: 5, unit: 'km' },
            { metric: 'Time to First Shot', value: 30, unit: 's' },
          ]
        }
      ],
      implementation: {
        overview: 'J-10C simulation requires AWACS integration for realistic BVR engagement modeling. The platform is non-stealth, making autonomous detection of F-35 challenging without network support.',
        backendRequirements: [
          { name: 'Python 3.10+', description: 'Monte Carlo simulation engine', command: 'python -m pip install numpy scipy matplotlib' },
          { name: 'Redis', description: 'Real-time ESM track correlation cache', command: 'docker run -d -p 6379:6379 redis:7-alpine' },
          { name: 'PostgreSQL', description: 'Engagement scenario persistence', command: 'docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=secret postgres:15' },
        ],
        codeExample: [
          {
            language: 'python',
            title: 'J-10C Monte Carlo Simulation',
            code: `import numpy as np
from scipy.stats import lognorm, beta

def j10c_engagement_mc(trials=10000, awacs_cued=True):
    """Monte Carlo simulation for J-10C vs F-35 engagement."""
    # Detection probability (AWACS-dependent)
    p_detect = 0.80 if awacs_cued else 0.35

    # Track quality (log-normal, mean=0.85, std=0.1)
    p_track = lognorm.rvs(s=0.15, loc=0, scale=0.85, size=trials)
    p_track = np.clip(p_track, 0, 1)

    # Launch reliability
    p_launch = 0.95

    # Guidance (reduced without stealth approach)
    p_guide = 0.65 if awacs_cued else 0.50

    # Terminal phase
    p_fuze = 0.90
    p_warhead = 0.80

    # Calculate Pk per trial
    pk = (p_detect * p_track * p_launch *
          p_guide * p_fuze * p_warhead)

    return {
        'pk_mean': np.mean(pk),
        'pk_std': np.std(pk),
        'pk_95ci': np.percentile(pk, [2.5, 97.5])
    }

# Run simulation
result = j10c_engagement_mc(trials=10000, awacs_cued=True)
print(f"Pk = {result['pk_mean']:.3f} ± {result['pk_std']:.3f}")`
          }
        ],
        apiEndpoints: [
          { method: 'POST', endpoint: '/api/sim/j10c/monte-carlo', description: 'Run Monte Carlo simulation with custom parameters' },
          { method: 'GET', endpoint: '/api/platforms/j10c/sensors', description: 'Retrieve KLJ-7A radar parameters' },
          { method: 'POST', endpoint: '/api/esm/triangulate', description: 'Calculate passive geolocation from ESM bearings' },
        ],
        dataFlowSteps: [
          '1. AWACS (KJ-500) detects F-35 via L/S-band radar',
          '2. Track data transmitted to J-10C via Link-17 datalink',
          '3. J-10C ESM confirms bearing from APG-81 sidelobe emissions',
          '4. Backend correlates AWACS radar + J-10C ESM for refined track',
          '5. Fire control solution computed, PL-15 launch authorized',
          '6. Midcourse updates relayed via AWACS datalink',
          '7. Terminal engagement logged for BDA analysis',
        ],
        systemArchitecture: [],
        databaseSchemas: [],
        messageFormats: []
      }
    },
    // JF-17 Block III Thunder
    {
      id: 'jf17',
      name: 'JF-17 Block III Thunder',
      designation: 'JF-17 Blk III',
      description: 'Lightweight multirole fighter with KLJ-7A variant AESA radar (~700 T/R modules). Cost-effective BVR platform heavily dependent on AWACS cueing for engagements against 5th-gen threats.',
      sensorSuite: [
        { name: 'KLJ-7A AESA Radar', type: 'X-band AESA', detail: '~700 T/R modules, smaller aperture than J-10C', range_km: 130 },
        { name: 'Integrated EW/CM', type: 'ESM/RWR', detail: 'CM-400AKG compatible electronic warfare suite', range_km: 200 },
        { name: 'Targeting Pod', type: 'EO/IR', detail: 'WMD-7 or ASELPOD for precision targeting', range_km: 50 },
      ],
      weapons: [
        { name: 'PL-15 (Export)', type: 'BVR AAM', range_km: 180, seeker: 'AESA ARH' },
        { name: 'SD-10A', type: 'BVR AAM', range_km: 70, seeker: 'Active Radar' },
        { name: 'PL-12', type: 'BVR AAM', range_km: 100, seeker: 'Active Radar' },
      ],
      detectionScenarios: [
        { id: 'jf17_awacs_cued', name: 'AWACS-Cued Engagement', description: 'JF-17 receives targeting data from KJ-500, launches PL-15 without own-radar illumination', f35_aspect: '0° (nose-on)', range_km: 100, detection_probability: 0.70, pl15_lock_range: 25 },
        { id: 'jf17_cooperative', name: 'Cooperative Passive', description: 'Multiple JF-17s share ESM data for passive triangulation of F-35 emissions', f35_aspect: '45° (quarter)', range_km: 140, detection_probability: 0.40, pl15_lock_range: 22 },
        { id: 'jf17_autonomous', name: 'Autonomous Search', description: 'JF-17 searches independently without AWACS support', f35_aspect: '0° (nose-on)', range_km: 80, detection_probability: 0.35, pl15_lock_range: 25 },
      ],
      killChain: [
        { phase: 'AWACS Detection', time_s: 0, system: 'KJ-500 L/S-band', description: 'KJ-500 detects F-35 at extended range, generates track', range_km: 400 },
        { phase: 'Datalink Cueing', time_s: 5, system: 'Tactical Datalink', description: 'Track data transmitted to JF-17 flight via Link-17', range_km: 300 },
        { phase: 'ESM Search', time_s: 12, system: 'EW Suite', description: 'JF-17 ESM confirms F-35 bearing from radar emissions', range_km: 180 },
        { phase: 'Radar Handoff', time_s: 22, system: 'KLJ-7A', description: 'Brief radar illumination for fire-control solution', range_km: 100 },
        { phase: 'Weapon Release', time_s: 28, system: 'Fire Control', description: 'PL-15 launched with AWACS-provided midcourse data', range_km: 90 },
        { phase: 'Midcourse', time_s: 65, system: 'PL-15 Datalink', description: 'AWACS relays updates through JF-17 datalink', range_km: 45 },
        { phase: 'Terminal', time_s: 85, system: 'PL-15 Seeker', description: 'Autonomous terminal homing', range_km: 25 },
      ],
      monteCarloResults: [
        { scenario: 'JF-17 AWACS-Cued', trials: 10000, pk: 0.22, pk_std: 0.05, meanDetectionRange: 140, meanEngagementTime: 110, histogramData: [{ bin: 0, count: 7800 }, { bin: 50, count: 220 }, { bin: 100, count: 200 }, { bin: 150, count: 350 }, { bin: 200, count: 450 }, { bin: 250, count: 400 }, { bin: 300, count: 280 }, { bin: 350, count: 150 }, { bin: 400, count: 120 }, { bin: 450, count: 30 }] },
        { scenario: 'JF-17 Cooperative (4-ship)', trials: 10000, pk: 0.30, pk_std: 0.04, meanDetectionRange: 170, meanEngagementTime: 95, histogramData: [{ bin: 0, count: 7000 }, { bin: 50, count: 250 }, { bin: 100, count: 280 }, { bin: 150, count: 450 }, { bin: 200, count: 600 }, { bin: 250, count: 620 }, { bin: 300, count: 420 }, { bin: 350, count: 230 }, { bin: 400, count: 110 }, { bin: 450, count: 40 }] },
        { scenario: 'JF-17 Autonomous', trials: 10000, pk: 0.10, pk_std: 0.03, meanDetectionRange: 100, meanEngagementTime: 130, histogramData: [{ bin: 0, count: 9000 }, { bin: 50, count: 180 }, { bin: 100, count: 200 }, { bin: 150, count: 250 }, { bin: 200, count: 180 }, { bin: 250, count: 100 }, { bin: 300, count: 60 }, { bin: 350, count: 20 }, { bin: 400, count: 10 }, { bin: 450, count: 0 }] },
      ],
      engagementGeometries: [
        {
          name: 'AWACS-Dependent BVR',
          description: 'JF-17 relies entirely on KJ-500 for detection and midcourse guidance, minimizing own emissions',
          parameters: [
            { name: 'JF-17 Speed', value: 1.4, unit: 'Mach' },
            { name: 'AWACS Orbit Range', value: 300, unit: 'km behind' },
            { name: 'Datalink Latency', value: 1.5, unit: 's' },
            { name: 'Launch Range', value: 90, unit: 'km' },
          ],
          calculation: 'JF-17 flies toward AWACS-designated target, brief radar burst for fire-control quality track, launches PL-15. AWACS maintains midcourse guidance. JF-17 RCS (~5 m²) detected by F-35 at ~250 km — must launch before F-35 counter-fires.',
          result: [
            { metric: 'JF-17 RCS', value: '~5', unit: 'm²' },
            { metric: 'F-35 Detection of JF-17', value: 250, unit: 'km' },
            { metric: 'Available Engagement Window', value: 45, unit: 's' },
            { metric: 'AWACS Dependency', value: 'Critical', unit: '' },
          ]
        },
        {
          name: 'Cooperative 4-Ship Swarm',
          description: 'Four JF-17s at wide spacing share ESM data via datalink, creating distributed sensor network for passive geolocation',
          parameters: [
            { name: 'Formation Spread', value: 120, unit: 'km' },
            { name: 'ESM Baseline', value: 80, unit: 'km' },
            { name: 'Target Range', value: 180, unit: 'km' },
            { name: 'Simultaneous Launches', value: 4, unit: 'missiles' },
          ],
          calculation: '4-ship spread provides 80 km ESM baseline. Passive triangulation CEP ~8 km. Salvo of 4× PL-15 with AWACS midcourse improves cumulative Pk. F-35 must defend against 4 inbound missiles from different azimuths.',
          result: [
            { metric: 'Passive Geolocation CEP', value: 8, unit: 'km' },
            { metric: 'Salvo Pk (4 missiles)', value: '0.59', unit: '' },
            { metric: 'F-35 Defensive Load', value: '4 simultaneous threats', unit: '' },
            { metric: 'Cost Ratio', value: 'Favorable', unit: '(4× JF-17 < 1× F-35)' },
          ]
        }
      ],
      implementation: {
        overview: 'JF-17 simulation focuses on cooperative engagement tactics and swarm coordination. The platform is highly AWACS-dependent for 5th-gen threat engagement, making network simulation critical.',
        backendRequirements: [
          { name: 'Python 3.10+', description: 'Swarm coordination simulation', command: 'python -m pip install numpy scipy simpy networkx' },
          { name: 'RabbitMQ', description: 'Distributed datalink message broker', command: 'docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management' },
          { name: 'InfluxDB', description: 'Time-series track data storage', command: 'docker run -d -p 8086:8086 influxdb:2.7' },
        ],
        codeExample: [
          {
            language: 'python',
            title: 'JF-17 Cooperative Swarm Simulation',
            code: `import numpy as np
from dataclasses import dataclass
from typing import List

@dataclass
class JF17Node:
    id: int
    position: np.ndarray  # [x, y, z] km
    esm_bearing: float    # degrees
    esm_snr: float        # dB

def cooperative_geolocation(nodes: List[JF17Node]) -> dict:
    """Calculate target position from distributed ESM bearings."""
    if len(nodes) < 2:
        raise ValueError("Minimum 2 nodes for triangulation")

    # Convert bearings to unit vectors
    bearings = []
    positions = []
    for node in nodes:
        rad = np.radians(node.esm_bearing)
        bearings.append([np.sin(rad), np.cos(rad)])
        positions.append(node.position[:2])

    bearings = np.array(bearings)
    positions = np.array(positions)

    # Least-squares intersection
    A = np.column_stack([-bearings[:, 1], bearings[:, 0]])
    b = (positions * A).sum(axis=1)

    # Solve for target position
    target_pos, residuals, _, _ = np.linalg.lstsq(
        bearings @ bearings.T, bearings @ b, rcond=None
    )

    # CEP from residuals (simplified)
    cep_km = np.sqrt(np.mean(residuals)) if len(residuals) > 0 else 8.0

    return {
        'target_position': target_pos,
        'cep_km': cep_km,
        'nodes_used': len(nodes)
    }

# Example: 4-ship formation
nodes = [
    JF17Node(1, np.array([0, 0, 10]), 45.2, 12),
    JF17Node(2, np.array([80, 0, 10]), 32.8, 10),
    JF17Node(3, np.array([40, 60, 10]), 28.5, 14),
    JF17Node(4, np.array([120, 40, 10]), 18.3, 11),
]
result = cooperative_geolocation(nodes)
print(f"Target at {result['target_position']} CEP={result['cep_km']:.1f}km")`
          }
        ],
        apiEndpoints: [
          { method: 'POST', endpoint: '/api/sim/jf17/swarm', description: 'Simulate N-ship cooperative engagement' },
          { method: 'POST', endpoint: '/api/esm/fusion', description: 'Fuse ESM data from multiple JF-17 nodes' },
          { method: 'GET', endpoint: '/api/datalink/status', description: 'Query Link-17 network health' },
          { method: 'POST', endpoint: '/api/weapons/salvo', description: 'Coordinate multi-aircraft PL-15 launch' },
        ],
        dataFlowSteps: [
          '1. AWACS provides initial wide-area detection of F-35',
          '2. JF-17 formation receives target bearing via datalink',
          '3. Each JF-17 ESM independently measures bearing to F-35 emissions',
          '4. ESM bearings fused in real-time via mesh datalink',
          '5. Cooperative geolocation algorithm computes target CEP',
          '6. Formation coordinates simultaneous PL-15 launch',
          '7. AWACS provides midcourse guidance to all missiles',
          '8. Multi-azimuth terminal attack overwhelms F-35 defenses',
        ],
        systemArchitecture: [],
        databaseSchemas: [],
        messageFormats: []
      }
    },
    // AWACS Platforms
    {
      id: 'awacs',
      name: 'AWACS (KJ-500 / KJ-2000)',
      designation: 'KJ-500/KJ-2000',
      description: 'Airborne early warning and control platforms providing long-range detection, tracking, and battle management. Not a shooter — serves as cueing and command platform for J-10C/JF-17/J-20 fighters.',
      sensorSuite: [
        { name: 'KJ-500 3-Panel AESA', type: 'L/S-band Fixed AESA', detail: '3 fixed electronically-scanned arrays, 360° coverage, no rotating antenna', range_km: 470 },
        { name: 'KJ-2000 Rotodome AESA', type: 'S-band AESA Rotodome', detail: 'Fixed phased array within rotating dome, wide-area surveillance', range_km: 400 },
        { name: 'ESM/ELINT Suite', type: 'Passive Collection', detail: 'Wide-spectrum passive electronic intelligence, acts as relay for fighter ESM data', range_km: 500 },
      ],
      weapons: [], // AWACS is not armed
      detectionScenarios: [
        { id: 'awacs_primary', name: 'AWACS Primary Sensor', description: 'KJ-500 L/S-band detection of F-35 exploiting reduced stealth at lower frequencies', f35_aspect: '0° (nose-on)', range_km: 250, detection_probability: 0.85, pl15_lock_range: 0 },
        { id: 'awacs_esm_relay', name: 'Passive ESM Relay', description: 'AWACS collects F-35 APG-81 emissions and relays bearing/frequency data to fighters', f35_aspect: '45° (quarter)', range_km: 350, detection_probability: 0.75, pl15_lock_range: 0 },
        { id: 'awacs_track_maint', name: 'Track Maintenance', description: 'AWACS maintains continuous track on F-35 even during fighter sensor gaps', f35_aspect: 'All aspects', range_km: 300, detection_probability: 0.90, pl15_lock_range: 0 },
      ],
      killChain: [
        // AWACS cueing timeline (not a kill chain — it's a cueing chain)
        { phase: 'Initial Detection', time_s: 0, system: 'KJ-500 L/S-band', description: 'F-35 detected at reduced RCS via lower-frequency radar', range_km: 470 },
        { phase: 'Track Formation', time_s: 3, system: 'Track Processor', description: 'Automated track initiation, classification as 5th-gen fighter', range_km: 400 },
        { phase: 'ESM Correlation', time_s: 8, system: 'ESM/ELINT', description: 'Passive emissions correlated with radar track for ID confirmation', range_km: 350 },
        { phase: 'Fighter Cueing', time_s: 10, system: 'Tactical Datalink', description: 'Target data transmitted to J-10C/JF-17/J-20 via datalink', range_km: 350 },
        { phase: 'Midcourse Support', time_s: 40, system: 'Datalink Relay', description: 'AWACS provides midcourse guidance updates to PL-15 via fighter relay', range_km: 200 },
        { phase: 'Track Update', time_s: 60, system: 'KJ-500 Radar', description: 'Continuous track updates as missile approaches terminal phase', range_km: 100 },
        { phase: 'BDA Assessment', time_s: 120, system: 'All Sensors', description: 'Battle damage assessment via radar and ESM status change', range_km: 300 },
      ],
      monteCarloResults: [
        // AWACS contribution measured as cueing effectiveness
        { scenario: 'AWACS + J-20 (Networked)', trials: 10000, pk: 0.48, pk_std: 0.03, meanDetectionRange: 280, meanEngagementTime: 80, histogramData: [{ bin: 0, count: 5200 }, { bin: 50, count: 280 }, { bin: 100, count: 380 }, { bin: 150, count: 650 }, { bin: 200, count: 900 }, { bin: 250, count: 1000 }, { bin: 300, count: 700 }, { bin: 350, count: 500 }, { bin: 400, count: 280 }, { bin: 450, count: 110 }] },
        { scenario: 'AWACS + 2× J-10C', trials: 10000, pk: 0.38, pk_std: 0.04, meanDetectionRange: 250, meanEngagementTime: 90, histogramData: [{ bin: 0, count: 6200 }, { bin: 50, count: 260 }, { bin: 100, count: 320 }, { bin: 150, count: 520 }, { bin: 200, count: 720 }, { bin: 250, count: 780 }, { bin: 300, count: 550 }, { bin: 350, count: 350 }, { bin: 400, count: 220 }, { bin: 450, count: 80 }] },
        { scenario: 'AWACS + 4× JF-17', trials: 10000, pk: 0.42, pk_std: 0.04, meanDetectionRange: 260, meanEngagementTime: 85, histogramData: [{ bin: 0, count: 5800 }, { bin: 50, count: 270 }, { bin: 100, count: 350 }, { bin: 150, count: 580 }, { bin: 200, count: 800 }, { bin: 250, count: 860 }, { bin: 300, count: 600 }, { bin: 350, count: 400 }, { bin: 400, count: 240 }, { bin: 450, count: 100 }] },
      ],
      engagementGeometries: [
        {
          name: 'Standoff Orbit (KJ-500)',
          description: 'KJ-500 orbits 300-400 km behind fighter screen, provides continuous wide-area surveillance and targeting data',
          parameters: [
            { name: 'Orbit Altitude', value: 9000, unit: 'm' },
            { name: 'Orbit Distance', value: 350, unit: 'km behind FEBA' },
            { name: 'Radar Range (vs F-35)', value: 250, unit: 'km' },
            { name: 'Datalink Range', value: 500, unit: 'km' },
          ],
          calculation: 'At 9 km altitude, radar horizon = 380 km. F-35 stealth reduces detection to ~250 km at L/S-band. KJ-500 stays outside F-35 weapon range (PL-15 cannot reach at 350 km standoff). Provides 360° coverage via 3 fixed AESA panels.',
          result: [
            { metric: 'Radar Horizon', value: 380, unit: 'km' },
            { metric: 'F-35 Detection Range', value: 250, unit: 'km (L/S-band)' },
            { metric: 'Survivability', value: 'High', unit: '(outside weapon range)' },
            { metric: 'Coverage', value: '360°', unit: 'continuous' },
          ]
        },
        {
          name: 'Cooperative Network (AWACS + Mixed Fighters)',
          description: 'KJ-500 acts as sensor fusion node for mixed J-20/J-10C/JF-17 force, enabling shoot-look-shoot tactics',
          parameters: [
            { name: 'Fighter Mix', value: 2, unit: 'J-20 + 4× J-10C + 4× JF-17' },
            { name: 'Network Latency', value: 0.8, unit: 's' },
            { name: 'Sensor Fusion', value: 6, unit: 'ESM + radar inputs' },
            { name: 'Simultaneous Tracks', value: 100, unit: 'targets' },
          ],
          calculation: 'AWACS fuses data from all platforms. J-20 provides stealth forward sensor. J-10C provides mid-tier radar/ESM. JF-17 provides volume fire. Combined network achieves 2-5 km CEP on F-35 targets at 200+ km.',
          result: [
            { metric: 'Network Geolocation CEP', value: '2-5', unit: 'km' },
            { metric: 'Total Missile Salvo', value: 20, unit: 'PL-15' },
            { metric: 'Pk (Networked Salvo)', value: '0.85+', unit: '' },
            { metric: 'F-35 Countermeasure Load', value: 'Overwhelmed', unit: '' },
          ]
        }
      ],
      implementation: {
        overview: 'AWACS (KJ-500) is the backbone of the kill web. Implementation requires robust sensor fusion, multi-source track correlation, and high-bandwidth datalink simulation.',
        backendRequirements: [
          { name: 'Python 3.10+', description: 'Sensor fusion and track management', command: 'python -m pip install numpy scipy filterpy pykalman' },
          { name: 'Apache Kafka', description: 'High-throughput track data streaming', command: 'docker-compose up -d kafka zookeeper' },
          { name: 'TimescaleDB', description: 'Time-series track history with hypertables', command: 'docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=secret timescale/timescaledb:latest-pg15' },
          { name: 'Kubernetes', description: 'Distributed simulation orchestration', command: 'minikube start --cpus 4 --memory 8192' },
        ],
        codeExample: [
          {
            language: 'python',
            title: 'AWACS Multi-Source Track Fusion (Extended Kalman Filter)',
            code: `import numpy as np
from filterpy.kalman import ExtendedKalmanFilter
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class SensorMeasurement:
    source: str          # 'kj500_radar', 'j20_esm', 'j10c_radar', etc.
    timestamp: float     # seconds
    measurement: np.ndarray  # [range, azimuth, elevation] or [azimuth] for ESM
    covariance: np.ndarray   # measurement noise covariance

class AWACSTrackFusion:
    """Multi-source track fusion for KJ-500 AWACS."""

    def __init__(self, track_id: str):
        self.track_id = track_id
        # State: [x, y, z, vx, vy, vz]
        self.ekf = ExtendedKalmanFilter(dim_x=6, dim_z=3)
        self.ekf.x = np.zeros(6)
        self.ekf.P = np.eye(6) * 1000  # Initial uncertainty
        self.ekf.Q = np.eye(6) * 0.1   # Process noise

    def process_measurement(self, meas: SensorMeasurement) -> dict:
        """Process incoming sensor measurement."""
        # Predict to measurement time
        dt = meas.timestamp - getattr(self, 'last_time', meas.timestamp)
        self.last_time = meas.timestamp

        if dt > 0:
            F = self._state_transition(dt)
            self.ekf.predict(F=F)

        # Update based on measurement type
        if 'radar' in meas.source:
            # Full range/azimuth/elevation measurement
            H = self._radar_jacobian()
            self.ekf.update(meas.measurement, HJacobian=lambda x: H,
                          Hx=self._radar_measurement_fn, R=meas.covariance)
        elif 'esm' in meas.source:
            # Bearing-only measurement
            H = self._esm_jacobian()
            z = meas.measurement[0:1]  # Azimuth only
            R = meas.covariance[0:1, 0:1]
            self.ekf.update(z, HJacobian=lambda x: H,
                          Hx=self._esm_measurement_fn, R=R)

        # Calculate track quality (CEP from covariance)
        pos_cov = self.ekf.P[0:3, 0:3]
        cep = 0.589 * np.sqrt(np.trace(pos_cov[0:2, 0:2]))

        return {
            'track_id': self.track_id,
            'position': self.ekf.x[0:3].tolist(),
            'velocity': self.ekf.x[3:6].tolist(),
            'cep_km': cep,
            'quality': 'WEAPONS' if cep < 5 else 'CUEING'
        }

    def _state_transition(self, dt: float) -> np.ndarray:
        F = np.eye(6)
        F[0, 3] = F[1, 4] = F[2, 5] = dt
        return F

    def _radar_jacobian(self) -> np.ndarray:
        # Simplified Jacobian for radar measurement
        return np.eye(3, 6)

    def _esm_jacobian(self) -> np.ndarray:
        # Bearing-only Jacobian
        x, y = self.ekf.x[0], self.ekf.x[1]
        r2 = x**2 + y**2
        return np.array([[-y/r2, x/r2, 0, 0, 0, 0]])

    def _radar_measurement_fn(self, x):
        return x[0:3]

    def _esm_measurement_fn(self, x):
        return np.array([np.arctan2(x[0], x[1])])

# Example usage
tracker = AWACSTrackFusion('TRK-001')
measurements = [
    SensorMeasurement('kj500_radar', 0.0,
                     np.array([250, 0.45, 0.1]), np.diag([4, 0.01, 0.01])),
    SensorMeasurement('j20_esm', 0.5,
                     np.array([0.43]), np.diag([0.02])),
    SensorMeasurement('kj500_radar', 1.0,
                     np.array([248, 0.44, 0.1]), np.diag([4, 0.01, 0.01])),
]
for m in measurements:
    result = tracker.process_measurement(m)
    print(f"[{m.source}] CEP={result['cep_km']:.2f}km Quality={result['quality']}")`
          }
        ],
        apiEndpoints: [
          { method: 'POST', endpoint: '/api/awacs/track/init', description: 'Initialize new track from radar detection' },
          { method: 'PUT', endpoint: '/api/awacs/track/{id}/update', description: 'Process sensor measurement for track update' },
          { method: 'GET', endpoint: '/api/awacs/tracks', description: 'List all active tracks with quality metrics' },
          { method: 'POST', endpoint: '/api/awacs/datalink/broadcast', description: 'Broadcast track data to fighter network' },
          { method: 'POST', endpoint: '/api/awacs/fusion/correlate', description: 'Correlate tracks from multiple sensors' },
        ],
        dataFlowSteps: [
          '1. KJ-500 L/S-band radar detects target, initiates track',
          '2. Track processor assigns ID and creates EKF state',
          '3. ESM suite correlates emissions with radar track',
          '4. Fighter ESM bearings received via datalink (J-20, J-10C, JF-17)',
          '5. Multi-source fusion updates track state and CEP',
          '6. Track quality assessed: CUEING (>5 km CEP) or WEAPONS (<5 km CEP)',
          '7. Weapons-quality tracks broadcast to shooters via tactical datalink',
          '8. Midcourse guidance computed and transmitted to PL-15 via fighter relay',
          '9. Post-engagement BDA from track status change or loss',
        ],
        systemArchitecture: [],
        databaseSchemas: [],
        messageFormats: []
      }
    }
  ]);

  // Computed: active platform data
  readonly activePlatformData = computed<AircraftPlatform | null>(() => {
    const id = this.selectedPlatform();
    if (id === 'j20') return null; // J-20 uses the existing inline data
    return this.platforms().find(p => p.id === id) || null;
  });

  // Computed: platform detection scenarios (returns active platform or J-20 default)
  readonly activeDetectionScenarios = computed(() => {
    const platform = this.activePlatformData();
    return platform ? platform.detectionScenarios : this.detectionScenarios();
  });

  readonly activeKillChain = computed(() => {
    const platform = this.activePlatformData();
    return platform ? platform.killChain : this.killChainSteps();
  });

  readonly activeMonteCarloResults = computed(() => {
    const platform = this.activePlatformData();
    return platform ? platform.monteCarloResults : this.monteCarloResults();
  });

  readonly activeEngagementGeometries = computed(() => {
    const platform = this.activePlatformData();
    return platform ? platform.engagementGeometries : this.engagementGeometries();
  });

  // J-20 default implementation (used when J-20 selected, since activePlatformData returns null)
  readonly j20Implementation = signal<PlatformImplementation>({
    overview: 'J-20 Mighty Dragon is the primary 5th-generation stealth fighter for sidelobe exploitation. Implementation requires ESM signal processing, passive geolocation algorithms, and PL-15 fire control integration.',
    backendRequirements: [
      { name: 'Python 3.10+', description: 'Core simulation engine with NumPy/SciPy', command: 'python -m pip install numpy scipy matplotlib pandas' },
      { name: 'Redis', description: 'Real-time ESM pulse deinterleaving cache', command: 'docker run -d -p 6379:6379 redis:7-alpine' },
      { name: 'PostgreSQL + PostGIS', description: 'Geospatial track storage', command: 'docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=secret postgis/postgis:15-3.3' },
      { name: 'FastAPI', description: 'REST API for simulation control', command: 'python -m pip install fastapi uvicorn' },
    ],
    codeExample: [
      {
        language: 'python',
        title: 'J-20 ESM Sidelobe Detection Simulation',
        code: `import numpy as np
from scipy import signal
from dataclasses import dataclass

@dataclass
class APG81Emission:
    """Represents F-35 APG-81 radar emission parameters."""
    frequency_ghz: float = 10.0      # X-band center
    peak_power_kw: float = 20.0
    mainlobe_gain_dbi: float = 35.1
    sidelobe_level_db: float = -25.0
    beamwidth_deg: float = 2.5

@dataclass
class J20ESM:
    """J-20 ESM receiver parameters."""
    sensitivity_dbm: float = -65.0
    frequency_range: tuple = (2.0, 18.0)  # GHz
    aoa_accuracy_deg: float = 2.0

def calculate_esm_detection_range(
    apg81: APG81Emission,
    j20_esm: J20ESM,
    aspect_angle_deg: float
) -> float:
    """Calculate ESM detection range based on F-35 aspect angle."""
    # Determine gain at aspect angle
    if abs(aspect_angle_deg) < apg81.beamwidth_deg / 2:
        # Mainlobe
        gain_db = apg81.mainlobe_gain_dbi
    elif abs(aspect_angle_deg) < 15:
        # First sidelobe region
        gain_db = apg81.mainlobe_gain_dbi + apg81.sidelobe_level_db
    else:
        # Far sidelobes (additional 10-20 dB suppression)
        gain_db = apg81.mainlobe_gain_dbi + apg81.sidelobe_level_db - 10

    # One-way range equation (ESM advantage)
    # R_esm = sqrt(P_t * G_t * lambda^2 / (4*pi * S_min))
    wavelength_m = 3e8 / (apg81.frequency_ghz * 1e9)
    power_w = apg81.peak_power_kw * 1000
    gain_linear = 10 ** (gain_db / 10)
    sensitivity_w = 10 ** ((j20_esm.sensitivity_dbm - 30) / 10)

    range_m = np.sqrt(
        power_w * gain_linear * wavelength_m**2 /
        (4 * np.pi * sensitivity_w)
    )

    # Apply practical losses (atmospheric, duty cycle, processing)
    practical_loss_db = 15
    range_km = range_m / 1000 / 10**(practical_loss_db/20)

    return range_km

# Run detection analysis
apg81 = APG81Emission()
j20_esm = J20ESM()

for aspect in [0, 15, 45, 90]:
    range_km = calculate_esm_detection_range(apg81, j20_esm, aspect)
    print(f"Aspect {aspect:3d}° → ESM detection: {range_km:.0f} km")`
      },
      {
        language: 'typescript',
        title: 'Angular Service for Simulation API',
        code: `import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface SimulationParams {
  platform: 'j20' | 'j10c' | 'jf17' | 'awacs';
  trials: number;
  scenario: string;
  f35_emcon: boolean;
}

interface SimulationResult {
  pk_mean: number;
  pk_std: number;
  detection_range_km: number;
  engagement_time_s: number;
  histogram: { bin: number; count: number }[];
}

@Injectable({ providedIn: 'root' })
export class SidelobeSimulationService {
  private http = inject(HttpClient);
  private apiUrl = '/api/sim';

  runMonteCarlo(params: SimulationParams): Observable<SimulationResult> {
    return this.http.post<SimulationResult>(
      \`\${this.apiUrl}/\${params.platform}/monte-carlo\`,
      params
    );
  }

  getESMDetectionRange(aspectAngle: number): Observable<number> {
    return this.http.get<number>(
      \`\${this.apiUrl}/esm/range?aspect=\${aspectAngle}\`
    );
  }
}`
      }
    ],
    apiEndpoints: [
      { method: 'POST', endpoint: '/api/sim/j20/monte-carlo', description: 'Run J-20 vs F-35 Monte Carlo simulation' },
      { method: 'GET', endpoint: '/api/esm/range', description: 'Calculate ESM detection range for given aspect' },
      { method: 'POST', endpoint: '/api/esm/deinterleave', description: 'Process raw ESM PDWs and extract emitter tracks' },
      { method: 'POST', endpoint: '/api/geolocation/tdoa', description: 'Compute TDOA-based geolocation from multi-platform data' },
      { method: 'GET', endpoint: '/api/platforms/j20/sensors', description: 'Retrieve J-20 sensor suite parameters' },
    ],
    dataFlowSteps: [
      '1. ESM receiver detects F-35 APG-81 sidelobe emissions',
      '2. Pulse Descriptor Words (PDWs) generated: TOA, PW, PA, RF, AOA',
      '3. Deinterleaver separates multiple emitter signals',
      '4. Emitter identified as AN/APG-81 (F-35) via parametric matching',
      '5. Track file initiated with bearing and signal strength',
      '6. IRST cued to ESM bearing for passive confirmation',
      '7. Multi-sensor fusion (ESM + IRST + L-band) refines track',
      '8. Fire control solution computed when CEP < 5 km',
      '9. PL-15 launched with datalink for midcourse updates',
    ],
    systemArchitecture: [],
    databaseSchemas: [],
    messageFormats: []
  });

  readonly activeImplementation = computed<PlatformImplementation | null>(() => {
    const id = this.selectedPlatform();
    if (id === 'j20') return this.j20Implementation();
    const platform = this.platforms().find(p => p.id === id);
    return platform?.implementation || null;
  });

  // Comparison data for all platforms
  readonly platformComparison = computed<{ id: PlatformId; name: string; radar: string; radarRange: number; esmRange: number; pk: number; stealth: boolean; trModules: number }[]>(() => [
    { id: 'j20' as PlatformId, name: 'J-20', radar: 'Type 1475', radarRange: 180, esmRange: 250, pk: 0.32, stealth: true, trModules: 2000 },
    { id: 'j10c' as PlatformId, name: 'J-10C', radar: 'KLJ-7A', radarRange: 170, esmRange: 250, pk: 0.28, stealth: false, trModules: 1000 },
    { id: 'jf17' as PlatformId, name: 'JF-17 Blk III', radar: 'KLJ-7A', radarRange: 130, esmRange: 200, pk: 0.22, stealth: false, trModules: 700 },
    { id: 'awacs' as PlatformId, name: 'KJ-500', radar: '3-Panel AESA', radarRange: 470, esmRange: 500, pk: 0, stealth: false, trModules: 0 },
  ]);

  ngOnInit(): void {
    // Initialize component
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.drawRadarPattern();
      this.drawDetectionEnvelope();
      this.drawKillChainTimeline();
      this.drawMonteCarloChart();
      this.drawSignalProcessingFlow();
      this.drawPlatformComparisonChart();
    }, 100);
  }

  private drawRadarPattern(): void {
    if (!this.radarPatternChart?.nativeElement) return;

    const container = this.radarPatternChart.nativeElement;
    const width = 600;
    const height = 400;
    const margin = { top: 40, right: 40, bottom: 50, left: 60 };

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`);

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const data = this.sidelobePattern();

    // Scales
    const x = d3.scaleLinear()
      .domain([-90, 90])
      .range([0, innerWidth]);

    const y = d3.scaleLinear()
      .domain([-60, 0])
      .range([innerHeight, 0]);

    // Grid lines
    g.append('g')
      .attr('class', 'grid')
      .selectAll('line')
      .data([-50, -40, -30, -20, -10, 0])
      .join('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', d => y(d))
      .attr('y2', d => y(d))
      .attr('stroke', '#1a3a5c')
      .attr('stroke-dasharray', '3,3');

    // Area fill
    const area = d3.area<SidelobeLevel>()
      .x(d => x(d.angle))
      .y0(innerHeight)
      .y1(d => y(d.level_dB))
      .curve(d3.curveMonotoneX);

    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', 'patternGradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '0%')
      .attr('y2', '100%');

    gradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#c9a227')
      .attr('stop-opacity', 0.8);

    gradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#c9a227')
      .attr('stop-opacity', 0.1);

    g.append('path')
      .datum(data)
      .attr('fill', 'url(#patternGradient)')
      .attr('d', area);

    // Line
    const line = d3.line<SidelobeLevel>()
      .x(d => x(d.angle))
      .y(d => y(d.level_dB))
      .curve(d3.curveMonotoneX);

    g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#c9a227')
      .attr('stroke-width', 2)
      .attr('d', line);

    // Sidelobe level annotations
    g.append('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', y(-25))
      .attr('y2', y(-25))
      .attr('stroke', '#e74c3c')
      .attr('stroke-dasharray', '5,5')
      .attr('stroke-width', 1.5);

    g.append('text')
      .attr('x', innerWidth - 10)
      .attr('y', y(-25) - 5)
      .attr('text-anchor', 'end')
      .attr('fill', '#e74c3c')
      .attr('font-size', '11px')
      .text('First Sidelobe Level (-25 dB)');

    // Axes
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x).tickValues([-90, -60, -30, 0, 30, 60, 90]))
      .selectAll('text').attr('fill', '#95a5a6');

    g.append('g')
      .call(d3.axisLeft(y).tickValues([0, -10, -20, -30, -40, -50, -60]))
      .selectAll('text').attr('fill', '#95a5a6');

    // Labels
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', height - 10)
      .attr('text-anchor', 'middle')
      .attr('fill', '#95a5a6')
      .attr('font-size', '12px')
      .text('Angle from Boresight (degrees)');

    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('fill', '#95a5a6')
      .attr('font-size', '12px')
      .text('Relative Power (dB)');

    // Title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('fill', '#c9a227')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text('AN/APG-81 AESA Antenna Pattern (Estimated)');
  }

  private drawDetectionEnvelope(): void {
    if (!this.detectionEnvelopeChart?.nativeElement) return;

    const container = this.detectionEnvelopeChart.nativeElement;
    const size = 500;
    const center = size / 2;

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg')
      .attr('width', size)
      .attr('height', size)
      .attr('viewBox', `0 0 ${size} ${size}`);

    // Range rings
    const ranges = [50, 100, 150, 200, 250];
    const maxRange = 250;
    const scale = (center - 50) / maxRange;

    ranges.forEach(range => {
      svg.append('circle')
        .attr('cx', center)
        .attr('cy', center)
        .attr('r', range * scale)
        .attr('fill', 'none')
        .attr('stroke', '#1a3a5c')
        .attr('stroke-dasharray', '3,3');

      svg.append('text')
        .attr('x', center + 5)
        .attr('y', center - range * scale - 3)
        .attr('fill', '#95a5a6')
        .attr('font-size', '10px')
        .text(`${range} km`);
    });

    // J-20 detection envelope (irregular due to aspect-dependent detection)
    const detectionData = [];
    for (let angle = 0; angle < 360; angle += 5) {
      const rad = (angle * Math.PI) / 180;
      // Detection range varies with aspect
      let range: number;
      if (angle >= 0 && angle < 30 || angle > 330) {
        range = 180 + Math.random() * 20; // Front aspect
      } else if (angle >= 30 && angle < 150 || angle > 210 && angle <= 330) {
        range = 120 + 40 * Math.sin((angle - 90) * Math.PI / 180) + Math.random() * 15; // Side
      } else {
        range = 200 + Math.random() * 30; // Rear (larger RCS)
      }
      detectionData.push({
        x: center + range * scale * Math.sin(rad),
        y: center - range * scale * Math.cos(rad)
      });
    }

    // Detection envelope
    const line = d3.line<{x: number, y: number}>()
      .x(d => d.x)
      .y(d => d.y)
      .curve(d3.curveCardinalClosed);

    svg.append('path')
      .datum(detectionData)
      .attr('fill', 'rgba(231, 76, 60, 0.2)')
      .attr('stroke', '#e74c3c')
      .attr('stroke-width', 2)
      .attr('d', line);

    // PL-15 NEZ
    svg.append('circle')
      .attr('cx', center)
      .attr('cy', center)
      .attr('r', 150 * scale)
      .attr('fill', 'rgba(231, 76, 60, 0.1)')
      .attr('stroke', '#e74c3c')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '5,5');

    // J-20 icon at center
    svg.append('polygon')
      .attr('points', `${center},${center - 15} ${center - 8},${center + 10} ${center + 8},${center + 10}`)
      .attr('fill', '#c9a227')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1);

    // F-35 positions for scenarios
    const scenarios = this.detectionScenarios();
    scenarios.forEach((scenario, i) => {
      const angle = scenario.f35_aspect === '0° (nose-on)' ? 0 :
                    scenario.f35_aspect === '90° (beam)' ? 90 :
                    scenario.f35_aspect === '180° (tail)' ? 180 : 45;
      const rad = (angle * Math.PI) / 180;
      const r = scenario.range_km * scale;
      const x = center + r * Math.sin(rad);
      const y = center - r * Math.cos(rad);

      svg.append('polygon')
        .attr('points', `${x},${y - 8} ${x - 5},${y + 5} ${x + 5},${y + 5}`)
        .attr('fill', '#3498db')
        .attr('stroke', '#fff')
        .attr('stroke-width', 1)
        .attr('transform', `rotate(${angle + 180}, ${x}, ${y})`);

      svg.append('text')
        .attr('x', x + 12)
        .attr('y', y + 4)
        .attr('fill', '#3498db')
        .attr('font-size', '10px')
        .text(scenario.name.split(' ')[0]);
    });

    // Legend
    svg.append('text')
      .attr('x', 20)
      .attr('y', 25)
      .attr('fill', '#c9a227')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text('J-20 Detection Envelope vs F-35');

    svg.append('rect')
      .attr('x', 20)
      .attr('y', 40)
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', 'rgba(231, 76, 60, 0.2)')
      .attr('stroke', '#e74c3c');

    svg.append('text')
      .attr('x', 40)
      .attr('y', 52)
      .attr('fill', '#95a5a6')
      .attr('font-size', '11px')
      .text('Detection Envelope');

    svg.append('circle')
      .attr('cx', 27)
      .attr('cy', 72)
      .attr('r', 8)
      .attr('fill', 'none')
      .attr('stroke', '#e74c3c')
      .attr('stroke-dasharray', '2,2');

    svg.append('text')
      .attr('x', 40)
      .attr('y', 76)
      .attr('fill', '#95a5a6')
      .attr('font-size', '11px')
      .text('PL-15 NEZ (150 km)');
  }

  private drawKillChainTimeline(): void {
    if (!this.killChainChart?.nativeElement) return;

    const container = this.killChainChart.nativeElement;
    const width = 800;
    const height = 200;
    const margin = { top: 40, right: 30, bottom: 30, left: 30 };

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`);

    const steps = this.activeKillChain();
    const innerWidth = width - margin.left - margin.right;
    const stepWidth = innerWidth / steps.length;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Timeline line
    g.append('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', 60)
      .attr('y2', 60)
      .attr('stroke', '#c9a227')
      .attr('stroke-width', 3);

    // Steps
    steps.forEach((step, i) => {
      const x = i * stepWidth + stepWidth / 2;

      // Node
      g.append('circle')
        .attr('cx', x)
        .attr('cy', 60)
        .attr('r', 15)
        .attr('fill', '#0a1628')
        .attr('stroke', '#c9a227')
        .attr('stroke-width', 2);

      g.append('text')
        .attr('x', x)
        .attr('y', 65)
        .attr('text-anchor', 'middle')
        .attr('fill', '#c9a227')
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .text(i + 1);

      // Phase name
      g.append('text')
        .attr('x', x)
        .attr('y', 20)
        .attr('text-anchor', 'middle')
        .attr('fill', '#fff')
        .attr('font-size', '11px')
        .attr('font-weight', 'bold')
        .text(step.phase);

      // Time
      g.append('text')
        .attr('x', x)
        .attr('y', 95)
        .attr('text-anchor', 'middle')
        .attr('fill', '#95a5a6')
        .attr('font-size', '10px')
        .text(`T+${step.time_s}s`);

      // Range
      g.append('text')
        .attr('x', x)
        .attr('y', 110)
        .attr('text-anchor', 'middle')
        .attr('fill', '#e74c3c')
        .attr('font-size', '10px')
        .text(`${step.range_km} km`);
    });

    // Title - dynamic based on platform
    const platformNames: Record<PlatformId, string> = {
      'j20': 'J-20 → PL-15 Kill Chain vs F-35',
      'j10c': 'J-10C → PL-15 Kill Chain (AWACS Cued)',
      'jf17': 'JF-17 → PL-15 Kill Chain (AWACS Dependent)',
      'awacs': 'KJ-500 AWACS Cueing Timeline'
    };
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 20)
      .attr('text-anchor', 'middle')
      .attr('fill', '#c9a227')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text(platformNames[this.selectedPlatform()]);
  }

  selectPlatform(id: PlatformId): void {
    this.selectedPlatform.set(id);
    // Reset selected scenario when platform changes
    const scenarios = this.activeDetectionScenarios();
    if (scenarios.length > 0) {
      this.selectedScenario.set(scenarios[0].id);
    }
    // Redraw platform-specific charts
    setTimeout(() => {
      this.drawKillChainTimeline();
      this.drawMonteCarloChart();
      this.drawPlatformComparisonChart();
      if (this.selectedPlatform() === 'awacs') {
        this.drawAwacsCoverageChart();
      }
    }, 50);
  }

  selectScenario(id: string): void {
    this.selectedScenario.set(id);
  }

  getSelectedScenario(): DetectionScenario | undefined {
    return this.detectionScenarios().find(s => s.id === this.selectedScenario());
  }

  toggleFormulas(): void {
    this.showFormulas.update(v => !v);
  }

  // Calculate sidelobe detection range
  calculateSidelobeRange(mainlobeRange: number, sidelobeLevel_dB: number): number {
    const sidelobeRatio = Math.pow(10, sidelobeLevel_dB / 10);
    return mainlobeRange * Math.pow(sidelobeRatio, 0.25);
  }

  selectDerivation(id: string): void {
    this.activeDerivedSection.set(id);
  }

  selectProcessingStep(index: number): void {
    this.activeProcessingStep.set(index);
  }

  getActiveDerivation(): TechnicalDerivation | undefined {
    return this.technicalDerivations().find(d => d.id === this.activeDerivedSection());
  }

  getActiveProcessingBlock(): SignalProcessingBlock | undefined {
    return this.signalProcessingChain()[this.activeProcessingStep()];
  }

  private drawMonteCarloChart(): void {
    if (!this.monteCarloChart?.nativeElement) return;

    const container = this.monteCarloChart.nativeElement;
    const width = 700;
    const height = 350;
    const margin = { top: 40, right: 30, bottom: 60, left: 60 };

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`);

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const results = this.activeMonteCarloResults();
    const barWidth = innerWidth / results.length;
    const colors = ['#3498db', '#e74c3c', '#c9a227', '#27ae60'];

    const x = d3.scaleBand<string>()
      .domain(results.map(r => r.scenario))
      .range([0, innerWidth])
      .padding(0.3);

    const y = d3.scaleLinear()
      .domain([0, 0.5])
      .range([innerHeight, 0]);

    // Grid
    g.append('g')
      .selectAll('line')
      .data([0.1, 0.2, 0.3, 0.4, 0.5])
      .join('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', d => y(d))
      .attr('y2', d => y(d))
      .attr('stroke', '#1a3a5c')
      .attr('stroke-dasharray', '3,3');

    // Bars
    g.selectAll('.bar')
      .data(results)
      .join('rect')
      .attr('x', d => x(d.scenario) || 0)
      .attr('y', d => y(d.pk))
      .attr('width', x.bandwidth())
      .attr('height', d => innerHeight - y(d.pk))
      .attr('fill', (_, i) => colors[i])
      .attr('rx', 4);

    // Error bars
    results.forEach((r, i) => {
      const cx = (x(r.scenario) || 0) + x.bandwidth() / 2;
      g.append('line')
        .attr('x1', cx).attr('x2', cx)
        .attr('y1', y(r.pk + r.pk_std))
        .attr('y2', y(r.pk - r.pk_std))
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);

      g.append('line')
        .attr('x1', cx - 8).attr('x2', cx + 8)
        .attr('y1', y(r.pk + r.pk_std))
        .attr('y2', y(r.pk + r.pk_std))
        .attr('stroke', '#fff').attr('stroke-width', 2);

      g.append('line')
        .attr('x1', cx - 8).attr('x2', cx + 8)
        .attr('y1', y(r.pk - r.pk_std))
        .attr('y2', y(r.pk - r.pk_std))
        .attr('stroke', '#fff').attr('stroke-width', 2);

      // Pk label
      g.append('text')
        .attr('x', cx)
        .attr('y', y(r.pk) - 10)
        .attr('text-anchor', 'middle')
        .attr('fill', '#fff')
        .attr('font-size', '13px')
        .attr('font-weight', 'bold')
        .text(`${(r.pk * 100).toFixed(1)}%`);
    });

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('fill', '#95a5a6')
      .attr('font-size', '10px')
      .attr('transform', 'rotate(-15)')
      .style('text-anchor', 'end');

    // Y axis
    g.append('g')
      .call(d3.axisLeft(y).tickFormat(d => `${(+d * 100).toFixed(0)}%`))
      .selectAll('text').attr('fill', '#95a5a6');

    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('fill', '#95a5a6')
      .attr('font-size', '12px')
      .text('Single-Shot Pk');

    const mcTitles: Record<PlatformId, string> = {
      'j20': 'J-20 Monte Carlo Pk Results (N=10,000)',
      'j10c': 'J-10C Monte Carlo Pk Results (N=10,000)',
      'jf17': 'JF-17 Monte Carlo Pk Results (N=10,000)',
      'awacs': 'AWACS-Enabled Network Pk Results (N=10,000)'
    };
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('fill', '#c9a227')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text(mcTitles[this.selectedPlatform()]);
  }

  private drawSignalProcessingFlow(): void {
    if (!this.signalProcessingChart?.nativeElement) return;

    const container = this.signalProcessingChart.nativeElement;
    const width = 800;
    const height = 120;

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`);

    const steps = this.signalProcessingChain();
    const boxWidth = 105;
    const boxHeight = 50;
    const gap = (width - steps.length * boxWidth) / (steps.length + 1);
    const colors = ['#e74c3c', '#c9a227', '#3498db', '#27ae60', '#9b59b6', '#e67e22'];

    steps.forEach((step, i) => {
      const x = gap + i * (boxWidth + gap);
      const y = (height - boxHeight) / 2;

      svg.append('rect')
        .attr('x', x)
        .attr('y', y)
        .attr('width', boxWidth)
        .attr('height', boxHeight)
        .attr('fill', 'rgba(26, 42, 74, 0.8)')
        .attr('stroke', colors[i % colors.length])
        .attr('stroke-width', 2)
        .attr('rx', 6)
        .style('cursor', 'pointer');

      svg.append('text')
        .attr('x', x + boxWidth / 2)
        .attr('y', y + boxHeight / 2 + 4)
        .attr('text-anchor', 'middle')
        .attr('fill', '#fff')
        .attr('font-size', '9px')
        .attr('font-weight', 'bold')
        .text(step.name);

      // Arrow
      if (i < steps.length - 1) {
        const arrowX = x + boxWidth + 2;
        svg.append('line')
          .attr('x1', arrowX)
          .attr('x2', arrowX + gap - 4)
          .attr('y1', height / 2)
          .attr('y2', height / 2)
          .attr('stroke', '#c9a227')
          .attr('stroke-width', 2)
          .attr('marker-end', 'url(#arrowhead)');
      }
    });

    // Arrowhead marker
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 8).attr('refY', 5)
      .attr('markerWidth', 6).attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M 0 0 L 10 5 L 0 10 z')
      .attr('fill', '#c9a227');
  }

  private drawPlatformComparisonChart(): void {
    if (!this.platformComparisonChart?.nativeElement) return;

    const container = this.platformComparisonChart.nativeElement;
    const width = 700;
    const height = 300;
    const margin = { top: 40, right: 120, bottom: 60, left: 60 };

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`);

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const data = this.platformComparison();
    const metrics = ['radarRange', 'esmRange'] as const;
    const metricLabels: Record<string, string> = { radarRange: 'Radar Detection', esmRange: 'ESM Detection' };
    const colors = { radarRange: '#3498db', esmRange: '#c9a227' };

    const x0 = d3.scaleBand()
      .domain(data.map(d => d.name))
      .range([0, innerWidth])
      .padding(0.2);

    const x1 = d3.scaleBand()
      .domain(metrics)
      .range([0, x0.bandwidth()])
      .padding(0.05);

    const y = d3.scaleLinear()
      .domain([0, 550])
      .range([innerHeight, 0]);

    // Grid lines
    g.append('g')
      .selectAll('line')
      .data([100, 200, 300, 400, 500])
      .join('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', d => y(d))
      .attr('y2', d => y(d))
      .attr('stroke', '#1a3a5c')
      .attr('stroke-dasharray', '3,3');

    // Grouped bars
    const platformGroups = g.selectAll('.platform-group')
      .data(data)
      .join('g')
      .attr('class', 'platform-group')
      .attr('transform', d => `translate(${x0(d.name)},0)`);

    platformGroups.selectAll('rect')
      .data(d => metrics.map(key => ({ key, value: d[key], platform: d.name })))
      .join('rect')
      .attr('x', d => x1(d.key) || 0)
      .attr('y', d => y(d.value))
      .attr('width', x1.bandwidth())
      .attr('height', d => innerHeight - y(d.value))
      .attr('fill', d => colors[d.key])
      .attr('rx', 3);

    // Value labels
    platformGroups.selectAll('.value-label')
      .data(d => metrics.map(key => ({ key, value: d[key], platform: d.name })))
      .join('text')
      .attr('class', 'value-label')
      .attr('x', d => (x1(d.key) || 0) + x1.bandwidth() / 2)
      .attr('y', d => y(d.value) - 5)
      .attr('text-anchor', 'middle')
      .attr('fill', '#fff')
      .attr('font-size', '10px')
      .text(d => d.value > 0 ? `${d.value}` : '');

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x0))
      .selectAll('text')
      .attr('fill', '#95a5a6')
      .attr('font-size', '11px');

    // Y axis
    g.append('g')
      .call(d3.axisLeft(y).tickValues([0, 100, 200, 300, 400, 500]))
      .selectAll('text').attr('fill', '#95a5a6');

    // Y axis label
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('fill', '#95a5a6')
      .attr('font-size', '12px')
      .text('Detection Range (km)');

    // Title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 22)
      .attr('text-anchor', 'middle')
      .attr('fill', '#c9a227')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text('Platform Detection Range Comparison vs F-35');

    // Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - margin.right + 10}, ${margin.top})`);

    metrics.forEach((m, i) => {
      legend.append('rect')
        .attr('x', 0)
        .attr('y', i * 22)
        .attr('width', 14)
        .attr('height', 14)
        .attr('fill', colors[m])
        .attr('rx', 2);

      legend.append('text')
        .attr('x', 20)
        .attr('y', i * 22 + 11)
        .attr('fill', '#95a5a6')
        .attr('font-size', '11px')
        .text(metricLabels[m]);
    });
  }

  private drawAwacsCoverageChart(): void {
    if (!this.awacsCoverageChart?.nativeElement) return;

    const container = this.awacsCoverageChart.nativeElement;
    const size = 450;
    const center = size / 2;

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg')
      .attr('width', size)
      .attr('height', size)
      .attr('viewBox', `0 0 ${size} ${size}`);

    const maxRange = 500;
    const scale = (center - 50) / maxRange;

    // Range rings
    const ranges = [100, 200, 300, 400, 500];
    ranges.forEach(range => {
      svg.append('circle')
        .attr('cx', center)
        .attr('cy', center)
        .attr('r', range * scale)
        .attr('fill', 'none')
        .attr('stroke', '#1a3a5c')
        .attr('stroke-dasharray', '3,3');

      svg.append('text')
        .attr('x', center + 5)
        .attr('y', center - range * scale - 3)
        .attr('fill', '#95a5a6')
        .attr('font-size', '10px')
        .text(`${range} km`);
    });

    // KJ-500 radar coverage (L/S-band detection of F-35)
    const radarCoverage = 250; // Reduced range vs stealth
    svg.append('circle')
      .attr('cx', center)
      .attr('cy', center)
      .attr('r', radarCoverage * scale)
      .attr('fill', 'rgba(52, 152, 219, 0.15)')
      .attr('stroke', '#3498db')
      .attr('stroke-width', 2);

    // Full radar range (vs conventional target)
    svg.append('circle')
      .attr('cx', center)
      .attr('cy', center)
      .attr('r', 470 * scale)
      .attr('fill', 'none')
      .attr('stroke', '#3498db')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '5,5');

    // ESM coverage
    svg.append('circle')
      .attr('cx', center)
      .attr('cy', center)
      .attr('r', 350 * scale)
      .attr('fill', 'rgba(201, 162, 39, 0.1)')
      .attr('stroke', '#c9a227')
      .attr('stroke-width', 2);

    // Datalink range
    svg.append('circle')
      .attr('cx', center)
      .attr('cy', center)
      .attr('r', 500 * scale)
      .attr('fill', 'none')
      .attr('stroke', '#27ae60')
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '8,4');

    // KJ-500 icon at center
    svg.append('rect')
      .attr('x', center - 20)
      .attr('y', center - 8)
      .attr('width', 40)
      .attr('height', 16)
      .attr('fill', '#2c3e50')
      .attr('stroke', '#c9a227')
      .attr('stroke-width', 2)
      .attr('rx', 3);

    svg.append('ellipse')
      .attr('cx', center)
      .attr('cy', center - 12)
      .attr('rx', 18)
      .attr('ry', 6)
      .attr('fill', 'none')
      .attr('stroke', '#c9a227')
      .attr('stroke-width', 1.5);

    // Fighter positions
    const fighters = [
      { type: 'J-20', angle: 20, range: 150, color: '#e74c3c' },
      { type: 'J-10C', angle: 90, range: 180, color: '#f39c12' },
      { type: 'J-10C', angle: 150, range: 200, color: '#f39c12' },
      { type: 'JF-17', angle: 240, range: 220, color: '#9b59b6' },
      { type: 'JF-17', angle: 300, range: 190, color: '#9b59b6' },
    ];

    fighters.forEach(f => {
      const rad = (f.angle * Math.PI) / 180;
      const x = center + f.range * scale * Math.sin(rad);
      const y = center - f.range * scale * Math.cos(rad);

      svg.append('polygon')
        .attr('points', `${x},${y - 8} ${x - 5},${y + 5} ${x + 5},${y + 5}`)
        .attr('fill', f.color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1);

      svg.append('text')
        .attr('x', x + 10)
        .attr('y', y + 4)
        .attr('fill', f.color)
        .attr('font-size', '9px')
        .text(f.type);

      // Datalink line
      svg.append('line')
        .attr('x1', center)
        .attr('y1', center)
        .attr('x2', x)
        .attr('y2', y)
        .attr('stroke', '#27ae60')
        .attr('stroke-width', 1)
        .attr('stroke-dasharray', '2,2')
        .attr('opacity', 0.5);
    });

    // Title
    svg.append('text')
      .attr('x', center)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('fill', '#c9a227')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text('KJ-500 AWACS Coverage & Network');

    // Legend
    const legendData = [
      { label: 'Radar (vs F-35)', color: '#3498db', dash: '' },
      { label: 'Radar (vs conv.)', color: '#3498db', dash: '5,5' },
      { label: 'ESM Coverage', color: '#c9a227', dash: '' },
      { label: 'Datalink Range', color: '#27ae60', dash: '8,4' },
    ];

    legendData.forEach((item, i) => {
      const ly = size - 80 + i * 18;
      svg.append('line')
        .attr('x1', 15)
        .attr('x2', 35)
        .attr('y1', ly)
        .attr('y2', ly)
        .attr('stroke', item.color)
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', item.dash);

      svg.append('text')
        .attr('x', 42)
        .attr('y', ly + 4)
        .attr('fill', '#95a5a6')
        .attr('font-size', '10px')
        .text(item.label);
    });
  }
}
