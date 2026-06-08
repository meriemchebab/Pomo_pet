from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit


class TasksWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('panelCard')
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel('Pomodoro Tasks')
        title.setStyleSheet('font-size: 20px; font-weight: 700;')
        root.addWidget(title)

        add_row = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText('Add a task for this pomodoro...')
        self.add_btn = QPushButton('Add')
        self.add_btn.setObjectName('accentButton')
        add_row.addWidget(self.task_input)
        add_row.addWidget(self.add_btn)
        root.addLayout(add_row)

        self.task_list = QListWidget()
        self.task_list.addItems(['Review math notes', 'Solve 2 algorithm exercises', 'Refactor timer logic'])
        root.addWidget(self.task_list)

        footer = QHBoxLayout()
        self.complete_btn = QPushButton('Mark done')
        self.remove_btn = QPushButton('Remove')
        footer.addWidget(self.complete_btn)
        footer.addWidget(self.remove_btn)
        root.addLayout(footer)