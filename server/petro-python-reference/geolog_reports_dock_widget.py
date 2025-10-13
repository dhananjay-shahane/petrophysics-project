import sys
import os
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QListView, QLineEdit, QPushButton, QMenuBar, QAction, QHBoxLayout

class FileViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Viewer")
        self.setGeometry(100, 100, 800, 400)

        # Create the main layout for the FileViewer window
        main_layout = QVBoxLayout(self)

        # Create a horizontal layout to hold the left and right parts
        horizontal_layout = QHBoxLayout()

        # Create a vertical layout for the left side (folder textbox, button, and list view)
        left_layout = QVBoxLayout()
         # Create a vertical layout for the left side (folder textbox, button, and list view)
        right_layout = QVBoxLayout()

        # Button to open the folder dialog
        self.button = QPushButton('Select Folder', self)
        self.button.clicked.connect(self.open_folder_dialog)

        # Textbox to display the selected folder path
        self.folderTextbox = QLineEdit(self)
        self.folderTextbox.setReadOnly(True)  # Make it read-only
        self.folderTextbox.setPlaceholderText("No folder selected")
        
        # Textbox to display the name of the output folder
        self.outputfolderTextbox = QLineEdit(self)
        self.outputfolderTextbox.setReadOnly(True)  # Make it read-only
        self.outputfolderTextbox.setPlaceholderText("No folder selected")

        # List view on the left (for .txt files)
        self.listViewLeft = QListView(self)
        self.modelLeft = QStringListModel(self)
        self.listViewLeft.setModel(self.modelLeft)

        # Add the folder textbox, button, and list view to the left layout
        left_layout.addWidget(self.folderTextbox)   # Folder path text box
        left_layout.addWidget(self.button)           # Select folder button
        left_layout.addWidget(self.listViewLeft)     # List view for files

       
        
        # List view on the right (for selected file content or additional info)
        self.listViewRight = QListView(self)
        self.modelRight = QStringListModel(self)
        self.listViewRight.setModel(self.modelRight)

        # Text box to display the content of the selected file
        self.textbox = QLineEdit(self)
        self.textbox.setReadOnly(True)

         # Add the folder textbox, button, and list view to the left layout
        right_layout.addWidget(self.outputfolderTextbox)   # Folder path text box
        right_layout.addWidget(self.listViewRight)     # List view for files
        # Add the left layout (with folder textbox, button, and list view) to the horizontal layout
        horizontal_layout.addLayout(left_layout)      # Left layout with folder textbox, button, and list view
        horizontal_layout.addLayout(right_layout)  # Right list view for file content

        # Add the horizontal layout and the file content textbox to the main layout
        main_layout.addLayout(horizontal_layout)        # Horizontal layout with left and right parts
        main_layout.addWidget(self.textbox)             # Textbox to display the file content

        # Set the layout for the FileViewer window
        self.setLayout(main_layout)

        # Initialize the selected file variable
        self.selected_file = None

    def open_folder_dialog(self):
        # Open folder selection dialog
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            # Update the folder textbox with the selected folder path
            self.folderTextbox.setText(folder)
            # Load the files from the selected folder into the list view
            self.load_files_in_folder(folder)

    def load_files_in_folder(self, folder_path):
        # Get all .txt files in the selected folder
        files = [f for f in os.listdir(folder_path) if f.endswith('.rpt')]  # Filter only .txt files
        self.modelLeft.setStringList(files)  # Populate the left list view with file names

        # Connect the listView click event to load file content
        self.listViewLeft.clicked.connect(lambda index: self.load_file_content(index, folder_path))

    def load_file_content(self, index, folder_path):
        filename = index.data()  # Get the selected filename
        self.selected_file = os.path.join(folder_path, filename)

        try:
            # Open the selected file and read its contents
            with open(self.selected_file, 'r') as file:
                lines = file.readlines()
                # Join lines with newline characters to show in the text box
                self.textbox.setText("".join(lines))
                # Optionally display the file content in the right QListView
                self.modelRight.setStringList(lines)
        except Exception as e:
            self.textbox.setText(f"Error reading file: {e}")

