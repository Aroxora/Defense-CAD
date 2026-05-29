# Project Glasswing — Computer Network Defense · TrenchWork.org

*A TrenchWork.org Computer Network Defense initiative.*

**A physics toolkit that turns open-source parameters into *actionable* engineering
recommendations** — radar cross section, RF propagation, ESM geolocation, missile
kinematics, and engagement modeling, all from public data with explicit uncertainty.

**Live web app:** https://osint-defense.web.app — interactive procurement &amp; R&amp;D
cost-benefit, the actionable EW strategy, and PLA/DoD doctrine, all driven by the same
`osint_cad` models.

> **Classification: UNCLASSIFIED // CONCEPTUAL // FOR PUBLIC RELEASE.**
> All adversary/system parameters are deduced from publicly available information with
> documented confidence levels. No classified or export-controlled information is included.

The goal of this repo is **not** to declare who "wins." It is to compute, from first
principles, **what is physically achievable** and therefore **what is worth building or
doing** — and, just as importantly, what is *not* (so effort isn't wasted on physics dead
ends).

---

## Start here: the actionable EW strategy

The flagship deliverable is a worked, reproducible example of the philosophy above.

```bash
pip install -e .
python scripts/ew_strategy_analysis.py
```

It establishes from the repo's own link-budget math that **jamming a directional,
frequency-hopping LPI/LPD datalink (e.g. MADL) from standoff is not physically
achievable** (modeled J/S ≈ −16 dB), and replaces that dead end with three lines of effort
the physics *does* reward — each with numbers computed live from `osint_cad.*`:

