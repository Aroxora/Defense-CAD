#!/usr/bin/env python3
"""
Proposed-System Cost-Benefit Analysis (strategy CAD).

A neutral, OSINT-grounded cost-benefit framework for *proposed* or *conceptual* defense
systems, so a doctrine/strategy discussion can be checked against acquisition economics and
survivability physics rather than advocacy. Includes a worked, deliberately conceptual
example -- the "Trump-class battleship" of a notional 'Golden Fleet' -- alongside real
comparators (DDG(X), Collaborative Combat Aircraft, Constellation-class frigate).

Cost figures are illustrative OSINT/order-of-magnitude estimates (CBO/GAO/CRS-style public
ranges) with confidence levels. They can be refreshed from open news via
`scripts/update_cost_data.py` (Tavily), which writes data/proposed_systems.json; any keys in
that file OVERRIDE the seed values below.

Descriptive analysis for education/budget study only -- NOT acquisition advice or guidance.

Classification: UNCLASSIFIED // OPEN-SOURCE ANALYSIS // PUBLIC RELEASE
"""

import json
import os
from dataclasses import dataclass, replace
from typing import List, Optional

# data/proposed_systems.json relative to repo root
_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data",
                          "proposed_systems.json")


@dataclass(frozen=True)
class ProposedSystem:
    """One proposed/conceptual system with OSINT cost and benefit estimates."""
    key: str
    name: str
    side: str                       # 'DoD' | 'PLA' | other
    status: str                     # 'conceptual' | 'proposed' | 'development' | 'fielded'
    description: str
    unit_cost_musd: float           # procurement unit cost (USD millions)
    quantity: int                   # planned buy
    rnd_cost_musd: float            # non-recurring R&D (USD millions)
    annual_oandm_musd: float        # operations & sustainment per unit per year (USD millions)
    service_life_years: int
    benefit_score: float            # 0-100 qualitative operational benefit (with rationale)
    survivability_score: float      # 0-100 survivability vs modern A2/AD threats
    key_benefits: List[str]
    key_risks: List[str]
    sources: List[str]
    confidence: float               # 0-1 confidence in the cost/benefit estimate
    news_query: str = ""            # query the news updater uses to refresh cost figures
    last_updated: str = "seed"      # ISO date when figures were last refreshed (or 'seed')

    # ---- derived economics -------------------------------------------------------------
    @property
    def acquisition_cost_musd(self) -> float:
        return self.rnd_cost_musd + self.unit_cost_musd * self.quantity

    @property
    def sustainment_cost_musd(self) -> float:
        return self.annual_oandm_musd * self.quantity * self.service_life_years

    @property
    def lifecycle_cost_busd(self) -> float:
        return (self.acquisition_cost_musd + self.sustainment_cost_musd) / 1000.0

    @property
    def benefit_per_billion(self) -> float:
        """Operational benefit delivered per $B lifecycle cost (higher = better value)."""
        lcc = self.lifecycle_cost_busd
        return (self.benefit_score / lcc) if lcc > 0 else 0.0

    @property
    def survivability_adjusted_benefit(self) -> float:
        """Benefit discounted by survivability vs modern threats (0-100)."""
        return self.benefit_score * self.survivability_score / 100.0

    @property
    def value_index(self) -> float:
        """Survivability-adjusted benefit per $B lifecycle cost -- the headline CBA metric."""
        lcc = self.lifecycle_cost_busd
        return (self.survivability_adjusted_benefit / lcc) if lcc > 0 else 0.0


# --- Seed catalogue (illustrative OSINT estimates) ------------------------------------

