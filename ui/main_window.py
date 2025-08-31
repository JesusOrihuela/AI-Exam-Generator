import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QGroupBox, QStatusBar, QMessageBox, QSplitter, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ui.results_window import ResultsWindow
from ui.exam_window import ExamWindow
from ui.bank_window import QuestionBankWindow

from ui.widgets import LoaderOverlay
from ui.panels.library_panel import LibraryPanel
from ui.panels.analysis_panel import AnalysisPanel
from ui.panels.generation_panel import GenerationPanel

from logic.workers.processing import ProcessingWorker
from logic.workers.exam_generation import ExamGenerationWorker
from logic.repositories import content_library as content_repo
from utils.paths import ensure_dirs


class MainWindow(QMainWindow):
    """Ventana principal: orquesta paneles y workers."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Exámenes con IA - Gestor de Contenido")
        self.setGeometry(100, 100, 1000, 700)

        self.processing_worker = None
        self.generation_worker = None

        self.pending_saves = []
        self.naming_dialog_active = False
        self.processing_all_done = False

        ensure_dirs()
        self._build_ui()
        self._connect_signals()
        self.load_content_library()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        api_group = QGroupBox("Configuración")
        api_layout = QHBoxLayout(api_group)
        api_label = QLabel("API Key:")
        api_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(os.getenv("OPENAI_API_KEY", ""))
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_key_input)

        # Compactar altura del área de API
        api_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        api_group.setMaximumHeight(90)

        main_layout.addWidget(api_group)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.library_panel = LibraryPanel()
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        right_splitter = QSplitter(Qt.Orientation.Vertical)
        self.analysis_panel = AnalysisPanel()
        right_splitter.addWidget(self.analysis_panel)

        self.generation_panel = GenerationPanel()
        right_splitter.addWidget(self.generation_panel)

        # Proporción vertical 5/8 (análisis) y 3/8 (generación)
        right_splitter.setStretchFactor(0, 5)
        right_splitter.setStretchFactor(1, 3)

        right_layout.addWidget(right_splitter)

        splitter.addWidget(self.library_panel)
        splitter.addWidget(right_widget)

        # Biblioteca ocupa toda la altura disponible
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)
        self.setStatusBar(QStatusBar())

        self.loader = LoaderOverlay(self)

    def _connect_signals(self):
        self.library_panel.request_delete.connect(self.delete_checked_content)
        self.library_panel.checked_count_changed.connect(
            lambda count: self.generation_panel.set_generate_enabled(count > 0)
        )
        self.generation_panel.request_manage_bank.connect(
            lambda: QuestionBankWindow(self).exec()
        )

        self.analysis_panel.request_process.connect(self.start_processing)
        self.generation_panel.request_generate.connect(self.start_generation)

    def show_loader(self, message="Procesando..."):
        self.loader.setMessage(message)
        self.loader.setGeometry(self.rect())
        self.loader.show()
        self.loader.raise_()
        self.setEnabled(False)

    def hide_loader(self):
        self.loader.hide()
        self.setEnabled(True)

    def load_content_library(self):
        items = content_repo.list_items()
        self.library_panel.load_items(items)
        self.generation_panel.set_generate_enabled(False)

    def start_processing(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "API Key Requerida", "Introduce tu API Key.")
            return
        file_paths = self.analysis_panel.get_file_paths()
        if not file_paths:
            QMessageBox.warning(self, "Archivos Requeridos", "Añade al menos un documento.")
            return

        self.pending_saves.clear()
        self.naming_dialog_active = False
        self.processing_all_done = False

        self.show_loader("Analizando documentos…")
        self._set_panels_enabled(False)

        self.processing_worker = ProcessingWorker(api_key, file_paths)
        self.processing_worker.progress.connect(self._update_status)
        self.processing_worker.error.connect(self._on_task_error)
        self.processing_worker.finished.connect(self._on_processing_finished)
        self.processing_worker.all_done.connect(self._on_processing_all_done)
        self.processing_worker.start()

    def _on_processing_finished(self, summary, filename):
        self.analysis_panel.mark_processed(filename)
        self.pending_saves.append((summary, filename))
        if not self.naming_dialog_active:
            self._process_next_save()

    def _process_next_save(self):
        if not self.pending_saves:
            if self.processing_worker and self.processing_worker.isRunning():
                self.show_loader("Analizando documentos…")
                self._set_panels_enabled(False)
            else:
                self.hide_loader()
                self._set_panels_enabled(True)
                if self.processing_all_done:
                    self.statusBar().showMessage("Análisis completado para todos los documentos.")
            return

        self.naming_dialog_active = True
        self.hide_loader()
        self._set_panels_enabled(True)

        summary, filename = self.pending_saves.pop(0)
        suggested = os.path.splitext(filename)[0]

        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(
            self,
            "Guardar Contenido",
            f"Introduce un nombre para el contenido generado desde '{filename}':",
            text=suggested
        )

        if ok and name:
            try:
                content_repo.save_item(name=name, source_files=[filename], summary=summary)
                self.load_content_library()
                self.statusBar().showMessage(f"Contenido '{name}' guardado en la biblioteca.")
            except Exception as e:
                QMessageBox.critical(self, "Error al Guardar", f"No se pudo guardar el archivo: {e}")
        else:
            self.statusBar().showMessage(f"Análisis de {filename} completado, pero no guardado.")

        self.naming_dialog_active = False
        if self.pending_saves:
            self._process_next_save()
        else:
            if self.processing_worker and self.processing_worker.isRunning():
                self.show_loader("Analizando documentos…")
                self._set_panels_enabled(False)
            else:
                self.hide_loader()
                self._set_panels_enabled(True)
                if self.processing_all_done:
                    self.statusBar().showMessage("Análisis completado para todos los documentos.")

    def _on_processing_all_done(self):
        self.processing_all_done = True
        if not self.naming_dialog_active and not self.pending_saves:
            self.hide_loader()
            self._set_panels_enabled(True)
            self.statusBar().showMessage("Análisis completado para todos los documentos.")

    def start_generation(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "API Key Requerida", "Introduce tu API Key.")
            return

        checked_data = self.library_panel.get_checked_data()
        if not checked_data:
            QMessageBox.information(self, "Selecciona contenido", "Marca uno o más contenidos en la biblioteca para generar el examen.")
            return

        summaries = [f"[{d['name']}]\n{d.get('summary','')}" for d in checked_data]
        combined_summary = "\n\n" + ("\n\n" + "="*80 + "\n\n").join(summaries) + "\n\n"

        n = self.generation_panel.get_num_questions()
        temp = self.generation_panel.get_temperature()
        top_p = self.generation_panel.get_top_p()

        self.show_loader("Generando examen…")
        self.generation_worker = ExamGenerationWorker(api_key, combined_summary, n, temp, top_p)
        self.generation_worker.progress.connect(self._update_status)
        self.generation_worker.error.connect(self._on_task_error)
        self.generation_worker.finished.connect(self._on_generation_finished)
        self.generation_worker.start()

    def _on_generation_finished(self, questions):
        self.hide_loader()
        exam_dialog = ExamWindow(questions, self)
        if exam_dialog.exec():
            ResultsWindow(questions, exam_dialog.user_answers, self).exec()

    def delete_checked_content(self):
        checked_data = self.library_panel.get_checked_data()
        if not checked_data:
            return

        names = "\n- " + "\n- ".join([d.get("name", "(sin nombre)") for d in checked_data])
        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Eliminar permanentemente los siguientes {len(checked_data)} contenidos?\n{names}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted = 0
        for d in checked_data:
            path = d.get("_file_path")
            if path and content_repo.delete_item_by_path(path):
                deleted += 1

        self.load_content_library()
        self.statusBar().showMessage(f"Eliminados {deleted} contenidos de la biblioteca.")

    def _update_status(self, message: str):
        self.statusBar().showMessage(message)

    def _on_task_error(self, message: str):
        self.hide_loader()
        self._set_panels_enabled(True)
        QMessageBox.critical(self, "Error", message)

    def _set_panels_enabled(self, enabled: bool):
        self.analysis_panel.setEnabled(enabled)
        self.generation_panel.setEnabled(enabled)
        self.library_panel.setEnabled(enabled)
