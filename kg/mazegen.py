
import random
import make_42_wall

Cell = tuple[int, int]

N = 1  # NORTH 0001 1は閉じてる
E = 2  # EAST 0010
S = 4  # SOUTH 0100
W = 8  # WEST 1000

DIRECTIONS: list[tuple[int, int, int]] = [
    (0, -1, N),
    (1, 0, E),
    (0, 1, S),
    (-1, 0, W),
    ]  # (dx,dy,方角bit)のタプルリスト、セルの移動時に使う

OPPOSITE = {N: S, S: N, E: W, W: E}


def _protected_cells(
    width: int, height: int, entry: Cell, exit: Cell
) -> set[Cell]:
    """
        "42"パターンが絶対に置いてはいけないセルを求める
        引数：
            width 迷路の幅
            height 迷路の高さ
            entry 入口の座標
            exit 出口の座標
        返し値:
            四隅・中央（候補：1個か2個か4個）・entry・exit をまとめたCell(座標)
    """
    corners = {
        (0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)
    }
    x_mid = {width // 2} if width % 2 else {width // 2 - 1, width // 2}
    y_mid = {height // 2} if height % 2 else {height // 2 - 1, height // 2}
    # centre = set()
    #     for x in x_mid:
    #         for y in y_mid:
    #             centre.add((x, y))
    centre = {(x, y) for x in x_mid for y in y_mid}
    protect_cells = corners.union(centre, {entry, exit})
    return protect_cells


class MazeGenerator:
    def __init__(
            self, width: int, height: int,
            entry: Cell, exit: Cell,
            perfect: bool = False,
            seed: int | None = None,
            ) -> None:
        """
        迷路を作るクラス
        """
        if not perfect and (width - 1) * (height - 1) < 2:
            raise ValueError(
                "maze is too small for PERFECT=False "
                "(need at least 2 independent loops)"
            )

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.seed = seed
        self._random = random.Random(seed)
        # randomモジュールのクラスrandom.Random、乱数生成インスタンス
        # seedに値がなければランダムに生成される、同じ数値で再現性
        self._walls: dict[Cell, int] = {
            (x, y): 15 for x in range(width) for y in range(height)}
        self._protected: set[Cell] = _protected_cells(
            width, height, entry, exit)
        # 保護するcell 中央値、四隅、入口出口
        self.pattern_omitted_reason: str | None = None
        # 42ブロックが保護するセルを上書きしようとした場合のフラグ
        proposed_42 = set(
            make_42_wall.make_42_walls(width, height, entry, exit)
        )
        if not proposed_42:
            self._42blocked: set[Cell] = set()
            self.pattern_omitted_reason = (
                "'42' pattern could not be placed for this maze size"
            )
        else:
            violations = proposed_42 & self._protected
            if violations:
                self._42blocked = set()
                self.pattern_omitted_reason = (
                    "'42' pattern overlapped a protected cell "
                    "and was omitted"
                )
            else:
                self._42blocked = proposed_42

    def generator(self) -> None:
        stack = [self.entry]
        un_visit = set(self._walls) - {self.entry} - self._42blocked
        # 未訪問Cellリスト、最初にentry以外のCellを全部入れる、set済み42ブロックも引く

        while stack:  # maze作成ロジック
            current = stack[-1]
            # 今いる場所、-1は後ろから1番目の意味、1だと前から、2だと前2番目...
            candidates = []
            # 壁を空ける候補を入れる箱
            for dx, dy, bit in DIRECTIONS:  # 進む方向を探る、次に進むセル候補をピックアップ
                nx, ny = current[0] + dx, current[1] + dy
                # 次進むセル、tupleなのでindexで取り出す
                if (
                    (0 <= nx < self.width)
                    and (0 <= ny < self.height)
                    and (nx, ny) in un_visit  # 外壁内で、まだ通っていなかったら
                ):
                    candidates.append((nx, ny, bit))  # 候補にcell入れる
            if candidates:  # 候補セルが存在すれば
                dx, dy, bit = self._random.choice(candidates)
                # 候補内から選んでcellにunpack、choiceは無作為
                next_cell = dx, dy  # 選んだ座標を次に進むセルとして入れる
                un_visit.discard(next_cell)
                # currentとnext_cellと壁の穴あけ、bitマスク↓、self.wallsの更新をここでやる
                self._walls[current] &= ~bit
                self._walls[next_cell] &= ~OPPOSITE[bit]
                stack.append(next_cell)  # whileで掘り進める
            else:
                stack.pop()  # どこにもいけないから戻る

        if not self.perfect:
            self._add_loops()  # loopを最低1つ作るメソッド、全域木perfect:True作った後の分岐

    def _add_loops(self) -> None:  # loop作るための壁の穴あけ
        cells = list(self._walls)
        self._random.shuffle(cells)
        loops: int = 0
        for cell in cells:
            if loops >= 2:
                break
            if cell in self._42blocked:
                continue
            for dx, dy, bit in DIRECTIONS:
                nx, ny = cell[0] + dx, cell[1] + dy
                if (
                    (0 <= nx < self.width)
                    and (0 <= ny < self.height)  # 幅高さチェック
                    and self._walls[cell] & bit
                    # 穴閉じてるか積集合＆チェック、共通して持っているbitがあればその方角に壁がある
                    and (nx, ny) not in self._42blocked  # 42ブロック避ける
                ):
                    # ここで3＊3穴にならないかチェックする、falseでbreak
                    if self._check_3X3(cell, bit, (nx, ny)):
                        self._walls[cell] &= ~bit
                        self._walls[(nx, ny)] &= ~OPPOSITE[bit]
                        loops += 1
                        break

    def _check_3X3(
        self, cell: Cell, bit: int, next_cell: Cell
    ) -> bool:  # 3X3マス回避
        """"3X3"空白マスになるかチェックする
            引数：
                cell 今いる座標
                bit 進む方向（東西南北）
                next_cell 壁を開ける先のセル
            返し値：
                True 3X3空白にならない ,False なる
        """
        cx, cy = cell
        nx, ny = next_cell
        min_x, max_x = min(cx, nx), max(cx, nx)
        min_y, max_y = min(cy, ny), max(cy, ny)

        for tx in range(max_x - 2, min_x + 1):
            for ty in range(max_y - 2, min_y + 1):
                block_ng_flg = True
                if not (
                    (0 <= tx) and (tx + 2 < self.width)
                    and (0 <= ty) and (ty + 2 < self.height)
                ):
                    continue
                for x in range(tx, tx + 3):
                    for y in range(ty, ty + 3):
                        if x < tx + 2:
                            scan_bit = E
                            is_candidate = (
                                (x, y) == cell and bit == scan_bit
                            ) or (
                                (x, y) == next_cell
                                and scan_bit == OPPOSITE[bit]
                            )
                            if not is_candidate and not (
                                self._walls[(x, y)] & scan_bit
                            ):
                                block_ng_flg = False
                        if y < ty + 2:
                            scan_bit = S
                            is_candidate = (
                                (x, y) == cell and bit == scan_bit
                            ) or (
                                (x, y) == next_cell
                                and (scan_bit == OPPOSITE[bit])
                            )
                            if not is_candidate and not (
                                self._walls[(x, y)] & scan_bit
                            ):
                                block_ng_flg = False
                if block_ng_flg:
                    return False
        return True
