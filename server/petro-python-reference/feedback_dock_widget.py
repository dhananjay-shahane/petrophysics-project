from PyQt5.QtWidgets import (
    QMainWindow, QDockWidget, QWidget, QVBoxLayout, QApplication, 
    QPushButton, QHBoxLayout, QTextEdit, QSpacerItem, QSizePolicy, 
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal
import sys
import os
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict
from Data_Import_Export import DataIMPEX
from fe_data_objects import Well, Dataset


class FileDropSignal(QObject):
    """Signal class for file drop events"""
    files_dropped = pyqtSignal(list)


class CustomTextEdit(QTextEdit):
    """Enhanced QTextEdit with robust drag and drop functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.dropped_files = []
        self.file_drop_signal = FileDropSignal()

    def dragEnterEvent(self, event):
        """Handle drag enter event with proper MIME type checking"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Process dropped files with validation"""
        if not event.mimeData().hasUrls():
            return

        self.dropped_files = []
        valid_files = []
        
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if self.parent().is_valid_file(file_path):
                valid_files.append(file_path)
                self.append(f'Loaded: {os.path.basename(file_path)}')
            else:
                self.append(f'[Ignored] {os.path.basename(file_path)} (unsupported format)')

        self.dropped_files = valid_files
        event.acceptProposedAction()
        
        if valid_files:
            self.file_drop_signal.files_dropped.emit(valid_files)


class FeedbackDockWidget(QDockWidget):
    """Enhanced feedback dock widget with file handling capabilities"""
    
    # Class constants
    ALLOWED_EXTENSIONS = ['.txt', '.las', '.csv']
    DEFAULT_BUTTON_WIDTH = 120
    
    def __init__(self, title: str, mainwindow: QMainWindow, parent=None):
        super().__init__(title, parent)
        self.mainwindow = mainwindow
        self.dropped_files = []
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self) -> None:
        """Initialize and configure the UI components"""
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        
        # Main container and layout
        container = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        container.setLayout(self.main_layout)
        self.setWidget(container)
        
        # Button panel
        self._setup_button_panel()
        
        # Text edit area
        self._setup_text_edit()
        
    def _setup_button_panel(self) -> None:
        """Configure the button control panel"""
        self.button_panel = QWidget()
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        
        # Action buttons
        self.clear_btn = self._create_button("Clear", self.clear_text_edit)
        self.load_las_btn = self._create_button("Load LAS", self.load_las_files)
        self.load_csv_btn = self._create_button("Load CSV", self.load_deviation_data)
        
        # Spacer to push buttons left
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        # Add widgets to layout
        self.button_layout.addWidget(self.clear_btn)
        self.button_layout.addWidget(self.load_las_btn)
        self.button_layout.addWidget(self.load_csv_btn)
        self.button_layout.addItem(spacer)
        
        self.button_panel.setLayout(self.button_layout)
        self.main_layout.addWidget(self.button_panel)
        
    def _setup_text_edit(self) -> None:
        """Configure the text display area"""
        self.text_edit = CustomTextEdit(self)
        self.text_edit.setPlaceholderText("Drag and drop files here or use the load buttons...")
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setReadOnly(False)
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.main_layout.addWidget(self.text_edit)
        
    def _create_button(self, text: str, handler) -> QPushButton:
        """Helper to create consistent buttons"""
        btn = QPushButton(text)
        btn.setMaximumWidth(self.DEFAULT_BUTTON_WIDTH)
        btn.clicked.connect(handler)
        return btn
        
    def _connect_signals(self) -> None:
        """Connect all signal-slot connections"""
        self.text_edit.file_drop_signal.files_dropped.connect(self.handle_dropped_files)
        
    def handle_dropped_files(self, files: List[str]) -> None:
        """Process files after being dropped"""
        self.dropped_files = files
        if files:
            self.append_message(f"Successfully loaded {len(files)} file(s)")
        else:
            self.append_message("No valid files were loaded")
            
    def is_valid_file(self, file_path: str) -> bool:
        """Validate file extension against allowed types"""
        if not os.path.isfile(file_path):
            return False
        return os.path.splitext(file_path)[1].lower() in self.ALLOWED_EXTENSIONS
        
    def append_message(self, message: str) -> None:
        """Safely append message to text edit"""
        self.text_edit.append(message)
        
    def clear_text_edit(self) -> None:
        """Clear the text display"""
        self.text_edit.clear()
        self.dropped_files = []
        
    def get_files(self) -> List[str]:
        """Get currently loaded files"""
        return self.dropped_files
        
    def load_las_files(self) -> None:
        """Load LAS files through file dialog"""
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select LAS Files",
                "",
                "LAS Files (*.las);;All Files (*)"
            )
            
            if files:
                self._process_selected_files(files, file_type="LAS")
                
        except Exception as e:
            self._handle_error("Error loading LAS files", e)
            
    def load_deviation_data(self) -> None:
        """Load deviation data from CSV"""
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Deviation Data CSV",
                "",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if files:
                self._process_selected_files(files, file_type="CSV")
                
        except Exception as e:
            self._handle_error("Error loading deviation data", e)
            
    def _process_selected_files(self, files: List[str], file_type: str) -> None:
        """Common processing for selected files"""
        valid_files = [f for f in files if self.is_valid_file(f)]
        
        if not valid_files:
            self.append_message(f"No valid {file_type} files selected")
            return
            
        self.dropped_files = valid_files
        self.text_edit.clear()
        
        for file in valid_files:
            self.append_message(f"Selected: {os.path.basename(file)}")
            
        if file_type == "LAS":
            self._import_las_files(valid_files)
        elif file_type == "CSV":
            self._import_deviation_data(valid_files[0])  # Currently handles single file
            
    def _import_las_files(self, las_files: List[str]) -> None:
        """Handle LAS file import"""
        try:
            if not hasattr(self.mainwindow, 'wells'):
                self.mainwindow.wells = []
                
            importer = DataIMPEX(self.mainwindow.wells)
            
            for las_file in las_files:
                importer.import_Single_LAS_File(las_file_path=las_file)
                self.append_message(f"Successfully imported: {os.path.basename(las_file)}")
                
            self.mainwindow.Load_Wells()
            
        except Exception as e:
            self._handle_error("LAS import failed", e)
            
    def _import_deviation_data(self, csv_file: str) -> None:
        """Handle deviation data import from CSV"""
        try:
            dev_df = pd.read_csv(csv_file)
            well_name = dev_df['Well'].unique()[0]
            
            dataset = Dataset(
                date_created=datetime.now(),
                name='DIRECTIONAL',
                type='Point',
                wellname=well_name,
                index_name='DEPTH'
            )
            
            # Find or create well
            well = next((w for w in self.mainwindow.wells if w.well_name == well_name), None)
            
            if well:
                well.datasets.append(dataset)
                self.append_message(f"Added directional data to existing well: {well_name}")
            else:
                well = Well(
                    date_created=datetime.now(),
                    well_name=well_name,
                    well_type='Dev'
                )
                well.datasets.append(dataset)
                self.mainwindow.wells.append(well)
                self.append_message(f"Created new well with directional data: {well_name}")
                
        except Exception as e:
            self._handle_error("Deviation data import failed", e)
            
    def _handle_error(self, context: str, error: Exception) -> None:
        """Consistent error handling"""
        error_msg = f"{context}: {str(error)}"
        self.append_message(error_msg)
        QMessageBox.critical(self, "Error", error_msg)
        print(error_msg)  # Also log to console