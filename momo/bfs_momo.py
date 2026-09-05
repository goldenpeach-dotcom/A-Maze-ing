from collections import deque

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


def bfs(walls: dict[Cell, int], start: Cell, goal: Cell) -> list[Cell] | None:
    queue = deque([start])
    came_from: dict[Cell, Cell] = {}   # 「このマスにはどこから来たか」
    visited = {start}
    Found = False

    while queue:
        current = queue.popleft()      # キューの先頭を取り出す(FIFO)

        if current == goal:
            Found = True
            break                      # ゴール到達 → ループ終了

        for dx, dy, bit in DIRECTIONS:
            nx, ny = current[0] + dx, current[1] + dy
            next_cell = (nx, ny)

            # 壁があったら次
            if walls[current] & bit:
                continue
            # 訪問済みなら次
            if next_cell in visited:
                continue

            visited.add(next_cell)
            came_from[next_cell] = current
            queue.append(next_cell)

    if not Found:
        return None

    # ここまで来たら current == goal のはず。goalからstartまで逆にたどる
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path
