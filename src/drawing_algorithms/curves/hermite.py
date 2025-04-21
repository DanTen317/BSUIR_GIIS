import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QPoint, QPointF


def compute_hermite_points(p1, p2, r1, r2, density=5):
    hermite_matrix = np.array([
        [ 2, -2,  1,  1],
        [-3,  3, -2, -1],
        [ 0,  0,  1,  0],
        [ 1,  0,  0,  0]
    ])
    geometry = np.array([p1, p2, r1, r2])
    def vec_length(v): return np.linalg.norm(v)
    curve_length_est = vec_length(np.array(p2) - np.array(p1)) + vec_length(r1) + vec_length(r2)
    num_points = int(curve_length_est * density)

    points = []
    for i in range(num_points + 1):
        t = i / num_points
        T = np.array([t**3, t**2, t, 1])
        pt = T @ hermite_matrix @ geometry
        points.append(pt)
    points = np.array(points)
    return points

class HermiteCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Интерактивная кривая Эрмита")
        self.setFixedSize(100, 100)
        self.points_clicked = []
        self.curve_points = None
        self.info = QLabel("Кликни: P₁ → P₂ → конец R₁ → конец R₂")
        layout = QVBoxLayout()
        layout.addWidget(self.info)
        layout.addStretch()
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x, y = event.position().toPoint().x(), event.position().toPoint().y()
            self.points_clicked.append((x, y))
            self.update()
            if len(self.points_clicked) == 4:
                p1, p2 = self.points_clicked[0], self.points_clicked[1]
                r1 = np.array(self.points_clicked[2]) - np.array(p1)
                r2 = np.array(self.points_clicked[3]) - np.array(p2)
                self.curve_points = compute_hermite_points(p1, p2, r1, r2)
                self.info.setText("Кривая построена. Перезапусти для нового ввода.")
                self.update()

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.fillRect(self.rect(), QColor("black"))

            pen = QPen(QColor("red"))
            pen.setWidth(6)
            painter.setPen(pen)

            # Отрисовка введённых точек
            for x, y in self.points_clicked:
                painter.drawPoint(int(x), int(y))

            if len(self.points_clicked) >= 3:
                painter.setPen(QPen(QColor("green"), 2))
                p1 = self.points_clicked[0]
                r1_end = self.points_clicked[2]
                painter.drawLine(int(p1[0]), int(p1[1]), int(r1_end[0]), int(r1_end[1]))

            if len(self.points_clicked) >= 4:
                painter.setPen(QPen(QColor("blue"), 2))
                p2 = self.points_clicked[1]
                r2_end = self.points_clicked[3]
                painter.drawLine(int(p2[0]), int(p2[1]), int(r2_end[0]), int(r2_end[1]))

            if self.curve_points is not None and len(self.curve_points) >= 2:
                painter.setPen(QPen(QColor("white"), 1))
                for i in range(len(self.curve_points) - 1):
                    p1 = QPointF(*self.curve_points[i])
                    p2 = QPointF(*self.curve_points[i + 1])
                    painter.drawLine(p1, p2)

        except Exception as e:
            print(f"Paint error: {e}")


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HermiteCanvas()
    window.show()
    sys.exit(app.exec())
