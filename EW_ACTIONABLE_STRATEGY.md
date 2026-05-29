# Actionable EW Strategy (CAD-Grounded)

**Classification: UNCLASSIFIED // CONCEPTUAL // PUBLIC RELEASE**

Every recommendation here is computed from this repository's physics modules
(`osint_cad.*`) and is reproducible by running:

```bash
python scripts/ew_strategy_analysis.py
```

Nothing on this page is asserted — the numbers come straight out of the radar/RF/ESM
math in the package.

---

## The premise: stop trying to jam MADL

A modern directional, electronically-steered, **frequency-hopping LPI/LPD** datalink
(MADL is the worked example) is **not reliably jammable from standoff**. The repo's own
link-budget math shows why: a standoff jammer sits off the steered link beam (large
spatial isolation), must overcome the waveform's despreading/processing gain, and a
fixed-band jammer dwells on a hopping link only a fraction of the time. Modeled J/S for a
30 kW jammer at 100 km is **about −16 dB vs MADL** (ineffective) versus **about +12 dB vs
the APG-81 radar** (effective). "Jam MADL to isolate the F-35" is therefore not a fundable
engineering line of effort. The three things below *are*.

---

## Line of Effort 1 — Passive ESM geolocation network *(detect, don't jam)*

The physically rewarded counter-LPI technique is **electronic support**: intercept the
link's sidelobes and geolocate by multi-platform TDOA/FDOA. This is detection, not attack.

**What the CAD shows** (`friis_intercept_range_km`, `processing_gain_db`,
`GeolocationEngine.calculate_gdop`, `calculate_crlb_tdoa`):

- **Intercept range scales with integration dwell.** For a ~2.8 W Ku-band sidelobe EIRP
  against a −74 dBm ESM receiver: ~4 km at 1 µs dwell → ~44 km at 100 µs → ~140 km at
  1 ms. These are **best-case** (observer must be in a sidelobe during an active burst;
  intercept is opportunistic and bearing-only per platform).
- **Geolocation needs geometry, not just sensitivity.** A 3D fix requires **≥4
  synchronized platforms**. With ≤10 ns time sync, a 4-platform ring with **GDOP < 5**
  reaches a CRLB floor of ~2 m; after a realistic ~5× degradation for hopping-induced
  coherence loss and calibration/multipath, **operational CEP ≈ 8–11 m (weapons-quality).**

**Actionable spec:** ~4 synchronized ESM platforms, ~30 km baseline (altitude-staggered to
keep the geometry well-conditioned), ≤10 ns GPS/PTP-disciplined sync, Ku-band coverage,
≈ −74 dBm sensitivity. *Caveat: CRLB is a lower bound; field CEP will be several× larger.*

---

## Line of Effort 2 — Harden your own datalink *(defeat the adversary's LoE 1)*

The same intercept math, run against your own link, is a **design requirement generator**.

**What the CAD shows** (sidelobe-level sweep through `friis_intercept_range_km`): the range
at which an adversary ESM can intercept your link is set by your **sidelobe EIRP**. Driving
sidelobes from −30 dB to −40 dB cuts the adversary's intercept range from ~44 km to ~14 km
(**~68 % reduction**) for a 100 µs-dwell adversary.

**Actionable upgrades:**
- Deeper sidelobes via aperture/illumination tapering (−30 → −40 dB is a large payoff).
- Emission control: shorter bursts / lower duty cycle reduce the adversary's integration
  opportunities (fewer chances to catch a sidelobe).
- Randomized beam scheduling so sidelobe geometry is unpredictable.

These are concrete antenna/EMCON requirements — no new weapon system.

---

## Line of Effort 3 — Reallocate active EW to where physics rewards it *(tactic)*

**What the CAD shows** (`_js_db` link budget): the *same* jammer that is useless against
MADL is decisive against the wide-open main radar (+12 dB J/S vs APG-81) and is valuable in
the **terminal phase** (seeker/datalink endgame, short range → high J/S).

**Actionable reallocation:**
- Spend jammer power/time on main-radar denial and terminal-phase self-protection.
- Do **not** budget standoff MADL jamming as a dependable effect; redirect that capacity to
  the passive ESM network (LoE 1) and radar denial.

---

## Bottom line (priority order)

1. **Build the passive multi-platform ESM geolocation network** (LoE 1).
2. **Harden your own datalink sidelobes / EMCON** (LoE 2).
3. **Reallocate active EW to radar denial + terminal defense** (LoE 3).
4. **Stop funding standoff MADL jamming** — modeled effect ≈ 0.

Reproduce all figures: `python scripts/ew_strategy_analysis.py`.
