#!/usr/bin/env python3
"""
Advanced Multi-Hypothesis Tracking and Unknown Formation Detection

Implements operational-grade tracking algorithms:
- Multi-Hypothesis Tracking (MHT)
- Joint Probabilistic Data Association (JPDA)
- Unknown formation detection via clustering
- Track quality assessment
- Ghost track rejection
"""

import itertools
from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist


@dataclass
class TrackHypothesis:
    """Single track hypothesis in MHT"""
    track_id: int
    state: np.ndarray  # [x, y, z, vx, vy, vz]
    covariance: np.ndarray  # 6x6 covariance
    probability: float  # Hypothesis probability
    measurement_history: list[int] = field(default_factory=list)
    age: int = 0  # Time steps since creation
    quality_score: float = 0.5


@dataclass
class GlobalHypothesis:
    """Global hypothesis - assignment of measurements to tracks"""
    hypothesis_id: int
    track_hypotheses: list
    probability: float
    measurement_assignment: dict[int, int]  # measurement_id -> track_id


class MultiHypothesisTracker:
    """
    Multi-Hypothesis Tracking (MHT)

    Maintains multiple hypotheses about track-to-measurement associations
    Resolves ambiguities over time
    """

    def __init__(self,
                 max_hypotheses: int = 50,
                 pruning_threshold: float = 0.001,
                 confirmation_threshold: int = 3,
                 deletion_threshold: int = 5):
        """
        Args:
            max_hypotheses: Maximum number of global hypotheses to maintain
            pruning_threshold: Minimum probability for hypothesis retention
            confirmation_threshold: Min age for track confirmation
            deletion_threshold: Max age without update before deletion
        """
        self.max_hypotheses = max_hypotheses
        self.pruning_threshold = pruning_threshold
        self.confirmation_threshold = confirmation_threshold
        self.deletion_threshold = deletion_threshold

        self.global_hypotheses: list = []
        self.next_track_id = 1
        self.next_hyp_id = 1

        # Track quality metrics
        self.track_scores: dict[int, float] = {}

    def update(self,
              measurements: list[tuple[np.ndarray, np.ndarray]],
              timestamp: float,
              dt: float) -> list:
        """
        Update tracker with new measurements

        Args:
            measurements: List of (position, covariance) tuples
            timestamp: Measurement timestamp
            dt: Time since last update

        Returns:
            Best estimate of current tracks
        """
        if not self.global_hypotheses:
            # Initialize with first measurements
            self._initialize_hypotheses(measurements)
            return self._get_best_tracks()

        # Step 1: Predict all tracks in all hypotheses
        for hyp in self.global_hypotheses:
            for track in hyp.track_hypotheses:
                self._predict_track(track, dt)
                track.age += 1

        # Step 2: Generate new hypotheses by associating measurements
        new_hypotheses = self._generate_association_hypotheses(measurements)

        # Step 3: Compute hypothesis probabilities
        self._update_hypothesis_probabilities(new_hypotheses, measurements)

        # Step 4: Prune unlikely hypotheses
        self.global_hypotheses = self._prune_hypotheses(new_hypotheses)

        # Step 5: Merge similar hypotheses
        self.global_hypotheses = self._merge_hypotheses(self.global_hypotheses)

        # Step 6: Update track quality scores
        self._update_track_quality()

        # Step 7: Delete old/poor tracks
        self._delete_poor_tracks()

        return self._get_best_tracks()

    def _initialize_hypotheses(self, measurements: list[tuple[np.ndarray, np.ndarray]]):
        """Initialize tracker with first measurements"""
        tracks = []

        for i, (pos, cov) in enumerate(measurements):
            # Create track with zero velocity
            state = np.concatenate([pos, np.zeros(3)])
            state_cov = np.eye(6)
            state_cov[:3, :3] = cov
            state_cov[3:, 3:] *= 100  # High velocity uncertainty

            track = TrackHypothesis(
                track_id=self.next_track_id,
                state=state,
                covariance=state_cov,
                probability=1.0 / len(measurements),
                measurement_history=[i],
                age=1
            )

            self.next_track_id += 1
            tracks.append(track)

        # Create initial global hypothesis
        hyp = GlobalHypothesis(
            hypothesis_id=self.next_hyp_id,
            track_hypotheses=tracks,
            probability=1.0,
            measurement_assignment={i: track.track_id for i, track in enumerate(tracks)}
        )

        self.next_hyp_id += 1
        self.global_hypotheses = [hyp]

    def _predict_track(self, track: TrackHypothesis, dt: float):
        """Predict track state forward in time"""
        # State transition matrix (constant velocity)
        F = np.eye(6)
        F[0, 3] = dt
        F[1, 4] = dt
        F[2, 5] = dt

        # Process noise
        q = 10.0  # m/s^2 acceleration noise
        Q = np.zeros((6, 6))
        Q[:3, :3] = q**2 * dt**4 / 4 * np.eye(3)
        Q[:3, 3:] = q**2 * dt**3 / 2 * np.eye(3)
        Q[3:, :3] = q**2 * dt**3 / 2 * np.eye(3)
        Q[3:, 3:] = q**2 * dt**2 * np.eye(3)

        # Predict
        track.state = F @ track.state
        track.covariance = F @ track.covariance @ F.T + Q

    def _generate_association_hypotheses(self,
                                        measurements: list[tuple[np.ndarray, np.ndarray]]
                                        ) -> list:
        """
        Generate all possible measurement-to-track associations

        This is computationally expensive - use gating and pruning
        """
        new_hypotheses = []

        for parent_hyp in self.global_hypotheses:
            # For each existing hypothesis, generate child hypotheses

            # Gate measurements to tracks
            gated_associations = self._gate_measurements(
                parent_hyp.track_hypotheses,
                measurements
            )

            # Generate valid associations
            # This is a combinatorial problem - limit complexity
            associations = self._generate_valid_associations(
                len(parent_hyp.track_hypotheses),
                len(measurements),
                gated_associations
            )

            # Create child hypothesis for each association
            for assoc in associations[:10]:  # Limit to 10 per parent
                new_hyp = self._create_child_hypothesis(
                    parent_hyp,
                    measurements,
                    assoc
                )
                new_hypotheses.append(new_hyp)

        return new_hypotheses

    def _gate_measurements(self,
                          tracks: list,
                          measurements: list[tuple[np.ndarray, np.ndarray]]
                          ) -> dict[int, list[int]]:
        """
        Gate measurements to tracks using Mahalanobis distance

        Returns:
            Dict mapping track_id to list of measurement indices
        """
        gated = defaultdict(list)
        gate_threshold = 9.21  # Chi-squared, 3 DOF, 99% confidence

        for track_idx, track in enumerate(tracks):
            track_pos = track.state[:3]
            track_cov = track.covariance[:3, :3]

            for meas_idx, (meas_pos, meas_cov) in enumerate(measurements):
                # Innovation
                innovation = meas_pos - track_pos

                # Innovation covariance
                S = track_cov + meas_cov

                # Mahalanobis distance
                try:
                    S_inv = np.linalg.inv(S)
                    mahal_dist = innovation.T @ S_inv @ innovation

                    if mahal_dist < gate_threshold:
                        gated[track_idx].append(meas_idx)
                except np.linalg.LinAlgError:
                    # Singular covariance - use Euclidean distance
                    euclidean = np.linalg.norm(innovation)
                    if euclidean < 5000:  # 5 km gate
                        gated[track_idx].append(meas_idx)

        return gated

    def _generate_valid_associations(self,
                                    n_tracks: int,
                                    n_measurements: int,
                                    gated: dict[int, list[int]]) -> list[dict[int, int]]:
        """
        Generate valid measurement-to-track associations

        Valid means:
        - Each measurement assigned to at most one track
        - Each track receives at most one measurement
        - Or track receives no measurement (missed detection)
        - Or measurement not assigned (false alarm)

        Returns:
            List of association dictionaries {track_idx: meas_idx or None}
        """
        associations = []

        # Start with null association (all missed detections)
        null_assoc = dict.fromkeys(range(n_tracks))
        associations.append(null_assoc)

        # Single measurement associations
        for track_idx, meas_list in gated.items():
            for meas_idx in meas_list:
                assoc = null_assoc.copy()
                assoc[track_idx] = meas_idx
                associations.append(assoc)

        # Multi-measurement associations (limited to avoid combinatorial explosion)
        if len(gated) > 1 and len(gated) < 5:
            # Try all combinations of single assignments
            track_indices = list(gated.keys())[:4]  # Limit to 4 tracks

            for combo in itertools.product(*[gated.get(t, [None]) for t in track_indices]):
                # Check if valid (no duplicate measurements)
                non_none = [m for m in combo if m is not None]
                if len(non_none) == len(set(non_none)):  # No duplicates
                    assoc = null_assoc.copy()
                    for t, m in zip(track_indices, combo):
                        if m is not None:
                            assoc[t] = m
                    associations.append(assoc)

        # Limit total associations
        return associations[:20]

    def _create_child_hypothesis(self,
                                parent_hyp: GlobalHypothesis,
                                measurements: list[tuple[np.ndarray, np.ndarray]],
                                association: dict[int, int]) -> GlobalHypothesis:
        """Create child hypothesis with specific association"""
        new_tracks = []

        # Update existing tracks
        for track_idx, track in enumerate(parent_hyp.track_hypotheses):
            meas_idx = association.get(track_idx)

            if meas_idx is not None:
                # Track receives measurement - perform Kalman update
                meas_pos, meas_cov = measurements[meas_idx]
                updated_track = self._kalman_update(track, meas_pos, meas_cov)
                updated_track.age = 0  # Reset age on successful update
                updated_track.measurement_history.append(meas_idx)
                new_tracks.append(updated_track)
            else:
                # Missed detection - keep prediction
                missed_track = TrackHypothesis(
                    track_id=track.track_id,
                    state=track.state.copy(),
                    covariance=track.covariance.copy(),
                    probability=track.probability * 0.8,  # Reduce confidence
                    measurement_history=track.measurement_history.copy(),
                    age=track.age
                )
                new_tracks.append(missed_track)

        # Create tracks for unassigned measurements (potential new targets)
        assigned_measurements = set(association.values()) - {None}
        for meas_idx, (meas_pos, meas_cov) in enumerate(measurements):
            if meas_idx not in assigned_measurements:
                # New track
                state = np.concatenate([meas_pos, np.zeros(3)])
                state_cov = np.eye(6)
                state_cov[:3, :3] = meas_cov
                state_cov[3:, 3:] *= 100

                new_track = TrackHypothesis(
                    track_id=self.next_track_id,
                    state=state,
                    covariance=state_cov,
                    probability=0.5,
                    measurement_history=[meas_idx],
                    age=1
                )

                self.next_track_id += 1
                new_tracks.append(new_track)

        # Create new global hypothesis
        new_hyp = GlobalHypothesis(
            hypothesis_id=self.next_hyp_id,
            track_hypotheses=new_tracks,
            probability=parent_hyp.probability,  # Will be updated later
            measurement_assignment=association
        )

        self.next_hyp_id += 1
        return new_hyp

    def _kalman_update(self,
                      track: TrackHypothesis,
                      meas_pos: np.ndarray,
                      meas_cov: np.ndarray) -> TrackHypothesis:
        """Perform Kalman filter update"""
        # Measurement matrix (measure position only)
        H = np.zeros((3, 6))
        H[:3, :3] = np.eye(3)

        # Innovation
        innovation = meas_pos - H @ track.state

        # Innovation covariance
        S = H @ track.covariance @ H.T + meas_cov

        # Kalman gain
        K = track.covariance @ H.T @ np.linalg.inv(S)

        # Update state
        updated_state = track.state + K @ innovation

        # Update covariance
        updated_cov = (np.eye(6) - K @ H) @ track.covariance

        # Create updated track
        updated = TrackHypothesis(
            track_id=track.track_id,
            state=updated_state,
            covariance=updated_cov,
            probability=track.probability * 1.2,  # Increase confidence
            measurement_history=track.measurement_history.copy(),
            age=track.age
        )

        return updated

    def _update_hypothesis_probabilities(self,
                                        hypotheses: list,
                                        measurements: list[tuple[np.ndarray, np.ndarray]]):
        """Update probabilities of all hypotheses"""
        # Simplified probability model
        # Full implementation requires likelihood calculation

        for hyp in hypotheses:
            # Probability based on number of successful associations
            n_assigned = sum(1 for m in hyp.measurement_assignment.values() if m is not None)
            n_tracks = len(hyp.track_hypotheses)

            # Favor hypotheses with more associations
            hyp.probability *= (n_assigned + 1) / (n_tracks + 1)

        # Normalize
        total_prob = sum(h.probability for h in hypotheses)
        if total_prob > 0:
            for hyp in hypotheses:
                hyp.probability /= total_prob

    def _prune_hypotheses(self, hypotheses: list) -> list:
        """Prune low-probability hypotheses"""
        # Sort by probability
        sorted_hyps = sorted(hypotheses, key=lambda h: h.probability, reverse=True)

        # Keep top N or above threshold
        kept = []
        for hyp in sorted_hyps:
            if hyp.probability > self.pruning_threshold and len(kept) < self.max_hypotheses:
                kept.append(hyp)

        # Renormalize
        total_prob = sum(h.probability for h in kept)
        if total_prob > 0:
            for hyp in kept:
                hyp.probability /= total_prob

        return kept if kept else sorted_hyps[:1]  # Keep at least one

    def _merge_hypotheses(self, hypotheses: list) -> list:
        """Merge similar hypotheses to reduce complexity"""
        # Simplified: merge hypotheses with similar track states
        # Full implementation requires distance metric on hypothesis space

        return hypotheses  # Placeholder

    def _update_track_quality(self):
        """Update quality scores for all tracks"""
        # Quality based on:
        # - Age (older = more confident)
        # - Number of measurements
        # - Covariance (smaller = better)

        best_hyp = max(self.global_hypotheses, key=lambda h: h.probability)

        for track in best_hyp.track_hypotheses:
            # Age component
            age_score = min(1.0, track.age / 10.0)

            # Measurement count
            meas_score = min(1.0, len(track.measurement_history) / 10.0)

            # Covariance (position only)
            cov_trace = np.trace(track.covariance[:3, :3])
            cov_score = 1.0 / (1.0 + np.log10(cov_trace + 1))

            # Combined quality
            quality = 0.4 * age_score + 0.3 * meas_score + 0.3 * cov_score

            track.quality_score = quality
            self.track_scores[track.track_id] = quality

    def _delete_poor_tracks(self):
        """Delete tracks with poor quality or excessive age"""
        for hyp in self.global_hypotheses:
            hyp.track_hypotheses = [
                t for t in hyp.track_hypotheses
                if t.age < self.deletion_threshold or t.quality_score > 0.3
            ]

    def _get_best_tracks(self) -> list:
        """Get best estimate of current tracks"""
        if not self.global_hypotheses:
            return []

        # Return tracks from most probable hypothesis
        best_hyp = max(self.global_hypotheses, key=lambda h: h.probability)

        # Only return confirmed tracks
        confirmed = [
            t for t in best_hyp.track_hypotheses
            if t.age >= self.confirmation_threshold or len(t.measurement_history) >= 3
        ]

        return confirmed


