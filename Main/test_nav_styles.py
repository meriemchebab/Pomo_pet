from __future__ import annotations

import os
import sys

import pytest
from PySide6.QtWidgets import QApplication

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from View.main_widget import Sidebar


@pytest.fixture(scope="module")
def app() :
    qapp = QApplication.instance() or QApplication([])
    yield qapp


def test_sidebar_nav_item_stylesheet_has_single_nav_rule(app: QApplication) -> None:
    """The nav-item selector should only be defined once to avoid style conflicts."""
    sidebar = Sidebar()

    stylesheet = sidebar.styleSheet()

    assert stylesheet.count("QWidget#NavItem {") == 1
    assert "QWidget#NavItem:hover" in stylesheet
