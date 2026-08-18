from __future__ import annotations
from typing import Dict

# palettes
#
# Token meaning (kept consistent across all three themes):
#   bg            page background
#   panel         primary text color used ON dark/mid surfaces (panelCard, taskRow, etc.)
#   panel_dark    darkest card surface (gradient stop, dialog chrome)
#   panel_mid     mid surface — task rows, secondary fills
#   panel_light   the "light" surface *within this theme* — used as the
#                 background for inputs and other elevated controls
#   line          border color, tuned to stay visible against BOTH
#                 panel_dark and panel_mid
#   text          body text color used ON panel_light surfaces (inputs,
#                 dialogs) — dark-on-light for Forest Light, light-on-dark
#                 for the two dark themes, since panel_light itself flips
#   muted         secondary/placeholder text, also used ON panel_light
#                 surfaces — same light/dark flip as `text`
#   text_dim      secondary / struck-through text used ON panel_mid or
#                 panel_dark surfaces (e.g. a completed task's title).
#                 This is intentionally a *separate* token from `muted`:
#                 `muted` and panel_mid/panel_dark are close in tone in
#                 every theme here, so reusing `muted` on those surfaces
#                 reads as invisible rather than "dim". text_dim is tuned
#                 against panel_mid specifically.
#   accent / accent_dark / accent_soft   brand green/purple family
#   danger        destructive actions
#   white         literal white, used on filled accent/danger buttons

PALETTES: Dict[str, Dict[str, str]] = {
    "Forest Light": {
        'bg':           '#0f2e22',
        'panel':        '#f6efd8',
        'panel_dark':   '#1d4a37',
        'panel_mid':    '#2e6b4d',
        'panel_light':  '#fbf8ec',
        'line':         '#527461',
        'text':         '#24301e',
        'muted':        '#5b6b53',
        'text_dim':     '#c3d8b9',
        'accent':       '#5f9a52',
        'accent_dark':  '#3f6f3c',
        'accent_soft':  '#a8d68c',
        'danger':       '#c1633c',
        'white':        '#ffffff',
    },
    "Forest Dark": {
        'bg':           '#071912',
        'panel':        '#dce6d4',
        'panel_dark':   '#0e2118',
        'panel_mid':    '#17331f',
        'panel_light':  '#355c40',
        'line':         '#2c4632',
        'text':         '#e4ecdb',
        'muted':        '#a9bca2',
        'text_dim':     '#7fa384',
        'accent':       '#4f9c45',
        'accent_dark':  '#357034',
        'accent_soft':  '#8ecb7a',
        'danger':       '#e2684a',
        'white':        '#ffffff',
    },
    "Pixel Night": {
        'bg':               '#0d0d1a',
        'panel':            '#e7e6ff',
        'panel_dark':       '#15152a',
        'panel_mid':        '#232350',
        'panel_light':      '#3a3a72',
        'line':             '#4a3f82',
        'text':             '#eceaff',
        'muted':            '#b3aede',
        'text_dim':         '#8b85c9',
        'accent':           '#8b5cf6',
        'secondary_button': '#a98bff',
        'accent_dark':      '#6d3fd6',
        'accent_soft':      '#c4a6ff',
        'danger':           '#ff4d6d',
        'white':            '#ffffff',
    },
}


AVAILABLE_THEMES: list[str] = list(PALETTES.keys())
# ["Forest Light", "Forest Dark", "Pixel Night"]

# backward-compatible single-palette export for modules that import `PALETTE`
PALETTE: Dict[str, str] = PALETTES["Forest Dark"]

# call themebuilder in the main window UI so you can change the theme
class ThemeBuilder():
    def __init__(self, parent=None):
        self.current_theme = "Forest Light"

    @property
    # helper to get the current palette theme
    def palette(self) -> Dict[str, str]:
        return PALETTES[self.current_theme]

    def set_theme(self, name: str) -> None:
        if name not in PALETTES:
            raise ValueError(f"Unknown theme '{name}'. Available: {AVAILABLE_THEMES}")
        self.current_theme = name

    def build_style(self) -> str:
        p = self.palette
        return f"""
    QWidget {{
        color: {p['text']};
        font-family: 'Segoe UI';
        font-size: 13px;
    }}
    QFrame#panelCard {{
        background: {p['panel']};
        border: 2px solid {p['line']};
        border-radius: 14px;
    }}
    QFrame#greenCard {{
        background: {p['panel_dark']};
        border: 2px solid {p['line']};
        border-radius: 14px;
    }}    QFrame#navPanel {{
        background: {p['panel']};
        border: 1px solid {p['line']};
        border-radius: 14px;
        padding: 14px;
    }}
    QLabel#appTitle {{
        color: {p['text']};
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 8px;
    }}    QPushButton {{
        background: {p['panel_light']};
        border: 1px solid {p['line']};
        border-radius: 8px;
        padding: 8px 8px;
    }}
    QPushButton:hover {{
        background: {p['panel_light']}cc;
    }}
    QPushButton:pressed {{
        background: {p['panel']}cc;
    }}
    QPushButton#accentButton {{
        background: {p['accent']};
        color: {p['white']};
        font-weight: 700;
    }}
    QPushButton#accentButton:hover {{
        background: {p['accent_dark']};
    }}
    QLineEdit, QComboBox, QSpinBox {{
        background: {p['panel_light']};
        color: {p['text']};
        border: 1px solid {p['line']};
        border-radius: 8px;
        padding: 6px 8px;
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 28px;
        border-left: 1px solid {p['line']};
        
    }}
    QComboBox QAbstractItemView {{
        background: {p['panel_light']};
        color: {p['text']};
        border: 1px solid {p['line']};
        selection-background-color: {p['accent']};
        selection-color: {p['white']};
    }}
    QListWidget {{
        background: {p['panel_light']};
        border: 1px solid {p['line']};
        border-radius: 10px;
        padding: 6px;
    }}
    QSlider::groove:horizontal {{
        height: 8px;
        background: {p['accent_soft']};
        border-radius: 4px;
    }}
    QSlider::handle:horizontal {{
        background: {p['panel_mid']};
        width: 16px;
        margin: -4px 0;
        border-radius: 8px;
    }}
    QPushButton.sidebarButton {{
        background: {p['panel_mid']};
        color: {p['white']};
        border: 1px solid {p['line']};
        border-radius: 12px;
        font-weight: 700;
        min-height: 56px;
    }}
    QPushButton.sidebarButton:checked {{
        background: {p['accent_dark']};
    }}
    QFrame#panelCard {{
        max-height: 780px;
        min-height: 320px;
    }}
    QLabel#cycleLabel {{
        font-size: 22px;
    }}
    QLabel#metaLabel {{
        font-size: 12px;
    }}
    QPushButton {{
        min-height: 40px;
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QPushButton#accentButton {{
        font-size: 13px;
    }}
    QPushButton#secondaryButton {{
        min-height: 36px;
    }}
    QDialog {{
        background: {p['panel_light']};
    }}
    """
    def stylesheet(self) -> str:
        return self.build_style()