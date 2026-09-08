"""
write_maze_file() のテストコード（unittest版・標準ライブラリのみ）

観点:
  1. 正常系: ファイルが実際に作られ、中身のフォーマットが仕様通りか
  2. 異常系: walls が壁情報のグリッド構築に必要なキーを欠いている場合 (KeyError)
  3. 異常系: path 内の移動が DIRECTIONS に定義されていない場合 (KeyError)
  4. 異常系: 書き込み先が存在しないディレクトリなどで開けない場合 (OSError)
  5. エッジケース: entry と exit が同じセルで path が1要素だけ（移動なし）の場合

実行方法:
    python3 -m unittest test_maze_writer_unittest.py -v
  もしくは
    python3 test_maze_writer_unittest.py
"""
import shutil
import tempfile
import unittest
from pathlib import Path

from maze_writer import write_maze_file


class TestWriteMazeFile(unittest.TestCase):

    def setUp(self):
        # テストごとに一時ディレクトリを作り、そこにファイルを書き出す
        self.tmp_dir = Path(tempfile.mkdtemp())

        self.walls = {
            (0, 0): 15,  # 'f'
            (1, 0): 10,  # 'a'
            (0, 1): 5,   # '5'
            (1, 1): 0,   # '0'
        }
        self.width, self.height = 2, 2
        self.entry = (0, 0)
        self.exit_cell = (1, 1)
        self.path = [(0, 0), (1, 0), (1, 1)]  # E -> S

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_returns_true_and_creates_file(self):
        """正常なデータならTrueを返し、ファイルが実際に作成される"""
        filepath = self.tmp_dir / "output_maze.txt"

        result = write_maze_file(
            str(filepath), self.walls, self.width, self.height,
            self.entry, self.exit_cell, self.path
        )

        self.assertTrue(result)
        self.assertTrue(filepath.exists())

    def test_content_format(self):
        """出力内容が仕様通りの構成（壁グリッド/空行/entry/exit/空行/経路）になっているか"""
        filepath = self.tmp_dir / "output_maze.txt"

        write_maze_file(
            str(filepath), self.walls, self.width, self.height,
            self.entry, self.exit_cell, self.path
        )

        content = filepath.read_text()
        lines = content.split('\n')

        # 末尾は改行で終わっているので split すると最後に空文字列が残る
        self.assertEqual(lines[-1], '')
        lines = lines[:-1]

        expected = [
            'fa',                          # y=0: (0,0)=f, (1,0)=a
            '50',                          # y=1: (0,1)=5, (1,1)=0
            '',
            '0,0         # entry  (x,y)',
            '1,1         # exit   (x,y)',
            '',
            'ES',
        ]
        self.assertEqual(lines, expected)

    def test_missing_wall_cell_returns_false(self):
        """wallsに存在しないセルがあるとKeyErrorを捕捉してFalseを返す"""
        broken_walls = {
            (0, 0): 15,
            (1, 0): 10,
            (0, 1): 5,
            # (1, 1) がわざと欠けている
        }
        filepath = self.tmp_dir / "output_maze.txt"

        result = write_maze_file(
            str(filepath), broken_walls, self.width, self.height,
            self.entry, self.exit_cell, self.path
        )

        self.assertFalse(result)
        self.assertFalse(filepath.exists())  # 失敗時はファイルを作らない

    def test_invalid_path_step_returns_false(self):
        """pathの移動量がDIRECTIONSにない(例:斜め移動)場合はKeyErrorでFalse"""
        bad_path = [(0, 0), (1, 1)]  # 斜め移動
        filepath = self.tmp_dir / "output_maze.txt"

        result = write_maze_file(
            str(filepath), self.walls, self.width, self.height,
            self.entry, self.exit_cell, bad_path
        )

        self.assertFalse(result)
        self.assertFalse(filepath.exists())

    def test_oserror_returns_false(self):
        """存在しないディレクトリへの書き込みなどOSErrorが起きた場合はFalseを返す"""
        bad_filepath = "/no_such_directory_xyz/output_maze.txt"

        result = write_maze_file(
            bad_filepath, self.walls, self.width, self.height,
            self.entry, self.exit_cell, self.path
        )

        self.assertFalse(result)

    def test_no_movement_path(self):
        """entryとexitが同じでpathが1要素(移動なし)の場合、経路の行は空文字列になる"""
        entry = exit_cell = (0, 0)
        path = [(0, 0)]  # 移動なし
        filepath = self.tmp_dir / "output_maze.txt"

        result = write_maze_file(
            str(filepath), self.walls, self.width, self.height,
            entry, exit_cell, path
        )

        self.assertTrue(result)
        lines = filepath.read_text().split('\n')[:-1]
        self.assertEqual(lines[-1], '')  # 経路の行が空文字列


if __name__ == '__main__':
    unittest.main(verbosity=2)
