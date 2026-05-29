#!/usr/bin/env python3
"""
VLBI Coherent Processing for Multi-Platform ESM

Very Long Baseline Interferometry applied to electronic warfare.
Synthesizes aperture across multiple distributed platforms for
extreme angular resolution in direction finding.

Key capability: Sub-degree bearing accuracy at 100+ km baselines.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict
from scipy.optimize import least_squares


@dataclass
class CoherentSample:
    """Coherent IQ sample with precise timing"""
    platform_id: str
    timestamp_ns: int  # Nanosecond-precision GPS time
    iq_sample: complex
    phase_calibration: float  # Platform-specific phase offset (radians)
    position: np.ndarray  # Platform position [x, y, z] at sample time


class VLBICoherentProcessor:
    """
    VLBI Coherent Processing Engine

    Combines signals from multiple distributed platforms to create
    a synthetic aperture with baseline equal to platform separation.

    Angular resolution: λ / baseline
    For 100 km baseline at 15 GHz: ~0.006 degrees
    """

    def __init__(self, wavelength: float):
        """
        Args:
            wavelength: Signal wavelength in meters
        """
        self.wavelength = wavelength
        self.platforms: Dict[str, List[CoherentSample]] = {}

    def add_sample(self, sample: CoherentSample):
        """
        Add coherent sample from platform

        Args:
            sample: CoherentSample with timing and IQ data
        """
        if sample.platform_id not in self.platforms:
            self.platforms[sample.platform_id] = []

        self.platforms[sample.platform_id].append(sample)

    def coherent_beamforming(self,
                            steering_azimuth_deg: float,
                            steering_elevation_deg: float) -> complex:
        """
        Coherent beamforming in specified direction

        Combines all platform samples with appropriate phase shifts
        to form beam in desired direction.

        Args:
            steering_azimuth_deg: Azimuth steering angle (degrees)
            steering_elevation_deg: Elevation steering angle (degrees)

        Returns:
            Complex beam output (coherent sum)
        """
        # Convert steering angles to unit vector
        az_rad = np.radians(steering_azimuth_deg)
        el_rad = np.radians(steering_elevation_deg)

        steering_vector = np.array([
            np.cos(el_rad) * np.cos(az_rad),
            np.cos(el_rad) * np.sin(az_rad),
            np.sin(el_rad)
        ])

        # Coherent sum across all platforms
        coherent_sum = 0.0 + 0.0j
        sample_count = 0

        # Find time-aligned samples across platforms
        # Simplified: use samples closest in time
        for platform_id, samples in self.platforms.items():
            if not samples:
                continue

            # Get most recent sample
            sample = samples[-1]

            # Calculate geometric delay to this platform
            # τ_geo = (platform_pos · steering_vector) / c
            geometric_delay_s = np.dot(sample.position, steering_vector) / 3e8

            # Phase shift for geometric delay
            phase_shift = 2 * np.pi * geometric_delay_s * (3e8 / self.wavelength)

            # Apply phase correction and calibration
            corrected_sample = sample.iq_sample * np.exp(-1j * (phase_shift + sample.phase_calibration))

            coherent_sum += corrected_sample
            sample_count += 1

        # Normalize by number of platforms
        if sample_count > 0:
            coherent_sum /= sample_count

        return coherent_sum

    def adaptive_beamforming_scan(self,
                                  azimuth_range: Tuple[float, float],
                                  elevation_range: Tuple[float, float],
                                  resolution_deg: float = 0.1) -> np.ndarray:
        """
        Scan beam across angular region

        Creates 2D beam pattern by scanning coherent beam.

        Args:
            azimuth_range: (min_az, max_az) in degrees
            elevation_range: (min_el, max_el) in degrees
            resolution_deg: Angular resolution for scan (degrees)

        Returns:
            2D array of beam power [azimuth x elevation]
        """
        az_points = int((azimuth_range[1] - azimuth_range[0]) / resolution_deg)
        el_points = int((elevation_range[1] - elevation_range[0]) / resolution_deg)

        az_grid = np.linspace(azimuth_range[0], azimuth_range[1], az_points)
        el_grid = np.linspace(elevation_range[0], elevation_range[1], el_points)

        beam_pattern = np.zeros((az_points, el_points))

        for i, az in enumerate(az_grid):
            for j, el in enumerate(el_grid):
                beam_output = self.coherent_beamforming(az, el)
                beam_pattern[i, j] = np.abs(beam_output)**2

        return beam_pattern

    def super_resolution_doa(self) -> Tuple[float, float]:
        """
        Super-resolution Direction of Arrival estimation

        Uses MUSIC-like algorithm extended for distributed aperture.

        Returns:
            Tuple of (azimuth_deg, elevation_deg)
        """
        # Simplified: Find peak in beam pattern
        beam_pattern = self.adaptive_beamforming_scan(
            azimuth_range=(-180, 180),
            elevation_range=(-90, 90),
            resolution_deg=0.5
        )

        # Find peak
        peak_idx = np.unravel_index(np.argmax(beam_pattern), beam_pattern.shape)

        # Convert indices to angles
        azimuth = -180 + peak_idx[0] * 0.5
        elevation = -90 + peak_idx[1] * 0.5

        return azimuth, elevation

    def calculate_baseline_resolution(self, platform_ids: List[str]) -> float:
        """
        Calculate angular resolution from platform geometry

        Resolution ≈ λ / max_baseline

        Args:
            platform_ids: List of platform IDs to include

        Returns:
            Angular resolution in degrees
        """
        if len(platform_ids) < 2:
            return float('inf')

        # Get latest positions
        positions = []
        for platform_id in platform_ids:
            if platform_id in self.platforms and self.platforms[platform_id]:
                positions.append(self.platforms[platform_id][-1].position)

        if len(positions) < 2:
            return float('inf')

        # Calculate maximum baseline
        max_baseline = 0
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                baseline = np.linalg.norm(positions[i] - positions[j])
                max_baseline = max(max_baseline, baseline)

        # Angular resolution (radians)
        resolution_rad = self.wavelength / max_baseline

        # Convert to degrees
        resolution_deg = np.degrees(resolution_rad)

        return resolution_deg


class TimeSynchronizationCorrector:
    """
    Corrects timing errors between platforms for coherent processing

    Critical for VLBI: timing errors translate directly to phase errors.
    1 ns timing error = 1 meter position error at speed of light.
    """

    def __init__(self):
        self.platform_offsets: Dict[str, float] = {}

    def estimate_timing_offset(self,
                               platform_a_id: str,
                               platform_b_id: str,
                               samples_a: List[CoherentSample],
                               samples_b: List[CoherentSample]) -> float:
        """
        Estimate timing offset between two platforms

        Uses cross-correlation of common signal to find delay.

        Args:
            platform_a_id: Platform A identifier
            platform_b_id: Platform B identifier
            samples_a: Samples from platform A
            samples_b: Samples from platform B

        Returns:
            Timing offset in nanoseconds (B relative to A)
        """
        # Extract IQ samples
        iq_a = np.array([s.iq_sample for s in samples_a])
        iq_b = np.array([s.iq_sample for s in samples_b])

        # Cross-correlate
        correlation = np.correlate(iq_a, iq_b, mode='full')

        # Find peak
        peak_idx = np.argmax(np.abs(correlation))
        center_idx = len(correlation) // 2

        # Convert to time delay (assuming 1 ns sample spacing for this example)
        delay_samples = peak_idx - center_idx
        delay_ns = delay_samples * 1.0  # 1 ns per sample

        return delay_ns

    def apply_timing_correction(self,
                               sample: CoherentSample,
                               reference_platform_id: str) -> CoherentSample:
        """
        Apply timing correction to align sample with reference platform

        Args:
            sample: Sample to correct
            reference_platform_id: Reference platform for timing

        Returns:
            Time-corrected sample
        """
        if sample.platform_id not in self.platform_offsets:
            # No correction needed (or not yet calibrated)
            return sample

        offset_ns = self.platform_offsets[sample.platform_id]

        # Adjust timestamp
        corrected_timestamp = sample.timestamp_ns - int(offset_ns)

        return CoherentSample(
            platform_id=sample.platform_id,
            timestamp_ns=corrected_timestamp,
            iq_sample=sample.iq_sample,
            phase_calibration=sample.phase_calibration,
            position=sample.position
        )


# Example usage
if __name__ == "__main__":
    print("VLBI Coherent Processing for Multi-Platform ESM")
    print("=" * 60)

    # Simulate 3-platform VLBI system
    wavelength = 0.02  # 15 GHz -> 2 cm wavelength
    processor = VLBICoherentProcessor(wavelength)

    # Platform positions (100 km baseline triangle)
    platform_positions = {
        'Platform-1': np.array([0, 0, 10000]),  # meters
        'Platform-2': np.array([100000, 0, 10000]),  # 100 km east
        'Platform-3': np.array([50000, 86600, 10000])  # 100 km northeast
    }

    # Simulate signal from bearing 45° azimuth, 0° elevation
    true_azimuth = 45.0
    true_elevation = 0.0
    signal_frequency = 15e9  # 15 GHz

    print(f"\nSimulating signal from:")
    print(f"  Azimuth: {true_azimuth}°")
    print(f"  Elevation: {true_elevation}°")

    # Add samples from each platform
    timestamp = int(1e18)  # Nanoseconds since epoch

    for platform_id, position in platform_positions.items():
        # Simulate received signal with geometric delay
        az_rad = np.radians(true_azimuth)
        el_rad = np.radians(true_elevation)

        signal_direction = np.array([
            np.cos(el_rad) * np.cos(az_rad),
            np.cos(el_rad) * np.sin(az_rad),
            np.sin(el_rad)
        ])

        # Geometric delay
        geometric_delay = np.dot(position, signal_direction) / 3e8  # seconds
        phase_delay = 2 * np.pi * signal_frequency * geometric_delay

        # Simulate received signal
        iq_sample = np.exp(1j * phase_delay) * (1.0 + 0.1j)

        sample = CoherentSample(
            platform_id=platform_id,
            timestamp_ns=timestamp,
            iq_sample=iq_sample,
            phase_calibration=0.0,
            position=position
        )

        processor.add_sample(sample)

    # Perform super-resolution DOA estimation
    print(f"\nPerforming VLBI DOA estimation...")
    estimated_az, estimated_el = processor.super_resolution_doa()

    print(f"  Estimated Azimuth: {estimated_az:.2f}°")
    print(f"  Estimated Elevation: {estimated_el:.2f}°")
    print(f"  Azimuth Error: {abs(estimated_az - true_azimuth):.2f}°")
    print(f"  Elevation Error: {abs(estimated_el - true_elevation):.2f}°")

    # Calculate theoretical resolution
    resolution = processor.calculate_baseline_resolution(list(platform_positions.keys()))
    print(f"\nTheoretical angular resolution: {resolution:.4f}°")
    print(f"  (vs monolithic antenna: ~3.0°)")
    print(f"  Improvement factor: {3.0 / resolution:.0f}x")

    print("\n" + "=" * 60)
    print("VLBI processing complete.")
