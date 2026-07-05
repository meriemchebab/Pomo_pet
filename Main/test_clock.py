from __future__ import annotations

import os
import sys
from PySide6.QtWidgets import QApplication

# ensure project root is on sys.path so package imports like View work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from View.clock_widget import ClockWidget
from View.theme import ThemeBuilder


def main() -> None:
    app = QApplication(sys.argv)
    # apply global theme
    builder = ThemeBuilder()
    app.setStyleSheet(builder.stylesheet())

    w = ClockWidget()
    w.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
