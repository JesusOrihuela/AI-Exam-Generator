import sys
from PyQt6.QtWidgets import QApplication
from ui.styles import DARK_STYLESHEET
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
