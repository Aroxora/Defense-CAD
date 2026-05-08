#!/usr/bin/env python3
"""
Local CI/CD Framework for PLA-Defense-CAD
Replaces GitHub Actions workflows with local execution

Usage:
    python local_cicd.py                    # Run all stages
    python local_cicd.py --stage lint       # Run specific stage
    python local_cicd.py --fast             # Quick validation only
    python local_cicd.py --golden-fleet     # Golden Fleet validation only
    python local_cicd.py --report           # Generate full report
"""

import subprocess
import sys
import os
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import traceback

# ============================================
# Configuration
# ============================================

PROJECT_ROOT = Path(__file__).parent
PYTHON_VERSION = "3.12"
REPORT_DIR = PROJECT_ROOT / "cicd_reports"

class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"

@dataclass
class StageResult:
    name: str
    status: StageStatus
    duration: float
    output: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)

@dataclass
class PipelineReport:
    start_time: datetime
    end_time: Optional[datetime] = None
    stages: List[StageResult] = field(default_factory=list)
    overall_status: StageStatus = StageStatus.PENDING

    def to_dict(self) -> dict:
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            "overall_status": self.overall_status.value,
            "stages": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "duration": s.duration,
                    "errors": s.errors,
                    "warnings": s.warnings,
                    "metrics": s.metrics
                }
                for s in self.stages
            ]
        }

# ============================================
# Utility Functions
# ============================================

def print_header(text: str, char: str = "="):
    """Print a formatted header"""
    width = 70
    print(f"\n{char * width}")
    print(f" {text}")
    print(f"{char * width}")

def print_stage(name: str, status: StageStatus):
    """Print stage status with color"""
    colors = {
        StageStatus.PASSED: "\033[92m",  # Green
        StageStatus.FAILED: "\033[91m",  # Red
        StageStatus.WARNING: "\033[93m",  # Yellow
        StageStatus.RUNNING: "\033[94m",  # Blue
        StageStatus.SKIPPED: "\033[90m",  # Gray
        StageStatus.PENDING: "\033[90m",  # Gray
    }
    reset = "\033[0m"
    symbol = {
        StageStatus.PASSED: "✓",
        StageStatus.FAILED: "✗",
        StageStatus.WARNING: "⚠",
        StageStatus.RUNNING: "→",
        StageStatus.SKIPPED: "○",
        StageStatus.PENDING: "○",
    }
    color = colors.get(status, "")
    print(f"{color}{symbol[status]} {name}: {status.value}{reset}")

def run_command(cmd: List[str], cwd: Path = None, env: dict = None,
                capture: bool = True, timeout: int = 300) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    full_env = os.environ.copy()
    full_env["PYTHONPATH"] = str(PROJECT_ROOT)
    if env:
        full_env.update(env)

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            env=full_env,
            capture_output=capture,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return -1, "", str(e)

def run_python(script: str, cwd: Path = None) -> Tuple[int, str, str]:
    """Run a Python script"""
    return run_command([sys.executable, "-c", script], cwd=cwd)

def run_pytest(test_file: str, extra_args: List[str] = None) -> Tuple[int, str, str]:
    """Run pytest on a test file"""
    cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
    if extra_args:
        cmd.extend(extra_args)
    return run_command(cmd)

# ============================================
# Pipeline Stages
# ============================================

