from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot

from Model.clock_model import Clock, ClockSettings, Phase
from View.clock_widget import ClockWidget


class ClockController(QObject):
    task_list_requested = Signal()
    task_selected = Signal(str)

    def __init__(self, parent=None, settings: Optional[ClockSettings] = None):
        super().__init__(parent)
        self.view = ClockWidget()
        self.model = Clock(settings)
        self.view.start_btn.clicked.connect(self.start_pomo)
        self.view.pause_btn.clicked.connect(self.toggle_pause)
        self.view.reset_btn.clicked.connect(self.reset_pomo)
        self.view.skip_btn.clicked.connect(self.skip)
        self.view.choose_task_requested.connect(self.request_task_choices)
        self.view.task_selected.connect(self.select_task)
        self.view.settings_requested.connect(self.on_settings_changed)

        self.model.time_remaining.connect(self.view.set_remaining)
        self.model.time_focused.connect(self.on_time_focused)
        self.model.phase_changed.connect(self.on_phase_change)
        self.model.work_session_completed.connect(self.on_work_session_completed)

    @Slot()
    def request_task_choices(self) -> None:
        self.task_list_requested.emit()

    @Slot(str)
    def select_task(self, task_id: str) -> None:
        self.task_selected.emit(task_id)
        self.model.change_phase(Phase.WORK)
        self.model.time_left = int(self.model.settings.duration)
        self.view.set_phase_info("Focus time", self.model.completed_pomos, self.model.settings.pomo_until_break)
        self.view.set_duration(self.model.time_left)
        self.start_pomo()

    def start_pomo(self):
        self.view.set_duration(self.model.time_left)
        self.model.start()

    def reset_pomo(self):
        self.model.reset_timer()
        self.view.set_duration(self.model.time_left)

    def toggle_pause(self):
        """toggle between pause and resume"""
        if self.view.pause_btn.text() == "Resume":
            self.view.pause_btn.setText("Pause")
            self.model.start()
        else:
            self.view.pause_btn.setText("Resume")
            self.model.pause()

    def on_settings_changed(self, values: dict):
        """handle settings changes from the quick setup dialog"""
        self.view.apply_settings(values)
        self.model.settings.update_settings(values)
        self.reset_pomo()

    def on_phase_change(self, phase: Phase):
        phase_name = phase.name.replace("_", " ").title()
        self.view.set_phase_info(
            phase_name=phase_name,
            cycle_index=self.model.completed_pomos,
            cycle_total=self.model.settings.pomo_until_break,
        )

    def on_time_focused(self, focused_seconds: int):
        self.view.set_focus_stats(
            focused_seconds,
            completed_sessions=self.model.completed_pomos,
        )

    @Slot(int)
    def on_work_session_completed(self, focused_seconds: int) -> None:
        return

    def skip(self):
        if self.model.phase == Phase.WORK:
            phase = Phase.SHORT_BREAK
        else:
            phase = Phase.WORK
        self.model.change_phase(phase)
        self.model.reset_timer()
        self.on_phase_change(phase=phase)
