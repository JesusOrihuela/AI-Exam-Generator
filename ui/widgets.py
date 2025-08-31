# ui/widgets.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtGui import QFont, QColor, QPainter, QPen
from PyQt6.QtCore import Qt, QTimer, QPointF, QSize


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

        self._bg_rgba = (0, 0, 0, 180)  # fondo ~70% opaco

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

        self.hide()

    def setMessage(self, message: str):
        self.label.setText(message)

    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)

    def showEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
            self.raise_()
        super().showEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        r, g, b, a = self._bg_rgba
        painter.fillRect(self.rect(), QColor(r, g, b, a))


class AutoWidthScrollArea(QScrollArea):
    """
    QScrollArea que ajusta el ancho del widget interno al ancho del viewport,
    permitiendo que los hijos se expandan horizontalmente y crezcan verticalmente
    según su contenido.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.widget()
        if w is not None:
            w.setFixedWidth(self.viewport().width())
