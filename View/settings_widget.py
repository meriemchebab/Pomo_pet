from __future__ import annotations

from PySide6.QtCore import Qt , Signal , Slot
from PySide6.QtWidgets import (
    QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSpinBox, QCheckBox, QComboBox, QSlider
)
from .theme import AVAILABLE_THEMES

# the change in settings here is saved in the database while the quick setup is just for a session
class SettingsWidget(QFrame):
    timer_changed = Signal(str, int)
    theme_changed = Signal(str)
    white_noise_track_changed = Signal(str)
    white_noise_volume_changed = Signal(str, int)


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('panelCard')

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        title = QLabel('Settings')
        title.setStyleSheet('font-size: 20px; font-weight: 700;')
        root.addWidget(title)

        form = QFormLayout()
        self.focus_minutes = QSpinBox()
        self.focus_minutes.setRange(1, 180)
        self.focus_minutes.setValue(25)

        self.break_minutes = QSpinBox()
        self.break_minutes.setRange(1, 60)
        self.break_minutes.setValue(5)

        self.long_break = QSpinBox()
        self.long_break.setRange(5, 60)
        self.long_break.setValue(30)

        self.cycles = QSpinBox()
        self.cycles.setRange(1, 12)
        self.cycles.setValue(4)

        self.theme_box = QComboBox()
        self.theme_box.addItems(AVAILABLE_THEMES)

        self.white_noise_box = QComboBox()

        self.auto_start_break = QCheckBox('Auto-start break')
        self.auto_start_focus = QCheckBox('Auto-start next focus')
        # self.pet_animate = QCheckBox('Animate pet while timer runs')
        # self.pet_animate.setChecked(True)

        form.addRow('Focus (min)', self.focus_minutes)
        form.addRow('Break (min)', self.break_minutes)
        form.addRow('Long break', self.long_break)
        form.addRow('Cycles', self.cycles)
        form.addRow('Theme', self.theme_box)
        form.addRow('White noise', self.white_noise_box)
        form.addRow('', self.auto_start_break)
        form.addRow('', self.auto_start_focus)
        
        root.addLayout(form)

        noise_row = QHBoxLayout()
        noise_row.addWidget(QLabel('Noise volume'))
        self.noise_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_slider.setRange(0, 100)
        self.noise_slider.setValue(35)
        noise_row.addWidget(self.noise_slider)
        root.addLayout(noise_row)

        buttons = QHBoxLayout()
        self.save_btn = QPushButton('Save settings')
        self.reset_btn = QPushButton('Reset defaults')
        self.save_btn.setObjectName('accentButton')
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.reset_btn)
        root.addLayout(buttons)

        # emit a signal when a value is changed with the name of the attribut 
        self.focus_minutes.valueChanged.connect(self.focus_changed)
        self.break_minutes.valueChanged.connect(self.break_changed)
        self.long_break.valueChanged.connect(self.long_break_changed)
        self.cycles.valueChanged.connect(self.cycles_changed)
        self.theme_box.currentTextChanged.connect(self.theme_changed)
        self.white_noise_box.currentTextChanged.connect(self._on_white_noise_track_changed)
        self.auto_start_focus.toggled.connect(self.auto_start_focus_changed)
        self.auto_start_break.toggled.connect(self.auto_start_break_changed)
        self.noise_slider.valueChanged.connect(self._on_noise_slider_changed)
        # self.theme_box.currentTextChanged.connect(self.theme_changed_slot)
        # self.auto_start_break.toggled.connect(self.auto_start_break_toggled)
        # self.auto_start_focus.toggled.connect(self.auto_start_focus_toggled)
        # self.pet_animate.toggled.connect(self.pet_animate_toggled)
        # self.noise_slider.valueChanged.connect(self.noise_volume_changed_slot)
        # self.save_btn.clicked.connect(self.save_clicked)
        # self.reset_btn.clicked.connect(self.reset_clicked)

    @Slot(int)
    def focus_changed(self, value : int):
        self.timer_changed.emit("work_duration",value)
    @Slot(int)
    def break_changed(self, value : int):
        self.timer_changed.emit("short_break",value)
    @Slot(int)
    def long_break_changed(self, value : int):
        self.timer_changed.emit("long_break",value)
    @Slot(int)
    def cycles_changed(self, value : int):
        self.timer_changed.emit("pomo_until_break", value)

    @Slot(bool)
    def auto_start_focus_changed(self,value:bool):
        self.timer_changed.emit("auto_start_focus" , value)

    @Slot(bool)
    def auto_start_break_changed(self,value:bool):
        self.timer_changed.emit("auto_start_break" , value)

    @Slot(str)
    def _on_white_noise_track_changed(self, track_name: str) -> None:
        if track_name in self._white_noise_volumes:
            self.noise_slider.blockSignals(True)
            self.noise_slider.setValue(int(self._white_noise_volumes[track_name] * 100))
            self.noise_slider.blockSignals(False)
        self.white_noise_track_changed.emit(track_name)

    @Slot(int)
    def _on_noise_slider_changed(self, value: int) -> None:
        track_name = self.white_noise_box.currentText()
        self._white_noise_volumes[track_name] = value / 100
        self.white_noise_volume_changed.emit(track_name, value)

    def set_settings(self, settings) -> None:
        self.focus_minutes.setValue(settings.timer.work_duration // 60)
        self.break_minutes.setValue(settings.timer.short_break // 60)
        self.long_break.setValue(settings.timer.long_break // 60)
        self.cycles.setValue(settings.timer.pomo_until_break)
        self.theme_box.setCurrentText(settings.theme.current_theme)

        self._white_noise_volumes = {
            name: track.volume
            for name, track in settings.sound.white_noise.items()
        }
        self.white_noise_box.clear()
        self.white_noise_box.addItems(list(self._white_noise_volumes.keys()))

        current_track = self.white_noise_box.currentText() or next(iter(self._white_noise_volumes), "")
        if current_track:
            self.noise_slider.blockSignals(True)
            self.noise_slider.setValue(int(self._white_noise_volumes[current_track] * 100))
            self.noise_slider.blockSignals(False)
        