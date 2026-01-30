"""
Parsing helpers for ECAD JSON inputs.
"""

from pathlib import Path
from typing import Tuple

from .models import BoardModel


def load_board(path: Path) -> Tuple[BoardModel, list[str]]:
	"""
	Parse the input JSON and return a BoardModel plus any parse warnings/errors.
	Implementation TBD; placeholder ensures call sites compile.
	"""
	return BoardModel(raw={"path": str(path)}), []
