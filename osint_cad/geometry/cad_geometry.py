#!/usr/bin/env python3
"""
Advanced 3D CAD Geometry Module

Provides parametric 3D modeling capabilities for defense platforms using
computational geometry. Integrates with RCS calculations and engagement
simulations through geometric parameterization.

Key Features:
- Parametric aircraft geometry (fuselage, wings, canards, intakes, nozzles)
- Parametric missile geometry (body, fins, seeker, motor sections)
- Ship geometry for surface platform modeling
- Geometric mesh generation for RCS estimation
- STL/STEP export for external CAD tool integration
- Volume/surface area calculations for mass properties

Classification: UNCLASSIFIED // PUBLIC RELEASE
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
from abc import ABC, abstractmethod


class PlatformType(Enum):
    """Platform type enumeration"""
    FIGHTER = "fighter"
    BOMBER = "bomber"
    TRANSPORT = "transport"
    UAV = "uav"
    MISSILE = "missile"
    SHIP = "ship"
    SUBMARINE = "submarine"
    GROUND_VEHICLE = "ground_vehicle"
    COMMAND_CENTER = "command_center"
    EW_SYSTEM = "ew_system"


class GeometryPrimitive(Enum):
    """Basic geometry primitive types"""
    BOX = "box"
    CYLINDER = "cylinder"
    CONE = "cone"
    SPHERE = "sphere"
    WEDGE = "wedge"
    TORUS = "torus"
    OGIVE = "ogive"
    SEARS_HAACK = "sears_haack"


@dataclass
class Point3D:
    """3D point representation"""
    x: float
    y: float
    z: float

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def distance_to(self, other: 'Point3D') -> float:
        return np.linalg.norm(self.to_array() - other.to_array())

    def __add__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Point3D') -> 'Point3D':
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> 'Point3D':
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)


@dataclass
class Vector3D:
    """3D vector representation"""
    dx: float
    dy: float
    dz: float

    def to_array(self) -> np.ndarray:
        return np.array([self.dx, self.dy, self.dz])

    def magnitude(self) -> float:
        return np.linalg.norm(self.to_array())

    def normalize(self) -> 'Vector3D':
        mag = self.magnitude()
        if mag < 1e-10:
            return Vector3D(0, 0, 0)
        return Vector3D(self.dx / mag, self.dy / mag, self.dz / mag)

    def dot(self, other: 'Vector3D') -> float:
        return self.dx * other.dx + self.dy * other.dy + self.dz * other.dz

    def cross(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(
            self.dy * other.dz - self.dz * other.dy,
            self.dz * other.dx - self.dx * other.dz,
            self.dx * other.dy - self.dy * other.dx
        )


@dataclass
class BoundingBox:
    """Axis-aligned bounding box"""
    min_point: Point3D
    max_point: Point3D

    @property
    def length(self) -> float:
        """Length along X-axis"""
        return self.max_point.x - self.min_point.x

    @property
    def width(self) -> float:
        """Width along Y-axis"""
        return self.max_point.y - self.min_point.y

    @property
    def height(self) -> float:
        """Height along Z-axis"""
        return self.max_point.z - self.min_point.z

    @property
    def center(self) -> Point3D:
        return Point3D(
            (self.min_point.x + self.max_point.x) / 2,
            (self.min_point.y + self.max_point.y) / 2,
            (self.min_point.z + self.max_point.z) / 2
        )

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height


@dataclass
class Triangle:
    """Triangle mesh element"""
    v1: Point3D
    v2: Point3D
    v3: Point3D

    @property
    def normal(self) -> Vector3D:
        """Calculate face normal"""
        edge1 = Vector3D(
            self.v2.x - self.v1.x,
            self.v2.y - self.v1.y,
            self.v2.z - self.v1.z
        )
        edge2 = Vector3D(
            self.v3.x - self.v1.x,
            self.v3.y - self.v1.y,
            self.v3.z - self.v1.z
        )
        return edge1.cross(edge2).normalize()

    @property
    def area(self) -> float:
        """Calculate triangle area"""
        edge1 = Vector3D(
            self.v2.x - self.v1.x,
            self.v2.y - self.v1.y,
            self.v2.z - self.v1.z
        )
        edge2 = Vector3D(
            self.v3.x - self.v1.x,
            self.v3.y - self.v1.y,
            self.v3.z - self.v1.z
        )
        cross = edge1.cross(edge2)
        return 0.5 * cross.magnitude()

    @property
    def centroid(self) -> Point3D:
        """Calculate triangle centroid"""
        return Point3D(
            (self.v1.x + self.v2.x + self.v3.x) / 3,
            (self.v1.y + self.v2.y + self.v3.y) / 3,
            (self.v1.z + self.v2.z + self.v3.z) / 3
        )


@dataclass
class TriangleMesh:
    """Triangle mesh representation for geometry"""
    triangles: List[Triangle] = field(default_factory=list)

    @property
    def surface_area(self) -> float:
        """Total surface area of mesh"""
        return sum(t.area for t in self.triangles)

    @property
    def bounding_box(self) -> BoundingBox:
        """Calculate mesh bounding box"""
        if not self.triangles:
            return BoundingBox(Point3D(0, 0, 0), Point3D(0, 0, 0))

        all_points = []
        for t in self.triangles:
            all_points.extend([t.v1, t.v2, t.v3])

        xs = [p.x for p in all_points]
        ys = [p.y for p in all_points]
        zs = [p.z for p in all_points]

        return BoundingBox(
            Point3D(min(xs), min(ys), min(zs)),
            Point3D(max(xs), max(ys), max(zs))
        )

    def to_stl_ascii(self) -> str:
        """Export mesh to ASCII STL format"""
        lines = ["solid mesh"]
        for tri in self.triangles:
            n = tri.normal
            lines.append(f"  facet normal {n.dx:.6f} {n.dy:.6f} {n.dz:.6f}")
            lines.append("    outer loop")
            for v in [tri.v1, tri.v2, tri.v3]:
                lines.append(f"      vertex {v.x:.6f} {v.y:.6f} {v.z:.6f}")
            lines.append("    endloop")
            lines.append("  endfacet")
        lines.append("endsolid mesh")
        return "\n".join(lines)

    def transform(self, translation: Point3D = None,
                  rotation_deg: Tuple[float, float, float] = None,
                  scale: float = 1.0) -> 'TriangleMesh':
        """Apply transformation to mesh"""
        new_triangles = []

        for tri in self.triangles:
            vertices = [tri.v1, tri.v2, tri.v3]
            new_vertices = []

            for v in vertices:
                # Apply scale
                p = np.array([v.x * scale, v.y * scale, v.z * scale])

                # Apply rotation (Euler angles: roll, pitch, yaw)
                if rotation_deg:
                    roll, pitch, yaw = np.radians(rotation_deg)

                    # Rotation matrices
                    Rx = np.array([
                        [1, 0, 0],
                        [0, np.cos(roll), -np.sin(roll)],
                        [0, np.sin(roll), np.cos(roll)]
                    ])
                    Ry = np.array([
                        [np.cos(pitch), 0, np.sin(pitch)],
                        [0, 1, 0],
                        [-np.sin(pitch), 0, np.cos(pitch)]
                    ])
                    Rz = np.array([
                        [np.cos(yaw), -np.sin(yaw), 0],
                        [np.sin(yaw), np.cos(yaw), 0],
                        [0, 0, 1]
                    ])
                    p = Rz @ Ry @ Rx @ p

                # Apply translation
                if translation:
                    p = p + translation.to_array()

                new_vertices.append(Point3D(p[0], p[1], p[2]))

            new_triangles.append(Triangle(new_vertices[0], new_vertices[1], new_vertices[2]))

        return TriangleMesh(triangles=new_triangles)


class GeometryComponent(ABC):
    """Abstract base class for geometry components"""

    @abstractmethod
    def generate_mesh(self, resolution: int = 16) -> TriangleMesh:
        """Generate triangle mesh representation"""
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get component parameters"""
        pass

    @abstractmethod
    def calculate_volume(self) -> float:
        """Calculate component volume"""
        pass


