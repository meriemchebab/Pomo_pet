from __future__ import annotations

from math import cos, sin, radians

from PySide6.QtCore import Qt, QSize, QRectF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .theme import PALETTE


class AnalogTimerFace(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0
        self.remaining_text = "25:00"
        self.phase_text = "Focus time"
        self.setMinimumSize(300, 300)

    def sizeHint(self):
        return QSize(320, 320)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(14, 14, -14, -14)
        side = min(rect.width(), rect.height())
        circle = QRectF(
            rect.center().x() - side / 2,
            rect.center().y() - side / 2,
            side,
            side,
        )

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#f2ead7"))
        p.drawEllipse(circle)

        track_pen = QPen(QColor("#d8cfb5"), 10)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(track_pen)
        p.drawArc(circle.adjusted(8, 8, -8, -8), 0, 360 * 16)

        arc_pen = QPen(QColor(PALETTE["accent_dark"]), 12)
        arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(arc_pen)
        p.drawArc(circle.adjusted(8, 8, -8, -8), 90 * 16, int(-360 * self.progress * 16))

        tick_pen = QPen(QColor("#9b9075"), 2)
        p.setPen(tick_pen)
        for i in range(12):
            angle = radians(i * 30 - 90)
            x1 = circle.center().x() + cos(angle) * (side * 0.37)
            y1 = circle.center().y() + sin(angle) * (side * 0.37)
            x2 = circle.center().x() + cos(angle) * (side * 0.42)
            y2 = circle.center().y() + sin(angle) * (side * 0.42)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        p.setPen(QColor("#8a7f65"))
        phase_font = QFont(p.font())
        phase_font.setPointSize(11)
        phase_font.setWeight(QFont.Weight.DemiBold)
        p.setFont(phase_font)
        phase_rect = circle.adjusted(0, side * 0.18, 0, 0)
        p.drawText(phase_rect, Qt.AlignmentFlag.AlignHCenter, self.phase_text)

        p.setPen(QColor(PALETTE["text"]))
        time_font = QFont(p.font())
        time_font.setPointSize(26)
        time_font.setBold(True)
        p.setFont(time_font)
        p.drawText(circle, Qt.AlignmentFlag.AlignCenter, self.remaining_text)


class QuickSetupDialog(QDialog):
    def __init__(
        self,
        duration_minutes: float = 25,
        break_minutes: float = 5,
        pomo_until_break: int = 4,
        long_break_minutes = 30,
        auto_start_next_phase: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Quick Setup")
        self.setModal(True)
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)

        intro = QLabel("Adjust your Pomodoro settings.")
        intro.setObjectName("dialogIntro")
        layout.addWidget(intro)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(1, 180)
        self.duration_spin.setSuffix(" min")
        self.duration_spin.setDecimals(0)
        self.duration_spin.setValue(duration_minutes)

        self.break_spin = QDoubleSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setSuffix(" min")
        self.break_spin.setDecimals(0)
        self.break_spin.setValue(break_minutes)
        
        self.long_break_spin = QDoubleSpinBox()
        self.long_break_spin.setRange(1, 180)
        self.long_break_spin.setSuffix(" min")
        self.long_break_spin.setDecimals(0)
        self.long_break_spin.setValue(long_break_minutes)

        self.pomo_spin = QSpinBox()
        self.pomo_spin.setRange(1, 12)
        self.pomo_spin.setValue(pomo_until_break)

        self.auto_start_check = QCheckBox("Auto start next phase")
        self.auto_start_check.setChecked(auto_start_next_phase)

        form.addRow("Work duration", self.duration_spin)
        form.addRow("Break duration", self.break_spin)
        form.addRow("Long Break duration", self.long_break_spin)
        form.addRow("Pomodoros until long break", self.pomo_spin)
        form.addRow("", self.auto_start_check)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> dict:
        return {
            "duration": int(self.duration_spin.value() * 60),
            "break_time": int(self.break_spin.value() * 60),
            "long_break_time": int(self.long_break_spin.value() * 60),
            "pomo_until_break": self.pomo_spin.value(),
            "auto_start_next_phase": self.auto_start_check.isChecked(),
        }


class ClockWidget(QFrame):
    settings_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panelCard")

        self._seconds = 25 * 60
        self._total = 25 * 60
        self._phase_name = "Focus time"
        self._cycle_index = 1
        self._cycle_total = 4
        self._break_seconds = 5 * 60
        self._long_break_seconds = 30 * 60
        self._auto_start_next_phase = False

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        self.phase_label = QLabel(self._phase_name)
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.phase_label.setObjectName("phaseLabel")

        self.cycle_label = QLabel(f"Work {self._cycle_index} of {self._cycle_total}")
        self.cycle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cycle_label.setObjectName("cycleLabel")

        self.face = AnalogTimerFace()
        self.face.phase_text = self._phase_name

        self.meta_label = QLabel("Next break 05:00")
        self.meta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.meta_label.setObjectName("metaLabel")

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("accentButton")

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setObjectName("secondaryButton")

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("secondaryButton")

        controls.addWidget(self.start_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.reset_btn)

        presets = QGridLayout()
        presets.setHorizontalSpacing(10)
        presets.setVerticalSpacing(10)

        self.work_btn = QPushButton("Work")
        self.short_break_btn = QPushButton("Short Break")
        self.long_break_btn = QPushButton("Long Break")
        self.skip_btn = QPushButton("Skip")
        self.quick_setup_btn = QPushButton("Quick Setup")

        for btn in [
            self.work_btn,
            self.short_break_btn,
            self.long_break_btn,
            self.skip_btn,
            self.quick_setup_btn,
        ]:
            btn.setObjectName("softButton")
            btn.setMinimumHeight(38)

        presets.addWidget(self.work_btn, 0, 0)
        presets.addWidget(self.short_break_btn, 0, 1)
        presets.addWidget(self.long_break_btn, 1, 0)
        presets.addWidget(self.skip_btn, 1, 1)
        presets.addWidget(self.quick_setup_btn, 2, 0, 1, 2)

        root.addWidget(self.phase_label)
        root.addWidget(self.cycle_label)
        root.addWidget(self.face, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.meta_label)
        root.addLayout(controls)
        root.addLayout(presets)

        self.quick_setup_btn.clicked.connect(self.open_quick_setup)

        self.setStyleSheet(
            """
            QFrame#panelCard {
                background: #fbf7ee;
                border: 1px solid #e4dcc8;
                border-radius: 20px;
            }
            QLabel#phaseLabel {
                color: #7d745f;
                font-size: 14px;
                font-weight: 700;
            }
            QLabel#cycleLabel {
                color: #2f2a22;
                font-size: 24px;
                font-weight: 800;
            }
            QLabel#metaLabel {
                color: #8a7f65;
                font-size: 13px;
                font-weight: 600;
            }
            QLabel#dialogIntro {
                color: #6f6654;
                font-size: 13px;
                margin-bottom: 6px;
            }
            QPushButton {
                min-height: 44px;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
                font-weight: 700;
                border: 1px solid #d8cfb9;
                background: #f4eedf;
                color: #2e2a22;
            }
            QPushButton:hover {
                background: #eee6d3;
            }
            QPushButton#accentButton {
                background: #7a5c2e;
                color: white;
                border: none;
            }
            QPushButton#accentButton:hover {
                background: #694d24;
            }
            QPushButton#secondaryButton {
                background: #f7f2e8;
            }
            QPushButton#softButton {
                background: #f3ecdc;
                color: #5e5442;
            }
            QDialog {
                background: #fcf9f1;
            }
            QDoubleSpinBox, QSpinBox {
                min-height: 36px;
                border: 1px solid #d7ceb8;
                border-radius: 10px;
                padding: 4px 8px;
                background: white;
            }
            QCheckBox {
                color: #3b352b;
                spacing: 8px;
            }
            """
        )

        self.refresh()

    def open_quick_setup(self):
        """open a dialog box to change the pomodoro session settings"""
        dialog = QuickSetupDialog(
            duration_minutes=self._total / 60,
            break_minutes=self._break_seconds / 60,
            long_break_minutes= int(self._long_break_seconds / 60),
            pomo_until_break=self._cycle_total,
            auto_start_next_phase=self._auto_start_next_phase,
            parent=self,
        )
        if dialog.exec():
            values = dialog.values()
            self.apply_settings(values)
            # values of the changes back to the controller
            self.settings_requested.emit(values)

    def apply_settings(self, settings: dict):
        """function to set the new prefered settings and update the UI , use after dialog box get closed"""
        self._total = int(settings["duration"])
        self._seconds = self._total
        self._break_seconds = int(settings["break_time"])
        self._long_break_seconds = int(settings["long_break_time"])
        self._cycle_total = int(settings["pomo_until_break"])
        self._auto_start_next_phase = bool(settings["auto_start_next_phase"])

        self._cycle_index = 1
        self._phase_name = "Focus time"
        self.phase_label.setText(self._phase_name)
        self.cycle_label.setText(f"Work {self._cycle_index} of {self._cycle_total}")
        self.meta_label.setText(f"Next break {self._break_seconds // 60:02d}:00")
        self.face.phase_text = self._phase_name
        self.refresh()

    def set_phase_info(self, phase_name: str, cycle_index: int, cycle_total: int):
        """function to change phase labels , use when a phase changes """
        self._phase_name = phase_name
        self._cycle_index = cycle_index
        self._cycle_total = cycle_total
        self.phase_label.setText(phase_name)
        self.cycle_label.setText(f"Work {cycle_index} of {cycle_total}")
        self.face.phase_text = phase_name
        self.face.update()

    def set_duration(self, seconds: int):
        """update the clock to full time at the start of each phase , use when a new phase starts"""
        self._total = max(1, seconds)
        self._seconds = max(0, seconds)
        self.refresh()

    def set_remaining(self, seconds: int):
        """call each second to update the clock circle"""
        self._seconds = max(0, seconds)
        self.refresh()

    def refresh(self):
        """update the clock numbers not the UI"""
        mins, secs = divmod(self._seconds, 60)
        self.face.remaining_text = f"{mins:02d}:{secs:02d}"
        self.face.progress = 1 - (self._seconds / max(1, self._total))
        self.face.update()
# New user preferences from dialog → apply_settings()

# Phase switched from work to break → set_phase_info() + set_duration()

# Timer ticking each second → set_remaining()