from random import choice, seed, uniform
from time import time

from manim import *

from ..data_structures.point import point
from ..data_structures.polygonal_subdivision import BoundedPolygonalSubdivision as BPS
from ..data_structures.utils import segment_intersection
from .screen_constants import MAX_X, MAX_Y


def random_lines(n: int, zone_line: tuple = None) -> list:
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


class DrawArrangement(Scene):
    """
    General code to draw an arrangment of lines.
    Stores the arrangment as a :class:`data_structures.polygonal_subdivision.BoundedPolygonalSubdivision` as `self.bps`.

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
    Extends :class:`animations.draw_arrangement.DrawArrangement`.
    Iniitalizes `self.lines` with 10 (can be changed) random lines from
    :func:`animations.draw_arrangement.random_lines`.

    :Authors:
        - William Boyles (wmboyles)
    """

    def setup(self):
        """:meta private:"""

        self.lines = random_lines(10)
