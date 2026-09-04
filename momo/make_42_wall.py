import logging

logger = logging.getLogger(__name__)


Cell = tuple[int, int]


def get_protected_points(
    width: int, height: int,
    entry: Cell, exit_point: Cell
) -> list[Cell]:
    """ Get the coordinates to protect

        parameter: width of maze, height of maze,
        entry point, exit point
        return list[tuple[int, int]]
    """

    corners: list[Cell] = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]

    # x_mid: int = [width // 2] if width % 2 else [width // 2 - 1, width // 2]
    # y_mid: int = [height // 2]
    # if height % 2 else [height // 2 - 1, height // 2]
    x_mid: list[int] = (
        [width // 2] if width % 2 else [width // 2 - 1, width // 2]
    )
    y_mid: list[int] = (
        [height // 2] if height % 2 else [height // 2 - 1, height // 2]
    )
    center: list[Cell] = [(x, y) for x in x_mid for y in y_mid]
    return corners + center + [entry, exit_point]


def fits_in_maze(start_x: int, start_y: int, width: int, height: int) -> bool:
    """ Check if it's within the outer frame of the maze

        parameter: center point(x, y),
        width & height of the maze
    """

    return (start_x - 3 >= 0 and start_x + 3 < width
            and start_y - 2 >= 0 and start_y + 2 < height)


def in_bounding_box(point: Cell, start_x: int, start_y: int) -> bool:
    """ Check for duplicates with the space that contains "42"

        parameter: coordinates to compare, coordinates of center
    """

    px, py = point
    if px == start_x:
        return False
    return (
        start_x - 3 <= px <= start_x + 3
        and start_y - 2 <= py <= start_y + 2
    )


def generate_offsets(max_shift: int) -> list[int]:
    """ Create a list of coordinates to check

        parameter: maximum distance to compare
    """

    offsets: list[int] = [0]
    for d in range(1, max_shift):
        offsets += [d, -d]
    return offsets


def find_valid_position(
    base_x: int, base_y: int, width: int, height: int, protected: list[Cell]
) -> tuple[int, int]:

    """ Find a place where 42 characters can fit

        move the center up and down to search
        parameter: coodinates of center of the maze,
        width & height of the maze
        coordinates to be protected
        return: valid_position[tuple[int, int]]
    """
    max_shift: int = height

    offsets = generate_offsets(max_shift)

    for dy in offsets:
        candidate_y = base_y + dy
        if not fits_in_maze(base_x, candidate_y, width, height):
            continue
        if not any(in_bounding_box(p, base_x, candidate_y) for p in protected):
            return base_x, candidate_y

    raise ValueError("no valid vertical position for 42 pattern")


def find_valid_position_2d(
    base_x: int, base_y: int, width: int, height: int, protected: list[Cell]
) -> tuple[int, int]:

    """ Find a place where 42 characters can fit

        parameter: coodinates of center of the maze,
        width & height of the maze
        coordinates to be protected
        return: valid_position[tuple[int, int]]
        Move in rings from the center outward to search
    """
    max_shift = max(width, height)

    for d in range(max_shift):
        for dx in range(-d, d + 1):
            for dy in range(-d, d + 1):
                if max(abs(dx), abs(dy)) != d:
                    continue  # d=0のリングを除き、外周だけを見る(内側は前のdで探索済み)
                cx, cy = base_x + dx, base_y + dy
                if not fits_in_maze(cx, cy, width, height):
                    continue
                if not any(in_bounding_box(p, cx, cy) for p in protected):
                    return cx, cy

    raise ValueError("no valid position for 42 pattern")


def build_pattern(start_x: int, start_y: int) -> list[Cell]:
    """ Return 42 pattern coordinates

        parameter: coordinates of center of the maze
        return: A list of coordinates showing 42 patterns
    """

    return [
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
        (start_x + 3, start_y - 1),
    ]


def make_42_walls(
    width: int, height: int,
    entry: Cell, goal: Cell
) -> list[Cell]:

    """ Make 42 walls

    parameter: width & height of the maze,
    coordinates of entry_point & exit_point

    Finds the median according to the size of the outer frame
    Gets the coordinates of the four corners, the center,
    the entrance, and the exit.
    Looks for a spot that doesn’t overlap with the coordinates
    to protect and fits within the outer frame.
    Returns the coordinates of a place where you can place 42
    Return an empty list if you can't find it
    """
    pattern_width: int = 7
    pattern_height: int = 5

    if width <= (pattern_width + 3) or height <= (pattern_height + 3):
        logger.warning("width or height is too small to add 42!")
        return []

    start_x: int = width // 2
    start_y: int = height // 2
    if width % 2 == 0:
        start_x -= 1
    if height % 2 == 0:
        start_y -= 1

    protected = get_protected_points(width, height, entry, goal)

    try:
        valid_x, valid_y = find_valid_position(
            start_x, start_y, width, height, protected
        )
    except ValueError:
        try:
            valid_x, valid_y = find_valid_position_2d(
                start_x, start_y, width, height, protected
            )
        except ValueError:
            logger.warning(
                "no valid position found for 42 pattern(both 1D and 2D search "
                "failed); returning empty wall list"
            )
            return []
    wall_42: list[Cell] = build_pattern(valid_x, valid_y)

    return wall_42


def print_42_shape(width: int, height: int, entry: Cell, goal: Cell) -> None:
    """ test print the 42 in the box

    parameter: width & height of the maze, coordinates of entry_point,
    coordinates of exit_point
    """

    wall_cells: list[Cell] = make_42_walls(width, height, entry, goal)
    if not wall_cells:
        return
    wall_set = set(wall_cells)
    for y in range(height):
        row = "".join("#" if (x, y) in wall_set else "." for x in range(width))
        print(row)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    try:
        print_42_shape(13, 16, (8, 2), (4, 5))
    except ValueError:
        print("error")
