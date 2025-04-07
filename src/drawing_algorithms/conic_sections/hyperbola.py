def draw_hyperbola(start, end):
    x0, y0 = start
    x1, y1 = end
    a = round(abs(x1 - x0) / 2)
    b = abs(y1 - y0)

    x = a
    y = 0
    d = (b ** 2) * (1 + 2 * abs(a)) - a ** 2  # начальное значение d
    points = []

    while x <= abs(x1 - x0):
        points.extend([(x + x0 - a, y + y0),
                       (x + x0 - a, y0 - y),
                       (x0 - a - x, y + y0),
                       (x0 - a - x, y0 - y)])
        if d < 0:
            delta = d * 2 + 2 * y * (a ** 2) + a ** 2
            if delta <= 0:
                x += 1
                d = d + (b ** 2) * (2 * x + 1)
            else:
                x += 1
                y += 1
                d = d + (2 * x + 1) * (b ** 2) - (2 * y + 1) * (a ** 2)
        elif d > 0:
            delta = 2 * d - 2 * x * (b ** 2) - b ** 2
            if delta > 0:
                y += 1
                d = d - (a ** 2) * (2 * y + 1)
            else:
                x += 1
                y += 1
                d = d + (2 * x + 1) * (b ** 2) - (2 * y + 1) * (a ** 2)
        elif d == 0:
            x += 1
            y += 1
            d = d + (2 * x + 1) * (b ** 2) - (2 * y + 1) * (a ** 2)

    return points
