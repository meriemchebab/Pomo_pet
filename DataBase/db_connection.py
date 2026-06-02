import sqlite3
# single connection in all the application , used once in the main.py and closed on shutdown
class Connection():
    def __init__(self, db_path : str) -> None:
        self.path = db_path
        self.conn = sqlite3.connect(self.path)
    def close_connection(self):
        self.conn.close()