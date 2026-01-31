# PCB Renderer Error Reference

This document provides detailed information about all 14 error codes that the PCB Renderer validation framework can detect.

## Error Format

Each error includes:
- **Code**: Unique error identifier (e.g., E001)
- **Severity**: ERROR, WARNING, or INFO
- **Message**: Human-readable description
- **Suggestion**: How to fix the error
- **Example**: Invalid JSON that triggers the error

---

## E001: Missing Boundary

**Severity**: ERROR
**Message**: Board boundary is missing or undefined

**Description**: The board must have a boundary polygon defining its outline.

**How to Fix**: Add a `boundary` field with a polygon containing at least 3 coordinate pairs.

**Example**:
```json
{
  "name": "board",
  "boundary": {},  // ❌ Empty boundary
  "stackup": {
    "layers": [
      {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"}
    ]
  }
}
```

**Correct**:
```json
{
  "name": "board",
  "boundary": {
    "points": [
      [0, 0],
      [50, 0],
      [50, 50],
      [0, 50],
      [0, 0]
    ]
  },
  "stackup": {
    "layers": [
      {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"}
    ]
  }
}
```

---

## E002: Malformed Coordinates

**Severity**: ERROR
**Message**: Coordinate data contains NaN, Infinity, or invalid values

**Description**: All coordinate values must be finite numbers.

**How to Fix**: Ensure all coordinate values are finite (not NaN or Infinity).

**Example**:
```json
{
  "boundary": {
    "points": [
      [0, NaN],  // ❌ Invalid
      [50, 0],
      [50, 50]
    ]
  }
}
```

---

## E003: Invalid Rotation

**Severity**: ERROR
**Message**: Rotation value is invalid (NaN, Infinity, or non-numeric)

**Description**: Component and pin rotation values must be finite numbers.

**How to Fix**: Ensure rotation values are finite numbers in degrees.

**Example**:
```json
{
  "components": {
    "R1": {
      "footprint": "RES",
      "position": {"x": 5, "y": 5},
      "rotation": "invalid"  // ❌ String instead of number
    }
  }
}
```

---

## E004: Negative Width

**Severity**: ERROR
**Message**: Trace or feature width is negative or zero

**Description**: Trace and feature widths must be positive numbers.

**How to Fix**: Set width to a positive value greater than zero.

**Example**:
```json
{
  "traces": {
    "trace1": {
      "net": "GND",
      "layer_hash": "top",
      "path": {"points": [[0, 0], [10, 10]]},
      "width": -0.5  // ❌ Negative
    }
  }
}
```

**Correct**:
```json
"width": 0.2  // ✅ Positive
```

---

## E005: Invalid Via Geometry

**Severity**: ERROR
**Message**: Via hole diameter is greater than or equal to outer diameter

**Description**: A via's hole must be smaller than its outer diameter.

**How to Fix**: Ensure `hole_diameter < outer_diameter` and both are positive.

**Example**:
```json
{
  "vias": {
    "via1": {
      "net": "GND",
      "center": {"x": 25, "y": 25},
      "outer_diameter": 0.8,
      "hole_diameter": 1.0,  // ❌ hole > outer
      "start_layer": "top",
      "end_layer": "bottom"
    }
  }
}
```

**Correct**:
```json
{
  "outer_diameter": 0.8,
  "hole_diameter": 0.4  // ✅ hole < outer
}
```

---

## E006: Nonexistent Layer

**Severity**: ERROR
**Message**: Feature references a layer hash that does not exist in the stackup

**Description**: Traces and vias must reference layers defined in the stackup.

**How to Fix**: Verify the `layer_hash` matches a layer defined in the stackup.

**Example**:
```json
{
  "stackup": {
    "layers": [
      {"name": "TOP", "type": "TOP", "index": 0, "hash": "top_layer"}
    ]
  },
  "traces": {
    "trace1": {
      "layer_hash": "nonexistent_layer"  // ❌ Not in stackup
    }
  }
}
```

---

## E007: Nonexistent Net

**Severity**: WARNING
**Message**: Feature references a net name that is not defined in the nets dictionary

**Description**: Traces, vias, and pins should reference defined nets.

