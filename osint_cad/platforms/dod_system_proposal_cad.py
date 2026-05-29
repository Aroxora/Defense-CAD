#!/usr/bin/env python3
"""
DOD New System Proposal CAD Framework
======================================

CLASSIFICATION: UNCLASSIFIED // FOR OFFICIAL USE ONLY

Generates and validates new defense system proposals following the core
philosophy of INTEGRATED WEAPONS AND INFORMATIONAL LINKS.

CORE PHILOSOPHY:
"No sensor fights alone. No shooter waits for data. No node is indispensable."

This CAD system implements:
1. System-of-systems architecture design
2. Any-sensor-any-shooter integration
3. Network resilience analysis (redundant datalinks, survivable nodes)
4. Kill chain probability calculations
5. Cost-effectiveness estimation
6. Information chain robustness validation

PROPOSAL CATEGORIES:
- TIER 1: Immediate Production (TRL 6-7)
- TIER 2: Near-Term Development (TRL 4-5)
- TIER 3: Integration Systems (Software-Heavy)

Author: CAD Analysis System
Date: 2026-01-02
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
from abc import ABC, abstractmethod
import json


# =============================================================================
# A2/AD THREAT MODEL
# =============================================================================
# The core strategic problem: adversary A2/AD systems have made traditional
# carrier-centric power projection unaffordable and high-risk.
#
# Key threat parameters (PRC-focused):
# - ASBM range: 1,500-4,000 km (DF-21D, DF-26)
# - ASBM cost: ~$10-20M per missile
# - SAM coverage: 400 km (HQ-9, S-400)
# - Fighter CAP: 1,000 km from bases
# - OTH radar detection: 3,000+ km
#
# US must achieve:
# 1. STAND-OFF: Strike from outside A2/AD envelope (>2,000 km)
# 2. COST EXCHANGE: Our weapons cost less than their defenses
# 3. SURVIVABILITY: Platforms survive to shoot
# 4. MASS: Enough volume to saturate defenses
# 5. PERSISTENCE: Sustained operations, not one-shot
# =============================================================================

@dataclass
class ThreatEnvelope:
    """Defines adversary A2/AD threat envelope"""
    name: str
    asbm_range_km: float          # Anti-ship ballistic missile range
    sam_range_km: float           # Surface-to-air missile range
    fighter_cap_range_km: float   # Fighter combat air patrol radius
    oth_radar_range_km: float     # Over-the-horizon radar detection
    asbm_cost_million: float      # Cost per ASBM
    sam_cost_million: float       # Cost per SAM engagement
    coastal_baseline_km: float    # Distance from adversary coast

    def get_safe_standoff_range(self) -> float:
        """Minimum range to operate with acceptable risk"""
        return max(self.asbm_range_km, self.fighter_cap_range_km) * 1.2

    def get_strike_range_required(self) -> float:
        """Weapon range needed to strike from safe standoff"""
        return self.get_safe_standoff_range() + 500  # Strike 500km inland


# Pre-defined threat envelopes
THREAT_PRC_PACIFIC = ThreatEnvelope(
    name="PRC Western Pacific",
    asbm_range_km=4000,       # DF-26 range
    sam_range_km=400,         # HQ-9/S-400
    fighter_cap_range_km=1500, # J-20 with tanker support
    oth_radar_range_km=3000,  # OTH-B class
    asbm_cost_million=15,     # Estimated DF-21D cost
    sam_cost_million=3,       # HQ-9 missile cost
    coastal_baseline_km=0
)

THREAT_PRC_TAIWAN = ThreatEnvelope(
    name="PRC Taiwan Strait",
    asbm_range_km=2000,       # DF-21D adequate
    sam_range_km=400,
    fighter_cap_range_km=800, # Shorter range, more coverage
    oth_radar_range_km=2000,
    asbm_cost_million=10,
    sam_cost_million=3,
    coastal_baseline_km=150   # Taiwan strait width
)

THREAT_RUSSIA_BALTIC = ThreatEnvelope(
    name="Russia Baltic/Kaliningrad",
    asbm_range_km=500,        # Iskander range
    sam_range_km=400,         # S-400
    fighter_cap_range_km=600,
    oth_radar_range_km=1500,
    asbm_cost_million=5,
    sam_cost_million=2,
    coastal_baseline_km=0
)


@dataclass
class CostExchangeAnalysis:
    """Analyzes cost exchange ratio against adversary"""
    our_weapon_cost_million: float
    their_defense_cost_million: float
    exchange_ratio: float  # >1 means we're winning
    weapons_per_salvo: int
    salvos_to_saturate: int
    total_cost_to_saturate_billion: float
    assessment: str  # "FAVORABLE", "UNFAVORABLE", "MARGINAL"


@dataclass
class StrategicAssessment:
    """Strategic assessment of system against A2/AD threat"""
    system_name: str
    threat_envelope: ThreatEnvelope

    # Range analysis
    weapon_range_km: float
    safe_standoff_km: float
    can_strike_from_standoff: bool
    range_margin_km: float

    # Cost exchange
    cost_exchange: CostExchangeAnalysis

    # Platform survivability
    platform_survivability_vs_threat: float
    can_operate_inside_envelope: bool
    requires_air_superiority: bool

    # Mass and persistence
    salvo_size: int
    reload_time_hours: float
    sustainable_rate_per_day: int

    # Overall
    strategic_viability: str  # "VIABLE", "MARGINAL", "NOT_VIABLE"
    recommendations: List[str]


# Simplified information chain types (standalone, no external dependencies)
class InformationChainNode(Enum):
    """Nodes in the information chain"""
    GNSS_CONSTELLATION = "gnss_constellation"
    SPACE_BASED_SENSOR = "space_based_sensor"
    AIRBORNE_SENSOR = "airborne_sensor"
    GROUND_RADAR = "ground_radar"
    LAUNCH_PLATFORM = "launch_platform"
    MISSILE_SEEKER = "missile_seeker"
    DATALINK_PRIMARY = "datalink_primary"
    DATALINK_BACKUP = "datalink_backup"
    FUSION_CENTER = "fusion_center"


@dataclass
class RobustnessScore:
    """Information chain robustness assessment"""
    overall_score: float
    sensor_fusion_score: float
    track_update_score: float
    communication_score: float
    discrimination_score: float
    midcourse_score: float
    terminal_score: float
    jam_resistance_score: float
    meets_requirements: bool
    deficiencies: List[str]
    recommendations: List[str]


@dataclass
class SensorNode:
    """Information chain sensor node"""
    node_type: InformationChainNode
    availability: float
    update_rate_hz: float
    track_accuracy_cep_m: float
    jam_resistance_db: float
    coverage_range_km: float
    latency_ms: float


@dataclass
class DatalinkPath:
    """Datalink communication path"""
    path_id: str
    is_primary: bool
    availability: float
    data_rate_kbps: float
    latency_ms: float
    jam_resistance_db: float
    max_range_km: float
    fec_capability: bool


@dataclass
class InformationChainConfiguration:
    """Complete information chain configuration"""
    sensor_nodes: List[SensorNode]
    datalink_paths: List[DatalinkPath]
    fusion_enabled: bool
    fusion_cep_m: float
    terminal_guidance_modes: List[str]
    backup_navigation: bool


class SystemDomain(Enum):
    """Operational domain for system"""
    AIR = "air"
    GROUND = "ground"
    SEA_SURFACE = "sea_surface"
    SUBSURFACE = "subsurface"
    SPACE = "space"
    CYBER = "cyber"
    MULTI_DOMAIN = "multi_domain"


class SystemRole(Enum):
    """Primary role of system"""
    SENSOR = "sensor"
    SHOOTER = "shooter"
    C2 = "command_and_control"
    COMMUNICATIONS = "communications"
    FUSION = "fusion"
    INTEGRATED = "integrated"  # Combines multiple roles


class TechnologyReadinessLevel(Enum):
    """Technology Readiness Level (TRL)"""
    TRL_1 = 1  # Basic principles observed
    TRL_2 = 2  # Technology concept formulated
    TRL_3 = 3  # Analytical/experimental proof of concept
    TRL_4 = 4  # Component validation in lab
    TRL_5 = 5  # Component validation in relevant environment
    TRL_6 = 6  # System prototype demo in relevant environment
    TRL_7 = 7  # System prototype demo in operational environment
    TRL_8 = 8  # Actual system completed and qualified
    TRL_9 = 9  # Actual system proven in operations


class ProductionTier(Enum):
    """Production readiness tier"""
    TIER_1_IMMEDIATE = "tier_1_immediate"  # TRL 6-7, ready for production
    TIER_2_NEAR_TERM = "tier_2_near_term"  # TRL 4-5, 2-4 year development
    TIER_3_SOFTWARE = "tier_3_software"    # Software/integration heavy


@dataclass
class DataLinkSpec:
    """Datalink specification"""
    name: str
    frequency_band: str
    bandwidth_mbps: float
    range_km: float
    latency_ms: float
    jam_resistance_db: float
    encryption: str
    redundancy_level: int  # Number of backup paths


@dataclass
class SensorSpec:
    """Sensor specification"""
    name: str
    sensor_type: str  # radar, esm, ir, eo, acoustic
    detection_range_km: float
    track_accuracy_cep_m: float
    update_rate_hz: float
    passive: bool
    jam_resistance_db: float


@dataclass
class WeaponSpec:
    """Weapon specification"""
    name: str
    weapon_type: str  # aam, sam, cruise, ballistic, torpedo
    range_km: float
    nez_km: float  # No-Escape Zone
    speed_mach: float
    guidance_modes: List[str]
    datalink_capable: bool
    unit_cost_million: float


@dataclass
class NetworkNode:
    """Node in the integrated network"""
    name: str
    domain: SystemDomain
    role: SystemRole
    survivability: float  # 0.0-1.0
    sensors: List[SensorSpec]
    weapons: List[WeaponSpec]
    datalinks: List[DataLinkSpec]
    can_relay: bool
    can_fuse_tracks: bool
    can_guide_weapons: bool  # Can guide weapons launched by other platforms


@dataclass
class SystemCostEstimate:
    """Cost breakdown for system"""
    development_cost_billion: float
    unit_cost_million: float
    annual_production_rate: int
    production_years: int
    total_program_cost_billion: float
    cost_per_capability_point: float  # Normalized metric


@dataclass
class NetworkResilienceScore:
    """Network resilience assessment"""
    overall_score: float  # 0-100
    node_redundancy_score: float
    link_redundancy_score: float
    graceful_degradation_score: float
    single_point_failures: List[str]
    critical_nodes: List[str]
    recommendations: List[str]


@dataclass
class SystemProposal:
    """Complete system proposal"""
    name: str
    codename: str
    description: str
    production_tier: ProductionTier
    trl: TechnologyReadinessLevel
    domains: List[SystemDomain]
    primary_role: SystemRole

    # Architecture
    network_nodes: List[NetworkNode]
    datalinks: List[DataLinkSpec]

    # Performance metrics
    detection_range_km: float
    track_accuracy_cep_m: float
    weapon_nez_km: float
    pk_at_200km: float
    passive_detection_capable: bool
    awacs_to_weapon_backup: bool

    # Scores
    network_resilience: NetworkResilienceScore
    information_chain_robustness: RobustnessScore

    # Costs
    cost_estimate: SystemCostEstimate

    # Metadata
    ioc_year: int
    foc_year: int
    confidence: float


class IntegratedSystemCAD:
    """
    Computer-Aided Design framework for integrated weapons systems.

    Generates system proposals following the core philosophy:
    - System-level integration over platform performance
    - Any-sensor-any-shooter architecture
    - Network resilience through redundancy
    - Passive detection for first-shot advantage
    - AWACS-to-weapon backup guidance

    BUDGET CONTEXT (FY2025):
    - Total DOD: $849.8B
    - Procurement: $168B
    - RDT&E: $143B
    - Total Acquisition: $311B/year
    - Realistic single program: $5-30B (major), $30-60B (flagship)
    """

    # FY2025 budget reference values (billions)
    BUDGET_PROCUREMENT = 168.0
    BUDGET_RDTE = 143.0
    BUDGET_TOTAL_ACQUISITION = 311.0

    # Program cost sanity limits
    MAX_REASONABLE_PROGRAM_COST = 80.0  # No single program > $80B except nuclear/carrier
    MAX_ANNUAL_SPEND_FRACTION = 0.15  # No program uses > 15% of annual acquisition

    def __init__(self):
        pass  # No external dependencies

    def validate_budget_sanity(
        self,
        cost_estimate: SystemCostEstimate,
        program_name: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that program costs are realistic against DOD budget.

        Returns (is_reasonable, list of warnings)
        """
        warnings = []
        is_reasonable = True

        total_cost = cost_estimate.total_program_cost_billion
        annual_cost = total_cost / max(1, cost_estimate.production_years)

        # Check total program cost
        if total_cost > self.MAX_REASONABLE_PROGRAM_COST:
            warnings.append(
                f"BUDGET WARNING: {program_name} total cost ${total_cost:.1f}B exceeds "
                f"reasonable limit of ${self.MAX_REASONABLE_PROGRAM_COST:.0f}B"
            )
            is_reasonable = False

        # Check annual spend rate
        annual_fraction = annual_cost / self.BUDGET_TOTAL_ACQUISITION
        if annual_fraction > self.MAX_ANNUAL_SPEND_FRACTION:
            warnings.append(
                f"BUDGET WARNING: {program_name} annual cost ${annual_cost:.1f}B/year is "
                f"{annual_fraction:.1%} of DOD acquisition budget (max {self.MAX_ANNUAL_SPEND_FRACTION:.0%})"
            )
            is_reasonable = False

        # Check unit cost sanity for platform programs
        if cost_estimate.unit_cost_million > 500:
            warnings.append(
                f"BUDGET WARNING: {program_name} unit cost ${cost_estimate.unit_cost_million:.0f}M "
                f"exceeds typical platform costs (suggest review)"
            )

        # Check production rate sanity
        if cost_estimate.annual_production_rate > 5000:
            warnings.append(
                f"BUDGET WARNING: {program_name} production rate {cost_estimate.annual_production_rate}/year "
                f"may exceed industrial base capacity"
            )

        return is_reasonable, warnings

    def assess_strategic_viability(
        self,
        proposal: 'SystemProposal',
        threat: ThreatEnvelope
    ) -> StrategicAssessment:
        """
        Assess system viability against A2/AD threat environment.

        This is the CRITICAL analysis: can this system actually contribute
        to defeating an A2/AD strategy, or is it a legacy concept?
        """
        recommendations = []

        # 1. RANGE ANALYSIS
        # Can we strike from outside the threat envelope?
        weapon_range = proposal.weapon_nez_km
        safe_standoff = threat.get_safe_standoff_range()
        required_range = threat.get_strike_range_required()

        can_strike_from_standoff = weapon_range >= required_range
        range_margin = weapon_range - required_range

        if not can_strike_from_standoff:
            recommendations.append(
                f"CRITICAL: Weapon range {weapon_range:.0f}km < required {required_range:.0f}km. "
                f"System must operate inside A2/AD envelope."
            )

        # 2. COST EXCHANGE ANALYSIS
        # Do our weapons cost less than their defenses?
        # Assume each of our weapons faces 2-4 SAM engagements
        our_weapon_cost = 0
        for node in proposal.network_nodes:
            for weapon in node.weapons:
                our_weapon_cost = max(our_weapon_cost, weapon.unit_cost_million)

        # Their defense cost: SAMs fired to intercept our weapon
        # Assume 2 SAMs per intercept attempt, 50% Pk per SAM = 4 SAMs to kill
        their_defense_cost = threat.sam_cost_million * 4

        if our_weapon_cost > 0:
            exchange_ratio = their_defense_cost / our_weapon_cost
        else:
            exchange_ratio = 0

        # Assessment of cost exchange
        if exchange_ratio >= 2.0:
            cost_assessment = "FAVORABLE"
        elif exchange_ratio >= 0.5:
            cost_assessment = "MARGINAL"
            recommendations.append(
                f"Cost exchange {exchange_ratio:.1f}:1 is marginal. "
                f"Consider lower-cost weapon variants."
            )
        else:
            cost_assessment = "UNFAVORABLE"
            recommendations.append(
                f"CRITICAL: Cost exchange {exchange_ratio:.2f}:1 is unfavorable. "
                f"Adversary wins attrition battle."
            )

        # Salvo analysis: how many weapons to saturate a defended target?
        # Assume target has 8-16 SAM launchers, each with 4 ready missiles
        defender_sam_inventory = 48  # Typical battalion
        weapons_per_salvo = int(defender_sam_inventory * 1.5)  # 1.5x to saturate
        salvos_to_saturate = 3  # Multiple target sets
        total_cost_to_saturate = (our_weapon_cost * weapons_per_salvo *
                                  salvos_to_saturate) / 1000

        cost_exchange = CostExchangeAnalysis(
            our_weapon_cost_million=our_weapon_cost,
            their_defense_cost_million=their_defense_cost,
            exchange_ratio=exchange_ratio,
            weapons_per_salvo=weapons_per_salvo,
            salvos_to_saturate=salvos_to_saturate,
            total_cost_to_saturate_billion=total_cost_to_saturate,
            assessment=cost_assessment
        )

        # 3. PLATFORM SURVIVABILITY
        # Can the launch platform survive in the threat environment?
        platform_domains = [n.domain for n in proposal.network_nodes if n.weapons]

        # Surface ships and aircraft are vulnerable to ASBMs/SAMs inside envelope
        operates_inside = not can_strike_from_standoff
        requires_air_sup = any(d == SystemDomain.AIR for d in platform_domains)

        if operates_inside:
            # Inside envelope, survivability is much lower
            if SystemDomain.SUBSURFACE in platform_domains:
                platform_survivability = 0.85  # Subs are survivable
            elif SystemDomain.GROUND in platform_domains:
                platform_survivability = 0.60  # Mobile ground is okay
            elif SystemDomain.AIR in platform_domains:
                platform_survivability = 0.30  # Aircraft very vulnerable
                recommendations.append(
                    "Aircraft platforms inside A2/AD envelope face high attrition. "
                    "Consider standoff weapons or unmanned options."
                )
            else:
                platform_survivability = 0.40
        else:
            # Outside envelope, much better
            platform_survivability = 0.90

        # 4. MASS AND PERSISTENCE
        # Can we generate enough volume to matter?
        total_weapons = sum(
            len(n.weapons) for n in proposal.network_nodes
        )
        salvo_size = max(1, total_weapons * 4)  # Assume 4 weapons per node
        reload_time = 4.0 if any(d == SystemDomain.GROUND for d in platform_domains) else 24.0
        sustainable_rate = int(salvo_size * (24 / reload_time))

        if sustainable_rate < 50:
            recommendations.append(
                f"Sustainable rate of {sustainable_rate}/day may be insufficient "
                f"for saturation attacks. Consider magazine depth."
            )

        # 5. OVERALL VIABILITY
        viable_factors = 0
        if can_strike_from_standoff:
            viable_factors += 2
        if exchange_ratio >= 1.0:
            viable_factors += 2
        if platform_survivability >= 0.6:
            viable_factors += 1
        if sustainable_rate >= 50:
            viable_factors += 1

        if viable_factors >= 5:
            viability = "VIABLE"
        elif viable_factors >= 3:
            viability = "MARGINAL"
        else:
            viability = "NOT_VIABLE"
            if not recommendations:
                recommendations.append(
                    "System concept does not address A2/AD threat. "
                    "Recommend redesign for standoff operations."
                )

        return StrategicAssessment(
            system_name=proposal.codename,
            threat_envelope=threat,
            weapon_range_km=weapon_range,
            safe_standoff_km=safe_standoff,
            can_strike_from_standoff=can_strike_from_standoff,
            range_margin_km=range_margin,
            cost_exchange=cost_exchange,
            platform_survivability_vs_threat=platform_survivability,
            can_operate_inside_envelope=operates_inside,
            requires_air_superiority=requires_air_sup,
            salvo_size=salvo_size,
            reload_time_hours=reload_time,
            sustainable_rate_per_day=sustainable_rate,
            strategic_viability=viability,
            recommendations=recommendations
        )

    def generate_strategic_report(
        self,
        assessment: StrategicAssessment
    ) -> str:
        """Generate strategic assessment report"""
        lines = []
        lines.append("")
        lines.append("STRATEGIC VIABILITY ASSESSMENT")
        lines.append("-" * 80)
        lines.append(f"System: {assessment.system_name}")
        lines.append(f"Threat: {assessment.threat_envelope.name}")
        lines.append(f"ASBM Range: {assessment.threat_envelope.asbm_range_km:.0f} km")
        lines.append(f"Safe Standoff: {assessment.safe_standoff_km:.0f} km")
        lines.append("")

        # Range verdict
        if assessment.can_strike_from_standoff:
            lines.append(f"  [PASS] STANDOFF: Weapon range {assessment.weapon_range_km:.0f} km")
            lines.append(f"         Margin: +{assessment.range_margin_km:.0f} km beyond required")
        else:
            lines.append(f"  [FAIL] STANDOFF: Weapon range {assessment.weapon_range_km:.0f} km")
            lines.append(f"         SHORTFALL: {-assessment.range_margin_km:.0f} km inside envelope")

        # Cost exchange verdict
        ce = assessment.cost_exchange
        if ce.assessment == "FAVORABLE":
            lines.append(f"  [PASS] COST EXCHANGE: {ce.exchange_ratio:.1f}:1 in our favor")
        elif ce.assessment == "MARGINAL":
            lines.append(f"  [WARN] COST EXCHANGE: {ce.exchange_ratio:.1f}:1 marginal")
        else:
            lines.append(f"  [FAIL] COST EXCHANGE: {ce.exchange_ratio:.2f}:1 unfavorable")
        lines.append(f"         Our weapon: ${ce.our_weapon_cost_million:.1f}M vs their defense: ${ce.their_defense_cost_million:.1f}M")

        # Platform survivability
        if assessment.platform_survivability_vs_threat >= 0.7:
            lines.append(f"  [PASS] SURVIVABILITY: {assessment.platform_survivability_vs_threat:.0%}")
        elif assessment.platform_survivability_vs_threat >= 0.5:
            lines.append(f"  [WARN] SURVIVABILITY: {assessment.platform_survivability_vs_threat:.0%}")
        else:
            lines.append(f"  [FAIL] SURVIVABILITY: {assessment.platform_survivability_vs_threat:.0%}")

        # Mass
        lines.append(f"  [INFO] SUSTAINABLE RATE: {assessment.sustainable_rate_per_day}/day")
        lines.append(f"         Salvo size: {assessment.salvo_size}, Reload: {assessment.reload_time_hours:.0f}h")

        lines.append("")
        lines.append(f"  OVERALL: *** {assessment.strategic_viability} ***")

        if assessment.recommendations:
            lines.append("")
            lines.append("  RECOMMENDATIONS:")
            for rec in assessment.recommendations:
                lines.append(f"    - {rec}")

        return "\n".join(lines)

    def calculate_network_resilience(
        self,
        nodes: List[NetworkNode],
        datalinks: List[DataLinkSpec]
    ) -> NetworkResilienceScore:
        """
        Calculate network resilience score.

        Based on:
        - Node redundancy (can survive node loss)
        - Link redundancy (multiple communication paths)
        - Graceful degradation (capability under attrition)
        """
        score = 0.0
        single_point_failures = []
        critical_nodes = []
        recommendations = []

        # Node redundancy (40 points max)
        node_score = 0.0

        # Count nodes by role
        role_counts = {}
        for node in nodes:
            role = node.role.value
            role_counts[role] = role_counts.get(role, 0) + 1

        # Sensor nodes
        sensor_count = sum(1 for n in nodes if n.sensors)
        if sensor_count >= 3:
            node_score += 15
        elif sensor_count >= 2:
            node_score += 10
        else:
            single_point_failures.append("Single sensor node")
            node_score += 5

        # Shooter nodes
        shooter_count = sum(1 for n in nodes if n.weapons)
        if shooter_count >= 4:
            node_score += 15
        elif shooter_count >= 2:
            node_score += 10
        else:
            node_score += 5

        # C2 nodes
        c2_count = sum(1 for n in nodes if n.can_fuse_tracks or n.can_guide_weapons)
        if c2_count >= 2:
            node_score += 10
        elif c2_count >= 1:
            node_score += 5
            critical_nodes.append("Single C2 node")
        else:
            single_point_failures.append("No C2 capability")

        # Apply survivability weighting
        survivabilities = [n.survivability for n in nodes]
        avg_survivability = sum(survivabilities) / len(survivabilities) if survivabilities else 0
        node_score *= avg_survivability
        score += min(40, node_score)

        # Link redundancy (30 points max)
        link_score = 0.0
        num_links = len(datalinks)

        if num_links >= 4:
            link_score += 20
        elif num_links >= 2:
            link_score += 15
        elif num_links >= 1:
            link_score += 8
            single_point_failures.append("Single datalink type")
        else:
            single_point_failures.append("No datalinks")

        # Check for relay capability
        relay_nodes = sum(1 for n in nodes if n.can_relay)
        if relay_nodes >= 2:
            link_score += 10
        elif relay_nodes >= 1:
            link_score += 5

        score += min(30, link_score)

        # Graceful degradation (30 points max)
        degrade_score = 0.0

        # AWACS-to-weapon backup (critical for resilience)
        awacs_backup = any(n.can_guide_weapons and n.domain == SystemDomain.AIR
                          for n in nodes)
        ground_backup = any(n.can_guide_weapons and n.domain == SystemDomain.GROUND
                           for n in nodes)

        if awacs_backup and ground_backup:
            degrade_score += 15
        elif awacs_backup or ground_backup:
            degrade_score += 10
        else:
            recommendations.append("Add AWACS-to-weapon backup guidance capability")
            degrade_score += 0

        # Multiple sensor types survive single-mode jamming
        sensor_types = set()
        for node in nodes:
            for sensor in node.sensors:
                sensor_types.add(sensor.sensor_type)

        if len(sensor_types) >= 4:
            degrade_score += 15
        elif len(sensor_types) >= 2:
            degrade_score += 10
        else:
            recommendations.append("Diversify sensor types for jam resistance")
            degrade_score += 5

        score += min(30, degrade_score)

        # Generate recommendations
        if score < 80:
            if node_score < 30:
                recommendations.append("Increase node redundancy")
            if link_score < 20:
                recommendations.append("Add backup datalink paths")

        return NetworkResilienceScore(
            overall_score=score,
            node_redundancy_score=node_score,
            link_redundancy_score=link_score,
            graceful_degradation_score=degrade_score,
            single_point_failures=single_point_failures,
            critical_nodes=critical_nodes,
            recommendations=recommendations
        )

    def calculate_kill_chain_pk(
        self,
        track_accuracy_cep_m: float,
        weapon_nez_km: float,
        engagement_range_km: float,
        network_resilience_score: float,
        awacs_backup: bool,
        mission_type: str = "air_defense"
    ) -> float:
        """
        Calculate kill chain probability (Pk).

        mission_type:
        - "air_defense": Engaging maneuvering air targets (aircraft, cruise missiles)
        - "strike": Attacking fixed/slow ground/sea targets
        - "sensor_only": No weapons, return sensor contribution factor

        Factors:
        - Track accuracy (better track = higher Pk)
        - Weapon NEZ (inside NEZ = higher Pk)
        - Network resilience (redundancy bonus)
        - AWACS backup (if shooter lost, weapon continues)
        """
        # Sensor-only systems contribute to kill chain but don't have direct Pk
        if mission_type == "sensor_only" or weapon_nez_km <= 0:
            # Return a "contribution factor" based on sensor quality
            if track_accuracy_cep_m <= 50:
                return 0.35  # High quality cueing
            elif track_accuracy_cep_m <= 200:
                return 0.25
            else:
                return 0.15

        if mission_type == "strike":
            # Strike missions against fixed/slow targets
            # CEP matters more than tracking rate
            # Defenses matter (addressed separately)

            # CEP-based Pk for strike
            if track_accuracy_cep_m <= 10:
                track_pk = 0.95  # Precision strike
            elif track_accuracy_cep_m <= 30:
                track_pk = 0.90
            elif track_accuracy_cep_m <= 100:
                track_pk = 0.80
            elif track_accuracy_cep_m <= 500:
                track_pk = 0.65  # Area effect needed
            else:
                track_pk = 0.40  # Requires large warhead

            # Range doesn't matter as much for strike - if in range, you're in range
            if engagement_range_km <= weapon_nez_km:
                range_pk = 0.95
            else:
                range_pk = 0.20  # Out of range

            # Defense penetration factor for strike
            # Hypersonic = high penetration, subsonic = lower
            # This is a simplification - real models need threat environment
            penetration_factor = 0.85  # Assumed moderate defenses

        else:
            # Air defense missions - maneuvering targets
            # Track accuracy baseline
            if track_accuracy_cep_m <= 25:
                track_pk = 0.92
            elif track_accuracy_cep_m <= 50:
                track_pk = 0.85
            elif track_accuracy_cep_m <= 100:
                track_pk = 0.75
            elif track_accuracy_cep_m <= 200:
                track_pk = 0.60
            else:
                track_pk = 0.40

            # Range factor (inside NEZ = optimal for air defense)
            range_ratio = engagement_range_km / weapon_nez_km
            if range_ratio <= 0.6:
                range_pk = 0.95  # Deep inside NEZ
            elif range_ratio <= 0.8:
                range_pk = 0.88
            elif range_ratio <= 1.0:
                range_pk = 0.75  # At NEZ edge
            elif range_ratio <= 1.2:
                range_pk = 0.50  # Tail chase possible
            else:
                range_pk = 0.20  # Very low Pk

            penetration_factor = 1.0  # Not applicable for air defense

        # Network resilience bonus (applies to all)
        # Good network = better track handoffs, guidance updates
        resilience_factor = 0.85 + (network_resilience_score / 600)  # 0.85-1.0

        # AWACS backup bonus (prevents missile going ballistic)
        backup_factor = 1.08 if awacs_backup else 1.00

        # Combined Pk
        pk = track_pk * range_pk * resilience_factor * backup_factor * penetration_factor

        # Reality cap - even best systems have some failure rate
        return min(0.95, pk)

    def estimate_costs(
        self,
        nodes: List[NetworkNode],
        development_complexity: float,  # 0.5-2.0 multiplier
        production_rate: int,
        production_years: int,
        is_munition_program: bool = False,
        munition_unit_cost_million: float = 0.0,
        launcher_count: int = 0
    ) -> SystemCostEstimate:
        """
        Estimate system costs.

        Based on node types, integration complexity, and production scale.

        For munition programs (missiles, drones), use:
        - is_munition_program=True
        - munition_unit_cost_million: cost per round/missile
        - launcher_count: number of launchers to procure
        - production_rate: munitions per year
        """
        # Base costs by node type ($ millions) - for platforms/launchers
        base_costs = {
            SystemDomain.AIR: 100,
            SystemDomain.GROUND: 50,
            SystemDomain.SEA_SURFACE: 500,
            SystemDomain.SUBSURFACE: 800,
            SystemDomain.SPACE: 200,
            SystemDomain.CYBER: 10,
            SystemDomain.MULTI_DOMAIN: 150
        }

        if is_munition_program:
            # For munition programs: launchers + munitions
            # Launcher cost
            launcher_unit_cost = 0
            for node in nodes:
                if node.domain == SystemDomain.GROUND:
                    launcher_unit_cost += 15  # Mobile launcher ~$15M
                elif node.domain == SystemDomain.AIR:
                    launcher_unit_cost += 5   # Aircraft integration
            launcher_unit_cost = max(10, launcher_unit_cost)  # Minimum $10M

            launcher_cost = (launcher_unit_cost * launcher_count) / 1000  # Billions

            # Munition cost
            total_munitions = production_rate * production_years
            munition_cost = (munition_unit_cost_million * total_munitions) / 1000  # Billions

            # Development cost
            base_dev_cost = 1.5  # Munition dev typically cheaper
            dev_cost = base_dev_cost * development_complexity

            total_cost = dev_cost + launcher_cost + munition_cost
            unit_cost = munition_unit_cost_million  # Report munition cost as unit cost

        else:
            # Standard platform program
            unit_cost = 0
            for node in nodes:
                unit_cost += base_costs.get(node.domain, 100)

                # Add sensor costs
                for sensor in node.sensors:
                    if sensor.sensor_type == 'radar':
                        unit_cost += 20
                    elif sensor.sensor_type == 'esm':
                        unit_cost += 15
                    elif sensor.sensor_type == 'ir':
                        unit_cost += 10

                # Add weapon integration costs (not per-weapon, integration only)
                if node.weapons:
                    unit_cost += 5 * len(node.weapons)

            unit_cost /= max(1, len(nodes))  # Average per node

            # Development cost (based on complexity and TRL)
            base_dev_cost = 2.0  # $2B baseline
            dev_cost = base_dev_cost * development_complexity

            # Integration cost (higher for more nodes/links)
            integration_cost = len(nodes) * 0.1 + len(set(n.domain for n in nodes)) * 0.3
            dev_cost += integration_cost

            # Total program cost
            total_units = production_rate * production_years
            production_cost = (unit_cost * total_units) / 1000  # Convert to billions
            total_cost = dev_cost + production_cost

        # Sanity check - no single program should exceed $200B
        if total_cost > 200:
            # This indicates a modeling error - cap and flag
            total_cost = min(total_cost, 200)

        # Cost per capability point (normalized)
        avg_resilience = 70  # Assumed average
        cost_per_point = total_cost / avg_resilience

        return SystemCostEstimate(
            development_cost_billion=dev_cost,
            unit_cost_million=unit_cost,
            annual_production_rate=production_rate,
            production_years=production_years,
            total_program_cost_billion=total_cost,
            cost_per_capability_point=cost_per_point
        )

    def create_information_chain_config(
        self,
        nodes: List[NetworkNode],
        datalinks: List[DataLinkSpec]
    ) -> InformationChainConfiguration:
        """
        Create information chain configuration from network nodes.
        """
        # Convert sensors to SensorNode format
        sensor_nodes = []
        for node in nodes:
            for sensor in node.sensors:
                # Map sensor type to InformationChainNode
                if 'gnss' in sensor.sensor_type.lower() or 'gps' in sensor.sensor_type.lower():
                    node_type = InformationChainNode.GNSS_CONSTELLATION
                elif 'awacs' in sensor.name.lower() or node.domain == SystemDomain.AIR:
                    node_type = InformationChainNode.AIRBORNE_SENSOR
                elif 'ground' in node.name.lower() or node.domain == SystemDomain.GROUND:
                    node_type = InformationChainNode.GROUND_RADAR
                elif 'seeker' in sensor.name.lower():
                    node_type = InformationChainNode.MISSILE_SEEKER
                elif 'space' in node.name.lower() or node.domain == SystemDomain.SPACE:
                    node_type = InformationChainNode.SPACE_BASED_SENSOR
                else:
                    node_type = InformationChainNode.AIRBORNE_SENSOR

                sensor_nodes.append(SensorNode(
                    node_type=node_type,
                    availability=node.survivability,
                    update_rate_hz=sensor.update_rate_hz,
                    track_accuracy_cep_m=sensor.track_accuracy_cep_m,
                    jam_resistance_db=sensor.jam_resistance_db,
                    coverage_range_km=sensor.detection_range_km,
                    latency_ms=100  # Default
                ))

        # Convert datalinks to DatalinkPath format
        datalink_paths = []
        for i, dl in enumerate(datalinks):
            datalink_paths.append(DatalinkPath(
                path_id=f"{dl.name}_{i}",
                is_primary=(i == 0),
                availability=0.95,
                data_rate_kbps=dl.bandwidth_mbps * 1000,
                latency_ms=dl.latency_ms,
                jam_resistance_db=dl.jam_resistance_db,
                max_range_km=dl.range_km,
                fec_capability=True
            ))

        # Determine guidance modes
        guidance_modes = set()
        for node in nodes:
            for weapon in node.weapons:
                guidance_modes.update(weapon.guidance_modes)

        return InformationChainConfiguration(
            sensor_nodes=sensor_nodes,
            datalink_paths=datalink_paths,
            fusion_enabled=any(n.can_fuse_tracks for n in nodes),
            fusion_cep_m=min((s.track_accuracy_cep_m for s in sensor_nodes), default=100),
            terminal_guidance_modes=list(guidance_modes),
            backup_navigation=True
        )

    def validate_information_chain(
        self,
        config: InformationChainConfiguration
    ) -> RobustnessScore:
        """
        Validate information chain robustness.

        Realistic scoring with inherent system limitations.
        No real system achieves 100/100 - there are always failure modes.
        """
        deficiencies = []
        recommendations = []

        # Sensor fusion score (0-100)
        # Even 4+ sensors have integration latency, correlation errors
        num_sensors = len(config.sensor_nodes)
        if num_sensors >= 4:
            sensor_score = 88  # Integration complexity limits perfect fusion
            if num_sensors >= 6:
                sensor_score = 92  # Diminishing returns
        elif num_sensors >= 3:
            sensor_score = 78
        elif num_sensors >= 2:
            sensor_score = 65
            recommendations.append("Add third sensor type for robust triangulation")
        else:
            sensor_score = 35
            deficiencies.append("Insufficient sensor redundancy")

        # Check sensor diversity (same-type sensors less valuable)
        if config.sensor_nodes:
            sensor_types = set(s.node_type.value for s in config.sensor_nodes)
            if len(sensor_types) < num_sensors:
                sensor_score -= 10  # Penalty for non-diverse sensors
                recommendations.append("Diversify sensor modalities (radar/ESM/IR)")

        # Track update score - real systems have latency
        if config.sensor_nodes:
            max_update = max(s.update_rate_hz for s in config.sensor_nodes)
            avg_latency = sum(s.latency_ms for s in config.sensor_nodes) / len(config.sensor_nodes)

            if max_update >= 10:
                track_score = 90  # Very fast but network latency exists
            elif max_update >= 5:
                track_score = 85
            elif max_update >= 1:
                track_score = 72
            else:
                track_score = 45
                deficiencies.append("Low track update rate")

            # Latency penalty
            if avg_latency > 200:
                track_score -= 10
                recommendations.append("Reduce sensor-to-fusion latency")
        else:
            track_score = 0

        # Communication score - jamming, atmospheric effects, range limits
        num_links = len(config.datalink_paths)
        if num_links >= 4:
            comm_score = 88  # Still vulnerable to coordinated jamming
        elif num_links >= 3:
            comm_score = 82
        elif num_links >= 2:
            comm_score = 70
        elif num_links >= 1:
            comm_score = 45
            deficiencies.append("Single datalink is critical vulnerability")
        else:
            comm_score = 0
            deficiencies.append("No datalinks configured")

        # Check for LOS limitations
        if config.datalink_paths:
            max_range = max(p.max_range_km for p in config.datalink_paths)
            if max_range < 500:
                comm_score -= 8
                recommendations.append("Extend datalink range for deep operations")

        # Discrimination score - decoys, clutter, ECM always degrade this
        if config.fusion_enabled:
            discrimination_score = 75  # Fusion helps but isn't perfect
            if num_sensors >= 3:
                discrimination_score = 82  # Multi-phenomenology improves discrimination
        else:
            discrimination_score = 48
            deficiencies.append("No sensor fusion degrades target discrimination")

        # Midcourse score - real-world comm blackouts, update gaps
        if num_links >= 3:
            midcourse_score = 82
        elif num_links >= 2:
            midcourse_score = 72
        else:
            midcourse_score = 50
            recommendations.append("Add backup midcourse update path")

        # Terminal score - seekers have FOV limits, countermeasures exist
        num_modes = len(config.terminal_guidance_modes)
        if num_modes >= 4:
            terminal_score = 88
        elif num_modes >= 3:
            terminal_score = 82
        elif num_modes >= 2:
            terminal_score = 70
        else:
            terminal_score = 45
            deficiencies.append("Single terminal guidance mode is vulnerable")

        # INS backup matters
        if not config.backup_navigation:
            terminal_score -= 15
            deficiencies.append("No INS backup for GNSS-denied environment")

        # Jam resistance score - even "jam resistant" systems have limits
        if config.sensor_nodes:
            min_jam = min(s.jam_resistance_db for s in config.sensor_nodes)
            avg_jam = sum(s.jam_resistance_db for s in config.sensor_nodes) / len(config.sensor_nodes)

            if min_jam >= 25 and avg_jam >= 28:
                jam_score = 85  # Good but determined adversary can still degrade
            elif avg_jam >= 20:
                jam_score = 72
            elif avg_jam >= 15:
                jam_score = 58
            else:
                jam_score = 35
                deficiencies.append("Insufficient jam resistance")

            # Weakest link matters
            if min_jam < avg_jam - 10:
                jam_score -= 8
                recommendations.append(f"Upgrade weakest sensor jam resistance ({min_jam:.0f} dB)")
        else:
            jam_score = 0

        # Overall score (weighted)
        overall = (
            sensor_score * 0.20 +
            track_score * 0.15 +
            comm_score * 0.20 +
            discrimination_score * 0.10 +
            midcourse_score * 0.15 +
            terminal_score * 0.15 +
            jam_score * 0.05
        )

        # Reality check - no operational system exceeds 92
        overall = min(92, overall)

        meets_requirements = overall >= 70 and len(deficiencies) == 0

        return RobustnessScore(
            overall_score=overall,
            sensor_fusion_score=sensor_score,
            track_update_score=track_score,
            communication_score=comm_score,
            discrimination_score=discrimination_score,
            midcourse_score=midcourse_score,
            terminal_score=terminal_score,
            jam_resistance_score=jam_score,
            meets_requirements=meets_requirements,
            deficiencies=deficiencies,
            recommendations=recommendations
        )

    def generate_proposal(
        self,
        name: str,
        codename: str,
        description: str,
        nodes: List[NetworkNode],
        datalinks: List[DataLinkSpec],
        trl: TechnologyReadinessLevel,
        ioc_year: int,
        foc_year: int,
        development_complexity: float = 1.0,
        production_rate: int = 50,
        production_years: int = 5,
        mission_type: str = "air_defense",
        is_munition_program: bool = False,
        munition_unit_cost_million: float = 0.0,
        launcher_count: int = 0
    ) -> SystemProposal:
        """
        Generate complete system proposal with all analyses.

        mission_type: "air_defense", "strike", or "sensor_only"
        is_munition_program: True for mass-production missiles/drones
        munition_unit_cost_million: Per-round cost if munition program
        launcher_count: Number of launchers if munition program
        """
        # Determine production tier from TRL
        if trl.value >= 6:
            production_tier = ProductionTier.TIER_1_IMMEDIATE
        elif trl.value >= 4:
            production_tier = ProductionTier.TIER_2_NEAR_TERM
        else:
            production_tier = ProductionTier.TIER_3_SOFTWARE

        # Determine domains
        domains = list(set(n.domain for n in nodes))

        # Primary role (most common)
        role_counts = {}
        for node in nodes:
            role_counts[node.role] = role_counts.get(node.role, 0) + 1
        primary_role = max(role_counts, key=role_counts.get) if role_counts else SystemRole.INTEGRATED

        # Calculate performance metrics
        all_sensors = [s for n in nodes for s in n.sensors]
        all_weapons = [w for n in nodes for w in n.weapons]

        detection_range = max((s.detection_range_km for s in all_sensors), default=0)
        track_accuracy = min((s.track_accuracy_cep_m for s in all_sensors), default=100)
        weapon_nez = max((w.nez_km for w in all_weapons), default=0)
        passive_capable = any(s.passive for s in all_sensors)
        awacs_backup = any(n.can_guide_weapons and n.domain == SystemDomain.AIR for n in nodes)

        # Calculate network resilience
        resilience = self.calculate_network_resilience(nodes, datalinks)

        # Calculate Pk with appropriate mission type
        # Use weapon range for engagement range in strike missions
        if mission_type == "strike":
            engagement_range = weapon_nez * 0.8  # Typical strike at 80% of max range
        else:
            engagement_range = 200  # Standard 200 km air defense engagement

        pk = self.calculate_kill_chain_pk(
            track_accuracy,
            weapon_nez,
            engagement_range,
            resilience.overall_score,
            awacs_backup,
            mission_type
        )

        # Create info chain config and validate
        info_config = self.create_information_chain_config(nodes, datalinks)
        info_robustness = self.validate_information_chain(info_config)

        # Estimate costs with proper parameters
        costs = self.estimate_costs(
            nodes,
            development_complexity,
            production_rate,
            production_years,
            is_munition_program,
            munition_unit_cost_million,
            launcher_count
        )

        # Confidence based on TRL and resilience
        confidence = 0.3 + (trl.value / 18) + (resilience.overall_score / 200)
        confidence = min(0.85, confidence)

        return SystemProposal(
            name=name,
            codename=codename,
            description=description,
            production_tier=production_tier,
            trl=trl,
            domains=domains,
            primary_role=primary_role,
            network_nodes=nodes,
            datalinks=datalinks,
            detection_range_km=detection_range,
            track_accuracy_cep_m=track_accuracy,
            weapon_nez_km=weapon_nez,
            pk_at_200km=pk,
            passive_detection_capable=passive_capable,
            awacs_to_weapon_backup=awacs_backup,
            network_resilience=resilience,
            information_chain_robustness=info_robustness,
            cost_estimate=costs,
            ioc_year=ioc_year,
            foc_year=foc_year,
            confidence=confidence
        )

    def generate_report(self, proposal: SystemProposal) -> str:
        """Generate comprehensive proposal report"""
        report = []
        report.append("=" * 80)
        report.append(f"SYSTEM PROPOSAL: {proposal.name}")
        report.append(f"CODENAME: {proposal.codename}")
        report.append("=" * 80)
        report.append("")
        report.append(f"Description: {proposal.description}")
        report.append("")
        report.append(f"Production Tier: {proposal.production_tier.value}")
        report.append(f"Technology Readiness Level: TRL-{proposal.trl.value}")
        report.append(f"IOC: {proposal.ioc_year} | FOC: {proposal.foc_year}")
        report.append(f"Confidence: {proposal.confidence:.0%}")
        report.append("")

        report.append("OPERATIONAL DOMAINS")
        report.append("-" * 80)
        for domain in proposal.domains:
            report.append(f"  - {domain.value}")
        report.append("")

        report.append("PERFORMANCE METRICS")
        report.append("-" * 80)
        report.append(f"  Detection Range:          {proposal.detection_range_km:.0f} km")
        report.append(f"  Track Accuracy:           {proposal.track_accuracy_cep_m:.1f} m CEP")
        report.append(f"  Weapon NEZ:               {proposal.weapon_nez_km:.0f} km")
        report.append(f"  Pk at 200 km:             {proposal.pk_at_200km:.2f}")
        report.append(f"  Passive Detection:        {'YES' if proposal.passive_detection_capable else 'NO'}")
        report.append(f"  AWACS-to-Weapon Backup:   {'YES' if proposal.awacs_to_weapon_backup else 'NO'}")
        report.append("")

        report.append("NETWORK ARCHITECTURE")
        report.append("-" * 80)
        report.append(f"  Nodes: {len(proposal.network_nodes)}")
        report.append(f"  Datalinks: {len(proposal.datalinks)}")
        for node in proposal.network_nodes:
            report.append(f"    [{node.domain.value}] {node.name}")
            report.append(f"        Sensors: {len(node.sensors)} | Weapons: {len(node.weapons)}")
            report.append(f"        Survivability: {node.survivability:.0%}")
            report.append(f"        Can Guide Weapons: {'YES' if node.can_guide_weapons else 'NO'}")
        report.append("")

        report.append("NETWORK RESILIENCE")
        report.append("-" * 80)
        res = proposal.network_resilience
        report.append(f"  Overall Score:            {res.overall_score:.1f}/100")
        report.append(f"  Node Redundancy:          {res.node_redundancy_score:.1f}/40")
        report.append(f"  Link Redundancy:          {res.link_redundancy_score:.1f}/30")
        report.append(f"  Graceful Degradation:     {res.graceful_degradation_score:.1f}/30")
        if res.single_point_failures:
            report.append("  Single Point Failures:")
            for spf in res.single_point_failures:
                report.append(f"    ! {spf}")
        if res.recommendations:
            report.append("  Recommendations:")
            for rec in res.recommendations:
                report.append(f"    - {rec}")
        report.append("")

        report.append("INFORMATION CHAIN ROBUSTNESS")
        report.append("-" * 80)
        info = proposal.information_chain_robustness
        report.append(f"  Overall Score:            {info.overall_score:.1f}/100")
        report.append(f"  Requirements Met:         {'YES' if info.meets_requirements else 'NO'}")
        report.append(f"  Sensor Fusion:            {info.sensor_fusion_score:.1f}/100")
        report.append(f"  Track Updates:            {info.track_update_score:.1f}/100")
        report.append(f"  Communications:           {info.communication_score:.1f}/100")
        report.append(f"  Terminal Guidance:        {info.terminal_score:.1f}/100")
        report.append(f"  Jam Resistance:           {info.jam_resistance_score:.1f}/100")
        report.append("")

        report.append("COST ESTIMATE")
        report.append("-" * 80)
        cost = proposal.cost_estimate
        report.append(f"  Development Cost:         ${cost.development_cost_billion:.2f}B")
        report.append(f"  Unit Cost:                ${cost.unit_cost_million:.1f}M")
        report.append(f"  Production Rate:          {cost.annual_production_rate}/year")
        report.append(f"  Production Period:        {cost.production_years} years")
        report.append(f"  Total Program Cost:       ${cost.total_program_cost_billion:.2f}B")

        # Budget sanity check
        is_reasonable, budget_warnings = self.validate_budget_sanity(cost, proposal.codename)
        annual_cost = cost.total_program_cost_billion / max(1, cost.production_years)
        budget_fraction = annual_cost / self.BUDGET_TOTAL_ACQUISITION
        report.append(f"  Annual Spend:             ${annual_cost:.1f}B/year ({budget_fraction:.1%} of DOD acquisition)")

        if not is_reasonable:
            report.append("  Budget Status:            *** EXCEEDS LIMITS ***")
        else:
            report.append("  Budget Status:            REASONABLE")

        for warning in budget_warnings:
            report.append(f"    ! {warning}")
        report.append("")

        report.append("=" * 80)
        report.append("Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY")
        report.append("=" * 80)

        return "\n".join(report)


