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


def random_lines(n: int) -> list:
    """
    Creates n random lines inside the screen.
    Lines are sorted by the x coordinate of their intersection with a
    horizontal zone line with :math:`y` coordinate of 0.

    :param int n: Number of lines to create
    :return: A list of lines
    :rtype: list[numpy.ndarray]
    """

    zone_line = (point(-MAX_X, 0), point(MAX_X, 0))

    seed(time())

    # generate n random lines by generating 2n random points on the border
    # every line is chosen to cross the horizontal zone line with y=0
    def random_border_pair():
        # For the top point, pick the left (0), top (1), or right (2) side
        top_side = choice(range(0, 3))

        # left side
        if top_side == 0:
            pt1 = point(-MAX_X, uniform(0, MAX_Y))
            bottom_side = choice(range(1, 3))
        # top side
        elif top_side == 1:
            pt1 = point(uniform(-MAX_X, MAX_X), MAX_Y)
            bottom_side = choice(range(0, 3, 2))
        # right side
        else:
            pt1 = point(MAX_X, uniform(0, MAX_Y))
            bottom_side = choice(range(0, 2))

        # left side
        if bottom_side == 0:
            pt2 = point(-MAX_X, uniform(-MAX_Y, 0))
        # bottom side
        elif bottom_side == 1:
            pt2 = point(uniform(-MAX_X, MAX_X), -MAX_Y)
        # left side
        else:
            pt2 = point(MAX_X, uniform(-MAX_Y, 0))

        return (pt1, pt2)

    lines = [random_border_pair() for _ in range(n)]

    # Get a key for a line based on x coordinate intersection with zone line
    def seg_cmp(line):
        intersection = segment_intersection(*zone_line, *line)
        return -MAX_X - 1 if intersection is None else intersection[0]

    return sorted(lines, key=seg_cmp)


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
    :func:`src.animations.draw_arrangement.random_lines`.
    """

    def setup(self):
        """:meta private:"""

        self.lines = random_lines(10)


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


class DrawProofBaseCase(Scene):
    """
    Animates the base case of the zone theorem by showing that adding the first
    line only adds 1 left bounding edge.
    """

    def construct(self):
        """:meta private:"""

        heading = Text("Proof: Base Case")
        heading.scale(1.5)
        heading.to_edge(UP)
        self.add(heading)

        statement = Tex("Trivially 1 left edge for $n = 1$")
        self.play(Write(statement), run_time=1.5)

        self.wait(2)
        self.clear()

        # Initialize self.lines for the draw arrangement
        self.lines = [(point(-MAX_X + 2, -MAX_Y), point(MAX_X - 2, MAX_Y))]
        DrawArrangement.setup(self)
        DrawArrangement.construct(self)

        # Draw red zone line
        zone_line = Line(point(-MAX_X, 0), point(MAX_X, 0), color=RED)
        self.play(ShowCreation(zone_line))

        # Highlight drawn line as left edge
        highlight_line = Line(*self.lines[0], color=GREEN, stroke_width=10)
        self.play(ShowCreation(highlight_line))


class DrawProofInductiveCase(Scene):
    """
    Animates the inductive step of the proof of the zone theorem by showing
    that adding the rightmost line only adds at most 3 edges: 2 splitting the
    left edges above and below the zone line, and one edge from the added line
    itself.
    """

    def construct(self):
        """:meta private:"""

        # Show our assumption going into the inductive step
        heading = Text("Proof: Inductive Step")
        heading.scale(1.5)
        heading.to_edge(UP)
        self.add(heading)

        assumption = Tex(
            r"Assume true for all lines in $L$ except $\ell_r$, the rightmost line in $L$.\\",
            tex_environment="flushleft",
        )
        assumption.shift(2 * UP)

        equation = MathTex(
            r"\bigg\lvert \text{zone}\left(A(L \setminus \{\ell_r\}), \ell\right) \bigg\rvert",
            r"\leq",
            r"3(n-1)",
            tex_environment="equation*",
        )
        equation.next_to(assumption, DOWN)
        self.play(Write(assumption), run_time=2)
        self.play(Write(equation), run_time=2)

        self.wait(2)
        self.clear()

        # Draw all the lines except the last one
        all_lines = random_lines(5)
        self.lines = all_lines[:-1]

        # sets self.bps for us
        DrawArrangement.setup(self)
        DrawArrangement.construct(self)

        # Draw the red zone line
        zone_line = (point(-MAX_X, 0), point(MAX_X, 0))
        self.play(ShowCreation(Line(*zone_line, color=RED)))

        # change the last line to be vertical
        # this isn't necessary for the proof, but it makes illustration easier
        last_line_x = segment_intersection(*zone_line, *all_lines[-1])[0]
        last_line = (point(last_line_x, -MAX_Y), point(last_line_x, MAX_Y))

        # Keep track of edges of rightmost polygon in the zone
        last_polygon = self.bps.find_zone(zone_line)[-1]
        before_add_edges = {
            (tuple(last_polygon[i]), tuple(last_polygon[i + 1]))
            for i in range(len(last_polygon))
        }

        # Add the rightmost line
        self.bps.add_line(last_line)
        self.play(ShowCreation(Line(*last_line)))

        # Keep track of edges of rightmost polygon in the zone
        last_polygon = self.bps.find_zone(zone_line)[-1]
        after_add_edges = {
            (tuple(last_polygon[i]), tuple(last_polygon[i + 1]))
            for i in range(len(last_polygon))
        }

        # The difference in edges are the added left edges
        for line in after_add_edges - before_add_edges:
            # This edge is the 1 added by the line itself
            if round(line[0][0] - line[1][0], 7) == 0:
                self.play(ShowCreation(Line(*line, color=GREEN, stroke_width=10)))
            # These edges are the 2 added by subdividing above and below lines
            else:
                self.play(ShowCreation(Line(*line, color=YELLOW, stroke_width=10)))

        self.wait(3)
        self.clear()

        # Now conclude we added 3 lines
        equation.scale(0.75)
        equation.next_to(heading, DOWN)
        self.add(heading, equation)

        list_heading = Tex(
            r"\underline{Added Edges}",
            tex_environment="flushleft",
        )
        list_heading.scale(0.75)
        list_heading.to_edge(LEFT)
        list_heading.shift(UP)
        # TODO: Is there a way to color text in bulleted lists?
        added_list = BulletedList(
            "$\ell_r$  itself (+1)",
            "Subdivide above, below (+2)",
            tex_environment="flushleft",
        )
        added_list.scale(0.75)
        added_list.next_to(list_heading, DOWN, aligned_edge=LEFT)

        self.play(Write(list_heading))
        self.play(Write(added_list), run_time=2)

        self.wait(2)

        # TODO: There has to be a better way to animate algebra than this
        final_equation1 = MathTex(
            r"\bigg\lvert \text{zone}\left(A(L, \ell)\right) \bigg\rvert",
            r"\leq",
            r"\bigg\lvert \text{zone}\left(A(L \setminus \{\ell_r\}), \ell\right) \bigg\rvert",
            r"+1",
            r"+2",
            tex_environment="equation*",
        )
        final_equation2 = MathTex(
            r"\bigg\lvert \text{zone}\left(A(L, \ell)\right) \bigg\rvert",
            r"\leq",
            r"3(n-1)",
            r"+1",
            r"+2",
            tex_environment="equation*",
        )
        final_equation3 = MathTex(
            r"\bigg\lvert \text{zone}\left(A(L, \ell)\right) \bigg\rvert",
            r"\leq",
            r"3n-3",
            r"+1",
            r"+2",
            tex_environment="equation*",
        )
        final_equation4 = MathTex(
            r"\bigg\lvert \text{zone}\left(A(L, \ell)\right) \bigg\rvert",
            r"\leq",
            r"3n",
            r"-3",
            r"+3",
            tex_environment="equation*",
        )
        final_equation5 = MathTex(
            r"\bigg\lvert \text{zone}\left(A(L, \ell)\right) \bigg\rvert",
            r"\leq",
            r"3n",
            r"",
            r"",
            tex_environment="equation*",
        )
        final_equation6 = MathTex(
            r"\bigg\lvert \text{zone}\left(A(L, \ell)\right) \bigg\rvert",
            r"=",
            r"O(n)",
            r"\hspace{1cm}",
            r"\blacksquare",
            tex_environment="equation*",
        )
        final_equation1.to_edge(DOWN)
        final_equation2.to_edge(DOWN)
        final_equation3.to_edge(DOWN)
        final_equation4.to_edge(DOWN)
        final_equation5.to_edge(DOWN)
        final_equation6.to_edge(DOWN)

        self.play(Write(final_equation1[:2]))
        self.play(ReplacementTransform(equation[0].copy(), final_equation1[2]))
        self.play(Write(final_equation1[-2:]))

        self.play(ReplacementTransform(final_equation1, final_equation2))
        self.wait(2)
        self.play(ReplacementTransform(final_equation2, final_equation3))
        self.wait(2)
        self.play(ReplacementTransform(final_equation3, final_equation4))
        self.wait(2)
        self.play(ReplacementTransform(final_equation4, final_equation5))
        self.wait(2)
        self.play(ReplacementTransform(final_equation5, final_equation6))
        self.wait(2)
