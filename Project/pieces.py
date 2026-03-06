"""
ピース（お皿）の定義
====================
各ピースはポリオミノ形状で、(col, row) オフセットのリストで表現される。
回転・ストック生成の機能を提供する。
"""

import random


# ===========================================
#  ピース形状の定義
#  cells: (x, y) オフセットのリスト
#  color: Pyxelパレット番号
# ===========================================
PIECE_TYPES = [
    {
        "name": "small_plate",
        "cells": [(0, 0)],
        "color": 9,     # オレンジ
    },
    {
        "name": "medium_plate",
        "cells": [(0, 0), (1, 0)],
        "color": 10,    # 黄色
    },
    {
        "name": "tall_glass",
        "cells": [(0, 0), (0, 1)],
        "color": 15,    # ピーチ
    },
    {
        "name": "long_plate",
        "cells": [(0, 0), (1, 0), (2, 0)],
        "color": 11,    # 黄緑
    },
    {
        "name": "bowl",
        "cells": [(0, 0), (1, 0), (0, 1)],
        "color": 14,    # ピンク
    },
    {
        "name": "large_plate",
        "cells": [(0, 0), (1, 0), (0, 1), (1, 1)],
        "color": 12,    # 水色
    },
    {
        "name": "l_plate",
        "cells": [(0, 0), (1, 0), (2, 0), (2, 1)],
        "color": 3,     # 深緑
    },
    {
        "name": "t_plate",
        "cells": [(0, 0), (1, 0), (2, 0), (1, 1)],
        "color": 2,     # 紫
    },
    {
        "name": "s_plate",
        "cells": [(1, 0), (2, 0), (0, 1), (1, 1)],
        "color": 4,     # 茶色
    },
]


def rotate_cells_cw(cells):
    """セルリストを時計回りに90度回転する"""
    rotated = [(y, -x) for x, y in cells]
    # 原点 (0,0) 基準に正規化
    min_x = min(x for x, y in rotated)
    min_y = min(y for x, y in rotated)
    return sorted([(x - min_x, y - min_y) for x, y in rotated])


class Piece:
    """配置可能なピース（お皿）"""

    def __init__(self, piece_type):
        self.name = piece_type["name"]
        self.cells = list(piece_type["cells"])
        self.color = piece_type["color"]
        self.rotation = 0

    def rotate(self):
        """時計回りに90度回転"""
        self.cells = rotate_cells_cw(self.cells)
        self.rotation = (self.rotation + 1) % 4

    def get_width(self):
        """ピースの幅（セル数）"""
        return max(x for x, y in self.cells) + 1

    def get_height(self):
        """ピースの高さ（セル数）"""
        return max(y for x, y in self.cells) + 1

    def get_cells_at(self, grid_x, grid_y):
        """指定グリッド座標に配置した場合のセル座標リストを返す"""
        return [(grid_x + dx, grid_y + dy) for dx, dy in self.cells]


def generate_stock(count=5):
    """ストック用のピースをランダムに生成する"""
    pieces = []
    for _ in range(count):
        piece_type = random.choice(PIECE_TYPES)
        pieces.append(Piece(piece_type))
    return pieces
