import sys
import os
import time
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QListWidget, QFileDialog, QComboBox, QDoubleSpinBox, QStatusBar,
                             QMessageBox, QLineEdit, QGroupBox, QInputDialog, QListWidgetItem, QSplitter)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ui.styles import DARK_STYLESHEET
from ui.exam_window import ExamWindow
from ui.results_window import ResultsWindow
from ui.bank_window import QuestionBankWindow
from logic.worker import ProcessingWorker, ExamGenerationWorker

class MainWindow(QMainWindow):
    """Ventana principal con dos flujos: Analizar Contenido y Generar Examen."""
    
    CONTENT_LIBRARY_PATH = "content_library"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Exámenes con IA - Gestor de Contenido")
        self.setGeometry(100, 100, 1000, 700)
        self.file_paths = []
        self.init_ui()
        self.load_content_library()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        api_group = QGroupBox("Configuración de API de OpenAI")
        api_layout = QHBoxLayout(api_group)
        api_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(os.getenv("OPENAI_API_KEY", ""))
        api_layout.addWidget(self.api_key_input)
        main_layout.addWidget(api_group)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- PANEL IZQUIERDO: Biblioteca de Contenido ---
        library_widget = QWidget()
        library_layout = QVBoxLayout(library_widget)
        library_layout.addWidget(QLabel("Biblioteca de Contenido Analizado"))
        self.content_list = QListWidget()
        self.content_list.currentItemChanged.connect(self.on_content_selected)
        library_layout.addWidget(self.content_list)
        delete_content_btn = QPushButton("Eliminar Contenido Seleccionado")
        delete_content_btn.clicked.connect(self.delete_selected_content)
        library_layout.addWidget(delete_content_btn)
        
        # --- PANEL DERECHO: Acciones (Analizar o Generar) ---
        actions_widget = QWidget()
        self.actions_layout = QVBoxLayout(actions_widget)
        
        # Grupo para analizar nuevo contenido
        self.analysis_group = QGroupBox("1. Analizar Nuevos Documentos")
        analysis_vbox = QVBoxLayout(self.analysis_group)
        self.file_list_widget = QListWidget()
        self.file_list_widget.setFixedHeight(150)
        analysis_vbox.addWidget(self.file_list_widget)
        analysis_btn_hbox = QHBoxLayout()
        add_files_btn = QPushButton("Añadir Archivos")
        add_files_btn.clicked.connect(self.add_files)
        clear_files_btn = QPushButton("Limpiar Lista")
        clear_files_btn.clicked.connect(self.clear_files)
        analysis_btn_hbox.addWidget(add_files_btn)
        analysis_btn_hbox.addWidget(clear_files_btn)
        analysis_vbox.addLayout(analysis_btn_hbox)
        self.process_btn = QPushButton("Analizar y Guardar en Biblioteca")
        self.process_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.process_btn.clicked.connect(self.start_processing)
        analysis_vbox.addWidget(self.process_btn)
        self.actions_layout.addWidget(self.analysis_group)

        # Grupo para generar examen
        self.generation_group = QGroupBox("2. Generar Examen desde Contenido Seleccionado")
        generation_vbox = QVBoxLayout(self.generation_group)
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Nº Preguntas:"))
        self.num_questions_combo = QComboBox()
        self.num_questions_combo.addItems([str(i) for i in range(10, 31, 5)])
        self.num_questions_combo.setCurrentText("25")
        config_layout.addWidget(self.num_questions_combo)
        config_layout.addWidget(QLabel("Temperature:"))
        self.temp_spinbox = QDoubleSpinBox()
        self.temp_spinbox.setRange(0.0, 2.0); self.temp_spinbox.setSingleStep(0.1); self.temp_spinbox.setValue(0.7)
        config_layout.addWidget(self.temp_spinbox)
        config_layout.addWidget(QLabel("Top P:"))
        self.top_p_spinbox = QDoubleSpinBox()
        self.top_p_spinbox.setRange(0.0, 1.0); self.top_p_spinbox.setSingleStep(0.1); self.top_p_spinbox.setValue(1.0)
        config_layout.addWidget(self.top_p_spinbox)
        generation_vbox.addLayout(config_layout)
        self.generate_btn = QPushButton("Generar Examen")
        self.generate_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.generate_btn.clicked.connect(self.start_generation)
        generation_vbox.addWidget(self.generate_btn)
        self.generation_group.setEnabled(False) # Deshabilitado por defecto
        self.actions_layout.addWidget(self.generation_group)

        self.actions_layout.addStretch()
        
        manage_bank_btn = QPushButton("Administrar Banco de Preguntas")
        manage_bank_btn.clicked.connect(lambda: QuestionBankWindow(self).exec())
        self.actions_layout.addWidget(manage_bank_btn)

        splitter.addWidget(library_widget)
        splitter.addWidget(actions_widget)
        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter)
        
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Listo. Selecciona contenido de la biblioteca o analiza nuevos archivos.")

    def load_content_library(self):
        self.content_list.clear()
        if not os.path.exists(self.CONTENT_LIBRARY_PATH):
            os.makedirs(self.CONTENT_LIBRARY_PATH)
        
        for filename in os.listdir(self.CONTENT_LIBRARY_PATH):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.CONTENT_LIBRARY_PATH, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        item = QListWidgetItem(data['name'])
                        item.setData(Qt.ItemDataRole.UserRole, data)
                        self.content_list.addItem(item)
                except Exception as e:
                    print(f"Error cargando el archivo de contenido '{filename}': {e}")
    
    def on_content_selected(self, current_item, _):
        self.generation_group.setEnabled(current_item is not None)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar documentos", "", "Documentos (*.pdf *.docx *.pptx)")
        if files:
            for file in files:
                if file not in self.file_paths: self.file_paths.append(file); self.file_list_widget.addItem(os.path.basename(file))
    
    def clear_files(self):
        self.file_paths.clear(); self.file_list_widget.clear()

    def start_processing(self):
        if not self.api_key_input.text().strip(): QMessageBox.warning(self, "API Key Requerida", "Por favor, introduce tu OpenAI API Key."); return
        if not self.file_paths: QMessageBox.warning(self, "Archivos Requeridos", "Por favor, añade al menos un documento para analizar."); return
        
        try: total_size_bytes = sum(os.path.getsize(p) for p in self.file_paths)
        except FileNotFoundError as e: QMessageBox.critical(self, "Error de Archivo", f"No se encontró: {os.path.basename(e.filename)}. Limpia la lista y vuelve a cargarlo."); return

        MAX_TOTAL_SIZE_MB = 50
        if total_size_bytes > MAX_TOTAL_SIZE_MB * 1024 * 1024:
            QMessageBox.warning(self, "Archivos Demasiado Grandes", f"El tamaño total ({total_size_bytes / (1024*1024):.2f} MB) supera el límite de {MAX_TOTAL_SIZE_MB} MB."); return

        self.set_ui_enabled(False)
        self.processing_worker = ProcessingWorker(self.api_key_input.text().strip(), self.file_paths)
        self.processing_worker.progress.connect(self.update_status)
        self.processing_worker.error.connect(self.on_task_error)
        self.processing_worker.finished.connect(self.on_processing_finished)
        self.processing_worker.start()

    def on_processing_finished(self, summary, filenames):
        self.set_ui_enabled(True)
        name_suggestion = " & ".join(filenames)[:50] # Sugiere un nombre con los primeros archivos
        name, ok = QInputDialog.getText(self, "Guardar Contenido", "Introduce un nombre para este bloque de contenido (ej. 'Clase 3 - Mitosis'):", text=name_suggestion)
        if ok and name:
            content_data = {
                'name': name,
                'source_files': filenames,
                'created_at': time.time(),
                'summary': summary
            }
            safe_filename = f"{int(time.time())}_{''.join(filter(str.isalnum, name))}.json"
            try:
                with open(os.path.join(self.CONTENT_LIBRARY_PATH, safe_filename), 'w', encoding='utf-8') as f:
                    json.dump(content_data, f, indent=4)
                self.load_content_library()
                self.clear_files()
                self.statusBar().showMessage(f"Contenido '{name}' guardado en la biblioteca.")
            except Exception as e:
                QMessageBox.critical(self, "Error al Guardar", f"No se pudo guardar el archivo de contenido: {e}")
        else:
            self.statusBar().showMessage("Análisis completado, pero no guardado.")

    def start_generation(self):
        selected_item = self.content_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Sin Selección", "Por favor, selecciona un bloque de contenido de la biblioteca."); return
        if not self.api_key_input.text().strip(): QMessageBox.warning(self, "API Key Requerida", "Por favor, introduce tu OpenAI API Key."); return
        
        self.set_ui_enabled(False)
        content_data = selected_item.data(Qt.ItemDataRole.UserRole)
        summary = content_data['summary']

        self.generation_worker = ExamGenerationWorker(
            self.api_key_input.text().strip(),
            summary,
            int(self.num_questions_combo.currentText()),
            self.temp_spinbox.value(),
            self.top_p_spinbox.value()
        )
        self.generation_worker.progress.connect(self.update_status)
        self.generation_worker.error.connect(self.on_task_error)
        self.generation_worker.finished.connect(self.on_generation_finished)
        self.generation_worker.start()
        
    def on_generation_finished(self, questions):
        self.set_ui_enabled(True)
        self.statusBar().showMessage("Examen generado con éxito. Listo para empezar.")
        
        if not os.path.exists("exams"):
            try: os.makedirs("exams")
            except OSError as e: QMessageBox.critical(self, "Error de Directorio", f"No se pudo crear la carpeta 'exams': {e}"); return
        filename = f"exams/exam_{time.strftime('%Y%m%d-%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f: json.dump(questions, f, ensure_ascii=False, indent=4)
        except (IOError, OSError) as e:
            QMessageBox.critical(self, "Error al Guardar", f"No se pudo guardar el examen en {filename}:\n{e}")
        
        exam_dialog = ExamWindow(questions, self)
        if exam_dialog.exec(): ResultsWindow(questions, exam_dialog.user_answers, self).exec()

    def delete_selected_content(self):
        selected_item = self.content_list.currentItem()
        if not selected_item: return

        data = selected_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Confirmar Eliminación",
                                     f"¿Estás seguro de que quieres eliminar permanentemente el contenido '{data['name']}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            safe_filename = f"{int(data['created_at'])}_{''.join(filter(str.isalnum, data['name']))}.json"
            file_path = os.path.join(self.CONTENT_LIBRARY_PATH, safe_filename)
            try:
                if os.path.exists(file_path): os.remove(file_path)
                self.load_content_library()
                self.statusBar().showMessage(f"Contenido '{data['name']}' eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el archivo: {e}")

    def update_status(self, message): self.statusBar().showMessage(message)
    def on_task_error(self, message):
        self.set_ui_enabled(True)
        QMessageBox.critical(self, "Error en la Tarea", message)
        self.statusBar().showMessage("Error. La tarea fue cancelada.")

    def set_ui_enabled(self, enabled):
        self.analysis_group.setEnabled(enabled)
        # La generación solo se habilita si hay un ítem seleccionado Y la UI general está habilitada
        self.generation_group.setEnabled(enabled and self.content_list.currentItem() is not None)
        self.content_list.setEnabled(enabled)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())