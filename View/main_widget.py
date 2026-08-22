from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QStackedWidget, QVBoxLayout, QWidget,
)
from PySide6.QtGui import QIcon,QPixmap
from .theme import ThemeBuilder
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

        self._icon = QLabel()
        self._icon.setObjectName("niIcon")
        self._icon.setFixedSize(22, 22)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pix = QPixmap(icon)
        self._icon.setPixmap(
            pix.scaled(
                18,
                18,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
        )
    )

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

        self._tog = QPushButton("")
        self._tog.setIcon(QIcon("assets/clock.png"))
        self._tog.setObjectName("sbToggle")
        self._tog.setFixedSize(36, 36)
        self._tog.clicked.connect(self.toggle)
        top_row.addWidget(self._tog)

        root.addWidget(top)
        root.addWidget(self._divider())

        # nav items
        nav = QFrame()
        self._nav_layout = QVBoxLayout(nav)
        self._nav_layout.setContentsMargins(6, 8, 6, 8)
        self._nav_layout.setSpacing(3)
        icons = {
        "forest": "assets/treeV2.png",
        "pet": "assets/petV2.png",
        "projects": "assets/list.png",
        "sounds": "assets/soso.png",
        "settings": "assets/setting.png",
                }
        tabs = [
    ("forest", icons["forest"], "Forest", ""),
    ("pet", icons["pet"], "Pet", ""),
    ("projects", icons["projects"], "Projects", ""),
    ("sounds", icons["sounds"], "Sounds", ""),
    ("settings", icons["settings"], "Settings", ""),
]
        for key, icon, label, badge in tabs:
            item = NavItem(icon, label, badge)
            item.clicked.connect(lambda k=key: self._on_click(k))
            self._nav_layout.addWidget(item)
            self._items[key] = item

        self._nav_layout.addStretch()
        self._nav_layout.addSpacing(8)
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
        theme = ThemeBuilder()
        p = theme.palette
        self.setStyleSheet(f"""
        /* Sidebar: Dark panel background with border */
        QFrame#Sidebar {{
            background: {p['panel_dark']};
            border: 1px solid {p['line']};
            border-radius: 14px;
        }}
        /* Top section: logo + toggle */
        QFrame#sbTop {{
            background: transparent;
            border-bottom: 1px solid {p['line']};
        }}
        /* Divider line */
        QFrame#sbDiv {{
            background: {p['line']};
            border: none;
        }}
        /* Logo text */
        QLabel#sbLogo {{
            font-size: 11px;
            font-weight: 700;
            color: {p['accent_soft']};
            letter-spacing: 0.5px;
        }}
        /* Toggle button (collapse/expand) */
        QPushButton#sbToggle {{
            background: {p['panel_mid']};
            border: 1px solid {p['line']};
            border-radius: 6px;
            font-size: 10px;
            color: {p['muted']};
        }}
        QPushButton#sbToggle:hover {{
            background: {p['panel_light']};
            color: {p['accent']};
        }}
        /* Navigation item: base styles */
        QWidget#NavItem {{
            border-radius: 9px;
            border: 1px solid transparent;
        }}
        QWidget#NavItem:hover {{
            background: {p['panel_mid']};
        }}
        /* Navigation item: active state */
        QWidget#NavItem[active=true] {{
            background: {p['panel_mid']};
            border-color: {p['accent']};
        }}
        /* Icon in nav item */
        QLabel#niIcon {{
            font-size: 15px;
        }}
        /* Label in nav item */
        QLabel#niLabel {{
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.5px;
            color: {p['muted']};
        }}
        QWidget#NavItem {{
        border-radius: 9px;
        border: 1px solid transparent;
        padding-left: 6px;
        }}
        QWidget#NavItem[active=true] QLabel#niLabel {{
            color: {p['accent']};
        }}
        QWidget#NavItem:hover QLabel#niLabel {{
            color: {p['accent_soft']};
        }}
        /* Badge: task/notification count */
        QLabel#niBadge {{
            font-size: 8px;
            font-weight: 700;
            color: {p['white']};
            background: {p['accent']};
            border: 1px solid {p['accent_dark']};
            border-radius: 8px;
            padding: 1px 5px;
        }}
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
        theme = ThemeBuilder()
        p = theme.palette
        self.setStyleSheet(f"""
        MainWindow {{
            background: {p['bg']};
        }}
        QStackedWidget#MainStack {{
            background: {p['panel']};
            border: 1px solid {p['line']};
            border-radius: 14px;
        }}
        """)
