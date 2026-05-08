#!/usr/bin/env python3
"""
Kill Chain Simulation Runner

Executes multi-layer defense engagement simulations with full
calculation logging and impossibility analysis for CI/CD pipelines.

Logs include:
- Kill chain phase probabilities with uncertainties
- Salvo engagement calculations
- Multi-layer defense effectiveness
- Comprehensive impossibility analysis

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
import json
import sys
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
from enum import Enum

from calculation_logger import (
    CalculationLogger, OutputFormat, init_logger
)


# =============================================================================
# KILL CHAIN DEFINITIONS
# =============================================================================

class KillChainPhase(Enum):
    """F2T2EA Kill Chain Phases"""
    FIND = "Find"
    FIX = "Fix"
    TRACK = "Track"
    TARGET = "Target"
    ENGAGE = "Engage"
    ASSESS = "Assess"


@dataclass
class PhaseProbability:
    """Kill chain phase probability with uncertainty"""
    phase: KillChainPhase
    probability: float
    confidence: float
    min_estimate: float
    max_estimate: float
    factors: List[str]


@dataclass
class EngagementScenario:
    """Engagement scenario definition"""
    name: str
    target_type: str
    target_rcs_dbsm: float
    target_speed_mach: float
    target_altitude_m: float
    defense_layers: List[str]
    salvo_size: int
    correlation_factor: float


# =============================================================================
# KILL PROBABILITY CALCULATOR
# =============================================================================

class KillProbabilityCalculator:
    """Calculate kill probability with full uncertainty quantification"""

    def __init__(self, logger: CalculationLogger):
        self.logger = logger

    def calculate_phase_pk(
        self,
        scenario: EngagementScenario
    ) -> Dict[KillChainPhase, PhaseProbability]:
        """Calculate probability for each kill chain phase"""

        # Phase probabilities based on scenario parameters
        # These are parametric estimates with documented uncertainty

        rcs_factor = min(1.0, 10 ** (scenario.target_rcs_dbsm / 20) / 10)
        speed_factor = max(0.5, 1.0 - (scenario.target_speed_mach - 1.0) * 0.1)
        altitude_factor = 1.0 if scenario.target_altitude_m < 15000 else 0.85

        phases = {}

        # FIND phase
        p_find = min(0.95, 0.7 + 0.25 * rcs_factor) * altitude_factor
        phases[KillChainPhase.FIND] = PhaseProbability(
            phase=KillChainPhase.FIND,
            probability=p_find,
            confidence=0.60,
            min_estimate=p_find * 0.8,
            max_estimate=min(0.99, p_find * 1.15),
            factors=[
                f"RCS factor: {rcs_factor:.3f}",
                f"Altitude factor: {altitude_factor:.2f}",
                "Sensor coverage uncertainty",
                "Electronic warfare effects unknown"
            ]
        )

        # FIX phase
        p_fix = min(0.90, 0.65 + 0.25 * rcs_factor) * speed_factor
        phases[KillChainPhase.FIX] = PhaseProbability(
            phase=KillChainPhase.FIX,
            probability=p_fix,
            confidence=0.55,
            min_estimate=p_fix * 0.75,
            max_estimate=min(0.95, p_fix * 1.2),
            factors=[
                f"Speed factor: {speed_factor:.2f}",
                "Track initiation latency",
                "Multi-target discrimination"
            ]
        )

        # TRACK phase
        p_track = min(0.88, 0.60 + 0.28 * rcs_factor) * speed_factor * altitude_factor
        phases[KillChainPhase.TRACK] = PhaseProbability(
            phase=KillChainPhase.TRACK,
            probability=p_track,
            confidence=0.50,
            min_estimate=p_track * 0.7,
            max_estimate=min(0.95, p_track * 1.25),
            factors=[
                "Track quality degradation over time",
                "Maneuver prediction uncertainty",
                "Clutter and jamming effects"
            ]
        )

        # TARGET phase
        p_target = min(0.85, 0.55 + 0.30 * rcs_factor)
        phases[KillChainPhase.TARGET] = PhaseProbability(
            phase=KillChainPhase.TARGET,
            probability=p_target,
            confidence=0.55,
            min_estimate=p_target * 0.75,
            max_estimate=min(0.92, p_target * 1.2),
            factors=[
                "Weapon-target assignment optimization",
                "Fire control solution quality",
                "Engagement timing"
            ]
        )

        # ENGAGE phase
        p_engage = min(0.82, 0.50 + 0.32 * rcs_factor) * speed_factor
        phases[KillChainPhase.ENGAGE] = PhaseProbability(
            phase=KillChainPhase.ENGAGE,
            probability=p_engage,
            confidence=0.45,
            min_estimate=p_engage * 0.65,
            max_estimate=min(0.90, p_engage * 1.3),
            factors=[
                "Missile guidance accuracy",
                "Target maneuvers during engagement",
                "Countermeasure effectiveness",
                "Fuze and warhead reliability"
            ]
        )

        # ASSESS phase
        p_assess = 0.75  # BDA is highly uncertain
        phases[KillChainPhase.ASSESS] = PhaseProbability(
            phase=KillChainPhase.ASSESS,
            probability=p_assess,
            confidence=0.40,
            min_estimate=0.50,
            max_estimate=0.90,
            factors=[
                "Battle damage assessment latency",
                "Kill confirmation uncertainty",
                "Re-engagement decision timing"
            ]
        )

        return phases

    def calculate_single_shot_pk(
        self,
        phases: Dict[KillChainPhase, PhaseProbability],
        scenario_name: str
    ) -> Tuple[float, float, float, float]:
        """
        Calculate single-shot kill probability

        Returns: (pk, confidence, pk_min, pk_max)
        """

        # Chain multiplication
        pk = 1.0
        pk_min = 1.0
        pk_max = 1.0
        confidence_product = 1.0

        self.logger.log_calculation(
            name=f"{scenario_name} Single-Shot Pk Chain",
            formula="Pk = P(find) × P(fix) × P(track) × P(target) × P(engage)",
            inputs={p.name: phases[p].probability for p in KillChainPhase if p != KillChainPhase.ASSESS},
            result=0,  # Will be updated
            unit="probability",
            confidence=0.50,
            intermediate_steps=[]
        )

        steps = []
        for phase in [KillChainPhase.FIND, KillChainPhase.FIX, KillChainPhase.TRACK,
                      KillChainPhase.TARGET, KillChainPhase.ENGAGE]:
            pp = phases[phase]
            pk *= pp.probability
            pk_min *= pp.min_estimate
            pk_max *= pp.max_estimate
            confidence_product *= pp.confidence

            steps.append({
                "step": f"After {phase.value}: Pk = {pk:.4f} [{pk_min:.4f}, {pk_max:.4f}]"
            })

            self.logger.log_calculation(
                name=f"{scenario_name} P({phase.value})",
                formula=f"P({phase.value}) with uncertainty",
                inputs={"factors": pp.factors},
                result=pp.probability,
                unit="probability",
                confidence=pp.confidence,
                notes=f"Range: [{pp.min_estimate:.3f}, {pp.max_estimate:.3f}]"
            )

        # Geometric mean of confidences
        overall_confidence = confidence_product ** (1/5)

        self.logger.log_calculation(
            name=f"{scenario_name} Final Single-Shot Pk",
            formula="Pk = Π(P_phase) for all phases",
            inputs={"phases": 5},
            result=pk,
            unit="probability",
            confidence=overall_confidence,
            intermediate_steps=steps,
            notes=f"Uncertainty range: [{pk_min:.4f}, {pk_max:.4f}]"
        )

        return pk, overall_confidence, pk_min, pk_max

    def calculate_salvo_pk(
        self,
        single_pk: float,
        salvo_size: int,
        correlation: float,
        scenario_name: str
    ) -> Tuple[float, float, float]:
        """
        Calculate salvo kill probability accounting for correlation

        Returns: (salvo_pk, n_effective, salvo_pk_independent)
        """

        # Independent case
        pk_independent = 1 - (1 - single_pk) ** salvo_size

        # Correlated case
        n_effective = 1 + (salvo_size - 1) * (1 - correlation)
        pk_correlated = 1 - (1 - single_pk) ** n_effective

        self.logger.log_calculation(
            name=f"{scenario_name} Salvo Pk (N={salvo_size})",
            formula="Pk_salvo = 1 - (1 - Pk_single)^N_effective",
            inputs={
                "single_pk": single_pk,
                "salvo_size": salvo_size,
                "correlation": correlation
            },
            result=pk_correlated,
            unit="probability",
            confidence=0.45,
            intermediate_steps=[
                {"step": f"N_effective = 1 + (N-1)(1-ρ) = 1 + ({salvo_size}-1)(1-{correlation}) = {n_effective:.2f}"},
                {"step": f"Pk_independent = 1 - (1-{single_pk:.4f})^{salvo_size} = {pk_independent:.4f}"},
                {"step": f"Pk_correlated = 1 - (1-{single_pk:.4f})^{n_effective:.2f} = {pk_correlated:.4f}"}
            ],
            notes=f"Correlation reduces effective salvo size from {salvo_size} to {n_effective:.1f}"
        )

        return pk_correlated, n_effective, pk_independent

    def calculate_multilayer_pk(
        self,
        layer_pks: List[Tuple[str, float]],
        scenario_name: str
    ) -> float:
        """Calculate multi-layer defense kill probability"""

        p_survive = 1.0
        steps = []

        for layer_name, layer_pk in layer_pks:
            p_survive *= (1 - layer_pk)
            steps.append({
                "step": f"After {layer_name} (Pk={layer_pk:.3f}): P(survive) = {p_survive:.4f}"
            })

        total_pk = 1 - p_survive

        self.logger.log_calculation(
            name=f"{scenario_name} Multi-Layer Pk",
            formula="Pk_total = 1 - Π(1 - Pk_layer)",
            inputs=dict(layer_pks),
            result=total_pk,
            unit="probability",
            confidence=0.40,
            intermediate_steps=steps,
            notes=f"Target must survive {len(layer_pks)} defense layers"
        )

        return total_pk


# =============================================================================
# IMPOSSIBILITY ANALYSIS
# =============================================================================

def generate_impossibility_analysis() -> str:
    """Generate comprehensive analysis of why 100% Pk is impossible"""

    analysis = """
