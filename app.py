import sys
import os
import time
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QFileDialog, QComboBox, QDoubleSpinBox, QStatusBar,
    QMessageBox, QLineEdit, QGroupBox, QInputDialog, QListWidgetItem, QSplitter
)
from PyQt6.QtGui import QFont, QColor, QPainter, QPen
from PyQt6.QtCore import Qt, QTimer, QPointF, QSize

from ui.styles import DARK_STYLESHEET
from ui.exam_window import ExamWindow
from ui.results_window import ResultsWindow
from ui.bank_window import QuestionBankWindow
from logic.worker import ProcessingWorker, ExamGenerationWorker


# =========================
# Loader circular + overlay
# =========================
class CircularSpinner(QWidget):
    """Spinner circular indeterminado dibujado con QPainter."""
    def __init__(self, parent=None, size: int = 64, line_count: int = 12, color: QColor = QColor(255, 255, 255)):
        super().__init__(parent)
        self._size = size
        self._line_count = line_count
        self._color = color
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(80)  # velocidad del giro (ms)
        self.setFixedSize(QSize(self._size, self._size))

    def _rotate(self):
        self._angle = (self._angle + 1) % self._line_count
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        center = QPointF(self.width() / 2.0, self.height() / 2.0)
        radius = min(self.width(), self.height()) / 2.0

        # Parámetros de las líneas
        line_length = radius * 0.42
        line_width = max(2, int(radius * 0.12))
        inner_radius = radius * 0.35

        for i in range(self._line_count):
            painter.save()
            painter.translate(center)
            angle = (360.0 * i) / self._line_count
            painter.rotate(angle)

            # Gradiente de alfa para crear efecto de giro
            distance = (i - self._angle) % self._line_count
            alpha = 80 + int(175 * (1.0 - (distance / self._line_count)))
            col = QColor(self._color)
            col.setAlpha(alpha)

            pen = QPen(col)
            pen.setWidth(line_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            # Dibuja una línea radial
            p1 = QPointF(0, -inner_radius)
            p2 = QPointF(0, -(inner_radius + line_length))
            painter.drawLine(p1, p2)
            painter.restore()


class LoaderOverlay(QWidget):
    """Overlay que cubre toda la ventana, con fondo semitransparente, spinner circular y texto centrado."""
    def __init__(self, parent=None, message="Procesando..."):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.SubWindow | Qt.WindowType.FramelessWindowHint)

        # Fondo más opaco (menos transparente)
        self._bg_rgba = (0, 0, 0, 180)  # (R,G,B,A) => A=180 ~ 70% opaco

        # Layout centrado
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        self.spinner = CircularSpinner(self, size=72, line_count=12, color=QColor(255, 255, 255))
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        self.label.setFont(f)
        self.label.setStyleSheet("color: white;")
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Por defecto oculto
        self.hide()

    def setMessage(self, message: str):
        self.label.setText(message)

    def resizeEvent(self, event):
        # Mantener el overlay cubriendo a su padre
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)

    def showEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
            self.raise_()
        super().showEvent(event)

    def paintEvent(self, event):
        # Pintar fondo semitransparente
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        r, g, b, a = self._bg_rgba
        painter.fillRect(self.rect(), QColor(r, g, b, a))


