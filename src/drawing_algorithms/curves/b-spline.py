import numpy as np
def draw_b_spline(control_points, num_points=100):
    """
    Генерирует дискретизированную B-сплайн кривую с матричными вычислениями.

    :param control_points: Список контрольных точек [(x0, y0), (x1, y1), ...]
    :param num_points: Количество точек на кривой
    :return: Список пикселей [(x, y), ...]
    """
    n = len(control_points) - 1  # Количество контрольных точек
    degree = 3  # Степень B-сплайна
    knots = np.linspace(0, 1, n + degree + 1)  # Узловой вектор

    # Матрица базисных функций B-сплайна
    B = np.array([
        [-1,  3, -3,  1],
        [ 3, -6,  3,  0],
        [-3,  0,  3,  0],
        [ 1,  4,  1,  0]
    ]) / 6  # Нормализация коэффициентов

    P = np.array(control_points)  # Контрольные точки в виде матрицы
    curve_points = []

    for t in np.linspace(0, 1, num_points):
        T = np.array([t**3, t**2, t, 1])  # Вектор параметра t
        point = T @ B @ P[:4]  # Используем только первые 4 точки

        pixel = (int(round(point[0])), int(round(point[1])))
        curve_points.append(pixel)

    return curve_points
