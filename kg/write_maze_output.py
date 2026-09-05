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


class FileOutputError(Exception):
    """迷路データが不正、またはファイル書き込みに失敗したときに送出される。"""


def write_maze_file(
    filename: str, walls: dict[Cell, int],
    width: int, height: int,
    entry: Cell, exit_cell: Cell, path: list[Cell]
) -> None:

    try:
        lines = []

        # ① 壁情報のグリッド(1マス=16進数1文字)
        for y in range(height):
            row = ''.join(format(walls[(x, y)], 'x') for x in range(width))
            lines.append(row)

        lines.append('')  # ② 空行

        # ③ entry / exit(コメントは付けない、maze_analyzer.pyが読めなくなるため)
        entry_str = f"{entry[0]},{entry[1]}"
        exit_str = f"{exit_cell[0]},{exit_cell[1]}"
        lines.append(entry_str)
        lines.append(exit_str)

        lines.append('')  # 空行

        # ④ 経路を方角の文字列に変換
        LETTER_FOR_BIT = {N: 'N', E: 'E', S: 'S', W: 'W'}
        dir_letters = {
            (dx, dy): LETTER_FOR_BIT[bit] for dx, dy, bit in DIRECTIONS
        }

        path_str = ''.join(
            dir_letters[(b[0] - a[0], b[1] - a[1])]
            for a, b in zip(path, path[1:])
        )
        lines.append(path_str)
    except (KeyError, TypeError) as e:
        raise FileOutputError(f"The maze data is invalid: {e}")

    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(lines) + '\n')
    except OSError as e:
        raise FileOutputError(f"Could not write output file '{filename}': {e}")