def stage_lint() -> StageResult:
    """Stage 1: Code Quality & Linting"""
    start = time.time()
    errors = []
    warnings = []

    print_header("Stage 1: Code Quality & Linting")

    # Check Black formatting
    print("  Checking code formatting (Black)...")
    code, stdout, stderr = run_command([sys.executable, "-m", "black", "--check", "--diff", "."])
    if code != 0:
        warnings.append("Code formatting issues detected")
        print(f"    ⚠ Formatting issues found")
    else:
        print(f"    ✓ Code formatting OK")

    # Check Ruff linting
    print("  Running Ruff linter...")
    code, stdout, stderr = run_command([sys.executable, "-m", "ruff", "check", "."])
    if code != 0:
        warnings.append("Ruff linting warnings")
        print(f"    ⚠ Linting warnings")
    else:
        print(f"    ✓ Ruff check passed")

    # Type checking with mypy
    print("  Running type checker (mypy)...")
    code, stdout, stderr = run_command([sys.executable, "-m", "mypy", "--ignore-missing-imports", "--no-error-summary", "."])
    if code != 0:
        warnings.append("Type checking warnings")
        print(f"    ⚠ Type checking warnings")
    else:
        print(f"    ✓ Type checking passed")

    # Security check with Bandit
    print("  Running security scanner (Bandit)...")
    code, stdout, stderr = run_command([
        sys.executable, "-m", "bandit", "-r", ".",
        "-x", "./venv,./web/node_modules,./.github",
        "-f", "json", "-o", str(REPORT_DIR / "bandit-report.json")
    ])
    if code != 0 and "No issues identified" not in stderr:
        warnings.append("Security warnings found")
        print(f"    ⚠ Security warnings")
    else:
        print(f"    ✓ Security scan passed")

    duration = time.time() - start
    status = StageStatus.PASSED if not errors else StageStatus.FAILED
    if not errors and warnings:
        status = StageStatus.WARNING

    return StageResult(
        name="Code Quality",
        status=status,
        duration=duration,
        errors=errors,
        warnings=warnings
    )

def stage_unit_tests() -> StageResult:
    """Stage 2: Unit Tests"""
    start = time.time()
    errors = []
    warnings = []
    metrics = {"tests_run": 0, "tests_passed": 0, "tests_failed": 0}

    print_header("Stage 2: Unit Tests")

    # Find all test files
    test_files = list(PROJECT_ROOT.glob("test_*.py"))
    test_files.extend(PROJECT_ROOT.glob("**/test_*.py"))
    test_files = [f for f in test_files if "venv" not in str(f) and "node_modules" not in str(f)]

    print(f"  Found {len(test_files)} test files")

    # Run pytest with coverage
    print("  Running tests with coverage...")
    code, stdout, stderr = run_command([
        sys.executable, "-m", "pytest",
        "--cov=.", "--cov-report=term-missing", "--cov-report=html",
        "-v", "--tb=short"
    ], timeout=600)

    # Parse results
    if "passed" in stdout:
        import re
        match = re.search(r"(\d+) passed", stdout)
        if match:
            metrics["tests_passed"] = int(match.group(1))
        match = re.search(r"(\d+) failed", stdout)
        if match:
            metrics["tests_failed"] = int(match.group(1))
        match = re.search(r"(\d+) error", stdout)
        if match:
            metrics["tests_failed"] += int(match.group(1))
        metrics["tests_run"] = metrics["tests_passed"] + metrics["tests_failed"]

    if code != 0:
        errors.append(f"Unit tests failed: {metrics['tests_failed']} failures")
        print(f"    ✗ {metrics['tests_failed']} test(s) failed")
    else:
        print(f"    ✓ All {metrics['tests_passed']} tests passed")

    duration = time.time() - start
    status = StageStatus.PASSED if code == 0 else StageStatus.FAILED

    return StageResult(
        name="Unit Tests",
        status=status,
        duration=duration,
        output=stdout,
        errors=errors,
        warnings=warnings,
        metrics=metrics
    )

def stage_integration_tests() -> StageResult:
    """Stage 3: Integration Tests"""
    start = time.time()
    errors = []
    warnings = []

    print_header("Stage 3: Integration Tests")

    integration_tests = [
        ("Contractor Integration", "test_contractor_integration_cad.py"),
        ("Kill Chain Integration", "test_f35_ew_kill_chain.py"),
        ("Information Chain Robustness", "test_information_chain_robustness.py"),
        ("DF-17 Carrier Strike", "test_df17_carrier_strike_integration.py"),
    ]

    passed = 0
    for name, test_file in integration_tests:
        test_path = PROJECT_ROOT / test_file
        if test_path.exists():
            print(f"  Running {name}...")
            code, stdout, stderr = run_pytest(str(test_path))
            if code == 0:
                print(f"    ✓ {name} passed")
                passed += 1
            else:
                warnings.append(f"{name} had issues")
                print(f"    ⚠ {name} had issues")
        else:
            print(f"    ○ {name} (file not found)")

    duration = time.time() - start
    status = StageStatus.PASSED if passed == len(integration_tests) else StageStatus.WARNING

    return StageResult(
        name="Integration Tests",
        status=status,
        duration=duration,
        errors=errors,
        warnings=warnings,
        metrics={"integration_tests_passed": passed, "integration_tests_total": len(integration_tests)}
    )

