#!/usr/bin/env python3
"""
Adaptive Antenna Patterns and Electronic Protection (EP) Countermeasures

Implements operational-grade electronic warfare capabilities:
- Adaptive antenna nulling
- Dynamic sidelobe control
- Electronic Protection (EP) techniques
- Deception and decoy emissions
- Low Probability of Detection/Intercept (LPD/LPI) features
"""

from dataclasses import dataclass
from enum import Enum

import numpy as np


class EPMode(Enum):
    """Electronic Protection operating modes"""
    NORMAL = "normal"
    SILENT = "silent"  # No emissions
    LPI_ENHANCED = "lpi_enhanced"  # Maximum LPI techniques
    DECEPTION = "deception"  # Active deception
    ADAPTIVE_POWER = "adaptive_power"  # Power management
    FREQUENCY_AGILE = "frequency_agile"  # Rapid frequency hopping


@dataclass
class ThreatVector:
    """Detected or suspected threat direction"""
    azimuth: float  # degrees
    elevation: float  # degrees
    threat_level: float  # 0-1
    detection_time: float  # timestamp


class AdaptiveAntennaPattern:
    """
    Adaptive phased array antenna with null steering

    Implements real-time pattern adaptation to reduce detection probability
    """

    def __init__(self,
                 n_elements: int = 64,
                 baseline_gain_db: float = 20,
                 baseline_beamwidth_deg: float = 3.0,
                 sidelobe_target_db: float = -30):
        """
        Args:
            n_elements: Number of antenna elements
            baseline_gain_db: Nominal main beam gain
            baseline_beamwidth_deg: Nominal 3dB beamwidth
            sidelobe_target_db: Target sidelobe level (dB below main beam)
        """
        self.n_elements = n_elements
        self.baseline_gain = baseline_gain_db
        self.baseline_beamwidth = baseline_beamwidth_deg
        self.sidelobe_target = sidelobe_target_db

        # Current antenna configuration
        self.mainbeam_azimuth = 0.0
        self.mainbeam_elevation = 0.0
        self.null_directions: list = []
        self.adaptive_nulling_enabled = True

        # Element weights (complex) for beamforming
        self.element_weights = np.ones(n_elements, dtype=complex)

    def point_mainbeam(self, azimuth: float, elevation: float):
        """
        Steer main beam to specified direction

        Args:
            azimuth: Azimuth angle (degrees)
            elevation: Elevation angle (degrees)
        """
        self.mainbeam_azimuth = azimuth
        self.mainbeam_elevation = elevation

        # Update element weights for beam steering
        self._compute_beamforming_weights()

    def add_adaptive_null(self, threat: ThreatVector):
        """
        Add adaptive null in threat direction

        Args:
            threat: Threat vector to null
        """
        self.null_directions.append(threat)

        # Re-compute weights with nulling constraint
        if self.adaptive_nulling_enabled:
            self._compute_adaptive_weights()

    def clear_nulls(self):
        """Clear all adaptive nulls"""
        self.null_directions = []
        self._compute_beamforming_weights()

    def get_gain(self, azimuth: float, elevation: float) -> float:
        """
        Calculate antenna gain in specified direction

        Args:
            azimuth: Look direction azimuth (degrees)
            elevation: Look direction elevation (degrees)

        Returns:
            Antenna gain (dB)
        """
        # Angle off mainbeam boresight
        angle_off = self._angular_separation(
            self.mainbeam_azimuth, self.mainbeam_elevation,
            azimuth, elevation
        )

        # Check if this direction has an adaptive null
        null_depth = 0
        for threat in self.null_directions:
            threat_separation = self._angular_separation(
                threat.azimuth, threat.elevation,
                azimuth, elevation
            )

            if threat_separation < 5.0:  # Within null region
                # Null depth depends on adaptive algorithm quality
                null_depth = max(null_depth, 20 + threat.threat_level * 20)  # 20-40 dB null

        # Baseline pattern
        if angle_off < self.baseline_beamwidth / 2:
            # Main beam
            baseline_gain = self.baseline_gain - 3 * (angle_off / (self.baseline_beamwidth / 2))**2
        elif angle_off < 10:
            # First sidelobe
            baseline_gain = self.baseline_gain - 13
        elif angle_off < 30:
            # Transitional sidelobes
            baseline_gain = self.baseline_gain - 20 - (angle_off - 10) * 0.5
        else:
            # Far sidelobes and backlobe
            baseline_gain = self.baseline_gain + self.sidelobe_target

        # Apply adaptive null
        effective_gain = baseline_gain - null_depth

        return effective_gain

    def get_dynamic_sidelobe_level(self, current_time: float) -> float:
        """
        Calculate dynamic sidelobe level

        In operational systems, sidelobe levels vary with:
        - Element failures
        - Temperature variations
        - Beamsteering angle
        - Array calibration errors

        Args:
            current_time: Current time (for time-varying effects)

        Returns:
            Actual sidelobe level (dB below main beam)
        """
        # Nominal target
        nominal = self.sidelobe_target

        # Random variation due to environmental factors (±3 dB)
        environmental_variation = np.random.uniform(-3, 3)

        # Slow drift due to temperature (sinusoidal, ±2 dB over time)
        temp_drift = 2 * np.sin(2 * np.pi * current_time / 3600)  # 1-hour period

        # Element failures degrade performance
        # Assume 1-2% element failure rate
        failure_rate = np.random.uniform(0.01, 0.02)
        n_failed = int(failure_rate * self.n_elements)
        failure_degradation = n_failed * 0.5  # 0.5 dB per failed element

        actual_sidelobe = nominal + environmental_variation + temp_drift + failure_degradation

        return actual_sidelobe

    def _angular_separation(self, az1: float, el1: float, az2: float, el2: float) -> float:
        """Calculate angular separation between two directions"""
        az1_rad, el1_rad = np.radians(az1), np.radians(el1)
        az2_rad, el2_rad = np.radians(az2), np.radians(el2)

        # Convert to unit vectors
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

    def _compute_beamforming_weights(self):
        """Compute element weights for basic beamsteering"""
        # Simplified: uniform weighting
        # Production systems use Taylor/Chebyshev tapering
        self.element_weights = np.ones(self.n_elements, dtype=complex)

    def _compute_adaptive_weights(self):
        """
        Compute adaptive weights with nulling constraints

        Uses constrained optimization (simplified LCMV beamformer)
        """
        # Simplified implementation
        # Real systems use LMS, RLS, or sample matrix inversion

        # For each null, apply a simple weight adjustment
        for _threat in self.null_directions:
            # This is a placeholder - real implementation requires
            # full array manifold and optimization
            pass


