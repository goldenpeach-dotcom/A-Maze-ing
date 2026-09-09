"""Reusable maze generator: grid mazes with entry/exit, optional extra loops,
and an embedded '42' pattern.
"""

from .generator import N, E, S, W, DIRECTIONS, OPPOSITE, Cell, MazeGenerator

__all__ = [
    "MazeGenerator",
    "Cell",
    "N",
    "E",
    "S",
    "W",
    "DIRECTIONS",
    "OPPOSITE",
]
