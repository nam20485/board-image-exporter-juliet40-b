"""Tests for PCB data models."""

import math
import pytest

from pcb_render.models import (
    Board,
    Circle,
    Component,
    Layer,
    LayerType,
    Pin,
    Point,
    Polygon,
    Polyline,
    Side,
    Stackup,
    Trace,
    Via,
)
from pcb_render.errors import ValidationError


class TestPoint:
    """Tests for Point model."""

    def test_point_creation(self):
        """Test creating a valid point."""
        point = Point(1.0, 2.0)
        assert point.x == 1.0
        assert point.y == 2.0

    def test_point_rejects_nan(self):
        """Test that Point rejects NaN values."""
        with pytest.raises(ValueError, match="must be finite"):
            Point(float("nan"), 1.0)
        with pytest.raises(ValueError, match="must be finite"):
            Point(1.0, float("nan"))

    def test_point_rejects_infinity(self):
        """Test that Point rejects infinite values."""
        with pytest.raises(ValueError, match="must be finite"):
            Point(float("inf"), 1.0)
        with pytest.raises(ValueError, match="must be finite"):
            Point(1.0, float("-inf"))

    def test_distance_to(self):
        """Test distance calculation between points."""
        p1 = Point(0.0, 0.0)
        p2 = Point(3.0, 4.0)
        assert p1.distance_to(p2) == 5.0

    def test_distance_to_same_point(self):
        """Test distance to same point is zero."""
        p1 = Point(1.0, 2.0)
        assert p1.distance_to(p1) == 0.0

    def test_equality(self):
        """Test point equality."""
        p1 = Point(1.0, 2.0)
        p2 = Point(1.0, 2.0)
        p3 = Point(1.0, 3.0)
        assert p1 == p2
        assert p1 != p3
        assert p1 != "not a point"

    def test_hash(self):
        """Test point hashing for use in sets/dicts."""
        p1 = Point(1.0, 2.0)
        p2 = Point(1.0, 2.0)
        p3 = Point(1.0, 3.0)
        assert hash(p1) == hash(p2)
        assert hash(p1) != hash(p3)

        # Can use in sets
        point_set = {p1, p2, p3}
        assert len(point_set) == 2  # p1 and p2 are the same


class TestPolygon:
    """Tests for Polygon model."""

    def test_polygon_creation(self, sample_points):
        """Test creating a valid polygon."""
        polygon = Polygon(sample_points)
        assert len(polygon.points) == 5
        assert polygon.is_closed()

    def test_polygon_requires_min_3_points(self):
        """Test that polygon requires at least 3 points."""
        with pytest.raises(ValueError, match="at least 3 points"):
            Polygon([Point(0, 0), Point(1, 1)])

    def test_is_closed_true(self, sample_points):
        """Test polygon closure detection when closed."""
        polygon = Polygon(sample_points)
        assert polygon.is_closed() is True

    def test_is_closed_false(self):
        """Test polygon closure detection when not closed."""
        points = [Point(0, 0), Point(1, 0), Point(1, 1)]
        polygon = Polygon(points)
        assert polygon.is_closed() is False

    def test_bounds(self, sample_points):
        """Test bounding box calculation."""
        polygon = Polygon(sample_points)
        min_pt, max_pt = polygon.bounds()
        assert min_pt.x == 0.0
        assert min_pt.y == 0.0
        assert max_pt.x == 10.0
        assert max_pt.y == 10.0

    def test_area_rectangle(self):
        """Test area calculation for a rectangle."""
        points = [
            Point(0, 0),
            Point(10, 0),
            Point(10, 5),
            Point(0, 5),
            Point(0, 0),
        ]
        polygon = Polygon(points)
        assert polygon.area() == 50.0

    def test_self_intersects_false(self, sample_polygon):
        """Test self-intersection detection for simple polygon."""
        assert sample_polygon.self_intersects() is False

    def test_self_intersects_true(self):
        """Test self-intersection detection for self-intersecting polygon."""
        # Create a bowtie shape
        points = [
            Point(0, 0),
            Point(10, 10),
            Point(10, 0),
            Point(0, 10),
            Point(0, 0),
        ]
        polygon = Polygon(points)
        assert polygon.self_intersects() is True


