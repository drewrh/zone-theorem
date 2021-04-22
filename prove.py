from manim import *

from src.animations.draw_bounding_edges import DrawBoundingEdges
from src.animations.draw_zones import DrawRandomZone


# TODO: This is kinda hacky?
class Main(Scene):
    def construct(self):
        DrawBoundingEdges.setup(self)
        DrawBoundingEdges.construct(self)

        self.clear()

        DrawRandomZone.setup(self)
        DrawRandomZone.construct(self)
