import numpy as np


def draw_b_spline(p0, p1, p2, p3, num_points=100):
    """
    Генерирует дискретизированную B-сплайн кривую с матричными вычислениями.

    :param control_points: Список контрольных точек [(x0, y0), (x1, y1), ...]
    :param num_points: Количество точек на кривой
    :return: Список пикселей [(x, y), ...]
    """

    # Матрица базисных функций B-сплайна
    B = np.array([
        [-1, 3, -3, 1],
        [3, -6, 3, 0],
        [-3, 0, 3, 0],
        [1, 4, 1, 0]
    ]) / 6  # Нормализация коэффициентов

    P = np.array([p0, p1, p2, p3])  # Контрольные точки в виде матрицы
    curve_points = []

    for t in np.linspace(0, 1, num_points):
        T = np.array([t ** 3, t ** 2, t, 1])  # Вектор параметра t
        point = T @ B @ P

        pixel = (int(round(point[0])), int(round(point[1])))
        curve_points.append(pixel)

    return curve_points
