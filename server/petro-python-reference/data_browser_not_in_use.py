from PyQt5.QtWidgets import QDockWidget, QTreeView, QTabWidget, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSplitter
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon
from PyQt5.QtCore import Qt, QModelIndex
from logs_widget import *
from logvalues_widget import *
from constants_widget import *
import pandas as pd

class DataBrowserDockWidget(QDockWidget):
    def __init__(self, title, mainwindow, parent=None):
        super().__init__(title,  parent)
        self.mainwindow = mainwindow
        self.logstab = LogsWidget()
        self.logvaluestab = LogValuesWidget()
        self.constantstab = ConstantsWidget()
        # Set up the main widget
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)

        # Create a horizontal layout
        layout = QHBoxLayout(self.main_widget)

        # Create a vertical splitter
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)

        
        
        # Initialize the tree model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Items'])
        
       
        # Set up the QTreeView
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setHeaderHidden(True)  # Hide the header for a list-like appearance
        self.tree_view.setUniformRowHeights(True)  # Makes all rows have the same height
        self.tree_view.setIndentation(0)  # Set indentation to 0
        
        self.label = QLabel()
        self.label.text='Well Name'
        
        self.splitter.addWidget( self.label)
        self.splitter.addWidget( self.tree_view)
        # Create a tab widget
        self.tab_widget = QTabWidget(self)
        self.splitter.addWidget(self.tab_widget)
        
        self.add_tab('Logs', self.logstab)
        self.add_tab('LogValues', self.logvaluestab)
        self.add_tab('Constants', self.constantstab)
        
    def create_tree_structure(self,datasets):
        # Create tree structure without indentation for child items
        type_dict = {}
        for dtst in datasets:
            dtst_type = dtst.type
            if dtst_type not in type_dict:
                type_dict[dtst_type] = []
            type_dict[dtst_type].append(dtst)

        # Create tree structure with colors and icons
        colors = {
            'Special': QColor(255, 223, 186),     # Light orange for fruit
            'Point': QColor(186, 255, 186),  # Light green for vegetables
            'Continuous': QColor(186, 186, 255),      # Light blue for dairy
        }

        # Icons for open and closed states
        icon_open = QIcon("images/right-arrow.png")  # Path to the expanded icon
        icon_closed = QIcon("images/down.png")  # Path to the closed icon

        for item_type, items in type_dict.items():
            type_item = QStandardItem(item_type)  # Create a parent node for the type
            type_item.setBackground(colors.get(item_type, QColor(255, 255, 255)))  # Set background color
            type_item.setEditable(False)  # Prevent editing of type names
            type_item.setIcon(icon_closed)  # Set the closed icon
            self.model.appendRow(type_item)  # Add type node to the model

            for item in items:
                item_node = QStandardItem(item.name)  # Create a child node for the food item
                item_node.setEditable(False)  # Prevent editing of item names
                print(item.wellname)
                item_node.setData({"type": "wellname", "metadata": item.wellname})  # Set metadata for items
                type_item.appendRow(item_node)  # Add item under the type
            # Expand the type item after adding child items
            self.tree_view.setExpanded(self.model.indexFromItem(type_item), True)
            
            # Set the icon for the type item to change when expanded
            type_item.setData(icon_open, Qt.UserRole + 1)  # Store the open icon for the expanded state
    
    
    def add_tab(self, tab_name, content_widget):
        """Add a new tab with a specified name and content widget."""
        self.tab_widget.addTab(content_widget, tab_name)
        
    def on_tree_item_clicked(self, index):
        """Handle item click event in the tree view."""
        item = self.model.itemFromIndex(index)
        if item:
            print(f"Clicked on dataset: {item.text()}")
            # You can perform additional actions here, such as updating the tab widget or sending data to another component
            
            log = self.mainwindow.wells
        
            
    def update_treeview(self, well):
        datasets = well.datasets
        print('Number of datasets', len(datasets))  # Print the number of datasets for debugging

        """Populate the tree view with dataset objects."""
        self.clear_tree_view()
         # Populate the tree structure
        self.create_tree_structure(datasets)
        
        # Connect the item clicked signal to the handler with relevant context
        self.tree_view.clicked.connect(lambda item: self.on_databrowser_dataset_clicked(item, "Dataset"))
        
    def clear_tree_view(self):
        # Clear all items from the model
        self.model.clear()
    def on_databrowser_dataset_clicked(self, index:QModelIndex, object_type):
        print('Dataset Browser treeview is clicked')
        if not index.isValid():
            return
        item = self.model.itemFromIndex(index)
        if item.hasChildren():
            print(f"Category clicked: {item.text()}")
        else:
            print(f"Dataset clicked: {item.text()}")
            if index.isValid():
                well_name=''
                metadata =item.data()
                if metadata:
                    if metadata["type"] == "category":
                        print(f"Category clicked: {item.text()}")
                    elif metadata["type"] == "wellname":
                        well_name=metadata["metadata"]
                        #print(f"Item clicked: {food_item.name} (Type: {food_item.type})")
                        
                print("Well:", well_name)
                print('Dataset:',item.text())
                self.mainwindow.feedback_manager.update_feedback(f"Selected Dataset: {item}")
                dataset_name = self.mainwindow.current_dataset=item.text()
                print('Selected dataset:', dataset_name)
                self.populateLogsTable(well_name, item.text())
                
    def populateLogsTable(self, wellname, datasetname):
        
        wells = [well for well in self.mainwindow.selected_wells if well.well_name==wellname]
        if wells:
            selected_well = wells[0]
            print('Well is', selected_well.well_name)
            datasets = [dataset for dataset in selected_well.datasets if dataset.name==datasetname]
            selected_dataset =datasets[0]
            
            print('Dataset is', selected_dataset.name)
            
            welllogs = selected_dataset.well_logs
            constants = selected_dataset.constants
            #print(welllogs[3])
            print('Log Count:' , len(welllogs))
            
            # Populate the table with WellLog data
            #table = LogsWidget.get_logs_table()
            self.populate_logtable(welllogs)
            self.populate_logvaluestable(welllogs)
            self.populate_constantstable(constants)
        
    def populate_logtable(self,well_logs):
        """Populate the table with WellLog data."""
        table=self.logstab.get_logs_table()
        #print(well_logs[0])

        table.setRowCount(len(well_logs))  # Set the number of rows
        # Set width of the checkbox column
        table.setColumnWidth(0, 10)  # Set width of the checkbox column (e.g., 100 pixels)
        for row, log in enumerate(well_logs):
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)  # Make it checkable and enabled
            checkbox_item.setCheckState(Qt.Unchecked)  # Default to unchecked
            checkbox_item.setText("")  # Ensure no text is set
            checkbox_item.setTextAlignment(Qt.AlignCenter)  # Center the checkbox
            table.setItem(row, 0, checkbox_item)
            
            table.setItem(row, 1, QTableWidgetItem(log.name))
            table.setItem(row, 2, QTableWidgetItem(log.date))
            table.setItem(row, 3, QTableWidgetItem(log.description))
            table.setItem(row, 4, QTableWidgetItem(log.dtst))
    
    def populate_logvaluestable(self,welllogs):
        """Populate the table with WellLog data."""
        # Extracting a list of names from the objects
        log_names = [log.name for log in welllogs]

         # Set the number of columns and rows
        table=self.logvaluestab.get_logvalues_table()
        table.setColumnCount(len(log_names))
        print(len(log_names))
        
        # Set the number of columns and rows
        num_logs = len(welllogs)
        if num_logs == 0:
            return  # No logs to display

        num_readings = len(welllogs[0].log)
        table.setRowCount(num_readings)
        table.setColumnCount(num_logs)
        
        print(num_logs)

        # Set the header labels
        table.setHorizontalHeaderLabels([log.name for log in welllogs])

        # Fill the table with readings
        for col_index, x in enumerate(welllogs):
            for row_index, log_value in enumerate(welllogs[col_index].log):
                table.setItem(row_index, col_index, QTableWidgetItem(str(log_value)))
                
    def populate_constantstable(self,constants):
        """Populate the table with WellLog data."""
        table=self.constantstab.get_constants_table()
        print('number', len(constants))

        table.setRowCount(len(constants))  # Set the number of rows
        # Set width of the checkbox column
        table.setColumnWidth(0, 10)  # Set width of the checkbox column (e.g., 100 pixels)
        for row, const in enumerate(constants):
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)  # Make it checkable and enabled
            checkbox_item.setCheckState(Qt.Unchecked)  # Default to unchecked
            checkbox_item.setText("")  # Ensure no text is set
            checkbox_item.setTextAlignment(Qt.AlignCenter)  # Center the checkbox
            table.setItem(row, 0, checkbox_item)
            
            print('Const name', const.value)
            table.setItem(row, 1, QTableWidgetItem(const.name))
            table.setItem(row, 2, QTableWidgetItem(str(const.value)))
            table.setItem(row, 3, QTableWidgetItem(const.tag))

                    
            
            