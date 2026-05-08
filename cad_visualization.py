#!/usr/bin/env python3
"""
CAD Engagement Visualization Module

Provides 3D visualization capabilities for engagement geometry, missile
trajectories, and detection envelopes. Uses matplotlib for basic 3D plots
with optional PyVista/VTK integration for advanced rendering.

Key Features:
- 3D engagement geometry visualization
- Missile trajectory rendering
- Radar detection envelope display
- Platform position and orientation
- RCS polar plots
- Time-series engagement animation export
- STL mesh export for external tools

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as mpatches

from cad_geometry import (
    Point3D, Vector3D, TriangleMesh, Triangle, BoundingBox,
    MissileCADModel, CADGeometryResult,
    create_pl15_cad_model, create_aim120_cad_model
)


class PlatformSymbol(Enum):
    """Standard military symbology for platforms"""
    FIGHTER = "fighter"
    AWACS = "awacs"
    TANKER = "tanker"
    MISSILE = "missile"
    SHIP = "ship"
    SAM_SITE = "sam"
    RADAR = "radar"


@dataclass
class PlatformState:
    """Platform position and state for visualization"""
    name: str
    platform_type: PlatformSymbol
    position: Point3D
    velocity: Vector3D
    heading_deg: float
    altitude_m: float
    is_hostile: bool = False
    color: str = None

    def __post_init__(self):
        if self.color is None:
            self.color = 'red' if self.is_hostile else 'blue'


@dataclass
class TrajectoryPoint:
    """Single point in a trajectory"""
    time_s: float
    position: Point3D
    velocity: Vector3D
    state: str = "active"  # "active", "terminal", "intercept", "miss"


@dataclass
class Trajectory:
    """Complete trajectory with time history"""
    name: str
    points: List[TrajectoryPoint] = field(default_factory=list)
    color: str = "orange"
    line_style: str = "-"

    def to_arrays(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convert to numpy arrays for plotting"""
        x = np.array([p.position.x for p in self.points])
        y = np.array([p.position.y for p in self.points])
        z = np.array([p.position.z for p in self.points])
        return x, y, z


@dataclass
class DetectionEnvelope:
    """Radar detection envelope for visualization"""
    name: str
    center: Point3D
    max_range_km: float
    min_range_km: float = 0
    azimuth_coverage_deg: Tuple[float, float] = (0, 360)
    elevation_coverage_deg: Tuple[float, float] = (-5, 60)
    color: str = "cyan"
    alpha: float = 0.2


@dataclass
class EngagementScenario:
    """Complete engagement scenario for visualization"""
    name: str
    platforms: List[PlatformState] = field(default_factory=list)
    trajectories: List[Trajectory] = field(default_factory=list)
    detection_envelopes: List[DetectionEnvelope] = field(default_factory=list)
    time_range_s: Tuple[float, float] = (0, 300)
    spatial_bounds_km: Tuple[float, float, float] = (500, 500, 50)


