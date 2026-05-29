# Methodology — Physics, Scoring, Code & Verification

**Classification: UNCLASSIFIED // OPEN-SOURCE ANALYSIS // PUBLIC RELEASE**

This document explains, in one place, *how* the analysis works: the physics behind it, the
scoring/rating math (its own section), exactly where each piece lives in the code, how
results are verified by CI/CD before anything is posted, and how hard facts are corroborated
against current open sources via Tavily.

---

## 1. Physics-based analysis

Everything quantitative traces to a textbook relationship — nothing is asserted. Each model
below names the code that implements it.

| Phenomenon | Relationship used | Code |
|---|---|---|
| Detection range | Radar range equation, **R ∝ σ¹ᐟ⁴** (R = [PtG²λ²σ / ((4π)³ k T B F · SNR · L)]¹ᐟ⁴) | `osint_cad/sensors/{f22,j20}_radar_model.py`, `osint_cad/analysis/radar_coverage.py` |
| RF propagation | Friis FSPL + **ITU-R P.676** gas absorption (O₂/H₂O) + P.838 rain | `osint_cad/physics/rf_propagation.py` |
| Radar cross section | Empirical aspect models + **Physical-Optics** mesh integral (γ² power scaling) | `osint_cad/physics/rcs_models.py`, `osint_cad/geometry/cad_rcs_calculator.py` |
| Passive geolocation | TDOA/FDOA least-squares, **GDOP**, TDOA **Cramér-Rao bound** | `osint_cad/sensors/geolocation_network.py` |
| EW link budget | Friis intercept range, non-coherent integration gain (10·log₁₀(BT)), J/S | `osint_cad/engagements/ew_strategy.py` |
| Radar horizon | 4/3-Earth horizon, **R ≈ 4.12·(√hᵣ+√hₜ)** km | `osint_cad/analysis/radar_coverage.py` |
| Missile-defense engagement | Salvo kill prob **1−(1−Pk)ⁿ**, magazine/leakage, cost-exchange | `osint_cad/analysis/missile_defense.py` |
| Ballistic / HGV kinematics | Phased trajectory, drag-bounded reentry, time-weighted glide | `osint_cad/targeting/*.py` |

Three physics bugs were corrected during the refactor (each pinned by a regression test in
`tests/test_physics_fixes.py`): seeker range must scale as **σ¹ᐟ⁴** (not σ⁰·²); the PO RCS
must carry the reflection coefficient as **γ²** (it was double-counted as γ⁴); and the
atmospheric model now matches **ITU-R P.676** (≈0.03 dB/km at Ku-band, ≈15 dB/km at the
60 GHz O₂ line). All adversary/system inputs are OSINT estimates with confidence bands; the
outputs are for **relative comparison**, not absolute truth.

---

## 2. Scoring & rating methodology  *(read this before trusting any number)*

The procurement/R&D portfolio rates each system with three transparent numbers plus a
confidence interval. The code is `osint_cad/doctrine/cost_benefit.py`.

### 2.1 The inputs (per system)
- **`unit_cost_musd`, `quantity`, `rnd_cost_musd`, `annual_oandm_musd`, `service_life_years`** —
  OSINT/order-of-magnitude cost figures (USD millions).
- **`benefit_score` (0–100)** — a qualitative judgment of operational benefit, each with a
  written rationale in `key_benefits`. It is **not** a physics output; it is an analyst
  rating, deliberately coarse.
- **`survivability_score` (0–100)** — how well the system survives modern A2/AD threats
  (RCS/dispersal/concentration), with rationale in `key_risks`.
- **`confidence` (0–1)** — how settled the open-source picture is (e.g. 0.30 for a conceptual
  system, 0.60 for a real program).

### 2.2 The derived metrics
```
lifecycle_cost ($B)            = (rnd + unit_cost·quantity + annual_O&M·quantity·service_life) / 1000
survivability_adjusted_benefit = benefit_score · survivability_score / 100      (0–100)
value_index                    = survivability_adjusted_benefit / lifecycle_cost($B)
benefit_per_billion            = benefit_score / lifecycle_cost($B)
```
**`value_index` is the headline rating: survivability-adjusted benefit delivered per $B of
lifecycle cost. Higher is better.** It deliberately punishes two things at once — paying a
lot, and buying capability that won't survive. That is why the conceptual "Trump-class
battleship" ranks last: very high lifecycle cost **and** low survivability against anti-ship
fires drive its value_index to ≈0.06, far below dispersed/attritable options.

