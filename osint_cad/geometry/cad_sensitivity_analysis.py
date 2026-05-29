#!/usr/bin/env python3
"""
CAD-Driven Sensitivity Analysis Module

Provides systematic sensitivity analysis of geometric parameters on
system performance metrics including RCS, detection range, and
engagement outcomes.

Key Features:
- Single-parameter sweeps with automated bounds
- Multi-parameter interaction analysis
- Monte Carlo uncertainty propagation
- Gradient estimation for optimization
- Integration with kill chain models
- Automated reporting and visualization

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Callable, Any
from enum import Enum
import copy

from osint_cad.geometry.cad_geometry import MissileCADModel, create_pl15_cad_model, create_aim120_cad_model
from osint_cad.geometry.cad_rcs_calculator import CADRCSIntegrator, MaterialProperties, RCSSweepResult
from osint_cad.geometry.cad_constraints import DesignConstraintEngine, create_missile_validator


class SensitivityMetric(Enum):
    """Output metrics for sensitivity analysis"""
    RCS_FRONTAL = "rcs_frontal_dbsm"
    RCS_BEAM = "rcs_beam_dbsm"
    RCS_TAIL = "rcs_tail_dbsm"
    RCS_MEAN = "rcs_mean_dbsm"
    VOLUME = "volume_m3"
    SURFACE_AREA = "surface_area_m2"
    FINENESS_RATIO = "fineness_ratio"
    MASS_ESTIMATE = "mass_estimate_kg"


@dataclass
class SensitivityPoint:
    """Single point in sensitivity analysis"""
    parameter_value: float
    metrics: Dict[str, float]
    is_valid: bool
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class SensitivityResult:
    """Result of single-parameter sensitivity analysis"""
    parameter_name: str
    parameter_values: List[float]
    points: List[SensitivityPoint]
    gradient_estimates: Dict[str, float]  # d(metric)/d(param) at nominal
    nominal_value: float
    nominal_metrics: Dict[str, float]

    def get_metric_values(self, metric: str) -> np.ndarray:
        """Get array of metric values across sweep"""
        return np.array([p.metrics.get(metric, np.nan) for p in self.points])

    def get_valid_points(self) -> List[SensitivityPoint]:
        """Get only valid design points"""
        return [p for p in self.points if p.is_valid]

    def to_report(self) -> str:
        """Generate sensitivity report"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"SENSITIVITY ANALYSIS: {self.parameter_name}")
        lines.append("=" * 70)
        lines.append(f"Nominal value: {self.nominal_value}")
        lines.append(f"Sweep range: [{min(self.parameter_values):.4f}, "
                    f"{max(self.parameter_values):.4f}]")
        lines.append(f"Valid designs: {len(self.get_valid_points())}/{len(self.points)}")
        lines.append("")

        # Gradient estimates
        lines.append("GRADIENT ESTIMATES (at nominal):")
        lines.append("-" * 40)
        for metric, gradient in self.gradient_estimates.items():
            lines.append(f"  d({metric})/d({self.parameter_name}) = {gradient:+.4f}")
        lines.append("")

        # Metric ranges
        lines.append("METRIC RANGES:")
        lines.append("-" * 40)
        for metric in self.nominal_metrics.keys():
            values = self.get_metric_values(metric)
            valid_values = values[~np.isnan(values)]
            if len(valid_values) > 0:
                lines.append(f"  {metric}:")
                lines.append(f"    Min: {np.min(valid_values):.4f}")
                lines.append(f"    Max: {np.max(valid_values):.4f}")
                lines.append(f"    Range: {np.max(valid_values) - np.min(valid_values):.4f}")

        lines.append("=" * 70)
        return "\n".join(lines)


@dataclass
class InteractionResult:
    """Result of two-parameter interaction analysis"""
    param1_name: str
    param2_name: str
    param1_values: np.ndarray
    param2_values: np.ndarray
    metric_grid: np.ndarray  # 2D array of metric values
    metric_name: str
    interaction_strength: float  # Measure of non-additive effects


@dataclass
class MonteCarloResult:
    """Result of Monte Carlo uncertainty analysis"""
    n_samples: int
    parameter_distributions: Dict[str, Tuple[float, float]]  # (mean, std)
    metric_statistics: Dict[str, Dict[str, float]]  # {metric: {mean, std, p5, p95}}
    samples: np.ndarray  # Raw samples if stored


