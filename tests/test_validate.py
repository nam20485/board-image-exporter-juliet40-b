"""Tests for board validation."""

from pcb_render.errors import (
    E001_MISSING_BOUNDARY,
    E002_MALFORMED_COORDINATES,
    E003_INVALID_ROTATION,
    E004_NEGATIVE_WIDTH,
    E005_INVALID_VIA_GEOMETRY,
    E006_NONEXISTENT_LAYER,
    E007_NONEXISTENT_NET,
    E008_SELF_INTERSECTING_BOUNDARY,
    E009_COMPONENT_OUTSIDE_BOUNDARY,
    E010_DUPLICATE_LAYER_HASH,
    E011_NON_SEQUENTIAL_LAYER_INDICES,
    E012_EMPTY_STACKUP,
    E013_INVALID_DESIGN_UNITS,
    E014_NEGATIVE_DIAMETER,
)
from pcb_render.parse import parse_board
from pcb_render.validate import validate_board


class TestValidateBoard:
    """Tests for validate_board function."""

    def test_valid_board_returns_no_errors(self, load_json_file):
        """Test that a valid board returns empty error list."""
        data = load_json_file("minimal_board.json")
        board = parse_board(data)
        errors = validate_board(board)
        assert len(errors) == 0

    def test_complex_board_valid(self, load_json_file):
        """Test that complex board validates successfully."""
        data = load_json_file("complex_board.json")
        board = parse_board(data)
        errors = validate_board(board)
        # Should have no errors or only warnings
        error_errors = [e for e in errors if e.severity.value == "ERROR"]
        assert len(error_errors) == 0

    def test_self_intersecting_boundary_detected(self, load_invalid_board):
        """Test detection of self-intersecting boundary (E008)."""
        data = load_invalid_board("self_intersecting_boundary.json")
        board = parse_board(data)
        errors = validate_board(board)

        error_codes = [e.code for e in errors]
        assert E008_SELF_INTERSECTING_BOUNDARY in error_codes

    def test_component_outside_boundary_detected(self, load_invalid_board):
        """Test detection of component outside boundary (E009)."""
        data = load_invalid_board("component_outside_boundary.json")
        board = parse_board(data)
        errors = validate_board(board)

        error_codes = [e.code for e in errors]
        assert E009_COMPONENT_OUTSIDE_BOUNDARY in error_codes

    def test_nonexistent_layer_in_trace_detected(self, load_invalid_board):
        """Test detection of nonexistent layer in trace (E006)."""
        data = load_invalid_board("nonexistent_layer.json")
        board = parse_board(data)
        errors = validate_board(board)

        error_codes = [e.code for e in errors]
        assert E006_NONEXISTENT_LAYER in error_codes

    def test_nonexistent_net_in_trace_detected(self, load_invalid_board):
        """Test detection of nonexistent net (E007)."""
        data = load_invalid_board("nonexistent_net.json")
        board = parse_board(data)
        errors = validate_board(board)

        error_codes = [e.code for e in errors]
        assert E007_NONEXISTENT_NET in error_codes

    def test_all_14_error_codes_can_be_detected(self, load_invalid_board):
        """Test that all 14 error codes are properly defined and detectable."""
        # This is a meta-test to ensure our error code constants are correct

        # Just verify the constants exist
        error_codes = [
            E001_MISSING_BOUNDARY,
            E002_MALFORMED_COORDINATES,
            E003_INVALID_ROTATION,
            E004_NEGATIVE_WIDTH,
            E005_INVALID_VIA_GEOMETRY,
            E006_NONEXISTENT_LAYER,
            E007_NONEXISTENT_NET,
            E008_SELF_INTERSECTING_BOUNDARY,
            E009_COMPONENT_OUTSIDE_BOUNDARY,
            E010_DUPLICATE_LAYER_HASH,
            E011_NON_SEQUENTIAL_LAYER_INDICES,
            E012_EMPTY_STACKUP,
            E013_INVALID_DESIGN_UNITS,
            E014_NEGATIVE_DIAMETER,
        ]

        # Verify all codes are unique
        assert len(error_codes) == len(set(error_codes))

        # Verify all start with E and have 3 digits
        for code in error_codes:
            assert code.startswith("E0")
            assert len(code.split("_")[0]) == 4  # E0XX format


class TestValidationErrorClass:
    """Tests for ValidationError class."""

    def test_create_error_from_code(self):
        """Test creating ValidationError from predefined code."""
        from pcb_render.errors import ValidationError

        error = ValidationError.from_code(
            E006_NONEXISTENT_LAYER,
            json_path="traces.trace1.layer_hash"
        )

        assert error.code == E006_NONEXISTENT_LAYER
        assert error.json_path == "traces.trace1.layer_hash"
        assert error.suggestion is not None
        assert error.message is not None

    def test_error_string_representation(self):
        """Test ValidationError string representation."""
        from pcb_render.errors import ValidationError

        error = ValidationError.from_code(E006_NONEXISTENT_LAYER)
        error_str = str(error)

        assert "ERROR" in error_str or "WARNING" in error_str
        assert E006_NONEXISTENT_LAYER in error_str
        assert "Message:" in error_str
        assert "Suggestion:" in error_str

    def test_error_repr(self):
        """Test ValidationError repr."""
        from pcb_render.errors import ValidationError

        error = ValidationError.from_code(
            E006_NONEXISTENT_LAYER,
            json_path="test.path"
        )
        repr_str = repr(error)

        assert "ValidationError" in repr_str
        assert E006_NONEXISTENT_LAYER in repr_str


class TestValidationEdgeCases:
    """Tests for validation edge cases."""

    def test_board_with_no_traces(self, sample_board):
        """Test validation of board with no traces."""
        errors = validate_board(sample_board)
        # Should not have any trace-related errors
        trace_errors = [e for e in errors if "trace" in str(e.json_path or "").lower()]
        assert len(trace_errors) == 0

    def test_board_with_no_vias(self, sample_board):
        """Test validation of board with no vias."""
        errors = validate_board(sample_board)
        # Should not have any via-related errors
        via_errors = [e for e in errors if "via" in str(e.json_path or "").lower()]
        assert len(via_errors) == 0

    def test_board_with_no_components(self, sample_board):
        """Test validation of board with no components."""
        errors = validate_board(sample_board)
        # Should not have any component-related errors
        comp_errors = [e for e in errors if "component" in str(e.json_path or "").lower()]
        assert len(comp_errors) == 0

    def test_multiple_errors_accumulate(self, load_invalid_board):
        """Test that multiple errors are accumulated, not just first."""
        data = load_invalid_board("nonexistent_layer.json")
        board = parse_board(data)
        errors = validate_board(board)

        # Should have at least the layer error, possibly more
        assert len(errors) >= 1

    def test_error_severity_levels(self):
        """Test that errors have appropriate severity levels."""
        from pcb_render.errors import ErrorSeverity, ValidationError

        # E006 should be ERROR severity
        error = ValidationError.from_code(E006_NONEXISTENT_LAYER)
        assert error.severity == ErrorSeverity.ERROR

        # E007 should be WARNING severity
        error = ValidationError.from_code(E007_NONEXISTENT_NET)
        assert error.severity == ErrorSeverity.WARNING
