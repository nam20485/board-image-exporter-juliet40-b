"""Generate all 14 invalid board fixtures for testing error detection."""

import json
from pathlib import Path

# Base valid board template
VALID_BOARD = {
    "name": "test_board",
    "designUnits": "MILLIMETER",
    "boundary": {
        "points": [
            [0.0, 0.0],
            [50.0, 0.0],
            [50.0, 50.0],
            [0.0, 50.0],
            [0.0, 0.0],
        ]
    },
    "stackup": {
        "layers": [
            {
                "name": "TOP",
                "type": "TOP",
                "index": 0,
                "hash": "top_layer_hash",
            }
        ]
    },
    "components": {
        "R1": {
            "footprint": "RES_0805",
            "position": {"x": 10.0, "y": 10.0},
            "rotation": 0.0,
            "side": "FRONT",
            "pins": {
                "1": {
                    "net": "GND",
                    "position": {"x": -1.0, "y": 0.0},
                    "rotation": 0.0,
                    "is_throughhole": False,
                }
            },
        }
    },
    "traces": {
        "trace1": {
            "net": "GND",
            "layer_hash": "top_layer_hash",
            "path": {"points": [[10.0, 10.0], [20.0, 10.0], [20.0, 20.0]]},
            "width": 0.2,
        }
    },
    "vias": {},
    "pours": {},
    "keepouts": [],
    "nets": {"GND": {"name": "GND"}},
}


def create_invalid_boards():
    """Create all 14 invalid board JSON files."""
    output_dir = Path(__file__).parent.parent / "invalid_boards"
    output_dir.mkdir(exist_ok=True)

    # E001: Missing boundary
    board_e001 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e001["boundary"] = {}
    save_invalid_board(board_e001, output_dir / "missing_boundary.json")

    # E002: Malformed coordinates (infinity values that pass parsing but fail validation)
    board_e002 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e002["boundary"]["points"] = [
        [0.0, 1e308],
        [50.0, 0.0],
        [50.0, 50.0],
        [0.0, 50.0],
        [0.0, 0.0],
    ]
    save_invalid_board(board_e002, output_dir / "malformed_coordinates.json")

    # E003: Invalid rotation (extreme value that's technically valid but unreasonable)
    board_e003 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e003["components"]["R1"]["rotation"] = 1e308  # Near infinity
    save_invalid_board(board_e003, output_dir / "invalid_rotation.json")

    # E004: Negative width
    board_e004 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e004["traces"]["trace1"]["width"] = -0.5
    save_invalid_board(board_e004, output_dir / "negative_width.json")

    # E005: Invalid via geometry (hole >= outer)
    board_e005 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e005["vias"]["via1"] = {
        "net": "GND",
        "center": {"x": 25.0, "y": 25.0},
        "outer_diameter": 0.8,
        "hole_diameter": 1.0,  # hole > outer
        "start_layer": "top_layer_hash",
        "end_layer": "top_layer_hash",
    }
    save_invalid_board(board_e005, output_dir / "invalid_via_geometry.json")

    # E006: Nonexistent layer
    board_e006 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e006["traces"]["trace1"]["layer_hash"] = "nonexistent_layer"
    save_invalid_board(board_e006, output_dir / "nonexistent_layer.json")

    # E007: Nonexistent net
    board_e007 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e007["traces"]["trace1"]["net"] = "NONEXISTENT_NET"
    save_invalid_board(board_e007, output_dir / "nonexistent_net.json")

    # E008: Self-intersecting boundary
    board_e008 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e008["boundary"]["points"] = [
        [0.0, 0.0],
        [50.0, 50.0],
        [50.0, 0.0],
        [0.0, 50.0],
        [0.0, 0.0],
    ]
    save_invalid_board(board_e008, output_dir / "self_intersecting_boundary.json")

    # E009: Component outside boundary
    board_e009 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e009["components"]["R1"]["position"] = {"x": 100.0, "y": 100.0}  # Outside 50x50 board
    board_e009["components"]["R1"]["outline"] = {
        "points": [[95.0, 95.0], [105.0, 95.0], [105.0, 105.0], [95.0, 105.0], [95.0, 95.0]]
    }
    save_invalid_board(board_e009, output_dir / "component_outside_boundary.json")

    # E010: Duplicate layer hash
    board_e010 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e010["stackup"]["layers"].append(
        {
            "name": "BOTTOM",
            "type": "BOTTOM",
            "index": 1,
            "hash": "top_layer_hash",  # Duplicate hash
        }
    )
    save_invalid_board(board_e010, output_dir / "duplicate_layer_hash.json")

    # E011: Non-sequential layer indices
    board_e011 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e011["stackup"]["layers"].append(
        {
            "name": "BOTTOM",
            "type": "BOTTOM",
            "index": 5,  # Not sequential
            "hash": "bottom_layer_hash",
        }
    )
    save_invalid_board(board_e011, output_dir / "non_sequential_layer_indices.json")

    # E012: Empty stackup
    board_e012 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e012["stackup"]["layers"] = []
    save_invalid_board(board_e012, output_dir / "empty_stackup.json")

    # E013: Invalid design units
    board_e013 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e013["designUnits"] = "INVALID_UNIT"
    save_invalid_board(board_e013, output_dir / "invalid_design_units.json")

    # E014: Negative diameter
    board_e014 = json.loads(json.dumps(VALID_BOARD))  # Deep copy
    board_e014["vias"]["via1"] = {
        "net": "GND",
        "center": {"x": 25.0, "y": 25.0},
        "outer_diameter": -0.5,  # Negative
        "hole_diameter": 0.3,
        "start_layer": "top_layer_hash",
        "end_layer": "top_layer_hash",
    }
    save_invalid_board(board_e014, output_dir / "negative_diameter.json")

    print(f"Created 14 invalid board fixtures in {output_dir}")


def save_invalid_board(board: dict, filepath: Path):
    """Save an invalid board to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(board, f, indent=2)


if __name__ == "__main__":
    create_invalid_boards()
