Cell = tuple[int, int]

N, E, S, W = 1, 2, 4, 8  # ビットが立ってる = 壁で閉じてる
DIRS = [(0, -1, N), (1, 0, E), (0, 1, S), (-1, 0, W)]
OPPOSITE = {N: S, S: N, E: W, W: E}


def full_grid(width: int, height: int) -> dict[Cell, int]:
    """全マス壁で閉じた初期状態(箱)"""
    return {(x, y): N | E | S | W for x in range(width) for y in range(height)}


def open_wall(maze: dict[Cell, int], a: Cell, direction: int) -> None:
    """aから指定方向へ壁を開ける(隣接セルの反対側も開ける)"""
    dx, dy = next((dx, dy) for dx, dy, bit in DIRS if bit == direction)
    b = (a[0] + dx, a[1] + dy)
    maze[a] &= ~direction
    maze[b] &= ~OPPOSITE[direction]


# ── パターン1: 2x2、シンプルに一本道で繋がってる ──
maze_2x2_simple = full_grid(2, 2)
open_wall(maze_2x2_simple, (0, 0), E)
open_wall(maze_2x2_simple, (1, 0), S)
# entry=(0,0), exit=(1,1)


# ── パターン2: 3x3、ループあり + 到達不可能マス(1,1)を含む ──
maze_3x3_loop = full_grid(3, 3)
for a, d in [
    ((0, 0), E), ((1, 0), E), ((2, 0), S), ((2, 1), S),  # 上ルート
    ((0, 0), S), ((0, 1), S), ((0, 2), E), ((1, 2), E),  # 下ルート
]:
    open_wall(maze_3x3_loop, a, d)
# entry=(0,0), exit=(2,2)。(1,1)はどこにも繋がってない孤立マス


# ── パターン3: 経路が存在しないケース(exitが完全に孤立) ──
maze_no_path = full_grid(2, 2)
open_wall(maze_no_path, (0, 0), E)  # (0,0)-(1,0)だけ繋がってる
# entry=(0,0), exit=(1,1) だが (1,1) は誰とも繋がってない → Noneが正しい


# ── ランダム迷路ジェネレータ(再帰的バックトラッカー、必ず全マス連結) ──
import random

def generate_maze(width: int, height: int, seed: int | None = None) -> dict[Cell, int]:
    rng = random.Random(seed)
    maze = full_grid(width, height)
    visited: set[Cell] = set()

    def carve(cell: Cell) -> None:
        visited.add(cell)
        dirs = DIRS.copy()
        rng.shuffle(dirs)
        for dx, dy, bit in dirs:
            nxt = (cell[0] + dx, cell[1] + dy)
            if 0 <= nxt[0] < width and 0 <= nxt[1] < height and nxt not in visited:
                open_wall(maze, cell, bit)
                carve(nxt)

    carve((0, 0))
    return maze


if __name__ == "__main__":
    # 使用例
    print(maze_2x2_simple)
    print(maze_3x3_loop)
    print(maze_no_path)
    print(generate_maze(5, 5, seed=42))

# open_wallは両側のビットを正しく整合させて開けるので、「壁の噛み合わせがおかしい」というミスが起きません
# パターン1〜3はbfsの基本動作・ループ耐性・None判定をそれぞれ確認できます
# generate_mazeは再帰的バックトラッカー方式で、必ず全マスが連結する(=entry/exitどこでも繋がってる)迷路をランダム生成できます。
# seedを固定すれば再現性のあるテストにも使えます