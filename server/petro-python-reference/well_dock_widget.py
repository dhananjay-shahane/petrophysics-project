from PyQt5.QtWidgets import QDockWidget, QListWidget, QTabWidget, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QSplitter
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import Qt

class WellsDockWidget(QDockWidget):
    def __init__(self, title, mainwindow):
        super().__init__("Wells", None)
        self.main_window = mainwindow
        layout = QVBoxLayout()
        layout.setContentsMargins(3, 0, 0, 0)  # (left, top, right, bottom)
        self.well_list_widget = QListWidget()
        # Connect the itemClicked signal to a custom slot
        #self.well_list_widget.itemClicked.connect(self.on_well_clicked)
        layout.addWidget(self.well_list_widget)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        container = QWidget()
        container.setLayout(layout)
        self.setWidget(container)  # Set the container widget
        self.wells=self.main_window.wells
        self.update_wells_list()
        
    def setAllowedAreas(self, areas):
        # Allow docking only to the left and right
        allowed_areas = Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
        super().setAllowedAreas(allowed_areas)
        
    def update_wells_list(self):
       
        for well in self.main_window.wells:
            self.well_list_widget.addItem(str(well.well_name))

        self.well_list_widget.itemClicked.connect(lambda item: self.on_well_clicked(item, object_list=self.wells))
        #return self.well_list_widget
        
    def on_well_clicked(self, item, object_list):
        print('Well list is clicked')
        selected_object = next((obj for obj in object_list if obj.well_name == item.text()), None)
        if selected_object:
            self.main_window.feedback_manager.update_feedback(f"Selected Well: {selected_object.well_name}") 
            
            # Update Dataset list box
            print('before update called',selected_object.well_name )
            self.main_window.update_datasetbrowser(selected_object)
            self.main_window.current_well=selected_object.well_name
            self.main_window.settings.setValue('current_well', self.main_window.current_well)