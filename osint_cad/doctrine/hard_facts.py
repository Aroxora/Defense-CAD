#!/usr/bin/env python3
"""
Registry of "hard facts" -- the key OSINT figures the analysis leans on -- so they can be
periodically corroborated against current open sources (see scripts/verify_facts.py, which
uses Tavily). Each fact carries the value used, a unit, the query to corroborate it, seed
sources, and an analyst confidence.

These are open-source estimates, not ground truth. The verifier records corroborating
sources and flags a POSSIBLE discrepancy only when a clearly different figure is parsed --
it never silently overwrites a value.

Classification: UNCLASSIFIED // OPEN-SOURCE ANALYSIS // PUBLIC RELEASE
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class HardFact:
    key: str
    claim: str                 # human-readable statement of the fact
    value: float               # the figure currently used in the models
    unit: str                  # 'USD_million' | 'km' | 'm2' | 'mach' | ...
    query: str                 # search query to corroborate it
    sources: List[str]
    confidence: float          # 0-1


HARD_FACTS: List[HardFact] = [
    HardFact("f35_frontal_rcs", "F-35 frontal RCS (best public estimate)", 0.0002, "m2",
             "F-35 radar cross section estimate frontal",
             ["Public RCS estimates (Aviation Week, academic)"], 0.45),
    HardFact("b21_unit_cost", "B-21 Raider average procurement unit cost", 700.0, "USD_million",
             "B-21 Raider unit cost estimate",
             ["USAF/GAO public estimates"], 0.55),
    HardFact("ddgx_unit_cost", "DDG(X) lead/early unit cost", 3300.0, "USD_million",
             "DDG(X) destroyer cost estimate",
             ["CBO/CRS DDG(X) reports"], 0.55),
    HardFact("sentinel_program_cost", "Sentinel ICBM R&D/program cost (order of magnitude)",
             40000.0, "USD_million", "Sentinel ICBM cost overrun program",
             ["USAF/GAO; Nunn-McCurdy reporting"], 0.55),
    HardFact("df17_terminal_mach", "DF-17 HGV terminal speed (open-source)", 5.0, "mach",
             "DF-17 hypersonic glide vehicle speed range",
             ["CSIS Missile Threat; DoD CMPR"], 0.40),
    HardFact("madl_band_ghz", "MADL operating band (open-source, Ku-band)", 14.4, "GHz",
             "MADL Multifunction Advanced Data Link frequency band",
             ["Public datalink analyses"], 0.40),
    HardFact("columbia_unit_cost", "Columbia-class SSBN unit cost", 9000.0, "USD_million",
             "Columbia class submarine cost per boat",
             ["CBO/CRS Columbia reports"], 0.60),
    HardFact("type055_full_load_t", "Type 055 full-load displacement", 13000.0, "tonnes",
             "Type 055 Renhai displacement tonnes",
             ["USNI/CSIS PLAN analyses"], 0.50),
]


def list_facts() -> List[HardFact]:
    return list(HARD_FACTS)


def get_fact(key: str) -> HardFact:
    for f in HARD_FACTS:
        if f.key == key:
            return f
    raise KeyError(f"unknown hard fact: {key!r}")
