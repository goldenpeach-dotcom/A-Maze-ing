import pytest
from config import Config, parse_config, read_config_file
from pathlib import Path


def write_config(tmp_path: Path, content: str) -> str:
    """設定ファイルを一時ディレクトリに書き出してパスを返すヘルパー"""

    file_path = tmp_path / "config.txt"
    file_path.write_text(content)
    return str(file_path)


VALID_CONFIG = """\
WIDTH=10
HEIGHT=10
ENTRY=0,0
EXIT=9,9
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
"""


def test_valid_config_returns_config(tmp_path: Path) -> None:
    path = write_config(tmp_path, VALID_CONFIG)
    config = parse_config(path)

    assert config == Config(
        width=10,
        height=10,
        maze_entry=(0, 0),
        maze_exit=(9, 9),
        output_file="maze.txt",
        perfect=True,
        seed=42,
    )


def test_seed_is_optional(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("SEED=42\n", "")
    path = write_config(tmp_path, content)
    config = parse_config(path)
    assert config.seed is None


def test_invalid_seed_raises(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("SEED=42", "SEED=not_a_number")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="SEED must be an integer"):
        parse_config(path)


def test_missing_key_raises(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("OUTPUT_FILE=maze.txt\n", "")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="Missing mandatory keys"):
        parse_config(path)

def test_invalid_width(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("WIDTH=10", "WIDTH=-10")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="WIDTH and HEIGHT must be greater than 1."):
        parse_config(path)

def test_invalid_height(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("HEIGHT=10", "HEIGHT=-10")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="WIDTH and HEIGHT must be greater than 1."):
        parse_config(path) 

@pytest.mark.parametrize("bad_value", ["abc", "3.5"])
def test_invalid_width_raises(tmp_path: Path, bad_value: str) -> None:
    content: str = VALID_CONFIG.replace("WIDTH=10", f"WIDTH={bad_value}")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="WIDTH and HEIGHT must be valid integers"):
        parse_config(path)


def test_width_too_small_raises(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("WIDTH=10", "WIDTH=1")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="greater than 1"):
        parse_config(path)


def test_entry_bad_format_raises(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("ENTRY=0,0", "ENTRY=0-0")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="ENTRY and EXIT must be formated"):
        parse_config(path)


def test_entry_out_of_bounds_raises(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("ENTRY=0,0", "ENTRY=99,99")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="ENTRY coordinates is out of grid bounds"):
        parse_config(path)


def test_entry_equals_exit_raises(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("EXIT=9,9", "EXIT=0,0")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="cannot be identical"):
        parse_config(path)


def test_invalid_perfect_raises(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("PERFECT=True", "PERFECT=maybe")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="Perfect must be True or False"):
        parse_config(path)


def test_empty_output_file_raises(tmp_path: Path) -> None:
    content = VALID_CONFIG.replace("OUTPUT_FILE=maze.txt", "OUTPUT_FILE=")
    path = write_config(tmp_path, content)
    with pytest.raises(ValueError, match="OUTPUT_FILE cannot be empty"):
        parse_config(path)

def test_read_config_file_ignores_comments(tmp_path: Path) -> None:
    content = """\
# これはコメント
WIDTH=10
# もう一つコメント
HEIGHT=10
"""
    file_path = tmp_path / "config.txt"
    file_path.write_text(content)

    result = read_config_file(str(file_path))

    assert result == {"WIDTH": "10", "HEIGHT": "10"}