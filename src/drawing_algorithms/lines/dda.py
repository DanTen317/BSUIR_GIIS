def dda_line(start_point, end_point):
    """
    Алгоритм ЦДА для рисования отрезка между двумя точками.

    :param start_point: Координаты начальной точки;
    :param end_point: Координаты конечной точки.
    """
    x1, y1 = start_point
    x2, y2 = end_point

    # Вычисление разностей по координатам
    dx = x2 - x1
    dy = y2 - y1

    # Определение количества шагов (максимальная длина по оси)
    steps = int(max(abs(dx), abs(dy)))

    # Вычисление приращений для каждой оси
    x_increment = dx / steps
    y_increment = dy / steps

    # Инициализация начальной точки
    x = x1
    y = y1

    # Список для хранения координат пикселей линии
    pixels = []

    for i in range(steps + 1):
        # Добавляем текущую точку в список (округляем координаты)
        pixels.append((round(x), round(y)))

        # Приращение координат
        x += x_increment
        y += y_increment
        print(x, y)

    return pixels
