from dataclasses import dataclass
from datetime import datetime
@dataclass
class Session:
    ID_S : int 
    date : datetime
    pomo_num : int = 0
    focus_time : int = 0
    day_open : bool = False

