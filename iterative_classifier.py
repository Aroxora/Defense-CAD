#!/usr/bin/env python3
"""
Iterative Classified Parameter Estimator

Uses Bayesian inference to iteratively refine guesses for classified parameters
based on:
1. Physics bounds (hard constraints)
2. OSINT observations (soft constraints)
3. Forward simulation (likelihood model)

Converges toward most probable classified values.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Callable
from scipy import stats
from scipy.optimize import minimize, differential_evolution
import json


@dataclass
class ClassifiedParameter:
    """A classified parameter we're trying to estimate."""
    name: str
    unit: str

    # Physics bounds (CANNOT be violated)
    physics_min: float
    physics_max: float

    # Current estimate (updated by inference)
    estimate: float
    std: float  # uncertainty

    # Confidence (0-1)
    confidence: float = 0.5

    # Reasoning chain
    reasoning: List[str] = field(default_factory=list)

    def sample(self, n: int = 1) -> np.ndarray:
        """Sample from current belief distribution (truncated normal)."""
        samples = np.random.normal(self.estimate, self.std, n)
        return np.clip(samples, self.physics_min, self.physics_max)

    def log_prior(self, value: float) -> float:
        """Log prior probability (uniform within physics bounds)."""
        if value < self.physics_min or value > self.physics_max:
            return -np.inf
        # Gaussian prior centered on current estimate
        return stats.norm.logpdf(value, self.estimate, self.std)

    def update(self, new_estimate: float, new_std: float, reasoning: str):
        """Bayesian update of estimate."""
        # Clip to physics bounds
        new_estimate = np.clip(new_estimate, self.physics_min, self.physics_max)

        self.estimate = new_estimate
        self.std = max(new_std, (self.physics_max - self.physics_min) * 0.01)  # min 1% uncertainty
        self.confidence = 1.0 - (self.std / (self.physics_max - self.physics_min))
        self.reasoning.append(reasoning)


@dataclass
class Observation:
    """An observable fact that constrains parameters."""
    name: str
    source: str  # OSINT source

    # The observation constrains a derived quantity
    observable: str  # e.g., "detection_range_km"
    observed_value: float
    observed_std: float  # uncertainty in observation

    # Confidence in this observation (0-1)
    credibility: float = 0.7

    def log_likelihood(self, predicted_value: float) -> float:
        """Log likelihood of observation given prediction."""
        # Gaussian likelihood weighted by credibility
        ll = stats.norm.logpdf(predicted_value, self.observed_value, self.observed_std)
        return ll * self.credibility


