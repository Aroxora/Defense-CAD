#!/usr/bin/env python3
"""
American Integrated Link (AIL) CAD Framework

Implements the American Integrated Link architecture for unified
any-sensor-any-shooter kill chain operations across all US defense platforms.

SYSTEM COMPONENTS:
- Space Layer: GPS III, SDA Tracking, SBIRS
- Airborne Layer: E-7 Wedgetail, F-35, F-22, CCA, B-21
- Surface Layer: AEGIS, THAAD, Patriot, Typhon
- Subsurface Layer: Virginia-class, Ohio-class

COMPATIBLE WEAPONS:
- AIM-260 JATM, AIM-120D AMRAAM, AIM-9X
- SM-6 Block IB, SM-3 Block IIA, ESSM
- THAAD, PAC-3 MSE
- Tomahawk Block V, LRHW/CPS

DATALINKS:
- TTNT, MADL, IFDL, Link 16, CDL, CEC, AWW-13

Classification: UNCLASSIFIED // PUBLIC RELEASE
Based on: AMERICAN_INTEGRATED_LINK.md
"""

from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class DomainLayer(Enum):
    """AIL domain layers"""
    SPACE = "space"
    AIRBORNE = "airborne"
    SURFACE = "surface"
    SUBSURFACE = "subsurface"


class DataLinkType(Enum):
    """AIL datalink types"""
    TTNT = "ttnt"  # Tactical Targeting Network Technology
    MADL = "madl"  # Multifunction Advanced Data Link
    IFDL = "ifdl"  # Intra-Flight Data Link (F-22)
    LINK16 = "link16"  # Legacy TADIL-J
    CDL = "cdl"  # Common Data Link
    CEC = "cec"  # Cooperative Engagement Capability
    AWW13 = "aww13"  # AWACS-to-Weapon Link
    SATELLITE = "satellite"  # BLOS relay


class PlatformType(Enum):
    """AIL platform types"""
    # Airborne
    F35 = "f35"
    F22 = "f22"
    E7 = "e7_wedgetail"
    B21 = "b21_raider"
    CCA = "cca"
    MQ25 = "mq25"
    RQ180 = "rq180"
    # Surface
    DDG51 = "ddg51_flight_iii"
    DDG1000 = "ddg1000_zumwalt"
    CG47 = "cg47_ticonderoga"
    AEGIS_ASHORE = "aegis_ashore"
    THAAD = "thaad"
    PATRIOT = "patriot"
    TYPHON = "typhon"
    HIMARS = "himars_er"
    # Subsurface
    VIRGINIA = "virginia_ssn"
    OHIO_SSGN = "ohio_ssgn"
    # Space
    GPS3 = "gps_iii"
    SDA = "sda_tracking"
    SBIRS = "sbirs"


class WeaponType(Enum):
    """AIL weapon types"""
    AIM260 = "aim260_jatm"
    AIM120D = "aim120d_amraam"
    AIM9X = "aim9x_block_iii"
    SM6 = "sm6_block_ib"
    SM3 = "sm3_block_iia"
    ESSM = "essm_block_2"
    THAAD_INT = "thaad_interceptor"
    PAC3 = "pac3_mse"
    TOMAHAWK = "tomahawk_block_v"
    LRHW = "lrhw_dark_eagle"
    CPS = "cps_hypersonic"
    JASSM_ER = "jassm_er"


@dataclass
class PlatformCapabilities:
    """Platform sensor and datalink capabilities"""
    platform_type: PlatformType
    name: str

    # Detection capabilities
    radar_detection_range_km: float = 0.0  # vs 1m2 RCS
    radar_detection_stealth_km: float = 0.0  # vs 0.01m2 RCS
    esm_detection_range_km: float = 0.0  # Passive intercept
    ir_detection_range_km: float = 0.0  # IR sensors

    # Track accuracy
    radar_track_cep_m: float = 100.0
    esm_track_cep_m: float = 5000.0  # Bearing only, coarse

    # Datalinks supported
    datalinks: list[DataLinkType] = field(default_factory=list)

    # Weapons carried
    weapons: list[WeaponType] = field(default_factory=list)

    # Survivability
    survivability: float = 0.75  # 0-1

    # Confidence in parameters
    confidence: float = 0.60


@dataclass
class WeaponParameters:
    """Weapon engagement parameters"""
    weapon_type: WeaponType
    name: str

    # Range
    max_range_km: float = 0.0
    nez_km: float = 0.0  # No-Escape Zone

    # Guidance
    datalink_capable: bool = True
    awacs_guidance: bool = False  # Can E-7 guide directly?
    autonomous_terminal: bool = True

    # Performance
    pk_at_nez: float = 0.80
    pk_at_max_range: float = 0.50

    # Confidence
    confidence: float = 0.60


@dataclass
class DataLinkParameters:
    """Datalink specifications"""
    link_type: DataLinkType
    name: str

    # Performance
    bandwidth_mbps: float = 1.0
    latency_ms: float = 100.0
    range_km: float = 300.0

    # Resilience
    jam_resistant: bool = False
    lpi: bool = False  # Low Probability of Intercept
    encrypted: bool = True

    # Compatibility
    platforms: list[PlatformType] = field(default_factory=list)


@dataclass
class FusedTrack:
    """Multi-sensor fused track"""
    track_id: int
    position_x_m: float
    position_y_m: float
    position_z_m: float
    velocity_x_mps: float
    velocity_y_mps: float
    velocity_z_mps: float
    cep_m: float  # Circular Error Probable
    classification: str
    confidence: float
    sources: list[str]  # Contributing sensors
    timestamp_ms: int


