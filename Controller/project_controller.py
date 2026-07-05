from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from Model.tasks_manager_model import ProjectManager


class ProjectController(QObject):
    task_list_ready = Signal(list)

    def __init__(self, view=None, parent=None):
        super().__init__(parent)
        self.model = ProjectManager()
        self.view = None
        if view is not None:
            self.set_view(view)

    def set_view(self, view) -> None:
        self.view = view
        self.view.new_project_requested.connect(self.add_project)
        self.view.delete_project_requested.connect(self.delete_project)
        self.view.add_task_requested.connect(self.add_task)
        self.view.delete_task_requested.connect(self.delete_task)
        self.view.toggle_task_requested.connect(self.toggle_task)
        self.view.focus_task_requested.connect(self.focus_task)
        self.refresh_view()

    @Slot(str)
    def add_project(self, name: str = "") -> None:
        self.model.add_project(name=name or "work")
        self.refresh_view()

    @Slot(str)
    def delete_project(self, project_id: str) -> None:
        try:
            self.model.delete_project(int(project_id))
        except ValueError:
            return
        self.refresh_view()

    @Slot(str, str)
    def add_task(self, project_id: str, title: str) -> None:
        try:
            project_key = int(project_id)
        except ValueError:
            return
        self.model.add_task(project_key, title)
        self.refresh_view()

    @Slot(str)
    def delete_task(self, task_id: str) -> None:
        try:
            task_key = int(task_id)
        except ValueError:
            return
        self.model.delete_task(task_key)
        self.refresh_view()

    @Slot(str, bool)
    def toggle_task(self, task_id: str, done: bool) -> None:
        try:
            task_key = int(task_id)
        except ValueError:
            return
        self.model.update_task(task_key, status="done" if done else "undone")
        self.refresh_view()

    @Slot(str)
    def focus_task(self, task_id: str) -> None:
        # Hook for the clock / focus screen later.
        return

    def refresh_view(self) -> None:
        if self.view is None:
            return

        self.view.set_projects_section(self._build_projects_payload())

    def _build_projects_payload(self) -> list[dict]:
        projects_data = []
        for project in self.model.projects:
            projects_data.append(
                {
                    "id": str(project.ID_P),
                    "title": project.name,
                    "color": project.tag or "#6c7a89",
                    "expanded": True,
                    "tasks": [
                        {
                            "id": str(task.ID_T),
                            "title": task.discription,
                            "tomatoes": task.pomo_num,
                            "done": task.status == "done",
                        }
                        for task in project.tasks
                    ],
                }
            )
        return projects_data

    def get_task_choices(self) -> list[dict]:
        choices: list[dict] = []
        for project in self.model.projects:
            choices.append(
                {
                    "id": str(project.ID_P),
                    "title": project.name,
                    "tasks": [
                        {
                            "id": str(task.ID_T),
                            "title": task.discription,
                            "project_name": project.name,
                            "project_id": str(project.ID_P),
                            "tomatoes": task.pomo_num,
                            "done": task.status == "done",
                        }
                        for task in project.tasks
                    ],
                }
            )
        return choices

    @Slot()
    def emit_task_choices(self) -> None:
        self.task_list_ready.emit(self.get_task_choices())

    @Slot(str)
    def increment_task_pomo(self, task_id: str) -> None:
        try:
            task_key = int(task_id)
        except ValueError:
            return

        task = self.model.get_task(task_key)
        if task is None:
            return

        task.pomo_num += 1
        self.model.update_task(task_key, pomo_num=task.pomo_num)
        self.refresh_view()
