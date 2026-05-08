#!/usr/bin/env python3
"""
LSC-X Armament Systems Model

Physics-based simulation of weapons effectiveness, magazine depth,
and engagement capacity for the Golden Fleet heavy cruiser.

Classification: UNCLASSIFIED // CONCEPTUAL DESIGN
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json


class WeaponStatus(Enum):
    EXISTING = "existing"
    MODIFIED = "modified"
    NEW_INTEGRATION = "new_integration"
    NEW_DEVELOPMENT = "new_development"


@dataclass
class Missile:
    """Missile specifications."""
    name: str
    length_m: float
    diameter_mm: float
    weight_kg: float
    range_km: float
    speed_mach: float
    pk_single: float  # Probability of kill (single shot)
    role: str
    status: WeaponStatus = WeaponStatus.EXISTING


@dataclass
class GunSystem:
    """Gun system specifications."""
    name: str
    caliber_mm: float
    rate_of_fire_rpm: float
    range_km: float
    magazine_capacity: int
    quantity: int
    status: WeaponStatus = WeaponStatus.EXISTING


@dataclass
class DirectedEnergy:
    """Directed energy weapon specifications."""
    name: str
    power_kw: float
    range_cruise_missile_km: float
    range_uav_km: float
    range_fiac_km: float
    quantity: int
    status: WeaponStatus = WeaponStatus.EXISTING


@dataclass
class VLSLoadout:
    """VLS cell allocation."""
    sm6: int = 64
    sm3_iia: int = 16
    sm2: int = 0
    tlam: int = 32
    lrasm: int = 0
    vl_asroc: int = 16
    essm_quad: int = 0  # Each quad pack uses 1 cell


class ArmamentModel:
    """
    Complete armament system model for LSC-X.
    """

    def __init__(self):
        self._init_missiles()
        self._init_guns()
        self._init_directed_energy()
        self._init_vls()
        self._init_new_systems()

    def _init_missiles(self):
        """Initialize missile database."""
        self.missiles = {
            'sm6': Missile(
                name="SM-6 Block IA",
                length_m=6.55, diameter_mm=533, weight_kg=1500,
                range_km=370, speed_mach=3.5, pk_single=0.85,
                role="Extended AAW/ASuW"
            ),
            'sm3_iia': Missile(
                name="SM-3 Block IIA",
                length_m=6.55, diameter_mm=533, weight_kg=1500,
                range_km=2500, speed_mach=15, pk_single=0.85,
                role="BMD Exoatmospheric"
            ),
            'sm2_iiic': Missile(
                name="SM-2 Block IIIC",
                length_m=4.72, diameter_mm=343, weight_kg=708,
                range_km=170, speed_mach=3.5, pk_single=0.80,
                role="Area AAW"
            ),
            'tlam_v': Missile(
                name="TLAM Block V",
                length_m=6.25, diameter_mm=518, weight_kg=1300,
                range_km=1600, speed_mach=0.75, pk_single=0.90,
                role="Land Attack"
            ),
            'lrasm': Missile(
                name="LRASM",
                length_m=4.27, diameter_mm=533, weight_kg=1020,
                range_km=930, speed_mach=0.85, pk_single=0.85,
                role="Anti-Ship"
            ),
            'vl_asroc': Missile(
                name="VL-ASROC",
                length_m=4.85, diameter_mm=343, weight_kg=635,
                range_km=28, speed_mach=1.0, pk_single=0.70,
                role="ASW"
            ),
            'essm_2': Missile(
                name="ESSM Block 2",
                length_m=3.66, diameter_mm=254, weight_kg=280,
                range_km=50, speed_mach=4.0, pk_single=0.80,
                role="Point Defense"
            ),
            'thaad_er': Missile(
                name="THAAD-ER",
                length_m=6.17, diameter_mm=370, weight_kg=900,
                range_km=350, speed_mach=10, pk_single=0.90,
                role="BMD Terminal",
                status=WeaponStatus.NEW_DEVELOPMENT
            ),
            'prsm_4': Missile(
                name="PrSM Increment 4",
                length_m=4.0, diameter_mm=280, weight_kg=500,
                range_km=1000, speed_mach=5, pk_single=0.85,
                role="Anti-Ship/Land Attack",
                status=WeaponStatus.NEW_INTEGRATION
            ),
            'ram_2': Missile(
                name="RAM Block 2",
                length_m=2.79, diameter_mm=127, weight_kg=74,
                range_km=10, speed_mach=2.5, pk_single=0.75,
                role="Point Defense CIWS"
            ),
        }

    def _init_guns(self):
        """Initialize gun systems."""
        self.guns = {
            'ags_m': GunSystem(
                name="155mm AGS-M",
                caliber_mm=155, rate_of_fire_rpm=10,
                range_km=70, magazine_capacity=400, quantity=1,
                status=WeaponStatus.MODIFIED
            ),
            'mk110': GunSystem(
                name="57mm Mk 110",
                caliber_mm=57, rate_of_fire_rpm=220,
                range_km=8.5, magazine_capacity=1000, quantity=2
            ),
            'mk46': GunSystem(
                name="30mm Mk 46 GWS",
                caliber_mm=30, rate_of_fire_rpm=200,
                range_km=2.5, magazine_capacity=500, quantity=4
            ),
            'phalanx': GunSystem(
                name="20mm Phalanx Block 1B",
                caliber_mm=20, rate_of_fire_rpm=4500,
                range_km=1.5, magazine_capacity=1550, quantity=2
            ),
        }

    def _init_directed_energy(self):
        """Initialize directed energy weapons."""
        self.dew = {
            'helios_150': DirectedEnergy(
                name="150 kW HELIOS",
                power_kw=150,
                range_cruise_missile_km=3,
                range_uav_km=5,
                range_fiac_km=2,
                quantity=2
            ),
            'hel_600': DirectedEnergy(
                name="600 kW HEL",
                power_kw=600,
                range_cruise_missile_km=8,
                range_uav_km=15,
                range_fiac_km=5,
                quantity=1,
                status=WeaponStatus.NEW_DEVELOPMENT
            ),
        }

    def _init_vls(self):
        """Initialize VLS configuration."""
        self.mk41_cells = 128
        self.mk57_cells = 32
        self.total_vls = self.mk41_cells + self.mk57_cells

        # Default loadout
        self.loadout = VLSLoadout()

    def _init_new_systems(self):
        """Initialize new systems requiring development."""
        self.new_systems = {
            'thaad_maritime': {
                'name': 'THAAD-ER Maritime (TEM)',
                'development_cost_b': 2.0,
                'timeline_years': 10,
                'risk': 'medium',
                'interceptors': 16,
                'launchers': 2
            },
            'hel_600kw': {
                'name': '600 kW High-Energy Laser',
                'development_cost_b': 1.0,
                'timeline_years': 10,
                'risk': 'medium-high',
                'power_kw': 600
            },
            'prsm_integration': {
                'name': 'PrSM Maritime Integration',
                'development_cost_b': 0.2,
                'timeline_years': 3,
                'risk': 'low',
                'missiles': 16,
                'containers': 4
            },
            'aegis_thaad': {
                'name': 'AEGIS-THAAD Fire Control Integration',
                'development_cost_b': 0.5,
                'timeline_years': 5,
                'risk': 'medium'
            },
            'ags_modification': {
                'name': 'AGS-M Naval Gun Modification',
                'development_cost_b': 0.1,
                'timeline_years': 2,
                'risk': 'low'
            }
        }

    def calculate_salvo_size(self, target_type: str) -> Dict:
        """
        Calculate maximum salvo size by target type.
        """
        salvos = {
            'air_defense': {
                'sm6': min(self.loadout.sm6, 16),
                'essm': min(self.loadout.essm_quad * 4, 32),
                'ram': 22,  # 2 SeaRAM launchers
                'total': 0
            },
            'bmd': {
                'sm3_iia': min(self.loadout.sm3_iia, 8),
                'thaad_er': 4,  # 2 per launcher
                'total': 0
            },
            'anti_ship': {
                'sm6': min(self.loadout.sm6 // 4, 8),  # Dual-mode
                'lrasm': min(self.loadout.lrasm, 8),
                'prsm': 8,
                'total': 0
            },
            'land_attack': {
                'tlam': min(self.loadout.tlam, 16),
                'prsm': 8,
                'total': 0
            },
            'asw': {
                'vl_asroc': min(self.loadout.vl_asroc, 4),
                'mk54_torpedo': 6,
                'total': 0
            }
        }

        for category in salvos:
            salvos[category]['total'] = sum(
                v for k, v in salvos[category].items() if k != 'total'
            )

        return salvos

    def calculate_magazine_depth(self) -> Dict:
        """
        Calculate engagement capacity based on magazine depth.
        """
        # Missiles per engagement (2-shot doctrine)
        missiles_per_engagement = 2

        engagements = {
            'aaw_sm6': self.loadout.sm6 // missiles_per_engagement,
            'aaw_sm2': self.loadout.sm2 // missiles_per_engagement,
            'bmd_sm3': self.loadout.sm3_iia // missiles_per_engagement,
            'bmd_thaad': 16 // missiles_per_engagement,  # Fixed THAAD capacity
            'strike_tlam': self.loadout.tlam,  # Single shot
            'asuw_lrasm': self.loadout.lrasm,  # Single shot
            'asuw_prsm': 16,  # Fixed PrSM capacity
            'asw_asroc': self.loadout.vl_asroc // missiles_per_engagement,
            'point_defense': (self.loadout.essm_quad * 4) // missiles_per_engagement,
        }

        # Gun engagements (rounds per engagement)
        gun_engagements = {
            '155mm': self.guns['ags_m'].magazine_capacity // 10,  # 10 rounds per fire mission
            '57mm': (self.guns['mk110'].magazine_capacity * 2) // 20,  # 20 rounds per engagement
            '30mm': (self.guns['mk46'].magazine_capacity * 4) // 50,  # 50 rounds per engagement
        }

        # DEW engagements (unlimited but power limited)
        dew_engagements = {
            '150kw_laser': 'unlimited (power limited)',
            '600kw_laser': 'unlimited (power limited)'
        }

        return {
            'missile_engagements': engagements,
            'gun_engagements': gun_engagements,
            'dew_engagements': dew_engagements,
            'total_missile_engagements': sum(engagements.values())
        }

    def calculate_layered_defense_pk(self, threat_type: str = 'cruise_missile') -> float:
        """
        Calculate probability of kill for layered defense.

        P(kill) = 1 - Product(1 - Pk_layer) for each layer
        """
        if threat_type == 'cruise_missile':
            layers = [
                ('SM-6', 0.85, 2),       # 2-shot salvo
                ('ESSM', 0.80, 2),       # 2-shot salvo
                ('SeaRAM', 0.75, 2),     # 2 missiles
                ('600kW HEL', 0.70, 1),  # Single engagement
                ('150kW HEL', 0.60, 1),  # Single engagement
                ('Phalanx', 0.50, 1),    # Last ditch
            ]
        elif threat_type == 'ballistic_missile':
            layers = [
                ('SM-3 IIA', 0.85, 2),   # 2-shot salvo
                ('THAAD-ER', 0.90, 2),   # 2-shot salvo
            ]
        elif threat_type == 'uav_swarm':
            layers = [
                ('600kW HEL', 0.85, 10),  # Multiple engagements
                ('150kW HEL', 0.80, 10),
                ('57mm', 0.70, 10),
                ('30mm', 0.60, 10),
            ]
        else:
            return 0.0

        p_survive = 1.0
        for layer_name, pk_single, shots in layers:
            pk_layer = 1 - (1 - pk_single) ** shots
            p_survive *= (1 - pk_layer)

        return round(1 - p_survive, 6)

    def calculate_anti_swarm_capacity(self, swarm_size: int = 100) -> Dict:
        """
        Calculate capacity to defeat drone/missile swarms.
        """
        # DEW engagement rate (engagements per minute)
        hel_600_rate = 6  # 10 second dwell time
        helios_rate = 4   # 15 second dwell time

        # Gun engagement rate
        gun_57mm_rate = 10  # per minute
        gun_30mm_rate = 15  # per minute

        # CIWS
        searam_missiles = 22  # Total SeaRAM
        phalanx_bursts = 10   # Effective bursts per Phalanx

        # Time to defeat swarm (minutes)
        dew_kills_per_min = (1 * hel_600_rate * 0.85) + (2 * helios_rate * 0.70)
        gun_kills_per_min = (2 * gun_57mm_rate * 0.60) + (4 * gun_30mm_rate * 0.50)

        total_rate = dew_kills_per_min + gun_kills_per_min

        time_to_defeat = swarm_size / total_rate if total_rate > 0 else float('inf')

        return {
            'swarm_size': swarm_size,
            'dew_kills_per_minute': round(dew_kills_per_min, 1),
            'gun_kills_per_minute': round(gun_kills_per_min, 1),
            'total_kill_rate_per_minute': round(total_rate, 1),
            'time_to_defeat_minutes': round(time_to_defeat, 1),
            'searam_reserve': searam_missiles,
            'phalanx_bursts': phalanx_bursts * 2,
            'assessment': 'CAPABLE' if time_to_defeat < 10 else 'AT RISK'
        }

    def calculate_strike_range_rings(self) -> Dict:
        """
        Calculate strike range rings for various weapons.
        """
        return {
            'weapons': {
                'TLAM Block V': {'range_km': 1600, 'type': 'land_attack'},
                'PrSM Inc 4': {'range_km': 1000, 'type': 'anti_ship/land'},
                'LRASM': {'range_km': 930, 'type': 'anti_ship'},
                'SM-6 ASuW': {'range_km': 370, 'type': 'anti_ship'},
                '155mm Excalibur': {'range_km': 70, 'type': 'ngfs'},
            },
            'strike_radius_km': 1600,
            'anti_ship_radius_km': 1000,
            'ngfs_radius_km': 70
        }

    def calculate_development_costs(self) -> Dict:
        """
        Calculate total new systems development costs.
        """
        total_cost = sum(s['development_cost_b'] for s in self.new_systems.values())

        return {
            'systems': self.new_systems,
            'total_development_cost_b': total_cost,
            'breakdown': {
                name: data['development_cost_b']
                for name, data in self.new_systems.items()
            }
        }

    def calculate_total_weight(self) -> Dict:
        """
        Calculate total armament weight.
        """
        # Missile weights
        missile_weights = {
            'SM-6': self.loadout.sm6 * self.missiles['sm6'].weight_kg,
            'SM-3 IIA': self.loadout.sm3_iia * self.missiles['sm3_iia'].weight_kg,
            'TLAM': self.loadout.tlam * self.missiles['tlam_v'].weight_kg,
            'VL-ASROC': self.loadout.vl_asroc * self.missiles['vl_asroc'].weight_kg,
            'THAAD-ER': 16 * self.missiles['thaad_er'].weight_kg,
            'PrSM': 16 * self.missiles['prsm_4'].weight_kg,
            'RAM': 22 * self.missiles['ram_2'].weight_kg,
        }

        # VLS structure weight
        vls_structure = {
            'Mk 41 (128 cells)': 180000,
            'Mk 57 (32 cells)': 65000,
        }

        # Gun systems
        gun_weights = {
            '155mm AGS-M': 95000,
            '57mm Mk 110 (2)': 14000,
            '30mm Mk 46 (4)': 6000,
            'Phalanx (2)': 12000,
            'SeaRAM (2)': 12000,
        }

        # DEW
        dew_weights = {
            '600kW HEL': 35000,
            '150kW HELIOS (2)': 22000,
        }

        # Support systems
        support_weights = {
            'THAAD Launchers (2)': 45000,
            'PrSM Containers (4)': 32000,
            'Mk 32 SVTT (2)': 1500,
            'Decoys/EW': 8000,
            'Fire Control': 25000,
            'Cabling': 40000,
        }

        total_missiles = sum(missile_weights.values())
        total_structure = sum(vls_structure.values())
        total_guns = sum(gun_weights.values())
        total_dew = sum(dew_weights.values())
        total_support = sum(support_weights.values())

        return {
            'missile_weights_kg': missile_weights,
            'vls_structure_kg': vls_structure,
            'gun_weights_kg': gun_weights,
            'dew_weights_kg': dew_weights,
            'support_weights_kg': support_weights,
            'totals': {
                'missiles': total_missiles,
                'vls_structure': total_structure,
                'guns': total_guns,
                'dew': total_dew,
                'support': total_support,
                'grand_total_kg': total_missiles + total_structure + total_guns + total_dew + total_support,
                'grand_total_tons': round((total_missiles + total_structure + total_guns + total_dew + total_support) / 1000, 1)
            }
        }

    def generate_report(self) -> str:
        """Generate armament capability report."""
        salvos = self.calculate_salvo_size('all')
        magazine = self.calculate_magazine_depth()
        swarm = self.calculate_anti_swarm_capacity(100)
        strike = self.calculate_strike_range_rings()
        costs = self.calculate_development_costs()
        weight = self.calculate_total_weight()

        report = f"""