@dataclass
class OgiveNose(GeometryComponent):
    """Ogive (tangent ogive) nose cone geometry

    Used for missile seekers and aircraft nose radomes.
    Provides good aerodynamic performance with radar transparency.
    """
    length: float  # Nose length (m)
    base_radius: float  # Base radius (m)
    ogive_radius: float = None  # Ogive curve radius (calculated if None)

    def __post_init__(self):
        if self.ogive_radius is None:
            # Calculate tangent ogive radius from length and base
            # rho = (L^2 + R^2) / (2*R)
            L = self.length
            R = self.base_radius
            self.ogive_radius = (L**2 + R**2) / (2 * R)

    def generate_mesh(self, resolution: int = 32) -> TriangleMesh:
        """Generate ogive nose mesh"""
        triangles = []

        # Generate ogive profile
        num_axial = resolution
        num_radial = resolution

        # Ogive equation: y = sqrt(rho^2 - (L-x)^2) + R - rho
        # where rho is ogive radius, L is length, R is base radius
        rho = self.ogive_radius
        L = self.length
        R = self.base_radius

        profiles = []
        for i in range(num_axial + 1):
            x = i * L / num_axial
            # Ogive radius at this x position
            if rho**2 - (L - x)**2 >= 0:
                y = np.sqrt(rho**2 - (L - x)**2) + R - rho
            else:
                y = 0

            ring = []
            for j in range(num_radial):
                theta = 2 * np.pi * j / num_radial
                ring.append(Point3D(x, y * np.cos(theta), y * np.sin(theta)))
            profiles.append(ring)

        # Connect rings with triangles
        for i in range(num_axial):
            for j in range(num_radial):
                j_next = (j + 1) % num_radial

                p1 = profiles[i][j]
                p2 = profiles[i][j_next]
                p3 = profiles[i + 1][j]
                p4 = profiles[i + 1][j_next]

                # Two triangles per quad
                triangles.append(Triangle(p1, p2, p3))
                triangles.append(Triangle(p2, p4, p3))

        # Add tip cap (if not fully closed)
        if profiles[0][0].y > 0.001:  # Has opening at tip
            tip_center = Point3D(0, 0, 0)
            for j in range(num_radial):
                j_next = (j + 1) % num_radial
                triangles.append(Triangle(tip_center, profiles[0][j_next], profiles[0][j]))

        return TriangleMesh(triangles=triangles)

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "length": self.length,
            "base_radius": self.base_radius,
            "ogive_radius": self.ogive_radius
        }

    def calculate_volume(self) -> float:
        """Calculate ogive volume using integration"""
        # Numerical integration
        n = 100
        volume = 0
        dx = self.length / n

        rho = self.ogive_radius
        L = self.length
        R = self.base_radius

        for i in range(n):
            x = (i + 0.5) * dx
            if rho**2 - (L - x)**2 >= 0:
                y = np.sqrt(rho**2 - (L - x)**2) + R - rho
            else:
                y = 0
            volume += np.pi * y**2 * dx

        return volume