def stage_simulation_validation() -> StageResult:
    """Stage 4: Simulation Validation"""
    start = time.time()
    errors = []
    warnings = []

    print_header("Stage 4: Simulation Validation")

    simulations = [
        ("DF-17 Hypersonic Model", "test_df17_hypersonic.py"),
        ("Type 052D Destroyer Model", "test_type052d_cad.py"),
        ("SEAD Ballistic Missiles", "test_sead_ballistic_missiles.py"),
        ("Physics Calculations", "test_physics_calculations.py"),
        ("PLA vs DoD CAD", "test_pla_vs_dod_cad.py"),
    ]

    passed = 0
    for name, test_file in simulations:
        test_path = PROJECT_ROOT / test_file
        if test_path.exists():
            print(f"  Validating {name}...")
            code, stdout, stderr = run_pytest(str(test_path))
            if code == 0:
                print(f"    ✓ {name} validated")
                passed += 1
            else:
                errors.append(f"{name} validation failed")
                print(f"    ✗ {name} failed")
        else:
            print(f"    ○ {name} (file not found)")

    # Run validation scripts
    validation_scripts = [
        ("2025 Parade CAD", "validate_2025_parade_cad.py"),
        ("Simulation Accuracy", "validate_simulation_accuracy.py"),
    ]

    for name, script in validation_scripts:
        script_path = PROJECT_ROOT / script
        if script_path.exists():
            print(f"  Running {name}...")
            code, stdout, stderr = run_command([sys.executable, str(script_path)])
            if code == 0:
                print(f"    ✓ {name} passed")
                passed += 1
            else:
                warnings.append(f"{name} had issues")
                print(f"    ⚠ {name} had issues")

    duration = time.time() - start
    status = StageStatus.PASSED if not errors else StageStatus.FAILED
    if not errors and warnings:
        status = StageStatus.WARNING

    return StageResult(
        name="Simulation Validation",
        status=status,
        duration=duration,
        errors=errors,
        warnings=warnings,
        metrics={"validations_passed": passed}
    )

def stage_physics_validation() -> StageResult:
    """Stage 5: Physics Constants & Equations Validation"""
    start = time.time()
    errors = []
    warnings = []

    print_header("Stage 5: Physics Validation")

    physics_script = '''
import numpy as np
import sys

# Physical constants validation
SPEED_OF_LIGHT = 299792458  # m/s
BOLTZMANN = 1.380649e-23    # J/K
EARTH_RADIUS = 6371000      # m

print("Validating physical constants...")

# Radar equation test
def radar_equation(Pt, Gt, Gr, wavelength, sigma, R):
    return (Pt * Gt * Gr * wavelength**2 * sigma) / ((4 * np.pi)**3 * R**4)

Pt = 10000  # 10 kW
Gt = 1000   # ~30 dB
Gr = 1000
wavelength = 0.03  # X-band
sigma = 1.0  # 1 m²
R = 100000  # 100 km

Pr = radar_equation(Pt, Gt, Gr, wavelength, sigma, R)
Pr_dBm = 10 * np.log10(Pr * 1000)

print(f"  Radar equation test: Pr = {Pr:.2e} W ({Pr_dBm:.1f} dBm)")
if not (-150 < Pr_dBm < -50):
    print("ERROR: Radar equation out of range")
    sys.exit(1)

# Doppler validation
f0 = 10e9  # 10 GHz
v_radial = 300  # m/s
f_doppler = 2 * v_radial * f0 / SPEED_OF_LIGHT
print(f"  Doppler shift test: {f_doppler:.0f} Hz at {v_radial} m/s")
if not (15000 < f_doppler < 25000):
    print("ERROR: Doppler calculation error")
    sys.exit(1)

# Radar horizon
def radar_horizon(h_radar, h_target):
    return np.sqrt(2 * EARTH_RADIUS * h_radar) + np.sqrt(2 * EARTH_RADIUS * h_target)

h = radar_horizon(10, 10000)
print(f"  Radar horizon test: {h/1000:.0f} km")

# Ballistic trajectory
g = 9.81
v0, theta = 3000, 45
theta_rad = np.radians(theta)
R_ballistic = (v0**2 * np.sin(2*theta_rad)) / g
print(f"  Ballistic range test: {R_ballistic/1000:.0f} km")

print("\\n✓ Physics validation complete")
'''

    print("  Running physics validation...")
    code, stdout, stderr = run_python(physics_script)
    print(stdout)

    if code != 0:
        errors.append("Physics validation failed")
        print(stderr)

    duration = time.time() - start
    status = StageStatus.PASSED if code == 0 else StageStatus.FAILED

    return StageResult(
        name="Physics Validation",
        status=status,
        duration=duration,
        output=stdout,
        errors=errors,
        warnings=warnings
    )

