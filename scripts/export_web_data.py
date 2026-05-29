#!/usr/bin/env python3
"""
Export the actionable analysis to JSON for the Angular/Firebase web app.

Writes web/src/assets/data/{cost_benefit,doctrine,ew_strategy}.json straight from the
osint_cad.* models so the web UI never drifts from the Python source of truth. Run before
building/deploying the web app (the CI/web build can call this).

Usage:  python scripts/export_web_data.py
"""

import json
import os

from osint_cad.doctrine import cost_benefit as cb
from osint_cad.doctrine.pla import strategy as pla
from osint_cad.doctrine.dod import strategy as dod
from osint_cad.engagements import ew_strategy as ew

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "web", "public", "data")


def _system_dict(s: cb.ProposedSystem) -> dict:
    return {
        "key": s.key, "name": s.name, "side": s.side, "domain": s.domain,
        "status": s.status, "description": s.description,
        "unit_cost_musd": s.unit_cost_musd, "quantity": s.quantity,
        "rnd_cost_musd": s.rnd_cost_musd, "annual_oandm_musd": s.annual_oandm_musd,
        "service_life_years": s.service_life_years,
        "benefit_score": s.benefit_score, "survivability_score": s.survivability_score,
        "key_benefits": s.key_benefits, "key_risks": s.key_risks,
        "sources": s.sources, "confidence": s.confidence, "last_updated": s.last_updated,
        # derived (the UI also recomputes these live when sliders move)
        "lifecycle_cost_busd": round(s.lifecycle_cost_busd, 2),
        "benefit_per_billion": round(s.benefit_per_billion, 3),
        "value_index": round(s.value_index, 3),
        "value_ci_low": round(s.value_ci[0], 3),
        "value_ci_high": round(s.value_ci[1], 3),
        "uncertainty": round(s.uncertainty, 3),
    }


def _concept_dict(c) -> dict:
    return {
        "key": c.key, "name_en": c.name_en, "name_native": c.name_native,
        "summary": c.summary, "public_sources": c.public_sources,
        "related_systems": c.related_systems, "analytical_notes": c.analytical_notes,
        "confidence": c.confidence,
    }


def main():
    os.makedirs(os.path.normpath(OUT_DIR), exist_ok=True)

    cost = {"systems": [_system_dict(s) for s in cb.rank_by_value()]}
    doctrine = {
        "pla": {"side": pla.SIDE,
                "concepts": [_concept_dict(c) for c in pla.list_concepts()],
                "systems_to_concepts": pla.systems_to_concepts()},
        "dod": {"side": dod.SIDE,
                "concepts": [_concept_dict(c) for c in dod.list_concepts()],
                "systems_to_concepts": dod.systems_to_concepts()},
    }
    ew_data = ew.export()

    for name, payload in [("cost_benefit", cost), ("doctrine", doctrine),
                          ("ew_strategy", ew_data)]:
        path = os.path.normpath(os.path.join(OUT_DIR, f"{name}.json"))
        with open(path, "w") as fh:
            json.dump(payload, fh, indent=2)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
