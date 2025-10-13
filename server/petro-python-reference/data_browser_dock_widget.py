from PyQt5.QtWidgets import (QDockWidget, QTreeView, QTabWidget, QVBoxLayout, 
                            QWidget, QHBoxLayout, QLabel, QSplitter, QTableWidgetItem)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon
from PyQt5.QtCore import Qt, QModelIndex
from logs_widget import *
from logvalues_widget import *
from constants_widget import *
import pandas as pd
from typing import List, Dict, Optional

class DataBrowserDockWidget(QDockWidget):
    """
    A dock widget for browsing and displaying well data including logs, log values, and constants.
    
    Features:
    - Tree view for dataset navigation
    - Tabbed interface for different data views
    - Performance optimizations for large datasets
    - Improved error handling
    - Cleaner, more modular code structure
    """
    
    # Color mapping for different dataset types
    DATASET_COLORS = {
        'Special': QColor(255, 223, 186),    # Light orange
        'Point': QColor(186, 255, 186),      # Light green
        'Continuous': QColor(186, 186, 255), # Light blue
    }
    
    def __init__(self, title: str, mainwindow: QWidget):
        """Initialize the data browser widget."""
        super().__init__(title, None)
        self.mainwindow = mainwindow
        
        # Initialize UI components
        self._init_ui()
        
        # Initialize data widgets
        self._init_data_widgets()
        
        # Set up initial size
        self.resize(600, 400)
        
    def _init_ui(self) -> None:
        """Initialize the user interface components."""
        # Create main splitter for left (tree) and right (tabs) panels
        self.splitter = QSplitter()
        
        # Initialize left panel with tree view
        self._init_left_panel()
        
        # Initialize right panel with tabs
        self._init_right_panel()
        
        # Set up main layout
        container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.splitter)
        container.setLayout(main_layout)
        self.setWidget(container)
        
    def _init_left_panel(self) -> None:
        """Initialize the left panel containing the tree view."""
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Well label and tree view
        self.well_label = QLabel("No well selected")
        self.tree_view = self._create_tree_view()
        
        left_layout.addWidget(self.well_label)
        left_layout.addWidget(self.tree_view)
        left_widget.setLayout(left_layout)
        
        self.splitter.addWidget(left_widget)
        
    def _init_right_panel(self) -> None:
        """Initialize the right panel containing the tab widget."""
        self.tab_widget = QTabWidget(self)
        self.splitter.addWidget(self.tab_widget)
        
    def _init_data_widgets(self) -> None:
        """Initialize the data display widgets."""
        self.logstab = LogsWidget()
        self.logvaluestab = LogValuesWidget()
        self.constantstab = ConstantsWidget()
        
        self.add_tab('Logs', self.logstab)
        self.add_tab('Log Values', self.logvaluestab)
        self.add_tab('Constants', self.constantstab)
        
    def _create_tree_view(self) -> QTreeView:
        """Create and configure the tree view for dataset navigation."""
        tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Items'])
        
        tree_view.setModel(self.model)
        tree_view.setHeaderHidden(True)
        tree_view.setUniformRowHeights(True)
        tree_view.setIndentation(0)
        
        return tree_view
        
    def add_tab(self, tab_name: str, content_widget: QWidget) -> None:
        """Add a new tab with the specified name and content widget."""
        self.tab_widget.addTab(content_widget, tab_name)
        
    def update_treeview(self, well):
        try:
            if not well or not well.datasets:
                self.well_label.setText("No data available")
                self.clear_tree_view()
                return
                
            self.well_label.setText(well.well_name)
            self.clear_tree_view()
            self.create_tree_structure(well.datasets)
            
            # Safely handle signal disconnection
            try:
                self.tree_view.clicked.disconnect()
            except TypeError:
                pass  # No connections to disconnect
                
            # Connect the click handler
            self.tree_view.clicked.connect(
                lambda index: self.on_databrowser_dataset_clicked(index, "Dataset"))
                
        except Exception as e:
            self.mainwindow.feedback_manager.update_feedback(
                f"Error updating tree view: {str(e)}")
            print(f"Error updating tree view: {str(e)}")
            
    def create_tree_structure(self, datasets: List['Dataset']) -> None:
        """
        Create a hierarchical tree structure from the datasets.
        
        Args:
            datasets: List of dataset objects to display in the tree
        """
        try:
            # Group datasets by type
            type_dict = self._group_datasets_by_type(datasets)
            
            # Create tree items for each type
            for item_type, items in type_dict.items():
                type_item = self._create_type_item(item_type)
                
                # Add child items for each dataset
                for item in items:
                    self._add_dataset_item(type_item, item)
                    
                # Expand the type item
                self.tree_view.setExpanded(self.model.indexFromItem(type_item), True)
                
        except Exception as e:
            self.mainwindow.feedback_manager.update_feedback(
                f"Error creating tree structure: {str(e)}")
            print(f"Error creating tree structure: {str(e)}")
            
    def _group_datasets_by_type(self, datasets: List['Dataset']) -> Dict[str, List['Dataset']]:
        """Group datasets by their type."""
        type_dict = {}
        for dataset in datasets:
            if not hasattr(dataset, 'type'):
                continue
            if dataset.type not in type_dict:
                type_dict[dataset.type] = []
            type_dict[dataset.type].append(dataset)
        return type_dict
        
    def _create_type_item(self, item_type: str) -> QStandardItem:
        """Create a tree item for a dataset type."""
        type_item = QStandardItem(item_type)
        type_item.setBackground(self.DATASET_COLORS.get(item_type, QColor(255, 255, 255)))
        type_item.setEditable(False)
        type_item.setIcon(QIcon("images/down.png"))  # Closed icon
        type_item.setData(QIcon("images/right-arrow.png"), Qt.UserRole + 1)  # Open icon
        self.model.appendRow(type_item)
        return type_item
        
    def _add_dataset_item(self, parent_item: QStandardItem, dataset: 'Dataset') -> None:
        """Add a dataset item to the tree."""
        if not hasattr(dataset, 'name') or not hasattr(dataset, 'wellname'):
            return
            
        item_node = QStandardItem(dataset.name)
        item_node.setEditable(False)
        item_node.setData({
            "type": "wellname",
            "metadata": dataset.wellname,
            "dataset": dataset  # Store the actual dataset object
        })
        parent_item.appendRow(item_node)
        
    def clear_tree_view(self) -> None:
        """Clear all items from the tree view."""
        self.model.clear()
        
    def on_databrowser_dataset_clicked(self, index: QModelIndex, object_type: str) -> None:
        """
        Handle clicks on dataset items in the tree view.
        
        Args:
            index: The index of the clicked item
            object_type: The type of object clicked
        """
        try:
            if not index.isValid():
                return
                
            item = self.model.itemFromIndex(index)
            if not item:
                return
                
            if item.hasChildren():
                print(f"Category clicked: {item.text()}")
                return
                
            # Handle dataset click
            self._handle_dataset_click(item)
                
        except Exception as e:
            self.mainwindow.feedback_manager.update_feedback(
                f"Error handling dataset click: {str(e)}")
            print(f"Error handling dataset click: {str(e)}")
            
    def _handle_dataset_click(self, item: QStandardItem) -> None:
        """Handle the click on a dataset item."""
        metadata = item.data()
        if not metadata or "type" not in metadata:
            return
            
        if metadata["type"] == "wellname":
            well_name = metadata.get("metadata", "")
            dataset_name = item.text()
            
            self.mainwindow.feedback_manager.update_feedback(
                f"Selected Dataset: {dataset_name}")
                
            self.mainwindow.current_dataset = dataset_name
            self._populate_data_tabs(well_name, dataset_name)
            
    def _populate_data_tabs(self, well_name: str, dataset_name: str) -> None:
        """
        Populate all data tabs with information from the selected dataset.
        
        Args:
            well_name: Name of the selected well
            dataset_name: Name of the selected dataset
        """
        try:
            # Find the selected well and dataset
            selected_well = next(
                (well for well in self.mainwindow.selected_wells 
                 if well.well_name == well_name), None)
                 
            if not selected_well:
                return
                
            selected_dataset = next(
                (dataset for dataset in selected_well.datasets 
                 if dataset.name == dataset_name), None)
                 
            if not selected_dataset:
                return
                
            # Populate each tab
            self._populate_log_table(selected_dataset.well_logs)
            self._populate_log_values_table(selected_dataset.well_logs)
            self._populate_constants_table(selected_dataset.constants)
            
        except Exception as e:
            self.mainwindow.feedback_manager.update_feedback(
                f"Error populating data tabs: {str(e)}")
            print(f"Error populating data tabs: {str(e)}")
            
    def _populate_log_table(self, well_logs: List['WellLog']) -> None:
        """
        Populate the logs table with well log data.
        
        Args:
            well_logs: List of WellLog objects to display
        """
        try:
            table = self.logstab.get_logs_table()
            table.setRowCount(len(well_logs))
            table.setColumnWidth(0, 10)  # Checkbox column width
            
            for row, log in enumerate(well_logs):
                # Add checkbox
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                checkbox_item.setText("")
                checkbox_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 0, checkbox_item)
                
                # Add log data
                table.setItem(row, 1, QTableWidgetItem(log.name))
                table.setItem(row, 2, QTableWidgetItem(log.date))
                table.setItem(row, 3, QTableWidgetItem(log.description))
                table.setItem(row, 4, QTableWidgetItem(log.dtst))
                table.setItem(row, 5, QTableWidgetItem(log.interpolation))
                table.setItem(row, 6, QTableWidgetItem(log.log_type))
                
        except Exception as e:
            self.mainwindow.feedback_manager.update_feedback(
                f"Error populating log table: {str(e)}")
            print(f"Error populating log table: {str(e)}")
            
    def _populate_log_values_table(self, well_logs: List['WellLog']) -> None:
        """
        Populate the log values table with well log data.
        
        Args:
            well_logs: List of WellLog objects to display
        """
        try:
            if not well_logs:
                return
                
            table = self.logvaluestab.get_logvalues_table()
            num_logs = len(well_logs)
            num_readings = len(well_logs[0].log) if well_logs else 0
            
            table.setRowCount(num_readings)
            table.setColumnCount(num_logs)
            table.setHorizontalHeaderLabels([log.name for log in well_logs])
            
            # Fill the table with readings
            for col_index, log in enumerate(well_logs):
                for row_index, log_value in enumerate(log.log):
                    table.setItem(row_index, col_index, 
                                QTableWidgetItem(str(log_value)))
                                
        except Exception as e:
            self.mainwindow.feedback_manager.update_feedback(
                f"Error populating log values table: {str(e)}")
            print(f"Error populating log values table: {str(e)}")
            
    def _populate_constants_table(self, constants: 'Constants') -> None:
        """
        Populate the constants table with well constants.
        
        Args:
            constants: Constants object containing well constants
        """
        try:
            if not constants:
                return
                
            table_view = self.constantstab.table_view
            dataframe = self._convert_constants_to_dataframe(constants)
            self.constants_model = ConstantsTableModel(dataframe)
            table_view.setModel(self.constants_model)
            
        except Exception as e:
            self.mainwindow.feedback_manager.update_feedback(
                f"Error populating constants table: {str(e)}")
            print(f"Error populating constants table: {str(e)}")
            
    def _convert_constants_to_dataframe(self, constants: 'Constants') -> pd.DataFrame:
        """Convert Constants object to pandas DataFrame."""
        return item_data_list_to_dataframe(constants)