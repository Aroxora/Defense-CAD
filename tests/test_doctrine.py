#!/usr/bin/env python3
"""Tests for the OSINT doctrine references (PLA, DoD) and proposed-system cost-benefit."""

import pytest

from osint_cad.doctrine.pla import strategy as pla
from osint_cad.doctrine.dod import strategy as dod
from osint_cad.doctrine import cost_benefit as cb


@pytest.mark.parametrize("mod,expect_key", [
    (pla, "systems_confrontation"),
    (dod, "cjadc2"),
])
def test_strategy_modules_well_formed(mod, expect_key):
    concepts = mod.list_concepts()
    assert len(concepts) >= 5
    assert expect_key in {c.key for c in concepts}
    for c in concepts:
        assert c.name_en and c.name_native and c.summary
        assert c.public_sources, f"{c.key} must cite open sources"
        assert c.related_systems, f"{c.key} must map to modeled areas"
        assert 0.0 < c.confidence <= 1.0
    # reverse index round-trips
    idx = mod.systems_to_concepts()
    for c in concepts:
        for sysname in c.related_systems:
            assert c.key in idx[sysname]
    # report self-identifies as non-operational
    assert "NOT operational guidance" in mod.summary_report()


def test_pla_and_dod_are_distinct():
    assert pla.SIDE != dod.SIDE
    assert {c.key for c in pla.list_concepts()} != {c.key for c in dod.list_concepts()}


def test_cost_benefit_economics_and_ranking():
    systems = cb.list_systems()
    keys = {s.key for s in systems}
    assert "trump_class_battleship" in keys

    bb = cb.get_system("trump_class_battleship")
    # lifecycle = R&D + unit*qty + O&M*qty*life
    expected_lcc = (bb.rnd_cost_musd + bb.unit_cost_musd * bb.quantity
                    + bb.annual_oandm_musd * bb.quantity * bb.service_life_years) / 1000.0
    assert bb.lifecycle_cost_busd == pytest.approx(expected_lcc)
    assert bb.value_index == pytest.approx(
        bb.benefit_score * bb.survivability_score / 100.0 / bb.lifecycle_cost_busd)

    # The conceptual battleship should rank as poor value among DoD options.
    dod_ranked = cb.rank_by_value(side="DoD")
    assert dod_ranked[-1].key == "trump_class_battleship"
    assert "NOT acquisition advice" in cb.cost_benefit_report()


def test_cost_benefit_multidomain_portfolio():
    systems = cb.list_systems()
    # broad procurement/R&D coverage across both sides and several domains
    assert len(systems) >= 12
    assert {"PLA", "DoD"} <= {s.side for s in systems}
    assert len(cb.domains()) >= 5
    # every system has a domain and the portfolio report is non-operational
    assert all(s.domain for s in systems)
    report = cb.procurement_portfolio_report()
    assert "NOT acquisition advice" in report
    # per-side filtering works
    assert all(s.side == "PLA" for s in cb.rank_by_value(side="PLA"))


def test_value_confidence_intervals():
    systems = cb.list_systems()
    for s in systems:
        lo, hi = s.value_ci
        assert lo <= s.value_index <= hi
        assert lo >= 0.0
    # lower confidence -> wider relative band
    lowest = min(systems, key=lambda s: s.confidence)
    highest = max(systems, key=lambda s: s.confidence)
    width = lambda s: (s.value_ci[1] - s.value_ci[0]) / max(s.value_index, 1e-9)
    assert width(lowest) > width(highest)


def test_portfolio_optimizer_respects_budget_and_maximizes():
    budget = 100.0
    res = cb.optimize_portfolio(budget, side="DoD")
    assert res["total_cost_busd"] <= budget + 1e-6
    assert all(s.side == "DoD" for s in res["selected"])
    # selecting nothing would be worse; the optimizer must pick at least one affordable item
    assert res["total_benefit"] > 0
    # a larger budget never reduces achievable benefit
    bigger = cb.optimize_portfolio(budget * 3, side="DoD")
    assert bigger["total_benefit"] >= res["total_benefit"]
    assert "NOT acquisition or operational guidance" in cb.optimize_report(budget)