================================================================================
IMPOSSIBILITY ANALYSIS: WHY 100% KILL PROBABILITY CANNOT BE ACHIEVED
================================================================================

1. FUNDAMENTAL PHYSICAL LIMITATIONS
================================================================================

1.1 Sensor Physics
------------------
- Radar equation: Signal decreases with R^4
- Thermal noise floor cannot be eliminated
- Atmospheric attenuation varies unpredictably
- Target RCS fluctuates with aspect angle (Swerling models)
- Multipath and clutter effects are stochastic

1.2 Guidance Limitations
------------------------
- All guidance systems have finite accuracy
- Miss distance follows statistical distribution
- Target maneuvers cannot be perfectly predicted
- Atmospheric effects on missile trajectory
- GPS/INS drift accumulates

1.3 Warhead Physics
-------------------
- Blast effects decay with distance
- Fragment patterns are statistical
- Target hardness varies
- Fuze timing has uncertainty

2. INFORMATION LIMITATIONS
================================================================================

2.1 Detection Uncertainty
-------------------------
- Cannot detect what you cannot see
- Stealth reduces signature below noise floor
- Low-altitude targets masked by terrain
- Space-based sensors have coverage gaps
- Passive sensors require target emissions

2.2 Track Quality
-----------------
- All measurements have error
- Kalman filter predictions are estimates
- Track correlation errors occur
- Maneuver detection has latency
- Track loss during engagement

