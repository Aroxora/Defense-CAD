#!/usr/bin/env python3
"""
Calculation Logger Module

Comprehensive logging system for CAD calculations, algorithms, and derived data.
Designed for CI/CD integration with structured output formats.

Logs include:
- Algorithm descriptions and mathematical basis
- Input parameters with validation status
- Intermediate calculation steps
- Output results with confidence levels
- Performance metrics
- Error tracking

Output formats:
- Console (human-readable)
- JSON (machine-readable)
- Markdown (documentation)
- GitHub Actions annotations

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
import json
import time
import sys
import os
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from contextlib import contextmanager
import traceback


# =============================================================================
# LOG LEVELS AND FORMATS
# =============================================================================

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    ALGORITHM = "ALGORITHM"
    CALCULATION = "CALCULATION"
    RESULT = "RESULT"
    VALIDATION = "VALIDATION"


class OutputFormat(Enum):
    CONSOLE = "console"
    JSON = "json"
    MARKDOWN = "markdown"
    GITHUB_ACTIONS = "github_actions"


# =============================================================================
# LOG ENTRY STRUCTURES
# =============================================================================

@dataclass
class AlgorithmLog:
    """Log entry for algorithm documentation"""
    name: str
    description: str
    mathematical_basis: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    complexity: str  # O(n), O(n^2), etc.
    limitations: List[str]
    references: List[str]
    execution_time_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class CalculationLog:
    """Log entry for individual calculations"""
    name: str
    formula: str
    inputs: Dict[str, float]
    intermediate_steps: List[Dict[str, Any]]
    result: float
    unit: str
    confidence: float
    validation_status: str
    notes: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ValidationLog:
    """Log entry for validation results"""
    component: str
    parameter: str
    value: Any
    expected_range: tuple
    is_valid: bool
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class PerformanceLog:
    """Log entry for performance metrics"""
    operation: str
    execution_time_ms: float
    memory_used_mb: float
    triangles_generated: int
    triangles_per_second: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# =============================================================================
# MAIN LOGGER CLASS
# =============================================================================

class CalculationLogger:
    """
    Comprehensive logger for CAD calculations and algorithms.

    Features:
    - Multi-format output (console, JSON, Markdown, GitHub Actions)
    - Algorithm documentation
    - Calculation step tracking
    - Validation logging
    - Performance metrics
    - CI/CD integration
    """

    def __init__(self,
                 name: str = "PLA-CAD",
                 output_formats: List[OutputFormat] = None,
                 log_file: str = None,
                 verbose: bool = True):
        self.name = name
        self.output_formats = output_formats or [OutputFormat.CONSOLE]
        self.log_file = log_file
        self.verbose = verbose

        # Log storage
        self.algorithms: List[AlgorithmLog] = []
        self.calculations: List[CalculationLog] = []
        self.validations: List[ValidationLog] = []
        self.performance: List[PerformanceLog] = []
        self.errors: List[Dict[str, Any]] = []

        # Timing
        self.start_time = time.time()
        self.section_times: Dict[str, float] = {}

        # GitHub Actions detection
        self.is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'

        # Start session
        self._log_session_start()

    def _log_session_start(self):
        """Log session initialization"""
        self._output(LogLevel.INFO, f"{'='*80}")
        self._output(LogLevel.INFO, f"CALCULATION LOGGER INITIALIZED: {self.name}")
        self._output(LogLevel.INFO, f"Timestamp: {datetime.utcnow().isoformat()}")
        self._output(LogLevel.INFO, f"Python: {sys.version}")
        self._output(LogLevel.INFO, f"NumPy: {np.__version__}")
        self._output(LogLevel.INFO, f"CI/CD Mode: {self.is_github_actions}")
        self._output(LogLevel.INFO, f"{'='*80}")

    def _output(self, level: LogLevel, message: str, **kwargs):
        """Output message in configured formats"""
        timestamp = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]

        for fmt in self.output_formats:
            if fmt == OutputFormat.CONSOLE:
                if self.verbose or level in [LogLevel.ERROR, LogLevel.CRITICAL, LogLevel.RESULT]:
                    print(f"[{timestamp}] [{level.value:12}] {message}")

            elif fmt == OutputFormat.GITHUB_ACTIONS and self.is_github_actions:
                if level == LogLevel.ERROR:
                    print(f"::error::{message}")
                elif level == LogLevel.WARNING:
                    print(f"::warning::{message}")
                elif level == LogLevel.DEBUG:
                    print(f"::debug::{message}")
                else:
                    print(message)

        # Write to log file if configured
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"[{timestamp}] [{level.value}] {message}\n")

    # =========================================================================
    # ALGORITHM LOGGING
    # =========================================================================

    def log_algorithm(self,
                      name: str,
                      description: str,
                      mathematical_basis: str,
                      inputs: Dict[str, Any],
                      complexity: str = "O(n)",
                      limitations: List[str] = None,
                      references: List[str] = None) -> 'AlgorithmContext':
        """
        Log algorithm with full documentation.

        Returns context manager for timing.
        """
        return AlgorithmContext(
            logger=self,
            name=name,
            description=description,
            mathematical_basis=mathematical_basis,
            inputs=inputs,
            complexity=complexity,
            limitations=limitations or [],
            references=references or []
        )

    def _record_algorithm(self, algo: AlgorithmLog):
        """Record completed algorithm log"""
        self.algorithms.append(algo)

        self._output(LogLevel.ALGORITHM, f"")
        self._output(LogLevel.ALGORITHM, f"{'─'*80}")
        self._output(LogLevel.ALGORITHM, f"ALGORITHM: {algo.name}")
        self._output(LogLevel.ALGORITHM, f"{'─'*80}")
        self._output(LogLevel.ALGORITHM, f"Description: {algo.description}")
        self._output(LogLevel.ALGORITHM, f"Mathematical Basis:")
        for line in algo.mathematical_basis.split('\n'):
            self._output(LogLevel.ALGORITHM, f"  {line}")
        self._output(LogLevel.ALGORITHM, f"Complexity: {algo.complexity}")
        self._output(LogLevel.ALGORITHM, f"Execution Time: {algo.execution_time_ms:.2f} ms")

        self._output(LogLevel.ALGORITHM, f"Inputs:")
        for key, val in algo.inputs.items():
            self._output(LogLevel.ALGORITHM, f"  {key}: {val}")

        self._output(LogLevel.ALGORITHM, f"Outputs:")
        for key, val in algo.outputs.items():
            if isinstance(val, float):
                self._output(LogLevel.ALGORITHM, f"  {key}: {val:.6g}")
            else:
                self._output(LogLevel.ALGORITHM, f"  {key}: {val}")

        if algo.limitations:
            self._output(LogLevel.ALGORITHM, f"Limitations:")
            for lim in algo.limitations:
                self._output(LogLevel.ALGORITHM, f"  - {lim}")

        self._output(LogLevel.ALGORITHM, f"{'─'*80}")

    # =========================================================================
    # CALCULATION LOGGING
    # =========================================================================

    def log_calculation(self,
                        name: str,
                        formula: str,
                        inputs: Dict[str, float],
                        result: float,
                        unit: str,
                        confidence: float = 1.0,
                        intermediate_steps: List[Dict] = None,
                        notes: str = ""):
        """Log individual calculation with all steps"""

        # Validate result
        if np.isnan(result) or np.isinf(result):
            validation_status = "INVALID"
            self._output(LogLevel.ERROR, f"Calculation '{name}' produced invalid result: {result}")
        else:
            validation_status = "VALID"

        calc = CalculationLog(
            name=name,
            formula=formula,
            inputs=inputs,
            intermediate_steps=intermediate_steps or [],
            result=result,
            unit=unit,
            confidence=confidence,
            validation_status=validation_status,
            notes=notes
        )

        self.calculations.append(calc)

        self._output(LogLevel.CALCULATION, f"")
        self._output(LogLevel.CALCULATION, f"CALC: {name}")
        self._output(LogLevel.CALCULATION, f"  Formula: {formula}")
        self._output(LogLevel.CALCULATION, f"  Inputs: {inputs}")

        if intermediate_steps:
            self._output(LogLevel.CALCULATION, f"  Steps:")
            for i, step in enumerate(intermediate_steps):
                self._output(LogLevel.CALCULATION, f"    {i+1}. {step}")

        self._output(LogLevel.CALCULATION, f"  Result: {result:.6g} {unit}")
        self._output(LogLevel.CALCULATION, f"  Confidence: {confidence:.0%}")
        self._output(LogLevel.CALCULATION, f"  Status: {validation_status}")

    # =========================================================================
    # VALIDATION LOGGING
    # =========================================================================

    def log_validation(self,
                       component: str,
                       parameter: str,
                       value: Any,
                       min_val: float = None,
                       max_val: float = None,
                       expected_type: type = None) -> bool:
        """Log parameter validation"""

        is_valid = True
        error_msg = ""

        # Type check
        if expected_type and not isinstance(value, expected_type):
            is_valid = False
            error_msg = f"Expected {expected_type.__name__}, got {type(value).__name__}"

        # Range check
        if isinstance(value, (int, float)):
            if min_val is not None and value < min_val:
                is_valid = False
                error_msg = f"Value {value} below minimum {min_val}"
            if max_val is not None and value > max_val:
                is_valid = False
                error_msg = f"Value {value} above maximum {max_val}"
            if np.isnan(value) or np.isinf(value):
                is_valid = False
                error_msg = f"Value is NaN or Inf"

        expected_range = (min_val, max_val)

        val_log = ValidationLog(
            component=component,
            parameter=parameter,
            value=value,
            expected_range=expected_range,
            is_valid=is_valid,
            error_message=error_msg
        )

        self.validations.append(val_log)

        level = LogLevel.VALIDATION if is_valid else LogLevel.ERROR
        status = "✓ PASS" if is_valid else "✗ FAIL"

        self._output(level, f"VALIDATE: {component}.{parameter} = {value} [{status}]")
        if error_msg:
            self._output(LogLevel.ERROR, f"  Error: {error_msg}")

        return is_valid

    # =========================================================================
    # PERFORMANCE LOGGING
    # =========================================================================

    def log_performance(self,
                        operation: str,
                        execution_time_ms: float,
                        triangles_generated: int = 0,
                        memory_mb: float = 0.0):
        """Log performance metrics"""

        triangles_per_sec = (triangles_generated / execution_time_ms * 1000) if execution_time_ms > 0 else 0

        perf = PerformanceLog(
            operation=operation,
            execution_time_ms=execution_time_ms,
            memory_used_mb=memory_mb,
            triangles_generated=triangles_generated,
            triangles_per_second=triangles_per_sec
        )

        self.performance.append(perf)

        self._output(LogLevel.INFO, f"PERF: {operation}")
        self._output(LogLevel.INFO, f"  Time: {execution_time_ms:.2f} ms")
        if triangles_generated > 0:
            self._output(LogLevel.INFO, f"  Triangles: {triangles_generated}")
            self._output(LogLevel.INFO, f"  Rate: {triangles_per_sec:.0f} tri/sec")

    # =========================================================================
    # RESULT LOGGING
    # =========================================================================

    def log_result(self, name: str, value: Any, unit: str = "",
                   confidence: float = 1.0, notes: str = ""):
        """Log final result"""
        self._output(LogLevel.RESULT, f"")
        self._output(LogLevel.RESULT, f"{'═'*60}")
        self._output(LogLevel.RESULT, f"RESULT: {name}")
        self._output(LogLevel.RESULT, f"  Value: {value} {unit}")
        self._output(LogLevel.RESULT, f"  Confidence: {confidence:.0%}")
        if notes:
            self._output(LogLevel.RESULT, f"  Notes: {notes}")
        self._output(LogLevel.RESULT, f"{'═'*60}")

    # =========================================================================
    # ERROR LOGGING
    # =========================================================================

    def log_error(self, error: Exception, context: str = ""):
        """Log error with full traceback"""
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }

        self.errors.append(error_info)

        self._output(LogLevel.ERROR, f"{'!'*60}")
        self._output(LogLevel.ERROR, f"ERROR: {type(error).__name__}")
        self._output(LogLevel.ERROR, f"  Message: {error}")
        self._output(LogLevel.ERROR, f"  Context: {context}")
        self._output(LogLevel.ERROR, f"{'!'*60}")

    # =========================================================================
    # SECTION TIMING
    # =========================================================================

    @contextmanager
    def section(self, name: str):
        """Context manager for timing sections"""
        self._output(LogLevel.INFO, f"")
        self._output(LogLevel.INFO, f"{'━'*80}")
        self._output(LogLevel.INFO, f"SECTION: {name}")
        self._output(LogLevel.INFO, f"{'━'*80}")

        start = time.time()
        try:
            yield
        finally:
            elapsed = (time.time() - start) * 1000
            self.section_times[name] = elapsed
            self._output(LogLevel.INFO, f"Section '{name}' completed in {elapsed:.2f} ms")
            self._output(LogLevel.INFO, f"{'━'*80}")

    # =========================================================================
    # REPORT GENERATION
    # =========================================================================

    def generate_json_report(self) -> str:
        """Generate JSON report of all logs"""
        report = {
            "session": {
                "name": self.name,
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "total_time_ms": (time.time() - self.start_time) * 1000,
                "is_ci": self.is_github_actions
            },
            "summary": {
                "algorithms_run": len(self.algorithms),
                "calculations_performed": len(self.calculations),
                "validations_run": len(self.validations),
                "validations_passed": sum(1 for v in self.validations if v.is_valid),
                "validations_failed": sum(1 for v in self.validations if not v.is_valid),
                "errors_encountered": len(self.errors)
            },
            "algorithms": [asdict(a) for a in self.algorithms],
            "calculations": [asdict(c) for c in self.calculations],
            "validations": [asdict(v) for v in self.validations],
            "performance": [asdict(p) for p in self.performance],
            "errors": self.errors,
            "section_times": self.section_times
        }

        return json.dumps(report, indent=2, default=str)

    def generate_markdown_report(self) -> str:
        """Generate Markdown report"""
        lines = []

        lines.append("# PLA CAD Calculation Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.utcnow().isoformat()}")
        lines.append(f"**Total Runtime:** {(time.time() - self.start_time)*1000:.2f} ms")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Algorithms Run: {len(self.algorithms)}")
        lines.append(f"- Calculations: {len(self.calculations)}")
        lines.append(f"- Validations: {len(self.validations)} "
                    f"({sum(1 for v in self.validations if v.is_valid)} passed)")
        lines.append(f"- Errors: {len(self.errors)}")
        lines.append("")

        # Algorithms
        if self.algorithms:
            lines.append("## Algorithms")
            lines.append("")
            for algo in self.algorithms:
                lines.append(f"### {algo.name}")
                lines.append("")
                lines.append(f"**Description:** {algo.description}")
                lines.append("")
                lines.append("**Mathematical Basis:**")
                lines.append("```")
                lines.append(algo.mathematical_basis)
                lines.append("```")
                lines.append("")
                lines.append(f"**Complexity:** {algo.complexity}")
                lines.append(f"**Execution Time:** {algo.execution_time_ms:.2f} ms")
                lines.append("")

                if algo.limitations:
                    lines.append("**Limitations:**")
                    for lim in algo.limitations:
                        lines.append(f"- {lim}")
                    lines.append("")

        # Calculations
        if self.calculations:
            lines.append("## Calculations")
            lines.append("")
            lines.append("| Name | Formula | Result | Unit | Confidence |")
            lines.append("|------|---------|--------|------|------------|")
            for calc in self.calculations:
                lines.append(f"| {calc.name} | `{calc.formula}` | {calc.result:.6g} | {calc.unit} | {calc.confidence:.0%} |")
            lines.append("")

        # Validations
        failed_validations = [v for v in self.validations if not v.is_valid]
        if failed_validations:
            lines.append("## Failed Validations")
            lines.append("")
            for val in failed_validations:
                lines.append(f"- **{val.component}.{val.parameter}**: {val.error_message}")
            lines.append("")

        # Performance
        if self.performance:
            lines.append("## Performance")
            lines.append("")
            lines.append("| Operation | Time (ms) | Triangles | Rate (tri/s) |")
            lines.append("|-----------|-----------|-----------|--------------|")
            for perf in self.performance:
                lines.append(f"| {perf.operation} | {perf.execution_time_ms:.2f} | {perf.triangles_generated} | {perf.triangles_per_second:.0f} |")
            lines.append("")

        # Errors
        if self.errors:
            lines.append("## Errors")
            lines.append("")
            for err in self.errors:
                lines.append(f"### {err['type']}")
                lines.append(f"**Message:** {err['message']}")
                lines.append(f"**Context:** {err['context']}")
                lines.append("")

        return "\n".join(lines)

    def generate_github_summary(self) -> str:
        """Generate GitHub Actions job summary"""
        passed = sum(1 for v in self.validations if v.is_valid)
        failed = sum(1 for v in self.validations if not v.is_valid)

        lines = []
        lines.append("## 🔬 PLA CAD Validation Results")
        lines.append("")

        # Status badge
        if failed == 0 and len(self.errors) == 0:
            lines.append("### ✅ All Validations Passed")
        else:
            lines.append("### ⚠️ Validation Issues Found")

        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Algorithms | {len(self.algorithms)} |")
        lines.append(f"| Calculations | {len(self.calculations)} |")
        lines.append(f"| Validations Passed | {passed} |")
        lines.append(f"| Validations Failed | {failed} |")
        lines.append(f"| Errors | {len(self.errors)} |")
        lines.append(f"| Total Runtime | {(time.time()-self.start_time)*1000:.0f} ms |")

        return "\n".join(lines)

    def finalize(self):
        """Finalize logging session and output reports"""
        total_time = (time.time() - self.start_time) * 1000

        self._output(LogLevel.INFO, f"")
        self._output(LogLevel.INFO, f"{'═'*80}")
        self._output(LogLevel.INFO, f"SESSION COMPLETE")
        self._output(LogLevel.INFO, f"{'═'*80}")
        self._output(LogLevel.INFO, f"Total Runtime: {total_time:.2f} ms")
        self._output(LogLevel.INFO, f"Algorithms: {len(self.algorithms)}")
        self._output(LogLevel.INFO, f"Calculations: {len(self.calculations)}")
        self._output(LogLevel.INFO, f"Validations: {len(self.validations)} "
                    f"({sum(1 for v in self.validations if v.is_valid)} passed)")
        self._output(LogLevel.INFO, f"Errors: {len(self.errors)}")
        self._output(LogLevel.INFO, f"{'═'*80}")

        # Write GitHub Actions summary if in CI
        if self.is_github_actions:
            summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
            if summary_file:
                with open(summary_file, 'a') as f:
                    f.write(self.generate_github_summary())


# =============================================================================
# ALGORITHM CONTEXT MANAGER
# =============================================================================

class AlgorithmContext:
    """Context manager for algorithm logging with timing"""

    def __init__(self, logger: CalculationLogger, name: str, description: str,
                 mathematical_basis: str, inputs: Dict[str, Any],
                 complexity: str, limitations: List[str], references: List[str]):
        self.logger = logger
        self.name = name
        self.description = description
        self.mathematical_basis = mathematical_basis
        self.inputs = inputs
        self.complexity = complexity
        self.limitations = limitations
        self.references = references
        self.outputs = {}
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.time() - self.start_time) * 1000

        algo = AlgorithmLog(
            name=self.name,
            description=self.description,
            mathematical_basis=self.mathematical_basis,
            inputs=self.inputs,
            outputs=self.outputs,
            complexity=self.complexity,
            limitations=self.limitations,
            references=self.references,
            execution_time_ms=elapsed
        )

        self.logger._record_algorithm(algo)
        return False

    def set_output(self, key: str, value: Any):
        """Set algorithm output"""
        self.outputs[key] = value


# =============================================================================
# GLOBAL LOGGER INSTANCE
# =============================================================================

_global_logger: Optional[CalculationLogger] = None


def get_logger() -> CalculationLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = CalculationLogger(
            output_formats=[OutputFormat.CONSOLE, OutputFormat.GITHUB_ACTIONS]
        )
    return _global_logger


def init_logger(name: str = "PLA-CAD", **kwargs) -> CalculationLogger:
    """Initialize global logger with custom settings"""
    global _global_logger
    _global_logger = CalculationLogger(name=name, **kwargs)
    return _global_logger


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Initialize logger
    logger = init_logger(
        name="CAD-Test",
        output_formats=[OutputFormat.CONSOLE],
        verbose=True
    )

    # Example algorithm logging
    with logger.log_algorithm(
        name="Tangent Ogive Generation",
        description="Generate tangent ogive nose cone geometry",
        mathematical_basis="ρ = (L² + R²) / (2R)\ny(x) = √(ρ² - (L-x)²) + R - ρ",
        inputs={"length": 1.0, "base_radius": 0.5},
        complexity="O(n²) where n = resolution",
        limitations=["Singular at x=0", "Assumes circular cross-section"],
        references=["MIL-HDBK-762"]
    ) as algo:
        # Simulate work
        time.sleep(0.1)
        algo.set_output("triangles", 512)
        algo.set_output("surface_area", 1.234)

    # Example calculation logging
    logger.log_calculation(
        name="Ogive Radius",
        formula="ρ = (L² + R²) / (2R)",
        inputs={"L": 1.0, "R": 0.5},
        result=1.25,
        unit="m",
        confidence=0.95,
        intermediate_steps=[
            {"step": "L² = 1.0"},
            {"step": "R² = 0.25"},
            {"step": "L² + R² = 1.25"},
            {"step": "2R = 1.0"},
            {"step": "ρ = 1.25"}
        ]
    )

    # Example validation logging
    logger.log_validation("Ogive", "length", 1.0, min_val=0.1, max_val=10.0)
    logger.log_validation("Ogive", "radius", 0.5, min_val=0.01, max_val=5.0)
    logger.log_validation("Ogive", "bad_value", float('nan'), min_val=0, max_val=1)

    # Finalize and generate reports
    logger.finalize()

    # Generate reports
    print("\n" + "="*80)
    print("JSON REPORT PREVIEW:")
    print("="*80)
    json_report = logger.generate_json_report()
    print(json_report[:2000] + "..." if len(json_report) > 2000 else json_report)

    print("\n" + "="*80)
    print("MARKDOWN REPORT:")
    print("="*80)
    print(logger.generate_markdown_report())
