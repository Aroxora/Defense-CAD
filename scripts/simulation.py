#!/usr/bin/env python3
"""
MADL Sidelobe-Intercept ESM Simulation (best-case feasibility study)

End-to-end simulation of the ESM problem of detecting and geolocating an F-35
MADL network using multiple synchronized passive platforms. Demonstrates the
signal-processing chain that a counter-stealth ESM network would require:

1. Faint signal detection (sidelobe intercept)
2. Multi-platform geolocation (TDOA/FDOA)
3. Network topology inference
4. Formation tracking over time

IMPORTANT -- REALISM CAVEAT:
MADL is a Ku-band, electronically-steered, narrow-beam (~few degrees) LPI/LPD
datalink with frequency hopping and low power spectral density. The detection
ranges and track accuracies produced here are BEST CASE: they assume favorable
beam geometry, an actively transmitting link, and tight time/frequency
synchronization across the ESM platforms. In practice intercept is
opportunistic and intermittent (the observer must catch a sidelobe during a
burst), bearing-only from a single platform, and TDOA/FDOA coherence degrades
against a hopping waveform. Treat the outputs as an upper bound on what a
well-resourced ESM network might achieve, not as a guaranteed capability.
This is electronic support (ES), NOT electronic attack: nothing here jams or
"disrupts" MADL -- a directional hopping LPI link is not reliably jammable
from standoff.
"""

import numpy as np
import matplotlib.pyplot as plt
from osint_cad.sensors.signal_processing import FaintSignalDetector, AngleOfArrivalEstimator, SidelobeDetector
from osint_cad.sensors.geolocation_network import (GeolocationEngine, NetworkInferenceEngine,
                                MultiTargetTracker, PlatformState, Measurement)
from osint_cad.sensors.visualization import TacticalDisplay, DetectionPerformanceAnalyzer


class MADLEmitter:
    """
    Simulates an F-35 MADL datalink emitter

    Models:
    - Directional antenna pattern
    - Burst transmissions
    - Frequency hopping
    - Power management
    """

    def __init__(self, emitter_id: int, position: np.ndarray,
                 velocity: np.ndarray, tx_power_dbm: float = 30):
        """
        Args:
            emitter_id: Unique emitter ID
            position: Initial position [x, y, z] (meters)
            velocity: Velocity vector [vx, vy, vz] (m/s)
            tx_power_dbm: Transmit power (dBm)
        """
        self.emitter_id = emitter_id
        self.position = position.astype(float)
        self.velocity = velocity.astype(float)
        self.tx_power_dbm = tx_power_dbm

        # MADL parameters
        self.frequency = 15e9  # 15 GHz (Ku-band)
        self.bandwidth = 100e6  # 100 MHz
        self.antenna_gain_db = 20  # 20 dBi (highly directional)
        self.beamwidth_deg = 3.0  # 3° beamwidth
        self.mainbeam_azimuth = 0  # Current pointing direction
        self.sidelobe_level_db = -30  # Sidelobe suppression

        # Transmission parameters
        self.burst_duration = 100e-6  # 100 μs bursts
        self.transmission_interval = 0.5  # Transmit every 500 ms
        self.last_transmission = -1.0

    def update(self, dt: float):
        """Update emitter position"""
        self.position += self.velocity * dt

    def point_antenna(self, target_position: np.ndarray):
        """
        Point antenna main beam toward target

        Args:
            target_position: Position to point toward [x, y, z]
        """
        # Calculate azimuth to target
        delta = target_position - self.position
        self.mainbeam_azimuth = np.degrees(np.arctan2(delta[1], delta[0]))

    def get_antenna_gain(self, observer_position: np.ndarray) -> float:
        """
        Calculate antenna gain toward observer

        Args:
            observer_position: Observer position [x, y, z]

        Returns:
            Antenna gain (dB)
        """
        # Calculate angle from mainbeam to observer
        delta = observer_position - self.position
        azimuth_to_observer = np.degrees(np.arctan2(delta[1], delta[0]))

        angle_off_boresight = abs(azimuth_to_observer - self.mainbeam_azimuth)
        if angle_off_boresight > 180:
            angle_off_boresight = 360 - angle_off_boresight

        # Antenna pattern model (simplified)
        if angle_off_boresight < self.beamwidth_deg / 2:
            # Main beam
            return self.antenna_gain_db
        elif angle_off_boresight < 10:
            # First sidelobe
            return self.antenna_gain_db + self.sidelobe_level_db
        else:
            # Far sidelobes
            return self.antenna_gain_db + self.sidelobe_level_db - 10

    def should_transmit(self, current_time: float) -> bool:
        """Check if emitter should transmit at current time"""
        if current_time - self.last_transmission >= self.transmission_interval:
            self.last_transmission = current_time
            return True
        return False

    def get_received_power(self, observer_position: np.ndarray,
                          frequency: float = None) -> float:
        """
        Calculate received power at observer location

        Args:
            observer_position: Observer position [x, y, z]
            frequency: Observation frequency (Hz), uses emitter freq if None

        Returns:
            Received power (dBm)
        """
        if frequency is None:
            frequency = self.frequency

        # Calculate range
        distance = np.linalg.norm(observer_position - self.position)

        # Free space path loss (Friis equation)
        wavelength = 3e8 / frequency
        path_loss_db = 20 * np.log10(4 * np.pi * distance / wavelength)

        # Antenna gain toward observer
        antenna_gain = self.get_antenna_gain(observer_position)

        # Received power = Tx power + Tx antenna gain - path loss + Rx antenna gain
        # (Assume 0 dBi receive antenna)
        rx_power = self.tx_power_dbm + antenna_gain - path_loss_db

        return rx_power


