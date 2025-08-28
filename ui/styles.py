# ui/styles.py
# --- Estilo de Grises Modernos y Profesionales ---
DARK_STYLESHEET = """
/* Colores de la paleta */
/* Gris oscuro de fondo principal */
@define FONT_COLOR_PRIMARY: #2e2e2e; /* Gris casi negro para texto principal */
@define FONT_COLOR_SECONDARY: #555555; /* Gris más claro para texto secundario */
@define BACKGROUND_DARK: #2a2a2a; /* Fondo más oscuro para elementos clave */
@define BACKGROUND_MEDIUM: #3f3f3f; /* Fondo intermedio para grupos y paneles */
@define BACKGROUND_LIGHT: #505050; /* Fondo ligeramente más claro para resaltar */
@define BORDER_COLOR: #666666; /* Bordes sutiles */
@define BUTTON_BG_NORMAL: #5a5a5a; /* Fondo de botón normal */
@define BUTTON_BG_HOVER: #6b6b6b; /* Fondo de botón al pasar el ratón */
@define BUTTON_BG_PRESSED: #7c7c7c; /* Fondo de botón al pulsar */
@define HIGHLIGHT_COLOR: #007acc; /* Azul para selecciones y realces */
@define TEXT_COLOR: #eeeeee; /* Texto general, un gris muy claro */
@define TEXT_INPUT_BG: #303030; /* Fondo de campos de entrada más oscuro */
@define TEXT_INPUT_BORDER: #505050; /* Borde de campos de entrada */
@define STATUS_BAR_BG: #333333; /* Fondo de barra de estado */

/* Estilos de widgets generales */
QWidget {
    background-color: @BACKGROUND_DARK;
    color: @TEXT_COLOR;
    font-family: 'Segoe UI', Arial, sans-serif; /* Fuente más moderna para Windows */
    font-size: 11pt;
}

QMainWindow, QDialog {
    background-color: @BACKGROUND_MEDIUM;
    border: 1px solid @BORDER_COLOR;
    border-radius: 5px; /* Bordes redondeados sutiles */
}

/* Botones */
QPushButton {
    background-color: @BUTTON_BG_NORMAL;
    border: 1px solid @BORDER_COLOR;
    padding: 10px 15px; /* Más padding para un look moderno */
    border-radius: 5px;
    color: @TEXT_COLOR;
    font-weight: 500;
}
QPushButton:hover {
    background-color: @BUTTON_BG_HOVER;
}
QPushButton:pressed {
    background-color: @BUTTON_BG_PRESSED;
    border-color: @HIGHLIGHT_COLOR; /* Resaltar al presionar */
}
QPushButton:disabled {
    background-color: #3a3a3a;
    border-color: #505050;
    color: #999999;
}

/* Campos de entrada de texto, listas desplegables, spinboxes */
QLineEdit, QListWidget, QComboBox, QDoubleSpinBox {
    background-color: @TEXT_INPUT_BG;
    border: 1px solid @TEXT_INPUT_BORDER;
    padding: 8px; /* Más padding */
    border-radius: 4px;
    color: @TEXT_COLOR;
    selection-background-color: @HIGHLIGHT_COLOR; /* Color de selección */
}

/* Listas (QListWidget) */
QListWidget::item {
    padding: 5px;
}
QListWidget::item:hover {
    background-color: @BACKGROUND_LIGHT;
}
QListWidget::item:selected {
    background-color: @HIGHLIGHT_COLOR;
    color: white;
}

/* Barras de estado */
QStatusBar {
    background-color: @STATUS_BAR_BG;
    color: @TEXT_COLOR;
    font-size: 10pt;
    padding: 3px;
    border-top: 1px solid @BORDER_COLOR;
}

/* Grupos (QGroupBox) */
QGroupBox {
    border: 1px solid @BORDER_COLOR;
    border-radius: 5px;
    margin-top: 20px; /* Espacio para el título */
    padding-top: 10px;
    background-color: @BACKGROUND_MEDIUM;
    color: @TEXT_COLOR;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px; /* Padding alrededor del título */
    color: @TEXT_COLOR;
    font-size: 12pt;
    background-color: @BACKGROUND_MEDIUM; /* Fondo para que el título no se mezcle */
    margin-left: 5px;
}

/* Radio Buttons */
QRadioButton {
    spacing: 5px;
    color: @TEXT_COLOR;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px; /* Hacerlos circulares */
    border: 1px solid @BORDER_COLOR;
    background-color: @TEXT_INPUT_BG;
}
QRadioButton::indicator:hover {
    border-color: @HIGHLIGHT_COLOR;
}
QRadioButton::indicator:checked {
    background-color: @HIGHLIGHT_COLOR;
    border: 2px solid @TEXT_COLOR; /* Borde interior blanco */
}
QRadioButton::indicator:checked:hover {
    border-color: @HIGHLIGHT_COLOR;
}

/* Scroll Areas */
QScrollArea {
    border: 1px solid @BORDER_COLOR;
    border-radius: 4px;
}
QScrollBar:vertical, QScrollBar:horizontal {
    border: 1px solid @BORDER_COLOR;
    background: @BACKGROUND_DARK;
    width: 10px;
    margin: 0px 0px 0px 0px;
    border-radius: 5px;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: @BUTTON_BG_NORMAL;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    height: 0px;
    width: 0px;
    background: none;
}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
    background: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* Splitter (divisores) */
QSplitter::handle {
    background-color: @BORDER_COLOR;
    border: 1px solid @BACKGROUND_DARK;
}
QSplitter::handle:hover {
    background-color: @HIGHLIGHT_COLOR;
}
QSplitter::handle:vertical {
    height: 3px;
}
QSplitter::handle:horizontal {
    width: 3px;
}
"""