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

CALCULATORS.push(
  {
    id: 'ssj-burnthrough',
    title: 'Self-Screening Jammer Burn-Through Range',
    category: 'EW',
    source: 'osint_cad/analysis/calculators.py:ssj_burnthrough_range_km',
    equation: 'R_bt = √( Pt·Gt·σ·B_j·(S/J)_req / (4π·Pj·Gj·B_r) )',
    why: 'A self-protection jammer dominates at long range (skin return falls as 1/R⁴), but as the target closes the radar "burns through" and re-acquires a real track. Inside R_bt the jammer is defeated. Sweep jammer power to see how much ERP is needed to push burn-through outside the lethal envelope.',
    inputs: [
      { key: 'pt_kw', label: 'Radar peak power', unit: 'kW', min: 1, max: 2000, default: 100, step: 1, log: true },
      { key: 'gt', label: 'Radar antenna gain', unit: 'dBi', min: 20, max: 50, default: 40, step: 0.5 },
      { key: 'sigma', label: 'Target RCS', unit: 'm²', min: 0.001, max: 100, default: 5, step: 0.001, log: true },
      { key: 'pj', label: 'Jammer power', unit: 'W', min: 1, max: 5000, default: 200, step: 1, log: true },
      { key: 'gj', label: 'Jammer antenna gain', unit: 'dBi', min: 0, max: 30, default: 10, step: 0.5 },
      { key: 'br', label: 'Radar bandwidth', unit: 'MHz', min: 0.1, max: 50, default: 1, step: 0.1, log: true },
      { key: 'bj', label: 'Jammer noise bandwidth', unit: 'MHz', min: 1, max: 500, default: 50, step: 1 },
      { key: 'sjreq', label: 'Required S/J', unit: 'dB', min: 0, max: 25, default: 13, step: 0.5 },
    ],
    compute: (v) => [
      { label: 'Burn-through range', unit: 'km', value: E.ssjBurnthroughRangeKm(v['pt_kw'], v['gt'], v['sigma'], v['pj'], v['gj'], v['br'], v['bj'], v['sjreq']), primary: true },
      { label: 'Jammer ERP', unit: 'dBW', value: 10 * Math.log10(v['pj']) + v['gj'] },
      { label: 'Bandwidth advantage', unit: 'dB', value: 10 * Math.log10(v['bj'] / v['br']) },
    ],
    chart: { xKey: 'pj', yLabel: 'Burn-through range (km)', logX: true, y: (x, v) => E.ssjBurnthroughRangeKm(v['pt_kw'], v['gt'], v['sigma'], x, v['gj'], v['br'], v['bj'], v['sjreq']) },
  },
  {
    id: 'albersheim-snr',
    title: 'Required SNR for Detection (Albersheim)',
    category: 'Detection',
    source: 'osint_cad/analysis/calculators.py:albersheim_required_snr_db',
    equation: 'SNR_dB = −5·log₁₀N + (6.2 + 4.54/√(N+0.44))·log₁₀(A + 0.12·A·B + 1.7·B);  A=ln(0.62/Pfa), B=ln(Pd/(1−Pd))',
    why: "Every range calculation hides one number: how much SNR you actually need. Albersheim's closed form gives it from Pd and Pfa — returning the ~13.1 dB used as the default detection threshold (Pd=0.9, Pfa=1e-6, N=1), and showing how integrating N pulses lowers the per-pulse requirement.",
    inputs: [
      { key: 'pd', label: 'Detection probability', unit: '-', min: 0.1, max: 0.99, default: 0.9, step: 0.01 },
      { key: 'pfa', label: 'False-alarm prob.', unit: '-', min: 1e-10, max: 1e-3, default: 1e-6, step: 1e-7, log: true },
      { key: 'n', label: 'Integrated pulses', unit: '-', min: 1, max: 4096, default: 1, step: 1, log: true },
    ],
    compute: (v) => [
      { label: 'Required single-pulse SNR', unit: 'dB', value: E.albersheimRequiredSnrDb(v['pd'], v['pfa'], Math.round(v['n'])), primary: true },
      { label: 'Integration gain vs N=1', unit: 'dB', value: E.albersheimRequiredSnrDb(v['pd'], v['pfa'], 1) - E.albersheimRequiredSnrDb(v['pd'], v['pfa'], Math.round(v['n'])) },
    ],
    chart: { xKey: 'pd', yLabel: 'Required SNR (dB)', y: (x, v) => E.albersheimRequiredSnrDb(x, v['pfa'], Math.round(v['n'])) },
  },
  {
    id: 'albersheim-pd',
    title: 'Detection Probability from SNR (Albersheim)',
    category: 'Detection',
    source: 'osint_cad/analysis/calculators.py:albersheim_pd_from_snr',
    equation: 'Pd = 1/(1+e^(−B)),  B=(10^Z−A)/(0.12A+1.7),  Z=(SNR_dB+5log₁₀N)/(6.2+4.54/√(N+0.44)),  A=ln(0.62/Pfa)',
    why: 'The complement of the required-SNR tool: given the SNR a radar actually achieves (the radar-range-equation output), what detection probability results at a chosen false-alarm rate? Sweep SNR to trace the detection curve.',
    inputs: [
      { key: 'snr', label: 'Achieved SNR', unit: 'dB', min: 0, max: 25, default: 13, step: 0.5 },
      { key: 'pfa', label: 'False-alarm prob.', unit: '-', min: 1e-10, max: 1e-3, default: 1e-6, step: 1e-7, log: true },
      { key: 'n', label: 'Integrated pulses', unit: '-', min: 1, max: 4096, default: 1, step: 1, log: true },
    ],
    compute: (v) => [{ label: 'Detection probability', unit: '', value: E.albersheimPdFromSnr(v['snr'], v['pfa'], Math.round(v['n'])), primary: true, fmt: 'pct' }],
    chart: { xKey: 'snr', yLabel: 'Pd', y: (x, v) => E.albersheimPdFromSnr(x, v['pfa'], Math.round(v['n'])) },
  },
  {
    id: 'chaff-rcs',
    title: 'Chaff Dipole-Cloud RCS',
    category: 'EW',
    source: 'osint_cad/analysis/calculators.py:chaff_cloud_rcs_m2',
    equation: 'σ_chaff ≈ k·N·λ²  (k ≈ 0.17 for many randomly-oriented resonant half-wave dipoles)',
    why: 'A burst of resonant dipoles can present a large radar cross section to mask or seduce a tracker. Sweep dipole count to see how a cloud cheaply generates tens to hundreds of m² of RCS at a chosen band.',
    inputs: [
      { key: 'n', label: 'Number of dipoles', unit: '-', min: 1e4, max: 1e8, default: 1e6, step: 1e4, log: true },
      { key: 'f', label: 'Frequency', unit: 'GHz', min: 1, max: 18, default: 10, step: 0.1 },
    ],
    compute: (v) => {
      const r = E.chaffCloudRcsM2(v['n'], v['f']);
      return [{ label: 'Cloud RCS', unit: 'm²', value: r, primary: true }, { label: 'Cloud RCS', unit: 'dBsm', value: 10 * Math.log10(r) }];
    },
    chart: { xKey: 'n', yLabel: 'Cloud RCS (m²)', logX: true, y: (x, v) => E.chaffCloudRcsM2(x, v['f']) },
  },
  {
    id: 'noise-jam-range',
    title: 'Noise-Jamming Detection-Range Reduction',
    category: 'EW',
    source: 'osint_cad/analysis/calculators.py:noise_jamming_range_factor',
    equation: 'R_eff / R_free = (1 / (1 + J/N))^(1/4)',
    why: 'Barrage noise jamming raises the receiver noise floor; because range scales as the 4th root of SNR, even a strong J/N only modestly shrinks detection range. A 10 dB J/N cuts range to ~55%, not to zero — the same fourth-root law that protects stealth also limits noise jamming.',
    inputs: [{ key: 'jn', label: 'Jam-to-noise ratio', unit: 'dB', min: 0, max: 40, default: 10, step: 1 }],
    compute: (v) => {
      const f = E.noiseJammingRangeFactor(v['jn']);
      return [{ label: 'Range retained', unit: '', value: f, primary: true, fmt: 'pct' }, { label: 'Range lost', unit: '', value: 1 - f, fmt: 'pct' }];
    },
    chart: { xKey: 'jn', yLabel: 'Range retained (fraction)', y: (x) => E.noiseJammingRangeFactor(x) },
  },
  {
    id: 'radar-range-vs-aspect',
    title: 'Detection Range vs Aspect (stealth envelope)',
    category: 'CAD-derived',
    source: 'osint_cad/analysis/calculators.py:aspect_rcs_m2 + radar_range_simple_km',
    equation: 'σ(θ) interpolated nose→beam→tail (dBsm), then R = [Pt·G²·λ²·σ / ((4π)³·Pmin)]^(1/4)',
    why: 'Combines an aspect-dependent RCS (low head-on, high on the beam) with the radar range equation to draw the detection envelope vs viewing angle — why a stealth aircraft is detected far sooner from the side than head-on, and why approach geometry is everything.',
    inputs: [
      { key: 'front', label: 'Frontal RCS', unit: 'dBsm', min: -50, max: 10, default: -37, step: 0.5 },
      { key: 'beam', label: 'Beam RCS', unit: 'dBsm', min: -20, max: 40, default: 10, step: 0.5 },
      { key: 'rear', label: 'Tail RCS', unit: 'dBsm', min: -30, max: 30, default: 0, step: 0.5 },
      { key: 'aspect', label: 'Aspect angle', unit: 'deg', min: 0, max: 360, default: 0, step: 1 },
      { key: 'pt_kw', label: 'Radar peak power', unit: 'kW', min: 1, max: 2000, default: 100, step: 1, log: true },
      { key: 'g', label: 'Antenna gain', unit: 'dBi', min: 25, max: 50, default: 40, step: 0.5 },
      { key: 'f', label: 'Frequency', unit: 'GHz', min: 1, max: 18, default: 10, step: 0.1 },
      { key: 'pmin_dbm', label: 'Min detectable power', unit: 'dBm', min: -130, max: -90, default: -100, step: 1 },
    ],
    compute: (v) => {
      const sig = E.aspectRcsM2(10 ** (v['front'] / 10), 10 ** (v['beam'] / 10), 10 ** (v['rear'] / 10), v['aspect']);
      const pminW = 10 ** ((v['pmin_dbm'] - 30) / 10);
      return [
        { label: 'RCS at aspect', unit: 'dBsm', value: 10 * Math.log10(sig) },
        { label: 'Detection range', unit: 'km', value: E.radarRangeSimpleKm(v['pt_kw'] * 1000, v['g'], v['f'], sig, pminW), primary: true },
      ];
    },
    chart: {
      xKey: 'aspect', yLabel: 'Detection range (km)',
      y: (x, v) => E.radarRangeSimpleKm(v['pt_kw'] * 1000, v['g'], v['f'],
        E.aspectRcsM2(10 ** (v['front'] / 10), 10 ** (v['beam'] / 10), 10 ** (v['rear'] / 10), x), 10 ** ((v['pmin_dbm'] - 30) / 10)),
    },
  },
  {
    id: 'ram-reflection',
    title: 'RAM Reflection Coefficient',
    category: 'CAD-derived',
    source: 'osint_cad/analysis/calculators.py:ram_reflection_coefficient(_eff)',
    equation: 'Γ = 10^(−A/10);  Γ_eff(f) = Γ·(1 − 0.1·log₁₀(f/10))',
    why: 'Radar-absorbent material is rated in dB of absorption; the power reflection coefficient Γ (and hence the RCS reduction it buys) follows directly, with a mild frequency dependence. Matches the RAM model used by the Physical-Optics RCS calculator.',
    inputs: [
      { key: 'a', label: 'RAM absorption', unit: 'dB', min: 0, max: 30, default: 10, step: 0.5 },
      { key: 'f', label: 'Frequency', unit: 'GHz', min: 1, max: 40, default: 10, step: 0.1 },
    ],
    compute: (v) => [
      { label: 'Reflection coefficient Γ', unit: '', value: E.ramReflectionCoefficient(v['a']), primary: true },
      { label: 'Γ_eff at frequency', unit: '', value: E.ramReflectionCoefficientEff(v['a'], v['f']) },
      { label: 'RCS reduction', unit: 'dB', value: -10 * Math.log10(Math.max(1e-9, E.ramReflectionCoefficientEff(v['a'], v['f']))) },
    ],
    chart: { xKey: 'a', yLabel: 'Reflection coefficient Γ', y: (x, v) => E.ramReflectionCoefficientEff(x, v['f']) },
  },
  {
    id: 'po-validity',
    title: 'Physical-Optics Validity (size / wavelength)',
    category: 'CAD-derived',
    source: 'osint_cad/analysis/calculators.py:po_validity_ratio',
    equation: 'λ = c/f;  validity ratio = L_char / λ  (Physical Optics valid when ≫ 1)',
    why: 'The Physical-Optics RCS method used on the CAD meshes is accurate only when the target is large compared to a wavelength. This shows the L/λ ratio so you know when a mesh RCS result is trustworthy vs. when resonant/creeping-wave effects dominate.',
    inputs: [
      { key: 'f', label: 'Frequency', unit: 'GHz', min: 0.1, max: 40, default: 10, step: 0.1 },
      { key: 'lc', label: 'Characteristic length', unit: 'm', min: 0.05, max: 20, default: 0.68, step: 0.01, log: true },
    ],
    compute: (v) => [
      { label: 'Size / wavelength', unit: '×λ', value: E.poValidityRatio(v['f'], v['lc']), primary: true },
      { label: 'Wavelength', unit: 'cm', value: (299792458 / (v['f'] * 1e9)) * 100 },
    ],
    chart: { xKey: 'f', yLabel: 'L / λ', y: (x, v) => E.poValidityRatio(x, v['lc']) },
  },
);

