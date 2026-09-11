"""A-Maze-ing のエントリーポイント。

configファイルを読み込み、迷路を生成してファイル出力し、
ターミナルでの表示・操作メニューを提供する。

使用方法:
    python3 a_maze_ing.py config.txt
"""

import sys

from mazegen import MazeGenerator
from src import (
    Config, parse_config, ConfigError,
    render, write_maze_file, FileOutputError
    )

MENU_TEXT = """
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colors
4. Quit
Choice? (1-4): """


def build_maze(config: Config) -> MazeGenerator:
    """configの内容から迷路を1個生成し、ファイルにも書き出す。

    Args:
        config: parse_config()で読み込んだ設定内容。

    Returns:
        生成済みのMazeGeneratorインスタンス。
    """
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


def run_gui(config: Config) -> int:
    """DISPLAY=2のとき、MLXウィンドウで迷路を表示する。

    再生成・経路表示・色変更・終了のメニュー操作は
    MazeRenderer自身がキー入力で受け付ける
    (ターミナルのinput()メニューループとは独立している)。

    Args:
        config: parse_config()で読み込んだ設定内容。

    Returns:
        プロセスの終了コード(正常終了は0、エラー時は1)。
    """
    try:
        from src.visualizer_mlx import MazeRenderer
    except ImportError as e:
        print(
            f"Error: MLX is not available ({e}). "
            "Install mlx (see requirements.txt) or set DISPLAY=1.",
            file=sys.stderr
        )
        return 1

    def make_maze() -> MazeGenerator:
        maze = build_maze(config)
        if maze.pattern_omitted_reason:
            print(f"Note: {maze.pattern_omitted_reason}")
        return maze

    CELL_PIXELS = 24  # 1マスあたりのピクセル数
    win_width = min(1400, max(800, config.width * CELL_PIXELS))
    win_height = min(1000, max(600, config.height * CELL_PIXELS)) + 160
    try:
        renderer = MazeRenderer(
            make_maze, win_width=win_width, win_height=win_height)
        renderer.run()
    except (ValueError, FileOutputError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    """configファイルを読み込み、対話メニューのループを回す。

    Returns:
        プロセスの終了コード(正常終了は0、エラー時は1)。
    """
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} config.txt", file=sys.stderr)
        return 1
    try:
        config = parse_config(sys.argv[1])
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    if config.display == 2:
        return run_gui(config)

    try:
        maze = build_maze(config)
        color_index: int = 0
        shortest_path: bool = False
        path = maze.shortest_path()
    except (ValueError, FileOutputError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    refresh = True
    while True:
        if refresh:
            print(render(maze, color_index, path if shortest_path else None))
            if maze.pattern_omitted_reason:
                print(f"Note: {maze.pattern_omitted_reason}")
            refresh = False
        try:
            text = input(MENU_TEXT)
        except (EOFError):
            print("EOF Quit")
            break
        try:
            instruction = int(text)
        except ValueError:
            print("Choose number: 1 2 3 4")
            continue
        if instruction == 1:
            try:
                maze = build_maze(config)
                path = maze.shortest_path()
                refresh = True
            except (ValueError, FileOutputError) as e:
                print(f"Error: {e}", file=sys.stderr)
        elif instruction == 2:
            shortest_path = not shortest_path
            refresh = True
        elif instruction == 3:
            color_index += 1
            refresh = True
        elif instruction == 4:
            break
        else:
            print("Choose number: 1 2 3 4")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        sys.exit(130)
    except BrokenPipeError:
        sys.exit(1)
