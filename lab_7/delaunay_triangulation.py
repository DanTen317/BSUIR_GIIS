import math
import numpy as np

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __str__(self):
        return f"({self.x}, {self.y})"

class Edge:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return (self.p1 == other.p1 and self.p2 == other.p2) or (self.p1 == other.p2 and self.p2 == other.p1)
    
    def __hash__(self):
        # Ребро (A, B) считается таким же, как и ребро (B, A)
        return hash(frozenset([hash(self.p1), hash(self.p2)]))
    
    def length(self):
        return self.p1.distance(self.p2)

class Triangle:
    def __init__(self, p1, p2, p3):
        self.vertices = [p1, p2, p3]
        self.edges = [
            Edge(p1, p2),
            Edge(p2, p3),
            Edge(p3, p1)
        ]
    
    def __eq__(self, other):
        if not isinstance(other, Triangle):
            return False
        # Два треугольника равны, если содержат одинаковые точки
        return set(self.vertices) == set(other.vertices)
    
    def __hash__(self):
        return hash(frozenset([hash(v) for v in self.vertices]))
    
    def contains_point(self, point):
        return point in self.vertices
    
    def contains_edge(self, edge):
        return edge in self.edges
    
    def circumcenter(self):
        """Вычисляет координаты центра описанной окружности."""
        x1, y1 = self.vertices[0].x, self.vertices[0].y
        x2, y2 = self.vertices[1].x, self.vertices[1].y
        x3, y3 = self.vertices[2].x, self.vertices[2].y
        
        D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        
        if abs(D) < 1e-10:  # Предотвращение деления на ноль
            # Точки лежат на одной прямой, возвращаем центр масс
            return Point((x1 + x2 + x3) / 3, (y1 + y2 + y3) / 3)
        
        Ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / D
        Uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / D
        
        return Point(Ux, Uy)
    
    def circumradius(self):
        """Вычисляет радиус описанной окружности."""
        center = self.circumcenter()
        return center.distance(self.vertices[0])
    
    def in_circumcircle(self, point):
        """Проверяет, находится ли точка внутри описанной окружности треугольника."""
        center = self.circumcenter()
        radius = self.circumradius()
        return center.distance(point) < radius

def create_super_triangle(points):
    """
    Создает большой треугольник, содержащий все точки из набора.
    """
    # Находим минимальные и максимальные координаты
    min_x = min(p.x for p in points)
    min_y = min(p.y for p in points)
    max_x = max(p.x for p in points)
    max_y = max(p.y for p in points)
    
    # Вычисляем размер и центр ограничивающего прямоугольника
    dx = max_x - min_x
    dy = max_y - min_y
    delta_max = max(dx, dy)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    
    # Создаем супертреугольник, который точно содержит все точки
    # Увеличиваем в 20 раз, чтобы быть уверенными
    p1 = Point(center_x - 20 * delta_max, center_y - delta_max)
    p2 = Point(center_x, center_y + 20 * delta_max)
    p3 = Point(center_x + 20 * delta_max, center_y - delta_max)
    
    return Triangle(p1, p2, p3)

class DelaunayTriangulation:
    """
    Класс для триангуляции Делоне
    """
    def __init__(self):
        self.points = []
        self.triangles = []
        self.edges = set()  # Множество всех рёбер в триангуляции
        
    def clear(self):
        """Очищает данные триангуляции"""
        self.points = []
        self.triangles = []
        self.edges = set()
    
    def add_point(self, x, y):
        """
        Добавляет точку в набор и перестраивает триангуляцию
        """
        point = Point(x, y)
        
        # Проверяем, нет ли уже такой точки
        for p in self.points:
            if p == point:
                return False
                
        self.points.append(point)
        
        # Если меньше 3 точек, просто добавляем и ждем
        if len(self.points) < 3:
            return True
            
        # Если ровно 3 точки, создаем первый треугольник
        if len(self.points) == 3:
            # Проверяем, не лежат ли точки на одной прямой
            p1, p2, p3 = self.points
            # Вычисляем площадь треугольника через векторное произведение
            area = 0.5 * abs((p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y))
            
            if area < 1e-10:  # Если площадь близка к нулю, точки коллинеарны
                return True
                
            self.triangles = [Triangle(p1, p2, p3)]
            self.edges = set(self.triangles[0].edges)
            return True
            
        # Перестраиваем триангуляцию для более 3 точек
        self.triangulate()
        return True
    
    def triangulate(self):
        """
        Выполняет триангуляцию Делоне для текущего набора точек
        """
        if len(self.points) < 3:
            self.triangles = []
            self.edges = set()
            return
            
        # Создаем супертреугольник, содержащий все точки
        super_triangle = create_super_triangle(self.points)
        
        # Начинаем с супертреугольника
        triangulation = [super_triangle]
        # Добавляем точки по одной
        for i, point in enumerate(self.points):
            
            # Найдем все треугольники, чьи описанные окружности содержат эту точку
            bad_triangles = []
            for triangle in triangulation:
                if triangle.in_circumcircle(point):
                    bad_triangles.append(triangle)
            
            # Найдем граничные рёбра полигона для этих треугольников
            boundary = []
            for triangle in bad_triangles:
                for edge in triangle.edges:
                    # Проверяем, является ли это ребро уникальным в наборе плохих треугольников
                    # Если оно повторяется, то оно не на границе
                    is_boundary = True
                    for other in bad_triangles:
                        if triangle != other and edge in other.edges:
                            is_boundary = False
                            break
                    
                    if is_boundary:
                        boundary.append(edge)

            
            # Удалим плохие треугольники
            for triangle in bad_triangles:
                triangulation.remove(triangle)
            
            # Создаем новые треугольники, соединяя точку со всеми рёбрами границы
            new_triangles = []
            for edge in boundary:
                new_triangle = Triangle(edge.p1, edge.p2, point)
                triangulation.append(new_triangle)
                new_triangles.append(new_triangle)
            
        
        # Удаляем треугольники, содержащие вершины супертреугольника
        super_vertices = set(super_triangle.vertices)
        i = 0
        while i < len(triangulation):
            if any(vertex in super_vertices for vertex in triangulation[i].vertices):
                triangulation.pop(i)
            else:
                i += 1
        
        # Обновляем результаты
        self.triangles = triangulation
        
        # Обновляем множество рёбер
        self.edges = set()
        for triangle in self.triangles:
            for edge in triangle.edges:
                self.edges.add(edge)
                
