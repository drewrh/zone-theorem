"""
This file contains animations that relate to zones, like defining and drawing
them.

:Authors:
    - William Boyles
"""

from manim import *

from ..data_structures.point import point
from .draw_arrangement import DrawArrangement, DrawRandomArrangement
from .screen_constants import MAX_X


class DrawZone(DrawArrangement):
    """
    General code to show the zone of an arrangement of lines.
    Draws an arrangement of while lines and a red zone line.
    Then highlights all polygons that are part of the zone of the red line.

    Requires a class to extend it and initialize it with the following:
        * `self.lines` -- A list of lines defining an arrangment of lines
        * `self.zone_line` -- A line defining a zone
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
    Extends :class:`src.animations.draw_zones.DrawZone` and
    :class:`src.animations.draw_arrangement.DrawRandomArrangement`. Initializes
    `self.zone_line` with a horizontal line with :math:`y` coordinate of 0.
    """

    def setup(self):
        """:meta private:"""

        # sets self.lines for us
        DrawRandomArrangement.setup(self)

        self.zone_line = (point(-MAX_X, 0), point(MAX_X, 0))


class DrawZoneDefintion(Scene):
    """
    Asks a motivating question about arrangments of lines that naturally leads
    to the idea of zones. Writes a formal defintion of the zone of a line in an
    arrangment of lines. Draws an example of the definition using
    :class:`src.animations.draw_zone.DrawRandomZone`.
    """

    def construct(self):
        """:meta private:"""

        # Ask motivating question
        question = Tex(r"How many edges do we visit\\when adding a line?\\")
        question.scale(2)
        question.to_edge(UP)
        self.add(question)
        self.wait(2)

        # Give an answer
        answer = Tex(r"At most every edge in every polygon the new line crosses")
        answer.scale(0.75)
        self.play(Write(answer))
        self.wait(2)

        self.clear()

        # Write the defintion of a zone
        definition = Tex(
            r"\textbf{Definition: } Let $A(L)$ be an arrangement of lines.\\",
            r"Let $\ell$ be a line in the plane. ",
            r"The \underline{zone} of $\ell$ in $A(L)$\\is the set of polygons in $A(L)$ that $\ell$ crosses.",
            tex_environment="flushleft",
        )
        definition.to_corner(UL)

        self.play(Write(definition), run_time=3)
        self.wait(2)

        self.clear()

        # Draw a random example of the definition
        DrawRandomZone.setup(self)
        DrawRandomZone.construct(self)
        self.wait(3)

        self.clear()

        # Bring back questions and ask about efficiency
        self.add(question, answer)
        self.wait(1)

        new_answer = Tex(r"Number of edges in the zone of $\ell$ in $A(L)$.")
        answer.scale(0.75)
        self.play(ReplacementTransform(answer, new_answer))

        question_list = BulletedList(
            "$O(n^2)$? (every edge)",
            "$O(n \log{n})$? (it shows up lots of other places)",
            "$O(n)$?",
        )
        question_list.to_edge(DOWN)
        question_list.shift(RIGHT)
        self.play(Write(question_list), run_time=3)