class EngagementVisualizer:
    """
    3D engagement geometry visualization using matplotlib.

    Provides tactical display of platforms, trajectories, and sensor coverage.
    """

    def __init__(self, figsize: Tuple[int, int] = (14, 10)):
        self.figsize = figsize
        self.fig = None
        self.ax = None

    def create_figure(self) -> Tuple[plt.Figure, Axes3D]:
        """Create a new 3D figure"""
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')
        return self.fig, self.ax

    def plot_platform(self, platform: PlatformState, scale: float = 10):
        """Plot a platform symbol at its position"""
        x, y, z = platform.position.x, platform.position.y, platform.position.z

        # Convert to km for display
        x_km, y_km, z_km = x / 1000, y / 1000, z / 1000

        marker = self._get_platform_marker(platform.platform_type)

        self.ax.scatter([x_km], [y_km], [z_km],
                        marker=marker,
                        s=100 * scale,
                        c=platform.color,
                        label=platform.name,
                        alpha=0.8,
                        edgecolors='black',
                        linewidths=1)

        # Draw velocity vector
        if platform.velocity.magnitude() > 1:
            vel_scale = 0.01  # Scale factor for velocity arrow
            vx = platform.velocity.dx * vel_scale
            vy = platform.velocity.dy * vel_scale
            vz = platform.velocity.dz * vel_scale

            self.ax.quiver(x_km, y_km, z_km,
                           vx, vy, vz,
                           color=platform.color,
                           alpha=0.5,
                           arrow_length_ratio=0.3)

    def plot_trajectory(self, trajectory: Trajectory):
        """Plot a trajectory path"""
        x, y, z = trajectory.to_arrays()

        # Convert to km
        x_km, y_km, z_km = x / 1000, y / 1000, z / 1000

        self.ax.plot(x_km, y_km, z_km,
                     color=trajectory.color,
                     linestyle=trajectory.line_style,
                     linewidth=2,
                     label=trajectory.name,
                     alpha=0.8)

        # Mark start and end points
        if len(x_km) > 0:
            self.ax.scatter([x_km[0]], [y_km[0]], [z_km[0]],
                            marker='o', s=50, c=trajectory.color)
            self.ax.scatter([x_km[-1]], [y_km[-1]], [z_km[-1]],
                            marker='x', s=100, c=trajectory.color)

    def plot_detection_envelope(self, envelope: DetectionEnvelope,
                                resolution: int = 20):
        """Plot a detection envelope as a 3D surface"""
        # Create spherical surface for radar coverage
        theta = np.linspace(np.radians(envelope.azimuth_coverage_deg[0]),
                            np.radians(envelope.azimuth_coverage_deg[1]),
                            resolution)
        phi = np.linspace(np.radians(90 - envelope.elevation_coverage_deg[1]),
                          np.radians(90 - envelope.elevation_coverage_deg[0]),
                          resolution // 2)

        theta, phi = np.meshgrid(theta, phi)

        r = envelope.max_range_km

        x = r * np.sin(phi) * np.cos(theta) + envelope.center.x / 1000
        y = r * np.sin(phi) * np.sin(theta) + envelope.center.y / 1000
        z = r * np.cos(phi) + envelope.center.z / 1000

        self.ax.plot_surface(x, y, z,
                             alpha=envelope.alpha,
                             color=envelope.color,
                             linewidth=0)

    def plot_scenario(self, scenario: EngagementScenario):
        """Plot complete engagement scenario"""
        self.create_figure()

        # Plot platforms
        for platform in scenario.platforms:
            self.plot_platform(platform)

        # Plot trajectories
        for trajectory in scenario.trajectories:
            self.plot_trajectory(trajectory)

        # Plot detection envelopes
        for envelope in scenario.detection_envelopes:
            self.plot_detection_envelope(envelope)

        # Set labels and limits
        self.ax.set_xlabel('X (km)', fontsize=10)
        self.ax.set_ylabel('Y (km)', fontsize=10)
        self.ax.set_zlabel('Altitude (km)', fontsize=10)

        bounds = scenario.spatial_bounds_km
        self.ax.set_xlim([-bounds[0], bounds[0]])
        self.ax.set_ylim([-bounds[1], bounds[1]])
        self.ax.set_zlim([0, bounds[2]])

        self.ax.set_title(scenario.name, fontsize=12, fontweight='bold')
        self.ax.legend(loc='upper left', fontsize=8)

        return self.fig

    def _get_platform_marker(self, platform_type: PlatformSymbol) -> str:
        """Get matplotlib marker for platform type"""
        markers = {
            PlatformSymbol.FIGHTER: '^',
            PlatformSymbol.AWACS: 's',
            PlatformSymbol.TANKER: 'D',
            PlatformSymbol.MISSILE: '>',
            PlatformSymbol.SHIP: 'p',
            PlatformSymbol.SAM_SITE: '*',
            PlatformSymbol.RADAR: 'h',
        }
        return markers.get(platform_type, 'o')

    def save_figure(self, filename: str, dpi: int = 150):
        """Save figure to file"""
        if self.fig:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')


class RCSPlotter:
    """
    Radar Cross Section visualization and polar plots.
    """

    def __init__(self, figsize: Tuple[int, int] = (12, 5)):
        self.figsize = figsize

    def plot_rcs_polar(self, azimuths_deg: np.ndarray,
                       rcs_dbsm: np.ndarray,
                       title: str = "RCS Polar Pattern",
                       filename: str = None) -> plt.Figure:
        """
        Create polar plot of RCS vs azimuth angle.

        Args:
            azimuths_deg: Azimuth angles in degrees (0-360)
            rcs_dbsm: RCS values in dBsm
            title: Plot title
            filename: Optional filename to save

        Returns:
            matplotlib Figure
        """
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='polar')

        # Convert azimuth to radians
        theta = np.radians(azimuths_deg)

        # Plot RCS (shift to positive range for polar plot)
        rcs_shifted = rcs_dbsm - np.min(rcs_dbsm) + 10

        ax.plot(theta, rcs_shifted, 'b-', linewidth=2)
        ax.fill(theta, rcs_shifted, alpha=0.3)

        # Mark key aspects
        key_aspects = {
            0: "Nose",
            90: "Beam",
            180: "Tail"
        }

        for az, label in key_aspects.items():
            idx = np.argmin(np.abs(azimuths_deg - az))
            if idx < len(rcs_dbsm):
                ax.annotate(f"{label}\n{rcs_dbsm[idx]:+.1f} dBsm",
                            xy=(np.radians(az), rcs_shifted[idx]),
                            fontsize=8,
                            ha='center')

        ax.set_title(title, fontsize=12, fontweight='bold', pad=20)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)

        if filename:
            fig.savefig(filename, dpi=150, bbox_inches='tight')

        return fig

    def plot_rcs_comparison(self,
                            platforms: Dict[str, Tuple[np.ndarray, np.ndarray]],
                            title: str = "RCS Comparison",
                            filename: str = None) -> plt.Figure:
        """
        Compare RCS patterns of multiple platforms.

        Args:
            platforms: Dict of {name: (azimuths, rcs_dbsm)}
            title: Plot title
            filename: Optional filename

        Returns:
            matplotlib Figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)

        colors = plt.cm.tab10(np.linspace(0, 1, len(platforms)))

        # Left: Cartesian plot
        for i, (name, (az, rcs)) in enumerate(platforms.items()):
            ax1.plot(az, rcs, color=colors[i], linewidth=2, label=name)

        ax1.set_xlabel('Azimuth (degrees)')
        ax1.set_ylabel('RCS (dBsm)')
        ax1.set_title('RCS vs Aspect Angle')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim([0, 180])

        # Right: Bar chart of key values
        metrics = ['Frontal\n(0°)', 'Beam\n(90°)', 'Tail\n(180°)']
        x = np.arange(len(metrics))
        width = 0.8 / len(platforms)

        for i, (name, (az, rcs)) in enumerate(platforms.items()):
            frontal_idx = np.argmin(np.abs(az - 0))
            beam_idx = np.argmin(np.abs(az - 90))
            tail_idx = np.argmin(np.abs(az - 180))

            values = [rcs[frontal_idx], rcs[beam_idx], rcs[tail_idx]]
            ax2.bar(x + i * width, values, width, label=name, color=colors[i])

        ax2.set_xticks(x + width * (len(platforms) - 1) / 2)
        ax2.set_xticklabels(metrics)
        ax2.set_ylabel('RCS (dBsm)')
        ax2.set_title('Key Aspect RCS Values')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        fig.suptitle(title, fontsize=14, fontweight='bold')
        fig.tight_layout()

        if filename:
            fig.savefig(filename, dpi=150, bbox_inches='tight')

        return fig


class MeshVisualizer:
    """
    3D mesh visualization for CAD geometry.
    """

    def __init__(self, figsize: Tuple[int, int] = (12, 10)):
        self.figsize = figsize

    def plot_mesh(self, mesh: TriangleMesh,
                  title: str = "CAD Mesh",
                  color: str = 'lightblue',
                  alpha: float = 0.7,
                  show_edges: bool = True,
                  filename: str = None) -> plt.Figure:
        """
        Plot triangle mesh in 3D.

        Args:
            mesh: TriangleMesh to visualize
            title: Plot title
            color: Face color
            alpha: Transparency
            show_edges: Whether to show edge lines
            filename: Optional filename to save

        Returns:
            matplotlib Figure
        """
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection='3d')

        # Convert triangles to vertices for plotting
        vertices = []
        for tri in mesh.triangles:
            v = [[tri.v1.x, tri.v1.y, tri.v1.z],
                 [tri.v2.x, tri.v2.y, tri.v2.z],
                 [tri.v3.x, tri.v3.y, tri.v3.z]]
            vertices.append(v)

        # Create polygon collection
        poly = Poly3DCollection(vertices,
                                alpha=alpha,
                                facecolor=color,
                                edgecolor='black' if show_edges else None,
                                linewidth=0.1 if show_edges else 0)
        ax.add_collection3d(poly)

        # Set axis limits from bounding box
        bb = mesh.bounding_box
        margin = 0.1

        ax.set_xlim([bb.min_point.x - margin, bb.max_point.x + margin])
        ax.set_ylim([bb.min_point.y - margin, bb.max_point.y + margin])
        ax.set_zlim([bb.min_point.z - margin, bb.max_point.z + margin])

        # Equal aspect ratio
        max_range = max(bb.length, bb.width, bb.height) / 2
        mid_x = (bb.min_point.x + bb.max_point.x) / 2
        mid_y = (bb.min_point.y + bb.max_point.y) / 2
        mid_z = (bb.min_point.z + bb.max_point.z) / 2

        ax.set_xlim([mid_x - max_range, mid_x + max_range])
        ax.set_ylim([mid_y - max_range, mid_y + max_range])
        ax.set_zlim([mid_z - max_range, mid_z + max_range])

        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(title, fontsize=12, fontweight='bold')

        if filename:
            fig.savefig(filename, dpi=150, bbox_inches='tight')

        return fig

    def plot_missile_cad(self, cad_model: MissileCADModel,
                         resolution: int = 24,
                         views: List[str] = None,
                         filename: str = None) -> plt.Figure:
        """
        Plot missile CAD model with multiple views.

        Args:
            cad_model: MissileCADModel to visualize
            resolution: Mesh resolution
            views: List of views ('front', 'side', 'top', '3d')
            filename: Optional filename

        Returns:
            matplotlib Figure
        """
        if views is None:
            views = ['3d', 'side', 'top', 'front']

        geometry = cad_model.generate_geometry(resolution)
        mesh = geometry.mesh

        fig = plt.figure(figsize=(16, 12))

        for i, view in enumerate(views, 1):
            ax = fig.add_subplot(2, 2, i, projection='3d')

            # Plot mesh
            vertices = []
            for tri in mesh.triangles:
                v = [[tri.v1.x, tri.v1.y, tri.v1.z],
                     [tri.v2.x, tri.v2.y, tri.v2.z],
                     [tri.v3.x, tri.v3.y, tri.v3.z]]
                vertices.append(v)

            poly = Poly3DCollection(vertices,
                                    alpha=0.7,
                                    facecolor='lightgray',
                                    edgecolor='darkgray',
                                    linewidth=0.1)
            ax.add_collection3d(poly)

            # Set view angle
            if view == 'front':
                ax.view_init(elev=0, azim=0)
                ax.set_title('Front View')
            elif view == 'side':
                ax.view_init(elev=0, azim=90)
                ax.set_title('Side View')
            elif view == 'top':
                ax.view_init(elev=90, azim=0)
                ax.set_title('Top View')
            else:  # 3d
                ax.view_init(elev=30, azim=-60)
                ax.set_title('3D View')

            # Set limits
            bb = mesh.bounding_box
            max_range = max(bb.length, bb.width, bb.height) * 0.6

            ax.set_xlim([0, bb.length])
            ax.set_ylim([-max_range, max_range])
            ax.set_zlim([-max_range, max_range])

            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
            ax.set_zlabel('Z (m)')

        fig.suptitle(f'{cad_model.name} CAD Model', fontsize=14, fontweight='bold')
        fig.tight_layout()

        if filename:
            fig.savefig(filename, dpi=150, bbox_inches='tight')

        return fig


class TrajectoryGenerator:
    """
    Generate realistic missile and aircraft trajectories for visualization.
    """

    @staticmethod
    def generate_missile_trajectory(
        launch_position: Point3D,
        target_position: Point3D,
        launch_velocity: float = 300,  # m/s
        max_velocity: float = 1400,  # m/s (Mach 4+)
        acceleration: float = 50,  # m/s²
        time_step: float = 1.0,
        max_time: float = 200
    ) -> Trajectory:
        """
        Generate simplified missile trajectory.

        Args:
            launch_position: Launch point
            target_position: Target point
            launch_velocity: Initial velocity (m/s)
            max_velocity: Maximum velocity (m/s)
            acceleration: Boost acceleration (m/s²)
            time_step: Time step for trajectory points
            max_time: Maximum flight time

        Returns:
            Trajectory object
        """
        trajectory = Trajectory(name="Missile", color="orange")

        # Calculate direction to target
        dx = target_position.x - launch_position.x
        dy = target_position.y - launch_position.y
        dz = target_position.z - launch_position.z
        distance = np.sqrt(dx**2 + dy**2 + dz**2)

        direction = Vector3D(dx/distance, dy/distance, dz/distance)

        # Generate trajectory points
        pos = Point3D(launch_position.x, launch_position.y, launch_position.z)
        velocity = launch_velocity
        t = 0

        while t < max_time:
            # Calculate current velocity
            velocity = min(max_velocity, launch_velocity + acceleration * t)

            # Update position
            vel_vector = Vector3D(
                direction.dx * velocity,
                direction.dy * velocity,
                direction.dz * velocity
            )

            trajectory.points.append(TrajectoryPoint(
                time_s=t,
                position=Point3D(pos.x, pos.y, pos.z),
                velocity=vel_vector,
                state="active"
            ))

            # Check if reached target
            current_distance = pos.distance_to(target_position)
            if current_distance < velocity * time_step:
                # Final intercept point
                trajectory.points.append(TrajectoryPoint(
                    time_s=t + current_distance/velocity,
                    position=target_position,
                    velocity=vel_vector,
                    state="intercept"
                ))
                break

            # Update position
            pos = Point3D(
                pos.x + vel_vector.dx * time_step,
                pos.y + vel_vector.dy * time_step,
                pos.z + vel_vector.dz * time_step
            )
            t += time_step

        return trajectory

    @staticmethod
    def generate_aircraft_trajectory(
        start_position: Point3D,
        heading_deg: float,
        velocity: float = 250,  # m/s
        duration: float = 300,
        time_step: float = 5.0
    ) -> Trajectory:
        """
        Generate straight-line aircraft trajectory.

        Args:
            start_position: Starting position
            heading_deg: Heading in degrees (0 = North)
            velocity: Speed (m/s)
            duration: Flight duration (s)
            time_step: Time step

        Returns:
            Trajectory object
        """
        trajectory = Trajectory(name="Aircraft", color="blue")

        heading_rad = np.radians(heading_deg)
        vx = velocity * np.sin(heading_rad)
        vy = velocity * np.cos(heading_rad)
        vz = 0

        pos = Point3D(start_position.x, start_position.y, start_position.z)
        t = 0

        while t <= duration:
            trajectory.points.append(TrajectoryPoint(
                time_s=t,
                position=Point3D(pos.x, pos.y, pos.z),
                velocity=Vector3D(vx, vy, vz),
                state="active"
            ))

            pos = Point3D(
                pos.x + vx * time_step,
                pos.y + vy * time_step,
                pos.z + vz * time_step
            )
            t += time_step

        return trajectory


def create_sample_engagement() -> EngagementScenario:
    """Create a sample engagement scenario for visualization"""

    scenario = EngagementScenario(
        name="J-20 vs F-35 BVR Engagement",
        spatial_bounds_km=(300, 300, 20)
    )

    # Blue forces (US)
    f35 = PlatformState(
        name="F-35A",
        platform_type=PlatformSymbol.FIGHTER,
        position=Point3D(150000, 0, 12000),  # 150 km East
        velocity=Vector3D(-250, 0, 0),  # Heading West
        heading_deg=270,
        altitude_m=12000,
        is_hostile=False,
        color='blue'
    )
    scenario.platforms.append(f35)

    # Add AWACS
    awacs = PlatformState(
        name="E-3 AWACS",
        platform_type=PlatformSymbol.AWACS,
        position=Point3D(250000, 50000, 10000),
        velocity=Vector3D(0, 0, 0),
        heading_deg=270,
        altitude_m=10000,
        is_hostile=False,
        color='darkblue'
    )
    scenario.platforms.append(awacs)

    # Red forces (China)
    j20 = PlatformState(
        name="J-20",
        platform_type=PlatformSymbol.FIGHTER,
        position=Point3D(-100000, 0, 11000),  # 100 km West
        velocity=Vector3D(280, 0, 0),  # Heading East
        heading_deg=90,
        altitude_m=11000,
        is_hostile=True,
        color='red'
    )
    scenario.platforms.append(j20)

    # KJ-500 AWACS
    kj500 = PlatformState(
        name="KJ-500",
        platform_type=PlatformSymbol.AWACS,
        position=Point3D(-200000, -30000, 9000),
        velocity=Vector3D(50, 0, 0),
        heading_deg=90,
        altitude_m=9000,
        is_hostile=True,
        color='darkred'
    )
    scenario.platforms.append(kj500)

    # PL-15 missile trajectory
    pl15_trajectory = TrajectoryGenerator.generate_missile_trajectory(
        launch_position=j20.position,
        target_position=f35.position,
        launch_velocity=300,
        max_velocity=1400,
        acceleration=80
    )
    pl15_trajectory.name = "PL-15"
    pl15_trajectory.color = "orange"
    scenario.trajectories.append(pl15_trajectory)

    # Detection envelopes
    kj500_radar = DetectionEnvelope(
        name="KJ-500 VHF Radar",
        center=kj500.position,
        max_range_km=200,
        azimuth_coverage_deg=(0, 360),
        elevation_coverage_deg=(-5, 30),
        color='red',
        alpha=0.1
    )
    scenario.detection_envelopes.append(kj500_radar)

    return scenario


if __name__ == "__main__":
    print("=" * 70)
    print("CAD Visualization Module - Demo")
    print("=" * 70)

    # 1. Engagement visualization
    print("\n[1] Generating engagement scenario visualization...")
    scenario = create_sample_engagement()
    visualizer = EngagementVisualizer()
    fig = visualizer.plot_scenario(scenario)
    visualizer.save_figure("engagement_scenario.png")
    print("  Saved: engagement_scenario.png")

    # 2. Missile CAD visualization
    print("\n[2] Generating missile CAD visualization...")
    pl15 = create_pl15_cad_model()
    mesh_viz = MeshVisualizer()
    fig = mesh_viz.plot_missile_cad(pl15, resolution=24)
    plt.savefig("pl15_cad_views.png", dpi=150, bbox_inches='tight')
    print("  Saved: pl15_cad_views.png")

    # 3. RCS polar plot (using synthetic data for demo)
    print("\n[3] Generating RCS polar plot...")
    azimuths = np.linspace(0, 360, 73)
    # Synthetic RCS pattern (roughly missile-shaped)
    rcs = -20 + 15 * np.sin(np.radians(azimuths * 2)) ** 2
    rcs[azimuths < 30] = -25  # Low frontal RCS
    rcs[azimuths > 150] = -18  # Higher tail RCS

    rcs_plotter = RCSPlotter()
    fig = rcs_plotter.plot_rcs_polar(azimuths, rcs, title="PL-15 RCS Pattern")
    plt.savefig("pl15_rcs_polar.png", dpi=150, bbox_inches='tight')
    print("  Saved: pl15_rcs_polar.png")

    print("\n" + "=" * 70)
    print("Visualization demo complete. Check generated PNG files.")
    print("=" * 70)

    plt.show()
