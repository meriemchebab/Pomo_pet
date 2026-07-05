from __future__ import annotations

from DataBase.db_connection import Connection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Model.tasks_manager_model import Project


class ProjectsDao:
    def __init__(self, connection: Connection, parent=None):
        self.db_conn = connection
        self.curr = connection.conn.cursor()

    def load_projects(self) -> list[Project]:
        from Model.tasks_manager_model import Project

        sql = "SELECT ID_P, name, tag, progress, state FROM Projects ORDER BY ID_P"
        self.curr.execute(sql)
        rows = self.curr.fetchall()
        return [
            Project(
                ID_P=row["ID_P"],
                name=row["name"] or "",
                tag=row["tag"] or "",
                progress=row["progress"] or 0.0,
                status=row["state"] or "undone",
            )
            for row in rows
        ]

    def load_project(self, project_id: int) -> Project | None:
        from Model.tasks_manager_model import Project

        sql = "SELECT ID_P, name, tag, progress, state FROM Projects WHERE ID_P = ?"
        self.curr.execute(sql, (project_id,))
        row = self.curr.fetchone()
        if row is None:
            return None
        return Project(
            ID_P=row["ID_P"],
            name=row["name"] or "",
            tag=row["tag"] or "",
            progress=row["progress"] or 0.0,
            status=row["state"] or "undone",
        )

    def save_project(self, project: Project) -> Project:
        sql = "INSERT INTO Projects(name, tag, progress, state) VALUES(?, ?, ?, ?)"
        self.curr.execute(sql, (project.name, project.tag, project.progress, project.status))
        self.db_conn.conn.commit()
        project.ID_P = self.curr.lastrowid
        return project

    def update_project(self, project: Project) -> bool:
        if project.ID_P is None:
            return False

        sql = "UPDATE Projects SET name = ?, tag = ?, progress = ?, state = ? WHERE ID_P = ?"
        self.curr.execute(sql, (project.name, project.tag, project.progress, project.status, project.ID_P))
        self.db_conn.conn.commit()
        return self.curr.rowcount > 0

    def delete_project(self, project_id: int) -> bool:
        sql = "DELETE FROM Projects WHERE ID_P = ?"
        self.curr.execute(sql, (project_id,))
        self.db_conn.conn.commit()
        return self.curr.rowcount > 0
