"""
Contains an animations to illustrate the concept of left and right bounding
edges of a polygon with respect to a zone line.

:Authors:
    - William Boyles (wmboyles)
"""

from math import cos, pi, sin
from random import seed, uniform
from time import time

from manim import *

from ..data_structures.point import point

# Have to rename to avoid conflict with manim's Polygon class
from ..data_structures.polygon import Polygon as BoundingPolygon
from ..data_structures.utils import orient
from .screen_constants import MAX_X


class DrawBoundingEdges(Scene):
    """
    This scene is meant to illustrate what left and right bounding edges are.
    It draws a convex polygon.
    It then draws a red line through the screen like in the zone animation.
    It then draws lines above and below the polygon, parallel to the zone line,
    which find the two points on the polygon that separate the elft and right
    sides.

    It requires that a calling or extending class initialize
    `self.show_rotation` to either `True` or `False`.
    If true, it will show how left and right bounding edges swap under a 180
    degree rotation.
    """

    @classmethod
    def random_circular_polygon(cls, sides: int, radius: float) -> BoundingPolygon:
        """
        Creates a polygon with a given number of sides where all vertices are on
        a circle of a given radius. This ensures the polygon is convex like in
        an arrangement of lines.

        :param int sides: number of sides in polygon
        :param float radius: radius of circle on which all polygon vertices will
            sit
        :return: A convex polygon with the given number of sides and all points on
            a circle of the given radius.
        :rtype: :class:`src.data_structures.polygon.Polygon`
        """

        seed(time())
        return BoundingPolygon(
            [
                radius * point(cos(t), sin(t))
                for t in sorted([uniform(0, 2 * pi) for _ in range(sides)])
            ]
        )

    def construct(self):
        """:meta private:"""

        # make a "random" convex polygon
        polygon_radius = 2.5
        self.polygon = DrawBoundingEdges.random_circular_polygon(
            sides=12, radius=polygon_radius
        )

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

        if not self.show_rotation:
            return

        # Show how left and right edges swap under rotation
        to_rotate = VGroup(
            manim_polygon,
            left_lines,
            right_lines,
            top_line,
            bottom_line,
            left_label,
            right_label,
            red_line,
        )

        self.play(Rotating(to_rotate, radians=PI, run_time=2))
        self.wait(1)

        new_left_label = Text("Left bounding edges", size=0.5, color=BLUE)
        new_left_label.move_to(right_label)
        new_right_label = Text("Right bounding edges", size=0.5, color=GREEN)
        new_right_label.move_to(left_label)

        self.play(
            ReplacementTransform(right_label, new_left_label),
            ReplacementTransform(left_label, new_right_label),
        )


class DrawBoundingEdgesDefinition(Scene):
    """
    This animation gives a definition of what bounding edges are and draws the
    left and right bounding edges on a random convex polygon using
    :class:`src.animations.draw_bounding_edges.DrawBoundingEdges`.
    """

    def construct(self):
        """:meta private:"""
        self.show_rotation = False

        heading = Text("Counting Edges")
        heading.scale(1.5)
        heading.to_edge(UP)
        self.add(heading)

        definition = Tex(
            r"\textbf{Definition: } The \underline{left bounding edges} of a convex polygon $P$\\",
            r"with respect to a horizontal line $\ell$ are all edges of $P$ that\\",
            r"are visible from a point infinitely far to the left on $\ell$.\\",
            r"All edges of $P$ are either left or right bounding.",
            tex_environment="flushleft",
        )
        definition.to_edge(LEFT)
        definition.shift(UP)

        self.play(Write(definition), run_time=7)
        self.wait(3)

        self.clear()

        DrawBoundingEdges.setup(self)
        DrawBoundingEdges.construct(self)

        self.wait(5)
        self.clear()

        self.add(heading, definition)
        idea = Tex(
            r"\textbf{Idea:} Count left and right bounding edges separately.",
            tex_environment="flushleft",
        )
        idea.to_edge(LEFT)
        idea.shift(2 * DOWN)

        self.play(Write(idea), run_time=2)


class DrawWhatAboutRightEdges(Scene):
    """
    This animation demonstrates why our proof of showing there are :math:`O(n)`
    left bounding edges also works to show there are :math:`O(n)` right
    bounding edges.
    We can simply rotate our view by 180 degrees and see that the right
    bounding edges of every polygon in the zone become the left bounding edges.
    So, we could simply go through the steps of our proof again to get
    :math:`O(n)` right bounding edges for the same arrangment.
    Since every edge is either left or right bounding and
    :math:`O(n) + O(n) = O(n)`, we have proved the zone theorem.
    """

    def construct(self):
        """:meta private:"""

        heading = Text("What about Right Edges?")
        heading.scale(1.5)
        heading.to_edge(UP)
        self.add(heading)

        statement = Text("Just Rotate!")
        self.play(Write(statement), run_time=1.5)

        self.wait(2)
        self.clear()

        self.show_rotation = True
        DrawBoundingEdges.setup(self)
        DrawBoundingEdges.construct(self)

        self.wait(3)
        self.clear()

        self.add(heading, statement)
        self.wait(2)

        equation = Tex(
            r"$O(n)$ left edges $+$ $O(n)$ right edges = $O(n)$ total $\hspace{1cm} \blacksquare$",
            tex_environment="flushleft",
        )
        equation.to_edge(DOWN)
        self.play(Write(equation), run_time=2)