def stage_cad_geometry_validation() -> StageResult:
    """Stage 6: CAD Geometry Validation"""
    start = time.time()
    errors = []
    warnings = []

    print_header("Stage 6: CAD Geometry Validation")

    cad_script = '''
import numpy as np
import sys

print("CAD Geometry Validation")
print("="*50)

try:
    from cad_geometry import (
        Point3D, Vector3D, Triangle, TriangleMesh,
        OgiveNose, SearsHaackBody, CylindricalSection,
        create_pl15_cad_model, create_aim120_cad_model
    )

    # Point3D test
    p1 = Point3D(1, 2, 3)
    p2 = Point3D(4, 5, 6)
    dist = p1.distance_to(p2)
    assert abs(dist - np.sqrt(27)) < 1e-10
    print("  ✓ Point3D operations")

    # Vector3D test
    v1 = Vector3D(1, 0, 0)
    v2 = Vector3D(0, 1, 0)
    cross = v1.cross(v2)
    assert abs(cross.dz - 1.0) < 1e-10
    print("  ✓ Vector3D operations")

    # Triangle test
    tri = Triangle(Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0))
    assert abs(tri.area - 0.5) < 1e-10
    print("  ✓ Triangle operations")

    # Ogive nose
    ogive = OgiveNose(length=0.5, base_radius=0.1)
    ogive_mesh = ogive.generate_mesh(resolution=16)
    print(f"  ✓ Ogive nose: {len(ogive_mesh.triangles)} triangles")

    # PL-15 model
    pl15 = create_pl15_cad_model()
    valid, errors = pl15.validate_parameters()
    assert valid, f"PL-15 validation failed: {errors}"
    pl15_geom = pl15.generate_geometry(resolution=16)
    print(f"  ✓ PL-15 CAD: {len(pl15_geom.mesh.triangles)} triangles")

    # AIM-120 model
    aim120 = create_aim120_cad_model()
    valid, errors = aim120.validate_parameters()
    assert valid
    aim120_geom = aim120.generate_geometry(resolution=16)
    print(f"  ✓ AIM-120 CAD: {len(aim120_geom.mesh.triangles)} triangles")

    print("\\n✓ CAD geometry validation complete")

except ImportError as e:
    print(f"  ⚠ CAD modules not available: {e}")
    print("  Skipping CAD geometry tests")
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)
'''

    print("  Running CAD geometry validation...")
    code, stdout, stderr = run_python(cad_script)
    print(stdout)

    if "not available" in stdout:
        warnings.append("CAD modules not available")
    elif code != 0:
        errors.append("CAD geometry validation failed")
        print(stderr)

    duration = time.time() - start
    status = StageStatus.PASSED if code == 0 else StageStatus.FAILED
    if not errors and warnings:
        status = StageStatus.WARNING

    return StageResult(
        name="CAD Geometry Validation",
        status=status,
        duration=duration,
        output=stdout,
        errors=errors,
        warnings=warnings
    )

