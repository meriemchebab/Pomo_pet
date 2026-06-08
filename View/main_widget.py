from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QStackedWidget, QVBoxLayout, QWidget,
)
SIDEBAR_OPEN      = 190
SIDEBAR_COLLAPSED = 50
ANIM_MS           = 220


class NavItem(QWidget):
    """Single sidebar row: icon · label · badge."""

    clicked = Signal()

    def __init__(self, icon: str, label: str, badge: str = ""):
        super().__init__()
        self.setObjectName("NavItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._active = False

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        row.setSpacing(9)

        self._icon = QLabel(icon)
        self._icon.setObjectName("niIcon")
        self._icon.setFixedWidth(20)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel(label)
        self._label.setObjectName("niLabel")
        self._label.setSizePolicy(QSizePolicy.Policy.Expanding,
                                  QSizePolicy.Policy.Preferred)

        self._badge = QLabel(badge)
        self._badge.setObjectName("niBadge")
        self._badge.setVisible(bool(badge))

        row.addWidget(self._icon)
        row.addWidget(self._label)
        row.addWidget(self._badge)

    def set_active(self, v: bool):
        self._active = v
        self.setProperty("active", v)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_collapsed(self, v: bool):
        self._label.setVisible(not v)
        self._badge.setVisible(not v and bool(self._badge.text()))

    def set_badge(self, text: str):
        self._badge.setText(text)
        self._badge.setVisible(bool(text))

    def mousePressEvent(self, _):
        self.clicked.emit()


class Sidebar(QFrame):
    nav_changed = Signal(str)   # key string

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(SIDEBAR_OPEN)
        self._collapsed = False
        self._items: dict[str, NavItem] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # top: logo + toggle
        top = QFrame()
        top.setObjectName("sbTop")
        top_row = QHBoxLayout(top)
        top_row.setContentsMargins(12, 10, 10, 8)
        top_row.setSpacing(8)

        self._logo = QLabel("Chrono Forest")
        self._logo.setObjectName("sbLogo")
        top_row.addWidget(self._logo, stretch=1)

        self._tog = QPushButton("◀")
        self._tog.setObjectName("sbToggle")
        self._tog.setFixedSize(24, 24)
        self._tog.clicked.connect(self.toggle)
        top_row.addWidget(self._tog)

        root.addWidget(top)
        root.addWidget(self._divider())

        # nav items
        nav = QFrame()
        self._nav_layout = QVBoxLayout(nav)
        self._nav_layout.setContentsMargins(6, 8, 6, 8)
        self._nav_layout.setSpacing(3)

        tabs = [
            ("forest",   "🌲", "Forest",   ""),
            ("pet",      "🍅", "Pet",      ""),
            ("projects", "📋", "Projects", ""),
            ("sounds",   "🎵", "Sounds",   ""),
            ("settings", "⚙",  "Settings", ""),
        ]
        for key, icon, label, badge in tabs:
            item = NavItem(icon, label, badge)
            item.clicked.connect(lambda k=key: self._on_click(k))
            self._nav_layout.addWidget(item)
            self._items[key] = item

        self._nav_layout.addStretch()
        root.addWidget(nav, stretch=1)

        # animation
        self._anim_min = QPropertyAnimation(self, b"minimumWidth")
        self._anim_max = QPropertyAnimation(self, b"maximumWidth")
        for a in (self._anim_min, self._anim_max):
            a.setDuration(ANIM_MS)
            a.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._on_click("forest")
        self._apply_style()

    def toggle(self):
        self._collapsed = not self._collapsed
        target = SIDEBAR_COLLAPSED if self._collapsed else SIDEBAR_OPEN
        for a in (self._anim_min, self._anim_max):
            a.stop()
            a.setStartValue(self.width())
            a.setEndValue(target)
            a.start()
        self._tog.setText("▶" if self._collapsed else "◀")
        self._logo.setVisible(not self._collapsed)
        for item in self._items.values():
            item.set_collapsed(self._collapsed)

    def set_badge(self, key: str, text: str):
        if key in self._items:
            self._items[key].set_badge(text)

    def _on_click(self, key: str):
        for k, item in self._items.items():
            item.set_active(k == key)
        self.nav_changed.emit(key)

    @staticmethod
    def _divider() -> QFrame:
        d = QFrame()
        d.setObjectName("sbDiv")
        d.setFrameShape(QFrame.Shape.HLine)
        d.setFixedHeight(1)
        return d

    def _apply_style(self):
        self.setStyleSheet("""
        QFrame#Sidebar {
            background: #0f2a1c;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 14px;
        }
        QFrame#sbTop {
            background: transparent;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        QFrame#sbDiv {
            background: rgba(255,255,255,0.06);
            border: none;
        }
        QLabel#sbLogo {
            font-size: 11px; font-weight: 700;
            color: #d0e8c0; letter-spacing: 0.5px;
        }
        QPushButton#sbToggle {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 6px; font-size: 10px;
            color: rgba(180,210,160,0.5);
        }
        QPushButton#sbToggle:hover {
            background: rgba(255,255,255,0.10);
            color: #d0e8c0;
        }
        QWidget#NavItem {
            border-radius: 9px;
            border: 1px solid transparent;
        }
        QWidget#NavItem:hover { background: rgba(255,255,255,0.05); }
        QWidget#NavItem[active=true] {
            background: #2d5224;
            border-color: rgba(138,184,96,0.2);
        }
        QLabel#niIcon  { font-size: 15px; }
        QLabel#niLabel {
            font-size: 10px; font-weight: 600; letter-spacing: 0.5px;
            color: rgba(180,210,160,0.45);
        }
        QWidget#NavItem[active=true] QLabel#niLabel { color: #d0e8c0; }
        QWidget#NavItem:hover       QLabel#niLabel { color: rgba(180,210,160,0.8); }
        QLabel#niBadge {
            font-size: 8px; font-weight: 700; color: #8ab860;
            background: rgba(138,184,96,0.12);
            border: 1px solid rgba(138,184,96,0.2);
            border-radius: 8px; padding: 1px 5px;
        }
        """)


class MainWindow(QWidget):
    """
    Main window — sidebar + stacked panels only.
    The clock floats separately as FloatingClock.

    ┌────────┬──────────────────────────────┐
    │Sidebar │     QStackedWidget           │
    │  nav   │     (active panel)           │
    └────────┴──────────────────────────────┘
    """

    def __init__(self, forest_widget, pet_widget,
                 projects_widget, sounds_widget,
                 settings_widget, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chrono Forest")
        self.setMinimumSize(640, 520)
        self.resize(860, 640)

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        # sidebar
        self.sidebar = Sidebar()

        # stacked panels
        self.stack = QStackedWidget()
        self.stack.setObjectName("MainStack")
        self.stack.addWidget(forest_widget)    # 0
        self.stack.addWidget(pet_widget)       # 1
        self.stack.addWidget(projects_widget)  # 2
        self.stack.addWidget(sounds_widget)    # 3
        self.stack.addWidget(settings_widget)  # 4

        self._idx = {
            "forest": 0, "pet": 1,
            "projects": 2, "sounds": 3, "settings": 4,
        }
        self.sidebar.nav_changed.connect(
            lambda k: self.stack.setCurrentIndex(self._idx[k])
        )

        root.addWidget(self.sidebar, stretch=0)
        root.addWidget(self.stack,   stretch=1)
        self._apply_style()

    def update_badge(self, key: str, text: str):
        self.sidebar.set_badge(key, text)

    def _apply_style(self):
        self.setStyleSheet("""
        MainWindow { background: #0e2318; }
        QStackedWidget#MainStack {
            background: #1a3228;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 14px;
        }
        """)