class ForwardModel:
    """Physics-based forward model: parameters → observables."""

    @staticmethod
    def madl_detection_range(tx_power_w: float, sidelobe_db: float,
                              esm_sensitivity_dbm: float = -120) -> float:
        """
        Calculate MADL sidelobe detection range.

        Physics: Free space path loss + antenna gain + receiver sensitivity
        """
        c = 3e8
        freq = 14.4e9  # MADL frequency (from OSINT)
        wavelength = c / freq

        # Antenna gain (main lobe ~31 dBi for 15cm aperture)
        main_lobe_gain_db = 31.5
        sidelobe_gain_db = main_lobe_gain_db + sidelobe_db  # sidelobe_db is negative

        # EIRP in sidelobe direction
        tx_power_dbm = 10 * np.log10(tx_power_w * 1000)
        eirp_dbm = tx_power_dbm + sidelobe_gain_db

        # ESM receiver
        esm_gain_db = 10  # Typical ESM antenna
        required_snr_db = 10  # Detection threshold

        # Solve for range: EIRP - PathLoss + RxGain >= Sensitivity + SNR
        # PathLoss = 20*log10(R) + 20*log10(f) + 20*log10(4*pi/c)
        # PathLoss = 20*log10(R) + constant

        constant = 20 * np.log10(freq) + 20 * np.log10(4 * np.pi / c)
        max_path_loss = eirp_dbm + esm_gain_db - esm_sensitivity_dbm - required_snr_db

        # 20*log10(R) = max_path_loss - constant
        log_range = (max_path_loss - constant) / 20
        range_m = 10 ** log_range

        return range_m / 1000  # km

    @staticmethod
    def radar_detection_range(power_kw: float, n_elements: int,
                               target_rcs_m2: float, wavelength_m: float = 0.03) -> float:
        """
        Radar range equation: R = (Pt * G^2 * λ^2 * σ / ((4π)^3 * Smin))^0.25
        """
        power_w = power_kw * 1000

        # Antenna gain from element count (AESA)
        element_gain = 4  # ~6 dBi per element
        array_gain = n_elements * element_gain * 0.7  # 70% efficiency
        gain_db = 10 * np.log10(array_gain)
        gain_linear = array_gain

        # Receiver sensitivity
        sensitivity_w = 1e-13  # Typical fighter radar

        # Radar range equation
        numerator = power_w * gain_linear**2 * wavelength_m**2 * target_rcs_m2
        denominator = (4 * np.pi)**3 * sensitivity_w

        range_m = (numerator / denominator) ** 0.25
        return range_m / 1000  # km

    @staticmethod
    def missile_nez(max_range_km: float, target_speed_mach: float = 1.6,
                    missile_speed_mach: float = 4.0) -> float:
        """
        No-Escape Zone calculation.

        NEZ = range where target cannot escape even with optimal maneuver.
        """
        # Target escape speed
        target_speed_ms = target_speed_mach * 340
        missile_speed_ms = missile_speed_mach * 340

        # Time for missile to reach max range
        avg_missile_speed = missile_speed_ms * 0.7  # Average over flight
        time_to_max = max_range_km * 1000 / avg_missile_speed

        # Target escape distance
        escape_distance_km = target_speed_ms * time_to_max / 1000

        # NEZ = max_range - escape_distance (simplified)
        nez = max_range_km - escape_distance_km * 0.8  # 80% factor for geometry

        return max(nez, max_range_km * 0.3)  # At least 30% of max range