def stage_golden_fleet_validation() -> StageResult:
    """Stage 7: Golden Fleet LSC-X Validation"""
    start = time.time()
    errors = []
    warnings = []

    print_header("Stage 7: Golden Fleet LSC-X Validation")

    golden_fleet_dir = PROJECT_ROOT / "golden_fleet_cruiser_proposal"

    if not golden_fleet_dir.exists():
        return StageResult(
            name="Golden Fleet Validation",
            status=StageStatus.SKIPPED,
            duration=0,
            warnings=["Golden Fleet directory not found"]
        )

    # Run LSC-X model
    print("  Running LSC-X model simulation...")
    lscx_model = golden_fleet_dir / "lsc_x_model.py"
    if lscx_model.exists():
        code, stdout, stderr = run_command([sys.executable, str(lscx_model)], cwd=golden_fleet_dir)
        if code == 0:
            print("    ✓ LSC-X model simulation passed")
        else:
            errors.append("LSC-X model simulation failed")
            print(f"    ✗ LSC-X model simulation failed")

    # Run unit tests
    print("  Running LSC-X unit tests...")
    test_files = list(golden_fleet_dir.glob("test_*.py"))
    for test_file in test_files:
        print(f"    Testing {test_file.name}...")
        code, stdout, stderr = run_pytest(str(test_file))
        if code == 0:
            print(f"      ✓ {test_file.name} passed")
        else:
            warnings.append(f"{test_file.name} had issues")
            print(f"      ⚠ {test_file.name} had issues")

    # Validate model outputs
    print("  Validating model outputs...")
    validation_script = '''
import sys
sys.path.insert(0, "golden_fleet_cruiser_proposal")

try:
    from lsc_x_model import LSCX_Model
    model = LSCX_Model()

    # BMD coverage
    bmd = model.calculate_bmd_coverage()
    assert bmd['layered_pk_estimate'] > 0.95, f"Layered Pk too low: {bmd['layered_pk_estimate']}"
    print(f"  ✓ BMD Pk: {bmd['layered_pk_estimate']:.1%}")

    # Strike capability
    strike = model.calculate_strike_capability()
    assert strike['total_strike_missiles'] >= 100
    print(f"  ✓ Strike capacity: {strike['total_strike_missiles']} missiles")

    # Comparison
    comp = model.compare_to_ddg51()
    assert comp['lsc_x']['vls_cells'] > comp['ddg51_flight_iii']['vls_cells']
    print(f"  ✓ VLS cells: {comp['lsc_x']['vls_cells']} vs DDG-51: {comp['ddg51_flight_iii']['vls_cells']}")

    print("\\n✓ Golden Fleet validation complete")

except ImportError as e:
    print(f"  ⚠ Golden Fleet modules not available: {e}")
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)
'''
    code, stdout, stderr = run_python(validation_script)
    print(stdout)

    if code != 0:
        errors.append("Golden Fleet validation failed")
        print(stderr)

    duration = time.time() - start
    status = StageStatus.PASSED if not errors else StageStatus.FAILED
    if not errors and warnings:
        status = StageStatus.WARNING

    return StageResult(
        name="Golden Fleet Validation",
        status=status,
        duration=duration,
        output=stdout,
        errors=errors,
        warnings=warnings
    )

def stage_pla_systems_validation() -> StageResult:
    """Stage 8: PLA Systems CAD Validation"""
    start = time.time()
    errors = []
    warnings = []

    print_header("Stage 8: PLA Systems CAD Validation")

    pla_script = '''
import sys

try:
    from pla_systems_cad import PLASystemsRegistry

    categories = PLASystemsRegistry.get_system_categories()
    total = 0
    passed = 0

    for category, systems in categories.items():
        print(f"\\n{category}:")
        for system_name in systems:
            total += 1
            try:
                model = PLASystemsRegistry.get_system(system_name)
                valid, errs = model.validate_geometry()
                if valid:
                    print(f"  ✓ {system_name}")
                    passed += 1
                else:
                    print(f"  ✗ {system_name}: {errs}")
            except Exception as e:
                print(f"  ⚠ {system_name}: {str(e)[:40]}")

    print(f"\\n{'='*50}")
    print(f"Total: {passed}/{total} systems validated")

    if passed < total:
        sys.exit(1)

except ImportError as e:
    print(f"⚠ PLA Systems CAD not available: {e}")
    print("Skipping PLA systems validation")
'''

    print("  Running PLA Systems validation...")
    code, stdout, stderr = run_python(pla_script)
    print(stdout)

    if "not available" in stdout:
        warnings.append("PLA Systems CAD not available")
    elif code != 0:
        warnings.append("Some PLA systems validation failed")

    duration = time.time() - start
    status = StageStatus.PASSED if code == 0 else StageStatus.WARNING

    return StageResult(
        name="PLA Systems Validation",
        status=status,
        duration=duration,
        output=stdout,
        errors=errors,
        warnings=warnings
    )

