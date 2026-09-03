# from .config import width, height

Cell = tuple[int, int]


def overlaps_start_or_exit(
    wall_cells: list[Cell],
    entry: Cell, exit_point: Cell
) -> bool:
    wall_set = set(wall_cells)
    return entry in wall_set or exit_point in wall_set


def get_protected_points(
    width: int,
    height: int,
    entry: Cell,
    exit_point: Cell
) -> list[Cell]:
    corners: list[Cell] = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]
    center: Cell = (width // 2, height // 2)
    return corners + [center, entry, exit_point]


def is_within_outer_wall(cells: list[Cell], width: int, height: int) -> bool:
    return all(0 <= nx < width and 0 <= ny < height for nx, ny in cells)


def in_bounding_box(point: Cell, start_x: int, start_y: int) -> bool:
    px, py = point
    return (
        start_x - 3 <= px <= start_x + 3
        and start_y - 2 <= py <= start_y + 2
    )


def fits_in_maze(start_x: int, start_y: int, width: int, height: int) -> bool:
    return (start_x - 3 >= 0 and start_x + 3 < width
            and start_y - 2 >= 0 and start_y + 2 < height)


def build_pattern(start_x: int, start_y: int) -> list[Cell]:
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


def find_valid_position(
    base_x: int, base_y: int, width: int, height: int,
    protected: list[Cell]
) -> tuple[int, int]:
    max_shift: int = height
    offsets: list[int] = [0]
    for d in range(1, max_shift):
        offsets += [d, -d]

    for dy in offsets:
        candidate_y = base_y + dy
        if not fits_in_maze(base_x, candidate_y, width, height):
            continue
        if not any(in_bounding_box(p, base_x, candidate_y) for p in protected):
            return base_x, candidate_y

    raise ValueError("no valid vertical position for 42 pattern")


def make_42_walls(
    width: int, height: int,
    entry: Cell, goal: Cell
) -> list[Cell]:

    pattern_width: int = 7
    pattern_height: int = 5

    if ((width + 3) <= pattern_width) | ((height + 3) <= pattern_height):
        raise ValueError("width or height is too small to add 42!")

    start_x: int = width // 2
    start_y: int = height // 2

    if width % 2 == 0:
        start_x -= 1
    if height % 2 == 0:
        start_y -= 1

    wall_42: list[Cell] = build_pattern(start_x, start_y)

    # entryとgoalの場所と４２の場所がかぶっていないか見る関数
    answer = overlaps_start_or_exit(wall_42, entry, goal)
    # 範囲内に収まっているかと、保護座標をかぶっていないかをチェックする。
    # 候補位置を順に試す。

    return wall_42


def print_42_shape(
    width: int, height: int, entry: tuple[int, int],
    goal: tuple[int, int]
) -> None:
    wall_cells: list[Cell] = make_42_walls(width, height, entry, goal)
    wall_set = set(wall_cells)
    for y in range(height):
        row = "".join("#" if (x, y) in wall_set else "." for x in range(width))
        print(row)


if __name__ == "__main__":
    try:
        print_42_shape(8, 6, (2, 2), (4, 5))
    except ValueError:
        print("error")
