# ui/styles.py
# --- Estilo de Grises Modernos y Profesionales ---
DARK_STYLESHEET = """
QWidget {
    background-color: #2a2a2a;
    color: #eeeeee;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QMainWindow, QDialog {
    background-color: #3f3f3f;
}

/* --- MODIFICACIÓN: Estilo para QLabel --- */
QLabel {
    background-color: transparent; /* Hace que todos los labels sean transparentes por defecto */
    padding: 2px;
}
QGroupBox > QLabel {
    background-color: transparent; /* Asegura que los labels dentro de un QGroupBox sean transparentes */
}

QPushButton {
    background-color: #5a5a5a;
    border: 1px solid #666666;
    padding: 8px 12px;
    border-radius: 4px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #6b6b6b;
}
QPushButton:pressed {
    background-color: #7c7c7c;
    border-color: #007acc;
}
QPushButton:disabled {
    background-color: #3a3a3a;
    border-color: #505050;
    color: #999999;
}

QLineEdit, QListWidget, QComboBox, QDoubleSpinBox {
    background-color: #303030;
    border: 1px solid #505050;
    padding: 6px;
    border-radius: 4px;
    selection-background-color: #007acc;
}

QListWidget::item {
    padding: 5px;
}
QListWidget::item:hover {
    background-color: #505050;
}
QListWidget::item:selected {
    background-color: #007acc;
    color: white;
}

QStatusBar {
    background-color: #333333;
    padding: 3px;
    border-top: 1px solid #666666;
}

QGroupBox {
    border: 1px solid #666666;
    border-radius: 5px;
    margin-top: 15px;
    padding: 10px;
    background-color: #3f3f3f;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    font-size: 11pt;
    font-weight: bold;
    background-color: #3f3f3f;
    margin-left: 5px;
}

QRadioButton {
    spacing: 5px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 1px solid #666666;
    background-color: #303030;
}
QRadioButton::indicator:hover {
    border-color: #007acc;
}
QRadioButton::indicator:checked {
    background-color: #007acc;
    border: 2px solid #eeeeee;
}

QScrollArea {
    border: 1px solid #666666;
    border-radius: 4px;
}
QScrollBar:vertical, QScrollBar:horizontal {
    border: none;
    background: #2a2a2a;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #5a5a5a;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line, QScrollBar::sub-line {
    height: 0px;
    width: 0px;
    background: none;
}
QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}

QSplitter::handle {
    background-color: #666666;
}
QSplitter::handle:hover {
    background-color: #007acc;
}
QSplitter::handle:horizontal {
    width: 1px;
}
"""