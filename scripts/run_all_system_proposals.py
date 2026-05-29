#!/usr/bin/env python3
"""
Comprehensive DOD System Proposal Generator
============================================

Runs all system proposals through the CAD framework and generates complete
analysis reports following the INTEGRATED WEAPONS AND INFORMATIONAL LINK
philosophy.

GENERATES:
1. VANGUARD - Integrated Airborne-Ground Strike Network
2. LOCUST - Scramjet Swarm Missile System
3. ODIN - AI Fusion Engine
4. PANDORA - Containerized Strike System
5. SENTINEL - Distributed Sensor Network
6. AEGIS ANYWHERE - Mobile Naval Air Defense

Usage:
    python run_all_system_proposals.py

Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY
Date: 2026-01-02
"""

import sys
from datetime import datetime
from typing import List

from osint_cad.platforms.dod_system_proposal_cad import (
    IntegratedSystemCAD,
    SystemProposal,
    NetworkNode,
    DataLinkSpec,
    SensorSpec,
    WeaponSpec,
    SystemDomain,
    SystemRole,
    TechnologyReadinessLevel,
    # Legacy systems
    create_vanguard_proposal,
    create_locust_swarm_proposal,
    create_odin_fusion_proposal,
    # A2/AD-optimized systems
    create_trident_conventional_proposal,
    create_rapid_dragon_proposal,
    create_typhon_island_chain_proposal,
    create_b21_lrso_proposal,
    # Threat models
    THREAT_PRC_PACIFIC,
    THREAT_PRC_TAIWAN,
    ThreatEnvelope
)


