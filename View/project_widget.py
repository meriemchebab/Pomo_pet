from __future__ import annotations
from .theme import ThemeBuilder
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class ProjectNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setModal(True)
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("Project name")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        self.input = QLineEdit()
        self.input.setPlaceholderText("work")
        layout.addWidget(self.input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def value(self) -> str:
        return self.input.text().strip()


class TaskRow(QFrame):
    focus_requested = Signal(str)
    deleted = Signal(str)
    toggled = Signal(str, bool)

    def __init__(self, task_id: str, title: str, tomatoes: int = 0, done: bool = False, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.setObjectName("taskRow")

        # Slightly taller vertical padding + tighter, more deliberate spacing
        # between elements so the row doesn't feel like one crowded strip.
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 10, 10, 10)
        root.setSpacing(10)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(done)
        self.checkbox.stateChanged.connect(self._emit_toggle)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("taskTitle")
        self.title_label.setProperty("done", done)
        self.title_label.setWordWrap(True)

        # Tomato count is now a small pill/badge instead of plain text,
        # so it reads as a metric rather than blending into the row.
        self.tomato_label = QLabel(f"🍅 {tomatoes}")
        self.tomato_label.setObjectName("tomatoCount")
        self.tomato_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Delete button: was 36x28 with a bulky " X " label that visually
        # outweighed everything else in a ~48px-tall row. Now a small,
        # circular, low-emphasis icon button that only asserts itself
        # (danger red + white glyph) on hover.
        self.delete_btn = QPushButton("×")
        self.delete_btn.setObjectName("deleteTaskBtn")
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(lambda: self.deleted.emit(self.task_id))

        root.addWidget(self.checkbox)
        root.addWidget(self.title_label, 1)
        root.addWidget(self.tomato_label)
        root.addWidget(self.delete_btn)

        self.mousePressEvent = self._click_focus

        self._refresh_done_style()

    def _click_focus(self, event):
        self.focus_requested.emit(self.task_id)
        QWidget.mousePressEvent(self, event)

    def _emit_toggle(self, state):
        done = state == Qt.CheckState.Checked.value
        self.title_label.setProperty("done", done)
        self._refresh_done_style()
        self.toggled.emit(self.task_id, done)

    def _refresh_done_style(self):
        self.title_label.style().unpolish(self.title_label)
        self.title_label.style().polish(self.title_label)


class ProjectSection(QFrame):
    add_task_requested = Signal(str, str)
    delete_project_requested = Signal(str)
    task_deleted = Signal(str)
    task_toggled = Signal(str, bool)
    task_focused = Signal(str)

    def __init__(self, project_id: str, title: str, color: str, expanded: bool = True, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.setObjectName("projectSection")

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(2, 0, 2, 0)
        header.setSpacing(10)

        left = QHBoxLayout()
        left.setSpacing(8)

        self.dot = QLabel("●")
        self.dot.setObjectName("projectDot")
        self.dot.setStyleSheet(f"color: {color};")

        self.title_label = QLabel(title)
        self.title_label.setObjectName("projectTitle")

        left.addWidget(self.dot)
        left.addWidget(self.title_label)

        self.delete_project_btn = QPushButton("Delete")
        self.delete_project_btn.setObjectName("deleteProjectBtn")
        self.delete_project_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_project_btn.clicked.connect(
            lambda: self.delete_project_requested.emit(self.project_id)
        )

        self.count_label = QLabel("0")
        self.count_label.setObjectName("projectCount")

        self.arrow = QToolButton()
        self.arrow.setObjectName("arrowBtn")
        self.arrow.setText("▾" if expanded else "▸")
        self.arrow.setCursor(Qt.CursorShape.PointingHandCursor)
        self.arrow.clicked.connect(self.toggle_expand)

        header.addLayout(left)
        header.addStretch()
        header.addWidget(self.count_label)
        header.addWidget(self.delete_project_btn)
        header.addWidget(self.arrow)

        self.root.addLayout(header)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(22, 4, 0, 0)
        self.body_layout.setSpacing(10)

        self.task_container = QVBoxLayout()
        self.task_container.setSpacing(8)
        self.body_layout.addLayout(self.task_container)

        add_row = QHBoxLayout()
        add_row.setSpacing(8)

        self.input = QLineEdit()
        self.input.setObjectName("taskInput")
        self.input.setPlaceholderText("Add task…")
        self.input.returnPressed.connect(self._submit_task)

        self.add_btn = QPushButton("+")
        self.add_btn.setObjectName("miniAddBtn")
        self.add_btn.setFixedSize(26, 26)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self._submit_task)

        add_row.addWidget(self.input, 1)
        add_row.addWidget(self.add_btn)

        self.body_layout.addLayout(add_row)
        self.root.addWidget(self.body)

        self.body.setVisible(expanded)

    def toggle_expand(self):
        expanded = not self.body.isVisible()
        self.body.setVisible(expanded)
        self.arrow.setText("▾" if expanded else "▸")

    def add_task(self, task_id: str, title: str, tomatoes: int = 0, done: bool = False):
        row = TaskRow(task_id, title, tomatoes, done)
        row.deleted.connect(self.task_deleted)
        row.toggled.connect(self.task_toggled)
        row.focus_requested.connect(self.task_focused)
        self.task_container.addWidget(row)
        self._update_count()

    def _submit_task(self):
        text = self.input.text().strip()
        if not text:
            return
        self.add_task_requested.emit(self.project_id, text)
        self.input.clear()

    def _update_count(self):
        self.count_label.setText(str(self.task_container.count()))


class ProjectsWidget(QFrame):
    add_task_requested = Signal(str, str)
    delete_project_requested = Signal(str)
    delete_task_requested = Signal(str)
    toggle_task_requested = Signal(str, bool)
    focus_task_requested = Signal(str)
    new_project_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panelCard")

        self._sections = {}

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(16, 16, 16, 14)
        self.root.setSpacing(12)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Projects & Tasks")
        title.setObjectName("pageTitle")

        self.new_project_btn = QPushButton("+ New Project")
        self.new_project_btn.setObjectName("newProjectBtn")
        self.new_project_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_project_btn.clicked.connect(self._open_new_project_dialog)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.new_project_btn)

        self.root.addLayout(top)

        self.sections_container = QVBoxLayout()
        self.sections_container.setSpacing(12)
        self.root.addLayout(self.sections_container)

        self.root.addStretch()

        self.footer_note = QLabel("• you can do this one task at a time")
        self.footer_note.setObjectName("footerNote")
        self.root.addWidget(self.footer_note)

        self._apply_style()

    def _open_new_project_dialog(self):
        dialog = ProjectNameDialog(self)
        if dialog.exec():
            self.new_project_requested.emit(dialog.value())

    def set_projects_section(self, projects: list[dict]):
        self._clear_sections()
        self._sections.clear()

        for project in projects:
            section = ProjectSection(
                project["id"],
                project["title"],
                project["color"],
                project.get("expanded", False),
            )

            for task in project.get("tasks", []):
                section.add_task(
                    task["id"],
                    task["title"],
                    task.get("tomatoes", 0),
                    task.get("done", False),
                )

            section.add_task_requested.connect(self.add_task_requested)
            section.delete_project_requested.connect(self.delete_project_requested)
            section.task_deleted.connect(self.delete_task_requested)
            section.task_toggled.connect(self.toggle_task_requested)
            section.task_focused.connect(self.focus_task_requested)

            self._sections[project["id"]] = section
            self.sections_container.addWidget(section)

    def _clear_sections(self):
        while self.sections_container.count():
            item = self.sections_container.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    def add_task_to_project(self, project_id: str, task: dict):
        project_id = project_id or "generic_work"
        section = self._sections.get(project_id)
        if section is None:
            return

        section.add_task(
            task["id"],
            task["title"],
            task.get("tomatoes", 0),
            task.get("done", False),
        )

    def _apply_style(self):
        p = ThemeBuilder().palette

        self.setStyleSheet(f"""
        QFrame#panelCard {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {p['panel_dark']},
                stop:1 {p['bg']}
            );
            border: 1px solid {p['line']};
            border-radius: 18px;
        }}

        QLabel#pageTitle {{
            color: {p['panel']};
            font-size: 18px;
            font-weight: 700;
        }}

        QPushButton#newProjectBtn {{
            background: {p['panel_mid']};
            color: {p['panel']};
            border: 1px solid {p['line']};
            border-radius: 12px;
            padding: 10px 14px;
            font-size: 14px;
            font-weight: 700;
        }}

        QPushButton#newProjectBtn:hover {{
            background: {p['accent_dark']};
        }}

        /* Was: background panel_mid + color muted -> muted brown-gray text
           on a mid-green fill had barely any contrast. Now a "ghost" button:
           transparent fill, light readable border/text, fills solid red
           with white text on hover so the destructive intent is obvious. */
        QPushButton#deleteProjectBtn {{
            background: transparent;
            color: {p['panel']};
            border: 1px solid {p['line']};
            border-radius: 10px;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 700;
        }}

        QPushButton#deleteProjectBtn:hover {{
            background: {p['danger']};
            border-color: {p['danger']};
            color: {p['white']};
        }}

        QLabel#projectDot {{
            font-size: 14px;
        }}

        QLabel#projectTitle {{
            color: {p['panel']};
            font-size: 16px;
            font-weight: 700;
        }}

        /* Was `muted` on the dark panelCard background -> nearly invisible.
           Swapped to accent_soft, which is the light green already used
           for the footer note and reads clearly here too. */
        QLabel#projectCount {{
            color: {p['accent_soft']};
            font-size: 13px;
            font-weight: 700;
            min-width: 16px;
        }}

        QToolButton#arrowBtn {{
            background: transparent;
            border: none;
            color: {p['accent_soft']};
            font-size: 14px;
            font-weight: 700;
            padding: 4px;
        }}

        QToolButton#arrowBtn:hover {{
            color: {p['panel']};
        }}

        QFrame#taskRow {{
            background: {p['panel_mid']};
            border: 1px solid {p['line']};
            border-radius: 12px;
        }}

        QFrame#taskRow:hover {{
            border: 1px solid {p['accent_soft']};
        }}

        QLabel#taskTitle {{
            color: {p['panel']};
            font-size: 14px;
            font-weight: 600;
        }}

        QLabel#taskTitle[done="true"] {{
            color: {p['text_dim']};
            text-decoration: line-through;
        }}

        /* Tomato count is now a small badge (accent fill + white text)
           instead of low-contrast text sitting directly on the row. */
        QLabel#tomatoCount {{
            background: {p['accent_dark']};
            color: {p['white']};
            border-radius: 9px;
            padding: 2px 8px;
            font-size: 12px;
            font-weight: 700;
        }}

        /* Was a 36x28 filled box with a bulky " X " label — heavier than
           the checkbox next to it. Now a small transparent circular icon
           button, quiet at rest, that turns into a clear red "delete"
           affordance only on hover. */
        QPushButton#deleteTaskBtn {{
            background: transparent;
            color: {p['panel']};
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 700;
            padding: 0px;
        }}

        QPushButton#deleteTaskBtn:hover {{
            background: {p['danger']};
            color: {p['white']};
        }}

        QLineEdit#taskInput {{
            background: {p['panel_light']};
            color: {p['text']};
            border: 1px solid {p['line']};
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 14px;
        }}

        /* Was `muted` on transparent (= dark panelCard bg showing through)
           -> barely legible "+" button. */
        QPushButton#miniAddBtn {{
            background: transparent;
            color: {p['accent_soft']};
            border: none;
            border-radius: 13px;
            font-size: 18px;
            font-weight: 700;
        }}

        QPushButton#miniAddBtn:hover {{
            background: {p['accent']};
            color: {p['white']};
        }}

        QCheckBox {{
            spacing: 0px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid {p['line']};
            background: {p['panel_light']};
        }}

        QCheckBox::indicator:checked {{
            background: {p['accent']};
            border: 1px solid {p['accent_dark']};
        }}

        QLabel#footerNote {{
            color: {p['accent_soft']};
            font-size: 13px;
            font-style: italic;
            padding-top: 6px;
        }}
        """)