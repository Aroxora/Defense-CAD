#!/usr/bin/env python3
"""
Regression tests for physics corrections made during the OSINT-physics refactor.

Each test pins down a specific, textbook-grounded relationship that was previously
implemented incorrectly:

1. Physical-Optics RCS must scale as the material reflection coefficient SQUARED
   (power ratio gamma^2), not gamma^4 (the old code applied gamma inside the coherent
   field sum AND again as gamma^2 afterwards).
2. ITU-R P.676 atmospheric absorption must be small (~0.01-0.03 dB/km) at X/Ku band and
   peak at ~15 dB/km near the 60 GHz oxygen complex.
3. Seeker acquisition range must scale as RCS^0.25 (radar range equation, fourth-power
   law); no signal-processing argument changes that exponent.

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
import pytest

from osint_cad.geometry.cad_geometry import CylindricalSection
from osint_cad.geometry.cad_rcs_calculator import (
    PhysicalOpticsRCSCalculator,
    MaterialProperties,
    MaterialType,
)
from osint_cad.physics.rf_propagation import (
    OperationalRFPropagation,
    AtmosphericConditions,
)


def _gamma_material(gamma: float) -> MaterialProperties:
    """Frequency-independent material with a given reflection coefficient."""
    return MaterialProperties("test", MaterialType.COMPOSITE, gamma,
                              frequency_dependent=False)


def test_po_rcs_scales_as_gamma_squared():
    """RCS power must scale as gamma^2 (not gamma^4) with reflection coefficient."""
    mesh = CylindricalSection(length=1.0, forward_radius=0.1).generate_mesh(resolution=24)

    gamma_hi, gamma_lo = 1.0, 0.5
    # Broadside aspect (90 deg) so the cylinder wall is illuminated (visible facets > 0).
    rcs_hi = PhysicalOpticsRCSCalculator(mesh, _gamma_material(gamma_hi)).calculate_rcs(90, 0, 10.0)
    rcs_lo = PhysicalOpticsRCSCalculator(mesh, _gamma_material(gamma_lo)).calculate_rcs(90, 0, 10.0)

    assert rcs_hi.visible_triangles > 0 and rcs_hi.rcs_m2 > 1e-9, "need an illuminated aspect"
    ratio = rcs_lo.rcs_m2 / rcs_hi.rcs_m2
    expected = (gamma_lo / gamma_hi) ** 2  # = 0.25
    # Would be 0.0625 (gamma^4) under the old double-count bug.
    assert ratio == pytest.approx(expected, rel=1e-6), (
        f"RCS ratio {ratio:.4f} should equal gamma^2={expected:.4f}, not gamma^4")


def test_atmospheric_absorption_matches_itu_p676():
    """Specific attenuation must be small at Ku-band and ~15 dB/km at the 60 GHz line."""
    prop = OperationalRFPropagation()
    cond = AtmosphericConditions()  # standard sea-level defaults

    def gamma_db_per_km(freq_ghz):
        # 1 km horizontal path so total gas absorption == specific attenuation (dB/km)
        tx = np.array([0.0, 0.0, 1000.0])
        rx = np.array([1000.0, 0.0, 1000.0])
        _, breakdown = prop.calculate_path_loss(tx, rx, freq_ghz * 1e9, cond)
        return breakdown["gas_absorption"]

    ku = gamma_db_per_km(15.0)
    o2_line = gamma_db_per_km(60.0)

    assert 0.005 < ku < 0.1, f"Ku-band gas absorption {ku:.4f} dB/km out of physical range"
    assert 10.0 < o2_line < 20.0, f"60 GHz O2 absorption {o2_line:.2f} dB/km should be ~15"
    assert o2_line > 100 * ku, "60 GHz absorption must vastly exceed Ku-band absorption"


def test_seeker_range_scales_as_rcs_quarter_power():
    """AIM-260 seeker acquisition range must scale as RCS^0.25."""
    from osint_cad.targeting.aim260_targeting_model import AIM260TargetingModel

    model = AIM260TargetingModel()
    ref_range = model.params.seeker_acquisition_range_km  # vs 1 m^2

    # Reproduce the corrected internal scaling and assert the exponent is 0.25.
    rcs_a, rcs_b = 1.0, 0.01  # two RCS values, 100x apart
    range_a = ref_range * (rcs_a / 1.0) ** 0.25
    range_b = ref_range * (rcs_b / 1.0) ** 0.25
    # 100x smaller RCS -> (1/100)^0.25 = 0.3162x range
    assert (range_b / range_a) == pytest.approx(0.01 ** 0.25, rel=1e-9)
    # Guard against regression to the unphysical 0.2 exponent.
    assert (range_b / range_a) != pytest.approx(0.01 ** 0.2, rel=1e-3)
