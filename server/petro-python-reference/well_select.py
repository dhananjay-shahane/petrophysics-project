import sys
import json
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QDialog
)
from PyQt5.QtCore import QSettings, Qt

class Well_Selection_Widget(QWidget):
    def __init__(self,main_window):
        super().__init__()
        self.main_window = main_window  # Store reference to main window

        # Create QSettings object
        self.settings = QSettings('Petrocene','PetroceneApp')

        # Create list widgets
        self.list1 = QListWidget()
        self.list2 = QListWidget()

        # Populate the first list with example items
        #self.list1.addItems(["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"])
        self.selected_well_names = self.selected_items_from_setting()
        self.all_well_names = [w.well_name for w in main_window.wells]
        self.well_names_not_selected = [item for item in self.all_well_names if item not in self.selected_well_names]
        print('All wells in the project', self.all_well_names)
        print('Selected wells', self.selected_well_names)
        
        self.populate_list1(self.well_names_not_selected)
        self.populate_list2(self.selected_well_names)
        # Create buttons for transferring items
        self.add_button = QPushButton(" >> ")
        self.remove_button = QPushButton(" << ")
        self.add_all_button = QPushButton(" >> All ")
        self.remove_all_button = QPushButton(" << All ")
        self.save_button = QPushButton("Save Selected")
        self.load_button = QPushButton("Load Selected")
        
        # Create OK and Cancel buttons
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        # Connect buttons to their respective methods
        self.add_button.clicked.connect(self.add_item)
        self.remove_button.clicked.connect(self.remove_item)
        self.add_all_button.clicked.connect(self.add_all_items)
        self.remove_all_button.clicked.connect(self.remove_all_items)
        self.save_button.clicked.connect(self.save_selected_items)
        self.load_button.clicked.connect(self.populate_selected_items)
        
        # Connect OK and Cancel buttons
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)

        # Set up layouts
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.add_all_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.remove_all_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        
        # Add OK and Cancel buttons
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(QLabel("Available Items"))
        main_layout.addWidget(self.list1)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel("Selected Items"))
        main_layout.addWidget(self.list2)

        self.setLayout(main_layout)

    def populate_list1(self, well_names):
        """Populate list1 with the given items."""
        self.list1.clear()  # Clear existing items
        self.list1.addItems(well_names)  # Add new items   
        
    def populate_list2(self,well_names):
        """Populate list1 with the given items."""
        self.list2.clear()  # Clear existing items
        self.list2.addItems(well_names)  # Add new items    
    
    def add_item(self):
        # Move selected item from list1 to list2, avoid duplicates
        selected_items = self.list1.selectedItems()
        for item in selected_items:
            if not self.list2.findItems(item.text(), Qt.MatchExactly):
                self.list2.addItem(item.text())
                self.list1.takeItem(self.list1.row(item))

    def remove_item(self):
        # Move selected item from list2 to list1, avoid duplicates
        selected_items = self.list2.selectedItems()
        for item in selected_items:
            if not self.list1.findItems(item.text(), Qt.MatchExactly):
                self.list1.addItem(item.text())
                self.list2.takeItem(self.list2.row(item))

    def add_all_items(self):
        # Move all items from list1 to list2, avoid duplicates
        for index in range(self.list1.count()):
            item = self.list1.item(index)
            if not self.list2.findItems(item.text(), Qt.MatchExactly):
                self.list2.addItem(item.text())
        self.list1.clear()  # Clear list1 after moving all items

    def remove_all_items(self):
        # Move all items from list2 to list1, avoid duplicates
        for index in range(self.list2.count()):
            item = self.list2.item(index)
            if not self.list1.findItems(item.text(), Qt.MatchExactly):
                self.list1.addItem(item.text())
        self.list2.clear()  # Clear list2 after moving all items

    def save_selected_items(self):
        # Save selected items from list2 to settings
        selected_items = [self.list2.item(i).text() for i in range(self.list2.count())]
        self.settings.setValue('selected_wells', json.dumps(selected_items))
        print("Selected items saved!",selected_items)
        
        
    def ok_clicked(self):
        """Send selected items to the main window."""
        self.save_selected_items()
        self.main_window.Load_Selected_Wells()
        self.parent().accept()  # Close the dialog

    def cancel_clicked(self):
        """Close the dialog without making changes."""
        self.parent().reject()  # Close the dialog    

    def populate_selected_items(self,selected_items):
        self.list2.clear()  # Clear current items in list2
        if selected_items:
            for item in selected_items:
                if not self.list2.findItems(item, Qt.MatchExactly):
                    self.list2.addItem(item)  # Avoid duplicates when loading
                
    def selected_items_from_setting(self):
        # Load selected items from settings
        selected_items = json.loads(self.settings.value('selected_wells', '[]'))
        return selected_items
    
class ListTransferDialog(QDialog):
    def __init__(self,main_window):
        super().__init__()
        self.setWindowTitle("List Transfer")
        self.setModal(True)  # Set as modal
        self.resize(400, 300)

        self.transfer_widget = Well_Selection_Widget(main_window)
        layout = QVBoxLayout()
        layout.addWidget(self.transfer_widget)
        self.setLayout(layout)

