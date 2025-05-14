from PyQt6.QtWidgets import QWidget, QStatusBar
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt, QPoint
from polygon_editor import PolygonEditor


class CanvasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.editor = PolygonEditor(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Рисуем белый фон
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        
        # Вызываем метод отрисовки редактора
        self.editor.draw(painter)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.add_vertex(event.pos().x(), event.pos().y())
        elif event.button() == Qt.MouseButton.RightButton:
            self.editor.check_point_in_polygon(event.pos().x(), event.pos().y())
        self.update()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.editor.finish_polygon()

    def clear(self):
        self.editor.clear()