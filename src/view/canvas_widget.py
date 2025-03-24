import numpy as np
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QImage, QColor, QMouseEvent, QPainter, QWheelEvent
from PyQt6.QtWidgets import QWidget, QScrollArea


class Canvas(QWidget):
    """Холст для рисования"""

    def __init__(self, status_bar=None, size: QSize = (200, 200)):
        super().__init__()

        # Параметры холста
        self.status_bar = status_bar
        self.image_width = size.width()
        self.image_height = size.height()

        # Масштабирование и перемещение
        self.zoom_factor = 1.0
        self.offset = QPoint(0, 0)  # Смещение при перетаскивании
        self.clamp_offset()
        self.update()

        self.dragging = False
        self.last_mouse_pos = QPoint(0, 0)

        # Создаем массив пикселей и QImage
        self.pixels = np.zeros((self.image_height, self.image_width, 4), dtype=np.uint8)
        self.pixels[:, :, :3] = 255  # Белый фон
        self.pixels[:, :, 3] = 255  # Альфа-канал
        self.image = QImage(self.pixels, self.image_width, self.image_height, QImage.Format.Format_RGBA8888)

        self.setMouseTracking(True)

    def sizeHint(self):
        """Размер холста с учетом масштаба"""
        return QSize(int(self.image_width * self.zoom_factor), int(self.image_height * self.zoom_factor))

    def clamp_offset(self, margin=200):
        """Ограничение смещения, позволяющее немного выходить за границы"""

        viewport_width = self.width()
        viewport_height = self.height()

        canvas_width = self.sizeHint().width()
        canvas_height = self.sizeHint().height()

        # Добавляем отступ (margin), чтобы можно было выйти за границы
        max_x = margin
        max_y = margin

        # Если холст больше окна — можно двигать свободно
        min_x = viewport_width - canvas_width - margin
        min_y = viewport_height - canvas_height - margin

        # Если холст меньше окна — ограничение по краям
        if canvas_width < viewport_width:
            min_x = max_x = (viewport_width - canvas_width) // 2

        if canvas_height < viewport_height:
            min_y = max_y = (viewport_height - canvas_height) // 2

        # Применяем ограничения
        self.offset.setX(max(min_x, min(self.offset.x(), max_x)))
        self.offset.setY(max(min_y, min(self.offset.y(), max_y)))

    def mouseMoveEvent(self, event: QMouseEvent):
        """Обработка движения мыши"""
        if self.dragging:
            # Перемещение холста
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()

            # Изменение смещения
            self.offset += delta
            self.clamp_offset()  # Ограничение выхода за края
            self.update()

        # Координаты с учетом масштаба
        x = int((event.position().x() - self.offset.x()) / self.zoom_factor)
        y = int((event.position().y() - self.offset.y()) / self.zoom_factor)

        try:
            if 0 <= x < self.image_width and 0 <= y < self.image_height:
                self.status_bar.showMessage(f"X: {x}, Y: {y}")
        finally:
            pass

    def mousePressEvent(self, event: QMouseEvent):
        """Начало перетаскивания"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.dragging = True
            self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Окончание перетаскивания"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.dragging = False

    def paintEvent(self, event):
        """Рендеринг холста"""
        painter = QPainter(self)

        # Масштабирование изображения
        scaled_image = self.image.scaled(self.sizeHint(), Qt.AspectRatioMode.IgnoreAspectRatio)

        # Отрисовка изображения с учетом смещения
        painter.drawImage(self.offset, scaled_image)

    def wheelEvent(self, event: QWheelEvent):
        """Масштабирование с помощью колесика"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Центрирование на точке курсора
            cursor_pos = event.position().toPoint()

            # Пересчет координат до масштабирования
            cursor_x = (cursor_pos.x() - self.offset.x()) / self.zoom_factor
            cursor_y = (cursor_pos.y() - self.offset.y()) / self.zoom_factor

            # Масштабирование
            factor = 1.2 if event.angleDelta().y() > 0 else 0.8
            self.zoom_factor *= factor
            self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))

            # Корректировка смещения, чтобы масштабирование было центрировано на курсоре
            new_x = int(cursor_x * self.zoom_factor - cursor_pos.x())
            new_y = int(cursor_y * self.zoom_factor - cursor_pos.y())
            self.offset = QPoint(-new_x, -new_y)

            # Ограничение выхода за края
            self.clamp_offset()

            # Обновление размеров для QScrollArea
            self.updateGeometry()
            self.update()

    def resizeEvent(self, a0):
        self.clamp_offset()
        self.update()
