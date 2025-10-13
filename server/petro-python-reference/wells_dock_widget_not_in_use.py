from PyQt5.QtWidgets import QDockWidget, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from custom_dock_widget import CustomDockWidget

class WellsDockWidget(CustomDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.set_allowed_areas(Qt.BottomDockWidgetArea)

    def set_allowed_areas(self, allowed_areas):
        """Set allowed dock widget areas."""
        self.setAllowedAreas(allowed_areas)

    def update_feedback(self, label, color, ydata):
        """Update the feedback text with curve details."""
        current_text = self.text_edit.toPlainText()
        new_text = f"Selected Curve:\nLabel: {label}\nColor: {color}\nY Data: {list(ydata)}\n\n"
        self.text_edit.setPlainText(current_text + new_text)
    def get_list_box(self):
        """Expose the QTextEdit widget."""
        return self.li