def run_simulation(duration: float = 60.0, dt: float = 0.1, visualize: bool = True):
    """
    Run complete MADL detection simulation

    Args:
        duration: Simulation duration (seconds)
        dt: Time step (seconds)
        visualize: Whether to show visualization
    """
    print("=" * 80)
    print("MADL Sidelobe-Intercept ESM Simulation (electronic support, best case)")
    print("Detection/geolocation is opportunistic & geometry-dependent -- see docstring")
    print("=" * 80)

    # --- Setup ---

    # Create F-35 formation (4-ship)
    print("\n[1] Creating F-35 MADL network (4-ship formation)...")
    f35_formation = [
        MADLEmitter(1, np.array([50000, 0, 35000]), np.array([250, 0, 0])),      # Lead
        MADLEmitter(2, np.array([48000, -3000, 35000]), np.array([250, 0, 0])),  # Wingman 1
        MADLEmitter(3, np.array([48000, 3000, 35000]), np.array([250, 0, 0])),   # Wingman 2
        MADLEmitter(4, np.array([46000, 0, 35000]), np.array([250, 0, 0])),      # Element 2 Lead
    ]

    # Point antennas toward each other (network communication)
    f35_formation[0].point_antenna(f35_formation[1].position)  # Lead → Wingman 1
    f35_formation[1].point_antenna(f35_formation[0].position)  # Wingman 1 → Lead
    f35_formation[2].point_antenna(f35_formation[0].position)  # Wingman 2 → Lead
    f35_formation[3].point_antenna(f35_formation[0].position)  # Element 2 → Lead

    print(f"  Created {len(f35_formation)} emitters")
    for emitter in f35_formation:
        print(f"    F-35 #{emitter.emitter_id}: Pos={emitter.position/1000} km, "
              f"Mainbeam={emitter.mainbeam_azimuth:.1f}°")

    # Create ESM platforms (friendly)
    print("\n[2] Deploying ESM platforms...")
    esm_platforms = [
        PlatformState("J-20-1", np.array([0, 0, 12000], dtype=float), np.array([200, 50, 0], dtype=float), 0),
        PlatformState("J-20-2", np.array([100000, 0, 12000], dtype=float), np.array([200, -50, 0], dtype=float), 0),
        PlatformState("J-16D", np.array([50000, 86600, 10000], dtype=float), np.array([200, 0, 0], dtype=float), 0),
        PlatformState("Ground-ESM", np.array([50000, -86600, 0], dtype=float), np.array([0, 0, 0], dtype=float), 0),
    ]

    print(f"  Deployed {len(esm_platforms)} ESM platforms")
    for platform in esm_platforms:
        print(f"    {platform.platform_id}: Pos={platform.position/1000} km")

    # Create processing engines
    geo_engine = GeolocationEngine()
    for platform in esm_platforms:
        geo_engine.update_platform_state(platform)

    network_engine = NetworkInferenceEngine(max_link_time_delta=0.2)
    tracker = MultiTargetTracker()

    # Detection parameters
    noise_floor_dbm = -110
    detection_threshold_db = 10  # 10 dB above noise floor

    # --- Simulation Loop ---

    print(f"\n[3] Running simulation ({duration}s, dt={dt}s)...")

    time_steps = int(duration / dt)
    detection_count = 0
    geolocation_count = 0

    all_detections = []  # Store all detections for analysis

    for step in range(time_steps):
        current_time = step * dt

        # Update emitter positions
        for emitter in f35_formation:
            emitter.update(dt)

        # Update platform positions
        for platform in esm_platforms:
            platform.position += platform.velocity * dt
            platform.timestamp = current_time
            geo_engine.update_platform_state(platform)

        # Detection phase - each platform tries to detect emissions
        detections_this_step = []

        for emitter in f35_formation:
            if emitter.should_transmit(current_time):
                # Emitter is transmitting

                # Check each platform for detection
                toa_measurements = []
                freq_measurements = []
                aoa_measurements = []

                for platform in esm_platforms:
                    # Calculate received power
                    rx_power = emitter.get_received_power(platform.position)

                    # Add noise
                    noise_power = noise_floor_dbm
                    snr = rx_power - noise_power

                    # Detection?
                    if snr > detection_threshold_db:
                        detection_count += 1

                        # Time of arrival (with noise)
                        distance = np.linalg.norm(platform.position - emitter.position)
                        toa = current_time + distance / 299792458.0
                        toa += np.random.randn() * 10e-9  # 10 ns timing jitter

                        toa_meas = Measurement(
                            platform_id=platform.platform_id,
                            timestamp=current_time,
                            measurement_type='TOA',
                            value=toa,
                            uncertainty=10e-9
                        )
                        toa_measurements.append(toa_meas)

                        # Frequency (with Doppler)
                        relative_velocity = np.dot(emitter.velocity - platform.velocity,
                                                   (emitter.position - platform.position)) / distance
                        doppler_shift = emitter.frequency * relative_velocity / 299792458.0
                        measured_freq = emitter.frequency + doppler_shift
                        measured_freq += np.random.randn() * 1e3  # 1 kHz noise

                        freq_meas = Measurement(
                            platform_id=platform.platform_id,
                            timestamp=current_time,
                            measurement_type='FREQ',
                            value=measured_freq,
                            uncertainty=1e3
                        )
                        freq_measurements.append(freq_meas)

                        # Angle of arrival (simplified)
                        delta = emitter.position - platform.position
                        azimuth = np.degrees(np.arctan2(delta[1], delta[0]))
                        azimuth += np.random.randn() * 2.0  # 2° noise

                        aoa_meas = Measurement(
                            platform_id=platform.platform_id,
                            timestamp=current_time,
                            measurement_type='AOA',
                            value=0,
                            uncertainty=2.0,
                            azimuth=azimuth,
                            elevation=0
                        )
                        aoa_measurements.append(aoa_meas)

                # If enough measurements, geolocate
                if len(toa_measurements) >= 4:
                    try:
                        # TDOA geolocation
                        estimated_pos, covariance = geo_engine.tdoa_geolocation(toa_measurements)

                        # Verify geolocation result is valid before using
                        if estimated_pos is None or not np.isfinite(estimated_pos).all():
                            continue  # Skip invalid result
                        if covariance is None or not np.isfinite(covariance).all():
                            continue  # Skip invalid covariance

                        # Update tracker
                        track_id = tracker.update(estimated_pos, covariance, current_time)

                        geolocation_count += 1

                        # Record for network inference
                        # Estimate mainbeam direction from detections
                        # (simplified - just use first detection bearing)
                        bearing = aoa_measurements[0].azimuth if aoa_measurements else None
                        network_engine.add_emission_event(track_id, current_time,
                                                         estimated_pos, bearing)

                        detections_this_step.append({
                            'time': current_time,
                            'track_id': track_id,
                            'true_id': emitter.emitter_id,
                            'position': estimated_pos,
                            'true_position': emitter.position.copy(),
                            'error': np.linalg.norm(estimated_pos - emitter.position)
                        })

                    except (ValueError, np.linalg.LinAlgError):
                        pass  # Expected failures for degenerate geometry

        all_detections.extend(detections_this_step)

        # Progress indicator
        if (step + 1) % (time_steps // 10) == 0:
            print(f"  Progress: {100 * (step + 1) / time_steps:.0f}% "
                  f"(Detections: {detection_count}, Geolocations: {geolocation_count})")

    # --- Analysis ---

    print(f"\n[4] Simulation complete.")
    print(f"  Total detections: {detection_count}")
    print(f"  Total geolocations: {geolocation_count}")
    print(f"  Average detection rate: {detection_count / duration:.1f} /sec")

    # Geolocation accuracy
    if all_detections:
        errors = [d['error'] for d in all_detections]
        print(f"\n[5] Geolocation Performance:")
        print(f"  Mean error: {np.mean(errors):.1f} m")
        print(f"  Median error: {np.median(errors):.1f} m")
        print(f"  95th percentile: {np.percentile(errors, 95):.1f} m")

    # Network inference
    print(f"\n[6] Network Inference:")
    links = network_engine.infer_links()
    print(f"  Detected {len(links)} communication links")

    for link in links:
        print(f"    Track {link.emitter_a} ↔ Track {link.emitter_b}: "
              f"Confidence={link.strength:.2f}, Observations={link.observations}")

    formation_type = network_engine.identify_formation_type()
    print(f"  Inferred formation type: {formation_type}")

    # --- Visualization ---

    if visualize:
        print(f"\n[7] Generating visualizations...")

        # Final tactical display
        display = TacticalDisplay(figsize=(16, 10))

        # Plot ESM platforms (final positions)
        for platform in esm_platforms:
            display.plot_platform(platform, color='#00ff00')
            display.plot_detection_range(platform, 100)  # 100 km range

        # Plot tracked emitters (final positions)
        for track_id, track in tracker.tracks.items():
            display.plot_emitter(track, color='#ff0000', show_uncertainty=True)

            # Find corresponding true emitter
            for emitter in f35_formation:
                if np.linalg.norm(track.position - emitter.position) < 5000:
                    display.plot_antenna_beam(track, emitter.mainbeam_azimuth,
                                            beamwidth=emitter.beamwidth_deg)

        # Plot inferred network links
        for link in links:
            if link.emitter_a in tracker.tracks and link.emitter_b in tracker.tracks:
                display.plot_link(tracker.tracks[link.emitter_a],
                                tracker.tracks[link.emitter_b],
                                link, color='#00ffff')

        display.finalize('MADL Network Detection - Final State')

        # Error distribution plot
        if all_detections:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.patch.set_facecolor('#1a1a1a')

            # Error over time
            times = [d['time'] for d in all_detections]
            errors = [d['error'] for d in all_detections]

            axes[0, 0].set_facecolor('#0a0a0a')
            axes[0, 0].plot(times, np.array(errors) / 1000, 'o', color='#00ff00', alpha=0.6)
            axes[0, 0].set_xlabel('Time (s)', color='white')
            axes[0, 0].set_ylabel('Geolocation Error (km)', color='white')
            axes[0, 0].set_title('Geolocation Error vs Time', color='white', fontweight='bold')
            axes[0, 0].grid(True, alpha=0.3, color='#00ff00', linestyle=':')
            axes[0, 0].tick_params(colors='white')

            # Error histogram
            axes[0, 1].set_facecolor('#0a0a0a')
            axes[0, 1].hist(np.array(errors) / 1000, bins=30, color='#00ff00', alpha=0.7)
            axes[0, 1].set_xlabel('Geolocation Error (km)', color='white')
            axes[0, 1].set_ylabel('Count', color='white')
            axes[0, 1].set_title('Error Distribution', color='white', fontweight='bold')
            axes[0, 1].grid(True, alpha=0.3, color='#00ff00', linestyle=':')
            axes[0, 1].tick_params(colors='white')

            # Track positions
            axes[1, 0].set_facecolor('#0a0a0a')
            for track_id, track in tracker.tracks.items():
                axes[1, 0].plot(track.position[0] / 1000, track.position[1] / 1000,
                              'o', markersize=10, label=f'Track {track_id}')

            for emitter in f35_formation:
                axes[1, 0].plot(emitter.position[0] / 1000, emitter.position[1] / 1000,
                              'x', markersize=12, color='red', markeredgewidth=2)

            axes[1, 0].set_xlabel('East (km)', color='white')
            axes[1, 0].set_ylabel('North (km)', color='white')
            axes[1, 0].set_title('Track vs True Positions', color='white', fontweight='bold')
            axes[1, 0].grid(True, alpha=0.3, color='#00ff00', linestyle=':')
            axes[1, 0].legend(facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
            axes[1, 0].tick_params(colors='white')
            axes[1, 0].set_aspect('equal')

            # Detection timeline
            axes[1, 1].set_facecolor('#0a0a0a')
            for track_id in set(d['track_id'] for d in all_detections):
                track_times = [d['time'] for d in all_detections if d['track_id'] == track_id]
                axes[1, 1].plot(track_times, [track_id] * len(track_times),
                              '|', markersize=10, markeredgewidth=2, label=f'Track {track_id}')

            axes[1, 1].set_xlabel('Time (s)', color='white')
            axes[1, 1].set_ylabel('Track ID', color='white')
            axes[1, 1].set_title('Detection Timeline', color='white', fontweight='bold')
            axes[1, 1].grid(True, alpha=0.3, color='#00ff00', linestyle=':')
            axes[1, 1].tick_params(colors='white')

            plt.tight_layout()

        print("  Visualization complete. Close plots to exit.")
        plt.show()

    print("\n" + "=" * 80)
    print("Simulation complete.")
    print("=" * 80)

    return {
        'detections': all_detections,
        'links': links,
        'tracks': tracker.tracks,
        'formation_type': formation_type
    }


if __name__ == "__main__":
    # Run simulation
    results = run_simulation(duration=30.0, dt=0.1, visualize=True)
