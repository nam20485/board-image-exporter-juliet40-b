"""
cli.py
------

This script defines a command‑line interface (CLI) for validating and
repairing PCB design files. It leverages deterministic validation
implemented in `validator.py` and optional natural language assistance
from a local LLM as defined in `llm_assistant.py`. The CLI is designed
for terminal usage and does not require any graphical user interface.

Key commands:

* `validate`: Validate a board file. Optionally request explanations or
  fix suggestions from the LLM. Fix suggestions are emitted as RFC6902
  JSON patch operations.
* `apply-fix`: Apply a JSON patch to a board file and save the result.

Example usage:

```bash
python cli.py validate board.json --explain --fix-suggest --patch-out patch.json
python cli.py apply-fix board.json --patch patch.json -o board.fixed.json
python cli.py validate board.fixed.json
```

In a real application, this script would be integrated into an
installed console script entry point (e.g., via setuptools). Here it
serves as a self‑contained demonstration.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import llm_assistant, validator


def print_error(err: validator.ValidationError) -> None:
    """Pretty print a validation error to stdout."""
    print(f"[error] {err['code']} at {err['json_path']}: {err['message']}")


def print_explanation(expl: dict[str, Any]) -> None:
    """Pretty print a LLM explanation for a validation error."""
    print(f"\nExplanation for {expl['code']}:")
    print(f"  Summary: {expl['summary']}")
    print(f"  Likely cause: {expl['likely_cause']}")
    if expl["fix_steps"]:
        print("  Suggested fix steps:")
        for step in expl["fix_steps"]:
            print(f"    - {step}")
    if expl["proposed_patch"]:
        print("  Proposed patch:")
        for op in expl["proposed_patch"]:
            print(f"    - {op}")
    print(f"  Confidence: {expl['confidence']:.2f}")
    print(f"  Needs human review: {expl['needs_human_review']}")


def command_validate(args: argparse.Namespace) -> int:
    """Handle the `validate` command."""
    board_path = Path(args.board)
    try:
        board = validator.load_board(str(board_path))
    except FileNotFoundError:
        print(f"Error: board file '{board_path}' not found.", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: failed to parse JSON: {e}", file=sys.stderr)
        return 1

    errors = validator.validate_board(board)
    if errors:
        print(f"Found {len(errors)} validation error(s).\n")
        for err in errors:
            print_error(err)
    else:
        print("No validation errors found. ✅")

    # Explanations
    if args.explain and errors:
        print("\nGenerating explanations using local LLM...")
        # Choose engine based on model flag
        if args.model == "noop":
            engine: llm_assistant.LlmEngine = llm_assistant.NoopEngine()
        else:
            engine = llm_assistant.OnnxRuntimeEngine(args.model if args.model != "onnx" else None)
        explanations = llm_assistant.explain_errors(errors, board_info=None, engine=engine)
        for expl in explanations:
            print_explanation(expl)

    # Fix suggestions
    patch_ops: list[dict[str, Any]] | None = None
    if args.fix_suggest and errors:
        patch_ops = llm_assistant.suggest_patch(errors, board)
        if patch_ops:
            print("\nSuggested JSON patch operations:")
            for op in patch_ops:
                print(f"  - op: {op['op']}, path: {op['path']}, value: {op['value']}")
        else:
            print("\nNo fix suggestions available.")

        # Optionally write patch to file
        if args.patch_out:
            patch_path = Path(args.patch_out)
            try:
                with open(patch_path, "w", encoding="utf-8") as f:
                    json.dump(patch_ops or [], f, indent=2)
                print(f"\nPatch written to {patch_path}")
            except Exception as e:
                print(f"Error: could not write patch file: {e}", file=sys.stderr)
                return 1

    return 0


def apply_patch(board: dict[str, Any], patch_ops: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply a list of JSON patch operations to a board dictionary.

    This implementation supports only the 'replace' operation and does not
    implement the full JSON Patch specification. Additional operations
    could be added as needed.

    Args:
        board: The original board data.
        patch_ops: A list of patch operations.

    Returns:
        A new dictionary with the operations applied.
    """
    import copy

    result = copy.deepcopy(board)
    for op in patch_ops:
        if op.get("op") != "replace":
            raise ValueError(f"Unsupported operation: {op.get('op')}")
        path = op.get("path")
        value = op.get("value")
        if path is None:
            continue
        # Split the path into parts, skipping the leading slash
        parts = path.lstrip("/").split("/")
        target = result
        for p in parts[:-1]:
            target = target.setdefault(p, {})
        target[parts[-1]] = value
    return result


def command_apply_fix(args: argparse.Namespace) -> int:
    """Handle the `apply-fix` command."""
    board_path = Path(args.board)
    patch_path = Path(args.patch)
    out_path = Path(args.output or args.board)

    # Load board
    try:
        board = validator.load_board(str(board_path))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: failed to load board: {e}", file=sys.stderr)
        return 1

    # Load patch
    try:
        with open(patch_path, encoding="utf-8") as f:
            patch_ops = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: failed to load patch: {e}", file=sys.stderr)
        return 1

    try:
        new_board = apply_patch(board, patch_ops)
    except Exception as e:
        print(f"Error: failed to apply patch: {e}", file=sys.stderr)
        return 1

    # Save result
    try:
        validator.save_board(new_board, str(out_path))
        print(f"Patched board written to {out_path}")
    except Exception as e:
        print(f"Error: failed to write patched board: {e}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="PCB board validation and repair CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a board file")
    validate_parser.add_argument("board", help="Path to the board JSON file")
    validate_parser.add_argument(
        "--explain",
        action="store_true",
        help="Generate natural language explanations via local LLM",
    )
    validate_parser.add_argument(
        "--fix-suggest",
        action="store_true",
        help="Suggest JSON patch operations to fix some errors",
    )
    validate_parser.add_argument(
        "--patch-out",
        metavar="PATCH_FILE",
        help="Write suggested patch operations to this file (used with --fix-suggest)",
    )
    validate_parser.add_argument(
        "--model",
        default="onnx",
        choices=["onnx", "noop"],
        help="Model type for LLM explanations (onnx uses OnnxRuntimeEngine, noop disables LLM)",
    )
    validate_parser.set_defaults(func=command_validate)

    # apply-fix command
    apply_parser = subparsers.add_parser("apply-fix", help="Apply a JSON patch to a board file")
    apply_parser.add_argument("board", help="Path to the input board JSON file")
    apply_parser.add_argument("--patch", required=True, help="Path to JSON patch file")
    apply_parser.add_argument(
        "-o",
        "--output",
        metavar="OUT",
        help="Path to write the patched board (defaults to overwrite)",
    )
    apply_parser.set_defaults(func=command_apply_fix)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