class IterativeClassifier:
    """
    Main inference engine.

    Uses Markov Chain Monte Carlo (MCMC) to sample posterior distribution
    of classified parameters given observations.
    """

    def __init__(self):
        self.parameters: Dict[str, ClassifiedParameter] = {}
        self.observations: List[Observation] = []
        self.forward_model = ForwardModel()
        self.iteration = 0
        self.history: List[Dict] = []

    def add_parameter(self, param: ClassifiedParameter):
        """Add a classified parameter to estimate."""
        self.parameters[param.name] = param

    def add_observation(self, obs: Observation):
        """Add an observation that constrains parameters."""
        self.observations.append(obs)

    def predict_observable(self, param_values: Dict[str, float],
                           observable_name: str) -> float:
        """Forward model: predict observable from parameters."""

        if observable_name == "madl_detection_range_km":
            return self.forward_model.madl_detection_range(
                tx_power_w=param_values.get('madl_tx_power_w', 2.0),
                sidelobe_db=param_values.get('madl_sidelobe_db', -30)
            )

        elif observable_name == "j20_vs_f35_detection_km":
            return self.forward_model.radar_detection_range(
                power_kw=param_values.get('j20_power_kw', 14),
                n_elements=int(param_values.get('j20_aesa_elements', 1500)),
                target_rcs_m2=param_values.get('f35_rcs_m2', 0.0001)
            )

        elif observable_name == "f35_vs_j20_detection_km":
            return self.forward_model.radar_detection_range(
                power_kw=12,  # APG-81 known
                n_elements=1200,  # APG-81 known
                target_rcs_m2=param_values.get('j20_rcs_m2', 0.05)
            )

        elif observable_name == "pl15_nez_km":
            return self.forward_model.missile_nez(
                max_range_km=param_values.get('pl15_max_range_km', 200)
            )

        else:
            raise ValueError(f"Unknown observable: {observable_name}")

    def log_posterior(self, param_values: Dict[str, float]) -> float:
        """Calculate log posterior probability."""

        # Log prior (product of individual priors)
        log_prior = 0
        for name, value in param_values.items():
            if name in self.parameters:
                log_prior += self.parameters[name].log_prior(value)

        if log_prior == -np.inf:
            return -np.inf

        # Log likelihood (product of observation likelihoods)
        log_likelihood = 0
        for obs in self.observations:
            try:
                predicted = self.predict_observable(param_values, obs.observable)
                log_likelihood += obs.log_likelihood(predicted)
            except Exception:
                pass  # Skip if observable not computable

        return log_prior + log_likelihood

    def run_mcmc(self, n_samples: int = 5000, burn_in: int = 1000) -> Dict[str, np.ndarray]:
        """
        Run MCMC to sample posterior distribution.

        Uses Metropolis-Hastings algorithm.
        """
        print(f"\n{'='*60}")
        print(f"MCMC ITERATION {self.iteration + 1}")
        print(f"{'='*60}")

        # Initialize from current estimates
        current = {name: p.estimate for name, p in self.parameters.items()}
        current_log_prob = self.log_posterior(current)

        # Proposal standard deviations
        proposal_std = {name: p.std * 0.5 for name, p in self.parameters.items()}

        # Storage for samples
        samples = {name: [] for name in self.parameters}
        accepted = 0

        print(f"Running {n_samples} MCMC samples (burn-in: {burn_in})...")

        for i in range(n_samples + burn_in):
            # Propose new values
            proposed = {}
            for name, value in current.items():
                proposed[name] = np.random.normal(value, proposal_std[name])

            # Calculate acceptance probability
            proposed_log_prob = self.log_posterior(proposed)
            log_alpha = proposed_log_prob - current_log_prob

            # Accept/reject
            if np.log(np.random.random()) < log_alpha:
                current = proposed
                current_log_prob = proposed_log_prob
                accepted += 1

            # Store samples after burn-in
            if i >= burn_in:
                for name, value in current.items():
                    samples[name].append(value)

            # Progress
            if (i + 1) % 1000 == 0:
                print(f"  Step {i+1}/{n_samples + burn_in}, "
                      f"acceptance rate: {accepted/(i+1):.1%}")

        # Convert to arrays
        samples = {name: np.array(vals) for name, vals in samples.items()}

        print(f"\nFinal acceptance rate: {accepted/(n_samples + burn_in):.1%}")

        return samples

    def update_estimates(self, samples: Dict[str, np.ndarray]):
        """Update parameter estimates from MCMC samples."""

        print(f"\nUPDATED ESTIMATES:")
        print("-" * 60)

        for name, sample_array in samples.items():
            param = self.parameters[name]

            old_estimate = param.estimate
            old_std = param.std

            new_estimate = np.median(sample_array)
            new_std = np.std(sample_array)

            # Calculate credible interval
            ci_low, ci_high = np.percentile(sample_array, [5, 95])

            param.update(
                new_estimate,
                new_std,
                f"Iteration {self.iteration + 1}: {old_estimate:.4g} → {new_estimate:.4g}"
            )

            change = new_estimate - old_estimate
            print(f"  {name}:")
            print(f"    Old: {old_estimate:.4g} ± {old_std:.4g}")
            print(f"    New: {new_estimate:.4g} ± {new_std:.4g}")
            print(f"    90% CI: [{ci_low:.4g}, {ci_high:.4g}]")
            print(f"    Change: {change:+.4g} ({change/old_estimate*100:+.1f}%)")
            print(f"    Confidence: {param.confidence:.1%}")
            print()

    def check_convergence(self, threshold: float = 0.05) -> bool:
        """Check if estimates have converged."""
        if len(self.history) < 2:
            return False

        prev = self.history[-2]
        curr = self.history[-1]

        max_change = 0
        for name in self.parameters:
            if name in prev and name in curr:
                change = abs(curr[name] - prev[name]) / (abs(prev[name]) + 1e-10)
                max_change = max(max_change, change)

        return max_change < threshold

    def iterate(self, max_iterations: int = 10, n_samples: int = 5000) -> Dict:
        """
        Main iteration loop.

        Runs MCMC, updates estimates, checks convergence.
        """
        print("\n" + "=" * 70)
        print("ITERATIVE CLASSIFIED PARAMETER ESTIMATION")
        print("=" * 70)
        print(f"\nParameters to estimate: {len(self.parameters)}")
        for name, param in self.parameters.items():
            print(f"  {name}: [{param.physics_min}, {param.physics_max}] {param.unit}")

        print(f"\nObservations: {len(self.observations)}")
        for obs in self.observations:
            print(f"  {obs.name}: {obs.observed_value} ± {obs.observed_std} ({obs.source})")

        for iteration in range(max_iterations):
            self.iteration = iteration

            # Run MCMC
            samples = self.run_mcmc(n_samples=n_samples)

            # Update estimates
            self.update_estimates(samples)

            # Store history
            self.history.append({
                name: param.estimate for name, param in self.parameters.items()
            })

            # Check convergence
            if self.check_convergence():
                print(f"\n✓ CONVERGED after {iteration + 1} iterations!")
                break
        else:
            print(f"\n⚠ Max iterations ({max_iterations}) reached")

        return self.get_results()

    def get_results(self) -> Dict:
        """Get final estimates."""
        results = {
            'converged': self.check_convergence(),
            'iterations': self.iteration + 1,
            'parameters': {}
        }

        for name, param in self.parameters.items():
            results['parameters'][name] = {
                'estimate': param.estimate,
                'std': param.std,
                'confidence': param.confidence,
                'unit': param.unit,
                'physics_bounds': [param.physics_min, param.physics_max],
                'reasoning': param.reasoning
            }

        return results


