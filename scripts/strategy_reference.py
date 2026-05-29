#!/usr/bin/env python3
"""
Print the OSINT strategy/doctrine references (PLA and DoD) plus the proposed-system
cost-benefit analysis, and the doctrine<->modeled-system cross-reference.

Descriptive open-source analysis for study/education only -- NOT operational guidance.
"""

import argparse

from osint_cad.doctrine.pla import strategy as pla
from osint_cad.doctrine.dod import strategy as dod
from osint_cad.doctrine import cost_benefit as cb


def _print_cross_ref(name, mod):
    print(f"\n{'=' * 88}\n{name}: MODELED-SYSTEM -> DOCTRINE CROSS-REFERENCE\n{'=' * 88}")
    for sysname, keys in sorted(mod.systems_to_concepts().items()):
        print(f"  {sysname:32s} -> {', '.join(keys)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--side", choices=["pla", "dod", "both"], default="both")
    ap.add_argument("--cba", action="store_true", help="also show cost-benefit analysis")
    args = ap.parse_args()

    if args.side in ("pla", "both"):
        print(pla.summary_report())
        _print_cross_ref("PLA", pla)
    if args.side in ("dod", "both"):
        print("\n" + dod.summary_report())
        _print_cross_ref("DoD", dod)
    if args.cba or args.side == "both":
        print("\n" + cb.cost_benefit_report())


if __name__ == "__main__":
    main()
