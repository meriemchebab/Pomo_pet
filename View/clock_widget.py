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
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .theme import ThemeBuilder

from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
class HoverButton(QPushButton):
    def __init__(self,text : str , icon_path :str):
        super().__init__()
        self._text = text
        self._icon_path = icon_path
    def enterEvent(self, event):
        self.setText(self._text)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setText("")
        super().leaveEvent(event)
    def set_icon(self):
        self.setIcon(QIcon(self._icon_path))
        self.setIconSize(QSize(20,20))

class AnalogTimerFace(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0
        self.remaining_text = "25:00"
        self.phase_text = "Focus time"
        self.theme = ThemeBuilder()
        self.setMinimumSize(220, 220)
        self.setMaximumSize(520, 520)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def sizeHint(self):
        return QSize(260, 260)

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

        # Use theme palette for timer face colors
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self.theme.palette["panel_light"]))
        p.drawEllipse(circle)

        # Track background
        track_pen = QPen(QColor(self.theme.palette["muted"]), 10)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(track_pen)
        p.drawArc(circle.adjusted(8, 8, -8, -8), 0, 360 * 16)

        # Progress arc (uses accent_dark for visual contrast)
        arc_pen = QPen(QColor(self.theme.palette["accent_dark"]), 12)
        arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(arc_pen)
        p.drawArc(circle.adjusted(8, 8, -8, -8), 90 * 16, int(-360 * self.progress * 16))

        # Hour ticks
        tick_pen = QPen(QColor(self.theme.palette["muted"]), 2)
        p.setPen(tick_pen)
        for i in range(12):
            angle = radians(i * 30 - 90)
            x1 = circle.center().x() + cos(angle) * (side * 0.37)
            y1 = circle.center().y() + sin(angle) * (side * 0.37)
            x2 = circle.center().x() + cos(angle) * (side * 0.42)
            y2 = circle.center().y() + sin(angle) * (side * 0.42)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Phase label (e.g., "Focus time")
        p.setPen(QColor(self.theme.palette["muted"]))
        phase_font = QFont(p.font())
        phase_font.setPointSize(11)
        phase_font.setWeight(QFont.Weight.DemiBold)
        p.setFont(phase_font)
        phase_rect = circle.adjusted(0, side * 0.18, 0, 0)
        p.drawText(phase_rect, Qt.AlignmentFlag.AlignHCenter, self.phase_text)

        # Remaining time (e.g., "25:00")
        p.setPen(QColor(self.theme.palette["text"]))
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
        long_break_minutes=30,
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

        p = ThemeBuilder().palette
        self.setStyleSheet(
            f"""
            QDialog {{
                background: {p['panel_dark']};
                border: 1px solid {p['line']};
                border-radius: 16px;
            }}
            QLabel {{
                color: {p['panel']};
                font-size: 13px;
                font-weight: 600;
            }}
            QLabel#dialogIntro {{
                color: {p['panel']};
                font-size: 14px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            QCheckBox {{
                color: {p['panel']};
                font-weight: 600;
            }}
            QDoubleSpinBox, QSpinBox {{
                background: {p['panel_light']};
                color: {p['text']};
                border: 1px solid {p['line']};
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton {{
                background: {p['panel_mid']};
                color: {p['panel']};
                border: 1px solid {p['line']};
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {p['accent']};
                color: {p['white']};
            }}
            """
        )


    def values(self) -> dict:
        return {
            "duration": int(self.duration_spin.value() * 60),
            "break_time": int(self.break_spin.value() * 60),
            "long_break_time": int(self.long_break_spin.value() * 60),
            "pomo_until_break": self.pomo_spin.value(),
            "auto_start_next_phase": self.auto_start_check.isChecked(),
        }


