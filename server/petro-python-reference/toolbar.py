from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction
def create_toolbar(parent):
    """Create and return a toolbar."""
    toolbar = QToolBar("Toolbar", parent)
    open_action = QAction("Open", parent)
    save_action = QAction("Save", parent)
    toolbar.addAction(open_action)
    toolbar.addAction(save_action)
    return toolbar

def create_main_toolbar(window):
    """Create and set up the main toolbar."""
    toolbar = QToolBar("Main Toolbar", window)
    window.addToolBar(toolbar)

    # Add actions to the toolbar
    new_action = QAction("New", window)
    open_action = QAction("Open", window)
    save_action = QAction("Save", window)
    exit_action = QAction("Exit", window)
    exit_action.setShortcut("Ctrl+Q")
    exit_action.setStatusTip("Exit application")
    exit_action.triggered.connect(window.close)

    toolbar.addAction(new_action)
    toolbar.addAction(open_action)
    toolbar.addAction(save_action)
    toolbar.addAction(exit_action)
