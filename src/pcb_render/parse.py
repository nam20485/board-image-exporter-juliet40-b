"""
PCB board JSON parsing and normalization.

This module provides functions to parse ECAD JSON board definitions
and normalize all coordinates to millimeters.
"""

import logging
from typing import Any

from .models import (
    Board,
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
from .units import normalize_coordinates, normalize_value

logger = logging.getLogger(__name__)


def parse_board(json_data: dict[str, Any]) -> Board:
    """
    Parse a board definition from JSON data.

    Extracts design units, normalizes all coordinates to millimeters,
    and constructs the complete Board object with all its components.

    Args:
        json_data: Dictionary containing the board JSON definition

    Returns:
        A Board instance with all data normalized to millimeters

    Raises:
        ValueError: If required fields are missing or invalid
        ValidationError: If board validation fails
    """
    # Extract design units (default to MICRON if not specified)
    design_units = json_data.get("designUnits", "MICRON")
    if not design_units:
        logger.warning("designUnits not specified, defaulting to MICRON")
        design_units = "MICRON"

    # Validate design units
    valid_units = ["MICRON", "MILLIMETER", "MILS", "INCH"]
    if design_units not in valid_units:
        raise ValueError(
            f"Invalid designUnits '{design_units}'. Must be one of: {valid_units}"
        )

    # Extract board name
    name = json_data.get("name", "unnamed_board")

    # Parse boundary
    boundary = _parse_boundary(json_data.get("boundary", {}), design_units)

    # Parse stackup
    stackup = _parse_stackup(json_data.get("stackup", {}))

    # Parse components
    components = _parse_components(
        json_data.get("components", {}), design_units
    )

    # Parse traces
    traces = _parse_traces(json_data.get("traces", {}), design_units)

    # Parse vias
    vias = _parse_vias(json_data.get("vias", {}), design_units)

    # Parse pours (placeholder)
    pours = json_data.get("pours", {})

    # Parse keepouts
    keepouts = _parse_keepouts(json_data.get("keepouts", []), design_units)

    # Parse nets
    nets = json_data.get("nets", {})

    # Construct and return the board
    board = Board(
        name=name,
        design_units=design_units,
        boundary=boundary,
        stackup=stackup,
        components=components,
        traces=traces,
        vias=vias,
        pours=pours,
        keepouts=keepouts,
        nets=nets,
    )

    logger.info(f"Successfully parsed board '{name}' with "
                f"{len(stackup.layers)} layers, "
                f"{len(components)} components, "
                f"{len(traces)} traces, "
                f"{len(vias)} vias")

    return board


def _parse_boundary(boundary_data: dict[str, Any], design_units: str) -> Polygon:
    """
    Parse board boundary polygon.

    Args:
        boundary_data: Dictionary containing boundary coordinates
        design_units: Design units for normalization

    Returns:
        A Polygon object with normalized coordinates
    """
    if not boundary_data:
        raise ValueError("Board boundary is missing")

    points_data = boundary_data.get("points", [])
    if not points_data:
        raise ValueError("Board boundary has no points")

    # Normalize coordinates
    normalized_coords = normalize_coordinates(points_data, design_units)

    # Convert to Point objects
    points = [Point(x, y) for x, y in normalized_coords]

    return Polygon(points)


def _parse_stackup(stackup_data: dict[str, Any]) -> Stackup:
    """
    Parse layer stackup definition.

    Args:
        stackup_data: Dictionary containing stackup information

    Returns:
        A Stackup object with all layers
    """
    layers_list = stackup_data.get("layers", [])
    if not layers_list:
        raise ValueError("Stackup must contain at least one layer")

    layers = []
    for layer_data in layers_list:
        layer_type_str = layer_data.get("type", "MID")
        try:
            layer_type = LayerType[layer_type_str]
        except KeyError:
            raise ValueError(
                f"Invalid layer type '{layer_type_str}'. "
                f"Must be one of: {[lt.name for lt in LayerType]}"
            ) from None

        layer = Layer(
            name=layer_data.get("name", ""),
            layer_type=layer_type,
            index=layer_data.get("index", 0),
            hash=layer_data.get("hash", ""),
            material=layer_data.get("material"),
        )
        layers.append(layer)

    return Stackup(layers)


def _parse_components(
    components_data: dict[str, Any], design_units: str
) -> dict[str, Component]:
    """
    Parse all components.

    Args:
        components_data: Dictionary of component definitions
        design_units: Design units for normalization

    Returns:
        Dictionary of Component objects keyed by reference designator
    """
    components = {}

    for ref_des, comp_data in components_data.items():
        # Parse position
        pos_data = comp_data.get("position", {})
        normalized_pos = normalize_coordinates(
            [pos_data.get("x", 0), pos_data.get("y", 0)], design_units
        )
        position = Point(normalized_pos[0], normalized_pos[1])

        # Parse side
        side_str = comp_data.get("side", "FRONT")
        try:
            side = Side[side_str]
        except KeyError:
            raise ValueError(
                f"Invalid component side '{side_str}'. Must be FRONT or BACK"
            ) from None

        # Parse rotation
        rotation = comp_data.get("rotation", 0.0)
        if not isinstance(rotation, (int, float)):
            raise ValueError(
                f"Component '{ref_des}' has non-numeric rotation: {rotation}"
            )

        # Parse outline if present
        outline = None
        if "outline" in comp_data:
            outline_points_data = comp_data["outline"].get("points", [])
            if outline_points_data:
                normalized_outline = normalize_coordinates(outline_points_data, design_units)
                outline_points = [Point(x, y) for x, y in normalized_outline]
                outline = Polygon(outline_points)

        # Parse pins
        pins = {}
        for pin_name, pin_data in comp_data.get("pins", {}).items():
            pin_pos_data = pin_data.get("position", {"x": 0, "y": 0})
            normalized_pin_pos = normalize_coordinates(
                [pin_pos_data.get("x", 0), pin_pos_data.get("y", 0)],
                design_units
            )
            pin_position = Point(normalized_pin_pos[0], normalized_pin_pos[1])

            pin = Pin(
                name=pin_name,
                net=pin_data.get("net"),
                position=pin_position,
                rotation=(
                    pin_data.get("rotation", 0.0)
                    if isinstance(pin_data.get("rotation", 0.0), (int, float))
                    else 0.0
                ),
                is_throughhole=pin_data.get("is_throughhole", False),
            )
            pins[pin_name] = pin

        component = Component(
            ref_des=ref_des,
            footprint=comp_data.get("footprint", ""),
            position=position,
            rotation=rotation,
            side=side,
            outline=outline,
            pins=pins,
        )
        components[ref_des] = component

    return components


def _parse_traces(
    traces_data: dict[str, Any], design_units: str
) -> dict[str, Trace]:
    """
    Parse all traces.

    Args:
        traces_data: Dictionary of trace definitions
        design_units: Design units for normalization

    Returns:
        Dictionary of Trace objects keyed by UID
    """
    traces = {}

    for trace_uid, trace_data in traces_data.items():
        # Parse path (polyline)
        path_data = trace_data.get("path", {})
        path_points_data = path_data.get("points", [])
        if not path_points_data:
            raise ValueError(f"Trace {trace_uid} has no path points")

        normalized_path = normalize_coordinates(path_points_data, design_units)
        path_points = [Point(x, y) for x, y in normalized_path]
        path = Polyline(path_points)

        # Normalize width
        width = trace_data.get("width", 0.0)
        normalized_width = normalize_value(width, design_units)

        trace = Trace(
            uid=trace_uid,
            net=trace_data.get("net", ""),
            layer_hash=trace_data.get("layer_hash", ""),
            path=path,
            width=normalized_width,
        )
        traces[trace_uid] = trace

    return traces


def _parse_vias(
    vias_data: dict[str, Any], design_units: str
) -> dict[str, Via]:
    """
    Parse all vias.

    Args:
        vias_data: Dictionary of via definitions
        design_units: Design units for normalization

    Returns:
        Dictionary of Via objects keyed by UID
    """
    vias = {}

    for via_uid, via_data in vias_data.items():
        # Parse center position
        center_data = via_data.get("center", {"x": 0, "y": 0})
        normalized_center = normalize_coordinates(
            [center_data.get("x", 0), center_data.get("y", 0)],
            design_units
        )
        center = Point(normalized_center[0], normalized_center[1])

        # Normalize diameters
        outer_diameter = normalize_value(via_data.get("outer_diameter", 0.0), design_units)
        hole_diameter = normalize_value(via_data.get("hole_diameter", 0.0), design_units)

        via = Via(
            uid=via_uid,
            net=via_data.get("net", ""),
            center=center,
            outer_diameter=outer_diameter,
            hole_diameter=hole_diameter,
            start_layer=via_data.get("start_layer", ""),
            end_layer=via_data.get("end_layer", ""),
        )
        vias[via_uid] = via

    return vias


def _parse_keepouts(
    keepouts_data: list[dict[str, Any]], design_units: str
) -> list[Polygon]:
    """
    Parse all keepout regions.

    Args:
        keepouts_data: List of keepout definitions
        design_units: Design units for normalization

    Returns:
        List of Polygon objects representing keepout regions
    """
    keepouts = []

    for keepout_data in keepouts_data:
        points_data = keepout_data.get("points", [])
        if not points_data:
            continue

        normalized = normalize_coordinates(points_data, design_units)
        points = [Point(x, y) for x, y in normalized]
        keepout = Polygon(points)
        keepouts.append(keepout)

    return keepouts
