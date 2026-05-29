# U.S. DoD Strategy & Doctrine — OSINT Analytical Reference

**Classification: UNCLASSIFIED // OPEN-SOURCE ANALYSIS // PUBLIC RELEASE**

Symmetric counterpart to [`PLA_STRATEGY_OSINT.md`](PLA_STRATEGY_OSINT.md): an open-source,
descriptive reference on publicly documented U.S. Department of Defense strategic/operational
concepts, cross-referenced to the repo's physics/CAD models. Backed by
[`osint_cad/doctrine/dod/strategy.py`](osint_cad/doctrine/dod/strategy.py):

```bash
python scripts/strategy_reference.py --side dod
```

> **Scope / non-goals.** Descriptive analysis for education and open study only — **not**
> operational guidance. PLA and DoD doctrine are kept in distinct packages
> (`osint_cad/doctrine/{pla,dod}/`) so each side is modeled neutrally and symmetrically.

## Concepts covered (all from open sources)

| Concept | What it is (OSINT) | Modeled areas to study it with | Conf. |
|---|---|---|---|
| Integrated Deterrence (2022 NDS) | Combine capabilities across domains/theaters/allies so deterrence is mutually reinforcing | `us_2025_defense_systems`, `integrated_kill_system`, `information_chain_robustness` | 75% |
| Combined Joint All-Domain C2 (CJADC2) | Connect any-sensor/any-shooter across services & domains into a resilient data fabric | `american_integrated_link`, `network_centric_killchain`, `integrated_kill_chain_cad` | 70% |
| Mosaic Warfare (DARPA) | Compose many low-cost, attritable, disaggregated systems into adaptable mosaics | `network_centric_killchain`, `information_chain_robustness`, `advanced_tracking` | 60% |
| Distributed Maritime Operations (USN) | Distribute combat power across more, widely-spaced nodes; mass fires via networking | `ddg51_model`, `carrier_strike_kill_chain`, `us_2025_defense_systems` | 65% |
| Agile Combat Employment (USAF) | Operate from dispersed, austere locations to complicate adversary targeting | `f35_integrated_kill_chain`, `f35_infrastructure_strike` | 65% |
| Replicator / Attritable Autonomy | Field large numbers of low-cost autonomous systems quickly (developmental) | `iterative_classifier`, `ml_waveform_classifier`, `advanced_tracking` | 45% |

## Representative open sources

- U.S. DoD, *2022 National Defense Strategy*; DoD *CJADC2 Strategy* (public summary).
- DARPA Strategic Technology Office (Mosaic Warfare); CSBA, *Mosaic Warfare* (2020).
- CNO *Navigation Plan* (DMO); USAF doctrine note on Agile Combat Employment.
- CRS/CSIS/CNAS open analyses; DoD Replicator announcements.

*(Confidence reflects how settled each open-source characterization is; developmental
concepts are scored lower.)*

## How to use it

Read a concept, open the modeled areas it lists, and run the matching analysis script
(`scripts/run_integrated_kill_chain.py`, `scripts/ew_strategy_analysis.py`,
`scripts/strategy_reference.py`). Use `systems_to_concepts()` to go from a modeled system to
the doctrinal ideas that reference it. The goal is comprehension and neutral, symmetric
analysis.
