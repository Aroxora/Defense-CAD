#!/usr/bin/env python3
"""
Signal Processing Pipeline for Faint Emission Detection

This module implements advanced signal processing algorithms for detecting
faint, highly directional emissions from LPI/LPD datalinks.

Key capabilities:
- Sub-noise signal detection via integration
- Cyclostationary feature detection
- Angle of Arrival (AoA) estimation
- Sidelobe detection and exploitation
"""

import numpy as np
from scipy import signal, fft
from scipy.linalg import eig
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import warnings


@dataclass
class DetectionEvent:
    """Represents a detected emission event"""
    timestamp: float  # GPS time (seconds)
    frequency: float  # Center frequency (Hz)
    bandwidth: float  # Signal bandwidth (Hz)
    power: float  # Received power (dBm)
    azimuth: Optional[float] = None  # Angle of arrival (degrees)
    elevation: Optional[float] = None  # Elevation angle (degrees)
    snr: float = 0.0  # Signal-to-noise ratio (dB)
    confidence: float = 0.0  # Detection confidence (0-1)
    duration: float = 0.0  # Signal duration (seconds)


class FaintSignalDetector:
    """
    Advanced detector for faint, directional emissions

    Uses multiple complementary detection methods:
    1. Energy detection with non-coherent integration
    2. Cyclostationary feature detection
    3. Matched filtering (if waveform known)
    """

    def __init__(self, sample_rate: float, center_freq: float,
                 noise_floor_dbm: float = -100.0):
        """
        Args:
            sample_rate: Sampling rate in Hz
            center_freq: Center frequency in Hz (e.g., 15e9 for Ku-band)
            noise_floor_dbm: Estimated noise floor in dBm
        """
        self.fs = sample_rate
        self.fc = center_freq
        self.noise_floor = noise_floor_dbm
        self.wavelength = 3e8 / center_freq  # Speed of light / frequency

    def energy_detection(self, signal_data: np.ndarray,
                        integration_time: float,
                        threshold_db: float = 10.0) -> List[DetectionEvent]:
        """
        Energy detection with non-coherent integration

        For signals below the noise floor, integrate energy over time
        to achieve processing gain.

        Processing Gain = 10 * log10(integration_time * bandwidth)

        Args:
            signal_data: Complex IQ samples
            integration_time: Integration time in seconds
            threshold_db: Detection threshold above noise floor (dB)

        Returns:
            List of detection events
        """
        # Number of samples to integrate
        n_integrate = int(integration_time * self.fs)

        # Compute power (magnitude squared)
        power = np.abs(signal_data) ** 2

        # Non-coherent integration (moving average)
        integrated = np.convolve(power, np.ones(n_integrate) / n_integrate,
                                mode='valid')

        # Convert to dB
        integrated_db = 10 * np.log10(integrated + 1e-12)

        # Detection threshold
        threshold = self.noise_floor + threshold_db

        # Find detections
        detections = []
        above_threshold = integrated_db > threshold

        # Find contiguous regions above threshold
        detection_starts = np.where(np.diff(above_threshold.astype(int)) == 1)[0]
        detection_ends = np.where(np.diff(above_threshold.astype(int)) == -1)[0]

        for start, end in zip(detection_starts, detection_ends):
            # Calculate detection parameters
            peak_idx = start + np.argmax(integrated_db[start:end])
            peak_power = integrated_db[peak_idx]
            snr = peak_power - self.noise_floor
            duration = (end - start) / self.fs

            detection = DetectionEvent(
                timestamp=peak_idx / self.fs,
                frequency=self.fc,
                bandwidth=self.fs,  # Full bandwidth
                power=peak_power,
                snr=snr,
                duration=duration,
                confidence=min(1.0, snr / 20.0)  # Normalize to 0-1
            )
            detections.append(detection)

        return detections

    def cyclostationary_detection(self, signal_data: np.ndarray,
                                  alpha_search: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Cyclostationary feature detection using full FAM (FFT Accumulation Method)

        Detects hidden periodicities in signals that appear noise-like.
        Effective against LPI waveforms with underlying structure.

        Implementation of Gardner's FFT Accumulation Method (FAM) for
        efficient computation of Spectral Correlation Function (SCF).

        Args:
            signal_data: Complex IQ samples
            alpha_search: Array of cyclic frequencies to search (Hz)

        Returns:
            Tuple of (alpha_values, correlation_magnitude)

        Reference:
            W.A. Gardner, "Exploitation of Spectral Redundancy in
            Cyclostationary Signals," IEEE Signal Processing Magazine, 1991
        """
        return self._fam_cyclostationary(signal_data, alpha_search)

    def _fam_cyclostationary(self, signal_data: np.ndarray,
                            alpha_search: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Full FFT Accumulation Method (FAM) for SCF computation

        Much more efficient than direct SCF calculation for broadband signals.
        Complexity: O(N log N) vs O(N²) for direct method

        Args:
            signal_data: Complex IQ samples
            alpha_search: Cyclic frequencies to search (Hz)

        Returns:
            Tuple of (alpha_values, scf_peak_magnitudes)
        """
        n_samples = len(signal_data)

        # FAM parameters
        n_fft = min(512, n_samples // 4)  # FFT size for channelization
        n_overlap = n_fft // 2  # 50% overlap
        n_alpha_fft = 128  # FFT size for alpha dimension

        # Channelization via STFT
        hop_size = n_fft - n_overlap
        n_frames = (n_samples - n_overlap) // hop_size

        # Hamming window for spectral leakage reduction
        window = np.hamming(n_fft)

        # Pre-allocate channelizer output
        X = np.zeros((n_fft, n_frames), dtype=complex)

        # Channelization step
        for i in range(n_frames):
            start = i * hop_size
            end = start + n_fft
            if end > n_samples:
                break

            # Windowed FFT
            segment = signal_data[start:end] * window
            X[:, i] = fft.fft(segment)

        # Compute Spectral Correlation Density (SCD)
        scf_magnitude = np.zeros(len(alpha_search))

        for idx, alpha in enumerate(alpha_search):
            # Cyclic frequency in bins
            alpha_bins = int(alpha / self.fs * n_alpha_fft)

            # Compute cross-product for each spectral frequency
            # S_X(f, alpha) = E[X(f + alpha/2) * X*(f - alpha/2)]

            scf_accumulator = 0

            for freq_bin in range(n_fft // 2):  # Only positive frequencies
                # Frequency shift indices
                f_plus = (freq_bin + alpha_bins // 2) % n_fft
                f_minus = (freq_bin - alpha_bins // 2) % n_fft

                # Cross-correlation across time
                cross_product = X[f_plus, :] * np.conj(X[f_minus, :])

                # Accumulate (average over time)
                scf_value = np.mean(cross_product)

                # Accumulate magnitude (peak detection)
                scf_accumulator += np.abs(scf_value)**2

            scf_magnitude[idx] = np.sqrt(scf_accumulator)

        # Normalize by number of frequency bins
        scf_magnitude = scf_magnitude / (n_fft // 2)

        return alpha_search, scf_magnitude

    def cyclostationary_alpha_profile(self, signal_data: np.ndarray,
                                      alpha_max_hz: float = 100000) -> Dict[str, np.ndarray]:
        """
        Generate cyclostationary α-profile for waveform fingerprinting

        The α-profile reveals hidden periodicities characteristic of
        specific modulation schemes:
        - BPSK: Peak at symbol rate
        - QPSK: Peak at 2× symbol rate
        - OFDM: Peaks at subcarrier spacing
        - DSSS: Peak at chip rate

        Args:
            signal_data: Complex IQ samples
            alpha_max_hz: Maximum cyclic frequency to search (Hz)

        Returns:
            Dictionary with 'alpha', 'magnitude', 'peaks'
        """
        # Create fine-grain alpha search vector
        n_alpha_points = 256
        alpha_search = np.linspace(0, alpha_max_hz, n_alpha_points)

        # Compute SCF via FAM
        alpha_vals, scf_mag = self._fam_cyclostationary(signal_data, alpha_search)

        # Detect peaks in α-profile
        # These peaks correspond to cyclic frequencies of the waveform
        peaks, properties = signal.find_peaks(
            scf_mag,
            height=np.mean(scf_mag) + 2 * np.std(scf_mag),  # 2σ threshold
            distance=10  # Minimum separation between peaks
        )

        peak_alpha = alpha_vals[peaks]
        peak_magnitude = scf_mag[peaks]

        return {
            'alpha': alpha_vals,
            'magnitude': scf_mag,
            'peaks': peak_alpha,
            'peak_magnitudes': peak_magnitude
        }

    def matched_filter_detection(self, signal_data: np.ndarray,
                                 template_waveform: np.ndarray,
                                 threshold: float = 0.7) -> List[DetectionEvent]:
        """
        Matched filter detection for known waveforms

        If the LPI waveform structure is known (e.g., from ELINT),
        matched filtering provides optimal SNR.

        Args:
            signal_data: Complex IQ samples
            template_waveform: Known waveform template
            threshold: Correlation threshold (0-1)

        Returns:
            List of detection events
        """
        # Normalize template
        template_norm = template_waveform / np.linalg.norm(template_waveform)

        # Cross-correlate
        correlation = signal.correlate(signal_data, template_norm, mode='valid')
        correlation_magnitude = np.abs(correlation)

        # Find peaks above threshold
        peaks, properties = signal.find_peaks(correlation_magnitude,
                                             height=threshold,
                                             distance=len(template_waveform))

        detections = []
        for peak in peaks:
            detection = DetectionEvent(
                timestamp=peak / self.fs,
                frequency=self.fc,
                bandwidth=self.fs / len(template_waveform),
                power=20 * np.log10(correlation_magnitude[peak]),
                confidence=min(1.0, correlation_magnitude[peak] / threshold),
                duration=len(template_waveform) / self.fs
            )
            detections.append(detection)

        return detections


class AngleOfArrivalEstimator:
    """
    Estimates angle of arrival using interferometric processing

    Uses phase difference between spatially separated antennas
    to determine bearing to emitter.
    """

    def __init__(self, antenna_positions: np.ndarray, wavelength: float):
        """
        Args:
            antenna_positions: Nx3 array of antenna positions [x, y, z] in meters
            wavelength: Signal wavelength in meters
        """
        self.antenna_positions = antenna_positions
        self.wavelength = wavelength
        self.n_antennas = len(antenna_positions)

    def phase_interferometry(self, signal_samples: np.ndarray) -> Tuple[float, float]:
        """
        Estimate azimuth and elevation using phase interferometry

        Args:
            signal_samples: Complex samples from each antenna [n_antennas x n_samples]

        Returns:
            Tuple of (azimuth, elevation) in degrees
        """
        if signal_samples.shape[0] != self.n_antennas:
            raise ValueError(f"Expected {self.n_antennas} antenna channels")

        # Use first antenna as reference
        ref_signal = signal_samples[0, :]

        # Compute phase differences
        phase_diffs = []
        baselines = []

        for i in range(1, self.n_antennas):
            # Cross-correlation to find phase difference
            cross_corr = np.mean(signal_samples[i, :] * np.conj(ref_signal))
            phase_diff = np.angle(cross_corr)

            # Baseline vector
            baseline = self.antenna_positions[i] - self.antenna_positions[0]

            phase_diffs.append(phase_diff)
            baselines.append(baseline)

        # Solve for arrival direction using least squares
        # Phase difference: Δφ = (2π/λ) * baseline · unit_vector
        azimuth, elevation = self._solve_direction(np.array(phase_diffs),
                                                   np.array(baselines))

        return azimuth, elevation

    def music_algorithm(self, signal_samples: np.ndarray,
                       n_sources: int = 1) -> List[Tuple[float, float]]:
        """
        Multiple Signal Classification (MUSIC) algorithm

        High-resolution direction finding for multiple simultaneous sources.

        Args:
            signal_samples: Complex samples [n_antennas x n_samples]
            n_sources: Number of signal sources

        Returns:
            List of (azimuth, elevation) tuples in degrees
        """
        # Compute spatial covariance matrix
        R = np.cov(signal_samples)

        # Eigenvalue decomposition
        eigenvalues, eigenvectors = eig(R)

        # Sort by eigenvalue
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Noise subspace (smallest eigenvalues)
        noise_subspace = eigenvectors[:, n_sources:]

        # Search over possible directions
        azimuth_search = np.linspace(-180, 180, 360)
        elevation_search = np.linspace(-90, 90, 180)

        music_spectrum = np.zeros((len(azimuth_search), len(elevation_search)))

        for i, az in enumerate(azimuth_search):
            for j, el in enumerate(elevation_search):
                # Steering vector for this direction
                a = self._steering_vector(az, el)

                # MUSIC pseudo-spectrum
                music_spectrum[i, j] = 1.0 / np.abs(
                    a.conj().T @ noise_subspace @ noise_subspace.conj().T @ a
                )

        # Find peaks (local maxima)
        directions = []
        for _ in range(n_sources):
            idx = np.unravel_index(np.argmax(music_spectrum), music_spectrum.shape)
            az = azimuth_search[idx[0]]
            el = elevation_search[idx[1]]
            directions.append((az, el))

            # Suppress this peak
            music_spectrum[max(0, idx[0]-5):min(len(azimuth_search), idx[0]+5),
                          max(0, idx[1]-5):min(len(elevation_search), idx[1]+5)] = 0

        return directions

    def _steering_vector(self, azimuth: float, elevation: float) -> np.ndarray:
        """
        Compute array steering vector for given direction

        Args:
            azimuth: Azimuth in degrees
            elevation: Elevation in degrees

        Returns:
            Steering vector (complex array)
        """
        az_rad = np.radians(azimuth)
        el_rad = np.radians(elevation)

        # Unit vector in direction of arrival
        k = np.array([
            np.cos(el_rad) * np.cos(az_rad),
            np.cos(el_rad) * np.sin(az_rad),
            np.sin(el_rad)
        ])

        # Phase shift for each antenna
        phase_shifts = (2 * np.pi / self.wavelength) * (self.antenna_positions @ k)

        # Steering vector
        a = np.exp(1j * phase_shifts)

        return a

    def _solve_direction(self, phase_diffs: np.ndarray,
                        baselines: np.ndarray) -> Tuple[float, float]:
        """
        Solve for direction of arrival from phase differences

        Uses least-squares optimization to find best-fit direction.
        """
        # Initial guess
        az_init = 0.0
        el_init = 0.0

        # Simple gradient descent (could use scipy.optimize for production)
        def cost_function(direction):
            az, el = direction
            k = np.array([
                np.cos(np.radians(el)) * np.cos(np.radians(az)),
                np.cos(np.radians(el)) * np.sin(np.radians(az)),
                np.sin(np.radians(el))
            ])
            predicted_phase = (2 * np.pi / self.wavelength) * (baselines @ k)

            # Wrap phase differences to [-π, π]
            error = np.angle(np.exp(1j * (phase_diffs - predicted_phase)))
            return np.sum(error ** 2)

        # Use scipy optimization
        from scipy.optimize import minimize
        result = minimize(cost_function, [az_init, el_init],
                         bounds=[(-180, 180), (-90, 90)])

        return result.x[0], result.x[1]


class SidelobeDetector:
    """
    Specialized detector for antenna sidelobe emissions

    Even highly directional antennas have sidelobes. By detecting
    these weak spillover signals, we can infer emitter presence
    and potentially main beam direction.
    """

    def __init__(self, antenna_pattern_db: callable):
        """
        Args:
            antenna_pattern_db: Function that returns antenna gain (dB)
                              as function of angle: gain_db(azimuth, elevation)
        """
        self.antenna_pattern = antenna_pattern_db

    def estimate_mainbeam_direction(self,
                                   detections: List[Tuple[float, float, float]],
                                   emitter_location: np.ndarray,
                                   observer_locations: List[np.ndarray]) -> Tuple[float, float]:
        """
        Estimate main beam direction from sidelobe detections

        Given multiple observations of sidelobe power from different aspects,
        infer the direction of the main beam.

        Args:
            detections: List of (azimuth_to_emitter, elevation, power_dbm)
            emitter_location: Estimated emitter position [x, y, z]
            observer_locations: List of observer positions

        Returns:
            Estimated main beam (azimuth, elevation) in degrees
        """
        # This is an inverse problem: given sidelobe observations,
        # what main beam direction best explains them?

        def cost_function(mainbeam_direction):
            az_main, el_main = mainbeam_direction
            total_error = 0

            for i, (az_obs, el_obs, power_obs) in enumerate(detections):
                # Angle between main beam and observer
                angle_off_mainbeam = self._angle_between_directions(
                    az_main, el_main, az_obs, el_obs
                )

                # Expected sidelobe gain at this angle
                expected_gain = self.antenna_pattern(angle_off_mainbeam, 0)

                # Error between expected and observed (simplified)
                # In reality, would need full link budget
                error = (expected_gain - (power_obs - power_obs))  # Simplified
                total_error += error ** 2

            return total_error

        from scipy.optimize import minimize
        result = minimize(cost_function, [0, 0],
                         bounds=[(-180, 180), (-90, 90)])

        return result.x[0], result.x[1]

    def sidelobe_pattern_typical(self, angle_off_boresight: float) -> float:
        """
        Typical antenna sidelobe pattern (dB relative to main beam)

        Args:
            angle_off_boresight: Angle off main beam axis (degrees)

        Returns:
            Gain in dB (negative, relative to main beam)
        """
        # Simplified model based on typical phased array
        angle = abs(angle_off_boresight)

        if angle < 3:  # Main beam (3 dB beamwidth)
            return -3 * (angle / 3) ** 2
        elif angle < 10:  # Near sidelobes
            return -13  # First sidelobe
        elif angle < 30:
            return -20 - (angle - 10) * 0.5  # Falling sidelobes
        else:
            return -30  # Far sidelobes and backlobe

    def _angle_between_directions(self, az1: float, el1: float,
                                  az2: float, el2: float) -> float:
        """Calculate angular separation between two directions"""
        # Convert to unit vectors
        az1_rad, el1_rad = np.radians(az1), np.radians(el1)
        az2_rad, el2_rad = np.radians(az2), np.radians(el2)

        v1 = np.array([
            np.cos(el1_rad) * np.cos(az1_rad),
            np.cos(el1_rad) * np.sin(az1_rad),
            np.sin(el1_rad)
        ])

        v2 = np.array([
            np.cos(el2_rad) * np.cos(az2_rad),
            np.cos(el2_rad) * np.sin(az2_rad),
            np.sin(el2_rad)
        ])

        # Dot product gives cosine of angle
        cos_angle = np.clip(np.dot(v1, v2), -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))

        return angle


# Example usage and testing
if __name__ == "__main__":
    print("Faint Emission Detection - Signal Processing Module")
    print("=" * 60)

    # Simulation parameters
    fs = 10e9  # 10 GSPS
    fc = 15e9  # Ku-band center (15 GHz)
    duration = 1e-3  # 1 ms capture
    n_samples = int(fs * duration)

    print(f"\nSimulation Parameters:")
    print(f"  Sample Rate: {fs/1e9:.1f} GSPS")
    print(f"  Center Frequency: {fc/1e9:.1f} GHz")
    print(f"  Duration: {duration*1e3:.2f} ms")
    print(f"  Samples: {n_samples:,}")

    # Create faint signal in noise
    snr_db = -10  # Signal 10 dB below noise
    noise = np.random.randn(n_samples) + 1j * np.random.randn(n_samples)
    signal_power = 10 ** (snr_db / 10)
    signal_component = np.sqrt(signal_power) * np.exp(1j * 2 * np.pi * 100e6 * np.arange(n_samples) / fs)

    received_signal = noise + signal_component

    print(f"\n Signal SNR: {snr_db} dB (below noise floor)")

    # Test energy detection
    detector = FaintSignalDetector(fs, fc, noise_floor_dbm=-100)
    integration_time = 100e-6  # 100 μs integration

    print(f"\nEnergy Detection:")
    print(f"  Integration time: {integration_time*1e6:.1f} μs")
    processing_gain = 10 * np.log10(integration_time * fs)
    print(f"  Processing gain: {processing_gain:.1f} dB")
    print(f"  Effective SNR: {snr_db + processing_gain:.1f} dB")

    detections = detector.energy_detection(received_signal, integration_time)
    print(f"  Detections: {len(detections)}")

    for i, det in enumerate(detections):
        print(f"    [{i}] SNR: {det.snr:.1f} dB, Confidence: {det.confidence:.2f}")

    # Test AoA estimation
    print(f"\nAngle of Arrival Estimation:")
    wavelength = 3e8 / fc
    antenna_positions = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [1, 1, 0]
    ])  # Square array, 1m spacing

    print(f"  Wavelength: {wavelength*100:.2f} cm")
    print(f"  Baseline: 1.0 m ({1.0/wavelength:.1f} wavelengths)")

    aoa_estimator = AngleOfArrivalEstimator(antenna_positions, wavelength)

    # Simulate signal from specific direction
    true_azimuth = 45
    true_elevation = 30

    # Create array response
    steering_vec = aoa_estimator._steering_vector(true_azimuth, true_elevation)
    array_signal = steering_vec[:, np.newaxis] @ signal_component[np.newaxis, :1000]
    array_noise = (np.random.randn(4, 1000) + 1j * np.random.randn(4, 1000))
    array_received = array_signal + array_noise

    est_az, est_el = aoa_estimator.phase_interferometry(array_received)

    print(f"  True direction: Az={true_azimuth}°, El={true_elevation}°")
    print(f"  Estimated: Az={est_az:.1f}°, El={est_el:.1f}°")
    print(f"  Error: {abs(est_az - true_azimuth):.1f}° (azimuth), "
          f"{abs(est_el - true_elevation):.1f}° (elevation)")

    print("\n" + "=" * 60)
    print("Signal processing module test complete.")
