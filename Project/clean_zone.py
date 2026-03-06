"""
洗い上がりゾーン - お皿仕分けシーン
====================================
洗浄済みのお皿をドラッグ＆ドロップで種類ごとに仕分ける。
正しいビンに入れると得点。全て仕分けたら完了。
"""

import pyxel
import random
import config

# 仕分け対象の皿タイプ
DISH_TYPES = [
    {"name": "SARA",  "color": 9,  "w": 30, "h": 16},
    {"name": "CUP",   "color": 15, "w": 16, "h": 24},
    {"name": "BOWL",  "color": 14, "w": 26, "h": 18},
    {"name": "TRAY",  "color": 12, "w": 36, "h": 14},
]
BIN_COUNT = len(DISH_TYPES)


class CleanZone:
    """仕分けシーンの状態管理"""

    def __init__(self):
        self.dishes = []
        self.dragging = -1
        self.drag_ox = 0
        self.drag_oy = 0
        self.done = False
        self.sorted_count = 0

    def setup(self):
        """新しいバッチの皿を生成"""
        self.dishes = []
        self.dragging = -1
        self.done = False
        self.sorted_count = 0

        px = config.CLEAN_PANEL_X + 30
        py = config.CLEAN_PANEL_Y + 30
        area_w = config.CLEAN_PANEL_W - 60
        area_h = 110

        for _ in range(config.SORT_DISH_COUNT):
            t = random.randint(0, BIN_COUNT - 1)
            dt = DISH_TYPES[t]
            self.dishes.append({
                "type": t,
                "x": px + random.randint(0, max(0, area_w - dt["w"])),
                "y": py + random.randint(0, max(0, area_h - dt["h"])),
                "sorted": False,
            })

    def _bin_rect(self, idx):
        """ビンidxの矩形 (x, y, w, h) を返す"""
        gap = 10
        total = config.CLEAN_PANEL_W - 40
        bw = (total - gap * (BIN_COUNT - 1)) // BIN_COUNT
        bx = config.CLEAN_PANEL_X + 20 + idx * (bw + gap)
        by = config.CLEAN_PANEL_Y + config.CLEAN_PANEL_H - 100
        return bx, by, bw, 60

    def update(self):
        """ドラッグ＆ドロップ処理。完了したら self.done = True"""
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        # SPACEでスキップ
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.done = True
            return

        # ドラッグ開始
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.dragging < 0:
            for i in range(len(self.dishes) - 1, -1, -1):
                d = self.dishes[i]
                if d["sorted"]:
                    continue
                dt = DISH_TYPES[d["type"]]
                if d["x"] <= mx <= d["x"] + dt["w"] and d["y"] <= my <= d["y"] + dt["h"]:
                    self.dragging = i
                    self.drag_ox = d["x"] - mx
                    self.drag_oy = d["y"] - my
                    break

        # ドラッグ中
        if self.dragging >= 0 and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            self.dishes[self.dragging]["x"] = mx + self.drag_ox
            self.dishes[self.dragging]["y"] = my + self.drag_oy

        # ドロップ
        if self.dragging >= 0 and pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
            d = self.dishes[self.dragging]
            dt = DISH_TYPES[d["type"]]
            cx = d["x"] + dt["w"] // 2
            cy = d["y"] + dt["h"] // 2
            placed = False

            for b in range(BIN_COUNT):
                bx, by, bw, bh = self._bin_rect(b)
                if bx <= cx <= bx + bw and by <= cy <= by + bh:
                    if d["type"] == b:
                        d["sorted"] = True
                        d["x"] = bx + random.randint(4, max(4, bw - dt["w"] - 4))
                        d["y"] = by + random.randint(20, max(20, bh - dt["h"] - 4))
                        self.sorted_count += 1
                        placed = True
                    break

            if not placed:
                # 元に戻すアニメーション（即戻し）
                d["x"] = config.CLEAN_PANEL_X + 30 + random.randint(0, config.CLEAN_PANEL_W - 90)
                d["y"] = config.CLEAN_PANEL_Y + 30 + random.randint(0, 110)

            self.dragging = -1

            if all(d["sorted"] for d in self.dishes):
                self.done = True

    def draw(self):
        """仕分けシーン全体を描画"""
        px, py = config.CLEAN_PANEL_X, config.CLEAN_PANEL_Y
        pw, ph = config.CLEAN_PANEL_W, config.CLEAN_PANEL_H
        pyxel.rect(px, py, pw, ph, config.COL_PANEL_BG)
        pyxel.rectb(px, py, pw, ph, config.COL_PANEL_BORDER)
        pyxel.rectb(px + 1, py + 1, pw - 2, ph - 2, config.COL_GRID_LINE)

        title = "SORT THE DISHES!"
        pyxel.text(px + pw // 2 - len(title) * 2, py + 8, title, config.COL_TEXT_ACCENT)

        progress = f"{self.sorted_count}/{len(self.dishes)}"
        pyxel.text(px + pw - len(progress) * 4 - 12, py + 8, progress, config.COL_TEXT)

        # ビン
        for b in range(BIN_COUNT):
            bx, by, bw, bh = self._bin_rect(b)
            dt = DISH_TYPES[b]
            pyxel.rect(bx, by, bw, bh, 1)
            pyxel.rectb(bx, by, bw, bh, dt["color"])
            pyxel.text(bx + bw // 2 - len(dt["name"]) * 2, by + 6, dt["name"], dt["color"])

        # 皿（ドラッグ中は最前面）
        for i, d in enumerate(self.dishes):
            if i != self.dragging:
                self._draw_dish(d)
        if self.dragging >= 0:
            self._draw_dish(self.dishes[self.dragging])

        # 操作説明
        pyxel.text(px + 8, py + ph - 14, "[DRAG] Sort dishes", config.COL_GRID_LINE)
        pyxel.text(px + pw - 80, py + ph - 14, "[SPACE] Skip", config.COL_GRID_LINE)

    def _draw_dish(self, d):
        dt = DISH_TYPES[d["type"]]
        x, y = int(d["x"]), int(d["y"])
        w, h = dt["w"], dt["h"]
        pyxel.rect(x, y, w, h, dt["color"])
        pyxel.rectb(x, y, w, h, config.COL_GRID_LINE)
        # ミニラベル
        label = dt["name"][:2]
        pyxel.text(x + w // 2 - len(label) * 2, y + h // 2 - 2, label, 0)
