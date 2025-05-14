from polygon.fill_algorithms.points_check import point_in_polygon, find_inner_point


def fill_scanline_seed(polygon):
    """Построчный алгоритм заполнения с затравкой"""
    vertices = polygon.vertices
    if len(vertices) < 3:
        return []  # Возвращаем пустой список, если вершин недостаточно

    # Находим внутреннюю затравочную точку
    seed = find_inner_point(vertices)
    if not seed:
        return []  # Не удалось найти точку внутри полигона

    # Определяем границы полигона для оптимизации
    x_min = min(v[0] for v in vertices)
    x_max = max(v[0] for v in vertices)
    y_min = min(v[1] for v in vertices)
    y_max = max(v[1] for v in vertices)

    # Создаем стек для затравочных точек и множество для заполненных точек
    stack = [seed]
    filled = set()
    fill_points = []  # Список точек для заливки

    while stack:
        x, y = stack.pop()

        # Пропускаем уже заполненные точки и точки вне области полигона
        if (x, y) in filled or not (x_min <= x <= x_max and y_min <= y <= y_max):
            continue

        # Находим левую границу текущей строки
        left = x
        while left > x_min and point_in_polygon((left - 1, y), vertices):
            left -= 1

        # Находим правую границу текущей строки
        right = x
        while right < x_max and point_in_polygon((right + 1, y), vertices):
            right += 1

        # Заполняем строку от левой до правой границы
        for px in range(left, right + 1):
            if (px, y) not in filled:
                fill_points.append((px, y))
                filled.add((px, y))

        # Проверяем строки выше и ниже для новых затравочных точек
        for ny in [y - 1, y + 1]:
            if y_min <= ny <= y_max:  # Проверяем, что мы в границах полигона
                # Ищем затравочные точки на строке выше/ниже
                px = left
                while px <= right:
                    # Находим начало непрерывного сегмента внутри полигона
                    if point_in_polygon((px, ny), vertices) and (px, ny) not in filled:
                        start = px
                        # Находим конец сегмента
                        while (px <= right and
                               point_in_polygon((px, ny), vertices) and
                               (px, ny) not in filled):
                            px += 1
                        # Добавляем среднюю точку сегмента как новую затравку
                        mid = start + (px - start) // 2
                        stack.append((mid, ny))
                    else:
                        px += 1

    return fill_points