2.3 Intelligence Gaps
---------------------
- Target capabilities partially unknown
- Countermeasure effectiveness uncertain
- Electronic warfare effects unpredictable
- Operational patterns change

3. OPERATIONAL LIMITATIONS
================================================================================

3.1 Timeline Constraints
------------------------
- Detection to engagement takes time
- Missile flight time is non-zero
- Target may exit engagement envelope
- Decision cycle delays
- Communication latency

3.2 Weapon Limitations
----------------------
- Finite magazine depth
- Reload time constraints
- Weapon system availability
- Maintenance requirements
- Supply chain dependencies

3.3 Human Factors
-----------------
- Operator errors occur
- Decision-making under stress
- Training variations
- Rules of engagement constraints
- Fratricide avoidance

4. COUNTERMEASURE EFFECTS
================================================================================

4.1 Electronic Warfare
----------------------
- Radar jamming effectiveness unknown
- Infrared countermeasures
- Decoys and chaff
- Cyber attacks on networks
- GPS denial effects

4.2 Tactical Countermeasures
----------------------------
- Saturation attacks
- Low-altitude penetration
- Terrain masking
- Formation tactics
- Timing coordination

4.3 Adaptive Threats
--------------------
- Tactics evolve during conflict
- New countermeasures deployed
- Intelligence on defender capabilities
- Targeting of defense nodes

5. SYSTEM INTEGRATION CHALLENGES
================================================================================

5.1 Network Vulnerabilities
---------------------------
- Single points of failure
- Communication bandwidth limits
- Latency accumulation
- Data fusion errors
- Interoperability issues

5.2 Coordination Problems
-------------------------
- Multiple engagements on same target
- Fratricide prevention
- Handoff between systems
- Coverage gaps
- Redundancy limitations

6. MATHEMATICAL PROOF
================================================================================

