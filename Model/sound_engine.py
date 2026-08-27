from __future__ import annotations

import os
import time
from pathlib import Path
from PySide6.QtCore import QEvent, QObject, QUrl, Qt
from PySide6.QtWidgets import QAbstractButton, QComboBox, QSlider
from PySide6.QtMultimedia import QSoundEffect


class UIClickSoundFilter(QObject):
    def __init__(self, click_sound_path: str, parent: QObject | None = None):
        super().__init__(parent)
        self.sound = QSoundEffect(self)
        self._last_click_at = 0.0
        if os.path.exists(click_sound_path):
            self.sound.setSource(QUrl.fromLocalFile(os.path.abspath(click_sound_path)))
            self.sound.setLoopCount(1)
            self.sound.setVolume(0.6)

    def set_volume(self, volume: float) -> None:
        self.sound.setVolume(max(0.0, min(1.0, volume)))

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonRelease:
            if isinstance(watched, (QAbstractButton, QComboBox, QSlider)):
                self.play_click()
            elif hasattr(watched, "cursor") and watched.cursor().shape() == Qt.CursorShape.PointingHandCursor:
                self.play_click()
        return super().eventFilter(watched, event)

    def play_click(self) -> None:
        now = time.monotonic()
        if now - self._last_click_at < 0.04:
            return
        self._last_click_at = now

        if self.sound.volume() > 0:
            self.sound.stop()
            self.sound.play()


class TrackAudio:
    def __init__(self, file_path: str, parent: QObject | None = None):
        self.file_path = file_path
        self.sound = QSoundEffect(parent)
        
        if os.path.exists(file_path):
            self.sound.setSource(QUrl.fromLocalFile(os.path.abspath(file_path)))
            self.sound.setLoopCount(QSoundEffect.Loop.Infinite.value)

        self.volume: float = 0.5  # 0.0 to 1.0
        self.enabled: bool = False

    def update_effective_volume(self, master_volume: float) -> None:
        """
        master_volume is 0.0 to 1.0
        """
        effective = max(0.0, min(1.0, master_volume * self.volume)) if self.enabled else 0.0
        self.sound.setVolume(effective)

        if self.enabled and master_volume > 0 and self.volume > 0:
            if not self.sound.isPlaying():
                self.sound.play()
        else:
            if self.sound.isPlaying():
                self.sound.stop()


class SoundEngine(QObject):
    SOUND_FILES = {
        "rain": "assets/mixkit-light-rain-loop-2393.wav",
        "ocean": "assets/mixkit-small-waves-harbor-rocks-1208.wav",
        "fireplace": "assets/mixkit-campfire-night-wind-1736.wav",
        "forest_wind": "assets/birds_forest.wav",
        "clock": "assets/mixkit-wall-clock-tick-tock-1060.wav",
    }

    NOTIFICATION_FILES = {
        "Bell sound": "assets/mixkit-achievement-bell-600.wav",
        "game win": "assets/mixkit-quick-win-video-game-notification-269.wav",
        "Keys Drop": "assets/mixkit-dropping-keys-in-the-floor-2839.wav",
        "Page chime": "assets/mixkit-page-forward-single-chime-1107.wav",
        "Fantasy win": "assets/mixkit-fantasy-game-success-notification-270.wav",
    }
        # "Bell sound",
        #         "game win",
        #         "Keys Drop",
        #         "Page chime",
        #         "Fantasy win",

    CLICK_SOUND_FILE = "assets/mixkit-twig-breaking-2945.wav"

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._master_volume: float = 0.6  # 0.0 to 1.0
        self.tracks: dict[str, TrackAudio] = {}

        # Resolve assets root path relative to project
        base_dir = Path(__file__).resolve().parent.parent

        for key, rel_path in self.SOUND_FILES.items():
            full_path = str(base_dir / rel_path)
            self.tracks[key] = TrackAudio(full_path, self)

        # Separate notification player
        self.notif_sound = QSoundEffect(self)
        self.notif_sound.setLoopCount(1)

        # UI click sound filter
        click_path = str(base_dir / self.CLICK_SOUND_FILE)
        self.click_filter = UIClickSoundFilter(click_path, self)

    def set_master_volume(self, volume: float) -> None:
        """volume: 0.0 to 1.0"""
        self._master_volume = max(0.0, min(1.0, volume))
        self.notif_sound.setVolume(self._master_volume)
        self.click_filter.set_volume(self._master_volume)
        for track in self.tracks.values():
            track.update_effective_volume(self._master_volume)

    def set_track_volume(self, track_key: str, volume: float) -> None:
        """volume: 0.0 to 1.0"""
        if track_key in self.tracks:
            self.tracks[track_key].volume = max(0.0, min(1.0, volume))
            self.tracks[track_key].update_effective_volume(self._master_volume)

    def set_track_enabled(self, track_key: str, enabled: bool) -> None:
        if track_key in self.tracks:
            self.tracks[track_key].enabled = enabled
            self.tracks[track_key].update_effective_volume(self._master_volume)

    def play_notification(self, sound_name: str) -> None:
        rel_path = self.NOTIFICATION_FILES.get(sound_name)
        if not rel_path:
            return
        base_dir = Path(__file__).resolve().parent.parent
        full_path = str(base_dir / rel_path)
        if os.path.exists(full_path):
            self.notif_sound.stop()
            self.notif_sound.setSource(QUrl.fromLocalFile(os.path.abspath(full_path)))
            self.notif_sound.setVolume(self._master_volume)
            self.notif_sound.play()
