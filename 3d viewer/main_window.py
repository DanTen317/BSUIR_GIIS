import math

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                             QLabel, QFileDialog, QSlider, QHBoxLayout)
from PyQt6.QtCore import Qt
from render_widget import RenderWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("3D Просмотр")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Создаем область рендеринга
        self.render_widget = RenderWidget(self)

        # Создаем контролы
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)

        # Кнопка загрузки файла
        load_button = QPushButton("Загрузить 3D объект")
        load_button.clicked.connect(self.load_file)
        controls_layout.addWidget(load_button)

        # Создаем слайдеры с текстовыми полями
        self.rotation_x, self.rotation_x_label = self.create_slider_with_label(
            "Поворот X", -180, 180, controls_layout,
            self.render_widget.set_rotation_x, "°")

        self.rotation_y, self.rotation_y_label = self.create_slider_with_label(
            "Поворот Y", -180, 180, controls_layout,
            self.render_widget.set_rotation_y, "°")

        self.rotation_z, self.rotation_z_label = self.create_slider_with_label(
            "Поворот Z", -180, 180, controls_layout,
            self.render_widget.set_rotation_z, "°")

        self.scale, self.scale_label = self.create_slider_with_label(
            "Масштаб", 10, 500, controls_layout,
            self.render_widget.set_scale, "%", initial=100)

        self.distance, self.distance_label = self.create_slider_with_label(
            "Дистанция", 200, 1000, controls_layout,
            self.render_widget.set_distance, "", initial=500)

        self.translate_x, self.translate_x_label = self.create_slider_with_label(
            "Сдвиг X", -1000, 1000, controls_layout,
            self.render_widget.set_translate_x)

        self.translate_y, self.translate_y_label = self.create_slider_with_label(
            "Сдвиг Y", -1000, 1000, controls_layout,
            self.render_widget.set_translate_y)

        self.translate_z, self.translate_z_label = self.create_slider_with_label(
            "Сдвиг Z", -1000, 1000, controls_layout,
            self.render_widget.set_translate_z)

        # Кнопка сброса
        reset_button = QPushButton("Сброс")
        reset_button.clicked.connect(self.reset_values)
        controls_layout.addWidget(reset_button)

        # Добавляем виджеты в главный layout
        layout.addWidget(self.render_widget, stretch=1)
        layout.addWidget(controls_widget)

    def create_slider_with_label(self, name, min_val, max_val, layout, slot, units="", initial=0):
        # Контейнер для слайдера и значения
        container = QWidget()
        container_layout = QVBoxLayout(container)

        # Заголовок
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(name)
        value_label = QLabel(f"{initial}{units}")

        title_layout.addWidget(label)
        title_layout.addWidget(value_label)
        title_layout.addStretch()

        # Слайдер
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(initial)

        def on_value_changed(value):
            value_label.setText(f"{value}{units}")
            slot(value)

        slider.valueChanged.connect(on_value_changed)

        container_layout.addWidget(title_container)
        container_layout.addWidget(slider)
        layout.addWidget(container)

        return slider, value_label

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите 3D объект",
            "",
            "Текстовые файлы (*.txt)"
        )
        if filename:
            self.render_widget.load_object(filename)

    def reset_values(self):
        # Сбрасываем значения слайдеров
        self.rotation_x.setValue(0)
        self.rotation_y.setValue(0)
        self.rotation_z.setValue(0)
        self.scale.setValue(100)
        self.distance.setValue(500)
        self.translate_x.setValue(0)
        self.translate_y.setValue(0)
        self.translate_z.setValue(0)

    def update_sliders_from_render(self):
        # Обновляем значения слайдеров в соответствии с значениями в render_widget
        self.rotation_x.setValue(int(math.degrees(self.render_widget.angle_x)))
        self.rotation_y.setValue(int(math.degrees(self.render_widget.angle_y)))
        self.rotation_z.setValue(int(math.degrees(self.render_widget.angle_z)))
        self.translate_x.setValue(int(self.render_widget.translate_x * 100))
        self.translate_y.setValue(int(self.render_widget.translate_y * 100))
        self.translate_z.setValue(int(self.render_widget.translate_z * 100))
