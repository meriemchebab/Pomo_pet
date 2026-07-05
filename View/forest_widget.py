from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen

POMO_SEC  = 25 * 60
BREAK_SEC =  5 * 60

# ── Day positions: direct pixel (x, y) = top-left of 68×68 tree tile ─────────
# Calculated for FRAME 997×589, TREE_SIZE 68×68
# Centered over the original 96×96 bush positions, scaled to the new frame size
DAY_POSITIONS = {
     1: ( 141,  516),
     2: ( 141,  453),
     3: (  14,  359),
     4: ( 110,  327),
     5: (  14,  202),
     6: ( 110,  202),
     7: (  14,  107),
     8: ( 110,  107),
     9: ( 237,  107),
    10: ( 237,  202),
    11: ( 205,  390),
    12: ( 301,  390),
    13: ( 333,  202),
    14: ( 333,  107),
    15: ( 429,  233),
    16: ( 429,  327),
    17: ( 429,  453),
    18: ( 556,  453),
    19: ( 556,  327),
    20: ( 556,  233),
    21: ( 556,  139),
    22: ( 652,  233),
    23: ( 652,  359),
    24: ( 652,  453),
    25: ( 780,  516),
    26: ( 780,  390),
    27: ( 780,  264),
    28: ( 780,  170),
    29: ( 843,   76),
    30: ( 875,  170),
    31: ( 971,   76),
}

FRAME_W   = 997   # forest.png width
FRAME_H   = 598  # forest.png height
TREE_SIZE = 68    # tree tile size in pixels (at 1:1 scale)


class MapWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.grown: set[int] = set()
        self.current_day: int = 1

        self._bg   = QPixmap("assets/forest_panel.png")
        self._tree = QPixmap("assets/tree_tile.png")

    def grow_tree(self, day: int):
        self.grown.add(day)
        self.update()

    def set_current_day(self, day: int):
        self.current_day = day
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        scale = min(w / FRAME_W, h / FRAME_H)

        offset_x = (w - int(FRAME_W * scale)) // 2
        offset_y = (h - int(FRAME_H * scale)) // 2

        # 1. Background
        if self._bg and not self._bg.isNull():
            p.drawPixmap(
                QRect(offset_x, offset_y, int(FRAME_W * scale), int(FRAME_H * scale)),
                self._bg,
            )
        else:
            p.fillRect(0, 0, w, h, QColor("#4a8c20"))

        current_tree_size = int(TREE_SIZE * scale)

        # 2. Trees on completed days
        for day, (px, py) in DAY_POSITIONS.items():
            if day in self.grown and self._tree and not self._tree.isNull():
                x = offset_x + int(px * scale)
                y = offset_y + int(py * scale)
                p.drawPixmap(QRect(x, y, current_tree_size, current_tree_size), self._tree)

        # 3. Gold highlight on active day
        if self.current_day in DAY_POSITIONS:
            px, py = DAY_POSITIONS[self.current_day]
            x = offset_x + int(px * scale)
            y = offset_y + int(py * scale)
            p.setPen(QPen(QColor("#FFD700"), max(1, int(3 * scale))))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(x + 1, y + 1, current_tree_size - 2, current_tree_size - 2)

        p.end()