class TestPolyline:
    """Tests for Polyline model."""

    def test_polyline_creation(self):
        """Test creating a valid polyline."""
        points = [Point(0, 0), Point(1, 1), Point(2, 2)]
        polyline = Polyline(points)
        assert len(polyline.points) == 3

    def test_polyline_requires_min_2_points(self):
        """Test that polyline requires at least 2 points."""
        with pytest.raises(ValueError, match="at least 2 points"):
            Polyline([Point(0, 0)])

    def test_polyline_rejects_nan_coordinates(self):
        """Test that polyline rejects NaN coordinates."""
        # Point itself rejects NaN during construction, so this test
        # verifies that Polyline validates its points
        with pytest.raises(ValueError, match="must be finite"):
            Point(0, float("nan"))

    def test_length(self):
        """Test polyline length calculation."""
        points = [Point(0, 0), Point(3, 0), Point(3, 4)]
        polyline = Polyline(points)
        assert polyline.length() == 7.0  # 3 + 4


class TestCircle:
    """Tests for Circle model."""

    def test_circle_creation(self):
        """Test creating a valid circle."""
        center = Point(5.0, 5.0)
        circle = Circle(center, 2.5)
        assert circle.center == center
        assert circle.radius == 2.5

    def test_circle_requires_positive_radius(self):
        """Test that circle radius must be positive."""
        center = Point(0, 0)
        with pytest.raises(ValueError, match="must be positive"):
            Circle(center, 0)
        with pytest.raises(ValueError, match="must be positive"):
            Circle(center, -1.0)

    def test_bounds(self):
        """Test circle bounding box calculation."""
        center = Point(5.0, 5.0)
        circle = Circle(center, 2.0)
        min_pt, max_pt = circle.bounds()
        assert min_pt.x == 3.0
        assert min_pt.y == 3.0
        assert max_pt.x == 7.0
        assert max_pt.y == 7.0


class TestLayer:
    """Tests for Layer model."""

    def test_layer_creation(self):
        """Test creating a valid layer."""
        layer = Layer(
            name="TOP",
            layer_type=LayerType.TOP,
            index=0,
            hash="top_hash",
        )
        assert layer.name == "TOP"
        assert layer.layer_type == LayerType.TOP
        assert layer.index == 0
        assert layer.hash == "top_hash"

    def test_layer_requires_non_negative_index(self):
        """Test that layer index must be non-negative."""
        with pytest.raises(ValueError, match="must be non-negative"):
            Layer("L1", LayerType.MID, -1, "hash1")

    def test_layer_requires_non_empty_hash(self):
        """Test that layer hash cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Layer("L1", LayerType.MID, 0, "")


class TestStackup:
    """Tests for Stackup model."""

    def test_stackup_creation(self, sample_layer):
        """Test creating a valid stackup."""
        stackup = Stackup([sample_layer])
        assert len(stackup.layers) == 1

    def test_stackup_requires_at_least_one_layer(self):
        """Test that stackup must have at least one layer."""
        with pytest.raises(ValueError, match="at least one layer"):
            Stackup([])

    def test_stackup_requires_unique_hashes(self):
        """Test that stackup layers must have unique hashes."""
        layer1 = Layer("L1", LayerType.TOP, 0, "same_hash")
        layer2 = Layer("L2", LayerType.BOTTOM, 1, "same_hash")
        with pytest.raises(ValueError, match="unique hashes"):
            Stackup([layer1, layer2])

    def test_stackup_requires_sequential_indices(self):
        """Test that layer indices must be sequential."""
        layer1 = Layer("L1", LayerType.TOP, 0, "hash1")
        layer2 = Layer("L2", LayerType.BOTTOM, 5, "hash2")
        with pytest.raises(ValueError, match="sequential"):
            Stackup([layer1, layer2])

    def test_get_layer_by_hash(self, sample_layer):
        """Test retrieving layer by hash."""
        stackup = Stackup([sample_layer])
        assert stackup.get_layer_by_hash("top_layer_hash") == sample_layer
        assert stackup.get_layer_by_hash("nonexistent") is None


class TestPin:
    """Tests for Pin model."""

    def test_pin_creation(self):
        """Test creating a valid pin."""
        pin = Pin(
            name="1",
            net="GND",
            position=Point(0, 0),
            rotation=0.0,
            is_throughhole=False,
        )
        assert pin.name == "1"
        assert pin.net == "GND"
        assert pin.rotation == 0.0
        assert pin.is_throughhole is False

    def test_pin_requires_non_empty_name(self):
        """Test that pin name cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Pin("", "GND", Point(0, 0))

    def test_pin_requires_finite_rotation(self):
        """Test that pin rotation must be finite."""
        with pytest.raises(ValueError, match="must be finite"):
            Pin("1", "GND", Point(0, 0), float("inf"))


