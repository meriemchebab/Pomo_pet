from __future__ import annotations
from typing import  Dict

# palettes

PALETTES: Dict[str, Dict[str, str]] = {
    "Forest Light": {
        'bg':           '#123c2f',
        'panel':        '#efe7d1',
        'panel_dark':   '#2f6d52',
        'panel_mid':    '#3e7e5f',
        'panel_light':  '#f7f1dd',
        'line':         '#6b5d43',
        'text':         '#2c2418',
        'muted':        '#6f6a57',
        'accent':       '#537d4f',
        'accent_dark':  '#35573b',
        'accent_soft':  '#9bbc73',
        'danger':       '#8b5e3c',
        'white':        '#ffffff',
    },
    "Forest Dark": {
        'bg':           '#0a1f17',
        'panel':        '#1a2e24',
        'panel_dark':   '#142318',
        'panel_mid':    '#1f3528',
        'panel_light':  "#487143",
        'line':         '#2e4a38',
        'text':         '#d4cdb8',
        'muted':        '#7a8c7e',
        'accent':       "#68C260",
        'accent_dark':  '#4a8a44',
        'accent_soft':  '#8fcc7a',
        'danger':       '#c0714a',
        'white':        '#ffffff',
    },
    "Pixel Night": {
        'bg':           '#0d0d1a',
        'panel':        '#1a1a2e',
        'panel_dark':   '#16213e',
        'panel_mid':    '#0f3460',
        'panel_light':  "#5252a5",
        'line':         '#533483',
        'text':         '#e0e0ff',
        'muted':        '#8888aa',
        'accent':       '#7b2fff',
        'secondary_button' :"#ae80ffff",
        'accent_dark':  '#5a1fcc',
        'accent_soft':  '#b57bee',
        'danger':       '#ff4466',
        'white':        '#ffffff',
    },
}


AVAILABLE_THEMES: list[str] = list(PALETTES.keys())
# ["Forest Light", "Forest Dark", "Pixel Night"]

# backward-compatible single-palette export for modules that import `PALETTE`
PALETTE: Dict[str, str] = PALETTES["Forest Dark"]

# call themebuilder in the main window UI so you can change the theme 
class ThemeBuilder():
    def __init__(self,parent = None):
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