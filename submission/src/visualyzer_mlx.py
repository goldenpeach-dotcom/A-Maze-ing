"""
A-Maze-ing: mlx (ctypes版 MiniLibX) を使った迷路描画モジュール

迷路データの形式:
    maze: dict[(x, y)] = mask
    mask はビットマスク (0〜15)
        bit0 (1)  = N (上に壁)
        bit1 (2)  = E (右に壁)
        bit2 (4)  = S (下に壁)
        bit3 (8)  = W (左に壁)

メニュー(下部帯、数字キーで操作):
    1: 迷路の再生成
    2: 最短経路アニメーションの表示/非表示トグル
    3: 壁の色を変える
    4: 終了

"""
import sys

from typing import Any, Callable, Literal

from mlx import Mlx

sys.argv = [sys.argv[0]]
Cell = tuple[int, int]
Palette = dict[str, int]
DataView = Any

N, E, S, W = 1, 2, 4, 8
ALL_WALLS = N | E | S | W  # 4方向とも壁 = "42"の文字を構成するセル

BG_COLOR = 0xFF000000     # 黒
WALL_THICKNESS = 3        # 壁の線の太さ(px)

# 壁色・経路色・42マーク色を1セットにしたパレット。3キーでセットごと切替
PALETTES: list[Palette] = [
    {"wall": 0xFFFFFFFF, "path": 0xFFF7A0AD, "mark": 0xFFB1E5E6,
     "entry": 0xFFF29191, "exit": 0xFFFF3D6E},
    {"wall": 0xFF2A835F, "path": 0xFF8BBB92, "mark": 0xFF12544F,
     "entry": 0xFF092328, "exit": 0xFFFFD25C},
    {"wall": 0xFFD9EFBD, "path": 0xFFF5FBDA, "mark": 0xFF450C3F,
     "entry": 0xFFD9EFBD, "exit": 0xFFFF5CC1},
    {"wall": 0xFF95CCDD, "path": 0xFF4274D9, "mark": 0xFFD0E7E6,
     "entry": 0xFF293681, "exit": 0xFFFF5C5C},
]

MENU_HEIGHT = 100
MENU_LINES = [
    "1: Regenerate maze",
    "2: Toggle shortest path animation",
    "3: Change color palette",
    "4: Quit",
]
LINE_HEIGHT = 20
PADDING = 16

ESC_KEY = 65307
KEY_1, KEY_2, KEY_3, KEY_4 = 49, 50, 51, 52


