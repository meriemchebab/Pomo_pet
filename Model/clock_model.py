from PySide6.QtCore import QTimer, QObject, Signal, Slot
from enum import Enum, auto
from typing import Optional


class Phase(Enum):
    WORK = auto()
    LONG_BREAK = auto()
    SHORT_BREAK = auto()


class ClockSettings(QObject):
    # use default pomodoro settings if not set 
    # to do : add white noise settings and sounds too , dont use it in the UI of the clock
    
    def __init__(self, duration: int = 25 * 60,
                  break_time: int = 5 * 60,
                    pomo_until_break: int = 4 ,
                    long_break_time : int = 30 * 60,
                    auto_start_next_phase: bool = False):
        super().__init__()
        self._duration = int(duration)
        self._break_time = int(break_time)
        self._pomo_until_break = int(pomo_until_break)
        self._auto_start_next_phase = bool(auto_start_next_phase)
        self._long_break_time = int(long_break_time)
    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, value: int):
        value = int(value)
        if value != self._duration:
            self._duration = value      

    @property
    def break_time(self) -> int:
        return self._break_time

    @break_time.setter
    def break_time(self, value: int):
        value = int(value)
        if value != self._break_time:
            self._break_time = value
            

    @property
    def pomo_until_break(self) -> int:
        return self._pomo_until_break

    @pomo_until_break.setter
    def pomo_until_break(self, value: int):
        value = int(value)
        if value != self._pomo_until_break:
            self._pomo_until_break = value

    @property
    def auto_start_next_phase(self) -> bool:
        return self._auto_start_next_phase   
     
    @auto_start_next_phase.setter
    def auto_start_next_phase(self,value : bool):
        value = bool(value)
        if value != self._auto_start_next_phase:
            self._auto_start_next_phase = value

    @property
    def long_break_time(self) -> int:
        return self._long_break_time
    
from PySide6.QtCore import QTimer, QObject, Signal, Slot
from enum import Enum, auto
from typing import Optional


class Phase(Enum):
    WORK = auto()
    LONG_BREAK = auto()
    SHORT_BREAK = auto()


class ClockSettings(QObject):
    # use default pomodoro settings if not set 
    # to do : add white noise settings and sounds too , dont use it in the UI of the clock
    
    def __init__(self, duration: int = 25 * 60,
                  break_time: int = 5 * 60,
                    pomo_until_break: int = 4 ,
                    long_break_time : int = 30 * 60,
                    auto_start_next_phase: bool = False):
        super().__init__()
        self._duration = int(duration)
        self._break_time = int(break_time)
        self._pomo_until_break = int(pomo_until_break)
        self._auto_start_next_phase = bool(auto_start_next_phase)
        self._long_break_time = int(long_break_time)
    @property
    def duration(self) -> int:
        return self._duration

    @duration.setter
    def duration(self, value: int):
        value = int(value)
        if value != self._duration:
            self._duration = value      

    @property
    def break_time(self) -> int:
        return self._break_time

    @break_time.setter
    def break_time(self, value: int):
        value = int(value)
        if value != self._break_time:
            self._break_time = value
            

    @property
    def pomo_until_break(self) -> int:
        return self._pomo_until_break

    @pomo_until_break.setter
    def pomo_until_break(self, value: int):
        value = int(value)
        if value != self._pomo_until_break:
            self._pomo_until_break = value

    @property
    def auto_start_next_phase(self) -> bool:
        return self._auto_start_next_phase   
     
    @auto_start_next_phase.setter
    def auto_start_next_phase(self,value : bool):
        value = bool(value)
        if value != self._auto_start_next_phase:
            self._auto_start_next_phase = value

    @property
    def long_break_time(self) -> int:
        return self._long_break_time
    
    @long_break_time.setter
    def long_break_time(self,value :int):
        value = int(value)
        if value != self._long_break_time:
            self._long_break_time = value
    
    def update_settings(self, values: dict):
        """this method updates the clock settings for the current session"""
        self._duration = values.get("duration", self._duration)
        self._break_time = values.get("break_time", self._break_time)
        self._long_break_time = values.get("long_break_time", self._long_break_time)
        self._pomo_until_break = values.get("pomo_until_break", self._pomo_until_break)
        self._auto_start_next_phase = values.get("auto_start_next_phase", self._auto_start_next_phase)

    @classmethod
    def from_app_settings(cls, app_settings) -> "ClockSettings":
        timer = getattr(app_settings, "timer", None)
        if not timer:
            return cls()
        return cls(
            duration=timer.work_duration,
            break_time=timer.short_break,
            long_break_time=timer.long_break,
            pomo_until_break=timer.pomo_until_break,
            auto_start_next_phase=getattr(timer, "auto_start_break", False) or getattr(timer, "auto_start_focus", False),
        )