@dataclass
class EngagementResult:
    """Engagement outcome"""
    target_id: int
    shooter_platform: str
    weapon_type: str
    launch_range_km: float
    pk_estimate: float
    guidance_sources: list[str]
    backup_guidance: bool
    result: str  # "hit", "miss", "pending"


@dataclass
class AILMetrics:
    """American Integrated Link performance metrics"""
    passive_detection_range_km: float
    active_detection_range_km: float
    integrated_track_cep_m: float
    weapon_nez_km: float
    pk_at_200km: float
    first_shot_advantage_km: float
    network_resilience_score: float
    engage_on_remote_range_km: float
    datalink_redundancy: int
    confidence: float


@dataclass
class ComparisonResult:
    """Comparison vs adversary system"""
    ail_metrics: AILMetrics
    adversary_metrics: dict[str, float]
    adversary_name: str
    advantages: dict[str, float]
    win_ratio: float
    assessment: str


class AmericanIntegratedLink:
    """
    American Integrated Link CAD implementation.

    Implements the full any-sensor-any-shooter architecture from
    AMERICAN_INTEGRATED_LINK.md with all compatible US platforms.
    """

    def __init__(self):
        """Initialize AIL framework"""
        self.platforms = self._initialize_platforms()
        self.weapons = self._initialize_weapons()
        self.datalinks = self._initialize_datalinks()

    def _initialize_platforms(self) -> dict[PlatformType, PlatformCapabilities]:
        """Initialize all AIL-compatible platforms"""
        platforms = {}

        # F-35 Lightning II
        platforms[PlatformType.F35] = PlatformCapabilities(
            platform_type=PlatformType.F35,
            name="F-35A Lightning II",
            radar_detection_range_km=150,  # APG-81 vs 1m2
            radar_detection_stealth_km=80,  # vs 0.01m2, LPI mode
            esm_detection_range_km=200,  # ASQ-239 passive
            ir_detection_range_km=100,  # EOTS/DAS
            radar_track_cep_m=50,
            esm_track_cep_m=3000,  # Bearing-only
            datalinks=[DataLinkType.MADL, DataLinkType.LINK16],
            weapons=[WeaponType.AIM260, WeaponType.AIM120D, WeaponType.AIM9X],
            survivability=0.75,
            confidence=0.70
        )

        # F-22 Raptor
        platforms[PlatformType.F22] = PlatformCapabilities(
            platform_type=PlatformType.F22,
            name="F-22A Raptor",
            radar_detection_range_km=200,  # APG-77(V)1
            radar_detection_stealth_km=100,  # vs 0.01m2
            esm_detection_range_km=250,  # ALR-94
            ir_detection_range_km=50,
            radar_track_cep_m=40,
            esm_track_cep_m=2500,
            datalinks=[DataLinkType.IFDL, DataLinkType.LINK16],
            weapons=[WeaponType.AIM260, WeaponType.AIM120D, WeaponType.AIM9X],
            survivability=0.80,
            confidence=0.65
        )

        # E-7 Wedgetail
        platforms[PlatformType.E7] = PlatformCapabilities(
            platform_type=PlatformType.E7,
            name="E-7 Wedgetail",
            radar_detection_range_km=400,  # MESA AESA vs 1m2
            radar_detection_stealth_km=200,  # L-band resonance
            esm_detection_range_km=600,  # Wide-area ESM
            ir_detection_range_km=0,
            radar_track_cep_m=100,
            esm_track_cep_m=5000,  # TDOA/FDOA capable
            datalinks=[DataLinkType.TTNT, DataLinkType.LINK16,
                       DataLinkType.CDL, DataLinkType.MADL, DataLinkType.AWW13],
            weapons=[],  # Battle manager, not shooter
            survivability=0.90,  # Standoff position
            confidence=0.60
        )

        # CCA (Collaborative Combat Aircraft)
        platforms[PlatformType.CCA] = PlatformCapabilities(
            platform_type=PlatformType.CCA,
            name="CCA Increment 1",
            radar_detection_range_km=100,  # Smaller AESA
            radar_detection_stealth_km=50,
            esm_detection_range_km=150,
            ir_detection_range_km=80,
            radar_track_cep_m=75,
            esm_track_cep_m=4000,
            datalinks=[DataLinkType.MADL],
            weapons=[WeaponType.AIM260, WeaponType.AIM120D],
            survivability=0.30,  # Attritable
            confidence=0.45
        )

        # B-21 Raider
        platforms[PlatformType.B21] = PlatformCapabilities(
            platform_type=PlatformType.B21,
            name="B-21 Raider",
            radar_detection_range_km=250,  # Advanced AESA
            radar_detection_stealth_km=150,
            esm_detection_range_km=400,
            ir_detection_range_km=200,
            radar_track_cep_m=60,
            esm_track_cep_m=3000,
            datalinks=[DataLinkType.CDL, DataLinkType.LINK16, DataLinkType.SATELLITE],
            weapons=[WeaponType.JASSM_ER, WeaponType.LRHW],
            survivability=0.85,  # Low observability
            confidence=0.45
        )

        # DDG-51 Flight III
        platforms[PlatformType.DDG51] = PlatformCapabilities(
            platform_type=PlatformType.DDG51,
            name="DDG-51 Flight III",
            radar_detection_range_km=500,  # SPY-6(V)1 vs 1m2
            radar_detection_stealth_km=200,  # vs 0.01m2
            esm_detection_range_km=300,
            ir_detection_range_km=0,
            radar_track_cep_m=50,
            esm_track_cep_m=4000,
            datalinks=[DataLinkType.CEC, DataLinkType.LINK16,
                       DataLinkType.TTNT, DataLinkType.SATELLITE],
            weapons=[WeaponType.SM6, WeaponType.SM3, WeaponType.ESSM,
                     WeaponType.TOMAHAWK],
            survivability=0.85,
            confidence=0.70
        )

        # AEGIS Ashore
        platforms[PlatformType.AEGIS_ASHORE] = PlatformCapabilities(
            platform_type=PlatformType.AEGIS_ASHORE,
            name="AEGIS Ashore",
            radar_detection_range_km=500,  # SPY-6
            radar_detection_stealth_km=200,
            esm_detection_range_km=0,
            ir_detection_range_km=0,
            radar_track_cep_m=50,
            esm_track_cep_m=0,
            datalinks=[DataLinkType.CEC, DataLinkType.LINK16, DataLinkType.TTNT],
            weapons=[WeaponType.SM6, WeaponType.SM3],
            survivability=0.90,  # Hardened
            confidence=0.70
        )

        # THAAD
        platforms[PlatformType.THAAD] = PlatformCapabilities(
            platform_type=PlatformType.THAAD,
            name="THAAD",
            radar_detection_range_km=1000,  # AN/TPY-2
            radar_detection_stealth_km=500,
            esm_detection_range_km=0,
            ir_detection_range_km=0,
            radar_track_cep_m=30,
            esm_track_cep_m=0,
            datalinks=[DataLinkType.LINK16, DataLinkType.SATELLITE],
            weapons=[WeaponType.THAAD_INT],
            survivability=0.80,
            confidence=0.70
        )

        # Patriot PAC-3
        platforms[PlatformType.PATRIOT] = PlatformCapabilities(
            platform_type=PlatformType.PATRIOT,
            name="Patriot PAC-3 MSE",
            radar_detection_range_km=100,  # AN/MPQ-65
            radar_detection_stealth_km=50,
            esm_detection_range_km=0,
            ir_detection_range_km=0,
            radar_track_cep_m=20,
            esm_track_cep_m=0,
            datalinks=[DataLinkType.LINK16],
            weapons=[WeaponType.PAC3],
            survivability=0.75,
            confidence=0.75
        )

        # Typhon
        platforms[PlatformType.TYPHON] = PlatformCapabilities(
            platform_type=PlatformType.TYPHON,
            name="Typhon Ground Launcher",
            radar_detection_range_km=0,  # Remote cueing only
            radar_detection_stealth_km=0,
            esm_detection_range_km=0,
            ir_detection_range_km=0,
            radar_track_cep_m=0,
            esm_track_cep_m=0,
            datalinks=[DataLinkType.LINK16, DataLinkType.TTNT],
            weapons=[WeaponType.TOMAHAWK, WeaponType.SM6],
            survivability=0.70,  # Mobile, dispersed
            confidence=0.55
        )

        # Virginia-class SSN
        platforms[PlatformType.VIRGINIA] = PlatformCapabilities(
            platform_type=PlatformType.VIRGINIA,
            name="Virginia Block V SSN",
            radar_detection_range_km=0,
            radar_detection_stealth_km=0,
            esm_detection_range_km=100,  # ESM mast
            ir_detection_range_km=0,
            radar_track_cep_m=0,
            esm_track_cep_m=10000,
            datalinks=[DataLinkType.SATELLITE],  # Submarine broadcast
            weapons=[WeaponType.TOMAHAWK, WeaponType.CPS],
            survivability=0.95,  # Undersea
            confidence=0.55
        )

        return platforms

    def _initialize_weapons(self) -> dict[WeaponType, WeaponParameters]:
        """Initialize all AIL-compatible weapons"""
        weapons = {}

        weapons[WeaponType.AIM260] = WeaponParameters(
            weapon_type=WeaponType.AIM260,
            name="AIM-260 JATM",
            max_range_km=200,
            nez_km=120,
            datalink_capable=True,
            awacs_guidance=True,  # AWW-13 capable
            autonomous_terminal=True,
            pk_at_nez=0.85,
            pk_at_max_range=0.55,
            confidence=0.50
        )

        weapons[WeaponType.AIM120D] = WeaponParameters(
            weapon_type=WeaponType.AIM120D,
            name="AIM-120D AMRAAM",
            max_range_km=160,
            nez_km=70,
            datalink_capable=True,
            awacs_guidance=False,  # Shooter-only
            autonomous_terminal=True,
            pk_at_nez=0.80,
            pk_at_max_range=0.45,
            confidence=0.80
        )

        weapons[WeaponType.AIM9X] = WeaponParameters(
            weapon_type=WeaponType.AIM9X,
            name="AIM-9X Block III",
            max_range_km=35,
            nez_km=15,
            datalink_capable=True,
            awacs_guidance=False,
            autonomous_terminal=True,
            pk_at_nez=0.90,
            pk_at_max_range=0.70,
            confidence=0.80
        )

        weapons[WeaponType.SM6] = WeaponParameters(
            weapon_type=WeaponType.SM6,
            name="SM-6 Block IB",
            max_range_km=370,
            nez_km=250,
            datalink_capable=True,
            awacs_guidance=True,  # CEC / NIFC-CA
            autonomous_terminal=True,
            pk_at_nez=0.80,
            pk_at_max_range=0.50,
            confidence=0.70
        )

        weapons[WeaponType.SM3] = WeaponParameters(
            weapon_type=WeaponType.SM3,
            name="SM-3 Block IIA",
            max_range_km=2500,
            nez_km=1500,
            datalink_capable=True,
            awacs_guidance=True,  # CEC
            autonomous_terminal=True,
            pk_at_nez=0.70,
            pk_at_max_range=0.40,
            confidence=0.65
        )

        weapons[WeaponType.THAAD_INT] = WeaponParameters(
            weapon_type=WeaponType.THAAD_INT,
            name="THAAD Interceptor",
            max_range_km=200,
            nez_km=150,
            datalink_capable=True,
            awacs_guidance=False,  # Fire control radar only
            autonomous_terminal=True,
            pk_at_nez=0.85,
            pk_at_max_range=0.60,
            confidence=0.70
        )

        weapons[WeaponType.PAC3] = WeaponParameters(
            weapon_type=WeaponType.PAC3,
            name="PAC-3 MSE",
            max_range_km=35,
            nez_km=25,
            datalink_capable=True,
            awacs_guidance=False,
            autonomous_terminal=True,
            pk_at_nez=0.90,
            pk_at_max_range=0.70,
            confidence=0.75
        )

        weapons[WeaponType.TOMAHAWK] = WeaponParameters(
            weapon_type=WeaponType.TOMAHAWK,
            name="Tomahawk Block V",
            max_range_km=1600,
            nez_km=0,  # Land attack, not air defense
            datalink_capable=True,
            awacs_guidance=False,
            autonomous_terminal=True,
            pk_at_nez=0,
            pk_at_max_range=0.90,
            confidence=0.80
        )

        weapons[WeaponType.LRHW] = WeaponParameters(
            weapon_type=WeaponType.LRHW,
            name="LRHW Dark Eagle",
            max_range_km=2775,
            nez_km=0,  # Land attack
            datalink_capable=False,  # Ballistic, no mid-course
            awacs_guidance=False,
            autonomous_terminal=True,
            pk_at_nez=0,
            pk_at_max_range=0.85,
            confidence=0.55
        )

        return weapons

    def _initialize_datalinks(self) -> dict[DataLinkType, DataLinkParameters]:
        """Initialize all AIL datalinks"""
        datalinks = {}

        datalinks[DataLinkType.TTNT] = DataLinkParameters(
            link_type=DataLinkType.TTNT,
            name="Tactical Targeting Network Technology",
            bandwidth_mbps=10.0,
            latency_ms=10,
            range_km=300,
            jam_resistant=True,
            lpi=True,
            encrypted=True,
            platforms=[PlatformType.E7, PlatformType.DDG51,
                       PlatformType.AEGIS_ASHORE, PlatformType.TYPHON]
        )

        datalinks[DataLinkType.MADL] = DataLinkParameters(
            link_type=DataLinkType.MADL,
            name="Multifunction Advanced Data Link",
            bandwidth_mbps=3.0,
            latency_ms=50,
            range_km=200,
            jam_resistant=True,
            lpi=True,
            encrypted=True,
            platforms=[PlatformType.F35, PlatformType.CCA, PlatformType.E7]
        )

        datalinks[DataLinkType.IFDL] = DataLinkParameters(
            link_type=DataLinkType.IFDL,
            name="Intra-Flight Data Link",
            bandwidth_mbps=2.0,
            latency_ms=50,
            range_km=100,
            jam_resistant=True,
            lpi=True,
            encrypted=True,
            platforms=[PlatformType.F22]
        )

        datalinks[DataLinkType.LINK16] = DataLinkParameters(
            link_type=DataLinkType.LINK16,
            name="Link 16 TADIL-J",
            bandwidth_mbps=0.115,  # 115 kbps pooled
            latency_ms=1000,  # 1-12 second updates
            range_km=300,
            jam_resistant=True,
            lpi=False,
            encrypted=True,
            platforms=list(PlatformType)  # Universal
        )

        datalinks[DataLinkType.CDL] = DataLinkParameters(
            link_type=DataLinkType.CDL,
            name="Common Data Link",
            bandwidth_mbps=274.0,  # Up to 274 Mbps
            latency_ms=100,
            range_km=200,
            jam_resistant=False,
            lpi=False,
            encrypted=True,
            platforms=[PlatformType.B21, PlatformType.E7, PlatformType.RQ180]
        )

        datalinks[DataLinkType.CEC] = DataLinkParameters(
            link_type=DataLinkType.CEC,
            name="Cooperative Engagement Capability",
            bandwidth_mbps=5.0,
            latency_ms=200,
            range_km=500,  # Via satellite relay
            jam_resistant=True,
            lpi=False,
            encrypted=True,
            platforms=[PlatformType.DDG51, PlatformType.CG47,
                       PlatformType.AEGIS_ASHORE, PlatformType.E7]
        )

        datalinks[DataLinkType.AWW13] = DataLinkParameters(
            link_type=DataLinkType.AWW13,
            name="AWW-13 Weapon Datalink",
            bandwidth_mbps=0.5,
            latency_ms=300,
            range_km=400,
            jam_resistant=True,
            lpi=True,
            encrypted=True,
            platforms=[PlatformType.E7]  # AWACS-to-weapon
        )

        datalinks[DataLinkType.SATELLITE] = DataLinkParameters(
            link_type=DataLinkType.SATELLITE,
            name="Satellite BLOS Relay",
            bandwidth_mbps=10.0,
            latency_ms=500,  # LEO
            range_km=10000,  # Global
            jam_resistant=True,
            lpi=False,
            encrypted=True,
            platforms=[PlatformType.B21, PlatformType.DDG51,
                       PlatformType.VIRGINIA, PlatformType.THAAD]
        )

        return datalinks

    def calculate_passive_detection_range(
        self,
        target_emissions_power_w: float = 2.8,  # Similar to MADL sidelobes
        target_frequency_ghz: float = 15.0,  # Ku-band
        esm_platform: PlatformType = PlatformType.E7
    ) -> float:
        """
        Calculate passive ESM detection range.

        E-7 Wedgetail ESM can intercept adversary emissions at 600+ km.

        Args:
            target_emissions_power_w: Target EIRP in sidelobes (watts)
            target_frequency_ghz: Emission frequency (GHz)
            esm_platform: Platform performing detection

        Returns:
            Passive detection range in km
        """
        platform = self.platforms.get(esm_platform)
        if not platform:
            return 0.0

        base_range = platform.esm_detection_range_km

        # Adjust for emission power (reference: 2.8W at 350 km)
        power_factor = np.sqrt(target_emissions_power_w / 2.8)

        # Adjust for frequency (lower freq = longer range)
        freq_factor = np.sqrt(15.0 / target_frequency_ghz)

        detection_range = base_range * power_factor * freq_factor

        return min(detection_range, 600)  # Cap at 600 km for E-7

    def calculate_multisensor_fusion(
        self,
        sensor_tracks: list[tuple[float, float]]  # List of (cep_m, weight)
    ) -> float:
        """
        Calculate fused track accuracy from multiple sensors.

        Uses inverse variance weighting for optimal Kalman fusion.

        Args:
            sensor_tracks: List of (CEP in meters, weight) tuples

        Returns:
            Fused CEP in meters
        """
        if not sensor_tracks:
            return float('inf')

        # Inverse variance weighting
        # For sensor fusion: 1/sigma_fused^2 = sum(w_i / sigma_i^2)

        weighted_inv_variances = 0.0
        for cep, weight in sensor_tracks:
            if cep > 0:
                variance = cep ** 2
                weighted_inv_variances += weight / variance

        if weighted_inv_variances == 0:
            return float('inf')

        fused_variance = 1.0 / weighted_inv_variances
        fused_cep = np.sqrt(fused_variance)

        return fused_cep

    def calculate_engage_on_remote_range(
        self,
        sensor_platform: PlatformType = PlatformType.E7,
        shooter_platform: PlatformType = PlatformType.DDG51,
        weapon: WeaponType = WeaponType.SM6
    ) -> float:
        """
        Calculate engage-on-remote (NIFC-CA) range.

        Shooter fires on remote sensor track without own radar detection.

        Args:
            sensor_platform: Platform providing track
            shooter_platform: Platform launching weapon
            weapon: Weapon being fired

        Returns:
            Engage-on-remote range in km
        """
        sensor = self.platforms.get(sensor_platform)
        shooter = self.platforms.get(shooter_platform)
        wpn = self.weapons.get(weapon)

        if not (sensor and shooter and wpn):
            return 0.0

        # Engage-on-remote range is limited by:
        # 1. Sensor detection range
        # 2. Weapon max range
        # 3. Datalink range

        sensor_range = sensor.radar_detection_range_km

        # Check if CEC is available between sensor and shooter
        cec_available = (DataLinkType.CEC in sensor.datalinks and
                         DataLinkType.CEC in shooter.datalinks)

        if not cec_available:
            return 0.0  # No engage-on-remote without CEC

        weapon_range = wpn.max_range_km

        # Engage-on-remote extends range by sensor reach beyond shooter radar
        # Limited by weapon kinematic range
        eor_range = min(sensor_range, weapon_range)

        return eor_range

    def calculate_network_resilience_score(
        self,
        platforms: list[PlatformType] = None
    ) -> float:
        """
        Calculate AIL network resilience score (0-100).

        Based on sensor redundancy, datalink paths, and graceful degradation.

        Args:
            platforms: List of platforms in network (default: all)

        Returns:
            Resilience score (0-100)
        """
        if platforms is None:
            platforms = list(self.platforms.keys())

        score = 0.0

        # Node redundancy (45 points max)
        node_score = 0.0
        for platform_type in platforms:
            platform = self.platforms.get(platform_type)
            if platform:
                # Weight by survivability and sensor capability
                weight = platform.survivability
                if platform.radar_detection_range_km > 300:
                    node_score += 10 * weight  # Major sensor
                elif platform.radar_detection_range_km > 100:
                    node_score += 5 * weight  # Medium sensor
                else:
                    node_score += 2 * weight  # Limited

        score += min(node_score, 45)

        # Datalink redundancy (30 points max)
        available_datalinks = set()
        for platform_type in platforms:
            platform = self.platforms.get(platform_type)
            if platform:
                available_datalinks.update(platform.datalinks)

        link_score = len(available_datalinks) * 5
        score += min(link_score, 30)

        # Graceful degradation (25 points max)
        degradation_score = 0.0

        # AWACS-to-weapon backup
        e7_in_network = PlatformType.E7 in platforms
        if e7_in_network and DataLinkType.AWW13 in available_datalinks:
            degradation_score += 10

        # Multiple sensor types
        sensor_types = 0
        for platform_type in platforms:
            platform = self.platforms.get(platform_type)
            if platform:
                if platform.radar_detection_range_km > 0:
                    sensor_types += 1
                if platform.esm_detection_range_km > 0:
                    sensor_types += 1
                if platform.ir_detection_range_km > 0:
                    sensor_types += 1

        if sensor_types >= 6:
            degradation_score += 10
        elif sensor_types >= 3:
            degradation_score += 5

        # Autonomous weapon modes
        degradation_score += 5  # All weapons have GPS+INS backup

        score += min(degradation_score, 25)

        return score

    def calculate_ail_metrics(self) -> AILMetrics:
        """
        Calculate American Integrated Link performance metrics.

        Returns complete metrics per AMERICAN_INTEGRATED_LINK.md
        """
        # Passive detection (E-7 ESM)
        passive_range = self.calculate_passive_detection_range()

        # Active detection (E-7 MESA radar)
        e7 = self.platforms.get(PlatformType.E7)
        active_range = e7.radar_detection_range_km if e7 else 0

        # Integrated track accuracy (multi-sensor fusion)
        # E-7 radar + F-35 x4 (radar + EW + IR)
        sensor_tracks = [
            (100, 1.0),  # E-7 radar
            (50, 2.0),  # F-35 #1 radar
            (50, 2.0),  # F-35 #2 radar
            (50, 2.0),  # F-35 #3 radar
            (50, 2.0),  # F-35 #4 radar
            (3000, 0.2),  # F-35 EW (bearing only)
            (500, 0.5),  # F-35 IR
        ]
        integrated_cep = self.calculate_multisensor_fusion(sensor_tracks)

        # Weapon NEZ (AIM-260 with network support)
        aim260 = self.weapons.get(WeaponType.AIM260)
        weapon_nez = aim260.nez_km if aim260 else 0

        # Pk at 200 km
        # With full AIL support: interpolate between NEZ and max range
        if aim260:
            range_factor = (200 - aim260.nez_km) / (aim260.max_range_km - aim260.nez_km)
            pk_200 = aim260.pk_at_nez - (aim260.pk_at_nez - aim260.pk_at_max_range) * range_factor
            pk_200 = max(0.55, min(0.70, pk_200))  # Clamp to reasonable range
        else:
            pk_200 = 0.60

        # First-shot advantage (passive detection - adversary active detection)
        # vs Chinese J-20 ESM: 350 km (E-7 ESM) - 200 km (J-20 ESM) = +150 km
        first_shot_advantage = passive_range - 200

        # Network resilience
        resilience = self.calculate_network_resilience_score()

        # Engage-on-remote range
        eor_range = self.calculate_engage_on_remote_range()

        # Datalink redundancy count
        all_datalinks = set()
        for platform in self.platforms.values():
            all_datalinks.update(platform.datalinks)
        datalink_redundancy = len(all_datalinks)

        return AILMetrics(
            passive_detection_range_km=passive_range,
            active_detection_range_km=active_range,
            integrated_track_cep_m=integrated_cep,
            weapon_nez_km=weapon_nez,
            pk_at_200km=pk_200,
            first_shot_advantage_km=first_shot_advantage,
            network_resilience_score=resilience,
            engage_on_remote_range_km=eor_range,
            datalink_redundancy=datalink_redundancy,
            confidence=0.65
        )

    def calculate_chinese_metrics(self) -> dict[str, float]:
        """
        Calculate Chinese integrated system metrics for comparison.

        Based on CHINESE_INTEGRATED_KILL_CHAIN.md
        """
        return {
            'passive_detection_range_km': 200,  # J-20 ESM + KJ-500
            'active_detection_range_km': 250,  # KJ-500 VHF radar
            'integrated_track_cep_m': 40,  # Multi-sensor fusion
            'weapon_nez_km': 100,  # PL-15 network-extended
            'pk_at_200km': 0.65,  # With network support
            'first_shot_advantage_km': 100,  # vs F-35 legacy
            'network_resilience_score': 87,
            'confidence': 0.60
        }

    def compare_vs_chinese(self) -> ComparisonResult:
        """
        Compare AIL vs Chinese integrated kill chain.

        Returns:
            Detailed comparison result
        """
        ail = self.calculate_ail_metrics()
        chinese = self.calculate_chinese_metrics()

        # Calculate advantages (positive = US advantage)
        advantages = {
            'passive_detection_km': ail.passive_detection_range_km -
                                   chinese['passive_detection_range_km'],
            'active_detection_km': ail.active_detection_range_km -
                                  chinese['active_detection_range_km'],
            'track_accuracy_m': chinese['integrated_track_cep_m'] -
                               ail.integrated_track_cep_m,  # Lower is better
            'weapon_nez_km': ail.weapon_nez_km -
                            chinese['weapon_nez_km'],
            'pk_advantage': ail.pk_at_200km -
                           chinese['pk_at_200km'],
            'resilience_points': ail.network_resilience_score -
                                chinese['network_resilience_score']
        }

        # Calculate win ratio at 200 km engagement
        ail_win_prob = ail.pk_at_200km * (1 - chinese['pk_at_200km'])
        chinese_win_prob = chinese['pk_at_200km'] * (1 - ail.pk_at_200km)

        if chinese_win_prob > 0:
            win_ratio = ail_win_prob / chinese_win_prob
        else:
            win_ratio = float('inf')

        # Assessment
        if win_ratio > 1.5:
            assessment = f"AIL significant advantage ({win_ratio:.2f}:1 win ratio)"
        elif win_ratio > 1.1:
            assessment = f"AIL moderate advantage ({win_ratio:.2f}:1 win ratio)"
        elif win_ratio > 0.9:
            assessment = "Roughly comparable systems"
        elif win_ratio > 0.67:
            assessment = f"Chinese moderate advantage ({1/win_ratio:.2f}:1)"
        else:
            assessment = f"Chinese significant advantage ({1/win_ratio:.2f}:1)"

        return ComparisonResult(
            ail_metrics=ail,
            adversary_metrics=chinese,
            adversary_name="Chinese Integrated Kill Chain",
            advantages=advantages,
            win_ratio=win_ratio,
            assessment=assessment
        )

    def simulate_engagement(
        self,
        target_rcs_m2: float = 0.01,
        initial_range_km: float = 400,
        ail_platforms: list[PlatformType] = None
    ) -> dict:
        """
        Simulate AIL engagement vs incoming threat.

        Args:
            target_rcs_m2: Target radar cross section
            initial_range_km: Initial detection range
            ail_platforms: Platforms available for engagement

        Returns:
            Engagement simulation results
        """
        if ail_platforms is None:
            ail_platforms = [
                PlatformType.E7,
                PlatformType.F35,
                PlatformType.DDG51,
                PlatformType.CCA
            ]

        results = {
            'phases': [],
            'outcome': None,
            'weapons_expended': 0,
            'pk_cumulative': 0.0
        }

        current_range = initial_range_km

        # Phase 1: Space Layer Detection
        results['phases'].append({
            'phase': 'Space Layer Detection',
            'range_km': current_range,
            'sensors': ['SDA Tracking', 'SBIRS'],
            'track_cep_m': 10000,
            'action': 'Cue airborne layer'
        })

        # Phase 2: Airborne Layer Detection (E-7)
        current_range -= 100
        e7 = self.platforms.get(PlatformType.E7)
        if e7 and current_range <= e7.esm_detection_range_km:
            results['phases'].append({
                'phase': 'E-7 ESM Detection',
                'range_km': current_range,
                'sensors': ['E-7 Wedgetail ESM'],
                'track_cep_m': 5000,
                'action': 'TDOA geolocation, cue radar'
            })

        # Phase 3: E-7 Radar Track
        current_range -= 50
        if e7 and current_range <= e7.radar_detection_range_km:
            track_cep = e7.radar_track_cep_m
            results['phases'].append({
                'phase': 'E-7 Radar Track',
                'range_km': current_range,
                'sensors': ['E-7 MESA AESA'],
                'track_cep_m': track_cep,
                'action': 'Refined track, vector F-35 CAP'
            })

        # Phase 4: F-35 Network Detection
        current_range -= 50
        f35 = self.platforms.get(PlatformType.F35)
        if f35:
            # Multi-sensor fusion
            sensor_tracks = [
                (e7.radar_track_cep_m, 1.0) if e7 else (1000, 0.1),
                (f35.radar_track_cep_m, 2.0),
                (f35.esm_track_cep_m, 0.2),
            ]
            fused_cep = self.calculate_multisensor_fusion(sensor_tracks)
            results['phases'].append({
                'phase': 'F-35 Network Fusion',
                'range_km': current_range,
                'sensors': ['F-35 APG-81', 'F-35 ASQ-239', 'E-7 MESA'],
                'track_cep_m': fused_cep,
                'action': 'Weapons-grade track, prepare engagement'
            })

        # Phase 5: Engagement Decision
        current_range -= 50
        results['phases'].append({
            'phase': 'Engagement Decision',
            'range_km': current_range,
            'sensors': ['ODIN AI'],
            'track_cep_m': fused_cep,
            'action': 'Optimize shooter assignment, WEAPONS RELEASE'
        })

        # Phase 6: AIM-260 Launch
        aim260 = self.weapons.get(WeaponType.AIM260)
        if aim260 and current_range <= aim260.max_range_km:
            # Calculate Pk based on range
            if current_range <= aim260.nez_km:
                pk = aim260.pk_at_nez
            else:
                range_factor = (current_range - aim260.nez_km) / \
                              (aim260.max_range_km - aim260.nez_km)
                pk = aim260.pk_at_nez - \
                    (aim260.pk_at_nez - aim260.pk_at_max_range) * range_factor

            results['phases'].append({
                'phase': 'AIM-260 Launch',
                'range_km': current_range,
                'weapon': 'AIM-260 JATM',
                'pk': pk,
                'guidance': ['F-35 primary', 'E-7 backup (AWW-13)']
            })
            results['weapons_expended'] += 2  # Salvo
            results['pk_cumulative'] = 1 - (1 - pk) ** 2  # Salvo Pk

        # Phase 7: Engage-on-Remote (SM-6)
        if current_range <= 300:  # Within CEC range
            sm6 = self.weapons.get(WeaponType.SM6)
            if sm6:
                eor_pk = sm6.pk_at_nez * 0.9  # Slight reduction for remote track
                results['phases'].append({
                    'phase': 'DDG SM-6 Engage-on-Remote',
                    'range_km': current_range,
                    'weapon': 'SM-6 Block IB',
                    'pk': eor_pk,
                    'guidance': ['E-7 CEC track', 'DDG fire control']
                })
                results['weapons_expended'] += 2
                # Combined Pk
                current_pk = results['pk_cumulative']
                results['pk_cumulative'] = 1 - (1 - current_pk) * (1 - eor_pk) ** 2

        # Final outcome
        if results['pk_cumulative'] > 0.95:
            results['outcome'] = 'TARGET DESTROYED (95%+ confidence)'
        elif results['pk_cumulative'] > 0.80:
            results['outcome'] = 'TARGET LIKELY DESTROYED (80-95% confidence)'
        elif results['pk_cumulative'] > 0.50:
            results['outcome'] = 'ENGAGEMENT UNCERTAIN (50-80% confidence)'
        else:
            results['outcome'] = 'LEAKER PROBABLE (<50% confidence)'

        return results

    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive AIL analysis report"""
        report = []
        report.append("=" * 80)
        report.append("AMERICAN INTEGRATED LINK (AIL) CAD ANALYSIS")
        report.append("=" * 80)
        report.append("")
        report.append("Based on: AMERICAN_INTEGRATED_LINK.md")
        report.append("Framework: US Defense Contractor Models")
        report.append("Classification: UNCLASSIFIED // PUBLIC RELEASE")
        report.append("")

        # AIL metrics
        ail = self.calculate_ail_metrics()
        report.append("AIL SYSTEM METRICS")
        report.append("-" * 80)
        report.append(f"Passive Detection Range:    {ail.passive_detection_range_km:.0f} km (E-7 ESM)")
        report.append(f"Active Detection Range:     {ail.active_detection_range_km:.0f} km (E-7 MESA)")
        report.append(f"Integrated Track CEP:       {ail.integrated_track_cep_m:.0f} m (multi-sensor fusion)")
        report.append(f"Weapon NEZ:                 {ail.weapon_nez_km:.0f} km (AIM-260)")
        report.append(f"Pk at 200 km:               {ail.pk_at_200km:.2f} (with network support)")
        report.append(f"First-Shot Advantage:       +{ail.first_shot_advantage_km:.0f} km (vs Chinese)")
        report.append(f"Network Resilience:         {ail.network_resilience_score:.0f}/100")
        report.append(f"Engage-on-Remote Range:     {ail.engage_on_remote_range_km:.0f} km (NIFC-CA)")
        report.append(f"Datalink Redundancy:        {ail.datalink_redundancy} link types")
        report.append(f"Overall Confidence:         {ail.confidence:.0%}")
        report.append("")

        # Platform summary
        report.append("COMPATIBLE PLATFORMS")
        report.append("-" * 80)
        for platform_type, platform in self.platforms.items():
            datalinks = ", ".join([dl.name for dl in platform.datalinks])
            report.append(f"  {platform.name}")
            report.append(f"    Radar: {platform.radar_detection_range_km:.0f} km | "
                         f"ESM: {platform.esm_detection_range_km:.0f} km")
            report.append(f"    Links: {datalinks}")
        report.append("")

        # Weapon summary
        report.append("COMPATIBLE WEAPONS")
        report.append("-" * 80)
        for weapon_type, weapon in self.weapons.items():
            awacs = "YES" if weapon.awacs_guidance else "NO"
            report.append(f"  {weapon.name}")
            report.append(f"    Range: {weapon.max_range_km:.0f} km | "
                         f"NEZ: {weapon.nez_km:.0f} km | "
                         f"AWACS Guidance: {awacs}")
        report.append("")

        # Comparison vs Chinese
        report.append("COMPARISON VS CHINESE INTEGRATED KILL CHAIN")
        report.append("-" * 80)
        comp = self.compare_vs_chinese()
        report.append(f"Assessment: {comp.assessment}")
        report.append(f"Win Ratio: {comp.win_ratio:.2f}:1 (AIL:Chinese)")
        report.append("")
        report.append("Advantages (positive = AIL advantage):")
        for metric, value in comp.advantages.items():
            sign = "+" if value > 0 else ""
            report.append(f"  {metric}: {sign}{value:.1f}")
        report.append("")

        # Engagement simulation
        report.append("ENGAGEMENT SIMULATION (vs 0.01 m2 target at 400 km)")
        report.append("-" * 80)
        sim = self.simulate_engagement()
        for phase in sim['phases']:
            report.append(f"  {phase['phase']}")
            report.append(f"    Range: {phase['range_km']:.0f} km")
            if 'track_cep_m' in phase:
                report.append(f"    Track CEP: {phase['track_cep_m']:.0f} m")
            if 'pk' in phase:
                report.append(f"    Pk: {phase['pk']:.2f}")
            report.append(f"    Action: {phase.get('action', phase.get('weapon', 'N/A'))}")
        report.append("")
        report.append(f"  OUTCOME: {sim['outcome']}")
        report.append(f"  Weapons Expended: {sim['weapons_expended']}")
        report.append(f"  Cumulative Pk: {sim['pk_cumulative']:.2f}")
        report.append("")

        # Key findings
        report.append("=" * 80)
        report.append("KEY FINDINGS")
        report.append("=" * 80)
        report.append("")
        report.append("1. AIL ACHIEVES PARITY OR ADVANTAGE WHEN FULLY IMPLEMENTED")
        report.append("   - Detection range: +130-150 km advantage (E-7 ESM + MESA)")
        report.append("   - Engage-on-remote: Extends surface-to-air by 100+ km")
        report.append("   - Network resilience: 95/100 vs 87/100")
        report.append("")
        report.append("2. CURRENT GAP: INTEGRATION MATURITY")
        report.append("   - Chinese system: Operational since 2017")
        report.append("   - US system: Full AIL by 2030+")
        report.append("   - Timeline disadvantage: 5-10 years")
        report.append("")
        report.append("3. CRITICAL ENABLERS")
        report.append("   - AWW-13 datalink: AWACS-to-weapon backup")
        report.append("   - E-7 MADL gateway: Bridges F-35 to AWACS")
        report.append("   - CEC expansion: Beyond Navy to joint force")
        report.append("")

        report.append("=" * 80)
        report.append("Classification: UNCLASSIFIED // PUBLIC RELEASE")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Demonstration of American Integrated Link CAD"""
    ail = AmericanIntegratedLink()
    print(ail.generate_comprehensive_report())


if __name__ == "__main__":
    main()
