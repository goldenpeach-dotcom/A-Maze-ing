
from mazegen import E, N, S, W, MazeGenerator


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

    for gy in range(0, grid_h, 2):
        for gx in range(0, grid_w, 2):
            canvas[gy][gx] = f"{WALL_COLOR}██{RESET}"

    for (x, y), walls in maze._walls.items():
        cx, cy = 2 * x + 1, 2 * y + 1
        if (x, y) in maze._42blocked:
            canvas[cy][cx] = "░░"
        if walls & N:
            canvas[cy - 1][cx] = f"{WALL_COLOR}██{RESET}"
        if walls & S:
            canvas[cy + 1][cx] = f"{WALL_COLOR}██{RESET}"
        if walls & W:
            canvas[cy][cx - 1] = f"{WALL_COLOR}██{RESET}"
        if walls & E:
            canvas[cy][cx + 1] = f"{WALL_COLOR}██{RESET}"

    ex, ey = maze.entry
    xx, xy = maze.exit
    canvas[2 * ey + 1][2 * ex + 1] = "EE"
    canvas[2 * xy + 1][2 * xx + 1] = "XX"

    return "\n".join("".join(row) for row in canvas)

    while True:


if __name__ == "__main__":
    maze = MazeGenerator(width=19, height=15, entry=(0, 0), exit=(18, 11), perfect=False)
    maze.generator()
    print(render(maze, color_index=1))
