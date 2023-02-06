from __future__ import annotations
from typing import List
import cv2
import numpy as np
import plotly.graph_objs as go
from my_math import LineSegment, Point, Vector


class Graph:
    def __init__(self, lines: List[LineSegment], normal_vector=Vector(0, 0, 1)):
        self.lines = lines
        self.normal_vector = normal_vector

        points = []
        for line in lines:
            points.append(line.p1)
            points.append(line.p2)

        x = [p.x for p in points]
        y = [p.y for p in points]
        self.min_x = min(x)
        self.max_x = max(x)
        self.min_y = min(y)
        self.max_y = max(y)
        self.max_z = max(abs(self.max_x), abs(self.min_x), abs(self.max_y), abs(self.min_y)) / 10
        self.min_z = -self.max_z

    def show(self):
        rx = []
        ry = []
        rz = []
        cx = []
        cy = []
        cz = []
        for x in np.linspace(self.min_x, self.max_x, 41):
            for y in np.linspace(self.min_y, self.max_y, 41):
                for z in np.linspace(self.min_z, self.max_z, 21):
                    point = Point(x, y, z)
                    c_vector = Vector(0, 0, 0)
                    for line in self.lines:
                        if point is None:
                            continue

                        c_point = line.distance_cast(point)
                        r_vector = Vector.by_points(c_point, point)
                        if r_vector.length() < 3:
                            point = None
                            continue

                        line_vector = line.line_vector().to_unit_vector()
                        c_vector = c_vector + line_vector.vector_mul(r_vector) * (1 / (r_vector.length() ** 2))

                    if point is None:
                        continue

                    rx.append(point.x)
                    ry.append(point.y)
                    rz.append(point.z)
                    cx.append(c_vector.x)
                    cy.append(c_vector.y)
                    cz.append(c_vector.z)

        fig = go.Figure(data=go.Cone(
            x=rx,
            y=ry,
            z=rz,
            u=cx,
            v=cy,
            w=cz))
        for line in self.lines:
            fig.add_trace(
                go.Scatter3d(
                    x=[line.p1.x, line.p2.x],
                    y=[line.p1.y, line.p2.y],
                    z=[line.p1.z, line.p2.z],
                    mode='lines'))
        fig.update_layout(scene=dict(aspectmode="manual",
                                     camera_eye=dict(x=0, y=2, z=0)),
                          margin=dict(t=0, b=0, l=0, r=0))
        fig.show()


def linearize_image(path: str):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    detected_lines = cv2.HoughLinesP(gray, 1, np.pi / 180, 50)
    detected_lines = [LineSegment(Point(line[0][0], line[0][1], 0), Point(line[0][2], line[0][3], 0)) for line in detected_lines]
    detected_lines = [d_line for d_line in detected_lines if d_line.p1 != d_line.p2]
    return detected_lines


if __name__ == "__main__":
    lines = set(linearize_image("paths/path0.png"))
    removed_lines = set()
    for line1 in lines:
        if line1 in removed_lines:
            continue

        for line2 in lines:
            if line2 in removed_lines or line1 == line2:
                continue
            line1_v = line1.line_vector()
            line2_v = line2.line_vector()
            alpha = min(abs(line1_v.angle_to_vector(line2_v)), abs(line1_v.invert().angle_to_vector(line2_v)))
            distance = max(line1.distance_to_point(line2.p1), line1.distance_to_point(line2.p2))
            if alpha < np.pi / 45 and distance < 10:
                removed_lines.add(line2)
    [lines.remove(la) for la in removed_lines]
    for line1 in lines:
        for line2 in lines:
            if line1.p1.distance_to_point(line2.p1) < 10:
                line1.p1 = line2.p1
            if line1.p1.distance_to_point(line2.p2) < 10:
                line1.p1 = line2.p2
            if line1.p2.distance_to_point(line2.p1) < 10:
                line1.p2 = line2.p1
            if line1.p2.distance_to_point(line2.p2) < 10:
                line1.p2 = line2.p2

    graph = Graph([l for l in lines])
    graph.show()
