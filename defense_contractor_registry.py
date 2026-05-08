#!/usr/bin/env python3
"""
Defense Contractor Model Registry

Organizes pretrained CAD models by defense contractor for Chinese and Russian
military industrial complexes. Integrates with kill chain analysis framework.

CHINESE CONTRACTORS:
- AVIC (Aviation Industry Corporation of China): J-20, J-10C, J-11B, J-15, J-16
- CASIC (China Aerospace Science and Industry Corporation): PL-15, PL-21, DF-17
- CASC (China Aerospace Science and Technology Corporation): Beidou, DF-21D, DF-26

RUSSIAN CONTRACTORS:
- Sukhoi (JSC Sukhoi Company): Su-35, Su-57, Su-30SM, Su-34
- MiG (Russian Aircraft Corporation): MiG-31
- NPO Almaz (JSC Almaz): S-400, S-300PMU-2

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Type
from enum import Enum

# Import all verified models
from rcs_models import (
    J20RCSModel, J10CRCSModel, J11BRCSModel, J15RCSModel, J16RCSModel,
    Su35RCSModel, Su57RCSModel, Su30SMRCSModel, MiG31RCSModel, Su34RCSModel,
    H6KRCSModel, F35ARCSModel
)
from j20_radar_model import J20RadarModel
from pl15_targeting_model import PL15TargetingModel
from df17_hgv_model import DF17HGVModel
from china_2025_parade_models import (
    DF61ICBMModel, DF5CICBMModel, DF31ICBMModel, JL3SLBMModel,
    YJ15HypersonicModel, YJ17HypersonicModel, YJ19HypersonicModel, YJ20HypersonicModel,
    JingleiJL1ALBMModel, H6NBomberModel, GJ11StealthUCAVModel,
    WingLoongUAVModel, RainbowUAVModel, LoyalWingmanDroneModel, AJX002UUVModel,
    RoboticWolvesUGVModel, ArmedGroundDroneModel, MineClearingRobotModel,
    DataSpectrumMonitoringModel, SignalJammingVehicleModel, EMReconnaissanceVehicleModel,
    NetworkNodeVehicleModel, UAVDataRelayModel, HQ9CSAMModel, HQ11SAMModel,
    HQ16CSAMModel, HQ19ABMModel, HQ20SAMModel, LY1LaserShipModel, LY1LaserTruckModel,
    Type100VehicleModel, HHQ9CNavalSAMModel, HQ10PointDefenseModel
)
from type052d_model import Type052DModel, Type052DVariant


class ContractorType(Enum):
    """Defense contractor classification"""
    CHINESE_AVIATION = "chinese_aviation"
    CHINESE_MISSILE = "chinese_missile"
    CHINESE_SPACE = "chinese_space"
    CHINESE_ELECTRONICS = "chinese_electronics"
    CHINESE_GROUND_SYSTEMS = "chinese_ground_systems"
    CHINESE_SHIPBUILDING = "chinese_shipbuilding"
    CHINESE_NAVAL_WEAPONS = "chinese_naval_weapons"
    CHINESE_NAVAL = "chinese_naval"
    RUSSIAN_AVIATION = "russian_aviation"
    RUSSIAN_AIR_DEFENSE = "russian_air_defense"
    US_AVIATION = "us_aviation"
    US_NAVAL = "us_naval"


@dataclass
class DefenseContractor:
    """Defense contractor organization"""
    name: str
    full_name: str
    country: str
    contractor_type: ContractorType
    established: int
    specialization: str
    operational_systems: List[str]
    confidence: float  # Overall confidence in contractor models (0.0-1.0)


@dataclass
class ContractorModel:
    """Model associated with a defense contractor"""
    model_name: str
    contractor: str
    platform_name: str
    model_class: Type
    fielded_date: int
    confidence: float
    classification: str
    integration_level: str  # "platform", "weapon", "sensor", "system"


class DefenseContractorRegistry:
    """
    Registry of defense contractors and their associated pretrained models.
    Integrates with CAD framework for kill chain analysis.
    """

    def __init__(self):
        """Initialize contractor registry"""
        self.contractors = self._initialize_contractors()
        self.models = self._initialize_models()

    def _initialize_contractors(self) -> Dict[str, DefenseContractor]:
        """Initialize defense contractor database"""
        contractors = {}

        # CHINESE CONTRACTORS
        contractors["AVIC"] = DefenseContractor(
            name="AVIC",
            full_name="Aviation Industry Corporation of China",
            country="China",
            contractor_type=ContractorType.CHINESE_AVIATION,
            established=2008,
            specialization="Fighter aircraft, bombers, trainers, UCAVs",
            operational_systems=["J-20", "J-10C", "J-11B", "J-15", "J-16", "H-6K", "H-6N", "GJ-11", "Wing Loong", "Loyal Wingman"],
            confidence=0.60
        )

        contractors["CASIC"] = DefenseContractor(
            name="CASIC",
            full_name="China Aerospace Science and Industry Corporation",
            country="China",
            contractor_type=ContractorType.CHINESE_MISSILE,
            established=1999,
            specialization="Air-to-air missiles, ballistic missiles, cruise missiles, SAMs",
            operational_systems=["PL-15", "PL-21", "PL-10", "DF-17", "DF-21D", "YJ-15", "YJ-17", "YJ-19", "YJ-20",
                               "Jinglei JL-1", "HQ-9C", "HQ-11", "HQ-16C", "HQ-19", "HQ-20", "HHQ-9C", "HQ-10"],
            confidence=0.55
        )

        contractors["CASC"] = DefenseContractor(
            name="CASC",
            full_name="China Aerospace Science and Technology Corporation",
            country="China",
            contractor_type=ContractorType.CHINESE_SPACE,
            established=1999,
            specialization="Satellites, launch vehicles, strategic missiles",
            operational_systems=["Beidou-3", "DF-26", "DF-61", "DF-5C", "DF-31", "JL-3", "Long March"],
            confidence=0.65
        )

        contractors["CETC"] = DefenseContractor(
            name="CETC",
            full_name="China Electronics Technology Group Corporation",
            country="China",
            contractor_type=ContractorType.CHINESE_ELECTRONICS,
            established=2002,
            specialization="Electronics, radars, EW systems, C4ISR",
            operational_systems=["ISF EW Vehicles", "Data Spectrum Monitoring", "Signal Jamming", "Network Nodes"],
            confidence=0.40
        )

        contractors["NORINCO"] = DefenseContractor(
            name="NORINCO",
            full_name="China North Industries Corporation",
            country="China",
            contractor_type=ContractorType.CHINESE_GROUND_SYSTEMS,
            established=1999,
            specialization="Ground vehicles, artillery, unmanned ground systems",
            operational_systems=["Type-100", "Robotic Wolves", "Armed UGVs", "Mine-Clearing Robots"],
            confidence=0.45
        )

        contractors["CSSC"] = DefenseContractor(
            name="CSSC",
            full_name="China State Shipbuilding Corporation",
            country="China",
            contractor_type=ContractorType.CHINESE_SHIPBUILDING,
            established=2019,
            specialization="Naval vessels, unmanned maritime systems",
            operational_systems=["Type 052D", "Type 055 Destroyer", "Type 003 Carrier", "AJX002 UUV"],
            confidence=0.50
        )

        contractors["CSIC"] = DefenseContractor(
            name="CSIC",
            full_name="China Shipbuilding Industry Corporation",
            country="China",
            contractor_type=ContractorType.CHINESE_NAVAL_WEAPONS,
            established=1999,
            specialization="Naval weapons, directed energy weapons",
            operational_systems=["LY-1 Laser", "Torpedo Systems", "Naval Guns"],
            confidence=0.40
        )

        # RUSSIAN CONTRACTORS
        contractors["Sukhoi"] = DefenseContractor(
            name="Sukhoi",
            full_name="JSC Sukhoi Company",
            country="Russia",
            contractor_type=ContractorType.RUSSIAN_AVIATION,
            established=1939,
            specialization="Fighter aircraft, strike aircraft",
            operational_systems=["Su-35", "Su-57", "Su-30SM", "Su-34"],
            confidence=0.65
        )

        contractors["MiG"] = DefenseContractor(
            name="MiG",
            full_name="Russian Aircraft Corporation MiG",
            country="Russia",
            contractor_type=ContractorType.RUSSIAN_AVIATION,
            established=1939,
            specialization="Interceptors, multirole fighters",
            operational_systems=["MiG-31", "MiG-29"],
            confidence=0.70
        )

        contractors["Almaz"] = DefenseContractor(
            name="Almaz",
            full_name="JSC Almaz-Antey",
            country="Russia",
            contractor_type=ContractorType.RUSSIAN_AIR_DEFENSE,
            established=2002,
            specialization="Air defense systems, anti-ballistic missiles",
            operational_systems=["S-400", "S-300PMU-2", "S-500"],
            confidence=0.70
        )

        # US CONTRACTORS (for American Integrated Link)
        contractors["Lockheed_Martin"] = DefenseContractor(
            name="Lockheed_Martin",
            full_name="Lockheed Martin Corporation",
            country="USA",
            contractor_type=ContractorType.US_AVIATION,
            established=1995,
            specialization="5th-gen fighters, missiles, hypersonics, strategic systems",
            operational_systems=["F-35", "F-22", "F-16", "LRHW", "THAAD", "AIM-260",
                               "Trident II D5", "Sentinel ICBM"],
            confidence=0.75
        )

        contractors["Raytheon"] = DefenseContractor(
            name="Raytheon",
            full_name="Raytheon Technologies (RTX)",
            country="USA",
            contractor_type=ContractorType.US_AVIATION,
            established=2020,
            specialization="Missiles, air defense, sensors, EW systems",
            operational_systems=["AIM-120D", "AIM-9X", "SM-6", "SM-3", "SM-2",
                               "ESSM", "Patriot PAC-3", "Tomahawk", "HACM"],
            confidence=0.80
        )

        contractors["Northrop_Grumman"] = DefenseContractor(
            name="Northrop_Grumman",
            full_name="Northrop Grumman Corporation",
            country="USA",
            contractor_type=ContractorType.US_AVIATION,
            established=1994,
            specialization="Stealth bombers, ICBMs, space systems, unmanned",
            operational_systems=["B-21 Raider", "B-2 Spirit", "Sentinel ICBM",
                               "RQ-180", "MQ-4C Triton", "E-2D Hawkeye"],
            confidence=0.70
        )

        contractors["Boeing"] = DefenseContractor(
            name="Boeing",
            full_name="The Boeing Company",
            country="USA",
            contractor_type=ContractorType.US_AVIATION,
            established=1916,
            specialization="Aircraft, naval systems, unmanned, missile defense",
            operational_systems=["F/A-18E/F", "EA-18G", "MQ-25", "P-8A Poseidon",
                               "KC-46", "E-7 Wedgetail", "Ground-Based Midcourse Defense"],
            confidence=0.80
        )

        contractors["General_Dynamics"] = DefenseContractor(
            name="General_Dynamics",
            full_name="General Dynamics Corporation",
            country="USA",
            contractor_type=ContractorType.US_NAVAL,
            established=1952,
            specialization="Submarines, surface combatants, ground vehicles, IT",
            operational_systems=["Virginia-class SSN", "Columbia-class SSBN",
                               "DDG-51 Flight III", "DDG-1000 Zumwalt",
                               "M1 Abrams", "Stryker"],
            confidence=0.75
        )

        contractors["Huntington_Ingalls"] = DefenseContractor(
            name="Huntington_Ingalls",
            full_name="Huntington Ingalls Industries",
            country="USA",
            contractor_type=ContractorType.US_NAVAL,
            established=2011,
            specialization="Aircraft carriers, amphibious ships, surface combatants",
            operational_systems=["Ford-class CVN", "America-class LHA",
                               "San Antonio-class LPD", "DDG-51 construction"],
            confidence=0.75
        )

        contractors["L3Harris"] = DefenseContractor(
            name="L3Harris",
            full_name="L3Harris Technologies",
            country="USA",
            contractor_type=ContractorType.US_AVIATION,
            established=2019,
            specialization="Communications, EW, ISR, space systems",
            operational_systems=["Link 16 terminals", "MADL", "TTNT",
                               "GPS payloads", "EW pods", "Radios"],
            confidence=0.70
        )

        contractors["General_Atomics"] = DefenseContractor(
            name="General_Atomics",
            full_name="General Atomics Aeronautical Systems",
            country="USA",
            contractor_type=ContractorType.US_AVIATION,
            established=1955,
            specialization="Unmanned aircraft, directed energy, nuclear technology",
            operational_systems=["MQ-9 Reaper", "MQ-1C Gray Eagle",
                               "Avenger (Predator C)", "HELIOS laser"],
            confidence=0.75
        )

        return contractors

    def _initialize_models(self) -> Dict[str, ContractorModel]:
        """Initialize contractor model associations"""
        models = {}

        # AVIC MODELS (Chinese Aviation)
        models["J20"] = ContractorModel(
            model_name="J20RCSModel",
            contractor="AVIC",
            platform_name="J-20 Mighty Dragon",
            model_class=J20RCSModel,
            fielded_date=2017,
            confidence=0.50,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["J10C"] = ContractorModel(
            model_name="J10CRCSModel",
            contractor="AVIC",
            platform_name="J-10C Vigorous Dragon",
            model_class=J10CRCSModel,
            fielded_date=2015,
            confidence=0.55,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["J11B"] = ContractorModel(
            model_name="J11BRCSModel",
            contractor="AVIC",
            platform_name="J-11B Flanker",
            model_class=J11BRCSModel,
            fielded_date=2007,
            confidence=0.60,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["J15"] = ContractorModel(
            model_name="J15RCSModel",
            contractor="AVIC",
            platform_name="J-15 Flying Shark",
            model_class=J15RCSModel,
            fielded_date=2013,
            confidence=0.55,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["J16"] = ContractorModel(
            model_name="J16RCSModel",
            contractor="AVIC",
            platform_name="J-16 Red Eagle",
            model_class=J16RCSModel,
            fielded_date=2015,
            confidence=0.55,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["H6K"] = ContractorModel(
            model_name="H6KRCSModel",
            contractor="AVIC",
            platform_name="H-6K Badger",
            model_class=H6KRCSModel,
            fielded_date=2009,
            confidence=0.65,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        # CASIC MODELS (Chinese Missiles)
        models["PL15"] = ContractorModel(
            model_name="PL15TargetingModel",
            contractor="CASIC",
            platform_name="PL-15 BVR AAM",
            model_class=PL15TargetingModel,
            fielded_date=2018,
            confidence=0.60,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["DF17"] = ContractorModel(
            model_name="DF17HGVModel",
            contractor="CASIC",
            platform_name="DF-17 Hypersonic Glide Vehicle",
            model_class=DF17HGVModel,
            fielded_date=2019,
            confidence=0.55,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        # CSSC MODELS (Chinese Naval)
        models["Type052D"] = ContractorModel(
            model_name="Type052DModel",
            contractor="CSSC",
            platform_name="Type 052D Destroyer (Luyang III)",
            model_class=Type052DModel,
            fielded_date=2014,
            confidence=0.60,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["Type052D_Enhanced"] = ContractorModel(
            model_name="Type052DModel_Enhanced",
            contractor="CSSC",
            platform_name="Type 052D Destroyer Enhanced (Loudi)",
            model_class=Type052DModel,
            fielded_date=2026,
            confidence=0.60,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        # SUKHOI MODELS (Russian Aviation)
        models["Su35"] = ContractorModel(
            model_name="Su35RCSModel",
            contractor="Sukhoi",
            platform_name="Su-35 Flanker-E",
            model_class=Su35RCSModel,
            fielded_date=2014,
            confidence=0.65,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["Su57"] = ContractorModel(
            model_name="Su57RCSModel",
            contractor="Sukhoi",
            platform_name="Su-57 Felon",
            model_class=Su57RCSModel,
            fielded_date=2020,
            confidence=0.50,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["Su30SM"] = ContractorModel(
            model_name="Su30SMRCSModel",
            contractor="Sukhoi",
            platform_name="Su-30SM Flanker-H",
            model_class=Su30SMRCSModel,
            fielded_date=2012,
            confidence=0.65,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["Su34"] = ContractorModel(
            model_name="Su34RCSModel",
            contractor="Sukhoi",
            platform_name="Su-34 Fullback",
            model_class=Su34RCSModel,
            fielded_date=2014,
            confidence=0.65,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        # MIG MODELS (Russian Aviation)
        models["MiG31"] = ContractorModel(
            model_name="MiG31RCSModel",
            contractor="MiG",
            platform_name="MiG-31 Foxhound",
            model_class=MiG31RCSModel,
            fielded_date=2011,
            confidence=0.70,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        # =====================================================================
        # CHINA 2025 MILITARY PARADE SYSTEMS
        # =====================================================================

        # CASC MODELS (Strategic Missiles)
        models["DF61"] = ContractorModel(
            model_name="DF61ICBMModel",
            contractor="CASC",
            platform_name="DF-61 ICBM",
            model_class=DF61ICBMModel,
            fielded_date=2025,
            confidence=0.45,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["DF5C"] = ContractorModel(
            model_name="DF5CICBMModel",
            contractor="CASC",
            platform_name="DF-5C ICBM",
            model_class=DF5CICBMModel,
            fielded_date=2015,
            confidence=0.60,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["DF31"] = ContractorModel(
            model_name="DF31ICBMModel",
            contractor="CASC",
            platform_name="DF-31 ICBM",
            model_class=DF31ICBMModel,
            fielded_date=2006,
            confidence=0.65,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["JL3"] = ContractorModel(
            model_name="JL3SLBMModel",
            contractor="CASC",
            platform_name="JL-3 SLBM",
            model_class=JL3SLBMModel,
            fielded_date=2021,
            confidence=0.50,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["Rainbow"] = ContractorModel(
            model_name="RainbowUAVModel",
            contractor="CASC",
            platform_name="Rainbow (CH-series) UAV",
            model_class=RainbowUAVModel,
            fielded_date=2010,
            confidence=0.60,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["UAVDataRelay"] = ContractorModel(
            model_name="UAVDataRelayModel",
            contractor="CASC",
            platform_name="UAV Data Relay System",
            model_class=UAVDataRelayModel,
            fielded_date=2024,
            confidence=0.40,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="system"
        )

        # CASIC MODELS (Hypersonic & Air Defense)
        models["YJ15"] = ContractorModel(
            model_name="YJ15HypersonicModel",
            contractor="CASIC",
            platform_name="YJ-15 Hypersonic ASM",
            model_class=YJ15HypersonicModel,
            fielded_date=2020,
            confidence=0.50,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["YJ17"] = ContractorModel(
            model_name="YJ17HypersonicModel",
            contractor="CASIC",
            platform_name="YJ-17 Hypersonic ASM",
            model_class=YJ17HypersonicModel,
            fielded_date=2022,
            confidence=0.45,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["YJ19"] = ContractorModel(
            model_name="YJ19HypersonicModel",
            contractor="CASIC",
            platform_name="YJ-19 Hypersonic ASM",
            model_class=YJ19HypersonicModel,
            fielded_date=2023,
            confidence=0.40,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["YJ20"] = ContractorModel(
            model_name="YJ20HypersonicModel",
            contractor="CASIC",
            platform_name="YJ-20 Hypersonic ASM",
            model_class=YJ20HypersonicModel,
            fielded_date=2024,
            confidence=0.35,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["JingleiJL1"] = ContractorModel(
            model_name="JingleiJL1ALBMModel",
            contractor="CASIC",
            platform_name="Jinglei JL-1 ALBM",
            model_class=JingleiJL1ALBMModel,
            fielded_date=2024,
            confidence=0.40,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["HQ9C"] = ContractorModel(
            model_name="HQ9CSAMModel",
            contractor="CASIC",
            platform_name="HQ-9C Long-Range SAM",
            model_class=HQ9CSAMModel,
            fielded_date=2020,
            confidence=0.55,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["HQ11"] = ContractorModel(
            model_name="HQ11SAMModel",
            contractor="CASIC",
            platform_name="HQ-11 Short-Range SAM",
            model_class=HQ11SAMModel,
            fielded_date=2015,
            confidence=0.60,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["HQ16C"] = ContractorModel(
            model_name="HQ16CSAMModel",
            contractor="CASIC",
            platform_name="HQ-16C Medium-Range SAM",
            model_class=HQ16CSAMModel,
            fielded_date=2019,
            confidence=0.55,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["HQ19"] = ContractorModel(
            model_name="HQ19ABMModel",
            contractor="CASIC",
            platform_name="HQ-19 ABM System",
            model_class=HQ19ABMModel,
            fielded_date=2017,
            confidence=0.45,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["HQ20"] = ContractorModel(
            model_name="HQ20SAMModel",
            contractor="CASIC",
            platform_name="HQ-20 Long-Range SAM",
            model_class=HQ20SAMModel,
            fielded_date=2023,
            confidence=0.40,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["HHQ9C"] = ContractorModel(
            model_name="HHQ9CNavalSAMModel",
            contractor="CASIC",
            platform_name="HHQ-9C Naval SAM",
            model_class=HHQ9CNavalSAMModel,
            fielded_date=2020,
            confidence=0.55,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["HQ10"] = ContractorModel(
            model_name="HQ10PointDefenseModel",
            contractor="CASIC",
            platform_name="HQ-10 Point Defense",
            model_class=HQ10PointDefenseModel,
            fielded_date=2012,
            confidence=0.60,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        # AVIC MODELS (Aircraft & UCAVs - 2025 Parade)
        models["H6N"] = ContractorModel(
            model_name="H6NBomberModel",
            contractor="AVIC",
            platform_name="H-6N Strategic Bomber",
            model_class=H6NBomberModel,
            fielded_date=2019,
            confidence=0.55,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["GJ11"] = ContractorModel(
            model_name="GJ11StealthUCAVModel",
            contractor="AVIC",
            platform_name="GJ-11 Stealth UCAV",
            model_class=GJ11StealthUCAVModel,
            fielded_date=2019,
            confidence=0.50,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["WingLoong"] = ContractorModel(
            model_name="WingLoongUAVModel",
            contractor="AVIC",
            platform_name="Wing Loong MALE UAV",
            model_class=WingLoongUAVModel,
            fielded_date=2015,
            confidence=0.60,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["LoyalWingman"] = ContractorModel(
            model_name="LoyalWingmanDroneModel",
            contractor="AVIC",
            platform_name="Loyal Wingman Drone",
            model_class=LoyalWingmanDroneModel,
            fielded_date=2024,
            confidence=0.35,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        # CETC MODELS (ISF / EW Systems)
        models["DataSpectrumMonitoring"] = ContractorModel(
            model_name="DataSpectrumMonitoringModel",
            contractor="CETC",
            platform_name="Data Spectrum Monitoring Vehicle",
            model_class=DataSpectrumMonitoringModel,
            fielded_date=2024,
            confidence=0.35,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="system"
        )

        models["SignalJammingVehicle"] = ContractorModel(
            model_name="SignalJammingVehicleModel",
            contractor="CETC",
            platform_name="Signal Jamming Vehicle",
            model_class=SignalJammingVehicleModel,
            fielded_date=2024,
            confidence=0.35,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="system"
        )

        models["EMReconnaissanceVehicle"] = ContractorModel(
            model_name="EMReconnaissanceVehicleModel",
            contractor="CETC",
            platform_name="EM Reconnaissance Vehicle",
            model_class=EMReconnaissanceVehicleModel,
            fielded_date=2024,
            confidence=0.35,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="system"
        )

        models["NetworkNodeVehicle"] = ContractorModel(
            model_name="NetworkNodeVehicleModel",
            contractor="CETC",
            platform_name="Network Node Vehicle",
            model_class=NetworkNodeVehicleModel,
            fielded_date=2024,
            confidence=0.35,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="system"
        )

        # NORINCO MODELS (Ground Systems)
        models["RoboticWolves"] = ContractorModel(
            model_name="RoboticWolvesUGVModel",
            contractor="NORINCO",
            platform_name="Robotic Wolves UGV",
            model_class=RoboticWolvesUGVModel,
            fielded_date=2023,
            confidence=0.40,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["ArmedGroundDrone"] = ContractorModel(
            model_name="ArmedGroundDroneModel",
            contractor="NORINCO",
            platform_name="Armed Ground Drone",
            model_class=ArmedGroundDroneModel,
            fielded_date=2024,
            confidence=0.35,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["MineClearingRobot"] = ContractorModel(
            model_name="MineClearingRobotModel",
            contractor="NORINCO",
            platform_name="Mine-Clearing Robot",
            model_class=MineClearingRobotModel,
            fielded_date=2022,
            confidence=0.45,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        models["Type100"] = ContractorModel(
            model_name="Type100VehicleModel",
            contractor="NORINCO",
            platform_name="Type-100 IFV/APC",
            model_class=Type100VehicleModel,
            fielded_date=2023,
            confidence=0.45,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        # CSSC MODELS (Unmanned Maritime)
        models["AJX002"] = ContractorModel(
            model_name="AJX002UUVModel",
            contractor="CSSC",
            platform_name="AJX002 Giant UUV",
            model_class=AJX002UUVModel,
            fielded_date=2024,
            confidence=0.30,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        # CSIC MODELS (Directed Energy Weapons)
        models["LY1Ship"] = ContractorModel(
            model_name="LY1LaserShipModel",
            contractor="CSIC",
            platform_name="LY-1 Laser (Shipborne)",
            model_class=LY1LaserShipModel,
            fielded_date=2024,
            confidence=0.35,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        models["LY1Truck"] = ContractorModel(
            model_name="LY1LaserTruckModel",
            contractor="CSIC",
            platform_name="LY-1 Laser (Truck)",
            model_class=LY1LaserTruckModel,
            fielded_date=2024,
            confidence=0.35,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="weapon"
        )

        # US MODELS (for comparison)
        models["F35A"] = ContractorModel(
            model_name="F35ARCSModel",
            contractor="Lockheed_Martin",
            platform_name="F-35A Lightning II",
            model_class=F35ARCSModel,
            fielded_date=2015,
            confidence=0.55,
            classification="UNCLASSIFIED // PUBLIC RELEASE",
            integration_level="platform"
        )

        return models

    def get_contractor(self, contractor_name: str) -> Optional[DefenseContractor]:
        """Get contractor by name"""
        return self.contractors.get(contractor_name)

    def get_model(self, model_id: str) -> Optional[ContractorModel]:
        """Get model by ID"""
        return self.models.get(model_id)

    def get_contractor_models(self, contractor_name: str) -> List[ContractorModel]:
        """Get all models for a contractor"""
        return [model for model in self.models.values()
                if model.contractor == contractor_name]

    def get_models_by_country(self, country: str) -> List[ContractorModel]:
        """Get all models for a country"""
        contractor_names = [c.name for c in self.contractors.values()
                           if c.country == country]
        return [model for model in self.models.values()
                if model.contractor in contractor_names]

    def get_chinese_integrated_kill_chain_models(self) -> Dict[str, ContractorModel]:
        """
        Get models for Chinese Integrated Kill Chain Architecture.

        Returns models for:
        - J-20 fighter (AVIC)
        - PL-15 missile (CASIC)
        - Beidou navigation (CASC)
        - KJ-500 AWACS (AVIC)
        """
        return {
            "shooter": self.models["J20"],
            "weapon": self.models["PL15"],
            # Note: KJ-500 and Beidou models would be added here when available
        }

    def get_russian_integrated_air_defense_models(self) -> Dict[str, ContractorModel]:
        """
        Get models for Russian Integrated Air Defense System.

        Returns models for:
        - Su-35/Su-57 fighters (Sukhoi)
        - MiG-31 interceptors (MiG)
        - S-400/S-300 SAMs (Almaz)
        """
        return {
            "air_superiority": self.models["Su35"],
            "stealth_fighter": self.models["Su57"],
            "interceptor": self.models["MiG31"],
            # Note: S-400/S-300 models would be added here when available
        }

    def get_american_integrated_link_models(self) -> Dict[str, ContractorModel]:
        """
        Get models for American Integrated Link (AIL) Architecture.

        Returns models for:
        - F-35 Lightning II (Lockheed Martin) - Primary sensor node, shooter
        - F-22 Raptor (Lockheed Martin) - Air superiority, sensor
        - E-7 Wedgetail (Boeing) - Battle management, AWACS
        - DDG-51 Flight III (General Dynamics) - AEGIS air defense
        - AIM-260 JATM (Lockheed Martin) - Long-range AAM
        - SM-6 (Raytheon) - Multi-role naval SAM
        - THAAD (Lockheed Martin) - Terminal BMD

        Platform roles in AIL:
        - Any-sensor-any-shooter integration
        - AWACS-to-weapon backup guidance (AWW-13)
        - CEC/NIFC-CA engage-on-remote
        - Multi-datalink fusion (TTNT, MADL, Link 16, CEC)
        """
        ail_models = {
            "primary_sensor": self.models.get("F35A"),
            # Additional AIL models would be added here as they are implemented
        }

        # Filter out None values
        return {k: v for k, v in ail_models.items() if v is not None}

    def get_all_ail_compatible_systems(self) -> List[str]:
        """
        Get list of all American Integrated Link compatible systems.

        These systems can participate in the any-sensor-any-shooter
        kill chain architecture defined in AMERICAN_INTEGRATED_LINK.md
        """
        return [
            # Airborne platforms
            "F-35A/B/C Lightning II",
            "F-22A Raptor",
            "E-7 Wedgetail",
            "B-21 Raider",
            "CCA (Collaborative Combat Aircraft)",
            "MQ-25A Stingray",
            "RQ-180",
            "B-52H Stratofortress",
            # Naval platforms
            "DDG-51 Arleigh Burke Flight III",
            "DDG-1000 Zumwalt",
            "CG-47 Ticonderoga",
            "CVN-78 Ford-class",
            "Virginia Block V SSN",
            "Ohio-class SSGN",
            "AEGIS Ashore",
            # Ground systems
            "THAAD",
            "Patriot PAC-3 MSE",
            "Typhon",
            "HIMARS-ER",
            # Weapons
            "AIM-260 JATM",
            "AIM-120D AMRAAM",
            "AIM-9X Block III",
            "SM-6 Block IB",
            "SM-3 Block IIA",
            "ESSM Block 2",
            "THAAD Interceptor",
            "PAC-3 MSE",
            "Tomahawk Block V",
            "LRHW Dark Eagle",
            "CPS",
            # Datalinks
            "TTNT",
            "MADL",
            "IFDL",
            "Link 16",
            "CDL",
            "CEC",
            "AWW-13",
        ]

    def generate_contractor_report(self) -> str:
        """Generate comprehensive contractor and model report"""
        report = []
        report.append("=" * 80)
        report.append("DEFENSE CONTRACTOR MODEL REGISTRY")
        report.append("=" * 80)
        report.append("")

        # Group by country
        for country in ["China", "Russia", "USA"]:
            country_contractors = [c for c in self.contractors.values()
                                  if c.country == country]
            if not country_contractors:
                continue

            report.append(f"\n{country} DEFENSE CONTRACTORS")
            report.append("-" * 80)

            for contractor in country_contractors:
                report.append(f"\n{contractor.name} ({contractor.full_name})")
                report.append(f"  Established: {contractor.established}")
                report.append(f"  Specialization: {contractor.specialization}")
                report.append(f"  Confidence: {contractor.confidence:.0%}")

                # Get models for this contractor
                contractor_models = self.get_contractor_models(contractor.name)
                report.append(f"  Operational Systems ({len(contractor_models)} models):")
                for model in contractor_models:
                    report.append(f"    • {model.platform_name} ({model.fielded_date})")
                    report.append(f"      Model: {model.model_name}")
                    report.append(f"      Confidence: {model.confidence:.0%}")
                    report.append(f"      Integration: {model.integration_level}")

        report.append("\n" + "=" * 80)
        report.append(f"TOTAL: {len(self.contractors)} contractors, {len(self.models)} models")
        report.append("=" * 80)
        report.append("\nClassification: UNCLASSIFIED // PUBLIC RELEASE")

        return "\n".join(report)


def main():
    """Demonstration of contractor registry"""
    registry = DefenseContractorRegistry()

    print(registry.generate_contractor_report())

    print("\n\nCHINESE INTEGRATED KILL CHAIN MODELS:")
    print("-" * 80)
    chinese_models = registry.get_chinese_integrated_kill_chain_models()
    for role, model in chinese_models.items():
        print(f"{role.upper()}: {model.platform_name}")
        print(f"  Contractor: {model.contractor}")
        print(f"  Fielded: {model.fielded_date}")
        print(f"  Confidence: {model.confidence:.0%}")
        print()

    print("\n\nRUSSIAN INTEGRATED AIR DEFENSE MODELS:")
    print("-" * 80)
    russian_models = registry.get_russian_integrated_air_defense_models()
    for role, model in russian_models.items():
        print(f"{role.upper()}: {model.platform_name}")
        print(f"  Contractor: {model.contractor}")
        print(f"  Fielded: {model.fielded_date}")
        print(f"  Confidence: {model.confidence:.0%}")
        print()


if __name__ == "__main__":
    main()