CALCULATORS.push(
  {
    id: 'comms-link-budget',
    title: 'RF / SATCOM Link Budget',
    category: 'Comms',
    source: 'osint_cad/analysis/calculators.py:parabolic_gain_dbi + link_margin_db',
    equation: 'P_rx = P_tx + G_tx + G_rx − FSPL − L;  Eb/N0 = P_rx − 10log₁₀(k·T) − 10log₁₀(R_b);  G = η(πD/λ)²',
    why: 'The master equation of every datalink/SATCOM link: chains EIRP, dish gain (∝ D²), free-space loss, and receiver noise into the Eb/N0 margin that decides whether a link closes. Sweep range to find the cliff where the link drops; positive margin = closes.',
    inputs: [
      { key: 'ptx', label: 'Transmit power', unit: 'dBW', min: -10, max: 30, default: 10, step: 0.5 },
      { key: 'gtx', label: 'Tx antenna gain', unit: 'dBi', min: 0, max: 60, default: 30, step: 0.5 },
      { key: 'd', label: 'Rx dish diameter', unit: 'm', min: 0.3, max: 35, default: 2.4, step: 0.1, log: true },
      { key: 'eta', label: 'Aperture efficiency', unit: '-', min: 0.45, max: 0.75, default: 0.6, step: 0.01 },
      { key: 'f', label: 'Frequency', unit: 'GHz', min: 0.25, max: 40, default: 12, step: 0.1, log: true },
      { key: 'r', label: 'Range', unit: 'km', min: 10, max: 40000, default: 1000, step: 10, log: true },
      { key: 'lother', label: 'Other losses', unit: 'dB', min: 0, max: 20, default: 3, step: 0.5 },
      { key: 'tsys', label: 'System noise temp', unit: 'K', min: 50, max: 1000, default: 290, step: 5 },
      { key: 'rb', label: 'Data rate', unit: 'Mbps', min: 0.001, max: 1000, default: 10, step: 0.001, log: true },
      { key: 'ebn0', label: 'Required Eb/N0', unit: 'dB', min: 2, max: 16, default: 7, step: 0.1 },
    ],
    compute: (v) => {
      const grx = E.parabolicGainDbi(v['d'], v['eta'], v['f']);
      const prx = v['ptx'] + v['gtx'] + grx - E.fsplDb(v['f'], v['r']) - v['lother'];
      const margin = E.linkMarginDb(v['ptx'], v['gtx'], v['d'], v['eta'], v['f'], v['r'], v['lother'], v['tsys'], v['rb'], v['ebn0']);
      return [
        { label: 'Link margin', unit: 'dB', value: margin, primary: true },
        { label: 'Rx dish gain', unit: 'dBi', value: grx },
        { label: 'Received power', unit: 'dBW', value: prx },
        { label: 'Eb/N0', unit: 'dB', value: margin + v['ebn0'] },
      ];
    },
    chart: { xKey: 'r', yLabel: 'Link margin (dB)', logX: true, y: (x, v) => E.linkMarginDb(v['ptx'], v['gtx'], v['d'], v['eta'], v['f'], x, v['lother'], v['tsys'], v['rb'], v['ebn0']) },
  },
  {
    id: 'gnss-dop-error',
    title: 'GNSS Position Error from DOP',
    category: 'PNT',
    source: 'osint_cad/analysis/calculators.py:gnss_uere_m + gnss_horizontal_error_m',
    equation: 'σ_pos = DOP × σ_UERE;  σ_UERE = √(Σ σ_i²)',
    why: 'GNSS accuracy = geometry (DOP) × per-satellite ranging error (UERE). Sweep HDOP to see why poor satellite geometry (urban canyon, few sats) degrades a sub-metre receiver to tens of metres — even with no jamming.',
    inputs: [
      { key: 'iono', label: 'Ionospheric error', unit: 'm', min: 0, max: 10, default: 4, step: 0.1 },
      { key: 'tropo', label: 'Tropospheric error', unit: 'm', min: 0, max: 5, default: 0.7, step: 0.1 },
      { key: 'clk', label: 'Sat clock+ephemeris', unit: 'm', min: 0, max: 5, default: 2.1, step: 0.1 },
      { key: 'mp', label: 'Multipath error', unit: 'm', min: 0, max: 5, default: 1.4, step: 0.1 },
      { key: 'rx', label: 'Receiver noise', unit: 'm', min: 0, max: 3, default: 0.5, step: 0.1 },
      { key: 'hdop', label: 'Horizontal DOP', unit: '-', min: 0.7, max: 20, default: 1, step: 0.1, log: true },
      { key: 'vdop', label: 'Vertical DOP', unit: '-', min: 1, max: 25, default: 1.7, step: 0.1, log: true },
    ],
    compute: (v) => {
      const uere = E.gnssUereM(v['iono'], v['tropo'], v['clk'], v['mp'], v['rx']);
      return [
        { label: 'Horizontal error (1σ)', unit: 'm', value: uere * v['hdop'], primary: true },
        { label: 'UERE (1σ ranging)', unit: 'm', value: uere },
        { label: 'Vertical error (1σ)', unit: 'm', value: uere * v['vdop'] },
        { label: '3D error (1σ)', unit: 'm', value: Math.sqrt(v['hdop'] ** 2 + v['vdop'] ** 2) * uere },
        { label: 'Horizontal CEP (50%)', unit: 'm', value: 0.833 * v['hdop'] * uere },
      ];
    },
    chart: { xKey: 'hdop', yLabel: 'Horizontal error (m)', logX: true, y: (x, v) => E.gnssHorizontalErrorM(E.gnssUereM(v['iono'], v['tropo'], v['clk'], v['mp'], v['rx']), x) },
  },
  {
    id: 'irst-detection',
    title: 'IRST / EO Detection Range',
    category: 'IR / EO',
    source: 'osint_cad/analysis/calculators.py:irst_radiant_intensity + irst_detection_range_km',
    equation: 'ΔI = ε·σ·(T_t⁴−T_b⁴)·A·frac/π;  detect when ΔI·τ_opt·e^(−αR)/R² ≥ NEI',
    why: 'Passive IR detection rides the Stefan-Boltzmann T⁴ contrast against the background, attenuated by Beer-Lambert atmosphere. Sweep the extinction coefficient to see why an IRST that sees a target 40+ km in dry air sees it only a few km in haze — the dominant uncertainty in any claimed IRST range.',
    inputs: [
      { key: 'tt', label: 'Target temperature', unit: 'K', min: 250, max: 1200, default: 330, step: 5 },
      { key: 'tb', label: 'Background temperature', unit: 'K', min: 200, max: 320, default: 280, step: 1 },
      { key: 'at', label: 'Emitting area', unit: 'm²', min: 0.1, max: 50, default: 2, step: 0.1, log: true },
      { key: 'eps', label: 'Emissivity', unit: '-', min: 0.3, max: 1, default: 0.9, step: 0.01 },
      { key: 'frac', label: 'In-band fraction', unit: '-', min: 0.05, max: 1, default: 0.35, step: 0.01 },
      { key: 'tauopt', label: 'Optics transmission', unit: '-', min: 0.3, max: 0.95, default: 0.7, step: 0.01 },
      { key: 'alpha', label: 'Atmospheric extinction', unit: '1/km', min: 0.02, max: 2, default: 0.1, step: 0.01, log: true },
      { key: 'nei', label: 'Noise-equiv. irradiance', unit: '×1e-12 W/m²', min: 1, max: 1000, default: 10, step: 1, log: true },
    ],
    compute: (v) => {
      const di = E.irstRadiantIntensity(v['tt'], v['tb'], v['at'], v['eps'], v['frac']);
      const r = E.irstDetectionRangeKm(v['tt'], v['tb'], v['at'], v['eps'], v['frac'], v['tauopt'], v['alpha'], v['nei'] * 1e-12);
      return [
        { label: 'Detection range (with atmosphere)', unit: 'km', value: r, primary: true },
        { label: 'Radiant intensity ΔI', unit: 'W/sr', value: di },
        { label: 'Atmos. transmission at range', unit: '', value: Math.exp(-v['alpha'] * r) },
      ];
    },
    chart: { xKey: 'alpha', yLabel: 'Detection range (km)', logX: true, y: (x, v) => E.irstDetectionRangeKm(v['tt'], v['tb'], v['at'], v['eps'], v['frac'], v['tauopt'], x, v['nei'] * 1e-12) },
  },
  {
    id: 'passive-sonar',
    title: 'Passive Sonar Equation',
    category: 'Undersea',
    source: 'osint_cad/analysis/calculators.py:sonar_figure_of_merit_db + sonar_detection_range_km',
    equation: 'SE = SL − TL − (NL − DI) − DT;  TL = 20log₁₀(r) + α·r (spherical);  detect when SE ≥ 0',
    why: 'The undersea analogue of the radar equation. Detection happens where transmission loss falls below the figure of merit (SL − NL + DI − DT). Sweep range to find where signal excess crosses zero — the passive detection range.',
    inputs: [
      { key: 'sl', label: 'Source level', unit: 'dB re µPa@1m', min: 80, max: 180, default: 130, step: 1 },
      { key: 'nl', label: 'Noise level', unit: 'dB re µPa', min: 30, max: 100, default: 65, step: 1 },
      { key: 'di', label: 'Array directivity index', unit: 'dB', min: 0, max: 35, default: 20, step: 1 },
      { key: 'dt', label: 'Detection threshold', unit: 'dB', min: -5, max: 20, default: 5, step: 0.5 },
      { key: 'alpha', label: 'Absorption coefficient', unit: 'dB/km', min: 0.01, max: 30, default: 1, step: 0.01, log: true },
      { key: 'r', label: 'Range (evaluation)', unit: 'km', min: 0.1, max: 500, default: 20, step: 0.1, log: true },
    ],
    compute: (v) => {
      const fom = E.sonarFigureOfMeritDb(v['sl'], v['nl'], v['di'], v['dt']);
      const tl = E.sonarTlSphericalDb(v['r'], v['alpha']);
      return [
        { label: 'Detection range', unit: 'km', value: E.sonarDetectionRangeKm(v['sl'], v['nl'], v['di'], v['dt'], v['alpha']), primary: true },
        { label: 'Figure of merit (max TL)', unit: 'dB', value: fom },
        { label: 'Transmission loss at range', unit: 'dB', value: tl },
        { label: 'Signal excess at range', unit: 'dB', value: fom - tl },
      ];
    },
    chart: { xKey: 'r', yLabel: 'Signal excess (dB)', logX: true, y: (x, v) => E.sonarFigureOfMeritDb(v['sl'], v['nl'], v['di'], v['dt']) - E.sonarTlSphericalDb(x, v['alpha']) },
  },
  {
    id: 'orbit-mechanics',
    title: 'Circular Orbit & Coverage',
    category: 'Space',
    source: 'osint_cad/analysis/calculators.py:orbital_velocity_kms + orbital_period_min + coverage_half_angle_deg',
    equation: 'v = √(μ/a);  T = 2π√(a³/μ);  a = R_E + h;  λ = arccos((R_E/a)cos(el)) − el',
    why: 'Sets the cadence and footprint of every space sensor (SDA tracking, ISR, SATCOM). Sweep altitude to see the period grow and the coverage footprint widen — the trade behind LEO mega-constellations vs. higher orbits.',
    inputs: [
      { key: 'h', label: 'Altitude', unit: 'km', min: 150, max: 36000, default: 550, step: 10, log: true },
      { key: 'el', label: 'Min elevation angle', unit: 'deg', min: 0, max: 30, default: 5, step: 1 },
    ],
    compute: (v) => {
      const half = E.coverageHalfAngleDeg(v['h'], v['el']);
      const vel = E.orbitalVelocityKms(v['h']);
      const vg = vel * E.R_EARTH / (E.R_EARTH + v['h']);
      const swath = 2 * E.R_EARTH * (half * Math.PI / 180);
      return [
        { label: 'Orbital period', unit: 'min', value: E.orbitalPeriodMin(v['h']), primary: true },
        { label: 'Orbital velocity', unit: 'km/s', value: vel },
        { label: 'Coverage half-angle', unit: 'deg', value: half },
        { label: 'Coverage swath width', unit: 'km', value: swath },
        { label: 'Max access per pass', unit: 'min', value: vg > 0 ? swath / vg / 60 : 0 },
      ];
    },
    chart: { xKey: 'h', yLabel: 'Orbital period (min)', logX: true, y: (x) => E.orbitalPeriodMin(x) },
  },
  {
    id: 'ballistic-range',
    title: 'Vacuum Ballistic Range',
    category: 'Kinematics',
    source: 'osint_cad/analysis/calculators.py:projectile_range_km / apogee / tof',
    equation: 'R = v₀²·sin(2θ)/g;  h = v₀²·sin²θ/(2g);  TOF = 2v₀·sinθ/g',
    why: 'The textbook vacuum trajectory — an upper bound (no drag) that teaches the 45° max-range result and the range/apogee/time-of-flight trade. Real atmospheric ranges are shorter; this is the clean reference case.',
    inputs: [
      { key: 'v0', label: 'Muzzle / launch speed', unit: 'm/s', min: 50, max: 3000, default: 827, step: 1, log: true },
      { key: 'theta', label: 'Launch angle', unit: 'deg', min: 1, max: 89, default: 45, step: 1 },
      { key: 'g', label: 'Gravity', unit: 'm/s²', min: 1.6, max: 9.81, default: 9.81, step: 0.01 },
    ],
    compute: (v) => [
      { label: 'Range (level ground)', unit: 'km', value: E.projectileRangeKm(v['v0'], v['theta'], v['g']), primary: true },
      { label: 'Maximum ordinate (apogee)', unit: 'km', value: E.projectileApogeeKm(v['v0'], v['theta'], v['g']) },
      { label: 'Time of flight', unit: 's', value: E.projectileTofS(v['v0'], v['theta'], v['g']) },
      { label: 'Max possible range (45°)', unit: 'km', value: v['v0'] ** 2 / v['g'] / 1000 },
    ],
    chart: { xKey: 'theta', yLabel: 'Range (km)', y: (x, v) => E.projectileRangeKm(v['v0'], x, v['g']) },
  },
);