def create_vanguard_proposal() -> SystemProposal:
    """
    Create VANGUARD Integrated Airborne-Ground Strike Network proposal.

    Based on: VANGUARD_INTEGRATED_STRIKE_NETWORK.md

    Core Philosophy: Integrated weapons and informational links
    - Any-sensor-any-shooter architecture
    - E-7 AWACS-to-weapon backup guidance
    - 4-path datalink redundancy
    - 350+ km passive detection range
    """
    cad = IntegratedSystemCAD()

    # Define datalinks
    datalinks = [
        DataLinkSpec(
            name="TTNT",
            frequency_band="UHF",
            bandwidth_mbps=10.0,
            range_km=300,
            latency_ms=10,
            jam_resistance_db=25,
            encryption="NSA Type 1",
            redundancy_level=4
        ),
        DataLinkSpec(
            name="CDL",
            frequency_band="Ku-band",
            bandwidth_mbps=274.0,
            range_km=200,
            latency_ms=50,
            jam_resistance_db=20,
            encryption="NSA Type 1",
            redundancy_level=2
        ),
        DataLinkSpec(
            name="Link16",
            frequency_band="UHF",
            bandwidth_mbps=0.115,
            range_km=300,
            latency_ms=200,
            jam_resistance_db=15,
            encryption="NSA Type 1",
            redundancy_level=1
        ),
        DataLinkSpec(
            name="AWW-13",
            frequency_band="C-band",
            bandwidth_mbps=1.0,
            range_km=400,
            latency_ms=300,
            jam_resistance_db=22,
            encryption="NSA Type 1",
            redundancy_level=3
        )
    ]

    # Define network nodes
    nodes = [
        # E-7 WEDGETAIL AWACS
        NetworkNode(
            name="E-7 WEDGETAIL",
            domain=SystemDomain.AIR,
            role=SystemRole.C2,
            survivability=0.85,
            sensors=[
                SensorSpec(
                    name="MESA AESA Radar",
                    sensor_type="radar",
                    detection_range_km=400,
                    track_accuracy_cep_m=100,
                    update_rate_hz=1.0,
                    passive=False,
                    jam_resistance_db=25
                ),
                SensorSpec(
                    name="Passive ESM Suite",
                    sensor_type="esm",
                    detection_range_km=600,
                    track_accuracy_cep_m=5000,  # Bearing only
                    update_rate_hz=10.0,
                    passive=True,
                    jam_resistance_db=30
                )
            ],
            weapons=[],
            datalinks=[datalinks[0], datalinks[1], datalinks[2], datalinks[3]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True  # CRITICAL: Can guide AIM-260, SM-6
        ),

        # F-35A Flight (4-ship)
        NetworkNode(
            name="F-35A Flight",
            domain=SystemDomain.AIR,
            role=SystemRole.SHOOTER,
            survivability=0.75,
            sensors=[
                SensorSpec(
                    name="APG-81 AESA",
                    sensor_type="radar",
                    detection_range_km=150,
                    track_accuracy_cep_m=50,
                    update_rate_hz=5.0,
                    passive=False,
                    jam_resistance_db=20
                ),
                SensorSpec(
                    name="ASQ-239 EW Suite",
                    sensor_type="esm",
                    detection_range_km=250,
                    track_accuracy_cep_m=3000,
                    update_rate_hz=10.0,
                    passive=True,
                    jam_resistance_db=25
                )
            ],
            weapons=[
                WeaponSpec(
                    name="AIM-260 JATM",
                    weapon_type="aam",
                    range_km=200,
                    nez_km=150,
                    speed_mach=4.0,
                    guidance_modes=["active_radar", "datalink", "inertial"],
                    datalink_capable=True,
                    unit_cost_million=3.0
                ),
                WeaponSpec(
                    name="AIM-120D AMRAAM",
                    weapon_type="aam",
                    range_km=160,
                    nez_km=80,
                    speed_mach=4.0,
                    guidance_modes=["active_radar", "datalink", "inertial"],
                    datalink_capable=True,
                    unit_cost_million=1.5
                )
            ],
            datalinks=[datalinks[0], datalinks[2]],
            can_relay=False,
            can_fuse_tracks=True,
            can_guide_weapons=True
        ),

        # CCA Swarm (8 drones)
        NetworkNode(
            name="CCA Swarm",
            domain=SystemDomain.AIR,
            role=SystemRole.SHOOTER,
            survivability=0.40,  # Attritable
            sensors=[
                SensorSpec(
                    name="CCA AESA",
                    sensor_type="radar",
                    detection_range_km=100,
                    track_accuracy_cep_m=80,
                    update_rate_hz=2.0,
                    passive=False,
                    jam_resistance_db=15
                )
            ],
            weapons=[
                WeaponSpec(
                    name="AIM-260 JATM",
                    weapon_type="aam",
                    range_km=200,
                    nez_km=150,
                    speed_mach=4.0,
                    guidance_modes=["active_radar", "datalink", "inertial"],
                    datalink_capable=True,
                    unit_cost_million=3.0
                )
            ],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),

        # SDA Satellite Layer
        NetworkNode(
            name="SDA Tracking Layer",
            domain=SystemDomain.SPACE,
            role=SystemRole.SENSOR,
            survivability=0.95,  # Proliferated constellation
            sensors=[
                SensorSpec(
                    name="WFOV IR Sensor",
                    sensor_type="ir",
                    detection_range_km=20000,
                    track_accuracy_cep_m=5000,
                    update_rate_hz=0.2,
                    passive=True,
                    jam_resistance_db=35
                )
            ],
            weapons=[],
            datalinks=[datalinks[1]],
            can_relay=True,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),

        # AEGIS Ashore
        NetworkNode(
            name="AEGIS Ashore",
            domain=SystemDomain.GROUND,
            role=SystemRole.SHOOTER,
            survivability=0.90,
            sensors=[
                SensorSpec(
                    name="SPY-6 AMDR",
                    sensor_type="radar",
                    detection_range_km=500,
                    track_accuracy_cep_m=30,
                    update_rate_hz=5.0,
                    passive=False,
                    jam_resistance_db=28
                )
            ],
            weapons=[
                WeaponSpec(
                    name="SM-6 Block IB",
                    weapon_type="sam",
                    range_km=370,
                    nez_km=200,
                    speed_mach=3.5,
                    guidance_modes=["active_radar", "semi_active", "datalink"],
                    datalink_capable=True,
                    unit_cost_million=4.5
                )
            ],
            datalinks=[datalinks[0], datalinks[2]],
            can_relay=False,
            can_fuse_tracks=True,
            can_guide_weapons=True  # Can guide on remote tracks (CEC)
        ),

        # Typhon Mobile Launcher
        NetworkNode(
            name="Typhon Battery",
            domain=SystemDomain.GROUND,
            role=SystemRole.SHOOTER,
            survivability=0.85,  # Mobile, shoot-and-scoot
            sensors=[],
            weapons=[
                WeaponSpec(
                    name="SM-6 Block IB",
                    weapon_type="sam",
                    range_km=370,
                    nez_km=200,
                    speed_mach=3.5,
                    guidance_modes=["active_radar", "semi_active", "datalink"],
                    datalink_capable=True,
                    unit_cost_million=4.5
                ),
                WeaponSpec(
                    name="Tomahawk Block V",
                    weapon_type="cruise",
                    range_km=1600,
                    nez_km=1600,
                    speed_mach=0.75,
                    guidance_modes=["gps", "tercom", "dsmac"],
                    datalink_capable=True,
                    unit_cost_million=2.0
                )
            ],
            datalinks=[datalinks[0], datalinks[2]],
            can_relay=False,
            can_fuse_tracks=False,
            can_guide_weapons=False  # Fire on remote tracks only
        ),

        # Ground Fusion Center
        NetworkNode(
            name="ODIN Fusion Center",
            domain=SystemDomain.GROUND,
            role=SystemRole.FUSION,
            survivability=0.95,  # Hardened, redundant
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0], datalinks[1], datalinks[2], datalinks[3]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True  # Backup weapon guidance via satellite
        )
    ]

    return cad.generate_proposal(
        name="VANGUARD Integrated Airborne-Ground Strike Network",
        codename="VANGUARD",
        description="Fully integrated any-sensor-any-shooter kill chain with E-7 AWACS-to-weapon backup guidance, 4-path datalink redundancy, and AI-optimized engagement planning.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_6,
        ioc_year=2029,
        foc_year=2032,
        development_complexity=1.5,
        production_rate=50,
        production_years=5
    )


