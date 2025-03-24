from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, \
    QToolBar, QGridLayout, QMenuBar, QMenu, QStatusBar, QScrollArea

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
        self.canvas_size = QSize(400, 400)  # Размер холста

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

    def build_window_content(self):
        main_layout = QVBoxLayout()

        # Контейнер для кнопок в правом нижнем углу
        button_layout = QHBoxLayout()
        # button_layout.addStretch()

        self.debug_button = QPushButton("Debug Start")
        self.debug_button.setStyleSheet("background-color:green")
        self.debug_next_button = QPushButton("Debug Next")
        self.debug_prev_button = QPushButton("Debug Prev")

        button_layout.addWidget(self.debug_prev_button)
        button_layout.addWidget(self.debug_next_button)
        button_layout.addWidget(self.debug_button)

        # Создание холста
        self.canvas = Canvas(self.status, self.canvas_size)

        # Оборачивание в QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.canvas)

        # Добавление в layout
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(button_layout)
        # self.drawing_widget.setLayout(main_layout)

        self.workspace.setLayout(main_layout)
