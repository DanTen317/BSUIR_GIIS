def fill_edge_list(polygon):
    """Алгоритм с упорядоченным списком ребер"""
    vertices = polygon.vertices
    if len(vertices) < 3:
        return []

    y_min = min(v[1] for v in vertices)
    y_max = max(v[1] for v in vertices)

    edges = []
    n = len(vertices)
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        if y1 != y2:  # Пропускаем горизонтальные рёбра
            if y1 < y2:
                edges.append((x1, y1, x2, y2))
            else:
                edges.append((x2, y2, x1, y1))

    edges.sort(key=lambda e: e[1])  # Сортировка рёбер по y-координате

    fill_points = []  # Список точек для заливки

    for y in range(y_min, y_max + 1):
        active_edges = []
        for edge in edges:
            x1, y1, x2, y2 = edge
            if y1 <= y < y2:  # Ребро активно на этой строке развёртки
                if y2 != y1:
                    # Вычисляем x-координату пересечения с текущей строкой
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    active_edges.append(x)

        active_edges.sort()  # Сортируем точки пересечения по x-координате

        # Заполняем области между парами точек пересечения
        for i in range(0, len(active_edges), 2):
            if i + 1 >= len(active_edges):
                break
            x_start = int(active_edges[i])
            x_end = int(active_edges[i + 1])
            # Добавляем все точки между x_start и x_end в список точек заливки
            for x in range(x_start, x_end + 1):
                fill_points.append((x, y))
    return fill_points
