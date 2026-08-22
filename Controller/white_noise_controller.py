from __future__ import annotations

from PySide6.QtCore import QObject, Slot

from Model.app_settings_model import AppSettings
from Model.sound_engine import SoundEngine
from View.whiteNoise_widget import WhiteNoiseWidget


class WhiteNoiseController(QObject):
    def __init__(
        self,
        view: WhiteNoiseWidget,
        app_settings: AppSettings | None = None,
        sound_engine: SoundEngine | None = None,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self.view = view
        self.settings = app_settings or AppSettings.load()
        self.engine = sound_engine or SoundEngine(self)

        # Apply settings to UI & engine
        self._apply_settings()

      
        self.view.track_volume_changed.connect(self.on_track_volume_changed)
        self.view.track_toggled.connect(self.on_track_toggled)
        self.view.master_volume_changed.connect(self.on_master_volume_changed)
        self.view.notification_sound_changed.connect(self.on_notification_sound_changed)

    def _apply_settings(self) -> None:
        sound = self.settings.sound

        # Master volume
        master_percent = int(sound.master_volume * 100)
        self.view.master_volume_row.slider.setValue(master_percent)
        self.view.master_volume_row.value_label.setText(f"{master_percent}%")
        self.engine.set_master_volume(sound.master_volume)

        # White noise tracks
        for key, track in sound.white_noise.items():
            if key in self.view.sound_rows:
                row = self.view.sound_rows[key]
                row.slider.setValue(int(track.volume * 100))
                row.switch.setChecked(track.enabled)
                self.engine.set_track_volume(key, track.volume)
                self.engine.set_track_enabled(key, track.enabled)

    @Slot(str, int)
    def on_track_volume_changed(self, key: str, value: int) -> None:
        vol = value / 100.0
        self.engine.set_track_volume(key, vol)
        if key in self.settings.sound.white_noise:
            self.settings.update_track(key, "volume", vol)

    @Slot(str, bool)
    def on_track_toggled(self, key: str, enabled: bool) -> None:
        self.engine.set_track_enabled(key, enabled)
        if key in self.settings.sound.white_noise:
            self.settings.update_track(key, "enabled", enabled)

    @Slot(int)
    def on_master_volume_changed(self, value: int) -> None:
        master_vol = value / 100.0
        self.engine.set_master_volume(master_vol)
        self.settings.update("sound", "master_volume", master_vol)

    @Slot(str, str)
    def on_notification_sound_changed(self, event_key: str, sound_name: str) -> None:
        # Preview the sound when user changes it in the dropdown
        self.engine.play_notification(sound_name)