### 2.3 Confidence interval on the rating
A point score implies false precision, so every `value_index` carries a band
(`ProposedSystem.value_ci`):
```
uncertainty (relative σ) = 1 − confidence
value_index CI           = value_index · (1 ± uncertainty·√3)        (clipped at 0)
```
The √3 comes from propagating three independent relative-error sources — cost, benefit, and
survivability — through the ratio. So a confidence-0.30 system shows a very wide band (e.g.
the battleship's ≈0.0–0.14) and a confidence-0.60 program a tighter one. The web UI draws
this as an error bar on each value bar and recomputes it live as you move the sliders.

### 2.4 What the score is NOT
It is a **value-for-money study aid**, not a procurement decision, a prediction, or
operational advice. The benefit/survivability inputs are coarse analyst ratings; treat
rankings as directional and always read the confidence band.

### 2.5 Optimization on top of the score
`optimize_portfolio(budget, side)` is a 0/1 knapsack that selects the mix **maximizing total
survivability-adjusted benefit** under a lifecycle-cost budget — side-neutral, for any side
or all sides. Again: an operations-research value study, not operational guidance.

---

## 3. Code map (where to look)

```
osint_cad/
  physics/        rf_propagation, rcs_models, vlbi
  sensors/        radar models, signal_processing, geolocation_network (GDOP/CRLB)
  geometry/       Physical-Optics RCS, CAD meshes
  targeting/      ballistic / HGV / BVR kinematics & link budgets
  engagements/    kill chains + ew_strategy (actionable EW helpers, shared by web export)
  analysis/       missile_defense (engagement + exchange ratio), radar_coverage (horizon)
  doctrine/       pla/ + dod/ strategy; cost_benefit (scoring + optimizer); hard_facts
scripts/          ew_strategy_analysis, cad_analysis, strategy_reference,
                  export_web_data (→ web JSON), update_cost_data, verify_facts
tests/            physics regression, doctrine/scoring, analysis, facts (237 tests)
web/              Angular 18 app → Firebase Hosting (https://osint-defense.web.app)
```

---

## 4. CI/CD — verified before posting

Nothing is published without the pipeline passing. `.github/workflows/ci.yml` runs on every
push and PR:
- **`test (3.10)` / `test (3.12)`** — the full `pytest` suite (237 tests, incl. the physics
  regression tests) plus smoke-tests of the analysis entry points.
- **`web-build`** — installs the package, runs `scripts/export_web_data.py`, then does a
  production Angular build (`ng build`), so the whole Python→web pipeline is proven to compile.

The site is rebuilt and redeployed (`firebase deploy`) only after the suite is green locally
and the same checks pass in CI. The build/run state is therefore reproducible: `pip install
-e .[dev] && pytest && (cd web && npm ci && npx ng build)`.

---

## 5. Hard-fact corroboration (Tavily)

Key OSINT figures the analysis leans on are registered in `osint_cad/doctrine/hard_facts.py`
and corroborated against current open sources by `scripts/verify_facts.py` (Tavily;
`TAVILY_API_KEY` from a GitHub secret). For each fact it records fresh source URLs and a
status:
- **corroborated** — a comparable figure within ±25% was found in the news;
- **possible_discrepancy** — a comparable figure differing by >25% was found (**flagged for a
  human to review** — the value is never auto-overwritten);
- **sources_refreshed** — sources updated but no comparable figure parsed;
- **lookup_failed** — query error.

A sanity gate ignores parsed numbers outside an order of magnitude (so unrelated figures in
the text don't create false flags). The cost updater (`scripts/update_cost_data.py`) works
the same way for cost figures. Both run weekly via
`.github/workflows/update-cost-data.yml` and only ever propose changes for review — they do
not fabricate numbers. Outputs: `data/fact_checks.json`, `data/proposed_systems.json`.
