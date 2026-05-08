#!/usr/bin/env python3
"""
Unit tests for LSC-X Armament Systems Model.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from armament_model import (
    ArmamentModel,
    Missile,
    GunSystem,
    DirectedEnergy,
    VLSLoadout,
    WeaponStatus
)


class TestMissileSpecifications:
    """Test missile data validity."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_sm6_specifications(self, model):
        """SM-6 should have valid specifications."""
        sm6 = model.missiles['sm6']
        assert sm6.range_km >= 300
        assert sm6.speed_mach >= 3.0
        assert 0.7 <= sm6.pk_single <= 0.95

    def test_sm3_bmd_capability(self, model):
        """SM-3 should have exo-atmospheric BMD range."""
        sm3 = model.missiles['sm3_iia']
        assert sm3.range_km >= 2000  # Exo-atmospheric
        assert sm3.speed_mach >= 10

    def test_thaad_er_is_new_development(self, model):
        """THAAD-ER should be marked as new development."""
        thaad = model.missiles['thaad_er']
        assert thaad.status == WeaponStatus.NEW_DEVELOPMENT
        assert thaad.range_km >= 300

    def test_prsm_integration_status(self, model):
        """PrSM should be marked as new integration."""
        prsm = model.missiles['prsm_4']
        assert prsm.status == WeaponStatus.NEW_INTEGRATION
        assert prsm.range_km >= 1000


class TestVLSConfiguration:
    """Test VLS cell configuration."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_total_vls_cells(self, model):
        """Should have 160 total VLS cells."""
        assert model.mk41_cells == 128
        assert model.mk57_cells == 32
        assert model.total_vls == 160

    def test_default_loadout_fits(self, model):
        """Default loadout should fit in Mk 41 cells."""
        loadout = model.loadout
        total = (loadout.sm6 + loadout.sm3_iia + loadout.sm2 +
                 loadout.tlam + loadout.lrasm + loadout.vl_asroc +
                 loadout.essm_quad)
        assert total <= model.mk41_cells

    def test_loadout_balanced(self, model):
        """Default loadout should be balanced."""
        loadout = model.loadout
        assert loadout.sm6 >= 32  # AAW
        assert loadout.sm3_iia >= 8  # BMD
        assert loadout.tlam >= 16  # Strike
        assert loadout.vl_asroc >= 8  # ASW


class TestGunSystems:
    """Test gun system specifications."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_ags_modified(self, model):
        """AGS should be marked as modified."""
        ags = model.guns['ags_m']
        assert ags.status == WeaponStatus.MODIFIED
        assert ags.caliber_mm == 155
        assert ags.range_km >= 50

    def test_total_gun_mounts(self, model):
        """Should have multiple gun mounts."""
        total_guns = sum(g.quantity for g in model.guns.values())
        assert total_guns >= 9  # 1 + 2 + 4 + 2

    def test_ciws_coverage(self, model):
        """Should have CIWS coverage."""
        phalanx = model.guns['phalanx']
        assert phalanx.quantity >= 2
        assert phalanx.rate_of_fire_rpm >= 3000


class TestDirectedEnergy:
    """Test directed energy weapons."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_600kw_is_new(self, model):
        """600 kW laser should be new development."""
        hel = model.dew['hel_600']
        assert hel.status == WeaponStatus.NEW_DEVELOPMENT
        assert hel.power_kw == 600

    def test_dew_ranges_scale_with_power(self, model):
        """Higher power DEW should have longer range."""
        hel_600 = model.dew['hel_600']
        helios = model.dew['helios_150']

        assert hel_600.range_cruise_missile_km > helios.range_cruise_missile_km
        assert hel_600.range_uav_km > helios.range_uav_km


class TestLayeredDefense:
    """Test layered defense calculations."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_cruise_missile_pk_very_high(self, model):
        """Layered Pk vs cruise missiles should be very high."""
        pk = model.calculate_layered_defense_pk('cruise_missile')
        assert pk > 0.99  # Near certainty with full layered defense

    def test_bmd_pk_high(self, model):
        """Layered BMD Pk should be high."""
        pk = model.calculate_layered_defense_pk('ballistic_missile')
        assert pk > 0.95  # SM-3 + THAAD layered

    def test_swarm_defense_capable(self, model):
        """Should be capable against drone swarms."""
        pk = model.calculate_layered_defense_pk('uav_swarm')
        assert pk > 0.99


class TestAntiSwarmCapacity:
    """Test anti-swarm calculations."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_can_defeat_100_drone_swarm(self, model):
        """Should defeat 100-drone swarm in reasonable time."""
        result = model.calculate_anti_swarm_capacity(100)
        assert result['time_to_defeat_minutes'] < 15
        assert result['assessment'] in ['CAPABLE', 'AT RISK']

    def test_kill_rate_positive(self, model):
        """Kill rate should be positive."""
        result = model.calculate_anti_swarm_capacity(50)
        assert result['total_kill_rate_per_minute'] > 0
        assert result['dew_kills_per_minute'] > 0
        assert result['gun_kills_per_minute'] > 0


class TestMagazineDepth:
    """Test magazine depth calculations."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_total_engagements(self, model):
        """Should have significant engagement capacity."""
        depth = model.calculate_magazine_depth()
        assert depth['total_missile_engagements'] >= 50

    def test_gun_engagements(self, model):
        """Gun engagement capacity should be significant."""
        depth = model.calculate_magazine_depth()
        assert depth['gun_engagements']['155mm'] >= 30
        assert depth['gun_engagements']['57mm'] >= 50


class TestStrikeRanges:
    """Test strike range calculations."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_max_strike_range(self, model):
        """Maximum strike range should be TLAM range."""
        ranges = model.calculate_strike_range_rings()
        assert ranges['strike_radius_km'] >= 1500

    def test_anti_ship_range(self, model):
        """Anti-ship range should include PrSM."""
        ranges = model.calculate_strike_range_rings()
        assert ranges['anti_ship_radius_km'] >= 900


class TestDevelopmentCosts:
    """Test new systems development cost calculations."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_total_development_cost(self, model):
        """Total new development should be ~$3.8B."""
        costs = model.calculate_development_costs()
        assert 3.0 <= costs['total_development_cost_b'] <= 5.0

    def test_thaad_maritime_most_expensive(self, model):
        """THAAD maritime should be most expensive."""
        costs = model.calculate_development_costs()
        thaad_cost = costs['breakdown']['thaad_maritime']
        assert thaad_cost >= 1.5  # Billion


class TestWeightCalculations:
    """Test armament weight calculations."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_total_weight_reasonable(self, model):
        """Total armament weight should be reasonable."""
        weight = model.calculate_total_weight()
        total_tons = weight['totals']['grand_total_tons']
        # Should be significant but less than 1000 tons
        assert 500 <= total_tons <= 1500

    def test_vls_structure_weight(self, model):
        """VLS structure should be heaviest component."""
        weight = model.calculate_total_weight()
        vls_weight = sum(weight['vls_structure_kg'].values())
        assert vls_weight > 200000  # > 200 tons


class TestReportGeneration:
    """Test report generation."""

    @pytest.fixture
    def model(self):
        return ArmamentModel()

    def test_report_contains_key_sections(self, model):
        """Report should contain all key sections."""
        report = model.generate_report()

        assert 'VLS CONFIGURATION' in report
        assert 'LAYERED DEFENSE' in report
        assert 'ANTI-SWARM' in report
        assert 'STRIKE RANGES' in report
        assert 'NEW SYSTEMS DEVELOPMENT' in report


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
