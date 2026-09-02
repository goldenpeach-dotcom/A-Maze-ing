# from .config import width, height


def make_42_walls(maze: MazeGenerator, width: int, height: int) -> None:

    pattern_width: int = 7
    pattern_height: int = 5

    if width + 2 < pattern_width or height + 2 < pattern_height:
        raise ValueError("width or height is too small to add 42!") 

    start_x: int = (width - pattern_width) // 2
    start_y: int = (height - pattern_height) // 2

    wall_42: list[tuple[int, int]] = [
        (start_x - 3, start_y - 2),
        (start_x - 3, start_y - 1),
        (start_x - 3, start_y),
        (start_x - 2, start_y),
        (start_x - 1, start_y),
        (start_x + 1, start_y),
        (start_x + 2, start_y),
        (start_x + 3, start_y),
        (start_x - 1, start_y + 1),
        (start_x - 1, start_y + 2),
        (start_x + 1, start_y + 1),
        (start_x + 1, start_y + 2),
        (start_x + 2, start_y + 2),
        (start_x + 3, start_y + 2),
        (start_x + 1, start_y - 2),
        (start_x + 2, start_y - 2),
        (start_x + 3, start_y - 2),
    ]

    for x, y in wall_42:
        maze[y][x].walls = 15
        maze[y][x].is_42 = True
