from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, \
    QToolBar, QGridLayout, QMenuBar, QMenu, QStatusBar, QScrollArea, QMessageBox

from src.view.canvas_widget import Canvas


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphic")
        try:
            self.setWindowIcon(QIcon("assets/logo.png"))
        finally:
            pass

        self.setMinimumSize(200, 100)
        self.resize(800, 600)

        # Статусная строка
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.workspace = QWidget()
        self.canvas_size = QSize(16, 16)  # Размер холста

        self.is_debug_mode = False  # Флаг для отслеживания режима отладки
        self.last_object = []

        self.build_menus()
        self.build_window_content()

        self.setCentralWidget(self.workspace)
        self.show()

    def build_menus(self):
        # Создание меню
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tool_menu = menu_bar.addMenu("Tools")
        lines_submenu = tool_menu.addMenu("Lines")

        # Действия для выбора алгоритма

        dda_action = QAction("DDA", self)
        dda_action.triggered.connect(lambda: self.canvas.set_algorithm("dda"))

        bresenham_action = QAction("Bresenham", self)
        bresenham_action.triggered.connect(lambda: self.canvas.set_algorithm("bresenham"))

        wu_action = QAction("Wu", self)
        wu_action.triggered.connect(lambda: self.canvas.set_algorithm("wu"))

        lines_submenu.addAction(dda_action)
        lines_submenu.addAction(bresenham_action)
        lines_submenu.addAction(wu_action)

    def build_window_content(self):
        main_layout = QVBoxLayout()

        # Создание холста
        self.canvas = Canvas(self.status, self.canvas_size)

        # Оборачивание в QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.canvas)

        # Контейнер для кнопок в правом нижнем углу
        button_layout = QHBoxLayout()
        # button_layout.addStretch()

        self.filler = QWidget()

        self.debug_button = QPushButton("Debug Start")
        self.debug_button.setStyleSheet("background-color: green; color: white;")
        self.debug_button.setMaximumWidth(100)
        self.debug_button.clicked.connect(self.enter_debug_mode)

        self.exit_debug_button = QPushButton("Debug End")
        self.exit_debug_button.setStyleSheet("background-color: red; color: white;")
        self.exit_debug_button.setMaximumWidth(100)
        self.exit_debug_button.clicked.connect(self.exit_debug_mode)
        self.exit_debug_button.hide()

        self.debug_next_button = QPushButton()
        self.debug_next_button.setMaximumWidth(64)
        self.debug_next_button.setIcon(QIcon("assets/right.png"))
        self.debug_next_button.clicked.connect(self.canvas.debug_next)
        self.debug_next_button.setEnabled(False)
        self.debug_next_button.hide()

        self.debug_prev_button = QPushButton()
        self.debug_prev_button.setMaximumWidth(64)
        self.debug_prev_button.setIcon(QIcon("assets/left.png"))
        self.debug_prev_button.clicked.connect(self.canvas.debug_prev)
        self.debug_prev_button.setEnabled(False)
        self.debug_prev_button.hide()

        button_layout.addWidget(self.filler)
        button_layout.addWidget(self.debug_prev_button)
        button_layout.addWidget(self.debug_next_button)
        button_layout.addWidget(self.debug_button)
        button_layout.addWidget(self.exit_debug_button)

        # Добавление в layout
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(button_layout)

        self.workspace.setLayout(main_layout)

    def enter_debug_mode(self):
        """Вход в debug mode"""
        self.is_debug_mode = True
        self.debug_prev_button.setEnabled(True)
        self.debug_next_button.setEnabled(True)

        self.debug_button.hide()
        self.exit_debug_button.show()
        self.debug_prev_button.show()
        self.debug_next_button.show()

        self.status.showMessage("Вход в режим отладки", 3000)
        self.menuBar().setEnabled(False)

        self.debug_mode()

    def exit_debug_mode(self):
        """Выход из debug mode"""
        self.is_debug_mode = False

        self.debug_prev_button.setEnabled(False)
        self.debug_next_button.setEnabled(False)

        self.debug_button.show()
        self.exit_debug_button.hide()
        self.debug_prev_button.show()
        self.debug_next_button.show()

        self.status.showMessage("Выход из режима отладки", 3000)
        self.menuBar().setEnabled(True)

        # self.canvas.objects.append(self.last_object)
        # self.canvas.redraw()

        # Сбрасываем визуальные подсказки
        self.canvas.setStyleSheet("")
        self.workspace.setStyleSheet("")
        self.canvas.exit_debug_mode()

    def debug_mode(self):
        """Дебаг-режим"""
        # last_painted = []
        # if self.canvas.objects:
        #     last_painted = self.canvas.objects.pop(-1)
        #     self.last_object = last_painted

        if self.is_debug_mode:
            # Меняем фон на серый в debug mode
            self.canvas.setStyleSheet("background-color: gray;")
            self.canvas.enter_debug_mode()


        else:
            self.canvas.setStyleSheet("")
            self.workspace.setStyleSheet("")
            # self.canvas.objects.append(last_painted)
            # self.canvas.redraw()
