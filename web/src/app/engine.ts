/**
 * Pure physics engine for the browser — a 1:1 TypeScript port of
 * osint_cad/analysis/calculators.py. No Angular imports, so it is parity-checked against the
 * Python source of truth in CI (web/parity-check.mjs vs public/data/parity.json).
 *
 * Every function mirrors the same textbook equation used by the Python analysis.
 */

export const C = 299_792_458; // m/s
export const K_BOLTZMANN = 1.380649e-23;
export const T0 = 290;

// ---------------------------------------------------------------- radar range equation
export function radarMaxRangeKm(
  ptW: number, gainDbi: number, freqGhz: number, rcsM2: number,
  bandwidthHz = 1e6, noiseFigureDb = 3, snrMinDb = 13, lossesDb = 5, nIntegrate = 1,
): number {
  if (rcsM2 <= 0 || ptW <= 0) return 0;
  const g = 10 ** (gainDbi / 10);
  const lam = C / (freqGhz * 1e9);
  const f = 10 ** (noiseFigureDb / 10);
  const snr = 10 ** (snrMinDb / 10);
  const loss = 10 ** (lossesDb / 10);
  const num = ptW * g * g * lam * lam * rcsM2 * Math.max(1, nIntegrate);
  const den = (4 * Math.PI) ** 3 * K_BOLTZMANN * T0 * bandwidthHz * f * snr * loss;
  return (num / den) ** 0.25 / 1000;
}

export function apertureGainDbi(aEffM2: number, eta: number, freqGhz: number): number {
  const lam = C / (freqGhz * 1e9);
  return 10 * Math.log10((4 * Math.PI * aEffM2 * eta) / (lam * lam));
}

export function scanLossDb(azDeg: number): number {
  return -1.5 * (azDeg / 60) ** 2;
}

export function fsplDb(freqGhz: number, rangeKm: number): number {
  const lam = C / (freqGhz * 1e9);
  return 20 * Math.log10((4 * Math.PI * (rangeKm * 1000)) / lam);
}

export function aspectRcsM2(frontalM2: number, sideM2: number, rearM2: number, aspectDeg: number): number {
  let a = ((aspectDeg % 360) + 360) % 360;
  if (a > 180) a = 360 - a;
  const fDb = 10 * Math.log10(frontalM2), sDb = 10 * Math.log10(sideM2), rDb = 10 * Math.log10(rearM2);
  let db: number;
  if (a <= 90) { const w = (1 - Math.cos((Math.PI * a) / 90)) / 2; db = fDb * (1 - w) + sDb * w; }
  else { const w = (1 - Math.cos((Math.PI * (a - 90)) / 90)) / 2; db = sDb * (1 - w) + rDb * w; }
  return 10 ** (db / 10);
}

// ---------------------------------------------------------------- radar horizon / coverage
export function radarHorizonKm(hRadarM: number, hTargetM: number): number {
  return 4.12 * (Math.sqrt(Math.max(0, hRadarM)) + Math.sqrt(Math.max(0, hTargetM)));
}

export function powerLimitedRangeKm(refRangeKm: number, refRcsM2: number, rcsM2: number): number {
  if (rcsM2 <= 0) return 0;
  return refRangeKm * (rcsM2 / refRcsM2) ** 0.25;
}

export interface Coverage {
  powerLimitedKm: number; horizonKm: number; effectiveKm: number;
  limitedBy: 'power' | 'horizon'; coverageAreaKm2: number;
}
export function effectiveCoverage(
  hRadarM: number, hTargetM: number, refRangeKm: number, refRcsM2: number, rcsM2: number,
): Coverage {
  const pwr = powerLimitedRangeKm(refRangeKm, refRcsM2, rcsM2);
  const hor = radarHorizonKm(hRadarM, hTargetM);
  const eff = round(Math.min(pwr, hor), 1);
  return {
    powerLimitedKm: round(pwr, 1), horizonKm: round(hor, 1), effectiveKm: eff,
    limitedBy: hor < pwr ? 'horizon' : 'power', coverageAreaKm2: Math.round(Math.PI * eff * eff),
  };
}

// ---------------------------------------------------------------- RF intercept / EW
export function friisInterceptRangeKm(
  eirpDbm: number, rxSensitivityDbm: number, freqGhz: number, procGainDb = 0,
): number {
  const lam = C / (freqGhz * 1e9);
  const plDb = eirpDbm - (rxSensitivityDbm - procGainDb);
  return (lam * 10 ** (plDb / 20) / (4 * Math.PI)) / 1000;
}

export function processingGainDb(bandwidthHz: number, integrationTimeS: number): number {
  return 10 * Math.log10(bandwidthHz * integrationTimeS);
}

export function jsRatioDb(
  jamPowerKw: number, rangeKm: number, victimSignalDbm: number, freqHz: number, jammerAntGainDb = 30,
): number {
  const jamPowerDbw = 10 * Math.log10(jamPowerKw * 1000);
  const pathLossDb = 20 * Math.log10(rangeKm * 1000) + 20 * Math.log10(freqHz) - 147.55;
  return jamPowerDbw + 30 - pathLossDb + jammerAntGainDb - victimSignalDbm;
}