LSC-X ARMAMENT CAPABILITY REPORT
================================

VLS CONFIGURATION
-----------------
Mk 41 Strike-Length: {self.mk41_cells} cells
Mk 57 Peripheral: {self.mk57_cells} cells
Total VLS: {self.total_vls} cells

DEFAULT LOADOUT
---------------
SM-6 Block IA: {self.loadout.sm6}
SM-3 Block IIA: {self.loadout.sm3_iia}
TLAM Block V: {self.loadout.tlam}
VL-ASROC: {self.loadout.vl_asroc}

ADDITIONAL SYSTEMS
------------------
THAAD-ER Interceptors: 16 (2 launchers)
PrSM Increment 4: 16 (4 containers)
SeaRAM: 22 missiles (2 launchers)

MAGAZINE DEPTH (ENGAGEMENTS)
----------------------------
Total Missile Engagements: {magazine['total_missile_engagements']}

LAYERED DEFENSE Pk
------------------
vs Cruise Missile: {self.calculate_layered_defense_pk('cruise_missile'):.2%}
vs Ballistic Missile: {self.calculate_layered_defense_pk('ballistic_missile'):.2%}
vs UAV Swarm: {self.calculate_layered_defense_pk('uav_swarm'):.2%}

ANTI-SWARM CAPACITY
-------------------
Swarm Size: {swarm['swarm_size']} drones
Kill Rate: {swarm['total_kill_rate_per_minute']}/min
Time to Defeat: {swarm['time_to_defeat_minutes']} min
Assessment: {swarm['assessment']}