class TaskCard(QFrame):
    clicked = Signal(dict)

    def __init__(self, task_data: dict, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.setObjectName("taskCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.title_label = QLabel(task_data.get("title", "Untitled task"))
        self.title_label.setObjectName("taskTitle")

        self.project_label = QLabel(f"Project: {task_data.get('project', 'Unknown')}")
        self.project_label.setObjectName("taskProject")

        status = "Done" if task_data.get("done", False) else "Pending"
        self.status_label = QLabel(status)
        self.status_label.setObjectName("taskStatus")

        layout.addWidget(self.title_label)
        layout.addWidget(self.project_label)
        layout.addWidget(self.status_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.task_data)
        super().mousePressEvent(event)


class TaskChooserDialog(QDialog):
    task_selected = Signal(str)

    def __init__(self, tasks: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Task")
        self.setModal(True)
        self.setMinimumSize(420, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Choose a task")
        title.setObjectName("chooserTitle")
        layout.addWidget(title)

        subtitle = QLabel("Pick a task from any project. The timer starts as soon as you click one.")
        subtitle.setObjectName("chooserSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("taskList")
        self.list_widget.setSpacing(8)
        layout.addWidget(self.list_widget)

        self.select_btn = QPushButton("Start with selected task")
        self.select_btn.setObjectName("accentButton")
        self.select_btn.setEnabled(False)
        

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.setFixedSize(76,60)
        btns = QHBoxLayout()
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.select_btn)
        layout.addLayout(btns)

        self.cancel_btn.clicked.connect(self.reject)
        self.select_btn.clicked.connect(self.accept_selection)

        self.selected_task = None
        self.populate_tasks(tasks)

        p = ThemeBuilder().palette
        self.setStyleSheet(
            f"""
            QDialog {{
                background: {p['panel_dark']};
                border: 1px solid {p['line']};
                border-radius: 16px;
            }}
            QLabel#chooserTitle {{
                color: {p['panel']};
                font-size: 17px;
                font-weight: 800;
            }}
            QLabel#chooserSubtitle {{
                color: {p['text_dim']};
                font-size: 12px;
                font-weight: 600;
            }}
            QListWidget#taskList {{
                border: none;
                background: transparent;
            }}
            QFrame#taskCard {{
                background: {p['panel_mid']};
                border: 1px solid {p['line']};
                border-radius: 14px;
            }}
            QFrame#taskCard:hover {{
                background: {p['panel_light']};
                border: 1px solid {p['accent']};
            }}
            QFrame#taskCard[selected="true"] {{
                background: {p['panel_light']};
                border: 2px solid {p['accent_dark']};
            }}
            QLabel#taskTitle {{
                color: {p['text']};
                font-size: 14px;
                font-weight: 800;
            }}
            QLabel#taskProject {{
                color: {p['text_dim']};
                font-size: 12px;
                font-weight: 600;
            }}
            QLabel#taskStatus {{
                color: {p['accent_soft']};
                font-size: 11px;
                font-weight: 700;
            }}
            """
        )


    def populate_tasks(self, tasks: list[dict]):
        self.list_widget.clear()
        for task in tasks:
            item = QListWidgetItem(self.list_widget)
            card = TaskCard(task)
            card.clicked.connect(self.on_card_clicked)
            item.setSizeHint(card.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, card)

    def on_card_clicked(self, task_data: dict):
        self.selected_task = task_data
        self.select_btn.setEnabled(True)
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget is not None:
                widget.setProperty("selected", widget== task_data)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update()

    def accept_selection(self):
        if self.selected_task is not None:
            self.task_selected.emit(self.selected_task["id"])
            self.accept()
        self.accept()


class ClockWidget(QFrame):
    settings_requested = Signal(dict)
    choose_task_requested = Signal()
    task_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = ThemeBuilder()
        self.setObjectName("panelCard")
        self.setMinimumHeight(360)
        self.setMaximumHeight(820)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._seconds = 25 * 60
        self._total = 25 * 60
        self._phase_name = "Focus time"
        self._cycle_index = 1
        self._cycle_total = 4
        self._break_seconds = 5 * 60
        self._long_break_seconds = 30 * 60
        self._auto_start_next_phase = False

        self._focused_today_seconds = 0
        self._completed_sessions = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        

        self.cycle_label = QLabel(f"{self._cycle_index} / {self._cycle_total}")
        self.cycle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cycle_label.setObjectName("cycleLabel")

        self.face = AnalogTimerFace()
        self.face.phase_text = self._phase_name

        self.meta_label = QLabel("Next break 05:00")
        self.meta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.meta_label.setObjectName("metaLabel")

        self.stats_card = QFrame()
        self.stats_card.setObjectName("statsCard")
        stats_layout = QVBoxLayout(self.stats_card)
        stats_layout.setContentsMargins(14, 12, 14, 12)
        stats_layout.setSpacing(2)

        self.focus_stat_label = QLabel("Focused today")
        self.focus_stat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_stat_label.setObjectName("statTitle")

        self.focus_time_label = QLabel("0m")
        self.focus_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_time_label.setObjectName("statValue")

        self.focus_sessions_label = QLabel("0 sessions completed")
        self.focus_sessions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_sessions_label.setObjectName("statMeta")

        stats_layout.addWidget(self.focus_stat_label)
        stats_layout.addWidget(self.focus_time_label)
        stats_layout.addWidget(self.focus_sessions_label)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("accentButton")
        self.choose_task_btn = QPushButton("Choose Task")
        self.choose_task_btn.setObjectName("accentButton")
        controls.addWidget(self.start_btn)
        controls.addWidget(self.choose_task_btn)


        presets = QHBoxLayout()
        presets.setSpacing(8)
        presets.setContentsMargins(0, 0, 0, 10)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setIcon(QIcon("assets/pause.png"))
        self.pause_btn.setObjectName("secondaryButton")
        self.pause_btn.setFixedSize(76, 40)
        self.skip_btn = HoverButton("Skip", "assets/skip.png")
        self.reset_btn = HoverButton("Reset", "assets/reset.png")

        for btn in [self.skip_btn, self.reset_btn]:
            btn.set_icon()
            btn.setObjectName("secondaryButton")
            btn.setFixedSize(76, 40)
        self.quick_setup_btn = QPushButton("Setup")
        self.quick_setup_btn.setObjectName("secondaryButton")
        self.quick_setup_btn.setIcon(QIcon("assets/clock.png"))
        self.quick_setup_btn.setIconSize(QSize(20, 20))
        self.quick_setup_btn.setFixedSize(120, 40)
        presets.addWidget(self.pause_btn)
        presets.addWidget(self.skip_btn)
        presets.addWidget(self.reset_btn)
        presets.addWidget(self.quick_setup_btn)
        presets.addStretch()

        self.active_task_label = QLabel("🎯 Task: None selected")
        self.active_task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.active_task_label.setObjectName("activeTaskLabel")

        # root.addWidget(self.phase_label)
        root.addLayout(presets, Qt.AlignmentFlag.AlignLeft)
        root.addWidget(self.stats_card)
        root.addWidget(self.active_task_label)
        root.addWidget(self.cycle_label, alignment=Qt.AlignmentFlag.AlignLeft)
        root.addWidget(self.face, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.meta_label)
        root.addLayout(controls)

        
        

        self.quick_setup_btn.clicked.connect(self.open_quick_setup)
        self.choose_task_btn.clicked.connect(self.choose_task_requested.emit)

        self._apply_style()
        self.refresh_focus_stats()
        self.refresh()

    def _apply_style(self):
        """Generate stylesheet using theme palette for consistency."""
        p = self.theme.palette
        self.setStyleSheet(
            f"""
            /* Main card styling */
            QFrame#panelCard {{
                background: {p['panel']};
                border: 1px solid {p['line']};
                border-radius: 20px;
                min-height: 400px;
                max-height: 780px;
                min-width: 280px;
            }}
            /* Active Task label */
            QLabel#activeTaskLabel {{
                color: {p['accent_dark']};
                font-size: 13px;
                font-weight: 700;
                padding: 4px 8px;
                background: {p['panel_light']};
                border-radius: 8px;
            }}
            /* Cycle indicator label */
            QLabel#cycleLabel {{
                color: {p['text']};
                font-size: 12px;
                font-weight: 800;
            }}

            /* Meta information label */
            QLabel#metaLabel {{
                color: {p['muted']};
                font-size: 12px;
                font-weight: 600;
            }}
            /* Stats card container */
            QFrame#statsCard {{
                background: {p['panel']};
                border: 1px solid {p['line']};
                border-radius: 16px;
                max-height: 170px;
            }}
            /* Stat title (e.g., "Focused today") */
            QLabel#statTitle {{
                color: {p['muted']};
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.4px;
            }}
            /* Stat main value (e.g., "3h 25m") */
            QLabel#statValue {{
                color: {p['text']};
                font-size: 20px;
                font-weight: 800;
            }}
            /* Stat meta (e.g., "5 sessions completed") */
            QLabel#statMeta {{
                color: {p['muted']};
                font-size: 12px;
                font-weight: 600;
            }}
            /* Dialog intro text */
            QLabel#dialogIntro {{
                color: {p['text']};
                font-size: 13px;
                margin-bottom: 6px;
            }}
            /* Default button styling */
            QPushButton {{
                min-height: 20px;
                border-radius: 10px;
                padding: 8px 8px;
                font-size: 13px;
                font-weight: 700;
                border: 1px solid {p['line']};
                background: {p['panel_light']};
                color: {p['text']};
            }}
            QPushButton:hover {{
                background: {p['panel_mid']};
            }}
            /* Primary action button */
            QPushButton#accentButton {{
                background: {p['accent']};
                color: {p['white']};
                border: none;
            }}
            QPushButton#accentButton:hover {{
                background: {p['accent_dark']};
            }}
            /* Secondary button */
            QPushButton#secondaryButton {{
                background: {p['panel']};
            }}
            QPushButton#secondaryButton:hover {{
                background: {p['panel_light']};
            }}
            /* Dialog background & text styling */
            QDialog {{
                background: {p['panel_dark']};
            }}
            QDialog QLabel {{
                color: {p['panel']};
                font-size: 13px;
                font-weight: 600;
            }}
            /* Number input fields */
            QDoubleSpinBox, QSpinBox {{
                min-height: 20px;
                border: 1px solid {p['line']};
                border-radius: 10px;
                padding: 4px 8px;
                background: {p['panel_light']};
                color: {p['text']};
            }}
            /* Checkbox styling */
            QCheckBox {{
                color: {p['panel']};
                spacing: 8px;
            }}
            """
        )


    def _format_focus_time(self, total_seconds: int) -> str:
        total_minutes = total_seconds // 60
        hours, minutes = divmod(total_minutes, 60)

        if hours > 0:
            return f"{hours}h {minutes:02d}m"
        return f"{minutes}m"

    def refresh_focus_stats(self):
        self.focus_time_label.setText(self._format_focus_time(self._focused_today_seconds))

        if self._completed_sessions == 1:
            self.focus_sessions_label.setText("1 session completed")
        else:
            self.focus_sessions_label.setText(f"{self._completed_sessions} sessions completed")

    def set_focus_stats(self, focused_seconds: int, completed_sessions: int):
        """set the focus time label"""
        self._focused_today_seconds += max(0, focused_seconds)
        self._completed_sessions = max(0, completed_sessions)
        self.refresh_focus_stats()


    def reset_focus_stats(self):
        self._focused_today_seconds = 0
        self._completed_sessions = 0
        self.refresh_focus_stats()

    def open_quick_setup(self):
        """open a dialog box to change the pomodoro session settings"""
        dialog = QuickSetupDialog(
            duration_minutes=self._total / 60,
            break_minutes=self._break_seconds / 60,
            long_break_minutes=int(self._long_break_seconds / 60),
            pomo_until_break=self._cycle_total,
            auto_start_next_phase=self._auto_start_next_phase,
            parent=self,
        )
        if dialog.exec():
            values = dialog.values()
            self.apply_settings(values)
            self.settings_requested.emit(values)

    def open_task_chooser(self, projects: list[dict]) -> None:
        flat_tasks = []
        for project in projects:
            for task in project.get("tasks", []):
                task_copy = dict(task)
                task_copy["project"] = project.get("title", "Unknown")
                flat_tasks.append(task_copy)

        dialog = TaskChooserDialog(flat_tasks, parent=self)
        dialog.task_selected.connect(self.task_selected.emit)
        dialog.exec()

    def set_active_task(self, task_title: str, project_title: str = ""):
        if project_title:
            self.active_task_label.setText(f"🎯 Task: {task_title} ({project_title})")
        else:
            self.active_task_label.setText(f"🎯 Task: {task_title}")


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
        
        self.cycle_label.setText(f"Work {self._cycle_index} of {self._cycle_total}")
        self.meta_label.setText(f"Next break {self._break_seconds // 60:02d}:00")
        self.face.phase_text = self._phase_name
        self.refresh()

    def set_phase_info(self, phase_name: str, cycle_index: int, cycle_total: int):
        """function to change phase labels , use when a phase changes """
        self._phase_name = phase_name
        self._cycle_index = cycle_index
        self._cycle_total = cycle_total
        
        self.cycle_label.setText(f"{cycle_index} / {cycle_total}")
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

    def _on_pause_toggled(self, checked: bool):
        """update pause button text based on checked state"""
        if checked:
            self.pause_btn.setText("Resume")
            
        else:
            self.pause_btn.setText("Pause")
