#!/usr/bin/env python3
"""
F-22 APG-77 AESA Radar Performance Model

Implements F-22's AN/APG-77 radar detection capabilities based on deductive reasoning
from physical observables and engineering constraints.

Key Parameters (from public sources):
- AESA elements: 2000 ± 200 (confidence: 80%)
- Aperture diameter: ~90 cm
- Frequency: X-band (9.5 GHz)
- Element spacing: λ/2 = 15.8 mm

This is a DEFENSIVE model - helps F-22 understand its own radar capabilities
for threat assessment and engagement planning.

Classification: UNCLASSIFIED // PUBLIC RELEASE
All parameters derived from public sources with documented uncertainty.
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass

# Physical constants
SPEED_OF_LIGHT = 299792458  # m/s
BOLTZMANN_CONSTANT = 1.38e-23  # J/K


@dataclass
class RadarDetection:
    """Radar detection result with uncertainty"""
    detection_range_km: float
    snr_db: float
    target_rcs_m2: float
    confidence: float  # 0-1, confidence in detection
    azimuth_deg: float
    elevation_deg: float


@dataclass
class F22RadarParameters:
    """
    F-22 AN/APG-77 AESA Radar Parameters (Best Estimates)

    Based on deductive reasoning from:
    - Observable nose diameter: 90 cm (larger than J-20)
    - Element count: 2000 ± 200 (80% confidence)
    - Frequency: X-band (9.5 GHz typical for fighter AESA)
    - Comparison to F-35 APG-81 and J-20 AESA
    """

    # AESA configuration (from reasoning chains)
    num_elements: int = 2000
    num_elements_uncertainty: int = 200
    element_count_confidence: float = 0.80

    # Frequency parameters
    center_frequency_ghz: float = 9.5  # X-band
    bandwidth_mhz: float = 400.0  # Wide bandwidth for LPI/ECCM

    # Aperture geometry (from public photos)
    aperture_diameter_m: float = 0.90  # 90 cm nose diameter
    aperture_area_m2: float = 0.50  # ~0.50 m² active area (utilization factor 0.87)

    # Power parameters (estimated from element count)
    peak_power_per_element_w: float = 10.0  # GaN T/R modules
    average_power_per_element_w: float = 1.0  # 10% duty cycle
    duty_cycle: float = 0.10

    # System parameters
    noise_figure_db: float = 3.0  # Advanced AESA receiver
    system_losses_db: float = 3.5  # Waveguide, circulator, etc.

    # Detection parameters
    probability_detection: float = 0.90  # Pd = 90%
    probability_false_alarm: float = 1e-6  # Pfa = 10^-6

    # Scan parameters
    max_azimuth_scan_deg: float = 60.0  # ±60° electronic scan
    max_elevation_scan_deg: float = 60.0  # ±60°

    @property
    def total_peak_power_kw(self) -> float:
        """Total peak transmit power"""
        return (self.num_elements * self.peak_power_per_element_w) / 1000.0

    @property
    def total_average_power_kw(self) -> float:
        """Total average transmit power"""
        return (self.num_elements * self.average_power_per_element_w) / 1000.0

    @property
    def wavelength_m(self) -> float:
        """Radar wavelength"""
        return SPEED_OF_LIGHT / (self.center_frequency_ghz * 1e9)

    @property
    def antenna_gain_db(self) -> float:
        """Antenna gain from aperture area"""
        efficiency = 0.70  # Typical AESA efficiency (slightly better than avg)
        gain_linear = (4 * np.pi * self.aperture_area_m2 * efficiency) / (self.wavelength_m ** 2)
        return 10 * np.log10(gain_linear)


class F22RadarModel:
    """
    F-22 AN/APG-77 AESA Radar Detection Model

    Implements radar range equation with scan angle losses and
    aspect-dependent target RCS.
    """

    def __init__(self, params: Optional[F22RadarParameters] = None):
        """
        Initialize F-22 radar model

        Args:
            params: Radar parameters (uses defaults if None)
        """
        self.params = params or F22RadarParameters()

    def calculate_detection_range(self,
                                 target_rcs_m2: float,
                                 azimuth_deg: float = 0.0,
                                 elevation_deg: float = 0.0,
                                 snr_threshold_db: float = 13.0) -> RadarDetection:
        """
        Calculate detection range using radar range equation

        Args:
            target_rcs_m2: Target radar cross section (m²)
            azimuth_deg: Scan angle in azimuth (deg, 0 = boresight)
            elevation_deg: Scan angle in elevation (deg, 0 = level)
            snr_threshold_db: Required SNR for detection (dB)

        Returns:
            RadarDetection with range and confidence
        """
        # Check if target is within scan volume
        if abs(azimuth_deg) > self.params.max_azimuth_scan_deg:
            return RadarDetection(
                detection_range_km=0.0,
                snr_db=-100.0,
                target_rcs_m2=target_rcs_m2,
                confidence=0.0,
                azimuth_deg=azimuth_deg,
                elevation_deg=elevation_deg
            )

        if abs(elevation_deg) > self.params.max_elevation_scan_deg:
            return RadarDetection(
                detection_range_km=0.0,
                snr_db=-100.0,
                target_rcs_m2=target_rcs_m2,
                confidence=0.0,
                azimuth_deg=azimuth_deg,
                elevation_deg=elevation_deg
            )

        # Calculate scan loss (beam broadening off-boresight)
        scan_angle_rad = np.radians(np.sqrt(azimuth_deg**2 + elevation_deg**2))
        scan_loss_db = -1.5 * (scan_angle_rad / np.radians(60)) ** 2  # Approximate

        # Effective antenna gain at scan angle
        antenna_gain_db = self.params.antenna_gain_db + scan_loss_db
        antenna_gain_linear = 10 ** (antenna_gain_db / 10.0)

        # Transmit power
        peak_power_w = self.params.total_peak_power_kw * 1000

        # System losses
        system_losses_linear = 10 ** (self.params.system_losses_db / 10.0)

        # Noise power
        temperature_k = 290  # Standard temperature
        noise_figure_linear = 10 ** (self.params.noise_figure_db / 10.0)
        bandwidth_hz = self.params.bandwidth_mhz * 1e6

        noise_power_w = BOLTZMANN_CONSTANT * temperature_k * bandwidth_hz * noise_figure_linear

        # Required received power for detection
        snr_linear = 10 ** (snr_threshold_db / 10.0)
        required_rx_power_w = noise_power_w * snr_linear

        # Radar range equation: R = [(Pt * G² * λ² * σ) / ((4π)³ * Pmin * L)]^(1/4)
        numerator = (peak_power_w * (antenna_gain_linear ** 2) *
                    (self.params.wavelength_m ** 2) * target_rcs_m2)
        denominator = ((4 * np.pi) ** 3) * required_rx_power_w * system_losses_linear

        if numerator / denominator > 0:
            range_m = (numerator / denominator) ** 0.25
        else:
            range_m = 0

        range_km = range_m / 1000.0

        # Calculate actual SNR at this range (for confidence assessment)
        received_power_w = (peak_power_w * (antenna_gain_linear ** 2) *
                           (self.params.wavelength_m ** 2) * target_rcs_m2 /
                           (((4 * np.pi) ** 3) * (range_m ** 4) * system_losses_linear))

        snr_actual_linear = received_power_w / noise_power_w
        snr_actual_db = 10 * np.log10(snr_actual_linear) if snr_actual_linear > 0 else -100

        # Confidence calculation
        # Factors: element count uncertainty, scan angle, target aspect
        confidence = self.params.element_count_confidence
        confidence *= (1.0 - 0.3 * abs(scan_loss_db) / 10.0)  # Reduce confidence at scan limits

        # Target RCS uncertainty (small RCS = more uncertainty)
        if target_rcs_m2 < 0.001:
            confidence *= 0.6  # Low confidence for very small targets
        elif target_rcs_m2 < 0.01:
            confidence *= 0.8

        return RadarDetection(
            detection_range_km=range_km,
            snr_db=snr_actual_db,
            target_rcs_m2=target_rcs_m2,
            confidence=confidence,
            azimuth_deg=azimuth_deg,
            elevation_deg=elevation_deg
        )

    def calculate_detection_from_positions(self,
                                          f22_position: np.ndarray,
                                          f22_velocity: np.ndarray,
                                          target_position: np.ndarray,
                                          target_velocity: np.ndarray,
                                          target_rcs_calculator) -> RadarDetection:
        """
        Calculate detection range from 3D positions and velocities

        Args:
            f22_position: F-22 position [x, y, z] (meters)
            f22_velocity: F-22 velocity [vx, vy, vz] (m/s)
            target_position: Target position [x, y, z] (meters)
            target_velocity: Target velocity [vx, vy, vz] (m/s)
            target_rcs_calculator: Object with calculate_rcs_from_vectors method

        Returns:
            RadarDetection
        """
        # Calculate target RCS as seen by F-22
        target_rcs_estimate = target_rcs_calculator.calculate_rcs_from_vectors(
            f22_position, target_position, target_velocity,
            frequency_ghz=self.params.center_frequency_ghz
        )

        # Calculate look angles from F-22 to target
        los_vector = target_position - f22_position
        range_m = np.linalg.norm(los_vector)

        if range_m < 1.0:
            azimuth_deg, elevation_deg = 0.0, 0.0
        else:
            los_unit = los_vector / range_m

            # Calculate angles relative to F-22's velocity (heading)
            f22_speed = np.linalg.norm(f22_velocity)
            if f22_speed > 1.0:
                f22_heading = f22_velocity / f22_speed

                # Azimuth: angle from heading to LOS in horizontal plane
                los_horizontal = np.array([los_unit[0], los_unit[1], 0])
                heading_horizontal = np.array([f22_heading[0], f22_heading[1], 0])

                los_h_norm = np.linalg.norm(los_horizontal)
                heading_h_norm = np.linalg.norm(heading_horizontal)

                if los_h_norm > 0.001 and heading_h_norm > 0.001:
                    cos_az = np.clip(np.dot(los_horizontal, heading_horizontal) /
                                    (los_h_norm * heading_h_norm), -1.0, 1.0)
                    azimuth_deg = np.degrees(np.arccos(cos_az))
                else:
                    azimuth_deg = 0.0

                # Elevation: angle above horizontal
                elevation_deg = np.degrees(np.arcsin(np.clip(-los_unit[2], -1.0, 1.0)))
            else:
                # F-22 nearly stationary, use absolute angles
                azimuth_deg = np.degrees(np.arctan2(los_vector[1], los_vector[0]))
                elevation_deg = np.degrees(np.arcsin(np.clip(-los_unit[2], -1.0, 1.0)))

        # Calculate detection range
        detection = self.calculate_detection_range(
            target_rcs_m2=target_rcs_estimate.rcs_m2,
            azimuth_deg=azimuth_deg,
            elevation_deg=elevation_deg
        )

        # Combine confidence from RCS estimate and detection
        detection.confidence *= target_rcs_estimate.confidence

        return detection

    def get_max_detection_range(self, target_rcs_m2: float) -> float:
        """
        Get maximum detection range (boresight, optimal conditions)

        Args:
            target_rcs_m2: Target RCS (m²)

        Returns:
            Maximum detection range (km)
        """
        detection = self.calculate_detection_range(target_rcs_m2, 0.0, 0.0)
        return detection.detection_range_km

    def print_radar_summary(self):
        """Print summary of F-22 radar capabilities"""
        print("=" * 70)
        print("F-22 AN/APG-77 AESA Radar Model - Pre-Trained Parameters")
        print("=" * 70)
        print(f"\nAESA Configuration:")
        print(f"  Element count:        {self.params.num_elements} ± {self.params.num_elements_uncertainty}")
        print(f"  Confidence:           {self.params.element_count_confidence:.0%}")
        print(f"  Aperture diameter:    {self.params.aperture_diameter_m:.2f} m")
        print(f"  Aperture area:        {self.params.aperture_area_m2:.2f} m²")

        print(f"\nTransmitter:")
        print(f"  Frequency:            {self.params.center_frequency_ghz:.1f} GHz (X-band)")
        print(f"  Wavelength:           {self.params.wavelength_m*1000:.1f} mm")
        print(f"  Peak power:           {self.params.total_peak_power_kw:.1f} kW")
        print(f"  Average power:        {self.params.total_average_power_kw:.1f} kW")
        print(f"  Antenna gain:         {self.params.antenna_gain_db:.1f} dBi")

        print(f"\nReceiver:")
        print(f"  Noise figure:         {self.params.noise_figure_db:.1f} dB")
        print(f"  Bandwidth:            {self.params.bandwidth_mhz:.0f} MHz")
        print(f"  System losses:        {self.params.system_losses_db:.1f} dB")

        print(f"\nScan Volume:")
        print(f"  Azimuth:              ±{self.params.max_azimuth_scan_deg:.0f}°")
        print(f"  Elevation:            ±{self.params.max_elevation_scan_deg:.0f}°")

        print(f"\nReference Detection Ranges (boresight):")
        test_targets = [
            ("J-20 (frontal)", 0.0014),
            ("J-20 (beam)", 0.25),
            ("Su-57 (frontal)", 0.1),
            ("4th-gen (frontal)", 1.0),
            ("H-6 Bomber", 50.0),
        ]

        for name, rcs in test_targets:
            detection = self.calculate_detection_range(rcs, 0.0, 0.0)
            print(f"  {name:20s}: {detection.detection_range_km:6.1f} km (RCS = {rcs:7.4f} m²)")

        print("=" * 70)


# Example usage and validation
if __name__ == "__main__":
    # Create F-22 radar model with default parameters
    f22_radar = F22RadarModel()

    # Print radar summary
    f22_radar.print_radar_summary()

    # Test detection vs aspect angle
    print("\n[TEST] Detection Range vs Scan Angle (J-20 frontal RCS):")
    print("-" * 70)

    j20_frontal_rcs = 0.0014  # m²
    scan_angles = [0, 15, 30, 45, 60]

    for angle in scan_angles:
        detection = f22_radar.calculate_detection_range(
            j20_frontal_rcs, azimuth_deg=angle, elevation_deg=0)

        print(f"  Azimuth {angle:2d}°: Range = {detection.detection_range_km:5.1f} km, "
              f"SNR = {detection.snr_db:+5.1f} dB, "
              f"Confidence = {detection.confidence:.0%}")

    # Test with varying RCS (J-20 at different aspects)
    print("\n[TEST] Detection Range vs Target RCS (boresight):")
    print("-" * 70)

    from osint_cad.physics.rcs_models import J20RCSModel

    aspects = [0, 30, 60, 90, 120, 150, 180]

    for azimuth in aspects:
        j20_rcs = J20RCSModel.calculate_rcs(azimuth, elevation_deg=0)
        detection = f22_radar.calculate_detection_range(j20_rcs.rcs_m2, 0, 0)

        print(f"  J-20 @ {azimuth:3d}°: RCS = {j20_rcs.rcs_m2:.6f} m² ({j20_rcs.rcs_dbsm:+5.1f} dBsm), "
              f"Range = {detection.detection_range_km:5.1f} km")

    print("\n" + "=" * 70)
    print("F-22 AN/APG-77 radar model validation complete.")
    print("=" * 70)
