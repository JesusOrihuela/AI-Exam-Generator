from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, QComboBox,
    QDoubleSpinBox, QPushButton
)
from PyQt6.QtCore import pyqtSignal


class GenerationPanel(QWidget):
    """Panel para configurar y lanzar la generación del examen."""
    request_generate = pyqtSignal()
    request_manage_bank = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        group = QGroupBox("2. Generar Examen (selecciona varios en la biblioteca con check)")
        layout = QVBoxLayout(group)

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
        self.temp_spinbox.setValue(0.90)
        config_layout.addWidget(self.temp_spinbox)

        config_layout.addWidget(QLabel("Top P:"))
        self.top_p_spinbox = QDoubleSpinBox()
        self.top_p_spinbox.setRange(0.0, 1.0)
        self.top_p_spinbox.setSingleStep(0.1)
        self.top_p_spinbox.setValue(1.0)
        config_layout.addWidget(self.top_p_spinbox)

        layout.addLayout(config_layout)

        self.generate_btn = QPushButton("Generar Examen")
        self.generate_btn.setEnabled(False)
        self.generate_btn.clicked.connect(lambda: self.request_generate.emit())
        layout.addWidget(self.generate_btn)

        self.manage_bank_btn = QPushButton("Administrar Banco de Preguntas")
        self.manage_bank_btn.clicked.connect(lambda: self.request_manage_bank.emit())
        layout.addWidget(self.manage_bank_btn)

        root = QVBoxLayout(self)
        root.addWidget(group)

    def set_generate_enabled(self, enabled: bool):
        self.generate_btn.setEnabled(enabled)

    def get_num_questions(self) -> int:
        return int(self.num_questions_combo.currentText())

    def get_temperature(self) -> float:
        return self.temp_spinbox.value()

    def get_top_p(self) -> float:
        return self.top_p_spinbox.value()
