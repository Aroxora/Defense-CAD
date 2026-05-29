#!/usr/bin/env python3
"""
CAD Trajectory Visualization and Export Module

Provides 3D trajectory generation, rendering, and export capabilities
for engagement simulations. Supports multiple export formats for
integration with external visualization and analysis tools.

Export Formats:
- JSON: Structured trajectory data
- CSV: Tabular time-series data
- KML: Google Earth visualization
- STL: 3D mesh for CAD tools
- GeoJSON: Geographic visualization

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
import json
from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import math

from osint_cad.geometry.cad_geometry import Point3D, Vector3D, TriangleMesh, Triangle


class TrajectoryPhase(Enum):
    """Flight phases for trajectory segments"""
    LAUNCH = "launch"
    BOOST = "boost"
    MIDCOURSE = "midcourse"
    TERMINAL = "terminal"
    INTERCEPT = "intercept"
    MISS = "miss"
    DESTROYED = "destroyed"


class CoordinateSystem(Enum):
    """Coordinate system types"""
    CARTESIAN = "cartesian"  # X, Y, Z in meters
    LLA = "lla"  # Latitude, Longitude, Altitude
    ECEF = "ecef"  # Earth-Centered Earth-Fixed
    ENU = "enu"  # East-North-Up local tangent


@dataclass
class TrajectoryWaypoint:
    """Single waypoint in a trajectory"""
    time_s: float
    position: Point3D
    velocity: Vector3D
    acceleration: Vector3D = None
    phase: TrajectoryPhase = TrajectoryPhase.MIDCOURSE
    heading_deg: float = 0.0
    pitch_deg: float = 0.0
    roll_deg: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.acceleration is None:
            self.acceleration = Vector3D(0, 0, 0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "time_s": self.time_s,
            "position": {"x": self.position.x, "y": self.position.y, "z": self.position.z},
            "velocity": {"dx": self.velocity.dx, "dy": self.velocity.dy, "dz": self.velocity.dz},
            "acceleration": {"dx": self.acceleration.dx, "dy": self.acceleration.dy, "dz": self.acceleration.dz},
            "phase": self.phase.value,
            "heading_deg": self.heading_deg,
            "pitch_deg": self.pitch_deg,
            "roll_deg": self.roll_deg,
            "metadata": self.metadata
        }


@dataclass
class Trajectory3D:
    """Complete 3D trajectory with metadata"""
    name: str
    platform_type: str
    waypoints: List[TrajectoryWaypoint] = field(default_factory=list)
    origin_lla: Tuple[float, float, float] = (0, 0, 0)  # Reference point
    coordinate_system: CoordinateSystem = CoordinateSystem.CARTESIAN
    color: Tuple[int, int, int] = (255, 165, 0)  # RGB
    line_width: float = 2.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_s(self) -> float:
        """Total trajectory duration"""
        if not self.waypoints:
            return 0
        return self.waypoints[-1].time_s - self.waypoints[0].time_s

    @property
    def distance_m(self) -> float:
        """Total distance traveled"""
        total = 0
        for i in range(1, len(self.waypoints)):
            p1 = self.waypoints[i-1].position
            p2 = self.waypoints[i].position
            total += p1.distance_to(p2)
        return total

    def get_position_at_time(self, t: float) -> Optional[Point3D]:
        """Interpolate position at given time"""
        if not self.waypoints:
            return None

        if t <= self.waypoints[0].time_s:
            return self.waypoints[0].position
        if t >= self.waypoints[-1].time_s:
            return self.waypoints[-1].position

        # Find bracketing waypoints
        for i in range(1, len(self.waypoints)):
            if self.waypoints[i].time_s >= t:
                w0, w1 = self.waypoints[i-1], self.waypoints[i]
                # Linear interpolation
                alpha = (t - w0.time_s) / (w1.time_s - w0.time_s)
                return Point3D(
                    w0.position.x + alpha * (w1.position.x - w0.position.x),
                    w0.position.y + alpha * (w1.position.y - w0.position.y),
                    w0.position.z + alpha * (w1.position.z - w0.position.z)
                )
        return None

    def to_arrays(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Convert to numpy arrays (t, x, y, z)"""
        t = np.array([w.time_s for w in self.waypoints])
        x = np.array([w.position.x for w in self.waypoints])
        y = np.array([w.position.y for w in self.waypoints])
        z = np.array([w.position.z for w in self.waypoints])
        return t, x, y, z


