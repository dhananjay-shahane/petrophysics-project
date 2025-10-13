class ThemeManager:
    """Class to manage application themes."""
    
    @staticmethod
    def get_dark_theme():
        return """
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
                border: 1px solid #4A4E50; 
            }
            QTabBar::tab:selected {
                background: #4A4E50;
                margin-right: 1px;  /* Small margin between tabs */
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
            QTreeView {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3C3F41;
            }
            QLabel {
                color: #FFFFFF; 
                background-color: #3C3F41; 
                padding: 5px;  
            }
            QComboBox {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3C3F41;
            }
            QPushButton {
                background-color: #3C3F41;
                color: #FFFFFF;
                border: 1px solid #4A4E50;
            }
            QPushButton:hover {
                background-color: #4A4E50;
            }
        """

    @staticmethod
    def get_light_theme():
        return """
            QMainWindow {
                background-color: #FFFFFF;
                color: #000000;
            }
            QDockWidget {
                background-color: #F0F0F0;
                color: #000000;
            }
            QSplitter {
                background-color: #F0F0F0;
            }
            QTextEdit {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
            }
            QTabWidget {
                background-color: #F0F0F0;
                color: #000000;
            }
             QTabBar::tab {
                background: #F0F0F0;
                padding: 10px 15px;  /* Adjusted padding */
                border: 1px solid #CCCCCC;
                margin-right: 2px;  /* Small margin between tabs */
            }
            QTabBar::tab:selected {
                background: #E0E0E0;
                margin-right: 2px;  /* Small margin between tabs */
            }
            }
            QListWidget {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
            }
            QTableView {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
            }
            QTreeView {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
            }
            QLabel {
                color: #000000;  
                background-color: #F0F0F0;  
                padding: 5px;  
            }
            QComboBox {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
            }
            QPushButton {
                background-color: #F0F0F0;
                color: #000000;
                border: 1px solid #CCCCCC;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """
    @staticmethod
    def get_teal_blue_theme():
        return """
            QMainWindow {
                background-color: #E5F6F7;  /* Light Background */
                color: #2C3E50;  /* Dark Text */
            }
            QDockWidget {
                background-color: #B2EBF2;  /* Light Teal */
                color: #2C3E50;
            }
            QSplitter {
                background-color: #B2EBF2;
            }
            QTextEdit {
                background-color: #FFFFFF;  /* White */
                color: #2C3E50;  /* Dark Text */
                border: 1px solid #007B7F;  /* Dark Teal */
            }
            QTabWidget {
                background-color: #B2EBF2;
                color: #2C3E50;
            }
            QTabBar::tab {
                background: #B2EBF2;
                padding: 8px 25px;  /* Increased padding */
                border: 1px solid #007B7F;
                margin: 0;  /* No margin to avoid cutting off */
            }
            QTabBar::tab:selected {
                background: #80DEEA;
                padding: 8px 25px;  /* Increased padding */

            }
            QTabBar::tab:!selected {
                margin-right: 1px;  /* Small margin for non-selected tabs */
                margin-left: 1px;  /* Small margin for non-selected tabs */
            }
            QListWidget {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #007B7F;
            }
            QTableView {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #007B7F;
                QTableView {
                margin: 0px;  /* Remove margins */
                padding: 0px;  /* Remove padding */
            }
            }
            QTreeView {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #007B7F;
            }
            QLabel {
                color: #2C3E50;  
                background-color: #B2EBF2;  
                padding: 5px;  
            }
            QComboBox {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #007B7F;
            }
            QPushButton {
                background-color: #A1D8E6;  /* Light Teal */
                color: #2C3E50;
                border: 1px solid #007B7F;  /* Darker Teal */
            }
            QPushButton:hover {
                background-color: #B2E0E6;  /* Lighter Teal */
            }
        """