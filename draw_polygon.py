from manim import *
from random import uniform

from data_structures.point import point
from data_structures.polygon import Polygon

# bounds on size of screen
from screen_constants import MAX_X, MAX_Y


class DrawPolygon(Scene):
    def construct(self):
        # Create all the points
        manim_points = VGroup(*[Dot(point, radius=0.05) for point in self.polygon])
        self.play(ShowCreation(manim_points))

        p0 = self.polygon[0]

        # This line will start on the left side of the screen and move right to the leftmost point
        left_line = Line(point(-MAX_X, MAX_Y), point(-MAX_X, -MAX_Y), color=RED)
        angle_line = Line(point(p0[0], MAX_Y), point(p0[0], -MAX_Y), color=RED)
        self.play(ReplacementTransform(left_line, angle_line), run_time=1.5)
        self.wait(1)

        for i in range(1, len(self.polygon) + 1):
            # the line will rotate until it hits a point
            new_angle_line = Line(
                p0 - MAX_X * (self.polygon[i] - p0),
                p0 + MAX_X * (self.polygon[i] - p0),
                color=RED,
            )
            self.play(ReplacementTransform(angle_line, new_angle_line), run_time=0.5)
            angle_line = new_angle_line

            # We'll draw another edge in out simple polygon
            polygon_line = Line(self.polygon[i - 1], self.polygon[i], color=BLUE)
            self.play(ShowCreation(polygon_line), run_time=0.5)

        self.wait(5)


class DrawSimplePolygon(DrawPolygon):
    def setup(self):
        # number of points
        n = 32

        # make n random points on the screen
        def rand_point():
            return point(uniform(-MAX_X + 1, MAX_X), uniform(-MAX_Y, MAX_Y))

        points = [rand_point() for _ in range(n)]

        # select the leftmost
        i, p0 = min(enumerate(points), key=lambda x: x[1][0])
        points.pop(i)

        # sort all other points by their angle relative to the leftmost
        points = [p0] + sorted(
            points[1:], key=lambda p: (p[1] - p0[1]) / (p[0] - p0[0])
        )

        # draw that simple polygon
        self.polygon = Polygon(points)