For ANY defense system:
- Let P_i = probability of phase i succeeding
- Each P_i < 1 (cannot be certain)
- Total Pk = Π(P_i) for all phases
- Since each P_i < 1, Pk < 1

Even with multiple layers:
- P(kill) = 1 - Π(1 - Pk_layer)
- Each layer has Pk < 1
- Therefore P(kill) < 1

The only way to achieve Pk = 1.0 would be:
- P(detect) = 1.0 AND
- P(track) = 1.0 AND
- P(engage) = 1.0 AND
- P(kill_given_engage) = 1.0

Each of these is physically impossible due to:
- Noise in all measurements
- Uncertainty in all predictions
- Statistical nature of kill mechanisms

7. CONFIDENCE ASSESSMENT
================================================================================

Overall Model Confidence: 40-60%

Sources of model uncertainty:
- Parameter estimates from open sources
- Algorithms simplified from classified methods
- No real engagement data for validation
- Threat capabilities partially unknown
- Environmental effects parametric only

CONCLUSION
================================================================================

A 100% kill probability is mathematically and physically impossible for ANY
weapon system against ANY target. The best achievable is high confidence
(>95%) through:
- Multiple redundant layers
- Large salvo sizes
- Excellent sensor coverage
- Well-trained operators
- Robust network architecture

Even then, some targets will survive due to irreducible uncertainties.

