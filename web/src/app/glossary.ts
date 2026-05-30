/** Curated glossary of standard terms/symbols used across the calculators. Concise,
 *  textbook definitions — not derived data, kept deliberately conservative and standard. */
export interface GlossaryTerm { term: string; unit: string; def: string; }

export const GLOSSARY: GlossaryTerm[] = [
  { term: 'RCS (radar cross section)', unit: 'm² / dBsm', def: 'Effective area a target presents to a radar — how strongly it back-scatters. Often quoted in dBsm = 10·log₁₀(σ / 1 m²).' },
  { term: 'σ^(1/4) law', unit: '—', def: 'Detection range scales as the fourth root of RCS (and of transmit power): a 1000× RCS cut shrinks range only ~5.6×.' },
  { term: 'SNR', unit: 'dB', def: 'Signal-to-noise ratio — received signal power over noise power; the basic detectability metric.' },
  { term: 'Pd / Pfa', unit: '—', def: 'Probability of detection / probability of false alarm. Albersheim’s equation links them to the required SNR.' },
  { term: 'FSPL', unit: 'dB', def: 'Free-space path loss, 20·log₁₀(4πR/λ) — the baseline spreading loss of any RF link or detection budget.' },
  { term: 'Eb/N0', unit: 'dB', def: 'Energy-per-bit to noise-spectral-density ratio; with the modulation it sets the bit-error rate. Link margin = Eb/N0 − required.' },
  { term: 'C/N0', unit: 'dB-Hz', def: 'Carrier-to-noise-density ratio at the receiver; divide by data rate to get Eb/N0.' },
  { term: 'J/S', unit: 'dB', def: 'Jammer-to-signal ratio at the victim receiver — the headline electronic-attack effectiveness number.' },
  { term: 'Burn-through range', unit: 'km', def: 'Range at which a radar’s skin return overtakes a self-screening jammer and a real track is re-acquired.' },
  { term: 'GDOP / HDOP / VDOP / PDOP / TDOP', unit: '—', def: 'Dilution of precision — how sensor/satellite geometry amplifies ranging error into position (or time) error.' },
  { term: 'UERE', unit: 'm', def: 'User-equivalent range error: the 1σ pseudorange error budget per satellite (iono, tropo, clock, multipath, receiver).' },
  { term: 'CEP', unit: 'm', def: 'Circular error probable — radius of the circle containing 50% of outcomes (e.g. impact points or geolocation fixes).' },
  { term: 'CRLB', unit: '—', def: 'Cramér-Rao lower bound — the theoretical best (smallest) variance any unbiased estimator can achieve; a floor, not a guarantee.' },
  { term: 'NEI / NETD', unit: 'W/m² / K', def: 'Noise-equivalent irradiance / temperature difference — an IR/EO sensor’s sensitivity floor.' },
  { term: 'GSD', unit: 'm', def: 'Ground sample distance — the smallest ground feature an imaging sensor can resolve; diffraction floor = 1.22·λ·R/D.' },
  { term: 'PRF', unit: 'Hz / kHz', def: 'Pulse repetition frequency — sets the unambiguous range (c/2·PRF) and unambiguous velocity (λ·PRF/4) trade in pulse-Doppler radar.' },
  { term: 'M² (beam quality)', unit: '—', def: 'How far a real laser beam is from an ideal Gaussian (M²=1); it multiplies the diffraction-limited divergence and spot size.' },
  { term: 'Transmission loss / Figure of merit', unit: 'dB', def: 'Sonar: TL is acoustic spreading+absorption loss; FOM = SL−(NL−DI)−DT is the maximum TL at which a target is still detected.' },
  { term: 'value index', unit: '—', def: 'This repo’s cost-benefit metric: survivability-adjusted benefit (0–100) per $B lifecycle cost. Higher = better value.' },
  { term: 'LPI / LPD', unit: '—', def: 'Low probability of intercept / detection — waveform design (low power spectral density, hopping, narrow beams) that resists interception and jamming.' },
];