class CADSensitivityAnalyzer:
    """
    Comprehensive sensitivity analysis for CAD-based defense models.

    Integrates with MissileCADModel and CADRCSIntegrator to analyze
    how geometric parameters affect RCS and performance metrics.
    """

    def __init__(self, base_model: MissileCADModel,
                 resolution: int = 16,
                 frequency_ghz: float = 10.0):
        """
        Initialize sensitivity analyzer.

        Args:
            base_model: Baseline CAD model to analyze
            resolution: Mesh resolution for calculations
            frequency_ghz: Radar frequency for RCS calculations
        """
        self.base_model = copy.deepcopy(base_model)
        self.resolution = resolution
        self.frequency_ghz = frequency_ghz
        self.constraint_engine = create_missile_validator()

    def _create_model_copy(self) -> MissileCADModel:
        """Create a deep copy of the base model"""
        return copy.deepcopy(self.base_model)

    def _calculate_metrics(self, model: MissileCADModel) -> Dict[str, float]:
        """Calculate all metrics for a given model"""
        try:
            integrator = CADRCSIntegrator(model)
            geometry = integrator.build_geometry(
                resolution=self.resolution,
                material=MaterialProperties.aluminum()
            )

            # Calculate RCS at key aspects
            frontal = integrator.rcs_calculator.calculate_rcs(0, 0, self.frequency_ghz)
            beam = integrator.rcs_calculator.calculate_rcs(90, 0, self.frequency_ghz)
            tail = integrator.rcs_calculator.calculate_rcs(180, 0, self.frequency_ghz)

            # Calculate sweep for mean
            sweep = integrator.rcs_calculator.calculate_rcs_sweep(
                azimuth_range=(0, 180),
                num_points=19,
                frequency_ghz=self.frequency_ghz
            )

            # Fineness ratio
            fineness = model.total_length / model.body_diameter

            # Mass estimate
            mass_props = model.get_mass_properties()

            return {
                SensitivityMetric.RCS_FRONTAL.value: frontal.rcs_dbsm,
                SensitivityMetric.RCS_BEAM.value: beam.rcs_dbsm,
                SensitivityMetric.RCS_TAIL.value: tail.rcs_dbsm,
                SensitivityMetric.RCS_MEAN.value: sweep.mean_rcs_dbsm,
                SensitivityMetric.VOLUME.value: geometry.total_volume,
                SensitivityMetric.SURFACE_AREA.value: geometry.total_surface_area,
                SensitivityMetric.FINENESS_RATIO.value: fineness,
                SensitivityMetric.MASS_ESTIMATE.value: mass_props['estimated_mass_kg'],
            }
        except Exception as e:
            # Return NaN for all metrics on error
            return {m.value: np.nan for m in SensitivityMetric}

    def _validate_model(self, model: MissileCADModel) -> Tuple[bool, List[str]]:
        """Validate model against constraints"""
        params = model.get_all_parameters()
        # Add derived parameters
        params['fin_span_ratio'] = model.fin_span / model.body_diameter

        results = self.constraint_engine.validate(params)
        errors = [r.message for r in results.errors]
        return results.all_satisfied, errors

    def single_parameter_sweep(self,
                               parameter_name: str,
                               values: List[float] = None,
                               relative_range: float = 0.3,
                               num_points: int = 11) -> SensitivityResult:
        """
        Perform sensitivity analysis on a single parameter.

        Args:
            parameter_name: Name of parameter to vary
            values: Explicit list of values to test (optional)
            relative_range: If values not given, sweep ±relative_range around nominal
            num_points: Number of points in sweep

        Returns:
            SensitivityResult with sweep data
        """
        # Get nominal value
        nominal = getattr(self.base_model, parameter_name)

        # Generate sweep values if not provided
        if values is None:
            min_val = nominal * (1 - relative_range)
            max_val = nominal * (1 + relative_range)
            values = np.linspace(min_val, max_val, num_points).tolist()

        # Calculate nominal metrics
        nominal_metrics = self._calculate_metrics(self.base_model)

        # Perform sweep
        points = []
        for value in values:
            model = self._create_model_copy()
            setattr(model, parameter_name, value)

            # Validate
            is_valid, errors = self._validate_model(model)

            # Calculate metrics
            metrics = self._calculate_metrics(model)

            points.append(SensitivityPoint(
                parameter_value=value,
                metrics=metrics,
                is_valid=is_valid,
                validation_errors=errors
            ))

        # Estimate gradients at nominal
        gradients = self._estimate_gradients(parameter_name, nominal, nominal_metrics)

        return SensitivityResult(
            parameter_name=parameter_name,
            parameter_values=values,
            points=points,
            gradient_estimates=gradients,
            nominal_value=nominal,
            nominal_metrics=nominal_metrics
        )

    def _estimate_gradients(self, parameter_name: str,
                            nominal_value: float,
                            nominal_metrics: Dict[str, float]) -> Dict[str, float]:
        """Estimate gradients using central difference"""
        delta = nominal_value * 0.01  # 1% perturbation

        # Plus perturbation
        model_plus = self._create_model_copy()
        setattr(model_plus, parameter_name, nominal_value + delta)
        metrics_plus = self._calculate_metrics(model_plus)

        # Minus perturbation
        model_minus = self._create_model_copy()
        setattr(model_minus, parameter_name, nominal_value - delta)
        metrics_minus = self._calculate_metrics(model_minus)

        # Central difference
        gradients = {}
        for metric in nominal_metrics.keys():
            if not np.isnan(metrics_plus.get(metric, np.nan)) and \
               not np.isnan(metrics_minus.get(metric, np.nan)):
                gradient = (metrics_plus[metric] - metrics_minus[metric]) / (2 * delta)
                gradients[metric] = gradient
            else:
                gradients[metric] = np.nan

        return gradients

    def multi_parameter_sweep(self,
                              parameters: List[str],
                              relative_range: float = 0.2,
                              points_per_param: int = 5) -> Dict[str, SensitivityResult]:
        """
        Perform sensitivity analysis on multiple parameters.

        Args:
            parameters: List of parameter names
            relative_range: Sweep range as fraction of nominal
            points_per_param: Points per parameter sweep

        Returns:
            Dictionary of parameter name to SensitivityResult
        """
        results = {}
        for param in parameters:
            results[param] = self.single_parameter_sweep(
                param, relative_range=relative_range, num_points=points_per_param
            )
        return results

    def interaction_analysis(self,
                             param1: str,
                             param2: str,
                             metric: SensitivityMetric,
                             n_points: int = 5,
                             relative_range: float = 0.2) -> InteractionResult:
        """
        Analyze interaction between two parameters.

        Args:
            param1, param2: Parameter names
            metric: Output metric to analyze
            n_points: Points per dimension
            relative_range: Range as fraction of nominal

        Returns:
            InteractionResult with 2D grid of metric values
        """
        nominal1 = getattr(self.base_model, param1)
        nominal2 = getattr(self.base_model, param2)

        values1 = np.linspace(
            nominal1 * (1 - relative_range),
            nominal1 * (1 + relative_range),
            n_points
        )
        values2 = np.linspace(
            nominal2 * (1 - relative_range),
            nominal2 * (1 + relative_range),
            n_points
        )

        metric_grid = np.zeros((n_points, n_points))

        for i, v1 in enumerate(values1):
            for j, v2 in enumerate(values2):
                model = self._create_model_copy()
                setattr(model, param1, v1)
                setattr(model, param2, v2)

                metrics = self._calculate_metrics(model)
                metric_grid[i, j] = metrics.get(metric.value, np.nan)

        # Calculate interaction strength
        # Compare actual grid to sum of marginal effects
        mean_metric = np.nanmean(metric_grid)
        row_effects = np.nanmean(metric_grid, axis=1) - mean_metric
        col_effects = np.nanmean(metric_grid, axis=0) - mean_metric

        additive_grid = mean_metric + row_effects[:, np.newaxis] + col_effects[np.newaxis, :]
        interaction_residuals = metric_grid - additive_grid
        interaction_strength = np.nanstd(interaction_residuals) / np.nanstd(metric_grid)

        return InteractionResult(
            param1_name=param1,
            param2_name=param2,
            param1_values=values1,
            param2_values=values2,
            metric_grid=metric_grid,
            metric_name=metric.value,
            interaction_strength=interaction_strength
        )

    def monte_carlo_analysis(self,
                             parameter_uncertainties: Dict[str, Tuple[float, float]],
                             n_samples: int = 100) -> MonteCarloResult:
        """
        Perform Monte Carlo uncertainty propagation.

        Args:
            parameter_uncertainties: {param_name: (mean, std_dev)}
            n_samples: Number of Monte Carlo samples

        Returns:
            MonteCarloResult with statistics
        """
        # Initialize storage
        all_metrics = {m.value: [] for m in SensitivityMetric}

        for _ in range(n_samples):
            model = self._create_model_copy()

            # Sample parameters
            for param, (mean, std) in parameter_uncertainties.items():
                sampled_value = np.random.normal(mean, std)
                # Ensure positive values for physical parameters
                sampled_value = max(sampled_value, mean * 0.1)
                setattr(model, param, sampled_value)

            # Calculate metrics
            metrics = self._calculate_metrics(model)

            for metric_name, value in metrics.items():
                all_metrics[metric_name].append(value)

        # Calculate statistics
        metric_stats = {}
        for metric_name, values in all_metrics.items():
            values = np.array(values)
            valid_values = values[~np.isnan(values)]

            if len(valid_values) > 0:
                metric_stats[metric_name] = {
                    'mean': np.mean(valid_values),
                    'std': np.std(valid_values),
                    'p5': np.percentile(valid_values, 5),
                    'p95': np.percentile(valid_values, 95),
                    'n_valid': len(valid_values)
                }
            else:
                metric_stats[metric_name] = {
                    'mean': np.nan, 'std': np.nan,
                    'p5': np.nan, 'p95': np.nan, 'n_valid': 0
                }

        return MonteCarloResult(
            n_samples=n_samples,
            parameter_distributions=parameter_uncertainties,
            metric_statistics=metric_stats,
            samples=None  # Don't store raw samples by default
        )

    def generate_comprehensive_report(self,
                                       parameters: List[str] = None) -> str:
        """Generate comprehensive sensitivity report"""
        if parameters is None:
            parameters = ['nose_length', 'body_diameter', 'total_length', 'fin_span']

        lines = []
        lines.append("=" * 80)
        lines.append("COMPREHENSIVE CAD SENSITIVITY ANALYSIS")
        lines.append("=" * 80)
        lines.append(f"Model: {self.base_model.name}")
        lines.append(f"Frequency: {self.frequency_ghz} GHz")
        lines.append(f"Resolution: {self.resolution} mesh elements/dimension")
        lines.append("")

        # Single parameter sweeps
        lines.append("SINGLE-PARAMETER SENSITIVITY")
        lines.append("-" * 80)

        results = self.multi_parameter_sweep(parameters, points_per_param=7)

        # Summary table
        lines.append(f"\n{'Parameter':<20} {'Nominal':<12} "
                    f"{'dRCS_frontal':<15} {'dRCS_beam':<15}")
        lines.append("-" * 65)

        for param, result in results.items():
            frontal_grad = result.gradient_estimates.get(
                SensitivityMetric.RCS_FRONTAL.value, np.nan)
            beam_grad = result.gradient_estimates.get(
                SensitivityMetric.RCS_BEAM.value, np.nan)

            lines.append(f"{param:<20} {result.nominal_value:<12.4f} "
                        f"{frontal_grad:<+15.4f} {beam_grad:<+15.4f}")

        # Key interactions
        lines.append("\n\nPARAMETER INTERACTIONS")
        lines.append("-" * 80)

        if len(parameters) >= 2:
            interaction = self.interaction_analysis(
                parameters[0], parameters[1],
                SensitivityMetric.RCS_FRONTAL,
                n_points=5
            )
            lines.append(f"\n{parameters[0]} x {parameters[1]} interaction:")
            lines.append(f"  Metric: {interaction.metric_name}")
            lines.append(f"  Interaction strength: {interaction.interaction_strength:.3f}")
            lines.append(f"  (0 = purely additive, 1 = strong interaction)")

        # Monte Carlo
        lines.append("\n\nMONTE CARLO UNCERTAINTY ANALYSIS")
        lines.append("-" * 80)

        # Use 10% uncertainty on key parameters
        uncertainties = {}
        for param in parameters[:3]:
            nominal = getattr(self.base_model, param)
            uncertainties[param] = (nominal, nominal * 0.1)

        mc_result = self.monte_carlo_analysis(uncertainties, n_samples=50)

        lines.append(f"\nSamples: {mc_result.n_samples}")
        lines.append(f"\n{'Metric':<25} {'Mean':<12} {'Std':<12} {'5%':<12} {'95%':<12}")
        lines.append("-" * 65)

        for metric, stats in mc_result.metric_statistics.items():
            lines.append(f"{metric:<25} {stats['mean']:<12.3f} {stats['std']:<12.3f} "
                        f"{stats['p5']:<12.3f} {stats['p95']:<12.3f}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


# =============================================================================
# Integration with Kill Chain Models
# =============================================================================

class KillChainSensitivityIntegrator:
    """
    Integrates CAD sensitivity analysis with kill chain simulations.

    Analyzes how geometric changes affect detection range, engagement
    probability, and overall kill chain effectiveness.
    """

    def __init__(self, missile_model: MissileCADModel):
        self.missile_model = missile_model
        self.cad_analyzer = CADSensitivityAnalyzer(missile_model)

    def analyze_detection_range_sensitivity(self,
                                            radar_params: Dict[str, float],
                                            parameter: str,
                                            relative_range: float = 0.2) -> Dict[str, Any]:
        """
        Analyze how geometric parameter affects detection range.

        Args:
            radar_params: Radar parameters (power, gain, frequency)
            parameter: Geometric parameter to vary
            relative_range: Sweep range

        Returns:
            Dictionary with detection range sensitivity
        """
        from osint_cad.physics.rcs_models import calculate_detection_range

        sweep = self.cad_analyzer.single_parameter_sweep(
            parameter, relative_range=relative_range, num_points=11
        )

        detection_ranges = []
        for point in sweep.points:
            if point.is_valid and not np.isnan(point.metrics.get('rcs_frontal_dbsm', np.nan)):
                rcs_m2 = 10 ** (point.metrics['rcs_frontal_dbsm'] / 10)

                det_range = calculate_detection_range(
                    peak_power_kw=radar_params.get('power_kw', 10),
                    antenna_gain_db=radar_params.get('gain_db', 35),
                    frequency_ghz=radar_params.get('frequency_ghz', 10),
                    target_rcs_m2=rcs_m2
                )
                detection_ranges.append(det_range)
            else:
                detection_ranges.append(np.nan)

        return {
            'parameter_values': sweep.parameter_values,
            'detection_ranges_km': detection_ranges,
            'nominal_range_km': detection_ranges[len(detection_ranges)//2],
            'min_range_km': np.nanmin(detection_ranges),
            'max_range_km': np.nanmax(detection_ranges)
        }


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("CAD SENSITIVITY ANALYSIS DEMO")
    print("=" * 80)

    # Create analyzer for PL-15
    pl15 = create_pl15_cad_model()
    analyzer = CADSensitivityAnalyzer(pl15, resolution=12, frequency_ghz=10.0)

    # Single parameter sweep
    print("\n[1] Nose Length Sensitivity Sweep")
    print("-" * 40)

    nose_result = analyzer.single_parameter_sweep(
        "nose_length",
        relative_range=0.4,
        num_points=9
    )

    print(nose_result.to_report())

    # Multi-parameter analysis
    print("\n[2] Multi-Parameter Analysis")
    print("-" * 40)

    params = ['nose_length', 'body_diameter']
    multi_results = analyzer.multi_parameter_sweep(params, points_per_param=5)

    for param, result in multi_results.items():
        print(f"\n{param}:")
        for metric, gradient in result.gradient_estimates.items():
            print(f"  d({metric})/d({param}) = {gradient:+.4f}")

    # Interaction analysis
    print("\n[3] Parameter Interaction Analysis")
    print("-" * 40)

    interaction = analyzer.interaction_analysis(
        'nose_length', 'body_diameter',
        SensitivityMetric.RCS_FRONTAL,
        n_points=5
    )

    print(f"Interaction between {interaction.param1_name} and {interaction.param2_name}")
    print(f"Metric: {interaction.metric_name}")
    print(f"Interaction strength: {interaction.interaction_strength:.3f}")
    print(f"(0 = additive, 1 = strong interaction)")

    # Monte Carlo
    print("\n[4] Monte Carlo Uncertainty Analysis")
    print("-" * 40)

    uncertainties = {
        'nose_length': (0.5, 0.05),
        'body_diameter': (0.203, 0.01),
    }

    mc_result = analyzer.monte_carlo_analysis(uncertainties, n_samples=50)

    print(f"Samples: {mc_result.n_samples}")
    for metric, stats in mc_result.metric_statistics.items():
        if not np.isnan(stats['mean']):
            print(f"  {metric}: {stats['mean']:.2f} +/- {stats['std']:.2f}")

    # Comprehensive report
    print("\n[5] Comprehensive Report")
    print("-" * 40)
    print(analyzer.generate_comprehensive_report(['nose_length', 'body_diameter']))

    print("\n" + "=" * 80)
    print("Sensitivity analysis demo complete.")
    print("=" * 80)
