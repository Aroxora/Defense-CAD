export interface ProposedSystem {
  key: string;
  name: string;
  side: string;
  domain: string;
  status: string;
  description: string;
  unit_cost_musd: number;
  quantity: number;
  rnd_cost_musd: number;
  annual_oandm_musd: number;
  service_life_years: number;
  benefit_score: number;
  survivability_score: number;
  key_benefits: string[];
  key_risks: string[];
  sources: string[];
  confidence: number;
  last_updated: string;
  lifecycle_cost_busd: number;
  benefit_per_billion: number;
  value_index: number;
  value_ci_low: number;
  value_ci_high: number;
  uncertainty: number;
}

export interface DoctrineConcept {
  key: string;
  name_en: string;
  name_native: string;
  summary: string;
  public_sources: string[];
  related_systems: string[];
  analytical_notes: string;
  confidence: number;
}

export interface DoctrineSide {
  side: string;
  concepts: DoctrineConcept[];
  systems_to_concepts: Record<string, string[]>;
}

export interface DoctrineData {
  pla: DoctrineSide;
  dod: DoctrineSide;
}

export interface FactCheck {
  key: string;
  claim: string;
  value_used: number;
  unit: string;
  checked: string;
  sources: string[];
  status: string;
  parsed_value?: number;
  relative_delta?: number;
}

export interface FactChecks {
  generated: string;
  facts: FactCheck[];
}

export interface CadModelDerived {
  rcs_profile: {
    model: string; frequency_ghz: number; num_triangles: number;
    azimuth_deg: number[]; rcs_dbsm: number[];
    min_dbsm: number; max_dbsm: number; mean_dbsm: number; median_dbsm: number; dynamic_range_db: number;
  };
  detection_envelope: {
    model: string; frequency_ghz: number; azimuth_deg: number[];
    detection_range_km: number[]; min_range_km: number; max_range_km: number;
  };
  mesh_properties: {
    model: string; num_triangles: number; resolution: number; surface_area_m2: number;
    bbox_length_m: number; bbox_width_m: number; bbox_height_m: number;
    divergence_volume_m3: number; volume_note: string; characteristic_length_m: number;
  };
}

export type CadDerived = Record<string, CadModelDerived>;

export interface EwLoe {
  id: number;
  title: string;
  subtitle: string;
  detail: string;
}

export interface EwStrategy {
  premise: string;
  intercept_vs_dwell: { dwell_us: number; proc_gain_db: number; intercept_range_km: number }[];
  geolocation_sizing: {
    platforms: number;
    baseline_km: number;
    gdop: number | null;
    crlb_floor_m: number | null;
    ops_cep_m: number | null;
    ill_conditioned: boolean;
  }[];
  hardening_sweep: { sidelobe_db: number; sidelobe_eirp_dbm: number; adversary_intercept_km: number }[];
  reallocation: {
    jam_power_kw: number;
    range_km: number;
    js_radar_db: number;
    radar_effective: boolean;
    js_madl_db: number;
    madl_effective: boolean;
    madl_isolation_db: number;
  };
  lines_of_effort: EwLoe[];
}
