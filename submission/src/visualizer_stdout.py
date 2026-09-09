
from mazegen import E, N, S, W, MazeGenerator, Cell

WALL_COLORS = [
    "\033[31m", "\033[32m", "\033[34m",
    "\033[33m", "\033[35m", "\033[36m"
    ]


def render(
    maze: MazeGenerator, color_index: int = 0,
    path: list[Cell] | None = None
) -> str:
    """迷路を標準出力でカラー付きの文字列に描画する。

    Args:
        maze: 描画対象の迷路。
        color_index: 壁の色(WALL_COLORSのインデックス)。
        path: 表示する最短経路(Noneなら表示しない)。

    Returns:
        画面にそのままprintできる、複数行の文字列。
    """
    grid_w, grid_h = 2 * maze.width + 1, 2 * maze.height + 1
    canvas = [["██"] * grid_w for _ in range(grid_h)]

    WALL_COLOR = WALL_COLORS[color_index % len(WALL_COLORS)]
    RESET = "\033[0m"
    current_color = WALL_COLOR

    for gy in range(0, grid_h, 2):
        for gx in range(0, grid_w, 2):
            canvas[gy][gx] = f"{current_color}██{RESET}"

    for (x, y), walls in maze._walls.items():
        cx, cy = 2 * x + 1, 2 * y + 1
        if (x, y) in maze._42blocked:
            canvas[cy][cx] = "░░"
        if walls & N:
            canvas[cy - 1][cx] = f"{current_color}██{RESET}"
        if walls & S:
            canvas[cy + 1][cx] = f"{current_color}██{RESET}"
        if walls & W:
            canvas[cy][cx - 1] = f"{current_color}██{RESET}"
        if walls & E:
            canvas[cy][cx + 1] = f"{current_color}██{RESET}"

    for (x, y) in maze._42blocked:
        cx, cy = 2 * x + 1, 2 * y + 1
        for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0)):
            if (x + dx, y + dy) in maze._42blocked:
                canvas[cy + dy][cx + dx] = "░░"

    path_cells = path or []
    for (x, y) in path_cells:
        canvas[2 * y + 1][2 * x + 1] = f"{WALL_COLORS[4]}░░{RESET}"
    for (x1, y1), (x2, y2) in zip(path_cells, path_cells[1:]):
        canvas[y1 + y2 + 1][x1 + x2 + 1] = f"{WALL_COLORS[4]}░░{RESET}"

    ex, ey = maze.entry
    xx, xy = maze.exit
    canvas[2 * ey + 1][2 * ex + 1] = f"{WALL_COLOR}EN{RESET}"
    canvas[2 * xy + 1][2 * xx + 1] = f"{WALL_COLOR}EX{RESET}"

    return "\n".join("".join(row) for row in canvas)


def main() -> None:
    """このファイル単体での動作確認用(決め打ちの迷路を1個描画する)。"""
    maze = MazeGenerator(
        width=19, height=15, entry=(0, 0), exit=(18, 11), perfect=False
    )
    maze.generator()
    print(render(maze, color_index=1, path=maze.shortest_path()))


if __name__ == "__main__":
    main()
