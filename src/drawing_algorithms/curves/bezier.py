import numpy as np


def draw_bezier_curve(p0, p1, p2, p3, num_points=300):
    """
    Генерирует дискретизированную кривую Безье третьего порядка (кубическую) с матричными вычислениями.

    :param p0: Первая контрольная точка (x0, y0)
    :param p1: Вторая контрольная точка (x1, y1)
    :param p2: Третья контрольная точка (x2, y2)
    :param p3: Четвертая контрольная точка (x3, y3)
    :param num_points: Количество точек на кривой
    :return: Список пикселей [(x, y), ...]
    """
    # Матрица Безье
    B = np.array([
        [-1, 3, -3, 1],
        [3, -6, 3, 0],
        [-3, 3, 0, 0],
        [1, 0, 0, 0]
    ])

    # Вектор контрольных точек
    P = np.array([p0, p1, p2, p3])

    curve_points = []
    prev_pixel = None

    # Генерируем дискретные точки
    for t in np.linspace(0, 1, num_points):
        T = np.array([t ** 3, t ** 2, t, 1])  # Вектор параметра t
        point = T @ B @ P  # Матричное умножение

        pixel = (int(round(point[0])), int(round(point[1])))

        # Удаляем повторяющиеся пиксели
        if pixel != prev_pixel:
            curve_points.append(pixel)
        prev_pixel = pixel

    return curve_points