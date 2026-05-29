#!/usr/bin/env python3
"""Run the standalone analytical CAD tools (missile defense + radar coverage)."""

from osint_cad.analysis import missile_defense as md
from osint_cad.analysis import radar_coverage as rc


def main():
    md._demo()
    print("\n")
    rc._demo()


if __name__ == "__main__":
    main()