@dataclass
class SearsHaackBody(GeometryComponent):
    """Sears-Haack body - minimum wave drag for given length and volume

    Optimal shape for supersonic flight. Used for missile bodies and
    transonic area ruling on aircraft.
    """
    length: float  # Body length (m)
    max_radius: float  # Maximum radius (m)

    def generate_mesh(self, resolution: int = 32) -> TriangleMesh:
        """Generate Sears-Haack body mesh"""
        triangles = []
        num_axial = resolution * 2
        num_radial = resolution

        L = self.length
        R = self.max_radius

        profiles = []
        for i in range(num_axial + 1):
            x = i * L / num_axial
            # Sears-Haack equation: r(x) = R * (4x/L * (1-x/L))^(3/4)
            xi = x / L  # Normalized position
            r = R * (4 * xi * (1 - xi))**(3 / 4) if 0 < xi < 1 else 0

            ring = []
            for j in range(num_radial):
                theta = 2 * np.pi * j / num_radial
                ring.append(Point3D(x, r * np.cos(theta), r * np.sin(theta)))
            profiles.append(ring)

        # Connect rings
        for i in range(num_axial):
            for j in range(num_radial):
                j_next = (j + 1) % num_radial

                p1 = profiles[i][j]
                p2 = profiles[i][j_next]
                p3 = profiles[i + 1][j]
                p4 = profiles[i + 1][j_next]

                triangles.append(Triangle(p1, p2, p3))
                triangles.append(Triangle(p2, p4, p3))

        return TriangleMesh(triangles=triangles)

    def get_parameters(self) -> Dict[str, Any]:
        return {"length": self.length, "max_radius": self.max_radius}

    def calculate_volume(self) -> float:
        """Sears-Haack volume: V = (3*pi/16) * L * R^2"""
        return (3 * np.pi / 16) * self.length * self.max_radius**2


