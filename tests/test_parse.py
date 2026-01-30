"""Tests for board JSON parsing."""

import pytest

from pcb_render.parse import parse_board
from pcb_render.models import LayerType, Side


class TestParseBoard:
    """Tests for parse_board function."""

    def test_parse_minimal_board(self, load_json_file):
        """Test parsing a minimal valid board."""
        data = load_json_file("minimal_board.json")
        board = parse_board(data)

        assert board.name == "minimal_board"
        assert board.design_units == "MILLIMETER"
        assert len(board.stackup.layers) == 1
        assert board.stackup.layers[0].layer_type == LayerType.TOP
        assert len(board.components) == 1
        assert len(board.traces) == 1
        assert len(board.vias) == 0
        assert len(board.nets) == 2

    def test_parse_complex_board(self, load_json_file):
        """Test parsing a complex multi-layer board with MICRON units."""
        data = load_json_file("complex_board.json")
        board = parse_board(data)

        assert board.name == "complex_board"
        assert board.design_units == "MICRON"
        assert len(board.stackup.layers) == 4
        assert len(board.components) == 2
        assert len(board.traces) == 2
        assert len(board.vias) == 2
        assert len(board.keepouts) == 1

        # Check coordinate normalization (MICRON to MILLIMETER)
        assert board.boundary.points[0].x == 0.0
        assert board.boundary.points[1].x == 100.0  # 100000 MICRON = 100 mm

    def test_parse_board_default_design_units(self):
        """Test that missing designUnits defaults to MICRON."""
        data = {
            "name": "test",
            "boundary": {
                "points": [[0, 0], [1000, 0], [1000, 1000], [0, 1000], [0, 0]]
            },
            "stackup": {
                "layers": [
                    {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"}
                ]
            },
        }
        board = parse_board(data)
        assert board.design_units == "MICRON"

    def test_parse_board_invalid_design_units_raises_error(self):
        """Test that invalid designUnits raises ValueError."""
        data = {
            "name": "test",
            "designUnits": "INVALID_UNIT",
            "boundary": {
                "points": [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
            },
            "stackup": {
                "layers": [
                    {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"}
                ]
            },
        }
        with pytest.raises(ValueError, match="Invalid designUnits"):
            parse_board(data)

    def test_parse_missing_boundary_raises_error(self):
        """Test that missing boundary raises ValueError."""
        data = {
            "name": "test",
            "boundary": {},
            "stackup": {
                "layers": [
                    {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"}
                ]
            },
        }
        with pytest.raises(ValueError, match="boundary is missing"):
            parse_board(data)

    def test_parse_boundary_without_points_raises_error(self):
        """Test that boundary without points raises ValueError."""
        data = {
            "name": "test",
            "boundary": {"points": []},
            "stackup": {
                "layers": [
                    {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"}
                ]
            },
        }
        with pytest.raises(ValueError, match="no points"):
            parse_board(data)

    def test_parse_component_with_both_sides(self, load_json_file):
        """Test parsing components on different sides."""
        data = load_json_file("complex_board.json")
        board = parse_board(data)

        # R1 is on FRONT
        assert board.components["R1"].side == Side.FRONT
        # U1 is on BACK
        assert board.components["U1"].side == Side.BACK

    def test_parse_component_rotation(self, load_json_file):
        """Test parsing component rotation."""
        data = load_json_file("complex_board.json")
        board = parse_board(data)

        assert board.components["R1"].rotation == 0.0
        assert board.components["U1"].rotation == 45.0

    def test_parse_component_outline(self, load_json_file):
        """Test parsing component outline."""
        data = load_json_file("complex_board.json")
        board = parse_board(data)

        # R1 has an outline
        r1_outline = board.components["R1"].outline
        assert r1_outline is not None
        assert len(r1_outline.points) == 5  # Closed polygon

        # Check outline is normalized (MICRON to MILLIMETER)
        assert r1_outline.points[0].x == 4.0  # 4000 MICRON = 4 mm

    def test_parse_trace_width_normalization(self, load_json_file):
        """Test that trace width is normalized correctly."""
        data = load_json_file("complex_board.json")
        board = parse_board(data)

        # trace1 has width 200 MICRON = 0.2 mm
        trace1 = board.traces["trace1"]
        assert trace1.width == 0.2

        # trace2 has width 300 MICRON = 0.3 mm
        trace2 = board.traces["trace2"]
        assert trace2.width == 0.3

    def test_parse_via_diameters(self, load_json_file):
        """Test parsing via with normalized diameters."""
        data = load_json_file("complex_board.json")
        board = parse_board(data)

        via1 = board.vias["via1"]
        assert via1.outer_diameter == 0.8  # 800 MICRON
        assert via1.hole_diameter == 0.4   # 400 MICRON

    def test_parse_keepouts(self, load_json_file):
        """Test parsing keepout regions."""
        data = load_json_file("complex_board.json")
        board = parse_board(data)

        assert len(board.keepouts) == 1
        keepout = board.keepouts[0]
        assert len(keepout.points) == 5  # Closed polygon

    def test_parse_empty_components(self):
        """Test parsing board with no components."""
        data = {
            "name": "test",
            "designUnits": "MILLIMETER",
            "boundary": {
                "points": [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
            },
            "stackup": {
                "layers": [
                    {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"}
                ]
            },
        }
        board = parse_board(data)
        assert len(board.components) == 0

    def test_parse_empty_traces(self):
        """Test parsing board with no traces."""
        data = {
            "name": "test",
            "designUnits": "MILLIMETER",
            "boundary": {
                "points": [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
            },
            "stackup": {
                "layers": [
                    {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"}
                ]
            },
        }
        board = parse_board(data)
        assert len(board.traces) == 0

    def test_parse_invalid_layer_type_raises_error(self):
        """Test that invalid layer type raises ValueError."""
        data = {
            "name": "test",
            "designUnits": "MILLIMETER",
            "boundary": {
                "points": [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
            },
            "stackup": {
                "layers": [
                    {"name": "TOP", "type": "INVALID_TYPE", "index": 0, "hash": "top"}
                ]
            },
        }
        with pytest.raises(ValueError, match="Invalid layer type"):
            parse_board(data)

    def test_parse_invalid_side_raises_error(self):
        """Test that invalid component side raises ValueError."""
        data = {
            "name": "test",
            "designUnits": "MILLIMETER",
            "boundary": {
                "points": [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
            },
            "stackup": {
                "layers": [
                    {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"}
                ]
            },
            "components": {
                "R1": {
                    "footprint": "RES",
                    "position": {"x": 5, "y": 5},
                    "side": "INVALID_SIDE",
                }
            },
        }
        with pytest.raises(ValueError, match="Invalid component side"):
            parse_board(data)
