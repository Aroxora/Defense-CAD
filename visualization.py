#!/usr/bin/env python3
"""
Network and Geolocation Visualization

Provides visualization tools for:
- Emitter positions and tracks
- Communication network topology
- ESM platform positions
- Detection coverage areas
- Geolocation uncertainty ellipses
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
from typing import List, Dict, Tuple, Optional
from geolocation_network import EmitterTrack, NetworkLink, PlatformState


class TacticalDisplay:
    """
    Tactical situation display for EW operations

    Visualizes the electromagnetic battlefield with emitters,
    platforms, and communication links.
    """

    def __init__(self, figsize=(14, 10)):
        """
        Args:
            figsize: Figure size (width, height) in inches
        """
        self.fig = plt.figure(figsize=figsize)
        self.ax_map = self.fig.add_subplot(121)  # 2D map view
        self.ax_3d = self.fig.add_subplot(122, projection='3d')  # 3D view

        # Styling
        self.ax_map.set_facecolor('#0a0a0a')
        self.fig.patch.set_facecolor('#1a1a1a')
        self.ax_map.grid(True, alpha=0.3, color='#00ff00', linestyle=':')

    def plot_platform(self, platform: PlatformState, color='#00ff00', label=None):
        """
        Plot ESM platform position

        Args:
            platform: Platform state
            color: Platform marker color
            label: Platform label
        """
        x, y, z = platform.position / 1000  # Convert to km

        # 2D plot
        self.ax_map.plot(x, y, '^', color=color, markersize=12,
                        label=label or platform.platform_id, markeredgecolor='white')

        # Add platform ID text
        self.ax_map.text(x, y + 5, platform.platform_id,
                        color='white', fontsize=8, ha='center')

        # 3D plot
        self.ax_3d.scatter(x, y, z, marker='^', color=color, s=100)

        # Velocity vector
        if np.linalg.norm(platform.velocity) > 0:
            vx, vy, vz = platform.velocity * 10  # Scale for visibility
            self.ax_3d.quiver(x, y, z, vx/1000, vy/1000, vz/1000,
                            color=color, alpha=0.6, arrow_length_ratio=0.3)

    def plot_emitter(self, track: EmitterTrack, color='#ff0000', show_uncertainty=True):
        """
        Plot emitter position with uncertainty

        Args:
            track: Emitter track
            color: Emitter marker color
            show_uncertainty: Whether to show uncertainty ellipse
        """
        x, y, z = track.position / 1000  # Convert to km

        # 2D plot
        self.ax_map.plot(x, y, 'o', color=color, markersize=10,
                        markeredgecolor='white', label=f'Target {track.track_id}')

        # Add track ID
        self.ax_map.text(x, y + 5, f'T{track.track_id}',
                        color='white', fontsize=8, ha='center')

        # Uncertainty ellipse
        if show_uncertainty and track.position_covariance is not None:
            # Extract 2D covariance
            cov_2d = track.position_covariance[:2, :2]

            # Eigenvalue decomposition for ellipse parameters
            eigenvalues, eigenvectors = np.linalg.eig(cov_2d)

            # Sort by eigenvalue
            idx = eigenvalues.argsort()[::-1]
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]

            # Ellipse angle
            angle = np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))

            # 95% confidence ellipse (2.45 * sigma for 2D)
            width = 2 * np.sqrt(5.991 * eigenvalues[0]) / 1000  # Convert to km
            height = 2 * np.sqrt(5.991 * eigenvalues[1]) / 1000

            ellipse = Ellipse((x, y), width, height, angle=angle,
                            facecolor='none', edgecolor=color,
                            linestyle='--', alpha=0.5, linewidth=2)
            self.ax_map.add_patch(ellipse)

        # 3D plot
        self.ax_3d.scatter(x, y, z, marker='o', color=color, s=100,
                          edgecolors='white')

        # Velocity vector
        if np.linalg.norm(track.velocity) > 0:
            vx, vy, vz = track.velocity * 10  # Scale for visibility
            self.ax_3d.quiver(x, y, z, vx/1000, vy/1000, vz/1000,
                            color=color, alpha=0.6, arrow_length_ratio=0.3)

    def plot_link(self, emitter_a: EmitterTrack, emitter_b: EmitterTrack,
                 link: NetworkLink, color='#00ffff'):
        """
        Plot communication link between emitters

        Args:
            emitter_a: First emitter
            emitter_b: Second emitter
            link: Link information
            color: Link color
        """
        x1, y1, z1 = emitter_a.position / 1000
        x2, y2, z2 = emitter_b.position / 1000

        # Line style based on link strength
        alpha = link.strength
        linewidth = 1 + link.strength * 2

        # 2D plot
        self.ax_map.plot([x1, x2], [y1, y2], color=color,
                        alpha=alpha, linewidth=linewidth,
                        linestyle='-' if link.bidirectional else '--')

        # Add link strength annotation
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        self.ax_map.text(mid_x, mid_y, f'{link.strength:.2f}',
                        color=color, fontsize=7, ha='center',
                        bbox={'boxstyle': 'round,pad=0.3', 'facecolor': 'black', 'alpha': 0.7})

        # 3D plot
        self.ax_3d.plot([x1, x2], [y1, y2], [z1, z2],
                       color=color, alpha=alpha, linewidth=linewidth)

    def plot_detection_range(self, platform: PlatformState,
                            detection_range_km: float,
                            color='#00ff00', alpha=0.1):
        """
        Plot detection range circle around platform

        Args:
            platform: Platform state
            detection_range_km: Detection range in km
            color: Circle color
            alpha: Transparency
        """
        x, y, _ = platform.position / 1000

        circle = Circle((x, y), detection_range_km,
                       facecolor=color, edgecolor=color,
                       alpha=alpha, linewidth=1.5, linestyle=':')
        self.ax_map.add_patch(circle)

    def plot_antenna_beam(self, emitter: EmitterTrack,
                         azimuth: float, beamwidth: float = 3.0,
                         range_km: float = 100, color='#ff9900'):
        """
        Plot directional antenna beam

        Args:
            emitter: Emitter track
            azimuth: Beam azimuth (degrees)
            beamwidth: 3dB beamwidth (degrees)
            range_km: Beam range for visualization (km)
            color: Beam color
        """
        x, y, _ = emitter.position / 1000

        # Create beam as wedge
        from matplotlib.patches import Wedge

        wedge = Wedge((x, y), range_km,
                     azimuth - beamwidth / 2,
                     azimuth + beamwidth / 2,
                     facecolor=color, edgecolor=color,
                     alpha=0.3, linewidth=2)
        self.ax_map.add_patch(wedge)

    def plot_network_graph(self, tracks: Dict[int, EmitterTrack],
                          links: List[NetworkLink], ax=None):
        """
        Plot network topology as a graph

        Args:
            tracks: Dictionary of emitter tracks
            links: List of network links
            ax: Matplotlib axis (creates new if None)
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.set_facecolor('#0a0a0a')

        # Build NetworkX graph
        G = nx.Graph()

        # Add nodes
        for track_id, track in tracks.items():
            G.add_node(track_id, confidence=track.confidence)

        # Add edges
        for link in links:
            G.add_edge(link.emitter_a, link.emitter_b,
                      weight=link.strength)

        # Layout
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Draw nodes
        node_colors = ['#ff0000' if tracks[n].confidence > 0.7 else '#ff9900'
                      for n in G.nodes()]
        node_sizes = [tracks[n].confidence * 1000 for n in G.nodes()]

        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                              node_size=node_sizes, ax=ax)

        # Draw edges
        edge_widths = [G[u][v]['weight'] * 5 for u, v in G.edges()]
        nx.draw_networkx_edges(G, pos, width=edge_widths,
                              alpha=0.6, edge_color='#00ffff', ax=ax)

        # Draw labels
        labels = {n: f'T{n}' for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_color='white',
                               font_size=10, ax=ax)

        ax.set_title('Network Topology', color='white', fontsize=14)
        ax.axis('off')

    def finalize(self, title='Tactical Electronic Warfare Display'):
        """
        Finalize and display the plot

        Args:
            title: Plot title
        """
        # 2D map styling
        self.ax_map.set_xlabel('East (km)', color='white')
        self.ax_map.set_ylabel('North (km)', color='white')
        self.ax_map.set_title('2D Tactical Map', color='white', fontsize=12)
        self.ax_map.tick_params(colors='white')
        self.ax_map.legend(facecolor='#1a1a1a', edgecolor='white',
                          labelcolor='white', fontsize=8)
        self.ax_map.set_aspect('equal')

        # 3D view styling
        self.ax_3d.set_xlabel('East (km)', color='white')
        self.ax_3d.set_ylabel('North (km)', color='white')
        self.ax_3d.set_zlabel('Altitude (km)', color='white')
        self.ax_3d.set_title('3D View', color='white', fontsize=12)
        self.ax_3d.tick_params(colors='white')
        self.ax_3d.xaxis.pane.fill = False
        self.ax_3d.yaxis.pane.fill = False
        self.ax_3d.zaxis.pane.fill = False

        # Overall title
        self.fig.suptitle(title, color='white', fontsize=16, fontweight='bold')

        plt.tight_layout()