def create_locust_swarm_proposal() -> SystemProposal:
    """
    Create LOCUST Scramjet Swarm Missile proposal.

    REALISTIC COST MODEL:
    - Current scramjets (X-51, etc.) cost $20-50M per test article
    - Mass production target: $3M/unit (aggressive but achievable by 2030s)
    - Compare: Tomahawk is $2M, JASSM-ER is $1.5M (subsonic, mature tech)
    - Scramjet premium is ~2x for thermal management + exotic materials

    Production rate: 500/year (one production line at rate)
    - Compare: Tomahawk production peaked at ~300/year
    """
    cad = IntegratedSystemCAD()

    datalinks = [
        DataLinkSpec(
            name="Swarm Mesh",
            frequency_band="UHF",
            bandwidth_mbps=1.0,
            range_km=100,
            latency_ms=50,
            jam_resistance_db=15,
            encryption="AES-256",
            redundancy_level=10  # Mesh network
        ),
        DataLinkSpec(
            name="Launch Control",
            frequency_band="Ku-band",
            bandwidth_mbps=10.0,
            range_km=500,
            latency_ms=100,
            jam_resistance_db=20,
            encryption="NSA Type 1",
            redundancy_level=2
        )
    ]

    nodes = [
        NetworkNode(
            name="LOCUST Missile Swarm",
            domain=SystemDomain.AIR,
            role=SystemRole.SHOOTER,
            survivability=0.30,  # Individual missiles expendable
            sensors=[
                SensorSpec(
                    name="MEMS INS",
                    sensor_type="inertial",
                    detection_range_km=0,
                    track_accuracy_cep_m=15,  # GPS denied
                    update_rate_hz=100.0,
                    passive=True,
                    jam_resistance_db=50  # No RF to jam
                ),
                SensorSpec(
                    name="MMW Seeker",
                    sensor_type="radar",
                    detection_range_km=30,
                    track_accuracy_cep_m=5,
                    update_rate_hz=20.0,
                    passive=False,
                    jam_resistance_db=15
                )
            ],
            weapons=[
                WeaponSpec(
                    name="LOCUST Scramjet",
                    weapon_type="cruise",
                    range_km=800,
                    nez_km=800,
                    speed_mach=5.0,
                    guidance_modes=["gps", "inertial", "mmw_terminal"],
                    datalink_capable=True,
                    unit_cost_million=3.0  # Realistic scramjet cost
                )
            ],
            datalinks=[datalinks[0]],
            can_relay=True,  # Mesh relay between missiles
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="Ground Launch Control",
            domain=SystemDomain.GROUND,
            role=SystemRole.C2,
            survivability=0.85,
            sensors=[],
            weapons=[],
            datalinks=[datalinks[1]],
            can_relay=False,
            can_fuse_tracks=False,
            can_guide_weapons=False
        )
    ]

    return cad.generate_proposal(
        name="LOCUST Scramjet Swarm Missile System",
        codename="LOCUST",
        description="Mach 5 scramjet cruise missiles ($3M/unit) for saturation attacks. Mesh-networked swarm coordination with ATR terminal guidance. 2,500 missiles over 5 years.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_5,  # Scramjet at scale is still TRL 5
        ioc_year=2031,  # Realistic: scramjet tech needs more development
        foc_year=2034,
        development_complexity=1.8,  # Scramjet is hard
        production_rate=500,  # 500 missiles/year - one production line
        production_years=5,
        mission_type="strike",
        is_munition_program=True,
        munition_unit_cost_million=3.0,  # $3M per missile (realistic for scramjet)
        launcher_count=50  # Mobile launchers
    )