def create_pandora_proposal() -> SystemProposal:
    """
    Create PANDORA Containerized Strike System proposal.

    Cruise missiles concealed in standard ISO shipping containers for
    covert global pre-positioning.
    """
    cad = IntegratedSystemCAD()

    datalinks = [
        DataLinkSpec(
            name="Iridium SATCOM",
            frequency_band="L-band",
            bandwidth_mbps=0.128,
            range_km=20000,  # Global
            latency_ms=500,
            jam_resistance_db=15,
            encryption="NSA Type 1",
            redundancy_level=2
        ),
        DataLinkSpec(
            name="HF NVIS",
            frequency_band="HF",
            bandwidth_mbps=0.01,
            range_km=500,  # NVIS range
            latency_ms=1000,
            jam_resistance_db=10,
            encryption="AES-256",
            redundancy_level=1
        )
    ]

    nodes = [
        NetworkNode(
            name="PANDORA Container Unit",
            domain=SystemDomain.GROUND,
            role=SystemRole.SHOOTER,
            survivability=0.90,  # Hidden in plain sight
            sensors=[
                SensorSpec(
                    name="GPS Receiver",
                    sensor_type="gnss",
                    detection_range_km=0,
                    track_accuracy_cep_m=5,
                    update_rate_hz=1.0,
                    passive=True,
                    jam_resistance_db=15
                )
            ],
            weapons=[
                WeaponSpec(
                    name="Tomahawk Block V",
                    weapon_type="cruise",
                    range_km=1600,
                    nez_km=1600,
                    speed_mach=0.75,
                    guidance_modes=["gps", "tercom", "dsmac", "datalink"],
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
            name="Global Strike Command",
            domain=SystemDomain.GROUND,
            role=SystemRole.C2,
            survivability=0.99,
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=False,
            can_guide_weapons=True  # Can retarget in flight
        )
    ]

    # NOTE: PANDORA raises significant legal/treaty concerns:
    # - INF Treaty (now defunct) prohibited ground-launched cruise missiles 500-5500km
    # - Concealment in civilian containers undermines arms control verification
    # - Creates risk of civilian shipping being targeted as potential threats
    # - May violate laws of armed conflict re: perfidy (disguising weapons as civilian)
    # These concerns would need resolution before operational deployment.

    return cad.generate_proposal(
        name="PANDORA Containerized Strike System",
        codename="PANDORA",
        description="Cruise missiles in ISO containers for covert pre-positioning. WARNING: Raises treaty verification, LOAC, and civilian targeting concerns that require legal review before deployment.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_7,
        ioc_year=2029,  # Realistic: legal review + development
        foc_year=2032,
        development_complexity=0.8,
        production_rate=100,  # Reduced - not mass production
        production_years=5,
        mission_type="strike",
        is_munition_program=True,
        munition_unit_cost_million=2.0,  # Tomahawk cost
        launcher_count=200  # Container launchers
    )


def create_sentinel_proposal() -> SystemProposal:
    """
    Create SENTINEL Distributed Sensor Network proposal.

    Proliferated ground-based passive sensors for wide-area surveillance.
    """
    cad = IntegratedSystemCAD()

    datalinks = [
        DataLinkSpec(
            name="SENTINEL Mesh",
            frequency_band="VHF",
            bandwidth_mbps=1.0,
            range_km=200,
            latency_ms=100,
            jam_resistance_db=20,
            encryption="AES-256",
            redundancy_level=10
        ),
        DataLinkSpec(
            name="Starshield Uplink",
            frequency_band="Ka-band",
            bandwidth_mbps=100.0,
            range_km=2000,
            latency_ms=50,
            jam_resistance_db=25,
            encryption="NSA Type 1",
            redundancy_level=5
        )
    ]

    nodes = [
        NetworkNode(
            name="SENTINEL Passive RF Node",
            domain=SystemDomain.GROUND,
            role=SystemRole.SENSOR,
            survivability=0.80,
            sensors=[
                SensorSpec(
                    name="Wideband ESM Receiver",
                    sensor_type="esm",
                    detection_range_km=400,
                    track_accuracy_cep_m=1000,  # Single node
                    update_rate_hz=10.0,
                    passive=True,
                    jam_resistance_db=35  # Passive = hard to jam
                )
            ],
            weapons=[],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="SENTINEL Acoustic Node",
            domain=SystemDomain.GROUND,
            role=SystemRole.SENSOR,
            survivability=0.85,
            sensors=[
                SensorSpec(
                    name="Infrasound Array",
                    sensor_type="acoustic",
                    detection_range_km=200,
                    track_accuracy_cep_m=5000,
                    update_rate_hz=1.0,
                    passive=True,
                    jam_resistance_db=50  # Cannot be jammed via RF
                )
            ],
            weapons=[],
            datalinks=[datalinks[0]],
            can_relay=True,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="SENTINEL Fusion Hub",
            domain=SystemDomain.GROUND,
            role=SystemRole.FUSION,
            survivability=0.90,
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0], datalinks[1]],
            can_relay=True,
            can_fuse_tracks=True,  # TDOA/FDOA geolocation
            can_guide_weapons=False
        )
    ]

    # SENTINEL cost model:
    # - Each sensor node is ~$1-2M (commercial-grade ESM/acoustic)
    # - 500 nodes total across 5 years = 100/year
    # - Fusion hubs are $10M each, need ~20
    # - Development is moderate (TRL 5 needs maturation)
    # Total should be ~$3-5B, not $58B

    return cad.generate_proposal(
        name="SENTINEL Distributed Passive Sensor Network",
        codename="SENTINEL",
        description="Proliferated ground-based passive RF and acoustic sensors. TDOA/FDOA fusion achieves 50m CEP. Covert, jam-resistant cueing for integrated kill chain.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_5,  # Realistic: TDOA fusion at scale is TRL 5
        ioc_year=2030,  # Realistic: 4-5 years from TRL 5
        foc_year=2033,
        development_complexity=0.8,  # Passive sensors are mature tech
        production_rate=100,  # Sensor nodes per year (reduced)
        production_years=5,
        mission_type="sensor_only",  # No direct weapons
        # Use munition-style costing for mass-produced low-cost sensors
        is_munition_program=True,
        munition_unit_cost_million=1.5,  # ~$1.5M per sensor node
        launcher_count=20  # Fusion hubs at ~$10M each
    )


