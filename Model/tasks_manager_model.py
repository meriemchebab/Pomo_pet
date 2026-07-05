
from dataclasses import dataclass, field
from typing import Optional
from DataBase.db_connection import Connection
          
@dataclass
class Task:
    ID_T: Optional[int] = None
    ID_P: Optional[int] = None
    status: str = ""
    discription: str = ""
    tag: str = ""
    pomo_num: int = 0

    # when you are finished from the task add 1 to the pomo_num then
    # so when the session ends "app close" save the number into table task_progress
    def __post_init__(self):
        if self.status is None:
            self.status = ""
        if self.ID_P is None:
            self.ID_P = None
        if self.discription is None:
            self.discription = ""
        if self.tag is None:
            self.tag = ""


@dataclass
class Project:
    tasks: list[Task] = field(default_factory=list)
    ID_P: Optional[int] = None
    name: str = ""
    tag: str = ""
    progress: float = 0.0
    status: str = ""

    def __post_init__(self):
        if self.status is None:
            self.status = "undone"
        if self.name is None:
            self.name = "work"
        if self.tag is None:
            self.tag = ""

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def delete_task(self, task: Task) -> None:
        self.tasks.remove(task)

    def get_task(self, task_id: int) -> Task | None:
        for task in self.tasks:
            if task.ID_T == task_id:
                return task
        return None

    def increment_pomo_task(self, task: Task) -> None:
        for stored_task in self.tasks:
            if stored_task == task:
                stored_task.pomo_num += 1
                break

    def delete_tasks(self) -> None:
        self.tasks.clear()


class ProjectManager:
    def __init__(self, connection: Connection, projects_dao=None, tasks_dao=None):
        if projects_dao is None or tasks_dao is None:
            from DataBase.DAO.projects_dao import ProjectsDao
            from DataBase.DAO.tasks_dao import TasksDao

            projects_dao = projects_dao or ProjectsDao(connection)
            tasks_dao = tasks_dao or TasksDao(connection)

        self.projects_dao = projects_dao
        self.tasks_dao = tasks_dao
        self.projects: list[Project] = []
        self._next_project_id = 1
        self._next_task_id = 1
        self.load_projects()

    def load_projects(self) -> None:
        projects = self.projects_dao.load_projects()
        tasks = self.tasks_dao.load_tasks()

        project_map: dict[int, Project] = {}
        for project in projects:
            project.tasks.clear()
            project_map[project.ID_P or 0] = project

        default_project: Project | None = None
        if not project_map:
            default_project = self.projects_dao.save_project(Project(name="work"))
            project_map[default_project.ID_P or 0] = default_project

        for task in tasks:
            if task.ID_P is None or task.ID_P not in project_map:
                if default_project is None:
                    default_project = next(iter(project_map.values()))
                task.ID_P = default_project.ID_P
                self.tasks_dao.update_task(task)
                project_map[default_project.ID_P or 0].add_task(task)
            else:
                project_map[task.ID_P].add_task(task)

        self.projects = list(project_map.values())
        self._next_project_id = self._compute_next_project_id()
        self._next_task_id = self._compute_next_task_id()

    def add_project(self, name: str, tag: str = "", status: str = "undone") -> Project:
        project = Project(
            name=name or "work",
            tag=tag or "",
            status=status or "undone",
        )
        self.projects_dao.save_project(project)
        self.projects.append(project)
        self._next_project_id = self._compute_next_project_id()
        return project

    def get_project(self, ID_P: int) -> Project | None:
        for project in self.projects:
            if project.ID_P == ID_P:
                return project
        return None

    def delete_project(self, ID_P: int) -> bool:
        project = self.get_project(ID_P)
        if project is None:
            return False
        if project.ID_P is not None:
            self.projects_dao.delete_project(project.ID_P)
        self.projects.remove(project)
        self._next_project_id = self._compute_next_project_id()
        return True

    def add_task(self, ID_P: int, description: str, tag: str = "", status: str = "") -> Task | None:
        project = self.get_project(ID_P)
        if project is None:
            return None

        task = Task(
            ID_P=ID_P,
            discription=description or "",
            tag=tag or "",
            status=status or "",
        )
        self.tasks_dao.save_task(task)
        project.add_task(task)
        self._next_task_id = self._compute_next_task_id()
        return task

    def delete_task(self, ID_T: int) -> bool:
        for project in self.projects:
            task = project.get_task(ID_T)
            if task is not None:
                if task.ID_T is not None:
                    self.tasks_dao.delete_task(task.ID_T)
                project.delete_task(task)
                self._next_task_id = self._compute_next_task_id()
                return True
        return False

    def get_task(self, ID_T: int) -> Task | None:
        for project in self.projects:
            task = project.get_task(ID_T)
            if task is not None:
                return task
        return None

    def update_task(
        self,
        ID_T: int,
        *,
        status: str | None = None,
        discription: str | None = None,
        tag: str | None = None,
        pomo_num: int | None = None,
    ) -> Task | None:
        task = self.get_task(ID_T)
        if task is None:
            return None

        if status is not None:
            task.status = status
        if discription is not None:
            task.discription = discription
        if tag is not None:
            task.tag = tag
        if pomo_num is not None:
            task.pomo_num = pomo_num
        self.tasks_dao.update_task(task)
        return task

    def set_projects(self, projects: list[Project]) -> None:
        self.projects = projects
        self._next_project_id = self._compute_next_project_id()
        self._next_task_id = self._compute_next_task_id()

    def _compute_next_project_id(self) -> int:
        highest = max((project.ID_P or 0 for project in self.projects), default=0)
        return highest + 1

    def _compute_next_task_id(self) -> int:
        highest = max(
            (task.ID_T or 0 for project in self.projects for task in project.tasks),
            default=0,
        )
        return highest + 1


# Backward-compatible aliases for older imports.
Tasks = Task
ProjectModel = Project
