"""
This file contains animation classes that just write text to the screen, like
in definitions or theorem statements.

:Authors:
    - William Boyles
"""

from manim import *


class DrawZoneTheoremStatement(Scene):
    """
    This animation states the zone theorem.
    """

    def construct(self):
        """:meta private:"""

        theorem = Tex(
            r"\textbf{Theorem (Zone Theorem):} There are $O(n)$ edges in\\",
            r"the zone of $\ell$ in $A(L)$.",
            tex_environment="flushleft",
        )
        theorem.to_corner(UL)
        self.play(Write(theorem))


class DrawZoneTheoremStartProof(Scene):
    """
    This animation starts to prove the zone theorem by clairifying our
    assumptions and listing the general steps we will take when proving.
    """

    def construct(self):
        """:meta private:"""

        proof = Text("Proof Outline")
        proof.scale(1.5)
        proof.to_edge(UP)
        self.add(proof)

        # Say what assumptions we're making in our proof
        assumptions = Tex(r"\underline{Assumptions}")
        assumption_list = BulletedList(
            "$\ell$ is horizontal",
            "No 3 lines intersect at a point",
            "No parallel lines",
        )
        assumption_list.scale(0.75)
        assumption_list.to_edge(LEFT)

        assumptions.align_to(assumption_list, LEFT + UP)
        assumptions.shift(UP)

        self.play(Write(assumptions))
        self.play(Write(assumption_list, run_time=len(assumption_list)))

        self.wait(2)

        # Give the general proof strategy
        strategy = Tex(r"\underline{Strategy}")
        strategy_list = BulletedList(
            "Add lines from $L$ one by one",
            "Count edges each line adds",
            "Show it's $O(1)$",
        )
        strategy_list.to_edge(RIGHT)
        strategy_list.scale(0.75)
        strategy.align_to(strategy_list, LEFT + UP)
        strategy.shift(UP)

        self.play(Write(strategy))
        self.play(Write(strategy_list), run_time=len(strategy_list))
