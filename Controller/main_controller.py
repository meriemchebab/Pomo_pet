from __future__ import annotations

from PySide6.QtCore import QObject, Slot


class MainController(QObject):
    def __init__(self, clock_controller, project_controller, white_noise_controller=None, parent=None):
        super().__init__(parent)
        self.clock_controller = clock_controller
        self.project_controller = project_controller
        self.white_noise_controller = white_noise_controller
        self._active_task_id: str | None = None

        self.clock_controller.task_list_requested.connect(self.request_task_list)
        self.clock_controller.task_selected.connect(self.on_task_selected)
        self.clock_controller.model.phase_changed.connect(self.on_phase_changed)
        self.clock_controller.model.work_session_completed.connect(self.on_work_session_completed)
        self.project_controller.task_list_ready.connect(self.clock_controller.view.open_task_chooser)

    @Slot()
    def request_task_list(self) -> None:
        self.project_controller.emit_task_choices()

    @Slot(str)
    def on_task_selected(self, task_id: str) -> None:
        self._active_task_id = task_id

        # Update visual active task label on clock view
        if hasattr(self.project_controller, "model") and self.project_controller.model:
            try:
                task_key = int(task_id)
                task = self.project_controller.model.get_task(task_key)
                if task:
                    project = self.project_controller.model.get_project(task.ID_P)
                    proj_title = project.name if project else ""
                    task_title = task.discription or f"Task #{task.ID_T}"
                    self.clock_controller.view.set_active_task(task_title, proj_title)
            except Exception as e:
                print("Error updating active task display:", e)


    @Slot(object)
    def on_phase_changed(self, phase) -> None:
        if self.white_noise_controller and hasattr(self.white_noise_controller, "engine"):
            engine = self.white_noise_controller.engine
            notif_settings = getattr(self.white_noise_controller.view, "notification_rows", {})
            
            # Map phase to notification row key ('start', 'break', 'finish')
            from Model.clock_model import Phase
            if phase == Phase.WORK:
                event_key = "start"
            else:
                event_key = "break"
            
            if event_key in notif_settings:
                row = notif_settings[event_key]
                if row.switch.isChecked():
                    sound_name = row.combo.currentText()
                    engine.play_notification(sound_name)

    @Slot(int)
    def on_work_session_completed(self, _focused_seconds: int) -> None:
        if self.white_noise_controller and hasattr(self.white_noise_controller, "engine"):
            engine = self.white_noise_controller.engine
            notif_settings = getattr(self.white_noise_controller.view, "notification_rows", {})
            if "finish" in notif_settings:
                row = notif_settings["finish"]
                if row.switch.isChecked():
                    sound_name = row.combo.currentText()
                    engine.play_notification(sound_name)

        if not self._active_task_id:
            return
        self.project_controller.increment_task_pomo(self._active_task_id)

