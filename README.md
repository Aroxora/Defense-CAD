# Defense-CAD

**Physics-based, open-source-intelligence (OSINT) analysis of modern air- and missile-defense systems.**

Defense-CAD estimates and stress-tests the *published* performance claims of contemporary
air-defense, radar, datalink, and missile systems using **only open-source information** and
**first-principles physics**. Every non-trivial parameter is derived from public observables
(photographs, manufacturer datasheets, published doctrine) combined with textbook physics
(the radar range equation, the Friis transmission equation, electromagnetic scattering,
ITU-R propagation models, and statistical detection theory) — and every result carries an
**explicit uncertainty range and confidence level**.

> **Nothing in this repository is derived from classified or export-controlled sources.**
> The outputs are *estimates with large, documented uncertainties*, intended for education,
> research, and open analysis — not for operational use. See
> [`docs/DISCLAIMER.md`](docs/DISCLAIMER.md) and [Scope & limitations](#scope--limitations).

---

## Why this exists

Public discussion of military systems is full of confident single numbers ("detects at X km",
"sidelobes at Y dB") with no derivation, no uncertainty, and frequently no physical basis.
Defense-CAD takes the opposite approach:

- **Show the work.** Each estimate is a reasoning chain from public observables → physical
  laws → engineering/economic constraints → a numerical conclusion.
- **Quantify uncertainty.** A chain is never "the answer." It is a central value, an
  uncertainty range, and a confidence level, and it is *no stronger than its weakest link*.
- **Be falsifiable.** Every calculation is runnable Python. If an assumption is wrong, change
  it and see how the conclusion moves.
- **Refuse magic.** If a claim cannot be closed with a physically realizable link budget or
  energy budget, it is flagged — not asserted. (See the worked example below.)

---

## A worked example: can a passive ESM "see" an F-35's MADL datalink?

A common claim is that an adversary fighter can passively detect a stealth aircraft's
low-probability-of-intercept (LPI) datalink far beyond radar range. Defense-CAD treats this as
a link-budget problem in
[`reasoning_chains/madl_detection_range.yaml`](reasoning_chains/madl_detection_range.yaml):

| Integration model (N≈500 bursts/s)             | Detection range |
|------------------------------------------------|-----------------|
| Single burst, no integration                   | ~6 km           |
| **Non-coherent √N (realistic for unknown LPI)**| **~21–32 km**   |
| Coherent N (only if waveform/timing is known)  | ~55 km (bound)  |

The key physical point: a non-cooperative receiver that does **not** know the spreading code or
burst timing of an LPI waveform is limited to **non-coherent** integration (SNR gain ∝ √N),
**not** coherent integration (gain ∝ N). Using the correct model, passive detection lands at
**~25 km (15–35 km, 50% confidence)** — *inside* typical radar detection range, not beyond it.
The "free passive warning" advantage largely evaporates. Every number in that chain is
reproduced by a runnable calculation and cross-checked against the link budget.

This is the standard the whole repository is held to.

---

## Repository layout

```
Defense-CAD/
├── reasoning_chains/      Computer-Aided Deduction: parameter derivations (YAML) + validator
│   ├── *.yaml             one reasoning chain per parameter (MADL TX power, J-20 AESA count, …)
│   ├── schema.yaml        formal schema a valid chain must satisfy
│   └── validate.py        checks structure, certainty propagation, uncertainty, physics
├── docs/                  Methodology, physics notes, system analyses, disclaimer
├── <physics library>.py   RF propagation, RCS, signal processing, EW/EP, geolocation, tracking
├── <system models>.py      AESA radars, datalinks, BVR/hypersonic missiles, naval combat systems
├── <engagement sims>.py    BVR / SEAD / detection simulations
├── test_*.py               142 unit/integration tests
├── pyproject.toml          tooling config (ruff, mypy, pytest, coverage)
├── requirements.txt
└── LICENSE                 MIT
```

### Physics library (first-principles, reusable)

| Module | What it models | Physical basis |
|--------|----------------|----------------|
| `rf_propagation.py` | Atmospheric path loss | ITU-R P.676 (gases), P.838 (rain), P.840 (clouds), P.618 (scintillation) |
| `rcs_models.py`, `cad_rcs_calculator.py` | Aspect-dependent radar cross-section | Physical-optics / canonical scatterer estimates with uncertainty |
| `signal_processing.py` | Faint-emission detection | Matched filtering, non-coherent integration, Marcum detection |
| `adaptive_antenna_ep.py` | Adaptive nulling, electronic protection | Phased-array beamforming, sidelobe control |
| `ml_waveform_classifier.py` | Emitter/waveform classification | Feature-based classification of pulse/waveform parameters |
| `vlbi_coherent_processing.py` | Multi-platform coherent processing | TDOA / cross-correlation geolocation |
| `geolocation_network.py` | Emitter geolocation & network inference | TDOA/FDOA multilateration |
| `advanced_tracking.py` | Multi-target tracking | Multi-hypothesis tracking (MHT) |
| `datalink_protocol.py`, `eob_database.py` | Datalink modeling, electronic order of battle | Link budgets, emitter databases |

### System & engagement models

AESA radar performance (`f22_radar_model.py`, `j20_radar_model.py`), BVR missile kinematics and
seekers (`pl15_targeting_model.py`, `aim260_targeting_model.py`, `bvr_engagement.py`),
hypersonic/ballistic trajectories (`df17_hgv_model.py`, `lrhw_hgv_model.py`,
`precision_ballistic_missiles.py`), naval combat systems (`ddg51_model.py`, `type052d_model.py`),
and engagement simulations (`simulation.py`, `operational_simulation.py`,
`sead_engagement_simulation.py`).

---

## Methodology: Computer-Aided Deduction (CAD)

Each `reasoning_chains/*.yaml` file encodes a derivation in a fixed structure:

```
Observable facts (public: photos, datasheets, doctrine)
        ↓
Physical laws (cited; cannot be violated)
        ↓
Engineering & economic constraints (technology limits, cost trade-offs)
        ↓
Logical steps (each with a runnable calculation)
        ↓
Conclusion (central value + uncertainty range + confidence)
```

`validate.py` enforces discipline on every chain:

- required structure is present and steps are sequential;
- physical laws are cited and their equation variables are defined;
- embedded calculations are syntactically valid Python;
- **the stated confidence does not exceed the weakest-link certainty** (a chain is only as
  strong as its least-certain necessary input; the naive independent-product is reported as a
  pessimistic lower bound, not a hard limit);
- the conclusion's uncertainty is consistent with the per-term uncertainty breakdown.

Read more in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) and
[`reasoning_chains/README.md`](reasoning_chains/README.md).