def create_odin_fusion_proposal() -> SystemProposal:
    """
    Create ODIN AI Fusion Engine proposal.

    Software-heavy system for unified battlespace picture.
    """
    cad = IntegratedSystemCAD()

    datalinks = [
        DataLinkSpec(
            name="ODIN Backbone",
            frequency_band="Fiber/Satellite",
            bandwidth_mbps=100000.0,  # 100 Gbps
            range_km=20000,  # Global via satellite
            latency_ms=50,
            jam_resistance_db=30,
            encryption="NSA Type 1 + Quantum",
            redundancy_level=5
        )
    ]

    nodes = [
        NetworkNode(
            name="ODIN Cloud",
            domain=SystemDomain.CYBER,
            role=SystemRole.FUSION,
            survivability=0.99,  # Multi-site redundancy
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True
        ),
        NetworkNode(
            name="ODIN Edge (E-7)",
            domain=SystemDomain.AIR,
            role=SystemRole.FUSION,
            survivability=0.85,
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True
        ),
        NetworkNode(
            name="ODIN Mobile",
            domain=SystemDomain.GROUND,
            role=SystemRole.FUSION,
            survivability=0.90,
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True
        )
    ]

    return cad.generate_proposal(
        name="ODIN AI-Powered Sensor Fusion Engine",
        codename="ODIN",
        description="AI-powered sensor fusion platform creating unified battlespace picture. Enables any-sensor-any-shooter with <100ms latency track correlation.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_5,
        ioc_year=2029,
        foc_year=2031,
        development_complexity=2.0,  # High software complexity
        production_rate=20,  # Sites/year
        production_years=4
    )


