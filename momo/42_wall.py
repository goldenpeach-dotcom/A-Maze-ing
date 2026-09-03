Cell = tuple[int, int]

def get_protected_points(width: int, height: int, entry: Cell, exit_point: Cell) -> list[Cell]:
    corners: list[Cell] = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]
    center: Cell = (width // 2, height // 2)
    return corners + [center, entry, exit_point]


def fits_in_maze(start_x: int, start_y: int, width: int, height: int) -> bool:
    return (start_x - 3 >= 0 and start_x + 3 < width
            and start_y - 2 >= 0 and start_y + 2 < height)


def in_bounding_box(point: Cell, start_x: int, start_y: int) -> bool:
    px, py = point
    if px == start_x:
        return False
    return (start_x - 3 <= px <= start_x + 3) and (start_y - 2 <= py <= start_y + 2)

def generate_offsets(max_shift: int) -> list[int]:
    offsets: list[int] = [0]
    for d in range(1, max_shift):
        offsets += [d, -d]
    return offsets


def find_valid_position(
    base_x: int, base_y: int, width: int, height: int, protected: list[Cell]) -> tuple[int, int]:
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


def build_pattern(start_x: int, start_y:int) -> list[Cell]:
    return[
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


def make_42_walls(width: int, height: int, entry: Cell, goal: Cell) -> list[Cell]:
    pattern_width: int = 7
    pattern_height: int = 5

    if (width + 3) <= pattern_width or (height + 3) <= pattern_height:
        raise ValueError("width or height is too small to add 42!")

    start_x: int = width // 2
    start_y: int = height // 2
    if width % 2 == 0:
        start_x -= 1
    if height % 2 == 0:
        start_y -= 1

    protected = get_protected_points(width, height, entry, goal)

    try:
        valid_x, valid_y = find_valid_position(start_x, start_y, width, height, protected)
    except ValueError:
        valid_x, valid_y = find_valid_position_2d(start_x, start_y, width, height, protected)


    wall_42 = build_pattern(valid_x, valid_y)

    return wall_42


def print_42_shape(width: int, height: int, entry: Cell, goal: Cell) -> None:
    wall_cells: list[Cell] = make_42_walls(width, height, entry, goal)
    wall_set = set(wall_cells)
    for y in range(height):
        row = "".join("#" if (x, y) in wall_set else "." for x in range(width))
        print(row)


if __name__ == "__main__":
    try:
        print_42_shape(17 , 15, (8 ,2), (4, 5))
    except ValueError:
        print("error")

