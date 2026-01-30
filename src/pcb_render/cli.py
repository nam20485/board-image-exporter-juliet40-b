"""
Command-line entrypoint for PCB Renderer CLI.
Currently a placeholder; will wire commands after core modules land.
"""

import argparse
from pathlib import Path
from typing import Iterable


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
	"""
	Configure CLI parser and return parsed arguments.
	"""
	parser = argparse.ArgumentParser(
		prog="pcb-render",
		description="Render and validate PCB ECAD JSON files.",
	)
	subparsers = parser.add_subparsers(dest="command", required=True)

	render_parser = subparsers.add_parser("render", help="Render a board to an image format.")
	render_parser.add_argument("file", type=Path, help="Path to ECAD JSON file.")
	render_parser.add_argument("-o", "--output", type=Path, help="Output file path.")
	render_parser.add_argument("--format", choices=["svg", "png", "pdf"], default="svg", help="Output format.")
	render_parser.add_argument("--dpi", type=int, default=300, help="Dots per inch when rasterizing.")
	render_parser.add_argument("--layers", nargs="*", help="Optional subset of layers to render.")

	validate_parser = subparsers.add_parser("validate", help="Validate a board without rendering.")
	validate_parser.add_argument("file", type=Path, help="Path to ECAD JSON file.")
	validate_parser.add_argument("--json", action="store_true", help="Emit validation output as JSON.")

	info_parser = subparsers.add_parser("info", help="Show board metadata summary.")
	info_parser.add_argument("file", type=Path, help="Path to ECAD JSON file.")

	return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
	"""
	Entry point wrapper. Implementation will delegate to parse/validate/render modules.
	"""
	args = parse_args(argv)
	# TODO: Wire up parse -> validate -> render once implemented.
	print(f"Command '{args.command}' not implemented yet.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
