"""
Validation pipeline for PCB data.
"""

from typing import List

from .models import BoardModel


def validate_board(board: BoardModel) -> List[str]:
	"""
	Run validation rules against the board model.
	Returns a list of error messages (placeholder).
	"""
	return []