class MainWindow(QMainWindow):
    CONTENT_LIBRARY_PATH = "content_library"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Exámenes con IA - Gestor de Contenido")
        self.setGeometry(100, 100, 1000, 700)
        self.file_paths = []
        self.init_ui()
        self.load_content_library()
        self.loader = LoaderOverlay(self)

    # ===== Loader helpers =====
    def show_loader(self, message="Procesando..."):
        self.loader.setMessage(message)
        self.loader.setGeometry(self.rect())
        self.loader.show()
        self.loader.raise_()
        # Deshabilitar la ventana para evitar interacción
        self.setEnabled(False)

    def hide_loader(self):
        self.loader.hide()
        # Rehabilitar la ventana
        self.setEnabled(True)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # API Key
        api_layout = QHBoxLayout()
        api_label = QLabel("API Key:")
        api_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        api_layout.addWidget(api_label)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(os.getenv("OPENAI_API_KEY", ""))
        api_layout.addWidget(self.api_key_input)
        main_layout.addLayout(api_layout)

        # Splitter horizontal: izquierda (biblioteca) / derecha (acciones)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo: biblioteca
        library_widget = QWidget()
        library_layout = QVBoxLayout(library_widget)
        library_group = QGroupBox("Biblioteca de Contenido Analizado")
        library_group_layout = QVBoxLayout(library_group)
        self.content_list = QListWidget()
        self.content_list.currentItemChanged.connect(self.on_content_selected)
        library_group_layout.addWidget(self.content_list)
        delete_content_btn = QPushButton("Eliminar Contenido Seleccionado")
        delete_content_btn.clicked.connect(self.delete_selected_content)
        library_group_layout.addWidget(delete_content_btn)
        library_layout.addWidget(library_group)

        # Panel derecho: acciones, dividido verticalmente
        actions_widget = QWidget()
        actions_splitter = QSplitter(Qt.Orientation.Vertical)

        # 1. Analizar Nuevos Documentos
        self.analysis_group = QGroupBox("1. Analizar Nuevos Documentos")
        analysis_vbox = QVBoxLayout(self.analysis_group)
        self.file_list_widget = QListWidget()
        self.file_list_widget.setFixedHeight(120)
        analysis_vbox.addWidget(self.file_list_widget)
        btns = QHBoxLayout()
        add_files_btn = QPushButton("Añadir Archivos")
        add_files_btn.clicked.connect(self.add_files)
        clear_files_btn = QPushButton("Limpiar Lista")
        clear_files_btn.clicked.connect(self.clear_files)
        btns.addWidget(add_files_btn)
        btns.addWidget(clear_files_btn)
        analysis_vbox.addLayout(btns)
        self.process_btn = QPushButton("Analizar y Guardar en Biblioteca")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        analysis_vbox.addWidget(self.process_btn)

        # 2. Generar examen + banco de preguntas
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        self.generation_group = QGroupBox("2. Generar Examen")
        generation_vbox = QVBoxLayout(self.generation_group)
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("Nº Preguntas:"))
        self.num_questions_combo = QComboBox()
        self.num_questions_combo.addItems([str(i) for i in range(10, 31, 5)])
        self.num_questions_combo.setCurrentText("25")
        config_layout.addWidget(self.num_questions_combo)
        config_layout.addWidget(QLabel("Temperature:"))
        self.temp_spinbox = QDoubleSpinBox()
        self.temp_spinbox.setRange(0.0, 2.0)
        self.temp_spinbox.setSingleStep(0.1)
        self.temp_spinbox.setValue(0.90)  # default 0.90
        config_layout.addWidget(self.temp_spinbox)
        config_layout.addWidget(QLabel("Top P:"))
        self.top_p_spinbox = QDoubleSpinBox()
        self.top_p_spinbox.setRange(0.0, 1.0)
        self.top_p_spinbox.setSingleStep(0.1)
        self.top_p_spinbox.setValue(1.0)
        config_layout.addWidget(self.top_p_spinbox)
        generation_vbox.addLayout(config_layout)
        self.generate_btn = QPushButton("Generar Examen")
        self.generate_btn.clicked.connect(self.start_generation)
        self.generate_btn.setEnabled(False)
        generation_vbox.addWidget(self.generate_btn)
        bottom_layout.addWidget(self.generation_group)

        manage_bank_btn = QPushButton("Administrar Banco de Preguntas")
        manage_bank_btn.clicked.connect(lambda: QuestionBankWindow(self).exec())
        bottom_layout.addWidget(manage_bank_btn)

        # Añadir widgets al splitter vertical
        actions_splitter.addWidget(self.analysis_group)
        actions_splitter.addWidget(bottom_widget)
        actions_splitter.setSizes([300, 300])  # mitad y mitad

        # Añadir splitter al panel derecho
        actions_layout = QVBoxLayout(actions_widget)
        actions_layout.addWidget(actions_splitter)

        # Añadir al splitter principal
        splitter.addWidget(library_widget)
        splitter.addWidget(actions_widget)
        splitter.setSizes([350, 650])  # izquierda / derecha

        main_layout.addWidget(splitter)
        self.setStatusBar(QStatusBar())

    # =======================
    # Funciones auxiliares UI
    # =======================
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
                except:
                    pass

    def on_content_selected(self, current_item, _):
        self.generate_btn.setEnabled(current_item is not None)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar documentos", "", "Documentos (*.pdf *.docx *.pptx)")
        for file in files:
            if file not in self.file_paths:
                self.file_paths.append(file)
                self.file_list_widget.addItem(os.path.basename(file))
        self.process_btn.setEnabled(len(self.file_paths) > 0)

    def clear_files(self):
        self.file_paths.clear()
        self.file_list_widget.clear()
        self.process_btn.setEnabled(False)

    # =====================
    # Flujo de procesamiento
    # =====================
    def start_processing(self):
        if not self.api_key_input.text().strip():
            QMessageBox.warning(self, "API Key Requerida", "Introduce tu API Key.")
            return
        if not self.file_paths:
            QMessageBox.warning(self, "Archivos Requeridos", "Añade al menos un documento.")
            return

        self.show_loader("Analizando documentos…")
        self.set_ui_enabled(False)
        self.processing_worker = ProcessingWorker(
            self.api_key_input.text().strip(),
            self.file_paths
        )
        self.processing_worker.progress.connect(self.update_status)
        self.processing_worker.error.connect(self.on_task_error)
        self.processing_worker.finished.connect(self.on_processing_finished)
        self.processing_worker.start()

    def on_processing_finished(self, summary, filename):
        self.hide_loader()
        self.set_ui_enabled(True)

        name_suggestion = os.path.splitext(filename)[0]
        name, ok = QInputDialog.getText(
            self,
            "Guardar Contenido",
            f"Introduce un nombre para el contenido generado desde '{filename}':",
            text=name_suggestion
        )

        if ok and name:
            content_data = {
                'name': name,
                'source_files': [filename],
                'created_at': time.time(),
                'summary': summary
            }
            safe_filename = f"{int(time.time())}_{''.join(filter(str.isalnum, name))}.json"
            try:
                with open(os.path.join(self.CONTENT_LIBRARY_PATH, safe_filename), 'w', encoding='utf-8') as f:
                    json.dump(content_data, f, indent=4, ensure_ascii=False)
                self.load_content_library()
                self.statusBar().showMessage(f"Contenido '{name}' guardado en la biblioteca.")
            except Exception as e:
                QMessageBox.critical(self, "Error al Guardar", f"No se pudo guardar el archivo: {e}")
        else:
            self.statusBar().showMessage(f"Análisis de {filename} completado, pero no guardado.")

        # eliminar de lista
        for i in range(self.file_list_widget.count()):
            if self.file_list_widget.item(i).text() == os.path.basename(filename):
                self.file_list_widget.takeItem(i)
                break
        if filename in self.file_paths:
            self.file_paths.remove(filename)
        self.process_btn.setEnabled(len(self.file_paths) > 0)

    # ====================
    # Flujo de generación
    # ====================
    def start_generation(self):
        selected_item = self.content_list.currentItem()
        if not selected_item:
            return
        if not self.api_key_input.text().strip():
            QMessageBox.warning(self, "API Key Requerida", "Introduce tu API Key.")
            return

        self.show_loader("Generando examen…")
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
        self.hide_loader()
        exam_dialog = ExamWindow(questions, self)
        if exam_dialog.exec():
            ResultsWindow(questions, exam_dialog.user_answers, self).exec()

    # ==========================
    # Otras utilidades de la UI
    # ==========================
    def delete_selected_content(self):
        selected_item = self.content_list.currentItem()
        if not selected_item:
            return
        data = selected_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar permanentemente el contenido '{data['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            safe_filename = f"{int(data['created_at'])}_{''.join(filter(str.isalnum, data['name']))}.json"
            file_path = os.path.join(self.CONTENT_LIBRARY_PATH, safe_filename)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                self.load_content_library()
                self.statusBar().showMessage(f"Contenido '{data['name']}' eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")

    def update_status(self, message):
        self.statusBar().showMessage(message)

    def on_task_error(self, message):
        self.hide_loader()
        self.set_ui_enabled(True)
        QMessageBox.critical(self, "Error", message)

    def set_ui_enabled(self, enabled):
        self.analysis_group.setEnabled(enabled)
        self.generation_group.setEnabled(enabled)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
