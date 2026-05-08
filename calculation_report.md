# PLA CAD Calculation Report

**Generated:** 2026-01-15T19:24:18.441485
**Total Runtime:** 86.25 ms

## Summary

- Algorithms Run: 0
- Calculations: 21
- Validations: 25 (25 passed)
- Errors: 0

## Calculations

| Name | Formula | Result | Unit | Confidence |
|------|---------|--------|------|------------|
| DF-41 Fineness Ratio | `L/D = total_length / diameter` | 9.33333 | ratio | 70% |
| DF-41 Body Length | `body_length = total_length - nose_length` | 18 | m | 65% |
| DF-41 Cross-Sectional Area | `A = π * (D/2)²` | 3.97608 | m² | 65% |
| DF-41 Estimated Volume | `V ≈ A × body_length` | 71.5694 | m³ | 50% |
| DF-41 Stage 1 Length Fraction | `f₁ = stage1_length / body_length` | 0.472222 | ratio | 45% |
| DF-41 Stage 2 Length Fraction | `f₂ = stage2_length / body_length` | 0.305556 | ratio | 45% |
| DF-41 Stage 3 Length Fraction | `f₃ = stage3_length / body_length` | 0.222222 | ratio | 45% |
| DF-41 Nose Ogive Radius | `ρ = (L² + R²) / (2R)` | 4.5625 | m | 55% |
| DF-41 Actual Surface Area | `Σ(triangle_areas)` | 158.606 | m² | 60% |
| HQ-9B Fineness Ratio | `L/D = total_length / diameter` | 14.4681 | ratio | 75% |
| HQ-9B Fin Aspect Ratio | `AR = b² / S` | 1.25 | ratio | 55% |
| HQ-9B Fin Sweep (radians) | `Λ_rad = Λ_deg × π/180` | 0.872665 | rad | 60% |
| HQ-9B Surface Area | `Σ(triangle_areas)` | 10.2435 | m² | 60% |
| J-20 Wing Aspect Ratio | `AR = b² / S` | 2.31507 | ratio | 55% |
| J-20 Estimated Wing Loading | `W/S = mass / wing_area` | 273.973 | kg/m² | 40% |
| J-20 Fuselage Fineness | `L_fuse / W_fuse` | 6.27692 | ratio | 50% |
| J-20 Surface Area | `Σ(triangle_areas)` | 269.899 | m² | 55% |
| Type 055 Length/Beam Ratio | `L/B = length / beam` | 9 | ratio | 85% |
| Type 055 Beam/Draft Ratio | `B/T = beam / draft` | 3.0303 | ratio | 75% |
| Type 055 Block Coefficient | `Cb = Δ / (ρ × L × B × T)` | 0.533793 | ratio | 60% |
| Type 055 Surface Area | `Σ(triangle_areas)` | 6034.71 | m² | 50% |

## Performance

| Operation | Time (ms) | Triangles | Rate (tri/s) |
|-----------|-----------|-----------|--------------|
| DF-41 CAD Generation | 50.00 | 2784 | 55680 |