Classification: UNCLASSIFIED // FOR ACADEMIC/RESEARCH USE ONLY
================================================================================
"""
    return analysis


# =============================================================================
# MAIN SIMULATION
# =============================================================================

def run_kill_chain_simulation():
    """Run complete kill chain simulation with logging"""

    # Initialize logger
    logger = init_logger(
        name="Kill-Chain-Simulation",
        output_formats=[OutputFormat.CONSOLE, OutputFormat.GITHUB_ACTIONS],
        log_file="kill_chain_log.txt",
        verbose=True
    )

    calculator = KillProbabilityCalculator(logger)

    # Define scenarios
    scenarios = [
        EngagementScenario(
            name="F-35A vs Multi-Layer Defense",
            target_type="5th Gen Fighter",
            target_rcs_dbsm=-30,  # Very low RCS
            target_speed_mach=1.6,
            target_altitude_m=10000,
            defense_layers=["HQ-9B", "HQ-16B", "HQ-7B"],
            salvo_size=4,
            correlation_factor=0.3
        ),
        EngagementScenario(
            name="F-22 vs Integrated Air Defense",
            target_type="5th Gen Fighter",
            target_rcs_dbsm=-35,
            target_speed_mach=2.0,
            target_altitude_m=15000,
            defense_layers=["HQ-9B", "HQ-22"],
            salvo_size=6,
            correlation_factor=0.25
        ),
        EngagementScenario(
            name="Tomahawk vs Point Defense",
            target_type="Cruise Missile",
            target_rcs_dbsm=-15,
            target_speed_mach=0.75,
            target_altitude_m=50,
            defense_layers=["HQ-17A", "Type 1130 CIWS"],
            salvo_size=8,
            correlation_factor=0.4
        ),
        EngagementScenario(
            name="B-2 vs Strategic Air Defense",
            target_type="Strategic Bomber",
            target_rcs_dbsm=-40,
            target_speed_mach=0.85,
            target_altitude_m=12000,
            defense_layers=["HQ-9B", "HQ-9B", "HQ-22"],  # Multiple batteries
            salvo_size=8,
            correlation_factor=0.35
        )
    ]

    all_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "scenarios": [],
        "summary": {}
    }

    print("=" * 80)
    print("KILL CHAIN SIMULATION RUNNER")
    print("=" * 80)

    for scenario in scenarios:
        print(f"\n{'─' * 80}")
        print(f"SCENARIO: {scenario.name}")
        print(f"Target: {scenario.target_type} (RCS: {scenario.target_rcs_dbsm} dBsm)")
        print(f"{'─' * 80}")

        with logger.section(scenario.name):

            # Calculate phase probabilities
            phases = calculator.calculate_phase_pk(scenario)

            # Log each phase
            for phase, pp in phases.items():
                logger.log_validation(
                    component=scenario.name,
                    parameter=f"P({phase.value})",
                    value=pp.probability,
                    min_val=pp.min_estimate,
                    max_val=pp.max_estimate
                )

            # Calculate single-shot Pk
            single_pk, confidence, pk_min, pk_max = calculator.calculate_single_shot_pk(
                phases, scenario.name
            )

            # Calculate salvo Pk
            salvo_pk, n_eff, pk_indep = calculator.calculate_salvo_pk(
                single_pk, scenario.salvo_size, scenario.correlation_factor, scenario.name
            )

            # Calculate multi-layer Pk
            layer_pks = []
            for i, layer in enumerate(scenario.defense_layers):
                # Each layer gets the salvo Pk adjusted for its position
                # Later layers face degraded target (may be damaged/maneuvering)
                layer_effectiveness = salvo_pk * (0.9 ** i)
                layer_pks.append((layer, layer_effectiveness))

            total_pk = calculator.calculate_multilayer_pk(layer_pks, scenario.name)

            # Log final result
            logger.log_calculation(
                name=f"{scenario.name} FINAL RESULT",
                formula="Multi-layer salvo engagement",
                inputs={
                    "target_rcs_dbsm": scenario.target_rcs_dbsm,
                    "salvo_size": scenario.salvo_size,
                    "defense_layers": len(scenario.defense_layers)
                },
                result=total_pk,
                unit="probability",
                confidence=confidence * 0.8,  # Reduce for multi-layer uncertainty
                notes=f"Range: [{pk_min:.4f}, {pk_max:.4f}] for single layer"
            )

            # Store results
            scenario_result = {
                "name": scenario.name,
                "target": {
                    "type": scenario.target_type,
                    "rcs_dbsm": scenario.target_rcs_dbsm,
                    "speed_mach": scenario.target_speed_mach,
                    "altitude_m": scenario.target_altitude_m
                },
                "engagement": {
                    "salvo_size": scenario.salvo_size,
                    "correlation": scenario.correlation_factor,
                    "layers": scenario.defense_layers
                },
                "results": {
                    "single_shot_pk": single_pk,
                    "salvo_pk": salvo_pk,
                    "total_pk": total_pk,
                    "confidence": confidence,
                    "pk_range": [pk_min, pk_max]
                },
                "phase_probabilities": {
                    phase.value: {
                        "probability": pp.probability,
                        "confidence": pp.confidence,
                        "range": [pp.min_estimate, pp.max_estimate]
                    }
                    for phase, pp in phases.items()
                }
            }
            all_results["scenarios"].append(scenario_result)

            # Print summary
            print(f"\nResults for {scenario.name}:")
            print(f"  Single-shot Pk: {single_pk:.4f} (confidence: {confidence:.2f})")
            print(f"  Salvo Pk (N={scenario.salvo_size}): {salvo_pk:.4f}")
            print(f"  Multi-layer Pk: {total_pk:.4f}")
            print(f"  Uncertainty range: [{pk_min:.4f}, {pk_max:.4f}]")

    # Generate summary
    pks = [s["results"]["total_pk"] for s in all_results["scenarios"]]
    all_results["summary"] = {
        "scenarios_analyzed": len(scenarios),
        "average_pk": np.mean(pks),
        "min_pk": min(pks),
        "max_pk": max(pks),
        "key_finding": "100% kill probability is mathematically impossible"
    }

    # Finalize logger
    logger.finalize()

    # Write JSON report
    with open("kill_chain_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print("\nWrote: kill_chain_results.json")

    # Write Markdown report
    md_report = logger.generate_markdown_report()

    # Add scenario summaries
    md_lines = [md_report, "\n\n# Engagement Scenario Summary\n"]

    for scenario in all_results["scenarios"]:
        md_lines.append(f"\n## {scenario['name']}\n")
        md_lines.append(f"- Target: {scenario['target']['type']} (RCS: {scenario['target']['rcs_dbsm']} dBsm)\n")
        md_lines.append(f"- Single-shot Pk: {scenario['results']['single_shot_pk']:.4f}\n")
        md_lines.append(f"- Salvo Pk: {scenario['results']['salvo_pk']:.4f}\n")
        md_lines.append(f"- **Total Pk: {scenario['results']['total_pk']:.4f}**\n")
        md_lines.append(f"- Confidence: {scenario['results']['confidence']:.2f}\n")

    with open("kill_chain_report.md", "w") as f:
        f.write("".join(md_lines))
    print("Wrote: kill_chain_report.md")

    # Write impossibility analysis
    impossibility = generate_impossibility_analysis()
    with open("impossibility_analysis.txt", "w") as f:
        f.write(impossibility)
    print("Wrote: impossibility_analysis.txt")

    print("\n" + "=" * 80)
    print("KILL CHAIN SIMULATION COMPLETE")
    print(f"Scenarios analyzed: {len(scenarios)}")
    print(f"Average Pk: {all_results['summary']['average_pk']:.4f}")
    print(f"Key finding: {all_results['summary']['key_finding']}")
    print("=" * 80)

    return all_results


if __name__ == "__main__":
    run_kill_chain_simulation()
