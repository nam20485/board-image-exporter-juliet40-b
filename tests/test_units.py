"""Tests for unit conversion utilities."""

import pytest

from pcb_render.units import normalize_value, normalize_coordinates


class TestNormalizeValue:
    """Tests for normalize_value function."""

    def test_micron_to_mm(self):
        """Test converting microns to millimeters."""
        assert normalize_value(1000, "MICRON") == 1.0
        assert normalize_value(50000, "MICRON") == 50.0
        assert normalize_value(0, "MICRON") == 0.0

    def test_millimeter_to_mm(self):
        """Test converting millimeters to millimeters (identity)."""
        assert normalize_value(1.0, "MILLIMETER") == 1.0
        assert normalize_value(25.4, "MILLIMETER") == 25.4
        assert normalize_value(0, "MILLIMETER") == 0.0

    def test_mils_to_mm(self):
        """Test converting mils to millimeters."""
        assert normalize_value(100, "MILS") == 2.54
        assert normalize_value(1000, "MILS") == 25.4

    def test_inch_to_mm(self):
        """Test converting inches to millimeters."""
        assert normalize_value(0.1, "INCH") == 2.54
        assert normalize_value(1.0, "INCH") == 25.4
        assert normalize_value(0.01, "INCH") == 0.254

    def test_case_insensitive_units(self):
        """Test that unit strings are case-insensitive."""
        assert normalize_value(1000, "micron") == 1.0
        assert normalize_value(1000, "Micron") == 1.0
        assert normalize_value(1000, "MICRON") == 1.0

    def test_unknown_unit_raises_error(self):
        """Test that unknown units raise ValueError."""
        with pytest.raises(ValueError, match="Unknown unit"):
            normalize_value(1.0, "UNKNOWN_UNIT")
        with pytest.raises(ValueError, match="Unknown unit"):
            normalize_value(1.0, "cm")

    def test_negative_values(self):
        """Test that negative values are handled correctly."""
        assert normalize_value(-1000, "MICRON") == -1.0
        assert normalize_value(-1.0, "MILLIMETER") == -1.0

    def test_large_values(self):
        """Test conversion of large values."""
        assert normalize_value(1_000_000, "MICRON") == 1000.0
        assert normalize_value(10000, "MILS") == 254.0


class TestNormalizeCoordinates:
    """Tests for normalize_coordinates function."""

    def test_flat_format_micron(self):
        """Test flat format coordinates in microns."""
        coords = [0, 0, 1000, 2000, 5000, 5000]
        result = normalize_coordinates(coords, "MICRON")
        assert result == [0.0, 0.0, 1.0, 2.0, 5.0, 5.0]

    def test_flat_format_millimeter(self):
        """Test flat format coordinates in millimeters."""
        coords = [0.0, 0.0, 1.5, 2.5, 10.0, 20.0]
        result = normalize_coordinates(coords, "MILLIMETER")
        assert result == [0.0, 0.0, 1.5, 2.5, 10.0, 20.0]

    def test_nested_format_micron(self):
        """Test nested format coordinates in microns."""
        coords = [[0, 0], [1000, 2000], [5000, 5000]]
        result = normalize_coordinates(coords, "MICRON")
        assert result == [[0.0, 0.0], [1.0, 2.0], [5.0, 5.0]]

    def test_nested_format_millimeter(self):
        """Test nested format coordinates in millimeters."""
        coords = [[0.0, 0.0], [1.5, 2.5], [10.0, 20.0]]
        result = normalize_coordinates(coords, "MILLIMETER")
        assert result == [[0.0, 0.0], [1.5, 2.5], [10.0, 20.0]]

    def test_empty_list(self):
        """Test normalizing an empty coordinate list."""
        assert normalize_coordinates([], "MICRON") == []

    def test_mixed_units(self):
        """Test conversion with different units."""
        # MILS
        coords = [0, 0, 100, 0]
        result = normalize_coordinates(coords, "MILS")
        assert result == [0.0, 0.0, 2.54, 0.0]

        # INCH
        coords = [[0, 0], [0.1, 0]]
        result = normalize_coordinates(coords, "INCH")
        assert result == [[0.0, 0.0], [2.54, 0.0]]

    def test_flat_format_odd_length_raises_error(self):
        """Test that flat format with odd length raises ValueError."""
        with pytest.raises(ValueError, match="even number"):
            normalize_coordinates([0, 1000, 2000], "MICRON")

    def test_single_point_flat(self):
        """Test single point in flat format."""
        result = normalize_coordinates([5000, 3000], "MICRON")
        assert result == [5.0, 3.0]

    def test_single_point_nested(self):
        """Test single point in nested format."""
        result = normalize_coordinates([[5000, 3000]], "MICRON")
        assert result == [[5.0, 3.0]]

    def test_negative_coordinates(self):
        """Test handling of negative coordinates."""
        coords = [[-1000, -1000], [1000, 1000]]
        result = normalize_coordinates(coords, "MICRON")
        assert result == [[-1.0, -1.0], [1.0, 1.0]]

    def test_zero_coordinates(self):
        """Test zero coordinates."""
        coords = [0, 0]
        result = normalize_coordinates(coords, "MILLIMETER")
        assert result == [0.0, 0.0]
