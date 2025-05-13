from dataclasses import dataclass
from typing import List


@dataclass
class RGBA:
    """Represents an RGBA color value."""
    r: int  # Red component (0-255)
    g: int  # Green component (0-255)
    b: int  # Blue component (0-255) 
    a: int = 255  # Alpha/transparency component (0-255)

    def __post_init__(self):
        """Validate that all color components are within valid range 0-255"""
        color_components = ['r', 'g', 'b', 'a']

        for component in color_components:
            value = getattr(self, component)
            if not 0 <= value <= 255:
                raise ValueError(f"Color {component} value must be between 0 and 255")
    def __repr__(self):
        return f'RGBA({self.r}, {self.g}, {self.b}, {self.a})'


@dataclass
class Point:
    x: int
    y: int


@dataclass
class BaseObject:
    main_points: List[Point]  # Key points defining the object
    pixels: List[Point]  # Actual pixels to be drawn
    params: dict  # Additional parameters like radius, axes etc.
    color: RGBA  # Object color
    visible: bool = True  # Whether an object should be drawn
    selected: bool = False  # Whether an object is currently selected
    name: str = ""  # Optional name/label for the object
    layer: int = 0  # Layer number for draw order
    style: dict = None  # Visual style properties (line width, pattern, etc.)


@dataclass
class Line(BaseObject):
    """Represents a straight line between two points"""
    start: Point  # Starting point of the line
    end: Point  # Ending point of the line

    def __post_init__(self):
        if not isinstance(self.start, Point) or not isinstance(self.end, Point):
            raise ValueError("Line must have valid start and end points")


@dataclass
class Circle(BaseObject):
    """Represents a circle defined by center point and radius"""
    center: Point  # Center point of the circle
    radius: int  # Radius of the circle

    def __post_init__(self):
        if not isinstance(self.center, Point) or not isinstance(self.radius, int):
            raise ValueError("Circle must have valid center point and radius")


@dataclass
class Ellipse(BaseObject):
    """Represents an ellipse defined by a center point and two axes"""
    center: Point  # Center point of the ellipse
    major_axis: int  # Length of the major axis
    minor_axis: int  # Length of the minor axis

    def __post_init__(self):
        if not isinstance(self.center, Point) or not isinstance(self.major_axis, int) or not isinstance(self.minor_axis,
                                                                                                        int):
            raise ValueError("Ellipse must have valid center point and axis lengths")


@dataclass
class Curve(BaseObject):
    """Base class for parametric curves defined by control points"""
    control_points: List[Point]  # List of control points defining the curve

    def __post_init__(self):
        if not isinstance(self.control_points, list) or len(self.control_points) < 2 or not all(
                isinstance(p, Point) for p in self.control_points):
            raise ValueError("Curve must have at least 2 valid control points")


rgb = RGBA(255, 0, 0)
print(rgb)
