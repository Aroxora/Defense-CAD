// ASBM Kill Chain — Shared Interfaces

export interface MissileSystem {
  name: string;
  designation: string;
  range_km: number | string;
  warhead: string;
  cep_m: string;
  guidance: string;
  speed: string;
  launch_platform: string;
  classification: string;
}

export interface KillChainPhase {
  phase: string;
  time_min: string;
  system: string;
  description: string;
  sensors: string[];
  vulnerabilities: string[];
}

export interface SensorNode {
  id: string;
  name: string;
  type: 'radar' | 'satellite' | 'sigint' | 'humint' | 'uav';
  range_km: number | string;
  description: string;
  coverage: string;
}

export interface CounterTargetingParam {
  name: string;
  value: string;
  unit: string;
  description: string;
}

export interface MonteCarloScenario {
  scenario: string;
  pk: number;
  pk_std: number;
  trials: number;
  description: string;
}

export interface Countermeasure {
  name: string;
  system: string;
  description: string;
  effectiveness: string;
}

export type MissileId = 'df21d' | 'df26' | 'df17';

export interface TechnicalDerivation {
  id: string;
  title: string;
  category: 'trajectory' | 'guidance' | 'terminal' | 'engagement' | 'propagation';
  equations: {
    name: string;
    latex: string;
    description: string;
    variables: { symbol: string; meaning: string; unit: string }[];
    derivation?: string[];
    numericalExample?: { inputs: Record<string, number | string>; calculation: string; result: string };
  }[];
}

export interface SignalProcessingBlock {
  name: string;
  function: string;
  inputs: string[];
  outputs: string[];
  algorithm: string;
  pseudocode: string[];
}

export interface EngagementGeometry {
  name: string;
  description: string;
  parameters: { name: string; value: number | string; unit: string }[];
  calculation: string;
  result: { metric: string; value: number | string; unit: string }[];
}

export interface MissilePlatformData {
  id: MissileId;
  name: string;
  designation: string;
  description: string;
  specs: MissileSystem;
  killChain: KillChainPhase[];
  monteCarloResults: MonteCarloScenario[];
  engagementGeometries: EngagementGeometry[];
  trajectoryProfile: { altitude_km: number; range_km: number; phase: string }[];
  subsystems: SubsystemDetail[];
}

// ─── Subsystem Deep-Dive Interfaces ──────────────────────────────────────────

export interface SpecEntry {
  name: string;
  value: string | number;
  unit?: string;
  note?: string;
}

export interface SubsystemComponent {
  name: string;
  description: string;
  specs: SpecEntry[];
  operationalNotes?: string;
}

export interface SubsystemEquation {
  name: string;
  latex: string;
  description: string;
  variables: { symbol: string; meaning: string; unit: string }[];
  numericalExample?: { inputs: Record<string, number | string>; calculation: string; result: string };
}

export interface SubsystemPseudocode {
  title: string;
  description: string;
  lines: string[];
}

export interface PerformanceMetric {
  metric: string;
  value: string | number;
  unit: string;
  context?: string;
}

export type SubsystemCategory = 'navigation' | 'seeker' | 'guidance' | 'propulsion' | 'warhead' | 'datalink' | 'isr' | 'fusion' | 'c2';

export interface SubsystemDetail {
  id: string;
  name: string;
  category: SubsystemCategory;
  icon: string;
  overview: string;
  components: SubsystemComponent[];
  performanceMetrics: PerformanceMetric[];
  equations?: SubsystemEquation[];
  pseudocode?: SubsystemPseudocode[];
  operationalNotes?: string[];
  interactionsWith?: string[];
}
