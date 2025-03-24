import math
import numpy as np

def ipart(x):
    """Целая часть числа."""
    return math.floor(x)

def round_int(x):
    """Округление до ближайшего целого."""
    return ipart(x + 0.5)

def fpart(x):
    """Дробная часть числа."""
    return x - math.floor(x)

def rfpart(x):
    """1 - дробная часть."""
    return 1 - fpart(x)


def wu_line(start_point, end_point):
    """Алгоритм Ву для сглаженной линии с альфа-каналом (0-255)."""
    x1, y1 = start_point
    x2, y2 = end_point

    pixels = []

    steep = abs(y2 - y1) > abs(x2 - x1)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dx = x2 - x1
    dy = y2 - y1
    gradient = dy / dx if dx != 0 else 1

    # Первый конец
    x_end = round_int(x1)
    y_end = y1 + gradient * (x_end - x1)
    x_gap = rfpart(x1 + 0.5)

    x_pixel1 = x_end
    y_pixel1 = ipart(y_end)

    if steep:
        pixels.append((y_pixel1, x_pixel1, np.uint8(255 * rfpart(y_end) * x_gap)))
        pixels.append((y_pixel1 + 1, x_pixel1, np.uint8(255 * fpart(y_end) * x_gap)))
    else:
        pixels.append((x_pixel1, y_pixel1, np.uint8(255 * rfpart(y_end) * x_gap)))
        pixels.append((x_pixel1, y_pixel1 + 1, np.uint8(255 * fpart(y_end) * x_gap)))

    intery = y_end + gradient

    # Второй конец
    x_end = round_int(x2)
    y_end = y2 + gradient * (x_end - x2)
    x_gap = fpart(x2 + 0.5)

    x_pixel2 = x_end
    y_pixel2 = ipart(y_end)

    if steep:
        pixels.append((y_pixel2, x_pixel2, np.uint8(255 * rfpart(y_end) * x_gap)))
        pixels.append((y_pixel2 + 1, x_pixel2, np.uint8(255 * fpart(y_end) * x_gap)))
    else:
        pixels.append((x_pixel2, y_pixel2, np.uint8(255 * rfpart(y_end) * x_gap)))
        pixels.append((x_pixel2, y_pixel2 + 1, np.uint8(255 * fpart(y_end) * x_gap)))

    # Основной цикл
    for x in range(x_pixel1 + 1, x_pixel2):
        if steep:
            pixels.append((ipart(intery), x, np.uint8(255 * rfpart(intery))))
            pixels.append((ipart(intery) + 1, x, np.uint8(255 * fpart(intery))))
        else:
            pixels.append((x, ipart(intery), np.uint8(255 * rfpart(intery))))
            pixels.append((x, ipart(intery) + 1, np.uint8(255 * fpart(intery))))
        intery += gradient

    return pixels
