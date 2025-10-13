from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QSizePolicy
)
from PyQt5.QtGui import QDrag
from PyQt5.QtCore import QMimeData, Qt
import sys

class LogsTable(QTableWidget):
    def __init__(self):
        super().__init__(5, 2)  # 5 rows, 2 columns
        self.setHorizontalHeaderLabels(['Column 1', 'Column 2', 'Column 3'])
        self.setDragEnabled(True)
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            drag = QDrag(self)
            mimeData = QMimeData()
            mimeData.setText(item.text())
            drag.setMimeData(mimeData)
            drag.exec_(supportedActions)

class LogsWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the main layout
        main_layout = QVBoxLayout()
        # Set layout margins to 0
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
        self.table = LogsTable()
        self.table.setRowCount(1)  # Set number of rows
        self.table.setColumnCount(7)  # Set number of columns
        # Connect the header click event
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_click)
        # Set drag and drop properties
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(False)
        self.table.setDropIndicatorShown(True)
        
        # Rename columns
        self.table.setHorizontalHeaderLabels(["S", "Name", "Date", "Description", "Dataset", "Interpolation", "Type"])
        
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
    def on_header_click(self, logicalIndex):
        # Check if the clicked header is the checkbox column
        if logicalIndex == 0:  # Assuming the checkbox column is the first column (index 0)
            # Determine the current state based on the first checkbox
            first_checkbox = self.table.item(0, 0)
            if first_checkbox.checkState() == Qt.Checked:
                new_state = Qt.Unchecked
            else:
                new_state = Qt.Checked

            # Set all checkboxes to the new state
            for row in range(self.table.rowCount()):
                checkbox_item = self.table.item(row, 0)
                checkbox_item.setCheckState(new_state)
    def get_logs_table(self):
        """Expose the QTextEdit widget."""
        return self.table
    

    # Button click handlers
    def on_button1_clicked(self):
        print("Button 1 clicked")

    def on_button2_clicked(self):
        print("Button 2 clicked")

    def on_button3_clicked(self):
        print("Button 3 clicked")
        
    def mimeData(self, items):
        """Override to provide the data for the drag operation."""
        mime_data = super().mimeData(items)
        return mime_data
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            drag = QDrag(self)
            mimeData = QMimeData()
            mimeData.setText(item.text())
            drag.setMimeData(mimeData)
            drag.exec_(supportedActions)