class ElectronicProtection:
    """
    Electronic Protection (EP) suite

    Implements techniques to reduce detection and tracking probability
    """

    def __init__(self):
        self.current_mode = EPMode.NORMAL
        self.threat_library: list = []

        # EP parameters
        self.power_adaptation_enabled = True
        self.frequency_hopping_enabled = True
        self.burst_shaping_enabled = True
        self.decoy_enabled = False

        # Frequency hopping pattern
        self.hop_frequencies_hz = []
        self.hop_index = 0
        self.hop_interval_sec = 0.1

        # Power management
        self.min_power_dbm = 10
        self.max_power_dbm = 33
        self.current_power_dbm = 30

    def set_mode(self, mode: EPMode):
        """Set EP operating mode"""
        self.current_mode = mode

        if mode == EPMode.SILENT:
            self.current_power_dbm = 0  # No transmission
        elif mode == EPMode.LPI_ENHANCED:
            self._activate_lpi_mode()
        elif mode == EPMode.DECEPTION:
            self.decoy_enabled = True
        elif mode == EPMode.ADAPTIVE_POWER:
            self.power_adaptation_enabled = True

    def _activate_lpi_mode(self):
        """Activate enhanced LPI mode"""
        # Reduce power to minimum needed for link
        self.current_power_dbm = self.min_power_dbm

        # Enable all LPI techniques
        self.frequency_hopping_enabled = True
        self.burst_shaping_enabled = True

    def compute_adaptive_power(self,
                              link_distance_m: float,
                              required_snr_db: float = 10,
                              receiver_noise_figure_db: float = 3) -> float:
        """
        Compute minimum power needed for link closure

        Args:
            link_distance_m: Distance to intended receiver
            required_snr_db: Required SNR for communication
            receiver_noise_figure_db: Receiver noise figure

        Returns:
            Transmit power (dBm)
        """
        # Link budget calculation
        # Required: Rx_power >= Noise_floor + NF + SNR_req

        # Noise floor (assuming 100 MHz bandwidth)
        k_boltzmann = -228.6  # dBW/Hz/K
        T = 290  # K
        bandwidth_hz = 100e6
        noise_floor_dbm = k_boltzmann + 10 * np.log10(T) + 10 * np.log10(bandwidth_hz) + 30

        required_rx_power = noise_floor_dbm + receiver_noise_figure_db + required_snr_db

        # Free space path loss (simplified, 15 GHz)
        frequency_hz = 15e9
        wavelength = 299792458.0 / frequency_hz
        path_loss_db = 20 * np.log10(4 * np.pi * link_distance_m / wavelength)

        # Required transmit power
        # Tx_power = Rx_power + Path_loss - Antenna_gains
        antenna_gain_tx = 20  # dBi
        antenna_gain_rx = 20  # dBi

        required_tx_power = required_rx_power + path_loss_db - antenna_gain_tx - antenna_gain_rx

        # Add margin
        margin_db = 3
        adaptive_power = required_tx_power + margin_db

        # Clamp to limits
        adaptive_power = np.clip(adaptive_power, self.min_power_dbm, self.max_power_dbm)

        if self.power_adaptation_enabled:
            self.current_power_dbm = adaptive_power

        return adaptive_power

    def get_next_frequency(self, current_time: float) -> float:
        """
        Get next frequency in hopping pattern

        Args:
            current_time: Current time

        Returns:
            Next frequency (Hz)
        """
        if not self.frequency_hopping_enabled or len(self.hop_frequencies_hz) == 0:
            return 15e9  # Default 15 GHz

        # Pseudo-random hopping pattern
        # Real systems use cryptographic sequences
        self.hop_index = (self.hop_index + 1) % len(self.hop_frequencies_hz)

        return self.hop_frequencies_hz[self.hop_index]

    def generate_hop_pattern(self,
                            center_freq_hz: float = 15e9,
                            bandwidth_hz: float = 3e9,
                            n_channels: int = 100):
        """
        Generate frequency hopping pattern

        Args:
            center_freq_hz: Center frequency
            bandwidth_hz: Total bandwidth available
            n_channels: Number of hop channels
        """
        # Divide bandwidth into channels
        freq_min = center_freq_hz - bandwidth_hz / 2
        freq_max = center_freq_hz + bandwidth_hz / 2

        # Random permutation of channels
        channels = np.linspace(freq_min, freq_max, n_channels)
        self.hop_frequencies_hz = list(np.random.permutation(channels))

    def shape_burst(self,
                   nominal_duration_sec: float = 100e-6,
                   randomize: bool = True) -> float:
        """
        Shape transmission burst for LPI

        Args:
            nominal_duration_sec: Nominal burst duration
            randomize: Whether to randomize duration

        Returns:
            Actual burst duration (seconds)
        """
        if not self.burst_shaping_enabled:
            return nominal_duration_sec

        if randomize:
            # Random variation ±50%
            variation = np.random.uniform(0.5, 1.5)
            actual_duration = nominal_duration_sec * variation
        else:
            actual_duration = nominal_duration_sec

        return actual_duration

    def generate_decoy_emission(self,
                               true_position: np.ndarray,
                               true_frequency_hz: float,
                               current_time: float) -> dict:
        """
        Generate decoy emission parameters

        Args:
            true_position: Actual emitter position
            true_frequency_hz: True emission frequency
            current_time: Current time

        Returns:
            Dictionary with decoy parameters
        """
        if not self.decoy_enabled or self.current_mode != EPMode.DECEPTION:
            return None

        # Create false emission at different location
        # Offset by 1-5 km in random direction
        offset_distance = np.random.uniform(1000, 5000)
        offset_angle = np.random.uniform(0, 360)

        offset = np.array([
            offset_distance * np.cos(np.radians(offset_angle)),
            offset_distance * np.sin(np.radians(offset_angle)),
            np.random.uniform(-500, 500)
        ])

        decoy_position = true_position + offset

        # Frequency offset
        freq_offset = np.random.uniform(-100e6, 100e6)
        decoy_frequency = true_frequency_hz + freq_offset

        # Timing offset (appears as different emitter)
        time_offset = np.random.uniform(0.001, 0.01)  # 1-10 ms

        decoy = {
            'position': decoy_position,
            'frequency': decoy_frequency,
            'time_offset': time_offset,
            'power_offset_db': np.random.uniform(-5, 5),
            'is_decoy': True
        }

        return decoy


