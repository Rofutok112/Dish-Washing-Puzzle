"""
洗い場シーンの描画
==================
間取り図ベース:
  左上: 食洗器 / 左下: 洗い上がりゾーン / 右: パズルゾーン
将来的にここのプレースホルダをスプライトに差し替える想定。
"""

import pyxel
import config


def draw_zone_frame(x, y, w, h, bg_col, label, clickable=False):
    """ゾーン共通の枠描画"""
    pyxel.rect(x, y, w, h, bg_col)
    pyxel.rectb(x, y, w, h, config.COL_ZONE_BORDER)
    pyxel.text(x + w // 2 - len(label) * 2, y + 6, label, config.COL_TEXT)
    if clickable:
        if pyxel.frame_count % 20 < 14:
            pyxel.rectb(x + 1, y + 1, w - 2, h - 2, config.COL_ZONE_HIGHLIGHT)
        pyxel.text(x + w // 2 - 8, y + h - 14, "TAP!", config.COL_ZONE_HIGHLIGHT)


def draw_puzzle_zone(x, y, w, h, tray_ready, fill_ratio):
    """パズル(皿セット)ゾーン — 右側の大きなエリア"""
    clickable = not tray_ready
    draw_zone_frame(x, y, w, h, config.COL_ZONE_PUZZLE, "PUZZLE ZONE", clickable)

    # 仮: トレイ表示
    tx, ty = x + 20, y + 30
    tw, th = w - 40, h - 60
    pyxel.rectb(tx, ty, tw, th, config.COL_GRID_LINE)

    if tray_ready:
        fill_h = int(th * fill_ratio)
        if fill_h > 0:
            pyxel.rect(tx + 1, ty + th - fill_h, tw - 2, fill_h, 12)
        pct = f"{int(fill_ratio * 100)}%"
        pyxel.text(tx + tw // 2 - len(pct) * 2, ty + th // 2, pct, config.COL_TEXT)
        pyxel.text(tx + tw // 2 - 12, ty + th + 4, "READY!", config.COL_TEXT_ACCENT)
    else:
        # プレイヤー（人）の仮表示
        cx = x + w // 2
        cy = y + h // 2 + 20
        pyxel.circb(cx, cy, 12, config.COL_GRID_LINE)
        pyxel.text(cx - 4, cy - 2, "YOU", config.COL_GRID_LINE)


def draw_washer_zone(x, y, w, h, tray_ready, washer_running, washer_timer):
    """食洗器ゾーン — 左上"""
    clickable = tray_ready and not washer_running
    draw_zone_frame(x, y, w, h, config.COL_ZONE_WASHER, "DISHWASHER", clickable)

    # 仮: 洗浄機本体
    mx, my = x + 16, y + 28
    mw, mh = w - 32, h - 52
    pyxel.rect(mx, my, mw, mh, 5)
    pyxel.rectb(mx, my, mw, mh, 13)

    # ドア
    cx, cy = mx + mw // 2, my + mh // 2
    r = min(mw, mh) // 3
    pyxel.circ(cx, cy, r, 0)
    pyxel.circb(cx, cy, r, 13)

    if washer_running:
        dots = "." * ((pyxel.frame_count // 8) % 4)
        pyxel.text(cx - 12, cy - 2, f"WASH{dots}", 11)
        # プログレスバー
        total = config.WASHER_TIME_SECONDS * config.FPS
        prog = 1.0 - (washer_timer / total) if total > 0 else 1.0
        bw = mw - 8
        pyxel.rect(mx + 4, my + mh + 4, bw, 5, 0)
        pyxel.rect(mx + 4, my + mh + 4, int(bw * prog), 5, 11)
        pyxel.rectb(mx + 4, my + mh + 4, bw, 5, 5)
    else:
        pyxel.text(cx - 8, cy - 2, "IDLE", config.COL_GRID_LINE)

    # 矢印（洗浄機→洗い上がりゾーンへの流れを示す）
    pyxel.text(x + w // 2 - 4, y + h - 10, "v", config.COL_ZONE_HIGHLIGHT)


def draw_clean_zone(x, y, w, h, clean_batches, dishes_to_sort):
    """洗い上がりゾーン — 左下"""
    clickable = dishes_to_sort > 0
    draw_zone_frame(x, y, w, h, config.COL_ZONE_CLEAN, "CLEAN ZONE", clickable)

    # 仕分け待ち表示
    if dishes_to_sort > 0:
        msg = f"UNSORTED: {dishes_to_sort}"
        pyxel.text(x + w // 2 - len(msg) * 2, y + 24, msg, config.COL_TEXT_ACCENT)

    # 完了済みの皿山
    count_str = f"SORTED: x{clean_batches}"
    pyxel.text(x + w // 2 - len(count_str) * 2, y + h - 28, count_str, config.COL_TEXT)

    plate_y = y + h - 40
    for i in range(min(clean_batches, 6)):
        py = plate_y - i * 12
        if py < y + 38:
            break
        pyxel.rect(x + 12, py, w - 24, 8, 12)
        pyxel.rectb(x + 12, py, w - 24, 8, config.COL_GRID_LINE)