# =============================================================================
# A2/AD-OPTIMIZED SYSTEMS
# =============================================================================
# These systems are specifically designed to defeat A2/AD strategies.
# Key requirements:
# 1. Weapon range > 5,000 km (outside DF-26 envelope + margin)
# 2. Favorable cost exchange (our weapons < their defenses)
# 3. Survivable platforms (subs, dispersed ground, unmanned)
# 4. Mass production for saturation
# =============================================================================

def create_trident_conventional_proposal() -> SystemProposal:
    """
    TRIDENT CONVENTIONAL - Submarine-Launched Conventional Strike

    WHY THIS WORKS AGAINST A2/AD:
    - SSGNs operate inside A2/AD envelope undetected
    - 154 Tomahawk capacity per SSGN
    - Can strike from <500 km (inside SAM envelope but sub is hidden)
    - No ASBM threat to submerged submarine
    - Cost exchange: $2M Tomahawk vs $12M SAM defense = 6:1 favorable
    """
    cad = IntegratedSystemCAD()

    datalinks = [
        DataLinkSpec(
            name="Submarine Broadcast",
            frequency_band="VLF/ELF",
            bandwidth_mbps=0.001,
            range_km=20000,
            latency_ms=30000,  # High latency for VLF
            jam_resistance_db=40,  # Hard to jam VLF
            encryption="NSA Type 1",
            redundancy_level=3
        ),
        DataLinkSpec(
            name="Floating Wire Antenna",
            frequency_band="HF",
            bandwidth_mbps=0.1,
            range_km=5000,
            latency_ms=1000,
            jam_resistance_db=20,
            encryption="NSA Type 1",
            redundancy_level=2
        )
    ]

    nodes = [
        NetworkNode(
            name="SSGN Ohio-class",
            domain=SystemDomain.SUBSURFACE,
            role=SystemRole.SHOOTER,
            survivability=0.95,  # Submarines are VERY survivable
            sensors=[
                SensorSpec(
                    name="BQQ-10 Sonar",
                    sensor_type="acoustic",
                    detection_range_km=100,
                    track_accuracy_cep_m=500,
                    update_rate_hz=0.1,
                    passive=True,
                    jam_resistance_db=50
                )
            ],
            weapons=[
                WeaponSpec(
                    name="Tomahawk Block V",
                    weapon_type="cruise",
                    range_km=1600,
                    nez_km=1600,
                    speed_mach=0.75,
                    guidance_modes=["gps", "tercom", "dsmac", "maritime_strike"],
                    datalink_capable=True,
                    unit_cost_million=2.0
                )
            ],
            datalinks=datalinks,
            can_relay=False,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="SUBPAC Command",
            domain=SystemDomain.GROUND,
            role=SystemRole.C2,
            survivability=0.99,
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True
        )
    ]

    return cad.generate_proposal(
        name="TRIDENT CONVENTIONAL Submarine Strike",
        codename="TRIDENT_CONV",
        description="SSGN-based conventional strike. 4 SSGNs with 154 Tomahawks each = 616 missiles. Subs penetrate A2/AD undetected, strike from close range. Favorable 6:1 cost exchange.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_9,  # Already operational
        ioc_year=2026,  # Already exists
        foc_year=2027,
        development_complexity=0.5,  # Existing capability
        production_rate=100,  # Missiles/year
        production_years=5,
        mission_type="strike",
        is_munition_program=True,
        munition_unit_cost_million=2.0,
        launcher_count=4  # 4 SSGNs
    )


