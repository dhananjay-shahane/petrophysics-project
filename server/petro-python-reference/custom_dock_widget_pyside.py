from PySide6.QtWidgets import QDockWidget
from PySide6.QtCore import Qt

class CustomDockWidget(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

    def setAllowedAreas(self, areas):
        # Ensure that the dock widget can only be docked to the left or right
        allowed_areas = Qt.BottomDockWidgetArea
        super().setAllowedAreas(allowed_areas)
        
class FeedbackDockWidget(CustomDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        # Restrict to bottom dock area only
        self.set_allowed_areas(Qt.BottomDockWidgetArea)
        
    def set_allowed_areas(self, allowed_areas):
        """Set allowed dock widget areas."""
        self.setAllowedAreas(allowed_areas)
