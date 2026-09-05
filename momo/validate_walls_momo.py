# セルAの方向dに壁がある ⇒ 
# 隣のセルB(Aからd方向に1マス進んだセル)の、dの逆方向にも壁がある
# を、全セル・全方向についてチェックする
import logging

Cell = tuple[int, int]

N = 1  # NORTH
E = 2  # EAST
S = 4  # SOUTH
W = 8  # WEST

DIRECTIONS: list[tuple[int, int, int]] = [
    (0, -1, N),
    (1, 0, E),
    (0, 1, S),
    (-1, 0, W),
]

OPPOSITE = {N: S, S: N, E: W, W: E}

def validate_walls(walls: Cell, width: int, height: int) -> bool:
    for y in range(height):
        for x in range(width):
            cell_walls = walls[(x, y)]
            for dx, dy, direction in DIRECTIONS:
                if not (cell_walls & direction):
                    continue  # この方向に壁がないならスキップ

                nx, ny = x + dx, y + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue  # 隣が範囲外なら対象外

                neighbor_walls = walls[(nx, ny)]
                if not (neighbor_walls & OPPOSITE[direction]):
                    logging.error(
                        f"壁の不整合: セル{(x,y)}に方向{direction}の壁があるが、"
                        f"隣セル{(nx,ny)}に対応する壁がない"
                    )
                    return False
    return True