def create_rapid_dragon_proposal() -> SystemProposal:
    """
    RAPID DRAGON - Palletized Long-Range Strike from Cargo Aircraft

    WHY THIS WORKS AGAINST A2/AD:
    - C-17/C-130 launch from 1,000+ km standoff (outside fighter CAP)
    - JASSM-XR range: 1,800+ km
    - Total standoff: 2,800+ km from target
    - Cargo aircraft fly from Guam/Australia (5,000+ km from China)
    - 36 JASSM per C-17 sortie
    - Cost: $1.5M JASSM vs $12M defense = 8:1 favorable
    """
    cad = IntegratedSystemCAD()

    datalinks = [
        DataLinkSpec(
            name="JASSM Datalink",
            frequency_band="UHF",
            bandwidth_mbps=0.5,
            range_km=2000,
            latency_ms=500,
            jam_resistance_db=18,
            encryption="NSA Type 1",
            redundancy_level=2
        ),
        DataLinkSpec(
            name="SATCOM Wideband",
            frequency_band="Ka-band",
            bandwidth_mbps=50,
            range_km=40000,
            latency_ms=300,
            jam_resistance_db=22,
            encryption="NSA Type 1",
            redundancy_level=4
        )
    ]

    nodes = [
        NetworkNode(
            name="C-17 Rapid Dragon Launcher",
            domain=SystemDomain.AIR,
            role=SystemRole.SHOOTER,
            survivability=0.90,  # Operating from standoff, not penetrating
            sensors=[],
            weapons=[
                WeaponSpec(
                    name="JASSM-XR",
                    weapon_type="cruise",
                    range_km=1800,
                    nez_km=1800,
                    speed_mach=0.85,
                    guidance_modes=["gps", "inertial", "ir_terminal"],
                    datalink_capable=True,
                    unit_cost_million=1.5
                )
            ],
            datalinks=[datalinks[1]],
            can_relay=False,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="SDA Targeting Layer",
            domain=SystemDomain.SPACE,
            role=SystemRole.SENSOR,
            survivability=0.95,
            sensors=[
                SensorSpec(
                    name="OPIR Tracking",
                    sensor_type="ir",
                    detection_range_km=20000,
                    track_accuracy_cep_m=100,
                    update_rate_hz=1.0,
                    passive=True,
                    jam_resistance_db=35
                )
            ],
            weapons=[],
            datalinks=[datalinks[1]],
            can_relay=True,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="Strike Planning Cell",
            domain=SystemDomain.GROUND,
            role=SystemRole.C2,
            survivability=0.95,
            sensors=[],
            weapons=[],
            datalinks=datalinks,
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True
        )
    ]

    return cad.generate_proposal(
        name="RAPID DRAGON Palletized Strike System",
        codename="RAPID_DRAGON",
        description="C-17 palletized JASSM-XR launch. 36 missiles per sortie, 1800km range. Launches from 1000km standoff = 2800km total. 8:1 cost exchange. Can surge 500+ missiles/day from Guam.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_7,  # Demonstrated, entering production
        ioc_year=2027,
        foc_year=2029,
        development_complexity=0.8,
        production_rate=500,  # JASSM-XR per year
        production_years=5,
        mission_type="strike",
        is_munition_program=True,
        munition_unit_cost_million=1.5,
        launcher_count=20  # Pallet systems for 20 C-17s
    )


