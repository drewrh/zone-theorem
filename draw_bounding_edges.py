"""
Contains an animation to illustrate the concept of left and right bounding edges.

:Authors:
    - William Boyles (wmboyles)
"""

from manim import Scene, VGroup
from manim.animation.creation import Write, ShowCreation
from manim.animation.transform import ReplacementTransform
from manim.mobject.geometry import Line, DashedLine
from manim.mobject.svg.text_mobject import Text
from manim.constants import DOWN, LEFT, RIGHT, UP
from manim.utils.color import RED, GREEN, BLUE

from random import uniform, seed
from time import time

from screen_constants import MAX_X

from data_structures.polygon import Polygon
from data_structures.point import point
from data_structures.utils import orient

from math import sin, cos, pi


def random_circular_polygon(sides: int, radius: float) -> Polygon:
    """
    Creates a polygon with a given number of sides where all vertices are on a
    circle of a given radius.
    This ensures the polygon is convex.

    :param int sides: number of sides in polygon
    :param float radius: radius of circle on which all polygon vertices will
        sit
    :return: A convex polygon with the given number of sides and all points on
        a circle of the given radius.
    :rtype: :class:`data_structures.polygon.Polygon`
    """

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

    :Authors:
        - William Boyles (wmboyles)
    """

    def construct(self):
        # make a "random" convex polygon
        polygon_radius = 2.5
        self.polygon = random_circular_polygon(sides=12, radius=polygon_radius)

        # Draw the random convex polyogn
        manim_polygon = VGroup(
            *[
                Line(self.polygon[i], self.polygon[i + 1])
                for i in range(len(self.polygon))
            ]
        )
        self.play(ShowCreation(manim_polygon))

        # Draw red line through polygon like in zone animation
        red_line = Line(point(-MAX_X, 0), point(MAX_X, 0), color=RED)
        self.play(ShowCreation(red_line))

        # Get min and max y points that separate polygon into left and right bounding edges
        min_y = min(self.polygon, key=lambda p: p[1])
        max_y = max(self.polygon, key=lambda p: p[1])

        # Create horizontal lines at these points
        top_line = DashedLine(point(-MAX_X, max_y[1]), point(MAX_X, max_y[1]))
        bottom_line = DashedLine(point(-MAX_X, min_y[1]), point(MAX_X, min_y[1]))

        # Draw horizontal lines above max_y and below
        above_line = DashedLine(point(-MAX_X, max_y[1] + 1), point(MAX_X, max_y[1] + 1))
        below_line = DashedLine(point(-MAX_X, min_y[1] - 1), point(MAX_X, min_y[1] - 1))
        self.play(ShowCreation(above_line), ShowCreation(below_line))

        # Move lines tangent to polygon via transformation
        self.play(
            ReplacementTransform(above_line, top_line),
            ReplacementTransform(below_line, bottom_line),
        )

        # Determine which edges are left and right bounding
        left_points = [pt for pt in self.polygon if orient(max_y, min_y, pt) >= 0]
        right_points = [pt for pt in self.polygon if orient(min_y, max_y, pt) >= 0]

        # orient left and right bounding edges ccw
        for i in range(len(left_points)):
            if all(left_points[i] == min_y):
                left_points = left_points[i:] + left_points[:i]
                break
        for i in range(len(right_points)):
            if all(right_points[i] == max_y):
                right_points = right_points[i:] + right_points[:i]
                break

        # Draw bounding edges
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

        self.play(ShowCreation(left_lines))
        self.play(ShowCreation(right_lines))

        # Add text labeling which sides are left and right bounding
        left_label = Text("Left bounding edges", size=0.5, color=GREEN)
        left_label.shift(1.7 * polygon_radius * LEFT + UP)

        right_label = Text("Right bounding edges", size=0.5, color=BLUE)
        right_label.shift(1.7 * polygon_radius * RIGHT + DOWN)

        self.play(Write(left_label), Write(right_label))

        self.wait(5)
