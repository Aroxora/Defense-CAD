#!/usr/bin/env python3
"""
Hardware Compatibility Test Suite

Comprehensive testing script to verify hardware and software compatibility
for the MADL Detection and J-20 EW simulation system.

Usage:
    python3 hardware_compatibility_test.py
    python3 hardware_compatibility_test.py --verbose
    python3 hardware_compatibility_test.py --quick

Exit codes:
    0: All tests passed
    1: One or more critical tests failed
    2: Warnings present but non-critical
"""

import sys
import platform
import subprocess
import warnings
from typing import Tuple, Dict, Any
import time


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def disable():
        """Disable colors (for non-TTY output)"""
        Colors.GREEN = Colors.YELLOW = Colors.RED = Colors.BLUE = Colors.BOLD = Colors.END = ''


def print_header(text: str):
    """Print formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_test(test_name: str, status: str, details: str = ""):
    """Print formatted test result"""
    if status == "PASS":
        symbol = f"{Colors.GREEN}✓{Colors.END}"
        status_text = f"{Colors.GREEN}PASS{Colors.END}"
    elif status == "WARN":
        symbol = f"{Colors.YELLOW}⚠{Colors.END}"
        status_text = f"{Colors.YELLOW}WARN{Colors.END}"
    elif status == "FAIL":
        symbol = f"{Colors.RED}✗{Colors.END}"
        status_text = f"{Colors.RED}FAIL{Colors.END}"
    else:
        symbol = "?"
        status_text = status

    print(f"{symbol} {test_name:<40} [{status_text}]")
    if details:
        print(f"  → {details}")


class HardwareCompatibilityTest:
    """Main test harness for hardware compatibility"""

    def __init__(self, verbose: bool = False, quick: bool = False):
        self.verbose = verbose
        self.quick = quick
        self.results = {
            'passed': 0,
            'warnings': 0,
            'failed': 0
        }
        self.critical_failures = []

    def record_result(self, test_name: str, status: str, details: str = "", critical: bool = False):
        """Record test result"""
        print_test(test_name, status, details)

        if status == "PASS":
            self.results['passed'] += 1
        elif status == "WARN":
            self.results['warnings'] += 1
        elif status == "FAIL":
            self.results['failed'] += 1
            if critical:
                self.critical_failures.append(test_name)

    def test_python_version(self):
        """Test Python version compatibility"""
        print_header("Python Environment")

        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version.major == 3 and version.minor >= 9:
            self.record_result("Python Version", "PASS", f"Python {version_str}")
        elif version.major == 3 and version.minor == 8:
            self.record_result("Python Version", "WARN",
                             f"Python {version_str} (3.9+ recommended)", critical=False)
        else:
            self.record_result("Python Version", "FAIL",
                             f"Python {version_str} (3.9+ required)", critical=True)

    def test_platform(self):
        """Test operating system and architecture"""
        system = platform.system()
        machine = platform.machine()
        release = platform.release()

        supported_systems = ['Linux', 'Darwin', 'Windows']
        supported_archs = ['x86_64', 'AMD64', 'arm64', 'aarch64']

        # OS test
        if system in supported_systems:
            self.record_result("Operating System", "PASS", f"{system} {release}")
        else:
            self.record_result("Operating System", "WARN",
                             f"{system} (untested platform)")

        # Architecture test
        if machine in supported_archs:
            self.record_result("CPU Architecture", "PASS", machine)
        else:
            self.record_result("CPU Architecture", "WARN",
                             f"{machine} (untested architecture)")

    def test_dependencies(self):
        """Test required Python packages"""
        print_header("Python Dependencies")

        required_packages = {
            'numpy': ('1.24.0', True),
            'scipy': ('1.10.0', True),
            'matplotlib': ('3.7.0', True),
            'networkx': ('3.0', True)
        }

        for package, (min_version, critical) in required_packages.items():
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')

                # Version comparison (simplified)
                if version != 'unknown':
                    self.record_result(f"{package} package", "PASS", f"v{version}")
                else:
                    self.record_result(f"{package} package", "WARN",
                                     f"version unknown", critical=False)

            except ImportError:
                self.record_result(f"{package} package", "FAIL",
                                 f"not installed (pip install {package})", critical=critical)

    def test_numpy_blas(self):
        """Test NumPy BLAS/LAPACK configuration"""
        print_header("NumPy Performance Configuration")

        try:
            import numpy as np
            config = np.show_config(mode='dicts')

            # Check for BLAS backend
            blas_info = None
            for key in config.get('Build Dependencies', {}):
                if 'blas' in key.lower():
                    blas_info = config['Build Dependencies'][key]
                    break

            if blas_info:
                # Try to extract BLAS library name
                blas_name = str(blas_info.get('name', 'unknown'))
                self.record_result("NumPy BLAS Backend", "PASS", blas_name)
            else:
                self.record_result("NumPy BLAS Backend", "WARN",
                                 "No optimized BLAS detected (performance may be degraded)")

            # Test NumPy performance with a simple benchmark
            if not self.quick:
                size = 1000
                start = time.time()
                A = np.random.rand(size, size)
                B = np.random.rand(size, size)
                C = np.dot(A, B)
                elapsed = time.time() - start

                # Expected: <0.5s on modern hardware with optimized BLAS
                if elapsed < 0.5:
                    self.record_result("NumPy Matrix Multiply", "PASS",
                                     f"{elapsed:.3f}s for {size}x{size}")
                elif elapsed < 2.0:
                    self.record_result("NumPy Matrix Multiply", "WARN",
                                     f"{elapsed:.3f}s (slow, check BLAS)")
                else:
                    self.record_result("NumPy Matrix Multiply", "FAIL",
                                     f"{elapsed:.3f}s (very slow, no optimized BLAS)")

        except ImportError:
            self.record_result("NumPy BLAS Backend", "FAIL",
                             "NumPy not installed", critical=True)

    def test_scipy_performance(self):
        """Test SciPy compilation and performance"""
        if self.quick:
            return

        print_header("SciPy Performance")

        try:
            import numpy as np
            from scipy import linalg

            # Test SVD performance (critical for geolocation)
            size = 500
            start = time.time()
            A = np.random.rand(size, size)
            U, s, Vh = linalg.svd(A)
            elapsed = time.time() - start

            # Expected: <1s on modern hardware
            if elapsed < 1.0:
                self.record_result("SciPy SVD Performance", "PASS",
                                 f"{elapsed:.3f}s for {size}x{size}")
            elif elapsed < 3.0:
                self.record_result("SciPy SVD Performance", "WARN",
                                 f"{elapsed:.3f}s (acceptable but slow)")
            else:
                self.record_result("SciPy SVD Performance", "FAIL",
                                 f"{elapsed:.3f}s (very slow)")

            # Test least-squares (used in TDOA geolocation)
            from scipy.optimize import least_squares

            def func(x):
                return x**2 - 4

            start = time.time()
            for _ in range(100):
                result = least_squares(func, x0=[1.0])
            elapsed = time.time() - start

            if elapsed < 0.5:
                self.record_result("SciPy Least Squares", "PASS",
                                 f"{elapsed:.3f}s for 100 iterations")
            else:
                self.record_result("SciPy Least Squares", "WARN",
                                 f"{elapsed:.3f}s (slow)")

        except ImportError as e:
            self.record_result("SciPy Performance", "FAIL",
                             f"Import error: {e}", critical=True)

    def test_matplotlib_backend(self):
        """Test Matplotlib backend configuration"""
        print_header("Matplotlib Configuration")

        try:
            import matplotlib
            backend = matplotlib.get_backend()

            # Check if backend is suitable
            headless_backends = ['Agg', 'pdf', 'ps', 'svg']
            gui_backends = ['TkAgg', 'Qt5Agg', 'macosx']

            if backend in headless_backends + gui_backends:
                self.record_result("Matplotlib Backend", "PASS", backend)
            else:
                self.record_result("Matplotlib Backend", "WARN",
                                 f"{backend} (unusual backend)")

            # Try creating a simple figure
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            plt.close(fig)

            self.record_result("Matplotlib Plot Creation", "PASS", "Figure created successfully")

        except ImportError:
            self.record_result("Matplotlib Backend", "FAIL",
                             "Matplotlib not installed", critical=True)
        except Exception as e:
            self.record_result("Matplotlib Plot Creation", "WARN",
                             f"Error: {e}")

    def test_cpu_features(self):
        """Test CPU features and capabilities"""
        print_header("CPU Capabilities")

        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()

            if cpu_count >= 4:
                self.record_result("CPU Core Count", "PASS", f"{cpu_count} cores")
            elif cpu_count >= 2:
                self.record_result("CPU Core Count", "WARN",
                                 f"{cpu_count} cores (4+ recommended)")
            else:
                self.record_result("CPU Core Count", "FAIL",
                                 f"{cpu_count} core(s) (insufficient)")

            # Check for CPU features (platform specific)
            machine = platform.machine()
            if machine in ['x86_64', 'AMD64']:
                # Try to detect SSE/AVX support
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()

                        if 'avx2' in cpuinfo:
                            self.record_result("AVX2 Support", "PASS", "Available")
                        elif 'sse4_2' in cpuinfo:
                            self.record_result("SSE4.2 Support", "PASS", "Available (AVX2 recommended)")
                        else:
                            self.record_result("SIMD Support", "WARN", "Limited SIMD support")
                except:
                    self.record_result("CPU Features", "WARN", "Cannot detect (non-Linux)")

            elif machine in ['arm64', 'aarch64']:
                self.record_result("ARM NEON", "PASS", "Assumed available on ARM64")

        except Exception as e:
            self.record_result("CPU Capabilities", "WARN", f"Error: {e}")

    def test_memory(self):
        """Test system memory"""
        print_header("System Memory")

        try:
            import os

            if hasattr(os, 'sysconf'):
                # Linux/Unix
                pages = os.sysconf('SC_PHYS_PAGES')
                page_size = os.sysconf('SC_PAGE_SIZE')
                total_memory_gb = (pages * page_size) / (1024**3)
            else:
                # Windows or other
                try:
                    import psutil
                    total_memory_gb = psutil.virtual_memory().total / (1024**3)
                except ImportError:
                    total_memory_gb = None

            if total_memory_gb:
                if total_memory_gb >= 16:
                    self.record_result("Total Memory", "PASS", f"{total_memory_gb:.1f} GB")
                elif total_memory_gb >= 8:
                    self.record_result("Total Memory", "WARN",
                                     f"{total_memory_gb:.1f} GB (16+ GB recommended)")
                else:
                    self.record_result("Total Memory", "FAIL",
                                     f"{total_memory_gb:.1f} GB (insufficient for large simulations)")
            else:
                self.record_result("Total Memory", "WARN", "Cannot detect memory size")

        except Exception as e:
            self.record_result("Total Memory", "WARN", f"Error: {e}")

    def test_module_imports(self):
        """Test importing project modules"""
        print_header("Project Module Imports")

        modules_to_test = [
            'osint_cad.sensors.signal_processing',
            'osint_cad.sensors.geolocation_network',
            'osint_cad.physics.rf_propagation',
            'osint_cad.sensors.advanced_tracking',
            'osint_cad.sensors.adaptive_antenna_ep',
            'osint_cad.sensors.visualization',
            'osint_cad.engagements.operational_simulation',
        ]

        for module_name in modules_to_test:
            try:
                __import__(module_name)
                self.record_result(f"Import {module_name}", "PASS", "")
            except ImportError as e:
                self.record_result(f"Import {module_name}", "FAIL",
                                 f"Import error: {e}", critical=True)
            except Exception as e:
                self.record_result(f"Import {module_name}", "WARN",
                                 f"Warning: {e}")

    def test_numerical_accuracy(self):
        """Test numerical accuracy of geolocation algorithms"""
        if self.quick:
            return

        print_header("Numerical Accuracy Tests")

        try:
            import numpy as np
            from osint_cad.sensors.geolocation_network import GeolocationEngine, PlatformState, Measurement

            # Test TDOA geolocation with known geometry
            geo = GeolocationEngine()

            # Setup 4 platforms in a square (100 km spacing)
            platforms = [
                PlatformState("P1", np.array([0, 0, 10000]), np.array([0, 0, 0]), 0),
                PlatformState("P2", np.array([100000, 0, 10000]), np.array([0, 0, 0]), 0),
                PlatformState("P3", np.array([100000, 100000, 10000]), np.array([0, 0, 0]), 0),
                PlatformState("P4", np.array([0, 100000, 10000]), np.array([0, 0, 0]), 0),
            ]

            for p in platforms:
                geo.update_platform_state(p)

            # True emitter position (center of square)
            true_pos = np.array([50000, 50000, 10000])

            # Calculate true time delays
            c = 3e8  # speed of light
            ranges = [np.linalg.norm(p.position - true_pos) for p in platforms]
            tdoas = [(ranges[i] - ranges[0]) / c for i in range(1, 4)]

            # Create measurements
            measurements = [
                Measurement(
                    emitter_id="TEST",
                    timestamp=0,
                    frequency=15e9,
                    power_dbm=-80,
                    platform_id=platforms[i].platform_id,
                    tdoa=tdoas[i-1] if i > 0 else 0
                )
                for i in range(4)
            ]

            # Perform TDOA geolocation
            try:
                position, covariance = geo.tdoa_geolocation(measurements)
                error = np.linalg.norm(position - true_pos)

                # Expected error: <1 km for this ideal geometry
                if error < 1000:
                    self.record_result("TDOA Geolocation Accuracy", "PASS",
                                     f"Error: {error:.1f} m")
                elif error < 5000:
                    self.record_result("TDOA Geolocation Accuracy", "WARN",
                                     f"Error: {error:.1f} m (high but acceptable)")
                else:
                    self.record_result("TDOA Geolocation Accuracy", "FAIL",
                                     f"Error: {error:.1f} m (algorithm failure)")
            except Exception as e:
                self.record_result("TDOA Geolocation Accuracy", "FAIL",
                                 f"Exception: {e}")

        except ImportError:
            self.record_result("Numerical Accuracy", "FAIL",
                             "Cannot import geolocation_network", critical=True)
        except Exception as e:
            self.record_result("Numerical Accuracy", "WARN",
                             f"Test error: {e}")

    def test_hardware_in_loop(self):
        """
        Hardware-in-the-loop tests

        Attempts to connect to actual hardware interfaces:
        - GPS receivers (serial/USB)
        - RF sensors (network/serial)
        - Timing references (PPS signals)
        """
        if self.quick:
            return

        print_header("Hardware-in-the-Loop Tests")

        # Test GPS receiver connectivity
        self._test_gps_hardware()

        # Test timing reference (1PPS)
        self._test_timing_hardware()

        # Test RF sensor interface
        self._test_rf_sensor_hardware()

    def _test_gps_hardware(self):
        """Test GPS receiver hardware connectivity"""
        try:
            import serial
            import serial.tools.list_ports

            # Find potential GPS devices
            ports = list(serial.tools.list_ports.comports())

            gps_found = False
            for port in ports:
                # Common GPS device identifiers
                if any(x in port.description.lower() for x in ['gps', 'gnss', 'u-blox', 'trimble']):
                    try:
                        # Attempt to open serial port
                        ser = serial.Serial(port.device, 9600, timeout=2)

                        # Try to read NMEA sentences
                        for _ in range(10):
                            line = ser.readline().decode('ascii', errors='ignore')
                            if line.startswith('$GP') or line.startswith('$GN'):
                                gps_found = True
                                self.record_result("GPS Hardware", "PASS",
                                                 f"Found on {port.device}")
                                ser.close()
                                return
                        ser.close()
                    except Exception:
                        pass

            if not gps_found:
                self.record_result("GPS Hardware", "WARN",
                                 "No GPS hardware detected (optional for simulation)")

        except ImportError:
            self.record_result("GPS Hardware", "WARN",
                             "pyserial not installed (pip install pyserial)")

    def _test_timing_hardware(self):
        """Test timing reference hardware (1PPS signal)"""
        # Check for common timing hardware interfaces
        try:
            # Linux: Check for PPS devices
            import os
            if os.path.exists('/dev/pps0'):
                self.record_result("Timing Hardware", "PASS",
                                 "PPS device found (/dev/pps0)")
            else:
                self.record_result("Timing Hardware", "WARN",
                                 "No PPS device (optional - using system time)")
        except Exception:
            self.record_result("Timing Hardware", "WARN",
                             "Cannot check PPS devices")

    def _test_rf_sensor_hardware(self):
        """Test RF sensor hardware connectivity"""
        # Check for common SDR hardware
        try:
            # Try to import SDR libraries
            sdr_found = False

            try:
                import rtlsdr
                # Try to open RTL-SDR
                sdr = rtlsdr.RtlSdr()
                sdr.close()
                sdr_found = True
                self.record_result("RF Sensor Hardware", "PASS",
                                 "RTL-SDR found")
                return
            except (ImportError, Exception):
                pass

            try:
                import SoapySDR
                # Enumerate devices
                results = SoapySDR.Device.enumerate()
                if results:
                    sdr_found = True
                    self.record_result("RF Sensor Hardware", "PASS",
                                     f"SoapySDR: {len(results)} device(s)")
                    return
            except (ImportError, Exception):
                pass

            if not sdr_found:
                self.record_result("RF Sensor Hardware", "WARN",
                                 "No SDR hardware detected (simulation mode)")

        except Exception as e:
            self.record_result("RF Sensor Hardware", "WARN",
                             f"Cannot check SDR hardware: {e}")

    def run_all_tests(self):
        """Run all compatibility tests"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║   MADL Detection System - Hardware Compatibility Test   ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print(Colors.END)

        # Core tests (always run)
        self.test_python_version()
        self.test_platform()
        self.test_dependencies()
        self.test_numpy_blas()
        self.test_matplotlib_backend()
        self.test_cpu_features()
        self.test_memory()

        # Extended tests (skip if --quick)
        if not self.quick:
            self.test_scipy_performance()
            self.test_module_imports()
            self.test_numerical_accuracy()
            self.test_hardware_in_loop()

        # Print summary
        print_header("Test Summary")

        total = sum(self.results.values())
        passed_pct = (self.results['passed'] / total * 100) if total > 0 else 0

        print(f"Total Tests:    {total}")
        print(f"{Colors.GREEN}Passed:         {self.results['passed']} ({passed_pct:.1f}%){Colors.END}")
        print(f"{Colors.YELLOW}Warnings:       {self.results['warnings']}{Colors.END}")
        print(f"{Colors.RED}Failed:         {self.results['failed']}{Colors.END}")

        if self.critical_failures:
            print(f"\n{Colors.RED}{Colors.BOLD}Critical failures:{Colors.END}")
            for failure in self.critical_failures:
                print(f"  {Colors.RED}✗ {failure}{Colors.END}")
            print(f"\n{Colors.RED}System is NOT ready for operation.{Colors.END}")
            return 1
        elif self.results['failed'] > 0:
            print(f"\n{Colors.RED}Some tests failed. Review and fix issues.{Colors.END}")
            return 1
        elif self.results['warnings'] > 0:
            print(f"\n{Colors.YELLOW}All critical tests passed, but warnings present.{Colors.END}")
            print(f"{Colors.YELLOW}System is operational but not optimally configured.{Colors.END}")
            return 2
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All tests passed! System is ready for operation.{Colors.END}")
            return 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Hardware compatibility test for MADL Detection System')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quick', '-q', action='store_true', help='Quick test (skip performance benchmarks)')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')

    args = parser.parse_args()

    if args.no_color or not sys.stdout.isatty():
        Colors.disable()

    tester = HardwareCompatibilityTest(verbose=args.verbose, quick=args.quick)
    exit_code = tester.run_all_tests()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