**How to Fix**: Add the net to the `nets` dictionary or verify spelling.

**Example**:
```json
{
  "nets": {
    "GND": {"name": "GND"}
  },
  "traces": {
    "trace1": {
      "net": "VCC"  // ❌ Not in nets
    }
  }
}
```

**Correct**:
```json
{
  "nets": {
    "GND": {"name": "GND"},
    "VCC": {"name": "VCC"}  // ✅ Added
  }
}
```

---

## E008: Self-Intersecting Boundary

**Severity**: ERROR
**Message**: Board boundary polygon self-intersects

**Description**: The board outline must not cross itself.

**How to Fix**: Fix the boundary polygon coordinates to remove self-intersections.

**Example**:
```json
{
  "boundary": {
    "points": [
      [0, 0],
      [50, 50],  // Creates crossing
      [50, 0],
      [0, 50],
      [0, 0]
    ]
  }
}
```

---

## E009: Component Outside Boundary

**Severity**: WARNING
**Message**: Component is positioned outside the board boundary

**Description**: A component's position should be within the board outline.

**How to Fix**: Check component position coordinates or adjust the board boundary.

**Example**:
```json
{
  "boundary": {
    "points": [[0, 0], [50, 0], [50, 50], [0, 50], [0, 0]]
  },
  "components": {
    "R1": {
      "position": {"x": 100, "y": 100}  // ❌ Outside 50x50 board
    }
  }
}
```

---

## E010: Duplicate Layer Hash

**Severity**: ERROR
**Message**: Multiple layers in the stackup have the same hash identifier

**Description**: Each layer must have a unique hash for referencing.

**How to Fix**: Ensure each layer has a unique `hash` value.

**Example**:
```json
{
  "stackup": {
    "layers": [
      {"name": "TOP", "type": "TOP", "index": 0, "hash": "layer1"},
      {"name": "BOTTOM", "type": "BOTTOM", "index": 1, "hash": "layer1"}  // ❌ Duplicate
    ]
  }
}
```

---

## E011: Non-Sequential Layer Indices

**Severity**: ERROR
**Message**: Layer indices are not sequential starting from 0

**Description**: Layer indices must be sequential (0, 1, 2, ...).

**How to Fix**: Renumber layer indices to be sequential.

**Example**:
```json
{
  "stackup": {
    "layers": [
      {"name": "TOP", "type": "TOP", "index": 0, "hash": "top"},
      {"name": "BOTTOM", "type": "BOTTOM", "index": 5, "hash": "bottom"}  // ❌ Skip
    ]
  }
}
```

**Correct**:
```json
{
  "index": 1  // ✅ Sequential
}
```

---

## E012: Empty Stackup

**Severity**: ERROR
**Message**: Stackup does not contain any layers

**Description**: A board must have at least one layer.

**How to Fix**: Add at least one layer to the stackup definition.

**Example**:
```json
{
  "stackup": {
    "layers": []  // ❌ Empty
  }
}
```

---

## E013: Invalid Design Units

**Severity**: ERROR
**Message**: Design units must be one of: MICRON, MILLIMETER, MILS, INCH

**Description**: The `designUnits` field must use a supported unit.

**How to Fix**: Set `designUnits` to one of the supported values.

**Example**:
```json
{
  "designUnits": "MM"  // ❌ Invalid
}
```

**Correct**:
```json
{
  "designUnits": "MILLIMETER"  // ✅ Valid
}
```

---

## E014: Negative Diameter

**Severity**: ERROR
**Message**: Via diameter (outer or hole) is negative or zero

**Description**: Via diameters must be positive numbers.

**How to Fix**: Ensure all diameter values are positive.

**Example**:
```json
{
  "vias": {
    "via1": {
      "outer_diameter": -0.5,  // ❌ Negative
      "hole_diameter": 0.3
    }
  }
}
```

---

## Testing Errors

All error codes are tested with dedicated invalid board fixtures in `tests/invalid_boards/`.

To test specific errors:

```bash
# Test a specific invalid board
uv run pytest tests/test_validate.py::TestValidateBoard::test_self_intersecting_boundary_detected

# Test all validation
uv run pytest tests/test_validate.py
```
