from polygon.fill_algorithms.points_check import point_in_polygon, find_inner_point


def fill_simple_seed(polygon):
    """Простой алгоритм заполнения с затравкой (4-связный)"""
    vertices = polygon.vertices
    if len(vertices) < 3:
        return []  # Возвращаем пустой список, если вершин недостаточно
    
    # Пытаемся найти внутреннюю точку (центр масс или другую точку)
    cx = sum(v[0] for v in vertices) / len(vertices)
    cy = sum(v[1] for v in vertices) / len(vertices)
    seed = (int(cx), int(cy))
    
    # Если центр масс не внутри полигона, ищем другую точку
    if not point_in_polygon(seed, vertices):
        seed = find_inner_point(vertices)
        if not seed:
            return []  # Не удалось найти точку внутри полигона
    
    # Определяем границы полигона для оптимизации
    x_min = min(v[0] for v in vertices)
    x_max = max(v[0] for v in vertices)
    y_min = min(v[1] for v in vertices)
    y_max = max(v[1] for v in vertices)
    
    # Инициализируем стек для затравочных точек и множество для хранения заполненных точек
    stack = [seed]
    filled = set()
    fill_points = []  # Список точек для заливки
    
    # Направления для 4-связности (вправо, влево, вниз, вверх)
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    while stack:
        x, y = stack.pop()
        
        # Если точка уже заполнена или вне диапазона, пропускаем
        if (x, y) in filled or not (x_min <= x <= x_max and y_min <= y <= y_max):
            continue
        
        # Добавляем точку в заполнение
        fill_points.append((x, y))
        filled.add((x, y))
        
        # Проверяем соседей в четырех направлениях (4-связность)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Если соседняя точка еще не заполнена и внутри полигона, добавляем в стек
            if ((nx, ny) not in filled and 
                    x_min <= nx <= x_max and 
                    y_min <= ny <= y_max and 
                    point_in_polygon((nx, ny), vertices)):
                stack.append((nx, ny))
    
    return fill_points