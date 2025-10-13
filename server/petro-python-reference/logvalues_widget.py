from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QSizePolicy
)
import sys

class LogValuesWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # (left, top, right, bottom)

        # Create a layout for the buttons
        button_layout = QHBoxLayout()

        # Create buttons with minimal space
        self.button1 = QPushButton("Button 1")
        self.button2 = QPushButton("Button 2")
        self.button3 = QPushButton("Button 3")

        # Connect buttons to methods
        self.button1.clicked.connect(self.on_button1_clicked)
        self.button2.clicked.connect(self.on_button2_clicked)
        self.button3.clicked.connect(self.on_button3_clicked)

        # Add buttons to the button layout
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        button_layout.addWidget(self.button3)

        # Add button layout to the main layout
        main_layout.addLayout(button_layout)

        # Create a table
        self.table = QTableWidget()
        self.table.setRowCount(1)  # Set number of rows
        
        # Set custom header height
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { height: 20px; }")
        
        # Add the table to the main layout
        main_layout.addWidget(self.table)

        # Set the layout for this widget
        self.setLayout(main_layout)

        # Set button sizes to minimal
        for button in (self.button1, self.button2, self.button3):
            button.setFixedHeight(30)  # Adjust height as needed
            button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
    def get_logvalues_table(self):
        """Expose the QTextEdit widget."""
        return self.table
    

    # Button click handlers
    def on_button1_clicked(self):
        print("Button 1 clicked")

    def on_button2_clicked(self):
        print("Button 2 clicked")

    def on_button3_clicked(self):
        print("Button 3 clicked")