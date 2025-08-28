import json
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, 
                             QPushButton, QInputDialog, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import Qt

class QuestionBankWindow(QDialog):
    """Ventana para administrar el banco de preguntas (categorías y preguntas)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administrar Banco de Preguntas")
        self.setMinimumSize(800, 600)
        self.bank_file = "question_bank.json"
        self.bank_data = {}
        self.init_ui()
        self.load_bank()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        cat_layout = QVBoxLayout()
        cat_layout.addWidget(QLabel("Categorías"))
        self.category_list = QListWidget()
        self.category_list.currentItemChanged.connect(self.display_questions)
        cat_layout.addWidget(self.category_list)
        
        cat_btn_layout = QHBoxLayout()
        rename_cat_btn = QPushButton("Renombrar")
        rename_cat_btn.clicked.connect(self.rename_category)
        delete_cat_btn = QPushButton("Eliminar")
        delete_cat_btn.clicked.connect(self.delete_category)
        cat_btn_layout.addWidget(rename_cat_btn)
        cat_btn_layout.addWidget(delete_cat_btn)
        cat_layout.addLayout(cat_btn_layout)
        
        q_layout = QVBoxLayout()
        q_layout.addWidget(QLabel("Preguntas en la categoría seleccionada"))
        self.question_list = QListWidget()
        q_layout.addWidget(self.question_list)
        
        delete_q_btn = QPushButton("Eliminar Pregunta Seleccionada")
        delete_q_btn.clicked.connect(self.delete_question)
        q_layout.addWidget(delete_q_btn)

        main_layout.addLayout(cat_layout, 1)
        main_layout.addLayout(q_layout, 2)
        
    def load_bank(self):
        try:
            with open(self.bank_file, 'r', encoding='utf-8') as f:
                self.bank_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.bank_data = {}
        
        self.category_list.clear()
        self.question_list.clear()
        self.category_list.addItems(self.bank_data.keys())

    def save_bank(self):
        try:
            with open(self.bank_file, 'w', encoding='utf-8') as f:
                json.dump(self.bank_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el banco de preguntas: {e}")
            return False

    def display_questions(self, current_item, _):
        self.question_list.clear()
        if not current_item:
            return
        
        category = current_item.text()
        questions = self.bank_data.get(category, [])
        for q_data in questions:
            list_item = QListWidgetItem(q_data['pregunta'])
            list_item.setData(Qt.ItemDataRole.UserRole, q_data)
            self.question_list.addItem(list_item)
    
    def rename_category(self):
        current_item = self.category_list.currentItem()
        if not current_item: return
        
        old_name = current_item.text()
        new_name, ok = QInputDialog.getText(self, "Renombrar Categoría", "Nuevo nombre:", text=old_name)
        
        if ok and new_name and new_name != old_name and new_name not in self.bank_data:
            self.bank_data[new_name] = self.bank_data.pop(old_name)
            if self.save_bank(): self.load_bank()

    def delete_category(self):
        current_item = self.category_list.currentItem()
        if not current_item: return
            
        category = current_item.text()
        reply = QMessageBox.question(self, "Confirmar Eliminación",
                                     f"¿Estás seguro de que quieres eliminar la categoría '{category}' y todas sus preguntas?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.bank_data[category]
            if self.save_bank(): self.load_bank()

    def delete_question(self):
        cat_item = self.category_list.currentItem()
        q_item = self.question_list.currentItem()
        if not cat_item or not q_item: return

        category = cat_item.text()
        question_to_delete = q_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, "Confirmar Eliminación",
                                     "¿Estás seguro de que quieres eliminar esta pregunta?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.bank_data[category].remove(question_to_delete)
            if self.save_bank(): self.display_questions(cat_item, None)