class FormationAdaptiveTactics:
    """
    Adaptive formation tactics to reduce network detectability
    """

    def __init__(self):
        self.emission_control_level = 0  # 0=normal, 1=reduced, 2=minimal, 3=silent

    def compute_emission_probability(self,
                                    emitter_id: int,
                                    threat_proximity_km: float,
                                    current_time: float) -> float:
        """
        Compute probability of emission based on threat level

        Args:
            emitter_id: Emitter identifier
            threat_proximity_km: Distance to nearest detected threat
            current_time: Current time

        Returns:
            Emission probability (0-1)
        """
        if self.emission_control_level == 3:
            # Silent - no emissions
            return 0.0

        base_probability = 1.0

        # Reduce emissions when threats nearby
        if threat_proximity_km < 10:
            # Very close threat
            base_probability *= 0.1
        elif threat_proximity_km < 50:
            # Moderate threat
            base_probability *= 0.5
        elif threat_proximity_km < 100:
            # Distant threat
            base_probability *= 0.8

        # Emission control level
        if self.emission_control_level == 1:
            base_probability *= 0.7
        elif self.emission_control_level == 2:
            base_probability *= 0.3

        # Random variation
        probability = base_probability * np.random.uniform(0.9, 1.1)

        return np.clip(probability, 0, 1)

    def adapt_formation_geometry(self,
                                emitter_positions: list,
                                threat_direction_deg: float) -> list:
        """
        Adapt formation geometry to reduce mutual detection

        Args:
            emitter_positions: Current emitter positions
            threat_direction_deg: Direction to threat (azimuth)

        Returns:
            Adapted positions
        """
        # Increase spacing when under observation
        # Reduces likelihood of detecting multiple members

        adapted_positions = []

        for _i, pos in enumerate(emitter_positions):
            # Spread formation perpendicular to threat
            perpendicular_angle = threat_direction_deg + 90

            # Add random offset
            offset_distance = np.random.uniform(2000, 5000)  # 2-5 km

            offset = np.array([
                offset_distance * np.cos(np.radians(perpendicular_angle)),
                offset_distance * np.sin(np.radians(perpendicular_angle)),
                np.random.uniform(-1000, 1000)
            ])

            adapted_pos = pos + offset
            adapted_positions.append(adapted_pos)

        return adapted_positions
