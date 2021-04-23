"""
This file contains animations related to arrangements of lines.
This includes defining them and drawing an example of them.

:Authors:
    - William Boyles
"""

from random import choice, seed, uniform
from time import time

from manim import *

from ..data_structures.point import point
from ..data_structures.polygonal_subdivision import BoundedPolygonalSubdivision as BPS
from ..data_structures.utils import segment_intersection
from .screen_constants import MAX_X, MAX_Y


class DrawArrangement(Scene):
    """
    General code to draw an arrangment of lines.
    Stores the arrangment as a :class:`src.data_structures.polygonal_subdivision.BoundedPolygonalSubdivision` as `self.bps`.

    Requires a class to extend it and initialize it with the following:
        * `self.lines` -- A list of lines defining an arrangment of lines
    """

    def construct(self):
        """:meta private:"""

        # Create a bounding box data structure
        self.bps = BPS(point(-MAX_X, -MAX_Y), point(MAX_X, MAX_Y))

        # Draw a bounding box
        box = Rectangle(height=2 * MAX_Y, width=2 * MAX_X)
        self.play(ShowCreation(box))

        # Create and draw the BPS lines
        manim_lines = []
        for line in self.lines:
            self.bps.add_line(line)
            manim_lines.append(Line(*line))
        manim_lines = VGroup(*manim_lines)

        self.play(ShowCreation(manim_lines), run_time=len(self.lines))


class DrawRandomArrangement(DrawArrangement):
    """
    Extends :class:`src.animations.draw_arrangement.DrawArrangement`.
    Iniitalizes `self.lines` with 10 (can be changed) random lines from
    :func:`src.animations.draw_arrangement.DrawRandomArrangement.random_lines`.
    """

    @classmethod
    def random_lines(cls, n: int, zone_line: tuple = None) -> list:
        """
        Creates n random lines inside the screen.
        Lines are sorted by the x coordinate of their intersection with the zone line.

        :param int n: Number of lines to create
        :param tuple[numpy.ndarray] zone_line: Line relative to which to sort lines. If `zone_line`
            is `None`, then it is assumed `zone_line` is the honrzontal line with a
            :math:`y` coordinate of 0.
        :return: A list of lines
        :rtype: list[numpy.ndarray]
        """

        if zone_line is None:
            zone_line = (point(-MAX_X, 0), point(MAX_X, 0))

        seed(time())

        # generate n random lines by generating 2n random points on the border
        def random_border_pair():
            sides = list(range(4))
            side1 = choice(sides)
            side2 = choice(sides[:side1] + sides[side1 + 1 :])

            def rand_side_point(side):
                x, y = uniform(-MAX_X, MAX_X), uniform(-MAX_Y, MAX_Y)
                if side == 0:
                    return point(-MAX_X, y)
                elif side == 1:
                    return point(x, MAX_Y)
                elif side == 2:
                    return point(MAX_X, y)
                elif side == 3:
                    return point(x, -MAX_Y)

            return (rand_side_point(side1), rand_side_point(side2))

        lines = [random_border_pair() for _ in range(n)]

        # Get a key for a line based on x coordinate intersection with zone line
        def seg_cmp(line):
            intersection = segment_intersection(*zone_line, *line)
            return -MAX_X - 1 if intersection is None else intersection[0]

        return sorted(lines, key=seg_cmp)

    def setup(self):
        """:meta private:"""

        self.lines = DrawRandomArrangement.random_lines(10)


class DrawArrangmementDefinition(Scene):
    """
    Writes the defintion of an arrangement of lines, draws an example of an
    arrangment of lines using :class:`src.animations.draw_arrangement.DrawRandomArrangement`,
    and lists some basic properties of arrangements.
    """

    def construct(self):
        """:meta private:"""

        # Defintion of an arrangment of lines
        definition = Tex(
            r"\textbf{Definition:} Let $L$ be a set of lines in the plane.\\"
            r"The \underline{arrangment of lines} $A(L)$ is the polygonal\\",
            r"subdivision induced by $L$.",
            tex_environment="flushleft",
        )
        definition.to_corner(UL)

        # Write the defintion of the screen
        self.play(Write(definition), run_time=3)
        self.wait(2)

        self.clear()

        # Draw a random example of the definition
        DrawRandomArrangement.setup(self)
        DrawRandomArrangement.construct(self)
        self.wait(2)

        self.clear()

        # Properties of an arrangment of lines
        self.add(definition)

        heading = Tex(r"Let $n = \lvert L \rvert$...", tex_environment="flushleft")
        heading.to_edge(LEFT)

        self.play(Write(heading))

        properties = BulletedList(
            "All polygons convex",
            "$O(n^2)$ vertices in subdivision ",
            "$O(n^2)$ total edges in all polygons",
            tex_environment="flushleft",
        )
        properties.to_edge(LEFT)
        properties.shift(2 * DOWN + 0.5 * RIGHT)
        self.play(Write(properties), run_time=len(properties))

        self.wait(2)
