# Proposed-System Cost-Benefit Analysis (Strategy CAD)

**Classification: UNCLASSIFIED // OPEN-SOURCE ANALYSIS // PUBLIC RELEASE**

A neutral, OSINT-grounded cost-benefit framework for *proposed* or *conceptual* defense
systems, so a strategy/doctrine discussion can be checked against acquisition economics and
survivability physics rather than advocacy. Backed by
[`osint_cad/doctrine/cost_benefit.py`](osint_cad/doctrine/cost_benefit.py):

```bash
python -m osint_cad.doctrine.cost_benefit          # ranked cost-benefit table
python scripts/strategy_reference.py --cba          # doctrine + cost-benefit together
```

> **Scope / non-goals.** Descriptive analysis for education/budget study only — **not**
> acquisition advice. Cost figures are illustrative OSINT/order-of-magnitude estimates with
> confidence levels.

## Metric

```
lifecycle_cost ($B) = R&D + (unit_cost × quantity) + (annual_O&M × quantity × service_life)
value_index         = survivability_adjusted_benefit / lifecycle_cost($B)
                    = (benefit_score × survivability_score / 100) / lifecycle_cost($B)
```

`benefit_score` and `survivability_score` are 0–100 qualitative scores (each with a stated
rationale and confidence). A **higher `value_index` = better cost-benefit**.

## Worked example: the conceptual "Trump-class battleship"

Included deliberately as a conceptual case (a notional 'Golden Fleet' capital ship — **not a
real program**) to show how the framework evaluates a "return of the battleship" proposal.
The analysis is unflattering for sound physical reasons, and that is the point:

- **Cost:** order-of-magnitude lifecycle cost on par with a small carrier program for only a
  handful of hulls.
- **Survivability (low):** a large-RCS, high-value, concentrated target against modern
  anti-ship ballistic/cruise/hypersonic fires — the same threats modeled in
  `osint_cad/targeting/` and the carrier-strike kill chain.
- **Doctrinal fit (poor):** runs against Distributed Maritime Operations (dispersal), which
  the DoD doctrine reference describes.

Result: it ranks **last** among the modeled DoD options on `value_index`, behind networked,
distributable, or attritable alternatives (DDG(X), CCA). Real comparators and a PLA entry
(Type 055) are included so the comparison is symmetric.

## Auto-updating cost figures from open news

`scripts/update_cost_data.py` queries the **Tavily** API (key from the `TAVILY_API_KEY`
environment variable / GitHub secret) and writes `data/proposed_systems.json`, whose entries
**override** the seed figures. The weekly **“Update cost data (Tavily)”** GitHub Action runs
it and commits any changes. With no key configured it is a graceful no-op, and it only
updates a cost figure when one is confidently parsed from the news — it never fabricates
numbers. See `.github/workflows/update-cost-data.yml`.
