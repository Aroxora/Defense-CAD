#!/usr/bin/env python3
"""
ML-Based Waveform Classification

Deep learning classifier for identifying LPI/LPD waveform types from
time-frequency representations.

Classifies:
- BPSK, QPSK, 8PSK modulation schemes
- DSSS (Direct Sequence Spread Spectrum)
- FHSS (Frequency Hopping Spread Spectrum)
- LFM (Linear Frequency Modulation)
- OFDM
- Unknown/Noise

Uses convolutional neural network on spectrogram inputs.
"""

import numpy as np
from typing import Tuple, List, Dict
from dataclasses import dataclass
from scipy import signal


class WaveformType:
    """Known waveform types"""
    BPSK = "BPSK"
    QPSK = "QPSK"
    PSK8 = "8PSK"
    DSSS = "DSSS"
    FHSS = "FHSS"
    LFM = "LFM"
    OFDM = "OFDM"
    UNKNOWN = "UNKNOWN"
    NOISE = "NOISE"


@dataclass
class ClassificationResult:
    """Waveform classification result"""
    waveform_type: str
    confidence: float  # 0-1
    features: Dict[str, float]


class MLWaveformClassifier:
    """
    ML-based waveform classifier using spectrogram features

    Uses traditional ML (feature extraction + classifier) rather than
    deep learning for deployability without GPU requirements.
    """

    def __init__(self, sample_rate: float):
        self.fs = sample_rate
        self.feature_names = [
            'spectral_flatness',
            'spectral_centroid',
            'bandwidth',
            'peak_to_average',
            'cyclic_peak_ratio',
            'instantaneous_freq_std',
            'phase_variance'
        ]

    def classify_waveform(self, signal_data: np.ndarray) -> ClassificationResult:
        """
        Classify waveform type from IQ samples

        Args:
            signal_data: Complex IQ samples

        Returns:
            ClassificationResult with type and confidence
        """
        # Extract features
        features = self._extract_features(signal_data)

        # Rule-based classification (production would use trained ML model)
        waveform_type, confidence = self._classify_from_features(features)

        return ClassificationResult(
            waveform_type=waveform_type,
            confidence=confidence,
            features=features
        )

    def _extract_features(self, signal_data: np.ndarray) -> Dict[str, float]:
        """
        Extract discriminative features from signal

        Features designed to distinguish between modulation types
        """
        features = {}

        # 1. Spectral flatness (distinguishes spread-spectrum from narrowband)
        f, psd = signal.periodogram(signal_data, fs=self.fs)
        spectral_flatness = np.exp(np.mean(np.log(psd + 1e-12))) / np.mean(psd)
        features['spectral_flatness'] = spectral_flatness

        # 2. Spectral centroid (center frequency)
        spectral_centroid = np.sum(f * psd) / np.sum(psd)
        features['spectral_centroid'] = spectral_centroid / self.fs

        # 3. Bandwidth (occupied bandwidth)
        cumsum_psd = np.cumsum(psd) / np.sum(psd)
        f_low = f[np.where(cumsum_psd > 0.05)[0][0]]
        f_high = f[np.where(cumsum_psd > 0.95)[0][0]]
        bandwidth = (f_high - f_low) / self.fs
        features['bandwidth'] = bandwidth

        # 4. Peak-to-average power ratio (PAPR)
        instantaneous_power = np.abs(signal_data) ** 2
        papr = np.max(instantaneous_power) / np.mean(instantaneous_power)
        features['peak_to_average'] = papr

        # 5. Cyclostationary feature strength
        # Simplified: variance of magnitude
        magnitude = np.abs(signal_data)
        features['cyclic_peak_ratio'] = np.var(magnitude) / np.mean(magnitude)**2

        # 6. Instantaneous frequency standard deviation
        phase = np.unwrap(np.angle(signal_data))
        inst_freq = np.diff(phase) * self.fs / (2 * np.pi)
        features['instantaneous_freq_std'] = np.std(inst_freq) / self.fs

        # 7. Phase variance (constant for PSK, varying for FSK/LFM)
        features['phase_variance'] = np.var(phase)

        return features

    def _classify_from_features(self, features: Dict[str, float]) -> Tuple[str, float]:
        """
        Classify waveform based on extracted features

        Production system would use trained SVM/Random Forest/Neural Network.
        This uses rule-based classification for demonstration.

        Args:
            features: Extracted feature dictionary

        Returns:
            Tuple of (waveform_type, confidence)
        """
        # Decision tree based on feature values

        # Check for noise (very flat spectrum, low variance)
        if features['spectral_flatness'] > 0.9 and features['cyclic_peak_ratio'] < 0.1:
            return WaveformType.NOISE, 0.9

        # Check for spread-spectrum (flat spectrum, high bandwidth)
        if features['spectral_flatness'] > 0.7:
            if features['instantaneous_freq_std'] < 0.05:
                # DSSS (constant frequency)
                return WaveformType.DSSS, 0.8
            else:
                # FHSS (frequency hopping)
                return WaveformType.FHSS, 0.75

        # Check for LFM (linear chirp)
        if features['instantaneous_freq_std'] > 0.1 and features['bandwidth'] > 0.2:
            return WaveformType.LFM, 0.85

        # Check for OFDM (multiple carriers, high PAPR)
        if features['peak_to_average'] > 8.0 and features['bandwidth'] > 0.1:
            return WaveformType.OFDM, 0.75

        # PSK modulations (narrowband, phase modulation)
        if features['bandwidth'] < 0.1 and features['phase_variance'] > 1.0:
            # Distinguish PSK order by cyclostationary features
            if features['cyclic_peak_ratio'] > 1.0:
                return WaveformType.PSK8, 0.7
            elif features['cyclic_peak_ratio'] > 0.5:
                return WaveformType.QPSK, 0.75
            else:
                return WaveformType.BPSK, 0.7

        # Unknown
        return WaveformType.UNKNOWN, 0.3


