"""
Dish-Washing × Puzzle - メインゲーム
====================================
洗い場 → パズル / 仕分け のシーン切替を管理する。

フロー:
  パズルゾーンTAP → パズル画面 (ピース配置)
  完成/スキップ → 洗い場 (トレイ準備完了)
  洗浄機TAP → 洗浄開始
  洗浄完了 → 仕分け待ち
  洗い上がりゾーンTAP → 仕分け画面 (ドラッグ＆ドロップ)
  仕分け完了 → 洗い場に戻る
"""

import pyxel
import config
from board import Board
from pieces import generate_stock
from clean_zone import CleanZone
import washing_area

SCENE_WASHING = 0
SCENE_PUZZLE = 1
SCENE_PUZZLE_DONE = 2
SCENE_CLEAN = 3
SCENE_GAMEOVER = 4


class App:
    def __init__(self):
        pyxel.init(config.SCREEN_WIDTH, config.SCREEN_HEIGHT,
                   title=config.TITLE, fps=config.FPS)
        pyxel.mouse(True)
        pyxel.colors.append(config.CUSTOM_COL_PREVIEW_OK_RGB)
        pyxel.colors.append(config.CUSTOM_COL_PREVIEW_NG_RGB)
        self.clean_zone = CleanZone()
        self._restart_game()
        pyxel.run(self.update, self.draw)

    def _restart_game(self):
        self.scene = SCENE_WASHING
        self.complete_timer = 0
        self.timer_frames = config.GAME_TIME_SECONDS * config.FPS
        self.total_score = 0
        self.puzzles_done = 0
        self.puzzles_completed = 0
        self.tray_ready = False
        self.tray_fill_ratio = 0.0
        self.washer_running = False
        self.washer_timer = 0
        self.dishes_to_sort = 0
        self.clean_batches = 0
        self.board = Board()
        self.stock = []
        self.selected_piece = None
        self.selected_index = -1

    # === ヘルパー ===
    def _in_rect(self, mx, my, rx, ry, rw, rh):
        return rx <= mx <= rx + rw and ry <= my <= ry + rh

    def _mouse_to_grid(self, mx, my):
        gx = (mx - config.PUZZLE_BOARD_X) // config.CELL_SIZE
        gy = (my - config.PUZZLE_BOARD_Y) // config.CELL_SIZE
        if 0 <= gx < self.board.size and 0 <= gy < self.board.size:
            return gx, gy
        return None, None

    def _get_stock_index(self, mx, my):
        slot = config.STOCK_SLOT_SIZE
        n = len(self.stock)
        start_x = (config.SCREEN_WIDTH - n * slot) // 2
        sy = config.PUZZLE_STOCK_Y
        if not (sy <= my <= sy + slot):
            return -1
        for i in range(n):
            if start_x + i * slot <= mx <= start_x + (i + 1) * slot:
                return i
        return -1

    # === 更新 ===
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        # タイマー
        if self.scene != SCENE_GAMEOVER:
            self.timer_frames -= 1
            if self.timer_frames <= 0:
                self.timer_frames = 0
                if self.scene == SCENE_PUZZLE:
                    self._record_score(False)
                self.scene = SCENE_GAMEOVER
                return
        # 洗浄機
        if self.washer_running:
            self.washer_timer -= 1
            if self.washer_timer <= 0:
                self.washer_running = False
                self.dishes_to_sort += 1
        # シーン別
        handlers = {
            SCENE_WASHING: self._update_washing,
            SCENE_PUZZLE: self._update_puzzle,
            SCENE_PUZZLE_DONE: self._update_puzzle_done,
            SCENE_CLEAN: self._update_clean,
            SCENE_GAMEOVER: self._update_gameover,
        }
        handlers.get(self.scene, lambda: None)()

    def _update_washing(self):
        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        # パズルゾーン
        if (not self.tray_ready and
            self._in_rect(mx, my, config.PUZZLE_ZONE_X, config.PUZZLE_ZONE_Y,
                          config.PUZZLE_ZONE_W, config.PUZZLE_ZONE_H)):
            self.board.clear()
            self.stock = generate_stock(config.STOCK_PIECE_COUNT)
            self.selected_piece = None
            self.selected_index = -1
            self.scene = SCENE_PUZZLE
        # 洗浄機
        elif (self.tray_ready and not self.washer_running and
              self._in_rect(mx, my, config.WASHER_ZONE_X, config.WASHER_ZONE_Y,
                            config.WASHER_ZONE_W, config.WASHER_ZONE_H)):
            self.washer_running = True
            self.washer_timer = config.WASHER_TIME_SECONDS * config.FPS
            self.tray_ready = False
        # 洗い上がりゾーン
        elif (self.dishes_to_sort > 0 and
              self._in_rect(mx, my, config.CLEAN_ZONE_X, config.CLEAN_ZONE_Y,
                            config.CLEAN_ZONE_W, config.CLEAN_ZONE_H)):
            self.clean_zone.setup()
            self.scene = SCENE_CLEAN

    def _update_puzzle(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self._record_score(False)
            self._exit_puzzle()
            return
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.selected_piece = None
            self.selected_index = -1
        if self.selected_piece:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT) or pyxel.btnp(pyxel.KEY_R):
                self.selected_piece.rotate()
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            if self.selected_piece:
                gx, gy = self._mouse_to_grid(mx, my)
                if gx is not None:
                    cells = self.selected_piece.get_cells_at(gx, gy)
                    if self.board.place_piece(cells, self.selected_piece.color):
                        self.stock.pop(self.selected_index)
                        self.selected_piece = None
                        self.selected_index = -1
                        if self.board.is_full():
                            self._record_score(True)
                            self.scene = SCENE_PUZZLE_DONE
                            self.complete_timer = 0
                            return
                        if len(self.stock) == 0:
                            self.stock = generate_stock(config.STOCK_PIECE_COUNT)
                        return
            idx = self._get_stock_index(mx, my)
            if 0 <= idx < len(self.stock):
                if self.selected_index == idx:
                    self.selected_piece = None
                    self.selected_index = -1
                else:
                    self.selected_piece = self.stock[idx]
                    self.selected_index = idx

    def _update_puzzle_done(self):
        self.complete_timer += 1
        if self.complete_timer > config.FPS * config.COMPLETE_ANIM_SEC:
            self._exit_puzzle()

    def _update_clean(self):
        self.clean_zone.update()
        if self.clean_zone.done:
            self.total_score += self.clean_zone.sorted_count * config.SCORE_PER_SORT
            self.dishes_to_sort -= 1
            self.clean_batches += 1
            self.scene = SCENE_WASHING

    def _update_gameover(self):
        if pyxel.btnp(pyxel.KEY_R):
            self._restart_game()

    def _record_score(self, is_full):
        filled = self.board.get_filled_count()
        self.total_score += filled * config.SCORE_PER_CELL
        if is_full:
            self.total_score += config.SCORE_COMPLETE_BONUS
            self.puzzles_completed += 1
        self.puzzles_done += 1

    def _exit_puzzle(self):
        filled = self.board.get_filled_count()
        total = self.board.size * self.board.size
        self.tray_ready = True
        self.tray_fill_ratio = filled / total if total > 0 else 0
        self.scene = SCENE_WASHING

    # === 描画 ===
    def draw(self):
        pyxel.cls(config.COL_BG)
        draw_map = {
            SCENE_WASHING: self._draw_washing,
            SCENE_PUZZLE: self._draw_puzzle_scene,
            SCENE_PUZZLE_DONE: self._draw_puzzle_scene,
            SCENE_CLEAN: self._draw_clean_scene,
            SCENE_GAMEOVER: self._draw_gameover_screen,
        }
        draw_map.get(self.scene, lambda: None)()

    def _draw_timer_score(self, x, y):
        sec = max(0, self.timer_frames // config.FPS)
        m, s = sec // 60, sec % 60
        tc = config.COL_TIMER_NORMAL
        if sec <= config.TIMER_WARNING_SEC:
            tc = config.COL_TIMER_WARNING if pyxel.frame_count % 10 < 6 else config.COL_TEXT
        pyxel.text(x, y, f"TIME {m}:{s:02d}", tc)
        ss = f"SCORE:{self.total_score}"
        pyxel.text(config.SCREEN_WIDTH - len(ss) * 4 - 4, y, ss, config.COL_TEXT_ACCENT)

    # --- 洗い場 ---
    def _draw_washing(self):
        self._draw_timer_score(4, 4)
        pyxel.text(4, 16, f"DONE:{self.puzzles_done}", config.COL_TEXT)
        pyxel.text(80, 16, f"FULL:{self.puzzles_completed}", config.COL_TEXT)
        washing_area.draw_washer_zone(
            config.WASHER_ZONE_X, config.WASHER_ZONE_Y,
            config.WASHER_ZONE_W, config.WASHER_ZONE_H,
            self.tray_ready, self.washer_running, self.washer_timer)
        washing_area.draw_clean_zone(
            config.CLEAN_ZONE_X, config.CLEAN_ZONE_Y,
            config.CLEAN_ZONE_W, config.CLEAN_ZONE_H,
            self.clean_batches, self.dishes_to_sort)
        washing_area.draw_puzzle_zone(
            config.PUZZLE_ZONE_X, config.PUZZLE_ZONE_Y,
            config.PUZZLE_ZONE_W, config.PUZZLE_ZONE_H,
            self.tray_ready, self.tray_fill_ratio)

    # --- パズル ---
    def _draw_puzzle_scene(self):
        px, py = config.PUZZLE_PANEL_X, config.PUZZLE_PANEL_Y
        pw, ph = config.PUZZLE_PANEL_W, config.PUZZLE_PANEL_H
        pyxel.rect(px, py, pw, ph, config.COL_PANEL_BG)
        pyxel.rectb(px, py, pw, ph, config.COL_PANEL_BORDER)
        pyxel.rectb(px + 1, py + 1, pw - 2, ph - 2, config.COL_GRID_LINE)
        self._draw_timer_score(px + 8, py + 8)
        filled = self.board.get_filled_count()
        total = self.board.size * self.board.size
        ps = f"{filled}/{total}"
        pyxel.text(px + pw // 2 - len(ps) * 2, py + 8, ps, config.COL_TEXT)
        self._draw_board()
        if self.scene == SCENE_PUZZLE:
            self._draw_preview()
        self._draw_stock()
        iy = py + ph - 14
        pyxel.text(px + 8, iy, "[CLICK]Place [R]Rotate", config.COL_GRID_LINE)
        pyxel.text(px + pw - 80, iy, "[SPACE]Skip", config.COL_GRID_LINE)
        if self.scene == SCENE_PUZZLE_DONE:
            bx = config.PUZZLE_BOARD_X
            by = config.PUZZLE_BOARD_Y
            bw = self.board.size * config.CELL_SIZE
            if (self.complete_timer // 4) % 2 == 0:
                pyxel.rectb(bx - 2, by - 2, bw + 4, bw + 4, config.COL_COMPLETE_FLASH)
            msg = "COMPLETE!"
            pyxel.text(config.SCREEN_WIDTH // 2 - len(msg) * 2,
                       config.PUZZLE_STOCK_Y, msg, config.COL_TEXT_ACCENT)

    def _draw_board(self):
        cs = config.CELL_SIZE
        bx, by = config.PUZZLE_BOARD_X, config.PUZZLE_BOARD_Y
        bw = self.board.size * cs
        pyxel.rectb(bx - 1, by - 1, bw + 2, bw + 2, config.COL_GRID_BORDER)
        for gy in range(self.board.size):
            for gx in range(self.board.size):
                px = bx + gx * cs
                py = by + gy * cs
                cell = self.board.grid[gy][gx]
                if cell == 0:
                    shade = config.COL_GRID_EMPTY if (gx + gy) % 2 == 0 else 0
                    pyxel.rect(px, py, cs, cs, shade)
                    pyxel.rectb(px, py, cs, cs, config.COL_GRID_LINE)
                else:
                    pyxel.rect(px, py, cs, cs, cell)
                    pyxel.rectb(px, py, cs, cs, config.COL_GRID_LINE)
                    pyxel.pset(px + 1, py + 1, min(cell + 1, 15))
                    pyxel.pset(px + 2, py + 1, min(cell + 1, 15))
                    pyxel.pset(px + 1, py + 2, min(cell + 1, 15))

    def _draw_preview(self):
        if not self.selected_piece:
            return
        gx, gy = self._mouse_to_grid(pyxel.mouse_x, pyxel.mouse_y)
        if gx is None:
            return
        cells = self.selected_piece.get_cells_at(gx, gy)
        valid = self.board.is_valid_placement(cells)
        cs = config.CELL_SIZE
        col = config.CUSTOM_COL_PREVIEW_OK if valid else config.CUSTOM_COL_PREVIEW_NG
        for cx, cy in cells:
            if self.board.is_inside(cx, cy):
                pyxel.rect(config.PUZZLE_BOARD_X + cx * cs + 1,
                           config.PUZZLE_BOARD_Y + cy * cs + 1,
                           cs - 2, cs - 2, col)

    def _draw_stock(self):
        slot = config.STOCK_SLOT_SIZE
        mini = config.STOCK_MINI_CELL
        n = len(self.stock)
        sx_start = (config.SCREEN_WIDTH - n * slot) // 2
        sy = config.PUZZLE_STOCK_Y
        label = "-- STOCK --"
        pyxel.text(config.SCREEN_WIDTH // 2 - len(label) * 2, sy - 10, label, config.COL_TEXT)
        for i, piece in enumerate(self.stock):
            sx = sx_start + i * slot
            is_sel = (i == self.selected_index)
            bg = config.COL_SELECTED_BG if is_sel else config.COL_STOCK_BG
            pyxel.rect(sx, sy, slot - 2, slot - 2, bg)
            pyxel.rectb(sx, sy, slot - 2, slot - 2, config.COL_GRID_LINE)
            if is_sel:
                pyxel.rectb(sx - 1, sy - 1, slot, slot, config.COL_SELECTED_BORDER)
            pw, ph = piece.get_width(), piece.get_height()
            ox = sx + (slot - 2 - pw * mini) // 2
            oy = sy + (slot - 2 - ph * mini) // 2
            for cx, cy in piece.cells:
                pyxel.rect(ox + cx * mini, oy + cy * mini, mini, mini, piece.color)
                pyxel.rectb(ox + cx * mini, oy + cy * mini, mini, mini, config.COL_GRID_LINE)

    # --- 仕分け ---
    def _draw_clean_scene(self):
        self._draw_timer_score(config.CLEAN_PANEL_X + 8, config.CLEAN_PANEL_Y - 16)
        self.clean_zone.draw()

    # --- ゲームオーバー ---
    def _draw_gameover_screen(self):
        self._draw_washing()
        cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
        bw, bh = 200, 110
        pyxel.rect(cx - bw // 2, cy - bh // 2, bw, bh, 0)
        pyxel.rectb(cx - bw // 2, cy - bh // 2, bw, bh, config.COL_TEXT_ACCENT)
        t = "TIME UP!"
        pyxel.text(cx - len(t) * 2, cy - 44, t, config.COL_TEXT_ACCENT)
        for i, line in enumerate([
            f"SCORE: {self.total_score}",
            f"PUZZLES: {self.puzzles_done}  FULL: {self.puzzles_completed}",
            f"WASHED: {self.clean_batches}",
        ]):
            pyxel.text(cx - len(line) * 2, cy - 24 + i * 14, line, config.COL_TEXT)
        r = "[R] RESTART"
        pyxel.text(cx - len(r) * 2, cy + 30, r, config.COL_GRID_LINE)


App()
