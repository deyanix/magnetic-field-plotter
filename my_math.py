from __future__ import annotations
import math
import numpy as np


class Point:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def distance_to_point(self, other: Point):
        return (self.to_vector() - other.to_vector()).length()

    def to_vector(self) -> Vector:
        return Vector(self.x, self.y, self.z)

    def transpile(self, vector: Vector) -> Point:
        transpiled = Vector.from_point(self) + vector
        return Point(transpiled.x, transpiled.y, transpiled.z)

    def __str__(self):
        return f"Point[{self.x}, {self.y}, {self.z}]"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Point):
            return False
        return self.x == o.x and self.y == o.y and self.z == o.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))


class LineSegment:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def distance_to_point(self, point: Point):
        p1_p2_v = Vector.by_points(self.p1, self.p2)
        p1_p_v = Vector.by_points(self.p1, point)
        p2_p_v = Vector.by_points(self.p2, point)
        angle1 = p1_p2_v.angle_to_vector(p1_p_v)
        angle2 = p1_p2_v.invert().angle_to_vector(p2_p_v)

        if angle1 > math.pi/2:
            return p1_p_v.length()
        if angle2 > math.pi/2:
            return p2_p_v.length()
        return self.to_line().distance_to_point(point)

    def distance_cast(self, point: Point) -> Point:
        p1_p2_v = Vector.by_points(self.p1, self.p2)
        p1_p_v = Vector.by_points(self.p1, point)
        p2_p_v = Vector.by_points(self.p2, point)
        angle1 = p1_p2_v.angle_to_vector(p1_p_v)
        angle2 = p1_p2_v.invert().angle_to_vector(p2_p_v)

        if angle1 > math.pi/2:
            return self.p1
        if angle2 > math.pi/2:
            return self.p2
        return self.to_line().perpendicular_cast(point)

    def line_vector(self) -> Vector:
        return self.to_line().v

    def to_line(self) -> Line:
        return Line.by_points(self.p1, self.p2)

    def __str__(self):
        return f"LineSegment[{self.p1}, {self.p2}]"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, LineSegment):
            return False
        return (self.p1 == o.p1 and self.p2 == o.p2) or (self.p1 == o.p2 and self.p2 == o.p1)

    def __hash__(self):
        return hash((self.p1, self.p2))


class Line:
    @staticmethod
    def by_points(p1: Point, p2: Point):
        return Line(p1, Vector.from_point(p1) - Vector.from_point(p2))

    def __init__(self, p: Point, v: Vector):
        self.p = p
        self.v = v

    def distance_to_point(self, point: Point):
        if self.v.length() == 0:
            print('KURWA DLACZEGO?', self.v)
        return Vector.by_points(self.p, point).vector_mul(self.v).length()/self.v.length()

    def distance_to_line(self, other: Line):
        w = self.v.vector_mul(other.v)
        v = w.scalar_mul(Vector.by_points(self.p, other.p))
        return abs(v)/w.length()

    def perpendicular_cast(self, point: Point) -> Point:
        p1_p_v = Vector.by_points(self.p, point)
        coeff = (p1_p_v.scalar_mul(self.v))/(self.v.invert().scalar_mul(self.v.invert()))
        return (coeff * self.v + self.p.to_vector()).to_point()

    def __str__(self):
        return f"Line[{self.p}, {self.v}]"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Line):
            return False
        return self.p == o.p and self.v == o.v

    def __hash__(self):
        return hash((self.p, self.v))


class Vector:
    @staticmethod
    def from_array(arr) -> Vector:
        return Vector(arr[0], arr[1], arr[2])

    @staticmethod
    def from_point(p: Point) -> Vector:
        return Vector(p.x, p.y, p.z)

    @staticmethod
    def by_points(p1: Point, p2: Point) -> Vector:
        return Vector.from_point(p2) - Vector.from_point(p1)

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def to_array(self):
        return np.array([self.x, self.y, self.z])

    def to_unit_vector(self):
        return Vector.from_array(self.to_array() / self.length())

    def angle_to_vector(self, other: Vector):
        return np.arccos((self.x * other.x + self.y * other.y + self.z * other.z) / (self.length() * other.length()))

    def vector_mul(self, other: Vector):
        matrix = np.array([self.to_array(), other.to_array()])
        x = np.linalg.det([matrix[:, 1], matrix[:, 2]])
        y = np.linalg.det([matrix[:, 0], matrix[:, 2]])
        z = np.linalg.det([matrix[:, 0], matrix[:, 1]])
        return Vector(x, -y, z)

    def scalar_mul(self, other: Vector):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def invert(self):
        return -1 * self

    def to_point(self, point = Point(0, 0, 0)):
        return point.transpile(self)

    def __mul__(self, c: float):
        return Vector(c*self.x, c*self.y, c*self.z)

    def __rmul__(self, c: float):
        return self.__mul__(c)

    def __add__(self, other: Vector):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector):
        return self + (-1 * other)

    def __abs__(self):
        return Vector(abs(self.x), abs(self.y), abs(self.z))

    def __str__(self):
        return f"Vector[{self.x}, {self.y}, {self.z}]"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Vector):
            return False
        return self.x == o.x and self.y == o.y and self.z == o.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))
