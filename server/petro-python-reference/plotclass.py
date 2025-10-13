import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QVBoxLayout, QWidget, 
    QSplitter, QAction, QMenuBar, QFrame, QScrollArea, QSizePolicy, QSpacerItem, QMenu
)
from PyQt5.QtCore import Qt, QEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import pandas as pd

class MainFigureWidget(QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.plot()

    def plot(self):
        ax = self.figure.add_subplot(111)
        ax.plot([0,np.min(self.df.DEPTH)], [0,10], label='Main Data')
        ax.set_title("Main Plot")
        ax.set_ylabel("Depth")
        ax.legend()
        self.canvas.draw()


class MatplotlibDockWidget(QDockWidget):
    def __init__(self, title, shared_axis, parent=None):
        super().__init__(title, parent)
        self.shared_axis = shared_axis
        self.setWidget(self.create_frame())
        self.setFixedHeight(2000)
        self.setStyleSheet("QDockWidget { background-color: pink; }")
        # Disable close and maximize buttons
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

        # Set the dock widget to be non-floatable and non-movable
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)  # Allow docking only to left and right
        self.setFloating(False)  # Disable floating

    def create_frame(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setLineWidth(2)
        frame.setStyleSheet("QFrame { border: 2px solid green; }")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(FigureWidget(self.shared_axis, self))  # Pass self as the dock widget
        frame.setLayout(layout)
        # Install an event filter to the frame
        frame.installEventFilter(self)
        return frame
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress and source is self.widget():
            if event.button() == Qt.LeftButton:
                # Change the border color when the dock is clicked
                self.setStyleSheet("QDockWidget { border: 2px solid red; }")
                # Notify the main window of selection
                self.parent().main_window.select_dock(self)
                return True  # Event handled
        return super().eventFilter(source, event)

    def mousePressEvent(self, event):
        print('mouse pressed')
        print(self)
        #self.setStyleSheet("QDockWidget { border: 2px solid red; }")
        if event.button() == Qt.LeftButton:  # Check if left button was clicked
            x, y = event.x(), event.y()
            print(f"Dock clicked at: x={x}, y={y}")
            # Notify main window of selection
            if self.parent() and isinstance(self.parent(), MainWindow):
                self.parent().select_dock(self)  # Notify main window of selection
        super().mousePressEvent(event)  # Call base class method


class FigureWidget(QWidget):
    def __init__(self, shared_axis, dock_widget):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create the figure and canvas
        height_in_inches = 200 / 2.54  # Convert 200 cm to inches
        self.figure = Figure(figsize=(10, height_in_inches))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # Connect mouse click event
        self.canvas.mpl_connect('button_press_event', self.on_click)

        # Example plot
        self.plot(shared_axis, dock_widget)

    def plot(self, shared_axis,dock_widget):
        ax = self.figure.add_subplot(111)
        
        # Adjust subplot parameters to reduce margins
        self.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  # Adjust as needed
        
        ax.plot(shared_axis.get_lines()[0].get_xdata(), shared_axis.get_lines()[0].get_ydata(), label='Dock Data')
        ax.set_title("Dock Plot")
        ax.set_ylabel("Common Y-Axis")
        ax.legend()
        # Move x-axis ticks and labels to the top
        ax.xaxis.set_ticks_position('top')  # Show ticks at the top
        ax.xaxis.tick_top()  # Move tick labels to the top
        
        self.canvas.draw()
        
        # Store the reference to the dock widget
        self.dock_widget = dock_widget

    def on_click(self, event):
        # Check if the click is within the axes
        #if event.inaxes:
        x, y = event.xdata, event.ydata
        print(f"Clicked at: x={x}, y={y} in dock '{self.dock_widget.windowTitle()}'")
        
         # Change the frame's border color
        frame_widget = self.parent()  # Get the parent frame
        #frame_widget.setStyleSheet("QFrame { border: 4px solid red; }")  # Change frame color
        print('notify')
        main_w = self.dock_widget.parent().parent().parent().parent()
        scr=self.dock_widget.parent().parent().parent()
        frm=self.dock_widget.parent().parent()
        print(frm)
        # Notify main window of selection
        if self.dock_widget.parent().parent().parent().parent() and isinstance(self.dock_widget.parent().parent().parent().parent(), MainWindow):
            print('notify')
            main_w.select_dock(self.dock_widget)  # Notify main window of selection
                
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print('mouse pressed')
            # Get the parent dock widget
            dock_widget = self.parent()  # Navigate up to the dock widget
            # Change the border color of the dock widget
            #dock_widget.setStyleSheet("QDockWidget { border: 2px solid red; }")
            # Notify the main window of selection
            self.parent().parent().main_window.select_dock(dock_widget)  # Update this line based on your main window reference


class MainWindow(QMainWindow):
    def __init__(self, current_well, current_dataset):
        super().__init__()

        self.setWindowTitle("Matplotlib with Dynamic Dock Widgets and Shared Y-Axis")
        self.setGeometry(100, 100, 800, 600)

        # Create a horizontal splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)
        well=  current_well
        dataset = current_dataset
        log_mnemonics = []
        for log in dataset.well_logs:
            log_mnemonics.append(log.name)
        data = {mnem:{} for mnem in log_mnemonics}

        for well_log in dataset.well_logs:
            mnem = well_log.name
            data[mnem] = well_log.log

        #Make a input curves dataframe 
        df_input = pd.DataFrame(data)
        #print(df_input.head())
        # Create the main figure widget
        well = [well for well in self.main_window.selected_wells if well.well_name == current_well][0]
        print(well.well_name)
        datasets = well.datasets
        self.main_figure_widget = MainFigureWidget(current_well, current_dataset)
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
        self.setCentralWidget(self.scroll_area)

        # Create menu bar actions
        self.create_menu()

        # Show the main window
        self.show()

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        add_dock_action = QAction("Add Dock", self)
        add_dock_action.triggered.connect(self.add_dock)
        file_menu.addAction(add_dock_action)

        remove_dock_action = QAction("Remove Dock", self)
        remove_dock_action.triggered.connect(self.remove_dock)
        file_menu.addAction(remove_dock_action)

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