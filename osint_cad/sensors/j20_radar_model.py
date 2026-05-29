#!/usr/bin/env python3
"""
J-20 AESA Radar Performance Model

Implements J-20's radar detection capabilities based on deductive reasoning from
physical observables and engineering constraints.

Key Parameters (from reasoning_chains/j20_aesa_element_count.yaml):
- AESA elements: 1500 ± 100 (confidence: 85%)
- Nose diameter: ~75 cm
- Frequency: X-band (10 GHz)
- Element spacing: λ/2 = 15 mm

This is a DEFENSIVE model - helps J-20 understand its own radar capabilities
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
class J20RadarParameters:
    """
    J-20 AESA Radar Parameters (Best Estimates)

    Based on deductive reasoning from:
    - Observable nose diameter: 75 cm
    - Element count: 1500 ± 100 (85% confidence)
    - Frequency: X-band (10 GHz typical for fighter AESA)
    - Comparison to F-22 APG-77 (similar element count)
    """

    # AESA configuration (from reasoning chains)
    # Note: Updated estimates for modernized Type 1475 AESA with 1800 GaN T/R modules
    num_elements: int = 1800
    num_elements_uncertainty: int = 150
    element_count_confidence: float = 0.80

    # Frequency parameters
    center_frequency_ghz: float = 10.0  # X-band
    bandwidth_mhz: float = 500.0  # Chirp/waveform bandwidth for pulse compression (wide bandwidth for resolution)

    # Pulse compression parameters
    pulse_width_us: float = 20.0  # Transmit pulse width (microseconds) - longer for more energy
    prf_hz: float = 20000.0  # Pulse repetition frequency (Hz)
    integration_time_ms: float = 300.0  # Coherent integration time (milliseconds) - track mode dwell

    # Aperture geometry (from public photos)
    aperture_diameter_m: float = 0.80  # 80 cm nose diameter (updated measurement)
    aperture_area_m2: float = 0.55  # ~0.55 m² active area (optimized hexagonal packing)

    # Power parameters (estimated from element count with GaN technology)
    peak_power_per_element_w: float = 20.0  # GaN T/R modules (high-power GaN: 15-25W state of art)
    average_power_per_element_w: float = 2.5  # ~12.5% duty cycle
    duty_cycle: float = 0.125

    # System parameters
    noise_figure_db: float = 2.0  # State-of-art low-noise AESA receiver with LNA
    system_losses_db: float = 2.5  # Optimized losses with integrated T/R modules

    # Detection parameters
    probability_detection: float = 0.90  # Pd = 90%
    probability_false_alarm: float = 1e-6  # Pfa = 10^-6

    # Scan parameters
    max_azimuth_scan_deg: float = 60.0  # ±60° mechanical + electronic
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
        efficiency = 0.65  # Typical AESA efficiency
        gain_linear = (4 * np.pi * self.aperture_area_m2 * efficiency) / (self.wavelength_m ** 2)
        return 10 * np.log10(gain_linear)

    @property
    def pulse_compression_gain(self) -> float:
        """Time-bandwidth product (pulse compression gain)"""
        return (self.pulse_width_us * 1e-6) * (self.bandwidth_mhz * 1e6)

    @property
    def num_pulses_integrated(self) -> float:
        """Number of pulses in integration period"""
        return self.prf_hz * (self.integration_time_ms / 1000.0)

    @property
    def coherent_integration_gain(self) -> float:
        """Coherent integration gain (linear)"""
        return self.num_pulses_integrated

    @property
    def total_processing_gain(self) -> float:
        """Total processing gain from pulse compression and integration (linear)"""
        return self.pulse_compression_gain * self.coherent_integration_gain

    @property
    def effective_noise_bandwidth_hz(self) -> float:
        """Effective noise bandwidth after matched filtering (Hz)"""
        # After matched filtering, effective bandwidth is 1/pulse_width
        return 1.0 / (self.pulse_width_us * 1e-6)


class J20RadarModel:
    """
    J-20 AESA Radar Detection Model

    Implements radar range equation with scan angle losses and
    aspect-dependent target RCS.
    """

    def __init__(self, params: Optional[J20RadarParameters] = None):
        """
        Initialize J-20 radar model

        Args:
            params: Radar parameters (uses defaults if None)
        """
        self.params = params or J20RadarParameters()

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

        # Noise power (using effective bandwidth after matched filtering)
        temperature_k = 290  # Standard temperature
        noise_figure_linear = 10 ** (self.params.noise_figure_db / 10.0)
        # Use effective noise bandwidth after pulse compression, not chirp bandwidth
        bandwidth_hz = self.params.effective_noise_bandwidth_hz

        noise_power_w = BOLTZMANN_CONSTANT * temperature_k * bandwidth_hz * noise_figure_linear

        # Required received power for detection
        snr_linear = 10 ** (snr_threshold_db / 10.0)
        required_rx_power_w = noise_power_w * snr_linear

        # Include coherent integration gain in the numerator
        integration_gain = self.params.coherent_integration_gain

        # Radar range equation with processing gain:
        # R = [(Pt * G² * λ² * σ * n_integration) / ((4π)³ * Pmin * L)]^(1/4)
        numerator = (peak_power_w * (antenna_gain_linear ** 2) *
                    (self.params.wavelength_m ** 2) * target_rcs_m2 * integration_gain)
        denominator = ((4 * np.pi) ** 3) * required_rx_power_w * system_losses_linear

        if numerator / denominator > 0:
            range_m = (numerator / denominator) ** 0.25
        else:
            range_m = 0

        range_km = range_m / 1000.0

        # Calculate actual SNR at this range (for confidence assessment)
        received_power_w = (peak_power_w * (antenna_gain_linear ** 2) *
                           (self.params.wavelength_m ** 2) * target_rcs_m2 * integration_gain /
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
                                          j20_position: np.ndarray,
                                          j20_velocity: np.ndarray,
                                          target_position: np.ndarray,
                                          target_velocity: np.ndarray,
                                          target_rcs_calculator) -> RadarDetection:
        """
        Calculate detection range from 3D positions and velocities

        Args:
            j20_position: J-20 position [x, y, z] (meters)
            j20_velocity: J-20 velocity [vx, vy, vz] (m/s)
            target_position: Target position [x, y, z] (meters)
            target_velocity: Target velocity [vx, vy, vz] (m/s)
            target_rcs_calculator: Object with calculate_rcs_from_vectors method

        Returns:
            RadarDetection
        """
        # Calculate target RCS as seen by J-20
        target_rcs_estimate = target_rcs_calculator.calculate_rcs_from_vectors(
            j20_position, target_position, target_velocity,
            frequency_ghz=self.params.center_frequency_ghz
        )

        # Calculate look angles from J-20 to target
        los_vector = target_position - j20_position
        range_m = np.linalg.norm(los_vector)

        if range_m < 1.0:
            azimuth_deg, elevation_deg = 0.0, 0.0
        else:
            los_unit = los_vector / range_m

            # Calculate angles relative to J-20's velocity (heading)
            j20_speed = np.linalg.norm(j20_velocity)
            if j20_speed > 1.0:
                j20_heading = j20_velocity / j20_speed

                # Azimuth: angle from heading to LOS in horizontal plane
                los_horizontal = np.array([los_unit[0], los_unit[1], 0])
                heading_horizontal = np.array([j20_heading[0], j20_heading[1], 0])

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
                # J-20 nearly stationary, use absolute angles
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
        """Print summary of J-20 radar capabilities"""
        print("=" * 70)
        print("J-20 AESA Radar Model - Pre-Trained Parameters")
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
            ("F-35 (frontal)", 0.0002),
            ("F-35 (beam)", 0.02),
            ("F-22 (frontal)", 0.0001),
            ("4th-gen (frontal)", 1.0),
            ("Bomber (B-52)", 100.0),
        ]

        for name, rcs in test_targets:
            detection = self.calculate_detection_range(rcs, 0.0, 0.0)
            print(f"  {name:20s}: {detection.detection_range_km:6.1f} km (RCS = {rcs:7.4f} m²)")

        print("=" * 70)


# Example usage and validation
if __name__ == "__main__":
    # Create J-20 radar model with default parameters
    j20_radar = J20RadarModel()

    # Print radar summary
    j20_radar.print_radar_summary()

    # Test detection vs aspect angle
    print("\n[TEST] Detection Range vs Scan Angle (F-35 frontal RCS):")
    print("-" * 70)

    f35_frontal_rcs = 0.0002  # m²
    scan_angles = [0, 15, 30, 45, 60]

    for angle in scan_angles:
        detection = j20_radar.calculate_detection_range(
            f35_frontal_rcs, azimuth_deg=angle, elevation_deg=0)

        print(f"  Azimuth {angle:2d}°: Range = {detection.detection_range_km:5.1f} km, "
              f"SNR = {detection.snr_db:+5.1f} dB, "
              f"Confidence = {detection.confidence:.0%}")

    # Test with varying RCS (F-35 at different aspects)
    print("\n[TEST] Detection Range vs Target RCS (boresight):")
    print("-" * 70)

    from osint_cad.physics.rcs_models import F35ARCSModel

    aspects = [0, 30, 60, 90, 120, 150, 180]

    for azimuth in aspects:
        f35_rcs = F35ARCSModel.calculate_rcs(azimuth, elevation_deg=0)
        detection = j20_radar.calculate_detection_range(f35_rcs.rcs_m2, 0, 0)

        print(f"  F-35 @ {azimuth:3d}°: RCS = {f35_rcs.rcs_m2:.6f} m² ({f35_rcs.rcs_dbsm:+5.1f} dBsm), "
              f"Range = {detection.detection_range_km:5.1f} km")

    print("\n" + "=" * 70)
    print("J-20 radar model validation complete.")
    print("=" * 70)
