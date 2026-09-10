*This project has been created as part of the 42 curriculum by kohira, mkaneko.*

# A-Maze-ing

## Description(概要)

プロジェクトの目的と概要
迷路生成アルゴリズムを実装し、ターミナル(またはMLX)で表示するCLIツールの作成。
迷路生成のモジュールを単一のクラスで実装し、属性を更新することによってクラスにアクセスして値を渡す方法をとっている。
モジュール全体（コードとドキュメント）は、単一のファイルにまとめておき、pipでインストールできるようにした。
モジュールを再利用できる形にする方法と、ソフトウェアライセンスや知的財産権について初めて学ぶ機会となった。

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
`SEED` `DISPLAY` は課題文が例示している追加キー(additional key、任意)です。

```
WIDTH=21
HEIGHT=20
ENTRY=0,0
EXIT=20,19
OUTPUT_FILE=maze.txt
SEED=
PERFECT=false
DISPLAY=1
```

| キー | 説明 | 区分 |
|---|---|---|
| `WIDTH` | 迷路の幅(セル数) | 必須/mandatory |
| `HEIGHT` | 迷路の高さ(セル数) | 必須/mandatory |
| `ENTRY` | 入口座標(x,y) | 必須/mandatory |
| `EXIT` | 出口座標(x,y) | 必須/mandatory |
| `OUTPUT_FILE` | 出力ファイル名 | 必須/mandatory |
| `SEED` | 空なら毎回ランダム、数値を指定すると再現可能 | 任意/additional |
| `PERFECT` | true: 完全迷路(ループ無し) / false: Pac-Man的な複数経路の盤面 | 必須/mandatory |
| `DISPLAY` | 1: ターミナル表示 / 2: MLX(GUI)表示。省略時は1 | 任意/additional |

コメントは行頭が`#`の行のみ対応(値の後ろに続けて書くインラインコメントには対応していないので、
上記のように別行にすること)。

### `DISPLAY=2`(MLX/GUI表示)を使うための準備

`mlx`パッケージはPyPIには無いため、`requirements.txt`とは別に手動でインストールする必要がある。
`mlx_parts/`フォルダに、使っているOS(Linuxディストリビューション)ごとのビルド済みwheelが入っている。

```bash
# Ubuntuの場合
pip install mlx_parts/ubuntu/mlx-2.2-py3-none-any.whl
# Fedoraの場合
pip install mlx_parts/fedora/mlx-2.2-py3-none-any.whl
```

インストール確認:

```bash
python3 -c "import mlx; print(mlx.__file__)"
```

これが通れば、`config.txt`で`DISPLAY=2`にしてから`make run`(または`python3 a_maze_ing.py config.txt`)を
実行するとMLXウィンドウが開く。


### 画面操作
ターミナル表示のときのメニュー表示
1. Re-generate a new maze　（迷路の再生成）
2. Show / Hide the shortest path　（経路の表示・非表示）
3. Rotate the wall colors　（色の変更）
4. Quit　（終了）
Choice? (1-4): 

ウィンドウ表示のとき。
1. Regenerate maze
2. Toggle shortest path animation
3. Change color palette
4. Quit　（ESCキー押下か✖ボタンクリックでも終了する）



## 迷路生成アルゴリズム

再帰的バックトラッカーを選択した。
迷路生成のロジックが明確で、シンプルに実装できると考えた。行けるとこまで行く、だめなら戻って探す。
再帰を使うとpythonの回数制限（深さ）を避けるためスタックでリストを使った反復版にした

## 経路探索アルゴリズム

BFS（幅優先探索）を選択。

この迷路では、隣接するマス同士の移動コストはすべて等しい（重みなし）。そのため、スタートから近い順に探索していくBFSを使えば、ゴールに到達した時点でそれが自動的に最短経路になる。

使用するデータ構造

| 変数 |役割|
|---|---|
|'queue'|	次に探索する候補地点を先入先出（FIFO）で保持|
|'visited'|	探索済みの地点の集合（二重登録防止）|
|'came_from'|	各地点に「どこから来たか」を記録。ゴールから逆にたどって経路を復元するために使う|

手順
1. queueにスタート地点(entry)を入れ、visitedにも登録する。
2. queueが空でない間、以下を繰り返す。
3. queueの先頭を取り出しcurrentとする（FIFO）。
4. currentがゴール(exit)なら探索終了。
5. そうでなければ、currentから壁のない方向に隣接するマスのうち、まだvisitedに入っていないものをqueueに追加し、visitedに登録、came_fromにも「どこから来たか」を記録する。
6. ゴールに到達せずqueueが空になった場合は経路なし（None）を返す。
7. ゴールに到達した場合、current（＝exit）からcame_fromを逆にたどりながらリストに追加していき、スタート地点(entry)に着いたら終了。できたリストを逆順にすると、それが最短経路になる。


## 再利用可能な部分について

`mazegen`パッケージの再利用可能性