def create_typhon_island_chain_proposal() -> SystemProposal:
    """
    TYPHON ISLAND CHAIN - Distributed Ground-Based Strike on First Island Chain

    WHY THIS WORKS AGAINST A2/AD:
    - Pre-positioned on Japan, Philippines, Guam
    - SM-6 for air defense (370 km)
    - Tomahawk for land attack (1600 km)
    - Mobile shoot-and-scoot survivability
    - Forces adversary to target dispersed ground sites (hard)
    - Flips the A2/AD equation: WE create the denied area for THEM
    """
    cad = IntegratedSystemCAD()

    datalinks = [
        DataLinkSpec(
            name="CEC",
            frequency_band="UHF/SHF",
            bandwidth_mbps=10.0,
            range_km=500,
            latency_ms=20,
            jam_resistance_db=25,
            encryption="NSA Type 1",
            redundancy_level=3
        ),
        DataLinkSpec(
            name="IBCS",
            frequency_band="UHF",
            bandwidth_mbps=5.0,
            range_km=300,
            latency_ms=50,
            jam_resistance_db=22,
            encryption="NSA Type 1",
            redundancy_level=4
        ),
        DataLinkSpec(
            name="SATCOM Backup",
            frequency_band="Ka-band",
            bandwidth_mbps=50,
            range_km=40000,
            latency_ms=200,
            jam_resistance_db=20,
            encryption="NSA Type 1",
            redundancy_level=5
        )
    ]

    nodes = [
        NetworkNode(
            name="Typhon Battery Alpha",
            domain=SystemDomain.GROUND,
            role=SystemRole.SHOOTER,
            survivability=0.75,  # Mobile, dispersed
            sensors=[],
            weapons=[
                WeaponSpec(
                    name="SM-6 Block IB",
                    weapon_type="sam",
                    range_km=370,
                    nez_km=200,
                    speed_mach=3.5,
                    guidance_modes=["active_radar", "semi_active", "datalink"],
                    datalink_capable=True,
                    unit_cost_million=4.5
                ),
                WeaponSpec(
                    name="Tomahawk Block V",
                    weapon_type="cruise",
                    range_km=1600,
                    nez_km=1600,
                    speed_mach=0.75,
                    guidance_modes=["gps", "tercom", "dsmac"],
                    datalink_capable=True,
                    unit_cost_million=2.0
                )
            ],
            datalinks=[datalinks[0], datalinks[1]],
            can_relay=False,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="Typhon Battery Bravo",
            domain=SystemDomain.GROUND,
            role=SystemRole.SHOOTER,
            survivability=0.75,
            sensors=[],
            weapons=[
                WeaponSpec(
                    name="SM-6 Block IB",
                    weapon_type="sam",
                    range_km=370,
                    nez_km=200,
                    speed_mach=3.5,
                    guidance_modes=["active_radar", "semi_active", "datalink"],
                    datalink_capable=True,
                    unit_cost_million=4.5
                ),
                WeaponSpec(
                    name="Tomahawk Block V",
                    weapon_type="cruise",
                    range_km=1600,
                    nez_km=1600,
                    speed_mach=0.75,
                    guidance_modes=["gps", "tercom", "dsmac"],
                    datalink_capable=True,
                    unit_cost_million=2.0
                )
            ],
            datalinks=[datalinks[0], datalinks[1]],
            can_relay=False,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="Mobile SPY-6 Radar",
            domain=SystemDomain.GROUND,
            role=SystemRole.SENSOR,
            survivability=0.70,
            sensors=[
                SensorSpec(
                    name="SPY-6(V)2",
                    sensor_type="radar",
                    detection_range_km=500,
                    track_accuracy_cep_m=30,
                    update_rate_hz=5.0,
                    passive=False,
                    jam_resistance_db=28
                )
            ],
            weapons=[],
            datalinks=[datalinks[0], datalinks[1]],
            can_relay=False,
            can_fuse_tracks=True,
            can_guide_weapons=True
        ),
        NetworkNode(
            name="Passive ESM Array",
            domain=SystemDomain.GROUND,
            role=SystemRole.SENSOR,
            survivability=0.85,
            sensors=[
                SensorSpec(
                    name="AN/SLQ-32 Derivative",
                    sensor_type="esm",
                    detection_range_km=600,
                    track_accuracy_cep_m=2000,
                    update_rate_hz=10.0,
                    passive=True,
                    jam_resistance_db=40
                )
            ],
            weapons=[],
            datalinks=[datalinks[1]],
            can_relay=True,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="IBCS Fire Control",
            domain=SystemDomain.GROUND,
            role=SystemRole.C2,
            survivability=0.80,
            sensors=[],
            weapons=[],
            datalinks=datalinks,
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True
        )
    ]

    return cad.generate_proposal(
        name="TYPHON ISLAND CHAIN Distributed Strike",
        codename="TYPHON_IC",
        description="Distributed Typhon batteries on first island chain (Japan, Philippines, Guam). SM-6 for air/missile defense, Tomahawk for strike. Creates OUR A2/AD against THEM. 16 batteries = 256 launchers.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_7,
        ioc_year=2027,  # Already deploying
        foc_year=2030,
        development_complexity=1.0,
        production_rate=32,  # Launchers/year
        production_years=5,
        mission_type="air_defense"  # Primary mission is defensive
    )


