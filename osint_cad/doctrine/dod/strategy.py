#!/usr/bin/env python3
"""
U.S. DoD Strategy & Doctrine -- OSINT analytical reference.

Structured, open-source characterization of publicly documented U.S. Department of Defense
strategic/operational concepts, cross-referenced to the physics/CAD models so they can be
studied in context. Sources are unclassified and public (2022 National Defense Strategy,
DARPA, Navy/Air Force published concepts, DoD CJADC2 / Replicator announcements, CSIS, CBO).

Descriptive and analytical only -- NOT operational guidance. See DOD_STRATEGY_OSINT.md.

Classification: UNCLASSIFIED // OPEN-SOURCE ANALYSIS // PUBLIC RELEASE
"""

from typing import Dict, List

from osint_cad.doctrine._base import (
    DoctrineConcept,
    get_concept as _get,
    render_report as _render,
    systems_to_concepts as _idx,
)

SIDE = "U.S. DoD"

CONCEPTS: List[DoctrineConcept] = [
    DoctrineConcept(
        key="integrated_deterrence",
        name_en="Integrated Deterrence",
        name_native="(2022 NDS)",
        summary=(
            "The 2022 National Defense Strategy's organizing concept: combine capabilities "
            "across domains, theaters, the spectrum of conflict, allies/partners, and other "
            "instruments of national power so deterrence is mutually reinforcing."
        ),
        public_sources=[
            "U.S. DoD, 2022 National Defense Strategy",
            "CSIS analyses of the 2022 NDS",
        ],
        related_systems=["us_2025_defense_systems", "integrated_kill_system",
                         "information_chain_robustness"],
        analytical_notes=(
            "Use the integrated-system and robustness models to study how cross-domain "
            "redundancy changes end-to-end resilience -- a deterrence-by-denial study."
        ),
        confidence=0.75,
    ),
    DoctrineConcept(
        key="cjadc2",
        name_en="Combined Joint All-Domain Command & Control (CJADC2)",
        name_native="(JADC2)",
        summary=(
            "The publicly-stated effort to connect sensors and shooters across all services "
            "and domains into a resilient, any-sensor/any-shooter data fabric -- the U.S. "
            "analogue of a reconnaissance-strike/kill-web concept."
        ),
        public_sources=[
            "DoD CJADC2 Strategy (public summary)",
            "CRS, 'Joint All-Domain Command and Control (JADC2)'",
        ],
        related_systems=["american_integrated_link", "network_centric_killchain",
                         "integrated_kill_chain_cad"],
        analytical_notes=(
            "Maps onto the integrated-link and network-centric kill-chain models; study "
            "latency, track fusion, and which links dominate the uncertainty budget."
        ),
        confidence=0.70,
    ),
    DoctrineConcept(
        key="mosaic_warfare",
        name_en="Mosaic Warfare",
        name_native="(DARPA)",
        summary=(
            "DARPA concept of composing many low-cost, disaggregated, attritable systems into "
            "adaptable 'mosaics', trading monolithic platforms for resilience and decision "
            "speed -- a force-design answer to systems-destruction logic."
        ),
        public_sources=[
            "DARPA Strategic Technology Office, Mosaic Warfare materials",
            "CSBA, 'Mosaic Warfare' (Clark, Patt, Schramm, 2020)",
        ],
        related_systems=["network_centric_killchain", "information_chain_robustness",
                         "advanced_tracking"],
        analytical_notes=(
            "The robustness model is ideal here: quantify how disaggregation/redundancy "
            "raises the number of nodes an adversary must defeat to break a chain."
        ),
        confidence=0.60,
    ),
    DoctrineConcept(
        key="distributed_maritime_ops",
        name_en="Distributed Maritime Operations (DMO)",
        name_native="(USN)",
        summary=(
            "U.S. Navy concept of distributing combat power across more, widely-spaced nodes "
            "(manned/unmanned) to complicate adversary targeting while massing fires via "
            "networking -- a counter to anti-ship reconnaissance-strike complexes."
        ),
        public_sources=[
            "CNO Navigation Plan (NAVPLAN), public editions",
            "USNI / CRS analyses of DMO",
        ],
        related_systems=["ddg51_model", "carrier_strike_kill_chain", "us_2025_defense_systems"],
        analytical_notes=(
            "Pair the ship/air-defense models with the carrier-strike kill chain to study "
            "how dispersion changes the defender's detection and engagement geometry."
        ),
        confidence=0.65,
    ),
    DoctrineConcept(
        key="agile_combat_employment",
        name_en="Agile Combat Employment (ACE)",
        name_native="(USAF)",
        summary=(
            "U.S. Air Force concept of operating from dispersed, austere locations with small "
            "logistics footprints to complicate adversary targeting of fixed main bases."
        ),
        public_sources=[
            "USAF Doctrine Note, Agile Combat Employment (public)",
            "RAND basing-resilience analyses",
        ],
        related_systems=["f35_integrated_kill_chain", "f35_infrastructure_strike",
                         "us_2025_defense_systems"],
        analytical_notes=(
            "Use the infrastructure-strike model to study how dispersal changes the number "
            "of aimpoints and required adversary salvo size -- a base-resilience study."
        ),
        confidence=0.65,
    ),
    DoctrineConcept(
        key="replicator_attritable_autonomy",
        name_en="Replicator / Attritable Autonomy",
        name_native="(DoD)",
        summary=(
            "Publicly-announced DoD push to field large numbers of low-cost autonomous "
            "systems quickly; open sources treat scale/maturity as developmental."
        ),
        public_sources=[
            "DoD Replicator initiative announcements (public)",
            "CSIS / CNAS open analyses",
        ],
        related_systems=["iterative_classifier", "ml_waveform_classifier", "advanced_tracking"],
        analytical_notes=(
            "Toy classifier/tracker analogues illustrate where automated autonomy sits in a "
            "chain; treat maturity as developmental (low confidence)."
        ),
        confidence=0.45,
    ),
]


def list_concepts() -> List[DoctrineConcept]:
    return list(CONCEPTS)


def get_concept(key: str) -> DoctrineConcept:
    return _get(CONCEPTS, key)


def systems_to_concepts() -> Dict[str, List[str]]:
    return _idx(CONCEPTS)


def summary_report() -> str:
    return _render(
        f"{SIDE} STRATEGY & DOCTRINE -- OSINT ANALYTICAL REFERENCE",
        "Open-source, descriptive context for the physics/CAD models. NOT operational guidance.",
        CONCEPTS,
    )


if __name__ == "__main__":
    print(summary_report())
