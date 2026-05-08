#!/usr/bin/env python3
"""
F-35 Defensive Model Against PL-15

Implements F-35 defensive analysis against PL-15 BVR missile threats.

Defensive Capabilities Modeled:
- RCS management (aspect-dependent)
- ESM threat warning (ASQ-239)
- Electronic countermeasures (ECM)
- Kinematic defense (beaming, notching, cranking)
- Chaff/flare deployment
- Terrain masking

Key Challenge:
- PL-15 NEZ ~100 km head-on
- J-20 ESM detects F-35 MADL sidelobes at 180+ km
- F-35 may not know PL-15 is inbound until terminal phase

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

from rcs_models import F35ARCSModel, RCSEstimate
from pl15_targeting_model import PL15TargetingModel, TargetState, EngagementPhase


class DefensiveManeuver(Enum):
    """Defensive maneuver types"""
    NONE = "none"
    BEAM = "beam"  # Turn 90° to missile, exploit Doppler notch
    NOTCH = "notch"  # Fly perpendicular + descend into ground clutter
    CRANK = "crank"  # Turn away while maintaining radar contact
    DRAG = "drag"  # Turn cold, max range, defeat kinematically
    DIVE = "dive"  # Descend rapidly, increase air density (missile drag)
    CHAFF = "chaff"  # Deploy chaff corridor


class ThreatWarningStatus(Enum):
    """Threat warning status"""
    NO_WARNING = "no_warning"
    LAUNCH_DETECTION = "launch_detection"  # IR/UV launch flash
    RADAR_WARNING = "radar_warning"  # Active radar illumination
    MISSILE_TRACKING = "missile_tracking"  # Active missile seeker detected
    IMMINENT = "imminent"  # Missile terminal phase


@dataclass
class F35DefensiveCapabilities:
    """F-35 defensive system parameters"""

    # ASQ-239 EW Suite
    esm_sensitivity_dbm: float = -65.0
    esm_warning_range_km: float = 200.0  # Detect J-20 radar at range
    launch_warning_range_km: float = 100.0  # UV/IR launch detection

    # RWR (Radar Warning Receiver)
    rwr_response_time_s: float = 0.5
    rwr_aoa_accuracy_deg: float = 5.0

    # ECM/Jamming
    ecm_effective_range_km: float = 30.0  # Effective jamming range
    ecm_jammer_power_dbw: float = 20.0
    ecm_techniques: List[str] = None

    # Kinematic performance
    max_g_sustained: float = 9.0
    max_speed_mach: float = 1.6
    corner_speed_ktas: float = 450.0

    # Countermeasures
    chaff_bundles: int = 60
    chaff_rcs_m2: float = 100.0  # RCS of chaff cloud
    flare_count: int = 120

    # Stealth advantage
    rcs_model: type = F35ARCSModel

    def __post_init__(self):
        if self.ecm_techniques is None:
            self.ecm_techniques = [
                "range_gate_pull_off",
                "velocity_gate_pull_off",
                "cross_eye_jamming",
                "coherent_noise_jamming"
            ]


@dataclass
class ThreatAssessment:
    """Assessment of PL-15 threat to F-35"""
    warning_status: ThreatWarningStatus
    time_to_impact_s: float
    missile_range_km: float
    f35_rcs_m2: float
    pk_against_f35: float
    best_maneuver: DefensiveManeuver
    survival_probability: float
    confidence: float
    recommendations: List[str]


@dataclass
class DefenseEffectiveness:
    """Effectiveness of defensive measures"""
    maneuver: DefensiveManeuver
    pk_reduction: float  # How much Pk is reduced (0-1)
    new_pk: float
    survival_probability: float
    energy_cost: float  # Speed/altitude lost
    repositioning_time_s: float  # Time to resume offensive


class F35DefensiveModel:
    """
    F-35 Defensive Analysis Against PL-15

    Models F-35 survivability against PL-15 BVR missile attacks,
    incorporating stealth, EW, and kinematic defenses.

    Key Advantages:
    - Low RCS reduces PL-15 seeker acquisition range
    - Advanced EW suite (ASQ-239) provides early warning
    - High maneuverability for kinematic defense

    Key Vulnerabilities:
    - MADL sidelobes detectable at 180+ km (passive targeting)
    - PL-15 datalink updates until terminal phase
    - Network guidance allows launch before J-20 radar detection
    """

    def __init__(self):
        """Initialize F-35 defensive model"""
        self.capabilities = F35DefensiveCapabilities()
        self.pl15 = PL15TargetingModel()

    def calculate_f35_rcs_vs_pl15(
        self,
        pl15_position: np.ndarray,
        f35_position: np.ndarray,
        f35_velocity: np.ndarray
    ) -> RCSEstimate:
        """
        Calculate F-35 RCS from PL-15 seeker perspective

        F-35's aspect-dependent RCS significantly affects PL-15 terminal
        seeker acquisition and tracking.
        """
        return F35ARCSModel.calculate_rcs_from_vectors(
            radar_position=pl15_position,
            target_position=f35_position,
            target_velocity=f35_velocity,
            frequency_ghz=10.0  # X-band seeker
        )

    def assess_threat_warning(
        self,
        pl15_position: np.ndarray,
        pl15_velocity: np.ndarray,
        f35_position: np.ndarray,
        f35_velocity: np.ndarray,
        j20_radar_active: bool = True
    ) -> ThreatWarningStatus:
        """
        Determine F-35 threat warning status

        Warning depends on:
        - J-20 radar emissions (detected by ASQ-239)
        - PL-15 launch flash (UV/IR sensors)
        - PL-15 seeker activation (RWR)
        """
        missile_range = np.linalg.norm(pl15_position - f35_position) / 1000.0

        # Calculate time to impact
        rel_pos = f35_position - pl15_position
        rel_vel = f35_velocity - pl15_velocity
        closure_rate = -np.dot(rel_vel, rel_pos) / np.linalg.norm(rel_pos)

        if closure_rate > 0:
            time_to_impact = (missile_range * 1000) / closure_rate
        else:
            time_to_impact = np.inf

        # Determine warning status
        if missile_range < 20:  # Terminal phase, seeker active
            return ThreatWarningStatus.MISSILE_TRACKING
        elif missile_range < 50:  # Approaching terminal
            if j20_radar_active:
                return ThreatWarningStatus.RADAR_WARNING
            else:
                # Passive launch - may have no warning
                return ThreatWarningStatus.LAUNCH_DETECTION
        elif missile_range < 100:  # Midcourse
            if j20_radar_active:
                return ThreatWarningStatus.RADAR_WARNING
            else:
                return ThreatWarningStatus.LAUNCH_DETECTION
        else:
            if j20_radar_active:
                return ThreatWarningStatus.RADAR_WARNING
            else:
                return ThreatWarningStatus.NO_WARNING  # Passive engagement

    def calculate_pk_against_f35(
        self,
        pl15_position: np.ndarray,
        pl15_velocity: np.ndarray,
        f35_position: np.ndarray,
        f35_velocity: np.ndarray,
        defensive_maneuver: DefensiveManeuver = DefensiveManeuver.NONE,
        ecm_active: bool = False
    ) -> float:
        """
        Calculate PL-15 Pk against F-35 with defensive measures

        Factors:
        - F-35 RCS (aspect-dependent)
        - Defensive maneuvers
        - ECM effectiveness
        - Engagement geometry
        """
        # Get F-35 RCS
        f35_rcs = self.calculate_f35_rcs_vs_pl15(
            pl15_position, f35_position, f35_velocity
        )

        # Calculate range
        range_km = np.linalg.norm(f35_position - pl15_position) / 1000.0

        # Calculate aspect angle (relative to missile)
        rel_pos = f35_position - pl15_position
        if np.linalg.norm(f35_velocity) > 0:
            f35_heading = f35_velocity / np.linalg.norm(f35_velocity)
            rel_pos_norm = rel_pos / np.linalg.norm(rel_pos)
            cos_aspect = np.dot(f35_heading, -rel_pos_norm)
            aspect_deg = np.degrees(np.arccos(np.clip(cos_aspect, -1, 1)))
        else:
            aspect_deg = 0.0

        # Create target state
        target = TargetState(
            position=f35_position,
            velocity=f35_velocity,
            acceleration=np.zeros(3),
            rcs_m2=f35_rcs.rcs_m2,
            aspect_angle_deg=aspect_deg
        )

        # Get base Pk from PL-15 model
        intercept = self.pl15.predict_intercept(
            pl15_position, pl15_velocity, target,
            phase=EngagementPhase.MIDCOURSE
        )

        base_pk = intercept.probability_kill

        # Apply defensive maneuver modifiers
        maneuver_modifier = self._get_maneuver_pk_modifier(
            defensive_maneuver, aspect_deg, range_km
        )

        # Apply ECM modifier
        ecm_modifier = 1.0
        if ecm_active and range_km < self.capabilities.ecm_effective_range_km:
            ecm_modifier = 0.6  # ECM reduces Pk by 40%

        # Apply F-35 stealth modifier
        # Low RCS reduces seeker acquisition probability
        stealth_modifier = 1.0
        if f35_rcs.rcs_m2 < 0.001:  # < -30 dBsm
            stealth_modifier = 0.75  # 25% reduction
        elif f35_rcs.rcs_m2 < 0.01:  # < -20 dBsm
            stealth_modifier = 0.85

        final_pk = base_pk * maneuver_modifier * ecm_modifier * stealth_modifier
        return np.clip(final_pk, 0.0, 0.95)

    def _get_maneuver_pk_modifier(
        self,
        maneuver: DefensiveManeuver,
        aspect_deg: float,
        range_km: float
    ) -> float:
        """Get Pk modifier for defensive maneuver"""

        if maneuver == DefensiveManeuver.NONE:
            return 1.0

        elif maneuver == DefensiveManeuver.BEAM:
            # Beaming: Turn 90° to exploit Doppler notch
            # Most effective at medium range
            if 30 < range_km < 80:
                return 0.5  # 50% reduction
            else:
                return 0.7

        elif maneuver == DefensiveManeuver.NOTCH:
            # Notching: Beam + terrain masking
            # Very effective if terrain available
            if 20 < range_km < 60:
                return 0.3  # 70% reduction
            else:
                return 0.5

        elif maneuver == DefensiveManeuver.CRANK:
            # Cranking: Turn 45-60° away while maintaining radar contact
            # Moderate effectiveness
            return 0.75

        elif maneuver == DefensiveManeuver.DRAG:
            # Drag: Turn cold, maximize range
            # Effective at long range
            if range_km > 80:
                return 0.4  # 60% reduction
            else:
                return 0.7

        elif maneuver == DefensiveManeuver.DIVE:
            # Dive: Increase air density for missile drag
            # Moderate effectiveness
            if range_km > 50:
                return 0.55
            else:
                return 0.8

        elif maneuver == DefensiveManeuver.CHAFF:
            # Chaff: Create false targets
            # Effective in terminal phase
            if range_km < 20:
                return 0.4  # 60% reduction
            else:
                return 0.85

        return 1.0

    def recommend_defense(
        self,
        pl15_position: np.ndarray,
        pl15_velocity: np.ndarray,
        f35_position: np.ndarray,
        f35_velocity: np.ndarray,
        terrain_available: bool = False
    ) -> Tuple[DefensiveManeuver, List[str]]:
        """
        Recommend optimal defensive maneuver and actions

        Returns best maneuver and list of recommendations.
        """
        range_km = np.linalg.norm(f35_position - pl15_position) / 1000.0
        recommendations = []

        # Calculate Pk for each maneuver
        maneuver_pks = {}
        for maneuver in DefensiveManeuver:
            pk = self.calculate_pk_against_f35(
                pl15_position, pl15_velocity,
                f35_position, f35_velocity,
                maneuver
            )
            maneuver_pks[maneuver] = pk

        # Find best maneuver (lowest Pk)
        best_maneuver = min(maneuver_pks, key=maneuver_pks.get)
        best_pk = maneuver_pks[best_maneuver]

        # Generate recommendations based on range and geometry
        if range_km > 80:
            recommendations.append("DRAG maneuver recommended - turn cold, maximize range")
            recommendations.append("Continue MADL emissions to maintain SA")
        elif range_km > 40:
            if terrain_available:
                recommendations.append("NOTCH into terrain - descend to ground clutter")
            else:
                recommendations.append("BEAM maneuver - turn 90° to exploit Doppler notch")
            recommendations.append("Prepare ECM deployment")
        elif range_km > 20:
            recommendations.append("DEFENSIVE BREAK - maximum G turn toward threat")
            recommendations.append("Deploy chaff corridor")
            recommendations.append("ECM active - RGPO/VGPO techniques")
        else:
            recommendations.append("TERMINAL DEFENSE - last-ditch maneuver")
            recommendations.append("Deploy chaff + flares")
            recommendations.append("Maximum G break")

        # Add general recommendations
        recommendations.append(f"Best maneuver: {best_maneuver.value} (Pk reduction to {best_pk:.2f})")

        return best_maneuver, recommendations

    def analyze_survivability(
        self,
        pl15_position: np.ndarray,
        pl15_velocity: np.ndarray,
        f35_position: np.ndarray,
        f35_velocity: np.ndarray,
        j20_radar_active: bool = True,
        terrain_available: bool = False
    ) -> ThreatAssessment:
        """
        Complete survivability analysis of F-35 vs PL-15
        """
        # Calculate range and time to impact
        range_km = np.linalg.norm(f35_position - pl15_position) / 1000.0

        rel_pos = f35_position - pl15_position
        rel_vel = f35_velocity - pl15_velocity
        closure_rate = -np.dot(rel_vel, rel_pos) / max(np.linalg.norm(rel_pos), 1)

        if closure_rate > 0:
            time_to_impact = (range_km * 1000) / closure_rate
        else:
            time_to_impact = np.inf

        # Get F-35 RCS
        f35_rcs = self.calculate_f35_rcs_vs_pl15(
            pl15_position, f35_position, f35_velocity
        )

        # Get threat warning status
        warning_status = self.assess_threat_warning(
            pl15_position, pl15_velocity,
            f35_position, f35_velocity,
            j20_radar_active
        )

        # Calculate Pk without defense
        pk_no_defense = self.calculate_pk_against_f35(
            pl15_position, pl15_velocity,
            f35_position, f35_velocity,
            DefensiveManeuver.NONE
        )

        # Get best defensive maneuver
        best_maneuver, recommendations = self.recommend_defense(
            pl15_position, pl15_velocity,
            f35_position, f35_velocity,
            terrain_available
        )

        # Calculate Pk with best defense + ECM
        pk_with_defense = self.calculate_pk_against_f35(
            pl15_position, pl15_velocity,
            f35_position, f35_velocity,
            best_maneuver,
            ecm_active=True
        )

        survival_probability = 1.0 - pk_with_defense

        # Add warning-specific recommendations
        if warning_status == ThreatWarningStatus.NO_WARNING:
            recommendations.insert(0, "WARNING: Passive engagement - minimal warning!")
            survival_probability *= 0.7  # Reduced survival without warning

        # Calculate confidence
        confidence = f35_rcs.confidence * 0.7

        return ThreatAssessment(
            warning_status=warning_status,
            time_to_impact_s=time_to_impact,
            missile_range_km=range_km,
            f35_rcs_m2=f35_rcs.rcs_m2,
            pk_against_f35=pk_with_defense,
            best_maneuver=best_maneuver,
            survival_probability=survival_probability,
            confidence=confidence,
            recommendations=recommendations
        )

    def generate_defensive_report(
        self,
        pl15_position: np.ndarray = np.array([80000, 0, 12000]),
        pl15_velocity: np.ndarray = np.array([1200, 0, 0]),
        f35_position: np.ndarray = np.array([0, 0, 12000]),
        f35_velocity: np.ndarray = np.array([-200, 0, 0])
    ) -> str:
        """Generate comprehensive F-35 defensive analysis report"""
        report = []
        report.append("=" * 80)
        report.append("F-35 DEFENSIVE ANALYSIS VS PL-15")
        report.append("=" * 80)
        report.append("")
        report.append("Classification: UNCLASSIFIED // PUBLIC RELEASE")
        report.append("")

        # Analyze survivability
        assessment = self.analyze_survivability(
            pl15_position, pl15_velocity,
            f35_position, f35_velocity,
            j20_radar_active=True,
            terrain_available=False
        )

        report.append("THREAT SITUATION")
        report.append("-" * 80)
        report.append(f"PL-15 Range:            {assessment.missile_range_km:.0f} km")
        report.append(f"Time to Impact:         {assessment.time_to_impact_s:.1f} s")
        report.append(f"Warning Status:         {assessment.warning_status.value}")
        report.append("")

        report.append("F-35 STATUS")
        report.append("-" * 80)
        report.append(f"RCS to Missile:         {assessment.f35_rcs_m2:.4f} m² "
                     f"({10*np.log10(assessment.f35_rcs_m2):.1f} dBsm)")
        report.append("")

        report.append("THREAT ASSESSMENT")
        report.append("-" * 80)
        report.append(f"Pk vs F-35 (defended):  {assessment.pk_against_f35:.2f}")
        report.append(f"Survival Probability:   {assessment.survival_probability:.2f}")
        report.append(f"Best Maneuver:          {assessment.best_maneuver.value}")
        report.append("")

        report.append("DEFENSIVE RECOMMENDATIONS")
        report.append("-" * 80)
        for rec in assessment.recommendations:
            report.append(f"  → {rec}")
        report.append("")

        # Maneuver comparison
        report.append("DEFENSIVE MANEUVER EFFECTIVENESS")
        report.append("-" * 80)
        for maneuver in DefensiveManeuver:
            pk = self.calculate_pk_against_f35(
                pl15_position, pl15_velocity,
                f35_position, f35_velocity,
                maneuver, ecm_active=True
            )
            survival = 1.0 - pk
            bar = "█" * int(survival * 20)
            report.append(f"  {maneuver.value:12s}: Pk={pk:.2f}, Surv={survival:.2f} {bar}")
        report.append("")

        # Key findings
        report.append("=" * 80)
        report.append("KEY FINDINGS")
        report.append("=" * 80)
        report.append("")
        report.append("1. F-35 STEALTH ADVANTAGE")
        report.append("   - Low RCS reduces PL-15 seeker acquisition range")
        report.append("   - Frontal RCS ~0.0002 m² limits terminal tracking")
        report.append("   - Aspect management critical for survival")
        report.append("")
        report.append("2. WARNING LIMITATIONS")
        report.append("   - Passive engagement (ESM-guided launch) may provide no warning")
        report.append("   - PL-15 datalink guidance until terminal phase")
        report.append("   - First indication may be seeker activation at ~20 km")
        report.append("")
        report.append("3. DEFENSIVE EFFECTIVENESS")
        report.append("   - Beaming/notching most effective at medium range")
        report.append("   - ECM adds ~40% survivability improvement")
        report.append("   - Chaff effective in terminal phase")
        report.append("")

        report.append("=" * 80)
        report.append("Classification: UNCLASSIFIED // PUBLIC RELEASE")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Demonstration of F-35 defensive model vs PL-15"""
    model = F35DefensiveModel()
    print(model.generate_defensive_report())


if __name__ == "__main__":
    main()
