import os
from PyQt5.QtCore import QSettings

class ProjectManager:
    def __init__(self):
        self.project_path = None
        self.settings = QSettings("Petrocene", "PetroceneApp")

    def create_project(self, base_folder, project_name):
        """Create a new project directory and structure."""
        if not base_folder or not project_name:
            print("Base folder or project name is missing.")
            return

        self.project_path = os.path.join(base_folder, project_name)

        # Create project directory and structure
        self.create_directory_structure()

        # Save project path to QSettings
        self.settings.setValue("project_path", self.project_path)
        print(f"Project created at: {self.project_path}")
        return self.project_path
        
    def open_project_path(self, folder_path):
        """Save a new project path to QSettings."""
        if not folder_path or not os.path.isdir(folder_path):
            print("Invalid folder path.")
            return None
        
        self.settings.setValue("project_path", folder_path)
        print(f"Project path set to: {folder_path}")
        return folder_path
        
    def create_directory_structure(self):
        """Create the directory structure for the project."""
        try:
            os.makedirs(self.project_path)

            # Define your folder structure
            subfolders = [
                "01-OUTPUT",
                "01-OUTPUT/Reports and Presentations/",
                "02-INPUT_LAS_FOLDER",
                "03-DEVIATION",
                "04-WELL_HEADER",
                "05-TOPS_FOLDER",
                "06-ZONES_FOLDER",
                "07-DATA_EXPORTS",
                "08-VOL_MODELS",
                "09-SPECS",
                "10-WELLS",
            ]

            for folder in subfolders:
                os.makedirs(os.path.join(self.project_path, folder))

        except Exception as e:
            print(f"Failed to create project structure: {e}")

    def load_project(self):
        """Load the project path from QSettings."""
        self.project_path = self.settings.value("project_path", None)
        if self.project_path:
            print(f"Loaded project from: {self.project_path}")
        else:
            print("No project path found in settings.")
    def get_project_path(self):
        """Check the current project path stored in QSettings."""
        project_path = self.settings.value("project_path", None)
        if project_path:
            print(f"Current project path in QSettings: {project_path}")
            return project_path
        else:
            print("No project path found in QSettings.")
        return None

if __name__ == "__main__":
    # Example usage
    base_folder = "/path/to/your/base/folder"  # Change this to your desired base folder
    project_name = "MyNewProject"  # Specify your project name

    pm = ProjectManager()
    pm.create_project(base_folder, project_name)  # Create a new project
    # pm.load_project()  # Uncomment to load an existing project from settings
