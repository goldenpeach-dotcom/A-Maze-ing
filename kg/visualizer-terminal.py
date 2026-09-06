
import os

from mazegen import E, N, S, W, MazeGenerator


STATE_FILE = os.path.join(os.path.dirname(__file__), ".color_state")

WALL_COLORS = [
    "\033[31m", "\033[32m", "\033[34m",
    "\033[33m", "\033[35m", "\033[36m"
    ]

MENU_TEXT = """
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colors
4. Quit
Choice? (1-4): """

def render(maze: MazeGenerator, color_index: int = 0) -> str:
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

    ex, ey = maze.entry
    xx, xy = maze.exit
    canvas[2 * ey + 1][2 * ex + 1] = f"{WALL_COLOR}EE{RESET}"
    canvas[2 * xy + 1][2 * xx + 1] = f"{WALL_COLOR}XX{RESET}"

    return "\n".join("".join(row) for row in canvas)


def _next_color_index() -> int:
    """スクリプトを起動するたびに前回より1つ進んだ色indexを返す（状態はファイルに保存）"""
    try:
        with open(STATE_FILE) as f:
            index = int(f.read().strip()) + 1
    except (FileNotFoundError, ValueError):
        index = 0
    with open(STATE_FILE, "w") as f:
        f.write(str(index))
    return index


def main() -> None:
    maze = MazeGenerator(width=13, height=15, entry=(0, 0), exit=(11, 14), perfect=True)
    maze.generator()
    color_index = _next_color_index()
    print(render(maze, color_index))


if __name__ == "__main__":
    main()
