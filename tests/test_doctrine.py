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