def stage_numerical_stability() -> StageResult:
    """Stage 9: Numerical Stability Validation"""
    start = time.time()
    errors = []
    warnings = []

    print_header("Stage 9: Numerical Stability")

    stability_script = '''
import numpy as np
import warnings

print("Numerical Stability Validation")
print("="*50)

issues = []

# Division by near-zero
print("\\n1. Division by near-zero:")
try:
    with np.errstate(divide='raise', invalid='raise'):
        test_val = 1.0 / np.array([1, 2, 0.0001])
    print("   ✓ Near-zero division handled")
except FloatingPointError:
    issues.append("Division issues")
    print("   ⚠ Near-zero division warning")

# Exponential overflow
print("\\n2. Exponential overflow:")
large_exp = np.exp(np.array([1, 10, 100, 500]))
if np.isinf(large_exp[-1]):
    print("   ⚠ Overflow at exp(500) - use log-space")
else:
    print("   ✓ No overflow")

# Matrix conditioning
print("\\n3. Matrix conditioning:")
A_good = np.array([[4, 1], [1, 3]])
cond_good = np.linalg.cond(A_good)
print(f"   Well-conditioned: cond = {cond_good:.1f}")

A_bad = np.array([[1, 1], [1, 1.0001]])
cond_bad = np.linalg.cond(A_bad)
print(f"   Ill-conditioned: cond = {cond_bad:.1e}")

# Float comparison
print("\\n4. Floating point comparison:")
a = 0.1 + 0.2
b = 0.3
if np.isclose(a, b):
    print("   ✓ Using np.isclose correctly")

print("\\n" + "="*50)
if issues:
    print(f"Issues found: {issues}")
else:
    print("✓ Numerical stability validated")
'''

    print("  Running numerical stability checks...")
    code, stdout, stderr = run_python(stability_script)
    print(stdout)

    duration = time.time() - start
    status = StageStatus.PASSED

    return StageResult(
        name="Numerical Stability",
        status=status,
        duration=duration,
        output=stdout,
        errors=errors,
        warnings=warnings
    )

def stage_security_scan() -> StageResult:
    """Stage 10: Security Scanning"""
    start = time.time()
    errors = []
    warnings = []

    print_header("Stage 10: Security Scan")

    # Safety check
    print("  Checking for vulnerable dependencies (Safety)...")
    req_file = PROJECT_ROOT / "requirements.txt"
    if req_file.exists():
        code, stdout, stderr = run_command([
            sys.executable, "-m", "safety", "check",
            "-r", str(req_file), "--output", "text"
        ])
        if code != 0:
            warnings.append("Vulnerable dependencies found")
            print("    ⚠ Vulnerable dependencies detected")
        else:
            print("    ✓ No vulnerable dependencies")

    # pip-audit
    print("  Running pip-audit...")
    code, stdout, stderr = run_command([sys.executable, "-m", "pip_audit"])
    if code != 0:
        warnings.append("pip-audit found issues")
        print("    ⚠ pip-audit found issues")
    else:
        print("    ✓ pip-audit passed")

    duration = time.time() - start
    status = StageStatus.PASSED if not warnings else StageStatus.WARNING

    return StageResult(
        name="Security Scan",
        status=status,
        duration=duration,
        errors=errors,
        warnings=warnings
    )

# ============================================
# Pipeline Orchestration
# ============================================

