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
# s.execute("PRAGMA foreign_keys = ON;")
    # s.execute(""" CREATE TABLE IF NOT EXISTS book_notes (
    # book_id REAL PRIMARY KEY,
    # note_text TEXT,
    # created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    # updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    # FOREIGN KEY (book_id) REFERENCES BOOKS(book_id) ON DELETE CASCADE)""")
    # conn.commit()
    # s.close()

db.conn.commit()

curr.execute(
    """ CREATE TABLE IF NOT EXISTS Tasks (
    ID_T INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    status TEXT ,
    discription TEXT ,
    tag TEXT)
"""
)
db.conn.commit()
curr.execute(
    """ CREATE TABLE IF NOT EXISTS task_progress(
    ID_prog INTEGER PRIMARY KEY AUTOINCREMENT,
FOREIGN KEY (ID_T) REFERENCES Tasks(ID_T) ON DELETE CASCADE,
FOREIGN KEY (ID_S) REFERENCES Session(ID_S) ON DELETE CASCADE,
pomo_count INTEGER DEFAULT 0
)
"""
)
db.conn.commit()
db.close_connection()
