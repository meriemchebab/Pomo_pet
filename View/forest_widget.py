from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen

POMO_SEC  = 25 * 60
BREAK_SEC =  5 * 60

# ── Day positions: direct pixel (x, y) = top-left of 68×68 tree tile ─────────
# Calculated for FRAME 997x598, TREE_SIZE 68×68

DAY_POSITIONS = {
     1: ( 109,  523),
     2: ( 109,  427),
     3: (  13,  299),
     4: ( 109,  299),
     5: (  13,  171),
     6: ( 109,  171),
     7: (  13,   75),
     8: ( 109,   75),
     9: ( 237,   75),
    10: ( 237,  171),
    11: ( 237,  363),
    12: ( 333,  363),
    13: ( 365,  171),
    14: ( 365,   75),
    15: ( 461,  203),
    16: ( 461,  299),
    17: ( 462,  459),
    18: ( 557,  459),
    19: ( 557,  299),
    20: ( 557,  203),
    21: ( 557,  107),
    22: ( 717,  203),
    23: ( 717,  299),
    24: ( 685,  459),
    25: ( 813,  491),
    26: ( 813,  331),
    27: ( 813,  235),
    28: ( 813,  139),
    29: ( 813,   11),
    30: ( 909,  139),
    31: ( 909,   11),
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