from manim import Scene, ShowCreation, VGroup
from manim.animation.transform import MoveToTarget
from manim.mobject.geometry import Line, Dot, DashedLine
from manim.utils.color import BLUE, RED, GREEN

from random import uniform, seed
from time import time

from screen_constants import MAX_X

from data_structures.polygon import Polygon
from data_structures.point import point
from data_structures.utils import orient

from math import sin, cos, pi


# Make a random polygon where all points are co-circular.
# This is basically a lazy way to make a random-ish convex polygon
def random_circular_polygon(sides: int, radius: int) -> Polygon:
    seed(time())
    return Polygon(
        [
            radius * point(cos(t), sin(t))
            for t in sorted([uniform(0, 2 * pi) for _ in range(sides)])
        ]
    )


class DrawBoundingEdges(Scene):
    """
    This scene is meant to illustrate what left and right bounding edges are.
    It draws a convex polygon.
    It then draws a red line through the screen like in the zone animation.
    Points are then added to each side of this line and brought to "infinity"
    (really just kinda far from the polygon) tangent lines are then drawn, to
    the shape
    """

    def construct(self):
        # make a "random" convex polygon
        self.polygon = random_circular_polygon(12, 2)

        # convert it to a manim object and draw it
        manim_polygon = VGroup(
            *[
                Line(self.polygon[i], self.polygon[i + 1])
                for i in range(len(self.polygon))
            ]
        )
        self.play(ShowCreation(manim_polygon))

        # Draw red line through polygon
        left_point, right_point = point(-MAX_X, 0), point(MAX_X, 0)
        red_line = Line(left_point, right_point, color=RED)
        self.play(ShowCreation(red_line))

        # Add a left and right point on the red line, then move them far-ish away
        manim_left_point, manim_right_point = Dot(left_point / 2), Dot(right_point / 2)
        manim_left_point.target = Dot(3 * left_point)
        manim_right_point.target = Dot(3 * right_point)
        self.play(ShowCreation(manim_left_point), ShowCreation(manim_right_point))
        self.play(
            MoveToTarget(
                manim_left_point,
            ),
            MoveToTarget(manim_right_point),
            run_time=2.5,
        )

        # Get min and max y points that separate polygon into left and right bounding edges
        min_y = min(self.polygon, key=lambda p: p[1])
        max_y = max(self.polygon, key=lambda p: p[1])

        # Draw lines from left and right points to min and max points
        left_lines = VGroup(
            *[
                DashedLine(manim_left_point.target, min_y),
                DashedLine(manim_left_point.target, max_y),
            ]
        )
        right_lines = VGroup(
            *[
                DashedLine(manim_right_point.target, min_y),
                DashedLine(manim_right_point.target, max_y),
            ]
        )
        self.play(ShowCreation(left_lines), ShowCreation(right_lines))

        left_points = [pt for pt in self.polygon if orient(max_y, min_y, pt) >= 0]
        right_points = [pt for pt in self.polygon if orient(min_y, max_y, pt) >= 0]

        # orient left and right parts ccw
        for i in range(len(left_points)):
            if all(left_points[i] == min_y):
                left_points = left_points[i:] + left_points[:i]
                break
        for i in range(len(right_points)):
            if all(right_points[i] == max_y):
                right_points = right_points[i:] + right_points[:i]
                break

        # Convert parts into manim objects
        left_lines = VGroup(
            *[
                Line(left_points[i], left_points[i + 1], color=BLUE, stroke_width=10)
                for i in range(len(left_points) - 1)
            ]
        )
        right_lines = VGroup(
            *[
                Line(right_points[i], right_points[i + 1], color=GREEN, stroke_width=10)
                for i in range(len(right_points) - 1)
            ]
        )

        # show manim objects
        self.play(ShowCreation(left_lines))
        self.play(ShowCreation(right_lines))

        self.wait(5)
