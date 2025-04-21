import math
from operator import invert
from typing import List

import numpy as np
from PyQt6.QtCore import Qt, QPoint, QSize, QPointF
from PyQt6.QtGui import QImage, QMouseEvent, QPainter, QWheelEvent, QIcon, QPen, QColor
from PyQt6.QtWidgets import QWidget, QMessageBox

from src.drawing_algorithms.conic_sections.circle import draw_circle
from src.drawing_algorithms.conic_sections.ellipse import draw_ellipse
from src.drawing_algorithms.conic_sections.hyperbola import draw_hyperbola
from src.drawing_algorithms.conic_sections.parabola import draw_parabola
from src.drawing_algorithms.lines.bresenham import bresenham_line
from src.drawing_algorithms.lines.dda import dda_line
from src.drawing_algorithms.lines.wu import wu_line


class Canvas(QWidget):
    """Холст для рисования"""

    def __init__(self, status_bar=None, size: QSize = (200, 200)):
        super().__init__()

        # Параметры холста
        self.status_bar = status_bar
        self.image_width = size.width()
        self.image_height = size.height()

        # Масштабирование и перемещение
        self.zoom_factor = float(
            min(self.width() - int(self.width() * 0.9) / self.image_width,
                int(self.height() * 0.9) / self.image_height))
        self.offset = QPoint(0, 0)  # Смещение при перетаскивании
        self.clamp_offset()
        self.update()

        self.dragging = False
        self.last_mouse_pos = QPoint(0, 0)

        # Холст в формате RGBA
        self.canvas_pixels = np.zeros((self.image_height, self.image_width, 4), dtype=np.uint8)
        self.canvas_pixels[:, :, :3] = 255  # Белый фон
        self.canvas_pixels[:, :, 3] = 255  # Полная прозрачность

        self.image = QImage(self.canvas_pixels, self.image_width, self.image_height, QImage.Format.Format_RGBA8888)

        self.setMouseTracking(True)

        # Переменные для хранения начальных и конечных точек
        self.drawing_line = False
        self.start_point = None
        self.end_point = None

        # Хранение всех фигур
        self.objects = []

        self.algorithm = "dda"

        # Стеки для дебага
        self.in_debug = False
        self.debug_stack = []  # Удаленные линии (для "назад")
        self.redo_stack = []  # Вернутые линии (для "вперед")
        self.object_debugging = False

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
        if self.drawing_line:
            self.end_point = self.to_canvas_coords(event.pos())
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
        """Обработка нажатия мыши"""
        if event.button() == Qt.MouseButton.LeftButton and not self.in_debug:
            # Начало рисования линии
            self.drawing_line = True
            self.start_point = self.to_canvas_coords(event.pos())
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Окончание перетаскивания"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.dragging = False

        """Обработка отпускания мыши"""
        if event.button() == Qt.MouseButton.LeftButton and self.drawing_line and not self.in_debug:
            # Завершение рисования линии
            self.end_point = self.to_canvas_coords(event.pos())
            self.draw_line_on_canvas(self.start_point, self.end_point)
            self.drawing_line = False
            self.start_point = None  # Убираем начальную точку
            self.end_point = None  # Убираем конечную точку
            self.update()

    def paintEvent(self, event):
        """Рендеринг холста с временной линией, не удаляя уже нарисованные объекты"""
        painter = QPainter(self)

        # Отображаем основное изображение
        scaled_image = self.image.scaled(self.sizeHint(), Qt.AspectRatioMode.IgnoreAspectRatio)
        painter.drawImage(self.offset, scaled_image)

        # Визуализация линии между точками
        if self.start_point and self.end_point:
            pen = QPen(QColor(255, 0, 0, 128))
            pen.setWidth(2)
            painter.setPen(pen)

            screen_start = QPointF(self.start_point[0] * self.zoom_factor + self.offset.x(),
                                   self.start_point[1] * self.zoom_factor + self.offset.y())
            screen_end = QPointF(self.end_point[0] * self.zoom_factor + self.offset.x(),
                                 self.end_point[1] * self.zoom_factor + self.offset.y())

            painter.drawLine(screen_start, screen_end)  # Рисуем только временную линию

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

    def to_canvas_coords(self, pos: QPoint) -> tuple:
        """Конвертирует координаты окна в координаты холста"""
        x = int((pos.x() - self.offset.x()) / self.zoom_factor)
        y = int((pos.y() - self.offset.y()) / self.zoom_factor)
        return x, y

    def draw_line_on_canvas(self, start, end):
        """Рисует линию выбранным алгоритмом."""
        if start == end:
            self.show_alert("Start and end cannot be the same")
            return
        # Выбор алгоритма
        if self.algorithm == "wu":
            pixels = wu_line(start, end)
            self.draw_object_from_pixels(pixels)
            self.objects.append(pixels)

        elif self.algorithm == "bresenham":
            pixels = bresenham_line(start, end)
            for x, y in pixels:
                if 0 <= x < self.image_width and 0 <= y < self.image_height:
                    self.canvas_pixels[y, x] = [0, 0, 0, 255]  # Черный цвет
            pixels_with_alpha = []
            for x, y in pixels:
                pixels_with_alpha.append([x, y, 255])
            self.objects.append(pixels_with_alpha)

        elif self.algorithm == "dda":
            pixels = dda_line(start, end)
            for x, y in pixels:
                if 0 <= x < self.image_width and 0 <= y < self.image_height:
                    self.canvas_pixels[y, x] = [0, 0, 0, 255]  # Черный цвет
            pixels_with_alpha = []
            for x, y in pixels:
                pixels_with_alpha.append([x, y, 255])
            self.objects.append(pixels_with_alpha)

        elif self.algorithm == "circle":
            pixels = draw_circle(start[0], start[1],
                                 round(math.sqrt(pow(start[0] - end[0], 2) + pow(start[1] - end[1], 2))))
            for x, y in pixels:
                if 0 <= x < self.image_width and 0 <= y < self.image_height:
                    self.canvas_pixels[y, x] = [0, 0, 0, 255]  # Черный цвет
            pixels_with_alpha = []
            for x, y in pixels:
                pixels_with_alpha.append([x, y, 255])
            self.objects.append(pixels_with_alpha)

        elif self.algorithm == "ellipse":
            pixels = draw_ellipse(start, end)
            for x, y in pixels:
                if 0 <= x < self.image_width and 0 <= y < self.image_height:
                    self.canvas_pixels[y, x] = [0, 0, 0, 255]  # Черный цвет
            pixels_with_alpha = []
            for x, y in pixels:
                pixels_with_alpha.append([x, y, 255])
            self.objects.append(pixels_with_alpha)

        elif self.algorithm == "parabola":
            pixels = draw_parabola(start, end)
            for x, y in pixels:
                if 0 <= x < self.image_width and 0 <= y < self.image_height:
                    self.canvas_pixels[y, x] = [0, 0, 0, 255]  # Черный цвет
            pixels_with_alpha = []
            for x, y in pixels:
                pixels_with_alpha.append([x, y, 255])
            self.objects.append(pixels_with_alpha)

        elif self.algorithm == "hyperbola":
            if start[0] == end[0] or abs(start[0] - end[0]) < 2:
                self.show_alert("Start x and end x cannot be the same")
                return
            if start[1] == end[1]:
                self.show_alert("Start y and end y cannot be the same")
                return
            else:
                pixels = draw_hyperbola(start, end)
                for x, y in pixels:
                    if 0 <= x < self.image_width and 0 <= y < self.image_height:
                        self.canvas_pixels[y, x] = [0, 0, 0, 255]  # Черный цвет
                pixels_with_alpha = []
                for x, y in pixels:
                    pixels_with_alpha.append([x, y, 255])
                self.objects.append(pixels_with_alpha)

        self.image = QImage(self.canvas_pixels, self.image_width, self.image_height, QImage.Format.Format_RGBA8888)
        self.update()

    def set_algorithm(self, algo_name):
        """Меняет алгоритм рисования"""
        if algo_name.lower() in {"wu", "bresenham", "dda", "circle", "ellipse", "parabola", "hyperbola"}:
            self.algorithm = algo_name.lower()
            print(f"Алгоритм изменен на: {self.algorithm}")

    def redraw(self):
        self.canvas_pixels[:, :, :3] = 255  # Белый фон
        self.canvas_pixels[:, :, 3] = 255  # Полная прозрачность
        for object in self.objects:
            self.draw_object_from_pixels(object)

        self.image = QImage(self.canvas_pixels, self.image_width, self.image_height, QImage.Format.Format_RGBA8888)
        self.update()

    def draw_object_from_pixels(self, object: List):
        for x, y, alpha in object:
            if 0 <= x < self.image_width and 0 <= y < self.image_height:
                existing_color = self.canvas_pixels[y, x]

                # Альфа-композиция
                new_alpha = alpha / 255.0
                inv_alpha = 1.0 - new_alpha

                r = int(existing_color[0] * inv_alpha)
                g = int(existing_color[1] * inv_alpha)
                b = int(existing_color[2] * inv_alpha)

                self.canvas_pixels[y, x] = [
                    np.uint8(r),
                    np.uint8(g),
                    np.uint8(b),
                    np.uint8(255 * new_alpha + existing_color[3] * inv_alpha)
                ]

    def enter_debug_mode(self):
        """Удаление последней линии при входе в дебаг."""
        self.in_debug = True
        if self.objects:
            self.remove_last_object()

    def exit_debug_mode(self):
        """Возвращение удаленной линии при выходе из дебага."""
        self.in_debug = False
        self.restore_last_object()

    def remove_last_object(self):
        """Удаляет последнюю линию и добавляет в стек дебага."""
        if self.objects:
            last_object = self.objects.pop()
            self.redo_stack = last_object
            self.redraw()
            self.object_debugging = False

    def restore_last_object(self):
        """Возвращает линию из стека дебага."""
        if self.object_debugging:
            self.objects.pop()
        restored_object = self.debug_stack + self.redo_stack
        self.debug_stack = []
        self.redo_stack = []
        self.objects.append(restored_object)
        self.redraw()

    def debug_prev(self):
        """Шаг назад (удаление линии)."""
        if self.debug_stack:
            if self.object_debugging:
                self.objects.pop()
            self.redo_stack.insert(0, self.debug_stack.pop())
            restored_object = self.debug_stack
            self.objects.append(restored_object)
            self.redraw()
            self.object_debugging = True
        else:
            self.show_alert("Nothing to undo.")

    def debug_next(self):
        """Шаг вперед (возврат линии)."""
        if self.redo_stack:
            if self.object_debugging:
                self.objects.pop()
            self.debug_stack.append(self.redo_stack.pop(0))
            restored_object = self.debug_stack
            self.objects.append(restored_object)
            self.redraw()
            self.object_debugging = True
        else:
            self.show_alert("Nothing to redo.")

    def show_alert(self, message: str):
        msg = QMessageBox()
        msg.setWindowTitle("Info")
        msg.setWindowIcon(QIcon("assets/logo.png"))
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