def create_b21_lrso_proposal() -> SystemProposal:
    """
    B-21 + LRSO - Penetrating Stealth Bomber with Standoff Cruise Missiles

    WHY THIS WORKS AGAINST A2/AD:
    - B-21 operates from CONUS (10,000+ km from China)
    - LRSO range: 2,500+ km
    - Can launch from outside all threat envelopes
    - Stealth allows penetration if needed
    - Nuclear-capable = strategic deterrent value
    - 20 B-21s with 16 LRSO each = 320 missiles per wave
    """
    cad = IntegratedSystemCAD()

    datalinks = [
        DataLinkSpec(
            name="B-21 Satcom",
            frequency_band="EHF",
            bandwidth_mbps=10.0,
            range_km=40000,
            latency_ms=250,
            jam_resistance_db=30,
            encryption="NSA Type 1",
            redundancy_level=5
        ),
        DataLinkSpec(
            name="LRSO Datalink",
            frequency_band="UHF",
            bandwidth_mbps=0.5,
            range_km=2500,
            latency_ms=500,
            jam_resistance_db=18,
            encryption="NSA Type 1",
            redundancy_level=2
        )
    ]

    nodes = [
        NetworkNode(
            name="B-21 Raider",
            domain=SystemDomain.AIR,
            role=SystemRole.SHOOTER,
            survivability=0.85,  # Very low observable
            sensors=[
                SensorSpec(
                    name="APQ-181 Derivative",
                    sensor_type="radar",
                    detection_range_km=300,
                    track_accuracy_cep_m=20,
                    update_rate_hz=2.0,
                    passive=False,  # LPI radar
                    jam_resistance_db=30
                ),
                SensorSpec(
                    name="DAS IR Suite",
                    sensor_type="ir",
                    detection_range_km=200,
                    track_accuracy_cep_m=50,
                    update_rate_hz=30.0,
                    passive=True,
                    jam_resistance_db=40
                )
            ],
            weapons=[
                WeaponSpec(
                    name="LRSO",
                    weapon_type="cruise",
                    range_km=2500,
                    nez_km=2500,
                    speed_mach=0.85,
                    guidance_modes=["gps", "tercom", "ir_terminal"],
                    datalink_capable=True,
                    unit_cost_million=3.0
                )
            ],
            datalinks=[datalinks[0]],
            can_relay=False,
            can_fuse_tracks=True,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="Global Strike Command",
            domain=SystemDomain.GROUND,
            role=SystemRole.C2,
            survivability=0.99,
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True
        ),
        NetworkNode(
            name="SDA Cueing Layer",
            domain=SystemDomain.SPACE,
            role=SystemRole.SENSOR,
            survivability=0.95,
            sensors=[
                SensorSpec(
                    name="OPIR Wide Field",
                    sensor_type="ir",
                    detection_range_km=20000,
                    track_accuracy_cep_m=500,
                    update_rate_hz=0.5,
                    passive=True,
                    jam_resistance_db=35
                )
            ],
            weapons=[],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=False,
            can_guide_weapons=False
        )
    ]

    return cad.generate_proposal(
        name="B-21 RAIDER with LRSO Strike System",
        codename="B21_LRSO",
        description="B-21 stealth bomber launching LRSO cruise missiles. Operates from CONUS (Whiteman, Dyess). 2500km LRSO range + 5000km B-21 combat radius = strike anywhere from sanctuary.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_6,  # B-21 in flight test
        ioc_year=2028,
        foc_year=2032,
        development_complexity=1.8,  # High but ongoing
        production_rate=100,  # LRSOs per year
        production_years=5,
        mission_type="strike",
        is_munition_program=True,
        munition_unit_cost_million=3.0,
        launcher_count=20  # Initial B-21 fleet
    )


def main():
    """Generate all system proposals and report"""
    print("=" * 80)
    print("DOD NEW SYSTEM PROPOSAL CAD")
    print("INTEGRATED WEAPONS AND INFORMATIONAL LINKS")
    print("=" * 80)
    print()
    print("Core Philosophy:")
    print("  'No sensor fights alone. No shooter waits for data. No node is indispensable.'")
    print()

    cad = IntegratedSystemCAD()

    # Generate all proposals
    proposals = [
        ("VANGUARD", create_vanguard_proposal),
        ("LOCUST", create_locust_swarm_proposal),
        ("ODIN", create_odin_fusion_proposal)
    ]

    for name, create_func in proposals:
        print(f"\nGenerating {name} proposal...")
        proposal = create_func()
        print(cad.generate_report(proposal))
        print()

    # Summary comparison
    print("\n" + "=" * 80)
    print("PROPOSAL COMPARISON SUMMARY")
    print("=" * 80)
    print()
    print(f"{'System':<20} {'Tier':<15} {'TRL':<8} {'Resilience':<12} {'Pk@200km':<10} {'Cost':<10}")
    print("-" * 80)

    for name, create_func in proposals:
        p = create_func()
        print(f"{p.codename:<20} {p.production_tier.value:<15} TRL-{p.trl.value:<5} "
              f"{p.network_resilience.overall_score:<12.1f} {p.pk_at_200km:<10.2f} "
              f"${p.cost_estimate.total_program_cost_billion:.1f}B")

    print()
    print("=" * 80)
    print("Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY")
    print("=" * 80)


if __name__ == "__main__":
    main()
