import sys
from dataclasses import dataclass

#: A maze bigger than this is impractical to render or hold in memory.
MAX_DIMENSION = 1000
QUOTE_CHARS = {'"', "'"}


class ConfigError(ValueError):
    """Raised when the config file is missing, malformed, or invalid."""


@dataclass
class Config:
    """ Contents of the settings file

    attributes: width, height, coordinates of entrance & exit
    output_file name, maze_mode, number to recreate the same maze
    """

    width: int
    height: int
    maze_entry: tuple[int, int]
    maze_exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def read_config_file(file_name: str) -> dict[str, str]:
    """Read the file(config.txt)

    parameter: configuration file name
    return: A dictionary of basic maze information
    """

    raw_data: dict[str, str] = {}

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            for line_num, raw_line in enumerate(file, start=1):
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ConfigError(
                        f"Syntax error on line {line_num}: "
                        f"missing '=' in {raw_line.strip()!r}"
                    )

                key, value = line.split("=", 1)
                raw_data[key.strip()] = value.strip()
    except OSError as e:
        raise ConfigError(f"Could not read config file. '{file_name}': {e}")
    except ValueError as e:
        raise ConfigError(f"Invalid config file '{file_name}': {e}")

    return raw_data


def parse_config(file_name: str) -> Config:
    """ Configuration file parser """

    raw_data = read_config_file(file_name)

    seed = None
    if "SEED" in raw_data and raw_data["SEED"]:
        try:
            seed = int(raw_data["SEED"])
        except ValueError:
            raise ConfigError(
                f"SEED must be an integer, got {raw_data['SEED']!r}"
            )

    required_keys = {
                     "WIDTH",
                     "HEIGHT",
                     "ENTRY",
                     "EXIT",
                     "OUTPUT_FILE",
                     "PERFECT"
    }

    missing_keys = required_keys - raw_data.keys()
    if missing_keys:
        raise ConfigError(
            f"Missing mandatory key(s): {missing_keys}"
        )

    try:
        width = int(raw_data["WIDTH"])
        height = int(raw_data["HEIGHT"])
    except ValueError:
        raise ConfigError("WIDTH and HEIGHT must be valid integers.")

    if width < 1 or height < 1:
        raise ConfigError("WIDTH and HEIGHT must be positive integers.")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ConfigError(
            f"WIDTH and HEIGHT must not exceed {MAX_DIMENSION}."
        )
    if width * height < 2:
        raise ConfigError(
            "The maze needs at least 2 cells (WIDTH * HEIGHT >= 2)."
        )

    m_entry = raw_data["ENTRY"]
    m_exit = raw_data["EXIT"]

    try:
        x_entry, y_entry = m_entry.split(",")
        x_exit, y_exit = m_exit.split(",")
    except ValueError:
        raise ConfigError("ENTRY and EXIT must be formated as x, y")

    try:
        maze_entry: tuple[int, int] = (int(x_entry), int(y_entry))
        maze_exit: tuple[int, int] = (int(x_exit), int(y_exit))
    except ValueError:
        raise ConfigError("ENTRY and EXIT must be a positive integer")

    if not (0 <= maze_entry[0] < width and 0 <= maze_entry[1] < height):
        raise ConfigError(
            f"ENTRY {maze_entry} is outside the {width}x{height} grid."
        )
    if not (0 <= maze_exit[0] < width and 0 <= maze_exit[1] < height):
        raise ConfigError(
            f"EXIT {maze_exit} is outside the {width}x{height} grid."
        )

    if maze_entry == maze_exit:
        raise ConfigError("ENTRY and EXIT must be different cells.")

    perfect_raw = raw_data["PERFECT"].lower()
    if perfect_raw not in ("true", "false"):
        raise ConfigError(
            f"PERFECT must be True or False, got {raw_data['PERFECT']!r}"
        )
    perfect = perfect_raw == "true"

    output_file = raw_data["OUTPUT_FILE"].strip()
    if not output_file:
        raise ConfigError("OUTPUT_FILE cannot be empty")
    if QUOTE_CHARS & set(output_file):
        raise ConfigError(
            f"OUTPUT_FILE must not contain quote characters, "
            f"got {output_file!r}"
        )

    return Config(
        width=width,
        height=height,
        maze_entry=maze_entry,
        maze_exit=maze_exit,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )


def main() -> None:
    """ test """
    try:
        result = read_config_file("config.txt")
        print(result)
        config = parse_config("config.txt")
        print(config)
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
