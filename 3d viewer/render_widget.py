from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen
import numpy as np
import math


class RenderWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.main_window = main_window

        # Инициализация параметров
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        self.scale = 1.0
        self.distance = 5.0
        self.translate_x = 0
        self.translate_y = 0
        self.translate_z = 0

        self.vertices = np.array([])
        self.faces = np.array([])
        
        # параметры для отслеживания мыши
        self.last_pos = None
        self.mouse_pressed = False

        self.setMouseTracking(True)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.movement_step = 0.1

    def load_object(self, filename):
        vertices = []
        faces = []

        try:
            with open(filename, 'r') as file:
                reading_faces = False
                for line in file:
                    if line.startswith("#") or line.strip() == "":
                        reading_faces = True
                        continue

                    parts = line.strip().split()
                    if reading_faces:
                        faces.append(list(map(int, parts)))
                    else:
                        vertices.append(list(map(float, parts)))

            self.vertices = np.array(vertices)
            self.faces = np.array(faces)
            self.update()

        except Exception as e:
            print(f"Ошибка загрузки 3D объекта: {e}")

    def paintEvent(self, event):
        if self.vertices.size == 0 or self.faces.size == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Настройка пера
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        painter.setPen(pen)

        # Матрицы преобразования
        rx = self.rotation_matrix_x()
        ry = self.rotation_matrix_y()
        rz = self.rotation_matrix_z()

        # Применяем преобразования
        transform = np.dot(rx, ry)
        transform = np.dot(transform, rz)
        transform = np.dot(transform, self.scale_matrix())
        transform = np.dot(self.translation_matrix(), transform)

        # Преобразуем вершины
        transformed = self.transform(transform)

        # Проецируем на экран
        projected = self.project(transformed)

        # Рисуем грани
        for face in self.faces:
            points = [projected[i] for i in face]
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                painter.drawLine(int(p1[0]), int(p1[1]),
                                 int(p2[0]), int(p2[1]))

    def transform(self, matrix):
        if self.vertices.size == 0:
            return self.vertices

        vertices = np.hstack((self.vertices, np.ones((len(self.vertices), 1))))
        return np.dot(vertices, matrix.T)[:, :3]

    def project(self, vertices):
        # Проекция точек на экран
        projected = np.array([
            [x / (max(z + self.distance, 0.0001)), y / (max(z + self.distance, 0.0001))]
            for x, y, z in vertices
        ])

        # Масштабирование и центрирование
        projected *= 200
        projected += np.array([self.width() / 2, self.height() / 2])
        return projected

    # Методы для установки параметров
    def set_rotation_x(self, value):
        self.angle_x = math.radians(value)
        self.update()

    def set_rotation_y(self, value):
        self.angle_y = math.radians(value)
        self.update()

    def set_rotation_z(self, value):
        self.angle_z = math.radians(value)
        self.update()

    def set_scale(self, value):
        self.scale = value / 100.0
        self.update()

    def set_distance(self, value):
        self.distance = value / 100.0
        self.update()

    def set_translate_x(self, value):
        self.translate_x = value / 100.0
        self.update()

    def set_translate_y(self, value):
        self.translate_y = value / 100.0
        self.update()

    def set_translate_z(self, value):
        self.translate_z = value / 100.0
        self.update()

    # Матрицы преобразования
    def rotation_matrix_x(self):
        return np.array([
            [1, 0, 0, 0],
            [0, math.cos(self.angle_x), -math.sin(self.angle_x), 0],
            [0, math.sin(self.angle_x), math.cos(self.angle_x), 0],
            [0, 0, 0, 1]
        ])

    def rotation_matrix_y(self):
        return np.array([
            [math.cos(self.angle_y), 0, math.sin(self.angle_y), 0],
            [0, 1, 0, 0],
            [-math.sin(self.angle_y), 0, math.cos(self.angle_y), 0],
            [0, 0, 0, 1]
        ])

    def rotation_matrix_z(self):
        return np.array([
            [math.cos(self.angle_z), -math.sin(self.angle_z), 0, 0],
            [math.sin(self.angle_z), math.cos(self.angle_z), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

    def scale_matrix(self):
        return np.array([
            [self.scale, 0, 0, 0],
            [0, self.scale, 0, 0],
            [0, 0, self.scale, 0],
            [0, 0, 0, 1]
        ])

    def translation_matrix(self):
        return np.array([
            [1, 0, 0, self.translate_x],
            [0, 1, 0, self.translate_y],
            [0, 0, 1, self.translate_z],
            [0, 0, 0, 1]
        ])
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_pos = event.pos()
            self.mouse_pressed = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pressed = False

    def mouseMoveEvent(self, event):
        if self.mouse_pressed and self.last_pos is not None:
            # Вычисляем разницу в координатах
            delta = event.pos() - self.last_pos
            self.last_pos = event.pos()
            
            # Преобразуем смещение мыши в углы поворота (коэффициент 0.5 для более плавного вращения)
            self.angle_y += math.radians(delta.x() * 0.5)
            self.angle_x += math.radians(delta.y() * 0.5)

            self.update()
            self.main_window.update_sliders_from_render()

    def keyPressEvent(self, event):
        # Обработка нажатий клавиш WASD
        if event.key() == Qt.Key.Key_W:
            self.translate_y -= self.movement_step
        elif event.key() == Qt.Key.Key_S:
            self.translate_y += self.movement_step
        elif event.key() == Qt.Key.Key_A:
            self.translate_x -= self.movement_step
        elif event.key() == Qt.Key.Key_D:
            self.translate_x += self.movement_step

        self.update()
        self.main_window.update_sliders_from_render()
