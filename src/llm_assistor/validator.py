"""
validator.py
---------------

This module implements a simple board validation routine for a hypothetical
printed circuit board (PCB) rendering application. The goal of this module
is to demonstrate how deterministic validation logic can feed a local
large‑language model (LLM) assistant. The LLM assistant can then produce
natural language explanations and propose candidate fixes for validation
errors.

The validation rules implemented here are intentionally simplistic and
serve only as examples. They cover a few basic domain constraints such as
ensuring trace widths are positive and via hole sizes are smaller than
their outer diameters. Real boards will require far more comprehensive
rules.

Each error is returned as a dictionary with the following keys:

```
{
    "code": str,        # machine‑readable error code
    "message": str,     # human‑readable description of the error
    "json_path": str,   # JSON pointer path to the offending element
    "severity": str     # one of "error" or "warning"
}
```
"""

import json
from typing import Any, TypedDict, TypeGuard, cast


class ValidationError(TypedDict):
    """Structured validation error information."""

    code: str
    message: str
    json_path: str
    severity: str


def _coerce_mapping(value: object) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for key, item in value.items():
        if isinstance(key, str) and isinstance(item, dict):
            result[key] = cast(dict[str, Any], item)
    return result


def _is_coord_pair(value: object) -> TypeGuard[tuple[float, float] | list[float]]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return False
    return all(isinstance(item, (int, float)) for item in value)


def validate_board(board: dict[str, Any]) -> list[ValidationError]:
    """Validate a board dictionary and return a list of validation errors.

    Args:
        board: Parsed board object loaded from a JSON file.

    Returns:
        A list of ValidationError dictionaries.
    """
    errors: list[ValidationError] = []

    # Validate top‑level keys
    units = board.get("units")
    if units not in {"mm", "mil"}:
        errors.append(
            ValidationError(
                code="units.invalid",
                message=f"Units must be 'mm' or 'mil', got '{units}'.",
                json_path="/units",
                severity="error",
            )
        )

    # Validate traces
    raw_traces = board.get("traces", {})
    traces: dict[str, dict[str, Any]] = {}
    if isinstance(raw_traces, dict):
        for trace_name, trace in raw_traces.items():
            if isinstance(trace_name, str) and isinstance(trace, dict):
                traces[trace_name] = trace
    for trace_name, trace in traces.items():
        width = trace.get("width")
        if width is None:
            errors.append(
                {
                    "code": "trace.width.missing",
                    "message": f"Trace '{trace_name}' is missing a width field.",
                    "json_path": f"/traces/{trace_name}/width",
                    "severity": "error",
                }
            )
        elif not isinstance(width, (int, float)):
            errors.append(
                {
                    "code": "trace.width.type",
                    "message": (
                        f"Trace '{trace_name}' width must be numeric, got {type(width)}."
                    ),
                    "json_path": f"/traces/{trace_name}/width",
                    "severity": "error",
                }
            )
        elif width <= 0:
            errors.append(
                {
                    "code": "trace.width.negative",
                    "message": f"Trace '{trace_name}' has non‑positive width {width}.",
                    "json_path": f"/traces/{trace_name}/width",
                    "severity": "error",
                }
            )

        # Validate start and end coordinates
        for coord_name in ["start", "end"]:
            coord = trace.get(coord_name)
            if not isinstance(coord, (list, tuple)) or len(coord) != 2:
                errors.append(
                    {
                        "code": f"trace.{coord_name}.invalid",
                        "message": (
                            f"Trace '{trace_name}' {coord_name} must be a two‑element list."
                        ),
                        "json_path": f"/traces/{trace_name}/{coord_name}",
                        "severity": "error",
                    }
                )

    # Validate vias
    raw_vias = board.get("vias", {})
    vias: dict[str, dict[str, Any]] = {}
    if isinstance(raw_vias, dict):
        for via_name, via in raw_vias.items():
            if isinstance(via_name, str) and isinstance(via, dict):
                vias[via_name] = via
    for via_name, via in vias.items():
        diameter = via.get("diameter")
        hole = via.get("hole")
        if diameter is None or hole is None:
            errors.append(
                {
                    "code": "via.dimensions.missing",
                    "message": (
                        f"Via '{via_name}' must have both 'diameter' and 'hole' fields."
                    ),
                    "json_path": f"/vias/{via_name}",
                    "severity": "error",
                }
            )
            continue
        if not isinstance(diameter, (int, float)) or not isinstance(hole, (int, float)):
            errors.append(
                {
                    "code": "via.dimensions.type",
                    "message": f"Via '{via_name}' dimensions must be numeric.",
                    "json_path": f"/vias/{via_name}",
                    "severity": "error",
                }
            )
            continue
        if diameter <= 0 or hole <= 0:
            errors.append(
                {
                    "code": "via.dimensions.negative",
                    "message": (
                        f"Via '{via_name}' has non‑positive diameter ({diameter}) or hole ({hole})."
                    ),
                    "json_path": f"/vias/{via_name}",
                    "severity": "error",
                }
            )
            continue
        if hole >= diameter:
            errors.append(
                {
                    "code": "via.hole.exceeds_diameter",
                    "message": (
                        f"Via '{via_name}' hole {hole} is greater than or equal to "
                        f"diameter {diameter}."
                    ),
                    "json_path": f"/vias/{via_name}",
                    "severity": "error",
                }
            )

    return errors


def load_board(path: str) -> dict[str, Any]:
    """Load a board JSON file from disk.

    Args:
        path: File path to the board JSON file.

    Returns:
        The parsed JSON as a Python dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_board(board: dict[str, Any], path: str) -> None:
    """Save a board dictionary to disk as JSON.

    Args:
        board: The board data to save.
        path: Destination file path.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(board, f, indent=2)