def create_aegis_anywhere_proposal() -> SystemProposal:
    """
    Create AEGIS ANYWHERE mobile naval air defense proposal.

    Distributed AEGIS capability on mobile ground launchers.
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
            name="Link 16",
            frequency_band="UHF",
            bandwidth_mbps=0.115,
            range_km=300,
            latency_ms=200,
            jam_resistance_db=15,
            encryption="NSA Type 1",
            redundancy_level=1
        ),
        DataLinkSpec(
            name="TTNT",
            frequency_band="UHF",
            bandwidth_mbps=10.0,
            range_km=300,
            latency_ms=10,
            jam_resistance_db=25,
            encryption="NSA Type 1",
            redundancy_level=4
        )
    ]

    nodes = [
        NetworkNode(
            name="Mobile SPY-6 Radar",
            domain=SystemDomain.GROUND,
            role=SystemRole.SENSOR,
            survivability=0.80,
            sensors=[
                SensorSpec(
                    name="SPY-6(V)2 AMDR",
                    sensor_type="radar",
                    detection_range_km=500,
                    track_accuracy_cep_m=30,
                    update_rate_hz=5.0,
                    passive=False,
                    jam_resistance_db=28
                )
            ],
            weapons=[],
            datalinks=[datalinks[0], datalinks[2]],
            can_relay=False,
            can_fuse_tracks=True,
            can_guide_weapons=True  # Fire control quality
        ),
        NetworkNode(
            name="Typhon SM-6 Launcher",
            domain=SystemDomain.GROUND,
            role=SystemRole.SHOOTER,
            survivability=0.85,
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
            name="AEGIS Engagement Center",
            domain=SystemDomain.GROUND,
            role=SystemRole.C2,
            survivability=0.90,
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0], datalinks[1], datalinks[2]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True
        ),
        NetworkNode(
            name="E-7 AWACS Support",
            domain=SystemDomain.AIR,
            role=SystemRole.C2,
            survivability=0.85,
            sensors=[
                SensorSpec(
                    name="MESA AESA",
                    sensor_type="radar",
                    detection_range_km=400,
                    track_accuracy_cep_m=100,
                    update_rate_hz=1.0,
                    passive=False,
                    jam_resistance_db=25
                )
            ],
            weapons=[],
            datalinks=[datalinks[0], datalinks[1], datalinks[2]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True  # Can guide SM-6 via CEC
        )
    ]

    return cad.generate_proposal(
        name="AEGIS ANYWHERE Mobile Naval Air Defense",
        codename="AEGIS_ANYWHERE",
        description="Distributed AEGIS capability with mobile SPY-6 radars, Typhon launchers, and E-7 AWACS integration. Full CEC engage-on-remote with shoot-and-scoot survivability.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_7,
        ioc_year=2027,
        foc_year=2029,
        development_complexity=1.3,
        production_rate=30,
        production_years=5
    )


def create_hyperion_hypersonic_proposal() -> SystemProposal:
    """
    Create HYPERION Ground-Launched Hypersonic Strike proposal.

    Long-range hypersonic glide vehicles with network-enabled targeting.
    """
    cad = IntegratedSystemCAD()

    datalinks = [
        DataLinkSpec(
            name="Hypersonic Datalink",
            frequency_band="Ka-band",
            bandwidth_mbps=10.0,
            range_km=2000,
            latency_ms=100,
            jam_resistance_db=20,
            encryption="NSA Type 1",
            redundancy_level=2
        ),
        DataLinkSpec(
            name="SDA Relay",
            frequency_band="Ka-band",
            bandwidth_mbps=50.0,
            range_km=5000,
            latency_ms=200,
            jam_resistance_db=25,
            encryption="NSA Type 1",
            redundancy_level=5
        )
    ]

    nodes = [
        NetworkNode(
            name="HYPERION TEL",
            domain=SystemDomain.GROUND,
            role=SystemRole.SHOOTER,
            survivability=0.85,
            sensors=[],
            weapons=[
                WeaponSpec(
                    name="LRHW Common HGV",
                    weapon_type="hypersonic",
                    range_km=2775,
                    nez_km=2775,
                    speed_mach=17.0,
                    guidance_modes=["inertial", "gps", "terminal_radar"],
                    datalink_capable=True,
                    unit_cost_million=40.0
                )
            ],
            datalinks=[datalinks[0]],
            can_relay=False,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="SDA Tracking Layer",
            domain=SystemDomain.SPACE,
            role=SystemRole.SENSOR,
            survivability=0.95,
            sensors=[
                SensorSpec(
                    name="OPIR Sensor",
                    sensor_type="ir",
                    detection_range_km=15000,
                    track_accuracy_cep_m=1000,
                    update_rate_hz=1.0,
                    passive=True,
                    jam_resistance_db=30
                )
            ],
            weapons=[],
            datalinks=[datalinks[1]],
            can_relay=True,
            can_fuse_tracks=False,
            can_guide_weapons=False
        ),
        NetworkNode(
            name="Targeting Fusion Center",
            domain=SystemDomain.GROUND,
            role=SystemRole.FUSION,
            survivability=0.95,
            sensors=[],
            weapons=[],
            datalinks=[datalinks[0], datalinks[1]],
            can_relay=True,
            can_fuse_tracks=True,
            can_guide_weapons=True  # Mid-course updates to HGV
        )
    ]

    return cad.generate_proposal(
        name="HYPERION Ground-Launched Hypersonic Strike",
        codename="HYPERION",
        description="Long-range (2775 km) hypersonic glide vehicles with mid-course updates via SDA satellite relay. Mach 17 terminal speed provides high penetration probability against current defenses.",
        nodes=nodes,
        datalinks=datalinks,
        trl=TechnologyReadinessLevel.TRL_6,  # LRHW is TRL 6-7
        ioc_year=2028,  # Army LRHW IOC target
        foc_year=2031,
        development_complexity=1.5,
        production_rate=50,  # Realistic for expensive hypersonics
        production_years=5,
        mission_type="strike",  # Strike weapon, not air defense
        is_munition_program=True,
        munition_unit_cost_million=40.0,  # Per HGV
        launcher_count=48  # 4 batteries of 12 TELs
    )


def generate_all_proposals() -> List[SystemProposal]:
    """Generate all system proposals"""
    proposals = []

    print("Generating system proposals...")
    print()

    # ==========================================================================
    # A2/AD COUNTER SYSTEMS (PRIORITY)
    # These are specifically designed to defeat A2/AD strategies
    # ==========================================================================
    print("=" * 60)
    print("A2/AD COUNTER SYSTEMS (PRIORITY)")
    print("=" * 60)
    print()

    print("  - TRIDENT_CONV: Submarine-Launched Strike...")
    proposals.append(create_trident_conventional_proposal())

    print("  - RAPID_DRAGON: Palletized Standoff Strike...")
    proposals.append(create_rapid_dragon_proposal())

    print("  - TYPHON_IC: Island Chain Distributed Strike...")
    proposals.append(create_typhon_island_chain_proposal())

    print("  - B21_LRSO: Stealth Bomber Standoff Strike...")
    proposals.append(create_b21_lrso_proposal())

    # ==========================================================================
    # LEGACY SYSTEMS (for comparison)
    # ==========================================================================
    print()
    print("=" * 60)
    print("LEGACY/INTEGRATION SYSTEMS")
    print("=" * 60)
    print()

    print("  - VANGUARD: Integrated Airborne-Ground Strike...")
    proposals.append(create_vanguard_proposal())

    print("  - PANDORA: Containerized Strike System...")
    proposals.append(create_pandora_proposal())

    print("  - AEGIS_ANYWHERE: Mobile Naval Air Defense...")
    proposals.append(create_aegis_anywhere_proposal())

    print("  - HYPERION: Ground-Launched Hypersonic...")
    proposals.append(create_hyperion_hypersonic_proposal())

    print("  - LOCUST: Scramjet Swarm Missiles...")
    proposals.append(create_locust_swarm_proposal())

    print("  - SENTINEL: Distributed Sensor Network...")
    proposals.append(create_sentinel_proposal())

    print("  - ODIN: AI Fusion Engine...")
    proposals.append(create_odin_fusion_proposal())

    print()
    print(f"Generated {len(proposals)} system proposals.")

    return proposals


def generate_executive_summary(proposals: List[SystemProposal]) -> str:
    """Generate executive summary of all proposals"""
    lines = []
    lines.append("=" * 80)
    lines.append("EXECUTIVE SUMMARY: DOD NEW SYSTEM PROPOSALS")
    lines.append("INTEGRATED WEAPONS AND INFORMATIONAL LINKS")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY")
    lines.append("")
    lines.append("CORE PHILOSOPHY:")
    lines.append("  'No sensor fights alone. No shooter waits for data. No node is indispensable.'")
    lines.append("")
    lines.append("-" * 80)

    # Summary table
    lines.append("")
    lines.append(f"{'System':<18} {'Tier':<12} {'TRL':<6} {'Resil':<8} {'Pk200':<8} {'IOC':<6} {'Cost':<10}")
    lines.append("-" * 80)

    total_cost = 0
    for p in proposals:
        tier_short = p.production_tier.value.replace("tier_", "T").replace("_", "-").upper()[:10]
        lines.append(
            f"{p.codename:<18} {tier_short:<12} {p.trl.value:<6} "
            f"{p.network_resilience.overall_score:<8.1f} {p.pk_at_200km:<8.2f} "
            f"{p.ioc_year:<6} ${p.cost_estimate.total_program_cost_billion:.1f}B"
        )
        total_cost += p.cost_estimate.total_program_cost_billion

    lines.append("-" * 80)
    lines.append(f"{'TOTAL INVESTMENT':<66} ${total_cost:.1f}B")
    lines.append("")

    # Budget context
    lines.append("BUDGET CONTEXT (FY2025 Reference):")
    lines.append(f"  DOD Total Acquisition Budget: $311B/year")
    lines.append(f"  Portfolio Total (5-year): ${total_cost:.1f}B")
    avg_annual = total_cost / 5
    lines.append(f"  Portfolio Annual Average: ${avg_annual:.1f}B/year ({avg_annual/311*100:.1f}% of acquisition)")

    if avg_annual > 50:
        lines.append(f"  STATUS: *** EXCEEDS REALISTIC PORTFOLIO SIZE ***")
        lines.append(f"  (Recommend prioritizing 2-3 systems or extending timeline)")
    elif avg_annual > 30:
        lines.append(f"  STATUS: AGGRESSIVE but achievable with prioritization")
    else:
        lines.append(f"  STATUS: REASONABLE portfolio size")
    lines.append("")

    # Key capabilities
    lines.append("KEY CAPABILITY IMPROVEMENTS:")
    lines.append("")

    # Find best performers
    best_resilience = max(proposals, key=lambda p: p.network_resilience.overall_score)
    best_pk = max(proposals, key=lambda p: p.pk_at_200km)
    best_detection = max(proposals, key=lambda p: p.detection_range_km)
    lowest_cost = min(proposals, key=lambda p: p.cost_estimate.total_program_cost_billion)

    lines.append(f"  Highest Network Resilience:  {best_resilience.codename} ({best_resilience.network_resilience.overall_score:.1f}/100)")
    lines.append(f"  Highest Pk at 200km:         {best_pk.codename} ({best_pk.pk_at_200km:.2f})")
    lines.append(f"  Longest Detection Range:     {best_detection.codename} ({best_detection.detection_range_km:.0f} km)")
    lines.append(f"  Lowest Program Cost:         {lowest_cost.codename} (${lowest_cost.cost_estimate.total_program_cost_billion:.1f}B)")
    lines.append("")

    # AWACS backup capability
    awacs_backup_systems = [p for p in proposals if p.awacs_to_weapon_backup]
    lines.append(f"  Systems with AWACS-to-Weapon Backup: {len(awacs_backup_systems)}/{len(proposals)}")
    for p in awacs_backup_systems:
        lines.append(f"    - {p.codename}")
    lines.append("")

    # Passive detection capability
    passive_systems = [p for p in proposals if p.passive_detection_capable]
    lines.append(f"  Systems with Passive Detection: {len(passive_systems)}/{len(proposals)}")
    for p in passive_systems:
        lines.append(f"    - {p.codename}")
    lines.append("")

    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    """Main entry point"""
    print()
    print("=" * 80)
    print("DOD NEW SYSTEM PROPOSAL CAD FRAMEWORK")
    print("INTEGRATED WEAPONS AND INFORMATIONAL LINKS")
    print("=" * 80)
    print()

    cad = IntegratedSystemCAD()

    # Generate all proposals
    proposals = generate_all_proposals()

    # Print executive summary
    print()
    print(generate_executive_summary(proposals))

    # Print detailed reports
    print()
    print("=" * 80)
    print("DETAILED SYSTEM REPORTS")
    print("=" * 80)

    for proposal in proposals:
        print()
        print(cad.generate_report(proposal))

    # Strategic assessment
    # ==========================================================================
    # A2/AD STRATEGIC VIABILITY ASSESSMENT
    # ==========================================================================
    print()
    print("=" * 80)
    print("A2/AD STRATEGIC VIABILITY ASSESSMENT")
    print("Threat: PRC Western Pacific (DF-26 4000km, J-20 CAP 1500km)")
    print("=" * 80)

    threat = THREAT_PRC_PACIFIC
    print(f"\nSafe Standoff Range: {threat.get_safe_standoff_range():.0f} km")
    print(f"Required Strike Range: {threat.get_strike_range_required():.0f} km")
    print()

    # Assess each proposal
    a2ad_results = []
    for proposal in proposals:
        assessment = cad.assess_strategic_viability(proposal, threat)
        a2ad_results.append((proposal, assessment))

    # Summary table
    print(f"{'System':<15} {'Range':<10} {'Standoff':<12} {'CostExch':<12} {'Surviv':<10} {'VERDICT':<12}")
    print("-" * 80)

    for proposal, assessment in a2ad_results:
        standoff = "PASS" if assessment.can_strike_from_standoff else "FAIL"
        cost_ex = f"{assessment.cost_exchange.exchange_ratio:.1f}:1"
        surviv = f"{assessment.platform_survivability_vs_threat:.0%}"
        print(f"{proposal.codename:<15} {assessment.weapon_range_km:<10.0f} {standoff:<12} {cost_ex:<12} {surviv:<10} {assessment.strategic_viability:<12}")

    print()

    # Detailed recommendations for non-viable systems
    print("DETAILED VIABILITY ANALYSIS:")
    print("-" * 80)
    for proposal, assessment in a2ad_results:
        print(cad.generate_strategic_report(assessment))

    print()
    print("=" * 80)
    print("STRATEGIC ASSESSMENT SUMMARY")
    print("=" * 80)
    print()
    print("A2/AD COUNTER-STRATEGY:")
    print("   The carrier-centric force is VULNERABLE to A2/AD.")
    print("   Key systems that WORK against PRC A2/AD:")
    print()

    viable_systems = [p.codename for p, a in a2ad_results if a.strategic_viability == "VIABLE"]
    marginal_systems = [p.codename for p, a in a2ad_results if a.strategic_viability == "MARGINAL"]
    not_viable_systems = [p.codename for p, a in a2ad_results if a.strategic_viability == "NOT_VIABLE"]

    if viable_systems:
        print(f"   VIABLE: {', '.join(viable_systems)}")
    if marginal_systems:
        print(f"   MARGINAL: {', '.join(marginal_systems)}")
    if not_viable_systems:
        print(f"   NOT VIABLE: {', '.join(not_viable_systems)}")

    print()
    print("COST EXCHANGE WINNERS (>2:1 favorable):")
    winners = [(p.codename, a.cost_exchange.exchange_ratio)
               for p, a in a2ad_results if a.cost_exchange.exchange_ratio >= 2.0]
    for name, ratio in sorted(winners, key=lambda x: -x[1]):
        print(f"   - {name}: {ratio:.1f}:1")

    print()
    print("RECOMMENDATION:")
    print("   Prioritize A2/AD COUNTER systems (TRIDENT_CONV, RAPID_DRAGON, TYPHON_IC, B21_LRSO)")
    print("   These operate from STANDOFF and achieve FAVORABLE cost exchange.")
    print("   Legacy platforms (carriers, short-range aircraft) should be de-emphasized")
    print()
    print("=" * 80)
    print("Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
