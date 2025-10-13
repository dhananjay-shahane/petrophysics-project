import sys, os. path
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QListWidget, QPushButton, QComboBox, QListWidgetItem,
    QVBoxLayout, QWidget, QHBoxLayout, QLabel, QFileDialog, QMenu
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt
import pandas as pd

class ZonationDockWidget(QDockWidget):
    def __init__(self, title, mainwindow, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.main_window = mainwindow
        # Set a border around the dock widget
        self.setStyleSheet("""
            QDockWidget {
                border: 2px solid #4CAF50;  /* Change color and thickness as needed */
            }
        """)
        # Create a vertical layout for the main components
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(1, 0, 0, 0)  # (left, top, right, bottom)
        # Create a horizontal layout for the label and button
        browse_zone_file_layout = QHBoxLayout()
        self.label = QLabel("Select Tops:")
        browse_zone_file_layout.addWidget(self.label)
        self.button = QPushButton("...")
        self.button.setFixedSize(80, 30)  # Set a fixed size for the button
        browse_zone_file_layout.addWidget(self.button)

        self.button.clicked.connect(self.load_csv)

        self.combo_box = QComboBox()
        #self.combo_box.addItems(["File 1", "File 2", "File 3"])

        # Create a horizontal layout for ListBox1 and buttons
        list_buttons1_layout = QHBoxLayout()
        list_zone_layout = QHBoxLayout()
        
        self.list_box1 = QListWidget()
        list_zone_layout.addWidget(self.list_box1)

        buttons1_layout = QVBoxLayout()
        buttons1_layout.setContentsMargins(0, 0, 5, 0)

        # Add buttons with icons
        icon_base_path = "path/to/icons/"
        for i in range(1, 6):
            icon_button = QPushButton(QIcon(f"{icon_base_path}icon{i}.png"), "")
            icon_button.setToolTip(f"Button {i}")
            icon_button.setFixedSize(30, 30)
            buttons1_layout.addWidget(icon_button)

        list_buttons1_layout.addLayout(list_zone_layout)
        list_buttons1_layout.addLayout(buttons1_layout)

        # Create a horizontal layout for ListBox2 and buttons
        derivative_zones_layout = QHBoxLayout()
        self.list_box2 = QListWidget()
        self.list_box2.addItems(["View All", "0 to 100m", "Derivative Zone 1"])
        derivative_zones_layout.addWidget(self.list_box2)

        # Add buttons for second layout
        buttons2_layout = QVBoxLayout()
        buttons2_layout.setContentsMargins(0, 0, 5, 0)
        for i in range(1, 5):
            icon_button = QPushButton(QIcon(f"{icon_base_path}icon{i}.png"), "")
            icon_button.setToolTip(f"Button {i}")
            icon_button.setFixedSize(30, 30)
            buttons2_layout.addWidget(icon_button)

        self.menu_button = QPushButton("Save")
        self.menu_button.setFixedSize(30, 30)
        self.menu_button.clicked.connect(self.show_menu)
        buttons2_layout.addWidget(self.menu_button)

        derivative_zones_layout.addLayout(buttons2_layout)

        # Add layouts to the main layout
        main_layout.addLayout(browse_zone_file_layout)
        main_layout.addWidget(self.combo_box)
        main_layout.addLayout(list_buttons1_layout)
        main_layout.addLayout(derivative_zones_layout)

        # Set the layout for the entire widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setWidget(central_widget)

        # Create the menu
        self.menu = QMenu(self)
        self.menu.addAction("Action 1", self.action_one)
        self.menu.addAction("Action 2", self.action_two)
        self.menu.addAction("Action 3", self.action_three)

    def show_menu(self):
        pos = self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft())
        self.menu.exec_(pos)

    def action_one(self):
        print("Action 1 triggered")

    def action_two(self):
        print("Action 2 triggered")

    def action_three(self):
        print("Action 3 triggered")

    def load_csv(self):
        print(self.main_window.project_path)
        project_dir= self.main_window.project_path
        default_folder = os.path.join(project_dir,"ZONES_FOLDER")
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", default_folder, "CSV Files (*.csv);;All Files (*)", options=options)
        
        self.combo_box.addItem(file_name)
        
        if file_name:
            pass
            self.load_items_from_csv(file_name)

    def load_items_from_csv(self, file_name):
        self.list_box1.clear()
        df = pd.read_csv(file_name,delimiter=',',header=0)
        
        unique_zones= df['ZONE'].unique().tolist()
        selected_Well = self.main_window.current_well
        #print(df.loc[df['Well'] == selected_Well, 'Zone'].tolist())
        try:
            for zone in unique_zones:
                list_item = QListWidgetItem(zone)
                
                print('selected well in zones',selected_Well)
                isZone_in_well = zone in df.loc[df['Well'] == selected_Well, 'Zone'].tolist()
                #list_item.setBackground(QColor(255, 0, 0))  # Red background
                if not isZone_in_well:
                    print('In well')
                    list_item.setBackground(QColor('gray'))  # Red background
                self.list_box1.addItem(list_item)
        except Exception as e:
            print(f"Error loading CSV file: {e}")

