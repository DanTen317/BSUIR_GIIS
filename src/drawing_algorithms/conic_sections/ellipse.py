def draw_ellipse(start, end):
    x0, y0 = start
    x1, y1 = end
    # Центр эллипса
    xc = (x0 + x1) // 2
    yc = (y0 + y1) // 2

    # Полуоси
    a = abs(x1 - x0) // 2
    b = abs(y1 - y0) // 2

    x = 0
    y = b
    a2 = a * a
    b2 = b * b
    fx = 0
    fy = 2 * a2 * y
    p = b2 - a2 * b + 0.25 * a2
    points = []

    def plot_points(cx, cy, x, y):
        for dx, dy in [(x, y), (-x, y), (-x, -y), (x, -y)]:
            if (cx + dx, cy + dy) not in points:
                points.append((cx + dx, cy + dy))

    # Первая область
    while fx < fy:
        plot_points(xc, yc, x, y)
        x += 1
        fx += 2 * b2
        if p < 0:
            p += b2 * (2 * x + 1)
        else:
            y -= 1
            fy -= 2 * a2
            p += b2 * (2 * x + 1) - a2 * (2 * y)

    # Вторая область
    p = b2 * (x + 0.5) ** 2 + a2 * (y - 1) ** 2 - a2 * b2
    while y >= 0:
        plot_points(xc, yc, x, y)
        y -= 1
        fy -= 2 * a2
        if p > 0:
            p -= a2 * (2 * y + 1)
        else:
            x += 1
            fx += 2 * b2
            p += fx - a2 * (2 * y + 1)

    return points
