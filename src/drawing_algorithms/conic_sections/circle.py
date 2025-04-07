def draw_circle(x0, y0, radius):
    x = 0
    y = radius
    d = 3 - 2 * radius
    points = []

    def plot_circle_points(cx, cy, x, y):
        for dx, dy in [(x, y), (y, x), (-x, y), (-y, x),
                       (-x, -y), (-y, -x), (x, -y), (y, -x)]:
            if (cx + dx, cy + dy) not in points:
                points.append((cx + dx, cy + dy))

    print(d)
    plot_circle_points(x0, y0, x, y)
    while x <= y:
        if d <= 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1

        plot_circle_points(x0, y0, x, y)
        print(d)

    return points
