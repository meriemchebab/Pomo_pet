from PySide6.QtCore import QObject
from View.settings_widget import SettingsWidget
from Model.app_settings_model import AppSettings

class SettingsController(QObject):
    def __init__(self, parent=None):
        super().__init__()
        self.view = SettingsWidget()
        self.model = AppSettings.load()
        self.original_model = self.model.clone()

        self.view.set_settings(self.model)

        self.view.timer_changed.connect(self.update_timer)
        self.view.theme_changed.connect(self.theme_changed_slot)
        self.view.white_noise_volume_changed.connect(self.noise_volume_changed_slot)
        self.view.save_btn.clicked.connect(self.save_clicked)
        self.view.reset_btn.clicked.connect(self.reset_clicked)
    def update_timer(self, field: str, value: int):
        self.model.update("timer", field=field, value=value)

    def theme_changed_slot(self, new_theme: str):
        self.model.update("theme", field="current_theme", value=new_theme)

    def noise_volume_changed_slot(self, track_name: str, value: int):
        self.model.update_track(track_name, "volume", value / 100)

    def save_clicked(self):
        self.model.save()
        self.original_model = self.model.clone()

    def reset_clicked(self):
        self.model = self.original_model.clone()
        self.view.set_settings(self.model)