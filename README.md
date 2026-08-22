# 🐾 Pomo Pet — Productivity Meets Companionship

> A delightful desktop Pomodoro productivity app built with **Python** & **PySide6**, featuring an interactive virtual pet, forest habit tracker, ambient multi-track white noise, and tactile game-like sound effects.

---

## Features

### Pomodoro Timer
* **Analog & Digital Display**: Clean visual progress arc with remaining time and active task display.
* **Smart Phase Progression**: Work (25m), Short Break (5m), and Long Break (30m) cycles.
* **Quick Setup & Global Preferences**: Customize session timers on-the-fly or save global default preferences.
* **Task Focus Integration**: Select a task from your projects to display and track Pomodoro completions.

### Virtual Pet & Forest Companion
* **Productivity Gamification**: Complete daily Pomodoro sessions to care for your virtual pet.
* **Streak & Habit Tracking**: Track completed focus days and visualize your growth in the forest panel.

### Ambient White Noise & Tactile Sounds
* **Multi-Track Mixer**: Simultaneously mix Rain , Ocean , Fireplace , Forest , and Clock ambient sounds.
* **Tactile Click Feedback**: Game-like wood tick sound feedback on button presses, sliders, toggles, and dropdowns.
* **Audio Notifications**: Configurable chime alerts for focus start, break start, and session completion.

### Projects & Task Management
* **Organized Workflow**: Group tasks under custom projects with color tags.
* **SQLite Persistence**: Automatically saves project structure, task progress, and user preferences.

### Themes & Customization
* **Built-in Palettes**: Includes **Forest Light**, **Forest Dark**, and **Pixel Night** themes.
* **Dynamic Styling**: High-contrast UI components and smooth animations.

---

## Quick Start

### 1. Prerequisites
* **Python 3.9+** installed on your system.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/Pomo_pet.git
cd Pomo_pet

# Create a virtual environment (optional but recommended)
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install PySide6
```

### 3. Run the App
```bash
python Main/main.py
```

---

## Project Architecture

`Pomo Pet` is structured using the **Model-View-Controller (MVC)** architectural pattern:

```
Pomo_pet/
├── Main/                    # Entry point & app setup
│   └── main.py              # Main execution script
├── View/                    # UI Components (PySide6)
│   ├── main_widget.py       # Main window container
│   ├── clock_widget.py      # Pomodoro timer view
│   ├── whiteNoise_widget.py # Ambient sound mixer view
│   ├── project_widget.py    # Tasks & projects view
│   ├── pet_widget.py        # Virtual pet status view
│   ├── forest_widget.py     # Forest tracker view
│   ├── settings_widget.py   # App settings view
│   └── theme.py             # Theme builder & color palettes
├── Controller/              # Business Logic & Event Mediators
│   ├── main_controller.py   # Application mediator
│   ├── clock_controller.py  # Timer lifecycle controller
│   ├── white_noise_controller.py # Audio engine controller
│   ├── project_controller.py# Task & project manager controller
│   └── settings_controller.py# Settings controller
├── Model/                   # Data Models & Audio Engine
│   ├── clock_model.py       # Pomodoro timer logic & state
│   ├── sound_engine.py      # QSoundEffect audio engine
│   ├── tasks_manager_model.py# Task & project data models
│   └── app_settings_model.py# Settings persistence model
├── DataBase/                # Database & DAO Layer
│   ├── db_connection.py    # SQLite database connection
│   └── DAO/                 # Data Access Objects (DAO)
└── assets/                  # Images, icons, and audio WAV files
```

---

## Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check out [issues](../../issues) if you want to contribute.

---

## License

Distributed under the **MIT License**. See `LICENSE` for more information.