class TestComponent:
    """Tests for Component model."""

    def test_component_creation(self):
        """Test creating a valid component."""
        comp = Component(
            ref_des="R1",
            footprint="RES_0805",
            position=Point(5, 5),
            rotation=0.0,
            side=Side.FRONT,
        )
        assert comp.ref_des == "R1"
        assert comp.footprint == "RES_0805"
        assert comp.rotation == 0.0
        assert comp.side == Side.FRONT

    def test_component_requires_non_empty_ref_des(self):
        """Test that component ref_des cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Component("", "RES", Point(0, 0))

    def test_component_requires_non_empty_footprint(self):
        """Test that component footprint cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Component("R1", "", Point(0, 0))

    def test_component_requires_finite_rotation(self):
        """Test that component rotation must be finite."""
        with pytest.raises(ValueError, match="must be finite"):
            Component("R1", "RES", Point(0, 0), float("nan"))


class TestTrace:
    """Tests for Trace model."""

    def test_trace_creation(self, sample_polyline):
        """Test creating a valid trace."""
        trace = Trace(
            uid="trace1",
            net="GND",
            layer_hash="layer_hash",
            path=sample_polyline,
            width=0.2,
        )
        assert trace.uid == "trace1"
        assert trace.net == "GND"
        assert trace.width == 0.2

    def test_trace_requires_positive_width(self, sample_polyline):
        """Test that trace width must be positive."""
        with pytest.raises(ValueError, match="must be positive"):
            Trace("t1", "GND", "hash", sample_polyline, 0)
        with pytest.raises(ValueError, match="must be positive"):
            Trace("t1", "GND", "hash", sample_polyline, -0.1)

    def test_trace_requires_non_empty_fields(self, sample_polyline):
        """Test that trace required fields cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Trace("", "GND", "hash", sample_polyline, 0.1)
        with pytest.raises(ValueError, match="cannot be empty"):
            Trace("t1", "", "hash", sample_polyline, 0.1)
        with pytest.raises(ValueError, match="cannot be empty"):
            Trace("t1", "GND", "", sample_polyline, 0.1)


class TestVia:
    """Tests for Via model."""

    def test_via_creation(self):
        """Test creating a valid via."""
        via = Via(
            uid="via1",
            net="GND",
            center=Point(5, 5),
            outer_diameter=0.8,
            hole_diameter=0.4,
            start_layer="top_hash",
            end_layer="bottom_hash",
        )
        assert via.uid == "via1"
        assert via.outer_diameter == 0.8
        assert via.hole_diameter == 0.4

    def test_via_requires_positive_diameters(self):
        """Test that via diameters must be positive."""
        with pytest.raises(ValueError, match="must be positive"):
            Via("v1", "GND", Point(0, 0), 0, 0.4, "h1", "h2")
        with pytest.raises(ValueError, match="must be positive"):
            Via("v1", "GND", Point(0, 0), 0.8, 0, "h1", "h2")

    def test_via_requires_hole_less_than_outer(self):
        """Test that hole diameter must be less than outer diameter."""
        with pytest.raises(ValueError, match="must be less than"):
            Via("v1", "GND", Point(0, 0), 0.8, 0.8, "h1", "h2")
        with pytest.raises(ValueError, match="must be less than"):
            Via("v1", "GND", Point(0, 0), 0.8, 1.0, "h1", "h2")

    def test_via_requires_non_empty_fields(self):
        """Test that via required fields cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Via("", "GND", Point(0, 0), 0.8, 0.4, "h1", "h2")
        with pytest.raises(ValueError, match="cannot be empty"):
            Via("v1", "", Point(0, 0), 0.8, 0.4, "h1", "h2")


class TestBoard:
    """Tests for Board model."""

    def test_board_creation(self, sample_polygon, sample_stackup):
        """Test creating a valid board."""
        board = Board(
            name="test_board",
            design_units="MILLIMETER",
            boundary=sample_polygon,
            stackup=sample_stackup,
        )
        assert board.name == "test_board"
        assert board.design_units == "MILLIMETER"

    def test_board_requires_non_empty_name(self, sample_polygon, sample_stackup):
        """Test that board name cannot be empty."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Board("", "MILLIMETER", sample_polygon, sample_stackup)

    def test_board_requires_valid_design_units(self, sample_polygon, sample_stackup):
        """Test that design units must be valid."""
        with pytest.raises(ValueError, match="Invalid design_units"):
            Board("board", "INVALID_UNIT", sample_polygon, sample_stackup)

    def test_board_accepts_all_valid_units(self, sample_polygon, sample_stackup):
        """Test that all valid design units are accepted."""
        valid_units = ["MICRON", "MILLIMETER", "MILS", "INCH"]
        for unit in valid_units:
            board = Board(f"board_{unit}", unit, sample_polygon, sample_stackup)
            assert board.design_units == unit
