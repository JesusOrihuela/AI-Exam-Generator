import json
import time
from fpdf import FPDF, HTMLMixin
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget,
    QGroupBox, QPushButton, QMessageBox, QInputDialog, QFileDialog, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


# --- Rutas de fuentes ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'assets', 'fonts')
CUSTOM_FONT_REGULAR = os.path.join(FONTS_DIR, 'DejaVuSansCondensed.ttf')
CUSTOM_FONT_BOLD = os.path.join(FONTS_DIR, 'DejaVuSansCondensed-Bold.ttf')
CUSTOM_FONT_NAME = 'DejaVu'


class PDF(FPDF, HTMLMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if not os.path.exists(CUSTOM_FONT_REGULAR):
                raise FileNotFoundError(f"Fuente regular no encontrada: {CUSTOM_FONT_REGULAR}")
            if not os.path.exists(CUSTOM_FONT_BOLD):
                raise FileNotFoundError(f"Fuente bold no encontrada: {CUSTOM_FONT_BOLD}")

            self.add_font(CUSTOM_FONT_NAME, '', CUSTOM_FONT_REGULAR, uni=True)
            self.add_font(CUSTOM_FONT_NAME, 'B', CUSTOM_FONT_BOLD, uni=True)
        except Exception as e:
            print(f"Advertencia: no se pudo cargar la fuente {CUSTOM_FONT_NAME}. Usando Arial. Error: {e}")
            self.set_font("Arial", '', 10)
            return

        self.set_font(CUSTOM_FONT_NAME, '', 10)
        self.set_doc_option('core_fonts_encoding', 'utf-8')

    def header(self):
        self.set_font(CUSTOM_FONT_NAME if hasattr(self, '_fonts') and CUSTOM_FONT_NAME in self._fonts else 'Arial', 'B', 15)
        self.set_x(self.l_margin)
        self.cell(self.w - 2 * self.l_margin, 10, 'Resultados del Examen', 0, 1, 'C')
        self.ln(5)

    # Sin footer → no números de página


class AutoWidthScrollArea(QScrollArea):
    """
    QScrollArea que ajusta el ancho del widget interno al ancho del viewport,
    permitiendo que los hijos (QGroupBox) se expandan horizontalmente y
    crezcan verticalmente según su contenido.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.widget()
        if w is not None:
            # Igualar el ancho del contenido al ancho visible (viewport)
            # dejando que la altura la determine el layout por el contenido.
            w.setFixedWidth(self.viewport().width())


class ResultsWindow(QDialog):
    """Ventana que muestra los resultados detallados del examen."""
    def __init__(self, questions, user_answers, parent=None):
        super().__init__(parent)
        self.questions = questions
        self.user_answers = user_answers
        self.setWindowTitle("Resultados del Examen")
        self.setMinimumSize(900, 700)
        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout(self)

        score, total = self.calculate_score()
        title_label = QLabel(f"Calificación Final: {score}/{total} ({score/total:.2%})")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        root.addWidget(title_label)

        # Scroll responsive
        self.scroll = AutoWidthScrollArea()
        scroll_content = QWidget()
        self.results_layout = QVBoxLayout(scroll_content)
        self.results_layout.setContentsMargins(8, 8, 8, 8)
        self.results_layout.setSpacing(12)
        self.scroll.setWidget(scroll_content)
        root.addWidget(self.scroll, stretch=1)

        self.display_results()

        # Acciones
        action_layout = QHBoxLayout()
        pdf_button = QPushButton("Descargar Resultados (PDF)")
        pdf_button.clicked.connect(self.download_pdf)
        action_layout.addWidget(pdf_button)
        action_layout.addStretch()
        root.addLayout(action_layout)

    def calculate_score(self):
        score = sum(1 for i, q in enumerate(self.questions) if self.user_answers.get(i) == q['respuesta_correcta'])
        return score, len(self.questions)

    def display_results(self):
        # Limpiar por si se reusa
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        for i, q in enumerate(self.questions):
            group_box = QGroupBox(f"Pregunta {i+1}")
            # EXPANDING horizontal (para ocupar todo el ancho disponible),
            # PREFERRED vertical (deja que la altura la determine el contenido).
            group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

            group_layout = QVBoxLayout(group_box)
            group_layout.setContentsMargins(12, 12, 12, 12)
            group_layout.setSpacing(6)

            # Pregunta
            lbl_q = QLabel(f"<b>Pregunta:</b> {q['pregunta']}")
            lbl_q.setWordWrap(True)
            lbl_q.setTextFormat(Qt.TextFormat.RichText)
            lbl_q.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            group_layout.addWidget(lbl_q)

            # Tu respuesta
            user_answer = self.user_answers.get(i, "No respondida")
            is_correct = user_answer == q['respuesta_correcta']
            color = "green" if is_correct else "red"
            lbl_user = QLabel(f"<b>Tu respuesta:</b> {user_answer}")
            lbl_user.setStyleSheet(f"color: {color};")
            lbl_user.setWordWrap(True)
            lbl_user.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            group_layout.addWidget(lbl_user)

            # Respuesta correcta
            lbl_correct = QLabel(f"<b>Respuesta correcta:</b> {q['respuesta_correcta']}")
            lbl_correct.setWordWrap(True)
            lbl_correct.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            group_layout.addWidget(lbl_correct)

            # Justificación
            lbl_just = QLabel(f"<b>Justificación:</b> {q['justificacion']}")
            lbl_just.setWordWrap(True)
            lbl_just.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            group_layout.addWidget(lbl_just)

            # Botones
            btn_layout = QHBoxLayout()
            save_btn = QPushButton("Guardar en Banco")
            save_btn.clicked.connect(lambda _, q_data=q: self.save_to_bank(q_data))
            report_btn = QPushButton("Reportar Pregunta")
            report_btn.clicked.connect(lambda _, q_idx=i: self.report_question(q_idx))
            btn_layout.addStretch()
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(report_btn)
            group_layout.addLayout(btn_layout)

            self.results_layout.addWidget(group_box)

        # Un stretch final para que el último bloque no quede pegado
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.results_layout.addWidget(spacer)

        # Forzar un primer ajuste del ancho del contenido al viewport
        self.scroll.resizeEvent(None)

    def save_to_bank(self, question_data):
        bank_file = "question_bank.json"
        try:
            with open(bank_file, 'r', encoding='utf-8') as f:
                bank = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            bank = {}

        categories = list(bank.keys())
        category, ok = QInputDialog.getItem(self, "Guardar Pregunta", "Selecciona o crea una categoría:", categories, 0, True)

        if ok and category:
            if category not in bank:
                bank[category] = []
            if question_data not in bank[category]:
                bank[category].append(question_data)
                try:
                    with open(bank_file, 'w', encoding='utf-8') as f:
                        json.dump(bank, f, indent=4, ensure_ascii=False)
                    QMessageBox.information(self, "Éxito", f"Pregunta guardada en '{category}'.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo guardar el banco de preguntas: {e}")
            else:
                QMessageBox.information(self, "Información", "Esta pregunta ya existe en la categoría.")

    def report_question(self, question_index):
        report_data = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "question_details": self.questions[question_index]}
        try:
            with open("reported_questions.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(report_data, ensure_ascii=False) + "\n")
            QMessageBox.information(self, "Pregunta Reportada", "Gracias. Tu reporte ha sido guardado para revisión.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar el reporte: {e}")

    def download_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_left_margin(20)
        pdf.set_right_margin(20)

        pdf.set_font(CUSTOM_FONT_NAME, '', 10)

        score, total = self.calculate_score()
        pdf.set_font(CUSTOM_FONT_NAME, 'B', 16)

        pdf.set_x(pdf.l_margin)
        pdf.cell(pdf.w - pdf.l_margin - pdf.r_margin, 10,
                 f"Calificación Final: {score}/{total} ({score/total:.2%})", 0, 1, 'C')
        pdf.ln(10)

        for i, q in enumerate(self.questions):
            pdf.set_x(pdf.l_margin)

            # Pregunta
            pdf.set_font(CUSTOM_FONT_NAME, 'B', 12)
            content_width = pdf.w - pdf.l_margin - pdf.r_margin
            pdf.multi_cell(content_width, 7, f"Pregunta {i+1}: {q['pregunta']}")
            pdf.ln(2)

            pdf.set_x(pdf.l_margin)
            user_answer = self.user_answers.get(i, "No respondida")
            is_correct = user_answer == q['respuesta_correcta']

            # Tu respuesta
            pdf.set_font(CUSTOM_FONT_NAME, '', 10)
            if is_correct:
                pdf.set_text_color(0, 128, 0)
                pdf.multi_cell(content_width, 6, f"Tu respuesta: {user_answer}")
            else:
                pdf.set_text_color(255, 0, 0)
                pdf.multi_cell(content_width, 6, f"Tu respuesta: {user_answer}")

            pdf.set_x(pdf.l_margin)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(content_width, 6, f"Respuesta correcta: {q['respuesta_correcta']}")

            pdf.set_x(pdf.l_margin)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font(CUSTOM_FONT_NAME, '', 10)
            pdf.multi_cell(content_width, 6, f"Justificación: {q['justificacion']}")
            pdf.ln(10)

        try:
            pdf.output(path)
            QMessageBox.information(self, "Éxito", f"Resultados guardados en {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el PDF: {e}\n\n"
                                                f"Si el problema persiste, intente usar otro nombre o carpeta.")
