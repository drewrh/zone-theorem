# Some stuff for randomization
from random import choice, seed, uniform
from time import time

from manim import *

from ..data_structures.point import point
from ..data_structures.polygonal_subdivision import BoundedPolygonalSubdivision as BPS
from ..data_structures.utils import orient, segment_intersection
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


def find_left_edges(polygon: Polygon) -> list:
    """
    Assuming the zone line is horizontal, finds the left bounding edge of a
    Polygon.

    :param data_structures.polygon.Polygon polygon: The polygon of which to
        find the left bounding edges.
    :return: A list of points, `left_points` that defines the left edges of the
        polygon. These points are ordered such that the edge between the
        :math:`i` th and :math:`i+1` th point are a left bounding edge, for
        :math:`i \in [0,\ldots,\\texttt{len(left_points)}-1]`.
    :rtype: list[numpy.ndarray]
    """

    # Assumes zone line is horizontal and through polygon
    max_y = max(polygon, key=lambda pt: pt[1])
    min_y = min(polygon, key=lambda pt: pt[1])

    left_points = [pt for pt in polygon if orient(min_y, max_y, pt) >= 0]
    for i in range(len(left_points)):
        if all(left_points[i] == min_y):
            left_points = left_points[i:] + left_points[:i]

    return left_points


class DrawZone(Scene):
    """
    General code to show the zone of an arrangement of lines.
    Draws an arrangement of while lines and a red zone line.
    Then highlights all polygons that are part of the zone of the red line.

    Requires a class to extend it and initialize it with the following:
        * `self.lines` -- A list of lines defining an arrangment of lines
        * `self.zone_line` -- A line defining a zone

    :Authors:
        - William Boyles (wmboyles)
    """

    def construct(self):
        """:meta private:"""

        # Create a bounding box data structure
        b = BPS(point(-MAX_X, -MAX_Y), point(MAX_X, MAX_Y))

        # Draw a bounding box
        box = Rectangle(height=2 * MAX_Y, width=2 * MAX_X)
        self.play(ShowCreation(box))

        # Create and draw the BPS lines
        manim_lines = []
        for line in self.lines:
            b.add_line(line)
            manim_lines.append(Line(*line))
        manim_lines = VGroup(*manim_lines)

        self.play(ShowCreation(manim_lines), run_time=len(self.lines))

        # Create and draw the red line that defines the zone
        manim_zone_line = Line(*self.zone_line, color=RED)
        self.bring_to_front(manim_zone_line)
        self.play(ShowCreation(manim_zone_line))

        # Draw the zone
        self.zone = b.find_zone(self.zone_line)
        manim_zone = VGroup(
            *[
                Polygon(*polygon.points, color=GREEN, fill_opacity=0.5)
                for polygon in self.zone
            ]
        )
        self.bring_to_back(manim_zone)
        self.play(ShowCreation(manim_zone), run_time=len(self.zone))


class DrawRandomZone(DrawZone):
    """
    Extends :class:`animations.draw_zones.DrawZone`.
    Initializes `self.lines` with 10 (can be changed) random lines from
    :func:`animations.draw_zones.random_lines`. Initializes `self.zone_line`
    with a horizontal line with :math:`y` coordinate of 0.

    :Authors:
        - William Boyles (wmboyles)
    """

    def setup(self):
        """:meta private:"""

        self.zone_line = (point(-MAX_X, 0), point(MAX_X, 0))
        self.lines = random_lines(10, self.zone_line)


class DrawGridZone(DrawZone):
    """
    Extends :class:`animations.draw_zones.DrawZone`. Draws a rectangular grid
    of lines with a slanted zone line. Note that although there are
    :math:`O(n^2)` total line segments, the zone line crosses at most a
    constant number of polygons in each row or column, and each polygon has a
    constant number of edges. Therefore, there are :math:`O(n)` edges in the
    zone.

    :Authors:
        - William Boyles
    """

    def setup(self):
        """:meta private:"""

        horizontal_lines = [
            (point(-MAX_X, y + 0.5), point(MAX_X, y + 0.5))
            for y in range(-MAX_Y, MAX_Y)
        ]
        vertical_lines = [
            (point(x, -MAX_Y), point(x, MAX_Y)) for x in range(-MAX_X + 1, MAX_X)
        ]

        self.lines = horizontal_lines + vertical_lines
        self.zone_line = (point(-MAX_X, -MAX_Y), point(MAX_X, MAX_Y))


class DrawLeftBoundingZone(DrawZone):
    """
    Extends :class:`animations.draw_zones.DrawZone` to not only draw the zone
    of a line, but also show the left bounding edges of each polygon in the
    zone. Like :class:`animations.draw_zones.DrawZone`, this class needs be be
    extended and initialized with `self.lines` to define the arrangment of
    lines. However, this class does not need to be initialized with
    `self.zone_line`, as it assumes the the zone line is horizontal with
    :math:`y` coordinate of 0.

    :Authors:
        - William Boyles
    """

    def construct(self):
        """:meta private:"""

        self.zone_line = (point(-MAX_X, 0), point(MAX_X, 0))

        DrawZone.construct(self)

        # self.zone is set in DrawZone.construct()
        for polygon in self.zone:
            left_points = find_left_edges(polygon)
            left_edges = VGroup(
                *[
                    Line(left_points[i], left_points[i + 1], color=BLUE, stroke_width=7)
                    for i in range(len(left_points) - 1)
                ]
            )
            self.play(ShowCreation(left_edges))

        self.wait(5)


class DrawRandomLeftBoundingZone(DrawLeftBoundingZone):
    """
    Extends :class:`animations.draw_zones.DrawLeftBoundingZone`. Initializes
    `self.lines` with 10 (can be changed) random lines from
    :func:`animations.draw_zones.random_lines`.

    :Authors:
        - William Boyles (wmboyles)
    """

    def setup(self):
        """:meta private:"""

        self.lines = random_lines(10)
