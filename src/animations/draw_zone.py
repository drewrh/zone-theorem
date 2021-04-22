from manim import *

from ..data_structures.point import point
from ..data_structures.utils import orient
from .draw_arrangement import DrawArrangement, DrawRandomArrangement
from .screen_constants import MAX_X, MAX_Y


class DrawZone(DrawArrangement):
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

        # Draw the arrangement
        DrawArrangement.construct(self)

        # Create and draw the red line that defines the zone
        manim_zone_line = Line(*self.zone_line, color=RED)
        self.bring_to_front(manim_zone_line)
        self.play(ShowCreation(manim_zone_line))

        # Draw the zone
        self.zone = self.bps.find_zone(self.zone_line)
        manim_zone = VGroup(
            *[
                Polygon(*polygon.points, color=GREEN, fill_opacity=0.5)
                for polygon in self.zone
            ]
        )
        self.bring_to_back(manim_zone)
        self.play(ShowCreation(manim_zone), run_time=len(self.zone))


class DrawRandomZone(DrawZone, DrawRandomArrangement):
    """
    Extends :class:`animations.draw_zones.DrawZone` and
    :class:`animations.draw_arrangement.DrawRandomArrangement`. Initializes
    `self.zone_line` with a horizontal line with :math:`y` coordinate of 0.

    :Authors:
        - William Boyles (wmboyles)
    """

    def setup(self):
        """:meta private:"""

        # sets self.lines for us
        DrawRandomArrangement.setup(self)

        self.zone_line = (point(-MAX_X, 0), point(MAX_X, 0))
