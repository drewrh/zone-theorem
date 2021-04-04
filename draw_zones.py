# Some stuff for randomization
from random import choice, seed, uniform
from time import time

from manim import *

from screen_constants import MAX_X, MAX_Y

from data_structures.point import point
from data_structures.polygonal_subdivision import BoundedPolygonalSubdivision as BPS


class DrawZone(Scene):
    """
    This is some general code to show the creation of a polygonal subdivision,
    draw a red line defining a zone in that subdivision, and highlight all
    polygons that are a part of the zone.

    It requires a class to extend it and initialize it with a set of boundary
    lines as self.lines.
    """

    def construct(self):
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

        # Draw all intersections of lines
        intersections = [h.point for h in b.point_dict.values()]
        self.play(
            *[
                ShowCreation(Dot(intersection, color=DARK_BLUE))
                for intersection in intersections
            ]
        )

        # Create and draw the red line that defines the zone
        manim_zone_line = Line(*self.zone_line, color=RED)
        self.bring_to_front(manim_zone_line)
        self.play(ShowCreation(manim_zone_line))

        # Draw the zone
        zone = b.find_zone(self.zone_line)
        manim_zone = VGroup(
            *[
                Polygon(*polygon.points, color=GREEN, fill_opacity=0.5)
                for polygon in zone
            ]
        )
        self.bring_to_back(manim_zone)
        self.play(ShowCreation(manim_zone), run_time=len(zone))

        self.wait(5)


class DrawRandomZone(DrawZone):
    """
    Draws a random zone of :math:`n` lines.
    """

    def setup(self):
        # number of lines
        n = 10

        seed(time())

        # generate n random lines by generating 2n random points on the border
        def random_border_pair():
            sides = [0, 1, 2, 3]
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

        self.lines = [random_border_pair() for _ in range(n)]
        self.zone_line = (point(-MAX_X, 0), point(MAX_X, 0))


class DrawGridZone(DrawZone):
    """
    Draws a grid of lines with a slanted zone line.
    Note how if there are :math:`2n` white lines drawn, there are :math:`n+1`
    rows and columns for a total of :math:`(n+1)^2` rectangular polygons.
    In each row or column, the zone line crosses a constant number of polygons.
    So, the zone line crosses :math:`O(n)` polygons.
    Each polygon has a constant number of sides (in this case 4) so the zone
    contains :math:`O(n)` edges.
    """

    def setup(self):
        horizontal_lines = [
            (point(-MAX_X, y + 0.5), point(MAX_X, y + 0.5))
            for y in range(-MAX_Y, MAX_Y)
        ]
        vertical_lines = [
            (point(x, -MAX_Y), point(x, MAX_Y)) for x in range(-MAX_X + 1, MAX_X)
        ]

        self.lines = horizontal_lines + vertical_lines
        self.zone_line = (point(-MAX_X, -MAX_Y), point(MAX_X, MAX_Y))
