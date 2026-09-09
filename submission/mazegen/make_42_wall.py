Cell = tuple[int, int]

PATTERN_WIDTH = 7
PATTERN_HEIGHT = 5


def get_protected_points(
    width: int, height: int,
    entry: Cell, exit_point: Cell
) -> list[Cell]:
    """ 保護すべき座標（四隅、中心、入口、出口）を取得する
        Obtain the coordinates to be protected
        (four corners, center, entrance, and exit).
        Args:width,height　壁の縦横
            entry,exit_point 入口出口座標

        Returns:（４２の壁をおけない）いじれないセルリスト
    """
    corners: list[Cell] = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]

    x_mid: list[int] = (
        [width // 2] if width % 2 else [width // 2 - 1, width // 2]
    )
    y_mid: list[int] = (
        [height // 2] if height % 2 else [height // 2 - 1, height // 2]
    )
    center: list[Cell] = [(x, y) for x in x_mid for y in y_mid]

    return corners + center + [entry, exit_point]


def build_pattern(start_x: int, start_y: int) -> list[Cell]:
    """ 42 coordinates 
        Args: strart_x start_y 42ブロックの座標かたまり
        Return:42ブロックの座標かたまり
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
    """ 条件をすべて満たし、最も中央に近い場所に42の壁を配置する

        Place the 42 walls in the location closest
        to the center that satisfies all conditions.
    """

    if width <= (PATTERN_WIDTH + 3) or height <= (PATTERN_HEIGHT + 3):
        return []

    protected_set = set(get_protected_points(width, height, entry, goal))

    # 42パターンが枠内に収まる中心候補
    # A top contender fitting within the 42-pattern framework.

    candidates = [
        (x, y)
        for x in range(3, width - 3)
        for y in range(2, height - 2)
    ]

    # 真の中心（偶数幅高さでも小数でOK）からの距離が近い順に並べ替える
    # Sort by proximity to the true center (decimal values ​​are acceptable,
    #  even with even-numbered widths or heights).

    center_x, center_y = (width - 1) / 2, (height - 1) / 2
    candidates.sort(
        key=lambda p: max(abs(p[0] - center_x), abs(p[1] - center_y))
    )

    for x, y in candidates:
        candidate_walls = build_pattern(x, y)
        if not protected_set.intersection(candidate_walls):
            return candidate_walls

    return []


def print_42_shape(width: int, height: int, entry: Cell, goal: Cell) -> None:
    """ test print """

    wall_cells: list[Cell] = make_42_walls(width, height, entry, goal)
    if not wall_cells:
        print("42walls can not placed...")
        return

    wall_set = set(wall_cells)
    protected_set = set(get_protected_points(width, height, entry, goal))

    for y in range(height):
        row = ""
        for x in range(width):
            if (x, y) == entry:
                row += "S"
            elif (x, y) == goal:
                row += "G"
            elif (x, y) in wall_set:
                row += "#"
            elif (x, y) in protected_set:
                row += "X"
            else:
                row += "."
        print(row)


def main() -> None:
    print_42_shape(60, 15, (10, 12), (40, 4))


if __name__ == "__main__":
    main()
