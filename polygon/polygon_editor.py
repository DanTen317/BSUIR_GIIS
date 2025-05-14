import math

from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QPen

from src.drawing_algorithms.lines.bresenham import bresenham_line
from src.drawing_algorithms.lines.dda import dda_line
from src.drawing_algorithms.lines.wu import wu_line


class Polygon:
    def __init__(self):
        self.vertices = []
        self.hull_points = []
        self.normals = []
        self.is_closed = False


def distance(p, q):
    return math.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)


class PolygonEditor(QObject):
    polygon_finished = pyqtSignal(str)
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.polygons = []  # Список завершенных полигонов
        self.current_polygon = Polygon()  # Текущий редактируемый полигон
        self.hull_method = "Graham"
        self.line_algorithm = "CDA"
        self.drawing_mode = "Полигон"  # Добавляем режим рисования
        self.points_in_polygons = {}  # point: inside?
        self.current_line_start = None  # Начальная точка линии
        self.lines = []
        self.intersections = []  # Точки пересечения
        print("PolygonEditor: Режим построения многоугольника включён.")

    def reset_current_action(self):
        """Сбрасывает текущее действие при смене режима"""
        self.current_line_start = None
        self.current_polygon = Polygon()
        self.intersections = []

    def add_vertex(self, x, y):
        """Добавляет новую вершину в зависимости от режима"""
        if self.drawing_mode == "Полигон":
            if self.current_polygon is None:
                self.current_polygon = Polygon()
            self.current_polygon.vertices.append((x, y))
            print(f"Добавлена вершина: ({x}, {y})")
        else:  # Режим "Линия"
            if self.current_line_start is None:
                self.current_line_start = (x, y)
                print(f"Начало линии: ({x}, {y})")
            else:
                end_point = (x, y)
                print(f"Конец линии: ({x}, {y})")
                self.lines.append((self.current_line_start, end_point))
                for line in self.lines:
                    self.find_all_intersections(line[0], line[1])
                self.current_line_start = None
        self.canvas.update()

    def find_all_intersections(self, start, end):
        """Находит все точки пересечения линии со всеми полигонами"""
        self.intersections = []

        # Проверяем пересечения со всеми замкнутыми полигонами
        for i, polygon in enumerate(self.polygons):
            if polygon.is_closed:
                inters = self.segment_polygon_intersections(start, end, polygon.vertices)
                if inters:
                    for point in inters:
                        self.intersections.append((point, f"Полигон {i}"))

        # Проверяем текущий полигон, если он замкнут
        if self.current_polygon.is_closed:
            inters = self.segment_polygon_intersections(start, end, self.current_polygon.vertices)
            if inters:
                for point in inters:
                    self.intersections.append((point, "Текущий полигон"))

        # Выводим найденные точки пересечения
        if self.intersections:
            print("Найдены точки пересечения:")
            for point, polygon_id in self.intersections:
                print(f"{polygon_id}: ({point[0]:.1f}, {point[1]:.1f})")
        else:
            print("Пересечений не найдено")

    def finish_polygon(self):
        """Завершает текущий полигон и создает новый"""
        if len(self.current_polygon.vertices) < 3:
            print("Недостаточно вершин для построения многоугольника.")
            return

        self.current_polygon.is_closed = True
        is_convex = self.check_convexity()
        convex_text = "выпуклый" if is_convex else "невыпуклый"
        print(f"Многоугольник замкнут. Он {convex_text}.")
        self.polygon_finished.emit(f"Многоугольник замкнут. Он {convex_text}.")

        # Вычисляем выпуклую оболочку
        self.current_polygon.hull_points = self.build_convex_hull()

        # Вычисляем внутренние нормали
        self.calculate_internal_normals()

        # Добавляем завершенный полигон в список
        self.polygons.append(self.current_polygon)
        # Создаем новый текущий полигон
        self.current_polygon = Polygon()
        self.canvas.update()

    def check_convexity(self):
        """Проверяет выпуклость полигона"""
        n = len(self.current_polygon.vertices)
        if n < 3:
            return False

        sign = None
        for i in range(n):
            x1, y1 = self.current_polygon.vertices[i]
            x2, y2 = self.current_polygon.vertices[(i + 1) % n]
            x3, y3 = self.current_polygon.vertices[(i + 2) % n]

            dx1, dy1 = x2 - x1, y2 - y1
            dx2, dy2 = x3 - x2, y3 - y2
            cross = dx1 * dy2 - dy1 * dx2

            if cross != 0:
                current_sign = cross > 0
                if sign is None:
                    sign = current_sign
                elif sign != current_sign:
                    return False
        return True

    def build_convex_hull(self):
        if self.hull_method == "Graham":
            return self.convex_hull_graham()
        elif self.hull_method == "Jarvis":
            return self.convex_hull_jarvis()
        else:
            return []

    def convex_hull_graham(self):
        points = self.current_polygon.vertices.copy()
        n = len(points)
        if n < 3:
            return points

        # Находим точку с минимальной y (и минимальной x при равенстве)
        pivot = min(points, key=lambda p: (p[1], p[0]))

        # Сортируем по полярному углу относительно pivot
        def polar_angle(p):
            angle = math.atan2(p[1] - pivot[1], p[0] - pivot[0])
            return angle if angle >= 0 else angle + 2 * math.pi

        sorted_points = sorted(points, key=polar_angle)
        hull = [pivot, sorted_points[1]]

        for p in sorted_points[2:]:
            while len(hull) >= 2:
                x1, y1 = hull[-2]
                x2, y2 = hull[-1]
                cross = (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1)
                if cross <= 0:
                    hull.pop()
                else:
                    break
            hull.append(p)

        return hull

    def convex_hull_jarvis(self):
        points = self.current_polygon.vertices.copy()
        n = len(points)
        if n < 3:
            return points

        hull = []
        leftmost = min(points, key=lambda p: p[0])
        current = leftmost

        while True:
            hull.append(current)
            next_point = points[0]

            for candidate in points:
                if candidate == current:
                    continue

                cross = (next_point[0] - current[0]) * (candidate[1] - current[1]) - \
                        (next_point[1] - current[1]) * (candidate[0] - current[0])

                if cross < 0 or (cross == 0 and
                                 distance(current, candidate) > distance(current, next_point)):
                    next_point = candidate

            current = next_point
            if current == hull[0]:
                break

        return hull

    def check_all_points_in_polygons(self):
        """Проверяет каждую точку на принадлежность всем полигонам"""
        results = []
        points_with_status = []
        for x, y in self.points_in_polygons:
            # Проверяем точку для каждого замкнутого полигона
            for i, polygon in enumerate(self.polygons):
                if polygon.is_closed:
                    inside = self.point_in_polygon((x, y), polygon.vertices)
                    results.append(((x, y), i, inside))
            if self.current_polygon.is_closed:
                inside = self.point_in_polygon((x, y), self.current_polygon.vertices)
                results.append(((x, y), "текущий", inside))

        for (x, y), polygon_id, inside in results:
            if (x, y) not in [p[0] for p in points_with_status]:
                if any(p[0] == (x, y) and p[2] for p in results):
                    points_with_status.append(((x, y), inside))
                    self.points_in_polygons[(x, y)] = True
                    continue
                else:
                    points_with_status.append(((x, y), inside))
                    self.points_in_polygons[(x, y)] = inside
        return points_with_status

    def check_point_in_polygon(self, px, py):
        """Проверяет, находится ли точка внутри всех полигонов"""
        point = (px, py)
        results = []

        # Проверяем точку для каждого замкнутого полигона
        for i, polygon in enumerate(self.polygons):
            if polygon.is_closed:
                inside = self.point_in_polygon(point, polygon.vertices)
                results.append(((px, py), i, inside))
                if self.points_in_polygons.get(point) is not None:
                    if self.points_in_polygons.get(point) is not True:
                        self.points_in_polygons[point] = inside
                else:
                    self.points_in_polygons[point] = inside

        # Проверяем текущий полигон, если он замкнут
        if self.current_polygon.is_closed:
            inside = self.point_in_polygon(point, self.current_polygon.vertices)
            results.append(((px, py), "текущий", inside))

            if self.points_in_polygons.get(point) is not None:
                if self.points_in_polygons.get(point) is not True:
                    self.points_in_polygons[point] = inside
            else:
                self.points_in_polygons[point] = inside

        # Выводим результаты
        if not results:
            print(f"Точка ({px}, {py}) не может быть проверена: нет замкнутых полигонов")
        else:
            for (x, y), polygon_id, inside in results:
                status = "внутри" if inside else "снаружи"
                print(f"Точка ({x}, {y}) находится {status} полигона {polygon_id}")

        return results

    def point_in_polygon(self, point, vertices):
        """Реализация алгоритма ray casting для определения положения точки"""
        x, y = point
        n = len(vertices)
        inside = False

        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]

            if y2 - y1 != 0:
                if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                    inside = not inside

        return inside

    def check_segment_intersection(self, x, y):
        """Проверяет пересечение отрезка со всеми полигонами"""
        if not hasattr(self, 'segment_start'):
            self.segment_start = (x, y)
            print(f"Начало отрезка установлено в ({x}, {y})")
            return None
        else:
            self.segment_end = (x, y)
        all_intersections = []

        # Проверяем пересечения со всеми замкнутыми полигонами
        for i, polygon in enumerate(self.polygons):
            if polygon.is_closed:
                intersections = self.segment_polygon_intersections(
                    self.segment_start, self.segment_end, polygon.vertices)
                if intersections:
                    all_intersections.extend((i, pt) for pt in intersections)

        # Проверяем текущий полигон, если он замкнут
        if self.current_polygon.is_closed:
            intersections = self.segment_polygon_intersections(
                self.segment_start, self.segment_end, self.current_polygon.vertices)
            if intersections:
                all_intersections.extend(("текущий", pt) for pt in intersections)

        if all_intersections:
            print(f"Найдены точки пересечения:")
            for polygon_id, pt in all_intersections:
                print(f"Полигон {polygon_id}: ({pt[0]:.1f}, {pt[1]:.1f})")
        else:
            print("Пересечений не найдено")

        del self.segment_start
        return all_intersections

    def segment_polygon_intersections(self, seg_start, seg_end, vertices):
        """
        Находит точки пересечения отрезка со всеми рёбрами многоугольника
        """
        intersections = []
        n = len(vertices)

        # Проходим по всем рёбрам многоугольника
        for i in range(n):
            poly_start = vertices[i]
            poly_end = vertices[(i + 1) % n]

            # Проверяем пересечение с текущим ребром
            pt = self.segment_intersection(seg_start, seg_end, poly_start, poly_end)
            if pt:
                intersections.append(pt)

        return intersections

    def segment_intersection(self, p1, p2, p3, p4):
        """
        Вычисляет точку пересечения двух отрезков
        p1, p2 - концы первого отрезка
        p3, p4 - концы второго отрезка
        """
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        # Вычисляем знаменатель
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        # Если отрезки параллельны
        if abs(denom) < 1e-10:  # Используем малое число вместо точного нуля
            return None

        # Вычисляем параметры t и u
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        # Проверяем, что пересечение находится на обоих отрезках
        if 0 <= t <= 1 and 0 <= u <= 1:
            # Вычисляем точку пересечения
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            # Округляем координаты до 1 десятичного знака
            x_rounded = int(round(x, 1))
            y_rounded = int(round(y, 1))

            return (x_rounded, y_rounded)

        return None

    def calculate_internal_normals(self):
        self.current_polygon.normals = []
        n = len(self.current_polygon.vertices)
        
        # Определяем ориентацию полигона
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += (self.current_polygon.vertices[i][0] * self.current_polygon.vertices[j][1] -
                    self.current_polygon.vertices[j][0] * self.current_polygon.vertices[i][1])
        clockwise = area < 0  # True если по часовой стрелке
        
        for i in range(n):
            p1 = self.current_polygon.vertices[i]
            p2 = self.current_polygon.vertices[(i + 1) % n]

            # Вычисляем вектор ребра
            edge_x = p2[0] - p1[0]
            edge_y = p2[1] - p1[1]

            # Нормаль к ребру
            if clockwise:
                normal_x = edge_y  # Меняем знак в зависимости от ориентации
                normal_y = -edge_x
            else:
                normal_x = -edge_y
                normal_y = edge_x

            # Нормализуем вектор нормали
            length = math.sqrt(normal_x ** 2 + normal_y ** 2)
            if length > 0:
                normal_x /= length
                normal_y /= length

            # Центр ребра
            center_x = (p1[0] + p2[0]) / 2
            center_y = (p1[1] + p2[1]) / 2

            # Добавляем нормаль
            normal_length = 20
            self.current_polygon.normals.append((
                (center_x, center_y),
                (center_x + normal_x * normal_length,
                 center_y + normal_y * normal_length)
            ))

    def draw(self, painter):
        """Отрисовывает все полигоны, текущий полигон и линии"""
        # Отрисовка завершенных полигонов
        for polygon in self.polygons:
            self._draw_polygon(painter, polygon)

        # Отрисовка текущего полигона
        if self.current_polygon and self.current_polygon.vertices:
            self._draw_polygon(painter, self.current_polygon)

        # Отрисовка текущей линии
        if self.current_line_start and self.drawing_mode == "Линия":
            point_pen = QPen(Qt.GlobalColor.blue, 6)
            painter.setPen(point_pen)
            painter.drawPoint(self.current_line_start[0], self.current_line_start[1])
        for line in self.lines:
            self._draw_line(painter, line[0], line[1])

        # Отрисовка точек пересечения
        for point, _ in self.intersections:
            intersection_pen = QPen(Qt.GlobalColor.yellow, 8)
            painter.setPen(intersection_pen)
            painter.drawPoint(point[0], point[1])

        # Отрисовка остальных точек
        self.check_all_points_in_polygons()
        for point, status in self.points_in_polygons.items():
            self._draw_vertice(painter, point, status)

    def _draw_vertice(self, painter, vertice, is_inside=False, is_intersection=False):
        point_inside_pen = QPen(Qt.GlobalColor.green, 6)
        point_outside_pen = QPen(Qt.GlobalColor.red, 6)

        if is_inside:
            painter.setPen(point_inside_pen)
            painter.drawPoint(vertice[0], vertice[1])
        else:
            if is_intersection:
                pass
            else:
                painter.setPen(point_outside_pen)
                painter.drawPoint(vertice[0], vertice[1])

    def _draw_line(self, painter, start, end):
        point_pen = QPen(Qt.GlobalColor.black, 1)
        painter.setPen(point_pen)
        x1, y1 = start
        x2, y2 = end
        if self.line_algorithm == "CDA":
            # Используем алгоритм ЦДА
            pixels = dda_line((x1, y1), (x2, y2))
            for px, py in pixels:
                painter.drawPoint(px, py)
        elif self.line_algorithm == "Bresenham":
            # Используем алгоритм Брезенхема
            pixels = bresenham_line((x1, y1), (x2, y2))
            for px, py in pixels:
                painter.drawPoint(px, py)
        elif self.line_algorithm == "Wu":
            # Используем алгоритм Ву
            pixels = wu_line((x1, y1), (x2, y2))
            for x, y, alpha in pixels:
                color = painter.pen().color()
                color.setAlpha(alpha)
                painter.setPen(QPen(color, 1))
                painter.drawPoint(x, y)

    def _draw_polygon(self, painter, polygon):
        """Отрисовывает отдельный полигон"""
        # Настраиваем перо для точек
        point_pen = QPen(Qt.GlobalColor.black, 1)
        vertex_pen = QPen(Qt.GlobalColor.blue, 6)
        normal_pen = QPen(Qt.GlobalColor.red, 1)

        painter.setPen(point_pen)

        # Рисуем все точки
        for x, y in polygon.vertices:
            painter.setPen(vertex_pen)

            painter.drawPoint(x, y)

            painter.setPen(point_pen)

            # Если есть больше одной точки, рисуем линии между ними
            if len(polygon.vertices) > 1:
                line_pen = QPen(Qt.GlobalColor.black, 2)
                painter.setPen(line_pen)

                for i in range(len(polygon.vertices) - 1):
                    x1, y1 = polygon.vertices[i]
                    x2, y2 = polygon.vertices[i + 1]

                    self._draw_line(painter, (x1, y1), (x2, y2))

                # Если полигон замкнут, соединяем последнюю точку с первой
                if polygon.is_closed and len(polygon.vertices) > 2:
                    x1, y1 = polygon.vertices[-1]
                    x2, y2 = polygon.vertices[0]

                    self._draw_line(painter, (x1, y1), (x2, y2))

        # Рисуем выпуклую оболочку
        if polygon.hull_points and polygon.is_closed:
            hull_pen = QPen(Qt.GlobalColor.blue, 1)
            hull_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(hull_pen)

            for i in range(len(polygon.hull_points)):
                x1, y1 = polygon.hull_points[i]
                x2, y2 = polygon.hull_points[(i + 1) % len(polygon.hull_points)]
                painter.drawLine(x1, y1, x2, y2)

        # Рисуем нормали
        if polygon.normals:
            painter.setPen(normal_pen)

            for normal in polygon.normals:
                start, end = normal
                painter.drawLine(int(start[0]), int(start[1]),
                                 int(end[0]), int(end[1]))

    def clear(self):
        self.polygons.clear()
        self.current_polygon = Polygon()
        self.points_in_polygons = {}
        self.lines = []
        self.intersections = []
        self.canvas.update()