// ---------------------------------------------------------------- atmospheric (ITU-R P.676)
export interface Atmos { oxygenDbKm: number; waterDbKm: number; totalDbKm: number; }
export function atmosphericSpecificAttenuation(freqGhz: number, rhoVapor = 7.5): Atmos {
  const f = freqGhz;
  let gammaO: number;
  if (f < 54) gammaO = (7.2 / (f ** 2 + 0.34) + 0.62 / ((54 - f) ** 1.16 + 0.83)) * f ** 2 * 1e-3;
  else if (f < 63) gammaO = 0.5 + 14.5 / (1 + ((f - 60) / 1.5) ** 2);
  else gammaO = 0.5 + 6 / (1 + ((f - 63) / 9) ** 2);
  const gammaW = (0.05 + 0.0021 * rhoVapor + 3.6 / ((f - 22.235) ** 2 + 8.5)) * f ** 2 * rhoVapor * 1e-4;
  return { oxygenDbKm: gammaO, waterDbKm: gammaW, totalDbKm: gammaO + gammaW };
}

// ---------------------------------------------------------------- geolocation (GDOP / CRLB)
type Vec = [number, number, number];
export function ringGeometry(n: number, baselineKm: number, altitudeM = 10000, altSpreadM = 3000): Vec[] {
  const r = baselineKm * 1000;
  const out: Vec[] = [];
  for (let i = 0; i < n; i++) {
    out.push([r * Math.cos((2 * Math.PI * i) / n), r * Math.sin((2 * Math.PI * i) / n),
      altitudeM + (i % 2 ? altSpreadM : -altSpreadM)]);
  }
  return out;
}

function mat3Inv(m: number[][]): number[][] | null {
  const [a, b, c] = m[0], [d, e, f] = m[1], [g, h, i] = m[2];
  const det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
  if (Math.abs(det) < 1e-12) return null;
  const id = 1 / det;
  return [
    [(e * i - f * h) * id, (c * h - b * i) * id, (b * f - c * e) * id],
    [(f * g - d * i) * id, (a * i - c * g) * id, (c * d - a * f) * id],
    [(d * h - e * g) * id, (b * g - a * h) * id, (a * e - b * d) * id],
  ];
}

function unit(p: Vec, q: number[]): Vec {
  const d: Vec = [p[0] - q[0], p[1] - q[1], p[2] - q[2]];
  const r = Math.hypot(d[0], d[1], d[2]) || 1;
  return [d[0] / r, d[1] / r, d[2] / r];
}

export function gdop(platforms: Vec[], emitter: number[]): number | null {
  if (platforms.length < 4) return null;
  const g = platforms.map((p) => unit(p, emitter));
  const gtg = [0, 1, 2].map((r) => [0, 1, 2].map((col) => g.reduce((s, v) => s + v[r] * v[col], 0)));
  const inv = mat3Inv(gtg);
  if (!inv) return null;
  return Math.sqrt(inv[0][0] + inv[1][1] + inv[2][2]);
}

export function crlbCepM(platforms: Vec[], emitter: number[], timingNs = 10): number | null {
  const n = platforms.length;
  if (n < 4) return null;
  const sigmaRange = timingNs * 1e-9 * C;
  const u0 = unit(platforms[0], emitter);
  const rows: Vec[] = [];
  for (let i = 1; i < n; i++) {
    const ui = unit(platforms[i], emitter);
    rows.push([ui[0] - u0[0], ui[1] - u0[1], ui[2] - u0[2]]);
  }
  const fim = [0, 1, 2].map((r) =>
    [0, 1, 2].map((col) => rows.reduce((s, v) => s + v[r] * v[col], 0) / sigmaRange ** 2));
  const inv = mat3Inv(fim);
  if (!inv) return null;
  const varXy = inv[0][0] + inv[1][1];
  return 1.1774 * Math.sqrt(Math.max(0, varXy) / 2);
}

export interface GeoQuality {
  platforms: number; baselineKm: number; gdop: number | null;
  crlbFloorM: number | null; opsCepM: number | null; illConditioned: boolean;
}
export function geolocationQuality(n: number, baselineKm: number, timingNs = 10, opsDegrade = 5): GeoQuality {
  const plats = ringGeometry(n, baselineKm);
  const emitter = [0, 0, 11000];
  const g = gdop(plats, emitter);
  const cep = crlbCepM(plats, emitter, timingNs);
  const ill = g === null || cep === null || cep > 10000;
  return {
    platforms: n, baselineKm, gdop: g === null ? null : round(g, 2),
    crlbFloorM: ill ? null : round(cep as number, 1),
    opsCepM: ill ? null : Math.round((cep as number) * opsDegrade), illConditioned: ill,
  };
}

