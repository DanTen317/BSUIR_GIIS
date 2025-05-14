from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QToolBar,
                             QMenuBar, QMenu, QComboBox, QPushButton, QStatusBar, QLabel, QCheckBox)
from PyQt6.QtGui import QAction, QActionGroup
from canvas_widget import CanvasWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор полигонов")
        self.setGeometry(100, 100, 800, 600)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Создаем layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Создаем холст
        self.canvas = CanvasWidget()
        layout.addWidget(self.canvas)

        # Создаем меню
        self.create_menu()

        # Создаем панель инструментов
        self.create_toolbar()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.canvas.editor.polygon_finished.connect(self.show_status_message)

    def show_status_message(self, message):
        self.status_bar.showMessage(message)

    def create_menu(self):
        menubar = self.menuBar()

        # Меню "Построение полигонов"
        polygon_menu = menubar.addMenu("Построение полигонов")

        # Подменю выбора метода построения выпуклой оболочки
        hull_menu = polygon_menu.addMenu("Метод построения выпуклой оболочки")

        # Создаем группу действий для методов
        hull_group = QActionGroup(self)

        # Действие для метода Грэхема
        graham_action = QAction("Метод Грэхема", self, checkable=True)
        graham_action.setChecked(True)
        graham_action.triggered.connect(lambda: self.set_hull_method("Graham"))
        hull_group.addAction(graham_action)
        hull_menu.addAction(graham_action)

        # Действие для метода Джарвиса
        jarvis_action = QAction("Метод Джарвиса", self, checkable=True)
        jarvis_action.triggered.connect(lambda: self.set_hull_method("Jarvis"))
        hull_group.addAction(jarvis_action)
        hull_menu.addAction(jarvis_action)

        # Действие очистки
        clear_action = QAction("Очистить", self)
        clear_action.triggered.connect(self.clear_canvas)
        polygon_menu.addAction(clear_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Режим рисования:
        mode_combo = QComboBox(self)
        mode_combo.addItems(["Полигон", "Линия"])
        mode_combo.currentTextChanged.connect(self.set_drawing_mode)
        toolbar.addWidget(mode_combo)

        # Режим выпуклых оболочек
        hull_combo = QComboBox(self)
        hull_combo.addItems(["Грэхем", "Джарвис"])
        hull_combo.currentTextChanged.connect(
            lambda text: self.set_hull_method("Graham" if text == "Грэхем" else "Jarvis"))
        toolbar.addWidget(hull_combo)

        # Алгоритм рисования линий
        line_combo = QComboBox(self)
        line_combo.addItems(["CDA", "Bresenham", "Wu"])
        line_combo.currentTextChanged.connect(
            lambda text: self.set_line_algorithm(text))
        toolbar.addWidget(line_combo)

        # Кнопка очистки
        clear_button = QPushButton("Очистить")
        clear_button.clicked.connect(self.clear_canvas)
        toolbar.addWidget(clear_button)

        toolbar.addSeparator()

        # Заливка
        fill_combo = QComboBox(self)
        fill_combo.addItems(["EdgeList", "ActiveEdge", "SimpleSeed", "ScanlineSeed", "None"])
        fill_combo.currentTextChanged.connect(
            lambda text: self.set_fill_algorithm(text))
        toolbar.addWidget(fill_combo)
        # fill_button = QPushButton("Залить")
        # fill_button.clicked.connect(self.fill)
        # toolbar.addWidget(fill_button)

        toolbar.addSeparator()

        # Секция отладки
        debug_label = QLabel("Отладка:")
        toolbar.addWidget(debug_label)

        # Чекбокс для режима отладки
        self.debug_checkbox = QCheckBox("Режим отладки")
        self.debug_checkbox.toggled.connect(self.toggle_debug_mode)
        toolbar.addWidget(self.debug_checkbox)

        # Кнопка "Следующий шаг"
        self.next_step_button = QPushButton("Следующий шаг")
        self.next_step_button.clicked.connect(self.next_debug_step)
        self.next_step_button.setEnabled(False)  # Изначально отключена
        toolbar.addWidget(self.next_step_button)

    def set_hull_method(self, method):
        print(f"Алгоритм построения оболочек: {method}")
        self.canvas.editor.hull_method = method
        self.canvas.update()

    def set_line_algorithm(self, algorithm):
        print(f"Алгоритм построения линий: {algorithm}")
        self.canvas.editor.line_algorithm = algorithm
        self.canvas.update()

    def set_drawing_mode(self, mode):
        print(f"Режим рисования: {mode}")
        self.canvas.editor.drawing_mode = mode
        self.canvas.editor.reset_current_action()
        self.canvas.update()

    def set_fill_algorithm(self, algorithm):
        print(f"Алгоритм заливки: {algorithm}")
        self.canvas.editor.set_fill_algorithm(algorithm)

    def fill(self):
        self.canvas.update()

    def clear_canvas(self):
        self.canvas.editor.clear()
        self.canvas.update()
        print("Очищено")

    def toggle_debug_mode(self, checked):
        print(f"Режим отладки {'включен' if checked else 'выключен'}")
        self.show_status_message(f"Режим отладки {'включен' if checked else 'выключен'}")

        self.canvas.editor.toggle_debug_mode(checked)
        self.next_step_button.setEnabled(checked)

    def next_debug_step(self):
        self.canvas.editor.next_debug_step()
