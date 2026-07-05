from db_connection import Connection
import sqlite3

db = Connection("pomo_pet.db")

curr = db.conn.cursor()
# curr.execute("PARAGMA foreign_keys = ON;")
curr.execute(
    """CREATE TABLE IF NOT EXISTS Session (
    ID_S INTEGER PRIMARY KEY AUTOINCREMENT ,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pomo_num INTEGER DEFAULT 0,
    focus_time INTEGER DEFAULT 0,
    day_open TEXT
    )
    """
)

db.conn.commit()

curr.execute(
    """ CREATE TABLE IF NOT EXISTS Projects(
    ID_P INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    tag TEXT,
    progress REAL,
    state TEXT
    )
"""
)
db.conn.commit()
curr.execute(
    """ CREATE TABLE IF NOT EXISTS Tasks (
    ID_T INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    ID_P INTEGER,
    status TEXT ,
    discription TEXT ,
    tag TEXT,
    FOREIGN KEY (ID_P) REFERENCES Projects(ID_P) ON DELETE CASCADE
    )
"""
)
db.conn.commit()
curr.execute(
    """ CREATE TABLE IF NOT EXISTS task_progress(
    ID_prog INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_T INTEGER,
    ID_S INTEGER,
    pomo_count INTEGER DEFAULT 0,
    FOREIGN KEY (ID_T) REFERENCES Tasks(ID_T) ON DELETE CASCADE,
    FOREIGN KEY (ID_S) REFERENCES Session(ID_S) ON DELETE CASCADE
)
"""
)
db.conn.commit()
db.close_connection()
