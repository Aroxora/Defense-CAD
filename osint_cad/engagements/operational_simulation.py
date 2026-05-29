#!/usr/bin/env python3
"""
Operational-Grade MADL Detection Simulation

Integrates all operational improvements:
- Realistic RF propagation (atmospheric effects)
- GPS timing synchronization errors
- Adaptive antenna patterns and EP countermeasures
- Multi-hypothesis tracking
- Unknown formation detection
- Processing latency modeling
- Monte Carlo validation
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict
import time as pytime

from osint_cad.sensors.signal_processing import FaintSignalDetector, AngleOfArrivalEstimator
from osint_cad.sensors.geolocation_network import GeolocationEngine, PlatformState, Measurement
from osint_cad.physics.rf_propagation import (OperationalRFPropagation, AtmosphericConditions,
                            TimingSynchronization, RFInterferenceEnvironment)
from osint_cad.sensors.adaptive_antenna_ep import (AdaptiveAntennaPattern, ElectronicProtection,
                                EPMode, FormationAdaptiveTactics)
from osint_cad.sensors.advanced_tracking import MultiHypothesisTracker, UnknownFormationDetector


@dataclass
class ProcessingDelay:
    """Models realistic processing latency"""
    detection_delay_ms: float = 5.0  # Signal detection processing
    geolocation_delay_ms: float = 50.0  # TDOA solution computation
    tracking_delay_ms: float = 20.0  # Track update
    network_delay_ms: float = 30.0  # Network inference

    def get_total_delay(self) -> float:
        """Get total processing delay in seconds"""
        return (self.detection_delay_ms +
                self.geolocation_delay_ms +
                self.tracking_delay_ms +
                self.network_delay_ms) / 1000.0


class OperationalMADLEmitter:
    """
    Operational F-35 MADL emitter with full EP capabilities
    """

    def __init__(self, emitter_id: int, position: np.ndarray, velocity: np.ndarray):
        self.emitter_id = emitter_id
        self.position = position.copy()
        self.velocity = velocity.copy()

        # Adaptive antenna
        self.antenna = AdaptiveAntennaPattern(
            n_elements=64,
            baseline_gain_db=20,
            baseline_beamwidth_deg=3.0,
            sidelobe_target_db=-30
        )

        # Electronic Protection suite
        self.ep_suite = ElectronicProtection()
        self.ep_suite.generate_hop_pattern(
            center_freq_hz=15e9,
            bandwidth_hz=3e9,
            n_channels=100
        )

        # Operating parameters
        self.base_tx_power_dbm = 30
        self.last_transmission = -1.0
        self.transmission_interval = 0.5  # Base interval
        self.detected_threats: List = []

    def update(self, dt: float, current_time: float):
        """Update emitter state"""
        self.position += self.velocity * dt

        # Adapt transmission interval based on threat level
        if len(self.detected_threats) > 0:
            # Reduce emission rate when threats detected
            self.transmission_interval = 1.0  # Slower
        else:
            self.transmission_interval = 0.5  # Normal

    def point_antenna(self, target_position: np.ndarray):
        """Point antenna toward communication partner"""
        delta = target_position - self.position
        azimuth = np.degrees(np.arctan2(delta[1], delta[0]))
        elevation = np.degrees(np.arctan2(delta[2],
                              np.sqrt(delta[0]**2 + delta[1]**2)))

        self.antenna.point_mainbeam(azimuth, elevation)

    def should_transmit(self, current_time: float, threat_proximity_km: float = 999) -> bool:
        """Determine if should transmit based on EP tactics"""
        # Check basic interval
        if current_time - self.last_transmission < self.transmission_interval:
            return False

        # EP tactics reduce emission probability
        tactics = FormationAdaptiveTactics()
        emission_prob = tactics.compute_emission_probability(
            self.emitter_id,
            threat_proximity_km,
            current_time
        )

        if np.random.random() > emission_prob:
            return False  # Skip transmission

        self.last_transmission = current_time
        return True

    def get_transmission_parameters(self, current_time: float, target_distance_m: float) -> Dict:
        """Get current transmission parameters"""
        # Adaptive power control
        tx_power = self.ep_suite.compute_adaptive_power(
            link_distance_m=target_distance_m,
            required_snr_db=10
        )

        # Frequency hopping
        frequency = self.ep_suite.get_next_frequency(current_time)

        # Burst shaping
        duration = self.ep_suite.shape_burst(
            nominal_duration_sec=100e-6,
            randomize=True
        )

        return {
            'power_dbm': tx_power,
            'frequency_hz': frequency,
            'duration_sec': duration
        }


def run_operational_simulation(duration: float = 60.0,
                               dt: float = 0.1,
                               weather_conditions: str = 'clear',
                               ep_mode: str = 'normal',
                               n_monte_carlo: int = 1) -> Dict:
    """
    Run operational simulation with all realistic effects

    Args:
        duration: Simulation duration (seconds)
        dt: Time step (seconds)
        weather_conditions: 'clear', 'rain', 'heavy_rain'
        ep_mode: 'normal', 'lpi_enhanced', 'deception'
        n_monte_carlo: Number of Monte Carlo runs

    Returns:
        Simulation results
    """
    print("=" * 80)
    print("OPERATIONAL MADL DETECTION SIMULATION")
    print("=" * 80)

    # Monte Carlo results storage
    all_results = []

    for mc_run in range(n_monte_carlo):
        if n_monte_carlo > 1:
            print(f"\n[Monte Carlo Run {mc_run + 1}/{n_monte_carlo}]")

        # Setup atmospheric conditions
        if weather_conditions == 'clear':
            atmo_conditions = AtmosphericConditions(
                temperature_c=15,
                humidity_percent=60,
                rain_rate_mm_hr=0
            )
        elif weather_conditions == 'rain':
            atmo_conditions = AtmosphericConditions(
                temperature_c=12,
                humidity_percent=85,
                rain_rate_mm_hr=5.0
            )
        elif weather_conditions == 'heavy_rain':
            atmo_conditions = AtmosphericConditions(
                temperature_c=10,
                humidity_percent=95,
                rain_rate_mm_hr=25.0
            )

        print(f"\n[1] Environmental Conditions:")
        print(f"  Temperature: {atmo_conditions.temperature_c}°C")
        print(f"  Humidity: {atmo_conditions.humidity_percent}%")
        print(f"  Rain rate: {atmo_conditions.rain_rate_mm_hr} mm/hr")

        # Create F-35 formation with operational EP
        print(f"\n[2] Creating F-35 formation with EP mode: {ep_mode}")
        f35_emitters = [
            OperationalMADLEmitter(1, np.array([50000, 0, 10000]), np.array([250, 0, 0])),
            OperationalMADLEmitter(2, np.array([48000, -3000, 10000]), np.array([250, 0, 0])),
            OperationalMADLEmitter(3, np.array([48000, 3000, 10000]), np.array([250, 0, 0])),
            OperationalMADLEmitter(4, np.array([46000, 0, 10000]), np.array([250, 0, 0])),
        ]

        # Set EP mode
        ep_mode_enum = EPMode.NORMAL
        if ep_mode == 'lpi_enhanced':
            ep_mode_enum = EPMode.LPI_ENHANCED
        elif ep_mode == 'deception':
            ep_mode_enum = EPMode.DECEPTION

        for emitter in f35_emitters:
            emitter.ep_suite.set_mode(ep_mode_enum)

        # Point antennas
        f35_emitters[0].point_antenna(f35_emitters[1].position)
        f35_emitters[1].point_antenna(f35_emitters[0].position)
        f35_emitters[2].point_antenna(f35_emitters[0].position)
        f35_emitters[3].point_antenna(f35_emitters[0].position)

        # Create ESM platforms
        print(f"\n[3] Deploying ESM platforms with operational sensors")
        esm_platforms = [
            PlatformState("ESM-1", np.array([0, 0, 12000]), np.array([200, 50, 0]), 0),
            PlatformState("ESM-2", np.array([100000, 0, 12000]), np.array([200, -50, 0]), 0),
            PlatformState("ESM-3", np.array([50000, 86600, 10000]), np.array([200, 0, 0]), 0),
            PlatformState("ESM-4", np.array([50000, -86600, 0]), np.array([0, 0, 0]), 0),
        ]

        # Initialize processing engines
        geo_engine = GeolocationEngine()
        for platform in esm_platforms:
            geo_engine.update_platform_state(platform)

        # Use MHT instead of simple tracker
        mht_tracker = MultiHypothesisTracker(
            max_hypotheses=50,
            pruning_threshold=0.001,
            confirmation_threshold=3
        )

        formation_detector = UnknownFormationDetector()

        # RF environment modeling
        rf_propagation = OperationalRFPropagation()
        timing_sync = TimingSynchronization(
            gps_timing_error_ns=10.0,
            oscillator_drift_ppb=1.0
        )
        rf_interference = RFInterferenceEnvironment()

        # Processing delay model
        processing_delay = ProcessingDelay()

        # Simulation metrics
        detection_count = 0
        geolocation_count = 0
        false_alarm_count = 0
        processing_times = []

        all_detections = []
        all_measurements = []

        # Simulation loop
        print(f"\n[4] Running simulation ({duration}s)...")
        time_steps = int(duration / dt)

        for step in range(time_steps):
            current_time = step * dt
            step_start_time = pytime.time()

            # Update emitters
            for emitter in f35_emitters:
                emitter.update(dt, current_time)

            # Update platforms
            for platform in esm_platforms:
                platform.position += platform.velocity * dt
                platform.timestamp = current_time
                geo_engine.update_platform_state(platform)

            # Detection phase with realistic propagation
            measurements_this_step = []

            for emitter in f35_emitters:
                target_distance = np.linalg.norm(
                    emitter.position - f35_emitters[(emitter.emitter_id % len(f35_emitters))].position
                )

                if emitter.should_transmit(current_time, threat_proximity_km=50):
                    # Get transmission parameters (adaptive)
                    tx_params = emitter.get_transmission_parameters(current_time, target_distance)

                    # Each platform attempts detection
                    toa_measurements = []
                    platform_detections = []

                    for platform in esm_platforms:
                        # Realistic path loss calculation
                        path_loss_db, breakdown = rf_propagation.calculate_path_loss(
                            emitter.position,
                            platform.position,
                            tx_params['frequency_hz'],
                            atmo_conditions
                        )

                        # Antenna gain
                        antenna_gain = emitter.antenna.get_gain(
                            np.degrees(np.arctan2(
                                platform.position[1] - emitter.position[1],
                                platform.position[0] - emitter.position[0]
                            )),
                            0
                        )

                        # Received power
                        rx_power_dbm = tx_params['power_dbm'] + antenna_gain - path_loss_db

                        # Interference and noise
                        interference_dbm = rf_interference.calculate_interference_power(
                            platform.position,
                            tx_params['frequency_hz'],
                            100e6,
                            rf_propagation
                        )

                        snr_db = rx_power_dbm - interference_dbm

                        # Detection threshold
                        if snr_db > 10:  # 10 dB threshold
                            detection_count += 1

                            # Time of arrival with GPS errors
                            distance = np.linalg.norm(platform.position - emitter.position)
                            true_toa = current_time + distance / 299792458.0

                            # Add timing synchronization errors
                            timing_error = timing_sync.get_timing_error(
                                platform.platform_id,
                                current_time
                            )
                            measured_toa = true_toa + timing_error

                            toa_meas = Measurement(
                                platform_id=platform.platform_id,
                                timestamp=current_time,
                                measurement_type='TOA',
                                value=measured_toa,
                                uncertainty=timing_sync.gps_timing_error
                            )
                            toa_measurements.append(toa_meas)

                            # AoA measurement
                            delta = emitter.position - platform.position
                            true_azimuth = np.degrees(np.arctan2(delta[1], delta[0]))
                            measured_azimuth = true_azimuth + np.random.normal(0, 2.0)

                            aoa_meas = Measurement(
                                platform_id=platform.platform_id,
                                timestamp=current_time,
                                measurement_type='AOA',
                                value=0,
                                uncertainty=2.0,
                                azimuth=measured_azimuth,
                                elevation=0
                            )
                            platform_detections.append(aoa_meas)

                    # Geolocation if enough measurements
                    if len(toa_measurements) >= 4:
                        try:
                            estimated_pos, covariance = geo_engine.tdoa_geolocation(toa_measurements)

                            if estimated_pos is not None and np.isfinite(estimated_pos).all():
                                geolocation_count += 1
                                measurements_this_step.append((estimated_pos, covariance))

                                error = np.linalg.norm(estimated_pos - emitter.position)
                                all_detections.append({
                                    'time': current_time,
                                    'true_id': emitter.emitter_id,
                                    'position': estimated_pos,
                                    'true_position': emitter.position.copy(),
                                    'error': error
                                })

                        except (ValueError, np.linalg.LinAlgError):
                            pass

            # Multi-hypothesis tracking update
            if measurements_this_step:
                confirmed_tracks = mht_tracker.update(
                    measurements_this_step,
                    current_time,
                    dt
                )

                # Store confirmed tracks
                all_measurements.extend(measurements_this_step)

            # Record processing time
            step_processing_time = pytime.time() - step_start_time
            processing_times.append(step_processing_time)

            # Progress
            if (step + 1) % (time_steps // 10) == 0:
                print(f"  Progress: {100 * (step + 1) / time_steps:.0f}% | "
                      f"Detections: {detection_count} | Geolocations: {geolocation_count}")

        # Formation detection
        if len(mht_tracker._get_best_tracks()) > 0:
            track_positions = [t.state[:3] for t in mht_tracker._get_best_tracks()]
            formation_analysis = formation_detector.detect_formation(track_positions)
        else:
            formation_analysis = {'n_formations': 0}

        # Results for this run
        run_results = {
            'detections': all_detections,
            'detection_count': detection_count,
            'geolocation_count': geolocation_count,
            'confirmed_tracks': len(mht_tracker._get_best_tracks()),
            'formation_analysis': formation_analysis,
            'processing_times': processing_times,
            'avg_processing_time_ms': np.mean(processing_times) * 1000,
            'max_processing_time_ms': np.max(processing_times) * 1000
        }

        all_results.append(run_results)

    # Aggregate Monte Carlo results
    print(f"\n[5] Simulation Complete")
    print(f"  Total detections: {sum(r['detection_count'] for r in all_results) / n_monte_carlo:.0f} (avg)")
    print(f"  Total geolocations: {sum(r['geolocation_count'] for r in all_results) / n_monte_carlo:.0f} (avg)")
    print(f"  Confirmed tracks: {sum(r['confirmed_tracks'] for r in all_results) / n_monte_carlo:.1f} (avg)")

    if all_results[0]['detections']:
        all_errors = []
        for run in all_results:
            all_errors.extend([d['error'] for d in run['detections']])

        print(f"\n[6] Geolocation Performance:")
        print(f"  Mean error: {np.mean(all_errors):.1f} m")
        print(f"  Median error: {np.median(all_errors):.1f} m")
        print(f"  95th percentile: {np.percentile(all_errors, 95):.1f} m")

    print(f"\n[7] Processing Performance:")
    print(f"  Avg processing time: {np.mean([r['avg_processing_time_ms'] for r in all_results]):.2f} ms/step")
    print(f"  Max processing time: {np.max([r['max_processing_time_ms'] for r in all_results]):.2f} ms/step")

    print("\n" + "=" * 80)

    return {
        'monte_carlo_results': all_results,
        'n_runs': n_monte_carlo,
        'conditions': {
            'weather': weather_conditions,
            'ep_mode': ep_mode
        }
    }


if __name__ == "__main__":
    # Run operational simulation with various conditions
    print("Running operational validation scenarios...\n")

    # Scenario 1: Clear weather, normal EP
    print("\nSCENARIO 1: Clear weather, normal EP mode")
    results_clear = run_operational_simulation(
        duration=30.0,
        dt=0.1,
        weather_conditions='clear',
        ep_mode='normal',
        n_monte_carlo=1
    )

    # Scenario 2: Rain, enhanced LPI
    print("\n\nSCENARIO 2: Rain conditions, LPI enhanced mode")
    results_rain = run_operational_simulation(
        duration=30.0,
        dt=0.1,
        weather_conditions='rain',
        ep_mode='lpi_enhanced',
        n_monte_carlo=1
    )

    # Scenario 3: Heavy rain, deception mode
    print("\n\nSCENARIO 3: Heavy rain, deception mode")
    results_heavy = run_operational_simulation(
        duration=30.0,
        dt=0.1,
        weather_conditions='heavy_rain',
        ep_mode='deception',
        n_monte_carlo=1
    )

    print("\n\n" + "=" * 80)
    print("OPERATIONAL VALIDATION COMPLETE")
    print("=" * 80)