@dataclass
class CylindricalSection(GeometryComponent):
    """Simple cylindrical section with optional taper"""
    length: float
    forward_radius: float
    aft_radius: float = None  # If None, same as forward (no taper)

    def __post_init__(self):
        if self.aft_radius is None:
            self.aft_radius = self.forward_radius

    def generate_mesh(self, resolution: int = 32) -> TriangleMesh:
        triangles = []
        num_axial = max(4, int(resolution / 4))
        num_radial = resolution

        profiles = []
        for i in range(num_axial + 1):
            x = i * self.length / num_axial
            t = x / self.length
            r = self.forward_radius * (1 - t) + self.aft_radius * t

            ring = []
            for j in range(num_radial):
                theta = 2 * np.pi * j / num_radial
                ring.append(Point3D(x, r * np.cos(theta), r * np.sin(theta)))
            profiles.append(ring)

        for i in range(num_axial):
            for j in range(num_radial):
                j_next = (j + 1) % num_radial
                triangles.append(Triangle(profiles[i][j], profiles[i][j_next], profiles[i + 1][j]))
                triangles.append(Triangle(profiles[i][j_next], profiles[i + 1][j_next], profiles[i + 1][j]))

        return TriangleMesh(triangles=triangles)

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "length": self.length,
            "forward_radius": self.forward_radius,
            "aft_radius": self.aft_radius
        }

    def calculate_volume(self) -> float:
        """Frustum volume"""
        R = self.forward_radius
        r = self.aft_radius
        h = self.length
        return (np.pi * h / 3) * (R**2 + R * r + r**2)


@dataclass
class WingGeometry(GeometryComponent):
    """Parametric wing geometry with sweep, taper, and dihedral"""
    root_chord: float  # Root chord length (m)
    tip_chord: float  # Tip chord length (m)
    span: float  # Full wingspan (m)
    sweep_angle_deg: float  # Leading edge sweep (degrees)
    dihedral_deg: float = 0.0  # Dihedral angle (degrees)
    thickness_ratio: float = 0.05  # t/c ratio
    taper_ratio: float = None  # Calculated from chords if None

    def __post_init__(self):
        if self.taper_ratio is None:
            self.taper_ratio = self.tip_chord / self.root_chord

    def generate_mesh(self, resolution: int = 16) -> TriangleMesh:
        """Generate wing mesh (simplified biconvex airfoil)"""
        triangles = []
        num_spanwise = resolution
        num_chordwise = resolution

        sweep = np.radians(self.sweep_angle_deg)
        dihedral = np.radians(self.dihedral_deg)

        # Generate both wings
        for side in [-1, 1]:
            profiles = []
            for i in range(num_spanwise + 1):
                y = side * i * (self.span / 2) / num_spanwise
                t = abs(y) / (self.span / 2)

                # Chord at this spanwise location
                chord = self.root_chord * (1 - t) + self.tip_chord * t

                # Leading edge position (swept)
                le_x = abs(y) * np.tan(sweep)
                le_z = abs(y) * np.sin(dihedral)

                # Biconvex airfoil profile
                profile = []
                for j in range(num_chordwise + 1):
                    xc = j / num_chordwise  # Chordwise position 0-1
                    x = le_x + xc * chord

                    # Biconvex: thickness = 4*t/c*x*(1-x)
                    thick = 4 * self.thickness_ratio * chord * xc * (1 - xc)

                    # Upper and lower surface
                    profile.append((Point3D(x, y, le_z + thick / 2),
                                    Point3D(x, y, le_z - thick / 2)))

                profiles.append(profile)

            # Create triangles from profiles
            for i in range(num_spanwise):
                for j in range(num_chordwise):
                    # Upper surface
                    p1u = profiles[i][j][0]
                    p2u = profiles[i][j + 1][0]
                    p3u = profiles[i + 1][j][0]
                    p4u = profiles[i + 1][j + 1][0]
                    triangles.append(Triangle(p1u, p2u, p3u))
                    triangles.append(Triangle(p2u, p4u, p3u))

                    # Lower surface
                    p1l = profiles[i][j][1]
                    p2l = profiles[i][j + 1][1]
                    p3l = profiles[i + 1][j][1]
                    p4l = profiles[i + 1][j + 1][1]
                    triangles.append(Triangle(p1l, p3l, p2l))
                    triangles.append(Triangle(p2l, p3l, p4l))

        return TriangleMesh(triangles=triangles)

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "root_chord": self.root_chord,
            "tip_chord": self.tip_chord,
            "span": self.span,
            "sweep_angle_deg": self.sweep_angle_deg,
            "dihedral_deg": self.dihedral_deg,
            "thickness_ratio": self.thickness_ratio,
            "taper_ratio": self.taper_ratio
        }

    def calculate_volume(self) -> float:
        """Approximate wing volume"""
        avg_chord = (self.root_chord + self.tip_chord) / 2
        avg_thickness = avg_chord * self.thickness_ratio
        return avg_chord * avg_thickness * self.span


