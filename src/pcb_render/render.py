"""
Rendering pipeline stubs.
"""

from pathlib import Path
from typing import Iterable

from .models import BoardModel


def render_board(board: BoardModel, output: Path, fmt: str = "svg", dpi: int = 300, layers: Iterable[str] | None = None) -> None:
	"""
	Render the board to the desired format.
	Implementation placeholder; will use matplotlib in future work.
	"""
	output.write_text(f"Rendering placeholder for {board.raw} to {output} ({fmt}@{dpi}) with layers={layers}")
