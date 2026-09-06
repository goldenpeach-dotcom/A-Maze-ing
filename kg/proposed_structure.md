
## 最終的に以下の構成にしようと思いますが、ご意見おねがいします！
venv前提です
```構成案
未├── Makefile
未├── README.md
未├── LICENCE.md              # 再利用・再配布を明示的に許可する内容
未├── a_maze_ing.py           # 全体の統括（エントリーポイント）
未├── config.txt
未├── requirements.txt        # 依存ライブラリ（mlx, mypy, flake8等
未├── mazegen/                # 【再利用可能なパッケージ】
未│   ├── __init__.py
未│   ├── pyproject.toml      # buildに必要な全要素（pipインストール用設定ファイル）
着│   ├── make_42_wall.py     # 迷路用42ブロック制作
着│   └── mazegen.py       　 # MazeGeneratorクラス（ロジック担当）名前重複、変える？
未└── src/                    # 【補助コード】
未    ├── __init__.py
着    ├── config_check.py     # 設定ファイルの読み込み担当
未    ├── visualizer_mlx.py   # 対応したい、GUI描画とユーザー入力監視（MLX）課題添付mlx使う
着    ├── visualizer_stdout.py # ターミナル表示担当
着    └── file_output.py      # 16進数形式でのファイル書き出し担当
```