export const CALC_BY_ID: Record<string, CalcDef> = Object.fromEntries(CALCULATORS.map((c) => [c.id, c]));

/** One-line "what it does" descriptions (kept faithful to each calculator's actual compute). */
export const BLURBS: Record<string, string> = {
  'radar-range-equation': 'Maximum radar detection range from the full radar range equation — transmit power, aperture gain, RCS, bandwidth and pulse integration.',
  'rcs-fourth-root': 'Predicts detection range against any target by scaling one known calibration point by the RCS^(1/4) law.',
  'radar-horizon': 'Power-limited range vs the 4/3-Earth radar horizon — reveals the low-altitude detection gap and coverage area.',
  'free-space-path-loss': 'Free-space path loss vs frequency and range — the baseline term of every link and detection budget.',
  'esm-intercept': 'How far a passive receiver can intercept an emitter (Friis), including the time-bandwidth processing gain 10·log₁₀(B·T) from dwell time.',
  'jammer-to-signal': 'Jammer-to-signal ratio against a radar and against an LPI link (after a spatial-isolation + processing-gain penalty).',
  'aspect-rcs': 'How radar cross section changes with viewing aspect — nose, beam, tail — interpolated in dBsm.',
  'tdoa-geolocation': 'Sizes a multi-platform TDOA geolocation network: GDOP and the Cramér-Rao CEP vs platform count, baseline and time sync.',
  'salvo-kill': 'Salvo kill probability and expected leakers for a raid against a finite interceptor magazine.',
  'cost-exchange': "The defender's cost-exchange ratio — dollars spent intercepting vs the threat's unit cost.",
  'value-index': 'Survivability-adjusted cost-benefit value index and its confidence interval for a proposed system.',
  'ssj-burnthrough': 'Range at which a radar burns through a self-screening jammer and re-acquires a real track.',
  'albersheim-snr': "Required single-pulse SNR for a target detection probability and false-alarm rate (Albersheim's equation).",
  'albersheim-pd': 'Detection probability achieved at a given SNR and false-alarm rate (inverse Albersheim).',
  'chaff-rcs': 'Average radar cross section of a cloud of randomly-oriented resonant half-wave dipoles (chaff).',
  'noise-jam-range': 'How much a given jam-to-noise ratio shrinks detection range (the fourth-root law).',
  'radar-range-vs-aspect': 'Detection range vs viewing aspect — combines aspect-dependent RCS with the radar range equation (stealth envelope).',
  'ram-reflection': 'Reflection coefficient and RCS reduction of radar-absorbent material vs absorption rating and frequency.',
  'po-validity': 'Object-size-to-wavelength ratio that tells you when the Physical-Optics RCS method is valid.',
  'comms-link-budget': 'Full RF/SATCOM link budget: dish gain, path loss, received power, and the Eb/N0 margin that decides if a link closes.',
  'gnss-dop-error': 'GNSS position error from satellite geometry (DOP) times the per-satellite ranging-error budget (UERE).',
  'irst-detection': 'Infrared search-and-track detection range from thermal contrast and Beer-Lambert atmospheric extinction.',
  'passive-sonar': 'Passive sonar equation: detection range where transmission loss falls below the figure of merit.',
  'orbit-mechanics': 'Circular-orbit velocity, period, and ground coverage footprint vs altitude.',
  'ballistic-range': 'Vacuum projectile range, apogee, and time of flight vs launch speed and angle (drag-free upper bound).',
};
