*This project has been created as part of the 42 curriculum by kohira, mkaneko.*

# A-Maze-ing

## Description(概要)

プロジェクトの目的と概要
迷路生成アルゴリズムを実装し、ターミナル(またはMLX)で表示するCLIツール

## Instructions(使い方)

### 必要環境

- Python 3.10以上
- 依存パッケージ: `requirements.txt` を参照

### インストール(install)

```bash
make install
```

### 実行(run)

```bash
make run
# または
python3 a_maze_ing.py config.txt
```

### デバッグ実行(debug)

```bash
make debug
```

### Lint / 型チェック

```bash
make lint
# より厳しいチェック
make lint-strict
```

## Configファイルの構造(Configuration file format)

config.txtの全キーと書式

`WIDTH` `HEIGHT` `ENTRY` `EXIT` `OUTPUT_FILE` `PERFECT` は必須(mandatory)キー、
`SEED` は課題文が例示している追加キー(additional key、任意)です。

```
WIDTH=21          # 迷路の幅(セル数)          [必須/mandatory]
HEIGHT=20         # 迷路の高さ(セル数)        [必須/mandatory]
ENTRY=0,0         # 入口座標(x,y)             [必須/mandatory]
EXIT=20,19        # 出口座標(x,y)             [必須/mandatory]
OUTPUT_FILE=maze.txt                          # [必須/mandatory]
SEED=             # 空なら毎回ランダム、数値を指定すると再現可能  [任意/additional]
PERFECT=false     # true: 完全迷路(ループ無し) / false: Pac-Man的な複数経路の盤面  [必須/mandatory]
```

## 迷路生成アルゴリズム

再帰的バックトラッカーを選択した。
迷路生成のロジックが明確で、シンプルに実装できると考えた。行けるとこまで行く、だめなら戻って探す。
再帰を使うとpythonの回数制限（深さ）を避けるためスタックでリストを使った反復版にした

## 再利用可能な部分について

`mazegen`パッケージのどの部分が再利用可能か、どう使うか。

「Instantiate and use」
maze = MazeGenerator(
    width=21, height=20,
    entry=(0, 0), exit=(20, 19),
    perfect=False,   # False: 複数の独立した経路(ループ)を持つ盤面 / True: 一本道
    seed=42,          # 同じseedなら同じ迷路になる(再現性のため)
)
maze.generator()

「Pass custom parameters」

| パラメータ | 型 | 説明 |

| `width`, `height` | `int` | 迷路の幅・高さ(セル数)。どちらも正の整数である必要がある |<br>
| `entry`, `exit` | `tuple[int, int]` | 迷路内の入口、出口が異なる`(x, y)`座標 |<br>
| `perfect` | `bool` | `True`ならループの無い一本道の迷路。`False`なら複数の独立した経路を持ち、行き止まりがない盤面（４２ブロック起因除く）|<br>
| `seed` | `int \| None` | `int`で同じ数字を渡すと再現可能な迷路になる。`None`ならランダム |

「Access the generated structure」

maze._walls: dict[(x, y), int] — bit 1=N, 2=E, 4=S, 8=W (ビットが立っている=壁が閉じている)
迷路の座標情報と壁情報が入ったdictがマス分生成される

maze.shortest_path() -> list[(x, y)] | None — 入口から出口までの最短経路の1つ
path = maze.shortest_path()

## チームと進め方

### 役割分担

kohira: 全体設計、迷路生成、標準出力
mkaneko: 42壁生成、最短経路、configパース、GUI出力 

### 計画とその変化

課題内容の理解と共有、迷路生成ロジックの理解と決定、共同設計、全体構成の考案
役割分担とコーディング

### うまくいった点・改善できる点

良かった点：役割分担を明確にしたことで責任感とスピードが得られた
改善点：githubの効率的な利用

### 使用したツール

python関連のwebポータルサイトやキュレーションサイト
およびAIをコードの使用方法例と解説・バグの原因調査・ドキュメント作成の補助などに使用した。
翻訳サイト

## Resources(参考資料)

- [\Maxe Algorithms\](https://www.jamisbuck.org/mazes/)
- [\[再帰的バックトラッキングによる迷路生成\]](https://qiita.com/hextomino/items/d0bda1bf3bc62ec60f9c)
- [\[グラフ理論　最短経路\]](https://qiita.com/taka256/items/a023a11efe17ab097433)

### AIの利用について

[TODO: 課題文Chapter VII必須(mandatory)項目。どのタスクに、プロジェクトのどの部分でAIを
使ったかを具体的に書く。例:
「迷路生成アルゴリズム(ランダム化再帰的バックトラッカー、ループ追加、
3x3空き部屋の回避判定)の設計・デバッグについて、Claude Codeとの対話を通じて
段階的に理解しながら実装した。ターミナル表示のANSIエスケープコード周りの
実装補助、エラーハンドリングの網羅的なテスト(境界値・異常系)の洗い出しにも使用した。」
のように、具体的な範囲を明記すること]
