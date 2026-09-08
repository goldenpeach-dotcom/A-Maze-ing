"""a_maze_ing - プロトタイプ
visualyzer_stdoutからUI部分を移植
mlxへのDISPRAY分岐はまだ、どのように分岐させるのかUIどうなるのか不明
迷路図
1のre-generateの定義はどうする？単純にmazegen呼び出し？何か変える？

使用方法: 課題例通り
    python3 a_maze_ing.py config.txt
"""

import sys

from mazegen import MazeGenerator
from src import Config, parse_config, ConfigError, render, write_maze_file

MENU_TEXT = """
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colors
4. Quit
Choice? (1-4): """


def build_maze(config: Config) -> MazeGenerator:
    maze = MazeGenerator(
        config.width, config.height,
        config.maze_entry, config.maze_exit,
        config.perfect, config.seed
    )
    maze.generator()
    write_maze_file(
        config.output_file, maze._walls, maze.width, maze.height,
        maze.entry, maze.exit, maze.shortest_path() or []
    )
    return maze


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} config.txt", file=sys.stderr)
        return 1
    try:
        config = parse_config(sys.argv[1])
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    maze = build_maze(config)
    color_index: int = 0
    shortest_path: bool = False
    path = maze.shortest_path()
    while True:
        print(render(maze, color_index, path if shortest_path else None))
        if maze.pattern_omitted_reason:
            print(f"Note: {maze.pattern_omitted_reason}")
        text = input(MENU_TEXT)
        try:
            instruction = int(text)
        except ValueError:
            print("Choose number: 1 2 3 4")
            continue
        if instruction == 1:
            maze = build_maze(config)
            path = maze.shortest_path()
        elif instruction == 2:
            shortest_path = not shortest_path
        elif instruction == 3:
            color_index += 1
        elif instruction == 4:
            break
        else:
            print("Choose number: 1 2 3 4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
