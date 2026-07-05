from __future__ import annotations

from PySide6.QtCore import QObject, Slot


class MainController(QObject):
    def __init__(self, clock_controller, project_controller, parent=None):
        super().__init__(parent)
        self.clock_controller = clock_controller
        self.project_controller = project_controller
        self._active_task_id: str | None = None

        self.clock_controller.task_list_requested.connect(self.request_task_list)
        self.clock_controller.task_selected.connect(self.on_task_selected)
        self.clock_controller.model.work_session_completed.connect(self.on_work_session_completed)
        self.project_controller.task_list_ready.connect(self.clock_controller.view.open_task_chooser)

    @Slot()
    def request_task_list(self) -> None:
        self.project_controller.emit_task_choices()

    @Slot(str)
    def on_task_selected(self, task_id: str) -> None:
        self._active_task_id = task_id

    @Slot(int)
    def on_work_session_completed(self, _focused_seconds: int) -> None:
        if not self._active_task_id:
            return
        self.project_controller.increment_task_pomo(self._active_task_id)
