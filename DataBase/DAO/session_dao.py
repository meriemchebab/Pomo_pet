import sqlite3
from DataBase.db_connection import Connection
from Model.session_model import Session
from datetime import datetime

class SessionDao():
    def __init__(self,connection : Connection,parent = None):
        self.db_conn = connection
        self.curr = connection.conn.cursor()
        
    def load_session(self,id_s : int) -> Session:
        """return the session with this ID"""
        sql = "SELECT * FROM Session WHERE ID_S = ?"
        self.curr.execute(  
            sql,(id_s,)
        )
        row = self.curr.fetchone()
        session = Session(
            row["ID_S"],
            row["date"],
            row["pomo_num"],
            row["focus_time"],
            row["day_open"]
        )
        return session
    def save_session(self, session :Session):
        sql = "INSERT INTO Session VALUES(?,?,?,?)"
        self.curr.execute(
            sql,(session.date,session.pomo_num,session.focus_time,session.day_open)
        )
        self.db_conn.conn.commit()
    def fetsh_session_bydate(self,date : datetime):
        """return all sessions of that day or date"""
        sql = "SELECT ID_S, pomo_num, focus_time FROM Session WHERE date = ?"
        self.curr.execute(
            sql,(date,)
        )
        