入出力(ファイル・GUI・mlx表示)から切り離されており、
引数がシンプルでまとまっていることから、他のプロジェクトに持っていってもそのまま使える。
generator() と shortest_path() が独立したメソッドとして分離されていて、
「迷路を作る」と「経路を探す」が別メソッドなので、
「迷路生成だけ使いたい(経路探索は要らない)」というケースでも一部だけ再利用できます。


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


### 経路のアニメーションについて

迷路の壁は初回に一括表示する。一方、経路はmlx_loop_hookで登録した_on_loop関数の中で1マスずつ描画することで経路が伸びていくアニメーションを実現している。

- _on_loopの処理内容
1. フレーム間隔の調整：_loop_countでカウントし、１０フレーム（0.1～0.2秒）ごとに一回だけ処理を進める。MiniLibXのループはそのままだと高速に回りすぎるため、人の目に見える速さに落としている。
2. 迷路の初回描画:_initialized_rendrerフラグを見て、まだ描画していなければ_render_maze()を一度だけ呼び、迷路の壁を描画する。
3. 経路の描画:show_pathが有効な場合、探索済みの経路座標リストからsearch_indexが指す１マスだけを_draw_serach_cellで描画し、search_indexをインクリメントする。全描画マス済み以降は、毎回全経路を描画しなおして表示を維持する。
4. 画面更新:mlx_clear_windowでクリアした後、画像バッファ(img_ptr)をmlx_put_image_to_windowでウィンドウに転送し、_draw_menu()ｓｗメニュー帯を描画する。

プロジェクトページにあるMiniLibx(mlx)をインポートして利用した。
Mlx()のインスタンスを作りmlx_init()を実行すると、様々なmlx_*関数を呼ぶことができる。
mlx_loop関数を用いると入力待ち状態となる。
キー入力に応じて、迷路の再生成や経路の表示、色の切り替えをできるようにした。

```Python
import mlx
m = mlx.Mlx()
mlx_ptr = m.mlx_init() <- 最初に一度実行する。
win_ptr = m.mlx_new_window(mlx_ptr, 800, 600)　<- 画像オブジェクトのポインタを返す
```

描画に必要な関数

　mlx_init() 初期化に必要

　mlx_new_image() 画像オブジェクトのポインタを返す

　mlx_get_data_addr()　画像の生ピクセルデータの先頭アドレスを返す

　mlx_put_image_to_window() 作った画像をウィンドウに一括で貼り付ける

　mlx_destroy_image()作った画像を破棄

キー操作や画面を閉じるのに必要な関数（コールバック関数を登録するための関数）

　mlx_key_hook()キーボードのキーが押されたときに呼ばれる関数を登録

　mlx_hook()様々なイベント番号を直接指定してそのイベントが発生したときに呼ばれる関数を登録

　mlx_loop_hook()ループが一周するたびに繰り返し呼ばれる関数を登録

　mlx_loop_exit()

　mlx_loop() イベントループ本体を開始する。

そのほかの関数については、
```
pip3 show -f mlx  # インストール場所とファイル一覧を確認
Pythonラッパーのソースコードを読む
```


## チームと進め方

### 役割分担

kohira: 全体設計、迷路生成、標準出力、パッケージ、Makefile、LICENCEの作成
mkaneko: 42壁生成、最短経路、configパース、GUI出力 

### 計画とその変化

課題内容の理解と共有
　
迷路生成ロジックの理解と決定
　
共同設計、全体構成の考案
　
役割分担とコーディング

### うまくいった点・改善できる点

良かった点：役割分担を明確にしたことで責任感とスピードが得られた。受け渡すデータの構成を先に話し合って決めたこと。
改善点：githubの効率的な利用

### 使用したツール

python関連のwebポータルサイトやキュレーションサイト
およびAIをコードの使用方法例と解説・バグの原因調査・ドキュメント作成の補助などに使用した。
翻訳サイト


## Resources(参考資料)

- [\Maxe Algorithms\](https://www.jamisbuck.org/mazes/)
- [\[再帰的バックトラッキングによる迷路生成\]](https://qiita.com/hextomino/items/d0bda1bf3bc62ec60f9c)
- [\[グラフ理論　最短経路\]](https://qiita.com/taka256/items/a023a11efe17ab097433)
- [\[BFS 幅優先検索\]](https://qiita.com/drken/items/996d80bcae64649a6580)

### AIの利用について

kohira
迷路生成アルゴリズム(ランダム化再帰的バックトラッカー、ループ追加、
3x3空き部屋の回避判定)の設計・デバッグについて、Claude Codeとの対話を通じて
段階的に理解しながら実装した。ターミナル表示のANSIエスケープコード周りの
実装補助、エラーハンドリングの網羅的なテスト(境界値・異常系)の洗い出しにも使用した。

mkaneko
経路探索実装方法調査やconfig.txtのパーサーのテストケース作成、デバッグの補助、
GUI描画で、画面表示の微調整の補助にclaude, copilotを利用した。