# --------------------------------------------------------------------------- #
# 生の画像バッファへの描画ヘルパー
# --------------------------------------------------------------------------- #
def put_pixel(
        data_view: DataView, size_line: int, bpp: int, x: int, y: int,
        color: int, endian: int
        ) -> None:
    """
        整数で表されたcolorを４バイトのバイト列に変換し、
        画像データを画面(x, y)の位置に画面表示する。
        Args：
            data_view 画像の生ピクセルデータ全体
            size_line　１行あたりのバイト数
            bpp　１ピクセルあたりの色情報を何ビットで表現するか
            x, y　書き込み先の座標
            color　色のコードを整数で表したもの
            endian　エンディアン情報（整数をバイト列に分解するとき、どちらの端から
            　　　　並べるか
    """

    offset = y * size_line + x * (bpp // 8)
    byteorder: Literal['little', 'big'] = 'little' if endian == 0 else 'big'
    color_bytes = color.to_bytes(4, byteorder=byteorder)
    data_view[offset:offset + bpp // 8] = color_bytes


def draw_hline(
        data_view: DataView, size_line: int, bpp: int,
        x: int, y: int, length: int, color: int, endian: int
        ) -> None:

    """
        横線を描く
        Args：
            data_view 画像の生ピクセルデータ全体
            size_line　１行あたりのバイト数
            bpp　１ピクセルあたりの色情報を何ビットで表現するか
            x, y　書き始めの座標
            length 線の長さ
            color　色のコードを整数で表したもの
            endian　エンディアン情報（整数をバイト列に分解するとき、どちらの端から
                        　　　　並べるか
    """

    for i in range(length):
        put_pixel(data_view, size_line, bpp, x + i, y, color, endian)


def draw_vline(
        data_view: DataView, size_line: int, bpp: int,
        x: int, y: int, length: int, color: int, endian: int
        ) -> None:

    """
        縦線を描く
        Args：
            data_view 画像の生ピクセルデータ全体
            size_line　１行あたりのバイト数
            bpp　１ピクセルあたりの色情報を何ビットで表現するか
            x, y　書き始めの座標
            length 線の長さ
            color　色のコードを整数で表したもの
            endian　エンディアン情報（整数をバイト列に分解するとき、どちらの端から
                        　　　　並べるか
    """
    for i in range(length):
        put_pixel(data_view, size_line, bpp, x, y + i, color, endian)


def fill_rect(
        data_view: DataView, size_line: int, bpp: int,
        x: int, y: int, width: int, height: int, color: int, endian: int
        ) -> None:

    """
        示された範囲を塗りつぶす
        Args：
            data_view 画像の生ピクセルデータ全体
            size_line　１行あたりのバイト数
            bpp　１ピクセルあたりの色情報を何ビットで表現するか
            x, y　書き始めの座標
            width 塗りつぶす幅
            height 塗りつぶす高さ
            color　色のコードを整数で表したもの
            endian　エンディアン情報（整数をバイト列に分解するとき、どちらの端から
                            　　　　並べるか
    """
    for row in range(height):
        draw_hline(data_view, size_line, bpp, x, y + row, width, color, endian)


def fill_all(
        data_view: DataView, size_line: int, bpp: int,
        width: int, height: int, color: int, endian: int
        ) -> None:

    """
        画面すべてを塗りつぶす（背景用）
        Args：
            data_view 画像の生ピクセルデータ全体
            size_line　１行あたりのバイト数
            bpp　１ピクセルあたりの色情報を何ビットで表現するか
            x, y　書き始めの座標
            width 塗りつぶす幅
            height 塗りつぶす高さ
            color　色のコードを整数で表したもの
            endian　エンディアン情報
    """
    for y in range(height):
        draw_hline(data_view, size_line, bpp, 0, y, width, color, endian)


def draw_cell_walls(
        data_view: DataView, size_line: int, bpp: int,
        cell_w: int, cell_h: int, x: int, y: int, mask: int,
        color: int, endian: int, thickness: int, max_x: int,
        max_y: int
        ) -> None:

    """
        壁の部分を塗る
        Args：
            data_view 画像の生ピクセルデータ全体
            size_line　１行あたりのバイト数
            bpp　１ピクセルあたりの色情報を何ビットで表現するか
            cell_x, cell_y セルの位置
            x, y　書き始めの座標
            mask 壁の情報を見るビットマスク
            color　色のコードを整数で表したもの
            endian　エンディアン情報（整数をバイト列に分解するとき、どちらの端から
                            　　　　並べるか
            thickness線の太さ
            max_x, max_y 線が画面をはみ出さないように境界値

    """

    px, py = x, y
    x_end = px + cell_w - 1
    y_end = py + cell_h - 1
    half = thickness // 2

    def h_at(cy: int, length: int, start_x: int) -> None:
        """
            曲がり角で隙間ができないよう、両端をthickness // 2ずつ延長する
            Args：
                cy　線の中心（基準）となるY座標
                length　線本来の長さ
                start_x 線の本来の開始x座標
        """
        ext_start = max(0, start_x - half)
        ext_end = min(max_x, start_x + length - 1 + half)
        ext_length = ext_end - ext_start + 1
        for t in range(thickness):
            yy = cy - half + t
            if 0 <= yy <= max_y:
                draw_hline(data_view, size_line, bpp, ext_start, yy,
                           ext_length, color, endian)

    def v_at(cx: int, length: int, start_y: int) -> None:
        """
            曲がり角で隙間ができないよう、両端をthickness // 2ずつ延長する
            Args:
                cx　線の中心（基準）となるx座標
                length　線本来の長さ
                start_y 線の本来の開始y座標
        """
        ext_start = max(0, start_y - half)
        ext_end = min(max_y, start_y + length - 1 + half)
        ext_length = ext_end - ext_start + 1
        for t in range(thickness):
            xx = cx - half + t
            if 0 <= xx <= max_x:
                draw_vline(data_view, size_line, bpp, xx, ext_start,
                           ext_length, color, endian)

    if mask & N:
        h_at(py, cell_w, px)
    if mask & E:
        v_at(x_end, cell_h, py)
    if mask & S:
        h_at(y_end, cell_w, px)
    if mask & W:
        v_at(px, cell_h, py)


def _distribute(total: int, count: int) -> list[int]:
    """
        totalピクセルをcount個の区画に分配する。割り切れないあまりは
        先頭の区画から1pxずつ足していく(結果、合計は必ずtotalぴったりになる)。
        迷路の再生成で利用

        Args：
            total 画面の幅
            count 分配する区画数

        Returns：
            各セルに割り当てられた長さのリスト
    """
    base, remainder = divmod(total, count)
    return [base + 1 if i < remainder else base for i in range(count)]


def _prefix_sums(sizes: list[int]) -> list[int]:
    """
        [w0, w1, w2] -> [0, w0, w0+w1, w0+w1+w2] のような累積開始位置。
        _distrebuteで配分するために迷路の幅や高さが均等ではないため、
        ○番目のセルは左端から何ピクセル目にあるかを予め計算する。
        Args：
            sizes セルの大きさのリスト
        Returns：
            左端から何ピクセル目にあるかの位置を示すリスト

    """
    result = [0]
    for size in sizes:
        result.append(result[-1] + size)
    return result


# --------------------------------------------------------------------------- #
# 本体
# --------------------------------------------------------------------------- #
class MazeRenderer:
    def __init__(
            self, maze_gen_factory: Callable[[], Any],
            win_width: int = 800, win_height: int = 600,
            title: str = "A-Maze-ing"
            ) -> None:
        """
            迷路を画面に描画するためのクラス

            maze_gen_factory: 呼び出すたびに新しい MazeGenerator インスタンスを
                作って generator() 済みで返す関数。再生成(メニュー1)のときに
                もう一度呼び出す。
        """
        self.maze_gen_factory = maze_gen_factory
        self.win_width = win_width
        self.win_height = win_height
        self.title = title

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()

        if not self.mlx_ptr:
            raise RuntimeError("Failed to initialize MLX")
        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr, win_width, win_height, title
        )

        if not self.win_ptr:
            raise RuntimeError("Failed to create MLX window")

        self._callbacks: list[Callable[..., int]] = []
        self.palette_index = 0
        self.show_path = False
        self.search_path: list[Cell] = []
        self.search_index = 0

        self.img_ptr = None
        self.data_view = None
        self.bpp = 0
        self.size_line = 0
        self.endian = 0
        self._loop_count = 0
        self._initialized_render = False
        self.maze: dict[Cell, int] = {}
        self.maze_w = 0
        self.maze_h = 0
        self.entry: Cell = (0, 0)
        self.exit: Cell = (0, 0)
        self.col_widths: list[int] = []
        self.row_heights: list[int] = []
        self.col_x: list[int] = []
        self.row_y: list[int] = []
        self.maze_pixel_w = 0
        self.maze_pixel_h = 0
        self._load_new_maze()

    def _load_new_maze(self) -> None:
        """
            迷路の再生成
        """
        mg = self.maze_gen_factory()
        self.maze = mg._walls
        self.maze_w = mg.width
        self.maze_h = mg.height
        self.entry = mg.entry
        self.exit = mg.exit
        self.search_path = mg.shortest_path()
        self.search_index = 0
        self.show_path = False

        maze_area_h = self.win_height - MENU_HEIGHT
        self.col_widths = _distribute(self.win_width, self.maze_w)
        self.row_heights = _distribute(maze_area_h, self.maze_h)
        self.col_x = _prefix_sums(self.col_widths)
        self.row_y = _prefix_sums(self.row_heights)
        self.maze_pixel_w = self.col_x[-1]
        self.maze_pixel_h = self.row_y[-1]

        # 迷路+メニュー全体を含む1枚の画像バッファを作り直す
        # (古いバッファが残っていれば先に解放してリークを防ぐ)
        if self.img_ptr is not None:
            self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.img_ptr = self.mlx.mlx_new_image(
            self.mlx_ptr, self.win_width, self.win_height
        )
        if not self.img_ptr:
            raise RuntimeError("Failed to create MLX image")
        self.data_view, self.bpp, self.size_line, self.endian = \
            self.mlx.mlx_get_data_addr(self.img_ptr)

    # -- 描画 ------------------------------------------------------------- #
    def _palette(self) -> Palette:
        """
        色の情報を返す
        """
        return PALETTES[self.palette_index]

    def _render_maze(self) -> None:
        """
            背景と壁と４２のセルと出発点と到達点を塗る
        """
        fill_all(
            self.data_view, self.size_line, self.bpp,
            self.win_width, self.win_height, BG_COLOR, self.endian
        )
        palette = self._palette()
        max_x = self.maze_pixel_w - 1
        max_y = self.maze_pixel_h - 1
        for (x, y), mask in self.maze.items():
            px, py = self.col_x[x], self.row_y[y]
            cw, ch = self.col_widths[x], self.row_heights[y]
            if mask == ALL_WALLS:
                # "42"の文字を構成するセルは丸ごと専用の色で塗る
                fill_rect(self.data_view, self.size_line, self.bpp,
                          px, py, cw, ch,
                          palette["mark"], self.endian)
                continue
            draw_cell_walls(
                self.data_view, self.size_line, self.bpp,
                cw, ch, px, py, mask,
                palette["wall"], self.endian, WALL_THICKNESS, max_x, max_y
            )

        self._fill_marker_cell(self.entry, palette["entry"])
        self._fill_marker_cell(self.exit, palette["exit"])

    def _fill_marker_cell(self, cell: Cell, color: int) -> None:
        """
            出発点と到達点を塗る
            Args：
                cell セルの座標
                color 整数の色番号
        """
        x, y = cell
        px, py = self.col_x[x], self.row_y[y]
        cw, ch = self.col_widths[x], self.row_heights[y]
        margin_w = max(1, cw // 4)
        margin_h = max(1, ch // 4)
        fill_rect(
            self.data_view, self.size_line, self.bpp,
            px + margin_w, py + margin_h,
            cw - 2 * margin_w, ch - 2 * margin_h,
            color, self.endian
        )

    def _draw_search_cell(self, x: int, y: int) -> None:
        """
            経路を１セル描画する
            Args：
                x,y 描画する座標
        """
        self._fill_marker_cell((x, y), self._palette()["path"])

    def _render_and_present(self) -> None:
        """【変更】迷路を画像に描き、ウィンドウに表示し、文字を乗せる一連の処理"""

        # 1. 画像バッファへの描画
        palette = self._palette()
        fill_all(
            self.data_view, self.size_line, self.bpp,
            self.win_width, self.win_height, BG_COLOR, self.endian
        )
        palette = self._palette()
        max_x = self.maze_pixel_w - 1
        max_y = self.maze_pixel_h - 1
        for (x, y), mask in self.maze.items():
            px, py = self.col_x[x], self.row_y[y]
            cw, ch = self.col_widths[x], self.row_heights[y]
            if mask == ALL_WALLS:
                fill_rect(self.data_view, self.size_line, self.bpp,
                          px, py, cw, ch, palette["mark"], self.endian)
                continue
            draw_cell_walls(
                self.data_view, self.size_line, self.bpp,
                cw, ch, px, py, mask, palette["wall"], self.endian,
                WALL_THICKNESS, max_x, max_y
            )

        self._fill_marker_cell(self.entry, palette["entry"])
        self._fill_marker_cell(self.exit, palette["exit"])

        # 探索経路の描画（アニメーションさせない場合はここで一気に塗る、またはフラグで制御）
        if self.show_path:
            for (x, y) in self.search_path[:self.search_index + 1]:
                self._fill_marker_cell((x, y), palette["path"])

        # 2. 画面へ画像を反映
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )
        # 3. 文字を上乗せ（画像を表示した『後』に描画するのがmlxの鉄則）
        self._draw_menu()

    def _draw_menu(self) -> None:
        """
            画面下部のメニューエリアに、操作説明などのテキストを行単位で描画する。

            全体のウィンドウ高さからメニュー領域（MENU_HEIGHT）を差し引いた位置を基準とし、
            `MENU_LINES` に定義された各文字列を順に `mlx_string_put` を用いて描画。
        """
        menu_top = self.win_height - MENU_HEIGHT
        for i, line in enumerate(MENU_LINES):
            y = menu_top + PADDING + i * LINE_HEIGHT
            self.mlx.mlx_string_put(
                self.mlx_ptr, self.win_ptr, PADDING, y, 0xFFFFFFFF, line
            )

    # -- ループ / イベント ------------------------------------------------ #
    def _on_loop(self, _param: int) -> int:
        """
            メインループと連動して一定時間につき１マスだけ描画し、画面を更新する

            Args:
                _param:MiniLibXのルールブック仕様に必要な引数（関数では未使用）
        """

        if not hasattr(self, '_loop_count'):
            self._loop_count = 0
        if self._loop_count < 10:  # 10フレーム（約0.1〜0.2秒）待つ
            self._loop_count += 1
            return 0

        if (not hasattr(self, '_initialized_render')
                or not self._initialized_render):
            self._render_maze()
            self._initialized_render = True

        # アニメーション処理（元のロジックを維持）
        if self.show_path and self.search_index < len(self.search_path):
            x, y = self.search_path[self.search_index]
            self._draw_search_cell(x, y)
            self.search_index += 1
        elif self.show_path:
            for (x, y) in self.search_path:
                self._draw_search_cell(x, y)

        self.mlx.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0
        )

        self._draw_menu()
        return 0

    def _on_close(self, *args: Any) -> int:
        """
            メインループを終了させ、プログラムを閉じる
            Args：
            MiniLibX（mlx）仕様の任意の引数

        """
        self.mlx.mlx_loop_exit(self.mlx_ptr)
        return 0

    def _on_key(self, keycode: int, _param: Any = None) -> int:
        """
            キー入力に対応したメソッドを呼び出す
            Args：
                keycode 入力されたキーのコード

            Returns：成功したら０
        """
        if keycode == KEY_1:
            self._load_new_maze()
            self._initialized_render = False
        elif keycode == KEY_2:
            self.show_path = not self.show_path
            self.search_index = 0
            self._initialized_render = False
        elif keycode == KEY_3:
            self.palette_index = (self.palette_index + 1) % len(PALETTES)
            self._initialized_render = False
        elif keycode in (KEY_4, ESC_KEY):
            self.mlx.mlx_loop_exit(self.mlx_ptr)
        return 0

    def _on_client_message(self, *args: Any) -> int:
        """
             ウィンドウの「×ボタン」がクリックされたときに呼ばれるコールバック関数。
            プログラムのメインループを安全に終了させ、ウィンドウを閉じます。

            Args:
                *args: MiniLibXのイベントから渡される任意の引数（関数内では未使用）

            Returns:
                int: 正常終了を示すステータスコード (常に 0)

        """
        self.mlx.mlx_loop_exit(self.mlx_ptr)
        return 0

    def run(self) -> None:
        """
            プログラムのメインループを開始し、各種イベントコールバックを登録する。

            ウィンドウの閉じる操作（×ボタン）、キー入力、および定期的なフレーム更新の
            フック関数を MiniLibX に登録し、無限ループ（イベント待ち受け状態）に入る。
            また、GC（ガベージコレクション）による意図しない解放を防ぐため、
            コールバック関数の参照を `_callbacks` リストに保持します。

            Raises:
                RuntimeError: 各種フック関数の登録、またはメインループの起動に失敗した場合。
        """

        self._callbacks.append(self._on_close)
        self._callbacks.append(self._on_client_message)
        self._callbacks.append(self._on_key)
        self._callbacks.append(self._on_loop)

        if self.mlx.mlx_hook(
            self.win_ptr, 17, (1 << 17),
            self._on_close, None
        ) != 0:
            raise RuntimeError("Failed to set close hook")

        if self.mlx.mlx_hook(
            self.win_ptr, 33, 0,
            self._on_client_message, None
        ) != 0:
            raise RuntimeError("Failed to set client message hook")

        if self.mlx.mlx_key_hook(
            self.win_ptr, self._on_key, None
        ) != 0:
            raise RuntimeError("Failed to set key hook")

        if self.mlx.mlx_loop_hook(
            self.mlx_ptr, self._on_loop, None
        ) != 0:
            raise RuntimeError("Failed to set loop hook")

        if self.mlx.mlx_loop(self.mlx_ptr) != 0:
            raise RuntimeError("MLX loop failed")


def main() -> None:
    """
        迷路自動生成および MiniLibX を用いたビジュアライザの起動を行う。
        単独で動かす用のメイン
        30x30 の迷路オブジェクトを生成し、500x500 ピクセルのウィンドウで
        描画システム（MazeRenderer）を初期化してメインループを実行します。
    """
    from mazegen import MazeGenerator

    def make_maze() -> MazeGenerator:
        mg = MazeGenerator(
            width=30, height=30, entry=(0, 0), exit=(25, 14),
            perfect=True
        )
        mg.generator()
        return mg

    try:
        renderer = MazeRenderer(make_maze, win_width=500, win_height=500)
        renderer.run()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