1. **Passive ESM geolocation network** *(detect, don't jam)* — sidelobe intercept +
   multi-platform TDOA/FDOA. CAD output: ≥4 synchronized platforms, ~30 km baseline,
   ≤10 ns sync → GDOP < 5, operational CEP ≈ 8–11 m (weapons-quality, with caveat).
2. **Harden your own datalink** *(defeat the adversary's LoE 1)* — driving sidelobes
   −30 → −40 dB cuts an adversary's intercept range ~68 %. Concrete antenna/EMCON spec.
3. **Reallocate active EW to where physics rewards it** — the same jammer that is useless
   against the LPI link is +12 dB J/S effective against the main radar and in the terminal
   endgame.

Full write-up: **[`EW_ACTIONABLE_STRATEGY.md`](EW_ACTIONABLE_STRATEGY.md)**.

### Doctrinal context + cost-benefit (OSINT)

To study the models in their strategic context, the repo includes **symmetric, open-source
analytical references on published PLA and U.S. DoD strategy/doctrine** — kept in distinct
packages `osint_cad/doctrine/{pla,dod}/` — plus a **proposed-system cost-benefit analysis**:

```bash
python scripts/strategy_reference.py --side both --cba   # PLA + DoD doctrine + cost-benefit
python -m osint_cad.doctrine.cost_benefit                # ranked cost-benefit table only
```

- **PLA**: systems-confrontation, A2/AD (counter-intervention), informatized & intelligentized
  warfare, reconnaissance-strike complex — see **[`PLA_STRATEGY_OSINT.md`](PLA_STRATEGY_OSINT.md)**.
- **DoD**: Integrated Deterrence, CJADC2, Mosaic Warfare, DMO, ACE, Replicator — see
  **[`DOD_STRATEGY_OSINT.md`](DOD_STRATEGY_OSINT.md)**.
- **Cost-benefit** of proposed systems (incl. the conceptual Trump-class battleship), with a
  Tavily news auto-updater — see **[`COST_BENEFIT_ANALYSIS.md`](COST_BENEFIT_ANALYSIS.md)**.

All of this is descriptive analysis for education/study — **not operational guidance**. CI
(`.github/workflows/ci.yml`) runs the test suite on every push/PR.

---

## What the toolkit computes (and the actionable output of each)

| Module area | Physics | Actionable use |
|---|---|---|
| `osint_cad.physics.rcs_models`, `osint_cad.geometry.cad_rcs_calculator` | Empirical + Physical-Optics RCS from CAD meshes | Detection-range and signature trades; sidelobe-level requirements |
| `osint_cad.physics.rf_propagation` | Friis + ITU-R P.676 gas absorption, P.838 rain, multipath | Honest link/detection budgets across bands and weather |
| `osint_cad.sensors.signal_processing` | Energy/cyclostationary detection, MUSIC DF, sidelobe model | Sensitivity & integration-dwell trades for ESM |
| `osint_cad.sensors.geolocation_network` | TDOA/FDOA least-squares, GDOP, TDOA CRLB | Platform count / geometry / timing sync to hit a target CEP |
| `osint_cad.sensors.f22_radar_model`, `.j20_radar_model` | Radar range equation with integration gain | Comparative detection-range envelopes |
| `osint_cad.targeting.*` | Ballistic/HGV kinematics, BVR/seeker link budgets | Engagement-envelope and Pk sensitivity studies |
| `osint_cad.platforms.*`, `osint_cad.engagements.*` | Platform models + integrated kill-chain composition | End-to-end scenario studies (for *relative* comparison) |

---

## Install & quickstart

```bash
git clone <this-repo> && cd Defense-CAD
python -m venv .venv && source .venv/bin/activate
pip install -e .

python scripts/ew_strategy_analysis.py        # the actionable EW strategy
python scripts/run_integrated_kill_chain.py    # integrated kill-chain scenario study
python scripts/simulation.py                   # passive MADL sidelobe-intercept ESM demo
pytest                                         # 220+ physics/regression tests
```

## Package layout

```
osint_cad/
├── geometry/      # CAD meshes, Physical-Optics RCS, constraints, sensitivity, export
├── physics/       # RF propagation (ITU-R), RCS models, VLBI coherent processing
├── sensors/       # signal processing, TDOA/FDOA geolocation, radar & ESM models
├── targeting/     # ballistic/HGV kinematics, BVR & seeker link budgets, datalinks
├── platforms/     # ship / air-defense / PLA & US system models
├── engagements/   # BVR, kill chains, network-centric & integrated scenarios
├── doctrine/      # OSINT analytical reference on published PLA strategy/doctrine
└── util/          # calculation logging
scripts/           # runnable entry points (analysis & demos)
tests/             # pytest suite (incl. physics regression tests)
web/               # Angular + Firebase interactive site (public/data holds exported JSON)
*_validated.stl    # OSINT-derived CAD geometries at repo root (df-41, hq-9b, j-20, type_055)
docs analyses      # platform/system CAD analyses (*.md)
```

---

## Methodology & uncertainty policy

- **Physics first.** Detection ranges use the radar range equation (R ∝ σ^¼); propagation
  uses Friis + ITU-R P.676/P.838; RCS uses empirical aspect models and a Physical-Optics
  mesh integrator; geolocation uses TDOA/FDOA with GDOP and Cramér-Rao bounds.
- **OSINT parameters carry confidence bands.** Adversary RCS, datalink characteristics,
  and Pk inputs are *deduced* (typically 40–70 % confidence) and labeled as such. They are
  estimates, not measurements.
- **Relative, not absolute.** Results are suitable for comparative trades ("does upgrade A
  beat upgrade B," "what geometry hits this CEP"), not as predictions of real engagements.
  Point-estimate "win ratios" are presented only as low-confidence sensitivity illustrations.
- **No physics dead ends sold as capability.** Where the math says something can't be done
  reliably (e.g. standoff jamming of an LPI link), the repo says so and pivots to what works.

## Scope & non-goals

This is conceptual, open-source modeling for analysis and education. It is **not** a
targeting system, contains **no** classified or export-controlled data, and makes **no**
claims about fielded performance of any real system.

## Web app (Angular + Firebase Hosting)

The interactive front-end lives in [`web/`](web/) (Angular 18, standalone). It reads JSON
exported from the Python models so the UI never drifts from the source of truth:

```bash
python scripts/export_web_data.py          # osint_cad.* -> web/public/data/*.json
cd web && npm install
npx ng build --configuration=production     # outputs web/dist/web/browser
firebase deploy --only hosting              # project: osint-defense (.firebaserc)
```

CI builds the whole pipeline (Python export → Angular build) on every push
(`.github/workflows/ci.yml`).

## License

MIT — see [`LICENSE`](LICENSE).