class Clock(QObject):
    
    time_remaining = Signal(int)
    phase_changed = Signal(object)
    time_focused = Signal(int)
    work_session_completed = Signal(int)
    def __init__(self, settings: Optional[ClockSettings] = None):
        super().__init__()
        self.settings = settings or ClockSettings()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.time_left = int(self.settings.duration)
        self.time_passed = 0
        self.elapsed = 0
        self.phase = Phase.WORK
        self.completed_pomos = 0

    def start(self):
        if not self.timer.isActive():
            if self.time_left <= 0:
                if self.phase == Phase.WORK:
                    self.time_left = int(self.settings.duration)
                elif self.phase == Phase.LONG_BREAK:
                    self.time_left = int(self.settings.long_break_time)
                else:
                    self.time_left = int(self.settings.break_time)
            self.timer.start(1000)   # fires every 1s

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()

    def reset_timer(self):
        """the reset function will stop the timer and set it back to maximum phase time"""
        self.pause()
        self.time_passed = 0
        self.elapsed = 0
        if self.phase == Phase.WORK:
            self.time_left = int(self.settings.duration)
        elif self.phase == Phase.LONG_BREAK:
            self.time_left = int(self.settings.long_break_time)
        elif self.phase == Phase.SHORT_BREAK:
            self.time_left = int(self.settings.break_time)
        self.time_remaining.emit(self.time_left)

    def change_phase(self, phase: Phase):
        """manual changing of phase"""
        if phase != self.phase:
            self.phase = phase
            if phase == Phase.WORK:
                self.time_left = int(self.settings.duration)
            elif phase == Phase.LONG_BREAK:
                self.time_left = int(self.settings.long_break_time)
            elif phase == Phase.SHORT_BREAK:
                self.time_left = int(self.settings.break_time)
            self.phase_changed.emit(self.phase)
            self.time_remaining.emit(self.time_left)
 
    @Slot()
    def _tick(self):
        self.time_left -= 1
        if self.phase == Phase.WORK:
            self.time_passed += 1 #only increment the focus time passed
        
        self.elapsed += 1
        if self.time_left <= 0:
            self.time_remaining.emit(0)
            self.pomo_end()
        else:
            self.time_remaining.emit(self.time_left)

    def pomo_end(self):
        self.pause()
        if self.phase == Phase.WORK:
            self.completed_pomos += 1
            self.time_focused.emit(self.time_passed) #emit the focused time 
            self.work_session_completed.emit(self.time_passed)
            self.time_passed = 0
            if self.completed_pomos % self.settings.pomo_until_break == 0:
                self.phase = Phase.LONG_BREAK
                self.time_left = int(self.settings.long_break_time)
            else:
                self.phase = Phase.SHORT_BREAK
                self.time_left = int(self.settings.break_time)
        else:
            self.phase = Phase.WORK
            self.time_left = int(self.settings.duration)
            self.time_passed = 0

        self.phase_changed.emit(self.phase)
        self.time_remaining.emit(self.time_left)

        if self.settings.auto_start_next_phase:
            self.start()
