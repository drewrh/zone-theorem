"""
Contains HalfEdge class, which is generally used in polygonal subdivision data
structures like
:class:`src.data_structures.polygonal_subdivision.BoundedPolygonalSubdivision`.

:Authors:
    - William Boyles (wmboyles)
"""


from dataclasses import dataclass
from numpy import ndarray

from .polygon import Polygon


@dataclass
class HalfEdge:
    """
    A HalfEdge is the most basic building block of a polygonal subdivision.
    HalfEdges connect two points that are joined by an edge.

    Since a single edge separates two faces, we split each edge in half so that
    we can associate a HalfEdge with a single face.

    The HalfEdge stores the point from which they originiate.

    HalfEdges are cyclically linked so that if we keep calling link or twin, we
    will get back to our starting HalfEdge after visiting all other HalfEdges
    in the same face.

    Each HalfEdge's other half is called it's twin.
    Going from a HalfEdge to its twin will change the current face in the
    polygonal subidvision.

    :Authors:
        - William Boyles (wmboyles)
    """

    point: ndarray = None
    """Point in subdivision from which this HalfEdge originates"""

    twin: "HalfEdge" = None
    """Other HalfEdge defining the same edge as this HalfEdge"""

    link: "HalfEdge" = None
    """Next HalfEdge in same Polygon as thisHalfEdge"""

    prev: "HalfEdge" = None
    """Previous Halfedge in same Polygon as this HalfEdge"""

    def get_polygon(self) -> Polygon:
        """
        Gets the Polygon of this HalfEdge.

        :return: The polygon of which this HalfEdge defines one edge.
        :rtype: :class:`src.data_structures.polygon.Polygon`
        """

        pts = [self.point]

        h = self.link
        while not all(h.point == self.point):
            pts.append(h.point)
            h = h.link

        return Polygon(pts)