def setup_f35_j20_estimation() -> IterativeClassifier:
    """
    Set up estimator for F-35 vs J-20 scenario.

    Uses all available OSINT observations.
    """
    classifier = IterativeClassifier()

    # =========================================================================
    # F-35 CLASSIFIED PARAMETERS
    # =========================================================================

    # MADL sidelobe level (CRITICAL - determines detectability)
    classifier.add_parameter(ClassifiedParameter(
        name='madl_sidelobe_db',
        unit='dB',
        physics_min=-45,  # Theoretical best for phased array
        physics_max=-15,  # Minimum acceptable for "LPI"
        estimate=-30,     # Initial guess
        std=5,
        reasoning=["Initial: Physics midpoint + LPI requirement"]
    ))

    # MADL TX power
    classifier.add_parameter(ClassifiedParameter(
        name='madl_tx_power_w',
        unit='W',
        physics_min=0.5,   # Minimum for any useful range
        physics_max=10,    # Max for conformal thermal limits
        estimate=2.0,
        std=1.5,
        reasoning=["Initial: Thermal limits + similar systems"]
    ))

    # F-35 frontal RCS
    classifier.add_parameter(ClassifiedParameter(
        name='f35_rcs_m2',
        unit='m²',
        physics_min=0.00001,  # Theoretical minimum for fighter
        physics_max=0.01,     # Max for "stealth" claim
        estimate=0.0001,
        std=0.0002,
        reasoning=["Initial: VLO requirement + physical limits"]
    ))

    # F-35 APG-81 peak power
    classifier.add_parameter(ClassifiedParameter(
        name='apg81_power_kw',
        unit='kW',
        physics_min=8,
        physics_max=20,
        estimate=12,
        std=3,
        reasoning=["Initial: GaN AESA + thermal limits"]
    ))

    # F-35 APG-81 elements
    classifier.add_parameter(ClassifiedParameter(
        name='apg81_elements',
        unit='count',
        physics_min=1000,
        physics_max=1600,
        estimate=1200,
        std=100,
        reasoning=["Initial: Nose aperture + λ/2 spacing at X-band"]
    ))

    # F-35 IR signature (afterburner)
    classifier.add_parameter(ClassifiedParameter(
        name='f35_ir_signature_w_sr',
        unit='W/sr',
        physics_min=5000,
        physics_max=50000,
        estimate=15000,
        std=8000,
        reasoning=["Initial: F119-derived engine + low-observable nozzle"]
    ))

    # AIM-120D max range
    classifier.add_parameter(ClassifiedParameter(
        name='aim120d_max_range_km',
        unit='km',
        physics_min=140,
        physics_max=200,
        estimate=180,
        std=20,
        reasoning=["Initial: Dual-pulse motor + size comparison to AMRAAM-C"]
    ))

    # AIM-120D NEZ
    classifier.add_parameter(ClassifiedParameter(
        name='aim120d_nez_km',
        unit='km',
        physics_min=50,
        physics_max=100,
        estimate=80,
        std=15,
        reasoning=["Initial: ~45% of max range typical for BVR missiles"]
    ))

    # =========================================================================
    # J-20 CLASSIFIED PARAMETERS
    # =========================================================================

    # J-20 frontal RCS
    classifier.add_parameter(ClassifiedParameter(
        name='j20_rcs_m2',
        unit='m²',
        physics_min=0.01,   # Minimum for less-mature stealth
        physics_max=0.5,    # Max with some shaping
        estimate=0.05,
        std=0.03,
        reasoning=["Initial: Canard penalty + engine nozzles"]
    ))

    # J-20 beam RCS (side aspect)
    classifier.add_parameter(ClassifiedParameter(
        name='j20_beam_rcs_m2',
        unit='m²',
        physics_min=0.5,
        physics_max=5.0,
        estimate=1.5,
        std=0.8,
        reasoning=["Initial: Large airframe + less side optimization"]
    ))

    # J-20 AESA elements
    classifier.add_parameter(ClassifiedParameter(
        name='j20_aesa_elements',
        unit='count',
        physics_min=800,    # Minimum for useful radar
        physics_max=2200,   # Max for nose aperture
        estimate=1500,
        std=200,
        reasoning=["Initial: Nose diameter + λ/2 spacing"]
    ))

    # J-20 radar power
    classifier.add_parameter(ClassifiedParameter(
        name='j20_power_kw',
        unit='kW',
        physics_min=6,      # Minimum for fighter radar
        physics_max=25,     # Max for cooling limits
        estimate=14,
        std=4,
        reasoning=["Initial: GaN technology limits"]
    ))

    # J-20 supercruise speed
    classifier.add_parameter(ClassifiedParameter(
        name='j20_supercruise_mach',
        unit='Mach',
        physics_min=1.2,
        physics_max=1.8,
        estimate=1.5,
        std=0.15,
        reasoning=["Initial: WS-15 not yet available, WS-10C limits"]
    ))

    # J-20 combat radius
    classifier.add_parameter(ClassifiedParameter(
        name='j20_combat_radius_km',
        unit='km',
        physics_min=1000,
        physics_max=2000,
        estimate=1500,
        std=200,
        reasoning=["Initial: Internal fuel + airframe size"]
    ))

    # =========================================================================
    # PL-15 CLASSIFIED PARAMETERS
    # =========================================================================

    # PL-15 max range
    classifier.add_parameter(ClassifiedParameter(
        name='pl15_max_range_km',
        unit='km',
        physics_min=120,    # Minimum for "long range" claim
        physics_max=300,    # Max for missile size
        estimate=200,
        std=40,
        reasoning=["Initial: Rocket equation + size comparison"]
    ))

    # PL-15 NEZ
    classifier.add_parameter(ClassifiedParameter(
        name='pl15_nez_km',
        unit='km',
        physics_min=50,
        physics_max=150,
        estimate=100,
        std=25,
        reasoning=["Initial: ~50% of max range for advanced missile"]
    ))

    # PL-15 seeker gimbal limit
    classifier.add_parameter(ClassifiedParameter(
        name='pl15_gimbal_deg',
        unit='deg',
        physics_min=40,
        physics_max=90,
        estimate=60,
        std=10,
        reasoning=["Initial: Modern AESA seeker capability"]
    ))

    # PL-15 terminal speed
    classifier.add_parameter(ClassifiedParameter(
        name='pl15_terminal_mach',
        unit='Mach',
        physics_min=3.0,
        physics_max=5.0,
        estimate=4.0,
        std=0.5,
        reasoning=["Initial: Dual-pulse solid motor"]
    ))

    # =========================================================================
    # DF-17 CLASSIFIED PARAMETERS
    # =========================================================================

    classifier.add_parameter(ClassifiedParameter(
        name='df17_cep_m',
        unit='m',
        physics_min=5,
        physics_max=50,
        estimate=15,
        std=10,
        reasoning=["Initial: HGV + terminal guidance"]
    ))

    classifier.add_parameter(ClassifiedParameter(
        name='df17_terminal_mach',
        unit='Mach',
        physics_min=5,
        physics_max=12,
        estimate=8,
        std=2,
        reasoning=["Initial: HGV glide physics"]
    ))

    classifier.add_parameter(ClassifiedParameter(
        name='df17_range_km',
        unit='km',
        physics_min=1500,
        physics_max=2500,
        estimate=1800,
        std=300,
        reasoning=["Initial: Boost + glide trajectory"]
    ))

    # =========================================================================
    # DF-21D ANTI-SHIP CLASSIFIED PARAMETERS
    # =========================================================================

    classifier.add_parameter(ClassifiedParameter(
        name='df21d_cep_m',
        unit='m',
        physics_min=10,
        physics_max=100,
        estimate=30,
        std=20,
        reasoning=["Initial: Maneuvering RV + OTH targeting uncertainty"]
    ))

    classifier.add_parameter(ClassifiedParameter(
        name='df21d_range_km',
        unit='km',
        physics_min=1200,
        physics_max=1800,
        estimate=1500,
        std=200,
        reasoning=["Initial: MRBM class + glide"]
    ))

    # =========================================================================
    # S-400 CLASSIFIED PARAMETERS
    # =========================================================================

    classifier.add_parameter(ClassifiedParameter(
        name='s400_detection_vs_f35_km',
        unit='km',
        physics_min=80,
        physics_max=250,
        estimate=150,
        std=40,
        reasoning=["Initial: S-band advantage vs stealth + large aperture"]
    ))

    classifier.add_parameter(ClassifiedParameter(
        name='s400_pk_vs_stealth',
        unit='fraction',
        physics_min=0.2,
        physics_max=0.7,
        estimate=0.45,
        std=0.12,
        reasoning=["Initial: Detection advantage offset by missile limitations"]
    ))

    # =========================================================================
    # SU-57 CLASSIFIED PARAMETERS
    # =========================================================================

    classifier.add_parameter(ClassifiedParameter(
        name='su57_rcs_m2',
        unit='m²',
        physics_min=0.1,
        physics_max=1.0,
        estimate=0.3,
        std=0.15,
        reasoning=["Initial: Stealth shaping but round nozzles + gaps"]
    ))

    classifier.add_parameter(ClassifiedParameter(
        name='su57_radar_power_kw',
        unit='kW',
        physics_min=15,
        physics_max=30,
        estimate=20,
        std=4,
        reasoning=["Initial: N036 AESA + Russian high-power philosophy"]
    ))

    # =========================================================================
    # YJ-21 HYPERSONIC ASBM PARAMETERS
    # =========================================================================

    classifier.add_parameter(ClassifiedParameter(
        name='yj21_range_km',
        unit='km',
        physics_min=800,
        physics_max=1500,
        estimate=1000,
        std=200,
        reasoning=["Initial: Ship-launched ballistic + glide"]
    ))

    classifier.add_parameter(ClassifiedParameter(
        name='yj21_terminal_mach',
        unit='Mach',
        physics_min=6,
        physics_max=10,
        estimate=8,
        std=1.5,
        reasoning=["Initial: HGV terminal dive"]
    ))

    # =========================================================================
    # KJ-500 AWACS PARAMETERS
    # =========================================================================

    classifier.add_parameter(ClassifiedParameter(
        name='kj500_detection_range_km',
        unit='km',
        physics_min=300,
        physics_max=500,
        estimate=400,
        std=60,
        reasoning=["Initial: AESA rotodome + S-band"]
    ))

    classifier.add_parameter(ClassifiedParameter(
        name='kj500_vs_stealth_km',
        unit='km',
        physics_min=100,
        physics_max=250,
        estimate=180,
        std=40,
        reasoning=["Initial: Lower frequency helps but F-35 optimized"]
    ))

    # =========================================================================
    # OSINT OBSERVATIONS (Constrain the parameter estimates)
    # =========================================================================

    # China claims MADL is detectable (implies sidelobe detection possible)
    classifier.add_observation(Observation(
        name='MADL detected by ESM',
        source='Chinese military journals (2018-2022)',
        observable='madl_detection_range_km',
        observed_value=60,
        observed_std=25,
        credibility=0.5
    ))

    # J-20 can engage F-35 at "BVR range"
    classifier.add_observation(Observation(
        name='J-20 detects F-35',
        source='PLAAF doctrine papers',
        observable='j20_vs_f35_detection_km',
        observed_value=80,
        observed_std=30,
        credibility=0.6
    ))

    # F-35 has "significant advantage" over J-20
    classifier.add_observation(Observation(
        name='F-35 detects J-20 first',
        source='USAF testimony + analysis',
        observable='f35_vs_j20_detection_km',
        observed_value=180,
        observed_std=40,
        credibility=0.75
    ))

    # PL-15 "outranges AIM-120D"
    classifier.add_observation(Observation(
        name='PL-15 NEZ',
        source='DOD China Military Power Report',
        observable='pl15_nez_km',
        observed_value=100,
        observed_std=25,
        credibility=0.7
    ))

    # DF-17 demonstrated in parade with claimed CEP
    classifier.add_observation(Observation(
        name='DF-17 precision',
        source='2019 National Day Parade + CCTV claims',
        observable='df17_cep_km',
        observed_value=0.015,  # 15m CEP
        observed_std=0.010,
        credibility=0.4
    ))

    # S-400 sales pitch claims detection vs stealth
    classifier.add_observation(Observation(
        name='S-400 vs stealth detection',
        source='Almaz-Antey marketing + Syrian deployment',
        observable='s400_detection_range_km',
        observed_value=200,
        observed_std=60,
        credibility=0.55
    ))

    # Su-57 RCS claims
    classifier.add_observation(Observation(
        name='Su-57 RCS',
        source='Russian MoD + Sukhoi claims',
        observable='su57_frontal_rcs_m2',
        observed_value=0.1,
        observed_std=0.1,
        credibility=0.4
    ))

    # KJ-500 detection claims
    classifier.add_observation(Observation(
        name='KJ-500 range',
        source='PLAAF exercise observations',
        observable='kj500_range_km',
        observed_value=450,
        observed_std=80,
        credibility=0.6
    ))

    return classifier