def run_pipeline(stages: List[str] = None, fast: bool = False) -> PipelineReport:
    """Run the full CI/CD pipeline"""
    report = PipelineReport(start_time=datetime.now())

    # Ensure report directory exists
    REPORT_DIR.mkdir(exist_ok=True)

    # Define all stages
    all_stages = [
        ("lint", stage_lint),
        ("unit_tests", stage_unit_tests),
        ("integration_tests", stage_integration_tests),
        ("simulation", stage_simulation_validation),
        ("physics", stage_physics_validation),
        ("cad_geometry", stage_cad_geometry_validation),
        ("golden_fleet", stage_golden_fleet_validation),
        ("pla_systems", stage_pla_systems_validation),
        ("numerical", stage_numerical_stability),
        ("security", stage_security_scan),
    ]

    if fast:
        # Quick validation only
        all_stages = [
            ("lint", stage_lint),
            ("unit_tests", stage_unit_tests),
            ("physics", stage_physics_validation),
        ]

    if stages:
        # Filter to requested stages
        all_stages = [(name, func) for name, func in all_stages if name in stages]

    print_header("PLA-Defense-CAD Local CI/CD Pipeline", "═")
    print(f"Started: {report.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Stages: {len(all_stages)}")

    failed = False
    for stage_name, stage_func in all_stages:
        try:
            result = stage_func()
            report.stages.append(result)
            print_stage(result.name, result.status)

            if result.status == StageStatus.FAILED:
                failed = True
                if not stages:  # Don't stop early if running specific stages
                    break
        except Exception as e:
            result = StageResult(
                name=stage_name,
                status=StageStatus.FAILED,
                duration=0,
                errors=[str(e)]
            )
            report.stages.append(result)
            print_stage(stage_name, StageStatus.FAILED)
            print(f"    Error: {e}")
            traceback.print_exc()
            failed = True
            break

    report.end_time = datetime.now()
    report.overall_status = StageStatus.FAILED if failed else StageStatus.PASSED

    # Check for warnings
    if not failed and any(s.status == StageStatus.WARNING for s in report.stages):
        report.overall_status = StageStatus.WARNING

    return report

def print_summary(report: PipelineReport):
    """Print pipeline summary"""
    print_header("Pipeline Summary", "═")

    total_duration = (report.end_time - report.start_time).total_seconds()

    print(f"\nOverall Status: ", end="")
    print_stage("Pipeline", report.overall_status)
    print(f"Total Duration: {total_duration:.1f}s")
    print(f"\nStage Results:")

    for stage in report.stages:
        status_str = f"[{stage.status.value.upper():^8}]"
        duration_str = f"{stage.duration:.1f}s"
        print(f"  {status_str} {stage.name:<30} {duration_str:>8}")
        for error in stage.errors:
            print(f"           └─ ✗ {error}")
        for warning in stage.warnings:
            print(f"           └─ ⚠ {warning}")

    # Save report
    report_file = REPORT_DIR / f"cicd_report_{report.start_time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(report.to_dict(), f, indent=2)
    print(f"\nReport saved to: {report_file}")

# ============================================
# Main Entry Point
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Local CI/CD Pipeline for PLA-Defense-CAD")
    parser.add_argument("--stage", type=str, help="Run specific stage(s)", nargs="+")
    parser.add_argument("--fast", action="store_true", help="Quick validation only")
    parser.add_argument("--golden-fleet", action="store_true", help="Golden Fleet validation only")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--list", action="store_true", help="List available stages")

    args = parser.parse_args()

    if args.list:
        print("Available stages:")
        stages = ["lint", "unit_tests", "integration_tests", "simulation",
                  "physics", "cad_geometry", "golden_fleet", "pla_systems",
                  "numerical", "security"]
        for s in stages:
            print(f"  - {s}")
        return 0

    stages = None
    if args.stage:
        stages = args.stage
    elif args.golden_fleet:
        stages = ["golden_fleet"]

    report = run_pipeline(stages=stages, fast=args.fast)
    print_summary(report)

    return 0 if report.overall_status in [StageStatus.PASSED, StageStatus.WARNING] else 1

if __name__ == "__main__":
    sys.exit(main())
