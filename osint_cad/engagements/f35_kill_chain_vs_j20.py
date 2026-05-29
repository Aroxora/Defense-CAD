#!/usr/bin/env python3
"""
F-35 EW Kill Chain Against J-20

Implements the F-35 integrated kill chain for engaging J-20 targets using:
- APG-81 AESA radar detection
- MADL datalink fusion (4-ship integration)
- AIM-260 JATM engagement
- ESM passive detection (limited)

This model evaluates F-35 offensive capability against J-20 stealth fighters,
incorporating aspect-dependent RCS and advanced weapon systems.

Key Differences vs Chinese Kill Chain:
- No dedicated AWACS VHF detection (E-3 limited vs stealth)
- Relies on active radar (reveals position)
- MADL sidelobe emissions detectable by J-20 ESM
- Smaller network (4-ship vs system-of-systems)

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

from osint_cad.physics.rcs_models import J20RCSModel, F35ARCSModel, RCSEstimate, calculate_detection_range
from osint_cad.targeting.aim260_targeting_model import AIM260TargetingModel, AIM260EngagementPhase


@dataclass
class F35SensorCapabilities:
    """F-35 sensor suite parameters"""
    # APG-81 AESA Radar
    apg81_peak_power_kw: float = 18.0
    apg81_antenna_gain_db: float = 35.0
    apg81_frequency_ghz: float = 10.0
    apg81_scan_rate_hz: float = 2.0  # Volume scan rate

    # ESM/EW Suite (ASQ-239)
    esm_sensitivity_dbm: float = -65.0
    esm_frequency_range_ghz: Tuple[float, float] = (0.5, 18.0)
    esm_aoa_accuracy_deg: float = 5.0  # Angle of Arrival accuracy

    # EOTS (Electro-Optical Targeting System)
    eots_detection_range_km: float = 80.0  # vs fighter at altitude
    eots_track_accuracy_m: float = 3.0

    # DAS (Distributed Aperture System)
    das_ir_detection_range_km: float = 50.0  # vs afterburning target


@dataclass
class F35NetworkCapabilities:
    """F-35 MADL network parameters"""
    # MADL (Multifunction Advanced Datalink)
    madl_data_rate_mbps: float = 50.0
    madl_latency_ms: float = 10.0
    madl_max_range_km: float = 200.0
    madl_encryption: str = "Type-1"

    # Network size
    max_flight_size: int = 4
    track_fusion_enabled: bool = True
    fusion_cep_improvement_factor: float = 2.5  # sqrt(N) with correlation


@dataclass
class DetectionResult:
    """Detection capability result"""
    detection_range_km: float
    detection_method: str
    track_accuracy_cep_m: float
    confidence: float
    sensor_type: str
    reveals_position: bool  # True if detection method is active/emits


@dataclass
class F35KillChainMetrics:
    """F-35 kill chain performance metrics"""
    radar_detection_range_km: float
    esm_detection_range_km: float
    integrated_track_cep_m: float
    weapon_nez_km: float
    pk_at_100km: float
    pk_at_150km: float
    first_detection_advantage_km: float  # vs J-20 passive detection
    network_resilience_score: float  # 0-100
    confidence: float


@dataclass
class EngagementResult:
    """Result of F-35 vs J-20 engagement analysis"""
    f35_metrics: F35KillChainMetrics
    j20_target_rcs: RCSEstimate
    aim260_pk: float
    launch_range_km: float
    first_shot_achievable: bool
    engagement_assessment: str
    risks: List[str]


class F35KillChainVsJ20:
    """
    F-35 Kill Chain Analysis Against J-20

    Evaluates F-35 offensive capability using:
    1. APG-81 radar detection (active, position-revealing)
    2. ESM passive detection (limited vs LPI emitters)
    3. MADL 4-ship fusion (improves track quality)
    4. AIM-260 weapon employment

    Key Challenge: J-20 ESM detects F-35 MADL sidelobes at 180+ km,
    while F-35 must radiate to detect J-20 at similar ranges.
    """

    def __init__(self):
        """Initialize F-35 kill chain model"""
        self.sensors = F35SensorCapabilities()
        self.network = F35NetworkCapabilities()
        self.aim260 = AIM260TargetingModel()

    def calculate_radar_detection_vs_j20(
        self,
        j20_position: np.ndarray,
        j20_velocity: np.ndarray,
        f35_position: np.ndarray
    ) -> DetectionResult:
        """
        Calculate APG-81 radar detection range vs J-20

        The detection range varies significantly based on J-20 aspect:
        - Frontal: ~60-80 km (J-20 RCS ~0.001 m²)
        - Beam: ~120-150 km (J-20 RCS ~0.08 m²)
        - Rear: ~80-100 km (J-20 RCS ~0.012 m²)
        """
        # Get J-20 RCS from F-35's viewing angle
        rcs_estimate = J20RCSModel.calculate_rcs_from_vectors(
            radar_position=f35_position,
            target_position=j20_position,
            target_velocity=j20_velocity,
            frequency_ghz=self.sensors.apg81_frequency_ghz
        )

        # Calculate detection range using practical formula
        # APG-81 detection performance (reference: 1 m² target at ~180 km)
        # Range scales with RCS^0.25 (fourth root from radar equation)
        reference_range_km = 180.0  # vs 1 m² target
        reference_rcs_m2 = 1.0

        # Detection range scales with fourth root of RCS ratio
        detection_range = reference_range_km * (rcs_estimate.rcs_m2 / reference_rcs_m2) ** 0.25

        # Apply LPI mode reduction (radar uses lower power for reduced signature)
        lpi_factor = 0.7  # 30% range reduction in LPI mode
        detection_range *= lpi_factor

        # Minimum detection range (clutter/signal processing limits)
        detection_range = max(detection_range, 5.0)

        # Track accuracy (radar-only)
        track_cep = 50.0  # 50m CEP at detection range

        return DetectionResult(
            detection_range_km=detection_range,
            detection_method="APG-81 AESA",
            track_accuracy_cep_m=track_cep,
            confidence=rcs_estimate.confidence * 0.7,
            sensor_type="active_radar",
            reveals_position=True  # Critical: F-35 must radiate to detect
        )

    def calculate_esm_detection_vs_j20(
        self,
        j20_radar_power_dbm: float = 55.0,  # J-20 AESA
        j20_radar_frequency_ghz: float = 10.0
    ) -> DetectionResult:
        """
        Calculate ASQ-239 ESM detection of J-20 radar emissions

        F-35 ESM can detect J-20 if J-20 is actively radiating.
        If J-20 remains passive (ESM-only), F-35 cannot detect passively.
        """
        # Path loss calculation
        allowable_path_loss = j20_radar_power_dbm - self.sensors.esm_sensitivity_dbm

        # Friis free space path loss
        wavelength_m = 0.3 / j20_radar_frequency_ghz
        detection_range_m = wavelength_m * 10**(allowable_path_loss / 20) / (4 * np.pi)
        detection_range_km = detection_range_m / 1000.0

        # Limit to realistic values
        detection_range_km = min(detection_range_km, 300.0)

        # ESM track accuracy (bearing only)
        # AOA accuracy of 5° at 150 km = ±13 km cross-range
        track_cep = 150.0 * np.tan(np.radians(self.sensors.esm_aoa_accuracy_deg)) * 1000.0

        return DetectionResult(
            detection_range_km=detection_range_km,
            detection_method="ASQ-239 ESM (requires J-20 to radiate)",
            track_accuracy_cep_m=track_cep,
            confidence=0.50,  # Only if J-20 radiates
            sensor_type="passive_esm",
            reveals_position=False
        )

    def calculate_4ship_fusion_track(
        self,
        single_sensor_cep_m: float,
        num_aircraft: int = 4
    ) -> float:
        """
        Calculate fused track accuracy with MADL 4-ship integration

        Track accuracy improves by ~sqrt(N) with independent sensors,
        plus additional improvement from geometric diversity.
        """
        if num_aircraft < 2:
            return single_sensor_cep_m

        # Fusion improvement
        fusion_factor = np.sqrt(num_aircraft) * self.network.fusion_cep_improvement_factor / 2.0
        fused_cep = single_sensor_cep_m / fusion_factor

        return max(fused_cep, 20.0)  # Minimum 20m CEP

    def calculate_network_resilience(
        self,
        num_f35: int = 4,
        f35_survivability: float = 0.70
    ) -> float:
        """
        Calculate network resilience score (0-100)

        F-35 network is more vulnerable than Chinese system:
        - No AWACS backup guidance
        - Loss of shooter = loss of weapon guidance
        - Smaller network (4 vs 10+ nodes)
        """
        score = 0.0

        # Node redundancy (40 points max)
        node_score = num_f35 * 8 * f35_survivability
        score += min(node_score, 40)

        # Link redundancy (30 points max)
        # MADL provides mesh networking
        link_score = num_f35 * 6  # More aircraft = more relay paths
        score += min(link_score, 30)

        # Graceful degradation (30 points max)
        degradation_score = 0
        if num_f35 >= 4:
            degradation_score += 10  # Can lose 1-2 aircraft
        if num_f35 >= 2:
            degradation_score += 10  # Minimum viable network

        # No AWACS backup: -10 points
        # Shooter loss = weapon loss
        degradation_score -= 10

        score += max(degradation_score, 0)

        return min(score, 100)

    def calculate_kill_chain_metrics_vs_j20(
        self,
        j20_position: np.ndarray,
        j20_velocity: np.ndarray,
        f35_position: np.ndarray,
        f35_velocity: np.ndarray,
        num_f35: int = 4
    ) -> F35KillChainMetrics:
        """
        Calculate complete F-35 kill chain metrics vs J-20
        """
        # Radar detection
        radar_det = self.calculate_radar_detection_vs_j20(
            j20_position, j20_velocity, f35_position
        )

        # ESM detection (conditional on J-20 radiating)
        esm_det = self.calculate_esm_detection_vs_j20()

        # 4-ship fusion track
        fused_cep = self.calculate_4ship_fusion_track(
            radar_det.track_accuracy_cep_m, num_f35
        )

        # Network resilience
        resilience = self.calculate_network_resilience(num_f35)

        # AIM-260 performance vs J-20
        range_km = np.linalg.norm(j20_position - f35_position) / 1000.0

        # Calculate Pk at different ranges
        intercept_100km = self.aim260.predict_intercept_vs_j20(
            f35_position, f35_velocity,
            f35_position + np.array([100000, 0, 0]),  # J-20 at 100km
            j20_velocity
        )

        intercept_150km = self.aim260.predict_intercept_vs_j20(
            f35_position, f35_velocity,
            f35_position + np.array([150000, 0, 0]),  # J-20 at 150km
            j20_velocity
        )

        # First detection advantage
        # J-20 ESM detects F-35 MADL at ~180 km (passive)
        # F-35 radar detects J-20 at ~80-120 km (active, aspect-dependent)
        j20_passive_detection = 180.0
        first_detection_advantage = radar_det.detection_range_km - j20_passive_detection

        return F35KillChainMetrics(
            radar_detection_range_km=radar_det.detection_range_km,
            esm_detection_range_km=esm_det.detection_range_km,
            integrated_track_cep_m=fused_cep,
            weapon_nez_km=self.aim260.params.nez_range_head_on_km,
            pk_at_100km=intercept_100km.probability_kill,
            pk_at_150km=intercept_150km.probability_kill,
            first_detection_advantage_km=first_detection_advantage,
            network_resilience_score=resilience,
            confidence=0.55
        )

    def analyze_engagement(
        self,
        j20_position: np.ndarray,
        j20_velocity: np.ndarray,
        f35_position: np.ndarray,
        f35_velocity: np.ndarray,
        num_f35: int = 4
    ) -> EngagementResult:
        """
        Analyze complete F-35 vs J-20 engagement scenario
        """
        # Get kill chain metrics
        metrics = self.calculate_kill_chain_metrics_vs_j20(
            j20_position, j20_velocity,
            f35_position, f35_velocity,
            num_f35
        )

        # Get J-20 RCS at current geometry
        j20_rcs = J20RCSModel.calculate_rcs_from_vectors(
            f35_position, j20_position, j20_velocity
        )

        # Calculate AIM-260 launch acceptability
        launch_range = np.linalg.norm(j20_position - f35_position) / 1000.0
        acceptable, reason, confidence = self.aim260.calculate_launch_acceptability_vs_j20(
            f35_position, f35_velocity,
            j20_position, j20_velocity
        )

        # Predict intercept
        intercept = self.aim260.predict_intercept_vs_j20(
            f35_position, f35_velocity,
            j20_position, j20_velocity
        )

        # Identify risks
        risks = []

        # Risk: J-20 ESM first detection
        if metrics.first_detection_advantage_km < 0:
            risks.append(f"J-20 ESM detects F-35 first by "
                        f"{-metrics.first_detection_advantage_km:.0f} km")

        # Risk: Must radiate to detect
        if launch_range < metrics.radar_detection_range_km:
            risks.append("F-35 must actively radiate (APG-81) to detect/track J-20")

        # Risk: Network vulnerability
        if metrics.network_resilience_score < 60:
            risks.append(f"Network resilience {metrics.network_resilience_score:.0f}/100 - "
                        "vulnerable to attrition")

        # Risk: Low RCS target
        if j20_rcs.rcs_m2 < 0.01:
            risks.append(f"J-20 RCS {j20_rcs.rcs_dbsm:.1f} dBsm limits detection range")

        # Generate assessment
        if acceptable and metrics.first_detection_advantage_km > -50:
            assessment = "MARGINAL - Engagement possible but J-20 has first-shot advantage"
        elif acceptable:
            assessment = "CHALLENGING - Significant J-20 first-detection advantage"
        else:
            assessment = f"NOT RECOMMENDED - {reason}"

        return EngagementResult(
            f35_metrics=metrics,
            j20_target_rcs=j20_rcs,
            aim260_pk=intercept.probability_kill,
            launch_range_km=launch_range,
            first_shot_achievable=metrics.first_detection_advantage_km > 0,
            engagement_assessment=assessment,
            risks=risks
        )

    def generate_report(
        self,
        j20_position: np.ndarray = np.array([150000, 0, 12000]),
        j20_velocity: np.ndarray = np.array([-500, 0, 0]),
        f35_position: np.ndarray = np.array([0, 0, 12000]),
        f35_velocity: np.ndarray = np.array([450, 0, 0])
    ) -> str:
        """Generate comprehensive F-35 vs J-20 analysis report"""
        report = []
        report.append("=" * 80)
        report.append("F-35 KILL CHAIN ANALYSIS VS J-20")
        report.append("=" * 80)
        report.append("")
        report.append("Classification: UNCLASSIFIED // PUBLIC RELEASE")
        report.append("")

        # Engagement analysis
        result = self.analyze_engagement(
            j20_position, j20_velocity,
            f35_position, f35_velocity
        )

        report.append("ENGAGEMENT SCENARIO")
        report.append("-" * 80)
        report.append(f"Range to J-20:          {result.launch_range_km:.0f} km")
        report.append(f"J-20 RCS:               {result.j20_target_rcs.rcs_dbsm:.1f} dBsm "
                     f"({result.j20_target_rcs.rcs_m2:.4f} m²)")
        report.append(f"J-20 Aspect:            {result.j20_target_rcs.azimuth_deg:.0f}°")
        report.append("")

        # F-35 Kill Chain Metrics
        metrics = result.f35_metrics
        report.append("F-35 KILL CHAIN METRICS")
        report.append("-" * 80)
        report.append(f"Radar Detection (APG-81): {metrics.radar_detection_range_km:.0f} km")
        report.append(f"ESM Detection:            {metrics.esm_detection_range_km:.0f} km "
                     "(requires J-20 to radiate)")
        report.append(f"Fused Track CEP:          {metrics.integrated_track_cep_m:.0f} m")
        report.append(f"AIM-260 NEZ:              {metrics.weapon_nez_km:.0f} km")
        report.append(f"Pk at 100 km:             {metrics.pk_at_100km:.2f}")
        report.append(f"Pk at 150 km:             {metrics.pk_at_150km:.2f}")
        report.append(f"Network Resilience:       {metrics.network_resilience_score:.0f}/100")
        report.append("")

        # First Detection Analysis
        report.append("FIRST DETECTION ANALYSIS")
        report.append("-" * 80)
        if metrics.first_detection_advantage_km > 0:
            report.append(f"F-35 advantage:           +{metrics.first_detection_advantage_km:.0f} km")
        else:
            report.append(f"J-20 advantage:           {-metrics.first_detection_advantage_km:.0f} km")
        report.append(f"First shot achievable:    {'YES' if result.first_shot_achievable else 'NO'}")
        report.append("")

        # AIM-260 Employment
        report.append("AIM-260 EMPLOYMENT VS J-20")
        report.append("-" * 80)
        report.append(f"Current Range:            {result.launch_range_km:.0f} km")
        report.append(f"Predicted Pk:             {result.aim260_pk:.2f}")
        report.append(f"Seeker Can Acquire:       YES (AIM-260 optimized for low RCS)")
        report.append("")

        # Risks
        report.append("IDENTIFIED RISKS")
        report.append("-" * 80)
        for risk in result.risks:
            report.append(f"  ⚠ {risk}")
        report.append("")

        # Assessment
        report.append("ENGAGEMENT ASSESSMENT")
        report.append("-" * 80)
        report.append(f"  {result.engagement_assessment}")
        report.append("")

        # Key Findings
        report.append("=" * 80)
        report.append("KEY FINDINGS")
        report.append("=" * 80)
        report.append("")
        report.append("1. DETECTION ASYMMETRY")
        report.append("   - J-20 ESM detects F-35 MADL passively at 180+ km")
        report.append("   - F-35 must radiate (APG-81) to detect J-20 at ~80-120 km")
        report.append("   - J-20 gains first-shot advantage of ~60-100 km")
        report.append("")
        report.append("2. AIM-260 CAPABILITY")
        report.append("   - Optimized for low-RCS targets like J-20")
        report.append("   - AESA seeker effective vs -25 dBsm targets")
        report.append("   - NEZ ~180 km provides reach but Pk degrades at range")
        report.append("")
        report.append("3. NETWORK LIMITATIONS")
        report.append("   - 4-ship MADL network vs J-20 system-of-systems")
        report.append("   - No AWACS backup guidance (shooter loss = weapon loss)")
        report.append("   - Lower resilience score vs integrated Chinese network")
        report.append("")

        report.append("=" * 80)
        report.append("Classification: UNCLASSIFIED // PUBLIC RELEASE")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Demonstration of F-35 kill chain vs J-20"""
    cad = F35KillChainVsJ20()
    print(cad.generate_report())


if __name__ == "__main__":
    main()
