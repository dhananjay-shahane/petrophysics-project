import sys
import numpy as np


from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QDockWidget, QToolBar,
    QMenuBar, QMenu, QListWidget, QWidget, QVBoxLayout,QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from matplotlib_widget import MatplotlibWidget
from toolbar import create_toolbar, create_main_toolbar
from felib.custom_dock_widget_pyside import CustomDockWidget, FeedbackDockWidget
from custom_object import CustomObject


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dockable Window Application")
        self.dock_count = 1
        self.docks = {}  # Dictionary to keep track of dock widgets
        self.yobjects_dock_created = False  # Flag to track YOBJECTS dock creation
        self.xobjects_items = []  # Initialize list for XOBJECTS
        self.yobjects_items = []  # Initialize list for YOBJECTS
        self.init_ui()

    def init_ui(self):
        # Set an empty central widget
        self.setCentralWidget(QWidget())  # Create and set an empty central widget

        # Create initial dockable windows
        self.create_xobject_dock()  # Create the XOBJECTS dock
        self.create_yobjects_dock()  # Create the YOBJECTS dock only once
        self.create_matplotlib_dock()  # Create a dockable window with Matplotlib plot
        self.create_feedback_dock()   # Create the Feedback dock

        # Create the menu bar
        self.create_menu_bar()

        # Create the main toolbar
        create_main_toolbar(self)  # Use the imported function

    def create_xobject_dock(self):
        """Create the dockable window with a list box titled 'XOBJECTS'."""
        container = QWidget()
        layout = QVBoxLayout(container)

        list_box = self.create_xobjects_list_box()
        layout.addWidget(list_box)

        xobject_dock = CustomDockWidget("XOBJECTS", self)
        xobject_dock.setWidget(container)
        self.addDockWidget(Qt.LeftDockWidgetArea, xobject_dock)
        self.docks["XOBJECTS"] = xobject_dock

    def create_yobjects_dock(self):
        """Create the dockable window with a list box titled 'YOBJECTS'."""
        if not self.yobjects_dock_created:
            container = QWidget()
            layout = QVBoxLayout(container)
            
            list_box = self.create_yobjects_list_box()
            layout.addWidget(list_box)

            yobjects_dock = CustomDockWidget("YOBJECTS", self)
            yobjects_dock.setWidget(container)
            self.addDockWidget(Qt.RightDockWidgetArea, yobjects_dock)
            self.docks["YOBJECTS"] = yobjects_dock
            self.yobjects_dock_created = True  # Update the flag

    def create_matplotlib_dock(self):
        """Create the dockable window with a Matplotlib plot."""
        container = QWidget()
        layout = QVBoxLayout(container)

        matplotlib_widget = MatplotlibWidget()
        layout.addWidget(matplotlib_widget)

        matplotlib_dock = CustomDockWidget("Matplotlib Plot", self)
        matplotlib_dock.setWidget(container)
        self.addDockWidget(Qt.TopDockWidgetArea, matplotlib_dock)
        self.docks["Matplotlib Plot"] = matplotlib_dock

    def create_feedback_dock(self):
        """Create the dockable window titled 'Feedback' with a QTextEdit, docked at the bottom."""
        feedback_text_edit = QTextEdit()
        feedback_text_edit.setPlaceholderText("Provide your feedback here...")
        feedback_text_edit.setAcceptRichText(False)  # Set to plain text
        feedback_text_edit.setReadOnly(False)  # Allow editing (optional)
        feedback_text_edit.setLineWrapMode(QTextEdit.WidgetWidth)  # Enable line wrapping
        
        feedback_dock = FeedbackDockWidget("Feedback", self)
        feedback_dock.setWidget(feedback_text_edit)
        self.addDockWidget(Qt.BottomDockWidgetArea, feedback_dock)
        self.docks["Feedback"] = feedback_dock

    def create_xobjects_list_box(self):
        """Create and return a QListWidget with custom objects for the 'XOBJECTS' dock."""
        list_widget = QListWidget()
        self.xobjects_items = [
            CustomObject("Item A", "Description for item A"),
            CustomObject("Item B", "Description for item B"),
            CustomObject("Item C", "Description for item C"),
            CustomObject("Item D", "Description for item D")
        ]
        for item in self.xobjects_items:
            list_widget.addItem(str(item))  # Use the __str__ method of CustomObject

        list_widget.itemClicked.connect(self.on_xobjects_item_clicked)
        return list_widget

    def create_yobjects_list_box(self):
        """Create and return a QListWidget with custom objects for the 'YOBJECTS' dock."""
        list_widget = QListWidget()
        self.yobjects_items = [
            CustomObject("Another Item 1", "Description for another item 1"),
            CustomObject("Another Item 2", "Description for another item 2"),
            CustomObject("Another Item 3", "Description for another item 3"),
            CustomObject("Another Item 4", "Description for another item 4")
        ]
        for item in self.yobjects_items:
            list_widget.addItem(str(item))  # Use the __str__ method of CustomObject

        list_widget.itemClicked.connect(self.on_yobjects_item_clicked)
        return list_widget

    def on_xobjects_item_clicked(self, item):
        """Slot to handle item clicks in the XOBJECTS list box and display the selected item's name in the Feedback dock widget."""
        selected_object = next((obj for obj in self.xobjects_items if str(obj) == item.text()), None)
        if selected_object:
            feedback_dock = self.docks.get("Feedback")
            if feedback_dock:
                text_edit = feedback_dock.widget()
                if isinstance(text_edit, QTextEdit):
                    current_text = text_edit.toPlainText()
                    new_text = f"Selected XOBJECT: {selected_object.name}\n"
                    text_edit.setPlainText(current_text + new_text)

    def on_yobjects_item_clicked(self, item):
        """Slot to handle item clicks in the YOBJECTS list box and display the selected item's name in the Feedback dock widget."""
        selected_object = next((obj for obj in self.yobjects_items if str(obj) == item.text()), None)
        if selected_object:
            feedback_dock = self.docks.get("Feedback")
            if feedback_dock:
                text_edit = feedback_dock.widget()
                if isinstance(text_edit, QTextEdit):
                    current_text = text_edit.toPlainText()
                    new_text = f"Selected YOBJECT: {selected_object.name}\n"
                    text_edit.setPlainText(current_text + new_text)

    def create_menu_bar(self):
        """Create and set up the menu bar."""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        new_dock_action = QAction("New Dockable Window", self)
        new_dock_action.triggered.connect(self.create_new_dockable_window)
        file_menu.addAction(new_dock_action)

        remove_central_action = QAction("Remove Central Widget", self)
        remove_central_action.triggered.connect(self.remove_central_widget)
        file_menu.addAction(remove_central_action)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        dock_menu = menu_bar.addMenu("Dock")
        for title in self.docks:
            show_hide_action = QAction(f"Toggle {title}", self, checkable=True)
            show_hide_action.setChecked(True)
            show_hide_action.triggered.connect(lambda checked, t=title: self.toggle_dock(checked, t))
            dock_menu.addAction(show_hide_action)

    def create_new_dockable_window(self):
        """Create a new dockable window with a QTextEdit."""
        self.dock_count += 1
        new_dock = CustomDockWidget(f"Dockable Window {self.dock_count}", self)
        new_dock.setWidget(QTextEdit())
        self.addDockWidget(Qt.RightDockWidgetArea, new_dock)
        self.docks[f"Dockable Window {self.dock_count}"] = new_dock

    def remove_central_widget(self):
        """Remove the central widget."""
        self.setCentralWidget(QWidget())  # Reset to an empty widget

    def toggle_dock(self, checked, title):
        """Show or hide dockable widgets."""
        dock = self.docks.get(title)
        if dock:
            if checked:
                dock.show()
            else:
                dock.hide()

# if __name__ == "__main__":
#     from PySide6.QtWidgets import QApplication
#     import sys

#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.resize(800, 600)
#     window.show()
#     sys.exit(app)