@dataclass
class FinGeometry(GeometryComponent):
    """Missile/aircraft fin geometry"""
    root_chord: float
    tip_chord: float
    span: float
    sweep_angle_deg: float
    thickness: float
    cant_angle_deg: float = 0.0  # Roll fin cant

    def generate_mesh(self, resolution: int = 8) -> TriangleMesh:
        """Generate fin mesh (flat plate with thickness)"""
        triangles = []
        sweep = np.radians(self.sweep_angle_deg)
        cant = np.radians(self.cant_angle_deg)

        # Simplified flat fin with thickness
        # Root LE at origin, fin extends in +Y direction
        root_le = Point3D(0, 0, 0)
        root_te = Point3D(self.root_chord, 0, 0)
        tip_le = Point3D(self.span * np.tan(sweep),
                         self.span * np.cos(cant),
                         self.span * np.sin(cant))
        tip_te = Point3D(tip_le.x + self.tip_chord, tip_le.y, tip_le.z)

        half_t = self.thickness / 2

        # Upper surface
        triangles.append(Triangle(
            Point3D(root_le.x, root_le.y, half_t),
            Point3D(root_te.x, root_te.y, half_t),
            Point3D(tip_le.x, tip_le.y, tip_le.z + half_t)
        ))
        triangles.append(Triangle(
            Point3D(root_te.x, root_te.y, half_t),
            Point3D(tip_te.x, tip_te.y, tip_te.z + half_t),
            Point3D(tip_le.x, tip_le.y, tip_le.z + half_t)
        ))

        # Lower surface
        triangles.append(Triangle(
            Point3D(root_le.x, root_le.y, -half_t),
            Point3D(tip_le.x, tip_le.y, tip_le.z - half_t),
            Point3D(root_te.x, root_te.y, -half_t)
        ))
        triangles.append(Triangle(
            Point3D(root_te.x, root_te.y, -half_t),
            Point3D(tip_le.x, tip_le.y, tip_le.z - half_t),
            Point3D(tip_te.x, tip_te.y, tip_te.z - half_t)
        ))

        return TriangleMesh(triangles=triangles)

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "root_chord": self.root_chord,
            "tip_chord": self.tip_chord,
            "span": self.span,
            "sweep_angle_deg": self.sweep_angle_deg,
            "thickness": self.thickness,
            "cant_angle_deg": self.cant_angle_deg
        }

    def calculate_volume(self) -> float:
        avg_chord = (self.root_chord + self.tip_chord) / 2
        return avg_chord * self.span * self.thickness


