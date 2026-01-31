"""Pytest configuration and fixtures."""

import json
from pathlib import Path
from typing import Any

import pytest

from pcb_render.models import (
    Board,
    Component,
    Layer,
    LayerType,
    Point,
    Polygon,
    Polyline,
    Side,
    Stackup,
)


@pytest.fixture
def sample_point() -> Point:
    """Create a sample Point at (1.0, 2.0)."""
    return Point(1.0, 2.0)


@pytest.fixture
def sample_points() -> list[Point]:
    """Create a list of sample points forming a rectangle."""
    return [
        Point(0.0, 0.0),
        Point(10.0, 0.0),
        Point(10.0, 10.0),
        Point(0.0, 10.0),
        Point(0.0, 0.0),  # Closed
    ]


@pytest.fixture
def sample_polygon(sample_points: list[Point]) -> Polygon:
    """Create a sample rectangular polygon."""
    return Polygon(sample_points)


@pytest.fixture
def sample_polyline() -> Polyline:
    """Create a sample polyline."""
    points = [
        Point(0.0, 0.0),
        Point(5.0, 5.0),
        Point(10.0, 0.0),
    ]
    return Polyline(points)


@pytest.fixture
def sample_layer() -> Layer:
    """Create a sample TOP layer."""
    return Layer(
        name="TOP",
        layer_type=LayerType.TOP,
        index=0,
        hash="top_layer_hash",
    )


@pytest.fixture
def sample_stackup(sample_layer: Layer) -> Stackup:
    """Create a sample stackup with one layer."""
    return Stackup([sample_layer])


@pytest.fixture
def sample_component() -> Component:
    """Create a sample component."""
    return Component(
        ref_des="R1",
        footprint="RES_0805",
        position=Point(5.0, 5.0),
        rotation=0.0,
        side=Side.FRONT,
    )


@pytest.fixture
def sample_board(sample_polygon: Polygon, sample_stackup: Stackup) -> Board:
    """Create a sample minimal board."""
    return Board(
        name="test_board",
        design_units="MILLIMETER",
        boundary=sample_polygon,
        stackup=sample_stackup,
    )


@pytest.fixture
def load_json_file():
    """Factory fixture to load JSON files from the fixtures directory."""
    def _load_file(filename: str) -> dict[str, Any]:
        fixtures_dir = Path(__file__).parent / "fixtures"
        with open(fixtures_dir / filename) as f:
            return json.load(f)

    return _load_file


@pytest.fixture
def load_invalid_board():
    """Factory fixture to load invalid board JSON files."""
    def _load_file(filename: str) -> dict[str, Any]:
        invalid_dir = Path(__file__).parent / "invalid_boards"
        with open(invalid_dir / filename) as f:
            return json.load(f)

    return _load_file