_SEED: List[ProposedSystem] = [
    ProposedSystem(
        key="trump_class_battleship",
        name="Trump-class Battleship (conceptual, 'Golden Fleet')",
        side="DoD",
        status="conceptual",
        description=(
            "A notional heavily-armored, big-gun/missile capital ship. Included as a "
            "deliberately conceptual case to show how cost-benefit + survivability physics "
            "evaluate a 'return of the battleship' proposal. NOT a real program."
        ),
        unit_cost_musd=10_000.0,   # order-of-magnitude for a >40 kt armored capital ship
        quantity=4,
        rnd_cost_musd=15_000.0,
        annual_oandm_musd=350.0,
        service_life_years=40,
        benefit_score=35.0,        # heavy firepower/presence, but narrow utility today
        survivability_score=20.0,  # large RCS, concentrated value vs ASBM/ASCM/torpedo/HGV
        key_benefits=[
            "Large magazine and survivable armor vs legacy threats",
            "Presence / deterrence symbolism",
        ],
        key_risks=[
            "High-value, concentrated target for anti-ship ballistic/cruise/hypersonic fires",
            "Very high unit + lifecycle cost; few hulls = brittle force",
            "Runs counter to Distributed Maritime Operations (dispersal) logic",
        ],
        sources=[
            "Conceptual; cost framed by CBO armored-warship/CVN-class order of magnitude",
            "Survivability per public ASBM/ASCM threat analyses (CSIS Missile Threat)",
        ],
        confidence=0.30,
        news_query="battleship OR 'Golden Fleet' capital ship cost proposal navy",
    ),
    ProposedSystem(
        key="ddgx_destroyer",
        name="DDG(X) Next-Generation Guided-Missile Destroyer",
        side="DoD",
        status="development",
        description="USN next-gen destroyer to follow the Arleigh Burke (DDG-51) line.",
        unit_cost_musd=3_300.0,
        quantity=28,
        rnd_cost_musd=6_000.0,
        annual_oandm_musd=60.0,
        service_life_years=35,
        benefit_score=75.0,
        survivability_score=60.0,
        key_benefits=["Networked air/missile defense", "Distributable combat power"],
        key_risks=["Cost growth risk", "Power/cooling for future weapons unproven"],
        sources=["CBO/CRS DDG(X) program estimates (public)"],
        confidence=0.55,
        news_query="DDG(X) destroyer program cost estimate navy",
    ),
    ProposedSystem(
        key="cca_increment1",
        name="Collaborative Combat Aircraft (CCA), Increment 1",
        side="DoD",
        status="development",
        description="Low-cost, semi-autonomous uncrewed combat aircraft teamed with fighters.",
        unit_cost_musd=30.0,
        quantity=1000,
        rnd_cost_musd=4_000.0,
        annual_oandm_musd=1.5,
        service_life_years=15,
        benefit_score=70.0,
        survivability_score=55.0,
        key_benefits=["Affordable mass", "Attritable; complicates adversary targeting"],
        key_risks=["Autonomy maturity", "Datalink dependence (see EW strategy)"],
        sources=["USAF CCA program public statements; CSIS/CBO analyses"],
        confidence=0.50,
        news_query="Collaborative Combat Aircraft CCA cost per unit Air Force",
    ),
    ProposedSystem(
        key="type055_destroyer",
        name="Type 055 (Renhai) Cruiser",
        side="PLA",
        status="fielded",
        description="PLAN large guided-missile cruiser/destroyer (for cross-side comparison).",
        unit_cost_musd=920.0,
        quantity=8,
        rnd_cost_musd=3_000.0,
        annual_oandm_musd=35.0,
        service_life_years=35,
        benefit_score=72.0,
        survivability_score=58.0,
        key_benefits=["Large VLS capacity", "Air-defense and land-attack flexibility"],
        key_risks=["High-value surface unit vs adversary strike", "Open-source cost uncertain"],
        sources=["Public PLAN order-of-battle analyses (USNI, CSIS)"],
        confidence=0.40,
        news_query="Type 055 Renhai cruiser cost PLAN",
    ),
]


def _load_overrides() -> dict:
    """Load data/proposed_systems.json overrides keyed by system key (empty if absent/bad)."""
    try:
        with open(os.path.normpath(_DATA_PATH)) as fh:
            data = json.load(fh)
        return {entry["key"]: entry for entry in data.get("systems", [])}
    except (OSError, ValueError, KeyError):
        return {}


def list_systems() -> List[ProposedSystem]:
    """Seed systems with any news-refreshed overrides applied (by key)."""
    overrides = _load_overrides()
    out: List[ProposedSystem] = []
    for sys in _SEED:
        ov = overrides.get(sys.key)
        if not ov:
            out.append(sys)
            continue
        fields = {k: ov[k] for k in ("unit_cost_musd", "rnd_cost_musd", "annual_oandm_musd",
                                     "quantity", "sources", "confidence", "last_updated")
                  if k in ov}
        out.append(replace(sys, **fields))
    return out


def get_system(key: str) -> ProposedSystem:
    for s in list_systems():
        if s.key == key:
            return s
    raise KeyError(f"unknown proposed system: {key!r}")


def rank_by_value(side: Optional[str] = None) -> List[ProposedSystem]:
    """Systems ranked by value_index (survivability-adjusted benefit per $B), best first."""
    systems = [s for s in list_systems() if side is None or s.side == side]
    return sorted(systems, key=lambda s: s.value_index, reverse=True)


def cost_benefit_report(side: Optional[str] = None) -> str:
    lines = [
        "=" * 96,
        "PROPOSED-SYSTEM COST-BENEFIT ANALYSIS (OSINT, illustrative)",
        "value_index = survivability-adjusted benefit (0-100) per $B lifecycle cost. "
        "NOT acquisition advice.",
        "=" * 96,
        f"{'system':40s} {'side':4s} {'LCC $B':>8s} {'benefit':>8s} {'surv':>5s} "
        f"{'val_idx':>8s} {'conf':>5s}",
        "-" * 96,
    ]
    for s in rank_by_value(side):
        lines.append(
            f"{s.name[:40]:40s} {s.side:4s} {s.lifecycle_cost_busd:8.1f} "
            f"{s.benefit_score:8.0f} {s.survivability_score:5.0f} "
            f"{s.value_index:8.2f} {s.confidence:5.0%}")
    lines += ["-" * 96,
              "Higher value_index = better cost-benefit. Lifecycle = R&D + unit*qty + "
              "O&M*qty*life.",
              "Figures are OSINT/illustrative; refresh via scripts/update_cost_data.py "
              "(Tavily)."]
    return "\n".join(lines)


if __name__ == "__main__":
    print(cost_benefit_report())
