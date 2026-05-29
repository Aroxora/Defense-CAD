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
    domain: str                     # 'air'|'naval'|'subsurface'|'missile'|'hypersonic'|
                                    # 'space'|'c2_network'|'autonomy'|'air_defense'|'ground'
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

    # ---- uncertainty / confidence interval --------------------------------------------
    @property
    def uncertainty(self) -> float:
        """Relative 1-sigma uncertainty on the inputs, derived from confidence.

        Low confidence -> wide band. Modeled as (1 - confidence) treated as the relative
        sigma shared by the cost and benefit/survivability estimates.
        """
        return max(0.0, 1.0 - self.confidence)

    @property
    def value_ci(self) -> tuple:
        """Approximate (low, high) confidence interval on value_index.

        Propagates the relative uncertainty through value = (benefit*surv)/cost. With three
        independent relative-error sources (benefit, survivability, cost) the combined
        relative sigma is u*sqrt(3); the band is +/- that (clipped at 0).
        """
        rel = self.uncertainty * (3 ** 0.5)
        v = self.value_index
        return (max(0.0, v * (1 - rel)), v * (1 + rel))


# --- Seed catalogue (illustrative OSINT estimates) ------------------------------------

_SEED: List[ProposedSystem] = [
    # ----- DoD ------------------------------------------------------------------------
    ProposedSystem(
        key="trump_class_battleship",
        name="Trump-class Battleship (conceptual, 'Golden Fleet')",
        side="DoD", domain="naval", status="conceptual",
        description=("Notional heavily-armored big-gun/missile capital ship. A deliberately "
                     "conceptual case showing how cost-benefit + survivability physics judge "
                     "a 'return of the battleship'. NOT a real program."),
        unit_cost_musd=10_000.0, quantity=4, rnd_cost_musd=15_000.0,
        annual_oandm_musd=350.0, service_life_years=40,
        benefit_score=35.0, survivability_score=20.0,
        key_benefits=["Large magazine/armor vs legacy threats", "Presence/deterrence symbolism"],
        key_risks=["High-value concentrated target for ASBM/ASCM/HGV/torpedo",
                   "Very high lifecycle cost; few hulls = brittle force",
                   "Counter to Distributed Maritime Operations (dispersal)"],
        sources=["Conceptual; cost framed by CBO armored-warship/CVN order of magnitude",
                 "Survivability per public ASBM/ASCM threat analyses (CSIS Missile Threat)"],
        confidence=0.30, news_query="battleship OR 'Golden Fleet' capital ship cost proposal navy"),
    ProposedSystem(
        key="b21_raider",
        name="B-21 Raider Stealth Bomber",
        side="DoD", domain="air", status="development",
        description="Next-gen stealth bomber; penetrating long-range strike.",
        unit_cost_musd=700.0, quantity=100, rnd_cost_musd=25_000.0,
        annual_oandm_musd=25.0, service_life_years=30,
        benefit_score=85.0, survivability_score=80.0,
        key_benefits=["Penetrating stealth strike", "Open-architecture upgradeability"],
        key_risks=["Sustainment cost growth", "Threat IADS evolution"],
        sources=["USAF/GAO B-21 program public estimates", "CBO long-range strike analyses"],
        confidence=0.55, news_query="B-21 Raider bomber unit cost program"),
    ProposedSystem(
        key="columbia_ssbn",
        name="Columbia-class SSBN",
        side="DoD", domain="subsurface", status="development",
        description="Ballistic-missile submarine; survivable strategic deterrent.",
        unit_cost_musd=9_000.0, quantity=12, rnd_cost_musd=15_000.0,
        annual_oandm_musd=110.0, service_life_years=42,
        benefit_score=95.0, survivability_score=95.0,
        key_benefits=["Survivable second-strike (sea-based deterrent)", "Quietness"],
        key_risks=["Schedule risk to deterrent patrols", "Industrial-base constraints"],
        sources=["CBO/CRS Columbia-class estimates (public)"],
        confidence=0.60, news_query="Columbia-class SSBN submarine cost program"),
    ProposedSystem(
        key="ddgx_destroyer",
        name="DDG(X) Next-Generation Guided-Missile Destroyer",
        side="DoD", domain="naval", status="development",
        description="USN next-gen destroyer following the Arleigh Burke line.",
        unit_cost_musd=3_300.0, quantity=28, rnd_cost_musd=6_000.0,
        annual_oandm_musd=60.0, service_life_years=35,
        benefit_score=75.0, survivability_score=60.0,
        key_benefits=["Networked air/missile defense", "Distributable combat power"],
        key_risks=["Cost growth risk", "Power/cooling for future weapons unproven"],
        sources=["CBO/CRS DDG(X) program estimates (public)"],
        confidence=0.55, news_query="DDG(X) destroyer program cost estimate navy"),
    ProposedSystem(
        key="constellation_ffg",
        name="Constellation-class Frigate (FFG-62)",
        side="DoD", domain="naval", status="development",
        description="Multi-mission guided-missile frigate; lower-cost surface combatant.",
        unit_cost_musd=1_300.0, quantity=20, rnd_cost_musd=1_500.0,
        annual_oandm_musd=30.0, service_life_years=30,
        benefit_score=68.0, survivability_score=55.0,
        key_benefits=["Affordable distributed surface combatant", "Proven parent design"],
        key_risks=["Design-change-driven schedule slip", "Weight/margin growth"],
        sources=["GAO/CRS FFG-62 program reports (public)"],
        confidence=0.55, news_query="Constellation class frigate FFG-62 cost"),
    ProposedSystem(
        key="ngad_fighter",
        name="NGAD Air-Dominance Fighter",
        side="DoD", domain="air", status="development",
        description="Next-Generation Air Dominance crewed fighter (teamed with CCA).",
        unit_cost_musd=300.0, quantity=200, rnd_cost_musd=16_000.0,
        annual_oandm_musd=20.0, service_life_years=30,
        benefit_score=82.0, survivability_score=75.0,
        key_benefits=["Penetrating counter-air", "CCA teaming/quarterback"],
        key_risks=["Very high unit cost (affordability review)", "Requirements churn"],
        sources=["USAF NGAD public statements; CSIS/CBO analyses"],
        confidence=0.45, news_query="NGAD fighter cost per unit Air Force program"),
    ProposedSystem(
        key="cca_increment1",
        name="Collaborative Combat Aircraft (CCA), Increment 1",
        side="DoD", domain="autonomy", status="development",
        description="Low-cost, semi-autonomous uncrewed combat aircraft teamed with fighters.",
        unit_cost_musd=30.0, quantity=1000, rnd_cost_musd=4_000.0,
        annual_oandm_musd=1.5, service_life_years=15,
        benefit_score=70.0, survivability_score=55.0,
        key_benefits=["Affordable mass", "Attritable; complicates adversary targeting"],
        key_risks=["Autonomy maturity", "Datalink dependence (see EW strategy)"],
        sources=["USAF CCA program public statements; CSIS/CBO analyses"],
        confidence=0.50, news_query="Collaborative Combat Aircraft CCA cost per unit Air Force"),
    ProposedSystem(
        key="sentinel_icbm",
        name="LGM-35A Sentinel ICBM",
        side="DoD", domain="missile", status="development",
        description="Ground-based strategic deterrent replacing Minuteman III.",
        unit_cost_musd=160.0, quantity=634, rnd_cost_musd=40_000.0,
        annual_oandm_musd=2.0, service_life_years=50,
        benefit_score=80.0, survivability_score=45.0,
        key_benefits=["Modernized land leg of the triad", "Responsiveness"],
        key_risks=["Major Nunn-McCurdy cost breach (public)", "Silo basing survivability debate"],
        sources=["USAF/GAO Sentinel program; public Nunn-McCurdy reporting"],
        confidence=0.55, news_query="Sentinel LGM-35A ICBM cost overrun program"),
    ProposedSystem(
        key="sda_leo_layer",
        name="Proliferated LEO Sensor/Transport Layer (SDA)",
        side="DoD", domain="space", status="development",
        description="Resilient mesh of small LEO satellites for missile tracking + transport.",
        unit_cost_musd=40.0, quantity=400, rnd_cost_musd=6_000.0,
        annual_oandm_musd=2.0, service_life_years=7,
        benefit_score=78.0, survivability_score=70.0,
        key_benefits=["Resilience via proliferation", "Hypersonic/missile tracking"],
        key_risks=["Launch cadence/cost", "Ground segment & data fusion maturity"],
        sources=["Space Development Agency public tranches; CSIS analyses"],
        confidence=0.50, news_query="Space Development Agency proliferated LEO satellites cost"),
    # ----- PLA ------------------------------------------------------------------------
    ProposedSystem(
        key="type055_destroyer",
        name="Type 055 (Renhai) Cruiser",
        side="PLA", domain="naval", status="fielded",
        description="PLAN large guided-missile cruiser/destroyer (cross-side comparison).",
        unit_cost_musd=920.0, quantity=8, rnd_cost_musd=3_000.0,
        annual_oandm_musd=35.0, service_life_years=35,
        benefit_score=72.0, survivability_score=58.0,
        key_benefits=["Large VLS capacity", "Air-defense + land-attack flexibility"],
        key_risks=["High-value surface unit vs adversary strike", "Open-source cost uncertain"],
        sources=["Public PLAN order-of-battle analyses (USNI, CSIS)"],
        confidence=0.40, news_query="Type 055 Renhai cruiser cost PLAN"),
    ProposedSystem(
        key="type003_carrier",
        name="Type 003 (Fujian) Aircraft Carrier",
        side="PLA", domain="naval", status="development",
        description="PLAN CATOBAR aircraft carrier.",
        unit_cost_musd=8_000.0, quantity=2, rnd_cost_musd=10_000.0,
        annual_oandm_musd=300.0, service_life_years=40,
        benefit_score=78.0, survivability_score=40.0,
        key_benefits=["Power projection / sortie generation", "CATOBAR airwing flexibility"],
        key_risks=["High-value target within A2/AD reach", "Carrier-ops maturity"],
        sources=["USNI/CSIS public PLAN carrier analyses"],
        confidence=0.35, news_query="Type 003 Fujian carrier cost PLAN"),
    ProposedSystem(
        key="df17_hgv",
        name="DF-17 Hypersonic Glide Vehicle (MRBM)",
        side="PLA", domain="hypersonic", status="fielded",
        description="Road-mobile MRBM with a hypersonic glide vehicle.",
        unit_cost_musd=15.0, quantity=200, rnd_cost_musd=5_000.0,
        annual_oandm_musd=0.4, service_life_years=20,
        benefit_score=74.0, survivability_score=72.0,
        key_benefits=["Maneuvering reentry stresses defenses", "Road-mobile launcher survivability"],
        key_risks=["Terminal accuracy uncertain (open source)", "Defense GPI development"],
        sources=["CSIS Missile Threat; DoD China Military Power Report"],
        confidence=0.40, news_query="DF-17 hypersonic glide vehicle PLA"),
    ProposedSystem(
        key="df41_icbm",
        name="DF-41 ICBM",
        side="PLA", domain="missile", status="fielded",
        description="Road-mobile/silo ICBM; strategic deterrent.",
        unit_cost_musd=30.0, quantity=100, rnd_cost_musd=8_000.0,
        annual_oandm_musd=0.6, service_life_years=30,
        benefit_score=85.0, survivability_score=60.0,
        key_benefits=["Long-range strategic reach", "Road-mobile basing options"],
        key_risks=["Silo-field survivability debate", "Open-source figures uncertain"],
        sources=["CSIS Missile Threat; DoD China Military Power Report"],
        confidence=0.35, news_query="DF-41 ICBM PLA road mobile"),
    ProposedSystem(
        key="j35_fighter",
        name="J-35 / FC-31 Stealth Fighter",
        side="PLA", domain="air", status="development",
        description="Medium stealth fighter (land- and carrier-based variants).",
        unit_cost_musd=80.0, quantity=200, rnd_cost_musd=8_000.0,
        annual_oandm_musd=6.0, service_life_years=30,
        benefit_score=70.0, survivability_score=62.0,
        key_benefits=["Carrier-capable stealth airwing", "Fleet stealth mass"],
        key_risks=["Engine/sensor maturity (open source)", "Cost figures uncertain"],
        sources=["USNI/CSIS public PLAAF/PLAN aviation analyses"],
        confidence=0.35, news_query="J-35 FC-31 stealth fighter China cost"),
    ProposedSystem(
        key="h20_bomber",
        name="H-20 Stealth Bomber (conceptual/R&D)",
        side="PLA", domain="air", status="conceptual",
        description="Reported PLAAF stealth bomber program; largely developmental in open sources.",
        unit_cost_musd=650.0, quantity=100, rnd_cost_musd=20_000.0,
        annual_oandm_musd=22.0, service_life_years=30,
        benefit_score=80.0, survivability_score=78.0,
        key_benefits=["Penetrating long-range strike (if fielded)", "Extends strike reach"],
        key_risks=["Program maturity unconfirmed (open source)", "Figures highly uncertain"],
        sources=["DoD China Military Power Report; public PLAAF analyses"],
        confidence=0.25, news_query="H-20 stealth bomber China program"),
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


def rank_by_value(side: Optional[str] = None,
                  domain: Optional[str] = None) -> List[ProposedSystem]:
    """Systems ranked by value_index (survivability-adjusted benefit per $B), best first."""
    systems = [s for s in list_systems()
               if (side is None or s.side == side) and (domain is None or s.domain == domain)]
    return sorted(systems, key=lambda s: s.value_index, reverse=True)


def domains() -> List[str]:
    """Sorted list of domains present in the catalogue."""
    return sorted({s.domain for s in list_systems()})


def optimize_portfolio(budget_busd: float, side: Optional[str] = None) -> dict:
    """Pick the procurement mix that MAXIMIZES total survivability-adjusted benefit under a
    lifecycle-cost budget (a 0/1 knapsack). Side-neutral: pass side=None for all sides, or a
    side string. This is analytical operations-research -- a value-for-money study of *what
    to buy with a fixed budget*, NOT operational guidance.

    Returns {selected: [systems], total_cost_busd, total_benefit, budget_busd}.
    """
    items = [s for s in list_systems() if side is None or s.side == side]
    cap = max(0, int(round(budget_busd)))
    # weights in whole $B (>=1 so every program consumes budget); values = adjusted benefit
    weights = [max(1, int(round(s.lifecycle_cost_busd))) for s in items]
    values = [s.survivability_adjusted_benefit for s in items]

    # 0/1 knapsack DP over integer $B budget
    dp = [0.0] * (cap + 1)
    keep = [[False] * (cap + 1) for _ in items]
    for i, (w, v) in enumerate(zip(weights, values)):
        for b in range(cap, w - 1, -1):
            cand = dp[b - w] + v
            if cand > dp[b]:
                dp[b] = cand
                keep[i][b] = True

    # backtrack
    chosen, b = [], cap
    for i in range(len(items) - 1, -1, -1):
        if b >= 0 and keep[i][b]:
            chosen.append(items[i])
            b -= weights[i]
    chosen.reverse()
    return {
        "budget_busd": budget_busd,
        "selected": chosen,
        "total_cost_busd": round(sum(s.lifecycle_cost_busd for s in chosen), 1),
        "total_benefit": round(sum(s.survivability_adjusted_benefit for s in chosen), 1),
    }


def optimize_report(budget_busd: float, side: Optional[str] = None) -> str:
    res = optimize_portfolio(budget_busd, side)
    who = side or "ALL sides"
    lines = [
        "=" * 88,
        f"VALUE-MAXIMIZING PORTFOLIO under ${budget_busd:.0f}B lifecycle budget ({who})",
        "Maximizes survivability-adjusted benefit per the cost-benefit model. "
        "Analytical value-for-money study; NOT acquisition or operational guidance.",
        "=" * 88,
    ]
    for s in sorted(res["selected"], key=lambda x: x.value_index, reverse=True):
        lines.append(f"  + {s.name[:48]:48s} {s.side:4s} {s.domain:11s} "
                     f"${s.lifecycle_cost_busd:7.1f}B  val {s.value_index:5.2f}")
    lines += ["-" * 88,
              f"  selected {len(res['selected'])} programs | spend "
              f"${res['total_cost_busd']:.1f}B / ${budget_busd:.0f}B | "
              f"total adjusted benefit {res['total_benefit']:.1f}"]
    return "\n".join(lines)


def cost_benefit_report(side: Optional[str] = None) -> str:
    lines = [
        "=" * 96,
        "PROPOSED-SYSTEM COST-BENEFIT ANALYSIS (OSINT, illustrative)",
        "value_index = survivability-adjusted benefit (0-100) per $B lifecycle cost. "
        "NOT acquisition advice.",
        "=" * 96,
        f"{'system':40s} {'side':4s} {'LCC $B':>8s} {'surv':>5s} "
        f"{'value_index (90% CI)':>26s} {'conf':>5s}",
        "-" * 96,
    ]
    for s in rank_by_value(side):
        lo, hi = s.value_ci
        ci = f"{s.value_index:5.2f} [{lo:4.2f}-{hi:4.2f}]"
        lines.append(
            f"{s.name[:40]:40s} {s.side:4s} {s.lifecycle_cost_busd:8.1f} "
            f"{s.survivability_score:5.0f} {ci:>26s} {s.confidence:5.0%}")
    lines += ["-" * 96,
              "Higher value_index = better cost-benefit. Lifecycle = R&D + unit*qty + "
              "O&M*qty*life.",
              "Figures are OSINT/illustrative; refresh via scripts/update_cost_data.py "
              "(Tavily)."]
    return "\n".join(lines)


def procurement_portfolio_report(side: Optional[str] = None) -> str:
    """Procurement & R&D portfolio view: best-value option per domain, per side.

    A neutral OSINT 'where does investment buy the most survivable benefit per dollar'
    study across all domains -- NOT acquisition advice or guidance.
    """
    sides = [side] if side else sorted({s.side for s in list_systems()})
    lines = [
        "=" * 96,
        "PROCUREMENT & R&D PORTFOLIO -- BEST VALUE PER DOMAIN (OSINT, illustrative)",
        "Neutral study of survivability-adjusted benefit per $B. NOT acquisition advice.",
        "=" * 96,
    ]
    for sd in sides:
        lines += ["", f"### {sd}", "-" * 96,
                  f"{'domain':14s} {'top-value system':42s} {'LCC $B':>8s} {'val_idx':>8s}"]
        for dom in domains():
            ranked = rank_by_value(side=sd, domain=dom)
            if not ranked:
                continue
            best = ranked[0]
            lines.append(f"{dom:14s} {best.name[:42]:42s} "
                         f"{best.lifecycle_cost_busd:8.1f} {best.value_index:8.2f}")
    lines += ["", "Higher val_idx = better value. Status mix spans fielded/development/"
              "conceptual; see confidence per system in cost_benefit_report()."]
    return "\n".join(lines)


if __name__ == "__main__":
    print(cost_benefit_report())
    print("\n")
    print(procurement_portfolio_report())
    print("\n")
    print(optimize_report(150.0))  # value-maximizing mix under $150B, all sides
