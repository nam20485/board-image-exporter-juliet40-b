"""
Unit conversion utilities for PCB coordinates.

This module provides functions to normalize various PCB coordinate units
to millimeters, which is the internal representation used throughout
the PCB renderer.
"""

from typing import Any


# Conversion factors to millimeters
_CONVERSION_FACTORS = {
    "MICRON": 0.001,
    "MILLIMETER": 1.0,
    "MILS": 0.0254,
    "INCH": 25.4,
}


def normalize_value(value: float, from_unit: str) -> float:
    """
    Convert a value from the specified unit to millimeters.

    Args:
        value: The value to convert
        from_unit: The source unit (MICRON, MILLIMETER, MILS, INCH)

    Returns:
        The value converted to millimeters

    Raises:
        ValueError: If the unit is not recognized

    Examples:
        >>> normalize_value(1000, "MICRON")
        1.0
        >>> normalize_value(1.0, "MILLIMETER")
        1.0
        >>> normalize_value(100, "MILS")
        2.54
        >>> normalize_value(0.1, "INCH")
        2.54
    """
    from_unit_upper = from_unit.upper()

    if from_unit_upper not in _CONVERSION_FACTORS:
        valid_units = ", ".join(_CONVERSION_FACTORS.keys())
        raise ValueError(
            f"Unknown unit '{from_unit}'. Valid units are: {valid_units}"
        )

    factor = _CONVERSION_FACTORS[from_unit_upper]
    return value * factor


def normalize_coordinates(coords: list, from_unit: str) -> list[Any]:
    """
    Convert coordinate values from the specified unit to millimeters.

    This function handles both flat and nested coordinate formats:
    - Flat: [x1, y1, x2, y2, ...]
    - Nested: [[x1, y1], [x2, y2], ...]

    Args:
        coords: Coordinate values in either flat or nested format
        from_unit: The source unit (MICRON, MILLIMETER, MILS, INCH)

    Returns:
        List of converted coordinate values in the same format as input

    Raises:
        ValueError: If the unit is not recognized or format is invalid

    Examples:
        >>> normalize_coordinates([0, 0, 1000, 2000], "MICRON")
        [0.0, 0.0, 1.0, 2.0]
        >>> normalize_coordinates([[0, 0], [1, 2]], "MILLIMETER")
        [[0.0, 0.0], [1.0, 2.0]]
    """
    if not coords:
        return []

    # Detect format by checking the first element
    if isinstance(coords[0], list):
        # Nested format: [[x1, y1], [x2, y2], ...]
        return [
            [normalize_value(x, from_unit), normalize_value(y, from_unit)]
            for x, y in coords
        ]
    else:
        # Flat format: [x1, y1, x2, y2, ...]
        if len(coords) % 2 != 0:
            raise ValueError(
                f"Flat coordinate list must have even number of elements, "
                f"got {len(coords)}"
            )
        return [normalize_value(v, from_unit) for v in coords]
