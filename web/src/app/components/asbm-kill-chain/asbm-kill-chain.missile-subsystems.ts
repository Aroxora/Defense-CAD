// ASBM Kill Chain — Per-Platform Missile Subsystem Data
// Each platform (DF-21D, DF-26, DF-17) gets 7 subsystems

import { SubsystemDetail } from './asbm-kill-chain.interfaces';

// ═══════════════════════════════════════════════════════════════════════════════
// DF-21D SUBSYSTEMS
// ═══════════════════════════════════════════════════════════════════════════════

export const DF21D_SUBSYSTEMS: SubsystemDetail[] = [
  // ── 1. INS / IMU ──────────────────────────────────────────────────────────
  {
    id: 'ins',
    name: 'Inertial Navigation System',
    category: 'navigation',
    icon: '\u{1F9ED}',
    overview: 'Ring laser gyroscope-based strapdown INS providing autonomous position, velocity, and attitude during boost and midcourse. Standard navigation-grade RLG triad with accelerometer package.',
    components: [
      {
        name: 'Ring Laser Gyroscope Triad',
        description: 'Three-axis ring laser gyroscope package for angular rate sensing',
        specs: [
          { name: 'Type', value: 'Ring Laser Gyroscope (RLG)' },
          { name: 'Bias Instability', value: 0.003, unit: 'deg/hr', note: 'Navigation grade' },
          { name: 'Angle Random Walk', value: 0.002, unit: 'deg/sqrt(hr)' },
          { name: 'Scale Factor Stability', value: 5, unit: 'ppm' },
          { name: 'Bandwidth', value: 1000, unit: 'Hz' },
          { name: 'Operating Temp', value: '-40 to +71', unit: 'C' }
        ]
      },
      {
        name: 'Accelerometer Triad',
        description: 'Three-axis pendulous integrating gyroscopic accelerometer (PIGA) or equivalent',
        specs: [
          { name: 'Bias Stability', value: 10, unit: 'micro-g' },
          { name: 'Scale Factor', value: 5, unit: 'ppm' },
          { name: 'Cross-Axis Sensitivity', value: 5, unit: 'micro-g/g' },
          { name: 'Range', value: '+-50', unit: 'g' }
        ]
      },
      {
        name: 'Navigation Computer',
        description: 'Strapdown INS mechanization with quaternion attitude representation',
        specs: [
          { name: 'Update Rate', value: 200, unit: 'Hz' },
          { name: 'Coordinate Frame', value: 'WGS-84 ECEF' },
          { name: 'Alignment Mode', value: 'Gyrocompass + Transfer', note: 'Pre-launch from TEL' },
          { name: 'Processor', value: 'Radiation-hardened DSP' }
        ]
      },
      {
        name: 'Temperature Compensation Module',
        description: 'Active thermal control and software model for gyro and accelerometer bias drift',
        specs: [
          { name: 'Control Method', value: 'Heater + Peltier' },
          { name: 'Stability', value: '+-0.1', unit: 'C' },
          { name: 'Compensation Model Order', value: '3rd order polynomial' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'CEP at 10 min (free inertial)', value: '150-300', unit: 'm', context: 'No external aiding' },
      { metric: 'CEP with stellar correction', value: '50-100', unit: 'm', context: 'Single stellar fix applied' },
      { metric: 'Velocity accuracy', value: 0.3, unit: 'm/s', context: 'After alignment' },
      { metric: 'Heading accuracy', value: 0.05, unit: 'deg', context: 'After gyrocompass' }
    ],
    equations: [
      {
        name: 'INS Error Propagation',
        latex: 'sigma_pos(t) = sigma_gyro * R_e * t + 0.5 * sigma_accel * t^2',
        description: 'Position error growth over time from gyro drift and accelerometer bias',
        variables: [
          { symbol: 'sigma_pos', meaning: 'Position error', unit: 'm' },
          { symbol: 'sigma_gyro', meaning: 'Gyro drift rate', unit: 'rad/s' },
          { symbol: 'R_e', meaning: 'Earth radius', unit: 'm' },
          { symbol: 'sigma_accel', meaning: 'Accelerometer bias', unit: 'm/s^2' },
          { symbol: 't', meaning: 'Elapsed time', unit: 's' }
        ],
        numericalExample: {
          inputs: { 'sigma_gyro': '0.003 deg/hr', 'sigma_accel': '10 micro-g', 't': '600 s' },
          calculation: 'sigma_pos = (0.003*pi/180/3600)*6.371e6*600 + 0.5*(10e-6*9.81)*600^2',
          result: '~200 m after 10 min free inertial'
        }
      },
      {
        name: 'Kalman Filter INS-Stellar Coupling',
        latex: 'x_hat(+) = x_hat(-) + K * (z_star - H * x_hat(-))',
        description: 'Optimal state update when stellar fix is incorporated into INS solution',
        variables: [
          { symbol: 'x_hat', meaning: 'State estimate (pos/vel/attitude)', unit: 'mixed' },
          { symbol: 'K', meaning: 'Kalman gain', unit: 'dimensionless' },
          { symbol: 'z_star', meaning: 'Stellar measurement', unit: 'rad' },
          { symbol: 'H', meaning: 'Observation matrix', unit: 'dimensionless' }
        ]
      }
    ],
    pseudocode: [
      {
        title: 'Strapdown INS Mechanization Loop',
        description: 'Core navigation loop executing at 200 Hz: reads sensors, updates attitude via quaternion, transforms specific force to nav frame, subtracts gravity, and integrates velocity/position.',
        lines: [
          'LOOP at 200 Hz:',
          '  // 1. Sensor read',
          '  omega = read_gyro_triad()    // angular rates [rad/s]',
          '  f_body = read_accel_triad()  // specific force [m/s^2]',
          '',
          '  // 2. Quaternion attitude update',
          '  delta_theta = omega * dt',
          '  q = q * quaternion_from_rotvec(delta_theta)',
          '  q = normalize(q)',
          '',
          '  // 3. Direction cosine matrix',
          '  C_bn = dcm_from_quaternion(q)  // body-to-nav',
          '',
          '  // 4. Transform specific force to nav frame',
          '  f_nav = C_bn * f_body',
          '',
          '  // 5. Gravity subtraction',
          '  g_nav = gravity_model(position, altitude)',
          '  a_nav = f_nav - g_nav',
          '',
          '  // 6. Velocity integration (trapezoidal)',
          '  velocity = velocity + 0.5 * (a_nav + a_nav_prev) * dt',
          '',
          '  // 7. Position integration',
          '  position = position + 0.5 * (velocity + velocity_prev) * dt',
          '',
          '  a_nav_prev = a_nav',
          '  velocity_prev = velocity'
        ]
      }
    ],
    operationalNotes: [
      'DF-21D uses standard navigation-grade RLG — established technology with well-understood error models',
      'Pre-launch alignment on TEL takes 5-10 minutes via gyrocompass; transfer alignment from external reference can reduce this',
      'INS drift is the primary error source during boost phase; stellar fix is applied during midcourse to correct accumulated error',
      'Vibration environment during boost degrades gyro performance; post-boost settle time of 2-5 seconds before stellar observation'
    ],
    interactionsWith: ['stellar-nav', 'gnc', 'beidou-datalink']
  },

  // ── 2. Radar Seeker ───────────────────────────────────────────────────────
  {
    id: 'radar-seeker',
    name: 'Radar Seeker',
    category: 'seeker',
    icon: '\u{1F4E1}',
    overview: 'Mechanically-steered parabolic dish radar seeker operating in X-band. Acquires carrier-sized targets at 50-70 km, discriminates by radar cross-section, and provides terminal homing guidance commands.',
    components: [
      {
        name: 'Antenna Assembly',
        description: 'Mechanically gimbaled parabolic dish antenna',
        specs: [
          { name: 'Type', value: 'Mechanically steered parabolic dish' },
          { name: 'Aperture Diameter', value: 0.5, unit: 'm' },
          { name: 'Beamwidth (3dB)', value: 3.5, unit: 'deg' },
          { name: 'Sidelobe Level', value: -25, unit: 'dB' },
          { name: 'Scan Cone', value: '+-30', unit: 'deg' },
          { name: 'Gimbal Rate', value: 60, unit: 'deg/s' }
        ]
      },
      {
        name: 'RF Transmitter',
        description: 'X-band solid-state or TWT transmitter',
        specs: [
          { name: 'Frequency Band', value: 'X-band (9.5-10.5 GHz)' },
          { name: 'Peak Power', value: 500, unit: 'W' },
          { name: 'Average Power', value: 50, unit: 'W' },
          { name: 'Bandwidth', value: 50, unit: 'MHz' }
        ]
      },
      {
        name: 'Waveform Generator',
        description: 'Linear FM chirp with pulse compression',
        specs: [
          { name: 'Chirp Type', value: 'Linear FM (LFM)' },
          { name: 'PRF', value: '5000-20000', unit: 'Hz' },
          { name: 'Pulse Width', value: '1-10', unit: 'microsec' },
          { name: 'Duty Cycle', value: 10, unit: '%' },
          { name: 'Range Resolution', value: 3, unit: 'm' }
        ]
      },
      {
        name: 'Signal Processor',
        description: 'Pulse-Doppler processing with CFAR detection',
        specs: [
          { name: 'Detection Algorithm', value: 'CA-CFAR' },
          { name: 'Clutter Model', value: 'K-distribution sea clutter' },
          { name: 'Doppler Bins', value: 256 },
          { name: 'Range Bins', value: 512 }
        ]
      },
      {
        name: 'Track Gate',
        description: 'Alpha-beta-gamma track filter for target state estimation',
        specs: [
          { name: 'Filter Type', value: 'Alpha-beta-gamma' },
          { name: 'Update Rate', value: 20, unit: 'Hz' },
          { name: 'Track Accuracy', value: '5-10', unit: 'm', note: 'At lock' }
        ]
      },
      {
        name: 'ECCM Module',
        description: 'Counter-countermeasures for jamming resistance',
        specs: [
          { name: 'Home-on-Jam', value: 'Yes', note: 'Passive angle tracking on jammer' },
          { name: 'Sidelobe Blanking', value: 'Yes' },
          { name: 'Frequency Agility', value: '+-200 MHz hop range' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Acquisition Range vs Carrier', value: '50-70', unit: 'km', context: 'RCS ~50,000 m^2' },
      { metric: '3dB Beamwidth', value: 3.5, unit: 'deg' },
      { metric: 'Min Detectable RCS (at 30 km)', value: 100, unit: 'm^2' },
      { metric: 'ECCM Effectiveness', value: 'Moderate', unit: '', context: 'Vulnerable to advanced ECM' }
    ],
    equations: [
      {
        name: 'Radar Range Equation (Seeker)',
        latex: 'R_max = (P_t * G^2 * lambda^2 * sigma / ((4*pi)^3 * k*T*B * SNR_min))^(1/4)',
        description: 'Maximum detection range of the onboard seeker against a target of given RCS',
        variables: [
          { symbol: 'R_max', meaning: 'Maximum detection range', unit: 'm' },
          { symbol: 'P_t', meaning: 'Peak transmit power', unit: 'W' },
          { symbol: 'G', meaning: 'Antenna gain', unit: 'linear' },
          { symbol: 'lambda', meaning: 'Wavelength', unit: 'm' },
          { symbol: 'sigma', meaning: 'Target RCS', unit: 'm^2' },
          { symbol: 'SNR_min', meaning: 'Minimum SNR for detection', unit: 'linear' }
        ],
        numericalExample: {
          inputs: { 'P_t': '500 W', 'G': '30 dBi (1000x)', 'lambda': '0.03 m', 'sigma': '50,000 m^2', 'SNR_min': '13 dB' },
          calculation: 'R = (500 * 1e6 * 9e-4 * 50000 / (1984 * 4e-21 * 50e6 * 20))^0.25',
          result: '~65 km acquisition range vs carrier'
        }
      },
      {
        name: 'Clutter-to-Noise Ratio',
        latex: 'CNR = (P_t * G^2 * lambda^2 * sigma_0 * A_cell) / ((4*pi)^3 * R^4 * k*T*B)',
        description: 'Sea clutter return power relative to noise floor — determines detection performance in clutter',
        variables: [
          { symbol: 'sigma_0', meaning: 'Sea surface backscatter coefficient', unit: 'dB/m^2' },
          { symbol: 'A_cell', meaning: 'Resolution cell area', unit: 'm^2' },
          { symbol: 'R', meaning: 'Range to surface', unit: 'm' }
        ]
      },
      {
        name: 'Detection Probability',
        latex: 'P_d = 0.5 * erfc(erfc_inv(2*P_fa) - sqrt(SNR))',
        description: 'Probability of detection given false alarm rate and signal-to-noise ratio (Swerling I target)',
        variables: [
          { symbol: 'P_d', meaning: 'Probability of detection', unit: '' },
          { symbol: 'P_fa', meaning: 'Probability of false alarm', unit: '' },
          { symbol: 'SNR', meaning: 'Signal-to-noise ratio', unit: 'linear' }
        ]
      }
    ],
    operationalNotes: [
      'Mechanically-steered dish provides good gain but limited scan rate compared to phased array',
      'Seeker window must survive reentry heating — ablative radome with known RF transmission loss curve',
      'Seeker activates at ~70 km altitude / 50 km range during terminal phase',
      'Sea clutter rejection critical — CFAR threshold adapts to local clutter statistics',
      'Home-on-Jam capability provides fallback guidance if target emits high-power jamming'
    ],
    interactionsWith: ['gnc', 'warhead-fuze']
  },

  // ── 3. Guidance & Control ─────────────────────────────────────────────────
  {
    id: 'gnc',
    name: 'Guidance & Control',
    category: 'guidance',
    icon: '\u{1F3AF}',
    overview: 'Midcourse guidance uses pre-programmed trajectory with INS/stellar corrections. Terminal phase switches to proportional navigation using radar seeker LOS rate. Aerodynamic fin control with hydraulic actuators.',
    components: [
      {
        name: 'Guidance Computer',
        description: 'Dual-mode guidance: midcourse trajectory shaping + terminal proportional navigation',
        specs: [
          { name: 'Midcourse Law', value: 'Pre-programmed + INS correction' },
          { name: 'Terminal Law', value: 'Augmented Proportional Navigation (APN)' },
          { name: 'Navigation Constant N', value: '3-5', note: 'Tuned for closing geometry' },
          { name: 'Guidance Update Rate', value: 50, unit: 'Hz' }
        ]
      },
      {
        name: 'Control Actuators',
        description: 'Hydraulic fin actuators for aerodynamic control surfaces',
        specs: [
          { name: 'Fin Type', value: 'Cruciform tail fins' },
          { name: 'Max Deflection', value: '+-25', unit: 'deg' },
          { name: 'Rate Limit', value: 150, unit: 'deg/s' },
          { name: 'Bandwidth', value: 20, unit: 'Hz' },
          { name: 'Actuator Type', value: 'Electro-hydraulic' }
        ]
      },
      {
        name: 'Autopilot',
        description: 'Three-axis autopilot with gain scheduling over Mach number and altitude',
        specs: [
          { name: 'Architecture', value: 'Three-loop (rate, attitude, accel)' },
          { name: 'Gain Schedule', value: 'Mach / altitude lookup' },
          { name: 'Phase Margin', value: '>45', unit: 'deg' },
          { name: 'Gain Margin', value: '>6', unit: 'dB' }
        ]
      },
      {
        name: 'Flight Control Surfaces',
        description: 'Four cruciform tail fins providing pitch, yaw, and roll control',
        specs: [
          { name: 'Fin Count', value: 4 },
          { name: 'Fin Span', value: 0.4, unit: 'm' },
          { name: 'Material', value: 'Titanium alloy' },
          { name: 'Max Dynamic Pressure', value: 200, unit: 'kPa' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Divert Capability (terminal)', value: '5-10', unit: 'km', context: '15 sec terminal phase' },
      { metric: 'Response Time (90% step)', value: 0.2, unit: 's' },
      { metric: 'Max Lateral Acceleration', value: 15, unit: 'g', context: 'At Mach 6, 20 km alt' },
      { metric: 'Control Authority at Impact', value: '8-10', unit: 'g', context: 'Mach 10, sea level' }
    ],
    equations: [
      {
        name: 'Augmented Proportional Navigation',
        latex: 'a_c = N * V_c * lambda_dot + (N * (N-1) / (2 * t_go)) * a_T',
        description: 'Terminal guidance law commanding lateral acceleration to null LOS rate, with target acceleration augmentation',
        variables: [
          { symbol: 'a_c', meaning: 'Commanded lateral acceleration', unit: 'm/s^2' },
          { symbol: 'N', meaning: 'Navigation constant', unit: '' },
          { symbol: 'V_c', meaning: 'Closing velocity', unit: 'm/s' },
          { symbol: 'lambda_dot', meaning: 'Line-of-sight rate', unit: 'rad/s' },
          { symbol: 'a_T', meaning: 'Estimated target acceleration', unit: 'm/s^2' },
          { symbol: 't_go', meaning: 'Time to go', unit: 's' }
        ],
        numericalExample: {
          inputs: { 'N': 4, 'V_c': '3400 m/s', 'lambda_dot': '0.005 rad/s', 'a_T': '0 (straight-line carrier)' },
          calculation: 'a_c = 4 * 3400 * 0.005 = 68 m/s^2 = 6.9g',
          result: '6.9g lateral demand — well within control authority'
        }
      },
      {
        name: 'Zero-Effort-Miss Distance',
        latex: 'ZEM = R * sin(lambda) + R_dot * lambda_dot * t_go^2 / 2',
        description: 'Predicted miss if no further corrections applied — drives guidance gain allocation',
        variables: [
          { symbol: 'ZEM', meaning: 'Zero-effort miss', unit: 'm' },
          { symbol: 'R', meaning: 'Range to target', unit: 'm' },
          { symbol: 'lambda', meaning: 'LOS angle error', unit: 'rad' },
          { symbol: 't_go', meaning: 'Time to go', unit: 's' }
        ]
      },
      {
        name: 'Control Moment',
        latex: 'M = q * S * d * C_m_delta * delta_fin',
        description: 'Aerodynamic control moment generated by fin deflection',
        variables: [
          { symbol: 'M', meaning: 'Control moment', unit: 'N*m' },
          { symbol: 'q', meaning: 'Dynamic pressure', unit: 'Pa' },
          { symbol: 'S', meaning: 'Reference area', unit: 'm^2' },
          { symbol: 'd', meaning: 'Reference diameter', unit: 'm' },
          { symbol: 'C_m_delta', meaning: 'Fin effectiveness coefficient', unit: '1/rad' },
          { symbol: 'delta_fin', meaning: 'Fin deflection', unit: 'rad' }
        ]
      }
    ],
    pseudocode: [
      {
        title: 'Midcourse Guidance Loop',
        description: 'Executes during ballistic midcourse — corrects trajectory using INS/stellar position against pre-programmed reference',
        lines: [
          'WHILE phase == MIDCOURSE:',
          '  pos_current = INS.get_position()',
          '  vel_current = INS.get_velocity()',
          '  pos_ref = trajectory_table.interpolate(time)',
          '  vel_ref = trajectory_table.interpolate_vel(time)',
          '',
          '  // Position and velocity error',
          '  delta_pos = pos_ref - pos_current',
          '  delta_vel = vel_ref - vel_current',
          '',
          '  // Guidance command (trajectory correction)',
          '  a_cmd = K_pos * delta_pos + K_vel * delta_vel',
          '  send_to_autopilot(a_cmd)'
        ]
      },
      {
        title: 'Terminal Homing Loop (PN)',
        description: 'Proportional navigation homing using radar seeker measurements',
        lines: [
          'WHILE phase == TERMINAL:',
          '  seeker_data = radar_seeker.get_track()',
          '  IF NOT seeker_data.valid:',
          '    CONTINUE with last estimate',
          '',
          '  // LOS rate extraction',
          '  lambda_dot = seeker_data.LOS_rate',
          '  V_c = seeker_data.closing_velocity',
          '  t_go = seeker_data.range / V_c',
          '',
          '  // Augmented PN command',
          '  a_cmd = N * V_c * lambda_dot',
          '',
          '  // Limit to available control authority',
          '  a_cmd = clamp(a_cmd, -a_max, a_max)',
          '  send_to_autopilot(a_cmd)'
        ]
      }
    ],
    operationalNotes: [
      'DF-21D uses conventional cruciform fin control — well-proven but lower authority than RCS thruster systems',
      'Fin effectiveness degrades at very high Mach due to strong shock interactions',
      'Autopilot gain schedule covers Mach 2-10 and altitude 0-400 km',
      'Guidance handover from midcourse to terminal occurs when seeker acquires target — typically 50-70 km range'
    ],
    interactionsWith: ['ins', 'radar-seeker', 'warhead-fuze']
  },

  // ── 4. Stellar Navigation ─────────────────────────────────────────────────
  {
    id: 'stellar-nav',
    name: 'Stellar Navigation',
    category: 'navigation',
    icon: '\u{2B50}',
    overview: 'Basic stellar-aided INS correction during midcourse exoatmospheric flight. Star tracker observes known reference stars to compute attitude fix and position correction, reducing accumulated INS drift.',
    components: [
      {
        name: 'Star Tracker',
        description: 'CCD-based star tracker for attitude determination',
        specs: [
          { name: 'Sensor Type', value: 'CCD focal plane array' },
          { name: 'FOV', value: '8x8', unit: 'deg' },
          { name: 'Accuracy (cross-boresight)', value: 5, unit: 'arcsec' },
          { name: 'Star Catalog Size', value: 5000, unit: 'stars' },
          { name: 'Limiting Magnitude', value: 6.0 }
        ]
      },
      {
        name: 'Star Identification Algorithm',
        description: 'Pattern matching for autonomous star identification',
        specs: [
          { name: 'Algorithm', value: 'Triangle matching' },
          { name: 'Lost-in-Space', value: 'Yes', note: 'Can identify stars without initial attitude' },
          { name: 'ID Time', value: '<2', unit: 's' },
          { name: 'Success Rate', value: '>99', unit: '%' }
        ]
      },
      {
        name: 'INS Coupling',
        description: 'Kalman filter integration of stellar observations with INS state',
        specs: [
          { name: 'Kalman Gain (typical)', value: '0.3-0.7', note: 'Depends on INS uncertainty' },
          { name: 'Measurement Noise (1-sigma)', value: 5, unit: 'arcsec' },
          { name: 'Update Rate', value: '1-2', unit: 'fixes during midcourse' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Attitude Accuracy (post-fix)', value: 5, unit: 'arcsec', context: '3-axis attitude' },
      { metric: 'Position Correction', value: '50-200', unit: 'm', context: 'Removes INS drift accumulation' },
      { metric: 'Update Latency', value: 3, unit: 's', context: 'Observation + processing' }
    ],
    equations: [
      {
        name: 'Stellar Fix Position Update',
        latex: 'delta_pos = R_e * delta_attitude',
        description: 'Position correction derived from attitude error measured by star tracker',
        variables: [
          { symbol: 'delta_pos', meaning: 'Position correction', unit: 'm' },
          { symbol: 'R_e', meaning: 'Earth radius', unit: 'm' },
          { symbol: 'delta_attitude', meaning: 'Attitude correction from stars', unit: 'rad' }
        ],
        numericalExample: {
          inputs: { 'R_e': '6.371e6 m', 'delta_attitude': '5 arcsec = 2.42e-5 rad' },
          calculation: 'delta_pos = 6.371e6 * 2.42e-5',
          result: '~154 m correction'
        }
      },
      {
        name: 'Attitude Quaternion from Star Vectors',
        latex: 'q_opt = argmin SUM(w_i * |b_i - C(q) * r_i|^2)',
        description: 'Wahba\'s problem: find optimal attitude quaternion q that rotates reference star vectors (r) to body-frame observations (b)',
        variables: [
          { symbol: 'q_opt', meaning: 'Optimal attitude quaternion', unit: '' },
          { symbol: 'b_i', meaning: 'Body-frame star unit vector', unit: '' },
          { symbol: 'r_i', meaning: 'Reference catalog star vector', unit: '' },
          { symbol: 'w_i', meaning: 'Measurement weight', unit: '' },
          { symbol: 'C(q)', meaning: 'Rotation matrix from quaternion', unit: '' }
        ]
      }
    ],
    operationalNotes: [
      'DF-21D has basic stellar nav — shorter flight time means less INS drift to correct',
      'Stellar observations only possible during exoatmospheric midcourse (above ~80 km)',
      'Observation window limited to 30-60 seconds during apogee passage',
      'Cannot observe if attitude is significantly off-nominal (star tracker FOV constraints)'
    ],
    interactionsWith: ['ins']
  },

  // ── 5. BeiDou Datalink ────────────────────────────────────────────────────
  {
    id: 'beidou-datalink',
    name: 'BeiDou Datalink',
    category: 'datalink',
    icon: '\u{1F4F6}',
    overview: 'Dual-function system: BeiDou-3 navigation receiver for position/timing, plus command datalink for midcourse target updates from C2 network. Provides position aiding to INS and updated target coordinates.',
    components: [
      {
        name: 'BeiDou Receiver',
        description: 'BeiDou-3 multi-frequency GNSS receiver',
        specs: [
          { name: 'Frequencies', value: 'B1C, B2a, B3I' },
          { name: 'Channels', value: 24 },
          { name: 'Acquisition Time (warm)', value: '<10', unit: 's' },
          { name: 'Position Accuracy', value: '<1', unit: 'm', note: 'Military signal' }
        ]
      },
      {
        name: 'Antenna',
        description: 'Conformal patch antenna on missile body',
        specs: [
          { name: 'Type', value: 'Microstrip patch (conformal)' },
          { name: 'Gain', value: 5, unit: 'dBic' },
          { name: 'Coverage', value: 'Upper hemisphere' },
          { name: 'Polarization', value: 'RHCP' }
        ]
      },
      {
        name: 'Message Processor',
        description: 'Processes encrypted targeting updates from ground C2',
        specs: [
          { name: 'Message Format', value: 'PLARF proprietary' },
          { name: 'Encryption', value: 'Military-grade symmetric' },
          { name: 'Update Rate', value: '1-5', unit: 'updates during midcourse' },
          { name: 'Latency', value: '<500', unit: 'ms' }
        ]
      },
      {
        name: 'Anti-Jam Module',
        description: 'Null-steering and spread-spectrum techniques for jam resistance',
        specs: [
          { name: 'Nulling', value: 'Adaptive antenna nulling (2 nulls)' },
          { name: 'Spread Spectrum', value: 'Direct sequence' },
          { name: 'Jam Resistance', value: '30-40', unit: 'dB J/S' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Position Accuracy', value: '<1', unit: 'm', context: 'Military encrypted signal' },
      { metric: 'Update Rate', value: 1, unit: 'Hz', context: 'Position fixes' },
      { metric: 'Jam Resistance', value: '30-40', unit: 'dB', context: 'Anti-jam processing gain' },
      { metric: 'TTFF (warm start)', value: '<10', unit: 's' }
    ],
    equations: [
      {
        name: 'Link Budget',
        latex: 'C/N0 = EIRP - L_path + G/T - k_boltz',
        description: 'Carrier-to-noise density ratio for BeiDou signal reception',
        variables: [
          { symbol: 'C/N0', meaning: 'Carrier-to-noise density', unit: 'dB-Hz' },
          { symbol: 'EIRP', meaning: 'Satellite effective radiated power', unit: 'dBW' },
          { symbol: 'L_path', meaning: 'Free-space path loss', unit: 'dB' },
          { symbol: 'G/T', meaning: 'Receiver antenna gain-to-noise temp', unit: 'dB/K' },
          { symbol: 'k_boltz', meaning: 'Boltzmann constant', unit: '-228.6 dBW/K/Hz' }
        ]
      }
    ],
    operationalNotes: [
      'BeiDou navigation available during boost and early midcourse; may be jammed during terminal approach',
      'Command datalink provides updated target coordinates if C2 has fresher data than pre-launch upload',
      'Datalink reception depends on missile attitude — receiver antenna has limited coverage during maneuvers',
      'BeiDou denied environment is a key vulnerability — INS+stellar must be sufficient as fallback'
    ],
    interactionsWith: ['ins', 'gnc']
  },

  // ── 6. Propulsion ─────────────────────────────────────────────────────────
  {
    id: 'propulsion',
    name: 'Propulsion',
    category: 'propulsion',
    icon: '\u{1F680}',
    overview: 'Two-stage solid-propellant ballistic missile motor derived from the DF-21 MRBM series. Provides ~4000 m/s burnout velocity for 1500 km range ballistic trajectory.',
    components: [
      {
        name: 'First Stage Motor',
        description: 'Large solid rocket motor for initial boost',
        specs: [
          { name: 'Type', value: 'Solid propellant' },
          { name: 'Propellant', value: 'HTPB composite (aluminized)' },
          { name: 'Thrust (vacuum)', value: 400, unit: 'kN' },
          { name: 'Burn Time', value: 55, unit: 's' },
          { name: 'Specific Impulse (vac)', value: 270, unit: 's' },
          { name: 'Mass (loaded)', value: 9000, unit: 'kg' }
        ]
      },
      {
        name: 'Second Stage Motor',
        description: 'Upper stage solid motor for final velocity',
        specs: [
          { name: 'Type', value: 'Solid propellant' },
          { name: 'Propellant', value: 'HTPB composite' },
          { name: 'Thrust (vacuum)', value: 120, unit: 'kN' },
          { name: 'Burn Time', value: 40, unit: 's' },
          { name: 'Specific Impulse (vac)', value: 285, unit: 's' },
          { name: 'Mass (loaded)', value: 3000, unit: 'kg' }
        ]
      },
      {
        name: 'Nozzle (Stage 1)',
        description: 'Submerged flex-seal nozzle with thrust vector control',
        specs: [
          { name: 'Type', value: 'Submerged, flex-seal TVC' },
          { name: 'Expansion Ratio', value: 12 },
          { name: 'TVC Deflection', value: '+-5', unit: 'deg' },
          { name: 'TVC Rate', value: 20, unit: 'deg/s' }
        ]
      },
      {
        name: 'Staging Mechanism',
        description: 'Explosive bolt separation and ullage motors',
        specs: [
          { name: 'Separation Type', value: 'Explosive bolts + linear shaped charge' },
          { name: 'Ullage Motors', value: '4x small solid' },
          { name: 'Separation Velocity', value: 2, unit: 'm/s' },
          { name: 'Staging Altitude', value: '~80', unit: 'km' }
        ]
      },
      {
        name: 'Thermal Protection',
        description: 'Ablative thermal protection for reentry vehicle',
        specs: [
          { name: 'Material', value: 'Carbon-phenolic ablator' },
          { name: 'Max Temperature', value: 2500, unit: 'C' },
          { name: 'Ablation Rate', value: '0.5-1.0', unit: 'mm/s', note: 'At Mach 10 reentry' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Total Impulse', value: '~15', unit: 'MN*s' },
      { metric: 'Burnout Velocity', value: '~4000', unit: 'm/s', context: 'Mach 12 at burnout' },
      { metric: 'Boost Phase Duration', value: 95, unit: 's', context: 'Stage 1 + Stage 2' },
      { metric: 'Launch Mass', value: '~15,000', unit: 'kg' }
    ],
    equations: [
      {
        name: 'Tsiolkovsky Rocket Equation',
        latex: 'delta_V = Isp * g0 * ln(m0 / mf)',
        description: 'Ideal velocity change achievable from propellant mass fraction',
        variables: [
          { symbol: 'delta_V', meaning: 'Velocity change', unit: 'm/s' },
          { symbol: 'Isp', meaning: 'Specific impulse', unit: 's' },
          { symbol: 'g0', meaning: 'Standard gravity', unit: '9.81 m/s^2' },
          { symbol: 'm0', meaning: 'Initial mass (wet)', unit: 'kg' },
          { symbol: 'mf', meaning: 'Final mass (dry)', unit: 'kg' }
        ],
        numericalExample: {
          inputs: { 'Isp_1': '270 s', 'm0_1': '15000 kg', 'mf_1': '6000 kg', 'Isp_2': '285 s', 'm0_2': '5500 kg', 'mf_2': '2500 kg' },
          calculation: 'dV1 = 270*9.81*ln(15000/6000) = 2426 m/s; dV2 = 285*9.81*ln(5500/2500) = 2196 m/s',
          result: 'Total dV ~4622 m/s (vacuum); ~4000 m/s after gravity/drag losses'
        }
      },
      {
        name: 'Thrust Profile',
        latex: 'F(t) = P_chamber * A_throat * C_F',
        description: 'Instantaneous thrust from chamber pressure, throat area, and thrust coefficient',
        variables: [
          { symbol: 'F', meaning: 'Thrust', unit: 'N' },
          { symbol: 'P_chamber', meaning: 'Chamber pressure', unit: 'Pa' },
          { symbol: 'A_throat', meaning: 'Nozzle throat area', unit: 'm^2' },
          { symbol: 'C_F', meaning: 'Thrust coefficient', unit: '' }
        ]
      }
    ],
    operationalNotes: [
      'Solid propellant allows rapid launch — no fueling delays like liquid missiles',
      'TEL provides climate-controlled canister to maintain propellant grain temperature',
      'TVC on first stage provides boost-phase attitude control; fins inactive until atmospheric reentry',
      'Stage separation event causes brief attitude transient — INS compensates automatically'
    ],
    interactionsWith: ['gnc', 'ins']
  },

  // ── 7. Warhead & Fuzing ───────────────────────────────────────────────────
  {
    id: 'warhead-fuze',
    name: 'Warhead & Fuzing',
    category: 'warhead',
    icon: '\u{1F4A5}',
    overview: 'Conventional unitary high-explosive warhead (estimated 500-700 kg) with contact and proximity fuzing. Designed for mission-kill effect against carrier through deck penetration and internal blast damage.',
    components: [
      {
        name: 'Warhead',
        description: 'Unitary high-explosive or semi-armor-piercing warhead',
        specs: [
          { name: 'Type', value: 'Unitary HE blast/fragmentation' },
          { name: 'Weight', value: '500-700', unit: 'kg' },
          { name: 'Explosive Fill', value: 'Comp-B or PBX equivalent' },
          { name: 'Alternative Config', value: 'Submunition dispenser', note: 'Possible variant' }
        ]
      },
      {
        name: 'Fuze System',
        description: 'Multi-mode fuzing for contact and proximity detonation',
        specs: [
          { name: 'Primary Mode', value: 'Contact (crush switch)' },
          { name: 'Secondary Mode', value: 'Proximity (radar altimeter)' },
          { name: 'Backup Mode', value: 'Timed delay' },
          { name: 'Arming Distance', value: '>10', unit: 'km from launch' }
        ]
      },
      {
        name: 'Safe & Arm Device',
        description: 'Mechanical safe-arm mechanism with multiple environmental sensors',
        specs: [
          { name: 'Mechanism', value: 'Rotating shutter' },
          { name: 'G-Switch Threshold', value: 20, unit: 'g', note: 'Must sense launch acceleration' },
          { name: 'Timer', value: 30, unit: 's', note: 'Minimum arm time after launch' },
          { name: 'Spin Detection', value: 'Yes' }
        ]
      },
      {
        name: 'Damage Assessment Model',
        description: 'Terminal effects analysis against carrier targets',
        specs: [
          { name: 'vs Carrier Deck', value: 'Penetrates flight deck + hangar deck' },
          { name: 'Compartment Flooding', value: '2-3 compartments' },
          { name: 'Mission Kill Radius', value: '15-20', unit: 'm', note: 'Direct hit required' },
          { name: 'Sink Probability', value: 'Low per single hit', note: 'Carrier has extensive damage control' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Lethal Radius (vs carrier deck)', value: '15-20', unit: 'm' },
      { metric: 'Penetration Depth (steel)', value: '50-80', unit: 'mm', context: 'At Mach 10 impact' },
      { metric: 'Blast Overpressure (at 10m)', value: '>100', unit: 'psi' },
      { metric: 'P(mission kill) per hit', value: '0.6-0.8', unit: '', context: 'Flight deck destruction' }
    ],
    equations: [
      {
        name: 'Blast Overpressure vs Distance',
        latex: 'P_s = K * W^(1/3) / R',
        description: 'Peak static overpressure from Hopkinson-Cranz scaling law',
        variables: [
          { symbol: 'P_s', meaning: 'Peak static overpressure', unit: 'psi' },
          { symbol: 'K', meaning: 'Explosive constant', unit: 'psi*m/kg^(1/3)' },
          { symbol: 'W', meaning: 'Charge weight (TNT equiv)', unit: 'kg' },
          { symbol: 'R', meaning: 'Distance from detonation', unit: 'm' }
        ]
      },
      {
        name: 'Kinetic Energy Penetration',
        latex: 't_pen = (m * V^2) / (2 * sigma_yield * A)',
        description: 'Simplified penetration depth into steel plate (no fragmentation)',
        variables: [
          { symbol: 't_pen', meaning: 'Penetration depth', unit: 'm' },
          { symbol: 'm', meaning: 'Projectile mass', unit: 'kg' },
          { symbol: 'V', meaning: 'Impact velocity', unit: 'm/s' },
          { symbol: 'sigma_yield', meaning: 'Target yield strength', unit: 'Pa' },
          { symbol: 'A', meaning: 'Contact area', unit: 'm^2' }
        ]
      },
      {
        name: 'Damage Probability',
        latex: 'P_damage = 1 - exp(-pi * R_lethal^2 / (2 * CEP^2))',
        description: 'Probability of lethal damage given CEP and lethal radius',
        variables: [
          { symbol: 'P_damage', meaning: 'Damage probability', unit: '' },
          { symbol: 'R_lethal', meaning: 'Lethal radius', unit: 'm' },
          { symbol: 'CEP', meaning: 'Circular error probable', unit: 'm' }
        ],
        numericalExample: {
          inputs: { 'R_lethal': '20 m (mission kill)', 'CEP': '30 m (DF-21D)' },
          calculation: 'P = 1 - exp(-pi * 400 / (2 * 900)) = 1 - exp(-0.698)',
          result: 'P_damage = 0.50 per hit (mission kill)'
        }
      }
    ],
    operationalNotes: [
      'Single conventional warhead may not sink a Nimitz-class carrier but can achieve mission kill by destroying flight deck',
      'Nuclear variant exists but conventional assumed for anti-ship role to avoid escalation',
      'Impact velocity of Mach 10 adds significant kinetic energy effect beyond explosive yield',
      'Submunition variant would spread damage but reduce penetration — tradeoff depends on target hardening'
    ],
    interactionsWith: ['gnc', 'radar-seeker']
  }
];


// ═══════════════════════════════════════════════════════════════════════════════
// DF-26 SUBSYSTEMS
// ═══════════════════════════════════════════════════════════════════════════════

export const DF26_SUBSYSTEMS: SubsystemDetail[] = [
  // ── 1. INS / IMU ──────────────────────────────────────────────────────────
  {
    id: 'ins',
    name: 'Inertial Navigation System',
    category: 'navigation',
    icon: '\u{1F9ED}',
    overview: 'High-performance fiber-optic gyroscope (FOG) based INS optimized for extended midcourse flight at IRBM ranges. Longer flight time (~25 min) demands superior gyro stability compared to DF-21D.',
    components: [
      {
        name: 'Fiber-Optic Gyroscope Triad',
        description: 'Three-axis FOG package for improved long-duration stability',
        specs: [
          { name: 'Type', value: 'Fiber-Optic Gyroscope (FOG)' },
          { name: 'Bias Instability', value: 0.001, unit: 'deg/hr', note: 'Superior to DF-21D RLG' },
          { name: 'Angle Random Walk', value: 0.001, unit: 'deg/sqrt(hr)' },
          { name: 'Scale Factor Stability', value: 1, unit: 'ppm' },
          { name: 'Bandwidth', value: 500, unit: 'Hz' },
          { name: 'Operating Temp', value: '-40 to +71', unit: 'C' }
        ]
      },
      {
        name: 'Accelerometer Triad',
        description: 'High-performance quartz flexure accelerometers',
        specs: [
          { name: 'Bias Stability', value: 5, unit: 'micro-g' },
          { name: 'Scale Factor', value: 2, unit: 'ppm' },
          { name: 'Cross-Axis Sensitivity', value: 2, unit: 'micro-g/g' },
          { name: 'Range', value: '+-60', unit: 'g' }
        ]
      },
      {
        name: 'Navigation Computer',
        description: 'Extended-range navigation processor with higher-order gravity model',
        specs: [
          { name: 'Update Rate', value: 400, unit: 'Hz' },
          { name: 'Coordinate Frame', value: 'WGS-84 ECEF' },
          { name: 'Gravity Model', value: 'EGM2008 (36x36)' },
          { name: 'Processor', value: 'Rad-hard FPGA + DSP' }
        ]
      },
      {
        name: 'Temperature Compensation Module',
        description: 'Precision thermal control with real-time calibration',
        specs: [
          { name: 'Control Method', value: 'Active Peltier + insulation' },
          { name: 'Stability', value: '+-0.05', unit: 'C' },
          { name: 'Compensation Model Order', value: '5th order polynomial' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'CEP at 25 min (free inertial)', value: '300-500', unit: 'm', context: 'Extended flight, no aiding' },
      { metric: 'CEP with stellar correction', value: '30-60', unit: 'm', context: 'Multiple stellar fixes' },
      { metric: 'Velocity accuracy', value: 0.1, unit: 'm/s', context: 'After alignment' },
      { metric: 'Heading accuracy', value: 0.02, unit: 'deg' }
    ],
    equations: [
      {
        name: 'INS Error Propagation (Extended Range)',
        latex: 'sigma_pos(t) = sigma_gyro * R_e * t + 0.5 * sigma_accel * t^2 + Schuler_osc(t)',
        description: 'Position error growth including Schuler oscillation term for extended flight',
        variables: [
          { symbol: 'sigma_pos', meaning: 'Position error', unit: 'm' },
          { symbol: 'sigma_gyro', meaning: 'Gyro drift rate', unit: 'rad/s' },
          { symbol: 'R_e', meaning: 'Earth radius', unit: 'm' },
          { symbol: 'sigma_accel', meaning: 'Accelerometer bias', unit: 'm/s^2' },
          { symbol: 'Schuler_osc', meaning: 'Schuler period oscillation (~84 min)', unit: 'm' }
        ]
      }
    ],
    pseudocode: [
      {
        title: 'Strapdown INS Mechanization (High-Rate)',
        description: 'Same core loop as DF-21D but at 400 Hz with higher-order compensation terms for extended flight',
        lines: [
          'LOOP at 400 Hz:',
          '  omega = read_FOG_triad()',
          '  f_body = read_accel_triad()',
          '  // Coning compensation for FOG',
          '  omega_comp = omega + coning_correction(omega, omega_prev)',
          '  q = q * quaternion_from_rotvec(omega_comp * dt)',
          '  q = normalize(q)',
          '  C_bn = dcm_from_quaternion(q)',
          '  f_nav = C_bn * f_body',
          '  // High-order gravity model',
          '  g_nav = EGM2008_gravity(position, altitude)',
          '  a_nav = f_nav - g_nav',
          '  velocity += 0.5 * (a_nav + a_nav_prev) * dt',
          '  position += 0.5 * (velocity + velocity_prev) * dt'
        ]
      }
    ],
    operationalNotes: [
      'FOG selected over RLG for DF-26 due to superior long-term stability at 25+ minute flight times',
      'Higher-order gravity model (EGM2008) needed for IRBM ranges where gravity anomalies become significant',
      'Multiple stellar fixes during extended midcourse phase are essential for maintaining accuracy',
      'Coning compensation algorithm critical for FOG during high-vibration boost phase'
    ],
    interactionsWith: ['stellar-nav', 'gnc', 'beidou-datalink']
  },

  // ── 2. Radar Seeker ───────────────────────────────────────────────────────
  {
    id: 'radar-seeker',
    name: 'Radar Seeker',
    category: 'seeker',
    icon: '\u{1F4E1}',
    overview: 'Active electronically scanned array (AESA) radar seeker with wider field of view than DF-21D to compensate for greater position uncertainty at 4000 km range. Digital beamforming enables simultaneous multi-target tracking.',
    components: [
      {
        name: 'Antenna Assembly',
        description: 'Active electronically scanned array with digital beamforming',
        specs: [
          { name: 'Type', value: 'AESA (Active Phased Array)' },
          { name: 'Element Count', value: 256 },
          { name: 'Aperture', value: '0.4 x 0.4', unit: 'm' },
          { name: 'Beamwidth (3dB)', value: 3.0, unit: 'deg' },
          { name: 'Sidelobe Level', value: -30, unit: 'dB' },
          { name: 'Electronic Scan', value: '+-60', unit: 'deg' },
          { name: 'Scan Rate', value: '1000+', unit: 'beams/s' }
        ]
      },
      {
        name: 'RF Transmitter (Distributed)',
        description: 'GaN T/R modules distributed across array',
        specs: [
          { name: 'Frequency Band', value: 'X-band (9-11 GHz)' },
          { name: 'Peak Power (total)', value: 1000, unit: 'W' },
          { name: 'Average Power', value: 200, unit: 'W' },
          { name: 'Bandwidth', value: 100, unit: 'MHz' }
        ]
      },
      {
        name: 'Waveform Generator',
        description: 'Programmable waveform with multiple chirp modes',
        specs: [
          { name: 'Chirp Type', value: 'LFM + NLFM selectable' },
          { name: 'PRF', value: '5000-30000', unit: 'Hz' },
          { name: 'Pulse Width', value: '0.5-20', unit: 'microsec' },
          { name: 'Duty Cycle', value: 20, unit: '%' },
          { name: 'Range Resolution', value: 1.5, unit: 'm' }
        ]
      },
      {
        name: 'Signal Processor',
        description: 'Multi-channel digital signal processor',
        specs: [
          { name: 'Detection Algorithm', value: 'OS-CFAR (Ordered Statistic)' },
          { name: 'Clutter Model', value: 'Compound Gaussian' },
          { name: 'Simultaneous Beams', value: 4 },
          { name: 'Doppler Bins', value: 512 },
          { name: 'Range Bins', value: 1024 }
        ]
      },
      {
        name: 'Track Gate',
        description: 'Extended Kalman filter with target classification',
        specs: [
          { name: 'Filter Type', value: 'Extended Kalman Filter' },
          { name: 'Update Rate', value: 50, unit: 'Hz' },
          { name: 'Multi-Target', value: 'Up to 8 tracks' },
          { name: 'Track Accuracy', value: '3-8', unit: 'm' }
        ]
      },
      {
        name: 'ECCM Module',
        description: 'Advanced ECCM suite for AESA',
        specs: [
          { name: 'Home-on-Jam', value: 'Yes (angle only or angle+range)' },
          { name: 'Sidelobe Blanking', value: 'Yes (adaptive)' },
          { name: 'Frequency Agility', value: '2 GHz hop bandwidth' },
          { name: 'LPI Mode', value: 'Power management + spread spectrum' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Acquisition Range vs Carrier', value: '70-100', unit: 'km', context: 'AESA advantage over dish' },
      { metric: '3dB Beamwidth', value: 3.0, unit: 'deg' },
      { metric: 'Min Detectable RCS (at 30 km)', value: 50, unit: 'm^2' },
      { metric: 'ECCM Effectiveness', value: 'High', unit: '', context: 'AESA provides significant ECCM advantage' }
    ],
    equations: [
      {
        name: 'AESA Radar Range Equation',
        latex: 'R_max = (N_elem * P_elem * G_elem^2 * lambda^2 * sigma / ((4*pi)^3 * k*T*B * SNR_min))^(1/4)',
        description: 'Maximum range for distributed AESA with N transmit/receive elements',
        variables: [
          { symbol: 'N_elem', meaning: 'Number of T/R elements', unit: '' },
          { symbol: 'P_elem', meaning: 'Power per element', unit: 'W' },
          { symbol: 'G_elem', meaning: 'Element gain', unit: 'linear' },
          { symbol: 'lambda', meaning: 'Wavelength', unit: 'm' },
          { symbol: 'sigma', meaning: 'Target RCS', unit: 'm^2' }
        ]
      }
    ],
    operationalNotes: [
      'AESA provides wider instantaneous FOV critical for DF-26 where target uncertainty is >20 km at 4000 km range',
      'Electronic scanning enables rapid search pattern — covers 30 km uncertainty circle in <5 seconds',
      'Multi-target capability allows discrimination of carrier from escorts within same scan',
      'AESA conformal radome better suited to Mach 18 reentry thermal environment than mechanical dish'
    ],
    interactionsWith: ['gnc', 'warhead-fuze']
  },

  // ── 3. Guidance & Control ─────────────────────────────────────────────────
  {
    id: 'gnc',
    name: 'Guidance & Control',
    category: 'guidance',
    icon: '\u{1F3AF}',
    overview: 'Maneuvering reentry vehicle (MaRV) with combined aerodynamic fin control and reaction control system (RCS) thrusters. Extended midcourse guidance with multiple correction opportunities. Terminal guidance uses proportional navigation with target acceleration estimation.',
    components: [
      {
        name: 'Guidance Computer',
        description: 'Tri-mode guidance: boost, midcourse shaping, and terminal PN',
        specs: [
          { name: 'Midcourse Law', value: 'Energy-optimal trajectory shaping' },
          { name: 'Terminal Law', value: 'APN with target maneuver estimation' },
          { name: 'Navigation Constant N', value: '4-5' },
          { name: 'Guidance Update Rate', value: 100, unit: 'Hz' }
        ]
      },
      {
        name: 'Control Actuators (Aerodynamic)',
        description: 'Grid fins for high-Mach aerodynamic control',
        specs: [
          { name: 'Fin Type', value: 'Grid fins (lattice)' },
          { name: 'Max Deflection', value: '+-20', unit: 'deg' },
          { name: 'Rate Limit', value: 200, unit: 'deg/s' },
          { name: 'Bandwidth', value: 30, unit: 'Hz' },
          { name: 'Effective Mach Range', value: '2-18' }
        ]
      },
      {
        name: 'Reaction Control System',
        description: 'Cold-gas RCS thrusters for exoatmospheric attitude control',
        specs: [
          { name: 'Thruster Type', value: 'Cold-gas (nitrogen)' },
          { name: 'Thrust per Jet', value: 50, unit: 'N' },
          { name: 'Number of Jets', value: 8, note: '4 clusters of 2' },
          { name: 'Total Impulse', value: 500, unit: 'N*s' }
        ]
      },
      {
        name: 'Autopilot',
        description: 'Hybrid aero/RCS autopilot with smooth blending',
        specs: [
          { name: 'Architecture', value: 'Hybrid aero + RCS with blending' },
          { name: 'RCS-to-Aero Handover', value: '~60 km altitude' },
          { name: 'Phase Margin', value: '>40', unit: 'deg' },
          { name: 'Gain Margin', value: '>6', unit: 'dB' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Divert Capability (terminal)', value: '10-15', unit: 'km', context: '15 sec terminal + RCS' },
      { metric: 'Response Time (90% step)', value: 0.15, unit: 's' },
      { metric: 'Max Lateral Acceleration', value: 20, unit: 'g', context: 'At Mach 10, 20 km alt' },
      { metric: 'Exoatmospheric Control', value: 'Full 3-axis via RCS', unit: '' }
    ],
    equations: [
      {
        name: 'Augmented PN with Target Acceleration',
        latex: 'a_c = N * V_c * lambda_dot + 0.5 * N * a_T_est',
        description: 'Terminal guidance with estimated target acceleration term for maneuvering carrier',
        variables: [
          { symbol: 'a_c', meaning: 'Commanded acceleration', unit: 'm/s^2' },
          { symbol: 'N', meaning: 'Navigation constant (4-5)', unit: '' },
          { symbol: 'V_c', meaning: 'Closing velocity', unit: 'm/s' },
          { symbol: 'lambda_dot', meaning: 'LOS rate', unit: 'rad/s' },
          { symbol: 'a_T_est', meaning: 'Estimated target accel', unit: 'm/s^2' }
        ]
      }
    ],
    pseudocode: [
      {
        title: 'Hybrid RCS/Aero Control Loop',
        description: 'Blends RCS and aerodynamic control based on dynamic pressure',
        lines: [
          'LOOP at 100 Hz:',
          '  q_dyn = 0.5 * rho(altitude) * V^2',
          '  IF q_dyn < Q_MIN_AERO:',
          '    // Pure RCS control (exoatmospheric)',
          '    cmd = compute_RCS_jets(a_cmd, attitude)',
          '    fire_RCS(cmd)',
          '  ELIF q_dyn < Q_BLEND:',
          '    // Blended regime',
          '    alpha = (q_dyn - Q_MIN_AERO) / (Q_BLEND - Q_MIN_AERO)',
          '    cmd_aero = compute_fin_deflection(a_cmd)',
          '    cmd_rcs = compute_RCS_jets(a_cmd * (1 - alpha))',
          '    actuate_fins(cmd_aero)',
          '    fire_RCS(cmd_rcs)',
          '  ELSE:',
          '    // Pure aerodynamic control',
          '    cmd_aero = compute_fin_deflection(a_cmd)',
          '    actuate_fins(cmd_aero)'
        ]
      }
    ],
    operationalNotes: [
      'MaRV capability makes DF-26 harder to intercept than purely ballistic DF-21D RV',
      'Grid fins effective across wide Mach range (2-18) — maintain control authority during reentry deceleration',
      'RCS provides exoatmospheric divert for gross trajectory corrections before atmospheric reentry',
      'Dual-capable (conventional/nuclear) requires different fuzing and guidance modes selectable pre-launch'
    ],
    interactionsWith: ['ins', 'radar-seeker', 'warhead-fuze']
  },

  // ── 4. Stellar Navigation ─────────────────────────────────────────────────
  {
    id: 'stellar-nav',
    name: 'Stellar Navigation',
    category: 'navigation',
    icon: '\u{2B50}',
    overview: 'Most sophisticated stellar navigation suite in the ASBM family. Extended midcourse at IRBM range provides longer observation window for multiple stellar fixes, achieving sub-arcminute attitude accuracy and corresponding position corrections.',
    components: [
      {
        name: 'Star Tracker',
        description: 'High-sensitivity CMOS focal plane star tracker',
        specs: [
          { name: 'Sensor Type', value: 'CMOS active pixel sensor' },
          { name: 'FOV', value: '10x10', unit: 'deg' },
          { name: 'Accuracy (cross-boresight)', value: 2, unit: 'arcsec' },
          { name: 'Star Catalog Size', value: 10000, unit: 'stars' },
          { name: 'Limiting Magnitude', value: 7.0 },
          { name: 'Update Rate', value: 5, unit: 'Hz' }
        ]
      },
      {
        name: 'Star Identification Algorithm',
        description: 'Advanced pattern matching with geometric voting',
        specs: [
          { name: 'Algorithm', value: 'Geometric voting + pyramid match' },
          { name: 'Lost-in-Space', value: 'Yes' },
          { name: 'ID Time', value: '<1', unit: 's' },
          { name: 'Success Rate', value: '>99.5', unit: '%' }
        ]
      },
      {
        name: 'INS Coupling',
        description: 'Tightly-coupled Kalman filter with continuous stellar updates',
        specs: [
          { name: 'Coupling Type', value: 'Tightly-coupled' },
          { name: 'Measurement Noise', value: 2, unit: 'arcsec' },
          { name: 'Update Rate', value: '3-5', unit: 'fixes during midcourse' },
          { name: 'States Estimated', value: 15, note: 'pos/vel/att + gyro/accel biases' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Attitude Accuracy', value: 2, unit: 'arcsec', context: 'Best in ASBM family' },
      { metric: 'Position Correction', value: '100-400', unit: 'm', context: 'Corrects 25-min INS drift' },
      { metric: 'Update Latency', value: 1.5, unit: 's' },
      { metric: 'Number of Fixes', value: '3-5', unit: 'per flight', context: 'Extended midcourse window' }
    ],
    equations: [
      {
        name: 'Multi-Star Fix Accuracy',
        latex: 'sigma_att = sigma_star / sqrt(N_stars)',
        description: 'Attitude accuracy improves with number of simultaneously observed stars',
        variables: [
          { symbol: 'sigma_att', meaning: 'Attitude error (1-sigma)', unit: 'arcsec' },
          { symbol: 'sigma_star', meaning: 'Single-star measurement noise', unit: 'arcsec' },
          { symbol: 'N_stars', meaning: 'Number of stars observed', unit: '' }
        ],
        numericalExample: {
          inputs: { 'sigma_star': '5 arcsec', 'N_stars': 6 },
          calculation: 'sigma_att = 5 / sqrt(6) = 2.04 arcsec',
          result: '~2 arcsec attitude accuracy -> ~60 m position correction at Earth surface'
        }
      }
    ],
    operationalNotes: [
      'DF-26 has most capable stellar nav due to longest midcourse phase (~15 min exoatmospheric)',
      'Extended observation window allows 3-5 stellar fixes with progressive INS calibration',
      'Tightly-coupled Kalman filter also estimates and removes gyro/accel biases in-flight',
      'Critical for achieving 30-50m CEP at 4000 km range — without stellar, CEP degrades to >500m'
    ],
    interactionsWith: ['ins']
  },

  // ── 5. BeiDou Datalink ────────────────────────────────────────────────────
  {
    id: 'beidou-datalink',
    name: 'BeiDou Datalink',
    category: 'datalink',
    icon: '\u{1F4F6}',
    overview: 'Enhanced BeiDou-3 receiver with relay satellite datalink capability for over-the-horizon target updates. Extended range operation at 4000 km may require relay satellite for midcourse updates if direct ground-to-missile link is unavailable.',
    components: [
      {
        name: 'BeiDou Receiver',
        description: 'Multi-frequency BeiDou-3 receiver with enhanced sensitivity',
        specs: [
          { name: 'Frequencies', value: 'B1C, B2a, B2b, B3I' },
          { name: 'Channels', value: 36 },
          { name: 'Acquisition Time', value: '<5', unit: 's' },
          { name: 'Position Accuracy', value: '<0.5', unit: 'm' }
        ]
      },
      {
        name: 'Relay Satellite Link',
        description: 'Tianlian relay satellite datalink for over-the-horizon C2',
        specs: [
          { name: 'Relay Satellite', value: 'Tianlian series' },
          { name: 'Data Rate', value: 2400, unit: 'bps' },
          { name: 'Encryption', value: 'Military-grade' },
          { name: 'Coverage', value: 'Asia-Pacific GEO footprint' }
        ]
      },
      {
        name: 'Anti-Jam Module',
        description: 'Enhanced anti-jam for contested environment',
        specs: [
          { name: 'Nulling Antennas', value: '4-element CRPA' },
          { name: 'Nulling Capability', value: '3 independent nulls' },
          { name: 'Jam Resistance', value: '40-50', unit: 'dB J/S' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Position Accuracy', value: '<0.5', unit: 'm' },
      { metric: 'Relay Update Rate', value: '1 per 30s', unit: '', context: 'Bandwidth limited' },
      { metric: 'Jam Resistance', value: '40-50', unit: 'dB' },
      { metric: 'Relay Availability', value: '~85', unit: '%', context: 'GEO satellite coverage' }
    ],
    operationalNotes: [
      'Relay satellite datalink critical for updating target position at 4000 km range where direct ground link may be unavailable',
      'Tianlian constellation provides near-continuous coverage over Asia-Pacific from GEO orbit',
      'Enhanced CRPA anti-jam enables reception in more contested electromagnetic environments',
      'Datalink denied fallback relies on INS+stellar — CEP degrades but remains functional'
    ],
    interactionsWith: ['ins', 'gnc']
  },

  // ── 6. Propulsion ─────────────────────────────────────────────────────────
  {
    id: 'propulsion',
    name: 'Propulsion',
    category: 'propulsion',
    icon: '\u{1F680}',
    overview: 'Two-stage solid-propellant IRBM motor with higher total impulse than DF-21D for 4000 km range. Larger first stage provides higher burnout velocity reaching Mach 18 at reentry.',
    components: [
      {
        name: 'First Stage Motor',
        description: 'High-energy solid motor for IRBM range',
        specs: [
          { name: 'Type', value: 'Solid propellant' },
          { name: 'Propellant', value: 'NEPE (nitrate ester plasticized polyether)' },
          { name: 'Thrust (vacuum)', value: 700, unit: 'kN' },
          { name: 'Burn Time', value: 65, unit: 's' },
          { name: 'Specific Impulse (vac)', value: 280, unit: 's' },
          { name: 'Mass (loaded)', value: 18000, unit: 'kg' }
        ]
      },
      {
        name: 'Second Stage Motor',
        description: 'Upper stage with high mass fraction',
        specs: [
          { name: 'Type', value: 'Solid propellant' },
          { name: 'Propellant', value: 'NEPE' },
          { name: 'Thrust (vacuum)', value: 200, unit: 'kN' },
          { name: 'Burn Time', value: 50, unit: 's' },
          { name: 'Specific Impulse (vac)', value: 295, unit: 's' },
          { name: 'Mass (loaded)', value: 6000, unit: 'kg' }
        ]
      },
      {
        name: 'Nozzle (Stage 1)',
        description: 'Flexible seal nozzle with TVC',
        specs: [
          { name: 'Type', value: 'Flex-seal TVC' },
          { name: 'Expansion Ratio', value: 15 },
          { name: 'TVC Deflection', value: '+-6', unit: 'deg' },
          { name: 'Material', value: 'Carbon-carbon throat insert' }
        ]
      },
      {
        name: 'Thermal Protection',
        description: 'Enhanced TPS for Mach 18 reentry',
        specs: [
          { name: 'Material', value: 'Carbon-carbon + UHTC nose tip' },
          { name: 'Max Temperature', value: 3000, unit: 'C' },
          { name: 'Ablation Rate', value: '1.0-2.0', unit: 'mm/s', note: 'Mach 18 reentry' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Total Impulse', value: '~30', unit: 'MN*s' },
      { metric: 'Burnout Velocity', value: '~6000', unit: 'm/s', context: 'Mach 18 at reentry' },
      { metric: 'Boost Phase Duration', value: 115, unit: 's' },
      { metric: 'Launch Mass', value: '~30,000', unit: 'kg' }
    ],
    equations: [
      {
        name: 'Tsiolkovsky Rocket Equation (2-stage)',
        latex: 'delta_V_total = Isp_1 * g0 * ln(m0_1/mf_1) + Isp_2 * g0 * ln(m0_2/mf_2)',
        description: 'Total velocity change from two-stage solid rocket',
        variables: [
          { symbol: 'Isp_1', meaning: 'Stage 1 specific impulse', unit: 's' },
          { symbol: 'Isp_2', meaning: 'Stage 2 specific impulse', unit: 's' },
          { symbol: 'm0/mf', meaning: 'Initial/final mass per stage', unit: 'kg' }
        ],
        numericalExample: {
          inputs: { 'Isp_1': '280 s', 'm0_1': '30000 kg', 'mf_1': '12000 kg', 'Isp_2': '295 s', 'm0_2': '11000 kg', 'mf_2': '5000 kg' },
          calculation: 'dV1 = 280*9.81*ln(30000/12000) = 2515; dV2 = 295*9.81*ln(11000/5000) = 2279',
          result: 'Total dV ~4794 m/s vacuum; ~6000 m/s effective with Earth rotation assist'
        }
      }
    ],
    operationalNotes: [
      'NEPE propellant provides higher energy density than HTPB used in DF-21D',
      'Larger missile requires 16-wheel TEL for road mobility',
      'UHTC (ultra-high temperature ceramic) nose tip required for Mach 18 reentry survivability',
      'Hot reload capability — TEL can re-arm in field within hours using crane vehicle'
    ],
    interactionsWith: ['gnc', 'ins']
  },

  // ── 7. Warhead & Fuzing ───────────────────────────────────────────────────
  {
    id: 'warhead-fuze',
    name: 'Warhead & Fuzing',
    category: 'warhead',
    icon: '\u{1F4A5}',
    overview: 'Dual-capable warhead system — can carry conventional HE (estimated 1000-1200 kg) or nuclear warhead. Anti-ship role assumed conventional. Higher kinetic energy than DF-21D due to Mach 18 impact velocity.',
    components: [
      {
        name: 'Warhead (Conventional)',
        description: 'Large unitary or penetrator warhead',
        specs: [
          { name: 'Type', value: 'Unitary penetrator + blast' },
          { name: 'Weight', value: '1000-1200', unit: 'kg' },
          { name: 'Explosive Fill', value: 'PBX-class insensitive munition' },
          { name: 'Penetrator', value: 'Hardened steel case' }
        ]
      },
      {
        name: 'Warhead (Nuclear Option)',
        description: 'Nuclear warhead for strategic strike role',
        specs: [
          { name: 'Type', value: 'Thermonuclear' },
          { name: 'Yield', value: '200-500', unit: 'kT', note: 'ESTIMATED' },
          { name: 'Role', value: 'Strategic deterrent / Guam strike' }
        ]
      },
      {
        name: 'Fuze System',
        description: 'Multi-mode fuzing with nuclear safety features',
        specs: [
          { name: 'Conventional Modes', value: 'Contact + Proximity + Delay' },
          { name: 'Nuclear S&A', value: 'Strong-link / Weak-link' },
          { name: 'PAL', value: 'Permissive Action Link', note: 'Nuclear only' }
        ]
      },
      {
        name: 'Damage Assessment Model',
        description: 'Effects modeling for conventional anti-ship strike',
        specs: [
          { name: 'KE at Impact', value: '~18 GJ', note: 'Mach 18, 1200 kg' },
          { name: 'vs Carrier Deck', value: 'Full penetration through multiple decks' },
          { name: 'P(mission kill)', value: '0.7-0.9', unit: '', note: 'Per hit, conventional' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Kinetic Energy at Impact', value: '~18', unit: 'GJ', context: 'Mach 18 × 1200 kg' },
      { metric: 'Penetration Depth', value: '100-150', unit: 'mm steel', context: 'Mach 18 impact' },
      { metric: 'P(mission kill) per hit', value: '0.7-0.9', unit: '' },
      { metric: 'Lethal Radius', value: '20-30', unit: 'm', context: 'Combined KE + HE effect' }
    ],
    equations: [
      {
        name: 'Kinetic Energy at Impact',
        latex: 'KE = 0.5 * m * V^2',
        description: 'Kinetic energy of warhead at Mach 18 impact',
        variables: [
          { symbol: 'KE', meaning: 'Kinetic energy', unit: 'J' },
          { symbol: 'm', meaning: 'Warhead mass', unit: 'kg' },
          { symbol: 'V', meaning: 'Impact velocity', unit: 'm/s' }
        ],
        numericalExample: {
          inputs: { 'm': '1200 kg', 'V': '5500 m/s (Mach 18 at altitude)' },
          calculation: 'KE = 0.5 * 1200 * 5500^2 = 1.815e10 J',
          result: '~18 GJ — equivalent to ~4.3 tons of TNT in kinetic energy alone'
        }
      }
    ],
    operationalNotes: [
      'Dual-capable nature creates ambiguity for adversary — cannot distinguish nuclear from conventional before impact',
      'This ambiguity is a strategic concern: adversary may assume nuclear launch and escalate',
      'Conventional anti-ship strike at Mach 18 delivers devastating kinetic energy even without warhead detonation',
      'Nuclear option primarily for Guam/fixed-base strike role — anti-ship role assumed conventional'
    ],
    interactionsWith: ['gnc', 'radar-seeker']
  }
];


// ═══════════════════════════════════════════════════════════════════════════════
// DF-17 HGV SUBSYSTEMS
// ═══════════════════════════════════════════════════════════════════════════════

export const DF17_SUBSYSTEMS: SubsystemDetail[] = [
  // ── 1. INS / IMU ──────────────────────────────────────────────────────────
  {
    id: 'ins',
    name: 'Inertial Navigation System',
    category: 'navigation',
    icon: '\u{1F9ED}',
    overview: 'Hardened INS designed for sustained hypersonic glide environment. Must maintain accuracy through plasma sheath effects, extreme thermal gradients, and prolonged high-g maneuvering during glide phase. Uses hemispherical resonator gyroscope (HRG) for vibration resilience.',
    components: [
      {
        name: 'Hemispherical Resonator Gyroscope Triad',
        description: 'HRG package chosen for extreme vibration and thermal resilience in hypersonic environment',
        specs: [
          { name: 'Type', value: 'Hemispherical Resonator Gyroscope (HRG)' },
          { name: 'Bias Instability', value: 0.001, unit: 'deg/hr' },
          { name: 'Angle Random Walk', value: 0.001, unit: 'deg/sqrt(hr)' },
          { name: 'Scale Factor Stability', value: 1, unit: 'ppm' },
          { name: 'Vibration Tolerance', value: '20g RMS', note: 'Hypersonic flight regime' },
          { name: 'Operating Temp', value: '-40 to +85', unit: 'C', note: 'Extended for thermal soak' }
        ]
      },
      {
        name: 'Accelerometer Triad',
        description: 'High-range MEMS/quartz accelerometers for sustained g-loading during glide',
        specs: [
          { name: 'Bias Stability', value: 5, unit: 'micro-g' },
          { name: 'Scale Factor', value: 2, unit: 'ppm' },
          { name: 'Range', value: '+-100', unit: 'g', note: 'Higher range for pull-up maneuver' }
        ]
      },
      {
        name: 'Navigation Computer',
        description: 'Hypersonic-optimized processor with plasma sheath atmospheric model',
        specs: [
          { name: 'Update Rate', value: 400, unit: 'Hz' },
          { name: 'Atmospheric Model', value: 'Hypersonic rarefied + continuum' },
          { name: 'Gravity Model', value: 'EGM2008 (50x50)' },
          { name: 'Thermal Compensation', value: 'Real-time from embedded sensors' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'CEP at 10 min (glide phase)', value: '100-200', unit: 'm', context: 'Degraded by plasma/vibration' },
      { metric: 'CEP with datalink correction', value: '20-50', unit: 'm' },
      { metric: 'Velocity accuracy', value: 0.5, unit: 'm/s', context: 'Degraded in plasma sheath' },
      { metric: 'Attitude accuracy', value: 0.1, unit: 'deg', context: 'During maneuvering' }
    ],
    equations: [
      {
        name: 'Plasma Sheath INS Degradation',
        latex: 'sigma_plasma = sigma_nominal * (1 + k_plasma * ne * L_path)',
        description: 'INS accuracy degradation due to plasma sheath effects on gyro/accel performance',
        variables: [
          { symbol: 'sigma_plasma', meaning: 'Degraded position error', unit: 'm' },
          { symbol: 'sigma_nominal', meaning: 'Nominal error without plasma', unit: 'm' },
          { symbol: 'k_plasma', meaning: 'Plasma coupling factor', unit: 'm^2' },
          { symbol: 'ne', meaning: 'Electron density in sheath', unit: 'm^-3' },
          { symbol: 'L_path', meaning: 'Path length through plasma', unit: 'm' }
        ]
      }
    ],
    operationalNotes: [
      'HRG chosen over RLG/FOG for superior vibration resilience in sustained hypersonic flight',
      'Plasma sheath at Mach 10+ creates electromagnetic blackout — GPS/BeiDou signals attenuated or blocked',
      'Thermal gradients across the vehicle cause differential expansion affecting sensor alignment',
      'INS must carry navigation through entire glide phase (~8 min) if datalink unavailable due to plasma',
      'Pull-up maneuver subjects sensors to 10-15g — accelerometer range sized accordingly'
    ],
    interactionsWith: ['beidou-datalink', 'gnc']
  },

  // ── 2. Radar Seeker ───────────────────────────────────────────────────────
  {
    id: 'radar-seeker',
    name: 'Radar Seeker',
    category: 'seeker',
    icon: '\u{1F4E1}',
    overview: 'Conformal AESA radar seeker hardened for hypersonic environment. Flush-mounted aperture survives Mach 10+ thermal loads. Seeker must operate through or after plasma sheath dissipation during terminal deceleration/pull-up maneuver.',
    components: [
      {
        name: 'Antenna Assembly',
        description: 'Conformal AESA with thermal-resistant radome',
        specs: [
          { name: 'Type', value: 'Conformal AESA (flush-mounted)' },
          { name: 'Element Count', value: 128, note: 'Compact for HGV nosecone' },
          { name: 'Aperture', value: '0.3 x 0.3', unit: 'm' },
          { name: 'Beamwidth (3dB)', value: 5.0, unit: 'deg' },
          { name: 'Electronic Scan', value: '+-45', unit: 'deg' },
          { name: 'Radome Material', value: 'Silicon nitride (Si3N4)', note: 'Withstands 2000C' }
        ]
      },
      {
        name: 'RF Transmitter',
        description: 'GaN T/R modules rated for elevated temperature operation',
        specs: [
          { name: 'Frequency Band', value: 'Ka-band (35 GHz)', note: 'Higher frequency for compact aperture' },
          { name: 'Peak Power (total)', value: 200, unit: 'W' },
          { name: 'Average Power', value: 50, unit: 'W' },
          { name: 'Bandwidth', value: 500, unit: 'MHz', note: 'Fine range resolution' }
        ]
      },
      {
        name: 'Signal Processor',
        description: 'Compact processor with plasma-adapted detection algorithms',
        specs: [
          { name: 'Detection Algorithm', value: 'Adaptive CFAR' },
          { name: 'Plasma Compensation', value: 'Signal attenuation model', note: 'Adjusts threshold dynamically' },
          { name: 'Range Resolution', value: 0.3, unit: 'm' },
          { name: 'Doppler Resolution', value: 50, unit: 'Hz' }
        ]
      },
      {
        name: 'ECCM Module',
        description: 'Ka-band ECCM with LPI operation',
        specs: [
          { name: 'Home-on-Jam', value: 'Yes' },
          { name: 'LPI Mode', value: 'Low-power spread spectrum' },
          { name: 'Frequency Agility', value: '+-1 GHz' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Acquisition Range vs Carrier', value: '30-50', unit: 'km', context: 'Smaller aperture than DF-26' },
      { metric: '3dB Beamwidth', value: 5.0, unit: 'deg' },
      { metric: 'Range Resolution', value: 0.3, unit: 'm', context: 'Ka-band advantage' },
      { metric: 'Seeker Activation Altitude', value: '20-30', unit: 'km', context: 'After pull-up, plasma thinning' }
    ],
    equations: [
      {
        name: 'Plasma Sheath RF Attenuation',
        latex: 'L_plasma = 8.686 * (omega_p^2 * nu * L) / (c * (omega^2 + nu^2))',
        description: 'RF signal attenuation through plasma sheath — determines when seeker can activate',
        variables: [
          { symbol: 'L_plasma', meaning: 'Attenuation through plasma', unit: 'dB' },
          { symbol: 'omega_p', meaning: 'Plasma frequency', unit: 'rad/s' },
          { symbol: 'nu', meaning: 'Collision frequency', unit: 'Hz' },
          { symbol: 'omega', meaning: 'RF carrier frequency', unit: 'rad/s' },
          { symbol: 'L', meaning: 'Sheath thickness', unit: 'm' }
        ]
      }
    ],
    operationalNotes: [
      'Ka-band chosen for HGV: smaller aperture, finer resolution, but higher atmospheric attenuation',
      'Seeker cannot operate through dense plasma sheath at Mach 10+ — activates after pull-up maneuver decelerates vehicle',
      'Conformal aperture does not protrude from vehicle surface — critical for aerothermal survivability',
      'Si3N4 radome maintains acceptable RF transparency at 2000C but with ~3 dB insertion loss',
      'Short terminal engagement time (~10 sec after seeker activation) demands rapid acquisition'
    ],
    interactionsWith: ['gnc', 'warhead-fuze']
  },

  // ── 3. Guidance & Control ─────────────────────────────────────────────────
  {
    id: 'gnc',
    name: 'Guidance & Control',
    category: 'guidance',
    icon: '\u{1F3AF}',
    overview: 'Hypersonic glide control using body flaps and aerodynamic surfaces. Tri-phase guidance: boost, glide cruise (energy management), and terminal pull-up/dive. Maintains 5-10g lateral maneuver capability throughout glide phase.',
    components: [
      {
        name: 'Guidance Computer',
        description: 'Three-phase guidance: boost, hypersonic glide, and terminal attack',
        specs: [
          { name: 'Boost Phase', value: 'Pre-programmed pitch profile' },
          { name: 'Glide Phase', value: 'Energy-optimal glide with waypoints' },
          { name: 'Terminal Law', value: 'Modified PN with altitude-rate constraint' },
          { name: 'Navigation Constant N', value: '4-6', note: 'Higher for high-speed closure' },
          { name: 'Update Rate', value: 200, unit: 'Hz' }
        ]
      },
      {
        name: 'Body Flaps',
        description: 'All-moving body flaps for hypersonic aerodynamic control',
        specs: [
          { name: 'Type', value: 'All-moving body flaps (4x)' },
          { name: 'Max Deflection', value: '+-15', unit: 'deg' },
          { name: 'Rate Limit', value: 100, unit: 'deg/s' },
          { name: 'Material', value: 'C/C-SiC ceramic matrix composite' },
          { name: 'Max Surface Temp', value: 1800, unit: 'C' }
        ]
      },
      {
        name: 'Electro-Mechanical Actuators',
        description: 'High-torque EMA for flap actuation in extreme thermal environment',
        specs: [
          { name: 'Type', value: 'Brushless DC electro-mechanical' },
          { name: 'Torque', value: 500, unit: 'N*m' },
          { name: 'Bandwidth', value: 25, unit: 'Hz' },
          { name: 'Thermal Rating', value: 200, unit: 'C ambient' }
        ]
      },
      {
        name: 'Autopilot',
        description: 'Adaptive gain-scheduled autopilot for Mach 5-12 flight regime',
        specs: [
          { name: 'Architecture', value: 'Adaptive gain-scheduled (neural network assist)' },
          { name: 'Mach Range', value: '5-12' },
          { name: 'Altitude Range', value: '20-80', unit: 'km' },
          { name: 'Stability Margins', value: 'Phase >35 deg, Gain >5 dB' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Cross-Range Maneuver', value: '+-400', unit: 'km', context: 'During glide phase' },
      { metric: 'Max Lateral Acceleration', value: '5-10', unit: 'g', context: 'Throughout glide' },
      { metric: 'Pull-Up G Load', value: '10-15', unit: 'g', context: 'Terminal pull-up maneuver' },
      { metric: 'Response Time', value: 0.1, unit: 's', context: 'Flap command to response' }
    ],
    equations: [
      {
        name: 'Hypersonic L/D and Turn Radius',
        latex: 'R_turn = V^2 / (g * sqrt(n^2 - 1))',
        description: 'Minimum turn radius at given velocity and load factor — determines maneuverability envelope',
        variables: [
          { symbol: 'R_turn', meaning: 'Turn radius', unit: 'm' },
          { symbol: 'V', meaning: 'Vehicle velocity', unit: 'm/s' },
          { symbol: 'g', meaning: 'Gravitational acceleration', unit: 'm/s^2' },
          { symbol: 'n', meaning: 'Load factor', unit: 'g' }
        ],
        numericalExample: {
          inputs: { 'V': '3400 m/s (Mach 10)', 'n': '5g' },
          calculation: 'R_turn = 3400^2 / (9.81 * sqrt(25-1)) = 11,560,000 / 48.06',
          result: 'R_turn ~240 km — defines minimum maneuver radius at Mach 10, 5g'
        }
      },
      {
        name: 'Glide Energy Management',
        latex: 'dE/dt = -D * V = -(q * S * C_D) * V',
        description: 'Energy dissipation rate during glide — guidance must balance range vs maneuver energy',
        variables: [
          { symbol: 'E', meaning: 'Total energy (KE + PE)', unit: 'J' },
          { symbol: 'D', meaning: 'Drag force', unit: 'N' },
          { symbol: 'q', meaning: 'Dynamic pressure', unit: 'Pa' },
          { symbol: 'S', meaning: 'Reference area', unit: 'm^2' },
          { symbol: 'C_D', meaning: 'Drag coefficient', unit: '' }
        ]
      }
    ],
    pseudocode: [
      {
        title: 'Hypersonic Glide Guidance',
        description: 'Energy-optimal glide with cross-range maneuvering and waypoint tracking',
        lines: [
          'WHILE phase == GLIDE:',
          '  state = INS.get_state()  // pos, vel, attitude',
          '  energy = 0.5*V^2 + g*altitude  // specific energy',
          '  range_to_target = distance(state.pos, target.pos)',
          '',
          '  // Energy management: modulate altitude to control range',
          '  E_required = energy_to_reach(range_to_target, L_D_ratio)',
          '  IF energy > E_required * 1.1:',
          '    // Excess energy: bank to increase drag (S-turn)',
          '    bank_cmd = compute_S_turn(excess_energy)',
          '  ELSE:',
          '    // Optimize L/D for max range',
          '    bank_cmd = compute_optimal_bank(state, target)',
          '',
          '  // Cross-range correction',
          '  cross_error = cross_track_error(state, target)',
          '  bank_cmd += K_cross * cross_error',
          '',
          '  // Altitude control',
          '  gamma_cmd = compute_flight_path_angle(energy, altitude_ref)',
          '  send_to_autopilot(bank_cmd, gamma_cmd)'
        ]
      },
      {
        title: 'Terminal Pull-Up and Dive',
        description: 'Pull-up maneuver to gain altitude for seeker activation, then steep dive onto target',
        lines: [
          'WHEN range_to_target < PULL_UP_RANGE:',
          '  phase = TERMINAL',
          '  // Pull-up to activate seeker above plasma sheath',
          '  gamma_cmd = +30 deg  // nose-up',
          '  WAIT until altitude > SEEKER_MIN_ALT',
          '',
          '  // Activate seeker',
          '  radar_seeker.activate()',
          '  target_lock = radar_seeker.acquire(search_box)',
          '',
          '  // Terminal dive with PN guidance',
          '  WHILE NOT impact:',
          '    LOS_rate = radar_seeker.get_LOS_rate()',
          '    V_c = radar_seeker.get_closing_velocity()',
          '    a_cmd = N * V_c * LOS_rate',
          '    a_cmd = clamp(a_cmd, -a_max, a_max)',
          '    send_to_autopilot(a_cmd, dive_angle)'
        ]
      }
    ],
    operationalNotes: [
      'Body flaps made of C/C-SiC ceramic matrix composite — withstand 1800C continuous exposure',
      'Cross-range maneuver of +-400 km makes trajectory prediction nearly impossible for BMD',
      'Energy management is key design challenge: too much maneuvering wastes energy and reduces range',
      'Pull-up maneuver trades kinetic energy for altitude, allowing seeker activation above plasma sheath',
      'Adaptive autopilot compensates for aerodynamic uncertainty at hypersonic speeds — neural network assists classical gains'
    ],
    interactionsWith: ['ins', 'radar-seeker', 'warhead-fuze']
  },

  // ── 4. Stellar Navigation ─────────────────────────────────────────────────
  {
    id: 'stellar-nav',
    name: 'Stellar Navigation',
    category: 'navigation',
    icon: '\u{2B50}',
    overview: 'Minimal stellar navigation capability. DF-17 has a short exoatmospheric phase (boost only) before HGV separates into atmosphere. Stellar fix window is very brief; glide phase occurs within atmosphere where stars are not observable through plasma/aerothermal environment.',
    components: [
      {
        name: 'Star Tracker',
        description: 'Compact star tracker for brief exoatmospheric window',
        specs: [
          { name: 'Sensor Type', value: 'CCD (compact)' },
          { name: 'FOV', value: '6x6', unit: 'deg' },
          { name: 'Accuracy', value: 10, unit: 'arcsec' },
          { name: 'Star Catalog', value: 2000, unit: 'stars' },
          { name: 'Weight', value: 1.5, unit: 'kg', note: 'Mass-constrained HGV' }
        ]
      },
      {
        name: 'INS Coupling',
        description: 'Single-fix Kalman update during brief exoatmospheric window',
        specs: [
          { name: 'Window Duration', value: '10-20', unit: 's' },
          { name: 'Fixes Available', value: '0-1', note: 'May be skipped if window too short' },
          { name: 'Position Correction', value: '50-150', unit: 'm' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Attitude Accuracy', value: 10, unit: 'arcsec', context: 'If fix obtained' },
      { metric: 'Fix Probability', value: '60-80', unit: '%', context: 'Brief window, high dynamics' },
      { metric: 'Update Window', value: '10-20', unit: 's', context: 'Between boost burnout and reentry' }
    ],
    operationalNotes: [
      'DF-17 may skip stellar nav entirely — short boost phase limits exoatmospheric observation window',
      'HGV separates at ~60 km altitude and immediately enters glide — atmospheric effects prevent stellar observation',
      'INS must carry navigation through entire glide phase (~8 min) without stellar correction',
      'Datalink updates (if available) more important than stellar for DF-17 glide-phase accuracy',
      'Some analysts suggest DF-17 may omit star tracker entirely to save mass/cost'
    ],
    interactionsWith: ['ins']
  },

  // ── 5. BeiDou Datalink ────────────────────────────────────────────────────
  {
    id: 'beidou-datalink',
    name: 'BeiDou Datalink',
    category: 'datalink',
    icon: '\u{1F4F6}',
    overview: 'BeiDou navigation and command datalink heavily challenged by plasma sheath at Mach 10+. Signal reception intermittent during glide phase. Antenna design attempts to exploit plasma-thinned regions on vehicle leeward side.',
    components: [
      {
        name: 'BeiDou Receiver',
        description: 'Plasma-hardened receiver with signal recovery algorithms',
        specs: [
          { name: 'Frequencies', value: 'B1C, B3I' },
          { name: 'Channels', value: 12, note: 'Reduced for plasma environment' },
          { name: 'Plasma Attenuation Tolerance', value: '20-30', unit: 'dB' },
          { name: 'Signal Recovery', value: 'Extended coherent integration' }
        ]
      },
      {
        name: 'Antenna (Plasma-Optimized)',
        description: 'Antenna placed in plasma-thinned region with electrodynamic window',
        specs: [
          { name: 'Type', value: 'Conformal slot antenna (leeward side)' },
          { name: 'Gain', value: '2-4', unit: 'dBic', note: 'Reduced by plasma' },
          { name: 'Placement', value: 'Leeward body surface' },
          { name: 'Plasma Mitigation', value: 'Magnetic window (experimental)' }
        ]
      },
      {
        name: 'Command Datalink',
        description: 'Ground-to-missile command link for target updates',
        specs: [
          { name: 'Frequency', value: 'UHF (lower attenuation through plasma)' },
          { name: 'Data Rate', value: 1200, unit: 'bps' },
          { name: 'Availability During Glide', value: '30-50', unit: '%', note: 'Intermittent due to plasma' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Position Fix Availability', value: '30-50', unit: '%', context: 'During Mach 10+ glide' },
      { metric: 'Position Accuracy (when available)', value: '<2', unit: 'm' },
      { metric: 'Blackout Duration', value: '30-60', unit: 's', context: 'Continuous blackout periods' },
      { metric: 'Datalink Update Success', value: '~40', unit: '%', context: 'Command gets through' }
    ],
    equations: [
      {
        name: 'Plasma Frequency vs Electron Density',
        latex: 'f_p = 9 * sqrt(n_e)  [Hz]',
        description: 'Plasma frequency — RF signals below this frequency are reflected, above are attenuated. At Mach 10+, f_p can exceed L-band BeiDou frequencies.',
        variables: [
          { symbol: 'f_p', meaning: 'Plasma frequency', unit: 'Hz' },
          { symbol: 'n_e', meaning: 'Electron density', unit: 'm^-3' }
        ],
        numericalExample: {
          inputs: { 'n_e': '1e18 m^-3 (typical Mach 10 sheath)' },
          calculation: 'f_p = 9 * sqrt(1e18) = 9e9 Hz = 9 GHz',
          result: '9 GHz plasma frequency — blocks L-band (1.5 GHz) BeiDou signals completely'
        }
      }
    ],
    operationalNotes: [
      'Plasma sheath at Mach 10+ creates electron densities of 1e17-1e19 m^-3 — blocks most RF signals',
      'BeiDou L-band (1.5 GHz) completely blocked when plasma frequency exceeds ~2 GHz',
      'UHF datalink has better penetration than L-band but still intermittent',
      'Magnetic window and ablative gas injection are being researched to create plasma-free communication windows',
      'DF-17 must accept degraded navigation during glide — INS carries the load between intermittent fixes',
      'This is the most significant technical challenge for HGV guidance accuracy'
    ],
    interactionsWith: ['ins', 'gnc']
  },

  // ── 6. Propulsion ─────────────────────────────────────────────────────────
  {
    id: 'propulsion',
    name: 'Propulsion',
    category: 'propulsion',
    icon: '\u{1F680}',
    overview: 'Single solid-rocket booster launches HGV to ~60 km altitude at ~Mach 10. After burnout, HGV separates and enters unpowered glide. No sustainer motor — glide range comes entirely from kinetic/potential energy at separation.',
    components: [
      {
        name: 'Solid Rocket Booster',
        description: 'Single-stage booster derived from DF-16 series',
        specs: [
          { name: 'Type', value: 'Solid propellant (single stage)' },
          { name: 'Propellant', value: 'HTPB composite (high energy)' },
          { name: 'Thrust (vacuum)', value: 500, unit: 'kN' },
          { name: 'Burn Time', value: 60, unit: 's' },
          { name: 'Specific Impulse', value: 275, unit: 's' },
          { name: 'Mass (loaded)', value: 12000, unit: 'kg' }
        ]
      },
      {
        name: 'HGV Separation Mechanism',
        description: 'Explosive bolt separation system with push springs',
        specs: [
          { name: 'Separation Type', value: 'Explosive bolts + push springs' },
          { name: 'Separation Velocity', value: 3, unit: 'm/s' },
          { name: 'Separation Altitude', value: '~60', unit: 'km' },
          { name: 'Separation Mach', value: '~10' },
          { name: 'Tumble Avoidance', value: 'Spin-stabilized during separation' }
        ]
      },
      {
        name: 'Thermal Protection System (HGV)',
        description: 'Multi-layer TPS for sustained Mach 10+ glide',
        specs: [
          { name: 'Nose Cap', value: 'UHTC (ZrB2-SiC)' },
          { name: 'Leading Edges', value: 'C/C-SiC ceramic matrix composite' },
          { name: 'Windward Surface', value: 'Ablative tiles' },
          { name: 'Leeward Surface', value: 'Insulated metallic' },
          { name: 'Max Temperature (nose)', value: 2500, unit: 'C' },
          { name: 'Sustained Surface Temp', value: '1200-1800', unit: 'C' }
        ]
      },
      {
        name: 'Booster Nozzle',
        description: 'Fixed nozzle with jet vane TVC',
        specs: [
          { name: 'Type', value: 'Fixed nozzle + jet vane TVC' },
          { name: 'Expansion Ratio', value: 10 },
          { name: 'TVC Method', value: 'Jet vanes in exhaust' },
          { name: 'TVC Deflection', value: '+-5', unit: 'deg' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'Burnout Velocity', value: '~3400', unit: 'm/s', context: 'Mach 10 at 60 km' },
      { metric: 'Separation Altitude', value: 60, unit: 'km' },
      { metric: 'Boost Duration', value: 60, unit: 's' },
      { metric: 'Launch Mass (total)', value: '~15,000', unit: 'kg' },
      { metric: 'HGV Mass (post-separation)', value: '~1500', unit: 'kg' }
    ],
    equations: [
      {
        name: 'Boost Phase Burnout Conditions',
        latex: 'V_bo = Isp * g0 * ln(m0/mf) - g * t_burn * sin(gamma) - D_loss',
        description: 'Burnout velocity accounting for gravity and drag losses during boost',
        variables: [
          { symbol: 'V_bo', meaning: 'Burnout velocity', unit: 'm/s' },
          { symbol: 'Isp', meaning: 'Specific impulse', unit: 's' },
          { symbol: 'gamma', meaning: 'Average flight path angle', unit: 'rad' },
          { symbol: 'D_loss', meaning: 'Integrated drag loss', unit: 'm/s' }
        ],
        numericalExample: {
          inputs: { 'Isp': '275 s', 'm0': '15000 kg', 'mf': '3000 kg', 'gamma': '45 deg', 't_burn': '60 s' },
          calculation: 'V_ideal = 275*9.81*ln(5) = 4340; gravity_loss = 9.81*60*0.707 = 416; drag_loss ~500',
          result: 'V_bo ~3400 m/s (Mach 10 at 60 km altitude)'
        }
      }
    ],
    operationalNotes: [
      'Single-stage booster simplifies TEL and launch operations compared to two-stage DF-21D/DF-26',
      'HGV is unpowered after separation — all subsequent energy comes from initial KE + PE at separation',
      'TPS is the critical engineering challenge — must survive 8+ minutes of sustained Mach 10 heating',
      'UHTC nose cap (ZrB2-SiC) is state-of-the-art material — limited global manufacturing capability',
      'Separation dynamics critical — any tumble at Mach 10 could be unrecoverable'
    ],
    interactionsWith: ['gnc', 'ins']
  },

  // ── 7. Warhead & Fuzing ───────────────────────────────────────────────────
  {
    id: 'warhead-fuze',
    name: 'Warhead & Fuzing',
    category: 'warhead',
    icon: '\u{1F4A5}',
    overview: 'Kinetic energy penetrator warhead — the HGV\'s Mach 10+ impact velocity delivers devastating kinetic energy equivalent to several tons of TNT. Small explosive payload supplements massive kinetic effect. Designed for deck penetration and internal blast.',
    components: [
      {
        name: 'Warhead',
        description: 'Kinetic energy penetrator with supplementary explosive',
        specs: [
          { name: 'Type', value: 'Kinetic energy penetrator + HE supplement' },
          { name: 'Total Weight', value: '300-500', unit: 'kg', note: 'Mass-constrained by HGV' },
          { name: 'HE Fill', value: '100-200', unit: 'kg' },
          { name: 'Penetrator Case', value: 'Tungsten alloy or depleted uranium' },
          { name: 'Impact Velocity', value: 'Mach 5-10+', unit: '', note: 'Depends on terminal profile' }
        ]
      },
      {
        name: 'Fuze System',
        description: 'Hardened contact fuze for high-velocity impact',
        specs: [
          { name: 'Primary Mode', value: 'Contact (piezoelectric crush sensor)' },
          { name: 'Delay Mode', value: 'Post-penetration delay (ms-class)' },
          { name: 'Survivability', value: 'Must survive >1000g impact deceleration' },
          { name: 'Arming', value: 'G-switch + timer + radar altimeter' }
        ]
      },
      {
        name: 'Damage Assessment Model',
        description: 'Terminal effects analysis for kinetic energy impact',
        specs: [
          { name: 'KE at Mach 10', value: '~8.7 GJ', note: '1500 kg * 3400 m/s' },
          { name: 'KE at Mach 5', value: '~2.2 GJ', note: 'Decelerated terminal profile' },
          { name: 'Steel Penetration', value: '200+', unit: 'mm', note: 'At Mach 10' },
          { name: 'Effect', value: 'Through carrier flight deck + hangar deck + possible keel' }
        ]
      }
    ],
    performanceMetrics: [
      { metric: 'KE at Mach 10 Impact', value: '~8.7', unit: 'GJ', context: '~2 tons TNT equiv in KE' },
      { metric: 'KE at Mach 5 Impact', value: '~2.2', unit: 'GJ', context: 'After pull-up deceleration' },
      { metric: 'Steel Penetration', value: '200+', unit: 'mm' },
      { metric: 'P(mission kill) per hit', value: '0.8-0.95', unit: '', context: 'KE + HE combined effect' }
    ],
    equations: [
      {
        name: 'Kinetic Energy at Impact',
        latex: 'KE = 0.5 * m * V^2',
        description: 'The dominant damage mechanism — kinetic energy scales with velocity squared',
        variables: [
          { symbol: 'KE', meaning: 'Kinetic energy', unit: 'J' },
          { symbol: 'm', meaning: 'HGV mass at impact', unit: 'kg' },
          { symbol: 'V', meaning: 'Impact velocity', unit: 'm/s' }
        ],
        numericalExample: {
          inputs: { 'm': '1500 kg (full HGV)', 'V': '3400 m/s (Mach 10)' },
          calculation: 'KE = 0.5 * 1500 * 3400^2 = 8.67e9 J',
          result: '8.67 GJ = ~2.07 tons TNT equivalent from kinetic energy alone'
        }
      },
      {
        name: 'Penetration Depth (de Marre)',
        latex: 'e = K * d^0.75 * (m/d^3)^0.5 * V^1.43',
        description: 'Armor plate penetration using de Marre empirical formula',
        variables: [
          { symbol: 'e', meaning: 'Plate thickness penetrated', unit: 'mm' },
          { symbol: 'K', meaning: 'Empirical constant', unit: '' },
          { symbol: 'd', meaning: 'Projectile diameter', unit: 'mm' },
          { symbol: 'm', meaning: 'Projectile mass', unit: 'kg' },
          { symbol: 'V', meaning: 'Impact velocity', unit: 'm/s' }
        ]
      }
    ],
    operationalNotes: [
      'At Mach 10, the kinetic energy alone (8.7 GJ) is more destructive than any conventional warhead in the inventory',
      'Even at Mach 5 (after pull-up deceleration), KE of 2.2 GJ still exceeds most anti-ship missile warheads',
      'Tungsten alloy penetrator survives impact deceleration and punches through multiple steel decks',
      'Post-penetration HE detonation creates secondary damage inside ship — fires, flooding, structural failure',
      'Single HGV impact likely achieves mission kill on any surface combatant',
      'Fuze must survive 1000+ g impact shock — piezoelectric crystal sensors preferred over mechanical'
    ],
    interactionsWith: ['gnc', 'radar-seeker']
  }
];
