def find_inner_point(vertices):
    """Находит внутреннюю точку полигона"""
    if not vertices:
        return None

    # Сначала пробуем центр масс
    cx = sum(v[0] for v in vertices) / len(vertices)
    cy = sum(v[1] for v in vertices) / len(vertices)

    if point_in_polygon((cx, cy), vertices):
        return (int(cx), int(cy))

    # Если центр масс не подходит, ищем точку внутри методом пересечений
    y_min = min(v[1] for v in vertices)
    y_max = max(v[1] for v in vertices)

    for y in range(int(y_min) + 1, int(y_max), 2):
        intersections = []
        n = len(vertices)

        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]

            # Проверяем, пересекает ли луч ребро
            if (y1 <= y <= y2) or (y2 <= y <= y1):
                if y1 != y2:  # Избегаем деления на ноль для горизонтальных рёбер
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    intersections.append(x)

        # Сортируем пересечения по x
        intersections.sort()

        # Ищем точку между парами пересечений (внутри полигона)
        for i in range(0, len(intersections) - 1, 2):
            if i + 1 < len(intersections):
                mid_x = (intersections[i] + intersections[i + 1]) / 2
                if point_in_polygon((mid_x, y), vertices):
                    return (int(mid_x), y)

    return None


def point_in_polygon(point, vertices):
    """Проверяет, находится ли точка внутри полигона (метод лучевой развертки)"""
    x, y = point
    n = len(vertices)
    inside = False

    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]

        # Проверяем, пересекает ли луч из точки (x,y) вправо ребро полигона
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside

    return inside