// ---------------------------------------------------------------- missile defense
export function killProbSalvo(pk: number, shots: number): number {
  return 1 - (1 - pk) ** Math.max(0, shots);
}

export interface MdEngage {
  pkPerTarget: number; engageable: number; engaged: number;
  expectedLeakers: number; interceptFraction: number; magazineExhausted: boolean;
}
export function mdEngage(pk: number, magazine: number, raid: number, shotsPerTarget = 2): MdEngage {
  const pkT = killProbSalvo(pk, shotsPerTarget);
  const engageable = Math.floor(magazine / Math.max(1, shotsPerTarget));
  const engaged = Math.min(raid, engageable);
  const leakers = raid - engaged + engaged * (1 - pkT);
  return {
    pkPerTarget: round(pkT, 4), engageable, engaged, expectedLeakers: round(leakers, 2),
    interceptFraction: raid ? round(1 - leakers / raid, 4) : 0, magazineExhausted: raid - engaged > 0,
  };
}

export interface MdExchange {
  interceptorsPerKill: number; defenderCostPerKillMusd: number;
  costExchangeRatio: number; favorableForDefender: boolean;
}
export function mdExchangeRatio(
  pk: number, interceptorCostMusd: number, threatCostMusd: number, shotsPerTarget = 2,
): MdExchange {
  const pkT = killProbSalvo(pk, shotsPerTarget);
  const perKill = pkT > 0 ? shotsPerTarget / pkT : Infinity;
  const defenderCost = perKill * interceptorCostMusd;
  const ratio = threatCostMusd ? defenderCost / threatCostMusd : Infinity;
  return {
    interceptorsPerKill: round(perKill, 2), defenderCostPerKillMusd: round(defenderCost, 1),
    costExchangeRatio: round(ratio, 2), favorableForDefender: ratio < 1,
  };
}

// ---------------------------------------------------------------- cost-benefit value
export function lifecycleCostBusd(unitMusd: number, qty: number, rndMusd: number, oandmMusd: number, lifeYears: number): number {
  return (rndMusd + unitMusd * qty + oandmMusd * qty * lifeYears) / 1000;
}
export function valueIndex(benefit: number, survivability: number, lccBusd: number): number {
  return lccBusd > 0 ? (benefit * survivability) / 100 / lccBusd : 0;
}
export function valueCi(benefit: number, survivability: number, lccBusd: number, confidence: number): [number, number] {
  const v = valueIndex(benefit, survivability, lccBusd);
  const rel = Math.max(0, 1 - confidence) * Math.sqrt(3);
  return [Math.max(0, v * (1 - rel)), v * (1 + rel)];
}

function round(x: number, d: number): number {
  const f = 10 ** d;
  return Math.round(x * f) / f;
}

// ---------------------------------------------------------------- parity dispatch (CI)
// Maps the names used in scripts/export_parity.py to scalar-returning calls.
export const PARITY: Record<string, (...a: number[]) => number> = {
  radarMaxRangeKm: (...a) => radarMaxRangeKm(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8]),
  apertureGainDbi: (...a) => apertureGainDbi(a[0], a[1], a[2]),
  scanLossDb: (...a) => scanLossDb(a[0]),
  fsplDb: (...a) => fsplDb(a[0], a[1]),
  aspectRcsM2: (...a) => aspectRcsM2(a[0], a[1], a[2], a[3]),
  radarHorizonKm: (...a) => radarHorizonKm(a[0], a[1]),
  powerLimitedRangeKm: (...a) => powerLimitedRangeKm(a[0], a[1], a[2]),
  friisInterceptRangeKm: (...a) => friisInterceptRangeKm(a[0], a[1], a[2], a[3]),
  processingGainDb: (...a) => processingGainDb(a[0], a[1]),
  jsRatioDb: (...a) => jsRatioDb(a[0], a[1], a[2], a[3], a[4]),
  atmosphericTotalDbKm: (...a) => atmosphericSpecificAttenuation(a[0], a[1]).totalDbKm,
  gdop: (...a) => { const q = geolocationQuality(a[0], a[1]); return q.gdop === null ? -1 : q.gdop; },
  opsCepM: (...a) => { const q = geolocationQuality(a[0], a[1]); return q.opsCepM === null ? -1 : q.opsCepM; },
  killProbSalvo: (...a) => killProbSalvo(a[0], a[1]),
  exchangeRatio: (...a) => mdExchangeRatio(a[0], a[1], a[2], a[3]).costExchangeRatio,
  expectedLeakers: (...a) => mdEngage(a[0], a[1], a[2], a[3]).expectedLeakers,
  lifecycleCostBusd: (...a) => lifecycleCostBusd(a[0], a[1], a[2], a[3], a[4]),
  valueIndex: (...a) => valueIndex(a[0], a[1], a[2]),
  valueCiLow: (...a) => valueCi(a[0], a[1], a[2], a[3])[0],
  valueCiHigh: (...a) => valueCi(a[0], a[1], a[2], a[3])[1],
};
