from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QSizePolicy, QTableView, QStyledItemDelegate, 
    QCheckBox, QMessageBox, QHeaderView, QStyle
)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
import pandas as pd
from typing import List, Optional, Dict, Any
from fe_data_objects import Constant,Constants

class ConstantsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Initialize and configure the UI components"""
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(2, 2, 2, 2)
        
        # Button panel
        self._setup_button_panel()
        
        # Table view
        self._setup_table_view()
        
    def _setup_button_panel(self):
        """Configure the button control panel"""
        button_panel = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_panel.setLayout(button_layout)
        
        self.delete_btn = self._create_button("Delete", self._on_delete_clicked)
        self.add_btn = self._create_button("Add", self._on_add_clicked)
        self.export_btn = self._create_button("Export", self._on_export_clicked)
        
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.export_btn)
        self.layout().addWidget(button_panel)
        
    def _setup_table_view(self):
        """Configure the table view and model"""
        # Initialize with empty DataFrame
        self._dataframe = pd.DataFrame(columns=['Checked', 'Name', 'Value', 'Description'])
        self.model = ConstantsTableModel(self._dataframe)
        
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setItemDelegateForColumn(0, CheckBoxDelegate())
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        
        self.layout().addWidget(self.table_view)
        
    def _create_button(self, text: str, handler) -> QPushButton:
        """Helper method to create consistent buttons"""
        btn = QPushButton(text)
        btn.setFixedHeight(30)
        btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        btn.clicked.connect(handler)
        return btn
        
    def _connect_signals(self):
        """Connect all signal-slot connections"""
        self.model.dataChanged.connect(self._on_data_changed)
        
    def get_table_view(self) -> QTableView:
        """Get the table view widget"""
        return self.table_view
        
    def load_constants(self, constants: Constants) -> None:
        """Load constants into the table"""
        try:
            data = [{
                'Checked': False,
                'Name': const.name,
                'Value': str(const.value),
                'Description': const.tag
            } for const in constants.constants]
            
            self.model.load_data(pd.DataFrame(data))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load constants: {str(e)}")
            
    def get_selected_constants(self) -> List[Constant]:
        """Get currently selected constants"""
        selected = []
        for i in range(self.model.rowCount()):
            if self.model._dataframe.at[i, 'Checked']:
                selected.append(Constant(
                    name=self.model._dataframe.at[i, 'Name'],
                    value=self.model._dataframe.at[i, 'Value'],
                    tag=self.model._dataframe.at[i, 'Description']
                ))
        return selected
        
    def _on_delete_clicked(self):
        """Handle delete button click"""
        selected = self.get_selected_constants()
        if not selected:
            QMessageBox.warning(self, "Warning", "No constants selected for deletion")
            return
            
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Delete {len(selected)} constants?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.model.remove_selected()
            
    def _on_add_clicked(self):
        """Handle add button click"""
        self.model.add_row({
            'Checked': False,
            'Name': "New Constant",
            'Value': "",
            'Description': ""
        })
        # Scroll to and edit the new row
        last_row = self.model.rowCount() - 1
        self.table_view.scrollToBottom()
        self.table_view.edit(self.model.index(last_row, 1))
        
    def _on_export_clicked(self):
        """Handle export button click"""
        constants = Constants(self.model.to_dataclass_list())
        QMessageBox.information(self, "Export", f"Exported {len(constants.constants)} constants")
        
    def _on_data_changed(self):
        """Handle data changes in the model"""
        pass


class ConstantsTableModel(QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame):
        super().__init__()
        self._dataframe = dataframe

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._dataframe)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._dataframe.columns)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        row, col = index.row(), index.column()
        
        if role == Qt.DisplayRole and col > 0:
            return str(self._dataframe.iat[row, col])
            
        if role == Qt.CheckStateRole and col == 0:
            return Qt.Checked if self._dataframe.at[row, 'Checked'] else Qt.Unchecked
            
        if role == Qt.EditRole and col > 0:
            return str(self._dataframe.iat[row, col])
            
        return None

    def setData(self, index: QModelIndex, value, role=Qt.EditRole) -> bool:
        if not index.isValid():
            return False
            
        row, col = index.row(), index.column()
        
        try:
            if role == Qt.CheckStateRole and col == 0:
                self._dataframe.at[row, 'Checked'] = value == Qt.Checked
            elif role == Qt.EditRole and col > 0:
                self._dataframe.iat[row, col] = value
            else:
                return False
                
            self.dataChanged.emit(index, index)
            return True
            
        except Exception as e:
            return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
            
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        
        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable
        else:
            flags |= Qt.ItemIsEditable
            
        return flags

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["", "Name", "Value", "Description"][section]
        return None

    def load_data(self, dataframe: pd.DataFrame) -> None:
        """Load new data into the model"""
        self.beginResetModel()
        self._dataframe = dataframe
        self.endResetModel()

    def add_row(self, row_data: dict) -> None:
        """Add a new row to the model"""
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._dataframe = pd.concat([self._dataframe, pd.DataFrame([row_data])], ignore_index=True)
        self.endInsertRows()

    def remove_selected(self) -> None:
        """Remove all selected rows"""
        selected = self._dataframe[self._dataframe['Checked']].index
        if not selected.empty:
            self.beginRemoveRows(QModelIndex(), selected[0], selected[-1])
            self._dataframe = self._dataframe[~self._dataframe['Checked']]
            self.endRemoveRows()

    def to_dataclass_list(self) -> List[Constant]:
        """Convert model data to list of Constant objects"""
        return [
            Constant(
                name=row['Name'],
                value=row['Value'],
                tag=row['Description']
            )
            for _, row in self._dataframe.iterrows()
        ]


class CheckBoxDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return None  # No editor needed for checkbox

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        
        if index.column() == 0:
            checked = index.model().data(index, Qt.CheckStateRole) == Qt.Checked
            checkbox_style = QStyleOptionButton()
            checkbox_style.state |= QStyle.State_Enabled
            if checked:
                checkbox_style.state |= QStyle.State_On
            else:
                checkbox_style.state |= QStyle.State_Off
            checkbox_style.rect = self.get_checkbox_rect(option)
            
            QApplication.style().drawControl(QStyle.CE_CheckBox, checkbox_style, painter)

    def editorEvent(self, event, model, option, index):
        if (event.type() == event.MouseButtonRelease and 
            event.button() == Qt.LeftButton and
            index.column() == 0):
            
            current = index.model().data(index, Qt.CheckStateRole)
            new = Qt.Unchecked if current == Qt.Checked else Qt.Checked
            return model.setData(index, new, Qt.CheckStateRole)
            
        return False

    def get_checkbox_rect(self, option):
        size = QApplication.style().pixelMetric(QStyle.PM_IndicatorWidth)
        rect = option.rect
        rect.setWidth(size)
        rect.moveCenter(option.rect.center())
        return rect
