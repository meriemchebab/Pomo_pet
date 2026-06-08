from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QSizePolicy

from .theme import PALETTES, ThemeBuilder


class ForestCanvas(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = ThemeBuilder()
        self.setMinimumSize(420, 260)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setObjectName('greenCard')
        self.map_pixmap = QPixmap()
        self.tile_pixmap = QPixmap()
        self.grid_rows = 5
        self.grid_cols = 7
        self.cell_padding = 10
        self.cell_labels = [[f'Plot {r+1}-{c+1}' for c in range(self.grid_cols)] for r in range(self.grid_rows)]
        self.state_map = [
            ['sprout', 'tree', 'tree', 'tree', 'tree', 'empty', 'empty'],
            ['tree', 'tree', 'sapling', 'tree', 'tree', 'tree', 'empty'],
            ['sprout', 'tree', 'tree', 'sapling', 'empty', 'empty', 'empty'],
            ['tree', 'sprout', 'empty', 'empty', 'empty', 'empty', 'empty'],
            ['empty', 'empty', 'empty', 'empty', 'empty', 'empty', 'empty'],
        ]

    def sizeHint(self):
        return QSize(760, 520)

    def set_map_image(self, path: str):
        self.map_pixmap = QPixmap(path)
        self.update()

    def set_tile_image(self, path: str):
        self.tile_pixmap = QPixmap(path)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)

        if not self.map_pixmap.isNull():
            p.drawPixmap(rect, self.map_pixmap)
        else:
            # Use theme accent_soft for grass background
            p.fillRect(rect, QColor(self.theme.palette['accent_soft']))
            # Use theme line color for grid
            p.setPen(QPen(QColor(self.theme.palette['accent_dark']), 3))
            for y in range(rect.top(), rect.bottom(), 28):
                p.drawLine(rect.left(), y, rect.right(), y)

        cols = self.grid_cols
        rows = self.grid_rows
        cell_w = rect.width() / cols
        cell_h = rect.height() / rows

        for r in range(rows):
            for c in range(cols):
                cell = QRectF(
                    rect.left() + c * cell_w + self.cell_padding,
                    rect.top() + r * cell_h + self.cell_padding,
                    cell_w - self.cell_padding * 2,
                    cell_h - self.cell_padding * 2,
                )
                state = self.state_map[r][c]
                self._draw_plot(p, cell, state, self.cell_labels[r][c])

    def _draw_plot(self, p: QPainter, cell: QRectF, state: str, label: str):
        """Draw a single plot cell with theme-aware colors."""
        p_pal = self.theme.palette
        
        # Soil: dark brown/panel color
        soil = QColor(p_pal['panel_dark'])
        # Grass/foliage: accent soft green
        grass = QColor(p_pal['accent_soft'])
        # Tree: accent green
        tree = QColor(p_pal['accent'])
        # Trunk: slightly lighter than panel_dark
        trunk = QColor(p_pal['panel_mid'])
        # Cell border: muted color
        cell_border = QColor(p_pal['muted'])

        p.setPen(QPen(cell_border, 2))
        p.setBrush(QBrush(soil))
        p.drawRoundedRect(cell, 10, 10)

        center_x = cell.center().x()
        if state in {'sprout', 'sapling', 'tree'}:
            if state == 'sprout':
                # Young sprout: bright accent
                p.setBrush(QBrush(QColor(p_pal['accent_soft'])))
                p.drawEllipse(QRectF(center_x - 8, cell.top() + 16, 16, 16))
                p.drawLine(int(center_x), int(cell.top() + 18), int(center_x), int(cell.top() + 30))
            else:
                # Sapling or tree: trunk + crown
                p.setBrush(QBrush(trunk))
                p.drawRoundedRect(QRectF(center_x - 6, cell.top() + 28, 12, 24), 4, 4)
                crown = QRectF(center_x - 24, cell.top() + (10 if state == 'tree' else 16), 48, 34)
                # Use grass for sapling, tree color for mature tree
                p.setBrush(QBrush(tree if state == 'tree' else grass))
                p.drawEllipse(crown)
                p.drawEllipse(crown.adjusted(-12, 8, -10, 8))
                p.drawEllipse(crown.adjusted(10, 8, 12, 8))

        # Badge with label
        badge = QRectF(cell.left() + 10, cell.bottom() - 18, 54, 16)
        p.setBrush(QColor(p_pal['panel_light']))
        p.setPen(QPen(QColor(p_pal['text']), 1))
        p.drawRoundedRect(badge, 8, 8)
        p.drawText(badge, Qt.AlignmentFlag.AlignCenter, label)


class ForestWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('panelCard')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel('Forest Widget')
        title.setStyleSheet('font-size: 18px; font-weight: 700;')
        subtitle = QLabel('Placeholder grid for your pixel map and tile overlays.')
        subtitle.setStyleSheet(f"color: {ThemeBuilder().palette['muted']};")

        self.canvas = ForestCanvas()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.canvas, 1)