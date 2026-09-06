import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))

target_dir = os.path.join(current_dir, "..", "kg")

sys.path.append(os.path.normpath(target_dir))

import mazegen
import config_parse
import write_maze_file

def main() -> None:
    config = config_parse.read_config_file("config.txt")
    maze = mazegen.MazeGenerator(config.width, config.height, config.maze_entry, config.maze_exit, config.perfect)
    maze.generator()
    path_list: list[mazegen.Cell] = maze.shortest_path()
    finished = write_maze_file(config.filename, maze.walls,
        config.width, config.height,
        config.maze_entry, config.maze_exit, path_list)
    


    

if __name__=="__main__":
    main()