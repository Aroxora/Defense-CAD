#!/usr/bin/env python3
"""
Geolocation and Network Inference Engine

This module implements algorithms for:
1. Geolocating emitters using TDOA, FDOA, and DF
2. Inferring network topology from detected emissions
3. Tracking multiple emitters over time
4. Reconstructing communication patterns

Designed for multi-platform Electronic Support (ES) operations
targeting LPI/LPD datalink networks like MADL.
"""

import numpy as np
from scipy.optimize import minimize, least_squares
from scipy.spatial.distance import cdist
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import networkx as nx


@dataclass
class PlatformState:
    """State of an ESM platform"""
    platform_id: str
    position: np.ndarray  # [x, y, z] in ECEF or local coords (meters)
    velocity: np.ndarray  # [vx, vy, vz] (m/s)
    timestamp: float  # GPS time (seconds)


@dataclass
class Measurement:
    """Single sensor measurement"""
    platform_id: str
    timestamp: float  # GPS time (seconds)
    measurement_type: str  # 'TOA', 'AOA', 'FREQ', 'POWER'
    value: float  # Time (s), Angle (deg), Frequency (Hz), or Power (dBm)
    uncertainty: float  # Measurement standard deviation
    azimuth: Optional[float] = None  # For AOA measurements
    elevation: Optional[float] = None


@dataclass
class EmitterTrack:
    """Track of a single emitter"""
    track_id: int
    position: np.ndarray  # Estimated position [x, y, z]
    velocity: np.ndarray  # Estimated velocity [vx, vy, vz]
    position_covariance: np.ndarray  # 3x3 covariance matrix
    last_update: float  # Timestamp of last update
    measurements: List[Measurement] = field(default_factory=list)
    confidence: float = 0.5  # Track quality (0-1)


@dataclass
class NetworkLink:
    """Detected communication link between emitters"""
    emitter_a: int  # Track ID
    emitter_b: int  # Track ID
    strength: float  # Link confidence (0-1)
    last_observed: float  # Timestamp
    observations: int = 0  # Number of times link observed
    bidirectional: bool = False


