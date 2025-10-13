import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QVBoxLayout, QPushButton, 
                             QWidget, QColorDialog, QMenu, QDialog, 
                             QFormLayout, QLabel, QLineEdit, QFileDialog)
from PyQt5.QtCore import Qt, QPoint, QMimeData
import xml.etree.ElementTree as ET
from collections import namedtuple

class CurvePropertiesDialog(QDialog):
    def __init__(self, line):
        super().__init__()
        self.line = line
        self.setWindowTitle("Curve Properties")
        self.layout = QFormLayout()
        
        self.color_label = QLabel("Color:")
        self.color_edit = QLineEdit(self.line.get_color())
        self.layout.addRow(self.color_label, self.color_edit)

        self.scale_label = QLabel("Scale (y-axis):")
        self.scale_edit = QLineEdit(str(self.line.get_ydata().max()))
        self.layout.addRow(self.scale_label, self.scale_edit)

        self.setLayout(self.layout)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.apply_properties)
        self.layout.addRow(self.ok_button)

    def apply_properties(self):
        color = self.color_edit.text()
        scale = float(self.scale_edit.text())
        self.line.set_color(color)
        self.line.axes.set_ylim(0, scale)
        self.line.axes.figure.canvas.draw()
        self.accept()

class MatplotlibWidget(QWidget):
    def __init__(self, feedback_dock_widget):
        super().__init__()
        self.figure, self.axs = plt.subplots(1, 3, figsize=(10, 4), sharey=True)
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        self.x = np.linspace(1, 10, 100)
        self.y_data = [np.log(self.x), np.log10(self.x), np.exp(self.x / 10)]
        self.plot_titles = ['Log', 'Log10', 'Exponential']
        self.plot_lines = []
        self.selected_line = None
        self.selected_subplot_index = None
        self.feedback_dock_widget = feedback_dock_widget

        self.init_plots()
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.setAcceptDrops(True)
        

    def init_plots(self):
        for i, ax in enumerate(self.axs):
            line, = ax.plot(self.x, self.y_data[i], label=self.plot_titles[i], picker=True)
            self.plot_lines.append(line)
            ax.set_title(self.plot_titles[i])
            ax.set_yscale('log')
            ax.legend()

        self.axs[0].set_ylabel('Common Y-Axis')
        for ax in self.axs[1:]:
            ax.yaxis.set_ticks([])

        self.canvas.draw()

    def on_pick(self, event):
        if isinstance(event.artist, plt.Line2D):
            self.selected_line = event.artist
            self.send_curve_to_feedback()

    def send_curve_to_feedback(self):
        if self.selected_line and self.feedback_dock_widget:
            feedback_text_edit = self.feedback_dock_widget.widget()
            current_text = feedback_text_edit.toPlainText()
            new_text = f"Selected Curve: {self.selected_line.get_label()}\n"
            feedback_text_edit.setPlainText(current_text + new_text)

    def on_click(self, event):
        if event.button == 3:  # Right-click
            for i, ax in enumerate(self.axs):
                if event.inaxes == ax:
                    self.selected_subplot_index = i
                    self.show_context_menu(event)
                    return

    def show_context_menu(self, event):
        context_menu = QMenu(self)

        change_color_action = context_menu.addAction("Change Color")
        remove_curve_action = context_menu.addAction("Remove Curve")
        add_curve_action = context_menu.addAction("Add Curve")
        save_plot_action = context_menu.addAction("Save Plot Settings")
        load_plot_action = context_menu.addAction("Load Plot Settings")

        properties_menu = context_menu.addMenu("Properties")
        properties_menu.addAction("Edit Curve Properties", self.edit_curve_properties)

        global_pos = self.mapToGlobal(QPoint(event.x, event.y))  # Corrected line
        action = context_menu.exec_(global_pos)

        if action == change_color_action:
            self.change_color()
        elif action == remove_curve_action:
            self.remove_curve()
        elif action == add_curve_action:
            self.add_curve_to_subplot()
        elif action == save_plot_action:
            self.save_plot_settings()
        elif action == load_plot_action:
            self.load_plot_settings()

    def change_color(self):
        if self.selected_line:
            color = QColorDialog.getColor()
            if color.isValid():
                self.selected_line.set_color(color.name())
                self.canvas.draw()
                
    def edit_curve_properties(self):
        if self.selected_line:
            dialog = CurvePropertiesDialog(self.selected_line)
            dialog.exec_()
    def save_plot_settings(self):
        plot_settings = ET.Element("plot_settings")

        for ax in self.axs:
            subplot = ET.SubElement(plot_settings, "subplot")
            subplot.set("title", ax.get_title())
            subplot.set("xlim", f"{ax.get_xlim()[0]},{ax.get_xlim()[1]}")
            subplot.set("ylim", f"{ax.get_ylim()[0]},{ax.get_ylim()[1]}")

            for line in ax.get_lines():
                line_elem = ET.SubElement(subplot, "line")
                line_elem.set("label", line.get_label())
                line_elem.set("color", line.get_color())
                line_elem.set("ydata", ",".join(map(str, line.get_ydata())))

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Plot Settings", "", "XML Files (*.xml)")
        if file_name:
            tree = ET.ElementTree(plot_settings)
            tree.write(file_name)
            print(f"Plot settings saved to {file_name}")

    def load_plot_settings(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Plot Settings", "", "XML Files (*.xml)")
        if file_name:
            tree = ET.parse(file_name)
            root = tree.getroot()

            for ax, subplot in zip(self.axs, root.findall("subplot")):
                ax.set_title(subplot.get("title"))
                xlim = list(map(float, subplot.get("xlim").split(",")))
                ax.set_xlim(xlim)
                ylim = list(map(float, subplot.get("ylim").split(",")))
                ax.set_ylim(ylim)

                for line_elem in subplot.findall("line"):
                    label = line_elem.get("label")
                    color = line_elem.get("color")
                    ydata = list(map(float, line_elem.get("ydata").split(",")))
                    line, = ax.plot(self.x[:len(ydata)], ydata, label=label, color=color, picker=True)
                    self.plot_lines.append(line)

            self.canvas.draw()
            print(f"Plot settings loaded from {file_name}")
            
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        Point = namedtuple('Point', ['x', 'y'])
        if event.mimeData().hasText():
            mouse_pos = event.pos()
            point = Point(x=mouse_pos.x(), y=mouse_pos.y())
            
            for i, ax in enumerate(self.axs):
                contains, _ = ax.contains(point)  # Use the Point object directly
                if contains:
                    
                    new_y = np.random.rand(100) * 10  # Example data for the new curve
                    line, = ax.plot(self.x, new_y, picker=True, label='Dropped Curve', linestyle='--', color='purple')
                    self.plot_lines.append(line)
                    ax.legend()
                    self.canvas.draw()
                    print(f"Dropped curve in subplot {i}")
                    return


