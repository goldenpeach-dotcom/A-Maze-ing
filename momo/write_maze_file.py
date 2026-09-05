import logging

def write_maze_file(filename, walls, width, height, entry, exit_cell, path) -> bool:

    try:
        lines = []

        # ① 壁情報のグリッド(1マス=16進数1文字)
        for y in range(height):
            row = ''.join(format(walls[(x, y)], 'x') for x in range(width))
            lines.append(row)

        lines.append('')  # ② 空行

        # ③ entry / exit
        entry_str = f"{entry[0]},{entry[1]}"
        exit_str = f"{exit_cell[0]},{exit_cell[1]}"
        lines.append(f"{entry_str:<12}# entry  (x,y)")
        lines.append(f"{exit_str:<12}# exit   (x,y)")

        lines.append('')  # 空行

        # ④ 経路を方角の文字列に変換
        dir_letters = {(0, -1): 'N', (1, 0): 'E', (0, 1): 'S', (-1, 0): 'W'}
        path_str = ''.join(
            dir_letters[(b[0] - a[0], b[1] - a[1])]
            for a, b in zip(path, path[1:])
        )
        lines.append(path_str)
    except(KeyError, TypeError) as e:
        logging.error(f"迷路データが不正です： {e}")
        return False

    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(lines) + '\n')
    except OSError as e:
        logging.error(f"Error! {e}")
        return False

    return True