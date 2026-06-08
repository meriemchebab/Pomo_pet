from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QListWidget


class WhiteNoiseWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('panelCard')

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel('White Noise')
        title.setStyleSheet('font-size: 20px; font-weight: 700;')
        root.addWidget(title)

        self.track_list = QListWidget()
        self.track_list.addItems([
            'Rain on Leaves', 'Forest Wind', 'Night Crickets', 'Cabin Ambience', 'River Loop'
        ])
        root.addWidget(self.track_list)

        controls = QHBoxLayout()
        self.play_btn = QPushButton('Play')
        self.stop_btn = QPushButton('Stop')
        self.loop_btn = QPushButton('Loop')
        self.shuffle_btn = QPushButton('Shuffle')
        controls.addWidget(self.play_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.loop_btn)
        controls.addWidget(self.shuffle_btn)
        root.addLayout(controls)

        vol = QHBoxLayout()
        vol.addWidget(QLabel('Volume'))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(40)
        vol.addWidget(self.volume_slider)
        root.addLayout(vol)