@dataclass
class NozzleGeometry(GeometryComponent):
    """Engine nozzle geometry (convergent-divergent)"""
    throat_radius: float
    exit_radius: float
    length: float
    inlet_radius: float = None

    def __post_init__(self):
        if self.inlet_radius is None:
            self.inlet_radius = self.throat_radius * 1.5

    def generate_mesh(self, resolution: int = 32) -> TriangleMesh:
        triangles = []
        num_axial = resolution
        num_radial = resolution

        # Create CD nozzle profile
        # Convergent section: 0 to 0.4*length
        # Throat: 0.4 to 0.5*length
        # Divergent section: 0.5 to 1.0*length

        profiles = []
        for i in range(num_axial + 1):
            x = i * self.length / num_axial
            t = x / self.length

            if t < 0.4:
                # Convergent
                r = self.inlet_radius - (self.inlet_radius - self.throat_radius) * (t / 0.4)
            elif t < 0.5:
                # Throat
                r = self.throat_radius
            else:
                # Divergent
                r = self.throat_radius + (self.exit_radius - self.throat_radius) * ((t - 0.5) / 0.5)

            ring = []
            for j in range(num_radial):
                theta = 2 * np.pi * j / num_radial
                ring.append(Point3D(x, r * np.cos(theta), r * np.sin(theta)))
            profiles.append(ring)

        for i in range(num_axial):
            for j in range(num_radial):
                j_next = (j + 1) % num_radial
                triangles.append(Triangle(profiles[i][j], profiles[i][j_next], profiles[i + 1][j]))
                triangles.append(Triangle(profiles[i][j_next], profiles[i + 1][j_next], profiles[i + 1][j]))

        return TriangleMesh(triangles=triangles)

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "throat_radius": self.throat_radius,
            "exit_radius": self.exit_radius,
            "length": self.length,
            "inlet_radius": self.inlet_radius
        }

    def calculate_volume(self) -> float:
        # Approximate as truncated cone
        return (np.pi * self.length / 3) * (
            self.inlet_radius**2 + self.inlet_radius * self.exit_radius + self.exit_radius**2
        )


@dataclass
class CADGeometryResult:
    """Result of CAD geometry generation"""
    mesh: TriangleMesh
    components: Dict[str, GeometryComponent]
    bounding_box: BoundingBox
    total_volume: float
    total_surface_area: float
    parameters: Dict[str, Any]
    platform_type: PlatformType


class ParametricPlatformCAD(ABC):
    """Abstract base class for parametric platform CAD models"""

    @abstractmethod
    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        """Generate full platform geometry"""
        pass

    @abstractmethod
    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """Validate geometric constraints"""
        pass

    @abstractmethod
    def get_mass_properties(self) -> Dict[str, float]:
        """Calculate mass properties from geometry"""
        pass


