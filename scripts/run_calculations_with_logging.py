#!/usr/bin/env python3
"""
Calculation Logging Runner

Executes all CAD calculations and logs every derived value with
full traceability for CI/CD pipelines.

Logs include:
- Every parameter used in calculations
- Intermediate calculation steps
- Final results with units
- Confidence levels
- Validation status

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
import json
import sys
from datetime import datetime

from osint_cad.util.calculation_logger import (
    CalculationLogger, OutputFormat, init_logger
)
from osint_cad.platforms.pla_validated_cad import (
    create_df41_validated_spec,
    create_hq9b_validated_spec,
    create_j20_validated_spec,
    create_type055_validated_spec,
    generate_df41_validated_cad,
    generate_hq9b_validated_cad,
    generate_j20_validated_cad,
    generate_type055_validated_cad,
    ValidatedGeometryGenerator,
    EPSILON
)


def run_all_calculations():
    """Run all CAD calculations with comprehensive logging"""

    # Initialize logger
    logger = init_logger(
        name="CAD-Calculations",
        output_formats=[OutputFormat.CONSOLE, OutputFormat.GITHUB_ACTIONS],
        log_file="calculation_log.txt",
        verbose=True
    )

    all_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "systems": {},
        "calculations": [],
        "summary": {}
    }

    print("=" * 80)
    print("CALCULATION LOGGING RUNNER")
    print("Logging all derived values from CAD calculations")
    print("=" * 80)

    # =========================================================================
    # SYSTEM 1: DF-41 ICBM
    # =========================================================================
    with logger.section("DF-41 ICBM Calculations"):
        spec = create_df41_validated_spec()

        # Log all input parameters
        for name, param in spec.parameters.items():
            logger.log_validation(
                component="DF-41",
                parameter=name,
                value=param.value,
                min_val=param.min_valid,
                max_val=param.max_valid
            )

        # Calculate derived values
        total_length = spec.get_value("total_length")
        diameter = spec.get_value("body_diameter")
        stage1_len = spec.get_value("stage1_length")
        stage2_len = spec.get_value("stage2_length")
        stage3_len = spec.get_value("stage3_length")
        nose_len = spec.get_value("nose_length")

        # Fineness ratio
        fineness = total_length / diameter
        logger.log_calculation(
            name="DF-41 Fineness Ratio",
            formula="L/D = total_length / diameter",
            inputs={"total_length": total_length, "diameter": diameter},
            result=fineness,
            unit="ratio",
            confidence=0.70,
            intermediate_steps=[
                {"step": f"L = {total_length} m"},
                {"step": f"D = {diameter} m"},
                {"step": f"L/D = {total_length}/{diameter} = {fineness:.2f}"}
            ],
            notes="Optimal range for ballistic missiles: 8-15"
        )

        # Body length (excluding nose)
        body_length = total_length - nose_len
        logger.log_calculation(
            name="DF-41 Body Length",
            formula="body_length = total_length - nose_length",
            inputs={"total_length": total_length, "nose_length": nose_len},
            result=body_length,
            unit="m",
            confidence=0.65
        )

        # Cross-sectional area
        cross_area = np.pi * (diameter / 2) ** 2
        logger.log_calculation(
            name="DF-41 Cross-Sectional Area",
            formula="A = π * (D/2)²",
            inputs={"diameter": diameter},
            result=cross_area,
            unit="m²",
            confidence=0.65,
            intermediate_steps=[
                {"step": f"radius = {diameter/2:.3f} m"},
                {"step": f"A = π × {diameter/2:.3f}² = {cross_area:.3f} m²"}
            ]
        )

        # Estimated volume (simplified cylinder)
        est_volume = cross_area * body_length
        logger.log_calculation(
            name="DF-41 Estimated Volume",
            formula="V ≈ A × body_length",
            inputs={"cross_area": cross_area, "body_length": body_length},
            result=est_volume,
            unit="m³",
            confidence=0.50,
            notes="Simplified estimate - actual volume includes nose cone and tapers"
        )

        # Stage mass fractions (estimates)
        stage1_fraction = stage1_len / body_length
        stage2_fraction = stage2_len / body_length
        stage3_fraction = stage3_len / body_length

        logger.log_calculation(
            name="DF-41 Stage 1 Length Fraction",
            formula="f₁ = stage1_length / body_length",
            inputs={"stage1_length": stage1_len, "body_length": body_length},
            result=stage1_fraction,
            unit="ratio",
            confidence=0.45
        )

        logger.log_calculation(
            name="DF-41 Stage 2 Length Fraction",
            formula="f₂ = stage2_length / body_length",
            inputs={"stage2_length": stage2_len, "body_length": body_length},
            result=stage2_fraction,
            unit="ratio",
            confidence=0.45
        )

        logger.log_calculation(
            name="DF-41 Stage 3 Length Fraction",
            formula="f₃ = stage3_length / body_length",
            inputs={"stage3_length": stage3_len, "body_length": body_length},
            result=stage3_fraction,
            unit="ratio",
            confidence=0.45
        )

        # Ogive radius calculation
        R = diameter / 2
        L = nose_len
        ogive_radius = (L**2 + R**2) / (2 * R)
        logger.log_calculation(
            name="DF-41 Nose Ogive Radius",
            formula="ρ = (L² + R²) / (2R)",
            inputs={"nose_length": L, "base_radius": R},
            result=ogive_radius,
            unit="m",
            confidence=0.55,
            intermediate_steps=[
                {"step": f"L² = {L**2:.3f}"},
                {"step": f"R² = {R**2:.3f}"},
                {"step": f"L² + R² = {L**2 + R**2:.3f}"},
                {"step": f"2R = {2*R:.3f}"},
                {"step": f"ρ = {ogive_radius:.3f} m"}
            ]
        )

        # Generate CAD and get actual values
        mesh, metadata = generate_df41_validated_cad(resolution=32)

        logger.log_calculation(
            name="DF-41 Actual Surface Area",
            formula="Σ(triangle_areas)",
            inputs={"triangles": metadata['total_triangles']},
            result=metadata['surface_area_m2'],
            unit="m²",
            confidence=0.60,
            notes="Calculated from mesh geometry"
        )

        logger.log_performance(
            operation="DF-41 CAD Generation",
            execution_time_ms=50,  # Approximate
            triangles_generated=metadata['total_triangles']
        )

        all_results["systems"]["DF-41"] = {
            "fineness_ratio": fineness,
            "body_length_m": body_length,
            "cross_area_m2": cross_area,
            "est_volume_m3": est_volume,
            "surface_area_m2": metadata['surface_area_m2'],
            "triangles": metadata['total_triangles'],
            "ogive_radius_m": ogive_radius
        }

    # =========================================================================
    # SYSTEM 2: HQ-9B SAM
    # =========================================================================
    with logger.section("HQ-9B SAM Calculations"):
        spec = create_hq9b_validated_spec()

        for name, param in spec.parameters.items():
            logger.log_validation(
                component="HQ-9B",
                parameter=name,
                value=param.value,
                min_val=param.min_valid,
                max_val=param.max_valid
            )

        total_length = spec.get_value("total_length")
        diameter = spec.get_value("body_diameter")
        nose_len = spec.get_value("nose_length")
        fin_span = spec.get_value("fin_span")
        fin_chord = spec.get_value("fin_root_chord")
        fin_sweep = spec.get_value("fin_sweep_deg")

        # Fineness ratio
        fineness = total_length / diameter
        logger.log_calculation(
            name="HQ-9B Fineness Ratio",
            formula="L/D = total_length / diameter",
            inputs={"total_length": total_length, "diameter": diameter},
            result=fineness,
            unit="ratio",
            confidence=0.75
        )

        # Fin aspect ratio
        fin_area = fin_span * (fin_chord + fin_chord * 0.4) / 2  # Trapezoid
        fin_ar = fin_span ** 2 / fin_area
        logger.log_calculation(
            name="HQ-9B Fin Aspect Ratio",
            formula="AR = b² / S",
            inputs={"fin_span": fin_span, "fin_area": fin_area},
            result=fin_ar,
            unit="ratio",
            confidence=0.55,
            intermediate_steps=[
                {"step": f"b = {fin_span} m"},
                {"step": f"S ≈ {fin_area:.4f} m²"},
                {"step": f"AR = {fin_span}² / {fin_area:.4f} = {fin_ar:.2f}"}
            ]
        )

        # Fin sweep angle (radians)
        fin_sweep_rad = np.radians(fin_sweep)
        logger.log_calculation(
            name="HQ-9B Fin Sweep (radians)",
            formula="Λ_rad = Λ_deg × π/180",
            inputs={"sweep_deg": fin_sweep},
            result=fin_sweep_rad,
            unit="rad",
            confidence=0.60
        )

        # Generate CAD
        mesh, metadata = generate_hq9b_validated_cad(resolution=32)

        logger.log_calculation(
            name="HQ-9B Surface Area",
            formula="Σ(triangle_areas)",
            inputs={"triangles": metadata['total_triangles']},
            result=metadata['surface_area_m2'],
            unit="m²",
            confidence=0.60
        )

        all_results["systems"]["HQ-9B"] = {
            "fineness_ratio": fineness,
            "fin_aspect_ratio": fin_ar,
            "fin_sweep_rad": fin_sweep_rad,
            "surface_area_m2": metadata['surface_area_m2'],
            "triangles": metadata['total_triangles']
        }

    # =========================================================================
    # SYSTEM 3: J-20 Fighter
    # =========================================================================
    with logger.section("J-20 Fighter Calculations"):
        spec = create_j20_validated_spec()

        for name, param in spec.parameters.items():
            logger.log_validation(
                component="J-20",
                parameter=name,
                value=param.value,
                min_val=param.min_valid,
                max_val=param.max_valid
            )

        length = spec.get_value("length")
        wingspan = spec.get_value("wingspan")
        height = spec.get_value("height")
        wing_area = spec.get_value("wing_area")
        wing_sweep = spec.get_value("wing_sweep_deg")

        # Wing aspect ratio
        wing_ar = wingspan ** 2 / wing_area
        logger.log_calculation(
            name="J-20 Wing Aspect Ratio",
            formula="AR = b² / S",
            inputs={"wingspan": wingspan, "wing_area": wing_area},
            result=wing_ar,
            unit="ratio",
            confidence=0.55,
            notes="Low AR typical for delta wings - good for supersonic"
        )

        # Wing loading estimate (assuming 20,000 kg)
        est_mass = 20000  # kg estimate
        wing_loading = est_mass / wing_area
        logger.log_calculation(
            name="J-20 Estimated Wing Loading",
            formula="W/S = mass / wing_area",
            inputs={"est_mass_kg": est_mass, "wing_area": wing_area},
            result=wing_loading,
            unit="kg/m²",
            confidence=0.40,
            notes="Mass is rough estimate"
        )

        # Fuselage fineness
        fuselage_fineness = length / (wingspan * 0.25)  # Assume fuselage width ~ 25% span
        logger.log_calculation(
            name="J-20 Fuselage Fineness",
            formula="L_fuse / W_fuse",
            inputs={"length": length, "est_fuselage_width": wingspan * 0.25},
            result=fuselage_fineness,
            unit="ratio",
            confidence=0.50
        )

        # Generate CAD
        mesh, metadata = generate_j20_validated_cad(resolution=24)

        logger.log_calculation(
            name="J-20 Surface Area",
            formula="Σ(triangle_areas)",
            inputs={"triangles": metadata['total_triangles']},
            result=metadata['surface_area_m2'],
            unit="m²",
            confidence=0.55
        )

        all_results["systems"]["J-20"] = {
            "wing_aspect_ratio": wing_ar,
            "wing_loading_kg_m2": wing_loading,
            "fuselage_fineness": fuselage_fineness,
            "surface_area_m2": metadata['surface_area_m2'],
            "triangles": metadata['total_triangles']
        }

    # =========================================================================
    # SYSTEM 4: Type 055 Destroyer
    # =========================================================================
    with logger.section("Type 055 Destroyer Calculations"):
        spec = create_type055_validated_spec()

        for name, param in spec.parameters.items():
            logger.log_validation(
                component="Type 055",
                parameter=name,
                value=param.value,
                min_val=param.min_valid,
                max_val=param.max_valid
            )

        length = spec.get_value("length")
        beam = spec.get_value("beam")
        draft = spec.get_value("draft")
        displacement = spec.get_value("displacement")

        # Length/beam ratio
        lb_ratio = length / beam
        logger.log_calculation(
            name="Type 055 Length/Beam Ratio",
            formula="L/B = length / beam",
            inputs={"length": length, "beam": beam},
            result=lb_ratio,
            unit="ratio",
            confidence=0.85,
            notes="Typical warship L/B: 7-10"
        )

        # Beam/draft ratio
        bd_ratio = beam / draft
        logger.log_calculation(
            name="Type 055 Beam/Draft Ratio",
            formula="B/T = beam / draft",
            inputs={"beam": beam, "draft": draft},
            result=bd_ratio,
            unit="ratio",
            confidence=0.75
        )

        # Block coefficient estimate
        est_volume = length * beam * draft * 0.5  # Typical Cb ~ 0.5 for warships
        block_coeff = (displacement * 1000 / 1025) / (length * beam * draft)  # 1025 kg/m³ seawater
        logger.log_calculation(
            name="Type 055 Block Coefficient",
            formula="Cb = Δ / (ρ × L × B × T)",
            inputs={"displacement": displacement, "length": length, "beam": beam, "draft": draft},
            result=block_coeff,
            unit="ratio",
            confidence=0.60,
            intermediate_steps=[
                {"step": f"Δ = {displacement} tonnes = {displacement*1000} kg"},
                {"step": f"V_displaced = {displacement*1000/1025:.0f} m³"},
                {"step": f"V_box = L×B×T = {length*beam*draft:.0f} m³"},
                {"step": f"Cb = {block_coeff:.3f}"}
            ]
        )

        # Generate CAD
        mesh, metadata = generate_type055_validated_cad(resolution=24)

        logger.log_calculation(
            name="Type 055 Surface Area",
            formula="Σ(triangle_areas)",
            inputs={"triangles": metadata['total_triangles']},
            result=metadata['surface_area_m2'],
            unit="m²",
            confidence=0.50
        )

        all_results["systems"]["Type 055"] = {
            "lb_ratio": lb_ratio,
            "bd_ratio": bd_ratio,
            "block_coefficient": block_coeff,
            "surface_area_m2": metadata['surface_area_m2'],
            "triangles": metadata['total_triangles']
        }

    # =========================================================================
    # SUMMARY
    # =========================================================================
    logger.finalize()

    # Calculate summary stats
    total_triangles = sum(
        s.get("triangles", 0) for s in all_results["systems"].values()
    )
    total_calculations = len(logger.calculations)
    validations_passed = sum(1 for v in logger.validations if v.is_valid)
    validations_failed = sum(1 for v in logger.validations if not v.is_valid)

    all_results["summary"] = {
        "total_systems": len(all_results["systems"]),
        "total_triangles": total_triangles,
        "total_calculations": total_calculations,
        "validations_passed": validations_passed,
        "validations_failed": validations_failed
    }

    # Write JSON report
    with open("calculation_log.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print("\nWrote: calculation_log.json")

    # Write Markdown report
    md_report = logger.generate_markdown_report()
    with open("calculation_report.md", "w") as f:
        f.write(md_report)
    print("Wrote: calculation_report.md")

    print("\n" + "=" * 80)
    print("CALCULATION LOGGING COMPLETE")
    print(f"Total calculations logged: {total_calculations}")
    print(f"Validations: {validations_passed} passed, {validations_failed} failed")
    print("=" * 80)

    return all_results


if __name__ == "__main__":
    run_all_calculations()
