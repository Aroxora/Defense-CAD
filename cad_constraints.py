#!/usr/bin/env python3
"""
CAD Parametric Constraints Module

Defines physical and aerodynamic constraints for platform geometry.
Enables design validation, optimization bounds, and manufacturing
feasibility checks.

Key Constraint Categories:
- Geometric constraints (dimensions, ratios)
- Aerodynamic constraints (fineness ratio, stability margins)
- Structural constraints (load paths, material limits)
- Manufacturing constraints (tolerances, assemblability)
- Performance constraints (RCS, weight, speed)

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Callable, Any
from enum import Enum
from abc import ABC, abstractmethod


class ConstraintType(Enum):
    """Types of design constraints"""
    GEOMETRIC = "geometric"
    AERODYNAMIC = "aerodynamic"
    STRUCTURAL = "structural"
    MANUFACTURING = "manufacturing"
    PERFORMANCE = "performance"
    PHYSICAL = "physical"


class ConstraintSeverity(Enum):
    """Constraint violation severity"""
    ERROR = "error"      # Must be fixed
    WARNING = "warning"  # Should be reviewed
    INFO = "info"        # Advisory only


@dataclass
class ConstraintResult:
    """Result of a constraint check"""
    constraint_name: str
    constraint_type: ConstraintType
    is_satisfied: bool
    actual_value: float
    limit_value: float
    margin: float  # Percentage margin to limit
    severity: ConstraintSeverity
    message: str
    recommendation: str = ""


@dataclass
class ConstraintSet:
    """Collection of constraint results"""
    results: List[ConstraintResult] = field(default_factory=list)

    @property
    def all_satisfied(self) -> bool:
        """Check if all constraints are satisfied"""
        return all(r.is_satisfied for r in self.results)

    @property
    def errors(self) -> List[ConstraintResult]:
        """Get error-level violations"""
        return [r for r in self.results if not r.is_satisfied
                and r.severity == ConstraintSeverity.ERROR]

    @property
    def warnings(self) -> List[ConstraintResult]:
        """Get warning-level violations"""
        return [r for r in self.results if not r.is_satisfied
                and r.severity == ConstraintSeverity.WARNING]

    def to_report(self) -> str:
        """Generate human-readable report"""
        lines = []
        lines.append("=" * 60)
        lines.append("CONSTRAINT VALIDATION REPORT")
        lines.append("=" * 60)

        for ctype in ConstraintType:
            type_results = [r for r in self.results if r.constraint_type == ctype]
            if type_results:
                lines.append(f"\n{ctype.value.upper()} CONSTRAINTS:")
                lines.append("-" * 40)
                for r in type_results:
                    status = "PASS" if r.is_satisfied else "FAIL"
                    lines.append(f"  [{status}] {r.constraint_name}")
                    lines.append(f"        Value: {r.actual_value:.4g}, "
                                f"Limit: {r.limit_value:.4g}, "
                                f"Margin: {r.margin:+.1f}%")
                    if not r.is_satisfied:
                        lines.append(f"        {r.message}")
                        if r.recommendation:
                            lines.append(f"        Recommendation: {r.recommendation}")

        lines.append("\n" + "=" * 60)
        lines.append(f"Summary: {len([r for r in self.results if r.is_satisfied])}"
                    f"/{len(self.results)} constraints satisfied")

        if self.errors:
            lines.append(f"ERRORS: {len(self.errors)} (must fix)")
        if self.warnings:
            lines.append(f"WARNINGS: {len(self.warnings)} (should review)")

        lines.append("=" * 60)
        return "\n".join(lines)


class ConstraintValidator(ABC):
    """Abstract base class for constraint validators"""

    @abstractmethod
    def validate(self, parameters: Dict[str, float]) -> ConstraintResult:
        """Validate constraint against parameters"""
        pass


class RangeConstraint(ConstraintValidator):
    """Constraint that checks if value is within range"""

    def __init__(self, name: str, param_name: str,
                 min_value: float, max_value: float,
                 constraint_type: ConstraintType = ConstraintType.GEOMETRIC,
                 severity: ConstraintSeverity = ConstraintSeverity.ERROR,
                 recommendation: str = ""):
        self.name = name
        self.param_name = param_name
        self.min_value = min_value
        self.max_value = max_value
        self.constraint_type = constraint_type
        self.severity = severity
        self.recommendation = recommendation

    def validate(self, parameters: Dict[str, float]) -> ConstraintResult:
        value = parameters.get(self.param_name, 0)
        is_valid = self.min_value <= value <= self.max_value

        if value < self.min_value:
            margin = (value - self.min_value) / self.min_value * 100
            limit = self.min_value
            message = f"Below minimum ({self.min_value})"
        elif value > self.max_value:
            margin = (value - self.max_value) / self.max_value * 100
            limit = self.max_value
            message = f"Above maximum ({self.max_value})"
        else:
            # Calculate margin to nearest limit
            margin_to_min = (value - self.min_value) / self.min_value * 100
            margin_to_max = (self.max_value - value) / self.max_value * 100
            margin = min(margin_to_min, margin_to_max)
            limit = self.min_value if margin == margin_to_min else self.max_value
            message = "Within range"

        return ConstraintResult(
            constraint_name=self.name,
            constraint_type=self.constraint_type,
            is_satisfied=is_valid,
            actual_value=value,
            limit_value=limit,
            margin=margin,
            severity=self.severity,
            message=message,
            recommendation=self.recommendation
        )


class RatioConstraint(ConstraintValidator):
    """Constraint that checks ratio of two parameters"""

    def __init__(self, name: str,
                 numerator_param: str, denominator_param: str,
                 min_ratio: float, max_ratio: float,
                 constraint_type: ConstraintType = ConstraintType.AERODYNAMIC,
                 severity: ConstraintSeverity = ConstraintSeverity.ERROR,
                 recommendation: str = ""):
        self.name = name
        self.numerator_param = numerator_param
        self.denominator_param = denominator_param
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
        self.constraint_type = constraint_type
        self.severity = severity
        self.recommendation = recommendation

    def validate(self, parameters: Dict[str, float]) -> ConstraintResult:
        num = parameters.get(self.numerator_param, 1)
        denom = parameters.get(self.denominator_param, 1)

        if denom == 0:
            return ConstraintResult(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                is_satisfied=False,
                actual_value=float('inf'),
                limit_value=self.max_ratio,
                margin=-100,
                severity=ConstraintSeverity.ERROR,
                message="Division by zero in ratio calculation",
                recommendation="Check denominator parameter"
            )

        ratio = num / denom
        is_valid = self.min_ratio <= ratio <= self.max_ratio

        if ratio < self.min_ratio:
            margin = (ratio - self.min_ratio) / self.min_ratio * 100
            limit = self.min_ratio
            message = f"Ratio {ratio:.2f} below minimum {self.min_ratio}"
        elif ratio > self.max_ratio:
            margin = (ratio - self.max_ratio) / self.max_ratio * 100
            limit = self.max_ratio
            message = f"Ratio {ratio:.2f} above maximum {self.max_ratio}"
        else:
            margin_to_min = (ratio - self.min_ratio) / self.min_ratio * 100
            margin_to_max = (self.max_ratio - ratio) / self.max_ratio * 100
            margin = min(margin_to_min, margin_to_max)
            limit = self.min_ratio if margin == margin_to_min else self.max_ratio
            message = "Within range"

        return ConstraintResult(
            constraint_name=self.name,
            constraint_type=self.constraint_type,
            is_satisfied=is_valid,
            actual_value=ratio,
            limit_value=limit,
            margin=margin,
            severity=self.severity,
            message=message,
            recommendation=self.recommendation
        )


class CustomConstraint(ConstraintValidator):
    """Constraint with custom validation function"""

    def __init__(self, name: str,
                 validation_func: Callable[[Dict[str, float]], Tuple[bool, float, float, str]],
                 constraint_type: ConstraintType,
                 severity: ConstraintSeverity = ConstraintSeverity.ERROR,
                 recommendation: str = ""):
        """
        Args:
            validation_func: Function that takes parameters dict and returns
                            (is_valid, actual_value, limit_value, message)
        """
        self.name = name
        self.validation_func = validation_func
        self.constraint_type = constraint_type
        self.severity = severity
        self.recommendation = recommendation

    def validate(self, parameters: Dict[str, float]) -> ConstraintResult:
        is_valid, actual, limit, message = self.validation_func(parameters)

        if limit != 0:
            margin = (actual - limit) / abs(limit) * 100
        else:
            margin = 0

        return ConstraintResult(
            constraint_name=self.name,
            constraint_type=self.constraint_type,
            is_satisfied=is_valid,
            actual_value=actual,
            limit_value=limit,
            margin=margin,
            severity=self.severity,
            message=message,
            recommendation=self.recommendation
        )


# =============================================================================
# Pre-defined Constraint Sets
# =============================================================================

class MissileConstraints:
    """Standard constraints for missile design"""

    @staticmethod
    def get_geometric_constraints() -> List[ConstraintValidator]:
        """Get geometric constraints for missiles"""
        return [
            RangeConstraint(
                name="Total Length",
                param_name="total_length",
                min_value=1.0,
                max_value=10.0,
                recommendation="Typical AAM: 2-5m, ARM: 3-6m, LACM: 4-8m"
            ),
            RangeConstraint(
                name="Body Diameter",
                param_name="body_diameter",
                min_value=0.1,
                max_value=0.6,
                recommendation="Typical: 150-400mm for air-launched"
            ),
            RangeConstraint(
                name="Nose Length",
                param_name="nose_length",
                min_value=0.1,
                max_value=2.0,
                recommendation="Typically 1.5-3x body diameter"
            ),
            RatioConstraint(
                name="Fineness Ratio (L/D)",
                numerator_param="total_length",
                denominator_param="body_diameter",
                min_ratio=6.0,
                max_ratio=25.0,
                recommendation="Optimal supersonic: 10-15"
            ),
            RatioConstraint(
                name="Nose Fineness",
                numerator_param="nose_length",
                denominator_param="body_diameter",
                min_ratio=1.5,
                max_ratio=5.0,
                recommendation="Sharp nose (>3) for Mach 3+, blunt (<2) for subsonic"
            ),
        ]

    @staticmethod
    def get_aerodynamic_constraints() -> List[ConstraintValidator]:
        """Get aerodynamic constraints for missiles"""
        return [
            RangeConstraint(
                name="Fin Span/Diameter Ratio",
                param_name="fin_span_ratio",
                min_value=0.3,
                max_value=1.5,
                constraint_type=ConstraintType.AERODYNAMIC,
                recommendation="Higher for subsonic, lower for supersonic"
            ),
            RangeConstraint(
                name="Fin Sweep Angle",
                param_name="fin_sweep_deg",
                min_value=20,
                max_value=70,
                constraint_type=ConstraintType.AERODYNAMIC,
                recommendation="Higher sweep for supersonic stability"
            ),
            RangeConstraint(
                name="Fin Taper Ratio",
                param_name="fin_taper_ratio",
                min_value=0.2,
                max_value=1.0,
                constraint_type=ConstraintType.AERODYNAMIC,
                recommendation="0.3-0.5 typical for reduced induced drag"
            ),
        ]

    @staticmethod
    def get_performance_constraints() -> List[ConstraintValidator]:
        """Get performance constraints for missiles"""

        def check_rcs_frontal(params: Dict[str, float]) -> Tuple[bool, float, float, str]:
            """Check if frontal RCS meets stealth requirements"""
            rcs_dbsm = params.get("rcs_frontal_dbsm", 0)
            limit = -15  # Low-observable threshold
            is_valid = rcs_dbsm < limit
            if is_valid:
                return True, rcs_dbsm, limit, "Low-observable achieved"
            else:
                return False, rcs_dbsm, limit, f"RCS {rcs_dbsm:.1f} dBsm exceeds LO threshold"

        return [
            RangeConstraint(
                name="Total Mass",
                param_name="total_mass_kg",
                min_value=50,
                max_value=1000,
                constraint_type=ConstraintType.PERFORMANCE,
                recommendation="Check carrier aircraft payload capacity"
            ),
            CustomConstraint(
                name="Frontal RCS (Low Observable)",
                validation_func=check_rcs_frontal,
                constraint_type=ConstraintType.PERFORMANCE,
                severity=ConstraintSeverity.WARNING,
                recommendation="Consider RAM coating or shaping changes"
            ),
        ]


class AircraftConstraints:
    """Standard constraints for aircraft design"""

    @staticmethod
    def get_wing_constraints() -> List[ConstraintValidator]:
        """Get wing geometry constraints"""
        return [
            RangeConstraint(
                name="Wingspan",
                param_name="wingspan",
                min_value=5.0,
                max_value=50.0,
                recommendation="Check hangar and parking constraints"
            ),
            RatioConstraint(
                name="Wing Aspect Ratio",
                numerator_param="wingspan",
                denominator_param="wing_chord_avg",
                min_ratio=2.0,
                max_ratio=12.0,
                constraint_type=ConstraintType.AERODYNAMIC,
                recommendation="Low AR (2-4) for high-speed, high AR (8-12) for efficiency"
            ),
            RangeConstraint(
                name="Wing Sweep",
                param_name="wing_sweep_deg",
                min_value=-5,
                max_value=70,
                constraint_type=ConstraintType.AERODYNAMIC,
                recommendation="Higher sweep delays compressibility effects"
            ),
            RangeConstraint(
                name="Wing Thickness Ratio",
                param_name="wing_thickness_ratio",
                min_value=0.02,
                max_value=0.18,
                constraint_type=ConstraintType.AERODYNAMIC,
                recommendation="Thin (0.03-0.06) for supersonic, thick (0.12-0.18) for subsonic"
            ),
        ]

    @staticmethod
    def get_stealth_constraints() -> List[ConstraintValidator]:
        """Get stealth-related constraints"""

        def check_edge_alignment(params: Dict[str, float]) -> Tuple[bool, float, float, str]:
            """Check if major edges are aligned to minimize RCS spikes"""
            # Simplified check - all sweep angles should be within 5 degrees of each other
            wing_sweep = params.get("wing_sweep_deg", 45)
            tail_sweep = params.get("tail_sweep_deg", 45)
            le_sweep = params.get("leading_edge_sweep_deg", wing_sweep)

            max_diff = max(
                abs(wing_sweep - tail_sweep),
                abs(wing_sweep - le_sweep),
                abs(tail_sweep - le_sweep)
            )

            limit = 10  # 10 degrees tolerance
            is_valid = max_diff <= limit

            if is_valid:
                return True, max_diff, limit, "Edge alignment acceptable"
            else:
                return False, max_diff, limit, f"Edge alignment difference {max_diff:.1f}° too large"

        return [
            CustomConstraint(
                name="Edge Alignment (Planform)",
                validation_func=check_edge_alignment,
                constraint_type=ConstraintType.PERFORMANCE,
                severity=ConstraintSeverity.WARNING,
                recommendation="Align major edges to common angles for RCS reduction"
            ),
            RangeConstraint(
                name="Cavity Depth",
                param_name="intake_depth_ratio",
                min_value=3.0,
                max_value=10.0,
                constraint_type=ConstraintType.PERFORMANCE,
                severity=ConstraintSeverity.WARNING,
                recommendation="Deeper cavities reduce engine face RCS"
            ),
        ]


# =============================================================================
# Constraint Validator Engine
# =============================================================================

class DesignConstraintEngine:
    """
    Engine for validating design parameters against constraints.

    Collects multiple constraint validators and runs them against
    a parameter dictionary.
    """

    def __init__(self):
        self.constraints: List[ConstraintValidator] = []

    def add_constraint(self, constraint: ConstraintValidator):
        """Add a single constraint"""
        self.constraints.append(constraint)

    def add_constraints(self, constraints: List[ConstraintValidator]):
        """Add multiple constraints"""
        self.constraints.extend(constraints)

    def add_missile_constraints(self):
        """Add standard missile constraints"""
        self.add_constraints(MissileConstraints.get_geometric_constraints())
        self.add_constraints(MissileConstraints.get_aerodynamic_constraints())
        self.add_constraints(MissileConstraints.get_performance_constraints())

    def add_aircraft_constraints(self):
        """Add standard aircraft constraints"""
        self.add_constraints(AircraftConstraints.get_wing_constraints())
        self.add_constraints(AircraftConstraints.get_stealth_constraints())

    def validate(self, parameters: Dict[str, float]) -> ConstraintSet:
        """
        Validate parameters against all constraints.

        Args:
            parameters: Dictionary of parameter names and values

        Returns:
            ConstraintSet with all results
        """
        results = ConstraintSet()

        for constraint in self.constraints:
            try:
                result = constraint.validate(parameters)
                results.results.append(result)
            except Exception as e:
                results.results.append(ConstraintResult(
                    constraint_name=constraint.name if hasattr(constraint, 'name') else "Unknown",
                    constraint_type=ConstraintType.PHYSICAL,
                    is_satisfied=False,
                    actual_value=0,
                    limit_value=0,
                    margin=0,
                    severity=ConstraintSeverity.ERROR,
                    message=f"Validation error: {str(e)}"
                ))

        return results

    def get_feasible_region(self, param_name: str) -> Optional[Tuple[float, float]]:
        """
        Get the feasible range for a parameter based on constraints.

        Args:
            param_name: Name of parameter

        Returns:
            Tuple of (min, max) feasible values, or None if unbounded
        """
        min_val = float('-inf')
        max_val = float('inf')

        for constraint in self.constraints:
            if isinstance(constraint, RangeConstraint):
                if constraint.param_name == param_name:
                    min_val = max(min_val, constraint.min_value)
                    max_val = min(max_val, constraint.max_value)

        if min_val == float('-inf') and max_val == float('inf'):
            return None

        return (min_val, max_val)


# =============================================================================
# Utility Functions
# =============================================================================

def create_missile_validator() -> DesignConstraintEngine:
    """Create a pre-configured missile design validator"""
    engine = DesignConstraintEngine()
    engine.add_missile_constraints()
    return engine


def create_aircraft_validator() -> DesignConstraintEngine:
    """Create a pre-configured aircraft design validator"""
    engine = DesignConstraintEngine()
    engine.add_aircraft_constraints()
    return engine


def validate_missile_design(parameters: Dict[str, float]) -> ConstraintSet:
    """
    Convenience function to validate missile design parameters.

    Args:
        parameters: Dictionary with keys like 'total_length', 'body_diameter', etc.

    Returns:
        ConstraintSet with validation results
    """
    # Calculate derived parameters
    if 'total_length' in parameters and 'body_diameter' in parameters:
        parameters['fin_span_ratio'] = parameters.get(
            'fin_span', parameters['body_diameter'] * 0.5
        ) / parameters['body_diameter']

    if 'fin_tip_chord' in parameters and 'fin_root_chord' in parameters:
        parameters['fin_taper_ratio'] = (
            parameters['fin_tip_chord'] / parameters['fin_root_chord']
        )

    engine = create_missile_validator()
    return engine.validate(parameters)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CAD PARAMETRIC CONSTRAINTS - DEMO")
    print("=" * 60)

    # Example: Validate PL-15 parameters
    pl15_params = {
        "total_length": 4.0,
        "body_diameter": 0.203,
        "nose_length": 0.5,
        "fin_span": 0.15,
        "fin_span_ratio": 0.15 / 0.203,
        "fin_sweep_deg": 45,
        "fin_taper_ratio": 0.4,
        "total_mass_kg": 210,
        "rcs_frontal_dbsm": -18.0,
    }

    print("\n[1] PL-15 Missile Validation")
    print("-" * 40)

    results = validate_missile_design(pl15_params)
    print(results.to_report())

    # Example: Invalid design
    print("\n[2] Invalid Missile Design (too stubby)")
    print("-" * 40)

    bad_params = {
        "total_length": 1.0,
        "body_diameter": 0.4,  # L/D = 2.5, too low
        "nose_length": 0.1,   # Too short
        "fin_span_ratio": 0.2,
        "fin_sweep_deg": 15,  # Too low for stability
        "total_mass_kg": 500,
    }

    bad_results = validate_missile_design(bad_params)
    print(bad_results.to_report())

    # Get feasible region
    print("\n[3] Feasible Region Analysis")
    print("-" * 40)

    engine = create_missile_validator()
    for param in ["total_length", "body_diameter", "fin_sweep_deg"]:
        region = engine.get_feasible_region(param)
        if region:
            print(f"  {param}: [{region[0]}, {region[1]}]")

    print("\n" + "=" * 60)
    print("Constraint validation demo complete.")
    print("=" * 60)
