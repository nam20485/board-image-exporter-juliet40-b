"""
Pydantic models for PCB geometric primitives and domain objects.

This module defines the core data structures used throughout the PCB renderer,
including geometric primitives (Point, Polygon, Polyline, Circle) and domain
models (Board, Component, Trace, Via, Layer, Stackup).
"""

from typing import Any
from enum import Enum
from math import isfinite, sqrt


class LayerType(str, Enum):
    """Enumeration of PCB layer types."""
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    MID = "MID"
    PLANE = "PLANE"
    DIELECTRIC = "DIELECTRIC"


class Side(str, Enum):
    """Enumeration of component placement sides."""
    FRONT = "FRONT"
    BACK = "BACK"


class Point:
    """
    Represents a 2D point in millimeter coordinates.

    Attributes:
        x: X-coordinate in millimeters
        y: Y-coordinate in millimeters

    Raises:
        ValueError: If x or y is NaN or infinite
    """

    def __init__(self, x: float, y: float):
        """Initialize a Point with x and y coordinates."""
        if not isfinite(x) or not isfinite(y):
            raise ValueError(f"Point coordinates must be finite, got x={x}, y={y}")
        self.x = x
        self.y = y

    def distance_to(self, other: "Point") -> float:
        """
        Calculate Euclidean distance to another point.

        Args:
            other: The target point

        Returns:
            Distance in millimeters
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return sqrt(dx * dx + dy * dy)

    def __eq__(self, other: Any) -> bool:
        """Check equality based on coordinates."""
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        """Hash based on coordinates for use in sets and dicts."""
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        """String representation of Point."""
        return f"Point({self.x}, {self.y})"


class Polygon:
    """
    Represents a closed polygon in 2D space.

    A polygon is defined by a sequence of points forming its boundary.
    The polygon should be closed (first point equals last point).

    Attributes:
        points: List of points defining the polygon boundary

    Raises:
        ValueError: If points list has fewer than 3 points or is not closed
    """

    def __init__(self, points: list[Point]):
        """Initialize a Polygon with a list of points."""
        if len(points) < 3:
            raise ValueError(f"Polygon must have at least 3 points, got {len(points)}")
        self.points = points

    def is_closed(self) -> bool:
        """
        Check if the polygon is closed (first point equals last point).

        Returns:
            True if polygon is closed, False otherwise
        """
        if len(self.points) < 2:
            return False
        return self.points[0] == self.points[-1]

    def bounds(self) -> tuple[Point, Point]:
        """
        Calculate the bounding box of the polygon.

        Returns:
            Tuple of (min_point, max_point) defining the bounding box
        """
        if not self.points:
            raise ValueError("Cannot calculate bounds of empty polygon")

        min_x = min(p.x for p in self.points)
        max_x = max(p.x for p in self.points)
        min_y = min(p.y for p in self.points)
        max_y = max(p.y for p in self.points)

        return Point(min_x, min_y), Point(max_x, max_y)

    def area(self) -> float:
        """
        Calculate the area using the shoelace formula.

        Returns:
            Area in square millimeters
        """
        if len(self.points) < 3:
            return 0.0

        # Shoelace formula
        area = 0.0
        n = len(self.points)
        for i in range(n):
            j = (i + 1) % n
            area += self.points[i].x * self.points[j].y
            area -= self.points[j].x * self.points[i].y

        return abs(area) / 2.0

    def self_intersects(self) -> bool:
        """
        Check if the polygon has self-intersections.

        Performs a basic O(n^2) edge intersection check.

        Returns:
            True if polygon self-intersects, False otherwise
        """
        n = len(self.points)
        if n < 4:
            return False

        # For a closed polygon, we have n-1 edges (the last point equals the first)
        # For an open polygon, we would also have n-1 edges
        # But for self-intersection checks, we check n-1 unique edges
        num_edges = n - 1

        for i in range(num_edges):
            p1 = self.points[i]
            p2 = self.points[i + 1]

            # Check against all non-adjacent edges
            # Start from i+2 to skip the adjacent edge
            for j in range(i + 2, num_edges):
                # For closed polygons, skip checking edge i against the edge that connects to it
                # Skip first and last edge (they share the first/last vertex)
                if i == 0 and j == num_edges - 1:
                    continue

                p3 = self.points[j]
                p4 = self.points[j + 1]

                if self._segments_intersect(p1, p2, p3, p4):
                    return True

        return False

    def _segments_intersect(
        self, p1: Point, p2: Point, p3: Point, p4: Point
    ) -> bool:
        """
        Check if two line segments intersect.

        Args:
            p1, p2: Endpoints of first segment
            p3, p4: Endpoints of second segment

        Returns:
            True if segments intersect, False otherwise
        """
        def ccw(a: Point, b: Point, c: Point) -> bool:
            """Check if three points are counter-clockwise."""
            return (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x)

        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

    def __repr__(self) -> str:
        """String representation of Polygon."""
        return f"Polygon({len(self.points)} points)"


class Polyline:
    """
    Represents an open polyline (connected line segments) in 2D space.

    Attributes:
        points: List of points defining the polyline

    Raises:
        ValueError: If points list has fewer than 2 points
    """

    def __init__(self, points: list[Point]):
        """Initialize a Polyline with a list of points."""
        if len(points) < 2:
            raise ValueError(f"Polyline must have at least 2 points, got {len(points)}")

        # Validate all points have finite coordinates
        for i, p in enumerate(points):
            if not isfinite(p.x) or not isfinite(p.y):
                raise ValueError(
                    f"Polyline point {i} has non-finite coordinates: ({p.x}, {p.y})"
                )

        self.points = points

    def length(self) -> float:
        """
        Calculate the total length of the polyline.

        Returns:
            Length in millimeters
        """
        total = 0.0
        for i in range(len(self.points) - 1):
            total += self.points[i].distance_to(self.points[i + 1])
        return total

    def __repr__(self) -> str:
        """String representation of Polyline."""
        return f"Polyline({len(self.points)} points, length={self.length():.2f}mm)"


class Circle:
    """
    Represents a circle in 2D space.

    Attributes:
        center: Center point of the circle
        radius: Radius in millimeters

    Raises:
        ValueError: If radius is not positive
    """

    def __init__(self, center: Point, radius: float):
        """Initialize a Circle with center point and radius."""
        if radius <= 0:
            raise ValueError(f"Circle radius must be positive, got {radius}")
        self.center = center
        self.radius = radius

    def bounds(self) -> tuple[Point, Point]:
        """
        Calculate the bounding box of the circle.

        Returns:
            Tuple of (min_point, max_point) defining the bounding box
        """
        min_point = Point(self.center.x - self.radius, self.center.y - self.radius)
        max_point = Point(self.center.x + self.radius, self.center.y + self.radius)
        return min_point, max_point

    def __repr__(self) -> str:
        """String representation of Circle."""
        return f"Circle(center={self.center}, radius={self.radius})"


class Layer:
    """
    Represents a single layer in the PCB stackup.

    Attributes:
        name: Human-readable layer name
        layer_type: Type of layer (TOP, BOTTOM, MID, PLANE, DIELECTRIC)
        index: Z-order position in the stackup (0 = top)
        hash: Unique identifier for referencing this layer
        material: Optional material specification
    """

    def __init__(
        self,
        name: str,
        layer_type: LayerType,
        index: int,
        hash: str,
        material: str | None = None,
    ):
        """Initialize a Layer with stackup properties."""
        if index < 0:
            raise ValueError(f"Layer index must be non-negative, got {index}")
        if not hash:
            raise ValueError("Layer hash cannot be empty")

        self.name = name
        self.layer_type = layer_type
        self.index = index
        self.hash = hash
        self.material = material

    def __repr__(self) -> str:
        """String representation of Layer."""
        return f"Layer(name={self.name}, type={self.layer_type}, index={self.index})"


class Stackup:
    """
    Represents the complete PCB layer stackup.

    Attributes:
        layers: List of layers in the stackup

    Raises:
        ValueError: If layer hashes are not unique or indices are not sequential
    """

    def __init__(self, layers: list[Layer]):
        """Initialize a Stackup with a list of layers."""
        if not layers:
            raise ValueError("Stackup must contain at least one layer")

        # Check for unique hashes
        hashes = [layer.hash for layer in layers]
        if len(hashes) != len(set(hashes)):
            raise ValueError("Stackup layers must have unique hashes")

        # Check sequential indices
        for i, layer in enumerate(layers):
            if layer.index != i:
                raise ValueError(
                    f"Layer indices must be sequential starting at 0, "
                    f"but layer {i} has index {layer.index}"
                )

        self.layers = layers

    def get_layer_by_hash(self, hash: str) -> Layer | None:
        """
        Get a layer by its hash identifier.

        Args:
            hash: Layer hash to look up

        Returns:
            Layer if found, None otherwise
        """
        for layer in self.layers:
            if layer.hash == hash:
                return layer
        return None

    def __repr__(self) -> str:
        """String representation of Stackup."""
        return f"Stackup({len(self.layers)} layers)"


class Pin:
    """
    Represents a component pin.

    Attributes:
        name: Pin name/number
        net: Connected net name (None if not connected)
        position: Position relative to component origin
        rotation: Rotation in degrees
        is_throughhole: True if through-hole pin, False if SMD
    """

    def __init__(
        self,
        name: str,
        net: str | None,
        position: Point,
        rotation: float = 0.0,
        is_throughhole: bool = False,
    ):
        """Initialize a Pin with properties."""
        if not name:
            raise ValueError("Pin name cannot be empty")
        if not isinstance(rotation, (int, float)):
            raise ValueError(f"Pin rotation must be numeric, got {type(rotation).__name__}: {rotation}")
        if not isfinite(rotation):
            raise ValueError(f"Pin rotation must be finite, got {rotation}")

        self.name = name
        self.net = net
        self.position = position
        self.rotation = rotation
        self.is_throughhole = is_throughhole

    def __repr__(self) -> str:
        """String representation of Pin."""
        return f"Pin(name={self.name}, net={self.net})"


class Component:
    """
    Represents a PCB component.

    Attributes:
        ref_des: Reference designator (e.g., "R1", "U2")
        footprint: Footprint name
        position: Position in board coordinates
        rotation: Rotation in degrees (counter-clockwise)
        side: Board side (FRONT or BACK)
        outline: Optional component boundary polygon
        pins: Dictionary of pins keyed by pin name
    """

    def __init__(
        self,
        ref_des: str,
        footprint: str,
        position: Point,
        rotation: float = 0.0,
        side: Side = Side.FRONT,
        outline: Polygon | None = None,
        pins: dict[str, Pin] | None = None,
    ):
        """Initialize a Component with properties."""
        if not ref_des:
            raise ValueError("Component ref_des cannot be empty")
        if not footprint:
            raise ValueError("Component footprint cannot be empty")
        if not isinstance(rotation, (int, float)):
            raise ValueError(f"Component rotation must be numeric, got {type(rotation).__name__}: {rotation}")
        if not isfinite(rotation):
            raise ValueError(f"Component rotation must be finite, got {rotation}")

        self.ref_des = ref_des
        self.footprint = footprint
        self.position = position
        self.rotation = rotation
        self.side = side
        self.outline = outline
        self.pins = pins or {}

    def __repr__(self) -> str:
        """String representation of Component."""
        return f"Component(ref_des={self.ref_des}, footprint={self.footprint})"


class Trace:
    """
    Represents a PCB trace (copper route).

    Attributes:
        uid: Unique identifier
        net: Net name for connectivity
        layer_hash: Reference to layer in stackup
        path: Centerline polyline
        width: Trace width in millimeters

    Raises:
        ValueError: If width is not positive
    """

    def __init__(
        self, uid: str, net: str, layer_hash: str, path: Polyline, width: float
    ):
        """Initialize a Trace with properties."""
        if not uid:
            raise ValueError("Trace uid cannot be empty")
        if not net:
            raise ValueError("Trace net cannot be empty")
        if not layer_hash:
            raise ValueError("Trace layer_hash cannot be empty")
        if width <= 0:
            raise ValueError(f"Trace width must be positive, got {width}")

        self.uid = uid
        self.net = net
        self.layer_hash = layer_hash
        self.path = path
        self.width = width

    def __repr__(self) -> str:
        """String representation of Trace."""
        return f"Trace(uid={self.uid}, net={self.net}, width={self.width})"


class Via:
    """
    Represents a PCB via (plated through-hole).

    Attributes:
        uid: Unique identifier
        net: Net name for connectivity
        center: Center point
        outer_diameter: Outer diameter in millimeters
        hole_diameter: Hole diameter in millimeters
        start_layer: Starting layer hash
        end_layer: Ending layer hash

    Raises:
        ValueError: If diameters are invalid or hole >= outer
    """

    def __init__(
        self,
        uid: str,
        net: str,
        center: Point,
        outer_diameter: float,
        hole_diameter: float,
        start_layer: str,
        end_layer: str,
    ):
        """Initialize a Via with properties."""
        if not uid:
            raise ValueError("Via uid cannot be empty")
        if not net:
            raise ValueError("Via net cannot be empty")
        if outer_diameter <= 0:
            raise ValueError(f"Via outer_diameter must be positive, got {outer_diameter}")
        if hole_diameter <= 0:
            raise ValueError(f"Via hole_diameter must be positive, got {hole_diameter}")
        if hole_diameter >= outer_diameter:
            raise ValueError(
                f"Via hole_diameter ({hole_diameter}) must be less than "
                f"outer_diameter ({outer_diameter})"
            )
        if not start_layer or not end_layer:
            raise ValueError("Via start_layer and end_layer cannot be empty")

        self.uid = uid
        self.net = net
        self.center = center
        self.outer_diameter = outer_diameter
        self.hole_diameter = hole_diameter
        self.start_layer = start_layer
        self.end_layer = end_layer

    def __repr__(self) -> str:
        """String representation of Via."""
        return (
            f"Via(uid={self.uid}, net={self.net}, "
            f"outer={self.outer_diameter}, hole={self.hole_diameter})"
        )


class Board:
    """
    Represents a complete PCB board definition.

    This is the root container for all PCB data including the board outline,
    layer stackup, components, traces, vias, and other features.

    Attributes:
        name: Board name/identifier
        design_units: Original design units (MICRON, MILLIMETER, MILS, INCH)
        boundary: Board outline polygon
        stackup: Layer stackup definition
        components: Dictionary of components keyed by reference designator
        traces: Dictionary of traces keyed by UID
        vias: Dictionary of vias keyed by UID
        pours: Dictionary of copper pours (placeholder)
        keepouts: List of keepout polygons
        nets: Dictionary of net definitions (placeholder)

    Raises:
        ValueError: If required fields are missing or invalid
    """

    def __init__(
        self,
        name: str,
        design_units: str,
        boundary: Polygon,
        stackup: Stackup,
        components: dict[str, Component] | None = None,
        traces: dict[str, Trace] | None = None,
        vias: dict[str, Via] | None = None,
        pours: dict[str, Any] | None = None,
        keepouts: list[Polygon] | None = None,
        nets: dict[str, Any] | None = None,
    ):
        """Initialize a Board with all properties."""
        if not name:
            raise ValueError("Board name cannot be empty")
        if not design_units:
            raise ValueError("Board design_units cannot be empty")

        # Validate design units
        valid_units = ["MICRON", "MILLIMETER", "MILS", "INCH"]
        if design_units not in valid_units:
            raise ValueError(
                f"Invalid design_units '{design_units}'. Must be one of: {valid_units}"
            )

        self.name = name
        self.design_units = design_units
        self.boundary = boundary
        self.stackup = stackup
        self.components = components or {}
        self.traces = traces or {}
        self.vias = vias or {}
        self.pours = pours or {}
        self.keepouts = keepouts or []
        self.nets = nets or {}

    def __repr__(self) -> str:
        """String representation of Board."""
        return (
            f"Board(name={self.name}, units={self.design_units}, "
            f"{len(self.stackup.layers)} layers, "
            f"{len(self.components)} components, "
            f"{len(self.traces)} traces, "
            f"{len(self.vias)} vias)"
        )