class GeolocationEngine:
    """
    Multi-sensor geolocation using TDOA, FDOA, and DF

    Implements various geolocation algorithms and fusion methods.
    """

    SPEED_OF_LIGHT = 299792458.0  # m/s

    def __init__(self):
        self.platform_states: Dict[str, PlatformState] = {}
        self.last_gdop: Optional[float] = None
        self.last_crlb: Optional[np.ndarray] = None

    def update_platform_state(self, state: PlatformState):
        """Update platform position and velocity"""
        self.platform_states[state.platform_id] = state

    def tdoa_geolocation(self, measurements: List[Measurement],
                        initial_guess: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Time Difference of Arrival (TDOA) geolocation

        Uses time differences between detection at multiple platforms
        to estimate emitter position.

        Args:
            measurements: List of TOA measurements from different platforms
            initial_guess: Initial position estimate [x, y, z]

        Returns:
            Tuple of (position, covariance_matrix)
        """
        if len(measurements) < 4:
            raise ValueError("Need at least 4 TOA measurements for 3D TDOA")

        # Reference measurement (first platform)
        ref_measurement = measurements[0]
        ref_platform = self.platform_states[ref_measurement.platform_id]

        # Time differences relative to reference
        tdoa_values = []
        platform_positions = [ref_platform.position]

        for meas in measurements[1:]:
            tdoa = meas.value - ref_measurement.value
            tdoa_values.append(tdoa)
            platform = self.platform_states[meas.platform_id]
            platform_positions.append(platform.position)

        tdoa_values = np.array(tdoa_values)
        platform_positions = np.array(platform_positions)

        # Initial guess (if not provided, use center of platforms)
        if initial_guess is None:
            initial_guess = np.mean(platform_positions, axis=0)

        # Solve non-linear least squares
        def residuals(emitter_pos):
            # Calculate expected TDOA for this emitter position
            ranges = np.linalg.norm(platform_positions - emitter_pos, axis=1)
            expected_tdoa = (ranges[1:] - ranges[0]) / self.SPEED_OF_LIGHT
            return tdoa_values - expected_tdoa

        # Optimize
        result = least_squares(residuals, initial_guess,
                              method='trf',  # Trust Region Reflective
                              ftol=1e-8,
                              xtol=1e-8)

        emitter_position = result.x

        # Estimate covariance from Jacobian
        try:
            # Covariance ≈ inverse(J^T J) * residual_variance
            jacobian = result.jac
            residual_var = np.var(result.fun)
            covariance = np.linalg.inv(jacobian.T @ jacobian) * residual_var
        except np.linalg.LinAlgError:
            # If singular, use large uncertainty
            covariance = np.eye(3) * 1e6

        return emitter_position, covariance

    def fdoa_geolocation(self, measurements: List[Measurement]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Frequency Difference of Arrival (FDOA) geolocation

        Uses Doppler shift differences between moving platforms.
        Often combined with TDOA for improved accuracy.

        Args:
            measurements: List of frequency measurements from different platforms

        Returns:
            Tuple of (position, covariance_matrix)
        """
        if len(measurements) < 4:
            raise ValueError("Need at least 4 frequency measurements for FDOA")

        # Reference measurement
        ref_measurement = measurements[0]
        ref_platform = self.platform_states[ref_measurement.platform_id]
        ref_freq = ref_measurement.value

        fdoa_values = []
        platform_positions = [ref_platform.position]
        platform_velocities = [ref_platform.velocity]

        for meas in measurements[1:]:
            fdoa = meas.value - ref_freq
            fdoa_values.append(fdoa)
            platform = self.platform_states[meas.platform_id]
            platform_positions.append(platform.position)
            platform_velocities.append(platform.velocity)

        fdoa_values = np.array(fdoa_values)
        platform_positions = np.array(platform_positions)
        platform_velocities = np.array(platform_velocities)

        # Initial guess
        initial_guess = np.mean(platform_positions, axis=0)

        def residuals(emitter_pos):
            """Calculate FDOA residuals"""
            residuals = []

            for i in range(len(fdoa_values)):
                # Vector from emitter to platforms
                r0 = ref_platform.position - emitter_pos
                ri = platform_positions[i + 1] - emitter_pos

                # Range rates (component of velocity toward emitter)
                r0_norm = np.linalg.norm(r0)
                ri_norm = np.linalg.norm(ri)

                range_rate_0 = np.dot(ref_platform.velocity, r0) / r0_norm
                range_rate_i = np.dot(platform_velocities[i + 1], ri) / ri_norm

                # Expected FDOA (Doppler difference)
                # f_d = f_0 * (v/c), so FDOA = f_0 * (v_i - v_0) / c
                expected_fdoa = (ref_freq / self.SPEED_OF_LIGHT) * (range_rate_i - range_rate_0)

                residuals.append(fdoa_values[i] - expected_fdoa)

            return np.array(residuals)

        result = least_squares(residuals, initial_guess, method='trf')
        emitter_position = result.x

        # Covariance estimation
        try:
            jacobian = result.jac
            residual_var = np.var(result.fun)
            covariance = np.linalg.inv(jacobian.T @ jacobian) * residual_var
        except np.linalg.LinAlgError:
            covariance = np.eye(3) * 1e6

        return emitter_position, covariance

    def df_triangulation(self, measurements: List[Measurement]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Direction Finding (DF) triangulation

        Uses bearing measurements from multiple platforms to triangulate
        emitter position.

        Args:
            measurements: List of AOA measurements with azimuth/elevation

        Returns:
            Tuple of (position, covariance_matrix)
        """
        if len(measurements) < 2:
            raise ValueError("Need at least 2 AOA measurements for DF")

        platform_positions = []
        bearing_vectors = []

        for meas in measurements:
            platform = self.platform_states[meas.platform_id]
            platform_positions.append(platform.position)

            # Convert azimuth/elevation to unit vector
            az_rad = np.radians(meas.azimuth)
            el_rad = np.radians(meas.elevation) if meas.elevation else 0

            bearing = np.array([
                np.cos(el_rad) * np.cos(az_rad),
                np.cos(el_rad) * np.sin(az_rad),
                np.sin(el_rad)
            ])
            bearing_vectors.append(bearing)

        platform_positions = np.array(platform_positions)
        bearing_vectors = np.array(bearing_vectors)

        # Solve for intersection of bearing lines (least squares)
        def residuals(emitter_pos):
            """Distance from emitter to each bearing line"""
            residuals = []

            for i in range(len(platform_positions)):
                # Vector from platform to emitter
                to_emitter = emitter_pos - platform_positions[i]

                # Cross product gives perpendicular distance to line
                cross = np.cross(to_emitter, bearing_vectors[i])
                distance = np.linalg.norm(cross)

                residuals.append(distance)

            return np.array(residuals)

        # Initial guess
        initial_guess = np.mean(platform_positions, axis=0)

        result = least_squares(residuals, initial_guess, method='lm')
        emitter_position = result.x

        # Covariance estimation (simplified)
        # In practice, would use measurement uncertainties
        covariance = np.eye(3) * 1000  # 1 km uncertainty (rough estimate)

        return emitter_position, covariance

    def hybrid_geolocation(self, tdoa_measurements: List[Measurement],
                          fdoa_measurements: List[Measurement],
                          df_measurements: List[Measurement]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Hybrid geolocation combining TDOA, FDOA, and DF

        Fuses multiple measurement types for optimal accuracy.

        Args:
            tdoa_measurements: TOA measurements
            fdoa_measurements: Frequency measurements
            df_measurements: AOA measurements

        Returns:
            Tuple of (position, covariance_matrix)
        """
        positions = []
        covariances = []
        weights = []

        # TDOA solution
        if len(tdoa_measurements) >= 4:
            try:
                pos, cov = self.tdoa_geolocation(tdoa_measurements)
                # Verify result is valid before adding
                if pos is not None and np.isfinite(pos).all() and np.isfinite(cov).all():
                    positions.append(pos)
                    covariances.append(cov)
                    weights.append(1.0)  # High weight for TDOA
            except (ValueError, np.linalg.LinAlgError):
                pass  # Expected failures for insufficient/degenerate geometry

        # FDOA solution
        if len(fdoa_measurements) >= 4:
            try:
                pos, cov = self.fdoa_geolocation(fdoa_measurements)
                # Verify result is valid before adding
                if pos is not None and np.isfinite(pos).all() and np.isfinite(cov).all():
                    positions.append(pos)
                    covariances.append(cov)
                    weights.append(0.7)  # Lower weight for FDOA
            except (ValueError, np.linalg.LinAlgError):
                pass  # Expected failures for insufficient/degenerate geometry

        # DF solution
        if len(df_measurements) >= 2:
            try:
                pos, cov = self.df_triangulation(df_measurements)
                # Verify result is valid before adding
                if pos is not None and np.isfinite(pos).all() and np.isfinite(cov).all():
                    positions.append(pos)
                    covariances.append(cov)
                    weights.append(0.5)  # Lowest weight for DF
            except (ValueError, np.linalg.LinAlgError):
                pass  # Expected failures for insufficient/degenerate geometry

        if not positions:
            raise ValueError("Unable to compute geolocation with available measurements")

        # Weighted fusion (inverse covariance weighting)
        fused_position = np.zeros(3)
        fused_covariance = np.zeros((3, 3))
        total_weight = 0

        for pos, cov, weight in zip(positions, covariances, weights):
            # Weight by inverse covariance (information matrix)
            try:
                info_matrix = np.linalg.inv(cov) * weight
                # Verify the inverse is valid
                if np.isfinite(info_matrix).all():
                    fused_position += info_matrix @ pos
                    total_weight += np.trace(info_matrix)
                else:
                    raise np.linalg.LinAlgError("Non-finite inverse")
            except np.linalg.LinAlgError:
                # If covariance singular or ill-conditioned, use simple weighted average
                fused_position += pos * weight
                total_weight += weight

        fused_position /= total_weight

        # Fused covariance (simplified)
        fused_covariance = np.mean([cov * w for cov, w in zip(covariances, weights)], axis=0)

        return fused_position, fused_covariance

    def calculate_gdop(self, platform_positions: np.ndarray,
                      emitter_position: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Calculate Geometric Dilution of Precision (GDOP)

        GDOP quantifies how sensor geometry affects position accuracy.
        Lower GDOP = better geometry, higher accuracy.

        Args:
            platform_positions: Nx3 array of platform positions
            emitter_position: 3D emitter position [x, y, z]

        Returns:
            Tuple of (gdop_value, geometry_matrix)

        GDOP interpretation:
            < 2: Excellent geometry
            2-5: Good geometry
            5-10: Moderate geometry
            10-20: Poor geometry
            > 20: Very poor geometry (unreliable)
        """
        n_platforms = len(platform_positions)

        if n_platforms < 4:
            # Insufficient platforms for 3D GDOP
            return float('inf'), np.zeros((3, 3))

        # Geometry matrix (Jacobian of range equations)
        G = np.zeros((n_platforms, 3))

        for i in range(n_platforms):
            # Vector from emitter to platform
            delta = platform_positions[i] - emitter_position
            range_i = np.linalg.norm(delta)

            if range_i < 1.0:  # Avoid division by zero
                range_i = 1.0

            # Unit vector
            G[i, :] = delta / range_i

        try:
            # Covariance of position estimate (assuming unit measurement variance)
            # Cov(x) = (G^T G)^(-1)
            GTG = G.T @ G
            GTG_inv = np.linalg.inv(GTG)

            # GDOP = sqrt(trace(covariance_matrix))
            gdop = np.sqrt(np.trace(GTG_inv))

            self.last_gdop = gdop

            return gdop, GTG_inv

        except np.linalg.LinAlgError:
            # Singular matrix - degenerate geometry
            return float('inf'), np.zeros((3, 3))

    def calculate_crlb_tdoa(self, platform_positions: np.ndarray,
                           emitter_position: np.ndarray,
                           timing_uncertainty_ns: float = 10.0) -> np.ndarray:
        """
        Calculate Cramer-Rao Lower Bound (CRLB) for TDOA geolocation

        CRLB provides theoretical best-case position accuracy given
        measurement noise and geometry.

        Args:
            platform_positions: Nx3 array of platform positions
            emitter_position: 3D emitter position
            timing_uncertainty_ns: Timing measurement uncertainty (nanoseconds RMS)

        Returns:
            3x3 CRLB covariance matrix (meters^2)
        """
        n_platforms = len(platform_positions)

        # Convert timing uncertainty to range uncertainty
        sigma_range = (timing_uncertainty_ns * 1e-9) * self.SPEED_OF_LIGHT  # meters

        # Geometry matrix
        G = np.zeros((n_platforms - 1, 3))  # TDOA uses differential measurements

        ranges = np.linalg.norm(platform_positions - emitter_position, axis=1)
        ref_range = ranges[0]

        if ref_range < 1.0:
            ref_range = 1.0

        for i in range(1, n_platforms):
            # Unit vector from emitter to platform i
            if ranges[i] < 1.0:
                ranges[i] = 1.0

            u_i = (platform_positions[i] - emitter_position) / ranges[i]

            # Unit vector from emitter to reference platform
            u_0 = (platform_positions[0] - emitter_position) / ref_range

            # TDOA gradient
            G[i - 1, :] = u_i - u_0

        # Fisher Information Matrix
        # For TDOA with independent, equal-variance measurements
        FIM = (1.0 / sigma_range ** 2) * (G.T @ G)

        try:
            # CRLB = inverse of Fisher Information Matrix
            crlb = np.linalg.inv(FIM)
            self.last_crlb = crlb

            return crlb

        except np.linalg.LinAlgError:
            # Singular FIM - return large uncertainty
            return np.eye(3) * 1e12

    def get_position_uncertainty_cep(self, covariance: np.ndarray) -> float:
        """
        Calculate Circular Error Probable (CEP) from covariance matrix

        CEP is the radius of circle containing 50% of position estimates.
        For 2D Gaussian: CEP ≈ 0.59 * (σ_x + σ_y)

        Args:
            covariance: 3x3 position covariance matrix

        Returns:
            CEP in meters (2D horizontal)
        """
        # Extract horizontal (x, y) components
        sigma_x = np.sqrt(covariance[0, 0])
        sigma_y = np.sqrt(covariance[1, 1])

        # CEP formula for 2D
        cep = 0.59 * (sigma_x + sigma_y)

        return cep

    def assess_geometry_quality(self, platform_positions: np.ndarray,
                                emitter_position: np.ndarray) -> Dict[str, any]:
        """
        Comprehensive geometry quality assessment

        Args:
            platform_positions: Nx3 array of platform positions
            emitter_position: 3D emitter position

        Returns:
            Dictionary with quality metrics and recommendations
        """
        # Calculate GDOP
        gdop, geom_matrix = self.calculate_gdop(platform_positions, emitter_position)

        # Calculate CRLB (assuming 10ns timing uncertainty)
        crlb = self.calculate_crlb_tdoa(platform_positions, emitter_position, 10.0)
        cep_theoretical = self.get_position_uncertainty_cep(crlb)

        # Assess quality
        if gdop < 2.0:
            quality = "EXCELLENT"
            recommendation = "Geometry optimal for precision geolocation"
        elif gdop < 5.0:
            quality = "GOOD"
            recommendation = "Geometry acceptable for precision operations"
        elif gdop < 10.0:
            quality = "MODERATE"
            recommendation = "Geometry marginal - consider repositioning platforms"
        elif gdop < 20.0:
            quality = "POOR"
            recommendation = "Geometry poor - reposition platforms before engagement"
        else:
            quality = "VERY POOR"
            recommendation = "CRITICAL: Geometry unreliable - DO NOT ENGAGE without repositioning"

        # Calculate platform spread (spatial diversity)
        platform_centroid = np.mean(platform_positions, axis=0)
        platform_spread = np.mean(np.linalg.norm(platform_positions - platform_centroid, axis=1))

        # Calculate aspect angle diversity
        angles_to_emitter = []
        for platform_pos in platform_positions:
            vec = platform_pos - emitter_position
            # Azimuth angle
            azimuth = np.degrees(np.arctan2(vec[1], vec[0]))
            angles_to_emitter.append(azimuth)

        angle_diversity = np.std(angles_to_emitter)  # Higher = better diversity

        return {
            'gdop': gdop,
            'quality': quality,
            'recommendation': recommendation,
            'cep_theoretical_meters': cep_theoretical,
            'platform_spread_km': platform_spread / 1000.0,
            'angle_diversity_deg': angle_diversity,
            'geometry_matrix': geom_matrix,
            'crlb_matrix': crlb
        }


class NetworkInferenceEngine:
    """
    Infer communication network topology from emission patterns

    Analyzes timing, direction, and frequency of emissions to determine:
    - Which emitters are communicating with each other
    - Network topology (formation structure)
    - Communication patterns
    """

    def __init__(self, max_link_time_delta: float = 0.1):
        """
        Args:
            max_link_time_delta: Maximum time between correlated transmissions (seconds)
        """
        self.tracks: Dict[int, EmitterTrack] = {}
        self.links: List[NetworkLink] = []
        self.max_link_time_delta = max_link_time_delta
        self.emission_history: List[Tuple[int, float, np.ndarray]] = []  # (track_id, time, position)

    def add_emission_event(self, track_id: int, timestamp: float,
                          position: np.ndarray, bearing: Optional[float] = None):
        """
        Record an emission event

        Args:
            track_id: Emitter track ID
            timestamp: Time of emission
            position: Emitter position
            bearing: Antenna pointing direction (degrees), if known
        """
        self.emission_history.append((track_id, timestamp, position, bearing))

    def infer_links(self) -> List[NetworkLink]:
        """
        Infer communication links from emission patterns

        Looks for correlated emissions that suggest bidirectional communication:
        - Emitter A transmits at time T1
        - Emitter B transmits at time T2 ≈ T1 + propagation_delay
        - A's antenna points toward B, B's antenna points toward A

        Returns:
            List of inferred network links
        """
        links = defaultdict(lambda: {'count': 0, 'last_time': 0})

        # Look for paired emissions
        for i, (track_a, time_a, pos_a, bearing_a) in enumerate(self.emission_history):
            for track_b, time_b, pos_b, bearing_b in self.emission_history[i + 1:]:
                if track_a == track_b:
                    continue  # Same emitter

                time_delta = abs(time_b - time_a)

                # Check if timing is consistent with communication
                distance = np.linalg.norm(pos_b - pos_a)
                propagation_delay = distance / 299792458.0  # Speed of light

                # Expected response time: propagation + processing (assume 1-10 ms processing)
                expected_delta = propagation_delay + 0.005  # 5 ms processing nominal

                if abs(time_delta - expected_delta) < self.max_link_time_delta:
                    # Check if bearings point toward each other (if available)
                    bearing_match = True
                    if bearing_a is not None and bearing_b is not None:
                        # Direction from A to B
                        vec_ab = pos_b - pos_a
                        azimuth_ab = np.degrees(np.arctan2(vec_ab[1], vec_ab[0]))

                        # Direction from B to A
                        vec_ba = pos_a - pos_b
                        azimuth_ba = np.degrees(np.arctan2(vec_ba[1], vec_ba[0]))

                        # Check if bearings align (within tolerance)
                        bearing_tolerance = 15  # degrees
                        a_points_to_b = abs(bearing_a - azimuth_ab) < bearing_tolerance
                        b_points_to_a = abs(bearing_b - azimuth_ba) < bearing_tolerance

                        bearing_match = a_points_to_b and b_points_to_a

                    if bearing_match:
                        # Record potential link
                        link_key = tuple(sorted([track_a, track_b]))
                        links[link_key]['count'] += 1
                        links[link_key]['last_time'] = max(time_a, time_b)

        # Convert to NetworkLink objects
        network_links = []
        for (track_a, track_b), info in links.items():
            # Confidence based on number of observations
            confidence = min(1.0, info['count'] / 10.0)  # Saturates at 10 observations

            link = NetworkLink(
                emitter_a=track_a,
                emitter_b=track_b,
                strength=confidence,
                last_observed=info['last_time'],
                observations=info['count'],
                bidirectional=True  # Assuming bidirectional if correlated
            )
            network_links.append(link)

        self.links = network_links
        return network_links

    def build_network_graph(self) -> nx.Graph:
        """
        Build network topology graph

        Returns:
            NetworkX graph representing communication network
        """
        G = nx.Graph()

        # Add nodes (emitters)
        for track_id, track in self.tracks.items():
            G.add_node(track_id, position=track.position, confidence=track.confidence)

        # Add edges (links)
        for link in self.links:
            G.add_edge(link.emitter_a, link.emitter_b,
                      strength=link.strength,
                      observations=link.observations)

        return G

    def identify_formation_type(self) -> str:
        """
        Identify formation type from network topology

        Returns:
            Formation type: 'line', 'wedge', 'wall', 'box', 'unknown'
        """
        G = self.build_network_graph()

        if G.number_of_nodes() < 2:
            return 'single'

        # Analyze connectivity
        avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()

        if nx.is_connected(G):
            if avg_degree > 2.5:
                return 'fully_connected'  # Tight formation
            elif avg_degree > 1.5:
                return 'partial_mesh'  # Spread formation
            else:
                return 'chain'  # Line formation
        else:
            return 'fragmented'  # Multiple separated elements

    def predict_next_transmission(self, track_id: int) -> Tuple[float, float]:
        """
        Predict next transmission time based on observed patterns

        Args:
            track_id: Emitter track ID

        Returns:
            Tuple of (predicted_time, confidence)
        """
        # Extract emission times for this track
        times = [t for tid, t, _, _ in self.emission_history if tid == track_id]

        if len(times) < 3:
            return (0, 0)  # Insufficient data

        times = np.array(sorted(times))
        intervals = np.diff(times)

        # Look for periodicity
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        # Confidence based on regularity
        confidence = max(0, 1.0 - (std_interval / mean_interval))

        # Predict next transmission
        predicted_time = times[-1] + mean_interval

        return predicted_time, confidence


class MultiTargetTracker:
    """
    Track multiple emitters over time using Kalman filtering

    Maintains tracks and associates new measurements with existing tracks.
    """

    def __init__(self):
        self.tracks: Dict[int, EmitterTrack] = {}
        self.next_track_id = 1
        self.association_threshold = 5000  # meters (gate for measurement association)

    def predict(self, dt: float):
        """
        Predict track states forward in time

        Args:
            dt: Time step (seconds)
        """
        for track in self.tracks.values():
            # Simple constant velocity model
            track.position += track.velocity * dt

            # Increase uncertainty
            process_noise = np.eye(3) * (10 * dt) ** 2  # 10 m/s^2 acceleration noise
            track.position_covariance += process_noise

    def update(self, measurement_position: np.ndarray,
              measurement_covariance: np.ndarray,
              timestamp: float) -> int:
        """
        Update tracks with new measurement

        Performs data association and Kalman filter update.

        Args:
            measurement_position: Measured position [x, y, z]
            measurement_covariance: Measurement covariance 3x3
            timestamp: Measurement time

        Returns:
            Track ID (existing or new)
        """
        # Find closest track
        best_track_id = None
        min_distance = float('inf')

        for track_id, track in self.tracks.items():
            distance = np.linalg.norm(track.position - measurement_position)

            # Mahalanobis distance (accounts for uncertainty)
            try:
                innovation = measurement_position - track.position
                S = track.position_covariance + measurement_covariance
                mahal_dist = np.sqrt(innovation.T @ np.linalg.inv(S) @ innovation)

                # Verify the Mahalanobis distance is valid before using
                if np.isfinite(mahal_dist) and mahal_dist < self.association_threshold and mahal_dist < min_distance:
                    min_distance = mahal_dist
                    best_track_id = track_id
            except np.linalg.LinAlgError:
                # If covariance singular, fall back to Euclidean distance
                if distance < self.association_threshold and distance < min_distance:
                    min_distance = distance
                    best_track_id = track_id

        # If no close track found, create new track
        if best_track_id is None or min_distance > self.association_threshold:
            track_id = self.next_track_id
            self.next_track_id += 1

            self.tracks[track_id] = EmitterTrack(
                track_id=track_id,
                position=measurement_position.copy(),
                velocity=np.zeros(3),
                position_covariance=measurement_covariance.copy(),
                last_update=timestamp,
                confidence=0.3  # Low initial confidence
            )
            return track_id

        # Update existing track with Kalman filter
        track = self.tracks[best_track_id]

        # Kalman gain
        S = track.position_covariance + measurement_covariance
        K = track.position_covariance @ np.linalg.inv(S)

        # Update position
        innovation = measurement_position - track.position
        track.position += K @ innovation

        # Update covariance
        track.position_covariance = (np.eye(3) - K) @ track.position_covariance

        # Update velocity estimate (simple differencing)
        dt = timestamp - track.last_update
        if dt > 0:
            track.velocity = innovation / dt

        # Increase confidence
        track.confidence = min(1.0, track.confidence + 0.1)
        track.last_update = timestamp

        return best_track_id


# Example usage
if __name__ == "__main__":
    print("Geolocation and Network Inference Engine")
    print("=" * 60)

    # Create geolocation engine
    geo_engine = GeolocationEngine()

    # Simulate 4 ESM platforms
    platforms = [
        PlatformState("ESM-1", np.array([0, 0, 10000]), np.array([200, 0, 0]), 0),
        PlatformState("ESM-2", np.array([100000, 0, 10000]), np.array([200, 0, 0]), 0),
        PlatformState("ESM-3", np.array([50000, 86600, 10000]), np.array([200, 0, 0]), 0),
        PlatformState("ESM-4", np.array([50000, -86600, 10000]), np.array([200, 0, 0]), 0),
    ]

    for platform in platforms:
        geo_engine.update_platform_state(platform)

    print("\nESM Platform Configuration:")
    for p in platforms:
        print(f"  {p.platform_id}: {p.position/1000} km")

    # Simulate emitter (true position)
    true_emitter_pos = np.array([50000, 0, 35000])  # 50 km east, 35 km altitude
    print(f"\nTrue Emitter Position: {true_emitter_pos/1000} km")

    # Simulate TDOA measurements
    print("\n--- TDOA Geolocation ---")
    tdoa_measurements = []
    for platform in platforms:
        # Calculate true time of arrival
        distance = np.linalg.norm(platform.position - true_emitter_pos)
        toa = distance / GeolocationEngine.SPEED_OF_LIGHT

        # Add measurement noise
        toa_noise = np.random.randn() * 10e-9  # 10 ns noise
        toa_measured = toa + toa_noise

        meas = Measurement(
            platform_id=platform.platform_id,
            timestamp=0,
            measurement_type='TOA',
            value=toa_measured,
            uncertainty=10e-9
        )
        tdoa_measurements.append(meas)

    # Estimate position
    estimated_pos, covariance = geo_engine.tdoa_geolocation(tdoa_measurements)

    print(f"Estimated Position: {estimated_pos/1000} km")
    print(f"Position Error: {np.linalg.norm(estimated_pos - true_emitter_pos):.1f} m")
    print(f"Position Uncertainty (CEP): {np.sqrt(np.trace(covariance[:2, :2])):.1f} m")

    # Network inference
    print("\n--- Network Inference ---")
    network_engine = NetworkInferenceEngine()

    # Simulate multiple emitters in formation
    emitter_positions = [
        np.array([50000, 0, 35000]),      # Lead
        np.array([48000, -2000, 35000]),  # Wingman 1
        np.array([48000, 2000, 35000]),   # Wingman 2
        np.array([46000, 0, 35000]),      # Wingman 3
    ]

    # Simulate emission events (communication pattern)
    for t in np.arange(0, 10, 0.5):  # 10 seconds, emissions every 500 ms
        for i in range(len(emitter_positions)):
            # Emitter transmits to neighbors
            bearing = np.random.uniform(0, 360)  # Simplified
            network_engine.add_emission_event(i, t, emitter_positions[i], bearing)

    # Infer network links
    links = network_engine.infer_links()

    print(f"Detected {len(links)} network links:")
    for link in links[:5]:  # Show first 5
        print(f"  Emitter {link.emitter_a} ↔ Emitter {link.emitter_b}: "
              f"Strength={link.strength:.2f}, Observations={link.observations}")

    print("\n" + "=" * 60)
    print("Geolocation and network inference test complete.")