---

## Quick start

Requires Python 3.9+.

```bash
git clone https://github.com/aroxora/defense-cad.git
cd defense-cad
python -m pip install -r requirements.txt   # numpy, scipy, matplotlib, networkx, pytest

# Run the test suite (142 tests)
python -m pytest -q

# Validate every reasoning chain
python reasoning_chains/validate.py reasoning_chains/
```

Use the physics library directly:

```python
import numpy as np
from rf_propagation import OperationalRFPropagation, AtmosphericConditions
from rcs_models import F35ARCSModel

# Atmospheric path loss (ITU-R models) at 14.4 GHz over 50 km in 5 mm/hr rain
rf = OperationalRFPropagation()
loss_db, breakdown = rf.calculate_path_loss(
    tx_pos=np.array([0, 0, 10000.0]),
    rx_pos=np.array([50000.0, 0, 10000.0]),
    frequency_hz=14.4e9,
    conditions=AtmosphericConditions(rain_rate_mm_hr=5.0),
)
print(f"Path loss: {loss_db:.1f} dB")            # ~167 dB

# Aspect-dependent RCS estimate, with confidence
est = F35ARCSModel().calculate_rcs(azimuth_deg=0, elevation_deg=0)
print(f"F-35A nose-on RCS: {est.rcs_dbsm:.1f} dBsm ({est.confidence:.0%} confidence)")
```

---

## Scope & limitations

- **Estimates, not ground truth.** Confidence levels are typically 50–85%. Uncertainty ranges
  are wide on purpose. A result of "~25 km ± 10 km, 50% confidence" means exactly that.
- **Open sources only.** Inputs are public photographs, datasheets, doctrine, and physics
  textbooks. Where a real value is classified, this repository derives a *bounded estimate* and
  says so — it does not claim knowledge of the classified figure.
- **Educational / research use.** This is open analysis in the tradition of public defense
  scholarship. It is not targeting data and is not validated for operational use.
- **Physically constrained.** Claims that cannot be closed with a realizable link/energy budget
  are flagged rather than asserted.

See [`docs/ACCURACY_AND_LIMITATIONS.md`](docs/ACCURACY_AND_LIMITATIONS.md) for a fuller treatment.

---

## Contributing

New analyses are welcome, provided they meet the repository's standard:

1. Add a reasoning chain under `reasoning_chains/` following `schema.yaml`.
2. Cite public sources for every observable fact and every physical law.
3. Show a runnable calculation for each quantitative step.
4. State an uncertainty range and a confidence level — and keep the confidence at or below the
   weakest necessary input.
5. Ensure `python reasoning_chains/validate.py reasoning_chains/` and `python -m pytest` pass.

---

## License

Released under the [MIT License](LICENSE). Copyright (c) 2024–2026 Bo Shang.

---

**Classification:** UNCLASSIFIED // derived entirely from public sources // for public release.