def main():
    """Run the iterative estimation."""

    # Set up estimator
    classifier = setup_f35_j20_estimation()

    # Run iteration
    results = classifier.iterate(max_iterations=10, n_samples=3000)

    # Print final results
    print("\n" + "=" * 70)
    print("FINAL CLASSIFIED PARAMETER ESTIMATES")
    print("=" * 70)

    for name, data in results['parameters'].items():
        print(f"\n{name}:")
        print(f"  Best estimate: {data['estimate']:.4g} {data['unit']}")
        print(f"  Uncertainty: ±{data['std']:.4g} {data['unit']}")
        print(f"  Confidence: {data['confidence']:.1%}")
        print(f"  Physics bounds: {data['physics_bounds']}")
        print(f"  Reasoning chain:")
        for r in data['reasoning'][-3:]:  # Last 3 updates
            print(f"    - {r}")

    # Save to file
    with open('CONVERGED_ESTIMATES.json', 'w') as f:
        # Convert numpy types to Python types
        clean_results = json.loads(json.dumps(results, default=float))
        json.dump(clean_results, f, indent=2)

    print(f"\n✓ Results saved to CONVERGED_ESTIMATES.json")

    # Update docs/PARAMETER_ESTIMATES.md
    print("\n" + "=" * 70)
    print("UPDATING docs/PARAMETER_ESTIMATES.md")
    print("=" * 70)

    update_lines = []
    for name, data in results['parameters'].items():
        update_lines.append(
            f"| **{name}** | {data['estimate']:.4g} {data['unit']} | "
            f"{data['confidence']:.0%} | Iterative Bayesian ({results['iterations']} iters) |"
        )

    print("\nNew estimates to add:")
    for line in update_lines:
        print(line)

    return results


if __name__ == '__main__':
    main()
