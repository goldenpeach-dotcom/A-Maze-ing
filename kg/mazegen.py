
import random
import make_42_wall
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
                dx, dy, bit = self._random.choice(candidates)
                next_cell = dx, dy
                un_visit.discard(next_cell)
                self._walls[current] &= ~bit
                self._walls[next_cell] &= ~OPPOSITE[bit]
                stack.append(next_cell)
            else:
                stack.pop()

        if not self.perfect:
            self._add_loops()

    def _add_loops(self) -> None:
        """
            perfectがfalseの時に必要となるloopを作る
            引数：
                クラスattribute
            返し値:
                なし
        """
        cells = list(self._walls)
        self._random.shuffle(cells)
        loops: int = 0
        for cell in cells:
            if loops >= 20:
                break
            if cell in self._42blocked:
                continue
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
                            if not is_candidate and (
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
                            if not is_candidate and (
                                self._walls[(x, y)] & scan_bit
                            ):
                                block_ng_flg = False
                if block_ng_flg:
                    return False
        return True

    def shortest_path(self) -> list[Cell] | None:
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
