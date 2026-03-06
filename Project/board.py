"""
盤面（ボード）の管理
===================
n×n のグリッド状態を管理し、ピースの配置・検証・クリアを行う。
"""

from config import GRID_SIZE


class Board:
    """n×n の盤面"""

    def __init__(self, size=GRID_SIZE):
        self.size = size
        # 0: 空きマス, それ以外: ピースの色番号
        self.grid = [[0] * size for _ in range(size)]

    def is_inside(self, x, y):
        """座標が盤面内かどうか"""
        return 0 <= x < self.size and 0 <= y < self.size

    def is_valid_placement(self, cells):
        """
        指定セル群が配置可能かチェックする。
        全セルが盤面内かつ空きマスであれば True。
        """
        for x, y in cells:
            if not self.is_inside(x, y):
                return False
            if self.grid[y][x] != 0:
                return False
        return True

    def place_piece(self, cells, color):
        """
        ピースを配置する。
        配置不可なら False を返す。
        """
        if not self.is_valid_placement(cells):
            return False
        for x, y in cells:
            self.grid[y][x] = color
        return True

    def is_full(self):
        """盤面のすべてのマスが埋まっているか"""
        for row in self.grid:
            for cell in row:
                if cell == 0:
                    return False
        return True

    def clear(self):
        """盤面を初期状態（全て空き）に戻す"""
        self.grid = [[0] * self.size for _ in range(self.size)]

    def get_filled_count(self):
        """埋まっているマスの数を返す"""
        count = 0
        for row in self.grid:
            for cell in row:
                if cell != 0:
                    count += 1
        return count

    def can_fit_any(self, pieces):
        """
        渡されたピースのいずれかが盤面に配置可能か判定する。
        （各ピースの全回転・全位置を試す）
        """
        for piece in pieces:
            # 4方向の回転を試す
            test_cells = list(piece.cells)
            for _ in range(4):
                for gy in range(self.size):
                    for gx in range(self.size):
                        placed = [(gx + dx, gy + dy) for dx, dy in test_cells]
                        if self.is_valid_placement(placed):
                            return True
                # 回転
                test_cells = [(y, -x) for x, y in test_cells]
                min_x = min(x for x, y in test_cells)
                min_y = min(y for x, y in test_cells)
                test_cells = sorted([(x - min_x, y - min_y) for x, y in test_cells])
        return False
