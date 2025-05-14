def fill_active_edge(polygon):
    """Растровая развертка с упорядоченным списком рёбер"""
    vertices = polygon.vertices
    if len(vertices) < 3:
        return []

    y_min = min(v[1] for v in vertices)
    y_max = max(v[1] for v in vertices)

    # Создаем таблицу рёбер
    edge_table = {}

    n = len(vertices)
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]

        # Пропускаем горизонтальные рёбра
        if y1 == y2:
            continue

        # Упорядочиваем точки так, чтобы y1 < y2
        if y1 > y2:
            x_top, y_top = x1, y1
            x_bottom, y_bottom = x2, y2
        else:
            x_top, y_top = x2, y2
            x_bottom, y_bottom = x1, y1

        # Вычисляем наклон ребра (dx/dy)
        dx = (x_top - x_bottom) / (y_top - y_bottom)
        
        # Добавляем ребро в таблицу рёбер
        edge = {'x': x_bottom, 'dx': dx, 'y_max': y_top}

        if y_bottom not in edge_table:
            edge_table[y_bottom] = []
        edge_table[y_bottom].append(edge)

    # Список точек для заливки
    fill_points = []

    # Список активных рёбер (AET)
    aet = []

    # Проходим растровую развертку сверху вниз
    for y in range(y_min, y_max + 1):
        # Добавляем рёбра из ET в AET
        if y in edge_table:
            aet.extend(edge_table[y])

        # Удаляем рёбра, которые закончились (y >= y_max)
        aet = [e for e in aet if e['y_max'] > y]

        # Сортируем рёбра по x-координате
        aet.sort(key=lambda e: e['x'])

        # Заполняем между парами пересечений
        for i in range(0, len(aet), 2):
            if i + 1 >= len(aet):
                break
            x_start = int(round(aet[i]['x']))
            x_end = int(round(aet[i + 1]['x']))

            # Добавляем все точки между x_start и x_end
            for x in range(x_start, x_end + 1):
                fill_points.append((x, y))

        # Обновляем x-координаты для следующей строки
        for edge in aet:
            edge['x'] += edge['dx']

    return fill_points  # Возвращаем все точки для заливки