STRIKE RANGES
-------------
Maximum: {strike['strike_radius_km']} km (TLAM)
Anti-Ship: {strike['anti_ship_radius_km']} km (PrSM)
NGFS: {strike['ngfs_radius_km']} km (155mm)

NEW SYSTEMS DEVELOPMENT
-----------------------
Total Cost: ${costs['total_development_cost_b']:.1f}B
"""
        for name, cost in costs['breakdown'].items():
            report += f"  {name}: ${cost:.1f}B\n"

        report += f"""
ARMAMENT WEIGHT
---------------
Total: {weight['totals']['grand_total_tons']} tons
"""

        return report


def main():
    """Run armament model simulation."""
    model = ArmamentModel()

    print("=" * 60)
    print("LSC-X Armament Systems Model")
    print("=" * 60)

    print(model.generate_report())

    # Export structured data
    output = {
        'vls_cells': {
            'mk41': model.mk41_cells,
            'mk57': model.mk57_cells,
            'total': model.total_vls
        },
        'loadout': model.loadout.__dict__,
        'salvo_capacity': model.calculate_salvo_size('all'),
        'magazine_depth': model.calculate_magazine_depth(),
        'layered_pk': {
            'cruise_missile': model.calculate_layered_defense_pk('cruise_missile'),
            'ballistic_missile': model.calculate_layered_defense_pk('ballistic_missile'),
            'uav_swarm': model.calculate_layered_defense_pk('uav_swarm')
        },
        'anti_swarm': model.calculate_anti_swarm_capacity(100),
        'strike_ranges': model.calculate_strike_range_rings(),
        'development_costs': model.calculate_development_costs(),
        'weight': model.calculate_total_weight()
    }

    print("\nStructured Output (JSON):")
    print("-" * 40)
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
