# mazegen

グリッド型の迷路生成器です。seedによる再現、Pac-Man的な盤面のための追加ループ、
"42"パターンの埋め込みに対応しています。

## インストール

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## インスタンス化と使い方(Instantiate and use)

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=21, height=20,
    entry=(0, 0), exit=(20, 19),
    perfect=False,   # False: 複数の独立した経路(ループ)を持つ盤面 / True: 一本道
    seed=42,          # 同じseedなら同じ迷路になる(再現性のため)
)
maze.generator()
```

## カスタムパラメータ(Pass custom parameters)

| パラメータ | 型 | 説明 |
|---|---|---|
| `width`, `height` | `int` | 迷路の幅・高さ(セル数)。どちらも正の整数である必要がある |
| `entry`, `exit` | `tuple[int, int]` | 迷路内の入口、出口が異なる`(x, y)`座標 |
| `perfect` | `bool` | `True`ならループの無い一本道の迷路。`False`なら複数の独立した経路を持ち、行き止まりがない盤面（４２ブロック起因除く） |
| `seed` | `int \| None` | `int`で同じ数字を渡すと再現可能な迷路になる。`None`ならランダム |

## 生成された構造とアクセス(Access the generated structure)

```python
# maze._walls: dict[(x, y), int] — bit 1=N, 2=E, 4=S, 8=W (ビットが立っている=壁が閉じている)
for (x, y), bits in maze._walls.items():
    ...

# maze.shortest_path() -> list[(x, y)] | None — 入口から出口までの有効な解の1つ
path = maze.shortest_path()
```

`write_maze_file`が書き出すファイルの形式とは別の説明です。
