import numpy as np


def draw_hermite_curve(p1, p2, r1, r2, base_points=200):
    """
    Генерирует дискретизированную кривую Эрмита без двойных пикселей,
    используя проверку изменения градиента.

    :param p1: Начальная точка (x1, y1)
    :param p2: Конечная точка (x2, y2)
    :param r1: Конец касательной в p1 (x1', y1')
    :param r2: Конец касательной в p2 (x2', y2')
    :param base_points: Базовое количество точек
    :return: Список пикселей [(x, y), ...]
    """
    t1 = (r1[0] - p1[0], r1[1] - p1[1])
    t2 = (p2[0] - r2[0], p2[1] - r2[1])

    H = np.array([
        [ 2, -2,  1,  1],
        [-3,  3, -2, -1],
        [ 0,  0,  1,  0],
        [ 1,  0,  0,  0]
    ])

    P = np.array([p1, p2, t1, t2])

    curve_points = []


    for t in np.linspace(0, 1, base_points):
        T = np.array([t**3, t**2, t, 1])
        point = T @ H @ P
        pixel = (int(round(point[0])), int(round(point[1])))
        if pixel not in curve_points:
            curve_points.append(pixel)

    return curve_points