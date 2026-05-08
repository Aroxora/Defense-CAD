#!/usr/bin/env python3
"""
Unit tests for LSC-X Heavy Cruiser model.

Tests physics calculations, capability assessments, and comparisons.
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lsc_x_model import (
    LSCX_Model,
    HullSpecifications,
    PowerPlant,
    WeaponSystems
)


class TestHullSpecifications:
    """Test hull specification constraints."""

    def test_displacement_reasonable(self):
        """Displacement should be between DDG and CVN."""
        hull = HullSpecifications()
        assert 15000 < hull.displacement_tons < 50000
        assert hull.displacement_tons == 23000

    def test_dimensions_physically_valid(self):
        """Hull dimensions should be proportional."""
        hull = HullSpecifications()
        # Length-to-beam ratio typically 7-10 for warships
        ratio = hull.length_m / hull.beam_m
        assert 6 < ratio < 12, f"L/B ratio {ratio} out of range"

    def test_speed_achievable(self):
        """Speed should be achievable with stated power."""
        hull = HullSpecifications()
        power = PowerPlant()
        # Admiralty coefficient check (rough estimate)
        # Speed^3 * Displacement^(2/3) / Power should be reasonable
        coeff = (hull.speed_knots ** 3) * (hull.displacement_tons ** 0.667) / (power.gas_turbines_mw * 1000)
        assert 100 < coeff < 1000, f"Admiralty coefficient {coeff} unreasonable"

    def test_crew_per_ton(self):
        """Crew should be reasonable for automation level."""
        hull = HullSpecifications()
        crew_per_1000_tons = hull.crew / (hull.displacement_tons / 1000)
        # Modern automated ships: 10-20 crew per 1000 tons
        assert 10 < crew_per_1000_tons < 30


class TestPowerPlant:
    """Test power generation specifications."""

    def test_total_power_sufficient(self):
        """Total power should exceed propulsion + combat needs."""
        power = PowerPlant()
        total = power.gas_turbines_mw + power.aux_diesel_mw
        required = power.propulsion_mw + power.combat_systems_mw
        assert total >= required, "Insufficient power generation"

    def test_combat_power_reserve(self):
        """Combat systems should have significant power reserve."""
        power = PowerPlant()
        # Should have at least 25 MW for DEW and large radars
        assert power.combat_systems_mw >= 25

    def test_lm2500_realistic(self):
        """LM2500+G4 power should be realistic (25 MW each)."""
        power = PowerPlant()
        # 4x LM2500+G4 at ~25 MW each = 100 MW
        assert 80 <= power.gas_turbines_mw <= 120


class TestWeaponSystems:
    """Test weapons integration specifications."""

    def test_vls_capacity(self):
        """VLS capacity should exceed DDG-51."""
        weapons = WeaponSystems()
        total_vls = weapons.mk41_cells + weapons.mk57_cells
        assert total_vls > 96, "Should exceed DDG-51 VLS count"
        assert total_vls == 160

    def test_bmd_interceptors(self):
        """Should have dedicated BMD interceptors."""
        weapons = WeaponSystems()
        assert weapons.thaad_interceptors >= 8
        assert weapons.mk57_cells >= 16  # SM-3 capable

    def test_laser_power(self):
        """Laser should be effective against small threats."""
        weapons = WeaponSystems()
        # 100+ kW needed for cruise missile defense
        assert weapons.laser_kw >= 100


class TestLSCXModel:
    """Test main simulation model."""

    @pytest.fixture
    def model(self):
        return LSCX_Model()

    def test_bmd_coverage_calculation(self, model):
        """BMD coverage should return valid results."""
        result = model.calculate_bmd_coverage()

        assert 'sm3_defended_area_km2' in result
        assert 'thaad_defended_area_km2' in result
        assert 'layered_pk_estimate' in result

        # SM-3 should defend larger area than THAAD
        assert result['sm3_defended_area_km2'] > result['thaad_defended_area_km2']

    def test_layered_pk_high(self, model):
        """Layered defense Pk should be very high."""
        result = model.calculate_bmd_coverage()
        # SM-3 + THAAD should achieve >95% Pk
        assert result['layered_pk_estimate'] > 0.95

    def test_strike_capability(self, model):
        """Strike capability should include Army integration."""
        result = model.calculate_strike_capability()

        assert 'prsm_capacity' in result
        assert result['prsm_capacity'] > 0
        assert result['prsm_range_km'] >= 500

    def test_dew_effectiveness(self, model):
        """DEW should be effective against soft targets."""
        result = model.calculate_dew_effectiveness()

        assert 'small_uav' in result
        assert result['small_uav']['effective'] is True

    def test_comparison_to_ddg51(self, model):
        """Comparison should show advantages over DDG-51."""
        result = model.compare_to_ddg51()

        assert 'ddg51_flight_iii' in result
        assert 'lsc_x' in result
        assert 'lscx_advantages' in result

        # LSC-X should have more VLS
        assert result['lsc_x']['vls_cells'] > result['ddg51_flight_iii']['vls_cells']

        # LSC-X should have more combat power
        assert result['lsc_x']['power_for_combat_mw'] > result['ddg51_flight_iii']['power_for_combat_mw']

    def test_report_generation(self, model):
        """Report should be generated without errors."""
        report = model.generate_report()

        assert isinstance(report, str)
        assert len(report) > 500
        assert 'LSC-X' in report
        assert 'BMD' in report


class TestPhysicsCalculations:
    """Test physics-based calculations."""

    @pytest.fixture
    def model(self):
        return LSCX_Model()

    def test_laser_attenuation(self, model):
        """Laser power should attenuate with range."""
        dew = model.calculate_dew_effectiveness()

        # Closer targets should receive more fluence
        # (implicitly tested by effectiveness at different ranges)
        assert dew['small_uav']['effective_range_km'] >= dew['fiac']['effective_range_km']

    def test_defended_area_formula(self, model):
        """Defended area should follow pi*r^2."""
        bmd = model.calculate_bmd_coverage()

        # Verify SM-3 area calculation
        expected_sm3_area = np.pi * (2500 ** 2)  # 2500 km range
        assert abs(bmd['sm3_defended_area_km2'] - expected_sm3_area) < 1

    def test_salvo_pk_formula(self, model):
        """Salvo Pk should follow 1-(1-Pk)^n formula."""
        # Test the layered Pk calculation
        pk_sm3 = 0.85
        pk_thaad = 0.90

        pk_sm3_salvo = 1 - (1 - pk_sm3) ** 2
        pk_thaad_salvo = 1 - (1 - pk_thaad) ** 2
        pk_layered = 1 - (1 - pk_sm3_salvo) * (1 - pk_thaad_salvo)

        bmd = model.calculate_bmd_coverage()
        assert abs(bmd['layered_pk_estimate'] - pk_layered) < 0.01


class TestCostEffectiveness:
    """Test cost-benefit analysis."""

    @pytest.fixture
    def model(self):
        return LSCX_Model()

    def test_cost_per_vls_better(self, model):
        """Cost per VLS should be competitive."""
        comparison = model.compare_to_ddg51()

        ddg_cost_per_vls = comparison['ddg51_flight_iii']['cost_per_vls']
        lscx_cost_per_vls = comparison['lsc_x']['cost_per_vls']

        # LSC-X should have similar or better cost per VLS
        assert lscx_cost_per_vls < ddg_cost_per_vls * 1.5

    def test_army_integration_unique(self, model):
        """Army integration should be unique capability."""
        comparison = model.compare_to_ddg51()

        assert comparison['ddg51_flight_iii']['army_integration'] is False
        assert comparison['lsc_x']['army_integration'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
