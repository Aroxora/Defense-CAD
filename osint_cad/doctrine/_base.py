#!/usr/bin/env python3
"""
Shared types/helpers for OSINT doctrine references.

A `DoctrineConcept` is a neutral, open-source characterization of one published military
strategic/operational concept, cross-referenced to the OSINT physics models in this repo so
the concept can be *studied* (defensive/robustness/sensitivity analysis) -- never planned.

Classification: UNCLASSIFIED // OPEN-SOURCE ANALYSIS // PUBLIC RELEASE
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class DoctrineConcept:
    """One publicly-documented strategic/operational concept (OSINT characterization)."""
    key: str
    name_en: str
    name_native: str                  # native-language term as commonly published
    summary: str                      # neutral, OSINT-level description
    public_sources: List[str]         # representative open-source references
    related_systems: List[str]        # OSINT-modeled systems/areas in this repo it touches
    analytical_notes: str             # how the repo's physics can be used to STUDY it
    confidence: float                 # analyst confidence in this open-source characterization


def get_concept(concepts: List[DoctrineConcept], key: str) -> DoctrineConcept:
    """Look up a concept by key (raises KeyError if unknown)."""
    for c in concepts:
        if c.key == key:
            return c
    raise KeyError(f"unknown doctrine concept: {key!r}")


def systems_to_concepts(concepts: List[DoctrineConcept]) -> Dict[str, List[str]]:
    """Reverse index: modeled system/area -> concept keys that reference it."""
    index: Dict[str, List[str]] = {}
    for c in concepts:
        for sysname in c.related_systems:
            index.setdefault(sysname, []).append(c.key)
    return index


def render_report(title: str, subtitle: str, concepts: List[DoctrineConcept]) -> str:
    """Human-readable, descriptive OSINT reference summary."""
    lines = ["=" * 88, title, subtitle, "=" * 88]
    for c in concepts:
        lines += [
            "",
            f"{c.name_en}  [{c.name_native}]   (confidence {c.confidence:.0%})",
            "-" * 88,
            f"  {c.summary}",
            f"  Related modeled areas: {', '.join(c.related_systems)}",
            f"  Study with: {c.analytical_notes}",
            f"  Open sources: {'; '.join(c.public_sources)}",
        ]
    lines += ["", "=" * 88,
              "Reminder: descriptive open-source analysis for study/education only --",
              "NOT operational guidance."]
    return "\n".join(lines)
