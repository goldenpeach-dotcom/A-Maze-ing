Cell = tuple[int, int]


def get_protected_points(
    width: int, height: int,
    entry: Cell, exit_point: Cell
) -> list[Cell]:
    """ 保護すべき座標（四隅、中心、入口、出口）を取得する """
    corners: list[Cell] = [
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
    ]

    # 偶数の場合は「田の字」の4マス、奇数の場合は1マスを正しく中心点として保護
    x_mid: list[int] = (
        [width // 2] if width % 2 else [width // 2 - 1, width // 2]
    )
    y_mid: list[int] = (
        [height // 2] if height % 2 else [height // 2 - 1, height // 2]
    )
    center: list[Cell] = [(x, y) for x in x_mid for y in y_mid]
    
    return corners + center + [entry, exit_point]


def fits_in_maze(start_x: int, start_y: int, width: int, height: int) -> bool:
    """ 42パターンの外枠（幅7 × 高さ5）が迷路の枠内に収まるかチェック """
    return (start_x - 3 >= 0 and start_x + 3 < width
            and start_y - 2 >= 0 and start_y + 2 < height)


def generate_offsets_2d(max_shift: int) -> list[tuple[int, int]]:
    """ 中心(0,0)から渦巻き（リング状）に外側へ広がる探索オフセットを生成する
        これにより、最初に見つかった安全な座標が「最も中央に近い」場所になります
    """
    offsets:list[tuple[int, int]] = []
    for d in range(max_shift):
        for dx in range(-d, d + 1):
            for dy in range(-d, d + 1):
                if max(abs(dx), abs(dy)) == d:
                    offsets.append((dx, dy))
    return offsets


def build_pattern(start_x: int, start_y: int) -> list[Cell]:
    """ 42パターン座標（デザイン維持） """
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
    """ 条件をすべて満たし、最も中央に近い場所に42の壁を配置する """
    pattern_width: int = 7
    pattern_height: int = 5

    # 迷路が小さすぎる（42の外枠＋周囲1マスの余白がない）ときは配置しない
    if width <= (pattern_width + 3) or height <= (pattern_height + 3):
        print("width or height is too small to add 42!")
        return []

    # 探索のスタート地点（基準となる中心）
    start_x: int = width // 2
    start_y: int = height // 2
    if width % 2 == 0:
        start_x -= 1
    if height % 2 == 0:
        start_y -= 1

    # 保護座標のセットを取得（重複チェックを高速化するため set に変換）
    protected_set = set(get_protected_points(width, height, entry, goal))

    # 縦横に渦巻き状に広がる探索オフセットを生成
    max_shift = max(width, height)
    offsets = generate_offsets_2d(max_shift)

    # 「できるだけ中央に近い場所」から順に全探索
    for dx, dy in offsets:
        candidate_x = start_x + dx
        candidate_y = start_y + dy

        # 迷路の外枠に収まらないならスキップ
        if not fits_in_maze(candidate_x, candidate_y, width, height):
            continue

        # 候補地の42の壁座標を実際に生成
        candidate_walls = build_pattern(candidate_x, candidate_y)

        # 【超重要】実際の壁のマスが、保護座標（入口・出口・中央・四隅）と1マスでも重なっていたらNG
        # 重なりがなければ、ここが「最も中央に近い有効な位置」なので即座に決定
        if not protected_set.intersection(candidate_walls):
            return candidate_walls

    print("no valid position found for 42 pattern; returning empty wall list")
    return []


def print_42_shape(width: int, height: int, entry: Cell, goal: Cell) -> None:
    """ テスト表示用関数 """
    wall_cells: list[Cell] = make_42_walls(width, height, entry, goal)
    if not wall_cells:
        print("配置できませんでした。")
        return

    wall_set = set(wall_cells)
    protected_set = set(get_protected_points(width, height, entry, goal))

    for y in range(height):
        row = ""
        for x in range(width):
            if (x, y) == entry:
                row += "S"  # Start
            elif (x, y) == goal:
                row += "G"  # Goal
            elif (x, y) in wall_set:
                row += "#"  # 42の壁
            elif (x, y) in protected_set:
                row += "X"  # 保護されている中心や四隅
            else:
                row += "."  # 通路
        print(row)


if __name__ == "__main__":
    print_42_shape(70, 36, (36, 17), (32, 18))