@dataclass
class EngagementScenario3D:
    """Complete engagement scenario with multiple trajectories"""
    name: str
    description: str = ""
    trajectories: List[Trajectory3D] = field(default_factory=list)
    reference_time: datetime = field(default_factory=datetime.now)
    origin_lla: Tuple[float, float, float] = (0, 0, 0)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TrajectoryExporter:
    """
    Export trajectories to various formats.
    """

    EARTH_RADIUS_M = 6371000

    def __init__(self, scenario: EngagementScenario3D):
        self.scenario = scenario

    def to_json(self, filename: str = None, indent: int = 2) -> str:
        """
        Export to JSON format.

        Args:
            filename: Optional file to write
            indent: JSON indentation

        Returns:
            JSON string
        """
        data = {
            "scenario": {
                "name": self.scenario.name,
                "description": self.scenario.description,
                "reference_time": self.scenario.reference_time.isoformat(),
                "origin": {
                    "latitude": self.scenario.origin_lla[0],
                    "longitude": self.scenario.origin_lla[1],
                    "altitude_m": self.scenario.origin_lla[2]
                },
                "metadata": self.scenario.metadata
            },
            "trajectories": []
        }

        for traj in self.scenario.trajectories:
            traj_data = {
                "name": traj.name,
                "platform_type": traj.platform_type,
                "duration_s": traj.duration_s,
                "distance_m": traj.distance_m,
                "color": list(traj.color),
                "waypoints": [w.to_dict() for w in traj.waypoints]
            }
            data["trajectories"].append(traj_data)

        json_str = json.dumps(data, indent=indent)

        if filename:
            with open(filename, 'w') as f:
                f.write(json_str)

        return json_str

    def to_csv(self, filename: str = None) -> str:
        """
        Export to CSV format (one file per trajectory).

        Args:
            filename: Base filename (trajectory name appended)

        Returns:
            CSV string of first trajectory
        """
        lines = []

        for traj in self.scenario.trajectories:
            # Header
            header = "time_s,x_m,y_m,z_m,vx_m_s,vy_m_s,vz_m_s,phase,heading_deg,pitch_deg"
            lines.append(f"# Trajectory: {traj.name}")
            lines.append(f"# Platform: {traj.platform_type}")
            lines.append(header)

            for w in traj.waypoints:
                line = f"{w.time_s:.3f},{w.position.x:.2f},{w.position.y:.2f},{w.position.z:.2f},"
                line += f"{w.velocity.dx:.2f},{w.velocity.dy:.2f},{w.velocity.dz:.2f},"
                line += f"{w.phase.value},{w.heading_deg:.1f},{w.pitch_deg:.1f}"
                lines.append(line)

            lines.append("")

        csv_str = "\n".join(lines)

        if filename:
            with open(filename, 'w') as f:
                f.write(csv_str)

        return csv_str

    def to_kml(self, filename: str = None) -> str:
        """
        Export to KML format for Google Earth.

        Args:
            filename: Optional file to write

        Returns:
            KML string
        """
        kml_parts = []
        kml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        kml_parts.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        kml_parts.append('<Document>')
        kml_parts.append(f'  <name>{self.scenario.name}</name>')
        kml_parts.append(f'  <description>{self.scenario.description}</description>')

        for traj in self.scenario.trajectories:
            # Convert color to KML format (AABBGGRR)
            r, g, b = traj.color
            kml_color = f"ff{b:02x}{g:02x}{r:02x}"

            kml_parts.append('  <Placemark>')
            kml_parts.append(f'    <name>{traj.name}</name>')
            kml_parts.append('    <Style>')
            kml_parts.append('      <LineStyle>')
            kml_parts.append(f'        <color>{kml_color}</color>')
            kml_parts.append(f'        <width>{traj.line_width}</width>')
            kml_parts.append('      </LineStyle>')
            kml_parts.append('    </Style>')
            kml_parts.append('    <LineString>')
            kml_parts.append('      <altitudeMode>absolute</altitudeMode>')
            kml_parts.append('      <coordinates>')

            # Convert Cartesian to LLA
            for w in traj.waypoints:
                lat, lon, alt = self._cartesian_to_lla(
                    w.position.x, w.position.y, w.position.z,
                    self.scenario.origin_lla
                )
                kml_parts.append(f'        {lon:.6f},{lat:.6f},{alt:.1f}')

            kml_parts.append('      </coordinates>')
            kml_parts.append('    </LineString>')
            kml_parts.append('  </Placemark>')

        kml_parts.append('</Document>')
        kml_parts.append('</kml>')

        kml_str = "\n".join(kml_parts)

        if filename:
            with open(filename, 'w') as f:
                f.write(kml_str)

        return kml_str

    def to_geojson(self, filename: str = None) -> str:
        """
        Export to GeoJSON format.

        Args:
            filename: Optional file to write

        Returns:
            GeoJSON string
        """
        features = []

        for traj in self.scenario.trajectories:
            coordinates = []

            for w in traj.waypoints:
                lat, lon, alt = self._cartesian_to_lla(
                    w.position.x, w.position.y, w.position.z,
                    self.scenario.origin_lla
                )
                coordinates.append([lon, lat, alt])

            feature = {
                "type": "Feature",
                "properties": {
                    "name": traj.name,
                    "platform_type": traj.platform_type,
                    "duration_s": traj.duration_s,
                    "distance_m": traj.distance_m
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                }
            }
            features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        geojson_str = json.dumps(geojson, indent=2)

        if filename:
            with open(filename, 'w') as f:
                f.write(geojson_str)

        return geojson_str

    def to_trajectory_mesh(self, trajectory: Trajectory3D,
                           tube_radius: float = 50) -> TriangleMesh:
        """
        Convert trajectory to 3D tube mesh for CAD visualization.

        Args:
            trajectory: Trajectory to convert
            tube_radius: Radius of trajectory tube in meters

        Returns:
            TriangleMesh representing the trajectory as a tube
        """
        if len(trajectory.waypoints) < 2:
            return TriangleMesh()

        triangles = []
        n_segments = 8  # Number of segments around tube

        for i in range(len(trajectory.waypoints) - 1):
            p1 = trajectory.waypoints[i].position
            p2 = trajectory.waypoints[i + 1].position

            # Direction vector
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            dz = p2.z - p1.z
            length = math.sqrt(dx*dx + dy*dy + dz*dz)

            if length < 0.01:
                continue

            # Normalized direction
            dir_x, dir_y, dir_z = dx/length, dy/length, dz/length

            # Find perpendicular vectors
            if abs(dir_z) < 0.9:
                perp1_x = -dir_y
                perp1_y = dir_x
                perp1_z = 0
            else:
                perp1_x = 1
                perp1_y = 0
                perp1_z = 0

            # Normalize
            perp1_len = math.sqrt(perp1_x**2 + perp1_y**2 + perp1_z**2)
            perp1_x /= perp1_len
            perp1_y /= perp1_len
            perp1_z /= perp1_len

            # Second perpendicular via cross product
            perp2_x = dir_y * perp1_z - dir_z * perp1_y
            perp2_y = dir_z * perp1_x - dir_x * perp1_z
            perp2_z = dir_x * perp1_y - dir_y * perp1_x

            # Generate ring vertices
            ring1 = []
            ring2 = []

            for j in range(n_segments):
                theta = 2 * math.pi * j / n_segments
                cos_t = math.cos(theta)
                sin_t = math.sin(theta)

                offset_x = tube_radius * (cos_t * perp1_x + sin_t * perp2_x)
                offset_y = tube_radius * (cos_t * perp1_y + sin_t * perp2_y)
                offset_z = tube_radius * (cos_t * perp1_z + sin_t * perp2_z)

                ring1.append(Point3D(p1.x + offset_x, p1.y + offset_y, p1.z + offset_z))
                ring2.append(Point3D(p2.x + offset_x, p2.y + offset_y, p2.z + offset_z))

            # Create triangles between rings
            for j in range(n_segments):
                j_next = (j + 1) % n_segments
                triangles.append(Triangle(ring1[j], ring1[j_next], ring2[j]))
                triangles.append(Triangle(ring1[j_next], ring2[j_next], ring2[j]))

        return TriangleMesh(triangles=triangles)

    def _cartesian_to_lla(self, x: float, y: float, z: float,
                          origin: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Convert local Cartesian coordinates to Lat/Lon/Alt.

        Args:
            x, y, z: Local coordinates in meters (x=East, y=North, z=Up)
            origin: Reference point (lat, lon, alt)

        Returns:
            (latitude, longitude, altitude)
        """
        lat0, lon0, alt0 = origin

        # Simple flat-Earth approximation for small distances
        lat0_rad = math.radians(lat0)

        # Meters per degree at this latitude
        m_per_deg_lat = 111132.92 - 559.82 * math.cos(2 * lat0_rad)
        m_per_deg_lon = 111412.84 * math.cos(lat0_rad)

        dlat = y / m_per_deg_lat
        dlon = x / m_per_deg_lon

        lat = lat0 + dlat
        lon = lon0 + dlon
        alt = alt0 + z

        return lat, lon, alt


class TrajectoryGenerator3D:
    """
    Generate realistic 3D trajectories for various platform types.
    """

    GRAVITY = 9.81  # m/s²

    @classmethod
    def generate_ballistic_missile(cls,
                                   launch_position: Point3D,
                                   target_position: Point3D,
                                   apogee_altitude: float,
                                   flight_time: float,
                                   time_step: float = 1.0) -> Trajectory3D:
        """
        Generate ballistic missile trajectory.

        Args:
            launch_position: Launch point
            target_position: Target point
            apogee_altitude: Maximum altitude (meters)
            flight_time: Total flight time (seconds)
            time_step: Time step for waypoints

        Returns:
            Trajectory3D with ballistic path
        """
        trajectory = Trajectory3D(
            name="Ballistic Missile",
            platform_type="MRBM",
            color=(255, 0, 0)
        )

        # Calculate parameters
        dx = target_position.x - launch_position.x
        dy = target_position.y - launch_position.y
        ground_range = math.sqrt(dx*dx + dy*dy)
        heading = math.degrees(math.atan2(dx, dy))

        # Generate waypoints
        t = 0
        while t <= flight_time:
            # Normalized time (0 to 1)
            tau = t / flight_time

            # Parabolic altitude profile
            alt = launch_position.z + 4 * apogee_altitude * tau * (1 - tau)

            # Linear ground track
            x = launch_position.x + tau * dx
            y = launch_position.y + tau * dy

            # Velocity (derivative of position)
            vx = dx / flight_time
            vy = dy / flight_time
            vz = 4 * apogee_altitude * (1 - 2*tau) / flight_time

            # Phase determination
            if tau < 0.15:
                phase = TrajectoryPhase.BOOST
            elif tau < 0.85:
                phase = TrajectoryPhase.MIDCOURSE
            else:
                phase = TrajectoryPhase.TERMINAL

            # Pitch angle
            pitch = math.degrees(math.atan2(vz, math.sqrt(vx*vx + vy*vy)))

            trajectory.waypoints.append(TrajectoryWaypoint(
                time_s=t,
                position=Point3D(x, y, alt),
                velocity=Vector3D(vx, vy, vz),
                phase=phase,
                heading_deg=heading,
                pitch_deg=pitch
            ))

            t += time_step

        return trajectory

    @classmethod
    def generate_cruise_missile(cls,
                                launch_position: Point3D,
                                target_position: Point3D,
                                cruise_altitude: float,
                                velocity: float = 250,
                                time_step: float = 5.0) -> Trajectory3D:
        """
        Generate cruise missile trajectory with terrain following.

        Args:
            launch_position: Launch point
            target_position: Target point
            cruise_altitude: Cruise altitude (meters AGL)
            velocity: Cruise speed (m/s)
            time_step: Time step for waypoints

        Returns:
            Trajectory3D with cruise path
        """
        trajectory = Trajectory3D(
            name="Cruise Missile",
            platform_type="LACM",
            color=(255, 165, 0)
        )

        # Calculate flight parameters
        dx = target_position.x - launch_position.x
        dy = target_position.y - launch_position.y
        ground_range = math.sqrt(dx*dx + dy*dy)
        flight_time = ground_range / velocity
        heading = math.degrees(math.atan2(dx, dy))

        # Normalize direction
        dir_x = dx / ground_range
        dir_y = dy / ground_range

        t = 0
        while t <= flight_time:
            tau = t / flight_time

            # Ground position
            x = launch_position.x + tau * dx
            y = launch_position.y + tau * dy

            # Altitude profile: climb, cruise, terminal dive
            if tau < 0.1:  # Climb phase
                climb_tau = tau / 0.1
                alt = launch_position.z + climb_tau * cruise_altitude
                phase = TrajectoryPhase.BOOST
            elif tau > 0.95:  # Terminal dive
                dive_tau = (tau - 0.95) / 0.05
                alt = cruise_altitude * (1 - dive_tau) + target_position.z * dive_tau
                phase = TrajectoryPhase.TERMINAL
            else:  # Cruise phase
                # Add small altitude variations for terrain following
                alt = cruise_altitude + 50 * math.sin(tau * 20)
                phase = TrajectoryPhase.MIDCOURSE

            vx = dir_x * velocity
            vy = dir_y * velocity
            vz = 0

            trajectory.waypoints.append(TrajectoryWaypoint(
                time_s=t,
                position=Point3D(x, y, alt),
                velocity=Vector3D(vx, vy, vz),
                phase=phase,
                heading_deg=heading,
                pitch_deg=0
            ))

            t += time_step

        return trajectory

    @classmethod
    def generate_air_to_air_missile(cls,
                                    launch_position: Point3D,
                                    launch_velocity: Vector3D,
                                    target_position: Point3D,
                                    target_velocity: Vector3D,
                                    max_acceleration: float = 400,
                                    time_step: float = 0.5) -> Trajectory3D:
        """
        Generate air-to-air missile trajectory with proportional navigation.

        Args:
            launch_position: Missile launch point
            launch_velocity: Initial velocity from launching aircraft
            target_position: Target position at launch
            target_velocity: Target velocity vector
            max_acceleration: Maximum lateral acceleration (m/s²)
            time_step: Time step

        Returns:
            Trajectory3D with intercept path
        """
        trajectory = Trajectory3D(
            name="AAM",
            platform_type="AAM",
            color=(255, 200, 0)
        )

        # Current state
        pos = Point3D(launch_position.x, launch_position.y, launch_position.z)
        vel = Vector3D(launch_velocity.dx, launch_velocity.dy, launch_velocity.dz)

        # Missile speed increases during boost
        boost_time = 3.0
        boost_acceleration = 100  # m/s²
        max_speed = 1400  # m/s (Mach 4+)

        t = 0
        max_time = 120  # Maximum flight time

        while t < max_time:
            # Update target position
            tgt_x = target_position.x + target_velocity.dx * t
            tgt_y = target_position.y + target_velocity.dy * t
            tgt_z = target_position.z + target_velocity.dz * t

            # Range to target
            dx = tgt_x - pos.x
            dy = tgt_y - pos.y
            dz = tgt_z - pos.z
            range_to_tgt = math.sqrt(dx*dx + dy*dy + dz*dz)

            # Check intercept
            if range_to_tgt < 50:  # 50m lethal radius
                trajectory.waypoints.append(TrajectoryWaypoint(
                    time_s=t,
                    position=Point3D(pos.x, pos.y, pos.z),
                    velocity=vel,
                    phase=TrajectoryPhase.INTERCEPT
                ))
                break

            # Calculate phase
            if t < boost_time:
                phase = TrajectoryPhase.BOOST
            elif range_to_tgt < 5000:
                phase = TrajectoryPhase.TERMINAL
            else:
                phase = TrajectoryPhase.MIDCOURSE

            # Proportional navigation guidance
            # Line of sight to target
            los_x = dx / range_to_tgt
            los_y = dy / range_to_tgt
            los_z = dz / range_to_tgt

            # Current velocity magnitude
            speed = vel.magnitude()

            # Desired velocity direction (toward predicted intercept)
            closing_velocity = (vel.dx - target_velocity.dx) * los_x + \
                              (vel.dy - target_velocity.dy) * los_y + \
                              (vel.dz - target_velocity.dz) * los_z

            time_to_intercept = range_to_tgt / max(abs(closing_velocity), 100)
            pred_x = tgt_x + target_velocity.dx * time_to_intercept * 0.5
            pred_y = tgt_y + target_velocity.dy * time_to_intercept * 0.5
            pred_z = tgt_z + target_velocity.dz * time_to_intercept * 0.5

            # Direction to predicted intercept
            dpx = pred_x - pos.x
            dpy = pred_y - pos.y
            dpz = pred_z - pos.z
            pred_range = math.sqrt(dpx*dpx + dpy*dpy + dpz*dpz)

            if pred_range > 0:
                desired_dir_x = dpx / pred_range
                desired_dir_y = dpy / pred_range
                desired_dir_z = dpz / pred_range
            else:
                desired_dir_x = los_x
                desired_dir_y = los_y
                desired_dir_z = los_z

            # Update velocity with acceleration
            if t < boost_time:
                speed = min(speed + boost_acceleration * time_step, max_speed)

            vel = Vector3D(
                desired_dir_x * speed,
                desired_dir_y * speed,
                desired_dir_z * speed
            )

            # Calculate attitude
            heading = math.degrees(math.atan2(vel.dx, vel.dy))
            pitch = math.degrees(math.atan2(vel.dz, math.sqrt(vel.dx**2 + vel.dy**2)))

            # Add waypoint
            trajectory.waypoints.append(TrajectoryWaypoint(
                time_s=t,
                position=Point3D(pos.x, pos.y, pos.z),
                velocity=vel,
                phase=phase,
                heading_deg=heading,
                pitch_deg=pitch
            ))

            # Update position
            pos = Point3D(
                pos.x + vel.dx * time_step,
                pos.y + vel.dy * time_step,
                pos.z + vel.dz * time_step
            )

            t += time_step

        return trajectory


def create_sample_engagement_3d() -> EngagementScenario3D:
    """Create a sample 3D engagement scenario"""
    scenario = EngagementScenario3D(
        name="BVR Engagement Demo",
        description="J-20 launches PL-15 at F-35",
        origin_lla=(25.0, 121.0, 0)  # Near Taiwan
    )

    # F-35 trajectory (evading)
    f35_start = Point3D(150000, 0, 12000)
    f35_trajectory = Trajectory3D(
        name="F-35A",
        platform_type="Fighter",
        color=(0, 100, 255)
    )

    for t in range(0, 120, 2):
        x = 150000 - 250 * t  # Heading west
        y = 5000 * math.sin(t * 0.05)  # Mild evasion
        z = 12000 + 500 * math.sin(t * 0.03)

        f35_trajectory.waypoints.append(TrajectoryWaypoint(
            time_s=t,
            position=Point3D(x, y, z),
            velocity=Vector3D(-250, 0, 0),
            phase=TrajectoryPhase.MIDCOURSE
        ))

    scenario.trajectories.append(f35_trajectory)

    # PL-15 trajectory
    pl15 = TrajectoryGenerator3D.generate_air_to_air_missile(
        launch_position=Point3D(-100000, 0, 11000),
        launch_velocity=Vector3D(300, 0, 0),
        target_position=Point3D(150000, 0, 12000),
        target_velocity=Vector3D(-250, 0, 0)
    )
    pl15.name = "PL-15"
    scenario.trajectories.append(pl15)

    return scenario


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CAD TRAJECTORY EXPORT DEMO")
    print("=" * 70)

    # Create scenario
    scenario = create_sample_engagement_3d()

    # Create exporter
    exporter = TrajectoryExporter(scenario)

    # Export to JSON
    print("\n[1] Exporting to JSON...")
    json_str = exporter.to_json("engagement_demo.json")
    print(f"  Written: engagement_demo.json ({len(json_str)} bytes)")

    # Export to CSV
    print("\n[2] Exporting to CSV...")
    csv_str = exporter.to_csv("engagement_demo.csv")
    print(f"  Written: engagement_demo.csv ({len(csv_str)} bytes)")

    # Export to KML
    print("\n[3] Exporting to KML...")
    kml_str = exporter.to_kml("engagement_demo.kml")
    print(f"  Written: engagement_demo.kml ({len(kml_str)} bytes)")

    # Export to GeoJSON
    print("\n[4] Exporting to GeoJSON...")
    geojson_str = exporter.to_geojson("engagement_demo.geojson")
    print(f"  Written: engagement_demo.geojson ({len(geojson_str)} bytes)")

    # Create trajectory mesh
    print("\n[5] Generating trajectory mesh...")
    if scenario.trajectories:
        mesh = exporter.to_trajectory_mesh(scenario.trajectories[0], tube_radius=100)
        stl = mesh.to_stl_ascii()
        with open("trajectory_mesh.stl", 'w') as f:
            f.write(stl)
        print(f"  Written: trajectory_mesh.stl ({len(stl)} bytes)")

    # Trajectory summary
    print("\n[6] Trajectory Summary:")
    print("-" * 40)
    for traj in scenario.trajectories:
        print(f"  {traj.name}:")
        print(f"    Duration: {traj.duration_s:.1f} s")
        print(f"    Distance: {traj.distance_m/1000:.1f} km")
        print(f"    Waypoints: {len(traj.waypoints)}")

    print("\n" + "=" * 70)
    print("Trajectory export demo complete.")
    print("=" * 70)