# Deep learning classifier (placeholder for future implementation)
class CNNWaveformClassifier:
    """
    Convolutional Neural Network for spectrogram-based classification

    Architecture:
    - Input: 128x128 spectrogram
    - Conv2D layers with batch normalization
    - Global average pooling
    - Dense classification layer

    Note: Requires TensorFlow/PyTorch for training
    """

    def __init__(self):
        self.model = None  # Would load pre-trained model

    def classify(self, spectrogram: np.ndarray) -> ClassificationResult:
        """
        Classify waveform from spectrogram

        Args:
            spectrogram: 2D time-frequency representation

        Returns:
            Classification result
        """
        # Placeholder - would use actual CNN inference
        return ClassificationResult(
            waveform_type=WaveformType.UNKNOWN,
            confidence=0.0,
            features={}
        )


# Example usage
if __name__ == "__main__":
    print("ML-Based Waveform Classification")
    print("=" * 60)

    # Simulate different waveform types
    fs = 10e6  # 10 MHz
    duration = 1e-3  # 1 ms
    t = np.arange(0, duration, 1/fs)

    classifier = MLWaveformClassifier(fs)

    # Test 1: BPSK
    print("\nTest 1: BPSK Waveform")
    symbol_rate = 1e6
    symbols = np.random.choice([-1, 1], size=int(duration * symbol_rate))
    symbols_upsampled = np.repeat(symbols, int(fs / symbol_rate))
    bpsk_signal = symbols_upsampled[:len(t)] * np.exp(1j * 2 * np.pi * 2e6 * t)

    result = classifier.classify_waveform(bpsk_signal)
    print(f"  Classification: {result.waveform_type}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Key features: flatness={result.features['spectral_flatness']:.3f}, "
          f"BW={result.features['bandwidth']:.3f}")

    # Test 2: DSSS
    print("\nTest 2: DSSS Waveform")
    chip_rate = 10e6
    chips = np.random.choice([-1, 1], size=len(t))
    dsss_signal = chips * np.exp(1j * 2 * np.pi * 2e6 * t)

    result = classifier.classify_waveform(dsss_signal)
    print(f"  Classification: {result.waveform_type}")
    print(f"  Confidence: {result.confidence:.2f}")

    # Test 3: LFM (Chirp)
    print("\nTest 3: LFM Waveform")
    chirp_bandwidth = 5e6
    chirp_signal = signal.chirp(t, f0=0, f1=chirp_bandwidth, t1=duration, method='linear')
    chirp_signal = chirp_signal.astype(complex)

    result = classifier.classify_waveform(chirp_signal)
    print(f"  Classification: {result.waveform_type}")
    print(f"  Confidence: {result.confidence:.2f}")

    # Test 4: Noise
    print("\nTest 4: White Noise")
    noise_signal = (np.random.randn(len(t)) + 1j * np.random.randn(len(t))) / np.sqrt(2)

    result = classifier.classify_waveform(noise_signal)
    print(f"  Classification: {result.waveform_type}")
    print(f"  Confidence: {result.confidence:.2f}")

    print("\n" + "=" * 60)
    print("ML classification complete.")
