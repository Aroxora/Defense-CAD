import * as E from './engine';

export interface CalcInput {
  key: string; label: string; unit: string; min: number; max: number; default: number; step: number; log?: boolean;
}
export interface CalcResult { label: string; unit: string; value: number | null; primary?: boolean; fmt?: string; }
export interface CalcDef {
  id: string;
  title: string;
  category: string;
  equation: string;
  why: string;
  source: string;
  inputs: CalcInput[];
  compute: (v: Record<string, number>) => CalcResult[];
  chart: { xKey: string; yLabel: string; logX?: boolean; y: (x: number, v: Record<string, number>) => number };
}

const num = (v: Record<string, number>, k: string) => v[k];

export const CALCULATORS: CalcDef[] = [
  {
    id: 'radar-range-equation',
    title: 'Radar Detection Range (range equation)',
    category: 'Radar',
    source: 'osint_cad/analysis/calculators.py:radar_max_range_km (+aperture gain, scan loss)',
    equation: 'R = [ Pt·G²·λ²·σ·n / ((4π)³·k·T₀·B·F·SNR·L) ]^(1/4),  G = 4π·A·η/λ²',
    why: 'The fourth-root coupling is the single most important idea in sensing: range scales only as σ^(1/4) and Pt^(1/4). A 10× RCS cut shrinks detection range to ~56%; doubling power buys only ~19%. Sweep RCS to see why a 1000× RCS reduction shrinks detection range only ~5.6×, not 1000×.',
    inputs: [
      { key: 'sigma', label: 'Target RCS', unit: 'm²', min: 0.0001, max: 100, default: 0.0014, step: 0.0001, log: true },
      { key: 'Pt_kw', label: 'Peak transmit power', unit: 'kW', min: 5, max: 40, default: 20, step: 0.5 },
      { key: 'A', label: 'Effective aperture', unit: 'm²', min: 0.3, max: 0.7, default: 0.5, step: 0.01 },
      { key: 'eta', label: 'Aperture efficiency', unit: '-', min: 0.5, max: 0.85, default: 0.7, step: 0.01 },
      { key: 'az', label: 'Scan off-boresight', unit: 'deg', min: 0, max: 60, default: 0, step: 1 },
      { key: 'f', label: 'Frequency', unit: 'GHz', min: 8, max: 12, default: 9.5, step: 0.1 },
      { key: 'B_mhz', label: 'Bandwidth', unit: 'MHz', min: 50, max: 800, default: 400, step: 10 },
      { key: 'NF', label: 'Noise figure', unit: 'dB', min: 1.5, max: 5, default: 3, step: 0.1 },
      { key: 'SNR', label: 'Detection SNR', unit: 'dB', min: 8, max: 20, default: 13, step: 0.5 },
      { key: 'L', label: 'System losses', unit: 'dB', min: 1, max: 6, default: 3.5, step: 0.1 },
      { key: 'n', label: 'Integration pulses', unit: '-', min: 1, max: 4000, default: 1000, step: 1 },
    ],
    compute: (v) => {
      const gain = E.apertureGainDbi(v['A'], v['eta'], v['f']) + E.scanLossDb(v['az']);
      const r = E.radarMaxRangeKm(v['Pt_kw'] * 1000, gain, v['f'], v['sigma'], v['B_mhz'] * 1e6, v['NF'], v['SNR'], v['L'], v['n']);
      return [
        { label: 'Detection range', unit: 'km', value: r, primary: true },
        { label: 'Antenna gain', unit: 'dBi', value: gain },
      ];
    },
    chart: {
      xKey: 'sigma', yLabel: 'Detection range (km)', logX: true,
      y: (x, v) => {
        const gain = E.apertureGainDbi(v['A'], v['eta'], v['f']) + E.scanLossDb(v['az']);
        return E.radarMaxRangeKm(v['Pt_kw'] * 1000, gain, v['f'], x, v['B_mhz'] * 1e6, v['NF'], v['SNR'], v['L'], v['n']);
      },
    },
  },
  {
    id: 'rcs-fourth-root',
    title: 'RCS¹ᐟ⁴ Range Scaling',
    category: 'Radar',
    source: 'osint_cad/analysis/calculators.py:power_limited_range_km',
    equation: 'R = R_ref · (σ / σ_ref)^(1/4)',
    why: 'Given one calibration point (R_ref at σ_ref), predict detection range against any target. A 10 m² bomber vs a 0.005 m² stealth fighter differ only ~6.7× in range — not 2000×.',
    inputs: [
      { key: 'R_ref', label: 'Reference range', unit: 'km', min: 50, max: 600, default: 300, step: 10 },
      { key: 'sigma_ref', label: 'Reference RCS', unit: 'm²', min: 0.001, max: 10, default: 1, step: 0.001, log: true },
      { key: 'sigma', label: 'Target RCS', unit: 'm²', min: 0.0001, max: 100, default: 0.1, step: 0.0001, log: true },
    ],
    compute: (v) => [{ label: 'Power-limited range', unit: 'km', value: E.powerLimitedRangeKm(v['R_ref'], v['sigma_ref'], v['sigma']), primary: true }],
    chart: { xKey: 'sigma', yLabel: 'Range (km)', logX: true, y: (x, v) => E.powerLimitedRangeKm(v['R_ref'], v['sigma_ref'], x) },
  },
  {
    id: 'radar-horizon',
    title: 'Radar Horizon & Coverage (low-altitude gap)',
    category: 'Radar',
    source: 'osint_cad/analysis/calculators.py:effective_coverage',
    equation: 'R_horizon ≈ 4.12·(√h_radar + √h_target);  R_eff = min(R_power, R_horizon)',
    why: 'Against a sea-skimmer the horizon — not power — sets coverage. Sweep target altitude to see the low-altitude gap appear, and why closing it needs elevated/airborne/space sensors, not more power.',
    inputs: [
      { key: 'hr', label: 'Antenna height', unit: 'm', min: 5, max: 300, default: 30, step: 1 },
      { key: 'ht', label: 'Target altitude', unit: 'm', min: 5, max: 15000, default: 10, step: 5 },
      { key: 'R_ref', label: 'Power-limited ref range', unit: 'km', min: 50, max: 600, default: 300, step: 10 },
      { key: 'sigma_ref', label: 'Reference RCS', unit: 'm²', min: 0.01, max: 10, default: 1, step: 0.01, log: true },
      { key: 'sigma', label: 'Target RCS', unit: 'm²', min: 0.001, max: 100, default: 0.1, step: 0.001, log: true },
    ],
    compute: (v) => {
      const c = E.effectiveCoverage(v['hr'], v['ht'], v['R_ref'], v['sigma_ref'], v['sigma']);
      return [
        { label: 'Effective range', unit: 'km', value: c.effectiveKm, primary: true },
        { label: 'Radar horizon', unit: 'km', value: c.horizonKm },
        { label: 'Power-limited', unit: 'km', value: c.powerLimitedKm },
        { label: 'Coverage area', unit: 'km²', value: c.coverageAreaKm2 },
      ];
    },
    chart: { xKey: 'ht', yLabel: 'Effective range (km)', y: (x, v) => E.effectiveCoverage(v['hr'], x, v['R_ref'], v['sigma_ref'], v['sigma']).effectiveKm },
  },
  {
    id: 'free-space-path-loss',
    title: 'Free-Space Path Loss',
    category: 'Propagation',
    source: 'osint_cad/analysis/calculators.py:fspl_db',
    equation: 'FSPL = 20·log₁₀(4π·R/λ)',
    why: 'The baseline of every link/detection budget. Loss grows 20 dB per decade of range and rises with frequency — the reason higher bands trade range for bandwidth.',
    inputs: [
      { key: 'f', label: 'Frequency', unit: 'GHz', min: 0.1, max: 40, default: 10, step: 0.1 },
      { key: 'range_km', label: 'Range', unit: 'km', min: 1, max: 1000, default: 100, step: 1, log: true },
    ],
    compute: (v) => [{ label: 'Free-space path loss', unit: 'dB', value: E.fsplDb(v['f'], v['range_km']), primary: true }],
    chart: { xKey: 'range_km', yLabel: 'FSPL (dB)', logX: true, y: (x, v) => E.fsplDb(v['f'], x) },
  },
  {
    id: 'esm-intercept',
    title: 'Passive ESM Intercept Range',
    category: 'EW',
    source: 'osint_cad/analysis/calculators.py:friis_intercept_range_km + processing_gain_db',
    equation: 'R = λ·10^(PL/20)/(4π),  PL = EIRP − (sensitivity − G_proc),  G_proc = 10·log₁₀(B·T)',
    why: 'Illustrative LPI sidelobe case: how far a passive receiver can intercept an emitter. Longer integration dwell buys range — but against a directional, hopping LPI link intercept is opportunistic. The defensible counter is detection, not jamming.',
    inputs: [
      { key: 'eirp', label: 'Emitter EIRP', unit: 'dBm', min: 0, max: 60, default: 34.5, step: 0.5 },
      { key: 'sens', label: 'ESM sensitivity', unit: 'dBm', min: -100, max: -50, default: -74, step: 1 },
      { key: 'f', label: 'Frequency', unit: 'GHz', min: 1, max: 40, default: 14.4, step: 0.1 },
      { key: 'B_mhz', label: 'Bandwidth', unit: 'MHz', min: 1, max: 500, default: 100, step: 1 },
      { key: 'dwell_us', label: 'Integration dwell', unit: 'µs', min: 1, max: 5000, default: 100, step: 1, log: true },
    ],
    compute: (v) => {
      const g = E.processingGainDb(v['B_mhz'] * 1e6, v['dwell_us'] * 1e-6);
      return [
        { label: 'Intercept range', unit: 'km', value: E.friisInterceptRangeKm(v['eirp'], v['sens'], v['f'], g), primary: true },
        { label: 'Processing gain', unit: 'dB', value: g },
      ];
    },
    chart: {
      xKey: 'dwell_us', yLabel: 'Intercept range (km)', logX: true,
      y: (x, v) => E.friisInterceptRangeKm(v['eirp'], v['sens'], v['f'], E.processingGainDb(v['B_mhz'] * 1e6, x * 1e-6)),
    },
  },
  {
    id: 'jammer-to-signal',
    title: 'Jammer-to-Signal Ratio',
    category: 'EW',
    source: 'osint_cad/analysis/calculators.py:js_ratio_db',
    equation: 'J/S = P_jam + G_ant − PL − S_victim',
    why: 'Why standoff jamming works against a wide-open radar (+10 dB+ J/S) but not against a directional, hopping LPI link: subtract a 25 dB spatial-isolation + processing-gain penalty and the same jammer is ineffective.',
    inputs: [
      { key: 'jam_kw', label: 'Jammer power', unit: 'kW', min: 1, max: 200, default: 30, step: 1 },
      { key: 'range_km', label: 'Range', unit: 'km', min: 10, max: 400, default: 100, step: 5 },
      { key: 'victim_dbm', label: 'Victim signal', unit: 'dBm', min: -90, max: -30, default: -60, step: 1 },
      { key: 'f_ghz', label: 'Frequency', unit: 'GHz', min: 1, max: 18, default: 10, step: 0.1 },
      { key: 'ant_db', label: 'Jammer antenna gain', unit: 'dBi', min: 10, max: 45, default: 30, step: 1 },
      { key: 'iso_db', label: 'LPI isolation penalty', unit: 'dB', min: 0, max: 40, default: 25, step: 1 },
    ],
    compute: (v) => {
      const js = E.jsRatioDb(v['jam_kw'], v['range_km'], v['victim_dbm'], v['f_ghz'] * 1e9, v['ant_db']);
      return [
        { label: 'J/S vs radar', unit: 'dB', value: js, primary: true },
        { label: 'J/S vs LPI link', unit: 'dB', value: js - v['iso_db'] },
      ];
    },
    chart: { xKey: 'range_km', yLabel: 'J/S (dB)', y: (x, v) => E.jsRatioDb(v['jam_kw'], x, v['victim_dbm'], v['f_ghz'] * 1e9, v['ant_db']) },
  },
  {
    id: 'aspect-rcs',
    title: 'Aspect-Dependent RCS',
    category: 'RCS',
    source: 'osint_cad/analysis/calculators.py:aspect_rcs_m2 (illustrative)',
    equation: 'σ(θ) interpolated in dBsm across nose / beam / tail sectors',
    why: 'Stealth is shaped to be lowest head-on. Sweeping aspect shows RCS rising tens of dB toward the beam — why approach geometry dominates whether a low-observable target is detected.',
    inputs: [
      { key: 'frontal', label: 'Frontal RCS', unit: 'm²', min: 0.0001, max: 1, default: 0.0002, step: 0.0001, log: true },
      { key: 'side', label: 'Beam RCS', unit: 'm²', min: 0.01, max: 100, default: 0.05, step: 0.01, log: true },
      { key: 'rear', label: 'Tail RCS', unit: 'm²', min: 0.001, max: 10, default: 0.01, step: 0.001, log: true },
      { key: 'aspect', label: 'Aspect angle', unit: 'deg', min: 0, max: 360, default: 0, step: 1 },
    ],
    compute: (v) => {
      const r = E.aspectRcsM2(v['frontal'], v['side'], v['rear'], v['aspect']);
      return [
        { label: 'RCS', unit: 'm²', value: r, primary: true },
        { label: 'RCS', unit: 'dBsm', value: 10 * Math.log10(r) },
      ];
    },
    chart: { xKey: 'aspect', yLabel: 'RCS (dBsm)', y: (x, v) => 10 * Math.log10(E.aspectRcsM2(v['frontal'], v['side'], v['rear'], x)) },
  },
  {
    id: 'tdoa-geolocation',
    title: 'TDOA Geolocation (GDOP / CRLB)',
    category: 'EW',
    source: 'osint_cad/analysis/calculators.py:geolocation_quality',
    equation: 'GDOP = √trace((GᵀG)⁻¹);  CEP from the TDOA Cramér-Rao bound × ops-degrade',
    why: 'Turning a passive intercept into a precise track needs ≥4 synchronized platforms with good geometry. Sweep baseline to see how geometry (GDOP) and achievable CEP scale — a worked sizing study, not a build spec.',
    inputs: [
      { key: 'n', label: 'Platforms', unit: '-', min: 4, max: 10, default: 4, step: 1 },
      { key: 'baseline_km', label: 'Baseline radius', unit: 'km', min: 10, max: 200, default: 30, step: 5 },
      { key: 'timing_ns', label: 'Time sync', unit: 'ns', min: 1, max: 50, default: 10, step: 1 },
    ],
    compute: (v) => {
      const q = E.geolocationQuality(Math.round(v['n']), v['baseline_km'], v['timing_ns']);
      return [
        { label: 'Operational CEP', unit: 'm', value: q.opsCepM, primary: true },
        { label: 'GDOP', unit: '-', value: q.gdop },
        { label: 'CRLB floor', unit: 'm', value: q.crlbFloorM },
      ];
    },
    chart: { xKey: 'baseline_km', yLabel: 'Operational CEP (m)', y: (x, v) => E.geolocationQuality(Math.round(v['n']), x, v['timing_ns']).opsCepM ?? NaN },
  },
  {
    id: 'salvo-kill',
    title: 'Salvo Kill Probability & Leakage',
    category: 'Missile defense',
    source: 'osint_cad/analysis/calculators.py:md_engage',
    equation: 'P_kill = 1 − (1 − Pk)ⁿ;  leakers = unengaged + engaged·(1 − P_kill)',
    why: 'Layered shots raise kill probability fast (two 0.7 shots → 0.91), but a finite magazine caps how many of a raid you can engage. Sweep shots-per-target to see the diminishing returns vs. magazine depletion.',
    inputs: [
      { key: 'pk', label: 'Single-shot Pk', unit: '-', min: 0.2, max: 0.95, default: 0.7, step: 0.01 },
      { key: 'shots', label: 'Shots per target', unit: '-', min: 1, max: 6, default: 2, step: 1 },
      { key: 'magazine', label: 'Magazine', unit: 'interceptors', min: 4, max: 200, default: 48, step: 2 },
      { key: 'raid', label: 'Raid size', unit: 'threats', min: 1, max: 100, default: 24, step: 1 },
    ],
    compute: (v) => {
      const e = E.mdEngage(v['pk'], Math.round(v['magazine']), Math.round(v['raid']), Math.round(v['shots']));
      return [
        { label: 'Intercept fraction', unit: '', value: e.interceptFraction, primary: true, fmt: 'pct' },
        { label: 'Pk per target', unit: '', value: e.pkPerTarget },
        { label: 'Expected leakers', unit: '', value: e.expectedLeakers },
        { label: 'Targets engageable', unit: '', value: e.engageable },
      ];
    },
    chart: { xKey: 'shots', yLabel: 'Pk per target', y: (x, v) => E.killProbSalvo(v['pk'], Math.round(x)) },
  },
  {
    id: 'cost-exchange',
    title: 'Cost-Exchange Ratio (cost imposition)',
    category: 'Missile defense',
    source: 'osint_cad/analysis/calculators.py:md_exchange_ratio',
    equation: 'ratio = (shots/P_kill)·C_interceptor / C_threat',
    why: 'The defender’s dilemma: cheap mass threats can be cost-favorable to launch even when intercepted. Sweep threat unit cost to find where defense flips from unfavorable (>1) to favorable (<1).',
    inputs: [
      { key: 'pk', label: 'Single-shot Pk', unit: '-', min: 0.2, max: 0.95, default: 0.7, step: 0.01 },
      { key: 'shots', label: 'Shots per target', unit: '-', min: 1, max: 4, default: 2, step: 1 },
      { key: 'int_cost', label: 'Interceptor cost', unit: '$M', min: 0.1, max: 30, default: 4.3, step: 0.1 },
      { key: 'threat_cost', label: 'Threat cost', unit: '$M', min: 0.1, max: 50, default: 1.5, step: 0.1, log: true },
    ],
    compute: (v) => {
      const x = E.mdExchangeRatio(v['pk'], v['int_cost'], v['threat_cost'], Math.round(v['shots']));
      return [
        { label: 'Cost-exchange ratio', unit: '×', value: x.costExchangeRatio, primary: true },
        { label: 'Interceptors per kill', unit: '', value: x.interceptorsPerKill },
        { label: 'Defender $/kill', unit: '$M', value: x.defenderCostPerKillMusd },
      ];
    },
    chart: { xKey: 'threat_cost', yLabel: 'Cost-exchange ratio (×)', logX: true, y: (x, v) => E.mdExchangeRatio(v['pk'], v['int_cost'], x, Math.round(v['shots'])).costExchangeRatio },
  },
  {
    id: 'value-index',
    title: 'System Value Index (cost-benefit)',
    category: 'Procurement',
    source: 'osint_cad/analysis/calculators.py:value_index + value_ci',
    equation: 'value = (benefit·survivability/100) / lifecycle($B);  LCC = (R&D + unit·qty + O&M·qty·life)/1000',
    why: 'The headline procurement rating: survivability-adjusted benefit per $B. It punishes both high cost and low survivability — which is why the conceptual battleship scores ~0.06. Sweep unit cost to see value erode.',
    inputs: [
      { key: 'unit', label: 'Unit cost', unit: '$M', min: 5, max: 12000, default: 700, step: 5, log: true },
      { key: 'qty', label: 'Quantity', unit: '-', min: 1, max: 1000, default: 100, step: 1 },
      { key: 'rnd', label: 'R&D cost', unit: '$M', min: 0, max: 50000, default: 25000, step: 500 },
      { key: 'oandm', label: 'Annual O&M / unit', unit: '$M', min: 0, max: 400, default: 25, step: 1 },
      { key: 'life', label: 'Service life', unit: 'yr', min: 5, max: 50, default: 30, step: 1 },
      { key: 'benefit', label: 'Benefit score', unit: '0–100', min: 5, max: 100, default: 85, step: 1 },
      { key: 'surv', label: 'Survivability', unit: '0–100', min: 5, max: 100, default: 80, step: 1 },
      { key: 'conf', label: 'Confidence', unit: '0–1', min: 0.1, max: 1, default: 0.55, step: 0.05 },
    ],
    compute: (v) => {
      const lcc = E.lifecycleCostBusd(v['unit'], Math.round(v['qty']), v['rnd'], v['oandm'], Math.round(v['life']));
      const [lo, hi] = E.valueCi(v['benefit'], v['surv'], lcc, v['conf']);
      return [
        { label: 'Value index', unit: '', value: E.valueIndex(v['benefit'], v['surv'], lcc), primary: true },
        { label: 'Lifecycle cost', unit: '$B', value: lcc },
        { label: 'CI low', unit: '', value: lo },
        { label: 'CI high', unit: '', value: hi },
      ];
    },
    chart: {
      xKey: 'unit', yLabel: 'Value index', logX: true,
      y: (x, v) => E.valueIndex(v['benefit'], v['surv'], E.lifecycleCostBusd(x, Math.round(v['qty']), v['rnd'], v['oandm'], Math.round(v['life']))),
    },
  },
];

export const CALC_BY_ID: Record<string, CalcDef> = Object.fromEntries(CALCULATORS.map((c) => [c.id, c]));
