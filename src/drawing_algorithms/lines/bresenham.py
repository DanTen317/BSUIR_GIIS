def bresenham_line(start_point, end_point):
    """
    Алгоритм Брезенхема для рисования отрезка между двумя точками.

    Аргументы:
    x1, y1 -- координаты начальной точки
    x2, y2 -- координаты конечной точки

    Возвращает:
    Список координат пикселей, которые формируют линию.
    """
    x1, y1 = start_point
    x2, y2 = end_point

    # Список для хранения координат пикселей линии
    pixels = []

    # Разности координат
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    # Направления приращения
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1

    # Начальное значение ошибки
    err = dx - dy

    # Начальная точка
    x, y = x1, y1

    while True:
        # Добавляем текущую точку в список
        pixels.append((x, y))

        # Если достигли конечной точки, выходим из цикла
        if x == x2 and y == y2:
            break

        # Сохраняем значение ошибки для дальнейшего использования
        e2 = 2 * err

        # Проверяем, нужно ли изменить x
        if e2 > -dy:
            err -= dy
            x += sx

        # Проверяем, нужно ли изменить y
        if e2 < dx:
            err += dx
            y += sy

    return pixels