class DetectionPerformanceAnalyzer:
    """
    Analyze and visualize detection performance

    Creates plots for:
    - Detection probability vs range
    - SNR vs integration time
    - Geolocation accuracy vs geometry
    """

    @staticmethod
    def plot_detection_probability(integration_times: np.ndarray,
                                   snr_values: np.ndarray,
                                   pfa: float = 1e-6):
        """
        Plot detection probability vs SNR for various integration times

        Args:
            integration_times: Array of integration times (seconds)
            snr_values: Array of SNR values (dB)
            pfa: Probability of false alarm
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor('#0a0a0a')
        fig.patch.set_facecolor('#1a1a1a')

        # Calculate detection probability (simplified Swerling 0 model)
        for int_time in integration_times:
            # Processing gain
            pg = 10 * np.log10(int_time * 1e9)  # Assume 1 GHz bandwidth

            # Effective SNR after integration
            snr_eff = snr_values + pg

            # Detection probability (approximation)
            # Using Neyman-Pearson detector
            threshold_snr = -5  # Simplified threshold for Pfa = 1e-6

            pd = 1 / (1 + np.exp(-2 * (snr_eff - threshold_snr)))

            ax.plot(snr_values, pd, linewidth=2,
                   label=f'Integration: {int_time*1e6:.1f} μs')

        ax.set_xlabel('Input SNR (dB)', color='white', fontsize=12)
        ax.set_ylabel('Detection Probability', color='white', fontsize=12)
        ax.set_title('Detection Performance vs Integration Time',
                    color='white', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, color='#00ff00', linestyle=':')
        ax.legend(facecolor='#1a1a1a', edgecolor='white',
                 labelcolor='white', fontsize=10)
        ax.tick_params(colors='white')

        plt.tight_layout()
        return fig

    @staticmethod
    def plot_geolocation_accuracy(baseline_km: np.ndarray,
                                  timing_accuracy_ns: float = 10,
                                  crossing_angles: Optional[List[float]] = None):
        """
        Plot geolocation accuracy vs baseline

        Args:
            baseline_km: Array of baseline distances (km)
            timing_accuracy_ns: Timing accuracy (nanoseconds)
            crossing_angles: List of crossing angles (degrees)
        """
        if crossing_angles is None:
            crossing_angles = [30, 60, 90]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor('#0a0a0a')
        fig.patch.set_facecolor('#1a1a1a')

        c = 299792458  # Speed of light (m/s)
        timing_acc_s = timing_accuracy_ns * 1e-9

        for angle in crossing_angles:
            # GDOP approximation
            gdop = 1.0 / np.sin(np.radians(angle))

            # CEP = c * timing_uncertainty * GDOP
            cep = c * timing_acc_s * gdop / 1000  # Convert to km

            # Position error doesn't scale with baseline directly,
            # but let's show relative improvement
            position_error = cep * np.ones_like(baseline_km)

            ax.plot(baseline_km, position_error, linewidth=2,
                   label=f'Crossing Angle: {angle}°')

        ax.set_xlabel('Platform Baseline (km)', color='white', fontsize=12)
        ax.set_ylabel('Position Error CEP (km)', color='white', fontsize=12)
        ax.set_title(f'TDOA Geolocation Accuracy ({timing_accuracy_ns} ns timing)',
                    color='white', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, color='#00ff00', linestyle=':')
        ax.legend(facecolor='#1a1a1a', edgecolor='white',
                 labelcolor='white', fontsize=10)
        ax.tick_params(colors='white')
        ax.set_yscale('log')

        plt.tight_layout()
        return fig


# Example usage
if __name__ == "__main__":
    print("Tactical Display Visualization")
    print("=" * 60)

    # Create display
    display = TacticalDisplay()

    # Create platforms
    platforms = [
        PlatformState("ESM-1", np.array([0, 0, 10000]), np.array([200, 0, 0]), 0),
        PlatformState("ESM-2", np.array([100000, 0, 10000]), np.array([200, 0, 0]), 0),
        PlatformState("ESM-3", np.array([50000, 86600, 10000]), np.array([200, 0, 0]), 0),
    ]

    # Plot platforms
    for platform in platforms:
        display.plot_platform(platform)
        display.plot_detection_range(platform, 75)  # 75 km detection range

    # Create emitter tracks
    from geolocation_network import EmitterTrack
    tracks = {
        1: EmitterTrack(1, np.array([50000, 0, 35000]), np.array([250, 0, 0]),
                       np.eye(3) * 500**2, 0, confidence=0.9),
        2: EmitterTrack(2, np.array([48000, -5000, 35000]), np.array([250, 0, 0]),
                       np.eye(3) * 800**2, 0, confidence=0.8),
        3: EmitterTrack(3, np.array([48000, 5000, 35000]), np.array([250, 0, 0]),
                       np.eye(3) * 600**2, 0, confidence=0.85),
    }

    # Plot emitters
    for track in tracks.values():
        display.plot_emitter(track, show_uncertainty=True)
        display.plot_antenna_beam(track, azimuth=90, beamwidth=3.0)

    # Create links
    from geolocation_network import NetworkLink
    links = [
        NetworkLink(1, 2, strength=0.9, last_observed=0, observations=15, bidirectional=True),
        NetworkLink(1, 3, strength=0.85, last_observed=0, observations=12, bidirectional=True),
        NetworkLink(2, 3, strength=0.6, last_observed=0, observations=8, bidirectional=True),
    ]

    # Plot links
    for link in links:
        display.plot_link(tracks[link.emitter_a], tracks[link.emitter_b], link)

    # Finalize display
    display.finalize('F-35 MADL Network Detection - Scenario')

    # Create performance analysis plots
    print("\nGenerating performance analysis plots...")

    analyzer = DetectionPerformanceAnalyzer()

    # Detection probability
    integration_times = np.array([10e-6, 50e-6, 100e-6, 500e-6])  # 10-500 μs
    snr_values = np.linspace(-20, 10, 100)
    fig1 = analyzer.plot_detection_probability(integration_times, snr_values)

    # Geolocation accuracy
    baselines = np.linspace(10, 200, 50)  # 10-200 km
    fig2 = analyzer.plot_geolocation_accuracy(baselines, timing_accuracy_ns=10)

    # Network topology
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    display.plot_network_graph(tracks, links, ax3)

    print("\nVisualization complete. Close plots to exit.")
    plt.show()
