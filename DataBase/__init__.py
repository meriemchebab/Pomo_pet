from .db_connection import Connection

__all__ = ["Connection", "ProjectsDao", "SessionDao", "TasksDao"]


def __getattr__(name: str):
    if name == "ProjectsDao":
        from .DAO.projects_dao import ProjectsDao

        return ProjectsDao
    if name == "SessionDao":
        from .DAO.session_dao import SessionDao

        return SessionDao
    if name == "TasksDao":
        from .DAO.tasks_dao import TasksDao

        return TasksDao
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
