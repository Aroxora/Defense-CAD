# PLA Strategy & Doctrine — OSINT Analytical Reference

**Classification: UNCLASSIFIED // OPEN-SOURCE ANALYSIS // PUBLIC RELEASE**

This document is an **open-source, descriptive reference** on publicly documented People's
Liberation Army (PLA) strategic and operational concepts, provided so the physics/CAD
models in this repo can be **studied in their doctrinal context**. It is backed by the
machine-readable module [`osint_cad/doctrine/pla/strategy.py`](osint_cad/doctrine/pla/strategy.py):

```bash
python scripts/strategy_reference.py --side pla
```

> **See also:** [`DOD_STRATEGY_OSINT.md`](DOD_STRATEGY_OSINT.md) (the symmetric U.S. DoD
> reference) and [`COST_BENEFIT_ANALYSIS.md`](COST_BENEFIT_ANALYSIS.md) (proposed-system
> cost-benefit). PLA and DoD doctrine live in distinct packages under
> `osint_cad/doctrine/{pla,dod}/`.

> **Scope / non-goals.** This is descriptive analysis for **education and open study**, the
> same treatment that would apply to any military's published doctrine. It is **not**
> operational guidance, target planning, or advice to improve any force's combat
> effectiveness. Every concept is characterized as *outside analysts publicly understand it*,
> with a stated confidence level, and is cross-referenced to the repo's models so you can run
> **defensive/robustness sensitivity studies** — not strike plans.

## Why include doctrine in a physics repo?

Physics tells you what a sensor or weapon *can* do; doctrine tells you *how a force says it
intends to use systems together*. Pairing the two lets a student or analyst ask grounded
questions — e.g. "the systems-confrontation idea stresses degrading sensor-to-shooter
cohesion; in our modeled kill chain, which single node dominates the track-quality budget,
and how much does redundancy buy?" That is exactly what
[`information_chain_robustness`](osint_cad/engagements/information_chain_robustness.py) and
the integrated kill-chain models already compute.

## Concepts covered (all from open sources)

| Concept (EN / 中文) | What it is (OSINT) | Modeled areas to study it with | Conf. |
|---|---|---|---|
| Systems Confrontation / 体系对抗 · 系统破击战 | War as a clash of rival operational *systems of systems*; emphasis on breaking sensor-to-shooter cohesion, not platform attrition | `integrated_kill_chain_cad`, `network_centric_killchain`, `information_chain_robustness` | 70% |
| Anti-Access / Area-Denial (Counter-Intervention) / 反介入·区域拒止 | Layered capabilities to raise cost/risk of operating within the island chains | `precision_ballistic_missiles`, `air_defense_targets`, `carrier_strike_kill_chain` | 65% |
| Informatized Warfare / 信息化战争 | Networked information dominance (ISR, links, PNT, EW) as the decisive enabler | `signal_processing`, `geolocation_network`, `datalink_protocol`, `adaptive_antenna_ep` | 70% |
| Intelligentized Warfare / 智能化战争 | AI/autonomy layered on informatized systems (largely developmental in open sources) | `iterative_classifier`, `ml_waveform_classifier`, `advanced_tracking` | 45% |
| Reconnaissance-Strike Complex / “Kill Web” / 侦察打击体系 | Closed, redundant sensor→C2→precision-fires loop realizing the above | `integrated_kill_chain_cad`, `df17_hypersonic_kill_chain`, `network_centric_killchain` | 65% |

## Representative open sources

- U.S. DoD, annual *Military and Security Developments Involving the People's Republic of China* (China Military Power Report).
- RAND, *Systems Confrontation and System Destruction Warfare* (Engstrom, 2018).
- China Aerospace Studies Institute (CASI) translations and analyses; CSIS Missile Threat; USNI.
- Public editions/translations of the PLA Academy of Military Science *Science of Military Strategy*.

*(Citations are to widely-available open literature; consult the originals for authoritative wording. Confidence levels reflect how settled each open-source characterization is.)*

## How to use it

- Read a concept, then open the modeled areas it lists and run the corresponding analysis
  script (e.g. `scripts/run_integrated_kill_chain.py`,
  `scripts/ew_strategy_analysis.py`) to see the physics behind it.
- Use `systems_to_concepts()` to go the other way — pick a modeled system and see which
  doctrinal ideas reference it.

The intent is comprehension and neutral analysis, consistent with the rest of this
conceptual, public-release toolkit.
