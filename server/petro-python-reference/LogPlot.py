from PyQt5.QtWidgets import QDockWidget, QTreeView, QTabWidget, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSplitter
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QPoint
from logs_widget import *
from logvalues_widget import *
import pandas as pd
from logplotclass import *

class LogPlotDockWidget(QDockWidget):
    def __init__(self, title, mainwindow, parent=None):
        super().__init__(title,  parent)
        self.mainwindow = mainwindow
        self.setWindowTitle("Matplotlib with Dynamic Dock Widgets and Shared Y-Axis")
        self.setGeometry(100, 100, 800, 600)

        # Set up the main widget
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        
        # Create a horizontal layout
        layout = QHBoxLayout(self.main_widget)

        # Create a horizontal splitter
        self.splitter = QSplitter(Qt.Horizontal)
        # Create the main figure widget
        self.main_figure_widget = MainFigureWidget()
        self.shared_axis = self.main_figure_widget.figure.axes[0]
        #self.splitter.addWidget(self.main_figure_widget)

        # Keep track of dock widgets
        self.docks = []

        # Create a scroll area for the splitter
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.splitter)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
         # Set the size policy for the main splitter to allow it to grow
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create a spacer item
        spacer_item_left = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # Create a dummy widget to hold the spacer item
        spacer_widget_left = QWidget()
        spacer_layout = QVBoxLayout(spacer_widget_left)
        spacer_layout.addItem(spacer_item_left)
        spacer_layout.addStretch()  # Add stretch to occupy remaining space
        
        # Add the spacer widget to the splitter
        self.splitter.addWidget(spacer_widget_left)
        

        # Set the central widget to the scroll area
        layout.addWidget(self.scroll_area)

        # Create menu bar actions
        #self.create_menu()

        # Show the main window
        #self.show()
        
    # def create_menu(self):
    #     menu_bar = self.menuBar()
    #     file_menu = menu_bar.addMenu("File")

    #     add_dock_action = QAction("Add Dock", self)
    #     add_dock_action.triggered.connect(self.add_dock)
    #     file_menu.addAction(add_dock_action)

    #     remove_dock_action = QAction("Remove Dock", self)
    #     remove_dock_action.triggered.connect(self.remove_dock)
    #     file_menu.addAction(remove_dock_action)

    def add_dock(self):
        dock_count = len(self.docks) + 1
        dock = MatplotlibDockWidget(f"Dock {dock_count}", self.shared_axis, self)
        self.splitter.addWidget(dock)
        self.docks.append(dock)

    def remove_dock(self):
        if self.docks:
            dock_to_remove = self.docks.pop()
            index = self.splitter.indexOf(dock_to_remove)
            if index != -1:
                dock_to_remove.deleteLater()
                self.splitter.setSizes(self.splitter.sizes())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remove_dock()
        elif event.key() == Qt.Key_D and event.modifiers() == Qt.ControlModifier:
            self.add_dock()
        elif event.key() == Qt.Key_Left:
            self.move_dock("left")
        elif event.key() == Qt.Key_Right:
            self.move_dock("right")
            
    def move_dock(self, direction):
        if direction == "left":
            if self.current_dock == self.middle_dock:
                self.removeDockWidget(self.middle_dock)
                self.addDockWidget(Qt.LeftDockWidgetArea, self.middle_dock)
                self.current_dock = self.left_dock
            elif self.current_dock == self.right_dock:
                self.removeDockWidget(self.right_dock)
                self.addDockWidget(Qt.RightDockWidgetArea, self.middle_dock)
                self.current_dock = self.middle_dock
        elif direction == "right":
            if self.current_dock == self.middle_dock:
                self.removeDockWidget(self.middle_dock)
                self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)
                self.current_dock = self.right_dock
            elif self.current_dock == self.left_dock:
                self.removeDockWidget(self.left_dock)
                self.addDockWidget(Qt.LeftDockWidgetArea, self.middle_dock)
                self.current_dock = self.middle_dock
            
    def select_dock(self, dock_widget):
        # Reset the frame color of all docks
        print('selected dock is: ',dock_widget.windowTitle())
        for dock in self.docks:
            pass
            frame_widget = dock.parent()  # Get the parent frame
            #frame_widget.setStyleSheet("QFrame { border: 4px solid red; }")  # Change frame color
        for d in self.docks:
            print(d.windowTitle())
            frame_widget = d.widget()
            if isinstance(frame_widget, QFrame):
                print("The object is a QFrame.")
                frame_widget.setStyleSheet("""
                    QFrame {
                        background-color: lightblue;  /* Background color */
                        border: 2px solid blue;        /* Border color and width */
                    }
                """)
        #Set the frame color of the selected dock to red
        dock_widget.widget().setStyleSheet("QFrame { border: 4px solid red; }")  # Change frame color
        
    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        # Create actions for the context menu
        action1 = QAction("Action 1", self)
        action2 = QAction("Action 2", self)
        action3 = QAction("Action 3", self)

        # Connect actions to slots
        action1.triggered.connect(self.action1_triggered)
        action2.triggered.connect(self.action2_triggered)
        action3.triggered.connect(self.action3_triggered)

        # Add actions to the menu
        context_menu.addAction(action1)
        context_menu.addAction(action2)
        context_menu.addAction(action3)

        # Show the context menu at the cursor position
        context_menu.exec_(event.globalPos())
    
    def show_context_menu(self, event):
        context_menu = QMenu(self)

        change_color_action = context_menu.addAction("Change Color")
        remove_curve_action = context_menu.addAction("Remove Curve")
        add_curve_action = context_menu.addAction("Add Curve")
        save_plot_action = context_menu.addAction("Save Plot Settings")
        load_plot_action = context_menu.addAction("Load Plot Settings")

        properties_menu = context_menu.addMenu("Properties")
        properties_menu.addAction("Edit Curve Properties", self.edit_curve_properties)

        global_pos = self.mapToGlobal(QPoint(event.x, event.y))  # Corrected line
        action = context_menu.exec_(global_pos)

        if action == change_color_action:
            self.change_color()
        elif action == remove_curve_action:
            self.remove_curve()
        elif action == add_curve_action:
            self.add_curve_to_subplot()
        elif action == save_plot_action:
            self.save_plot_settings()
        elif action == load_plot_action:
            self.load_plot_settings()
    
    def action1_triggered(self):
        print("Action 1 selected!")
        self.print_widget_locations()

    def action2_triggered(self):
        print("Action 2 selected!")

    def action3_triggered(self):
        print("Action 3 selected!")
        
    def print_widget_locations(self):
        # Iterate through widgets in the splitter
        for i in range(self.splitter.count()):
            widget = self.splitter.widget(i)
            geometry = widget.geometry()
            print(f"Widget {i + 1}: Position ({geometry.x()}, {geometry.y()}), Size ({geometry.width()} x {geometry.height()})")