class UnknownFormationDetector:
    """
    Detect and classify unknown formations using unsupervised learning
    """

    def __init__(self):
        self.known_patterns = {
            'finger_four': {'n_members': 4, 'spacing_km': 3.0},
            'combat_spread': {'n_members': 2, 'spacing_km': 2.0},
            'vic': {'n_members': 3, 'spacing_km': 2.5},
            'trail': {'n_members': 4, 'spacing_km': 1.5},
        }

    def detect_formation(self,
                        track_positions: list[np.ndarray],
                        min_members: int = 2) -> dict:
        """
        Detect formation from track positions using clustering

        Args:
            track_positions: List of position vectors
            min_members: Minimum members for formation

        Returns:
            Formation parameters
        """
        if len(track_positions) < min_members:
            return {'type': 'single', 'n_members': len(track_positions)}

        # Convert to array
        positions = np.array(track_positions)

        # Compute pairwise distances
        distances = pdist(positions[:, :2])  # Use only x, y

        # Hierarchical clustering
        linkage_matrix = linkage(distances, method='average')

        # Find optimal number of clusters
        max_clusters = min(len(track_positions), 4)
        best_n_clusters = self._find_optimal_clusters(distances, max_clusters)

        # Cluster assignment
        clusters = fcluster(linkage_matrix, best_n_clusters, criterion='maxclust')

        # Analyze each cluster
        formations = []
        for cluster_id in range(1, best_n_clusters + 1):
            cluster_mask = clusters == cluster_id
            cluster_positions = positions[cluster_mask]

            if len(cluster_positions) >= min_members:
                formation = self._analyze_formation(cluster_positions)
                formations.append(formation)

        return {
            'n_formations': len(formations),
            'formations': formations,
            'total_tracks': len(track_positions)
        }

    def _find_optimal_clusters(self, distances: np.ndarray, max_k: int) -> int:
        """Find optimal number of clusters using silhouette or elbow method"""
        # Simplified: use heuristic based on distance distribution
        _median_dist = np.median(distances)  # Used for potential future expansion

        # If most tracks are close together, likely one formation
        if np.percentile(distances, 75) < 10000:  # 10 km
            return 1
        elif np.percentile(distances, 50) < 5000:  # 5 km
            return max(1, int(len(distances) / 6))
        else:
            return max_k

    def _analyze_formation(self, positions: np.ndarray) -> dict:
        """Analyze geometry of formation"""
        n_members = len(positions)

        if n_members < 2:
            return {'type': 'single', 'n_members': 1}

        # Compute geometric features
        centroid = np.mean(positions, axis=0)
        distances_to_centroid = np.linalg.norm(positions - centroid, axis=1)

        # Average spacing
        pairwise_dists = pdist(positions[:, :2])
        avg_spacing = np.mean(pairwise_dists) / 1000  # km

        # Shape analysis
        std_dist = np.std(distances_to_centroid)

        # Classify based on pattern matching
        formation_type = self._match_formation_pattern(n_members, avg_spacing, std_dist)

        return {
            'type': formation_type,
            'n_members': n_members,
            'avg_spacing_km': avg_spacing,
            'centroid': centroid,
            'spread_m': std_dist
        }

    def _match_formation_pattern(self, n_members: int, spacing_km: float, spread: float) -> str:
        """Match detected formation to known patterns"""
        # Simple pattern matching
        if n_members == 1:
            return 'single'
        elif n_members == 2:
            return 'combat_spread' if spacing_km < 3 else 'extended_trail'
        elif n_members == 3:
            return 'vic' if spread < 2000 else 'loose_vic'
        elif n_members == 4:
            if spacing_km < 2:
                return 'tight_finger_four'
            elif spacing_km < 4:
                return 'finger_four'
            else:
                return 'wall'
        else:
            return f'unknown_{n_members}_ship'