@dataclass
class MissileCADModel(ParametricPlatformCAD):
    """Parametric missile CAD model

    Components:
    - Seeker nose (ogive)
    - Forward body section
    - Motor section
    - Aft body/nozzle section
    - Control fins (4x)
    - Tail fins (4x, optional)
    """
    name: str

    # Overall dimensions
    total_length: float  # m
    body_diameter: float  # m

    # Nose section
    nose_length: float  # m
    nose_type: str = "ogive"  # "ogive", "cone", "blunt"

    # Body sections
    forward_section_length: float = None
    motor_section_length: float = None
    aft_section_length: float = None

    # Fins
    num_fins: int = 4
    fin_root_chord: float = None
    fin_tip_chord: float = None
    fin_span: float = None
    fin_sweep_deg: float = 45.0
    fin_thickness: float = None

    # Nozzle
    nozzle_exit_diameter: float = None

    # Mass properties (for validation)
    total_mass_kg: float = None

    def __post_init__(self):
        body_length = self.total_length - self.nose_length

        if self.forward_section_length is None:
            self.forward_section_length = body_length * 0.2

        if self.motor_section_length is None:
            self.motor_section_length = body_length * 0.5

        if self.aft_section_length is None:
            self.aft_section_length = body_length * 0.3

        if self.fin_root_chord is None:
            self.fin_root_chord = self.body_diameter * 0.8

        if self.fin_tip_chord is None:
            self.fin_tip_chord = self.fin_root_chord * 0.4

        if self.fin_span is None:
            self.fin_span = self.body_diameter * 0.6

        if self.fin_thickness is None:
            self.fin_thickness = self.fin_root_chord * 0.04

        if self.nozzle_exit_diameter is None:
            self.nozzle_exit_diameter = self.body_diameter * 0.7

    def generate_geometry(self, resolution: int = 32) -> CADGeometryResult:
        """Generate complete missile geometry"""
        components = {}
        all_meshes = []

        body_radius = self.body_diameter / 2

        # 1. Nose section
        nose = OgiveNose(
            length=self.nose_length,
            base_radius=body_radius
        )
        nose_mesh = nose.generate_mesh(resolution)
        all_meshes.append(nose_mesh)
        components["nose"] = nose

        # 2. Forward section
        x_offset = self.nose_length
        forward = CylindricalSection(
            length=self.forward_section_length,
            forward_radius=body_radius
        )
        forward_mesh = forward.generate_mesh(resolution)
        forward_mesh = forward_mesh.transform(translation=Point3D(x_offset, 0, 0))
        all_meshes.append(forward_mesh)
        components["forward_section"] = forward

        # 3. Motor section
        x_offset += self.forward_section_length
        motor = CylindricalSection(
            length=self.motor_section_length,
            forward_radius=body_radius
        )
        motor_mesh = motor.generate_mesh(resolution)
        motor_mesh = motor_mesh.transform(translation=Point3D(x_offset, 0, 0))
        all_meshes.append(motor_mesh)
        components["motor_section"] = motor

        # 4. Aft section
        x_offset += self.motor_section_length
        aft = CylindricalSection(
            length=self.aft_section_length,
            forward_radius=body_radius,
            aft_radius=self.nozzle_exit_diameter / 2
        )
        aft_mesh = aft.generate_mesh(resolution)
        aft_mesh = aft_mesh.transform(translation=Point3D(x_offset, 0, 0))
        all_meshes.append(aft_mesh)
        components["aft_section"] = aft

        # 5. Control fins
        fin_x = self.total_length - self.fin_root_chord - 0.1
        for i in range(self.num_fins):
            angle = i * 360 / self.num_fins
            fin = FinGeometry(
                root_chord=self.fin_root_chord,
                tip_chord=self.fin_tip_chord,
                span=self.fin_span,
                sweep_angle_deg=self.fin_sweep_deg,
                thickness=self.fin_thickness
            )
            fin_mesh = fin.generate_mesh(resolution // 2)
            # Position and rotate fin
            fin_mesh = fin_mesh.transform(
                translation=Point3D(fin_x, body_radius, 0),
                rotation_deg=(angle, 0, 0)
            )
            all_meshes.append(fin_mesh)
            components[f"fin_{i}"] = fin

        # Combine all meshes
        combined_triangles = []
        for mesh in all_meshes:
            combined_triangles.extend(mesh.triangles)

        combined_mesh = TriangleMesh(triangles=combined_triangles)

        # Calculate totals
        total_volume = sum(c.calculate_volume() for c in components.values())
        total_surface_area = combined_mesh.surface_area

        return CADGeometryResult(
            mesh=combined_mesh,
            components=components,
            bounding_box=combined_mesh.bounding_box,
            total_volume=total_volume,
            total_surface_area=total_surface_area,
            parameters=self.get_all_parameters(),
            platform_type=PlatformType.MISSILE
        )

    def get_all_parameters(self) -> Dict[str, Any]:
        """Get all missile parameters"""
        return {
            "name": self.name,
            "total_length": self.total_length,
            "body_diameter": self.body_diameter,
            "nose_length": self.nose_length,
            "nose_type": self.nose_type,
            "forward_section_length": self.forward_section_length,
            "motor_section_length": self.motor_section_length,
            "aft_section_length": self.aft_section_length,
            "num_fins": self.num_fins,
            "fin_root_chord": self.fin_root_chord,
            "fin_tip_chord": self.fin_tip_chord,
            "fin_span": self.fin_span,
            "fin_sweep_deg": self.fin_sweep_deg,
            "nozzle_exit_diameter": self.nozzle_exit_diameter
        }

    def validate_parameters(self) -> Tuple[bool, List[str]]:
        """Validate missile geometry constraints"""
        errors = []

        # Length-diameter ratio (fineness ratio)
        fineness = self.total_length / self.body_diameter
        if fineness < 5:
            errors.append(f"Fineness ratio {fineness:.1f} too low (minimum 5)")
        if fineness > 25:
            errors.append(f"Fineness ratio {fineness:.1f} too high (maximum 25)")

        # Nose length
        if self.nose_length < self.body_diameter * 1.5:
            errors.append("Nose too short for supersonic flight")
        if self.nose_length > self.body_diameter * 5:
            errors.append("Nose excessively long")

        # Fin geometry
        if self.fin_span < self.body_diameter * 0.2:
            errors.append("Fins too small for stable flight")
        if self.fin_span > self.body_diameter * 1.5:
            errors.append("Fins excessively large")

        # Section lengths
        total_body = (self.forward_section_length +
                      self.motor_section_length +
                      self.aft_section_length)
        expected_body = self.total_length - self.nose_length
        if abs(total_body - expected_body) > 0.01:
            errors.append(f"Section lengths don't sum to body length")

        return len(errors) == 0, errors

    def get_mass_properties(self) -> Dict[str, float]:
        """Calculate mass properties from geometry"""
        geometry = self.generate_geometry(resolution=16)

        # Estimate mass from volume (aluminum density ~2700 kg/m³)
        # But missiles have complex internals, use 1500 kg/m³ average
        avg_density = 1500  # kg/m³

        volume = geometry.total_volume
        estimated_mass = volume * avg_density

        # Center of mass (assume uniform density)
        cx = self.nose_length + (self.forward_section_length +
                                  self.motor_section_length +
                                  self.aft_section_length) * 0.45

        # Moment of inertia (simplified cylinder)
        r = self.body_diameter / 2
        L = self.total_length
        Ixx = estimated_mass * r**2 / 2
        Iyy = estimated_mass * (3 * r**2 + L**2) / 12
        Izz = Iyy

        return {
            "volume_m3": volume,
            "estimated_mass_kg": estimated_mass,
            "actual_mass_kg": self.total_mass_kg or estimated_mass,
            "center_of_mass_x": cx,
            "Ixx_kg_m2": Ixx,
            "Iyy_kg_m2": Iyy,
            "Izz_kg_m2": Izz
        }


# Pre-configured missile models
def create_pl15_cad_model() -> MissileCADModel:
    """Create PL-15 AAM CAD model from known parameters"""
    return MissileCADModel(
        name="PL-15",
        total_length=4.0,
        body_diameter=0.203,  # ~8 inches
        nose_length=0.5,
        nose_type="ogive",
        total_mass_kg=210
    )


def create_aim120_cad_model() -> MissileCADModel:
    """Create AIM-120 AMRAAM CAD model"""
    return MissileCADModel(
        name="AIM-120D",
        total_length=3.66,
        body_diameter=0.178,  # 7 inches
        nose_length=0.45,
        nose_type="ogive",
        total_mass_kg=161
    )


def create_aim260_cad_model() -> MissileCADModel:
    """Create AIM-260 JATM CAD model (estimated)"""
    return MissileCADModel(
        name="AIM-260",
        total_length=3.7,  # Estimated similar to AIM-120
        body_diameter=0.178,
        nose_length=0.5,
        nose_type="ogive",
        total_mass_kg=170  # Estimated
    )


if __name__ == "__main__":
    print("=" * 70)
    print("CAD Geometry Module - Validation")
    print("=" * 70)

    # Create and validate PL-15 model
    print("\n[1] PL-15 CAD Model:")
    print("-" * 70)
    pl15 = create_pl15_cad_model()

    valid, errors = pl15.validate_parameters()
    print(f"  Valid: {valid}")
    if errors:
        for e in errors:
            print(f"  Error: {e}")

    geometry = pl15.generate_geometry(resolution=16)
    print(f"  Total Volume: {geometry.total_volume:.6f} m³")
    print(f"  Surface Area: {geometry.total_surface_area:.4f} m²")
    print(f"  Bounding Box: {geometry.bounding_box.length:.3f} x "
          f"{geometry.bounding_box.width:.3f} x {geometry.bounding_box.height:.3f} m")

    mass = pl15.get_mass_properties()
    print(f"  Estimated Mass: {mass['estimated_mass_kg']:.1f} kg")
    print(f"  Actual Mass: {mass['actual_mass_kg']:.1f} kg")
    print(f"  Center of Mass X: {mass['center_of_mass_x']:.3f} m")

    # Create AIM-120 for comparison
    print("\n[2] AIM-120D CAD Model:")
    print("-" * 70)
    aim120 = create_aim120_cad_model()

    valid, errors = aim120.validate_parameters()
    print(f"  Valid: {valid}")

    geometry = aim120.generate_geometry(resolution=16)
    print(f"  Total Volume: {geometry.total_volume:.6f} m³")
    print(f"  Length: {geometry.bounding_box.length:.3f} m")

    print("\n" + "=" * 70)
    print("CAD Geometry validation complete.")
    print("=" * 70)
