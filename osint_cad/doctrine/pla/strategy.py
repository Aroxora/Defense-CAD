#!/usr/bin/env python3
"""
PLA Strategy & Doctrine -- OSINT analytical reference.

Structured, open-source characterization of publicly documented People's Liberation Army
(PLA) strategic/operational concepts, cross-referenced to the physics/CAD models so they can
be studied in context. Sources are unclassified (U.S. DoD China Military Power Report, RAND,
China Aerospace Studies Institute, CSIS, USNI, public editions of the PLA *Science of
Military Strategy*).

Descriptive and analytical only -- NOT operational guidance. See PLA_STRATEGY_OSINT.md.

Classification: UNCLASSIFIED // OPEN-SOURCE ANALYSIS // PUBLIC RELEASE
"""

from typing import Dict, List

from osint_cad.doctrine._base import (
    DoctrineConcept,
    get_concept as _get,
    render_report as _render,
    systems_to_concepts as _idx,
)

SIDE = "PLA"

CONCEPTS: List[DoctrineConcept] = [
    DoctrineConcept(
        key="systems_confrontation",
        name_en="Systems Confrontation / Systems-Destruction Warfare",
        name_native="体系对抗 / 系统破击战",
        summary=(
            "The widely-cited PLA framing of modern war as a clash between rival operational "
            "'systems of systems' (sensing, C2, fires, networks) rather than platform-vs-"
            "platform attrition; emphasis on degrading adversary system cohesion -- its "
            "sensing-to-shooter linkages -- rather than destroying every platform."
        ),
        public_sources=[
            "RAND, 'Systems Confrontation and System Destruction Warfare' (Engstrom, 2018)",
            "U.S. DoD annual China Military Power Report (CMPR)",
        ],
        related_systems=["integrated_kill_chain_cad", "network_centric_killchain",
                         "information_chain_robustness"],
        analytical_notes=(
            "Study node criticality with the kill-chain and information-chain-robustness "
            "models: which single nodes most reduce end-to-end track quality / Pk, and how "
            "redundancy changes that. A study of fragility, not a strike plan."
        ),
        confidence=0.70,
    ),
    DoctrineConcept(
        key="a2ad_counterintervention",
        name_en="Anti-Access / Area-Denial (Counter-Intervention)",
        name_native="反介入/区域拒止",
        summary=(
            "Outside-analyst label (the PLA prefers 'counter-intervention') for layered "
            "capabilities meant to raise the cost/risk of an opposing force operating within "
            "the first/second island chains: long-range sensing, ballistic/cruise missiles, "
            "integrated air defense, and maritime strike."
        ),
        public_sources=[
            "U.S. DoD China Military Power Report",
            "CSIS Missile Defense Project / Missile Threat",
        ],
        related_systems=["precision_ballistic_missiles", "air_defense_targets",
                         "pla_systems_cad", "carrier_strike_kill_chain"],
        analytical_notes=(
            "Bound engagement envelopes and the defender's required warning/intercept "
            "timelines against the modeled threats; the defensive framing is the useful one."
        ),
        confidence=0.65,
    ),
    DoctrineConcept(
        key="informatized_warfare",
        name_en="Informatized Warfare",
        name_native="信息化战争",
        summary=(
            "The publicly-stated goal of fighting 'informatized' wars in which networked "
            "information dominance (ISR, secure data links, PNT, EW) is the decisive enabler "
            "tying sensors to shooters."
        ),
        public_sources=[
            "PLA 'Science of Military Strategy' (Academy of Military Science, public eds.)",
            "China Aerospace Studies Institute (CASI) translations & analyses",
        ],
        related_systems=["signal_processing", "geolocation_network", "datalink_protocol",
                         "adaptive_antenna_ep"],
        analytical_notes=(
            "Maps onto the ES/EW and datalink models; EW_ACTIONABLE_STRATEGY.md is the "
            "physics reality-check on link attack vs. passive support."
        ),
        confidence=0.70,
    ),
    DoctrineConcept(
        key="intelligentized_warfare",
        name_en="Intelligentized Warfare",
        name_native="智能化战争",
        summary=(
            "A more recent publicly-discussed evolution emphasizing AI/autonomy and "
            "algorithmic decision support atop informatized systems; open sources treat much "
            "of it as aspirational/developmental."
        ),
        public_sources=[
            "U.S. DoD China Military Power Report (intelligentization sections)",
            "CASI / CNA open analyses on PLA AI",
        ],
        related_systems=["iterative_classifier", "ml_waveform_classifier",
                         "advanced_tracking"],
        analytical_notes=(
            "The classifier/tracker modules are toy analogues for where automated "
            "classification/track-fusion sits in a chain; real-world maturity confidence low."
        ),
        confidence=0.45,
    ),
    DoctrineConcept(
        key="recon_strike_complex",
        name_en="Reconnaissance-Strike Complex / 'Kill Web'",
        name_native="侦察打击体系",
        summary=(
            "Integration of long-range sensing, C2, and precision fires into a closed, "
            "redundant sensor-to-shooter loop -- the mechanism by which the above concepts "
            "are meant to be realized."
        ),
        public_sources=[
            "RAND systems-confrontation studies",
            "U.S. DoD China Military Power Report (long-range precision strike)",
        ],
        related_systems=["integrated_kill_chain_cad", "carrier_strike_kill_chain",
                         "df17_hypersonic_kill_chain", "network_centric_killchain"],
        analytical_notes=(
            "The integrated kill-chain models are the natural object of study; the useful "
            "questions are defensive: chain latency, track-quality propagation, dominant links."
        ),
        confidence=0.65,
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
