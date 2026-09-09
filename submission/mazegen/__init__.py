"""再利用可能な迷路生成ツール：入り口と出口があるグリッド状の迷路を生成し、
オプションでループを追加したり、「42」のパターンを埋め込んだりすることが可能です。
Reusable maze generator: grid mazes with entry/exit, optional extra loops,
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
