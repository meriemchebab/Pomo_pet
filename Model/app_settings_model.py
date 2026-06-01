from PySide6.QtCore import QObject
from typing import Optional
from clock_model import ClockSettings

class SoundSettings(QObject):
    def __init__(self, parent = None):
        super().__init__()
        # attributs of the settings of white noise and sounds 
        self.white_noise_list = ""
        self.sound_on_finish = ""
        self.sound_on_break = ""
        self.volume = 0
        self.auto_play = False
        # here put the methods that will update the sound and volum too 
class ThemeSettings(QObject):
    def __init__(self, parent = None):
        super().__init__()
        # put the attribut of themes files that you can laod and stuff like this 
class AppSettings(QObject):
    def __init__(self, parent = None):
        super().__init__()
        self.clock_settings = ClockSettings() # this one will presist and get saved to the db
        self.sound_settings = SoundSettings()
        self.theme_settings = ThemeSettings()