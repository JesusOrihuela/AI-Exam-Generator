import os
from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QListWidget, QPushButton, QHBoxLayout,
    QFileDialog
)
from PyQt6.QtCore import pyqtSignal


class AnalysisPanel(QWidget):
    """Panel para cargar y preparar documentos a analizar."""
    request_process = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_paths: List[str] = []

        group = QGroupBox("1. Analizar Nuevos Documentos")
        layout = QVBoxLayout(group)

        self.file_list_widget = QListWidget()
        layout.addWidget(self.file_list_widget)

        btns = QHBoxLayout()
        add_files_btn = QPushButton("Añadir Archivos")
        add_files_btn.clicked.connect(self._add_files)
        clear_files_btn = QPushButton("Limpiar Lista")
        clear_files_btn.clicked.connect(self._clear_files)
        btns.addWidget(add_files_btn)
        btns.addWidget(clear_files_btn)
        layout.addLayout(btns)

        self.process_btn = QPushButton("Analizar y Guardar en Biblioteca")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(lambda: self.request_process.emit())
        layout.addWidget(self.process_btn)

        root = QVBoxLayout(self)
        root.addWidget(group)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar documentos", "", "Documentos (*.pdf *.docx *.pptx)")
        for file in files:
            if file not in self._file_paths:
                self._file_paths.append(file)
                self.file_list_widget.addItem(os.path.basename(file))
        self.process_btn.setEnabled(len(self._file_paths) > 0)

    def _clear_files(self):
        self._file_paths.clear()
        self.file_list_widget.clear()
        self.process_btn.setEnabled(False)

    def get_file_paths(self) -> List[str]:
        return list(self._file_paths)

    def mark_processed(self, filename: str):
        base = os.path.basename(filename)
        for i in range(self.file_list_widget.count()):
            if self.file_list_widget.item(i).text() == base:
                self.file_list_widget.takeItem(i)
                break
        if filename in self._file_paths:
            self._file_paths.remove(filename)
        self.process_btn.setEnabled(len(self._file_paths) > 0)
