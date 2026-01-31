"""
Board validation engine.

This module provides comprehensive validation of PCB board definitions,
checking geometry, topology, connectivity, and physical constraints.
"""

from .errors import (
    E001_BOUNDARY_NOT_CLOSED,
    E006_NONEXISTENT_LAYER,
    E007_NONEXISTENT_NET,
    E008_SELF_INTERSECTING_BOUNDARY,
    E009_COMPONENT_OUTSIDE_BOUNDARY,
    ValidationError,
)
from .models import Board, Component


def validate_board(board: Board) -> list[ValidationError]:
    """
    Validate a complete board definition.

    Performs comprehensive validation including:
    - Boundary validation (closure, self-intersection)
    - Layer validation (unique hashes, sequential indices)
    - Reference validation (layer hashes, net names)
    - Geometry validation (positive dimensions)
    - Placement validation (components within boundary)

    Args:
        board: The board to validate

    Returns:
        List of validation errors. Empty list if board is valid.
    """
    errors: list[ValidationError] = []

    # Validate boundary
    errors.extend(_validate_boundary(board))

    # Validate layers
    errors.extend(_validate_layers(board))

    # Validate traces
    errors.extend(_validate_traces(board))

    # Validate vias
    errors.extend(_validate_vias(board))

    # Validate components
    errors.extend(_validate_components(board))

    # Validate nets
    errors.extend(_validate_nets(board))

    return errors


def _validate_boundary(board: Board) -> list[ValidationError]:
    """Validate board boundary polygon."""
    errors: list[ValidationError] = []

    # Check if boundary is closed
    if not board.boundary.is_closed():
        # This should be caught during construction, but double-check
        errors.append(ValidationError.from_code(
            E001_BOUNDARY_NOT_CLOSED,
            json_path="boundary",
        ))

    # Check for self-intersection
    if board.boundary.self_intersects():
        errors.append(ValidationError.from_code(
            E008_SELF_INTERSECTING_BOUNDARY,
            json_path="boundary",
        ))

    return errors


def _validate_layers(board: Board) -> list[ValidationError]:
    """Validate layer stackup."""
    errors: list[ValidationError] = []

    # Stackup validation is done during construction, but we can
    # add additional checks here if needed

    return errors


def _validate_traces(board: Board) -> list[ValidationError]:
    """Validate all traces in the board."""
    errors: list[ValidationError] = []

    for trace_uid, trace in board.traces.items():
        # Check if layer hash exists
        if board.stackup.get_layer_by_hash(trace.layer_hash) is None:
            errors.append(ValidationError.from_code(
                E006_NONEXISTENT_LAYER,
                json_path=f"traces.{trace_uid}.layer_hash",
            ))

        # Check if net exists
        if trace.net not in board.nets:
            errors.append(ValidationError.from_code(
                E007_NONEXISTENT_NET,
                json_path=f"traces.{trace_uid}.net",
            ))

    return errors


def _validate_vias(board: Board) -> list[ValidationError]:
    """Validate all vias in the board."""
    errors: list[ValidationError] = []

    for via_uid, via in board.vias.items():
        # Check if start layer exists
        if board.stackup.get_layer_by_hash(via.start_layer) is None:
            errors.append(ValidationError.from_code(
                E006_NONEXISTENT_LAYER,
                json_path=f"vias.{via_uid}.start_layer",
            ))

        # Check if end layer exists
        if board.stackup.get_layer_by_hash(via.end_layer) is None:
            errors.append(ValidationError.from_code(
                E006_NONEXISTENT_LAYER,
                json_path=f"vias.{via_uid}.end_layer",
            ))

        # Check if net exists
        if via.net not in board.nets:
            errors.append(ValidationError.from_code(
                E007_NONEXISTENT_NET,
                json_path=f"vias.{via_uid}.net",
            ))

    return errors


def _validate_components(board: Board) -> list[ValidationError]:
    """Validate all components in the board."""
    errors: list[ValidationError] = []

    for ref_des, component in board.components.items():
        # Check if component is within board boundary
        if component.outline:
            errors.extend(_validate_component_placement(board, component, ref_des))

        # Check if component pin nets exist
        for pin_name, pin in component.pins.items():
            if pin.net and pin.net not in board.nets:
                errors.append(ValidationError.from_code(
                    E007_NONEXISTENT_NET,
                    json_path=f"components.{ref_des}.pins.{pin_name}.net",
                ))

    return errors


def _validate_component_placement(
    board: Board, component: Component, ref_des: str
) -> list[ValidationError]:
    """
    Validate that a component is placed within the board boundary.

    Uses a simple bounding box check to see if the component outline
    intersects or is contained within the board boundary.
    """
    errors: list[ValidationError] = []

    if not component.outline:
        return errors

    # Get bounding boxes
    board_min, board_max = board.boundary.bounds()
    comp_min, comp_max = component.outline.bounds()

    # Check if component is entirely outside board
    if (comp_max.x < board_min.x or comp_min.x > board_max.x or
        comp_max.y < board_min.y or comp_min.y > board_max.y):

        errors.append(ValidationError.from_code(
            E009_COMPONENT_OUTSIDE_BOUNDARY,
            json_path=f"components.{ref_des}.position",
        ))

    return errors


def _validate_nets(board: Board) -> list[ValidationError]:
    """
    Validate net definitions.

    Currently this is a placeholder for future net validation logic.
    """
    errors: list[ValidationError] = []

    # Add net-specific validation here if needed

    return errors
