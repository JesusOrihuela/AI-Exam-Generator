from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, 
                             QRadioButton, QButtonGroup, QPushButton, QMessageBox)
from PyQt6.QtGui import QFont

class ExamWindow(QDialog):
    """Ventana donde el usuario realiza el examen interactivamente."""
    def __init__(self, questions, parent=None):
        super().__init__(parent)
        self.questions = questions
        self.user_answers = {}
        self.current_question_index = 0
        self.setWindowTitle("Examen Interactivo")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_question()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.question_label)

        self.options_group_box = QGroupBox("Opciones")
        self.options_layout = QVBoxLayout(self.options_group_box)
        self.button_group = QButtonGroup()
        self.radio_buttons = []
        for i in range(3):
            rb = QRadioButton()
            self.radio_buttons.append(rb)
            self.options_layout.addWidget(rb)
            self.button_group.addButton(rb, i)
        
        self.button_group.idClicked.connect(self.save_answer)
        self.layout.addWidget(self.options_group_box)
        self.layout.addStretch()

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Anterior")
        self.prev_button.clicked.connect(self.prev_question)
        self.next_button = QPushButton("Siguiente")
        self.next_button.clicked.connect(self.next_question)
        self.finish_button = QPushButton("Finalizar Examen")
        self.finish_button.clicked.connect(self.finish_exam)
        self.progress_label = QLabel()
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.progress_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.finish_button)
        self.layout.addLayout(nav_layout)
        
    def load_question(self):
        checked_button = self.button_group.checkedButton()
        if checked_button:
            self.button_group.setExclusive(False)
            checked_button.setChecked(False)
            self.button_group.setExclusive(True)

        question_data = self.questions[self.current_question_index]
        self.question_label.setText(f"Pregunta {self.current_question_index + 1}: {question_data['pregunta']}")
        
        options = question_data.get('opciones', [])
        for i, rb in enumerate(self.radio_buttons):
            if i < len(options):
                rb.setText(options[i]); rb.show()
            else:
                rb.hide()
        
        if self.current_question_index in self.user_answers:
            answer_text = self.user_answers[self.current_question_index]
            for i, option_text in enumerate(options):
                if option_text == answer_text: self.radio_buttons[i].setChecked(True)
        
        self.update_navigation()

    def save_answer(self, button_id):
        self.user_answers[self.current_question_index] = self.button_group.button(button_id).text()

    def next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_question()

    def prev_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_question()
            
    def update_navigation(self):
        self.prev_button.setEnabled(self.current_question_index > 0)
        self.next_button.setEnabled(self.current_question_index < len(self.questions) - 1)
        self.progress_label.setText(f"Pregunta {self.current_question_index + 1}/{len(self.questions)}")

    def finish_exam(self):
        unanswered = len(self.questions) - len(self.user_answers)
        if unanswered > 0:
            reply = QMessageBox.question(self, "Finalizar Examen",
                                         f"Tienes {unanswered} pregunta(s) sin responder. ¿Seguro?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        self.accept()