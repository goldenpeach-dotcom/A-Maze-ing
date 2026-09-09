
import random
from . import make_42_wall
from collections import deque

Cell = tuple[int, int]

N = 1
E = 2
S = 4
W = 8

DIRECTIONS: list[tuple[int, int, int]] = [
    (0, -1, N),
    (1, 0, E),
    (0, 1, S),
    (-1, 0, W),
    ]

OPPOSITE = {N: S, S: N, E: W, W: E}

MIN_LOOPS = 2  # PERFECT=Falseの迷路が持つべき、独立したループの最低数(課題要件)


def _protected_cells(
    width: int, height: int, entry: Cell, exit: Cell
) -> set[Cell]:
    """"42"パターンを置いてはいけないセルの集合を求める。

    Args:
        width: 迷路の幅。
        height: 迷路の高さ。
        entry: 入口の座標。
        exit: 出口の座標。

    Returns:
        四隅・中央・entry・exit をまとめたセルの集合。
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
    """グリッド型の迷路を生成するクラス。

    入口・出口・42パターンを持つ迷路を作り、最短経路の取得もできる。
    """
    def __init__(
            self, width: int, height: int,
            entry: Cell, exit: Cell,
            perfect: bool = False,
            seed: int | None = None,
            ) -> None:
        """迷路の設定を受け取り、初期状態(全セル壁閉じ)を作る。

        Args:
            width: 迷路の幅(セル数)。
            height: 迷路の高さ(セル数)。
            entry: 入口の座標。
            exit: 出口の座標(entryと異なる必要がある)。
            perfect: Trueならループの無い一本道、Falseなら複数経路の盤面。
            seed: 乱数のシード。同じ値なら同じ迷路になる。

        例外:
            ValueError: サイズ・座標・PERFECTの組み合わせが不正な場合。
        """
        if width < 1 or height < 1:
            raise ValueError("width and height must be positive")
        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("entry is outside the maze bounds")
        if not (0 <= exit[0] < width and 0 <= exit[1] < height):
            raise ValueError("exit is outside the maze bounds")
        if entry == exit:
            raise ValueError("entry and exit must be different cells")
        if not perfect and (width - 1) * (height - 1) < MIN_LOOPS:
            raise ValueError(
                "maze is too small for PERFECT=False "
                f"(need at least {MIN_LOOPS} independent loops)"
            )

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.seed = seed
        self._random = random.Random(seed)
        self._walls: dict[Cell, int] = {
            (x, y): 15 for x in range(width) for y in range(height)}
        self._protected: set[Cell] = _protected_cells(
            width, height, entry, exit)
        self.pattern_omitted_reason: str | None = None
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
        """スパニングツリー方式で迷路を掘り進める。

        perfect=Falseの場合は、この後さらに_add_loops()でループを追加する。
        """
        stack = [self.entry]
        un_visit = set(self._walls) - {self.entry} - self._42blocked

        while stack:
            current = stack[-1]
            candidates = []
            for dx, dy, bit in DIRECTIONS:
                nx, ny = current[0] + dx, current[1] + dy
                if (
                    (0 <= nx < self.width)
                    and (0 <= ny < self.height)
                    and (nx, ny) in un_visit
                ):
                    candidates.append((nx, ny, bit))
            if candidates:
                nx, ny, bit = self._random.choice(candidates)
                next_cell = nx, ny
                un_visit.discard(next_cell)
                self._walls[current] &= ~bit
                self._walls[next_cell] &= ~OPPOSITE[bit]
                stack.append(next_cell)
            else:
                stack.pop()

        if not self.perfect:
            self._add_loops()

    def _add_loops(self) -> None:
        """行き止まりを解消しつつ、最低MIN_LOOPS個のループを作る。

        まず行き止まりのセルを狙って壁を開ける。それでもループ数が
        足りない場合は、盤面全体から追加でループを探す。
        """
        cells = list(self._walls)
        dead_ends = [
            cell for cell in cells if self._walls[cell]
            in {7, 11, 13, 14} and cell not in self._42blocked
        ]
        self._random.shuffle(dead_ends)
        loops = 0
        for cell in dead_ends:
            for dx, dy, bit in DIRECTIONS:
                nx, ny = cell[0] + dx, cell[1] + dy
                if (
                    (0 <= nx < self.width)
                    and (0 <= ny < self.height)
                    and self._walls[cell] & bit
                    and (nx, ny) not in self._42blocked
                ):
                    if self._check_3X3(cell, bit, (nx, ny)):
                        self._walls[cell] &= ~bit
                        self._walls[(nx, ny)] &= ~OPPOSITE[bit]
                        loops += 1
                        break

        if loops < MIN_LOOPS:
            # 行き止まり解消だけではループ数が足りなかった場合の保険。
            # 行き止まりに限らず、盤面全体から追加でループを探す。
            fallback_candidates = [
                cell for cell in cells if cell not in self._42blocked
            ]
            self._random.shuffle(fallback_candidates)
            for cell in fallback_candidates:
                if loops >= MIN_LOOPS:
                    break
                for dx, dy, bit in DIRECTIONS:
                    nx, ny = cell[0] + dx, cell[1] + dy
                    if (
                        (0 <= nx < self.width)
                        and (0 <= ny < self.height)
                        and self._walls[cell] & bit
                        and (nx, ny) not in self._42blocked
                    ):
                        if self._check_3X3(cell, bit, (nx, ny)):
                            self._walls[cell] &= ~bit
                            self._walls[(nx, ny)] &= ~OPPOSITE[bit]
                            loops += 1
                            break

    def _check_3X3(
        self, cell: Cell, bit: int, next_cell: Cell
    ) -> bool:
        """壁を開けると3x3の空き部屋になるかを判定する。

        Args:
            cell: 今いる座標。
            bit: 開こうとしている方向(N/E/S/W)。
            next_cell: 壁を開ける先のセル。

        Returns:
            True: 3x3の空き部屋にならない(安全)。False: なる(危険)。
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
                            if (not is_candidate) and (
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
                            if (not is_candidate) and (
                                self._walls[(x, y)] & scan_bit
                            ):
                                block_ng_flg = False
                if block_ng_flg:
                    return False
        return True

    def shortest_path(self) -> list[Cell] | None:
        """BFSで入口から出口までの最短経路を求める。

        Returns:
            entryからexitまでの座標のリスト。到達できなければNone。
        """
        queue = deque([self.entry])
        came_from: dict[Cell, Cell] = {}   # 「このマスにはどこから来たか」
        visited = {self.entry}
        found: bool = False

        while queue:
            current = queue.popleft()      # キューの先頭を取り出す(FIFO)

            if current == self.exit:
                found = True
                break                      # ゴール到達 → ループ終了

            for dx, dy, bit in DIRECTIONS:
                # 壁があったら次
                if self._walls[current] & bit:
                    continue

                nx, ny = current[0] + dx, current[1] + dy
                next_cell = (nx, ny)

                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue  # 念のための境界チェック

                # 訪問済みなら次
                if next_cell in visited:
                    continue

                visited.add(next_cell)
                came_from[next_cell] = current
                queue.append(next_cell)

        if not found:
            return None

        # ここまで来たら current == goal のはず。goalからstartまで逆にたどる
        path = [current]
        while current != self.entry:
            current = came_from[current]
            path.append(current)

        path.reverse()
        return path
