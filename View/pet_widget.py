from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QPushButton, QVBoxLayout, QHBoxLayout

from .theme import ThemeBuilder


class PetWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('panelCard')
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        self.pet_preview = QLabel('PET ART\n128 x 128')
        self.pet_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_preview.setMinimumHeight(170)
        muted_palette = ThemeBuilder().palette
        self.pet_preview.setStyleSheet(
            f"background: #9fc985; border: 2px dashed {muted_palette['accent_dark']}; border-radius: 10px; font-weight: 700;"
        )

        top = QHBoxLayout()
        self.name_label = QLabel('Verdant')
        self.name_label.setStyleSheet('font-size: 20px; font-weight: 700;')
        self.favorite_btn = QPushButton('♥')
        self.favorite_btn.setFixedWidth(34)
        top.addWidget(self.name_label)
        top.addStretch(1)
        top.addWidget(self.favorite_btn)

        self.mood_label = QLabel('Mood: Calm')
        self.happiness = QProgressBar()
        self.happiness.setRange(0, 100)
        self.happiness.setValue(72)
        self.happiness.setTextVisible(False)
        palette = ThemeBuilder().palette
        self.happiness.setStyleSheet(
            "QProgressBar {background:#ddd2b8; border:1px solid #6b5d43; border-radius:7px; height:14px;}"
            f"QProgressBar::chunk {{background:{palette['accent']}; border-radius:6px;}}"
        )

        root.addWidget(self.pet_preview)
        root.addLayout(top)
        root.addWidget(self.mood_label)
        root.addWidget(self.happiness)

    def set_pet_art(self, path: str):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.pet_preview.setPixmap(pixmap.scaled(
                self.pet_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation
            ))