from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtCore import Qt

class CustomDockWidget(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

    def setAllowedAreas(self, areas):
        # Allow docking only to the left and right
        allowed_areas = Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
        super().setAllowedAreas(allowed_areas)