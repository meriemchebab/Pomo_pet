from __future__ import annotations

from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(42, 24)

        self._checked = checked
        self._offset = 20 if checked else 3

        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(170)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._track_off = QColor("#20372c")
        self._track_on = QColor("#49752f")
        self._border_off = QColor(255, 255, 255, 18)
        self._border_on = QColor(155, 197, 95, 70)
        self._thumb = QColor("#9cc661")

    def isChecked(self):
        return self._checked

    def setChecked(self, value: bool):
        if self._checked == value:
            return
        self._checked = value
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(20 if self._checked else 3)
        self._anim.start()
        self.toggled.emit(self._checked)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
        super().mousePressEvent(event)

    def getOffset(self):
        return self._offset

    def setOffset(self, value):
        self._offset = value
        self.update()

    offset = Property(float, getOffset, setOffset)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)
        radius = rect.height() / 2

        p.setPen(QPen(self._border_on if self._checked else self._border_off, 1))
        p.setBrush(self._track_on if self._checked else self._track_off)
        p.drawRoundedRect(rect, radius, radius)

        knob = QRectF(self._offset, 3, 18, 18)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._thumb)
        p.drawEllipse(knob)

        p.end()


class SectionTitle(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("sectionTitle")


class SoundRow(QFrame):
    volume_changed = Signal(str, int)
    toggled = Signal(str, bool)

    def __init__(self, key: str, icon: str, title: str, value: int, checked: bool, parent=None):
        super().__init__(parent)
        self.key = key
        self.setObjectName("soundRow")

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        self.icon_label = QLabel(icon)
        self.icon_label.setObjectName("iconBox")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(34, 34)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("rowTitle")
        self.title_label.setMinimumWidth(102)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("soundSlider")
        self.slider.setRange(0, 100)
        self.slider.setValue(value)
        self.slider.setFixedWidth(118)

        self.switch = ToggleSwitch(checked=checked)

        root.addWidget(self.icon_label)
        root.addWidget(self.title_label)
        root.addStretch()
        root.addWidget(self.slider)
        root.addSpacing(4)
        root.addWidget(self.switch)

        self.slider.valueChanged.connect(lambda v: self.volume_changed.emit(self.key, v))
        self.switch.toggled.connect(lambda c: self.toggled.emit(self.key, c))


class NotificationRow(QFrame):
    sound_changed = Signal(str, str)
    toggled = Signal(str, bool)

    def __init__(self, event_key: str, icon: str, label: str, sound="Forest Bell", checked=True, parent=None):
        super().__init__(parent)
        self.event_key = event_key
        self.setObjectName("soundRow")

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        self.icon_label = QLabel(icon)
        self.icon_label.setObjectName("iconBox")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(34, 34)

        self.title_label = QLabel(label)
        self.title_label.setObjectName("rowTitle")
        self.title_label.setFixedWidth(64)
        self.title_label.setWordWrap(True)

        self.combo = QComboBox()
        self.combo.setObjectName("soundCombo")
        self.combo.addItems([
            "Bell sound",
            "game win",
            "Keys Drop",
            "Page chime",
            "Fantasy win",
        ])
        self.combo.setCurrentText(sound)
        self.combo.setMinimumHeight(38)

        self.switch = ToggleSwitch(checked=checked)

        root.addWidget(self.icon_label)
        root.addWidget(self.title_label)
        root.addWidget(self.combo, 1)
        root.addSpacing(4)
        root.addWidget(self.switch)

        self.combo.currentTextChanged.connect(lambda s: self.sound_changed.emit(self.event_key, s))
        self.switch.toggled.connect(lambda c: self.toggled.emit(self.event_key, c))


class MasterVolumeRow(QFrame):
    volume_changed = Signal(int)

    def __init__(self, value=60, parent=None):
        super().__init__(parent)
        self.setObjectName("soundRow")

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        self.icon_label = QLabel("🔊")
        self.icon_label.setObjectName("iconBox")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(34, 34)

        self.title_label = QLabel("Master")
        self.title_label.setObjectName("rowTitle")
        self.title_label.setFixedWidth(72)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("soundSlider")
        self.slider.setRange(0, 100)
        self.slider.setValue(value)

        self.value_label = QLabel(f"{value}%")
        self.value_label.setObjectName("percentLabel")
        self.value_label.setFixedWidth(34)

        self.slider.valueChanged.connect(self._on_value_changed)

        root.addWidget(self.icon_label)
        root.addWidget(self.title_label)
        root.addWidget(self.slider, 1)
        root.addWidget(self.value_label)

    def _on_value_changed(self, v: int):
        self.value_label.setText(f"{v}%")
        self.volume_changed.emit(v)


class WhiteNoiseWidget(QFrame):
    track_volume_changed = Signal(str, int)
    track_toggled = Signal(str, bool)
    master_volume_changed = Signal(int)
    notification_sound_changed = Signal(str, str)
    notification_toggled = Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panelCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(9)

        title = QLabel("WHITE NOISE")
        title.setObjectName("pageTitle")
        root.addWidget(title)
        root.addSpacing(2)

        self.sound_rows: dict[str, SoundRow] = {}
        sound_configs = [
            ("rain", "🌧", "Rain", 58, True),
            ("ocean", "🌊", "Ocean", 34, False),
            ("fireplace", "🔥", "Fireplace", 39, False),
            ("forest_wind", "🍃", "Forest", 20, True),
            ("clock", "☕", "Clock", 31, False),
        ]

        for key, icon, name, val, checked in sound_configs:
            row = SoundRow(key, icon, name, val, checked)
            row.volume_changed.connect(self.track_volume_changed.emit)
            row.toggled.connect(self.track_toggled.emit)
            self.sound_rows[key] = row
            root.addWidget(row)

        root.addSpacing(8)
        root.addWidget(SectionTitle("NOTIFICATION SOUNDS"))

        self.notification_rows: dict[str, NotificationRow] = {}
        notif_configs = [
            ("start", "🔔", "start"),
            ("break", "🎵", "break"),
            ("finish", "✅", "finish"),
        ]

        for event_key, icon, label in notif_configs:
            row = NotificationRow(event_key, icon, label)
            row.sound_changed.connect(self.notification_sound_changed.emit)
            row.toggled.connect(self.notification_toggled.emit)
            self.notification_rows[event_key] = row
            root.addWidget(row)

        root.addSpacing(8)
        root.addWidget(SectionTitle("MASTER VOLUME"))

        self.master_volume_row = MasterVolumeRow(60)
        self.master_volume_row.volume_changed.connect(self.master_volume_changed.emit)
        root.addWidget(self.master_volume_row)
        root.addStretch()

        self.setStyleSheet("""
        QFrame#panelCard {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #143427,
                stop:1 #102c21
            );
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }

        QLabel#pageTitle {
            color: rgba(213, 226, 194, 0.72);
            font-size: 17px;
            font-weight: 800;
            letter-spacing: 1.8px;
            padding-left: 2px;
        }

        QLabel#sectionTitle {
            color: rgba(187, 204, 170, 0.52);
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 1.6px;
            padding-left: 2px;
            padding-top: 2px;
        }

        QFrame#soundRow {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.045);
            border-radius: 14px;
        }

        QLabel#iconBox {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.04);
            border-radius: 10px;
            color: #eff4e7;
            font-size: 17px;
        }

        QLabel#rowTitle {
            color: #e7eedc;
            font-size: 15px;
            font-weight: 600;
        }

        QLabel#percentLabel {
            color: rgba(202, 217, 188, 0.72);
            font-size: 12px;
            font-weight: 600;
        }

        QSlider::groove:horizontal {
            height: 5px;
            background: rgba(20, 40, 28, 0.75);
            border-radius: 3px;
        }

        QSlider::sub-page:horizontal {
            background: #8eb85d;
            border-radius: 3px;
        }

        QSlider::handle:horizontal {
            background: #9ec764;
            width: 15px;
            height: 15px;
            margin: -5px 0;
            border-radius: 7px;
            border: 1px solid rgba(255,255,255,0.12);
        }

        QComboBox#soundCombo {
            background: #f3f1eb;
            color: #26241f;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 14px;
            font-weight: 600;
        }

        QComboBox#soundCombo::drop-down {
            border: none;
            width: 24px;
        }

        QComboBox#soundCombo QAbstractItemView {
            background: white;
            color: #222;
            selection-background-color: #dce8c8;
        }
        """)