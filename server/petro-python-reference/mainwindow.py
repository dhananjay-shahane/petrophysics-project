import sys, datetime, os, pathlib
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit,QAction, QListWidget, QWidget, QVBoxLayout,QFileDialog
)
from PyQt5.QtCore import Qt, QSettings, QByteArray
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QTextCursor
from matplotlib_widget import MatplotlibWidget
from custom_dock_widget import CustomDockWidget
from custom_object import CustomObject
from feedback_dock_widget import FeedbackDockWidget
from feedback_manager import *
from fe_data_objects import *
from well_dock_widget import *
from data_browser_dock_widget import *
from feedback_dock_widget import *
from Utility import *
from logplotclass import *
from LogPlot import *
from well_select import *
from tops_dock_widget import *
from geolog_reports_dock_widget import *
from CPI import *
from Style_Themes import *



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.project_path = ""  # Initialize the global variable
        self.dock_count = 1
        self.docks = {}
        self.yobjects_dock_created = False
        self.datasets_dock_created = False
        self.xobjects_items = []
        self.yobjects_items = []
        
        self.wells = []
        self.selected_wells = []

        self.current_well=''
        self.current_dataset=None
        # Initialize settings
        self.settings = QSettings("Petrocene", "PetroceneApp")
        
        # Load previously saved settings
        self.project_path = self.settings.value("project_path", "", type=str)
        self.current_well=self.settings.value("current_well", "", type=str)
        self.setWindowTitle(self.project_path)
        self.wells_Folder = os.path.join(self.project_path, '10-WELLS')
        
        self.init_ui()
        
        # Initialize FeedbackManager with the FeedbackDockWidget
        feedback_dock = self.docks.get("Feedback")
        self.wells_dock = self.docks.get("Wells")
        self.tops_dock = self.docks.get("Tops")
        
        if feedback_dock:
            self.feedback_manager = FeedbackManager(feedback_dock)
        else:
            self.feedback_manager = None  # Handle the case where the dock doesn't exist
        
        # Work after GUI is complete. Loads the well data select a well, update datasets and select a dataset
        self.Load_Wells()
        self.Load_Selected_Wells()
        welldock= self.docks["Wells"]
        listwidget = welldock.well_list_widget
        listwidget.setCurrentRow(0)
        current_item = listwidget.currentItem()
        if current_item:
            selected_well = current_item.text()
            print('selected well', selected_well)
        print('well',len(self.selected_wells))
        well=None
        if current_item:
            well=find_item_by_name(self.selected_wells,selected_well)
            print('Returnd well name', well.well_name)
        if well:
            self.update_datasetbrowser(well)
        dbdock = self.docks["DatasetBrowser"]
        tv = dbdock.tree_view
        item_index = dbdock.model.index(0, 0)
        if item_index:
            tv.setCurrentIndex(item_index)
            tv.expand(item_index)
            dbdock.on_databrowser_dataset_clicked(item_index, "Dataset")

    def init_ui(self):
        self.setCentralWidget(QWidget())
        self.create_wells_dock("Wells")
        self.create_tops_dock("Zonation")
        self.create_data_browser_dock("Data Browser")
        #self.create_log_plot_dock()
        #self.create_datasets_dock()
        #self.create_yobjects_dock()
        self.create_feedback_dock("Feedback")
        #self.create_matplotlib_dock()  # Pass the feedback dock to this method
        self.create_menu_bar()
        # Apply dark theme
        # Apply default theme
        self.set_theme("teal_blue")

        

    # def create_docks(self):
    #     self.create_wells_dock()
    #     self.create_datasets_dock()
    #     self.create_yobjects_dock()
    #     self.create_matplotlib_dock()
    #     self.create_feedback_dock()
    
    def save_layout(self):
        # Save the state to a file
        filename, _ = QFileDialog.getSaveFileName(self, "Save Layout", "", "Layout Files (*.layout)")
        if filename:
            with open(filename, 'wb') as file:
                file.write(self.saveState())

    def load_layout(self):
        # Load the state from a file
        filename, _ = QFileDialog.getOpenFileName(self, "Load Layout", "", "Layout Files (*.layout)")
        if filename:
            with open(filename, 'rb') as file:
                layout_data = QByteArray(file.read())
                self.restoreState(layout_data)
    def set_theme(self, theme):
        """Apply the specified theme."""
        if theme == "dark":
            self.setStyleSheet(ThemeManager.get_dark_theme())
        elif theme == "light":
            self.setStyleSheet(ThemeManager.get_light_theme())
        elif theme == "teal_blue":
            self.setStyleSheet(ThemeManager.get_teal_blue_theme())

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current_style = self.styleSheet()
        if "2C2C2C" in current_style:  # Checking for dark theme
            self.set_theme("light")
        else:
            self.set_theme("dark")
                
    def Load_Wells(self):
        print('Loading wells from previously used project folder')
        # Load previously saved settings
        self.settings = QSettings('Petrocene', 'PetroceneApp')
        self.project_path = self.settings.value("project_path", "", type=str)
        project_path = self.project_path
        print('Project path from setting', self.wells_Folder)
        if self.wells_Folder:
            # List all files in the selected folder
            files = os.listdir(self.wells_Folder)
            # Filter files by extension
            well_files = [f for f in files if f.endswith('ptrc')]    
            for f in well_files:
                filepath = os.path.join(self.wells_Folder,f)
                
                w = Well.deserialize(filepath=filepath)
                self.wells.append(w)
                #print(w.well_name)
        #print(self.wells)
            
    def Load_Selected_Wells(self):
        print('Loading wells from slected wells list from memory after well selection')
        # Load previously saved settings
        self.settings = QSettings('Petrocene', 'PetroceneApp')
        self.project_path = self.settings.value("project_path", "", type=str) 
        project_path = self.project_path
        self.selected_wells=[]
        # Load selected items from settings
        selected_well_names = json.loads(self.settings.value('selected_wells', '[]')) # Need to fix this error after aa well file is deleted
        print('selected well names inside Load', selected_well_names)
        print('Project path from setting', project_path)
        if self.wells_Folder:
            # List all files in the selected folder
            files = os.listdir(self.wells_Folder)
            if selected_well_names:
                for well_name in selected_well_names:
                    well_file_name = well_name + '.ptrc'
                    print('Selected well file', well_file_name)
                    file_path = os.path.join(self.wells_Folder,well_file_name)
                    if os.path.exists(file_path):
                        w = Well.deserialize(filepath=file_path)
                        self.selected_wells.append(w)
                        print(w.well_name)
                    else:
                        pass
                        if well_name in selected_well_names:
                            selected_well_names.remove(well_name)
                            print('After removing', selected_well_names)
                            self.settings.setValue('selected_items', selected_well_names)
                
                self.update_well_list_widget(self.selected_wells)
            
    def generate_datasets(self):  #Not in use
        """Generate datasets at runtime and update the DataBrowser."""
        datasets = [
            Dataset("Dataset A"),
            Dataset("Dataset B"),
            Dataset("Dataset C"),
        ]
        self.data_browser_dock.update_datasets(datasets)
        
    def create_wells_dock(self, title):
        wells_dock = WellsDockWidget(title, self)
        wells_dock.setObjectName(title)
        self.addDockWidget(Qt.LeftDockWidgetArea, wells_dock)
        self.docks["Wells"] = wells_dock
        
    def create_tops_dock(self,title):
        tops_dock = TopsDockWidget(title, self)
        tops_dock.setObjectName(title)
        self.addDockWidget(Qt.LeftDockWidgetArea, tops_dock)
        self.docks["Tops"] = tops_dock
    
    def create_data_browser_dock(self,title):
        data_browser_dock = DataBrowserDockWidget(title, self)
        data_browser_dock.setObjectName(title)
        self.addDockWidget(Qt.RightDockWidgetArea, data_browser_dock)
        self.docks["DatasetBrowser"] = data_browser_dock
        
    def create_log_plot_dock(self):
        log_plot_dock = LogPlotDockWidget("Log Plot", self)
        self.addDockWidget(Qt.TopDockWidgetArea, log_plot_dock)
        self.docks["LogPlot"] = log_plot_dock
        
        
        #log_plot_dock = CustomDockWidget("Log Plot", self)
        log_plot_dock.setFloating(True)
         # Define size of the floating dock widget
        log_plot_dock.resize(900, 600)  # Width, Height
        # Move the dock widget to a specific position
        log_plot_dock.move(2000, 100)  # X, Y coordinates
         # Set minimum size (optional)
        log_plot_dock.setMinimumSize(500, 500)  # Optional: Set minimum size

    def create_datasets_dock(self): # Not in use
        if not self.yobjects_dock_created:
            container = QWidget()
            layout = QVBoxLayout(container)
            dataset_list_box = self.create_datasets_list_box()
            layout.addWidget(dataset_list_box)

            datasets_dock = CustomDockWidget("Datasets", self)
            datasets_dock.setWidget(dataset_list_box)
            self.addDockWidget(Qt.RightDockWidgetArea, datasets_dock)
            self.docks["Datasets"] = datasets_dock
            self.datasets_dock_created = True
            
    def create_xobject_dock(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        list_box = self.create_xobjects_list_box()
        layout.addWidget(list_box)
        xobject_dock = CustomDockWidget("XOBJECTS", self)
        xobject_dock.setWidget(container)
        self.addDockWidget(Qt.LeftDockWidgetArea, xobject_dock)
        self.docks["XOBJECTS"] = xobject_dock
                
    def create_yobjects_dock(self):
        if not self.yobjects_dock_created:
            container = QWidget()
            layout = QVBoxLayout(container)
            list_box = self.create_yobjects_list_box()
            layout.addWidget(list_box)

            yobjects_dock = CustomDockWidget("YOBJECTS", self)
            yobjects_dock.setWidget(container)
            self.addDockWidget(Qt.RightDockWidgetArea, yobjects_dock)
            self.docks["YOBJECTS"] = yobjects_dock
            self.yobjects_dock_created = True
            
    def create_feedback_dock(self,title):
        feedback_dock = FeedbackDockWidget(title, self, self)
        feedback_dock.setObjectName(title)
        feedback_text_edit = feedback_dock.text_edit
        #feedback_dock.setWidget(feedback_text_edit)
        self.addDockWidget(Qt.BottomDockWidgetArea, feedback_dock)
        self.docks["Feedback"] = feedback_dock
        
    def create_matplotlib_dock_NOT_IN_USE(self):
        
        container = QWidget()
        layout = QVBoxLayout(container)

        # Pass the FeedbackDockWidget instance to MatplotlibWidget

        matplotlib_dock = CustomDockWidget("Matplotlib Plot", self)
        matplotlib_dock.setFloating(True)
         # Define size of the floating dock widget
        matplotlib_dock.resize(900, 600)  # Width, Height
        # Move the dock widget to a specific position
        matplotlib_dock.move(2000, 100)  # X, Y coordinates
         # Set minimum size (optional)
        matplotlib_dock.setMinimumSize(500, 500)  # Optional: Set minimum size
        
        
        matplotlib_dock.setWidget(container)
        self.addDockWidget(Qt.TopDockWidgetArea, matplotlib_dock)
        self.docks["Matplotlib Plot"] = matplotlib_dock

    def create_xobjects_list_box(self):
        list_widget = QListWidget()
        self.xobjects_items = [
            CustomObject("Item A", "Description for item A"),
            CustomObject("Item B", "Description for item B"),
            CustomObject("Item C", "Description for item C"),
            CustomObject("Item D", "Description for item D")
        ]
        for item in self.xobjects_items:
            list_widget.addItem(str(item))

        list_widget.itemClicked.connect(lambda item: self.on_item_clicked(item, self.xobjects_items, "XOBJECT"))
        return list_widget
    

    
    def create_datasets_list_box(self):
        dataset_list_widget = QListWidget()
        self.dataset_items = [
        ]
        dataset_list_widget.itemClicked.connect(lambda item: self.on_dataset_clicked(item, self.dataset_items, "Dataset"))
        return dataset_list_widget
    
    def update_well_list_widget(self, wells):
        wells_dock = self.docks.get("Wells")
        well_list_widget = wells_dock.well_list_widget
        well_list_widget.clear()
        for index in range(well_list_widget.count()):
            item = self.well_list_widget.item(index)
            print('these items are:',item.text())

        if wells:
            # Prepare a list of well names
            well_names = [well.well_name for well in wells]
            print('Well names to update',well_names)
            well_list_widget.addItems(well_names)
            well_list_widget.sortItems()
    
    def update_datasets_list_box(self, well):
        datasets_dock = self.docks.get("Datasets")
        
        if not datasets_dock:
            return  # Handle the case where the dock doesn't exist

        dataset_list = datasets_dock.widget()
        datasets = well.datasets

        print(len(datasets))  # Print the number of datasets for debugging

        # Clear the existing items in the list
        dataset_list.clear()

        # Prepare a list of dataset names
        dataset_names = [dataset.name for dataset in datasets]
        
        # Add the new dataset names to the list widget
        dataset_list.addItems(dataset_names)

        # Connect the item clicked signal to the handler with relevant context
        dataset_list.itemClicked.connect(lambda item: self.on_dataset_clicked(item, datasets, "Dataset"))
        
    def update_datasetbrowser(self, well):
        print('DatasetBrowser Clicked')
        datasetbrowser_dock = self.docks.get("DatasetBrowser")
        
        if not datasetbrowser_dock:
            return  # Handle the case where the dock doesn't exist
        datasetbrowser_dock.update_treeview(well)

    def create_yobjects_list_box(self):
        list_widget = QListWidget()
        self.yobjects_items = [
            CustomObject("Another Item 1", "Description for another item 1"),
            CustomObject("Another Item 2", "Description for another item 2"),
            CustomObject("Another Item 3", "Description for another item 3"),
            CustomObject("Another Item 4", "Description for another item 4")
        ]
        for item in self.yobjects_items:
            list_widget.addItem(str(item))

        list_widget.itemClicked.connect(lambda item: self.on_item_clicked(item, self.yobjects_items, "YOBJECT"))
        list_widget.setDragEnabled(True)
        list_widget.itemPressed.connect(self.start_drag)
        return list_widget

    
            
            
    def on_dataset_clicked(self, item, object_list, object_type):
        print('Dataset list is clicked')
        selected_object = next((obj for obj in object_list if obj.name == item.text()), None)
        print(item.text())
        self.current_dataset=selected_object.well_name
        if selected_object:
            self.feedback_manager.update_feedback(f"Selected Dataset: {selected_object.name}")
            
    
    def on_item_clicked(self, item, object_list, object_type):
        selected_object = next((obj for obj in object_list if str(obj) == item.text()), None)
        if selected_object:
            feedback_dock = self.docks.get("Feedback")
            if feedback_dock:
                text_edit = feedback_dock.widget()
                if isinstance(text_edit, QTextEdit):
                    current_text = text_edit.toPlainText()
                    new_text = f"Selected {object_type}: {selected_object.name}\n"
                    text_edit.setPlainText(current_text + new_text)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        project_menu = menu_bar.addMenu("Project")
        file_menu = menu_bar.addMenu("File")
        petrophysics_menu = menu_bar.addMenu("Petrophysics")
       

        # Create an action to browse for a project folder

        project_open_action = QAction("Open Project", self) # project open
        project_save_wells_action = QAction("Save Wells", self) # project save wells
        project_select_wells_action = QAction("Select Wells", self) # project save wells
        
        
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        
        project_menu.addAction(project_open_action) #project open
        project_menu.addAction(project_save_wells_action) #project save wells
        project_menu.addAction(project_select_wells_action) #project select wells
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        

        new_dock_action = QAction("New Dockable Window", self)
        
        project_open_action.triggered.connect(self.project_open)    #project open
        project_save_wells_action.triggered.connect(self.project_save_wells)    #project save wells
        project_select_wells_action.triggered.connect(self.open_list_transfer_dialog)    #project save wells
        
        new_dock_action.triggered.connect(self.create_new_dockable_window)
        file_menu.addAction(new_dock_action)

        remove_central_action = QAction("Remove Central Widget", self)
        remove_central_action.triggered.connect(self.remove_central_widget)
        file_menu.addAction(remove_central_action)
        
        petrophysics_d_model_all_action = QAction("D-Model-All", self) # project save wells
        petrophysics_menu.addAction(petrophysics_d_model_all_action)
        petrophysics_d_model_all_action.triggered.connect(self.calculate_d_model_all)
        
        
        
        geolog_menu = menu_bar.addMenu("Geolog")
        goelog_open_action = QAction("Open Geolog Utilities", self) # project open
        goelog_open_action.triggered.connect(self.geolog_open)
        geolog_menu.addAction(goelog_open_action)
        
        
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
            
        save_action = QAction("Save Layout", self)
        save_action.triggered.connect(self.save_layout)
        dock_menu.addAction(save_action)
        
        load_action = QAction("Load Layout", self)
        load_action.triggered.connect(self.load_layout)
        dock_menu.addAction(load_action)
        
        # Add theme toggle action
        theme_action = QAction("Toggle Theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        dock_menu.addAction(theme_action)
        
        # Add theme selection submenu
        theme_menu = dock_menu.addMenu("Select Theme")
        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        teal_blue_theme_action = QAction("Teal & Blue Theme", self)
        teal_blue_theme_action.triggered.connect(lambda: self.set_theme("teal_blue"))
        theme_menu.addAction(teal_blue_theme_action)

    def project_open(self):
        """Open a dialog to browse for a folder and store the path in a global variable."""
        project_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        print(project_path)
        if project_path:
            self.project_path = project_path  # Store the selected folder path
            self.settings = QSettings('Petrocene','PetroceneApp')
            print(f"Selected folder: {self.project_path}")
            self.settings.setValue('project_path', self.project_path)
            self.feedback_manager.update_feedback(f"project_path: {self.project_path}")
            self.wells_Folder = os.path.join(self.project_path, '10-WELLS')
            # List all files in the selected folder
            files = os.listdir(self.wells_Folder)
            # Filter files by extension
            well_files = [f for f in files if f.endswith('ptrc')]    
            for f in well_files:
                file_path = os.path.join(self.wells_Folder,f)
                print(file_path)
                w = Well.deserialize(filepath=file_path)
                self.wells.append(w)
                print(w.well_name)
            self.update_well_list_widget(self.wells)
            
    def geolog_open(self):
        # Create and show the FileViewer window
        self.fileViewer = FileViewer()
        self.fileViewer.show()
        
    def open_list_transfer_dialog(self):
        dialog = ListTransferDialog(self)
        dialog.exec_()  # Show the dialog as modal
        
    def project_save_wells(self):
        print('Saving wells')
        folder=self.wells_Folder
        for w in self.wells:
            filepath = os.path.join(folder,w.well_name+'.ptrc')
            w.serialize(filename=filepath)
            print('Saved Wells to :', folder)
        
            
    def create_new_dockable_window(self):
        self.dock_count += 1
        new_dock = CustomDockWidget(f"Dockable Window {self.dock_count}", self)
        new_dock.setWidget(QTextEdit())
        self.addDockWidget(Qt.RightDockWidgetArea, new_dock)
        self.docks[f"Dockable Window {self.dock_count}"] = new_dock

    def remove_central_widget(self):
        self.setCentralWidget(QWidget())

    def toggle_dock(self, checked, title):
        dock = self.docks.get(title)
        if dock:
            if checked:
                dock.show()
            else:
                dock.hide()
    
    def start_drag(self, item):
        if item:
            mime_data = QMimeData()
            mime_data.setText(item.text())
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction | Qt.MoveAction)
            
    def calculate_d_model_all(self):
        print('Calculating D Model...')
        calc_dtst = CPI.calculate_d_model_all(self, self)
        if calc_dtst:
            self.feedback_manager.update_feedback('VSHGR computation completed')

    def set_dark_theme(self):
        """Apply a dark theme to the application."""
        dark_style = """
            QMainWindow {
                background-color: #2C2C2C;
                color: #FFFFFF;
            }
            QDockWidget {
                background-color: #3C3F41;
                color: #FFFFFF;
            }
            QSplitter {
                background-color: #3C3F41;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3C3F41;
            }
            QTabWidget {
                background-color: #3C3F41;
                color: #FFFFFF;
            }
            QTabBar::tab {
                background: #3C3F41;
                padding: 10px;
                border: 1px solid #4A4E50;  /* Make the tab border more visible */
            }
            QTabBar::tab:selected {
                background: #4A4E50;
                font-weight: bold;  /* Make selected tab text bold */
            }
            QListWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3C3F41;
            }
            QTableView {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3C3F41;
            }
            QTableView::item {
                background-color: #1E1E1E;
            }
            QTableView::item:selected {
                background-color: #4A4E50;
            }
            QHeaderView {
                background-color: #3C3F41;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #3C3F41;
                color: #FFFFFF;
                padding: 4px;
                border: 1px solid #4A4E50;  /* Border for header sections */
            }
            QTreeView {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3C3F41;
            }
            QLabel {
                color: #FFFFFF;  /* Color for QLabel text */
                background-color: #3C3F41;  /* Optional background for QLabel */
                padding: 5px;  /* Padding around the text */
            }
            QComboBox {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3C3F41;
                padding: 5px;
            }
            QComboBox::drop-down {
                background-color: #3C3F41;
            }
            QPushButton {
                background-color: #3C3F41;
                color: #FFFFFF;
                border: 1px solid #4A4E50;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4A4E50;
            }
            QMenuBar {
                background-color: #3C3F41;
                color: #FFFFFF;
            }
            QMenu {
                background-color: #3C3F41;
                color: #FFFFFF;
            }
            QMenu::item {
                background-color: #3C3F41;
            }
            QMenu::item:selected {
                background-color: #4A4E50;
            }
            QAction {
                color: #FFFFFF;
            }
        """
