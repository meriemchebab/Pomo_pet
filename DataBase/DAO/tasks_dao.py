from __future__ import annotations

from typing import Iterable

from DataBase.db_connection import Connection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Model.tasks_manager_model import Task


class TasksDao:
    def __init__(self, connection: Connection, parent=None):
        self.db_conn = connection
        self.curr = connection.conn.cursor()

    def load_tasks(self) -> list[Task]:
        from Model.tasks_manager_model import Task

        sql = "SELECT ID_T, ID_P, status, discription, tag FROM Tasks ORDER BY ID_T"
        self.curr.execute(sql)
        rows = self.curr.fetchall()
        return [Task(
                ID_T=row["ID_T"],
                ID_P=row["ID_P"],
                status=row["status"] or "",
                discription=row["discription"] or "",
                tag=row["tag"] or "",
            )
            for row in rows]
            
        

    def load_task(self, task_id: int) -> Task | None:
        from Model.tasks_manager_model import Task

        sql = "SELECT ID_T, ID_P, status, discription, tag FROM Tasks WHERE ID_T = ?"
        self.curr.execute(sql, (task_id,))
        row = self.curr.fetchone()
        if row is None:
            return None
        return Task(
            ID_T=row["ID_T"],
            ID_P=row["ID_P"],
            status=row["status"] or "",
            discription=row["discription"] or "",
            tag=row["tag"] or "",
        )

    def save_task(self, task: Task) -> Task:
        sql = "INSERT INTO Tasks(ID_P, status, discription, tag) VALUES(?, ?, ?, ?)"
        self.curr.execute(sql, (task.ID_P, task.status, task.discription, task.tag))
        self.db_conn.conn.commit()
        task.ID_T = self.curr.lastrowid
        return task

    def update_task(self, task: Task) -> bool:
        if task.ID_T is None:
            return False

        sql = "UPDATE Tasks SET ID_P = ?, status = ?, discription = ?, tag = ? WHERE ID_T = ?"
        self.curr.execute(sql, (task.ID_P, task.status, task.discription, task.tag, task.ID_T))
        self.db_conn.conn.commit()
        return self.curr.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        sql = "DELETE FROM Tasks WHERE ID_T = ?"
        self.curr.execute(sql, (task_id,))
        self.db_conn.conn.commit()
        return self.curr.rowcount > 0

    def save_tasks(self, tasks: Iterable[Task]) -> None:
        for task in tasks:
            self.save_task(task)
