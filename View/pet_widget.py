from __future__ import annotations
from .forest_widget import MapWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

from .theme import ThemeBuilder


class PetWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panelCard")

        self._pet_pixmap = QPixmap("assets/takopi_watching1.png")

        # Dummy theme fallback palette (replace with your ThemeBuilder)
        palette = {
            "panel_light": "#fbf8eb",
            "line": "#d4cbb3",
            "white": "#ffffff",
            "accent_dark": "#6b5d43",
            "accent": "#4a8c20",
            "text": "#2c2519",
            "muted": "#8c826e",
        }

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 12)
        root.setSpacing(6)

        # ── Header ────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        self.name_label = QLabel("Verdant")
        self.name_label.setStyleSheet("font-size: 18px; font-weight: 700;")
        self.favorite_btn = QPushButton("♥")
        self.favorite_btn.setFixedSize(34, 34)
        header.addWidget(self.name_label)
        header.addStretch(1)
        header.addWidget(self.favorite_btn)

        # ── Pet Preview ───────────────────────────────────────────────────────
        self.pet_preview = QLabel()
        self.pet_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_preview.setFixedSize(96, 96)
        self.pet_preview.setStyleSheet("background: transparent;")

        # ── Forest Frame Stage Container ──────────────────────────────────────
        self.forest_container = QFrame()
        self.forest_container.setObjectName("forestStage")
        self.forest_container.setMinimumSize(280, 240)
        self.forest_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.forest_container.setStyleSheet(
            f"QFrame#forestStage {{ background: {palette['panel_light']}; border: 1px solid {palette['line']}; border-radius: 18px; }}"
        )

        container_layout = QVBoxLayout(self.forest_container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(0)

        # INTEGRATION POINT: Add the custom MapWidget here
        self.forest_stage = MapWidget(self.forest_container)
        container_layout.addWidget(self.forest_stage)

        # Heart Badge Overlay
        self.heart_badge = QLabel("♥♥", self.forest_container)
        self.heart_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heart_badge.setFixedSize(42, 24)
        self.heart_badge.setStyleSheet(
            f"QLabel {{ color: {palette['white']}; background: {palette['accent_dark']}; border-radius: 10px; font-size: 12px; font-weight: 800; }}"
        )
        self.heart_badge.move(12, 12)

        scene = QVBoxLayout()
        scene.addWidget(
            self.pet_preview, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        scene.addWidget(self.forest_container)

        # ── HUD Controls ──────────────────────────────────────────────────────
        hud = QHBoxLayout()
        self.hp_label = QLabel("HP 100")
        self.hp_label.setStyleSheet(
            f"color: {palette['white']}; background: {palette['accent_dark']}; border-radius: 10px; padding: 4px 10px;"
        )
        self.stamina_label = QLabel("STA 80")
        self.stamina_label.setStyleSheet(
            f"color: {palette['text']}; background: {palette['panel_light']}; border: 1px solid {palette['line']}; border-radius: 10px; padding: 4px 10px;"
        )
        hud.addWidget(self.hp_label)
        hud.addWidget(self.stamina_label)
        hud.addStretch(1)

        self.mood_label = QLabel("Mood: Calm")
        self.happiness = QProgressBar()
        self.happiness.setValue(72)
        self.happiness.setTextVisible(False)
        self.happiness.setFixedHeight(12)

        root.addLayout(header)
        root.addLayout(scene)
        root.addLayout(hud)
        root.addWidget(self.mood_label)
        root.addWidget(self.happiness)

        self._update_pet_preview()

    def _update_pet_preview(self):
        """Only updates fixed-bounds UI overlays like the Pet profile picture"""
        if not self._pet_pixmap.isNull():
            self.pet_preview.setPixmap(
                self._pet_pixmap.scaled(
                    self.pet_preview.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation,
                )
            )
        self.heart_badge.move(12, 12)
        self.heart_badge.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_pet_preview()

    # ── CLEAN PUBLIC INTERACTION CONTROLS ─────────────────────────────────────
    def complete_day(self, day: int):
        """Call this externally to plant a tree on a specific month day slot."""
        self.forest_stage.grow_tree(day)

    def change_active_focus_day(self, day: int):
        """Call this externally to move the gold active indicator tile highlight."""
        self.forest_stage.set_current_day(day)