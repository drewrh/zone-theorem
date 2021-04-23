"""
This file contains the main animation for the introduction to and proof of the
zone theorem.

:Authors:
    - William Boyles (wmboyles)
"""

from manim import *

from src.animations.draw_arrangement import DrawArrangmementDefinition
from src.animations.draw_statements import (
    DrawZoneTheoremStartProof,
    DrawZoneTheoremStatement,
)
from src.animations.draw_zone import DrawZoneDefintion
from src.animations.draw_bounding_edges import DrawBoundingEdgesDefinition


class Main(Scene):
    """
    This is the main animation that runs all subanimations to create the full
    introduction to and proof of the zone theorem.
    """

    def construct(self):
        """:meta private:"""

        # Say what an arrangment is
        DrawArrangmementDefinition.setup(self)
        DrawArrangmementDefinition.construct(self)

        self.wait(3)
        self.clear()

        # Lead in to idea of zones
        DrawZoneDefintion.setup(self)
        DrawZoneDefintion.construct(self)

        self.wait(3)
        self.clear()

        # State the zone theorem
        DrawZoneTheoremStatement.setup(self)
        DrawZoneTheoremStatement.construct(self)

        self.wait(3)
        self.clear()

        # Outline the proof strategy
        DrawZoneTheoremStartProof.setup(self)
        DrawZoneTheoremStartProof.construct(self)

        self.wait(3)
        self.clear()

        DrawBoundingEdgesDefinition.setup(self)
        DrawBoundingEdgesDefinition.construct(self)

        self.wait(3)