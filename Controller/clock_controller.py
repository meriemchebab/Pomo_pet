from PySide6.QtCore import QObject, Signal, Slot
from Model.clock_model import Clock, ClockSettings,Phase
from View.clock_widget import ClockWidget
from typing import Optional

class ClockController(QObject):
    def __init__(self,parent = None,settings : Optional[ClockSettings] = None):
        super().__init__()
        self.view = ClockWidget()
        self.model = Clock(settings)

        self.view.start_btn.clicked.connect(self.start_pomo)
        self.model.time_remaining.connect(self.view.set_remaining)
        self.view.pause_btn.clicked.connect(self.toggle_pause)
        self.view.reset_btn.clicked.connect(self.reset_pomo)
        self.view.settings_requested.connect(self.on_settings_changed)
        self.model.time_focused.connect(self.on_time_focused)
        self.view.skip_btn.clicked.connect(self.skip)
        self.model.phase_changed.connect(self.on_phase_change)
    def start_pomo(self):
        self.view.set_duration(self.model.time_left)
        self.model.start() # the tick method will be called by the  timer each 1 sec
    
    def reset_pomo(self):
        self.model.reset_timer()
        self.view.set_duration(self.model.time_left)
        # emit the focused time passed for the session 
        # self.view.set_focus_stats(self.model.time_passed, self.model.completed_pomos)

    def toggle_pause(self):
        """toggle between pause and resume"""
        if self.view.pause_btn.isChecked():
            self.model.pause()
        else:
            self.model.start()

    def on_settings_changed(self, values: dict):
        """handle settings changes from the quick setup dialog"""
        # refresh UI
        self.view.apply_settings(values)
        self.model.settings.update_settings(values)
        # Reset the timer to apply new settings
        self.reset_pomo()

    def on_phase_change(self,phase : Phase):
        phase_name = phase.name.replace("_", " ").title()
        self.view.set_phase_info(phase_name= phase_name , cycle_index=self.model.completed_pomos,cycle_total=self.model.settings.pomo_until_break)
        # self.view.set_duration(self.model.time_left)

    def on_time_focused(self, focused_seconds : int):
        self.view.set_focus_stats(  focused_seconds,
                                    completed_sessions= self.model.completed_pomos)
        
    def skip(self):
        if self.model.phase == Phase.WORK:
            phase = Phase.SHORT_BREAK
        else:
            phase = Phase.WORK
        self.model.change_phase(phase)
        self.model.reset_timer()
        self.on_phase_change(phase=phase)