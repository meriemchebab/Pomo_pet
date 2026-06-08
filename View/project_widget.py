from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class TaskRow(QFrame):
    focus_requested = Signal(str)
    deleted = Signal(str)
    toggled = Signal(str, bool)

    def __init__(self, task_id: str, title: str, tomatoes: int = 0, done: bool = False, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.setObjectName("taskRow")

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(done)
        self.checkbox.stateChanged.connect(self._emit_toggle)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("taskTitle")
        self.title_label.setProperty("done", done)

        self.tomato_label = QLabel(f"🍓 {tomatoes}")
        self.tomato_label.setObjectName("tomatoCount")

        self.delete_btn = QPushButton("×")
        self.delete_btn.setObjectName("deleteTaskBtn")
        self.delete_btn.setFixedSize(28, 28)
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

        left = QHBoxLayout()
        left.setSpacing(8)

        self.dot = QLabel("●")
        self.dot.setObjectName("projectDot")
        self.dot.setStyleSheet(f"color: {color};")

        self.title_label = QLabel(title)
        self.title_label.setObjectName("projectTitle")

        left.addWidget(self.dot)
        left.addWidget(self.title_label)

        self.count_label = QLabel("0")
        self.count_label.setObjectName("projectCount")

        self.arrow = QToolButton()
        self.arrow.setObjectName("arrowBtn")
        self.arrow.setText("▾" if expanded else "▸")
        self.arrow.clicked.connect(self.toggle_expand)

        header.addLayout(left)
        header.addStretch()
        header.addWidget(self.count_label)
        header.addWidget(self.arrow)

        self.root.addLayout(header)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(22, 2, 0, 0)
        self.body_layout.setSpacing(8)

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
        self.add_btn.setFixedSize(24, 24)
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panelCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 14)
        root.setSpacing(12)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Projects & Tasks")
        title.setObjectName("pageTitle")

        self.new_project_btn = QPushButton("+ New Project")
        self.new_project_btn.setObjectName("newProjectBtn")

        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.new_project_btn)

        root.addLayout(top)

        self.chrono_section = ProjectSection("chrono_forest", "Chrono Forest", "#78b54d", True)
        self.generic_section = ProjectSection("generic_work", "Generic Work", "#d8b24e", True)
        self.ibm_section = ProjectSection("ibm_certificate", "IBM Certificate", "#6b88ea", False)

        self.chrono_section.add_task("t1", "Build ClockWidget", 6, True)
        self.chrono_section.add_task("t2", "Build ForestWidget", 3, False)
        self.chrono_section.add_task("t3", "Wire signals", 0, False)

        self.generic_section.add_task("t4", "Quick task without project", 1, False)

        for section in (self.chrono_section, self.generic_section, self.ibm_section):
            section.add_task_requested.connect(self._forward_add_task)
            root.addWidget(section)

        root.addStretch()

        self.footer_note = QLabel("• No active task — click a task to focus")
        self.footer_note.setObjectName("footerNote")
        root.addWidget(self.footer_note)

        self._apply_style()

    def _forward_add_task(self, project_id: str, text: str):
        self.add_task_requested.emit(project_id, text)

    def _apply_style(self):
        self.setStyleSheet("""
        QFrame#panelCard {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #143427,
                stop:1 #102c21
            );
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }

        QLabel#pageTitle {
            color: #e5eedb;
            font-size: 18px;
            font-weight: 700;
        }

        QPushButton#newProjectBtn {
            background: rgba(37, 71, 52, 0.9);
            color: #dce9d0;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 10px 14px;
            font-size: 14px;
            font-weight: 700;
        }

        QPushButton#newProjectBtn:hover {
            background: rgba(48, 88, 64, 0.95);
        }

        QLabel#projectDot {
            font-size: 14px;
        }

        QLabel#projectTitle {
            color: #dbe8cf;
            font-size: 16px;
            font-weight: 700;
        }

        QLabel#projectCount {
            color: rgba(188, 206, 170, 0.58);
            font-size: 13px;
            font-weight: 700;
            min-width: 14px;
        }

        QToolButton#arrowBtn {
            background: transparent;
            border: none;
            color: rgba(188, 206, 170, 0.58);
            font-size: 14px;
            font-weight: 700;
        }

        QFrame#taskRow {
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.045);
            border-radius: 13px;
        }

        QLabel#taskTitle {
            color: #e7eedc;
            font-size: 14px;
            font-weight: 600;
        }

        QLabel#taskTitle[done="true"] {
            color: rgba(198, 212, 182, 0.45);
            text-decoration: line-through;
        }

        QLabel#tomatoCount {
            color: rgba(214, 183, 184, 0.72);
            font-size: 13px;
            font-weight: 600;
        }

        QPushButton#deleteTaskBtn {
            background: rgba(255,255,255,0.03);
            color: rgba(207, 220, 193, 0.5);
            border: 1px solid rgba(255,255,255,0.04);
            border-radius: 10px;
            font-size: 16px;
        }

        QPushButton#deleteTaskBtn:hover {
            background: rgba(255,255,255,0.06);
            color: #e3ecd8;
        }

        QLineEdit#taskInput {
            background: #f4f2ec;
            color: #26231f;
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 14px;
            font-style: italic;
        }

        QPushButton#miniAddBtn {
            background: transparent;
            color: rgba(188, 206, 170, 0.50);
            border: none;
            font-size: 18px;
            font-weight: 700;
        }

        QPushButton#miniAddBtn:hover {
            color: #dfead5;
        }

        QCheckBox {
            spacing: 0px;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 1px solid rgba(210,225,194,0.18);
            background: transparent;
        }

        QCheckBox::indicator:checked {
            background: #4a7333;
            border: 1px solid rgba(156,198,99,0.28);
        }

        QLabel#footerNote {
            color: rgba(215, 189, 118, 0.75);
            font-size: 13px;
            font-style: italic;
            padding-top: 6px;
        }
        """)