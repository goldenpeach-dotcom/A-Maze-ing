from bfs_momo import bfs
from validate_walls_momo import validate_walls

Cell = tuple[int, int]

def main() -> None:
    maze: dict[Cell, int] = {(0, 0): 11, (0, 1): 10, (0, 2): 12, (0, 3): 9, (0, 4): 12, (1, 0): 9, (1, 1): 14, (1, 2): 5, (1, 3): 5, (1, 4): 5, (2, 0): 1, (2, 1): 12, (2, 2): 5, (2, 3): 7, (2, 4): 5, (3, 0): 5, (3, 1): 5, (3, 2): 5, (3, 3): 9, (3, 4): 4, (4, 0): 7, (4, 1): 3, (4, 2): 2, (4, 3): 6, (4, 4): 7}

    m_entry: Cell = (0, 0)
    m_exit: Cell = (4, 4)
    w: int = 5
    h: int = 5

    res: list[Cell] = bfs(maze, m_entry, m_exit, w, h)
    print(res)
    val: bool = validate_walls(maze, w, h)
    print(val)

if __name__=="__main__":
    main()