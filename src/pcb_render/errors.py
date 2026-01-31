"""
Error definitions and validation error reporting.

This module defines the error taxonomy used throughout the PCB renderer,
including error severity levels and specific error codes for board validation.
"""

from enum import Enum


class ErrorSeverity(str, Enum):
    """Severity level for validation errors."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


# Error code constants
E001_MISSING_BOUNDARY = "E001_MISSING_BOUNDARY"
E001_BOUNDARY_NOT_CLOSED = "E001_BOUNDARY_NOT_CLOSED"
E002_MALFORMED_COORDINATES = "E002_MALFORMED_COORDINATES"
E003_INVALID_ROTATION = "E003_INVALID_ROTATION"
E004_NEGATIVE_WIDTH = "E004_NEGATIVE_WIDTH"
E005_INVALID_VIA_GEOMETRY = "E005_INVALID_VIA_GEOMETRY"
E006_NONEXISTENT_LAYER = "E006_NONEXISTENT_LAYER"
E007_NONEXISTENT_NET = "E007_NONEXISTENT_NET"
E008_SELF_INTERSECTING_BOUNDARY = "E008_SELF_INTERSECTING_BOUNDARY"
E009_COMPONENT_OUTSIDE_BOUNDARY = "E009_COMPONENT_OUTSIDE_BOUNDARY"
E010_DUPLICATE_LAYER_HASH = "E010_DUPLICATE_LAYER_HASH"
E011_NON_SEQUENTIAL_LAYER_INDICES = "E011_NON_SEQUENTIAL_LAYER_INDICES"
E012_EMPTY_STACKUP = "E012_EMPTY_STACKUP"
E013_INVALID_DESIGN_UNITS = "E013_INVALID_DESIGN_UNITS"
E014_NEGATIVE_DIAMETER = "E014_NEGATIVE_DIAMETER"


# Error messages and suggestions
_ERROR_MESSAGES = {
    E001_MISSING_BOUNDARY: {
        "severity": ErrorSeverity.ERROR,
        "message": "Board boundary is missing or undefined",
        "suggestion": (
            "Add a 'boundary' field with a polygon containing at least 3 coordinate pairs"
        ),
    },
    E001_BOUNDARY_NOT_CLOSED: {
        "severity": ErrorSeverity.ERROR,
        "message": "Board boundary polygon is not closed (first point != last point)",
        "suggestion": "Ensure the boundary polygon's first point equals its last point",
    },
    E002_MALFORMED_COORDINATES: {
        "severity": ErrorSeverity.ERROR,
        "message": "Coordinate data contains NaN, Infinity, or invalid values",
        "suggestion": "Ensure all coordinate values are finite numbers (not NaN or Infinity)",
    },
    E003_INVALID_ROTATION: {
        "severity": ErrorSeverity.ERROR,
        "message": "Rotation value is invalid (NaN, Infinity, or non-numeric)",
        "suggestion": "Ensure rotation values are finite numbers in degrees",
    },
    E004_NEGATIVE_WIDTH: {
        "severity": ErrorSeverity.ERROR,
        "message": "Trace or feature width is negative or zero",
        "suggestion": "Width values must be positive numbers greater than zero",
    },
    E005_INVALID_VIA_GEOMETRY: {
        "severity": ErrorSeverity.ERROR,
        "message": "Via hole diameter is greater than or equal to outer diameter",
        "suggestion": "Ensure hole_diameter < outer_diameter and both are positive",
    },
    E006_NONEXISTENT_LAYER: {
        "severity": ErrorSeverity.ERROR,
        "message": "Feature references a layer hash that does not exist in the stackup",
        "suggestion": "Check that the layer_hash value matches a layer defined in the stackup",
    },
    E007_NONEXISTENT_NET: {
        "severity": ErrorSeverity.WARNING,
        "message": "Feature references a net name that is not defined in the nets dictionary",
        "suggestion": "Add the net to the nets dictionary or verify the net name spelling",
    },
    E008_SELF_INTERSECTING_BOUNDARY: {
        "severity": ErrorSeverity.ERROR,
        "message": "Board boundary polygon self-intersects",
        "suggestion": "Fix the boundary polygon coordinates to remove self-intersections",
    },
    E009_COMPONENT_OUTSIDE_BOUNDARY: {
        "severity": ErrorSeverity.WARNING,
        "message": "Component is positioned outside the board boundary",
        "suggestion": "Check component position coordinates or adjust the board boundary",
    },
    E010_DUPLICATE_LAYER_HASH: {
        "severity": ErrorSeverity.ERROR,
        "message": "Multiple layers in the stackup have the same hash identifier",
        "suggestion": "Ensure each layer has a unique hash value",
    },
    E011_NON_SEQUENTIAL_LAYER_INDICES: {
        "severity": ErrorSeverity.ERROR,
        "message": "Layer indices are not sequential starting from 0",
        "suggestion": "Renumber layer indices to be sequential (0, 1, 2, ...)",
    },
    E012_EMPTY_STACKUP: {
        "severity": ErrorSeverity.ERROR,
        "message": "Stackup does not contain any layers",
        "suggestion": "Add at least one layer to the stackup definition",
    },
    E013_INVALID_DESIGN_UNITS: {
        "severity": ErrorSeverity.ERROR,
        "message": "Design units must be one of: MICRON, MILLIMETER, MILS, INCH",
        "suggestion": "Set designUnits to one of the supported unit types",
    },
    E014_NEGATIVE_DIAMETER: {
        "severity": ErrorSeverity.ERROR,
        "message": "Via diameter (outer or hole) is negative or zero",
        "suggestion": "Ensure all diameter values are positive numbers greater than zero",
    },
}


class ValidationError:
    """
    Represents a single validation error found in a board definition.

    Attributes:
        code: Error code (e.g., "E001_MISSING_BOUNDARY")
        severity: Error severity level (ERROR, WARNING, INFO)
        message: Human-readable error description
        json_path: JSON path to the error location (e.g., "components.R1.position")
        suggestion: How to fix the error
    """

    def __init__(
        self,
        code: str,
        severity: ErrorSeverity,
        message: str,
        json_path: str | None = None,
        suggestion: str | None = None,
    ):
        """Initialize a ValidationError with all properties."""
        self.code = code
        self.severity = severity
        self.message = message
        self.json_path = json_path
        self.suggestion = suggestion

    @classmethod
    def from_code(
        cls, code: str, json_path: str | None = None
    ) -> "ValidationError":
        """
        Create a ValidationError from a predefined error code.

        Args:
            code: Error code constant (e.g., E001_MISSING_BOUNDARY)
            json_path: Optional JSON path to the error location

        Returns:
            A ValidationError instance with predefined message and suggestion

        Raises:
            ValueError: If the error code is not recognized
        """
        if code not in _ERROR_MESSAGES:
            raise ValueError(f"Unknown error code: {code}")

        error_info = _ERROR_MESSAGES[code]
        return cls(
            code=code,
            severity=error_info["severity"],
            message=error_info["message"],
            json_path=json_path,
            suggestion=error_info["suggestion"],
        )

    def __repr__(self) -> str:
        """String representation of ValidationError."""
        path_str = f" @ {self.json_path}" if self.json_path else ""
        return f"ValidationError({self.code}{path_str}: {self.message})"

    def __str__(self) -> str:
        """User-friendly string representation."""
        lines = [
            f"[{self.severity.value}] {self.code}",
            f"  Message: {self.message}",
        ]
        if self.json_path:
            lines.append(f"  Location: {self.json_path}")
        if self.suggestion:
            lines.append(f"  Suggestion: {self.suggestion}")
        return "\n".join(lines)
