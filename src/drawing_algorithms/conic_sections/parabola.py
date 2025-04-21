import matplotlib.pyplot as plt

def draw_parabola(start, end):
    """
    Строит параболу x^2 = 2py, смещённую так, чтобы проходить через (x0, y0) и (x1, y1).
    Поддерживает параболы, открытые вверх и вниз.
    """

    x0, y0 = start
    x1, y1 = end

    if y1 == y0:
        raise ValueError("y1 не должно быть равно y0 (иначе парабола вырождается)")

    dy = y1 - y0
    dx = x1 - x0
    direction = 1 if dy > 0 else -1  # 1 — вверх, -1 — вниз

    # Вычисление начального p
    p = dx ** 2 / (2 * abs(dy))

    # Центрирование: вершина -> (0,0)
    x = 0
    y = 0
    d = 1 - 2 * p
    border_x = 2 * p

    points = []
    prev_points = []

    # Итеративно уточняем p
    iteration = 0
    while True:
        iteration += 1
        points.clear()
        prev_points.clear()

        # Строим параболу с текущим p
        x = 0
        y = 0
        d = 1 - 2 * p
        border_x = 2 * p

        # Зона 1
        while x < border_x and abs(y) <= abs(dy):
            points.append((x0 + x, y0 + y))
            points.append((x0 - x, y0 + y))
            if d < 0:
                d = d + 2 * x + 3
            else:
                d = d + 2 * x - 4 * p + 3
                y = y + direction
            x += 1

        # Зона 2
        while abs(y) <= abs(dy):
            points.append((x0 + x, y0 + y))
            points.append((x0 - x, y0 + y))
            if d > 0:
                d = d - 4 * p + 2
            else:
                d = d + 2 * x - 4 * p + 2
                x += 1
            y = y + direction

        # Проверяем попадание в (x1, y1)
        if any((px, py) == (x1, y1) for px, py in points):
            break

        # Если точка не попала, уточняем p с помощью интерполяции
        p = p - 0.1 * (dy / (y1 - y0))  # Примерная корректировка

        # Ограничение на количество итераций
        if iteration > 100:
            print("Не удалось точно попасть в точку (x1, y1) после 100 итераций.")
            break

    return points