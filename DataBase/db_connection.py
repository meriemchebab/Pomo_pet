import os
import sqlite3

# single connection in all the application , used once in the main.py and closed on shutdown
class Connection():
    def __init__(self, db_path : str) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, db_path)

        self.path = os.path.normpath(db_path)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row # will return a dict like row["id"]
    def close_connection(self):
        self.conn.close()
