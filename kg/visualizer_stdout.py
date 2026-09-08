
import os
from mazegen import E, N, S, W, MazeGenerator, Cell
import config_parse
from config_parse import ConfigError


STATE_FILE = os.path.join(os.path.dirname(__file__), ".color_state")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.txt")

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


class VisualizeError(Exception):
    pass


def render(
    maze: MazeGenerator, color_index: int = 0,
    path: list[Cell] | None = None
) -> str:
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
    canvas[2 * ey + 1][2 * ex + 1] = f"{WALL_COLOR}EE{RESET}"
    canvas[2 * xy + 1][2 * xx + 1] = f"{WALL_COLOR}XX{RESET}"

    return "\n".join("".join(row) for row in canvas)


def main() -> None:
    try:
        config = config_parse.parse_config(CONFIG_FILE)
        maze = MazeGenerator(
            config.width, config.height,
            config.maze_entry, config.maze_exit,
            config.perfect, config.seed
        )
    except ConfigError as e:
        print(f"{e}")
        return
    color_index: int = 0
    shortest_path: bool = False
    maze.generator()
    path = maze.shortest_path()
    while True:
        if shortest_path and path is not None:
            print(render(maze, color_index, path))
        else:
            print(render(maze, color_index,))
        text = input(MENU_TEXT)
        try:
            instruction = int(text)
            if instruction == 1:
                maze = MazeGenerator(
                    config.width, config.height,
                    config.maze_entry, config.maze_exit,
                    config.perfect, config.seed
                    )
                maze.generator()
                path = maze.shortest_path()
            elif instruction == 2:
                shortest_path = not shortest_path
            elif instruction == 3:
                color_index += 1
            elif instruction == 4:
                exit()
            else:
                print("Choose number: 1 2 3 4")
        except ValueError:
            print("Choose number: 1 2 3 4")


if __name__ == "__main__":
    main()
