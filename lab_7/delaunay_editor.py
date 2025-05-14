from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QObject
from PyQt6.QtGui import QColor
import math

from .delaunay_triangulation import DelaunayTriangulation, Point


class DelaunayEditor(QObject):
    polygon_finished = pyqtSignal(str)

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.delaunay = DelaunayTriangulation()
        self.points = []
        self.debug_mode = False
        self.debug_step_ready = True
        self.selected_point = None
        self.point_radius = 5
        self.line_width = 1
        self.point_color = QColor(0, 0, 255)  # Синий
        self.edge_color = QColor(255, 0, 0)  # Красный
        self.triangle_color = QColor(0, 255, 0, 50)  # Полупрозрачный зеленый
        self.debug_color = QColor(255, 165, 0)  # Оранжевый для отладочной информации

    def reset(self):
        """Сбрасывает редактор к начальному состоянию"""
        self.delaunay= DelaunayTriangulation()
        self.points = []
        self.selected_point = None
        self.debug_step_ready = True
        self.canvas.update()

    def add_point(self, x, y):
        """Добавляет точку в триангуляцию"""
        if self.delaunay.add_point(x, y):
            self.points.append((x, y))
            self.canvas.update()

    def toggle_debug_mode(self, enabled):
        """Включает/выключает режим отладки"""
        self.debug_mode = enabled
        if enabled:
            self.delaunay.reset_debug()
            self.debug_step_ready = True
        self.canvas.update()

    def next_debug_step(self):
        """Переходит к следующему шагу в режиме отладки"""
        if self.debug_mode and self.debug_step_ready:
            self.delaunay.next_debug_step()
            self.canvas.update()

    def clear(self):
        """Очищает редактор"""
        self.reset()

    def draw(self, painter):
        """Отрисовка всех элементов триангуляции"""
        # Рисуем треугольники
        if not self.debug_mode:
            for triangle in self.delaunay.triangles:
                self._draw_triangle(painter, triangle)

            # Рисуем рёбра
            for edge in self.delaunay.edges:
                self._draw_edge(painter, edge)
        else:
            # В режиме отладки показываем текущий шаг
            debug_info = self.delaunay.get_debug_step()

            # Рисуем уже созданные треугольники (не из "плохих")
            for triangle in self.delaunay.triangles:
                if triangle not in debug_info["bad_triangles"]:
                    self._draw_triangle(painter, triangle)

                    # Рисуем рёбра этих треугольников
                    for edge in triangle.edges:
                        self._draw_edge(painter, edge)

            # Рисуем "плохие" треугольники полупрозрачным красным цветом
            for triangle in debug_info["bad_triangles"]:
                self._draw_triangle(painter, triangle, QColor(255, 0, 0, 50))

                # Рисуем рёбра "плохих" треугольников пунктиром
                for edge in triangle.edges:
                    self._draw_edge(painter, edge, QColor(255, 0, 0), True)

            # Рисуем граничные рёбра текущего шага
            for edge in debug_info["boundary"]:
                self._draw_edge(painter, edge, self.debug_color, False, 2)

            # Рисуем новые треугольники другим цветом
            for triangle in debug_info["new_triangles"]:
                self._draw_triangle(painter, triangle, QColor(0, 255, 0, 80))

                # Рисуем рёбра новых треугольников
                for edge in triangle.edges:
                    self._draw_edge(painter, edge, QColor(0, 150, 0))

            # Рисуем текущую точку увеличенным размером
            if debug_info["current_point"]:
                point = debug_info["current_point"]
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(255, 165, 0))
                painter.drawEllipse(int(point.x - self.point_radius * 1.5),
                                    int(point.y - self.point_radius * 1.5),
                                    int(self.point_radius * 3),
                                    int(self.point_radius * 3))

                # Рисуем окружности для "плохих" треугольников
                for triangle in debug_info["bad_triangles"]:
                    center = triangle.circumcenter()
                    radius = triangle.circumradius()
                    painter.setPen(QColor(255, 0, 0, 100))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawEllipse(int(center.x - radius),
                                        int(center.y - radius),
                                        int(radius * 2),
                                        int(radius * 2))

        # Рисуем все точки
        for point in self.delaunay.points:
            self._draw_point(painter, point)

    def _draw_point(self, painter, point, color=None):
        """Рисует точку"""
        if color is None:
            color = self.point_color

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(int(point.x - self.point_radius),
                            int(point.y - self.point_radius),
                            int(self.point_radius * 2),
                            int(self.point_radius * 2))

    def _draw_edge(self, painter, edge, color=None, dashed=False, width=None):
        """Рисует ребро"""
        if color is None:
            color = self.edge_color

        if width is None:
            width = self.line_width

        pen = painter.pen()
        pen.setColor(color)
        pen.setWidth(width)

        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(int(edge.p1.x), int(edge.p1.y), int(edge.p2.x), int(edge.p2.y))

    def _draw_triangle(self, painter, triangle, color=None):
        """Рисует треугольник"""
        if color is None:
            color = self.triangle_color

        points = [(v.x, v.y) for v in triangle.vertices]

        # Создаем многоугольник (треугольник)
        polygon = []
        for x, y in points:
            polygon.append((int(x), int(y)))

        # Рисуем заливку треугольника
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)

        # Преобразуем точки в QPoint
        qt_points = [QPoint(x, y) for x, y in polygon]
        painter.drawPolygon(qt_points)