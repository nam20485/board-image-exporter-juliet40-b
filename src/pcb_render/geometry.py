"""
Geometry utilities for transforms and measurements.
"""

from typing import Iterable, Tuple


def rotate(point: Tuple[float, float], degrees: float) -> Tuple[float, float]:
	"""
	Placeholder rotation utility; returns input until implemented.
	"""
	return point


def translate(point: Tuple[float, float], offset: Tuple[float, float]) -> Tuple[float, float]:
	"""
	Placeholder translation utility; returns translated point.
	"""
	return point[0] + offset[0], point[1] + offset[1]


def mirror(point: Tuple[float, float]) -> Tuple[float, float]:
	"""
	Placeholder mirror utility; returns mirrored point over X-axis.
	"""
	return point[0], -point[1]
