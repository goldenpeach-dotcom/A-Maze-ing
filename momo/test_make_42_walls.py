"""
make_42_walls の境界値・中心パターン・異常系テスト。

観点:
  1. width/height の奇数・偶数の4パターン（中心の座標定義が変わる）
  2. 「小さすぎて配置不可」の境界ちょうど（ぎりぎりOK / ぎりぎりNG）
  3. 極端な縦横比（幅だけ広い／高さだけ広い）
  4. entry/exit が中心の保護マスに重なる・隣接するケース
  5. entry/exit が四隅（既に保護済み）と重なるケース
  6. 実際に「解なし」になることが分かっているケース（クラッシュせず[]を返すか）
  7. entry == exit など、通常はあり得ない入力でも例外を出さないか
"""

from make_42_wall_simple import make_42_walls, get_protected_points, print_42_shape

Cell = tuple[int, int]


def check_result(
    label: str, width: int, height: int, entry: Cell, goal: Cell,
    expect_empty: bool | None = None,
) -> None:
    protected = set(get_protected_points(width, height, entry, goal))
    try:
        walls = make_42_walls(width, height, entry, goal)
    except Exception as e:
        print(f"[NG] {label}: 例外発生 -> {e!r}")
        return

    if expect_empty is True and walls:
        print(f"[NG] {label}: 空を期待したが {len(walls)} マス返ってきた")
        return
    if expect_empty is False and not walls:
        print(f"[NG] {label}: 配置できることを期待したが空だった")
        return

    if walls:
        # 保護座標と重なっていないか
        overlap = protected.intersection(walls)
        if overlap:
            print(f"[NG] {label}: 保護座標と重複 -> {overlap}")
            return
        # 盤面からはみ出していないか
        out_of_bounds = [
            (x, y) for x, y in walls
            if not (0 <= x < width and 0 <= y < height)
        ]
        if out_of_bounds:
            print(f"[NG] {label}: 盤外にはみ出し -> {out_of_bounds}")
            return

    print(f"[OK] {label}: walls={len(walls)}マス")


if __name__ == "__main__":
    # --- 1. 奇数/偶数の4パターン（中心の座標定義が変わる境界） ---
    check_result("奇数幅×奇数高さ", 71, 37, (0, 1), (70, 35), expect_empty=False)
    check_result("偶数幅×奇数高さ", 70, 37, (0, 1), (69, 35), expect_empty=False)
    check_result("奇数幅×偶数高さ", 71, 36, (0, 1), (70, 34), expect_empty=False)
    check_result("偶数幅×偶数高さ", 70, 36, (34, 18), (34, 14), expect_empty=False)

    # --- 2. 配置可否のちょうど境界 ---
    check_result("ぎりぎり配置可(11,9)", 11, 9, (0, 0), (10, 8), expect_empty=False)
    check_result("幅が1足りない(10,9)は不可", 10, 9, (0, 0), (9, 8), expect_empty=True)
    check_result("高さが1足りない(11,8)は不可", 11, 8, (0, 0), (10, 7), expect_empty=True)

    # --- 3. 極端な縦横比 ---
    check_result("横に極端に細長い(101,9)", 101, 9, (0, 0), (100, 8), expect_empty=False)
    check_result("縦に極端に細長い(11,101)", 11, 101, (0, 0), (10, 100), expect_empty=False)

    # --- 4. entry/exitが中心の保護マスに重なる・隣接する ---
    # 偶数×偶数の中心4マスのうちの2つをそのままentry/exitにする
    check_result("entry/exitが中心の保護マスそのもの", 70, 36, (34, 17), (35, 18), expect_empty=False)
    # 中心のすぐ隣にentry/exitを置き、さらに配置を難しくする
    check_result("entry/exitが中心のすぐ隣", 70, 36, (33, 17), (36, 18), expect_empty=False)

    # --- 5. entry/exitが四隅（既に保護済み）と重なる ---
    check_result("entry/exitが四隅と重複", 70, 36, (0, 0), (69, 35), expect_empty=False)

    # --- 6. 実際に「解なし」が発生するケース（総当たりで発見済み） ---
    check_result("解なしになる小さい迷路", 12, 9, (4, 5), (7, 4), expect_empty=True)

    # --- 7. 通常あり得ない入力でも例外を出さないか ---
    check_result("entry == exit", 15, 11, (5, 5), (5, 5), expect_empty=False)
    check_result("width/heightが極端に小さい(1,1)", 1, 1, (0, 0), (0, 0), expect_empty=True)
    check_result("width/heightが0", 0, 0, (0, 0), (0, 0), expect_empty=True)

    print()
    print("--- 目視確認用: 偶数×偶数で保護4マスと壁の位置関係 ---")
    print_42_shape(70, 36, (34, 18), (34, 14))
