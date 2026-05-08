// ASBM Kill Chain — Shared ISR / C2 Subsystem Data

import { SubsystemDetail } from './asbm-kill-chain.interfaces';

export const ISR_C2_SUBSYSTEMS: SubsystemDetail[] = [

  // ── 1. OTH-B Radar ────────────────────────────────────────────────────────
  {
    id: 'othb-radar',
    name: 'OTH-B Skywave Radar',
    category: 'isr',
    icon: '\u{1F4E1}',
    overview: 'Over-the-horizon backscatter radar providing wide-area maritime surveillance at 1000-3000 km range. Uses HF skywave propagation via ionospheric refraction to detect carrier-sized targets beyond line-of-sight. Provides initial cueing for satellite tasking.',
    components: [
      {
        name: 'Transmit Array',
        description: 'Large HF phased-array transmitter for ionospheric illumination',
        specs: [
          { name: 'Element Count', value: '30-50 dipoles' },
          { name: 'Power per Element', value: 100, unit: 'kW' },
          { name: 'Total EIRP', value: 'up to 80', unit: 'dBW' },
          { name: 'Frequency Range', value: '5-28', unit: 'MHz' },
          { name: 'Array Length', value: '~1000', unit: 'm' },
          { name: 'Beam Steering', value: 'Electronic (azimuth)' }
        ]
      },
      {
        name: 'Receive Array',
        description: 'Separate receive array with digital beamforming',
        specs: [
          { name: 'Configuration', value: 'Linear dipole array (~500 m)' },
          { name: 'Digital Beamforming', value: 'Yes (per-element digitization)' },
          { name: 'Channels', value: '50-100' },
          { name: 'Dynamic Range', value: '>80', unit: 'dB' }
        ]
      },
      {
        name: 'Ionosonde Module',
        description: 'Real-time ionospheric sounding for propagation path calibration',
        specs: [
          { name: 'Sounding Method', value: 'Vertical + oblique ionosonde' },
          { name: 'Electron Density Profile', value: 'Real-time Ne(h) estimation' },
          { name: 'Ray-Trace Model', value: '3D numerical ray tracing' },
          { name: 'Update Rate', value: 'Every 5 min' }
        ]
      },
      {
        name: 'Doppler Processor',
        description: 'Coherent Doppler processing for target detection against sea clutter',
        specs: [
          { name: 'FFT Size', value: 4096 },
          { name: 'Integration Time', value: '10-30', unit: 's' },
          { name: 'Velocity Resolution', value: 0.5, unit: 'm/s' },
          { name: 'Doppler Ambiguity', value: 'Resolved via stagger PRF' }
        ]
      },
      {
        name: 'CFAR Detector',
        description: 'Constant false alarm rate detection against variable sea clutter',
        specs: [
          { name: 'Algorithm', value: 'CA-CFAR with guard cells' },
          { name: 'P_fa Setting', value: '1e-6' },
          { name: 'CFAR Window', value: '32 range cells' },
          { name: 'Guard Cells', value: 4 }
        ]
      },
      {
        name: 'Sea Clutter Model',
        description: 'Bragg scattering model for HF sea surface returns',
        specs: [
          { name: 'Primary Mechanism', value: 'Bragg scattering from ocean waves' },
          { name: 'Bragg Wavelength', value: 'lambda_RF / 2', note: 'Half the radar wavelength' },
          { name: 'Sea State Dependence', value: 'Wind speed + direction model' },
          { name: 'Clutter Level', value: '-20 to +10', unit: 'dB sigma_0' }
        ]
      },
      {
        name: 'ECCM Controller',
        description: 'Counter-jamming and interference mitigation',
        specs: [
          { name: 'Frequency Diversity', value: 'Hop across 5-28 MHz band' },
          { name: 'Adaptive Nulling', value: 'Null jammers in receive pattern' },
          { name: 'Sidelobe Cancellation', value: 'Auxiliary element cancellers' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Detection Range', value: '1000-3000', unit: 'km', context: 'Against carrier-sized target' },
      { metric: 'Bearing Accuracy', value: '+-2', unit: 'deg' },
      { metric: 'Range Accuracy', value: '10-30', unit: 'km' },
      { metric: 'Revisit Rate', value: '60-120', unit: 's' },
      { metric: 'False Alarm Rate', value: '<1e-6', unit: 'per cell per scan' },
      { metric: 'Coverage Sector', value: '60', unit: 'deg azimuth' }
    ],
    equations: [
      {
        name: 'OTH Ionospheric Propagation',
        latex: 'R_OTH = 2 * h_iono * tan(theta_elev) + R_earth_curvature',
        description: 'Simplified single-hop OTH range via ionospheric refraction',
        variables: [
          { symbol: 'R_OTH', meaning: 'OTH detection range', unit: 'km' },
          { symbol: 'h_iono', meaning: 'Ionospheric reflection height', unit: 'km' },
          { symbol: 'theta_elev', meaning: 'Elevation angle to ionosphere', unit: 'deg' }
        ],
        numericalExample: {
          inputs: { 'h_iono': '300 km (F-layer)', 'theta_elev': '20 deg (low angle)' },
          calculation: 'R = 2 * 300 * tan(70 deg) = 2 * 300 * 2.75 = 1648 km (single hop)',
          result: '~1500-1800 km per single-hop; 2500-3000 km for two-hop'
        }
      },
      {
        name: 'Bragg Scattering Cross-Section',
        latex: 'sigma_Bragg = 2^6 * pi^5 * k_0^4 * S(2*k_0)',
        description: 'Sea surface radar cross-section at the Bragg resonance — dominant clutter mechanism for OTH radar',
        variables: [
          { symbol: 'sigma_Bragg', meaning: 'Bragg cross-section per unit area', unit: 'm^2/m^2' },
          { symbol: 'k_0', meaning: 'Radar wavenumber', unit: 'rad/m' },
          { symbol: 'S(2k_0)', meaning: 'Ocean wave spectrum at Bragg wavelength', unit: 'm^3/rad' }
        ]
      },
      {
        name: 'CFAR Threshold',
        latex: 'T_CFAR = alpha * (1/N) * SUM(x_i)',
        description: 'Cell-averaging CFAR threshold computed from surrounding reference cells',
        variables: [
          { symbol: 'T_CFAR', meaning: 'Detection threshold', unit: 'power units' },
          { symbol: 'alpha', meaning: 'Threshold multiplier (from P_fa)', unit: '' },
          { symbol: 'N', meaning: 'Number of reference cells', unit: '' },
          { symbol: 'x_i', meaning: 'Power in reference cell i', unit: '' }
        ]
      }
    ],
    pseudocode: [
      {
        title: 'OTH-B Detection Pipeline',
        description: 'Full processing chain from HF backscatter to fused detection report',
        lines: [
          '// 1. Ionospheric calibration',
          'iono_profile = ionosonde.get_Ne_profile()',
          'ray_paths = trace_rays(iono_profile, freq_band)',
          'select_optimal_freq(ray_paths, target_range)',
          '',
          '// 2. Transmit and receive',
          'tx_waveform = generate_chirp(freq, bandwidth, PRF)',
          'transmit_array.beam_steer(azimuth_sector)',
          'raw_returns = receive_array.digitize()',
          '',
          '// 3. Digital beamforming',
          'beamformed = digital_beamform(raw_returns, steering_vectors)',
          '',
          '// 4. Range-Doppler processing',
          'range_compressed = matched_filter(beamformed, tx_waveform)',
          'doppler_map = FFT(range_compressed, N=4096)',
          '',
          '// 5. Ionospheric correction',
          'corrected_map = apply_iono_correction(doppler_map, ray_paths)',
          '',
          '// 6. Sea clutter suppression',
          'clutter_estimate = bragg_model(sea_state, wind, freq)',
          'signal = doppler_map - clutter_estimate',
          '',
          '// 7. CFAR detection',
          'FOR each range-Doppler cell:',
          '  threshold = CFAR(signal, guard=4, ref=32, Pfa=1e-6)',
          '  IF signal[cell] > threshold:',
          '    detection = {range, bearing, doppler, SNR}',
          '    EMIT to fusion center'
        ]
      }
    ],
    operationalNotes: [
      'OTH-B is NOT weapons-quality — provides initial cueing with 10-30 km accuracy',
      'Ionospheric variability (day/night, solar activity, geomagnetic storms) affects performance unpredictably',
      'Bragg scattering from ocean waves is the dominant clutter source — limits detection of slow-moving targets',
      'OTH radar can detect carrier groups (large RCS, ~50,000 m^2) but NOT individual ship identification',
      'Two sites believed operational: one near Hubei (Western Pacific coverage), one near Shandong (East China Sea)',
      'Vulnerable to HF jamming, but wide frequency agility (5-28 MHz) provides some resilience'
    ],
    interactionsWith: ['fusion-center']
  },

  // ── 2. Yaogan SAR Constellation ───────────────────────────────────────────
  {
    id: 'yaogan-sar',
    name: 'Yaogan SAR Constellation',
    category: 'isr',
    icon: '\u{1F6F0}',
    overview: 'Space-based synthetic aperture radar constellation providing all-weather, day/night maritime surveillance. SAR imagery enables ship detection, classification (carrier vs destroyer vs tanker), and position fix to weapons-quality accuracy.',
    components: [
      {
        name: 'SAR Antenna',
        description: 'X-band SAR antenna for maritime surveillance',
        specs: [
          { name: 'Aperture', value: '10 x 2', unit: 'm', note: 'Deployable array' },
          { name: 'Frequency', value: 'X-band (9.6 GHz)' },
          { name: 'Polarization', value: 'HH + VV (dual-pol)' },
          { name: 'Peak Power', value: 5, unit: 'kW' }
        ]
      },
      {
        name: 'Chirp Generator',
        description: 'Wideband LFM chirp for high range resolution',
        specs: [
          { name: 'Bandwidth', value: 300, unit: 'MHz' },
          { name: 'Center Frequency', value: 9.6, unit: 'GHz' },
          { name: 'Pulse Width', value: '10-50', unit: 'microsec' },
          { name: 'Range Resolution (achievable)', value: 0.5, unit: 'm' }
        ]
      },
      {
        name: 'Range Compressor',
        description: 'Matched filter for pulse compression',
        specs: [
          { name: 'Method', value: 'Matched filter (frequency domain)' },
          { name: 'Compression Ratio', value: '>1000' },
          { name: 'Sidelobe Level', value: '-30', unit: 'dB', note: 'With Taylor weighting' }
        ]
      },
      {
        name: 'Azimuth Compressor',
        description: 'SAR image formation via azimuth compression',
        specs: [
          { name: 'Algorithm', value: 'Omega-K (wavenumber domain)' },
          { name: 'Alternative', value: 'Chirp scaling (for wide swath)' },
          { name: 'Azimuth Resolution', value: '1-3', unit: 'm', note: 'Spotlight mode' },
          { name: 'Motion Compensation', value: 'Autofocus (PGA)' }
        ]
      },
      {
        name: 'Ship Detector',
        description: 'Automated ship detection on SAR imagery',
        specs: [
          { name: 'Algorithm', value: 'CFAR on SAR amplitude image' },
          { name: 'P_fa', value: 1e-4, note: 'Per pixel' },
          { name: 'Min Ship Size', value: 30, unit: 'm' },
          { name: 'Wake Detection', value: 'Kelvin wake pattern matching' }
        ]
      },
      {
        name: 'CNN Classifier',
        description: 'Deep learning ship classification from SAR chips',
        specs: [
          { name: 'Architecture', value: 'ResNet-50 (modified for SAR)' },
          { name: 'Classes', value: 'Carrier, Destroyer, Cruiser, Tanker, Merchant' },
          { name: 'Training Data', value: '>100,000 SAR ship chips' },
          { name: 'Classification Accuracy', value: '>90', unit: '%', note: 'Carrier vs non-carrier' }
        ]
      },
      {
        name: 'Orbit Control',
        description: 'Constellation orbit parameters for maritime revisit',
        specs: [
          { name: 'Altitude', value: 500, unit: 'km' },
          { name: 'Inclination', value: 97.4, unit: 'deg', note: 'Sun-synchronous' },
          { name: 'Period', value: 94.6, unit: 'min' },
          { name: 'Revisit (constellation)', value: '4-8', unit: 'hours', note: 'Critical gap' },
          { name: 'Swath Width', value: '10-100', unit: 'km', note: 'Mode dependent' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Range Resolution (spotlight)', value: '0.5-1', unit: 'm' },
      { metric: 'Azimuth Resolution (spotlight)', value: '1-3', unit: 'm' },
      { metric: 'Swath Width (stripmap)', value: '50-100', unit: 'km' },
      { metric: 'Revisit Interval', value: '4-8', unit: 'hours', context: 'CRITICAL vulnerability' },
      { metric: 'Ship Detection Pd', value: '>0.95', unit: '', context: 'For ships >100m' },
      { metric: 'Position Accuracy', value: '10-50', unit: 'm', context: 'Weapons-quality' }
    ],
    equations: [
      {
        name: 'SAR Range Resolution',
        latex: 'delta_r = c / (2 * B)',
        description: 'Range resolution determined by chirp bandwidth',
        variables: [
          { symbol: 'delta_r', meaning: 'Range resolution', unit: 'm' },
          { symbol: 'c', meaning: 'Speed of light', unit: 'm/s' },
          { symbol: 'B', meaning: 'Chirp bandwidth', unit: 'Hz' }
        ],
        numericalExample: {
          inputs: { 'c': '3e8 m/s', 'B': '300 MHz' },
          calculation: 'delta_r = 3e8 / (2 * 3e8) = 0.5 m',
          result: '0.5 m range resolution'
        }
      },
      {
        name: 'SAR Azimuth Resolution',
        latex: 'delta_az = D / 2',
        description: 'Best achievable azimuth resolution equals half the real antenna length (unfocused SAR limit is worse)',
        variables: [
          { symbol: 'delta_az', meaning: 'Azimuth resolution', unit: 'm' },
          { symbol: 'D', meaning: 'Real antenna length', unit: 'm' }
        ],
        numericalExample: {
          inputs: { 'D': '2 m (antenna physical length)' },
          calculation: 'delta_az = 2 / 2 = 1 m (spotlight mode)',
          result: '1 m azimuth resolution — sufficient to image carrier flight deck features'
        }
      },
      {
        name: 'SAR Doppler Bandwidth',
        latex: 'B_D = 2 * V_sat * cos(theta) / lambda',
        description: 'Doppler bandwidth determines synthetic aperture integration time',
        variables: [
          { symbol: 'B_D', meaning: 'Doppler bandwidth', unit: 'Hz' },
          { symbol: 'V_sat', meaning: 'Satellite velocity', unit: 'm/s' },
          { symbol: 'theta', meaning: 'Look angle', unit: 'rad' },
          { symbol: 'lambda', meaning: 'Wavelength', unit: 'm' }
        ]
      }
    ],
    pseudocode: [
      {
        title: 'SAR Maritime Detection Pipeline',
        description: 'From raw SAR echo to classified ship detection with position fix',
        lines: [
          '// 1. SAR image formation',
          'raw = collect_SAR_echo(swath_params)',
          'range_comp = matched_filter(raw, chirp_replica)',
          'azimuth_comp = omega_K_focus(range_comp, orbit_data)',
          'image = autofocus(azimuth_comp)  // Phase gradient autofocus',
          '',
          '// 2. Ship detection',
          'FOR each subimage in tile(image, 256x256):',
          '  threshold = CFAR_2D(subimage, Pfa=1e-4)',
          '  detections = subimage > threshold',
          '  ships = cluster_and_filter(detections, min_size=30m)',
          '',
          '// 3. Ship classification',
          'FOR each ship in ships:',
          '  chip = extract_chip(image, ship.center, 128x128)',
          '  class, confidence = CNN_classify(chip)',
          '  IF class == "CARRIER" AND confidence > 0.8:',
          '    position = geocode(ship.center, orbit_data)',
          '    EMIT high_priority_report(position, class, confidence)',
          '',
          '// 4. Wake detection (supplementary)',
          'wake_map = detect_kelvin_wake(image)',
          'FOR each wake in wake_map:',
          '  heading, speed = estimate_from_wake(wake)',
          '  associate_with_ship(wake, ships)'
        ]
      }
    ],
    operationalNotes: [
      'Yaogan constellation operates in SAR, ELINT, and optical triplet formations',
      '4-8 hour revisit gap is the CRITICAL vulnerability — U.S. can exploit by maneuvering between passes',
      'SAR operates in all weather and night — advantage over optical satellites',
      'Ship classification accuracy >90% for carrier-class but degrades for smaller vessels or when ships are close together',
      'SAR image download via Tianlian relay or Chinese ground stations — adds minutes of latency',
      'Anti-satellite weapons (ASAT) could remove SAR capability from the kill chain entirely'
    ],
    interactionsWith: ['fusion-center']
  },

  // ── 3. Multi-Source Fusion Center ─────────────────────────────────────────
  {
    id: 'fusion-center',
    name: 'Multi-Source Fusion Center',
    category: 'fusion',
    icon: '\u{1F504}',
    overview: 'Central data fusion facility combining OTH radar, satellite SAR/ELINT, SIGINT, HUMINT, and UAV reports into unified track files. Extended Kalman filter fuses heterogeneous measurements with vastly different accuracies and update rates.',
    components: [
      {
        name: 'EKF Engine',
        description: 'Extended Kalman filter for multi-source track fusion',
        specs: [
          { name: 'State Vector', value: '[x, y, vx, vy, ax, ay]', note: '6-state (pos/vel/accel)' },
          { name: 'Process Noise Q', value: 'Singer model (correlated accel)' },
          { name: 'OTH Measurement Noise R', value: 'diag([10km, 2deg])^2', note: 'Large uncertainty' },
          { name: 'SAR Measurement Noise R', value: 'diag([30m, 30m])^2', note: 'Weapons-quality' },
          { name: 'ELINT Measurement Noise R', value: 'diag([5km, 5deg])^2' },
          { name: 'HUMINT Measurement Noise R', value: 'diag([50km, 20deg])^2', note: 'Rough estimate' }
        ]
      },
      {
        name: 'Track Correlator',
        description: 'Associates new measurements with existing tracks',
        specs: [
          { name: 'Gating Distance', value: '3-sigma Mahalanobis' },
          { name: 'Scoring Function', value: 'Log-likelihood ratio' },
          { name: 'Ambiguity Resolution', value: 'Global nearest neighbor (GNN)' },
          { name: 'Multi-Hypothesis', value: 'MHT fallback for dense scenarios' }
        ]
      },
      {
        name: 'Track Manager',
        description: 'Track lifecycle management (initiation, maintenance, deletion)',
        specs: [
          { name: 'Initiation Rule', value: '3-of-5 detections' },
          { name: 'Deletion Rule', value: '5 consecutive misses' },
          { name: 'Track Quality Metric', value: 'Integrated track score' },
          { name: 'Max Tracks', value: 500 }
        ]
      },
      {
        name: 'Sensor Interface Module',
        description: 'Normalizes heterogeneous sensor data into common format',
        specs: [
          { name: 'Data Normalization', value: 'WGS-84 coordinates, UTC time' },
          { name: 'Timestamp Alignment', value: '< 100 ms accuracy' },
          { name: 'Latency Compensation', value: 'Retrodiction for late-arriving data' },
          { name: 'Interfaces', value: 'OTH, SAR, ELINT, HUMINT, UAV' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Fused Track CEP (with SAR)', value: '30-100', unit: 'm', context: 'After SAR update' },
      { metric: 'Fused Track CEP (OTH only)', value: '10-30', unit: 'km', context: 'Between SAR passes' },
      { metric: 'Track Latency (to weapons quality)', value: '5-15', unit: 'min', context: 'From initial detection' },
      { metric: 'Track Capacity', value: 500, unit: 'simultaneous tracks' },
      { metric: 'False Track Rate', value: '<0.01', unit: 'per hour' }
    ],
    equations: [
      {
        name: 'Kalman Filter Predict Step',
        latex: 'x_pred = F * x_est; P_pred = F * P_est * F^T + Q',
        description: 'State prediction using process model — propagates track between sensor updates',
        variables: [
          { symbol: 'x_pred', meaning: 'Predicted state', unit: 'mixed' },
          { symbol: 'F', meaning: 'State transition matrix', unit: '' },
          { symbol: 'P_pred', meaning: 'Predicted covariance', unit: 'm^2' },
          { symbol: 'Q', meaning: 'Process noise (target maneuver)', unit: 'm^2' }
        ]
      },
      {
        name: 'Kalman Filter Update Step',
        latex: 'K = P_pred * H^T * (H * P_pred * H^T + R)^-1; x_est = x_pred + K * (z - H * x_pred)',
        description: 'Measurement update — incorporates new sensor observation to refine track',
        variables: [
          { symbol: 'K', meaning: 'Kalman gain', unit: '' },
          { symbol: 'H', meaning: 'Observation matrix', unit: '' },
          { symbol: 'z', meaning: 'Measurement vector', unit: 'mixed' },
          { symbol: 'R', meaning: 'Measurement noise covariance', unit: 'mixed' }
        ]
      },
      {
        name: 'Mahalanobis Gating Distance',
        latex: 'd_M = sqrt((z - H*x)^T * S^-1 * (z - H*x))',
        description: 'Statistical distance for measurement-to-track association gating',
        variables: [
          { symbol: 'd_M', meaning: 'Mahalanobis distance', unit: '' },
          { symbol: 'S', meaning: 'Innovation covariance (H*P*H^T + R)', unit: '' },
          { symbol: 'z', meaning: 'Measurement', unit: '' },
          { symbol: 'H*x', meaning: 'Predicted measurement', unit: '' }
        ]
      },
      {
        name: 'Track Score (Log-Likelihood)',
        latex: 'L = SUM(ln(P_d / P_fa) - 0.5 * d_M^2)',
        description: 'Cumulative track score — higher score indicates more confident track',
        variables: [
          { symbol: 'L', meaning: 'Track log-likelihood score', unit: '' },
          { symbol: 'P_d', meaning: 'Detection probability', unit: '' },
          { symbol: 'P_fa', meaning: 'False alarm probability', unit: '' },
          { symbol: 'd_M', meaning: 'Mahalanobis distance of update', unit: '' }
        ]
      }
    ],
    pseudocode: [
      {
        title: 'Complete Fusion Cycle',
        description: 'Predict → Gate → Associate → Update → Manage tracks',
        lines: [
          '// Fusion cycle runs on each new measurement arrival',
          'FUNCTION process_measurement(z, sensor_type, timestamp):',
          '',
          '  // 1. Predict all tracks to measurement time',
          '  FOR each track in active_tracks:',
          '    dt = timestamp - track.last_update',
          '    track.x_pred = F(dt) * track.x_est',
          '    track.P_pred = F(dt) * track.P_est * F(dt)^T + Q(dt)',
          '',
          '  // 2. Compute gating',
          '  H = observation_matrix(sensor_type)',
          '  R = noise_covariance(sensor_type)',
          '  candidates = []',
          '  FOR each track in active_tracks:',
          '    S = H * track.P_pred * H^T + R',
          '    d_M = mahalanobis(z, H * track.x_pred, S)',
          '    IF d_M < GATE_THRESHOLD:  // 3-sigma gate',
          '      candidates.append({track, d_M, S})',
          '',
          '  // 3. Associate (GNN)',
          '  IF candidates.length > 0:',
          '    best = min(candidates, key=d_M)',
          '    // 4. Update best track',
          '    K = best.track.P_pred * H^T * inv(best.S)',
          '    innovation = z - H * best.track.x_pred',
          '    best.track.x_est = best.track.x_pred + K * innovation',
          '    best.track.P_est = (I - K*H) * best.track.P_pred',
          '    best.track.score += ln(Pd/Pfa) - 0.5*best.d_M^2',
          '  ELSE:',
          '    // No gate match — tentative new track',
          '    create_tentative_track(z, sensor_type)',
          '',
          '  // 5. Track management',
          '  FOR each track in all_tracks:',
          '    IF track.consecutive_misses > 5:',
          '      delete_track(track)',
          '    IF track.tentative AND track.hits >= 3:',
          '      promote_to_confirmed(track)'
        ]
      }
    ],
    operationalNotes: [
      'Fusion center is the CRITICAL node — single point of failure for the entire kill chain',
      'OTH radar provides continuous but low-accuracy tracks; SAR provides intermittent but high-accuracy updates',
      'Between SAR passes, track uncertainty grows rapidly — a carrier can move 30 km in 30 minutes',
      'HUMINT (fishing fleet) data is very low quality but can fill gaps between satellite passes',
      'Retrodiction capability handles late-arriving data by "rewinding" track state to measurement time',
      'Physical location likely underground, hardened against conventional strike — but vulnerable to cyber attack'
    ],
    interactionsWith: ['othb-radar', 'yaogan-sar', 'c2-network']
  },

  // ── 4. C2 Network & Targeting ─────────────────────────────────────────────
  {
    id: 'c2-network',
    name: 'C2 Network & Targeting',
    category: 'c2',
    icon: '\u{1F3DB}',
    overview: 'Command, control, and targeting chain from Central Military Commission (CMC) to individual TEL. Targeting data package generation, authorization chain, and communications infrastructure connecting ISR to shooters.',
    components: [
      {
        name: 'Command Authorization Terminal',
        description: 'Multi-level authorization chain for ASBM launch',
        specs: [
          { name: 'Authorization Levels', value: 'CMC → Theater → PLARF → Brigade → Battalion → TEL' },
          { name: 'Decision Chain Time', value: '5-15', unit: 'min', note: 'Peacetime procedures' },
          { name: 'Pre-Delegated Authority', value: 'Possible in crisis', note: 'Reduces to 2-5 min' },
          { name: 'Authentication', value: 'Multi-factor + physical key' }
        ]
      },
      {
        name: 'Targeting Data Package Generator',
        description: 'Assembles weapons-quality targeting data from fused tracks',
        specs: [
          { name: 'Coordinate Frame', value: 'WGS-84 geodetic' },
          { name: 'Target Uncertainty', value: 'Covariance matrix from fusion', note: 'Drives seeker search box' },
          { name: 'Seeker Search Box', value: '3-sigma containment ellipse' },
          { name: 'Target Velocity', value: 'Course + speed for extrapolation' },
          { name: 'Package Format', value: 'Encrypted digital targeting message' }
        ]
      },
      {
        name: 'Communications Subsystem',
        description: 'Multi-path communications linking C2 chain',
        specs: [
          { name: 'Primary Path', value: 'Fiber optic backbone' },
          { name: 'Fiber Latency', value: '<50', unit: 'ms' },
          { name: 'Satellite Relay', value: 'Tianlian data relay satellite' },
          { name: 'Satellite Latency', value: '500-1000', unit: 'ms' },
          { name: 'HF Radio Backup', value: 'Degraded mode, 2400 bps' },
          { name: 'Redundancy', value: '3-path (fiber + sat + HF)' }
        ]
      },
      {
        name: 'Decision Support System',
        description: 'Automated tools for threat assessment and weapon-target assignment',
        specs: [
          { name: 'Threat Assessment', value: 'Automatic threat ranking by target type' },
          { name: 'Weapon-Target Assignment', value: 'Optimization: min missiles per target Pk' },
          { name: 'BDA (Battle Damage)', value: 'Post-strike satellite imagery analysis' },
          { name: 'Recommendation Engine', value: 'Salvo size + missile type recommendation' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Authorization Timeline', value: '5-15', unit: 'min', context: 'Peacetime chain of command' },
      { metric: 'Pre-Delegated Authorization', value: '2-5', unit: 'min', context: 'Crisis/wartime' },
      { metric: 'Targeting Latency', value: '1-3', unit: 'min', context: 'From fused track to package' },
      { metric: 'Link Reliability (fiber)', value: '>99.9', unit: '%' },
      { metric: 'Link Reliability (satellite)', value: '95-99', unit: '%' },
      { metric: 'Redundancy Level', value: 3, unit: 'independent paths' }
    ],
    pseudocode: [
      {
        title: 'Authorization Chain Flow',
        description: 'Decision flow from fusion center alert to TEL launch authorization',
        lines: [
          'FUNCTION authorize_launch(track):',
          '  // Fusion center raises alert',
          '  IF track.quality > WEAPONS_QUALITY_THRESHOLD:',
          '    alert = create_alert(track, priority="HIGH")',
          '    send_to(PLARF_COMMAND, alert)',
          '',
          '  // PLARF validates and requests authorization',
          '  IF PLARF.validate(alert):',
          '    request = create_auth_request(alert, recommended_salvo)',
          '    send_to(THEATER_COMMAND, request)',
          '',
          '  // Theater command reviews and escalates',
          '  IF THEATER.approve(request):',
          '    send_to(CMC, request)  // May be pre-delegated in wartime',
          '',
          '  // CMC authorizes (or pre-delegated authority)',
          '  IF CMC.authorize(request):',
          '    auth_code = generate_launch_auth()',
          '    send_to(BRIGADE, auth_code)',
          '',
          '  // Brigade assigns battalion/TEL',
          '  tel_assignment = weapon_target_assign(auth_code, available_TELs)',
          '  send_to(BATTALION, tel_assignment)',
          '',
          '  // Battalion/TEL executes',
          '  TEL.receive_targeting(targeting_package)',
          '  TEL.receive_auth(auth_code)',
          '  TEL.execute_launch()'
        ]
      },
      {
        title: 'Targeting Package Assembly',
        description: 'Generates the data package uploaded to missile pre-launch',
        lines: [
          'FUNCTION assemble_targeting_package(track, missile_type):',
          '  // Get latest fused track',
          '  state = fusion_center.get_track(track.id)',
          '  t_now = current_time()',
          '',
          '  // Estimate time-of-flight',
          '  range = distance(TEL.position, state.position)',
          '  tof = estimate_TOF(missile_type, range)',
          '',
          '  // Predict target position at impact',
          '  predicted_pos = state.position + state.velocity * tof',
          '  predicted_cov = state.covariance + Q_maneuver * tof^2',
          '',
          '  // Compute seeker search box',
          '  search_box = 3 * sqrt(eigenvalues(predicted_cov))',
          '',
          '  // Assemble package',
          '  package = {',
          '    aim_point: predicted_pos,',
          '    target_velocity: state.velocity,',
          '    search_box: search_box,',
          '    confidence: state.track_quality,',
          '    timestamp: t_now,',
          '    missile_config: get_config(missile_type)',
          '  }',
          '  RETURN encrypt(package)'
        ]
      }
    ],
    operationalNotes: [
      'Authorization chain is a CRITICAL vulnerability — decapitation strike on C2 nodes breaks the kill chain',
      'Pre-delegated authority in wartime reduces timeline but increases risk of unauthorized/accidental launch',
      'Dual-capable DF-26 complicates C2 — adversary cannot distinguish nuclear from conventional launch',
      'Fiber backbone hardened but HF radio backup is low-bandwidth — may not support full targeting data',
      'Cyber attack on C2 network is high-priority U.S. counter-ASBM strategy',
      'Decision support system recommends salvo size based on target type, BMD estimate, and required Pk'
    ],
    interactionsWith: ['fusion-center', 'othb-radar', 'yaogan-sar']
  }
];
