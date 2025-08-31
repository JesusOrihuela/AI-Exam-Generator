from typing import List, Dict, Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QListWidget, QPushButton, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal


class LibraryPanel(QWidget):
    """Panel de biblioteca con checkboxes y eliminación múltiple."""
    request_delete = pyqtSignal()
    checked_count_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)

        group = QGroupBox("Biblioteca de Contenido Analizado")
        g_layout = QVBoxLayout(group)

        self.content_list = QListWidget()
        self.content_list.itemChanged.connect(self._on_item_changed)
        g_layout.addWidget(self.content_list)

        self.delete_content_btn = QPushButton("Eliminar Contenido Seleccionado")
        self.delete_content_btn.clicked.connect(lambda: self.request_delete.emit())
        self.delete_content_btn.setEnabled(False)
        g_layout.addWidget(self.delete_content_btn)

        root.addWidget(group)

    def load_items(self, items: List[Dict[str, Any]]):
        self.content_list.clear()
        for data in items:
            try:
                item = QListWidgetItem(data.get("name", "(sin nombre)"))
                item.setData(Qt.ItemDataRole.UserRole, data)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.content_list.addItem(item)
            except Exception:
                continue
        self._update_delete_enabled()

    def get_checked_items(self) -> List[QListWidgetItem]:
        items = []
        for i in range(self.content_list.count()):
            it = self.content_list.item(i)
            if it.checkState() == Qt.CheckState.Checked:
                items.append(it)
        return items

    def get_checked_data(self) -> List[Dict[str, Any]]:
        return [it.data(Qt.ItemDataRole.UserRole) for it in self.get_checked_items()]

    def _on_item_changed(self, _item: QListWidgetItem):
        self._update_delete_enabled()
        self.checked_count_changed.emit(len(self.get_checked_items()))

    def _update_delete_enabled(self):
        has_checked = len(self.get_checked_items()) > 0
        self.delete_content_btn.setEnabled(has_checked)
